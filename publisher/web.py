"""The web app: one page to pick a video, review it per platform, and confirm."""
import hmac
import re
import secrets
import shutil
import time
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request, UploadFile, File
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from . import config, episodes, jobs, store
from .platforms import PLATFORMS, META_KEY, PublishError, account_key
from .platforms.meta import set_page, selected_page

STATIC = config.HERE / "static"
# Sign-in flows: Facebook and Instagram share one Meta login.
AUTH = {"youtube": PLATFORMS["youtube"], "meta": PLATFORMS["facebook"], "tiktok": PLATFORMS["tiktok"]}
ALLOWED = {
    "youtube": {"title", "description", "tags", "privacy", "made_for_kids", "publish_at",
                "category_id", "language", "captions", "thumbnail", "short"},
    "facebook": {"title", "description", "as_reel"},
    "instagram": {"caption", "share_to_feed"},
    "tiktok": {"caption", "mode", "privacy", "disable_comment", "disable_duet", "disable_stitch"},
}


def _session_secret():
    if config.SECRET_KEY:
        return config.SECRET_KEY
    f = config.DATA_DIR / "session.key"
    if not f.exists():
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(secrets.token_urlsafe(48))
        f.chmod(0o600)
    return f.read_text().strip()


app = FastAPI(title="One-click video publisher", docs_url=None, redoc_url=None)
app.mount("/static", StaticFiles(directory=STATIC), name="static")


def logged_in(request):
    return not config.APP_PASSWORD or request.session.get("ok") is True


@app.middleware("http")
async def require_login(request: Request, call_next):
    path = request.url.path
    if path.startswith(("/static/", "/login")) or logged_in(request):
        return await call_next(request)
    if path.startswith("/api/"):
        return JSONResponse({"detail": "Sign in first"}, status_code=401)
    return RedirectResponse("/login")


# Added last so it runs first: the login check above needs the session.
app.add_middleware(SessionMiddleware, secret_key=_session_secret(), session_cookie="publisher",
                   same_site="lax", https_only=config.BASE_URL.startswith("https://"),
                   max_age=30 * 86400)


# ---------------------------------------------------------------- pages
@app.get("/", response_class=HTMLResponse)
def index():
    return FileResponse(STATIC / "index.html")


@app.get("/login", response_class=HTMLResponse)
def login_page():
    return FileResponse(STATIC / "login.html")


@app.post("/login")
async def login(request: Request):
    form = await request.form()
    if config.APP_PASSWORD and hmac.compare_digest(str(form.get("password", "")), config.APP_PASSWORD):
        request.session["ok"] = True
        return RedirectResponse("/", status_code=303)
    time.sleep(1)
    return RedirectResponse("/login?wrong=1", status_code=303)


@app.post("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/login", status_code=303)


# ---------------------------------------------------------------- accounts
@app.get("/api/status")
def status():
    out = {"dry_run": config.DRY_RUN, "base_url": config.BASE_URL, "password": bool(config.APP_PASSWORD),
           "platforms": []}
    for name, p in PLATFORMS.items():
        account = store.get_account(account_key(name))
        out["platforms"].append({
            "name": name, "label": p.label, "configured": p.configured() or config.DRY_RUN,
            "connected": bool(account) or config.DRY_RUN,
            "account": p.describe(account) if account else ("dry run" if config.DRY_RUN else ""),
            "auth": "meta" if name in ("facebook", "instagram") else name,
            "hint": p.setup_hint(),
        })
    meta = store.get_account(META_KEY)
    if meta:
        page = selected_page(meta)
        out["meta_pages"] = [{"id": pg["id"], "name": pg["name"],
                              "instagram": pg["ig"]["username"] if pg["ig"] else "",
                              "selected": pg["id"] == page["id"]} for pg in meta["pages"]]
    return out


@app.get("/auth/{flow}/start")
def auth_start(flow: str, request: Request):
    p = AUTH.get(flow)
    if not p:
        raise HTTPException(404)
    if not p.configured():
        raise HTTPException(400, p.setup_hint())
    state = secrets.token_urlsafe(24)
    request.session[f"oauth_{flow}"] = state
    return RedirectResponse(p.auth_url(state))


@app.get("/auth/{flow}/callback", response_class=HTMLResponse)
def auth_callback(flow: str, request: Request, code: str = "", state: str = "", error: str = "",
                  error_description: str = ""):
    p = AUTH.get(flow)
    if not p:
        raise HTTPException(404)
    expected = request.session.pop(f"oauth_{flow}", None)
    if error:
        return _back(f"Sign-in was cancelled or refused: {error_description or error}")
    if not expected or not hmac.compare_digest(expected, state) or not code:
        return _back("The sign-in link expired. Try connecting again.")
    try:
        account = p.handle_callback(code, {})
    except PublishError as e:
        return _back(str(e))
    store.save_account(getattr(p, "account_key", p.name), account)
    return RedirectResponse("/?connected=" + flow)


def _back(message):
    from urllib.parse import quote
    return RedirectResponse("/?error=" + quote(message[:500]))


@app.post("/api/disconnect/{flow}")
def disconnect(flow: str):
    p = AUTH.get(flow)
    if not p:
        raise HTTPException(404)
    store.delete_account(getattr(p, "account_key", p.name))
    return {"ok": True}


@app.post("/api/meta/page")
async def choose_page(request: Request):
    body = await request.json()
    try:
        set_page(str(body.get("page_id", "")))
    except PublishError as e:
        raise HTTPException(400, str(e))
    return {"ok": True}


@app.get("/api/tiktok/creator")
def tiktok_creator():
    if config.DRY_RUN:
        return {"creator_nickname": "dry run", "privacy_level_options":
                ["PUBLIC_TO_EVERYONE", "MUTUAL_FOLLOW_FRIENDS", "SELF_ONLY"], "max_video_post_duration_sec": 600}
    account = store.get_account("tiktok")
    if not account:
        raise HTTPException(400, "TikTok is not connected")
    try:
        return PLATFORMS["tiktok"].creator_info(account)
    except PublishError as e:
        raise HTTPException(400, str(e))


# ---------------------------------------------------------------- videos
@app.get("/api/episodes")
def list_episodes():
    return episodes.list_episodes()


@app.post("/api/upload")
def upload(file: UploadFile = File(...)):
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in (".mp4", ".mov", ".m4v"):
        raise HTTPException(400, "Upload an MP4 or MOV video")
    config.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    stem = re.sub(r"[^A-Za-z0-9._-]+", "-", Path(file.filename).stem)[:60] or "video"
    name = f"{time.strftime('%Y%m%d-%H%M%S')}-{secrets.token_hex(3)}-{stem}{suffix}"
    with open(config.UPLOAD_DIR / name, "wb") as out:
        shutil.copyfileobj(file.file, out, 4 * 1024 * 1024)
    return {"upload": name, "name": file.filename}


def _inside(path, *roots):
    p = Path(path).resolve()
    return any(r.resolve() in p.parents for r in roots)


def _clean(platform, opts):
    opts = {k: v for k, v in (opts or {}).items() if k in ALLOWED[platform]}
    if platform == "youtube":
        roots = (config.OUTPUT_DIR, config.UPLOAD_DIR)
        opts["captions"] = [c for c in opts.get("captions") or []
                            if isinstance(c, dict) and c.get("path") and _inside(c["path"], *roots)]
        if opts.get("thumbnail") and not _inside(opts["thumbnail"], *roots):
            opts["thumbnail"] = ""
        if opts.get("privacy") not in ("private", "unlisted", "public"):
            opts["privacy"] = "private"
        if isinstance(opts.get("tags"), str):
            opts["tags"] = [t.strip() for t in opts["tags"].split(",") if t.strip()]
    return opts


@app.post("/api/posts")
async def create_post(request: Request):
    body = await request.json()
    src = body.get("source") or {}
    try:
        if src.get("upload"):
            video = (config.UPLOAD_DIR / Path(src["upload"]).name).resolve()
            if not video.exists():
                raise FileNotFoundError(src["upload"])
            label = src.get("name") or video.name
        else:
            video = episodes.resolve_video(src.get("episode", ""), src.get("file", ""))
            label = f"{src['episode']} / {src['file']}"
    except (ValueError, FileNotFoundError, KeyError):
        raise HTTPException(400, "Pick a video first")

    platforms = [p for p in body.get("platforms") or [] if p in PLATFORMS]
    if not platforms:
        raise HTTPException(400, "Pick at least one platform")
    missing = [PLATFORMS[p].label for p in platforms
               if not config.DRY_RUN and not store.get_account(account_key(p))]
    if missing:
        raise HTTPException(400, f"Connect {', '.join(missing)} first")

    settings = {p: _clean(p, (body.get("settings") or {}).get(p)) for p in platforms}
    if "tiktok" in platforms and settings["tiktok"].get("mode") != "inbox" and not settings["tiktok"].get("privacy"):
        raise HTTPException(400, "Choose who can see the TikTok post")
    settings["_duration"] = jobs.video_duration(video)
    post_id = store.create_post(video, label, settings, platforms)
    jobs.start(post_id, platforms)
    return {"id": post_id}


@app.get("/api/posts")
def posts():
    return store.list_posts()


@app.get("/api/posts/{post_id}")
def post(post_id: int):
    p = store.get_post(post_id)
    if not p:
        raise HTTPException(404)
    p.pop("settings", None)
    return p


@app.post("/api/posts/{post_id}/retry/{platform}")
def retry(post_id: int, platform: str):
    p = store.get_post(post_id)
    if not p or not any(j["platform"] == platform for j in p["jobs"]):
        raise HTTPException(404)
    job = next(j for j in p["jobs"] if j["platform"] == platform)
    if job["state"] in ("running", "queued", "done"):
        raise HTTPException(400, "Only failed uploads can be retried")
    store.update_job(post_id, platform, state="queued", message="Retrying", progress=0)
    jobs.start(post_id, [platform])
    return {"ok": True}
