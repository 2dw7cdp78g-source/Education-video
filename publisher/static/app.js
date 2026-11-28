"use strict";
const $ = (s, el = document) => el.querySelector(s);

function h(tag, attrs = {}, ...kids) {
  const el = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (k === "class") el.className = v;
    else if (k.startsWith("on")) el.addEventListener(k.slice(2), v);
    else if (v === true) el.setAttribute(k, "");
    else if (v !== false && v != null) el.setAttribute(k, v);
  }
  for (const kid of kids.flat()) if (kid != null) el.append(kid);
  return el;
}

async function api(path, opts = {}) {
  const res = await fetch(path, {
    ...opts,
    headers: opts.body && !(opts.body instanceof FormData) ? { "Content-Type": "application/json" } : {},
  });
  if (res.status === 401) { location.href = "/login"; throw new Error("Sign in first"); }
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.detail || `Error ${res.status}`);
  return data;
}

function flash(msg, kind = "bad") {
  const el = $("#flash");
  el.textContent = msg; el.className = `flash ${kind}`; el.hidden = !msg;
  if (msg) window.scrollTo({ top: 0, behavior: "smooth" });
}

const LABELS = { youtube: "YouTube", facebook: "Facebook", instagram: "Instagram", tiktok: "TikTok" };
const TT_PRIVACY = { PUBLIC_TO_EVERYONE: "Everyone", MUTUAL_FOLLOW_FRIENDS: "Friends", FOLLOWER_OF_CREATOR: "Followers", SELF_ONLY: "Only me" };
let status = { platforms: [] };
let episodes = [];
let source = null;            // {episode, file} or {upload, name}
let tiktokCreator = null;
const forms = {};             // platform -> {root, get(), set(values)}

// ---------------------------------------------------------------- accounts
async function loadStatus() {
  status = await api("/api/status");
  $("#dryrun").hidden = !status.dry_run;
  $("#logout").hidden = !status.password;
  const box = $("#accounts"); box.replaceChildren();
  for (const p of status.platforms) {
    let btn;
    if (!p.configured) btn = h("div", { class: "muted", style: "font-size:13px" }, p.hint);
    else if (p.connected && !status.dry_run) btn = h("button", { onclick: () => disconnect(p) }, "Disconnect");
    else if (!p.connected) btn = h("a", { href: `/auth/${p.auth}/start` }, h("button", {}, "Connect"));
    box.append(h("div", { class: "acct" }, h("b", {}, p.label),
      h("div", { class: "who" }, p.connected ? `✓ ${p.account}` : "Not connected"), btn));
  }
  const pages = status.meta_pages || [];
  $("#pagepick").hidden = pages.length < 2;
  $("#page").replaceChildren(...pages.map(pg => h("option", { value: pg.id, selected: pg.selected },
    pg.name + (pg.instagram ? ` (Instagram @${pg.instagram})` : " (no Instagram)"))));
  for (const p of status.platforms) {
    const f = forms[p.name];
    if (f) f.root.querySelector(".note").textContent = p.connected ? "" : " (not connected)";
  }
  updateReview();
}

async function disconnect(p) {
  const shared = p.auth === "meta" ? "Facebook and Instagram" : p.label;
  if (!confirm(`Disconnect ${shared}?`)) return;
  await api(`/api/disconnect/${p.auth}`, { method: "POST" });
  loadStatus();
}

$("#page").addEventListener("change", async e => {
  await api("/api/meta/page", { method: "POST", body: JSON.stringify({ page_id: e.target.value }) });
  loadStatus();
});

// ---------------------------------------------------------------- per-platform forms
function field(label, input, max) {
  const wrap = h("label", {}, label, input);
  if (max) {
    const c = h("div", { class: "counter" });
    const upd = () => { c.textContent = `${input.value.length} / ${max}`; c.classList.toggle("error", input.value.length > max); };
    input.addEventListener("input", upd); wrap.append(c); input._upd = upd;
  }
  return wrap;
}
const text = (max) => h("input", { type: "text", maxlength: max });
const area = () => h("textarea");
const select = (opts) => h("select", {}, opts.map(([v, l]) => h("option", { value: v }, l)));
const box = (label) => { const i = h("input", { type: "checkbox" }); return [i, h("label", { class: "check" }, i, label)]; };
function setVal(el, v) { if (el.type === "checkbox") el.checked = !!v; else el.value = v ?? ""; el._upd && el._upd(); }

function buildForms() {
  const root = $("#platforms");
  // YouTube
  {
    const title = text(100), desc = area(), tags = text(), privacy = select([["private", "Private"], ["unlisted", "Unlisted"], ["public", "Public"]]);
    const when = h("input", { type: "datetime-local" });
    const [extras, extrasL] = box("");
    let preset = {};
    const f = makePlatform("youtube", [field("Title", title, 100), field("Description", desc, 5000),
      field("Tags (comma separated)", tags), h("div", { class: "row" }, field("Visibility", privacy),
        field("Schedule (optional, goes public then)", when)), extrasL]);
    f.set = (v) => {
      preset = v; setVal(title, v.title); setVal(desc, v.description); setVal(tags, (v.tags || []).join(", "));
      setVal(privacy, v.privacy || "private"); setVal(when, "");
      const n = (v.captions || []).length, t = !!v.thumbnail;
      extrasL.hidden = !n && !t; setVal(extras, true);
      extrasL.lastChild.textContent = ` Also add ${[n ? `${n} subtitle file${n > 1 ? "s" : ""} (${v.captions.map(c => c.name).join(", ")})` : "", t ? "the thumbnail" : ""].filter(Boolean).join(" and ")}`;
    };
    f.get = () => ({
      title: title.value, description: desc.value, privacy: privacy.value, short: !!preset.short,
      tags: tags.value.split(",").map(s => s.trim()).filter(Boolean),
      publish_at: when.value ? new Date(when.value).toISOString() : "",
      captions: extras.checked ? preset.captions || [] : [], thumbnail: extras.checked ? preset.thumbnail || "" : "",
    });
    f.summary = (s) => [`${s.title}`, `Visibility: ${s.publish_at ? `scheduled ${new Date(s.publish_at).toLocaleString()}` : s.privacy}${s.short ? " · Short" : ""}`, s.description];
  }
  // Facebook
  {
    const title = text(255), desc = area(); const [reel, reelL] = box(" Post as a Reel (vertical, 3 to 90 seconds)");
    const titleL = field("Title", title);
    const f = makePlatform("facebook", [reelL, titleL, field("Description", desc)]);
    reel.addEventListener("change", () => { titleL.hidden = reel.checked; });
    f.set = (v) => { setVal(title, v.title); setVal(desc, v.description); setVal(reel, v.as_reel); titleL.hidden = !!v.as_reel; };
    f.get = () => ({ title: title.value, description: desc.value, as_reel: reel.checked });
    f.summary = (s) => [s.as_reel ? "Reel" : `Video: ${s.title}`, s.description];
  }
  // Instagram
  {
    const cap = area(); const [feed, feedL] = box(" Also show it in the main feed");
    const f = makePlatform("instagram", [h("p", { class: "muted" }, "Posts as a Reel. Instagram needs MP4/MOV, 3 seconds to 15 minutes."),
      field("Caption", cap, 2200), feedL]);
    f.set = (v) => { setVal(cap, v.caption); setVal(feed, v.share_to_feed ?? true); };
    f.get = () => ({ caption: cap.value, share_to_feed: feed.checked });
    f.summary = (s) => ["Reel" + (s.share_to_feed ? " + feed" : ""), s.caption];
  }
  // TikTok
  {
    const cap = area(), mode = select([["direct", "Post directly"], ["inbox", "Send to my TikTok inbox as a draft (finish in the app)"]]);
    const privacy = h("select"), who = h("p", { class: "muted" });
    const [c1, c1L] = box(" Allow comments"), [c2, c2L] = box(" Allow Duet"), [c3, c3L] = box(" Allow Stitch");
    const direct = h("div", {}, field("Who can see it (required)", privacy), h("div", { class: "row" }, c1L, c2L, c3L));
    const f = makePlatform("tiktok", [who, field("Caption", cap, 2200), field("Mode", mode), direct]);
    mode.addEventListener("change", () => { direct.hidden = mode.value === "inbox"; updateReview(); });
    privacy.addEventListener("change", updateReview);
    f.loadCreator = async () => {
      if (tiktokCreator) return;
      try {
        tiktokCreator = await api("/api/tiktok/creator");
        who.textContent = `Posting as ${tiktokCreator.creator_nickname}. Max length ${tiktokCreator.max_video_post_duration_sec || "?"} s.`;
        privacy.replaceChildren(h("option", { value: "" }, "Choose…"),
          ...(tiktokCreator.privacy_level_options || []).map(o => h("option", { value: o }, TT_PRIVACY[o] || o)));
        c1.disabled = !!tiktokCreator.comment_disabled; c2.disabled = !!tiktokCreator.duet_disabled; c3.disabled = !!tiktokCreator.stitch_disabled;
      } catch (e) { who.textContent = `Couldn't read your TikTok settings: ${e.message}`; }
    };
    f.set = (v) => { setVal(cap, v.caption); [c1, c2, c3].forEach(c => setVal(c, !c.disabled)); };
    f.get = () => ({ caption: cap.value, mode: mode.value, privacy: privacy.value,
      disable_comment: !c1.checked, disable_duet: !c2.checked, disable_stitch: !c3.checked });
    f.valid = () => mode.value === "inbox" || !!privacy.value;
    f.summary = (s) => [s.mode === "inbox" ? "Draft to TikTok inbox" : `Visible to: ${TT_PRIVACY[s.privacy] || s.privacy}`, s.caption];
  }
}

function makePlatform(name, fields) {
  const on = h("input", { type: "checkbox" });
  const wrap = h("div", { class: "plat off" }, h("label", { class: "check" }, on, LABELS[name], h("span", { class: "note muted" })),
    h("div", { class: "fields" }, fields));
  on.addEventListener("change", () => {
    wrap.classList.toggle("off", !on.checked);
    if (on.checked && name === "tiktok") forms.tiktok.loadCreator();
    updateReview();
  });
  $("#platforms").append(wrap);
  const f = forms[name] = { root: wrap, on, valid: () => true };
  return f;
}

function enable(name, yes) {
  const f = forms[name];
  const connected = status.platforms.find(p => p.name === name)?.connected;
  f.on.checked = yes && connected;
  f.root.classList.toggle("off", !f.on.checked);
  if (f.on.checked && name === "tiktok") f.loadCreator();
}

// ---------------------------------------------------------------- choosing a video
async function loadEpisodes() {
  episodes = await api("/api/episodes");
  const sel = $("#episode");
  sel.replaceChildren(...episodes.map(e => h("option", { value: e.id }, e.title + (e.draft ? " (DRAFT)" : ""))));
  $("#noeps").hidden = episodes.length > 0;
  sel.parentElement.hidden = episodes.length === 0;
  renderVideos();
}

function renderVideos() {
  const ep = episodes.find(e => e.id === $("#episode").value);
  const list = $("#videos"); list.replaceChildren();
  if (!ep) return;
  ep.videos.forEach((v, i) => {
    const r = h("input", { type: "radio", name: "video", value: v.file });
    r.addEventListener("change", () => pickVideo(ep, v));
    list.append(h("label", {}, r, v.label, h("span", { class: "muted" }, ` · ${v.file}`)));
    if (i === 0) { r.checked = true; pickVideo(ep, v); }
  });
}
$("#episode").addEventListener("change", renderVideos);

function pickVideo(ep, v) {
  source = { episode: ep.id, file: v.file, label: `${ep.title}: ${v.label}`, draft: ep.draft };
  for (const name of Object.keys(forms)) { forms[name].set(v.presets[name] || {}); enable(name, v.platforms.includes(name)); }
  updateReview();
}

document.querySelectorAll(".tab").forEach(t => t.addEventListener("click", () => {
  document.querySelectorAll(".tab").forEach(x => x.classList.toggle("active", x === t));
  $("#tab-episodes").hidden = t.dataset.tab !== "episodes";
  $("#tab-file").hidden = t.dataset.tab !== "file";
  source = null;
  if (t.dataset.tab === "episodes") renderVideos(); else if (uploaded) pickUpload();
  updateReview();
}));

let uploaded = null;
$("#file").addEventListener("change", () => {
  const file = $("#file").files[0];
  if (!file) return;
  const fd = new FormData(); fd.append("file", file);
  const xhr = new XMLHttpRequest();
  $("#upmsg").textContent = "Copying the video into the app…"; uploaded = null; source = null; updateReview();
  xhr.upload.onprogress = e => { $("#upbar").style.width = `${(e.loaded / e.total) * 100}%`; };
  xhr.onload = () => {
    if (xhr.status !== 200) { $("#upmsg").textContent = "Upload failed: " + (JSON.parse(xhr.responseText || "{}").detail || xhr.status); return; }
    uploaded = JSON.parse(xhr.responseText);
    $("#upmsg").textContent = `Ready: ${uploaded.name}`;
    pickUpload();
  };
  xhr.onerror = () => { $("#upmsg").textContent = "Upload failed"; };
  xhr.open("POST", "/api/upload"); xhr.send(fd);
});
$("#filevertical").addEventListener("change", () => uploaded && pickUpload());

function pickUpload() {
  const vertical = $("#filevertical").checked;
  const title = uploaded.name.replace(/\.[^.]+$/, "").replace(/[-_]+/g, " ");
  source = { upload: uploaded.upload, name: uploaded.name, label: uploaded.name };
  const presets = {
    youtube: { title: vertical ? `${title} #Shorts` : title, description: "", tags: [], privacy: "private", short: vertical },
    facebook: { title, description: "", as_reel: vertical },
    instagram: { caption: title }, tiktok: { caption: title },
  };
  for (const name of Object.keys(forms)) { forms[name].set(presets[name]); enable(name, vertical || ["youtube", "facebook"].includes(name)); }
  updateReview();
}

// ---------------------------------------------------------------- review and post
function chosen() { return Object.keys(forms).filter(n => forms[n].on.checked); }

function updateReview() {
  const ok = source && chosen().length && chosen().every(n => forms[n].valid());
  $("#review").disabled = !ok;
}

$("#review").addEventListener("click", () => {
  const sum = $("#summary"); sum.replaceChildren();
  if (source.draft) sum.append(h("p", { class: "error" }, "This episode was built without narration (DRAFT). Are you sure?"));
  sum.append(h("p", {}, h("b", {}, "Video: "), source.label));
  for (const n of chosen()) {
    const lines = forms[n].summary(forms[n].get());
    sum.append(h("div", { class: "sum" }, h("b", {}, LABELS[n]), " · ", lines[0],
      lines.length > 2 ? h("div", {}, lines[1]) : null, h("pre", {}, lines[lines.length - 1] || "(no text)")));
  }
  $("#confirm").showModal();
});
$("#cancel").addEventListener("click", () => $("#confirm").close());

$("#go").addEventListener("click", async () => {
  $("#go").disabled = true;
  try {
    const platforms = chosen();
    const settings = Object.fromEntries(platforms.map(n => [n, forms[n].get()]));
    const src = source.upload ? { upload: source.upload, name: source.name } : { episode: source.episode, file: source.file };
    const { id } = await api("/api/posts", { method: "POST", body: JSON.stringify({ source: src, platforms, settings }) });
    $("#confirm").close(); flash("");
    watch(id);
  } catch (e) { $("#confirm").close(); flash(e.message); }
  finally { $("#go").disabled = false; }
});

let timer = null;
async function watch(id) {
  clearTimeout(timer);
  const box = $("#statusbox"); box.hidden = false;
  const post = await api(`/api/posts/${id}`);
  const jobs = $("#jobs"); jobs.replaceChildren(h("p", { class: "muted" }, post.label));
  for (const j of post.jobs) {
    const state = { queued: "Waiting", running: `${Math.round(j.progress * 100)}%`, done: "✓ Posted", failed: "✗ Failed" }[j.state];
    jobs.append(h("div", { class: `job ${j.state}` },
      h("div", { class: "top" }, h("b", {}, LABELS[j.platform]),
        h("span", { class: "state" }, state)),
      j.state === "running" ? h("div", { class: "bar" }, h("div", { style: `width:${j.progress * 100}%` })) : null,
      h("div", { class: "msg" }, j.state === "done" ? (j.message === "Posted" ? "" : j.message) : j.message),
      j.url ? h("a", { href: j.url, target: "_blank", rel: "noopener" }, "Open post") : null,
      j.state === "failed" ? h("button", { onclick: async () => { await api(`/api/posts/${id}/retry/${j.platform}`, { method: "POST" }); watch(id); } }, "Retry") : null));
  }
  box.scrollIntoView({ behavior: "smooth", block: "nearest" });
  if (post.jobs.some(j => j.state === "queued" || j.state === "running")) timer = setTimeout(() => watch(id), 1500);
  else loadHistory();
}

async function loadHistory() {
  const posts = await api("/api/posts");
  const box = $("#history");
  if (!posts.length) return;
  box.className = ""; box.replaceChildren(...posts.map(p => h("div", { class: "hist" },
    h("a", { href: "#", onclick: (e) => { e.preventDefault(); watch(p.id); } }, new Date(p.created * 1000).toLocaleString()),
    p.label, " · ", p.jobs.map(j => `${LABELS[j.platform]} ${j.state === "done" ? "✓" : j.state === "failed" ? "✗" : "…"}`).join("  "))));
}

// ---------------------------------------------------------------- start
(async () => {
  const q = new URLSearchParams(location.search);
  if (q.get("error")) flash(q.get("error"));
  else if (q.get("connected")) flash(`Connected ${q.get("connected") === "meta" ? "Facebook and Instagram" : LABELS[q.get("connected")]}.`, "ok");
  if (q.toString()) history.replaceState(null, "", "/");
  buildForms();
  await loadStatus();
  await loadEpisodes();
  loadHistory();
})().catch(e => flash(e.message));
