"""Turn the pipeline's output/<id>/ folders into ready-to-post presets."""
import json
import re

from . import config


def _strip_marks(text):
    return re.sub(r"\*([^*]+)\*", r"\1", text or "").strip()


def _hashtags(tags):
    return " ".join(t if t.startswith("#") else f"#{t}" for t in tags)


def _kit(out_dir):
    """upload.json from the build, or a fallback assembled from episode.json."""
    kit_file = out_dir / "upload.json"
    if kit_file.exists():
        return json.loads(kit_file.read_text(encoding="utf-8"))
    ep_file = config.EPISODES_DIR / out_dir.name / "episode.json"
    if not ep_file.exists():
        return {"id": out_dir.name, "title": out_dir.name, "titles": [out_dir.name], "description": "",
                "tags": [], "hashtags": [], "shorts": []}
    ep = json.loads(ep_file.read_text(encoding="utf-8"))
    up = ep.get("upload", {})
    desc = "\n\n".join(x for x in (up.get("description", ""), up.get("footer", "")) if x)
    return {"id": ep["id"], "title": ep["title"], "titles": up.get("titles", [ep["title"]]),
            "description": desc, "tags": up.get("tags", []), "hashtags": up.get("hashtags", []),
            "shorts": [{"id": s["id"], "hook": s.get("hook", ""), "caption": s.get("caption", s.get("hook", "")),
                        "hashtags": s.get("hashtags", up.get("hashtags", []))} for s in ep.get("shorts", [])]}


def long_preset(kit, out_dir):
    title = kit["titles"][0] if kit.get("titles") else kit["title"]
    tags_line = _hashtags(kit.get("hashtags", []))
    description = kit.get("description", "")
    if tags_line and tags_line not in description:
        description = f"{description}\n\n{tags_line}".strip()
    captions = [{"path": str(out_dir / f), "language": lang, "name": name}
                for f, lang, name in (("en.srt", "en", "English"), ("my.srt", "my", "Burmese"))
                if (out_dir / f).exists()]
    thumb = out_dir / "thumbnail.jpg"
    return {
        "youtube": {"title": title, "description": description, "tags": kit.get("tags", []),
                    "privacy": "private", "captions": captions,
                    "thumbnail": str(thumb) if thumb.exists() else ""},
        "facebook": {"title": title,
                     "description": (kit.get("description", "").split("\n\n")[0]
                                     + (f"\n\n{tags_line}" if tags_line else "")).strip(),
                     "as_reel": False},
        "instagram": {"caption": f"{title}\n\n{tags_line}".strip()},
        "tiktok": {"caption": f"{title} {tags_line}".strip()},
    }


def short_preset(short, kit):
    hook = _strip_marks(short.get("hook")) or kit["title"]
    caption = short.get("caption") or hook
    tags_line = _hashtags(short.get("hashtags", []))
    text = f"{caption}\n\n{tags_line}".strip()
    yt_title = hook if len(hook) <= 90 else hook[:87] + "..."
    return {
        "youtube": {"title": f"{yt_title} #Shorts", "description": text, "tags": kit.get("tags", []),
                    "privacy": "private", "short": True, "captions": [], "thumbnail": ""},
        "facebook": {"title": hook, "description": text, "as_reel": True},
        "instagram": {"caption": text},
        "tiktok": {"caption": f"{caption} {tags_line}".strip()},
    }


def list_episodes():
    out = []
    if not config.OUTPUT_DIR.exists():
        return out
    for d in sorted(config.OUTPUT_DIR.iterdir()):
        if not d.is_dir():
            continue
        kit = _kit(d)
        videos = []
        if (d / "long.mp4").exists():
            videos.append({"file": "long.mp4", "kind": "long", "label": "Long video (16:9)",
                           "platforms": ["youtube", "facebook"], "presets": long_preset(kit, d)})
        shorts = {s["id"]: s for s in kit.get("shorts", [])}
        for f in sorted(d.glob("short-*.mp4")):
            sh = shorts.get(f.stem, {"id": f.stem, "hook": f.stem, "caption": "", "hashtags": kit.get("hashtags", [])})
            videos.append({"file": f.name, "kind": "short", "label": f"Short: {_strip_marks(sh.get('hook')) or f.stem}",
                           "platforms": ["youtube", "facebook", "instagram", "tiktok"],
                           "presets": short_preset(sh, kit)})
        if videos:
            out.append({"id": d.name, "title": kit.get("title", d.name), "draft": bool(kit.get("draft")),
                        "videos": videos})
    return out


def resolve_video(episode_id, filename):
    """Path to a pipeline video, refusing anything outside the output folder."""
    path = (config.OUTPUT_DIR / episode_id / filename).resolve()
    if config.OUTPUT_DIR.resolve() not in path.parents or path.suffix.lower() not in (".mp4", ".mov"):
        raise ValueError("Not a pipeline video")
    if not path.exists():
        raise FileNotFoundError(filename)
    return path
