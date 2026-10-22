from pathlib import Path
import json
import math
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1] / "assets"
OUT = ROOT / "sparkvsr-overview.png"
W, H, SCALE = 2400, 3970, 2
COL = {"bg": "#F3F6FA", "ink": "#142638", "sub": "#506579", "line": "#DDE5EE", "white": "#FFFFFF", "cyan": "#087FA0", "cyan_bg": "#E9F7FB", "purple": "#7054B3", "purple_bg": "#F1EDFA", "green": "#237C62", "green_bg": "#EBF7F1", "amber": "#9B6216", "amber_bg": "#FFF3DE"}
im = Image.new("RGB", (W * SCALE, H * SCALE), COL["bg"])
d = ImageDraw.Draw(im)
fonts = {}
checks = []

def font(size, bold=False):
    key = size, bold
    if key not in fonts:
        name = "msyhbd.ttc" if bold else "msyh.ttc"
        fonts[key] = ImageFont.truetype(str(Path("C:/Windows/Fonts") / name), round(size * SCALE))
    return fonts[key]

def rect(box, fill, outline=None, radius=22, width=2):
    d.rounded_rectangle(tuple(round(v * SCALE) for v in box), radius=radius * SCALE, fill=fill, outline=outline, width=width * SCALE)

def line(points, fill, width=3):
    d.line([(round(x*SCALE), round(y*SCALE)) for x,y in points], fill=fill, width=width*SCALE, joint="curve")

def text(x, y, value, size=36, color=None, bold=False):
    d.text((round(x*SCALE), round(y*SCALE)), value, font=font(size,bold), fill=color or COL["ink"], anchor="lt")

def measure(value, size=36, bold=False):
    return d.textlength(value, font=font(size,bold)) / SCALE

def wrap(value, width, size=36, bold=False):
    output = []
    for para in value.split("\n"):
        current = ""
        for char in para:
            if current and measure(current+char,size,bold) > width:
                output.append(current)
                current=char
            else:
                current+=char
        output.append(current)
    return output

def para(x, y, value, width, size=36, color=None, bold=False, leading=52):
    for item in wrap(value,width,size,bold):
        text(x,y,item,size,color,bold)
        y += leading
    return y

def card(x,y,w,h,num,title,color):
    rect((x,y,x+w,y+h),COL["white"],COL["line"])
    rect((x+30,y+31,x+103,y+87),COL[color],radius=14)
    text(x+42,y+41,num,31,COL["white"],True)
    text(x+122,y+37,title,43,COL["ink"],True)
    return y+116

def bullets(x,y,w,items,size=36,leading=51,gap=13,color=None):
    for item in items:
        rect((x,y+14,x+9,y+23),color or COL["cyan"],radius=4)
        y=para(x+27,y,item,w-27,size,COL["ink"],leading=leading)+gap
    return y

def checked(label, end, bottom):
    checks.append({"section":label,"content_bottom":end,"available_bottom":bottom,"fits":end<=bottom})
    if end > bottom:
        raise RuntimeError(f"Overflow {label}: {end} > {bottom}")

def arrow(points,color,width=5):
    line(points,color,width)
    (x0,y0),(x1,y1)=points[-2:]
    angle=math.atan2(y1-y0,x1-x0)
    a=(x1-20*math.cos(angle-.5), y1-20*math.sin(angle-.5))
    b=(x1-20*math.cos(angle+.5), y1-20*math.sin(angle+.5))
    d.polygon([(round(x*SCALE),round(y*SCALE)) for x,y in [(x1,y1),a,b]],fill=color)

def film(x,y,color):
    rect((x,y,x+70,y+56),COL["white"],color,radius=7,width=3)
    for off in [8,23,38,53]:
        rect((x+off,y+4,x+off+8,y+10),color,radius=1)
        rect((x+off,y+46,x+off+8,y+52),color,radius=1)
    line([(x+17,y+36),(x+29,y+24),(x+39,y+33),(x+50,y+19),(x+60,y+36)],color,3)

# Header
rect((100,77,116,241),COL["cyan"],radius=5)
text(145,73,"SparkVSR",111,bold=True)
text(149,218,"能力 · 原理 · 效果 · 价值 · 当前判断",42,COL["sub"])
rect((1844,104,2300,164),COL["white"],COL["line"],radius=30)
text(1875,118,"项目理解整理  /  2026-10-22",27,COL["sub"])
text(1848,190,"GENERATIVE VIDEO SUPER-RESOLUTION",20,COL["cyan"],True)

# Core interpretation
rect((100,300,2300,565),COL["ink"],radius=26)
text(140,334,"我们的理解",32,"#8BD4E7",True)
text(140,389,"以原视频为约束，结合高清关键帧，生成式重建高清视频。",49,COL["white"],True)
text(140,467,"原视频提供运动与结构；关键帧提供外观与细节。",36,"#DAE7F1")
text(1615,487,"清晰度提升 ≠ 真实细节完全恢复",29,"#FFD18A",True)

M, GAP, CW = 100, 36, 1082
L, R = 100, 1218
y=card(L,600,CW,500,"01","它能做什么","cyan")
end=bullets(L+34,y,CW-68,[
    "视频超分：提高输出分辨率，默认宽、高各放大 4 倍。",
    "可控修复：先修好少量关键帧，再将细节传播到其他帧。",
    "无参考修复：可直接处理低清视频，主要作为备用模式。",
    "扩展示例：老片修复、上色、风格迁移；属于作者展示。",
],size=35,leading=49,gap=13)
checked("01",end,1085)
y=card(R,600,CW,500,"02","它的专项价值","green")
end=bullets(R+34,y,CW-68,[
    "可干预：关键帧不满意，可以先修改，再生成整段视频。",
    "复用图像模型：由强图像模型提供参考帧的细节。",
    "跨帧一致：让纹理随动作连续变化，减少细节闪烁。",
    "减少逐帧处理：适合老片、低清素材与 AIGC 视频的视觉增强。",
],size=35,leading=49,gap=13,color=COL["green"])
checked("02",end,1085)

# Two-input reconstruction pipeline
card(100,1130,2200,545,"03","推理原理：两类信息，共同约束重建","cyan")
rect((145,1261,790,1388),COL["cyan_bg"],radius=18)
film(172,1295,COL["cyan"])
text(266,1281,"低清原视频 → 放大并编码",35,COL["cyan"],True)
text(266,1334,"提供运动、构图与结构",30,COL["sub"])
rect((145,1450,790,1577),COL["purple_bg"],radius=18)
film(172,1484,COL["purple"])
text(266,1470,"选关键帧 → 单图修复 / 编辑",34,COL["purple"],True)
text(266,1523,"PiSA-SR / NBP / 外部参考图",30,COL["sub"])
arrow([(806,1323),(897,1323),(897,1390),(1010,1390)],COL["cyan"])
arrow([(806,1513),(897,1513),(897,1443),(1010,1443)],COL["purple"])
rect((1025,1316,1685,1521),COL["ink"],radius=22)
text(1110,1342,"视频 Transformer 联合重建",37,COL["white"],True)
text(1095,1401,"原视频特征 + 稀疏参考特征",33,"#D9E8F1")
text(1165,1456,"单步去噪 → 解码",35,"#9BD9E6")
arrow([(1705,1417),(1821,1417)],COL["green"])
rect((1834,1345,2255,1490),COL["green_bg"],radius=20)
text(1893,1372,"高清重建视频",44,COL["green"],True)
text(1900,1433,"原始动作 + 补充细节",28,COL["sub"])
text(145,1613,"关键帧可手选、随机选或按 I 帧选；短片可先用第一帧。流程为示意，非运行结果。",31,COL["sub"])

# Training and controls
y=card(L,1705,CW,525,"04","模型与训练","purple")
end=bullets(L+34,y,CW-68,[
    "底座：CogVideoX1.5-5B-I2V。",
    "双路编码：原视频特征与稀疏参考特征融合，无参考位置填零。",
    "第一阶段：在压缩特征空间学习重建与细节传播。",
    "第二阶段：在像素空间优化清晰度、感知纹理与帧一致性。",
    "训练时随机移除参考，也学习无参考修复。",
],size=34,leading=47,gap=11,color=COL["purple"])
checked("04",end,2210)
y=card(R,1705,CW,525,"05","如何控制效果","purple")
y=para(R+34,y,"参考来源：本地 PiSA-SR、外部图片或商业图像 API。",CW-68,34,leading=48)+14
y=para(R+34,y,"参考位置：选择需要重点修复的时刻。",CW-68,34,leading=48)+18
text(R+34,y,"参考强度  ref_guidance_scale",33,COL["purple"],True)
y+=57
for xx,label,desc in [(R+34,"0","无参考重建"),(R+380,"1","标准参考引导"),(R+726,">1","更强参考细节")]:
    rect((xx,y,xx+320,y+102),COL["purple_bg"],radius=15)
    text(xx+19,y+14,label,39,COL["purple"],True)
    text(xx+72,y+30,desc,28,COL["ink"])
y+=128
end=para(R+34,y,"强度更高，不代表细节更真实；参考中的错误也可能传播。",CW-68,34,COL["sub"],leading=47)
checked("05",end,2210)

# Quantitative evidence
card(100,2260,2200,490,"06","效果：观感改善与像素保真存在取舍","green")
text(138,2355,"作者论文 UDM10 评测｜以下指标均越高越好｜NBP = Nano-Banana-Pro",29,COL["sub"])
tx, ty = 138, 2408
widths=[540,380,580,623]
rows=[
    ["指标","DOVE","SparkVSR 无参考","SparkVSR + NBP 参考"],
    ["PSNR  像素保真 / dB","26.52","26.62","23.70"],
    ["CLIP-IQA  图像观感","0.5011","0.4303","0.5501"],
    ["DOVER  视频质量","0.5664","0.5494","0.6902"],
]
for i,row in enumerate(rows):
    yy=ty+i*64
    rect((tx,yy,tx+sum(widths),yy+64),COL["ink"] if i==0 else ("#F1F6FA" if i%2 else "#FFFFFF"),radius=0)
    xx=tx
    for j,(val,ww) in enumerate(zip(row,widths)):
        col=COL["white"] if i==0 else COL["ink"]
        bold=i==0 or (i==1 and j==2) or (i>1 and j==3)
        if bold and i>0: col=COL["green"]
        text(xx+18,yy+17,val,29 if i==0 else 33,col,bold)
        xx+=ww
text(138,2685,"参考模式的观感评分上升，但 PSNR 下降。作者报告与示例，非本机实测；不代表全部指标领先。",30,COL["sub"])

# Limits and cost
y=card(L,2780,CW,600,"07","局限与边界","amber")
end=bullets(L+34,y,CW-68,[
    "细节可能由 AI 推测，文字、脸部和纹理可能发生偏差。",
    "参考图质量会影响结果，错误细节可能扩散到其他帧。",
    "输出 4K 表示像素尺寸，不等于原生 4K 的真实信息量。",
    "官方示例中边缘与纹理更清楚；不同素材的效果仍需验证。",
    "更适合改善观看效果；真实性要求高的用途需逐项验证。",
],size=35,leading=49,gap=14,color=COL["amber"])
checked("07",end,3360)
y=card(R,2780,CW,600,"08","开源与使用成本","cyan")
end=bullets(R+34,y,CW-68,[
    "已提供推理代码、训练代码、权重和 ComfyUI 工作流。",
    "主要依赖 Python、PyTorch、Diffusers 与 GPU 环境。",
    "支持分块、VAE 切片及 CPU 卸载等内存优化。",
    "PiSA-SR 可本地运行；商业 API 模式可能产生费用。",
    "推理速度与显存未实测；单步去噪不等于实时处理。",
],size=35,leading=49,gap=14)
checked("08",end,3360)

# Project decision, explicitly our judgment
rect((100,3410,2300,3695),COL["amber_bg"],"#E9D3AF",radius=24)
text(140,3450,"当前决策｜了解并留档，暂不深入研究",51,COL["amber"],True)
end=para(140,3533,"我们的判断：核心仍是模型的视频生成与重建能力；专项价值在于关键帧控制和时序传播。",2110,36,COL["ink"],leading=53)
end=para(140,end+17,"当前不投入部署复现；出现明确的可控视频修复需求时再评估。",2110,36,COL["sub"],leading=53)
checked("decision",end,3680)

text(105,3742,"来源  github.com/taco-group/SparkVSR",30,COL["sub"])
text(105,3794,"论文  arxiv.org/abs/2603.16864     示例  sparkvsr.github.io",30,COL["sub"])
text(105,3846,"依据本次已有资料与讨论整理；未新增实验。流程为示意，评测来自作者报告。",29,COL["sub"])
text(2173,3850,"01 / 01",27,COL["sub"],True)

im=im.resize((W,H),Image.Resampling.LANCZOS)
im.save(OUT,optimize=True)
(ROOT / "sparkvsr-overview-2026-10-22-layout.json").write_text(json.dumps({"size":[W,H],"checks":checks},ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps({"output":str(OUT),"size":[W,H],"bytes":OUT.stat().st_size,"checks":checks},ensure_ascii=False))
