// Animation and lifecycle wrapper; upstream rendering/art remain under their MIT license.
import { AriaRenderer, PALETTE } from './upstream-renderer.js';

const CSS = `
:host{display:block;color:#c8d4de;font:14px/1.5 system-ui,sans-serif;contain:content}
*{box-sizing:border-box}
.room{position:relative;aspect-ratio:800/700;overflow:hidden;border:1px solid #293b46;border-radius:18px;background:radial-gradient(ellipse at 50% 35%,#19272a,#0b121a 75%)}
.art{position:absolute;inset:0;animation:breathe 6.4s ease-in-out infinite}
pre{position:absolute;left:50%;top:50%;font:15px/1.06 'Cascadia Mono','DejaVu Sans Mono',Consolas,monospace;white-space:pre;margin:0;font-variant-ligatures:none;transform:translate(-50%,-50%) scale(var(--scale,.7));transform-origin:center}
i{font-style:normal}
.lamp{position:absolute;right:16px;top:13px;display:flex;align-items:center;gap:7px;z-index:3;color:#9bb8bd;font-size:12px}
.lamp::before{content:'';width:7px;height:7px;border-radius:50%;background:#83d4c2}
.lamp[data-state=thinking]::before{background:#e2bb6f}
.lamp[data-state=writing]::before{background:#c8a1e9}
.lamp[data-state=speaking]::before{background:#ee9575}
.name{position:absolute;bottom:12px;left:16px;font-size:11px;letter-spacing:.12em;color:#92a4b4}
.bubble{position:absolute;top:42px;left:6%;right:6%;max-height:31%;overflow:auto;padding:12px 15px;border:1px solid #46616c;border-radius:13px;background:#12202bf5;font-size:clamp(12px,1.7vw,15px);opacity:0;z-index:2;overflow-wrap:anywhere;white-space:pre-wrap;transition:opacity .2s}
.bubble.show{opacity:1}
.caret{color:#81d3c2}
.reduced .art{animation:none}
@keyframes breathe{50%{transform:translateY(-2px)}}
${PALETTE}`;
const LABELS = { listening: '等待输入', thinking: '思考中', writing: '工作中', speaking: '正在回复' };
const isCJK = c => /[\u3400-\u9fff]/u.test(c);

class Avatar extends AriaRenderer {
  constructor(container, options = {}) {
    super();
    if (!(container instanceof HTMLElement)) throw new TypeError('mountAvatar requires an HTMLElement');
    this.host = document.createElement('div');
    this.root = this.host.attachShadow({ mode: 'open' });
    this.root.innerHTML = `<style>${CSS}</style><section class="room"><div class="art"><pre aria-hidden="true"></pre></div><div class="lamp" role="status"></div><div class="bubble"><span class="text"></span><span class="caret" aria-hidden="true">▌</span></div><div class="name"></div></section>`;
    container.append(this.host);
    this.room = this.root.querySelector('.room');
    this.el = this.root.querySelector('pre');
    this.bubble = this.root.querySelector('.bubble');
    this.bubbleText = this.root.querySelector('.text');
    this.caret = this.root.querySelector('.caret');
    this.lamp = this.root.querySelector('.lamp');
    this.root.querySelector('.name').textContent = options.name ?? 'ARIA · AGENT AVATAR';
    this.opts = { cps: 30, ...options };
    this.mood = 'warm'; this.state = 'listening';
    this.tick = 0; this.headShift = 0;
    this.eyes = 'open'; this.brow = 'warm'; this.mouth = 'smile';
    this.destroyed = false; this.generation = 0; this.listeners = new Map();
    this.timeouts = new Set(); this.intervals = new Set(); this.jobs = new Set();
    this.queue = Promise.resolve(); this.active = null; this.currentStream = null;
    this.media = matchMedia('(prefers-reduced-motion: reduce)');
    this.reducedMotion = options.reducedMotion ?? this.media.matches;
    this.room.classList.toggle('reduced', this.reducedMotion);
    this.voice = createVoice(options.muted ?? true);
    this.wakeVoice = () => this.voice.wake();
    this.host.addEventListener('pointerdown', this.wakeVoice);
    this.host.addEventListener('keydown', this.wakeVoice);
    this.observer = new ResizeObserver(([entry]) => {
      this.room.style.setProperty('--scale', Math.min(entry.contentRect.width / 800, entry.contentRect.height / 700));
    });
    this.observer.observe(this.room);
    this._every(() => { if (!this.reducedMotion) { this.tick++; this.render(); } }, 150);
    const blink = () => {
      if (!this.reducedMotion && !this.musing && this.state !== 'speaking') {
        this.eyes = 'shut'; this.render();
        this._later(() => { this.eyes = 'open'; this.render(); }, 150);
      }
      this._later(blink, 2400 + Math.random() * 3600);
    };
    this._later(blink, 1700);
    this._every(() => { if (this.state === 'listening' && !this.reducedMotion) this.nod(); }, 6400);
    this._every(() => {
      if (this.state !== 'listening' || this.reducedMotion) return;
      this.eyes = Math.random() < .5 ? 'left' : 'right'; this.render();
      this._later(() => { if (this.state === 'listening') { this.eyes = 'open'; this.render(); } }, 900);
    }, 7600);
    this._state('listening'); this.render();
  }
  _later(fn, delay) {
    if (this.destroyed) return null;
    const id = setTimeout(() => { this.timeouts.delete(id); if (!this.destroyed) fn(); }, delay);
    this.timeouts.add(id); return id;
  }
  _every(fn, delay) {
    const id = setInterval(() => { if (!this.destroyed) fn(); }, delay);
    this.intervals.add(id); return id;
  }
  _clear(id) { clearTimeout(id); this.timeouts.delete(id); }
  on(name, fn) {
    if (this.destroyed) return () => {};
    if (!this.listeners.has(name)) this.listeners.set(name, new Set());
    this.listeners.get(name).add(fn);
    return () => this.listeners.get(name)?.delete(fn);
  }
  emit(name, value) { for (const fn of this.listeners.get(name) ?? []) fn(value); }
  _state(state) {
    this.state = state;
    this.lamp.dataset.state = state; this.lamp.textContent = LABELS[state] ?? state;
    this.emit('state', state);
  }
  _cancelMuse() { clearInterval(this.musing); this.intervals.delete(this.musing); this.musing = null; }
  _enqueue(source, options = {}) {
    if (this.destroyed) return Promise.resolve('');
    let resolve;
    const result = new Promise(r => { resolve = r; });
    const job = { source, options, resolve, result, settled: false, said: '' };
    this.jobs.add(job);
    this.queue = this.queue.then(() => job.settled ? undefined : this._drain(job));
    return result;
  }
  say(text, options) { return this._enqueue({ buf: String(text), ended: true }, options); }
  stream(options) {
    const source = { buf: '', ended: false };
    const done = this._enqueue(source, options);
    let closed = this.destroyed;
    return {
      push: text => { if (!closed && !source.cancelled && !this.destroyed) source.buf += String(text ?? ''); },
      end: () => { source.ended = true; closed = true; },
      done,
    };
  }
  _finish(job, cancelled = false) {
    if (job.settled) return;
    job.source.cancelled = cancelled;
    job.settled = true; this._clear(job.timer); this.jobs.delete(job);
    if (this.active === job) {
      this.active = null; this.mouth = 'smile'; this.eyes = 'open'; this.brow = 'warm';
      this.caret.hidden = true;
      if (!this.destroyed) {
        this._state('listening'); this.render();
        this.emit(cancelled ? 'cancel' : 'speakend', job.said);
        if (!cancelled) this.hideTimer = this._later(() => this.bubble.classList.remove('show'), 3600);
      }
    }
    job.resolve(job.said);
  }
  _drain(job) {
    this._cancelMuse(); this._clear(this.hideTimer);
    this.active = job; this._state('speaking');
    this.bubbleText.textContent = ''; this.bubble.classList.add('show'); this.caret.hidden = false;
    this.emit('speakstart', job.source.buf);
    const cps = Math.max(1, Math.min(1000, Number(job.options.cps ?? this.opts.cps) || 30));
    const step = () => {
      if (job.settled || this.destroyed) return;
      const src = job.source;
      if (!src.buf) {
        if (src.ended) return this._finish(job);
        this.mouth = 'smile'; this.render(); job.timer = this._later(step, 40); return;
      }
      // Preserve a surrogate pair even when it spans two provider chunks.
      const first = src.buf.charCodeAt(0);
      if (src.buf.length === 1 && first >= 0xd800 && first <= 0xdbff && !src.ended) {
        job.timer = this._later(step, 40); return;
      }
      const c = String.fromCodePoint(src.buf.codePointAt(0));
      src.buf = src.buf.slice(c.length); job.said += c;
      this.bubbleText.textContent = job.said;
      this.mouth = this.reducedMotion ? 'smile' : viseme(c, job.said.length);
      this.brow = 'warm'; this.render();
      this.voice.blip(c); this.emit('speakchar', c);
      const pause = /[，,；;：:]/u.test(c) ? 170 : /[。.!！?？]/u.test(c) ? 330 : 0;
      job.timer = this._later(step, 1000 / cps + pause);
    };
    step(); return job.result;
  }
  _muse(state, interrupt = true) {
    if (this.destroyed) return this;
    if (interrupt) this.stop();
    this._cancelMuse(); this._clear(this.hideTimer); this.caret.hidden = true;
    this._state(state); this.brow = 'thoughtful';
    this.bubble.classList.add('show'); let i = 0;
    const beat = () => {
      this.bubbleText.textContent = ['·', '· ·', '· · ·'][i % 3];
      if (!this.reducedMotion) {
        this.eyes = (state === 'writing' ? ['down', 'down', 'left'] : ['right', 'up', 'shut'])[i % 3];
        this.mouth = ['mm', 'small', 'eh'][i % 3];
      }
      i++; this.render();
    };
    beat(); if (!this.reducedMotion) this.musing = this._every(beat, 300);
    return this;
  }
  think() { return this._muse('thinking'); }
  write() { return this._muse('writing'); }
  listen() { return this.stop(); }
  idle() { return this.stop(); }
  nod() {
    if (!this.destroyed && !this.reducedMotion) [1, 1, 0, -1, -1, 0].forEach((v, i) => this._later(() => { this.headShift = v; this.render(); }, i * 110));
    return this;
  }
  stop() {
    this.generation++;
    this.currentStream = null;
    for (const job of [...this.jobs]) this._finish(job, true);
    this.queue = Promise.resolve(); this._cancelMuse(); this._clear(this.hideTimer);
    this.headShift = 0; this.mouth = 'smile'; this.eyes = 'open'; this.brow = 'warm';
    this.bubble.classList.remove('show'); this.caret.hidden = true;
    if (!this.destroyed) { this._state('listening'); this.render(); }
    return this;
  }
  handle(event) {
    if (this.destroyed) return;
    switch (event.type) {
      case 'thinking':
      case 'working': {
        // Provider events may arrive faster than the character can speak.
        // Finish prior text before showing the next tool/thinking state.
        if (this.currentStream) { this.currentStream.end(); this.currentStream = null; }
        const generation = this.generation;
        const apply = () => {
          if (!this.destroyed && generation === this.generation) this._muse(event.type === 'working' ? 'writing' : 'thinking', false);
        };
        if (this.jobs.size) { this.queue = this.queue.then(apply); return this.queue; }
        apply(); return;
      }
      case 'listening': return this.listen();
      case 'nod': return this.nod();
      case 'stop': return this.stop();
      case 'error': this.stop(); this.emit('error', String(event.text ?? 'Agent 执行失败')); return;
      case 'message': return this.say(event.text ?? '');
      case 'delta':
        this.currentStream ??= this.stream();
        this.currentStream.push(event.text ?? ''); return;
      case 'done': {
        const stream = this.currentStream; this.currentStream = null;
        if (stream) { stream.end(); return stream.done; }
        const generation = this.generation;
        this.queue = this.queue.then(() => {
          if (!this.destroyed && generation === this.generation) {
            if (this.state === 'thinking' || this.state === 'writing') {
              this.bubbleText.textContent = ''; this.bubble.classList.remove('show');
            }
            this._cancelMuse(); this.eyes = 'open'; this.mouth = 'smile'; this._state('listening'); this.render();
          }
        });
        return this.queue;
      }
      default: throw new TypeError(`Unknown avatar event: ${event.type}`);
    }
  }
  setMuted(value) { this.voice.muted = Boolean(value); if (!value) this.voice.wake(); }
  destroy() {
    if (this.destroyed) return;
    this.stop(); this.destroyed = true;
    this.observer.disconnect();
    this.host.removeEventListener('pointerdown', this.wakeVoice);
    this.host.removeEventListener('keydown', this.wakeVoice);
    for (const id of this.timeouts) clearTimeout(id);
    for (const id of this.intervals) clearInterval(id);
    this.timeouts.clear(); this.intervals.clear(); this.listeners.clear();
    this.voice.destroy(); this.host.remove();
  }
}

function viseme(char, index) {
  const c = char.toLowerCase();
  if (/[\s，。！？；：、,.!?;:—-]/u.test(c)) return 'smile';
  if (isCJK(c)) return ['ah', 'ee', 'oo', 'small'][index % 4];
  if ('a'.includes(c)) return 'aa';
  if ('ou'.includes(c)) return 'oo';
  if ('eiy'.includes(c)) return 'ee';
  if ('mbp'.includes(c)) return 'mm';
  if ('fvw'.includes(c)) return 'small';
  return 'ah';
}

function createVoice(muted) {
  let ctx, master, last = -1, dead = false;
  return {
    muted,
    wake() {
      if (dead || this.muted) return;
      const Audio = window.AudioContext || window.webkitAudioContext;
      if (!Audio) return;
      try {
        if (!ctx) { ctx = new Audio(); master = ctx.createGain(); master.gain.value = .10; master.connect(ctx.destination); }
        if (ctx.state === 'suspended') ctx.resume().catch(() => {});
      } catch { /* Text and animation continue when audio is unavailable. */ }
    },
    blip(char) {
      if (this.muted || !ctx || ctx.state !== 'running' || !/[a-z0-9\u3400-\u9fff]/iu.test(char)) return;
      const now = ctx.currentTime;
      if (now - last < .025) return;
      last = now;
      const frequency = 420 * 2 ** ((char.codePointAt(0) % 7 - 3) / 12);
      const gain = ctx.createGain(), filter = ctx.createBiquadFilter();
      filter.type = 'lowpass'; filter.frequency.value = 1700; filter.connect(gain); gain.connect(master);
      gain.gain.setValueAtTime(.0001, now); gain.gain.exponentialRampToValueAtTime(.45, now + .006);
      gain.gain.exponentialRampToValueAtTime(.0001, now + .06);
      const oscillator = ctx.createOscillator();
      oscillator.type = 'triangle'; oscillator.frequency.setValueAtTime(frequency, now);
      oscillator.frequency.exponentialRampToValueAtTime(frequency * .94, now + .06);
      oscillator.connect(filter); oscillator.start(now); oscillator.stop(now + .075);
      oscillator.onended = () => { oscillator.disconnect(); filter.disconnect(); gain.disconnect(); };
    },
    destroy() { dead = true; if (ctx) ctx.close().catch(() => {}); },
  };
}

export function mountAvatar(container, options) { return new Avatar(container, options); }
