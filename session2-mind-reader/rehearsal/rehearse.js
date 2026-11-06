// Full run of session 2 in headless Chrome: two kids take the quiz, the big screen
// counts them, cards print, delete ceremony wipes everything.
// Usage: npm i --no-save playwright-core && node rehearse.js   (stack must be running)
const { chromium, devices } = require('playwright-core');
const BASE = process.env.BASE || 'http://127.0.0.1:8100';
const OUT = process.env.OUT || require('os').tmpdir();
const CHROME = process.env.CHROME || '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const IPAD_DESKTOP_UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Safari/605.1.15';
const results = [];
const ok = (cond, msg) => results.push((cond ? 'PASS ' : 'FAIL ') + msg);

async function newPage(browser, opts) {
  const ctx = await browser.newContext(opts);
  const page = await ctx.newPage();
  const problems = [];
  page.on('pageerror', e => problems.push('pageerror: ' + e.message));
  page.on('console', m => m.type() === 'error' && !m.text().includes('409') && problems.push('console: ' + m.text()));
  page.on('response', r => r.status() >= 400 && r.status() !== 409 && problems.push(`${r.status()} ${r.url()}`));
  return { ctx, page, problems };
}

async function takeQuiz(page, avatarIndex, { changeTwice = false } = {}) {
  await page.goto(BASE + '/');
  await page.locator('.avatar').nth(avatarIndex).click();
  for (let i = 0; i < 10; i++) {
    const opts = page.locator('.option');
    if (changeTwice && i === 1) {
      await opts.nth(0).click(); await page.waitForTimeout(150);
      await opts.nth(1).click(); await page.waitForTimeout(150);
    }
    await opts.nth(i % 4).click();
    await page.locator('button.primary').click();
  }
}

async function finishReveal(page) {
  await page.waitForSelector('.guess');
  for (const thumbs of await page.locator('.guess .thumbs').all()) await thumbs.locator('.thumb').first().click();
  const score = await page.textContent('.score');
  await page.click('text=But wait');
  while (await page.locator('text=Show me more').isVisible()) await page.click('text=Show me more');
  return { score, facts: await page.locator('.fact').allInnerTexts() };
}

(async () => {
  const browser = await chromium.launch({ executablePath: CHROME, headless: true });
  try {
    await fetch(BASE + '/api/delete', { method: 'POST' });
    const ipad = await newPage(browser, { ...devices['iPad (gen 7)'], userAgent: IPAD_DESKTOP_UA });
    const laptop = await newPage(browser, { viewport: { width: 1440, height: 900 } });
    const late = await newPage(browser, { viewport: { width: 1440, height: 900 } });
    const screen = await newPage(browser, { viewport: { width: 1920, height: 1080 } });
    await screen.page.goto(BASE + '/screen');

    // two kids take the quiz; the iPad kid changes question 2 twice
    await takeQuiz(ipad.page, 0, { changeTwice: true });
    const a = await finishReveal(ipad.page);
    ok(a.score === '5 out of 5 from silly questions!', `score line: ${a.score}`);
    ok(a.facts.length === 5, `5 noticed lines on iPad`);
    ok(a.facts[0].includes('“Pick a snack” 2 times'), `noticed the changes: ${a.facts[0]}`);
    ok(a.facts[3] === "You're using an iPad", `iPad in desktop mode detected: ${a.facts[3]}`);
    await ipad.page.waitForTimeout(600);
    await ipad.page.screenshot({ path: `${OUT}/s2-ipad-noticed.png`, fullPage: true });

    // a second kid opens the page before the first finishes, then picks the same animal
    await late.page.goto(BASE + '/');
    await takeQuiz(laptop.page, 1);
    const b = await finishReveal(laptop.page);
    ok(b.facts[0] === 'You never changed an answer. Very decisive!', `decisive kid: ${b.facts[0]}`);
    await late.page.locator('.avatar').nth(1).click();
    for (let i = 0; i < 10; i++) { await late.page.locator('.option').first().click(); await late.page.locator('button.primary').click(); }
    await late.page.waitForSelector('.warn');
    ok((await late.page.textContent('.warn')).includes('took that animal'), 'same avatar: told to pick another');
    ok(await late.page.locator('.avatar').nth(1).isDisabled(), 'taken avatar greyed out');
    await late.page.locator('.avatar').nth(2).click();
    const kept = await late.page.waitForSelector('.guess', { timeout: 5000 }).then(() => true, () => false);
    ok(kept, 'after picking another animal her answers are kept (straight to results)');

    // big screen and cards
    await screen.page.waitForFunction(() => document.querySelectorAll('.tile').length === 3, null, { timeout: 5000 });
    ok((await screen.page.textContent('#count')) === '3 profiles stored on this computer', 'screen counts 3');
    await screen.page.screenshot({ path: `${OUT}/s2-screen.png` });
    const cards = await newPage(browser, {});
    await cards.page.goto(BASE + '/cards');
    await cards.page.waitForSelector('.card');
    ok((await cards.page.locator('.card').count()) === 3, '3 data cards');
    await cards.page.emulateMedia({ media: 'print' });
    const pdf = await cards.page.pdf({ format: 'A4', preferCSSPageSize: true, path: `${OUT}/s2-cards.pdf` });
    const pages = (pdf.toString('latin1').match(/\/Type\s*\/Page[^s]/g) || []).length;
    ok(pages === 1, `cards fit 1 A4 page (${pages})`);

    // worst-case card content (two-line title, long fields) must stay inside the card
    const worst = { avatar: 'bee', emoji: '🐝', title: 'The High-Flying Friend-Maker', interests: ['A board game', 'Crafts and DIY', 'Chocolate'],
      notify: 'Early in the morning, around 7:00', ad: 'A Minecraft skin pack (and a chocolate advert)', stars: 5 };
    const fit = await newPage(browser, {});
    await fit.page.route('**/api/profiles', r => r.fulfill({ json: { count: 2, profiles: [{ card: { ...worst, title: 'The Wild Joker' } }, { card: worst }] } }));
    await fit.page.goto(BASE + '/cards');
    await fit.page.waitForSelector('.card');
    for (const media of ['screen', 'print']) {
      await fit.page.emulateMedia({ media });
      const spill = await fit.page.evaluate(() => [...document.querySelectorAll('.card')].map(c => {
        const inner = c.getBoundingClientRect().bottom - parseFloat(getComputedStyle(c).borderBottomWidth);
        return Math.round(Math.max(0, ...[...c.children].map(ch => ch.getBoundingClientRect().bottom)) - inner);
      }));
      ok(spill.every(px => px <= 0), `${media}: card content stays inside the border (overflow px: ${spill.join(', ')})`);
    }
    await fit.page.emulateMedia({ media: 'print' });
    await fit.page.screenshot({ path: `${OUT}/s2-cards-worst-${Date.now()}.png` });
    await fit.ctx.close();

    // delete ceremony
    await screen.page.click('#delete');
    ok((await screen.page.textContent('#delete')).includes('Tap again'), 'delete asks to confirm');
    await screen.page.click('#delete');
    await screen.page.waitForFunction(() => document.getElementById('count').textContent.startsWith('0 profiles'), null, { timeout: 8000 });
    ok((await screen.page.textContent('#count')) === '0 profiles. Nothing about you is stored any more.', 'delete ceremony ends at 0');
    await screen.page.waitForTimeout(2500);
    ok((await screen.page.textContent('#count')).startsWith('0 profiles. Nothing'), 'message survives the next poll');
    await screen.page.screenshot({ path: `${OUT}/s2-screen-deleted.png` });
    const profiles = await (await fetch(BASE + '/api/profiles')).json();
    ok(profiles.count === 0 && profiles.profiles.length === 0, 'API empty after delete');
    await cards.page.reload();
    await cards.page.waitForSelector('.none');
    ok((await cards.page.textContent('.none')).includes('deleted'), 'cards page shows nothing after delete');

    for (const [n, p] of [['ipad', ipad], ['laptop', laptop], ['late', late], ['screen', screen], ['cards', cards]]) {
      ok(p.problems.length === 0, `${n}: no errors ${p.problems.join(' | ')}`);
    }
  } finally {
    await browser.close();
    console.log(results.join('\n'));
    process.exitCode = results.some(r => r.startsWith('FAIL')) ? 1 : 0;
  }
})();
