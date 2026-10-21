/* Presentation controls only. Product visuals are unchanged upstream PNGs. */
(() => {
  "use strict";
  const $ = (selector) => document.querySelector(selector);
  const COMMIT = "2ae76fc80b0b96ad8191e3d1ae4949ee340190a7";
  const SOURCE = `https://github.com/salarzeidanlou/todofy/blob/${COMMIT}/`;
  const shots = {
    today:{title:"Today · 今日任务",alt:"Todofy 官方今日视图：下一步任务、逾期和今日分组、子任务、优先级和计时",seen:"上方突出下一步任务，下方区分逾期与今天；任务同时带有优先级、标签、子任务进度、预估与实际用时。",meaning:"它把日期计划和执行所需的信息放在同一处，帮助使用者决定下一步处理什么。",boundary:"这是作者拍摄时的任务与日期。图中的计时和完成数量是截图内容，不是本页在运行的任务。"},
    board:{title:"Board · 看板",alt:"Todofy 官方看板原图，任务按 To do、In progress、Blocked 和 Done 分列",seen:"任务分布在待办、进行中、受阻和已完成四列，卡片保留日期、标签、优先级、步骤和用时信息。",meaning:"看板围绕工作阶段组织任务；日期和阶段是不同属性，能够同时出现在同一张任务卡片上。",boundary:"原生应用支持拖动和自定义列。此处原样展示官方图片，卡片内的控件属于图片内容。"},
    calendar:{title:"Calendar · 日历",alt:"Todofy 官方月日历原图，展示任务、日程与 Month、Week、Day 切换入口",seen:"任务和独立日程出现在月历中；右上方有月、周、日切换和新建事件入口，左侧保留日期导航。",meaning:"同一批任务可以从日期角度查看，独立日程则用于补充时间安排。",boundary:"截图展示本地日历。Google Calendar 的单向任务推送是另一条集成路径，依据源码分析，不能从这张图推导成双向同步。"},
    focus:{title:"Focus · 专注计时",alt:"Todofy 官方专注界面，含番茄钟、专注与休息配置、当天和本周历史",seen:"左侧是专注倒计时，右侧配置专注、短休息、长休息和轮数，下方可查看专注历史。",meaning:"除了安排任务，应用还帮助记录实际投入并保持专注节奏。任务秒表和番茄钟使用不同的状态模型。",boundary:"图中的倒计时是拍摄瞬间的数字。实际计时在原生程序内运行，当前源码对超长会话设有 12 小时安全上限。"},
    quickadd:{title:"Quick capture · 快速记录",width:1880,height:480,alt:"Todofy 官方快速记录浮窗，英文输入被解析成 P1、日期、时间、每周重复和 Work 标签",seen:"英文输入下方直接出现优先级、相对日期、时间、每周重复与已有标签的字段提示。",meaning:"使用者可以在一个输入框内同时填写多项属性。源码采用规则和 chrono-node 提取字段。",boundary:"相对日期来自拍摄时刻。已有标签匹配和英文日期解析有明确语法范围，不代表通用中文排期理解。"},
    journal:{title:"Journal · 日志",alt:"Todofy 官方日志原图，含 Markdown 编辑器、心情、每日完成与专注摘要及历史记录",seen:"编辑区支持 Markdown、心情和当天摘要，下方把已有日志按日期排列。",meaning:"任务执行之外，还可以记录当天感受与复盘。源码中的摘要通过完成数和专注分钟数生成简短文字。",boundary:"这些日志是作者的官方展示内容；摘要是结构化计数，不是大模型对工作质量的评价。"},
    voice:{title:"Voice · 本地语音设置",alt:"Todofy 官方语音设置原图，展示 whisper.cpp 引擎、Base 与 Tiny 模型和 Voice Mode 开关",seen:"设置页显示本地语音引擎、Base / Tiny 多语言模型、安装状态，以及语音模式开关。",meaning:"用户按需下载引擎和模型，录音后由 whisper.cpp 在本机转成可编辑文字。",boundary:"安装状态属于作者的展示环境。本次没有测量识别准确率与速度，语音转写也不等于中文日期字段会自动识别。"},
    settings:{title:"Settings · 账号与集成设置",alt:"Todofy 官方设置原图，包含 Cloud Sync 登录、Google Calendar 连接条件和本地语音下载",seen:"界面提供 Cloud Sync 账号入口、Google Calendar 提示和语音模型管理，明确区分可选服务。",meaning:"本地任务管理可以先独立使用；需要多端和日历连接时，再选择相应账号、授权和服务。",boundary:"图中展示的是设置入口，不是已经完成同步的证明。官方云同步属于 Pro，独立本地日程不进入账号同步或 Google 推送。"},
  };
  const state = {shot:"today",step:"input",scenario:"work"};
  const imagePath = (key) => `./assets/upstream/${key}.png`;
  function selectTab(attribute,value) {
    document.querySelectorAll(`[${attribute}]`).forEach((button) => {const active=button.getAttribute(attribute)===value;button.setAttribute("aria-selected",String(active));button.tabIndex=active?0:-1;});
  }
  function renderShot(key) {
    if(!Object.hasOwn(shots,key)) return;
    state.shot=key;
    const shot=shots[key],width=shot.width??2880,height=shot.height??1800;
    const image=$("#official-image");
    image.src=imagePath(key);image.alt=shot.alt;image.width=width;image.height=height;
    $("#screenshot-title").textContent=shot.title;
    $("#screenshot-file").textContent=`docs/${key}.png · ${width} × ${height} · 上游原图`;
    $("#original-image").href=imagePath(key);
    $("#source-image").href=SOURCE+`docs/${key}.png`;
    $("#screenshot-panel").setAttribute("aria-labelledby",`shot-${key}`);
    $("#screenshot-observations").innerHTML=`<article><span>01 / 界面里看到了什么</span><p>${shot.seen}</p></article><article><span>02 / 对应什么能力</span><p>${shot.meaning}</p></article><article><span>03 / 使用条件与边界</span><p>${shot.boundary}</p></article>`;
    $("#open-image").setAttribute("aria-label",`放大官方截图：${shot.title}`);
    selectTab("data-shot",key);
  }
  const dialog=$("#image-dialog");
  function openImage() {
    const shot=shots[state.shot];
    $("#dialog-title").textContent=shot.title;
    $("#dialog-file").textContent=`docs/${state.shot}.png · © Salar Zeidanlou / unifybrowse`;
    $("#dialog-image").src=imagePath(state.shot);$("#dialog-image").alt=shot.alt;
    $("#dialog-image").width=shot.width??2880;$("#dialog-image").height=shot.height??1800;
    $("#dialog-original").href=imagePath(state.shot);
    dialog.showModal();
  }
  $("#open-image").addEventListener("click",openImage);
  $("#zoom-image").addEventListener("click",openImage);
  $("#close-dialog").addEventListener("click",()=>dialog.close());
  dialog.addEventListener("click",(event)=>{if(event.target===dialog){const b=dialog.getBoundingClientRect();if(event.clientX<b.left||event.clientX>b.right||event.clientY<b.top||event.clientY>b.bottom)dialog.close();}});
  document.querySelectorAll("[data-shot]").forEach((button)=>button.addEventListener("click",()=>renderShot(button.dataset.shot)));
  function showShot(key) {
    renderShot(key);
    $("#showcase").scrollIntoView({behavior:matchMedia("(prefers-reduced-motion: reduce)").matches?"instant":"smooth",block:"start"});
    $("#shot-"+key).focus({preventScroll:true});
  }
  document.querySelectorAll("[data-show-shot]").forEach((button)=>button.addEventListener("click",()=>showShot(button.dataset.showShot)));
  const principles={
    input:{label:"INPUT / STRUCTURE",title:"从输入中获得任务字段。",body:"界面收集标题、日期、优先级和标签。快速添加通过正则识别优先级与重复标记，再由 chrono-node 解析英文日期，未识别的内容保留为标题。",note:"语音是另一条输入路径：先用本地模型转成文字，再由用户检查并确认。",chip:"文字 → 标题 / 日期 / 优先级 / 标签",file:"src/lib/nlp.ts"},
    store:{label:"LOCAL / PERSISTENCE",title:"先把记录保存到本机。",body:"Preact 界面通过 Tauri invoke 调用 Rust 命令，由 Rust 操作本地 SQLite。核心任务管理不要求先登录账号。",note:"任务、标签、日志和计时状态都有本地存储；账号同步在此基础上按需启用。",chip:"界面 → Tauri 命令 → Rust → SQLite",file:"src-tauri/src/db.rs"},
    view:{label:"VIEW / PROJECTION",title:"按字段组织出不同视图。",body:"今日列表按日期筛选和分组；看板按阶段与完成状态分列；日历按日期定位。同一个任务 ID 能被不同视图引用。",note:"列表与看板的手动排序分别保存。移动工作阶段，不会自动修改截止日期。",chip:"同一任务 → 日期分组 / 阶段分组 / 日历位置",file:"src/lib/grouping.ts"},
    background:{label:"BACKGROUND / ASSIST",title:"由后台处理提醒与计时。",body:"Rust 线程约每 20 秒检查到期提醒。计时保存累计值与运行起点，重启后读取时间戳重算，而不是依赖窗口内每秒计数。",note:"完全退出后无法发送提醒。未暂停的计时可能计入离开时长，源码有 12 小时安全上限。",chip:"持久化状态 → 到期检查 / 计时恢复",file:"src-tauri/src/scheduler.rs"},
  };
  function renderPrinciple() {
    const item=principles[state.step];
    $("#principle-detail").setAttribute("aria-labelledby",`step-${state.step}`);
    $("#principle-detail").innerHTML=`<span class="detail-label">${item.label}</span><h3>${item.title}</h3><p>${item.body}</p><div class="principle-chip">${item.chip}</div><p>${item.note}</p><a href="${SOURCE+item.file}" target="_blank" rel="noopener noreferrer">查看对应源码 ↗</a>`;
    selectTab("data-step",state.step);
  }
  document.querySelectorAll("[data-step]").forEach((button)=>button.addEventListener("click",()=>{state.step=button.dataset.step;renderPrinciple();}));
  const scenarios={
    work:{kicker:"DAILY PLANNING",title:"每天，知道先处理什么。",problem:"事情散落在便签和消息里。先收集任务，再给有期限的事情设置日期和优先级，早上从今日与逾期分组里决定下一步。",steps:["快速收集","日期与优先级","查看今日","完成后回顾"],result:"把分散事项组织成当天可以查阅和执行的清单。",boundary:"计划与顺序仍由使用者判断；给任务填日期，不代表系统自动留出了足够的工作时间。",shot:"today"},
    project:{kicker:"PERSONAL PROJECT",title:"看见推进，也看见阻塞。",problem:"个人作品或研究有多个阶段。用标签归类、子任务拆解，再通过看板观察哪些在做、哪些被卡住。",steps:["标签归类","拆解步骤","看板推进","标记受阻"],result:"阶段、截止日期和任务细节共同描述工作进展。",boundary:"WIP 是数量提醒，不会禁止超限；个人看板不等于团队派工与共享权限系统。",shot:"board"},
    study:{kicker:"LEARNING RHYTHM",title:"让学习有步骤，也有节奏。",problem:"把学习目标拆成阅读、练习和复盘；借助重复任务保持节奏，用番茄钟和历史记录观察投入。",steps:["建立学习任务","拆解步骤","专注与休息","日志回顾"],result:"把长期目标落实为可以执行的小步骤与专注节奏。",boundary:"重复任务完成后原地推进日期，没有每期独立完成记录；投入时长不能代表知识掌握程度。",shot:"focus"},
    time:{kicker:"ESTIMATE & ACTUAL",title:"用实际投入，修正时间估计。",problem:"先填写预计用时，执行时正确开始、暂停和结束任务计时，之后比较为什么超时，调整下一次的拆分和估计。",steps:["填写预估","开始与暂停","对比实际","修正计划"],result:"用实际记录改善对工作量的判断，减少安排过满。",boundary:"官方 Today 图直接展示预估、实际和超时值。计时依赖正确操作，也不等于工时结算或开票。",shot:"today"},
    offline:{kicker:"LOCAL FIRST",title:"本机记录，按需使用语音。",problem:"网络不稳定时，核心记录仍在本机。用户预先下载引擎与模型后，可以把口述转成草稿，检查后保存。",steps:["本机保存","离线记录","可选语音转写","检查并确认"],result:"日常记录可以在设备内完成，外部服务按需连接。",boundary:"语音设置图展示的是作者的模型安装状态；本次未测识别准确率与速度，中文转写不等于中文日期识别。",shot:"voice"},
    calendar:{kicker:"CALENDAR PLANNING",title:"从日期视角，看清交付安排。",problem:"把带期限的任务放到日期视图中，与独立日程一起查看。需要时，可在原生设置中单独授权 Google 日历集成。",steps:["任务设置日期","查看本地日历","补充独立日程","按需连接外部日历"],result:"看清不同日期上的任务和日程，结合工作阶段做计划。",boundary:"对应原图展示本地日历。Google 集成为任务单向推送，不导入原有会议，独立本地日程不参与推送。",shot:"calendar"},
  };
  function renderScenario() {
    const item=scenarios[state.scenario];
    $("#scenario-panel").setAttribute("aria-labelledby",`scenario-${state.scenario}`);
    $("#scenario-panel").innerHTML=`<span class="scenario-kicker">${item.kicker}</span><h3>${item.title}</h3><p class="scenario-problem">${item.problem}</p><div class="scenario-route">${item.steps.map((step,index)=>`${index?'<i aria-hidden="true">→</i>':""}<span>${step}</span>`).join("")}</div><p class="scenario-result">${item.result}</p><p class="scenario-boundary"><b>使用条件与边界</b><br>${item.boundary}</p><button type="button" class="button primary" id="scenario-shot">查看对应官方界面 ↗</button>`;
    selectTab("data-scenario",state.scenario);
  }
  document.querySelectorAll("[data-scenario]").forEach((button)=>button.addEventListener("click",()=>{state.scenario=button.dataset.scenario;renderScenario();}));
  $("#scenario-panel").addEventListener("click",(event)=>{if(event.target.closest("#scenario-shot"))showShot(scenarios[state.scenario].shot);});
  document.querySelectorAll('[role="tablist"]').forEach((group)=>group.addEventListener("keydown",(event)=>{
    const current=event.target.closest('[role="tab"]');if(!current)return;
    const tabs=[...group.querySelectorAll('[role="tab"]')],index=tabs.indexOf(current),vertical=group.getAttribute("aria-orientation")==="vertical";
    let target;const next=vertical?"ArrowDown":"ArrowRight",previous=vertical?"ArrowUp":"ArrowLeft";
    if(event.key===next)target=(index+1)%tabs.length;else if(event.key===previous)target=(index-1+tabs.length)%tabs.length;else if(event.key==="Home")target=0;else if(event.key==="End")target=tabs.length-1;else return;
    event.preventDefault();tabs[target].focus();tabs[target].click();
  }));
  renderShot(state.shot);renderPrinciple();renderScenario();
})();
