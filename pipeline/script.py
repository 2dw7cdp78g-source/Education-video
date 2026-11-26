#!/usr/bin/env python3
"""Export an episode's narration as an easy-to-read script for recording.

Usage: python3 pipeline/script.py episodes/01-civil-war-explained
Writes SCRIPT.md in the episode folder.
"""
import json
import sys
from pathlib import Path

ep_dir = Path(sys.argv[1])
ep = json.loads((ep_dir / "episode.json").read_text(encoding="utf-8"))
out = [f"# {ep['title']}: narration script", "",
       "Pause about 1 second between sentences and 2 seconds between parts. If you stumble, re-record that whole part file.", ""]
part, words = 1, 0
out += [f"## File: narration-{part:02d} (intro)", ""]
for sc in ep["scenes"]:
    if sc["type"] == "chapter":
        part += 1
        out += [f"## File: narration-{part:02d} (Part {sc.get('number')}: {sc['title']})", ""]
    for l in sc["lines"]:
        out.append(l["en"])
        out.append("")
        words += len(l["en"].split())
out.insert(2, f"About {words} words, roughly {words / 150:.0f} minutes at a calm pace.\n")
(ep_dir / "SCRIPT.md").write_text("\n".join(out), encoding="utf-8")
print(f"{ep_dir / 'SCRIPT.md'}: {words} words, {part} parts")
