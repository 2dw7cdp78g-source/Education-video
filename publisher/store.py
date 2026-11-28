"""SQLite storage: encrypted account tokens, posts and per-platform job status."""
import json
import sqlite3
import threading
import time

from cryptography.fernet import Fernet

from . import config

_lock = threading.Lock()
_conn = None
_fernet = None


def _key_file():
    return config.DATA_DIR / "secret.key"


def fernet():
    """Tokens are encrypted with a key kept in data/secret.key (created on first run)."""
    global _fernet
    if _fernet is None:
        kf = _key_file()
        if not kf.exists():
            kf.parent.mkdir(parents=True, exist_ok=True)
            kf.write_bytes(Fernet.generate_key())
            kf.chmod(0o600)
        _fernet = Fernet(kf.read_bytes().strip())
    return _fernet


def conn():
    global _conn
    if _conn is None:
        config.DATA_DIR.mkdir(parents=True, exist_ok=True)
        _conn = sqlite3.connect(config.DB_PATH, check_same_thread=False)
        _conn.row_factory = sqlite3.Row
        _conn.executescript("""
            CREATE TABLE IF NOT EXISTS accounts (
                platform TEXT PRIMARY KEY,
                data BLOB NOT NULL,
                updated REAL NOT NULL
            );
            CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created REAL NOT NULL,
                video TEXT NOT NULL,
                label TEXT NOT NULL,
                settings TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS jobs (
                post_id INTEGER NOT NULL,
                platform TEXT NOT NULL,
                state TEXT NOT NULL,
                message TEXT NOT NULL DEFAULT '',
                url TEXT NOT NULL DEFAULT '',
                progress REAL NOT NULL DEFAULT 0,
                updated REAL NOT NULL,
                PRIMARY KEY (post_id, platform)
            );
        """)
    return _conn


def _exec(sql, args=()):
    with _lock:
        c = conn()
        cur = c.execute(sql, args)
        c.commit()
        return cur


def _query(sql, args=()):
    with _lock:
        return [dict(r) for r in conn().execute(sql, args).fetchall()]


# ---------------------------------------------------------------- accounts
def save_account(platform, data):
    blob = fernet().encrypt(json.dumps(data).encode())
    _exec("INSERT OR REPLACE INTO accounts (platform, data, updated) VALUES (?, ?, ?)",
          (platform, blob, time.time()))


def get_account(platform):
    rows = _query("SELECT data FROM accounts WHERE platform = ?", (platform,))
    if not rows:
        return None
    return json.loads(fernet().decrypt(rows[0]["data"]))


def delete_account(platform):
    _exec("DELETE FROM accounts WHERE platform = ?", (platform,))


# ---------------------------------------------------------------- posts and jobs
def create_post(video, label, settings, platforms):
    cur = _exec("INSERT INTO posts (created, video, label, settings) VALUES (?, ?, ?, ?)",
                (time.time(), str(video), label, json.dumps(settings)))
    post_id = cur.lastrowid
    for p in platforms:
        _exec("INSERT INTO jobs (post_id, platform, state, updated) VALUES (?, ?, 'queued', ?)",
              (post_id, p, time.time()))
    return post_id


def get_post(post_id):
    rows = _query("SELECT * FROM posts WHERE id = ?", (post_id,))
    if not rows:
        return None
    post = rows[0]
    post["settings"] = json.loads(post["settings"])
    post["jobs"] = _query("SELECT platform, state, message, url, progress, updated FROM jobs "
                          "WHERE post_id = ? ORDER BY platform", (post_id,))
    return post


def list_posts(limit=20):
    posts = _query("SELECT id, created, label FROM posts ORDER BY id DESC LIMIT ?", (limit,))
    for p in posts:
        p["jobs"] = _query("SELECT platform, state, url FROM jobs WHERE post_id = ? ORDER BY platform",
                           (p["id"],))
    return posts


def update_job(post_id, platform, **fields):
    fields["updated"] = time.time()
    cols = ", ".join(f"{k} = ?" for k in fields)
    _exec(f"UPDATE jobs SET {cols} WHERE post_id = ? AND platform = ?",
          (*fields.values(), post_id, platform))
