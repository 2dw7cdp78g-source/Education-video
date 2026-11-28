"""TikTok Content Posting API: Direct Post, or Upload (sends a draft to your TikTok inbox)."""
import time
from urllib.parse import urlencode

from .. import config, store
from .base import Platform, PublishError, NotConnected, check, client, wait_until

API = "https://open.tiktokapis.com/v2"
SCOPES = ["user.info.basic", "video.publish", "video.upload"]
MIN_CHUNK = 5 * 1024 * 1024
CHUNK = 10 * 1024 * 1024


def tt_check(resp, what):
    """TikTok answers HTTP 200 with error.code != 'ok' for some failures."""
    data = check(resp, what)
    err = data.get("error") or {}
    if err.get("code") not in (None, "ok"):
        msg = err.get("message") or err["code"]
        if err["code"] == "unaudited_client_can_only_post_to_private_accounts":
            msg = ("until TikTok approves your app's audit, Direct Post only works when your TikTok "
                   "account is set to Private. Switch the account to Private, or use 'Send to TikTok "
                   "inbox' mode")
        raise PublishError(f"{what} failed: {msg}")
    return data.get("data", data)


def chunk_plan(size):
    """Return (chunk_size, total_chunk_count) following TikTok's rules:
    files under 5 MB go in one chunk; otherwise fixed chunks, with the remainder
    added to the last chunk (so the count is size // chunk_size)."""
    if size <= 0:
        raise PublishError("The video file is empty")
    if size < MIN_CHUNK:
        return size, 1
    chunk = min(CHUNK, size)
    return chunk, size // chunk


def chunk_ranges(size):
    chunk, count = chunk_plan(size)
    for i in range(count):
        start = i * chunk
        end = size - 1 if i == count - 1 else start + chunk - 1
        yield start, end


class TikTok(Platform):
    name = "tiktok"
    label = "TikTok"

    def configured(self):
        return bool(config.TIKTOK_CLIENT_KEY and config.TIKTOK_CLIENT_SECRET)

    def setup_hint(self):
        return "Set TIKTOK_CLIENT_KEY and TIKTOK_CLIENT_SECRET in publisher/.env"

    def auth_url(self, state):
        return "https://www.tiktok.com/v2/auth/authorize/?" + urlencode({
            "client_key": config.TIKTOK_CLIENT_KEY,
            "scope": ",".join(SCOPES),
            "response_type": "code",
            "redirect_uri": config.redirect_uri(self.name),
            "state": state,
        })

    def _token_request(self, **form):
        with client() as c:
            tok = check(c.post(f"{API}/oauth/token/", data={
                "client_key": config.TIKTOK_CLIENT_KEY,
                "client_secret": config.TIKTOK_CLIENT_SECRET, **form},
                headers={"Content-Type": "application/x-www-form-urlencoded"}), "TikTok sign-in")
        if "access_token" not in tok:
            raise PublishError(f"TikTok sign-in failed: {tok.get('error_description') or tok}")
        now = time.time()
        return {"access_token": tok["access_token"], "refresh_token": tok["refresh_token"],
                "expires_at": now + tok.get("expires_in", 86400) - 120,
                "refresh_expires_at": now + tok.get("refresh_expires_in", 365 * 86400),
                "open_id": tok.get("open_id", "")}

    def handle_callback(self, code, state_data):
        account = self._token_request(code=code, grant_type="authorization_code",
                                      redirect_uri=config.redirect_uri(self.name))
        with client() as c:
            info = tt_check(c.get(f"{API}/user/info/", params={"fields": "open_id,display_name"},
                                  headers={"Authorization": f"Bearer {account['access_token']}"}),
                            "Reading your TikTok profile")
        account["name"] = info.get("user", {}).get("display_name", "TikTok")
        return account

    def token(self, account):
        if time.time() < account.get("expires_at", 0):
            return account["access_token"]
        if time.time() > account.get("refresh_expires_at", 0):
            raise NotConnected("The TikTok login expired. Connect TikTok again.")
        fresh = self._token_request(grant_type="refresh_token", refresh_token=account["refresh_token"])
        account.update({k: v for k, v in fresh.items() if v})
        store.save_account(self.name, account)
        return account["access_token"]

    def creator_info(self, account):
        with client() as c:
            return tt_check(c.post(f"{API}/post/publish/creator_info/query/",
                                   headers={"Authorization": f"Bearer {self.token(account)}",
                                            "Content-Type": "application/json; charset=UTF-8"}),
                            "Reading your TikTok posting options")

    def publish(self, account, video, opts, report):
        if not account:
            raise NotConnected("TikTok is not connected")
        auth = {"Authorization": f"Bearer {self.token(account)}",
                "Content-Type": "application/json; charset=UTF-8"}
        size = video.stat().st_size
        chunk, count = chunk_plan(size)
        source = {"source": "FILE_UPLOAD", "video_size": size, "chunk_size": chunk,
                  "total_chunk_count": count}
        inbox = opts.get("mode") == "inbox"

        with client() as c:
            if inbox:
                init = tt_check(c.post(f"{API}/post/publish/inbox/video/init/", headers=auth,
                                       json={"source_info": source}), "Starting the TikTok upload")
            else:
                creator = self.creator_info(account)
                privacy = opts.get("privacy") or ""
                allowed = creator.get("privacy_level_options") or []
                if privacy not in allowed:
                    raise PublishError(f"Pick who can see the TikTok post. Options for your account: "
                                       f"{', '.join(allowed) or 'none'}")
                max_sec = creator.get("max_video_post_duration_sec")
                if max_sec and opts.get("duration") and opts["duration"] > max_sec:
                    raise PublishError(f"TikTok allows videos up to {max_sec} s on your account")
                init = tt_check(c.post(f"{API}/post/publish/video/init/", headers=auth, json={
                    "post_info": {
                        "title": (opts.get("caption") or "")[:2200],
                        "privacy_level": privacy,
                        "disable_comment": bool(opts.get("disable_comment")),
                        "disable_duet": bool(opts.get("disable_duet")),
                        "disable_stitch": bool(opts.get("disable_stitch")),
                        "video_cover_timestamp_ms": 1000,
                    },
                    "source_info": source}), "Starting the TikTok post")
            publish_id, upload_url = init["publish_id"], init["upload_url"]

            with open(video, "rb") as f:
                for start, end in chunk_ranges(size):
                    f.seek(start)
                    data = f.read(end - start + 1)
                    check(c.put(upload_url, content=data, headers={
                        "Content-Type": "video/mp4", "Content-Length": str(len(data)),
                        "Content-Range": f"bytes {start}-{end}/{size}"}), "Uploading to TikTok")
                    report(0.8 * (end + 1) / size, f"Uploading {(end + 1) * 100 // size}%")

            report(0.85, "TikTok is processing the video")
            result = {}

            def done():
                st = tt_check(c.post(f"{API}/post/publish/status/fetch/", headers=auth,
                                     json={"publish_id": publish_id}), "Checking the TikTok post")
                status = st.get("status")
                if status == "FAILED":
                    raise PublishError(f"TikTok rejected the video: {st.get('fail_reason', 'unknown reason')}")
                if status in ("PUBLISH_COMPLETE", "SEND_TO_USER_INBOX"):
                    result.update(st)
                    return True
                return False
            wait_until(done, "TikTok to process the video", every=5)

        if inbox:
            return {"url": "", "note": "Sent to your TikTok inbox. Open TikTok to finish and post it."}
        ids = result.get("publicaly_available_post_id") or result.get("publicly_available_post_id") or []
        url = f"https://www.tiktok.com/@/video/{ids[0]}" if ids else ""
        note = "" if ids else "Posted. TikTok gives a link only for public posts; find it in your profile."
        return {"url": url, "note": note}
