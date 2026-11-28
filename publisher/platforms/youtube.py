"""YouTube Data API v3: resumable video upload, plus optional captions and thumbnail."""
import json
import time
import uuid
from pathlib import Path
from urllib.parse import urlencode

from .. import config, store
from .base import Platform, PublishError, NotConnected, check, client

AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"
API = "https://www.googleapis.com/youtube/v3"
UPLOAD_API = "https://www.googleapis.com/upload/youtube/v3"
# youtube.upload for videos; youtube.force-ssl for captions and reading the channel name.
SCOPES = ["https://www.googleapis.com/auth/youtube.upload",
          "https://www.googleapis.com/auth/youtube.force-ssl"]
CHUNK = 8 * 1024 * 1024  # must be a multiple of 256 KiB


def _trim_tags(tags, limit=480):
    """YouTube caps the combined tag length at 500 characters."""
    out, total = [], 0
    for t in tags:
        t = t.strip().lstrip("#")
        if not t:
            continue
        cost = len(t) + (2 if " " in t else 0) + 1
        if total + cost > limit:
            break
        out.append(t)
        total += cost
    return out


class YouTube(Platform):
    name = "youtube"
    label = "YouTube"

    def configured(self):
        return bool(config.GOOGLE_CLIENT_ID and config.GOOGLE_CLIENT_SECRET)

    def setup_hint(self):
        return "Set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET in publisher/.env"

    def auth_url(self, state):
        return AUTH_URL + "?" + urlencode({
            "client_id": config.GOOGLE_CLIENT_ID,
            "redirect_uri": config.redirect_uri(self.name),
            "response_type": "code",
            "scope": " ".join(SCOPES),
            "access_type": "offline",
            "prompt": "consent",
            "include_granted_scopes": "true",
            "state": state,
        })

    def handle_callback(self, code, state_data):
        with client() as c:
            tok = check(c.post(TOKEN_URL, data={
                "code": code,
                "client_id": config.GOOGLE_CLIENT_ID,
                "client_secret": config.GOOGLE_CLIENT_SECRET,
                "redirect_uri": config.redirect_uri(self.name),
                "grant_type": "authorization_code",
            }), "Google sign-in")
            if not tok.get("refresh_token"):
                raise PublishError("Google did not return a refresh token. Remove the app's access at "
                                   "myaccount.google.com/permissions and connect again.")
            account = {
                "access_token": tok["access_token"],
                "refresh_token": tok["refresh_token"],
                "expires_at": time.time() + tok.get("expires_in", 3600) - 60,
            }
            ch = check(c.get(f"{API}/channels", params={"part": "snippet", "mine": "true"},
                             headers={"Authorization": f"Bearer {account['access_token']}"}),
                       "Reading your YouTube channel")
            items = ch.get("items") or []
            if not items:
                raise PublishError("This Google account has no YouTube channel yet. Create one first.")
            account["channel_id"] = items[0]["id"]
            account["name"] = items[0]["snippet"]["title"]
        return account

    def token(self, account):
        if time.time() < account.get("expires_at", 0):
            return account["access_token"]
        with client() as c:
            tok = check(c.post(TOKEN_URL, data={
                "client_id": config.GOOGLE_CLIENT_ID,
                "client_secret": config.GOOGLE_CLIENT_SECRET,
                "refresh_token": account["refresh_token"],
                "grant_type": "refresh_token",
            }), "Refreshing the YouTube login")
        account["access_token"] = tok["access_token"]
        account["expires_at"] = time.time() + tok.get("expires_in", 3600) - 60
        store.save_account(self.name, account)
        return account["access_token"]

    def publish(self, account, video, opts, report):
        if not account:
            raise NotConnected("YouTube is not connected")
        token = self.token(account)
        auth = {"Authorization": f"Bearer {token}"}
        size = video.stat().st_size

        title = (opts.get("title") or video.stem).strip()[:100]
        status = {"privacyStatus": opts.get("privacy", "private"),
                  "selfDeclaredMadeForKids": bool(opts.get("made_for_kids", False))}
        if opts.get("publish_at"):
            # Scheduled videos must be private until the publish time.
            status["privacyStatus"] = "private"
            status["publishAt"] = opts["publish_at"]
        body = {
            "snippet": {
                "title": title,
                "description": (opts.get("description") or "")[:5000],
                "tags": _trim_tags(opts.get("tags") or []),
                "categoryId": str(opts.get("category_id") or "27"),  # 27 = Education
                "defaultAudioLanguage": opts.get("language") or "en",
            },
            "status": status,
        }

        with client() as c:
            init = c.post(f"{UPLOAD_API}/videos",
                          params={"uploadType": "resumable", "part": "snippet,status"},
                          headers={**auth, "Content-Type": "application/json; charset=UTF-8",
                                   "X-Upload-Content-Length": str(size),
                                   "X-Upload-Content-Type": "video/mp4"},
                          content=json.dumps(body))
            check(init, "Starting the YouTube upload")
            session_url = init.headers["Location"]

            sent, result = 0, None
            with open(video, "rb") as f:
                while sent < size:
                    f.seek(sent)
                    data = f.read(CHUNK)
                    end = sent + len(data) - 1
                    resp = c.put(session_url, content=data, headers={
                        **auth, "Content-Length": str(len(data)),
                        "Content-Range": f"bytes {sent}-{end}/{size}"})
                    if resp.status_code == 308:
                        rng = resp.headers.get("Range")
                        sent = int(rng.split("-")[1]) + 1 if rng else 0
                    elif resp.status_code in (200, 201):
                        result = resp.json()
                        sent = size
                    else:
                        check(resp, "Uploading to YouTube")
                    report(0.9 * sent / size, f"Uploading {sent * 100 // size}%")
            if not result:
                raise PublishError("YouTube upload finished without returning a video")

            video_id = result["id"]
            notes = []
            if result.get("status", {}).get("privacyStatus") == "private" and status["privacyStatus"] != "private":
                notes.append("YouTube locked it to private: your Google Cloud project hasn't passed the API audit yet")

            for cap in opts.get("captions") or []:
                report(0.93, f"Adding {cap['language']} subtitles")
                try:
                    self._caption(c, auth, video_id, Path(cap["path"]), cap["language"], cap.get("name", ""))
                except PublishError as e:
                    notes.append(f"subtitles {cap['language']} skipped: {e}")

            if opts.get("thumbnail"):
                report(0.97, "Setting the thumbnail")
                try:
                    thumb = Path(opts["thumbnail"])
                    ctype = "image/png" if thumb.suffix.lower() == ".png" else "image/jpeg"
                    check(c.post(f"{UPLOAD_API}/thumbnails/set",
                                 params={"videoId": video_id, "uploadType": "media"},
                                 headers={**auth, "Content-Type": ctype}, content=thumb.read_bytes()),
                          "Thumbnail")
                except (PublishError, OSError) as e:
                    notes.append(f"thumbnail skipped: {e} (custom thumbnails need a phone-verified channel)")

        is_short = bool(opts.get("short"))
        url = f"https://youtube.com/shorts/{video_id}" if is_short else f"https://youtu.be/{video_id}"
        return {"url": url, "note": "; ".join(notes)}

    def _caption(self, c, auth, video_id, path, language, name):
        boundary = uuid.uuid4().hex
        meta = json.dumps({"snippet": {"videoId": video_id, "language": language,
                                       "name": name, "isDraft": False}})
        body = (f"--{boundary}\r\nContent-Type: application/json; charset=UTF-8\r\n\r\n{meta}\r\n"
                f"--{boundary}\r\nContent-Type: application/octet-stream\r\n\r\n").encode() \
            + path.read_bytes() + f"\r\n--{boundary}--\r\n".encode()
        check(c.post(f"{UPLOAD_API}/captions", params={"part": "snippet", "uploadType": "multipart"},
                     headers={**auth, "Content-Type": f"multipart/related; boundary={boundary}"},
                     content=body), "Subtitles upload")
