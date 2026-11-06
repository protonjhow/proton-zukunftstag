// Checks the advertiser facts page. Read-only: safe to run at any time, even mid-session.
// Usage: node check-facts.js   (stack must be running)
const { chromium } = require('playwright-core');
const BASE = process.env.BASE || 'http://127.0.0.1:8100';
const OUT = process.env.OUT || require('os').tmpdir();
const CHROME = process.env.CHROME || '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const results = [];
const ok = (cond, msg) => results.push((cond ? 'PASS ' : 'FAIL ') + msg);

(async () => {
  const browser = await chromium.launch({ executablePath: CHROME, headless: true });
  try {
    const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
    const problems = [];
    page.on('pageerror', e => problems.push('pageerror: ' + e.message));
    page.on('console', m => m.type() === 'error' && problems.push('console: ' + m.text()));
    page.on('response', r => r.status() >= 400 && problems.push(`${r.status()} ${r.url()}`));

    await page.goto(BASE + '/screen');
    await page.click('#facts-link');
    await page.waitForURL('**/facts');
    await page.waitForSelector('.box');
    ok(true, 'the 💰 on the big screen opens /facts');

    const fit = await page.evaluate(() => ({
      page: document.scrollingElement.scrollHeight - innerHeight,
      boxes: [...document.querySelectorAll('.box, .sources')].map(b => b.scrollHeight - b.clientHeight),
    }));
    ok(fit.page <= 0 && fit.boxes.every(px => px <= 1), `fits one 1080p screen, nothing cut off (page ${fit.page}px, boxes ${fit.boxes.join(',')})`);
    await page.screenshot({ path: `${OUT}/s2-facts-tv-${Date.now()}.png` });

    await page.emulateMedia({ media: 'print' });
    const pdf = await page.pdf({ format: 'A4', preferCSSPageSize: true, path: `${OUT}/s2-facts.pdf` });
    const pages = (pdf.toString('latin1').match(/\/Type\s*\/Page[^s]/g) || []).length;
    ok(pages === 1, `prints on 1 A4 page (${pages})`);
    ok(!(await page.isVisible('#back')), 'back arrow is not printed');
    await page.emulateMedia({ media: 'screen' });

    await page.click('#back');
    await page.waitForURL('**/screen');
    ok(true, 'the ← goes back to the big screen');
    ok(problems.length === 0, `no errors ${problems.join(' | ')}`);
  } finally {
    await browser.close();
    console.log(results.join('\n'));
    process.exitCode = results.some(r => r.startsWith('FAIL')) ? 1 : 0;
  }
})();
