"use strict";

// Editorial guidance data, not emotion recognition or image inference.
(() => {
  const $ = selector => document.querySelector(selector);
  if (!$("#emotion-library")) return;
  let data, current, family="warmth", appliedKey="", editorModified=false, editorAcknowledged=false;
  const make=(tag,text,className)=>{const el=document.createElement(tag);if(text!==undefined)el.textContent=text;if(className)el.className=className;return el;};
  const asset=file=>"./assets/"+file;
  const settings=()=>({primaryId:current.id,secondaryId:$("#emotion-secondary").value,level:$("#emotion-level").value,notes:$("#emotion-context").value.trim()});
  const key=()=>JSON.stringify(settings());
  function loadedStatus() {
    const text=!appliedKey?"选择与修改只更新下方情绪指令；点击“载入原风格编辑器”才会同步主方案。":appliedKey!==key()?"情绪方案已调整；重新载入后，主编辑器才会使用这些新要求。":editorModified?"档案已载入，主编辑器又做了微调；最终完整指令以主编辑器为准。":"情绪方案已载入原风格编辑器，主体、标题、识别中心、允许区域与画幅保持原值。";
    $("#emotion-load-status").textContent=text;
  }
  function visualText(profile) {
    const v=profile.visual;
    return "配色："+data.vocabularies.palette[v.palette]+"\n光线："+v.light+"\n空间与叙事："+v.space+"\n材质："+v.material+"\n标题："+v.typography+"\n计算关系建议："+data.vocabularies.method[v.method]+" / "+data.vocabularies.extension[v.extension]+"。"+v.data;
  }
  function brief() {
    const s=settings(),secondary=data.profiles.find(p=>p.id===s.secondaryId)||null,level=data.levels[s.level];
    const intent=current.goal+"\n避免："+current.avoid+(secondary?"\n副情绪："+secondary.name+"；"+secondary.goal+" 避免："+secondary.avoid:"")+"\n表达力度："+level.name+"；"+level.instruction+(s.notes?"\n本次补充："+s.notes:"");
    const direction=[
      "主情绪："+current.name+"。情绪、光色、空间与数据节奏围绕这一目标组织。",
      "故事："+current.story,
      visualText(current),
      secondary?"副情绪："+secondary.name+"。故事线索："+secondary.story+" 只选一处局部细节或关系作为补充，主情绪的光色、构图与避免项优先；不要合并两套全部视觉配方。":"",
      "情绪表达力度："+level.instruction+" 这不等于数据覆盖率或密度。",
      s.notes?"本次补充约束："+s.notes:"",
      "常见跑偏："+current.drift.problem+"。返修方向："+current.drift.repair,
      "本档案评审："+current.check,
      "通用检查：\n"+data.checks.join("\n")
    ].filter(Boolean).join("\n\n");
    const prompt="把以下情绪要求用于完整艺术创作，并与原有风格规范合用。实体与数据的关系、识别中心和模块化标题仍保留；情绪不是统一滤镜。\n\n目标感受："+intent+"\n\n"+direction+"\n\n输入角色：主体图确定身份与形状，风格图说明视觉语法，情绪参考只借鉴对应光色与空间。当前主体、情绪和具体要求优先。\n\n这些是创作与返修要求；实际感受需要看成图并收集反馈。";
    return {version:1,kind:"emotion-direction-brief",generated:false,source:"assets/emotions/profiles.json",primary:current,secondary,expression:{id:s.level,...level},notes:s.notes,checks:data.checks,config:{intent,metaphor:current.visual.metaphor,light:current.visual.light+"\n材质："+current.visual.material,palette:current.visual.palette,method:current.visual.method,extension:current.visual.extension,intensity:current.visual.intensity,"emotion-direction":direction},prompt};
  }
  function updateBrief() { $("#emotion-prompt").textContent=brief().prompt;$("#emotion-copy-status").textContent="可单独复制情绪要求，或载入下方原风格编辑器，导出含主体与固定规则的完整方案。";loadedStatus(); }
  function renderReference() {
    const box=$("#emotion-reference");box.replaceChildren();
    if(!current.reference) {box.append(make("p","这份档案暂无独立成图。以下是创作指导要求，可在实际生成后积累自己的正反例。","emotion-no-reference"));return;}
    const ref=current.reference,details=make("details"),summary=make("summary","查看已有成图参照 · 供观察，不是当前方案输出"),figure=make("figure");
    const button=make("button");button.type="button";button.className="emotion-reference-image";button.setAttribute("aria-label","放大已有参照："+current.name);
    const img=document.createElement("img");img.src=asset(ref.image);img.alt=ref.caption;img.width=1122;img.height=1402;img.loading="lazy";button.append(img);
    button.addEventListener("click",()=>{$("#art-dialog-image").src=asset(ref.image);$("#art-dialog-image").alt=ref.caption;$("#art-dialog-title").textContent="历史成图参照 / "+current.name;$("#art-dialog").showModal();$("#art-dialog").scrollTop=0;});
    const caption=make("figcaption",ref.caption),link=make("a","参照图的实际生成指令 ↓");link.href=asset(ref.prompt);link.download=ref.prompt.split("/").pop();figure.append(button,caption,link);details.append(summary,figure);box.append(details);
  }
  function renderProfile() {
    const f=data.families.find(item=>item.id===current.family);
    $("#emotion-profile-code").textContent=f.name+" / v1 创作指导档案";
    $("#emotion-profile-name").textContent=current.name;
    for(const field of ["goal","avoid","story","uses","check"])$("#emotion-"+field).textContent=current[field];
    $("#emotion-problem").textContent=current.drift.problem;$("#emotion-repair").textContent=current.drift.repair;
    const labels={palette:"配色家族",light:"光线与气氛",space:"空间与叙事",material:"真实材质",typography:"标题语气",data:"计算转化与节奏"};
    $("#emotion-visual").replaceChildren(...Object.entries(labels).flatMap(([field,name])=>[make("dt",name),make("dd",field==="palette"?data.vocabularies.palette[current.visual.palette]:field==="data"?data.vocabularies.method[current.visual.method]+" / "+data.vocabularies.extension[current.visual.extension]+"。"+current.visual.data:current.visual[field])]));
    const previous=$("#emotion-secondary").value;
    $("#emotion-secondary").replaceChildren(...[{id:"none",name:"无副情绪"},...data.profiles.filter(p=>p.id!==current.id)].map(p=>{const o=make("option",p.name);o.value=p.id;return o;}));
    $("#emotion-secondary").value=previous&&previous!==current.id?previous:"none";
    renderReference();updateBrief();
  }
  function renderCards() {
    const query=$("#emotion-search").value.trim().toLowerCase();
    const profiles=data.profiles.filter(p=>(family==="all"||p.family===family)&&(!query||[p.name,p.goal,p.avoid,p.story,p.uses,...p.keywords].join(" ").toLowerCase().includes(query)));
    document.querySelectorAll("[data-emotion-family]").forEach(b=>b.setAttribute("aria-pressed",String(b.dataset.emotionFamily===family)));
    $("#emotion-results").textContent=profiles.length?"显示 "+profiles.length+" 份档案 · 点击卡片查看完整要求":"未找到匹配档案。可清除搜索，或在下方“本次情绪补充”中描述自己的目标；详情保留上一份。";
    if(profiles.length&&!profiles.some(p=>p.id===current.id)){current=profiles[0];renderProfile();}
    $("#emotion-cards").replaceChildren(...profiles.map(p=>{
      const b=make("button",undefined,"emotion-card");b.type="button";b.dataset.emotionId=p.id;b.setAttribute("aria-pressed",String(current.id===p.id));
      b.append(make("strong",p.name),make("span",p.goal),make("small","避免："+p.avoid));
      b.addEventListener("click",()=>{current=p;renderProfile();document.querySelectorAll("[data-emotion-id]").forEach(el=>el.setAttribute("aria-pressed",String(el.dataset.emotionId===p.id)));$("#emotion-detail").scrollIntoView({behavior:matchMedia("(prefers-reduced-motion: reduce)").matches?"instant":"smooth",block:"start"});});return b;
    }));
  }
  function download(content,type,name) {const url=URL.createObjectURL(new Blob([content],{type})),a=make("a");a.href=url;a.download=name;document.body.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),2000);}
  $("#emotion-search").addEventListener("input",()=>{if(!data)return;if($("#emotion-search").value.trim())family="all";renderCards();});
  $("#emotion-clear").addEventListener("click",()=>{if(!data)return;$("#emotion-search").value="";family="warmth";renderCards();$("#emotion-search").focus();});
  for(const id of ["secondary","level","context"])$("#emotion-"+id).addEventListener(id==="context"?"input":"change",()=>{if(data)updateBrief();});
  $("#emotion-apply").addEventListener("click",()=>{const bundle=brief();editorAcknowledged=false;document.dispatchEvent(new CustomEvent("poster:apply-emotion",{detail:bundle}));if(!editorAcknowledged){$("#emotion-load-status").textContent="原风格编辑器未就绪，可先复制或下载当前情绪指令，刷新后重试载入。";return;}appliedKey=key();editorModified=false;loadedStatus();$("#original-guidance").scrollIntoView({behavior:matchMedia("(prefers-reduced-motion: reduce)").matches?"instant":"smooth",block:"start"});});
  $("#emotion-copy").addEventListener("click",async()=>{try{await navigator.clipboard.writeText(brief().prompt);$("#emotion-copy-status").textContent="已复制当前主／副情绪、视觉要求与返修指令。";}catch{$("#emotion-copy-status").textContent="浏览器未允许复制，可选择下方文本或下载指令。";}});
  $("#emotion-export").addEventListener("click",()=>download(JSON.stringify(brief(),null,2)+"\n","application/json;charset=utf-8",current.id+"-emotion-brief.json"));
  $("#emotion-txt").addEventListener("click",()=>download("\ufeff"+brief().prompt+"\n","text/plain;charset=utf-8",current.id+"-emotion-prompt.txt"));
  $("#emotion-download-all").addEventListener("click",()=>{if(data)download(JSON.stringify(data,null,2)+"\n","application/json;charset=utf-8","emotion-profiles-library.json");});
  document.addEventListener("poster:emotion-cleared",()=>{appliedKey="";editorModified=false;if(data)loadedStatus();});
  document.addEventListener("poster:emotion-state",event=>{editorAcknowledged=true;editorModified=event.detail.modified;if(data)loadedStatus();});
  async function init() {
    try {
      const response=await fetch(asset("emotions/profiles.json"));if(!response.ok)throw new Error("Emotion profiles unavailable");data=await response.json();current=data.profiles[0];
      $("#emotion-families").replaceChildren(...[{id:"all",name:"全部 21"},...data.families].map(f=>{const b=make("button",f.name);b.type="button";b.dataset.emotionFamily=f.id;b.addEventListener("click",()=>{family=f.id;renderCards();});return b;}));
      renderProfile();renderCards();$("#emotion-content").hidden=false;$("#emotion-loading").hidden=true;$("#emotion-download-all").disabled=false;
      document.dispatchEvent(new Event("poster:emotion-library-ready"));
    } catch {$("#emotion-loading").textContent="情绪档案加载失败，请刷新本地 HTTP 页面；完整 JSON 档案仍可通过链接查看。";}
  }
  init();
})();
