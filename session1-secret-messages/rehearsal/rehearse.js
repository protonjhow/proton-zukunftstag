const { chromium } = require('playwright-core');
const { execSync } = require('child_process');
const CHAT = process.env.CHAT || 'http://127.0.0.1:8000';
const EVE = process.env.EVE || 'http://127.0.0.1:8001';
const OUT = process.env.OUT || require('os').tmpdir();
const STACK = require('path').resolve(__dirname, '..');
const results = [];
const ok = (cond, msg) => results.push((cond ? 'PASS ' : 'FAIL ') + msg);

async function newPage(browser, opts) {
  const ctx = await browser.newContext(opts);
  const page = await ctx.newPage();
  const problems = [];
  page.on('pageerror', e => problems.push('pageerror: ' + e.message));
  page.on('console', m => m.type() === 'error' && problems.push('console: ' + m.text()));
  page.on('response', r => r.status() >= 400 && !r.url().endsWith('/favicon.ico') && problems.push(`${r.status()} ${r.url()}`));
  return { ctx, page, problems };
}
const setDial = (page, v) => page.evaluate(v => { const d = document.getElementById('dial'); d.value = v; d.dispatchEvent(new Event('input')); }, v);
const send = async (page, text) => { await page.fill('#text', text); await page.press('#text', 'Enter'); };
const lastTheirs = page => page.locator('#messages li.theirs').last();
const topCard = page => page.locator('#sightings li').first();

(async () => {
  const browser = await chromium.launch({ executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', headless: true });
  try {
    const laptop = { viewport: { width: 1440, height: 900 } };
    const alice = await newPage(browser, laptop);
    const bob = await newPage(browser, laptop);
    const tv = await newPage(browser, { viewport: { width: 1920, height: 1080 } });
    await tv.page.goto(EVE + '/');
    await alice.page.goto(CHAT + '/?me=Alice');
    await bob.page.goto(CHAT + '/?me=Bob');
    await alice.page.waitForTimeout(800);

    // 1. Alice sends at setting 7, Eve cracks it
    await setDial(alice.page, 7);
    ok((await alice.page.textContent('#dial-map')) === 'A → H', 'dial shows A → H at setting 7');
    await send(alice.page, 'MEET ME AT THE PARK');
    await tv.page.waitForFunction(() => { const li = document.querySelector('#sightings li'); return li && li.classList.contains('cracked') && !li.classList.contains('spinning'); }, null, { timeout: 5000 });
    const card1 = await topCard(tv.page).innerText();
    ok(card1.includes('Wheel setting: 7') && card1.includes('MEET ME AT THE PARK') && card1.includes('From: Alice'), 'Eve cracks setting 7: ' + card1.replace(/\n/g, ' / '));
    await tv.page.screenshot({ path: `${OUT}/tv-cracked.png` });

    // 2. Bob at wrong setting sees gibberish, then fixes it live
    await bob.page.waitForSelector('#messages li.theirs');
    const wrong = await lastTheirs(bob.page).locator('.text').innerText();
    ok(wrong !== 'MEET ME AT THE PARK', `Bob at setting 3 sees gibberish: ${wrong}`);
    await setDial(bob.page, 7);
    ok((await lastTheirs(bob.page).locator('.text').innerText()) === 'MEET ME AT THE PARK', 'Bob turns dial to 7 and reads it live');

    // 3. VPN on: Bob reads, Eve can't
    await alice.page.click('label.vpn');
    ok((await alice.page.textContent('#vpn-label')).includes('VPN on'), 'VPN switch turns on');
    await send(alice.page, 'SECRET PLAN AT NOON');
    await bob.page.waitForFunction(() => document.querySelectorAll('#messages li.theirs').length === 2);
    const vpnMsg = await lastTheirs(bob.page).innerText();
    ok(vpnMsg.includes('SECRET PLAN AT NOON') && vpnMsg.includes('VPN'), 'Bob reads VPN message with lock badge');
    await tv.page.waitForSelector('#sightings li.locked', { timeout: 5000 });
    await tv.page.waitForTimeout(1500);
    const card2 = await topCard(tv.page).innerText();
    ok(card2.includes('From: ???') && card2.includes('vault:v1:') && card2.includes("can't read this"), 'Eve is blind with VPN on: ' + card2.replace(/\n/g, ' / '));
    await tv.page.screenshot({ path: `${OUT}/tv-locked.png` });
    await alice.page.screenshot({ path: `${OUT}/alice.png` });
    await bob.page.screenshot({ path: `${OUT}/bob.png` });

    // 4. Vault down: Alice gets the friendly error, nothing goes out
    execSync('docker compose stop vault', { cwd: STACK, stdio: 'ignore' });
    const before = await tv.page.locator('#sightings li').count();
    await send(alice.page, 'THIS SHOULD NOT LEAK');
    await send(alice.page, 'NOR THIS ONE');
    await alice.page.waitForFunction(() => [...document.querySelectorAll('#messages li.mine')].slice(-2).every(li => li.innerText.includes('not sent')), null, { timeout: 10000 });
    ok((await alice.page.textContent('#status')).includes("VPN isn't working"), 'Vault down: Alice sees VPN error');
    ok(true, 'Vault down: both unsent messages marked not sent');
    await tv.page.waitForTimeout(1000);
    ok((await tv.page.locator('#sightings li').count()) === before, 'Vault down: nothing reached Eve');
    await alice.page.screenshot({ path: `${OUT}/alice-vault-down.png` });
    execSync('docker compose start vault', { cwd: STACK, stdio: 'ignore' });
    execSync('until [ "$(docker compose ps vault --format {{.Health}})" = healthy ]; do sleep 1; done', { cwd: STACK, shell: '/bin/sh' });
    await send(alice.page, 'BACK ONLINE');
    await bob.page.waitForFunction(() => document.querySelectorAll('#messages li.theirs').length === 3, null, { timeout: 8000 });
    ok((await lastTheirs(bob.page).locator('.text').innerText()) === 'BACK ONLINE', 'Vault restarted alone: VPN works again');

    // 5. TV reload keeps history; TV fits one screen
    await tv.page.reload();
    await tv.page.waitForSelector('#sightings li.locked');
    ok((await tv.page.locator('#sightings li').count()) >= 3, 'TV reload keeps history');
    const fit = await tv.page.evaluate(() => document.documentElement.scrollWidth - innerWidth);
    ok(fit <= 0, `TV no horizontal overflow (${fit}px)`);

    // 6. Two laptops opened without ?me= still see each other
    const g1 = await newPage(browser, laptop), g2 = await newPage(browser, laptop);
    await g1.page.goto(CHAT + '/'); await g2.page.goto(CHAT + '/');
    await g1.page.waitForTimeout(800);
    await send(g1.page, 'HELLO GUEST');
    await g2.page.waitForSelector('#messages li.theirs', { timeout: 5000 }).catch(() => {});
    ok((await g2.page.locator('#messages li.theirs').count()) === 1, 'no ?me=: guests see each other (' + await g1.page.textContent('#me') + ' / ' + await g2.page.textContent('#me') + ')');

    for (const [n, p] of [['alice', alice], ['bob', bob], ['tv', tv], ['guest1', g1], ['guest2', g2]]) ok(p.problems.length === 0, `${n}: no errors ${p.problems.join(' | ')}`);
  } finally {
    await browser.close();
    console.log(results.join('\n'));
  }
})();
