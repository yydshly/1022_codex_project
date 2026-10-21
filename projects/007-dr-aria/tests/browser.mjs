// Runs against the local static demo. Playwright is a development-only test dependency.
import assert from 'node:assert/strict';
import { createRequire } from 'node:module';
import { writeFile } from 'node:fs/promises';
const require = createRequire(import.meta.url);
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const base = process.env.AVATAR_BASE_URL || 'http://127.0.0.1:8047/';
const browser = await chromium.launch({ headless: true });
const checks = [];
const errors = [];
const page = await browser.newPage({ viewport: { width: 1440, height: 1100 } });
page.on('pageerror', error => errors.push(error.message));
page.on('console', message => { if (message.type() === 'error') errors.push(message.text()); });
page.on('requestfailed', request => errors.push(request.url()));
try {
  await page.goto(base);
  await page.locator('#avatar pre').waitFor();
  await page.getByRole('button', { name: '思考', exact: true }).click();
  assert.equal(await page.locator('#avatar .lamp').getAttribute('data-state'), 'thinking');
  await page.getByRole('button', { name: '工作中', exact: true }).click();
  assert.equal(await page.locator('#avatar .lamp').getAttribute('data-state'), 'writing');
  await page.getByRole('button', { name: '停止', exact: true }).click();
  checks.push('UI 状态按钮 → 独立组件');

  assert.equal(await page.locator('.state-card').count(), 4);
  assert(await page.locator('#expression').textContent().then(text => text.includes('尚未内置') && text.includes('根据回复含义自动判断情绪')));
  await page.getByRole('button', { name: '正在回复', exact: true }).click();
  assert.equal(await page.locator('.state-card[data-state=speaking]').getAttribute('aria-pressed'), 'true');
  assert.equal(await page.locator('.state-card[aria-pressed=true]').count(), 1);
  await page.getByRole('button', { name: '停止', exact: true }).click();
  await page.locator('#tour').click();
  await page.waitForFunction(() => document.querySelector('#tour-progress').textContent.includes('2 / 4'));
  await page.getByRole('button', { name: '停止', exact: true }).click();
  await page.waitForTimeout(1700);
  assert.equal(await page.locator('#avatar .lamp').getAttribute('data-state'), 'listening');
  await page.locator('#tour').click();
  await page.waitForFunction(() => document.querySelector('#tour-progress').textContent.includes('演示完成'));
  await page.locator('#warm-preview').click();
  assert.equal(await page.locator('#avatar .lamp').getAttribute('data-state'), 'listening');
  checks.push('四状态卡片、单一表情能力标注、一键展示与中途停止、基础表情回看');

  const lifecycle = await page.evaluate(async () => {
    const { mountAvatar } = await import('./avatar.js');
    const container = document.createElement('div'); document.body.append(container);
    const avatar = mountAvatar(container, { cps: 1000, reducedMotion: true });
    const chars = [];
    avatar.on('speakchar', c => chars.push(c));
    const stream = avatar.stream();
    stream.push('你好\ud83d');
    await new Promise(r => setTimeout(r, 110));
    stream.push('\ude42世界'); stream.end();
    const text = await stream.done;
    const first = avatar.say('这是一段应该被停止的很长文字'.repeat(20), { cps: 1 });
    const queued = avatar.say('这段排队的文字也应该取消', { cps: 1 });
    await new Promise(r => setTimeout(r, 20)); avatar.stop();
    const cancelled = await Promise.race([Promise.all([first, queued]), new Promise(r => setTimeout(() => r('timeout'), 500))]);
    const safe = '<img src=x onerror=alert(1)>🙂';
    await avatar.say(safe, { cps: 1000 });
    const safeResult = { text: avatar.bubbleText.textContent, images: avatar.root.querySelectorAll('img').length };
    const starved = avatar.stream(); starved.push('等');
    const beforeDestroy = avatar.say('排队'); avatar.destroy(); avatar.destroy();
    const disposed = await Promise.race([Promise.all([starved.done, beforeDestroy]), new Promise(r => setTimeout(() => r('timeout'), 500))]);
    const result = { text, chars, cancelled, safeResult, disposed, timers: avatar.timeouts.size + avatar.intervals.size, connected: avatar.host.isConnected };
    container.remove(); return result;
  });
  assert.equal(lifecycle.text, '你好🙂世界');
  assert(lifecycle.chars.includes('🙂'));
  assert.notEqual(lifecycle.cancelled, 'timeout'); assert.equal(lifecycle.cancelled[1], '');
  assert.equal(lifecycle.safeResult.text, '<img src=x onerror=alert(1)>🙂'); assert.equal(lifecycle.safeResult.images, 0);
  assert.notEqual(lifecycle.disposed, 'timeout'); assert.equal(lifecycle.timers, 0); assert.equal(lifecycle.connected, false);
  checks.push('流式分块、跨块 emoji、中文、文本转义、停止当前与排队任务、销毁清理');

  const isolation = await page.evaluate(async () => {
    const { mountAvatar } = await import('./avatar.js');
    const parent = document.createElement('div'); document.body.append(parent);
    const one = mountAvatar(parent, { reducedMotion: true });
    const two = mountAvatar(parent, { reducedMotion: true });
    one.think(); two.write(); const values = [one.state, two.state];
    await two.handle({ type: 'done' });
    if (two.state !== 'listening' || two.bubbleText.textContent !== '') throw new Error('Empty result left a waiting indicator');
    one.destroy(); two.nod(); two.listen(); values.push(two.state, two.host.isConnected);
    two.destroy(); parent.remove(); return values;
  });
  assert.deepEqual(isolation, ['thinking', 'writing', 'listening', true]);
  checks.push('多实例状态隔离与单独卸载');

  const providerResult = await page.evaluate(async () => {
    const { mountAvatar } = await import('./avatar.js');
    const { createClaudeAdapter, createCodexAdapter } = await import('./adapters.js');
    async function run(factory, events) {
      const box = document.createElement('div'); document.body.append(box);
      const avatar = mountAvatar(box, { cps: 1000, reducedMotion: true });
      const spoken = []; avatar.on('speakend', text => spoken.push(text));
      const receive = factory(avatar); for (const event of events) receive(event);
      await avatar.queue; const result = { spoken, text: avatar.bubbleText.textContent };
      avatar.destroy(); box.remove(); return result;
    }
    const text = '这是模型回复';
    return {
      claude: await run(createClaudeAdapter, [
        {type:'stream_event',event:{type:'message_start',message:{id:'m1'}}},
        {type:'stream_event',event:{type:'content_block_delta',index:0,delta:{type:'text_delta',text}}},
        {type:'assistant',message:{id:'m1',content:[{type:'text',text}]}},
        {type:'result',subtype:'success',result:text},
      ]),
      codex: await run(createCodexAdapter, [
        {type:'turn.started'},
        {type:'item.completed',item:{id:'x1',type:'agent_message',text}},
        {type:'item.completed',item:{id:'x1',type:'agent_message',text}},
        {type:'turn.completed'},
      ]),
      claudeToolCycle: await run(createClaudeAdapter, [
        {type:'stream_event',event:{type:'message_start',message:{id:'a'}}},
        {type:'stream_event',event:{type:'content_block_delta',delta:{type:'text_delta',text:'先检查文件'}}},
        {type:'stream_event',event:{type:'message_stop'}},
        {type:'assistant',message:{id:'a',content:[{type:'text',text:'先检查文件'},{type:'tool_use',name:'Read'}]}},
        {type:'user',message:{content:[{type:'tool_result',content:'tool output'}]}},
        {type:'stream_event',event:{type:'message_start',message:{id:'b'}}},
        {type:'stream_event',event:{type:'content_block_delta',delta:{type:'text_delta',text:'检查完成'}}},
        {type:'result',subtype:'success',result:'检查完成'},
      ]),
      codexToolCycle: await run(createCodexAdapter, [
        {type:'turn.started'},
        {type:'item.completed',item:{id:'a',type:'agent_message',text:'先检查文件'}},
        {type:'item.started',item:{id:'t',type:'command_execution',status:'in_progress'}},
        {type:'item.completed',item:{id:'t',type:'command_execution',status:'completed'}},
        {type:'item.completed',item:{id:'b',type:'agent_message',text:'检查完成'}},
        {type:'turn.completed'},
      ]),
    };
  });
  assert.deepEqual(providerResult.claude.spoken, ['这是模型回复']);
  assert.deepEqual(providerResult.codex.spoken, ['这是模型回复']);
  assert.deepEqual(providerResult.claudeToolCycle.spoken, ['先检查文件', '检查完成']);
  assert.deepEqual(providerResult.codexToolCycle.spoken, ['先检查文件', '检查完成']);
  checks.push('Claude 部分流与最终消息去重；Codex 完整消息及重复 item 去重');
  checks.push('CLI 事件快于角色字速时，工具前后多段文字完整播放');

  await page.locator('#reply').fill('你好，我是你的 Agent 角色界面。');
  await page.getByRole('button', { name: '播放完整回复' }).click();
  await page.waitForFunction(() => {
    const root = document.querySelector('#avatar').firstElementChild.shadowRoot;
    return root.querySelector('.text').textContent === '你好，我是你的 Agent 角色界面。' && root.querySelector('.lamp').dataset.state === 'listening';
  });
  await page.mouse.move(0, 0);
  await page.screenshot({ path: new URL('../assets/demo-desktop.png', import.meta.url).pathname.replace(/^\/([A-Za-z]:)/, '$1'), fullPage: true });
  await page.locator('.developer-details > summary').click();
  await page.locator('#provider').selectOption('codex');
  await page.locator('#provider-demo').click();
  await page.waitForFunction(() => document.querySelector('#events').textContent.includes('"type":"turn.completed"'));
  await page.locator('#provider').selectOption('claude');
  await page.locator('#provider-demo').click();
  await page.waitForFunction(() => document.querySelector('#events').textContent.includes('"type":"result"'));
  checks.push('Claude 与 Codex 样例完整按钮流程');

  await page.locator('.developer-details > summary').click();
  await page.setViewportSize({ width: 390, height: 844 });
  await page.screenshot({ path: new URL('../assets/demo-mobile.png', import.meta.url).pathname.replace(/^\/([A-Za-z]:)/, '$1'), fullPage: true });
  assert(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth));
  await page.emulateMedia({ reducedMotion: 'reduce' });
  await page.reload();
  assert(await page.evaluate(() => document.querySelector('#avatar').firstElementChild.shadowRoot.querySelector('.room').classList.contains('reduced')));
  assert.deepEqual(errors, []);
  checks.push('390px 无横向溢出、减少动态效果、无浏览器报错或失败请求');
  await writeFile(new URL('../verification.json', import.meta.url), JSON.stringify({date:'2026-10-21',scope:'角色效果、四状态与情绪表达汇总展示页；本地组件与模拟 CLI 事件，未连接真实模型',base,checks,errors,lifecycle,providerResult}, null, 2) + '\n');
  console.log(`PASS ${checks.length} groups: ${checks.join(' / ')}`);
} finally { await browser.close(); }
