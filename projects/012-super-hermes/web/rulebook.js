(() => {
  'use strict';
  const data = window.RULEBOOK;
  const $ = selector => document.querySelector(selector);
  const list = $('#rulebook-list');
  const labels = key => ['scan','full','3way','discover','reflect'].includes(key) ? 'prism-' + key : key === 'readme' ? 'README · 运行说明' : key;
  const state = {group:'common', source:'all', query:''};
  const ruleMap = new Map(data.rules.map(rule => [rule.id, rule]));
  const node = (tag, text, className) => {
    const element = document.createElement(tag);
    if (text !== undefined) element.textContent = text;
    if (className) element.className = className;
    return element;
  };
  const sourceButton = (evidence, text) => {
    const button = node('button', text, 'text-button rule-source-button');
    button.type = 'button';
    button.addEventListener('click', () => document.dispatchEvent(new CustomEvent('study-source', {detail:evidence})));
    return button;
  };
  function card(rule) {
    const details = node('details', undefined, 'rule-card');
    details.dataset.ruleId = rule.id;
    const summary = node('summary');
    summary.append(node('span', rule.id, 'rule-id'), node('span', rule.title, 'rule-title'),
      node('span', [...new Set(rule.sources.map(source => labels(source.key)))].join(' / '), 'rule-scope'));
    const body = node('div', undefined, 'rule-body');
    body.append(node('p', rule.kind, 'rule-kind'));
    const fields = node('dl', undefined, 'rule-fields');
    for (const [label, value] of [['原文动作 · 中文概括', rule.action], ['如何指导 AI · 研究解读', rule.how],
      ['应留下的产物', rule.output], ['应用示例 · 研究者举例', rule.example]]) {
      const item = node('div');
      item.append(node('dt', label), node('dd', value));
      fields.append(item);
    }
    body.append(fields);
    if (rule.caveat) body.append(node('p', '使用边界 · ' + rule.caveat, 'rule-caveat'));
    const actions = node('div', undefined, 'rule-actions');
    for (const evidence of rule.sources) {
      actions.append(sourceButton(evidence, labels(evidence.key) + ' 原文 L' + evidence.line + ' ↗'));
    }
    const copy = node('button', '复制这条整理', 'text-button rule-copy');
    copy.type = 'button';
    copy.addEventListener('click', () => document.dispatchEvent(new CustomEvent('study-copy', {detail:
      [rule.id + ' · ' + rule.title, '类型：' + rule.kind, '原文动作概括：' + rule.action, '如何指导 AI：' + rule.how,
        '产物：' + rule.output, '教学示例：' + rule.example, rule.caveat ? '使用边界：' + rule.caveat : '',
        ...rule.sources.map(source => 'https://github.com/Cranot/super-hermes/blob/' + data.revision + '/' + source.path + '#L' + source.line)].filter(Boolean).join('\n')
    })));
    actions.append(copy);
    body.append(actions);
    details.append(summary, body);
    return details;
  }
  function render() {
    const terms = state.query.trim().toLocaleLowerCase().split(/\s+/).filter(Boolean);
    const rules = data.rules.filter(rule =>
      (state.group === 'all' || rule.group === state.group) &&
      (state.source === 'all' || rule.sources.some(source => source.key === state.source)) &&
      terms.every(term => [rule.id, rule.title, rule.action, rule.how, rule.output, rule.example, rule.caveat,
        ...rule.sources.map(source => labels(source.key))].join(' ').toLocaleLowerCase().includes(term)));
    list.replaceChildren(...rules.map(card));
    $('#rulebook-result').textContent = (state.group === 'all' ? '全部规则' : data.groups[state.group]) + ' · ' + rules.length + ' / ' + data.rules.length + ' 条';
    $('#rulebook-empty').hidden = rules.length > 0;
    for (const button of document.querySelectorAll('[data-rule-group]')) {
      button.setAttribute('aria-pressed', String(button.dataset.ruleGroup === state.group));
    }
    $('#rulebook-expand').disabled = rules.length === 0;
    $('#rulebook-collapse').disabled = rules.length === 0;
  }
  $('#rulebook-total').textContent = data.rules.length;
  for (const button of document.querySelectorAll('[data-rule-group]')) {
    const group = button.dataset.ruleGroup;
    button.querySelector('span').textContent = group === 'all' ? data.rules.length : data.rules.filter(rule => rule.group === group).length;
    button.addEventListener('click', () => {state.group = group; render();});
  }
  for (const source of data.sources) {
    const option = node('option', labels(source.key));
    option.value = source.key;
    $('#rulebook-source').append(option);
    const row = node('tr');
    row.append(node('th', labels(source.key)), node('td', source.ruleIds.join(' · ')));
    row.firstChild.scope = 'row';
    const last = node('td');
    const first = ruleMap.get(source.ruleIds[0]).sources.find(evidence => evidence.key === source.key);
    last.append(sourceButton(first, '查看原文 ↗'));
    row.append(last);
    $('#rulebook-source-table').append(row);
  }
  $('#rulebook-search').addEventListener('input', event => {state.query = event.target.value; render();});
  $('#rulebook-source').addEventListener('change', event => {
    state.source = event.target.value;
    state.group = 'all';
    render();
  });
  $('#rulebook-reset').addEventListener('click', () => {
    Object.assign(state, {group:'common', source:'all', query:''});
    $('#rulebook-search').value = '';
    $('#rulebook-source').value = 'all';
    render();
  });
  $('#rulebook-search-all').addEventListener('click', () => {
    state.group = 'all';
    state.source = 'all';
    $('#rulebook-source').value = 'all';
    render();
  });
  $('#rulebook-expand').addEventListener('click', () => {
    list.querySelectorAll('details').forEach(details => {details.open = true;});
  });
  $('#rulebook-collapse').addEventListener('click', () => {
    list.querySelectorAll('details').forEach(details => {details.open = false;});
  });
  render();
})();
