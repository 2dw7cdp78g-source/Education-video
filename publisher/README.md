# One-click publisher

Post a video to **YouTube, Facebook, Instagram and TikTok** from one page: pick the video, check the text for each platform, press **Review & post**, then **Confirm & post**. All four upload at the same time and the page shows progress, links and a Retry button.

It reads your built episodes from `output/<id>/`. Titles, descriptions, tags, hashtags, subtitles (`en.srt`, `my.srt`) and the thumbnail are filled in for you:

| Video | Goes to (pre-ticked) |
|---|---|
| `long.mp4` | YouTube (with subtitles and thumbnail), Facebook video |
| `short-*.mp4` | YouTube Shorts, Facebook Reel, Instagram Reel, TikTok |

You can also upload any MP4/MOV from your computer.

## 1. Install and try it (no accounts needed)

```bash
pip install -r publisher/requirements.txt
cp publisher/.env.example publisher/.env
PUBLISHER_DRY_RUN=1 python3 -m publisher
```

Open http://localhost:8000. Dry run goes through every step but uploads nothing. When you're ready for real posts, set `PUBLISHER_DRY_RUN=0` (or remove it) and connect your accounts.

## 2. Connect each platform (one time)

Each platform needs a free developer app. You put its keys in `publisher/.env`, then press **Connect** in the page. Logins are stored encrypted in `publisher/data/` (git ignores that folder). Never share the folder or `.env`.

### YouTube
1. Go to https://console.cloud.google.com, create a project, then **APIs & Services → Library → YouTube Data API v3 → Enable**.
2. **OAuth consent screen**: External, add your own Google address under **Test users**.
3. **Credentials → Create credentials → OAuth client ID → Web application**. Authorised redirect URI: `http://localhost:8000/auth/youtube/callback`.
4. Copy the client ID and secret into `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET`.

**Limits:**
- The free quota is about 6 uploads a day.
- Until Google approves an [API audit](https://support.google.com/youtube/contact/yt_api_form), every upload is locked to **Private**. You can make it public by hand in YouTube Studio, or apply for the audit.
- Custom thumbnails need a phone-verified channel.
- While the consent screen is in "Testing" mode, Google sign-ins expire after 7 days. Publish the consent screen (you can leave it unverified for personal use) to avoid reconnecting every week.

### Facebook and Instagram (one login connects both)
1. Your Instagram account must be **Business or Creator**, and linked to a **Facebook Page**. Personal Facebook profiles can't be posted to through the API.
2. Go to https://developers.facebook.com, then **Create app → Other → Business**.
3. Add **Facebook Login for Business** (or Facebook Login). Under Valid OAuth Redirect URIs, add `http://localhost:8000/auth/meta/callback`. Meta normally allows localhost in development mode; if it refuses, use the https tunnel described below.
4. Add the **Instagram** product (the API setup that uses Facebook Login).
5. Copy the App ID and secret into `META_APP_ID` / `META_APP_SECRET`.
6. Leave the app in **Development** mode. As the app's admin you can post to your own Page and Instagram without App Review.
7. Press **Connect** next to Facebook, and tick your Page (and its Instagram) when Facebook asks. If you have several Pages, a picker appears.

**Limits:**
- Instagram Reels: 3 s to 15 min, MP4/MOV, and about 50 API posts a day.
- Facebook Reels: 3 to 90 s, vertical.
- Long Facebook videos: up to 1 GB through this simple upload.

### TikTok
1. Go to https://developers.tiktok.com, then **Manage apps → Connect an app**.
2. Add the **Login Kit** and **Content Posting API** products, with the scopes `user.info.basic`, `video.publish` and `video.upload`. Turn on **Direct Post**.
3. TikTok only accepts **https** redirect addresses, so run the app behind a tunnel, for example `cloudflared tunnel --url http://localhost:8000`. Then in `.env`:
   ```
   PUBLIC_BASE_URL=https://<your-tunnel>.trycloudflare.com
   APP_PASSWORD=<a long password>
   ```
   Register `https://<your-tunnel>/auth/tiktok/callback` as the redirect URI. Open the app through the tunnel address and register that same base address with Google and Meta too. The app refuses to start without `APP_PASSWORD` when it isn't on localhost.
   A quick tunnel gets a new address each time, so use a named tunnel (a fixed address) to keep the redirect URIs valid.
4. Copy the client key and secret into `TIKTOK_CLIENT_KEY` / `TIKTOK_CLIENT_SECRET`.

**Limits:**
- Until TikTok audits your app, Direct Post only works while your TikTok account is set to **Private**, and posts are visible to you only. After the audit you can post publicly.
- Meanwhile you can choose **Send to my TikTok inbox**. The video arrives as a draft in the TikTok app, and you finish posting there.
- TikTok's review also asks for a privacy policy and terms URL for the app.

## 3. Daily use
1. `python3 pipeline/build.py episodes/<id>` (the build also writes `upload.json` for this app).
2. `python3 -m publisher`, then open the page.
3. Pick the episode and the video, adjust text if you like, then **Review & post → Confirm & post**.

## Files
- `platforms/youtube.py`, `meta.py` (Facebook + Instagram), `tiktok.py`: the uploaders.
- `web.py`: the page, sign-ins, posting API. `jobs.py`: runs uploads in parallel.
- `episodes.py`: turns `output/<id>/` into ready-made text for each platform.
- Tests: `python3 -m pytest publisher/tests` (uses fake platform APIs, uploads nothing).
