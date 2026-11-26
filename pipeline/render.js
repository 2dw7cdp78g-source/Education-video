// Screenshots HTML scene files to PNG with headless Chromium.
// Usage: node render.js jobs.json
// jobs.json: [{ "html": "/abs/scene.html", "png": "/abs/scene.png", "w": 1920, "h": 1080 }]
const fs = require('fs');
const { chromium } = require('playwright');

(async () => {
  const jobs = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
  const browser = await chromium.launch();
  const contexts = {};
  for (const job of jobs) {
    const key = `${job.w}x${job.h}`;
    if (!contexts[key]) {
      const ctx = await browser.newContext({ viewport: { width: job.w, height: job.h }, deviceScaleFactor: job.scale || 2 });
      contexts[key] = await ctx.newPage();
    }
    const page = contexts[key];
    await page.goto('file://' + job.html);
    await page.evaluate(() => document.fonts.ready);
    await page.screenshot({ path: job.png });
  }
  await browser.close();
})().catch((e) => { console.error(e); process.exit(1); });
