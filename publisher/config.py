"""Settings, read from publisher/.env (or the real environment)."""
import os
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent


def _load_dotenv(path):
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


_load_dotenv(HERE / ".env")


def env(name, default=""):
    return os.environ.get(name, default).strip()


BASE_URL = env("PUBLIC_BASE_URL", "http://localhost:8000").rstrip("/")
HOST = env("HOST", "127.0.0.1")
PORT = int(env("PORT", "8000"))
APP_PASSWORD = env("APP_PASSWORD")
SECRET_KEY = env("SECRET_KEY")
DRY_RUN = env("PUBLISHER_DRY_RUN") in ("1", "true", "yes")

DATA_DIR = Path(env("PUBLISHER_DATA_DIR", str(HERE / "data")))
UPLOAD_DIR = DATA_DIR / "uploads"
DB_PATH = DATA_DIR / "publisher.db"
OUTPUT_DIR = Path(env("PIPELINE_OUTPUT_DIR", str(ROOT / "output")))
EPISODES_DIR = ROOT / "episodes"

GOOGLE_CLIENT_ID = env("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = env("GOOGLE_CLIENT_SECRET")

META_APP_ID = env("META_APP_ID")
META_APP_SECRET = env("META_APP_SECRET")
GRAPH_VERSION = env("META_GRAPH_VERSION", "v24.0")

TIKTOK_CLIENT_KEY = env("TIKTOK_CLIENT_KEY")
TIKTOK_CLIENT_SECRET = env("TIKTOK_CLIENT_SECRET")


def redirect_uri(platform):
    return f"{BASE_URL}/auth/{platform}/callback"


def is_local_url(url):
    return any(h in url for h in ("://localhost", "://127.0.0.1", "://[::1]"))
