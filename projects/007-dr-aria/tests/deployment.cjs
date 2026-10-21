// Development-only: PLAYWRIGHT_MODULE may point at an existing Playwright install.
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const project = path.resolve(__dirname, '..');
const base = process.env.AVATAR_BASE_URL || 'https://yydshly.github.io/1022_codex_project/007-dr-aria/';

(async () => {
  const browser = await chromium.launch({ headless: true });
  const errors = [];
  try {
    const page = await browser.newPage({ viewport: { width: 1440, height: 1100 } });
    page.setDefaultNavigationTimeout(60000);
    page.on('pageerror', error => errors.push(error.message));
    page.on('console', message => { if (message.type() === 'error') errors.push(message.text()); });
    await page.goto(base, { waitUntil: 'domcontentloaded' });
    await page.locator('#avatar pre').waitFor();
    await page.waitForFunction(() => document.querySelector('#overview img').naturalWidth === 1536);
    assert.deepEqual(await page.locator('.understanding-summary dt').allTextContents(), ['能力', '原理', '效果', '价值']);
    await page.getByRole('button', { name: '放大理解总结图' }).click();
    assert(await page.locator('#overview-dialog').evaluate(dialog => dialog.open));
    await page.keyboard.press('Escape');
    assert.equal(await page.locator('#overview-dialog').evaluate(dialog => dialog.open), false);
    const pendingDownload = page.waitForEvent('download');
    await page.locator('.overview-caption a').click();
    assert.equal((await pendingDownload).suggestedFilename(), 'dr-aria-understanding-summary.png');
    for (const [name, state] of [['等待输入', 'listening'], ['思考', 'thinking'], ['工作中', 'writing'], ['正在回复', 'speaking']]) {
      await page.getByRole('button', { name, exact: true }).click();
      assert.equal(await page.locator('#avatar .lamp').getAttribute('data-state'), state);
    }
    await page.getByRole('button', { name: '停止', exact: true }).click();
    await page.locator('#tour').click();
    await page.waitForFunction(() => document.querySelector('#tour-progress').textContent.includes('演示完成'));
    await page.locator('#reply').fill('你好，线上角色展示已准备好。🙂');
    await page.locator('#stream').click();
    await page.waitForFunction(() => {
      const root = document.querySelector('#avatar').firstElementChild.shadowRoot;
      return root.querySelector('.text').textContent === '你好，线上角色展示已准备好。🙂' && root.querySelector('.lamp').dataset.state === 'listening';
    });
    await page.locator('.developer-details > summary').click();
    await page.locator('#provider').selectOption('codex');
    await page.locator('#provider-demo').click();
    await page.waitForFunction(() => document.querySelector('#events').textContent.includes('"type":"turn.completed"'));
    await page.locator('#provider').selectOption('claude');
    await page.locator('#provider-demo').click();
    await page.waitForFunction(() => document.querySelector('#events').textContent.includes('"type":"result"'));
    await page.locator('.developer-details > summary').click();
    await page.getByRole('button', { name: '停止', exact: true }).click();
    await page.mouse.move(0, 0);
    await page.screenshot({ path: path.join(project, 'assets/deployed-desktop.png'), fullPage: true });
    const responsive = [];
    for (const width of [375, 768, 1440]) {
      await page.setViewportSize({ width, height: 900 });
      const noOverflow = await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth);
      assert(noOverflow); responsive.push({ width, noOverflow });
      if (width === 375) await page.screenshot({ path: path.join(project, 'assets/deployed-mobile.png'), fullPage: true });
    }
    await page.goto(new URL('../', base).href, { waitUntil: 'domcontentloaded' });
    const card = page.locator('article').filter({ hasText: 'dr-aria · 角色效果与表达图鉴' });
    assert.equal(await card.count(), 1);
    assert.equal(await card.locator('img').getAttribute('src'), './007-dr-aria/assets/understanding-summary.png');
    assert.deepEqual(errors, []);
    const date = new Intl.DateTimeFormat('en-CA', { timeZone: 'Asia/Shanghai', year: 'numeric', month: '2-digit', day: '2-digit' }).format(new Date());
    const report = { date, base, status: 'passed', browser: browser.version(),
      checks: ['能力/原理/效果/价值四项摘要', '指定ImageGen引导图加载、放大、Esc关闭、下载', '四状态切换与停止', '一键完整演示', '中文与emoji流式播放', 'Claude/Codex模拟事件样例', '站点总导航及指定封面'],
      responsive, errors, scope: '线上静态展示与模拟事件，未连接真实模型' };
    fs.writeFileSync(path.join(project, 'deployment-ui-verification.json'), JSON.stringify(report, null, 2) + '\n');
    console.log('PASS live summary, guide, state tour, streaming, provider demos, navigation and responsive layout');
  } finally { await browser.close(); }
})().catch(error => { console.error(error); process.exitCode = 1; });
