// Renders HTML scenes with headless Chromium.
// Usage: node render.js jobs.json
// Still job:    { "html": "/abs/a.html", "png": "/abs/a.png", "w": 1920, "h": 1080, "scale": 2 }
// Animated job: { "html": "/abs/a.html", "mp4": "/abs/a.mp4", "w": 1920, "h": 1080, "dur": 4.2, "fps": 25 }
// Animated jobs freeze every CSS animation and step them frame by frame, so motion is
// perfectly smooth and deterministic no matter how slow the machine is.
const fs = require('fs');
const { spawn } = require('child_process');
const { chromium } = require('playwright');

async function encode(page, job) {
  const frames = Math.max(1, Math.round(job.dur * job.fps));
  const ff = spawn('ffmpeg', ['-v', 'error', '-y', '-f', 'image2pipe', '-c:v', 'mjpeg', '-framerate', String(job.fps), '-i', '-',
    '-frames:v', String(frames), '-c:v', 'libx264', '-preset', job.preset || 'veryfast', '-crf', '17', '-pix_fmt', 'yuv420p',
    '-r', String(job.fps), job.mp4], { stdio: ['pipe', 'inherit', 'inherit'] });
  const done = new Promise((res, rej) => ff.on('close', (c) => (c ? rej(new Error('ffmpeg ' + c)) : res())));
  for (let i = 0; i < frames; i++) {
    const t = (i / job.fps) * 1000;
    await page.evaluate((t) => {
      for (const a of document.getAnimations()) { a.pause(); a.currentTime = t; }
    }, t);
    const buf = await page.screenshot({ type: 'jpeg', quality: 92 });
    if (!ff.stdin.write(buf)) await new Promise((r) => ff.stdin.once('drain', r));
  }
  ff.stdin.end();
  await done;
}

(async () => {
  const jobs = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
  const browser = await chromium.launch();
  const pages = {};
  for (const job of jobs) {
    const scale = job.mp4 ? 1 : job.scale || 2;
    const key = `${job.w}x${job.h}@${scale}`;
    if (!pages[key]) {
      const ctx = await browser.newContext({ viewport: { width: job.w, height: job.h }, deviceScaleFactor: scale });
      pages[key] = await ctx.newPage();
    }
    const page = pages[key];
    await page.goto('file://' + job.html);
    await page.evaluate(() => document.fonts.ready);
    await page.evaluate(() => Promise.all([...document.images].map((i) => i.decode().catch(() => {}))));
    if (job.mp4) {
      await encode(page, job);
      process.stdout.write('.');
    } else {
      await page.screenshot({ path: job.png });
    }
  }
  await browser.close();
})().catch((e) => { console.error(e); process.exit(1); });
