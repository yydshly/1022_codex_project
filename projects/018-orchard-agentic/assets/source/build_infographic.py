from pathlib import Path
from functools import lru_cache
from xml.sax.saxutils import escape
import math
import json
from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).resolve().parent
W, H, SCALE = 2400, 5480, 2
M, GAP = 92, 28
CW = W - M * 2
C = {
    'bg': '#F3F6FB', 'white': '#FFFFFF', 'ink': '#172D47',
    'muted': '#53677F', 'line': '#DCE5EF', 'navy': '#112B46',
    'teal': '#087F76', 'teal_bg': '#E5F5F1',
    'blue': '#325CD5', 'blue_bg': '#EAF0FF',
    'purple': '#7650B9', 'purple_bg': '#F0EAFA',
    'amber': '#9F6714', 'amber_bg': '#FFF3DC',
}
FONTS = {'regular': r'C:\Windows\Fonts\msyh.ttc', 'bold': r'C:\Windows\Fonts\msyhbd.ttc'}

@lru_cache(None)
def font(size, bold=False, scaled=False):
    return ImageFont.truetype(FONTS['bold' if bold else 'regular'], round(size * (SCALE if scaled else 1)))

im = Image.new('RGB', (W * SCALE, H * SCALE), C['bg'])
d = ImageDraw.Draw(im)
svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="title desc">',
       '<title id="title">一图读懂 Orchard-Agentic</title>',
       '<desc id="desc">项目定位、工作原理、十二项沙箱能力、评测与训练、Docker 对比、使用价值、作者报告的效果与能力边界。</desc>',
       '<style>text{font-family:"Microsoft YaHei","Noto Sans CJK SC",sans-serif}</style>',
       f'<rect width="{W}" height="{H}" fill="{C["bg"]}"/>']
checks = []

def rect(x, y, w, h, fill, radius=24, stroke=None, sw=1):
    coords = tuple(round(v * SCALE) for v in (x, y, x+w, y+h))
    d.rounded_rectangle(coords, radius=round(radius*SCALE), fill=fill, outline=stroke, width=max(1,round(sw*SCALE)))
    svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" fill="{fill}"'+(f' stroke="{stroke}" stroke-width="{sw}"' if stroke else '')+'/>')

def line(points, color, width=3, dashed=False):
    pts = [(round(x*SCALE),round(y*SCALE)) for x,y in points]
    if dashed:
        for (x1,y1),(x2,y2) in zip(points,points[1:]):
            dist=math.hypot(x2-x1,y2-y1)
            for t in range(0, math.ceil(dist), 18):
                a=t/max(dist,1); b=min(t+10,dist)/max(dist,1)
                d.line((round((x1+(x2-x1)*a)*SCALE),round((y1+(y2-y1)*a)*SCALE),round((x1+(x2-x1)*b)*SCALE),round((y1+(y2-y1)*b)*SCALE)),fill=color,width=round(width*SCALE))
    else:
        d.line(pts, fill=color, width=round(width*SCALE), joint='curve')
    svg.append('<polyline points="'+' '.join(f'{x},{y}' for x,y in points)+f'" fill="none" stroke="{color}" stroke-width="{width}" stroke-linejoin="round"'+(' stroke-dasharray="10 8"' if dashed else '')+'/>')

def arrow(points, color, width=4, dashed=False, both=False):
    line(points,color,width,dashed)
    def head(a,b):
        ang=math.atan2(b[1]-a[1],b[0]-a[0]); ln=15; aw=8
        p=[b,(b[0]-ln*math.cos(ang)+aw*math.sin(ang),b[1]-ln*math.sin(ang)-aw*math.cos(ang)),(b[0]-ln*math.cos(ang)-aw*math.sin(ang),b[1]-ln*math.sin(ang)+aw*math.cos(ang))]
        d.polygon([(round(x*SCALE),round(y*SCALE)) for x,y in p],fill=color)
        svg.append('<polygon points="'+' '.join(f'{x:.1f},{y:.1f}' for x,y in p)+f'" fill="{color}"/>')
    head(points[-2],points[-1])
    if both: head(points[1],points[0])

def text(x,y,s,size=30,color=None,bold=False,align='left',maxw=None):
    color=color or C['ink']; f=font(size,bold)
    tw=f.getlength(s)
    if maxw is not None:
        checks.append({'text':s,'width':round(tw,1),'allowed':round(maxw,1),'ok':tw<=maxw+1})
        if tw>maxw+1: raise ValueError(f'Text overflow {tw}>{maxw}: {s}')
    if align=='center': x-=tw/2
    elif align=='right': x-=tw
    baseline=y+f.getmetrics()[0]
    d.text((round(x*SCALE),round(baseline*SCALE)),s,font=font(size,bold,True),fill=color,anchor='ls')
    svg.append(f'<text x="{x:.2f}" y="{baseline:.2f}" font-size="{size}" font-weight="{700 if bold else 400}" fill="{color}" xml:space="preserve">{escape(s)}</text>')
    return tw

def wrap(s,size,maxw,bold=False):
    result=[]; f=font(size,bold)
    for para in s.split('\n'):
        if not para: result.append(''); continue
        current=''
        for ch in para:
            if current and f.getlength(current+ch)>maxw:
                result.append(current); current=ch
            else: current+=ch
        if current: result.append(current)
    return result

def para(x,y,s,size=30,color=None,bold=False,maxw=1000,leading=None):
    leading=leading or round(size*1.48)
    lines=wrap(s,size,maxw,bold)
    for i,v in enumerate(lines): text(x,y+i*leading,v,size,color,bold,maxw=maxw)
    return y+len(lines)*leading

def section(y,number,title,note=None):
    rect(M,y+6,70,54,C['navy'],16)
    text(M+35,y+10,number,31,C['white'],True,'center')
    text(M+94,y,title,44,bold=True)
    if note: text(W-M,y+16,note,25,C['muted'],align='right')

def pill(x,y,w,label,color,bg,size=29,h=62):
    rect(x,y,w,h,bg,20)
    text(x+w/2,y+(h-size*1.35)/2-2,label,size,color,True,'center',maxw=w-(12 if w<80 else 28))

def bullet(x,y,label,width,size=30,color=None):
    rect(x,y+15,9,9,color or C['teal'],4)
    return para(x+26,y,label,size,maxw=width-26,leading=44)

# Header: typography and a small container motif, without product logos.
rect(0,0,W,360,C['navy'],0)
text(M,44,'一图读懂 Orchard-Agentic',88,C['white'],True,maxw=2050)
text(M,166,'面向 AI Agent 的容器沙箱、批量评测与训练研究体系',38,'#D7E5F3',maxw=2100)
text(M,235,'独立执行环境  +  Agent 工具  +  批量管理服务',48,'#7CE0D0',True,maxw=2100)
text(M,307,'Orchard Env 是沙箱底座；整个仓库还包含评测、训练配方与研究数据。',28,'#D7E5F3',maxw=2200)

# 01: Separate model, harness and environment.
section(400,'01','先分清：谁负责什么？')
role_w=680
for x,title,desc,col,bg,index in [
    (92,'大模型','判断下一步做什么',C['purple'],C['purple_bg'],'决策'),
    (860,'Agent 框架','组织任务、上下文与工具调用',C['blue'],C['blue_bg'],'组织'),
    (1628,'Orchard Env','提供环境，执行操作，返回结果',C['teal'],C['teal_bg'],'执行')]:
    rect(x,484,role_w,190,C['white'],24,C['line'])
    pill(x+26,506,100,index,col,bg,25,48)
    text(x+150,505,title,42,col,True,maxw=role_w-180)
    text(x+30,589,desc,31,maxw=role_w-60)
arrow([(786,572),(846,572)],C['muted'],3,both=True)
arrow([(1554,572),(1614,572)],C['muted'],3,both=True)
text(1200,694,'模型与框架通过请求 / 动作交互；框架与沙箱通过操作 / 反馈交互。',29,C['muted'],align='center',maxw=CW)

# 02: Accurate two-plane architecture.
section(774,'02','工作原理：把大量容器变成统一的沙箱服务')
rect(M,852,CW,600,C['white'],28,C['line'])
for x,w,title,body,col,bg in [
    (128,360,'使用方','自建程序 / 评测器\n训练器与任务驱动',C['ink'],C['bg']),
    (550,300,'接入接口','HTTP API\nPython SDK',C['blue'],C['blue_bg']),
    (930,550,'Orchard 编排服务','状态 / 并发 / 时限 / 回收\nRedis 支持多副本共享状态',C['teal'],C['teal_bg']),
    (1700,570,'Kubernetes','容器调度与生命周期\n网络策略与资源分配',C['blue'],C['blue_bg'])]:
    rect(x,900,w,178,bg,20)
    text(x+24,919,title,34,col,True,maxw=w-48)
    para(x+24,979,body,27,C['muted'],maxw=w-48,leading=37)
arrow([(496,985),(538,985)],C['blue'],4)
arrow([(860,985),(918,985)],C['blue'],4,both=True)
arrow([(1494,985),(1685,985)],C['blue'],4,dashed=True)
text(1594,936,'管理',25,C['blue'],align='center')
arrow([(1205,1092),(1205,1157)],C['teal'],5,both=True)
text(1252,1104,'直接通过 Pod IP 执行 / 返回',27,C['teal'],maxw=690)
arrow([(1985,1092),(1985,1157)],C['blue'],4,dashed=True)
text(2040,1104,'创建 / 删除',26,C['blue'],maxw=230)
text(150,1116,'每个任务一个独立 Pod',28,C['muted'],True,maxw=700)
for i,x in enumerate([128,862,1596]):
    rect(x,1170,676,185,C['teal_bg'],20,'#B8DDD5',2)
    text(x+26,1185,f'沙箱 {chr(65+i)} · 任务 {chr(65+i)}',33,C['teal'],True,maxw=624)
    text(x+26,1236,'任务镜像 + 项目文件 + 轻量执行服务',27,maxw=624)
    text(x+26,1283,'命令 / 文件 / 终端 → 输出 / 错误',27,C['muted'],maxw=624)
text(128,1370,'Pod 内轻量服务负责执行命令；模型决策来自另行配置的模型接口。',28,C['muted'],maxw=2100)
text(128,1409,'执行与文件请求直达 Pod，减少 Kubernetes 控制接口的负担。',26,C['muted'],maxw=2100)

# 03: Twelve capabilities, grouped as concrete actions.
section(1490,'03','沙箱具体包含哪些能力？','现有功能 · 任务依赖按需准备')
capabilities=[
    ('自选镜像','按任务准备 Linux 容器环境'),
    ('创建与销毁','为每个任务分配独立环境'),
    ('运行代码','执行命令、脚本、编译和测试'),
    ('文件操作','上传、下载、列目录；用命令编辑'),
    ('Git 补丁','应用补丁，配合命令导出代码差异'),
    ('交互终端','PTY 输入输出与持续交互'),
    ('任务查询','状态、标准输出、错误和退出码'),
    ('资源限制','CPU、内存与执行时限'),
    ('网络策略','禁外网、放行或 IP / 端口白名单'),
    ('自动回收','时限、心跳与清理机制'),
    ('批量运行','异步并发，多机器集群调度'),
    ('程序接入','同步 / 异步 SDK，API Key 认证')]
tile_w=(CW-60)/4
for i,(title,body) in enumerate(capabilities):
    x=M+(i%4)*(tile_w+20); y=1570+(i//4)*188
    rect(x,y,tile_w,168,C['white'],20,C['line'])
    pill(x+20,y+20,48,f'{i+1:02}',C['teal'],C['teal_bg'],22,44)
    text(x+86,y+21,title,34,bold=True,maxw=tile_w-110)
    para(x+24,y+91,body,27,C['muted'],maxw=tile_w-48,leading=37)
rect(M,2142,CW,84,C['blue_bg'],20)
text(M+24,2146,'预装 Agent：Codex CLI、Claude Code、pi、OpenCode、Hermes、mini-swe-agent',29,C['blue'],True,maxw=CW-48)
text(M+24,2186,'工具需配置模型接口与凭据；Python、浏览器及项目依赖按所选镜像和任务准备。',26,C['muted'],maxw=CW-48)

# 04: Practical workflow, evaluation and training.
section(2260,'04','一次任务怎么完成？')
steps=['创建沙箱','放入项目','Agent 执行','查看反馈','修改并重试','导出结果','回收环境']
step_w=290
for i,label in enumerate(steps):
    x=125+i*310
    rect(x,2355,step_w,90,C['teal_bg'] if i in [0,2,3,6] else C['white'],18,C['line'])
    text(x+step_w/2,2373,label,31,C['teal'] if i in [0,2,3,6] else C['ink'],True,'center',maxw=step_w-24)
    if i<6: arrow([(x+step_w+2,2400),(x+step_w+18,2400)],C['muted'],3)
arrow([(1200,2458),(1200,2490),(890,2490),(890,2458)],C['teal'],3)
rect(942,2472,210,38,C['bg'],8)
text(1047,2473,'根据反馈继续尝试',23,C['teal'],align='center',maxw=220)
half=(CW-GAP)/2
rect(M,2525,half,410,C['white'],24,C['line'])
rect(M+half+GAP,2525,half,410,C['white'],24,C['line'])
text(M+32,2550,'评测 · Orchard Eval',39,C['blue'],True,maxw=half-64)
eval_items=[
    '标准任务：SWE-bench / Terminal-Bench 等',
    '保存交互轨迹、日志、补丁和成绩',
    '代码修复在新沙箱中，沿用基准评分逻辑',
    '支持恢复评测，区分环境故障与任务失败']
yy=2625
for item in eval_items:
    yy=bullet(M+34,yy,item,half-68,30,C['blue'])+15
text(M+34,2878,'基准、Agent 框架与环境保持分层。',26,C['muted'],maxw=half-68)
tx=M+half+GAP
text(tx+32,2550,'训练 · trainer / slime',39,C['purple'],True,maxw=half-64)
train_items=[
    '专家轨迹 → 监督微调 SFT',
    '执行任务与反馈 → 强化学习 RL',
    'BAR：组织成功 / 失败样本组',
    'OPD：教师指导；RPR：过程质量奖励',
    '价值模型：重新排序多个候选结果']
yy=2620
for item in train_items:
    yy=bullet(tx+34,yy,item,half-68,29,C['purple'])+5
text(tx+34,2884,'以上方法按具体配方选用。',25,C['muted'],maxw=half-68)
project_tiles=[('Orchard-SWE','修代码'),('Orchard-GUI','操作网页'),('Orchard-Claw','工具工作流'),('后续项目','OpenWebRL / OpenForge RL')]
pw=(CW-60)/4
for i,(name,desc) in enumerate(project_tiles):
    x=M+i*(pw+20)
    rect(x,2960,pw,92,C['purple_bg'],18)
    text(x+20,2966,name,29,C['purple'],True,maxw=pw-40)
    text(x+20,3010,desc,25,C['muted'],maxw=pw-40)

# 05: Docker comparison, without implying absent Docker features.
section(3090,'05','与直接用 Docker 的区别')
table_x,table_y=M,3170
colw=[390,800,CW-1190]
headers=['对比项','直接用 Docker','Orchard Env']
rect(table_x,table_y,CW,443,C['white'],24,C['line'])
rect(table_x,table_y,CW,68,C['navy'],20)
x=table_x
for width,label in zip(colw,headers):
    text(x+26,table_y+12,label,31,C['white'],True,maxw=width-52); x+=width
rows=[
    ['执行与隔离','提供基础容器能力','复用容器能力，封装沙箱接口'],
    ['批量任务','自己写脚本或组合工具','状态、并发、回收等现成服务'],
    ['跨机器运行','另外配置编排与管理','基于 Kubernetes 调度'],
    ['AI 评测与训练','自行组织流程与工具','仓库提供配套工具与研究配方'],
    ['部署维护','单机通常简单','需集群、网络策略及服务维护']]
for row_i,row in enumerate(rows):
    yy=table_y+68+row_i*75
    if row_i%2==1: rect(table_x+1,yy,CW-2,75,'#F6F8FC',0)
    x=table_x
    for j,(width,label) in enumerate(zip(colw,row)):
        text(x+26,yy+18,label,29,C['teal'] if j==2 else C['ink'],j==0,maxw=width-52)
        x+=width
    if row_i<4: line([(table_x+20,yy+75),(table_x+CW-20,yy+75)],C['line'],1)
text(M+12,3638,'Docker 也有 API、资源限制和网络能力；Orchard 的价值是减少管理与集成工作。',29,C['muted'],maxw=CW-24)

# 06: Value and practical adoption guidance.
section(3730,'06','价值：什么时候值得用？','选择建议 · 按任务规模和维护成本判断')
for i,label in enumerate(['少写管理代码','统一执行与评测流程','环境与模型训练独立扩展']):
    pill(M+i*748,3810,720,label,C['teal'],C['teal_bg'],31,64)
rect(M,3896,half,210,C['white'],24,C['line'])
text(M+32,3918,'优先用 Docker',38,C['ink'],True,maxw=half-64)
para(M+32,3982,'本机试验 / 少量固定任务\n已有脚本够用，维护成本低',30,C['muted'],maxw=half-64,leading=46)
rect(tx,3896,half,210,C['teal_bg'],24)
text(tx+32,3918,'考虑 Orchard',38,C['teal'],True,maxw=half-64)
para(tx+32,3982,'统一远程沙箱 / 跨机器大量任务\nAgent 批量评测 / 交互数据采集 / RL',30,C['muted'],maxw=half-64,leading=46)
rect(M,4128,CW,90,C['blue_bg'],20)
text(M+24,4135,'资源与配置：环境层使用 CPU；模型推理与训练所需资源另配。',29,C['blue'],True,maxw=CW-48)
text(M+24,4178,'任务、模型接口、凭据、项目依赖与评分规则仍需按具体用途准备。',27,C['muted'],maxw=CW-48)

# 07: Research results with explicit conditions, not universal guarantees.
section(4250,'07','作者报告了哪些效果？','论文第三版与仓库指标 · 未本地复现')
metrics=[
    (M,4330,'代码修复 · SWE-bench Verified','61.4% → 69.7% → 73.0%',
     '基础模型 → RPR 训练 → 候选重排\nQwen3.5-35B-A3B；73.0% 使用 6 个候选筛选。',C['purple'],C['purple_bg']),
    (tx,4330,'网页操作 · 4B 模型','74.1% / 67.0% / 64.0%',
     '依次为 WebVoyager / Online-Mind2Web / DeepShop\n三项平均成功率 68.4%。',C['blue'],C['blue_bg']),
    (M,4590,'工具工作流 · Claw-Eval','59.6% → 73.9%',
     '原框架 → ZeroClaw；两项均为 pass@3。\npass@3：三次尝试至少一次成功。',C['purple'],C['purple_bg']),
    (tx,4590,'沙箱性能 · 作者测试配置','0.28 秒 · 1,000 个',
     '平均命令延迟 0.28 秒；并行启动 1,000 个沙箱\n约 26 秒。实际表现取决于部署配置。',C['teal'],C['teal_bg'])]
for x,y,title,big,body,col,bg in metrics:
    rect(x,y,half,240,C['white'],24,C['line'])
    text(x+28,y+17,title,31,col,True,maxw=half-56)
    text(x+28,y+69,big,47,col,True,maxw=half-56)
    para(x+28,y+149,body,26,C['muted'],maxw=half-56,leading=37)
text(M+12,4855,'这些成绩受模型、Agent 框架、任务和配置影响；使用沙箱本身不会自动获得对应模型能力。',28,C['muted'],maxw=CW-24)

# 08: Important boundaries and current roadmap status.
section(4930,'08','能力边界与后续计划')
rect(M,5010,CW,205,C['amber_bg'],24)
text(M+28,5022,'当前边界',32,C['amber'],True,maxw=CW-56)
text(M+28,5070,'基础是容器隔离与可控执行；实际隔离强度取决于底层容器与集群配置。',29,C['ink'],maxw=CW-56)
text(M+28,5123,'后续计划',32,C['amber'],True,maxw=CW-56)
text(M+28,5171,'完整状态快照、暂停 / 恢复、从同一状态分叉与前缀共享，目前列在路线图中。',28,C['ink'],maxw=CW-56)

line([(M,5250),(W-M,5250)],C['line'],2)
text(M,5270,'资料核对：2026-10-22  ·  项目许可：MIT  ·  本图为独立整理的技术说明',27,C['muted'],maxw=CW)
text(M,5316,'项目：github.com/microsoft/Orchard-Agentic  ｜  论文：arXiv:2605.15040v3',26,C['muted'],maxw=CW)
text(M,5360,'依据：orchard_env/README.md · docs/architecture.md · docs/api.md · orchard_eval/README.md',25,C['muted'],maxw=CW)
text(M,5403,'制作：矢量图形与文字排版；完整来源与生成脚本随图提供。',24,C['muted'],maxw=CW)

svg.append('</svg>')
svg_path=OUT/'orchard-agentic-overview.svg'
png_path=OUT/'orchard-agentic-overview.png'
svg_path.write_text('\n'.join(svg),encoding='utf-8')
im=im.resize((W,H),Image.Resampling.LANCZOS)
im.save(png_path,optimize=True,dpi=(200,200))
preview=im.resize((1200,2740),Image.Resampling.LANCZOS)
preview.save(OUT/'orchard-agentic-preview.png',optimize=True)
(OUT/'layout-checks.json').write_text(json.dumps({'canvas':[W,H],'text_checks':len(checks),'all_fit':all(c['ok'] for c in checks),'checks':checks},ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'png':str(png_path),'svg':str(svg_path),'size':[W,H],'text_checks':len(checks),'all_fit':True},ensure_ascii=False))
