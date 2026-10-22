"use strict";

// Original browser illustrations of visual directions. This does not execute the upstream Skill.
(() => {
  const $ = (selector) => document.querySelector(selector);
  const root = $("#extensions");
  if (!root) return;
  const W = 320, H = 420, CW = 1200, CH = 760;
  const styles = [
    {id:"ascii", name:"ASCII 字符", en:"ASCII FIELD", group:"digital", upstream:true, headline:["真实有形", "字符无界"], description:"用字符的疏密和原图色彩，重新描述同一个轮廓。", technique:"读取像素亮度，将不同亮度映射为字符；字符位置可沿流场移动。", prompt:"以 ASCII 字母、数字与符号构成主体轮廓；字符密度跟随明暗，不把文字平铺在主体上。"},
    {id:"pixels", name:"像素马赛克", en:"PIXEL SAMPLING", group:"digital", upstream:true, headline:["把自然", "重新采样"], description:"连续的颜色被拆成离散色块，细节随采样密度变化。", technique:"按网格采样原图颜色，以带间隙的小方块重建画面。", prompt:"让实体局部过渡为大小有秩序的像素色块，保留原图色彩关系和可辨识轮廓。"},
    {id:"voxels", name:"体素方块", en:"VOXEL RELIEF", group:"digital", upstream:false, headline:["以方块", "重建物质"], description:"平面色块获得厚度，呈现浮雕般的方块结构。", technique:"每个采样单元绘制正面、顶面和侧面，用明暗构成 2.5D 厚度；没有建立三维模型。", prompt:"把选定区域重构为具有厚度与光照差异的体素方块，方块沿主体曲面和明暗形成层次。"},
    {id:"particles", name:"粒子点云", en:"PARTICLE CLOUD", group:"digital", upstream:true, headline:["聚散之间", "形态浮现"], description:"颜色成为点，轮廓在消散与聚合之间依然可辨。", technique:"将颜色样本变成圆点，用确定性的位移场与指针斥力移动每个样本。", prompt:"让主体边缘成为带有原色的粒子与点云；粒子的疏密、尺度和轨迹共同维持轮廓。"},
    {id:"wireframe", name:"线框拓扑", en:"CONTOUR NETWORK", group:"digital", upstream:false, headline:["看见轮廓", "读懂结构"], description:"颜色让位于连线与三角网，展示结构化的观察方式。", technique:"连接相邻可见采样点，用亮度偏移模拟起伏；这是二维网格示意，不是几何重建。", prompt:"以线框、三角网络和局部拓扑线描述主体；网络跟随轮廓与透视，保留完整实体到结构线的过渡。"},
    {id:"scan", name:"扫描光谱", en:"SPECTRAL SCAN", group:"digital", upstream:true, headline:["正在扫描", "一朵自然"], description:"扫描带、坐标与网格穿过原图，显现分析标本的语气。", technique:"在原图上绘制移动的扫描带、等间距线和取样坐标；不代表真实仪器测量。", prompt:"让一道扫描光带穿过主体，配合少量坐标、网格与光谱色；避免无意义的界面堆叠。"},
    {id:"glitch", name:"信号故障", en:"SIGNAL FAILURE", group:"digital", upstream:true, headline:["信号之间", "真实闪烁"], description:"横向错位、红青分离和扫描纹理构成受控的信号失真。", technique:"把原图切成水平条带并错位，叠加红青着色副本与 CRT 细线。", prompt:"以局部水平撕裂、受控 RGB 分离和 CRT 扫描纹理表现信号故障，主体与标题仍然可读。"},
    {id:"petals", name:"花瓣重组", en:"PETAL ASSEMBLY", group:"material", upstream:false, headline:["一片花瓣", "另一种生长"], description:"同一批颜色样本变成有方向的花瓣，组成柔软的材料轮廓。", technique:"以弯曲花瓣路径替代采样点，并根据位置与时间旋转；不是模型生成的新物种。", prompt:"让主体局部转化为有方向、层叠且带原图色彩的花瓣；用生长与重组替代机械式像素消散。"},
    {id:"smoke", name:"烟雾消散", en:"VAPOR DISSOLUTION", group:"material", upstream:false, headline:["轮廓散去", "气息留下"], description:"硬边界变成柔和的半透明团簇，沿向上的流场缓缓散开。", technique:"将采样点绘制为缓存的软边径向纹理，并沿正弦流场上移；不做流体求解。", prompt:"让主体边缘化为半透明烟雾，烟雾沿光线与上升气流延展，保留实体与气态之间的清晰关系。"},
    {id:"ink", name:"水墨晕染", en:"INK DIFFUSION", group:"material", upstream:false, headline:["算法落笔", "自然成墨"], description:"明暗转为墨色、笔触与浅淡晕染，保留纸张般的空白。", technique:"按亮度映射墨色，以短笔触和半透明软点叠加出水墨感；不是物理纸张渗透模拟。", prompt:"让主体的部分轮廓转为墨色笔触与水墨晕染，保留纸张留白，让浓淡与虚实描述结构。"},
    {id:"liquid", name:"液态流动", en:"LIQUID WARP", group:"material", upstream:false, headline:["形态流动", "边界松动"], description:"图像在连续波形中弯曲，呈现有黏性的流动与折射。", technique:"逐行偏移原图采样，用连续波形形成弯曲；属于二维图像形变。", prompt:"让主体选定边缘变成连续的液态流动与柔和折射，保持材料连贯、光泽统一，避免随机融化。"},
    {id:"glass", name:"玻璃晶体", en:"REFRACTED FACETS", group:"material", upstream:false, headline:["光穿过", "新的棱面"], description:"图像被切成透明感棱面，局部采样偏移制造折射关系。", technique:"三角切片内偏移采样原图，叠加棱面高光与边线；不使用光线追踪。", prompt:"把主体局部转为透明玻璃与晶体棱面，折射随结构变化，保留原始主体和光线方向。"},
    {id:"weave", name:"织物编织", en:"WOVEN MATTER", group:"material", upstream:false, headline:["经纬交错", "物质重织"], description:"颜色分解成经纬交错的短带，远看仍然组成原始形态。", technique:"用原图色彩绘制横纵短带，根据行列奇偶交换覆盖顺序，模拟编织结构。", prompt:"让主体局部成为经纬交错的织物，纤维色彩来自原图，以编织方向和密度构成形态。"},
  ];
  const canvas = $("#extension-canvas");
  const ctx = canvas.getContext("2d");
  if (!ctx) { $("#extension-status").textContent = "当前浏览器未提供 Canvas 2D，仍可阅读样式说明与组合提示词。"; return; }
  const source = document.createElement("canvas"); source.width=W; source.height=H;
  const sourceCtx = source.getContext("2d", {willReadFrequently:true});
  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
  const state = {style:"particles", source:"flower", sourceLabel:"原创矢量花朵", density:68, amount:88, speed:1, motion:"flow", layout:"specimen", playing:!reducedMotion.matches, time:.6, burst:0, pointer:null, ready:false};
  let pixels, sampleCache = new Map(), tintCache = new Map(), spriteCache = new Map();
  let activeGroup="all", visible=false, raf=0, lastFrame=0, dirty=true, atlasDirty=true, tourTimer=0, loadVersion=0;
  const hash = (n) => { const x=Math.sin(n*127.1+311.7)*43758.5453; return x-Math.floor(x); };
  const color = (p, alpha=1, shade=1) => `rgba(${Math.min(255,p.r*shade)|0},${Math.min(255,p.g*shade)|0},${Math.min(255,p.b*shade)|0},${alpha*p.a})`;
  const selectedStyle = () => styles.find(style=>style.id===state.style);
  const motionNames = {static:"静态", dissolve:"消散", gather:"聚合", flow:"流动", penetrate:"穿透", reform:"重组"};
  const layoutNames = {specimen:"单主体画布", dual:"实体 / 数据双世界", pair:"双主体对话", series:"三联系列"};

  function samples(step) {
    step=Math.max(5,Math.round(step));
    if (sampleCache.has(step)) return sampleCache.get(step);
    const list=[];
    for (let y=step/2|0;y<H;y+=step) for (let x=step/2|0;x<W;x+=step) {
      const k=(y*W+x)*4;
      if (pixels[k+3]<28) continue;
      const p={x,y,r:pixels[k],g:pixels[k+1],b:pixels[k+2],a:pixels[k+3]/255};
      p.l=(p.r*.2126+p.g*.7152+p.b*.0722)/255;
      p.seed=x*17+y*31;
      list.push(p);
    }
    sampleCache.set(step,list); return list;
  }

  function moved(p, t, motion, strength, pointer, burst) {
    let dx=0,dy=0;
    const seed=hash(p.seed), phase=(Math.sin(t*.85)+1)/2;
    const spread=(motion==="dissolve"?phase:motion==="gather"?1-phase:motion==="reform"?Math.pow(phase,4):0)*55*strength;
    dx+=(seed-.35)*spread;dy+=(hash(p.seed+2)-.65)*spread;
    if (motion==="flow") { dx+=Math.sin(t*1.2+p.y*.027)*10*strength;dy+=Math.cos(t+p.x*.025)*6*strength; }
    if (motion==="penetrate") { const band=Math.exp(-Math.pow((p.x-((t*62)%(W+100)-50))/45,2));dx+=band*25*strength;dy+=Math.sin(p.y*.1)*band*10; }
    dx+=(seed-.5)*burst*100;dy+=(hash(p.seed+4)-.5)*burst*85;
    if (pointer) {
      const vx=p.x-pointer.x,vy=p.y-pointer.y,d=Math.hypot(vx,vy);
      if (d<78&&d>.01) { const force=(1-d/78)*34;dx+=vx/d*force;dy+=vy/d*force; }
    }
    return [p.x+dx,p.y+dy];
  }

  function tint(tone) {
    if (!tintCache.has(tone)) {
      const c=document.createElement("canvas");c.width=W;c.height=H;
      const cctx=c.getContext("2d");cctx.drawImage(source,0,0);cctx.globalCompositeOperation="source-in";cctx.fillStyle=tone;cctx.fillRect(0,0,W,H);
      tintCache.set(tone,c);
    }
    return tintCache.get(tone);
  }

  function smokeSprite(p, ink=false) {
    const tone=ink?"ink":`${p.r>>6},${p.g>>6},${p.b>>6}`;
    if (!spriteCache.has(tone)) {
      const c=document.createElement("canvas");c.width=64;c.height=64;const cctx=c.getContext("2d");
      const g=cctx.createRadialGradient(32,32,0,32,32,32);
      const rgb=ink?"53,49,36":`${(p.r>>6)*64+30},${(p.g>>6)*64+30},${(p.b>>6)*64+30}`;
      g.addColorStop(0,`rgba(${rgb},${ink?.22:.48})`);g.addColorStop(.45,`rgba(${rgb},.15)`);g.addColorStop(1,`rgba(${rgb},0)`);
      cctx.fillStyle=g;cctx.fillRect(0,0,64,64);spriteCache.set(tone,c);
    }
    return spriteCache.get(tone);
  }

  function drawStyle(g, style, settings, pointer) {
    const mix=settings.amount/100,t=settings.motion==="static"?0:settings.time,step=Math.round(24-settings.density*.18);
    const list=samples(style.id==="smoke"?step*1.5:step);
    if (mix<.99) {g.save();g.globalAlpha=1-mix;g.drawImage(source,0,0);g.restore();}
    g.save();g.globalAlpha=mix;
    const location=(p)=>moved(p,t,settings.motion,mix,pointer,settings.burst);
    const drawMovingStrips=(height,wave=false)=>{
      for(let y=0;y<H;y+=height){
        const [x,dy]=location({x:W/2,y,seed:y*31});
        const shift=wave?(Math.sin(y*.038+t*1.7)*8+Math.sin(y*.087-t)*4)*mix:0;
        g.drawImage(source,0,y,W,Math.min(height,H-y),x-W/2+shift,dy,W,Math.min(height,H-y));
      }
    };
    if (["ascii","pixels","voxels","particles","petals","smoke","ink","weave"].includes(style.id)) {
      g.textAlign="center";g.textBaseline="middle";g.font=`bold ${step+2}px Consolas,monospace`;
      for (const p of list) {
        const [x,y]=location(p),seed=hash(p.seed);
        if (style.id==="ascii") {
          const chars="@%#*+=-:.";g.fillStyle=color(p,.95,1.12);g.fillText(chars[Math.min(chars.length-1,(p.l*(chars.length-1))|0)],x,y);
        } else if (style.id==="pixels") {
          g.fillStyle=color(p);g.fillRect(x-step*.44,y-step*.44,step*.88,step*.88);
        } else if (style.id==="voxels") {
          const s=step*.82,z=2+p.l*step*.65;
          g.fillStyle=color(p,.95,.6);g.beginPath();g.moveTo(x+s,y);g.lineTo(x+s+z,y-z);g.lineTo(x+s+z,y+s-z);g.lineTo(x+s,y+s);g.fill();
          g.fillStyle=color(p,1,1.2);g.beginPath();g.moveTo(x,y);g.lineTo(x+z,y-z);g.lineTo(x+s+z,y-z);g.lineTo(x+s,y);g.fill();
          g.fillStyle=color(p);g.fillRect(x,y,s,s);
        } else if (style.id==="particles") {
          g.fillStyle=color(p);g.beginPath();g.arc(x,y,Math.max(.8,step*(.12+seed*.2)),0,Math.PI*2);g.fill();
          if (seed>.88) {g.strokeStyle=color(p,.3);g.lineWidth=.5;g.beginPath();g.moveTo(x,y);g.lineTo(x+13,y-8);g.stroke();}
        } else if (style.id==="petals") {
          g.save();g.translate(x,y);g.rotate(seed*Math.PI*2+Math.sin(t+p.y*.03)*.45);g.fillStyle=color(p);g.beginPath();
          g.moveTo(-step*.6,0);g.bezierCurveTo(-step*.1,-step*.6,step*.6,-step*.45,step*.7,0);g.bezierCurveTo(step*.25,step*.4,-step*.3,step*.45,-step*.6,0);g.fill();
          g.strokeStyle=color(p,.45,1.4);g.lineWidth=.5;g.beginPath();g.moveTo(-step*.4,0);g.lineTo(step*.45,0);g.stroke();g.restore();
        } else if (style.id==="smoke") {
          const size=step*(2.4+seed);const rise=Math.sin(t*.5+seed*6)*20;
          g.drawImage(smokeSprite(p),x-size/2+Math.sin(t*.7+p.y*.03)*11,y-size/2-rise,size,size);
        } else if (style.id==="ink") {
          const darkness=.2+(1-p.l)*.75;g.drawImage(smokeSprite(p,true),x-step*1.1,y-step*1.1,step*2.2,step*2.2);
          g.strokeStyle=`rgba(44,43,32,${darkness*p.a})`;g.lineWidth=1+seed*step*.25;g.lineCap="round";g.beginPath();
          g.moveTo(x-step*.33,y+seed*3);g.quadraticCurveTo(x,y-step*.22,x+step*.3,y-step*.15);g.stroke();
          if (seed>.91) {g.fillStyle="rgba(44,43,32,.2)";g.beginPath();g.arc(x+step,y-step,seed*2,0,7);g.fill();}
        } else if (style.id==="weave") {
          const s=step*.92,vertical=(Math.floor(p.x/step)+Math.floor(p.y/step))%2===0;
          g.fillStyle=color(p,.7,.6);g.fillRect(x-s/2,y-s/2,s,s);
          g.fillStyle=color(p,1,1.12);g.fillRect(x-s/2,y-step*.18,s,step*.36);g.fillStyle=color(p,.95,.83);
          if(vertical)g.fillRect(x-step*.18,y-s/2,step*.36,s);
          else {g.fillRect(x-step*.18,y-s/2,step*.36,step*.29);g.fillRect(x-step*.18,y+step*.2,step*.36,step*.29);}
          g.strokeStyle=color(p,.5,1.5);g.lineWidth=.5;g.beginPath();g.moveTo(x-s/2,y-step*.08);g.lineTo(x+s/2,y-step*.08);g.stroke();
        }
      }
    } else if (style.id==="wireframe") {
      const grid=new Map(list.map(p=>[`${p.x},${p.y}`,p]));
      for (const p of list) {
        const [x,y]=location(p);g.strokeStyle=`rgba(133,211,193,${.25+p.l*.65})`;g.lineWidth=.6;
        for(const [dx,dy] of [[step,0],[0,step],[step,step]]) {
          const next=grid.get(`${p.x+dx},${p.y+dy}`);if(!next)continue;const [nx,ny]=location(next);
          g.beginPath();g.moveTo(x,y-p.l*7);g.lineTo(nx,ny-next.l*7);g.stroke();
        }
      }
    } else if (style.id==="scan") {
      drawMovingStrips(Math.max(2,Math.round(step/3)));g.fillStyle="rgba(15,29,23,.32)";g.fillRect(0,0,W,H);
      g.strokeStyle="rgba(165,214,173,.22)";g.lineWidth=.5;
      for(let y=0;y<H;y+=Math.max(3,Math.round(step/2))){g.beginPath();g.moveTo(0,y);g.lineTo(W,y);g.stroke();}
      const scanY=(t*68+100)%(H+60)-30;const gradient=g.createLinearGradient(0,scanY-32,0,scanY+12);
      gradient.addColorStop(0,"rgba(133,245,180,0)");gradient.addColorStop(.85,"rgba(133,245,180,.22)");gradient.addColorStop(1,"rgba(133,245,180,0)");
      g.fillStyle=gradient;g.fillRect(0,scanY-32,W,44);g.strokeStyle="#c5ed8d";g.lineWidth=1.3;g.beginPath();g.moveTo(-12,scanY);g.lineTo(W+12,scanY);g.stroke();
      g.font="8px Consolas,monospace";g.fillStyle="#bdeca6";g.fillText(`y / ${Math.round(scanY)}`,5,Math.max(9,scanY-6));
      g.strokeStyle="rgba(133,211,193,.6)";g.lineWidth=.6;for(const p of samples(step*4)){g.strokeRect(p.x-5,p.y-5,10,10);}
    } else if (style.id==="glitch") {
      g.globalAlpha=mix*.35;g.drawImage(tint("#e94f58"),-5-Math.sin(t*2)*4,0);g.drawImage(tint("#63ceda"),5+Math.cos(t*2)*4,0);g.globalAlpha=mix*.85;
      const strip=Math.max(2,Math.round(step/2));
      for(let y=0;y<H;y+=strip){const d=hash(y+Math.floor(t*7))*mix;const offset=d>.74?(d-.5)*38:0;const [x,dy]=location({x:W/2,y,seed:y*31});g.drawImage(source,0,y,W,Math.min(strip,H-y),x-W/2+offset,dy,W,Math.min(strip,H-y));}
      g.fillStyle="rgba(0,0,0,.3)";for(let y=0;y<H;y+=4)g.fillRect(0,y,W,1);
    } else if (style.id==="liquid") {
      drawMovingStrips(Math.max(1,Math.round(step/4)),true);
      g.strokeStyle="rgba(245,250,226,.3)";g.lineWidth=1.4;
      for(const p of samples(48)){const [x,y]=location(p);g.beginPath();g.moveTo(x-7,y);g.quadraticCurveTo(x,y-6-Math.sin(t)*4,x+9,y-1);g.stroke();}
    } else if (style.id==="glass") {
      const cell=Math.max(16,step*1.5);
      for(const p of samples(cell)) {
        const [mx,my]=location(p);g.save();g.translate(mx-p.x,my-p.y);
        const s=cell*.9,shift=(hash(p.seed)-.5)*(10+Math.sin(t)*3);
        for(let half=0;half<2;half++) {
          g.save();g.beginPath();g.moveTo(p.x-s/2,p.y-s/2);g.lineTo(half?p.x-s/2:p.x+s/2,half?p.y+s/2:p.y-s/2);g.lineTo(p.x+s/2,p.y+s/2);g.closePath();g.clip();
          g.drawImage(source,shift,Math.sin(p.seed)*4);g.fillStyle=half?"rgba(147,210,230,.16)":"rgba(255,255,255,.16)";g.fillRect(p.x-s/2,p.y-s/2,s,s);g.restore();
          g.strokeStyle="rgba(188,230,238,.35)";g.lineWidth=.6;g.beginPath();g.moveTo(p.x-s/2,p.y-s/2);g.lineTo(p.x+s/2,p.y+s/2);g.stroke();
        }
        g.restore();
      }
    }
    g.restore();
  }

  function drawFrame(target, style, settings, thumbnail=false) {
    const g=target.getContext("2d");g.setTransform(target.width/CW,0,0,target.height/CH,0,0);
    const light=style.id==="ink",bg=light?"#ede9dc":"#101912",fg=light?"#303a2a":"#eaf0de",accent=light?"#647550":"#c5ed8d";
    g.clearRect(0,0,CW,CH);g.fillStyle=bg;g.fillRect(0,0,CW,CH);
    g.strokeStyle=light?"rgba(88,99,69,.09)":"rgba(163,190,133,.07)";g.lineWidth=1;
    for(let x=30;x<CW;x+=38){g.beginPath();g.moveTo(x,30);g.lineTo(x,CH-30);g.stroke();}
    for(let y=30;y<CH;y+=38){g.beginPath();g.moveTo(30,y);g.lineTo(CW-30,y);g.stroke();}
    g.textAlign="left";g.textBaseline="alphabetic";g.fillStyle=accent;g.font="15px Consolas,monospace";g.fillText(`STUDY / ${String(styles.indexOf(style)+1).padStart(2,"0")}    ${style.en}`,54,56);
    const drawAt=(x,y,scale,amount=settings.amount,dual=false) => {
      g.save();g.translate(x,y);g.scale(scale,scale);
      const pointer=!thumbnail&&settings.pointer?{x:(settings.pointer.x-x)/scale,y:(settings.pointer.y-y)/scale}:null;
      if(dual){g.drawImage(source,0,0);g.save();const boundary=W*(1-amount/100);g.beginPath();g.rect(boundary,-45,W+90,H+90);g.clip();drawStyle(g,style,{...settings,amount:100},pointer);g.restore();g.strokeStyle=accent;g.lineWidth=.65;g.beginPath();g.moveTo(boundary,0);g.lineTo(boundary,H);g.stroke();}
      else drawStyle(g,style,{...settings,amount},pointer);
      g.restore();
    };
    if(settings.layout==="series") {
      g.fillStyle=fg;g.font='600 34px "Microsoft YaHei",sans-serif';g.fillText(`${style.name} / 三联系列`,54,116);
      for(let i=0;i<3;i++){const x=65+i*375;g.strokeStyle=light?"#ccd0ba":"#3d5035";g.strokeRect(x-14,153,340,510);drawAt(x,175,.96,30+i*35);g.fillStyle=accent;g.font="13px Consolas,monospace";g.fillText(`MATTER → DATA / ${30+i*35}%`,x,640);}
    } else if(settings.layout==="pair") {
      g.fillStyle=fg;g.font='600 34px "Microsoft YaHei",sans-serif';g.fillText(`${style.name} / 实体与材料的对话`,54,116);
      g.save();g.globalAlpha=.9;g.drawImage(source,165,162,330,433);g.restore();drawAt(700,162,1.03);
      g.strokeStyle=accent;g.lineWidth=1;g.beginPath();g.moveTo(520,370);g.lineTo(670,370);g.lineTo(660,364);g.moveTo(670,370);g.lineTo(660,376);g.stroke();
      g.fillStyle=accent;g.font="14px Consolas,monospace";g.fillText("SOURCE",165,638);g.fillText("REINTERPRETATION",700,638);
    } else {
      g.fillStyle=fg;g.font='650 66px "Microsoft YaHei",sans-serif';g.fillText(style.headline[0],54,220);g.fillText(style.headline[1],54,307);
      g.fillStyle=accent;g.font='19px "Microsoft YaHei",sans-serif';g.fillText(style.name,58,376);
      g.font="12px Consolas,monospace";g.fillStyle=light?"#7a806c":"#8d9f7e";g.fillText(settings.layout==="dual"?"INTACT MATTER / COMPUTATIONAL MATTER":"ONE SUBJECT / ANOTHER MATERIAL",58,416);
      drawAt(609,95,1.34,settings.amount,settings.layout==="dual");
      g.strokeStyle=accent;g.lineWidth=1;g.beginPath();g.moveTo(58,558);g.lineTo(120,558);g.stroke();
      g.fillStyle=light?"#647151":"#9db88a";g.font="13px Consolas,monospace";g.fillText(`DENSITY / ${settings.density}   MIX / ${settings.amount}%`,58,590);
    }
    g.fillStyle=light?"#69775a":"#8ba17a";g.font='14px "Microsoft YaHei",sans-serif';g.fillText(`${state.sourceLabel}  ·  ${motionNames[settings.motion]}  ·  ${layoutNames[settings.layout]}`,54,710);
    g.textAlign="right";g.font="12px Consolas,monospace";g.fillText("ORIGINAL CANVAS STUDY / 2026",CW-54,710);g.textAlign="left";
  }

  function requestDraw() {dirty=true;if(!raf&&visible&&!document.hidden)raf=requestAnimationFrame(frame);}
  function frame(now) {
    raf=0;if(!visible||document.hidden||!state.ready)return;
    const delta=Math.min(.08,(now-lastFrame)/1000||.016);
    if(now-lastFrame<33){raf=requestAnimationFrame(frame);return;}
    lastFrame=now;
    if(state.playing)state.time+=delta*state.speed;
    if(state.burst>0)state.burst=Math.max(0,state.burst-delta*.8);
    if(dirty||state.playing||state.burst>0){drawFrame(canvas,selectedStyle(),state);dirty=false;}
    if(state.playing||state.burst>0)raf=requestAnimationFrame(frame);
  }

  function renderStyleButtons() {
    const fragment=document.createDocumentFragment();
    styles.filter(style=>activeGroup==="all"||style.group===activeGroup).forEach(style=>{
      const button=document.createElement("button");button.type="button";button.className="extension-style";button.dataset.extensionStyle=style.id;button.setAttribute("aria-pressed",String(style.id===state.style));
      const number=document.createElement("span");number.textContent=String(styles.indexOf(style)+1).padStart(2,"0");
      const name=document.createElement("b");name.textContent=style.name;const badge=document.createElement("small");badge.textContent=style.upstream?"上游方向":"研究扩展";
      button.append(number,name,badge);button.addEventListener("click",()=>chooseStyle(style.id));fragment.append(button);
    });
    $("#extension-styles").replaceChildren(fragment);
  }

  function chooseStyle(id) {
    state.style=id;const style=selectedStyle();renderStyleButtons();
    $("#extension-active-style").value=id;
    $("#extension-name").textContent=style.name;$("#extension-description").textContent=style.description;$("#extension-technique").textContent=style.technique;
    $("#extension-origin").textContent=style.upstream?"上游风格方向 · 本页原创实时实现":"本次研究新增 · 需补充风格规则";
    canvas.setAttribute("aria-label",`${style.name}算法示意，输入为${state.sourceLabel}。可使用下方控件调节，或点击画面重新聚合。`);canvas.dataset.style=id;
    $("#extension-status").textContent=`已切换到${style.name}。${style.description}`;requestDraw();
  }

  function updateOutputs() {
    $("#extension-density-value").textContent=state.density;
    $("#extension-amount-value").textContent=`${state.amount}%`;
    $("#extension-speed-value").textContent=`${state.speed.toFixed(1)}×`;
    $("#extension-play").textContent=state.playing?"暂停动画":"播放动画";
    $("#extension-play").setAttribute("aria-pressed",String(state.playing));
    $("#extension-source-label").textContent=state.sourceLabel;
    requestDraw();
  }

  const promptSelect=$("#prompt-extension");
  for(const style of styles.filter(style=>style.group==="digital")){const option=document.createElement("option");option.value=style.id;option.textContent=`${style.name}${style.upstream?"":" · 同风格扩展"}`;option.dataset.prompt=style.prompt;promptSelect.append(option);}
  for(const style of styles){const option=document.createElement("option");option.value=style.id;option.textContent=style.name;$("#extension-active-style").append(option);}
  $("#extension-active-style").addEventListener("change",event=>chooseStyle(event.target.value));
  $("#extension-to-prompt").addEventListener("click",()=>{
    const style=styles.find(item=>item.id===state.style);
    if(style.group==="material"){
      $("#direction-method").value=style.id;
      $("#direction-notes").value="材料旁支探索："+style.prompt;
      $("#direction-form").dispatchEvent(new Event("input",{bubbles:true}));
      $("#direction-studio").scrollIntoView({behavior:reducedMotion.matches?"instant":"smooth"});
      $("#direction-method").focus({preventScroll:true});return;
    }
    promptSelect.value=state.style;promptSelect.dispatchEvent(new Event("change",{bubbles:true}));
    $("#prompt-lab").scrollIntoView({behavior:reducedMotion.matches?"instant":"smooth"});promptSelect.focus({preventScroll:true});
  });

  for(const button of root.querySelectorAll("[data-extension-group]"))button.addEventListener("click",()=>{
    activeGroup=button.dataset.extensionGroup;root.querySelectorAll("[data-extension-group]").forEach(item=>item.setAttribute("aria-pressed",String(item===button)));renderStyleButtons();
  });
  for(const [id,key] of [["density","density"],["amount","amount"],["speed","speed"]])$("#extension-"+id).addEventListener("input",event=>{state[key]=Number(event.target.value);updateOutputs();});
  $("#extension-motion").addEventListener("change",event=>{state.motion=event.target.value;requestDraw();});
  $("#extension-layout").addEventListener("change",event=>{state.layout=event.target.value;requestDraw();});
  $("#extension-play").addEventListener("click",()=>{state.playing=!state.playing;updateOutputs();});
  const reassemble=()=>{state.burst=reducedMotion.matches?0:1;state.time=.6;requestDraw();};
  $("#extension-reassemble").addEventListener("click",reassemble);canvas.addEventListener("click",reassemble);
  canvas.addEventListener("pointermove",event=>{
    if(!$("#extension-pointer").checked)return;const box=canvas.getBoundingClientRect();
    state.pointer={x:(event.clientX-box.left)/box.width*CW,y:(event.clientY-box.top)/box.height*CH};requestDraw();
  });
  canvas.addEventListener("pointerleave",()=>{state.pointer=null;requestDraw();});
  $("#extension-pointer").addEventListener("change",()=>{state.pointer=null;requestDraw();});
  window.addEventListener("scroll",()=>{
    if(!$("#extension-scroll").checked)return;
    const box=root.getBoundingClientRect();state.amount=Math.round(Math.max(0,Math.min(100,(-box.top+window.innerHeight*.25)/Math.max(1,box.height-window.innerHeight*.35)*100)));
    $("#extension-amount").value=state.amount;updateOutputs();
  },{passive:true});

  $("#extension-tour").addEventListener("click",()=>{
    if(tourTimer){clearInterval(tourTimer);tourTimer=0;}else{tourTimer=setInterval(()=>{const index=styles.findIndex(style=>style.id===state.style);chooseStyle(styles[(index+1)%styles.length].id);},3000);}
    $("#extension-tour").textContent=tourTimer?"停止巡览":"自动巡览 13 种";$("#extension-tour").setAttribute("aria-pressed",String(Boolean(tourTimer)));
  });
  document.addEventListener("visibilitychange",()=>{
    if(document.hidden){if(raf)cancelAnimationFrame(raf);raf=0;if(tourTimer){clearInterval(tourTimer);tourTimer=0;$("#extension-tour").textContent="自动巡览 13 种";$("#extension-tour").setAttribute("aria-pressed","false");}}
    else{lastFrame=performance.now();requestDraw();}
  });
  new IntersectionObserver(entries=>{visible=entries[0].isIntersecting;if(!visible){if(raf)cancelAnimationFrame(raf);raf=0;}else{lastFrame=performance.now();requestDraw();}},{rootMargin:"120px"}).observe($("#extension-stage"));

  async function loadImage(url) {
    return new Promise((resolve,reject)=>{const image=new Image();image.onload=()=>resolve(image);image.onerror=()=>reject(new Error("图片无法读取"));image.src=url;});
  }
  async function setSource(kind, imageUrl) {
    const version=++loadVersion;
    try {
      const image=await loadImage(imageUrl||(kind==="photo"?"./assets/03-pumpkin-before-after.png":"./assets/study-flower.svg"));
      if(version!==loadVersion)return;
      sourceCtx.clearRect(0,0,W,H);
      const crop=kind==="photo"?[57,268,1305,1450]:[0,0,image.naturalWidth,image.naturalHeight];
      const scale=Math.min((W-12)/crop[2],(H-12)/crop[3]);
      sourceCtx.drawImage(image,...crop,(W-crop[2]*scale)/2,(H-crop[3]*scale)/2,crop[2]*scale,crop[3]*scale);
      pixels=sourceCtx.getImageData(0,0,W,H).data;sampleCache.clear();tintCache.clear();spriteCache.clear();
      state.source=kind;state.sourceLabel=kind==="photo"?"作者示例中的原始照片":kind==="upload"?"你的本地图片":"原创矢量花朵";state.ready=true;atlasDirty=true;
      root.querySelectorAll("[data-extension-source]").forEach(button=>button.setAttribute("aria-pressed",String(button.dataset.extensionSource===kind)));
      updateOutputs();chooseStyle(state.style);if($("#extension-atlas").open)renderAtlas();
    }catch(error){$("#extension-status").textContent="图片读取失败。可切回原创花朵，或选择 PNG、JPEG、WebP 图片。";}
  }
  root.querySelectorAll("[data-extension-source]").forEach(button=>button.addEventListener("click",()=>setSource(button.dataset.extensionSource)));
  $("#extension-upload").addEventListener("change",async event=>{
    const file=event.target.files[0];if(!file)return;
    if(!["image/png","image/jpeg","image/webp"].includes(file.type)||file.size>10*1024*1024){$("#extension-status").textContent="请选择不超过 10 MB 的 PNG、JPEG 或 WebP 图片。";event.target.value="";return;}
    const url=URL.createObjectURL(file);try{await setSource("upload",url);}finally{URL.revokeObjectURL(url);event.target.value="";}
  });

  $("#extension-export").addEventListener("click",()=>{
    if(!state.ready)return;
    drawFrame(canvas,selectedStyle(),state);
    canvas.toBlob(blob=>{
      if(!blob){$("#extension-status").textContent="PNG 导出失败，请重试。";return;}
      const url=URL.createObjectURL(blob),link=document.createElement("a");link.href=url;link.download=`sublime-${state.style}.png`;document.body.append(link);link.click();link.remove();setTimeout(()=>URL.revokeObjectURL(url),2000);
      $("#extension-status").textContent=`已准备下载 ${selectedStyle().name} 的当前算法示意，1200 × 760 PNG。`;
    },"image/png");
  });

  function renderAtlas() {
    if(!state.ready||!atlasDirty)return;
    const fragment=document.createDocumentFragment();
    for(const style of styles){
      const button=document.createElement("button");button.type="button";button.className="atlas-item";button.dataset.atlasStyle=style.id;
      const preview=document.createElement("canvas");preview.width=600;preview.height=380;preview.setAttribute("aria-hidden","true");
      drawFrame(preview,style,{...state,motion:"static",time:.6,pointer:null,burst:0,layout:"specimen",amount:100,density:76},true);
      const caption=document.createElement("span");caption.textContent=`${String(styles.indexOf(style)+1).padStart(2,"0")} / ${style.name}`;
      button.append(preview,caption);button.addEventListener("click",()=>{chooseStyle(style.id);$("#extension-stage").scrollIntoView({behavior:reducedMotion.matches?"instant":"smooth"});});fragment.append(button);
    }
    $("#extension-atlas-grid").replaceChildren(fragment);atlasDirty=false;
  }
  $("#extension-atlas").addEventListener("toggle",()=>{if($("#extension-atlas").open)renderAtlas();});
  renderStyleButtons();updateOutputs();chooseStyle(state.style);setSource("flower");
})();
