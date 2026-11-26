# Myanmar Stories video pipeline

This pipeline turns a script plus your recorded voice into a finished long video, vertical shorts, Burmese and English subtitles, a thumbnail and upload text.

## Making an episode
1. Script: `episodes/<id>/episode.json` (scenes, English lines, Burmese lines, shorts).
2. Read-aloud script: `python3 pipeline/script.py episodes/<id>` writes `SCRIPT.md`.
3. Record: put `narration-01.m4a`, `narration-02.m4a`, … (one per part) in `episodes/<id>/audio/`.
4. Build: `python3 pipeline/build.py episodes/<id>`. Add `--fast` for a quick preview.
5. Output: `output/<id>/` contains `long.mp4`, the `short-*.mp4` files, `thumbnail.jpg`, `en.srt`, `my.srt` and `upload.md`.

Without audio, the build makes a silent draft with estimated timing so you can preview it.

Requires `ffmpeg`, Python 3, Node, and Playwright with Chromium.

See [PLAN.md](PLAN.md) for the channel strategy and safety checklist.

## Channel defaults
`pipeline/channel.json` holds the author bio (shown as an intro after the title) and the standard ending (subscribe, share your experience, contact for research animation). Every episode gets both automatically. Set `"author_intro": false` or `"standard_outro": false` in an episode to turn one off. Burmese terminology lives in `GLOSSARY.md`.
