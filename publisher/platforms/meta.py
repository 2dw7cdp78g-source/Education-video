"""Facebook Pages and Instagram (professional accounts) through the Meta Graph API.

One Facebook Login connects both: the Page you pick, and the Instagram account linked to it.
"""
from urllib.parse import urlencode

from .. import config, store
from .base import Platform, PublishError, NotConnected, check, client, read_chunks, wait_until

SCOPES = ["pages_show_list", "pages_read_engagement", "pages_manage_posts",
          "business_management", "instagram_basic", "instagram_content_publish"]
ACCOUNT_KEY = "meta"


def graph(path=""):
    return f"https://graph.facebook.com/{config.GRAPH_VERSION}/{path}"


def selected_page(account):
    if not account or not account.get("pages"):
        return None
    for p in account["pages"]:
        if p["id"] == account.get("page_id"):
            return p
    return account["pages"][0]


def rupload(c, url, token, video, what):
    """Send the whole file to a rupload.facebook.com URL (used by Reels and Instagram)."""
    size = video.stat().st_size
    return check(c.post(url, headers={"Authorization": f"OAuth {token}", "offset": "0",
                                      "file_size": str(size), "Content-Length": str(size),
                                      "Content-Type": "application/octet-stream"},
                        content=read_chunks(video, 4 * 1024 * 1024)), what)


class _Meta(Platform):
    account_key = ACCOUNT_KEY

    def configured(self):
        return bool(config.META_APP_ID and config.META_APP_SECRET)

    def setup_hint(self):
        return "Set META_APP_ID and META_APP_SECRET in publisher/.env"

    def auth_url(self, state):
        return f"https://www.facebook.com/{config.GRAPH_VERSION}/dialog/oauth?" + urlencode({
            "client_id": config.META_APP_ID,
            "redirect_uri": config.redirect_uri("meta"),
            "state": state,
            "scope": ",".join(SCOPES),
            "response_type": "code",
        })

    def handle_callback(self, code, state_data):
        with client() as c:
            short = check(c.get(graph("oauth/access_token"), params={
                "client_id": config.META_APP_ID, "client_secret": config.META_APP_SECRET,
                "redirect_uri": config.redirect_uri("meta"), "code": code}), "Facebook sign-in")
            long = check(c.get(graph("oauth/access_token"), params={
                "grant_type": "fb_exchange_token", "client_id": config.META_APP_ID,
                "client_secret": config.META_APP_SECRET,
                "fb_exchange_token": short["access_token"]}), "Getting a long-lived Facebook token")
            user_token = long["access_token"]
            me = check(c.get(graph("me"), params={"fields": "name", "access_token": user_token}),
                       "Reading your Facebook profile")
            pages = []
            url, params = graph("me/accounts"), {
                "fields": "id,name,access_token,instagram_business_account{id,username}",
                "access_token": user_token, "limit": 100}
            while url:
                data = check(c.get(url, params=params), "Listing your Facebook Pages")
                for p in data.get("data", []):
                    ig = p.get("instagram_business_account")
                    pages.append({"id": p["id"], "name": p["name"], "token": p["access_token"],
                                  "ig": {"id": ig["id"], "username": ig.get("username", "")} if ig else None})
                url, params = data.get("paging", {}).get("next"), None
        if not pages:
            raise PublishError("No Facebook Pages found. Posting through the API needs a Page "
                               "(personal profiles aren't supported). Create a Page and make sure you "
                               "ticked it when Facebook asked which Pages to allow.")
        with_ig = [p for p in pages if p["ig"]]
        return {"name": me.get("name", ""), "user_token": user_token, "pages": pages,
                "page_id": (with_ig or pages)[0]["id"]}

    def describe(self, account):
        page = selected_page(account)
        return page["name"] if page else "no Page"


class Facebook(_Meta):
    name = "facebook"
    label = "Facebook"

    def publish(self, account, video, opts, report):
        page = selected_page(account)
        if not page:
            raise NotConnected("Facebook is not connected")
        if opts.get("as_reel"):
            return self._reel(page, video, opts, report)
        report(0.05, "Uploading to your Page")
        with client() as c, open(video, "rb") as f:
            data = check(c.post(
                f"https://graph-video.facebook.com/{config.GRAPH_VERSION}/{page['id']}/videos",
                data={"title": (opts.get("title") or "")[:255],
                      "description": opts.get("description") or "",
                      "access_token": page["token"]},
                files={"source": (video.name, f, "video/mp4")}), "Facebook video upload")
        return {"url": f"https://www.facebook.com/watch/?v={data['id']}"}

    def _reel(self, page, video, opts, report):
        tok = {"access_token": page["token"]}
        with client() as c:
            start = check(c.post(graph(f"{page['id']}/video_reels"),
                                 data={"upload_phase": "start", **tok}), "Starting the Facebook Reel")
            vid = start["video_id"]
            report(0.1, "Uploading the Reel")
            rupload(c, start["upload_url"], page["token"], video, "Facebook Reel upload")
            report(0.7, "Publishing the Reel")
            check(c.post(graph(f"{page['id']}/video_reels"), data={
                "upload_phase": "finish", "video_id": vid, "video_state": "PUBLISHED",
                "description": opts.get("description") or "", **tok}), "Publishing the Facebook Reel")

            def ready():
                st = check(c.get(graph(vid), params={"fields": "status", **tok}),
                           "Checking the Reel").get("status", {})
                if st.get("video_status") == "error":
                    raise PublishError(f"Facebook rejected the Reel: {st}")
                return st.get("publishing_phase", {}).get("status") == "complete" or \
                    st.get("video_status") == "ready"
            report(0.8, "Facebook is processing the Reel")
            wait_until(ready, "Facebook to process the Reel")
        return {"url": f"https://www.facebook.com/reel/{vid}"}


class Instagram(_Meta):
    name = "instagram"
    label = "Instagram"

    def describe(self, account):
        page = selected_page(account)
        if page and page["ig"]:
            return "@" + page["ig"]["username"]
        return "no Instagram linked to this Page"

    def publish(self, account, video, opts, report):
        page = selected_page(account)
        if not page:
            raise NotConnected("Instagram is not connected")
        if not page["ig"]:
            raise PublishError(f"The Page '{page['name']}' has no Instagram professional account linked. "
                               "Link one in Instagram settings (Account type: Business or Creator).")
        ig, token = page["ig"]["id"], page["token"]
        with client() as c:
            container = check(c.post(graph(f"{ig}/media"), data={
                "media_type": "REELS", "upload_type": "resumable",
                "caption": (opts.get("caption") or "")[:2200],
                "share_to_feed": "true" if opts.get("share_to_feed", True) else "false",
                "access_token": token}), "Creating the Instagram post")
            cid = container["id"]
            report(0.1, "Uploading to Instagram")
            rupload(c, container["uri"], token, video, "Instagram upload")

            def finished():
                st = check(c.get(graph(cid), params={"fields": "status_code,status", "access_token": token}),
                           "Checking the Instagram upload")
                code = st.get("status_code")
                if code in ("ERROR", "EXPIRED"):
                    raise PublishError(f"Instagram couldn't process the video: {st.get('status', code)}. "
                                       "Reels must be MP4/MOV, H.264, 3 s to 15 min.")
                return code in ("FINISHED", "PUBLISHED")
            report(0.6, "Instagram is processing the video")
            wait_until(finished, "Instagram to process the video", every=8)

            report(0.9, "Publishing")
            media = check(c.post(graph(f"{ig}/media_publish"),
                                 data={"creation_id": cid, "access_token": token}), "Publishing on Instagram")
            link = check(c.get(graph(media["id"]), params={"fields": "permalink", "access_token": token}),
                         "Reading the post link")
        return {"url": link.get("permalink", "")}


def set_page(page_id):
    account = store.get_account(ACCOUNT_KEY)
    if not account or not any(p["id"] == page_id for p in account["pages"]):
        raise PublishError("Unknown Page")
    account["page_id"] = page_id
    store.save_account(ACCOUNT_KEY, account)
