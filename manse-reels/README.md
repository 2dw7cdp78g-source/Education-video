# MANSE Korean Food: Facebook Reels

There are 10 vertical reels (1080×1920, 20–26 s each), one per menu item. They're in `reels/`, with a cover image for each and ready-to-paste captions in `reels/CAPTIONS.md` (English and Thai, plus hashtags).

Each reel follows the same plan:
1. **Hook (first 2 s):** a big headline built to stop scrolling (price shock, challenge, myth-busting, curiosity, relatable moment).
2. **Two "what's inside" beats:** ingredient tags pop up while the voiceover describes the dish.
3. **Options:** choice of meat, vegan or spice level.
4. **Price sticker:** price in baht, with the Thai price in a line underneath.
5. **End card:** your mascot, the MANSE name, "แวะมาชิมกันได้เลย!" and a comment or tag prompt (comments and tags are what spread a reel).

The voiceover (English AI voice), the music and the sound effects were all generated for these videos, so there are no copyright problems.

## Posting tips
- Post one reel a day, at lunch (11:00–12:00) or dinner (17:00–19:00).
- Choose the `-cover.jpg` as the cover. In `CAPTIONS.md`, replace `[your area]` and add your location.
- Reply to every comment within the first hour, because Facebook pushes reels that get conversations going.
- If the menu photos are AI-generated or stock photos, switch on Facebook's "AI info" label when you upload, or replace them with real photos of your food (see below).

## Rebuilding / editing
Edit the text in `reels.json`, then run `python3 build.py` (all reels) or `python3 build.py 03` (one reel).
To swap in a real photo, replace `assets/menu/<dish>.jpg`. Needs Python 3, ffmpeg, Node and Playwright, plus the Kokoro voice model in `../pipeline/models`.
