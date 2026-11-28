"""Run a confirmed post: every chosen platform uploads in parallel, in the background."""
import json
import logging
import subprocess
import threading
import time
import traceback
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from . import config, store
from .platforms import PLATFORMS, PublishError, account_key

log = logging.getLogger("publisher")
_pool = ThreadPoolExecutor(max_workers=8)
_running = set()
_running_lock = threading.Lock()


def video_duration(path):
    """Seconds, via ffprobe if it's installed; None otherwise."""
    try:
        out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                              "-of", "json", str(path)], capture_output=True, text=True, timeout=30)
        return float(json.loads(out.stdout)["format"]["duration"])
    except Exception:
        return None


def _simulate(platform, video, opts, report):
    for i in range(1, 6):
        time.sleep(0.2)
        report(i / 5, f"[dry run] uploading {i * 20}%")
    return {"url": f"https://example.com/{platform}/dry-run", "note": "Dry run: nothing was uploaded"}


def run_job(post_id, platform):
    key = (post_id, platform)
    with _running_lock:
        if key in _running:
            return
        _running.add(key)
    try:
        post = store.get_post(post_id)
        video = Path(post["video"])
        opts = dict(post["settings"].get(platform, {}))
        opts.setdefault("duration", post["settings"].get("_duration"))
        store.update_job(post_id, platform, state="running", message="Starting", progress=0, url="")

        def report(progress, message):
            store.update_job(post_id, platform, progress=round(max(0, min(1, progress)), 3), message=message)

        if config.DRY_RUN:
            result = _simulate(platform, video, opts, report)
        else:
            if not video.exists():
                raise PublishError(f"The video file is gone: {video}")
            account = store.get_account(account_key(platform))
            result = PLATFORMS[platform].publish(account, video, opts, report)
        note = result.get("note") or ""
        store.update_job(post_id, platform, state="done", progress=1, url=result.get("url", ""),
                         message=f"Posted. {note}".strip() if note else "Posted")
    except PublishError as e:
        store.update_job(post_id, platform, state="failed", message=str(e))
    except Exception as e:  # unexpected: keep the details in the log
        log.error("Job %s/%s crashed:\n%s", post_id, platform, traceback.format_exc())
        store.update_job(post_id, platform, state="failed", message=f"Unexpected error: {e}")
    finally:
        with _running_lock:
            _running.discard(key)


def start(post_id, platforms):
    for p in platforms:
        _pool.submit(run_job, post_id, p)
