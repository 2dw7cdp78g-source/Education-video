"""Shared pieces for the platform uploaders."""
import time

import httpx

TIMEOUT = httpx.Timeout(60.0, read=600.0, write=600.0)


class PublishError(Exception):
    """A problem worth showing to the user as-is."""


class NotConnected(PublishError):
    pass


def client():
    return httpx.Client(timeout=TIMEOUT, follow_redirects=True)


def check(resp, what):
    """Raise a readable PublishError for a failed HTTP response, else return its JSON (or {})."""
    if resp.status_code >= 400:
        detail = resp.text[:600]
        try:
            body = resp.json()
            err = body.get("error", body)
            if isinstance(err, dict):
                detail = err.get("message") or err.get("error_user_msg") or err.get("code") or str(err)
                if err.get("error_description"):
                    detail = f"{detail}: {err['error_description']}"
            elif body.get("error_description"):
                detail = f"{err}: {body['error_description']}"
            else:
                detail = str(err)
        except ValueError:
            pass
        raise PublishError(f"{what} failed (HTTP {resp.status_code}): {detail}")
    if not resp.content:
        return {}
    try:
        return resp.json()
    except ValueError:
        return {}


def read_chunks(path, chunk_size):
    with open(path, "rb") as f:
        while True:
            data = f.read(chunk_size)
            if not data:
                return
            yield data


def wait_until(fn, what, timeout=900, every=5):
    """Call fn() until it returns a truthy value; fn raises PublishError on a hard failure."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        result = fn()
        if result:
            return result
        time.sleep(every)
    raise PublishError(f"Timed out waiting for {what}")


class Platform:
    name = ""
    label = ""
    # Which settings fields the UI shows for this platform.
    fields = ()

    def configured(self):
        raise NotImplementedError

    def setup_hint(self):
        return "Add this platform's app credentials to publisher/.env"

    def auth_url(self, state):
        raise NotImplementedError

    def handle_callback(self, code, state_data):
        """Exchange the OAuth code and return the account dict to store."""
        raise NotImplementedError

    def describe(self, account):
        return account.get("name", "connected")

    def publish(self, account, video, opts, report):
        """Upload `video` (a Path). Call report(progress 0..1, message). Return the post URL."""
        raise NotImplementedError
