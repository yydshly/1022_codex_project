'use strict';
const $ = (q,root=document)=>root.querySelector(q);
const $$ = (q,root=document)=>[...root.querySelectorAll(q)];
function el(tag,attrs={},...children){const n=document.createElement(tag);for(const[k,v]of Object.entries(attrs)){if(k==='class')n.className=v;else n.setAttribute(k,v);}for(const c of children.flat()){n.append(c instanceof Node?c:document.createTextNode(String(c)));}return n;}
const dialog=$('#guide-dialog'), viewport=$('.guide-viewport'), zoom=$('#guide-zoom');
let opener=null;
function openGuide(e){opener=e.currentTarget;dialog.showModal();document.body.style.overflow='hidden';$('#guide-close').focus();}
$$('[data-open-guide]').forEach(b=>b.addEventListener('click',openGuide));
$('#guide-close').addEventListener('click',()=>dialog.close());
dialog.addEventListener('close',()=>{document.body.style.overflow='';opener?.focus();});
dialog.addEventListener('click',e=>{if(e.target===dialog)dialog.close();});
zoom.addEventListener('click',()=>{const on=viewport.classList.toggle('original');zoom.setAttribute('aria-pressed',String(on));zoom.textContent=on?'适合窗口宽度':'按原始大小查看';viewport.scrollTo(0,0);});
const flows={
execute:{nodes:[['Agent 框架','请求模型，组织动作'],['SDK / HTTP API','提交命令、文件与任务'],['Orchard 编排服务','控制状态、并发与预算'],['Pod 内执行服务','运行命令，返回结果']],description:'高频命令和文件请求经编排服务直达 Pod IP，减少经过 Kubernetes 控制接口的负担。Agent 可以根据输出与错误继续尝试。'},
manage:{nodes:[['编排服务','接收环境创建与删除'],['Kubernetes','调度 Pod，分配资源'],['沙箱池','任务镜像 + 执行服务'],['状态与回收','心跳、TTL、Redis 共享']],description:'Kubernetes 管容器的生命周期与策略；Orchard 提供面向任务的 API 和治理。多副本状态可由 Redis 共享，CPU 环境和模型资源独立配置。'},
research:{nodes:[['任务与框架','固定问题、工具与预算'],['沙箱执行','收集原始交互事件'],['轨迹与评分','日志、补丁、干净验证'],['训练或比较','按具体配方消费反馈']],description:'评测使用任务自身的评分协议，并区分环境故障和模型失败。训练依赖额外模型、数据与计算资源；不是每个配方都使用所有训练方法。'}
};
function showFlow(key,focus=false){const flow=flows[key];const tabs=$$('[data-flow]');tabs.forEach(b=>{const on=b.dataset.flow===key;b.setAttribute('aria-selected',String(on));b.tabIndex=on?0:-1;if(on&&focus)b.focus();});const panel=$('#flow-panel');panel.setAttribute('aria-labelledby','tab-'+key);panel.replaceChildren(el('div',{class:'flow-nodes'},flow.nodes.map(([a,b])=>el('div',{class:'flow-node'},el('strong',{},a),el('span',{},b)))),el('p',{class:'flow-description'},flow.description));}
$$('[data-flow]').forEach((b,i,all)=>{b.addEventListener('click',()=>showFlow(b.dataset.flow));b.addEventListener('keydown',e=>{let n;if(e.key==='ArrowRight')n=(i+1)%all.length;else if(e.key==='ArrowLeft')n=(i+all.length-1)%all.length;else if(e.key==='Home')n=0;else if(e.key==='End')n=all.length-1;if(n!==undefined){e.preventDefault();showFlow(all[n].dataset.flow,true);}});});
showFlow('execute');
async function start(){
const response=await fetch('./research.json');if(!response.ok)throw new Error('研究数据加载失败：HTTP '+response.status);const data=await response.json();
$('#project-summary').textContent=data.summary;
$('#roles').replaceChildren(...data.roles.map(([title,body,note],i)=>el('article',{class:'role'},el('span',{class:'role-index'},'0'+(i+1)+' / '+['决策','组织','执行'][i]),el('h3',{},title),el('p',{},body),el('small',{},note))));
$('#steps').replaceChildren(...data.steps.map(([title,body],i)=>el('article',{class:'step'},el('span',{},'0'+(i+1)),el('h3',{},title),el('p',{},body))));
const sourceURL=path=>data.upstream+'/blob/'+data.commit+'/'+path;
$('#capability-list').replaceChildren(...data.capabilities.map(([title,body,api,path],i)=>el('article',{class:'capability'},el('span',{},String(i+1).padStart(2,'0')+' / ENVIRONMENT'),el('h3',{},title),el('p',{},body),el('details',{},el('summary',{},'接口与源码参照'),el('code',{},api),el('a',{href:sourceURL(path),target:'_blank',rel:'noreferrer'},'查看固定版本源码 ↗')))));
$('#layers').replaceChildren(...data.layers.map(([name,type,body])=>el('article',{class:'layer'},el('h3',{},name),el('span',{},type),el('p',{},body))));
$('#comparison').replaceChildren(...data.comparisons.map(row=>el('tr',{},row.map(cell=>el('td',{},cell)))));
function choose(key){const item=data.decisions.find(x=>x.key===key);$$('#decision-buttons button').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.key===key)));$('#decision-result').replaceChildren(el('h4',{},item.title),el('p',{},item.body),el('small',{},item.needs));}
$('#decision-buttons').replaceChildren(...data.decisions.map(x=>{const b=el('button',{'data-key':x.key,'aria-pressed':'false'},x.label);b.addEventListener('click',()=>choose(x.key));return b;}));choose('local');
$('#techniques').replaceChildren(...data.techniques.map(x=>el('details',{class:'technique'},el('summary',{},el('span',{class:'priority'},x.priority),el('strong',{},x.name),el('p',{},x.description),el('b',{'aria-hidden':'true'},'+')),el('dl',{class:'technique-body'},el('div',{},el('dt',{},'输入'),el('dd',{},x.input)),el('div',{},el('dt',{},'输出'),el('dd',{},x.output)),el('div',{class:'acceptance'},el('dt',{},'验收条件'),el('dd',{},x.acceptance),el('a',{class:'text-link',href:sourceURL(x.source),target:'_blank',rel:'noreferrer'},'固定源码参照 ↗'))))));
function filter(type){const rows=data.scenarios.filter(x=>type==='全部'||x.type===type);$$('#scenario-filters button').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.type===type)));$('#scenario-count').textContent='显示 '+rows.length+' 个场景 · '+type;$('#scenario-list').replaceChildren(...rows.map(x=>el('article',{class:'scenario'},el('span',{},x.type),el('h3',{},x.name),el('dl',{},el('dt',{},'可复用'),el('dd',{},x.reuse),el('dt',{},'仍需补充'),el('dd',{},x.extra)),el('p',{class:'stage'},x.stage))));}
$('#scenario-filters').replaceChildren(...['全部',...new Set(data.scenarios.map(x=>x.type))].map(type=>{const b=el('button',{'data-type':type,'aria-pressed':'false'},type);b.addEventListener('click',()=>filter(type));return b;}));filter('全部');
$('#metrics').replaceChildren(...data.metrics.map(x=>el('article',{class:'metric'},el('h3',{},x.title),el('div',{class:'metric-value'},x.value),el('p',{},x.body),el('small',{},x.condition),el('a',{href:x.url,target:'_blank',rel:'noreferrer'},'查看作者报告 ↗'))));
$('#source-list').replaceChildren(...data.sources.map(x=>el('a',{href:x.url,target:'_blank',rel:'noreferrer'},x.label+' ↗')));
document.documentElement.dataset.researchReady='true';
}
start().catch(error=>{$('#load-status').textContent=error.message+'。请重试，或直接查看引导图与研究文档。';console.error(error);});
