import json
import time

import httpx
import pytest
from fastapi.testclient import TestClient

from publisher import config, episodes, store
from publisher.platforms import meta, tiktok, youtube
from publisher.platforms.base import PublishError


def make_episode(root, ep_id="99-test"):
    out = root / "output" / ep_id
    out.mkdir(parents=True, exist_ok=True)
    (out / "long.mp4").write_bytes(b"\0" * 1000)
    (out / "short-01-hook.mp4").write_bytes(b"\0" * 500)
    (out / "en.srt").write_text("1\n00:00:00,000 --> 00:00:01,000\nHi\n")
    (out / "thumbnail.jpg").write_bytes(b"\xff\xd8\xff")
    (out / "upload.json").write_text(json.dumps({
        "id": ep_id, "title": "Test Episode", "draft": False, "titles": ["Test Episode, Explained"],
        "description": "First paragraph.\n\nSources\n- x", "tags": ["Myanmar", "Burma"],
        "hashtags": ["#Myanmar"],
        "shorts": [{"id": "short-01-hook", "hook": "The *big* hook", "caption": "Short caption.",
                    "hashtags": ["#Myanmar", "#Shorts"]}]}))
    return out


# ---------------------------------------------------------------- pure helpers
def test_tiktok_chunk_plan():
    assert tiktok.chunk_plan(1000) == (1000, 1)
    mb = 1024 * 1024
    assert tiktok.chunk_plan(25 * mb) == (10 * mb, 2)      # remainder joins the last chunk
    ranges = list(tiktok.chunk_ranges(25 * mb))
    assert ranges == [(0, 10 * mb - 1), (10 * mb, 25 * mb - 1)]
    assert tiktok.chunk_plan(7 * mb) == (7 * mb, 1)
    with pytest.raises(PublishError):
        tiktok.chunk_plan(0)


def test_youtube_tag_limit():
    tags = youtube._trim_tags(["#Myanmar", "civil war"] + ["x" * 50] * 20)
    assert tags[:2] == ["Myanmar", "civil war"]
    assert sum(len(t) + 1 for t in tags) <= 500


def test_episode_presets(tmp_root):
    make_episode(tmp_root)
    ep = next(e for e in episodes.list_episodes() if e["id"] == "99-test")
    long, short = ep["videos"]
    assert long["presets"]["youtube"]["title"] == "Test Episode, Explained"
    assert "#Myanmar" in long["presets"]["youtube"]["description"]
    assert long["presets"]["youtube"]["captions"][0]["language"] == "en"
    assert long["presets"]["youtube"]["thumbnail"].endswith("thumbnail.jpg")
    assert short["presets"]["youtube"]["title"] == "The big hook #Shorts"
    assert short["presets"]["facebook"]["as_reel"] is True
    assert short["presets"]["tiktok"]["caption"].startswith("Short caption.")
    assert set(short["platforms"]) == {"youtube", "facebook", "instagram", "tiktok"}


def test_resolve_video_refuses_escape(tmp_root):
    make_episode(tmp_root)
    with pytest.raises(ValueError):
        episodes.resolve_video("99-test", "../../data/publisher.db")
    assert episodes.resolve_video("99-test", "long.mp4").name == "long.mp4"


def test_tokens_are_encrypted():
    store.save_account("unit", {"access_token": "very-secret"})
    raw = store.conn().execute("SELECT data FROM accounts WHERE platform='unit'").fetchone()[0]
    assert b"very-secret" not in raw
    assert store.get_account("unit")["access_token"] == "very-secret"


# ---------------------------------------------------------------- the app, dry run
def test_post_dry_run_end_to_end(tmp_root):
    make_episode(tmp_root)
    from publisher.web import app
    c = TestClient(app)
    assert {p["name"] for p in c.get("/api/status").json()["platforms"]} == {"youtube", "facebook", "instagram", "tiktok"}
    r = c.post("/api/posts", json={"source": {"episode": "99-test", "file": "short-01-hook.mp4"},
                                   "platforms": ["youtube", "instagram", "tiktok"],
                                   "settings": {"youtube": {"title": "T", "captions": [{"path": "/etc/passwd", "language": "en"}]},
                                                "tiktok": {"caption": "c", "privacy": "SELF_ONLY"}}})
    assert r.status_code == 200, r.text
    pid = r.json()["id"]
    assert store.get_post(pid)["settings"]["youtube"]["captions"] == []   # paths outside output/ are dropped
    for _ in range(50):
        jobs = c.get(f"/api/posts/{pid}").json()["jobs"]
        if all(j["state"] == "done" for j in jobs):
            break
        time.sleep(0.2)
    assert [j["state"] for j in jobs] == ["done"] * 3
    assert c.get("/api/posts").json()[0]["id"] == pid


def test_post_validation(tmp_root):
    make_episode(tmp_root)
    from publisher.web import app
    c = TestClient(app)
    src = {"episode": "99-test", "file": "long.mp4"}
    assert c.post("/api/posts", json={"source": src, "platforms": []}).status_code == 400
    assert c.post("/api/posts", json={"source": {"episode": "99-test", "file": "nope.mp4"},
                                      "platforms": ["youtube"]}).status_code == 400
    r = c.post("/api/posts", json={"source": src, "platforms": ["tiktok"], "settings": {"tiktok": {}}})
    assert r.status_code == 400 and "TikTok" in r.json()["detail"]


def test_upload_file(tmp_root):
    from publisher.web import app
    c = TestClient(app)
    r = c.post("/api/upload", files={"file": ("my clip.mp4", b"\0" * 10, "video/mp4")})
    assert r.status_code == 200
    assert (config.UPLOAD_DIR / r.json()["upload"]).exists()
    assert c.post("/api/upload", files={"file": ("x.exe", b"MZ", "application/octet-stream")}).status_code == 400


def test_password_required(monkeypatch):
    from publisher import web
    monkeypatch.setattr(config, "APP_PASSWORD", "pw")
    c = TestClient(web.app)
    assert c.get("/api/status").status_code == 401
    c.post("/login", data={"password": "pw"})
    assert c.get("/api/status").status_code == 200


# ---------------------------------------------------------------- uploaders against fake APIs
def fake_client(monkeypatch, module, handler):
    monkeypatch.setattr(module, "client", lambda: httpx.Client(transport=httpx.MockTransport(handler)))
    monkeypatch.setattr("publisher.platforms.base.time.sleep", lambda s: None)


def test_youtube_upload(monkeypatch, tmp_path):
    video = tmp_path / "v.mp4"
    video.write_bytes(b"a" * (youtube.CHUNK + 10))
    srt = tmp_path / "en.srt"
    srt.write_text("1\n")
    calls = []

    def handler(req):
        calls.append((req.method, req.url.path))
        if req.url.path == "/upload/youtube/v3/videos":
            body = json.loads(req.content)
            assert body["snippet"]["title"] == "Hello" and body["status"]["privacyStatus"] == "unlisted"
            return httpx.Response(200, headers={"Location": "https://www.googleapis.com/session/1"})
        if req.url.path == "/session/1":
            start, end = req.headers["Content-Range"].split()[1].split("/")[0].split("-")
            if int(end) + 1 < video.stat().st_size:
                return httpx.Response(308, headers={"Range": f"bytes=0-{end}"})
            return httpx.Response(200, json={"id": "VID", "status": {"privacyStatus": "unlisted"}})
        if req.url.path == "/upload/youtube/v3/captions":
            assert b'"language": "en"' in req.content
            return httpx.Response(200, json={"id": "cap"})
        if req.url.path == "/upload/youtube/v3/thumbnails/set":
            return httpx.Response(403, json={"error": {"message": "not verified"}})
        raise AssertionError(req.url)

    fake_client(monkeypatch, youtube, handler)
    account = {"access_token": "t", "refresh_token": "r", "expires_at": time.time() + 999}
    res = youtube.YouTube().publish(account, video, {
        "title": "Hello", "privacy": "unlisted", "tags": ["a"],
        "captions": [{"path": str(srt), "language": "en", "name": "English"}],
        "thumbnail": str(srt)}, lambda p, m: None)
    assert res["url"] == "https://youtu.be/VID"
    assert "thumbnail skipped" in res["note"]
    assert [c for c in calls if c[1] == "/session/1"].__len__() == 2


def test_instagram_reel(monkeypatch, tmp_path):
    video = tmp_path / "v.mp4"
    video.write_bytes(b"a" * 100)
    polls = iter(["IN_PROGRESS", "FINISHED"])

    def handler(req):
        p = req.url.path
        if p.endswith("/IG/media"):
            return httpx.Response(200, json={"id": "C1", "uri": "https://rupload.facebook.com/ig-api-upload/v24.0/C1"})
        if "rupload" in str(req.url):
            assert req.headers["file_size"] == "100" and req.headers["Authorization"] == "OAuth PT"
            return httpx.Response(200, json={"success": True})
        if p.endswith("/C1"):
            return httpx.Response(200, json={"status_code": next(polls)})
        if p.endswith("/media_publish"):
            return httpx.Response(200, json={"id": "M1"})
        if p.endswith("/M1"):
            return httpx.Response(200, json={"permalink": "https://instagram.com/reel/x"})
        raise AssertionError(req.url)

    fake_client(monkeypatch, meta, handler)
    account = {"pages": [{"id": "P", "name": "Page", "token": "PT", "ig": {"id": "IG", "username": "me"}}], "page_id": "P"}
    res = meta.Instagram().publish(account, video, {"caption": "hi"}, lambda p, m: None)
    assert res["url"] == "https://instagram.com/reel/x"


def test_instagram_needs_linked_account(tmp_path):
    video = tmp_path / "v.mp4"
    video.write_bytes(b"a")
    account = {"pages": [{"id": "P", "name": "Page", "token": "PT", "ig": None}], "page_id": "P"}
    with pytest.raises(PublishError, match="no Instagram"):
        meta.Instagram().publish(account, video, {}, lambda p, m: None)


def test_tiktok_direct_post(monkeypatch, tmp_path):
    video = tmp_path / "v.mp4"
    video.write_bytes(b"a" * 300)
    ok = {"error": {"code": "ok"}}

    def handler(req):
        p = req.url.path
        if p.endswith("/creator_info/query/"):
            return httpx.Response(200, json={**ok, "data": {"creator_nickname": "me",
                                                             "privacy_level_options": ["SELF_ONLY"]}})
        if p.endswith("/post/publish/video/init/"):
            body = json.loads(req.content)
            assert body["source_info"] == {"source": "FILE_UPLOAD", "video_size": 300, "chunk_size": 300,
                                           "total_chunk_count": 1}
            assert body["post_info"]["privacy_level"] == "SELF_ONLY"
            return httpx.Response(200, json={**ok, "data": {"publish_id": "PUB", "upload_url": "https://up.tiktok/x"}})
        if req.url.host == "up.tiktok":
            assert req.headers["Content-Range"] == "bytes 0-299/300"
            return httpx.Response(201)
        if p.endswith("/status/fetch/"):
            return httpx.Response(200, json={**ok, "data": {"status": "PUBLISH_COMPLETE",
                                                             "publicaly_available_post_id": [123]}})
        raise AssertionError(req.url)

    fake_client(monkeypatch, tiktok, handler)
    account = {"access_token": "t", "refresh_token": "r", "expires_at": time.time() + 999,
               "refresh_expires_at": time.time() + 9999}
    res = tiktok.TikTok().publish(account, video, {"caption": "c", "privacy": "SELF_ONLY"}, lambda p, m: None)
    assert res["url"].endswith("/video/123")
    with pytest.raises(PublishError, match="Options"):
        tiktok.TikTok().publish(account, video, {"caption": "c", "privacy": "PUBLIC_TO_EVERYONE"}, lambda p, m: None)


def test_tiktok_unaudited_message(monkeypatch, tmp_path):
    def handler(req):
        return httpx.Response(200, json={"error": {"code": "unaudited_client_can_only_post_to_private_accounts"}})
    fake_client(monkeypatch, tiktok, handler)
    with pytest.raises(PublishError, match="Private"):
        tiktok.TikTok().creator_info({"access_token": "t", "expires_at": time.time() + 99})
