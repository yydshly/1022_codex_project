import { mountAvatar } from './avatar.js';
import { createClaudeAdapter, createCodexAdapter } from './adapters.js';

const avatar = mountAvatar(document.querySelector('#avatar'), { name: 'ARIA / YOUR AGENT', cps: 30 });
const events = document.querySelector('#events');
let playback = 0;
const delay = ms => new Promise(resolve => setTimeout(resolve, ms));
function log(value) {
  const lines = events.textContent.split('\n').filter(Boolean);
  lines.push(typeof value === 'string' ? value : JSON.stringify(value));
  events.textContent = lines.slice(-45).join('\n'); events.scrollTop = events.scrollHeight;
}
const labels = { listening: '等待输入', thinking: '思考中', writing: '工作中', speaking: '正在回复' };
const descriptions = {
  listening: '等待输入：温和的基础表情，加上眨眼和轻微动作。',
  thinking: '思考中：看向别处，眉形和嘴部有细微变化，衔接回答前的等待。',
  writing: '工作中：目光朝下、笔在移动，表达正在工作或整理。',
  speaking: '正在回复：文字逐字展示，嘴型跟随；开启音效后可听到字符短音。',
};
avatar.on('state', state => {
  document.querySelector('#current-state').textContent = labels[state];
  document.querySelector('#state-description').textContent = descriptions[state];
  document.querySelectorAll('[data-state]').forEach(card => card.setAttribute('aria-pressed', String(card.dataset.state === state)));
});
avatar.on('speakend', text => log(`展示完成：${text}`));
avatar.on('error', text => log(`错误：${text}`));
function cancel() {
  playback++; avatar.stop();
  document.querySelector('#tour-progress').textContent = '依次体验：等待 → 思考 → 工作 → 回复。';
}
function showCharacter() {
  document.querySelector('#states').scrollIntoView({ behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'instant' : 'smooth', block: 'start' });
}
document.querySelectorAll('[data-action]').forEach(button => button.addEventListener('click', () => {
  cancel();
  const event = button.dataset.action === 'speaking'
    ? { type: 'message', text: '你好！我把结果准备好了，我们一起看看吧。' }
    : { type: button.dataset.action };
  log(event); avatar.handle(event);
}));
async function tour() {
  cancel(); showCharacter(); const id = playback;
  const progress = document.querySelector('#tour-progress');
  for (const [type, title] of [['listening', '1 / 4 · 等待输入：先看眨眼、呼吸和轻微动作。'], ['thinking', '2 / 4 · 思考：视线移动，像在斟酌下一句话。'], ['working', '3 / 4 · 工作：低头、动笔，表现正在整理。']]) {
    if (id !== playback) return;
    avatar.handle({ type }); progress.textContent = title; log({ type });
    await delay(type === 'listening' ? 1800 : 1500);
  }
  if (id !== playback) return;
  progress.textContent = '4 / 4 · 回复：文字、嘴型与节奏一起出现。';
  await avatar.say('整理好了，我们一起看看结果吧。');
  if (id === playback) progress.textContent = '演示完成。四类状态，共用一套温和的基础表情。';
}
document.querySelector('#tour').addEventListener('click', tour);
document.querySelector('#expression-tour').addEventListener('click', tour);
document.querySelector('#warm-preview').addEventListener('click', () => { cancel(); showCharacter(); avatar.listen(); });
document.querySelector('#say').addEventListener('click', () => {
  cancel(); showCharacter(); const event = { type: 'message', text: document.querySelector('#reply').value }; log(event); avatar.handle(event);
});
document.querySelector('#stream').addEventListener('click', async () => {
  cancel(); showCharacter(); const id = playback; avatar.handle({ type: 'thinking' }); log({ type: 'thinking' });
  await delay(650);
  const chunks = Array.from(document.querySelector('#reply').value);
  for (let i = 0; i < chunks.length; i += 4) {
    if (id !== playback) return;
    const event = { type: 'delta', text: chunks.slice(i, i + 4).join('') }; log(event); avatar.handle(event); await delay(130);
  }
  if (id === playback) { log({ type: 'done' }); await avatar.handle({ type: 'done' }); }
});
document.querySelector('#provider').addEventListener('change', event => {
  document.querySelector('#provider-note').textContent = event.target.value === 'claude'
    ? 'Claude 样例用文字增量驱动嘴型；所有事件均为模拟。'
    : 'Codex exec --json 样例收到完整 agent_message 后播放；所有事件均为模拟。';
});
document.querySelector('#provider-demo').addEventListener('click', async () => {
  cancel(); showCharacter(); const id = playback;
  const provider = document.querySelector('#provider').value;
  const receive = provider === 'claude' ? createClaudeAdapter(avatar) : createCodexAdapter(avatar);
  const text = document.querySelector('#reply').value;
  const samples = provider === 'claude' ? [
    { type: 'system', subtype: 'init', session_id: 'demo-only' },
    { type: 'stream_event', event: { type: 'message_start', message: { id: 'm1' } } },
    { type: 'stream_event', event: { type: 'content_block_start', index: 0, content_block: { type: 'tool_use', id: 't1', name: 'Read' } } },
    { type: 'stream_event', event: { type: 'message_start', message: { id: 'm2' } } },
    ...Array.from(text).reduce((chunks, c, i) => { if (i % 6 === 0) chunks.push(''); chunks[chunks.length - 1] += c; return chunks; }, []).map(chunk => ({ type: 'stream_event', event: { type: 'content_block_delta', index: 0, delta: { type: 'text_delta', text: chunk } } })),
    { type: 'assistant', message: { id: 'm2', content: [{ type: 'text', text }] } },
    { type: 'result', subtype: 'success', result: text },
  ] : [
    { type: 'thread.started', thread_id: 'demo-only' },
    { type: 'turn.started' },
    { type: 'item.started', item: { id: 'i1', type: 'command_execution', command: '示例工具调用（未执行）', status: 'in_progress' } },
    { type: 'item.completed', item: { id: 'i1', type: 'command_execution', status: 'completed', exit_code: 0, aggregated_output: 'demo' } },
    { type: 'item.completed', item: { id: 'i2', type: 'agent_message', text } },
    { type: 'turn.completed', usage: { input_tokens: 0, output_tokens: 0 } },
  ];
  for (const raw of samples) {
    if (id !== playback) return;
    log(raw); receive(raw); await delay(raw.type === 'stream_event' && raw.event.type === 'content_block_delta' ? 180 : 650);
  }
});
document.querySelector('#voice').addEventListener('click', event => {
  const enabled = event.currentTarget.getAttribute('aria-pressed') !== 'true';
  event.currentTarget.setAttribute('aria-pressed', String(enabled));
  event.currentTarget.textContent = enabled ? '关闭字符音效' : '开启字符音效'; avatar.setMuted(!enabled);
});
document.querySelector('#clear-log').addEventListener('click', () => { events.textContent = ''; });
const overviewDialog = document.querySelector('#overview-dialog');
document.querySelector('#open-overview').addEventListener('click', () => overviewDialog.showModal());
document.querySelector('#close-overview').addEventListener('click', () => overviewDialog.close());
overviewDialog.addEventListener('click', event => { if (event.target === overviewDialog) overviewDialog.close(); });
window.addEventListener('pagehide', () => { playback++; avatar.destroy(); }, { once: true });
log('等待事件。可播放文字，或运行 Claude / Codex 模拟样例。');
