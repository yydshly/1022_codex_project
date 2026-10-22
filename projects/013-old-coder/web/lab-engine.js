/* Original teaching experiments, not an upstream old-coder runtime. */
(function (root) {
  'use strict';
  const VERSION = '1.0.0';
  const clone = value => JSON.parse(JSON.stringify(value));
  const equal = (a, b) => JSON.stringify(a) === JSON.stringify(b);
  const row = (id, title, expected, actual) => ({ id, title, expected, actual, pass: equal(expected, actual) });

  function inventory({ variant = 'atomic', pattern = 'serial', requests = 5, orders } = {}) {
    let durable = { stock: 10, processed: [], effects: 0 };
    let memory = new Set();
    const trace = [];
    const items = orders || Array.from({ length: requests }, () => 'order-001');
    const apply = (id, injectFailure = false) => {
      const before = clone(durable);
      const seen = variant === 'memory' ? memory.has(id) : durable.processed.includes(id);
      if (variant !== 'naive' && seen) { trace.push(`${id}：重复通知，返回已有结果，不扣库存`); return; }
      try {
        if (variant === 'memory') memory.add(id);
        else durable.processed.push(id);
        if (injectFailure) throw new Error('模拟：标记后、扣库存前故障');
        durable.stock -= 1;
        durable.effects += 1;
        trace.push(`${id}：扣库存 1，剩余 ${durable.stock}`);
      } catch (error) {
        if (variant === 'atomic') { durable = before; trace.push(`${error.message} → 整笔事务回滚`); }
        else trace.push(`${error.message} → 标记残留，后续重试可能被吞掉`);
      }
    };
    if (pattern === 'concurrent' && variant === 'race') {
      // Deterministic interleaving: every caller reads before any caller writes.
      const pending = items.filter(id => {
        const unseen = !durable.processed.includes(id);
        trace.push(`${id}：请求先读到 ${unseen ? '未处理' : '已处理'}`);
        return unseen;
      });
      pending.forEach(id => { durable.processed.push(id); durable.stock -= 1; durable.effects += 1; trace.push(`${id}：随后写入并扣库存，剩余 ${durable.stock}`); });
    } else if (pattern === 'restart') {
      apply(items[0]);
      durable = clone(durable); memory = new Set();
      trace.push('模拟进程重启：恢复序列化业务状态，清空进程内缓存');
      items.slice(1).forEach(id => apply(id));
    } else if (pattern === 'failure') {
      apply(items[0], true);
      trace.push('同一通知重试');
      apply(items[0]);
    } else {
      if (pattern === 'concurrent') trace.push('用确定性调度模拟争抢；atomic 分支串行执行模型事务');
      items.forEach(id => apply(id));
    }
    return { ...durable, trace };
  }

  function createLimiter(variant, limit, windowMs) {
    if (!Number.isInteger(limit) || limit <= 0 || !Number.isFinite(windowMs) || windowMs <= 0) throw new Error('invalid configuration');
    const hits = new Map();
    const buckets = new Map();
    return (key, now) => {
      if (typeof key !== 'string' || !key) throw new Error('invalid key');
      if (variant === 'deny') return false;
      if (variant === 'fixed') {
        const bucket = Math.floor(now / windowMs);
        const last = buckets.get(key) || { bucket, count: 0 };
        if (bucket !== last.bucket) { last.bucket = bucket; last.count = 0; }
        if (last.count >= limit) return false;
        last.count++; buckets.set(key, last); return true;
      }
      const live = (hits.get(key) || []).filter(t => variant === 'boundary' ? now - t < windowMs : now - t <= windowMs);
      hits.set(key, live);
      if (live.length >= limit) return false;
      live.push(now); return true;
    };
  }

  function rateSequence(variant, events, limit = 3, windowMs = 1000) {
    const allow = createLimiter(variant, limit, windowMs);
    return events.map(([key, time]) => ({ key, time, allowed: allow(key, time) }));
  }

  function permission(variant, { tenant = 'alpha', bodyTenant = 'alpha', id = 'A-01', action = 'get' } = {}) {
    const records = [{ id: 'A-01', tenant: 'alpha', amount: 120 }, { id: 'B-01', tenant: 'beta', amount: 900 }];
    if (!tenant) return { status: 401, ids: [] };
    const boundary = variant === 'body' ? bodyTenant : tenant;
    if (action !== 'get') {
      const visible = variant === 'id-only' ? records : records.filter(r => r.tenant === boundary);
      return { status: 200, ids: visible.map(r => r.id) };
    }
    const record = records.find(r => r.id === id);
    if (!record) return { status: 404, ids: [] };
    if (variant !== 'id-only' && record.tenant !== boundary) return { status: 403, ids: [] };
    return { status: 200, ids: [record.id] };
  }

  function api(variant, payload = {}) {
    if (variant === 'validation' && !payload.country) return { status: 400, error: 'country is required' };
    const user = { id: 'u_001', email: 'alice@example.test', created_at: '2026-10-22T00:00:00Z' };
    if (variant === 'rename') { user.user_id = user.id; delete user.id; }
    else if (variant === 'type') user.id = 1;
    else if (variant === 'additive') user.display_name = 'Alice';
    return { status: 200, user };
  }

  function random(seed) {
    let state = seed >>> 0;
    return () => { state = (Math.imul(state, 1664525) + 1013904223) >>> 0; return state / 4294967296; };
  }
  function propertyCheck(variant, seed = 42) {
    const rng = random(seed);
    let upperBound = true, oracleMatch = true, firstMismatch = null;
    for (let sequence = 0; sequence < 100; sequence++) {
      const allow = createLimiter(variant, 3, 1000);
      const accepted = new Map(), oracle = new Map();
      let now = 0;
      for (let i = 0; i < 40; i++) {
        now += Math.floor(rng() * 300);
        const key = rng() < 0.8 ? 'alice' : 'bob';
        const live = (oracle.get(key) || []).filter(t => now - t <= 1000);
        const expected = live.length < 3;
        if (expected) live.push(now);
        oracle.set(key, live);
        const actual = allow(key, now);
        const real = (accepted.get(key) || []).filter(t => now - t <= 1000);
        if (actual) real.push(now);
        accepted.set(key, real);
        if (real.length > 3) upperBound = false;
        if (actual !== expected) {
          oracleMatch = false;
          firstMismatch ||= { sequence, step: i, key, now, expected, actual };
        }
      }
    }
    return { upperBound, oracleMatch, firstMismatch, inputs: 4000, seed };
  }

  const variants = {
    inventory: [['naive', '每次通知都扣库存'], ['memory', '只用内存防重复'], ['race', '先查询、后写入'], ['atomic', '原子事务模型']],
    limiter: [['fixed', '固定时间桶'], ['boundary', '提前释放窗口边界'], ['deny', '一律拒绝'], ['sliding', '滑动窗口实现']],
    permission: [['id-only', '只按订单 ID 查询'], ['body', '信任请求中的租户'], ['secure', '使用身份中的租户']],
    api: [['rename', '改名 id → user_id'], ['type', '把字符串 ID 改成数字'], ['validation', '新增必填 country'], ['additive', '只新增响应字段']]
  };
  const correct = { inventory: 'atomic', limiter: 'sliding', permission: 'secure', api: 'additive' };

  function runSuite(scenario, variant, strength = 'full', seed = 42) {
    let rows = [];
    if (scenario === 'inventory') {
      rows.push(row('I1', '单条通知正常扣库存', 9, inventory({ variant, requests: 1 }).stock));
      if (strength === 'full') {
        for (const [id, title, pattern] of [['I2', '10 次重复通知只扣一次', 'serial'], ['I3', '先读后写交错也只扣一次', 'concurrent'], ['I4', '重启后重复通知不再扣库存', 'restart'], ['I5', '写入中断后重试能完成且只扣一次', 'failure']]) {
          const value = inventory({ variant, requests: 10, pattern });
          rows.push(row(id, title, { stock: 9, effects: 1 }, { stock: value.stock, effects: value.effects }));
        }
        rows.push(row('I6', '不同订单分别处理', 8, inventory({ variant, orders: ['order-001', 'order-002'] }).stock));
      }
    } else if (scenario === 'limiter') {
      const property = propertyCheck(variant, seed);
      if (strength === 'weak') rows.push(row('L0', '随机序列：放行数从不超限（只有上界）', true, property.upperBound));
      else {
        const outcomes = events => rateSequence(variant, events).map(r => r.allowed);
        rows.push(row('L1', '连续 5 次：放行 3 次、拒绝 2 次', [true,true,true,false,false], outcomes([0,0,0,0,0].map(t => ['alice',t]))));
        rows.push(row('L2', '窗口闭边界 1000ms 仍拒绝，1001ms 恢复', [true,true,true,false,true], outcomes([0,0,0,1000,1001].map(t => ['alice',t]))));
        rows.push(row('L3', '跨整秒边界不能在一个窗口内放行 6 次', [true,true,true,false,false,false], outcomes([950,960,970,1001,1002,1003].map(t => ['alice',t]))));
        rows.push(row('L4', '不同用户额度相互独立', [true,true,true,true], outcomes([['alice',0],['alice',0],['alice',0],['bob',0]])));
        rows.push(row('L5', '4000 次随机输入与独立参考模型一致', true, property.oracleMatch));
        let rejects = 0;
        for (const value of [0, -1, NaN, Infinity, 1.5]) { try { createLimiter(variant,value,1000); } catch { rejects++; } }
        rows.push(row('L6', '非法配置被拒绝', 5, rejects));
      }
    } else if (scenario === 'permission') {
      rows.push(row('P1', '本租户读取自己的订单', {status:200,ids:['A-01']}, permission(variant)));
      if (strength === 'full') {
        rows.push(row('P2', '猜中其他租户订单 ID 仍不可读取', {status:403,ids:[]}, permission(variant,{id:'B-01'})));
        rows.push(row('P3', '伪造 bodyTenant 不能越权', {status:403,ids:[]}, permission(variant,{id:'B-01',bodyTenant:'beta'})));
        rows.push(row('P4', '列表只返回本租户订单', {status:200,ids:['A-01']}, permission(variant,{action:'list'})));
        rows.push(row('P5', '导出不能绕过租户边界', {status:200,ids:['A-01']}, permission(variant,{action:'export',bodyTenant:'beta'})));
        rows.push(row('P6', '未认证的请求返回 401', {status:401,ids:[]}, permission(variant,{tenant:null})));
      }
    } else if (scenario === 'api') {
      const result = api(variant,{country:'CN'});
      rows.push(row('A1', '新客户端仍能收到成功响应', 200, result.status));
      if (strength === 'full') {
        rows.push(row('A2', '旧客户端仍能读取 id 字段', true, Object.hasOwn(result.user,'id')));
        rows.push(row('A3', 'ID 继续保持字符串类型', 'string', typeof result.user.id));
        rows.push(row('A4', '旧请求不传 country 仍然成功', 200, api(variant,{}).status));
        rows.push(row('A5', '原有 email 和 created_at 字段保留', true, typeof result.user.email === 'string' && typeof result.user.created_at === 'string'));
        const legacy = api(variant,{});
        const works = legacy.status === 200 && typeof legacy.user.id === 'string';
        rows.push(row('A6', '旧客户端按原请求与原字段工作', true, works));
      }
    } else throw new Error(`Unknown scenario: ${scenario}`);
    return { scenario, variant, strength, seed, rows, passed: rows.filter(r => r.pass).length, failed: rows.filter(r => !r.pass).length, total: rows.length };
  }

  function mutation(scenario, strength = 'full', seed = 42) {
    const baseline = runSuite(scenario, correct[scenario], strength, seed);
    const mutants = variants[scenario].filter(([id]) => id !== correct[scenario]).map(([id,title]) => {
      const result = runSuite(scenario,id,strength,seed);
      return { id, title, killed: result.failed > 0, failures: result.rows.filter(r => !r.pass).map(r => r.id) };
    });
    return { baselinePassed: baseline.failed === 0, mutants, killed: mutants.filter(r => r.killed).length, total: mutants.length };
  }

  const exported = { VERSION, inventory, createLimiter, rateSequence, permission, api, propertyCheck, variants, correct, runSuite, mutation };
  if (typeof module !== 'undefined' && module.exports) module.exports = exported;
  else root.OCLab = exported;
})(typeof window !== 'undefined' ? window : globalThis);
