'use strict';
(() => {
  const data = window.FOREST_RESEARCH;
  const $ = id => document.getElementById(id);
  const sourceUrl = path => `${data.repository}/blob/${data.commit}/${path}`;
  document.querySelectorAll('[data-source]').forEach(link => {
    link.href = sourceUrl(link.dataset.source); link.target = '_blank'; link.rel = 'noopener';
  });
  $('capabilityGrid').innerHTML = data.capabilities.map((item,i) => `<article class="capability"><span class="cap-icon" aria-hidden="true">${item.icon}</span><span class="cap-no">0${i+1}</span><h3>${item.title}</h3><p>${item.text}</p></article>`).join('');
  $('shotTimeline').innerHTML = data.shots.map(shot => `<div class="shot" style="--duration:${shot.duration}"><span>${shot.time}</span><strong>${shot.name}</strong></div>`).join('');
  $('pipeline').innerHTML = data.pipeline.map((step,i) => `<article><span class="pipe-number">0${i+1}</span><div class="pipe-symbol" aria-hidden="true">${step.symbol}</div><h3>${step.title}</h3><p>${step.text}</p><span class="pipe-label">${step.label}</span></article>`).join('');
  $('valueGrid').innerHTML = data.values.map(item => `<article class="value-card"><span class="eyebrow">${item.tag}</span><h3>${item.title}</h3><p>${item.text}</p><dl><dt>可借鉴</dt><dd>${item.reuse}</dd><dt>还需要</dt><dd>${item.cost}</dd></dl></article>`).join('');
  $('sourceGrid').innerHTML = data.sources.map(([title,path]) => `<a href="${sourceUrl(path)}" target="_blank" rel="noopener">${title} ↗<span>${path}</span></a>`).join('');

  function tabKeyboard(container, activate) {
    container.addEventListener('keydown', event => {
      const buttons = [...container.querySelectorAll('[role=tab]')];
      const index = buttons.indexOf(document.activeElement);
      if (index < 0) return;
      let next;
      if(event.key === 'ArrowRight') next = (index+1)%buttons.length;
      if(event.key === 'ArrowLeft') next = (index-1+buttons.length)%buttons.length;
      if(event.key === 'Home') next = 0;
      if(event.key === 'End') next = buttons.length-1;
      if(next === undefined) return;
      event.preventDefault(); activate(next); buttons[next].focus();
    });
  }

  let galleryIndex = 0;
  $('galleryTabs').innerHTML = data.gallery.map((image,i) => `<button class="gallery-tab" id="galleryTab${i}" data-image="${i}" role="tab" aria-selected="false" aria-controls="galleryImagePanel" tabindex="-1"><span>${image.tag}</span><strong>${image.title}</strong><p>${image.text}</p></button>`).join('');
  const galleryFigure = $('galleryImage').closest('figure');
  galleryFigure.id = 'galleryImagePanel'; galleryFigure.setAttribute('role','tabpanel');
  function setGallery(index) {
    galleryIndex = index;
    const image = data.gallery[index];
    $('galleryImage').src = image.src; $('galleryImage').alt = image.alt;
    $('galleryCaption').textContent = image.caption;
    galleryFigure.setAttribute('aria-labelledby',`galleryTab${index}`);
    $('enlargeImage').setAttribute('aria-label',`放大截图：${image.title}`);
    document.querySelectorAll('.gallery-tab').forEach((button,i) => {
      button.classList.toggle('active',i===index); button.setAttribute('aria-selected',String(i===index)); button.tabIndex = i===index?0:-1;
    });
  }
  $('galleryTabs').addEventListener('click', event => {const button = event.target.closest('[data-image]'); if(button) setGallery(Number(button.dataset.image));});
  tabKeyboard($('galleryTabs'),setGallery); setGallery(0);

  const dialog = $('imageDialog'); let dialogMode = 'gallery';
  function updateDialog() {
    const isGallery = dialogMode === 'gallery';
    const image = isGallery ? data.gallery[galleryIndex] : dialogMode === 'overview' ? {src:'assets/understanding-overview.png',alt:'Verdant Forest 能力、效果、原理与四类复用价值的研究总结图',title:'Verdant Forest · 自然场景的制作与运行能力'} : {src:'assets/upstream/bark-comparison.jpg',alt:'上游白桦树皮离线材质对照：改进前、改进后与另一棵树',title:'树皮材质：从重复横纹到连续变化'};
    $('dialogImage').src = image.src; $('dialogImage').alt = image.alt;
    $('dialogCaption').textContent = isGallery ? `${image.title} · ${image.caption}` : image.title;
    $('previousImage').hidden = !isGallery; $('nextImage').hidden = !isGallery;
    dialog.querySelector('.dialog-footer span').textContent = isGallery ? '方向键切换 · Esc 关闭' : dialogMode === 'overview' ? '研究总结图 · Esc 关闭' : '上游离线对照图 · Esc 关闭';
  }
  function openDialog(mode) {dialogMode=mode; updateDialog();dialog.showModal();document.body.classList.add('dialog-open');}
  $('enlargeImage').addEventListener('click',()=>openDialog('gallery'));
  $('enlargeBark').addEventListener('click',()=>openDialog('bark'));
  $('enlargeOverview').addEventListener('click',()=>openDialog('overview'));
  $('closeDialog').addEventListener('click',()=>dialog.close());
  dialog.addEventListener('close',()=>document.body.classList.remove('dialog-open'));
  dialog.addEventListener('click',event=>{if(event.target===dialog)dialog.close();});
  function stepImage(direction) {setGallery((galleryIndex+direction+data.gallery.length)%data.gallery.length);updateDialog();}
  $('previousImage').addEventListener('click',()=>stepImage(-1));$('nextImage').addEventListener('click',()=>stepImage(1));
  dialog.addEventListener('keydown',event=>{if(dialogMode!=='gallery')return;if(event.key==='ArrowRight'){event.preventDefault();stepImage(1);}if(event.key==='ArrowLeft'){event.preventDefault();stepImage(-1);}});

  let liveMode='explore',liveFrame=null,liveTimer=0;
  const originalUrl = () => 'https://verdant-forest.lexn8.chatgpt.site/'+(liveMode==='cinematic'?'?cinematic=1':'');
  function stopOriginal(focus=false) {
    clearTimeout(liveTimer); liveFrame?.remove(); liveFrame=null;
    $('liveCover').hidden=false;$('fullscreenForest').hidden=true;$('stopForest').hidden=true;
    $('liveStatus').textContent='原版已停止，释放其页面与图形资源。可以再次载入。';
    if(focus)$('loadForest').focus();
  }
  function loadOriginal() {
    if(liveFrame)return;
    $('liveCover').hidden=true;$('liveStatus').textContent='正在打开作者托管的原版页面。首次构建森林可能需要一些时间。';
    liveFrame=document.createElement('iframe');liveFrame.title=liveMode==='cinematic'?'Verdant Forest 上游原版：30 秒自动导览':'Verdant Forest 上游原版：自由漫游';
    liveFrame.allow='fullscreen';liveFrame.allowFullscreen=true;liveFrame.referrerPolicy='strict-origin-when-cross-origin';
    liveFrame.addEventListener('load',()=>{$('liveStatus').textContent='已打开上游页面。点击画面操作；若未正常渲染，可使用“新窗口打开原版”。';});
    liveFrame.addEventListener('error',()=>{$('liveStatus').textContent='嵌入页面未能正常打开，请使用“新窗口打开原版”。';});
    liveFrame.src=originalUrl();$('frameMount').append(liveFrame);
    $('stopForest').hidden=false;$('fullscreenForest').hidden=!document.fullscreenEnabled;
    liveTimer=setTimeout(()=>{if(liveFrame)$('liveStatus').textContent='原版在上方独立运行。若停在加载画面或提示不支持 3D，请使用新窗口并检查 WebGL 2 支持。';},20000);
  }
  document.querySelectorAll('[data-live-mode]').forEach(button=>button.addEventListener('click',()=>{
    if(button.dataset.liveMode===liveMode)return;
    const wasRunning=Boolean(liveFrame);if(wasRunning)stopOriginal();liveMode=button.dataset.liveMode;
    document.querySelectorAll('[data-live-mode]').forEach(item=>{const active=item===button;item.classList.toggle('active',active);item.setAttribute('aria-pressed',String(active));});
    $('openOriginal').href=originalUrl();
    $('liveTitle').textContent=liveMode==='cinematic'?'跟随光线，穿过森林':'走进这片森林';
    $('liveDescription').textContent=liveMode==='cinematic'?'五个预设镜头，30 秒循环，观察花草、枯木和树冠。':'载入上游原版，鼠标控制视角，WASD 移动。';
    if(wasRunning)loadOriginal();
  }));
  $('loadForest').addEventListener('click',loadOriginal);$('stopForest').addEventListener('click',()=>stopOriginal(true));
  $('fullscreenForest').addEventListener('click',async()=>{try{await $('liveStage').requestFullscreen();}catch{$('liveStatus').textContent='当前浏览器未允许全屏，可使用新窗口体验。';}});
  $('exitFullscreenForest').addEventListener('click',async()=>{try{await document.exitFullscreen();}catch{$('liveStatus').textContent='请使用浏览器的退出全屏操作返回研究页面。';}});

  // Independent explanatory drawings. These do not execute upstream shaders or measure GPU performance.
  const canvas=$('labCanvas'),ctx=canvas.getContext('2d');
  let labIndex=0,labValue=48,visible=false,frame=0,lastTime=0,time=0;
  const motion=matchMedia('(prefers-reduced-motion: reduce)');let paused=motion.matches;
  const animated=()=>['wind','geometry'].includes(data.labs[labIndex].id);
  $('labTabs').innerHTML=data.labs.map((lab,i)=>`<button class="lab-tab" id="labTab${i}" role="tab" data-lab="${i}" aria-selected="false" aria-controls="labPanel" tabindex="-1"><span>0${i+1}</span>${lab.label}</button>`).join('');
  function setLab(index){
    labIndex=index;const lab=data.labs[index];labValue=lab.initial;
    $('labPanel').setAttribute('aria-labelledby',`labTab${index}`);
    $('labNumber').textContent=`0${index+1}`;$('labTitle').textContent=lab.title;$('labText').textContent=lab.text;
    $('labVisualLabel').textContent=lab.english;$('labRangeLabel').textContent=lab.range;
    $('labRange').min=lab.min;$('labRange').max=lab.max;$('labRange').value=lab.initial;
    $('rangeMin').textContent=lab.ends[0];$('rangeMax').textContent=lab.ends[1];$('labInsight').textContent=lab.insight;$('labSource').href=sourceUrl(lab.source);
    $('labRange').setAttribute('aria-label',lab.range);
    $('labTabs').querySelectorAll('button').forEach((button,i)=>{button.classList.toggle('active',i===index);button.setAttribute('aria-selected',String(i===index));button.tabIndex=i===index?0:-1;});
    updatePause();updateReadout();schedule();
  }
  function updatePause(){$('pauseLab').disabled=!animated();$('pauseLab').textContent=!animated()?'静态示意':paused?'播放演示':'暂停演示';$('pauseLab').setAttribute('aria-pressed',String(paused));}
  function updateReadout(){
    const lab=data.labs[labIndex];$('labRangeValue').textContent=labValue+lab.unit;
    const values={terrain:['4 层起伏叠加','改变网格顶点的高度'],geometry:['96 个三角形','本页教学叶片 · 可见曲面结构'],instances:[`${labValue} 株 / 3 种树形`,'位置、尺寸和色调各不相同'],wind:[labValue===0?'风静止了':'时间 × 相位 × 高度','同一株协调，不同株错开'],lod:[labValue<24?'高细节 / 8 面':labValue<56?'中细节 / 4 面':'低细节 / 2 面','代表叶片 · 桌面 quality = 1']};
    $('labMetric').textContent=values[lab.id][0];$('labMetricNote').textContent=values[lab.id][1];
    canvas.setAttribute('aria-label',`${lab.label}教学示意，${lab.range} ${labValue}${lab.unit}。${values[lab.id][0]}。${lab.insight}`);
  }
  $('labTabs').addEventListener('click',event=>{const button=event.target.closest('[data-lab]');if(button)setLab(Number(button.dataset.lab));});
  tabKeyboard($('labTabs'),setLab);
  $('labRange').addEventListener('input',event=>{labValue=Number(event.target.value);updateReadout();draw();});
  $('showMesh').addEventListener('change',draw);
  $('pauseLab').addEventListener('click',()=>{paused=!paused;updatePause();schedule();});
  motion.addEventListener('change',()=>{paused=motion.matches;updatePause();schedule();});
  function hash(n){const v=Math.sin(n*127.1+311.7)*43758.5453;return v-Math.floor(v);}
  function polygon(points,fill,stroke){ctx.beginPath();points.forEach(([x,y],i)=>i?ctx.lineTo(x,y):ctx.moveTo(x,y));ctx.closePath();if(fill){ctx.fillStyle=fill;ctx.fill();}if(stroke){ctx.strokeStyle=stroke;ctx.lineWidth=.8;ctx.stroke();}}
  function line(points,color,width=1){ctx.beginPath();points.forEach(([x,y],i)=>i?ctx.lineTo(x,y):ctx.moveTo(x,y));ctx.strokeStyle=color;ctx.lineWidth=width;ctx.stroke();}
  function text(message,x,y,size=12,color='#a9bc96',align='left'){ctx.fillStyle=color;ctx.font=`${size*(canvas.getBoundingClientRect().width<450?1.7:1)}px "Segoe UI", "Microsoft YaHei", sans-serif`;ctx.textAlign=align;ctx.fillText(message,x,y);}
  function drawTerrain(){
    const n=28,m=23,amp=labValue/100;
    const point=(i,j)=>{const x=i/n*6,z=j/m*6;const h=(Math.sin(x*.85+z*.45)*.53+Math.cos(z*2+x*.34)*.27+Math.sin(x*4+z*2.6)*.13+Math.cos(x*7-z*5)*.07)*amp;return [460+(i-j-2.5)*14.2,255+(i+j)*5.6-h*130];};
    for(let j=0;j<m;j++)for(let i=0;i<n;i++){
      const p=point(i,j),q=point(i+1,j),r=point(i+1,j+1),s=point(i,j+1);
      const shade=35+Math.round(16*hash(i+j*31)+amp*8);
      polygon([p,q,r],`hsl(94,22%,${shade}%)`,$('showMesh').checked?'#b2cd8a65':null);
      polygon([p,r,s],`hsl(99,20%,${shade-5}%)`,$('showMesh').checked?'#b2cd8a65':null);
    }
    line([[100,506],[460,630],[810,490]],'#95b77c66');
    text('大尺度坡地 + 中尺度起伏 + 微小凹凸',460,116,15,'#c5d6b3','center');
    text('同一套高度，决定地面和植被的落点',460,555,12,'#93aa80','center');
  }
  function projectLeaf(point,fold,angle=0){
    const [s,t]=point,w=Math.pow(Math.sin(Math.PI*t),.78)*140,x=s*w,y=(t-.5)*490;
    const z=fold*(70*Math.sin(Math.PI*t)*(1-Math.abs(s))-105*t*t+45*s*t);
    const yaw=.65+angle;const rx=x*Math.cos(yaw)+z*Math.sin(yaw),depth=-x*Math.sin(yaw)+z*Math.cos(yaw);
    return [460+rx*.92+y*.48,325+y*.60-rx*.35-depth*.57];
  }
  function leafMesh(fold,level='teaching'){
    let faces=[];
    if(level==='teaching')for(let j=0;j<12;j++)for(let i=0;i<4;i++){const s=-1+i*.5,t=j/12;faces.push([[s,t],[s+.5,t],[s+.5,t+1/12]],[[s,t],[s+.5,t+1/12],[s,t+1/12]]);}
    else if(level==='high'){
      const a=[0,0],b=[-1,.32],c=[0,.32],d=[1,.32],e=[-1,.68],f=[0,.68],g=[1,.68],h=[0,1];
      faces=[[a,b,c],[a,c,d],[b,e,c],[c,e,f],[c,f,d],[d,f,g],[e,h,f],[f,h,g]];
    }else if(level==='medium'){
      const a=[0,0],b=[-1,.5],c=[0,.5],d=[1,.5],e=[0,1];faces=[[a,b,c],[a,c,d],[b,e,c],[c,e,d]];
    }else faces=[[[0,0],[-1,.5],[1,.5]],[[-1,.5],[0,1],[1,.5]]];
    const angle=level==='teaching'?Math.sin(time*.28)*.25:0;
    faces.forEach((face,i)=>{const t=face.reduce((sum,p)=>sum+p[1],0)/3,s=face.reduce((sum,p)=>sum+p[0],0)/3;polygon(face.map(p=>projectLeaf(p,fold,angle)),`hsl(${83+t*12},${29+fold*10}%,${43+t*8-s*9+fold*Math.sin(i)*3}%)`,$('showMesh').checked?'#e1f2b989':null);});
    line(Array.from({length:25},(_,i)=>projectLeaf([0,i/24],fold,angle)),'#e3eab58a',1.2);
    const base=projectLeaf([0,0],fold,angle);line([[base[0]-14,base[1]-25],base],'#c2c78f',2);
  }
  function drawGeometry(){
    ctx.save();ctx.translate(0,15);leafMesh(labValue/100);ctx.restore();
    line([[216,480],[665,480]],'#b1c58c33');
    text('弯曲 · 中脊 · 扭转',460,112,15,'#c5d6b3','center');
    text('每条结构线，都连接着真实的顶点',460,550,12,'#96ad83','center');
  }
  function miniTree(x,y,s,variant,tone){
    ctx.save();ctx.translate(x,y);ctx.scale(s,s);
    ctx.fillStyle='#0c170f44';ctx.beginPath();ctx.ellipse(4,3,21,6,0,0,Math.PI*2);ctx.fill();
    line([[0,0],[1,-48]],'#8a9370',2.8);
    const colors=[`hsl(85,29%,${37+tone}%)`,`hsl(103,24%,${43+tone}%)`,`hsl(77,31%,${40+tone}%)`];
    if(variant===0){polygon([[-22,-30],[0,-79],[24,-30]],colors[0],$('showMesh').checked?'#b3cc8460':null);polygon([[-25,-18],[0,-63],[25,-18]],colors[0],null);}
    else{for(let k=0;k<4;k++){ctx.fillStyle=colors[variant];ctx.beginPath();ctx.ellipse((hash(k+variant*21)-.5)*23,-39-k*6,19-variant*2,16+variant*2,k*.5,0,Math.PI*2);ctx.fill();if($('showMesh').checked){ctx.strokeStyle='#c9e0a24a';ctx.lineWidth=.7;ctx.stroke();}}}
    ctx.restore();
  }
  function drawInstances(){
    const count=Math.round(labValue),items=Array.from({length:count},(_,i)=>({x:100+hash(i*3+2)*700,y:145+hash(i*3+9)*350,s:.56+hash(i*3+17)*.7,v:i%3,tone:(hash(i+7)-.5)*14}));
    for(let j=0;j<10;j++)line([[90,170+j*35],[830,170+j*35]],'#93af7430');
    items.sort((a,b)=>a.y-b.y).forEach(item=>miniTree(item.x,item.y,item.s,item.v,item.tone));
    text('共享树形 + 实例变换 = 一片森林',460,106,15,'#c5d6b3','center');
    text('此图为批量摆放示意，未运行 GPU 实例化',460,554,12,'#93aa80','center');
  }
  function drawWind(){
    const strength=labValue/100;
    for(let row=0;row<3;row++){
      ctx.globalAlpha=.45+row*.25;
      for(let i=0;i<9;i++){
        const x=110+i*87+hash(i+row*11)*12,y=365+row*65,h=95+hash(i*3+row*13)*105;
        const phase=x*.013+row*2,wave=(Math.sin(time*1.25+phase)+.36*Math.sin(time*2.17+phase*1.47));
        const bend=wave*strength*42,tipX=x+bend;
        ctx.beginPath();ctx.moveTo(x,y);ctx.quadraticCurveTo(x+bend*.12,y-h*.6,tipX,y-h);ctx.strokeStyle='#b6c491';ctx.lineWidth=1.5;ctx.stroke();
        for(let k=1;k<7;k++){
          const t=k/7,l=24*Math.sin(t*Math.PI)+7,cy=y-h*t,cx=x+bend*t*t;
          for(const side of [-1,1]){const flutter=Math.sin(time*4.3+i*1.7+k)*strength*3;polygon([[cx,cy],[cx+side*l,cy-12+flutter],[cx+side*l*.6,cy+2],[cx,cy+3]],side<0?'#6e9650':'#94b46a',$('showMesh').checked?'#d5e7ae55':null);}
        }
      }
    }
    ctx.globalAlpha=1;text('根部稳住，越靠近叶尖越灵活',460,112,15,'#c5d6b3','center');
    text('sin(时间 × 频率 + 位置相位) × 高度权重',460,555,12,'#93aa80','center');
  }
  function drawLod(){
    const d=labValue,level=d<24?'high':d<56?'medium':'low';leafMesh(.67,level);
    const start=180,length=560,y=526;
    line([[start,y],[start+length,y]],'#6c8758',2);
    [0,24,56,100].forEach(v=>{line([[start+v/100*length,y-5],[start+v/100*length,y+5]],'#8fa976');text(v+' m',start+v/100*length,y+25,11,'#9db68b','center');});
    ctx.fillStyle='#dfefa4';ctx.beginPath();ctx.arc(start+d/100*length,y,6,0,Math.PI*2);ctx.fill();
    text('保留轮廓，降低远处的结构复杂度',460,112,15,'#c5d6b3','center');
  }
  function draw(){
    if(!ctx)return;
    const rect=canvas.getBoundingClientRect();if(!rect.width||!rect.height)return;
    const ratio=Math.min(devicePixelRatio||1,2),pw=Math.round(rect.width*ratio),ph=Math.round(rect.height*ratio);
    if(canvas.width!==pw||canvas.height!==ph){canvas.width=pw;canvas.height=ph;}
    ctx.setTransform(1,0,0,1,0,0);ctx.clearRect(0,0,pw,ph);
    const scale=Math.min(pw/920,ph/650);ctx.translate((pw-920*scale)/2,(ph-650*scale)/2);ctx.scale(scale,scale);
    const functions={terrain:drawTerrain,geometry:drawGeometry,instances:drawInstances,wind:drawWind,lod:drawLod};functions[data.labs[labIndex].id]();
  }
  function tick(now){frame=0;const dt=lastTime?Math.min((now-lastTime)/1000,.05):0;lastTime=now;if(visible&&!document.hidden&&!paused&&animated())time+=dt;draw();if(visible&&!document.hidden&&!paused&&animated())frame=requestAnimationFrame(tick);}
  function schedule(){if(frame)cancelAnimationFrame(frame);frame=0;lastTime=0;draw();if(visible&&!document.hidden&&!paused&&animated())frame=requestAnimationFrame(tick);}
  new ResizeObserver(draw).observe(canvas);
  new IntersectionObserver(entries=>{visible=entries[0].isIntersecting;schedule();},{threshold:.05}).observe(canvas);
  document.addEventListener('visibilitychange',schedule);
  setLab(0);
})();
