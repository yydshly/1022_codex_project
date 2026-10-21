"""Generate the complete WebGL gallery from the pinned MIT Metal sources.

Only the small language/API boundary is translated; effect algorithms stay upstream.
Run from any directory. No third-party Python packages are required.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
COMMIT = "6b644a8bd4f3131401bd6765990e476352d3cdef"
METAL = ROOT / "upstream/Sources/SwiftUIShaders/Shaders/SwiftUIShaders.metal"

# Chinese editorial descriptions. Algorithm, parameter order/ranges/defaults come
# from the actual upstream files, not from these descriptions.
EDITORIAL = {
    "Aurora": ("极光", "光影材质", "彩色光带缓慢掠过画面，像夜空中的极光。", "多层正弦光带、噪声扰动与亮度混合。"),
    "BlackHole": ("黑洞", "几何空间", "画面被中心引力拉弯，周围形成发光的吸积环。", "按径向距离改变采样坐标，叠加旋转光环与中心遮罩。"),
    "ChromaticSplit": ("色彩分离", "色彩轮廓", "红绿蓝通道错开，制造棱镜边缘和光学色差。", "沿指定方向分别采样 RGB 通道，可按距中心的距离衰减。"),
    "Datamosh": ("数据损坏", "故障解构", "图像块随机错位、拖抹，呈现视频解码故障的观感。", "随机块遮罩、采样偏移、通道分离与颜色量化。"),
    "Disintegrate": ("粒化消散", "故障解构", "画面沿噪声边界逐渐消散，留下发亮的燃烧边缘。", "噪声阈值决定透明度，并在阈值附近加入漂移和高光。"),
    "Duochrome": ("双色映射", "色彩轮廓", "把明暗映射到两种色相，得到双色海报般的画面。", "以亮度为插值因子混合两种颜色，并调节对比度。"),
    "Echo": ("重影回声", "几何空间", "多层半透明轮廓沿一个方向展开，像视觉的回声。", "叠加多次偏移采样，以递减权重混合。"),
    "Emboss": ("浮雕", "光影材质", "细节呈现凸起或雕刻般的明暗，光线方向可以调节。", "沿光照方向比较相邻位置的亮度差。"),
    "EtherealAura": ("灵动光晕", "光影材质", "边缘呼吸、轻微液化，彩色光晕随时间起伏。", "边缘距离遮罩、噪声位移与周期性的光晕混合。"),
    "Frosted": ("磨砂玻璃", "光影材质", "画面局部像蒙上霜雾，中心保留柔和的清晰窗口。", "噪声决定散射方向，五次邻域采样近似模糊。"),
    "GeometricWarp": ("几何螺旋", "几何空间", "画面卷入重复的螺旋，也可逐渐混入镜面对称。", "对数极坐标变换、循环缩放与扇区镜像。"),
    "Glitch": ("数字故障", "故障解构", "间歇性的横向撕裂、扫描线和 RGB 错位。", "按时间和图像条带生成随机位移与通道偏移。"),
    "GravityWells": ("引力井", "几何空间", "多个移动的引力中心同时牵引、扭曲画面。", "叠加多个径向衰减的采样偏移场。"),
    "HeatShimmer": ("热浪", "流体波纹", "画面像隔着热空气一样轻微摇晃，上方可更明显。", "不同频率的正弦波叠加为采样位移。"),
    "Holographic": ("全息镭射", "光影材质", "彩虹光泽掠过图像，明亮区域像镭射卡纸一样反光。", "三个相位错开的正弦波生成彩虹，再按原图亮度叠加。"),
    "InkBleed": ("水墨晕染", "流体波纹", "图像像湿纸上的颜料一样缓慢渗化、流动。", "多层分形噪声相互扰动，形成 domain warping 位移场。"),
    "Kaleidoscope": ("万花筒", "几何空间", "原图被折叠成旋转、对称的放射状花纹。", "在极坐标中折叠角度，再映射回图像采样。"),
    "LiquidChrome": ("液态金属", "光影材质", "表面像流动的水银，带有起伏的白色金属高光。", "噪声位移、由高度差估算法线、去饱和与镜面高光。"),
    "LiquidMirror": ("水面倒影", "流体波纹", "画面下部变成有涟漪的倒影，反射边界平滑过渡。", "翻转局部纵坐标，叠加波纹并按深度衰减。"),
    "LiveRipple": ("连续涟漪", "流体波纹", "多个波源持续产生向外扩散的同心波纹。", "多波源的径向正弦位移叠加，并按距离衰减。"),
    "MagneticField": ("磁场", "流体波纹", "图像沿弯曲的力线流动，呈现磁流体般的走势。", "模拟磁偶极场方向，用场向量和噪声改变采样坐标。"),
    "Melt": ("熔化", "故障解构", "图像像被加热的蜡一样向下融化、滴落。", "按列生成噪声下垂量，并叠加暖色与边缘高光。"),
    "MorphBreathe": ("有机呼吸", "流体波纹", "画面整体缓慢膨胀、收缩，并带有不规则起伏。", "周期性的径向变形叠加分形噪声扰动。"),
    "NeonEdge": ("霓虹轮廓", "色彩轮廓", "图像的轮廓变成流动的彩色霓虹线条。", "Sobel 亮度边缘检测、按边缘方向着色与亮度增强。"),
    "PixelateMosaic": ("立体马赛克", "故障解构", "画面变成带斜面、间隙的方砖，并能动态聚合。", "网格量化采样、砖块偏移与程序化斜面明暗。"),
    "PixelateStorm": ("像素风暴", "故障解构", "像素块脉冲、偏移，卷入旋转的像素风暴。", "网格采样、随机块偏移与极坐标旋转。"),
    "Plasma": ("等离子光", "光影材质", "彩色能量波在原图上交错、流动。", "多组正弦场和噪声构造彩色干涉图案。"),
    "Pulse": ("心跳脉冲", "流体波纹", "画面按指定 BPM 律动，边缘同步闪动。", "周期性的尖峰波形驱动径向位移和边缘光。"),
    "RefractLens": ("交互透镜", "触摸交互", "拖动玻璃球，让局部画面折射、放大并出现彩边。", "以交互点为中心计算球面折射、边缘扭曲和色散。"),
    "Shatter": ("碎片散开", "故障解构", "画面沿不规则碎片分开，碎片带玻璃高光。", "Voronoi 单元确定碎片，按单元偏移和旋转采样。"),
    "ShatterGlass": ("碎玻璃", "光影材质", "玻璃裂纹布满画面，裂缝处出现折射和棱镜彩边。", "Voronoi 最近与次近距离确定裂纹，叠加折射与色散。"),
    "Shockwave": ("冲击波", "流体波纹", "明亮的冲击环周期性扩散，沿途拉动图像。", "按传播半径计算环形遮罩，再执行径向采样偏移。"),
    "SmokeReveal": ("烟雾显影", "光影材质", "内容在流动的烟雾中显露，伴随柔和的光线。", "分形噪声构建烟雾密度，控制图像混合与光束亮度。"),
    "Solarize": ("曝光反转", "色彩轮廓", "画面局部反相，出现强烈、超现实的色彩分区。", "按阈值和曲线对 RGB 通道执行非线性色彩映射。"),
    "Thermal": ("热成像", "色彩轮廓", "明暗转为冷暖热力色带，并带有热空气扰动。", "按亮度映射伪彩色，再加入噪声位移；颜色不代表真实温度。"),
    "Topographic": ("等高线", "色彩轮廓", "明暗层次变成密集等高线，像一张彩色地形图。", "把原图亮度分层，用周期阈值描出主次轮廓线。"),
    "TouchRipple": ("触摸涟漪", "触摸交互", "点击画面，从触点产生扩散后逐渐消退的水波。", "传播半径由 touchAge 决定，正弦波包络控制位移与衰减。"),
    "UnderwaterCaustics": ("水下焦散", "流体波纹", "游动的水光、波纹和淡蓝色深度感覆盖画面。", "多层周期场生成焦散亮纹，叠加水面位移和光束。"),
    "Vortex": ("旋涡", "几何空间", "图像围绕中心旋转、扭曲，中心与边缘转角不同。", "按径向距离指数衰减旋转角，重新映射采样坐标。"),
    "WavePool": ("波浪池", "流体波纹", "多个方向的波浪交叠，让画面像水面一样起伏。", "叠加不同方向和频率的正弦位移场。"),
    "Wormhole": ("虫洞", "几何空间", "画面卷进带纵深与旋转感的隧道。", "径向透视式缩放、角度扭转与中心雾化。"),
}

PARAM_NAMES = {
    "intensity":"强度", "bands":"光带数量", "speed":"速度", "colorShift":"色彩偏移",
    "mass":"中心质量", "spin":"旋转速度", "distortion":"扭曲程度", "ringBrightness":"光环亮度",
    "spread":"分离距离", "angle":"方向角度", "edgeOnly":"边缘权重", "animate":"动画幅度",
    "blockCorruption":"损坏比例", "smearAmount":"拖抹距离", "colorBleed":"颜色溢出", "glitchRate":"故障频率",
    "threshold":"阈值", "edgeWidth":"边缘宽度", "driftAmount":"漂移距离", "direction":"漂移方向",
    "hue1":"暗部色相", "hue2":"亮部色相", "contrast":"对比度", "echoCount":"重影数量",
    "fade":"衰减", "strength":"强度", "mixAmount":"混合比例", "auraWidth":"光晕宽度",
    "auraIntensity":"光晕强度", "pulseSpeed":"脉冲速度", "hueShift":"色相偏移",
    "frostAmount":"结霜程度", "grainSize":"霜晶尺度", "clearRadius":"清晰半径", "clearSoftness":"过渡柔度",
    "spiralTight":"螺旋紧密度", "zoomRepeat":"重复缩放", "rotation":"旋转角度", "blend":"镜像混合",
    "blockSize":"图块大小", "scanLines":"扫描线", "wellStrength":"引力强度", "wellCount":"引力井数量",
    "orbitSpeed":"轨道速度", "warpFalloff":"引力衰减", "amplitude":"位移幅度", "frequency":"频率",
    "verticalBias":"顶部权重", "scale":"纹理尺度", "angleOffset":"光带角度", "warpStrength":"扭曲强度",
    "detail":"噪声层数", "segments":"镜像分段", "zoom":"缩放", "animateSpeed":"自转速度",
    "chromeIntensity":"金属强度", "flowSpeed":"流动速度", "reflectionScale":"反射尺度", "mirrorAxis":"反射起点",
    "ripple":"涟漪幅度", "depth":"深度", "damping":"距离衰减", "ringCount":"波源数量",
    "fieldStrength":"磁场强度", "lineCount":"线条数量", "fieldTurbulence":"磁场扰动", "polarity":"磁极形态",
    "meltAmount":"熔化距离", "dripScale":"滴流尺度", "heat":"暖色偏移", "breatheDepth":"呼吸幅度",
    "breatheRate":"呼吸频率", "warpComplexity":"扰动层数", "organic":"有机程度", "edgeStrength":"轮廓强度",
    "glowAmount":"发光强度", "colorCycle":"变色速度", "mixOriginal":"原图权重", "pixelSize":"像素大小",
    "bevel":"斜面强度", "animateAssemble":"聚合动画", "gap":"砖块间隙", "stormAmount":"风暴强度",
    "swirl":"旋转强度", "pulse":"脉冲频率", "colorMode":"配色模式", "bpm":"每分钟心跳",
    "sharpness":"脉冲锐度", "glowIntensity":"边缘光", "touchPos":"交互位置", "lensRadius":"透镜半径",
    "refraction":"折射强度", "aberration":"色散距离", "wobble":"边缘起伏", "shardCount":"碎片密度",
    "explode":"散开程度", "rotationAmt":"碎片转角", "edgeGlow":"裂缝发光", "crackDensity":"裂纹密度",
    "glassRefraction":"裂缝折射", "prismStrength":"棱镜强度", "shatterSpread":"碎片分离",
    "waveSpeed":"传播速度", "ringWidth":"波环宽度", "repeatRate":"重复间隔", "smokeAmount":"烟雾浓度",
    "smokeScale":"烟雾尺度", "windSpeed":"风速", "smokeTurb":"烟雾扰动", "curveIntensity":"曲线强度",
    "colorSeparation":"颜色分离", "shimmer":"热扰动", "noiseSpeed":"噪声速度", "paletteShift":"色带偏移",
    "lineWidth":"线条宽度", "colorize":"着色比例", "touchAge":"触摸经过时间", "decay":"时间衰减",
    "causticScale":"焦散尺度", "causticIntensity":"水光强度", "waterDistortion":"水面扭曲", "waterDepth":"水体深度",
    "twistAmount":"扭转角度", "radius":"作用半径", "falloff":"距离衰减", "wavelength":"波长",
    "complexity":"叠加波数", "twist":"隧道扭转",
}


def functions(source: str) -> list[dict]:
    pattern = re.compile(r"\[\[\s*stitchable\s*\]\]\s+half4\s+(bcs_\w+)\s*\((.*?)\)\s*\{", re.S)
    result = []
    for match in pattern.finditer(source):
        depth, end = 1, match.end()
        while depth:
            depth += (source[end] == "{") - (source[end] == "}")
            end += 1
        params = re.sub(r"//[^\n]*", "", match[2])
        args = [tuple(part.strip().rsplit(None, 1)) for part in params.split(",")]
        result.append({"name": match[1], "args": args, "source": source[match.start():end], "line": source[:match.start()].count("\n") + 1})
    return result


def translate(text: str) -> str:
    text = re.sub(r"//[^\n]*", "", text)
    text = re.sub(r"\[\[\s*stitchable\s*\]\]", "", text)
    text = re.sub(r"SwiftUI::Layer\s+layer\s*,?", "", text)
    text = re.sub(r"\bstatic\s+", "", text)
    text = text.replace("layer.sample(", "sampleLayer(")
    for dim in (2, 3, 4):
        text = re.sub(rf"\b(?:half|float){dim}\b", f"vec{dim}", text)
    text = re.sub(r"\bhalf\b", "float", text)
    text = re.sub(r"(?<=\d)h\b", "", text)
    text = re.sub(r"\batan2\b", "atan", text)
    text = re.sub(r"\bfmod\b", "metalFmod", text)
    # Upstream uses decreasing smoothstep edges (undefined in GLSL). Preserve
    # the intended smooth interpolation explicitly on both edge directions.
    text = re.sub(r"\bsmoothstep\b", "metalSmoothstep", text)
    return re.sub(r"\n\s*\n\s*\n", "\n\n", text).strip()


PREAMBLE = """#version 300 es
// Derived from SwiftUIShaders, Copyright (c) 2026 Kris Puckett. MIT.
precision highp float;
precision highp int;
uniform sampler2D uImage;
uniform vec2 uSize;
uniform vec2 uResolution;
uniform float uTime;
uniform float uParams[8];
uniform vec2 uTouch;
uniform float uCompare;
out vec4 fragColor;
vec4 sampleLayer(vec2 p) {
    if (any(lessThan(p, vec2(0.0))) || any(greaterThan(p, uSize))) return vec4(0.0);
    return texture(uImage, p / uSize);
}
float metalFmod(float x, float y) { return x - y * trunc(x / y); }
vec3 metalFmod(vec3 x, float y) { return x - y * trunc(x / y); }
float metalSmoothstep(float a, float b, float x) {
    if (abs(b - a) < 0.000001) return step(a, x);
    float t = clamp((x - a) / (b - a), 0.0, 1.0);
    return t * t * (3.0 - 2.0 * t);
}
"""


def build() -> dict[Path, str]:
    source = METAL.read_text(encoding="utf-8")
    upstream = json.loads((ROOT / "upstream/Docs/parameters.json").read_text(encoding="utf-8"))["shaders"]
    fns = {fn["name"]: fn for fn in functions(source)}
    assert len(fns) == len(upstream) == len(EDITORIAL) == 41
    shared = translate(source[source.index("static float bcs_hash"):source.index("// MARK: - 1.")])
    shaders, issues = [], []
    for index, item in enumerate(upstream):
        fn = fns[item["metal"]]
        key = item["modifier"][3:]
        name, category, description, principle = EDITORIAL[key]
        params = item["params"]
        supplied = iter(enumerate(params))
        call = []
        for kind, arg in fn["args"]:
            if arg == "position": call.append("position")
            elif arg == "layer": continue
            elif arg == "size": call.append("uSize")
            elif arg == "time": call.append("uTime")
            else:
                number, param = next(supplied)
                assert re.sub("_", "", arg).lower() == param["label"].lower(), (item["metal"], arg, param)
                call.append("uTouch * uSize" if kind == "float2" else f"uParams[{number}]")
        assert len(fn["args"]) - 3 - int(item["animated"]) == len(params)
        for param in params:
            param["name"] = PARAM_NAMES[param["label"]]
            if param["type"] == "float" and param["min"] is None:
                bounds = {"auraWidth": (0, 0.5), "auraIntensity": (0, 3), "pulseSpeed": (0, 5),
                          "distortion": (0, 30), "hueShift": (0, 8), "touchAge": (0, 5)}
                param["uiMin"], param["uiMax"] = bounds[param["label"]]
                param["rangeNote"] = "上游未指定范围；此滑块区间为本展示页的实验范围。"
            elif param["type"] == "float" and not param["min"] <= param["default"] <= param["max"]:
                issues.append(f"{item['modifier']}.{param['label']}: default={param['default']}, suggested=[{param['min']}, {param['max']}]")
                param["rangeNote"] = "上游默认值超出建议区间；滑块已扩展以保留原默认值。"
        frag = PREAMBLE + shared + "\n" + translate(fn["source"]) + f"""
void main() {{
    vec2 position = vec2(gl_FragCoord.x, uResolution.y - gl_FragCoord.y) / uResolution * uSize;
    vec4 color = {fn['name']}({', '.join(call)});
    if (uCompare >= 0.0 && position.x / uSize.x < uCompare) color = sampleLayer(position);
    fragColor = color;
}}
"""
        time_used = len(re.findall(r"\btime\b", re.sub(r"//[^\n]*", "", fn["source"]))) > 1
        shaders.append({**item, "timeUsed": time_used, "id": key, "index": index + 1, "name": name, "category": category,
                        "description": description, "principle": principle, "line": fn["line"],
                        "fragment": frag, "metalSource": fn["source"]})
    manifest = {"upstream": "https://github.com/krispuckett/SwiftUIShaders", "commit": COMMIT,
                "sourceSha256": hashlib.sha256(METAL.read_bytes()).hexdigest(),
                "count": len(shaders), "rangeNotes": issues, "shaders": shaders}
    license_text = (ROOT / "upstream/LICENSE").read_text(encoding="utf-8")
    capabilities = ["# SwiftUIShaders 完整能力清单", "", f"研究固定版本：`{COMMIT}`。共 41 个公开修饰器。上游有 37 个动画封装，但其中 Shatter 不使用 time；实际为 36 个时间变化效果、3 个静态/参数驱动效果和 2 个交互效果。", "",
                    "[浏览器展示](web/standalone.html) · [研究说明](README.md) · [原生展示](native/README.md)", "",
                    "本文件由 `scripts/build_gallery.py` 从实际 Metal 签名与上游参数表生成。中文描述为本研究补充；每种效果都对应独立的原始算法。", "",
                    "## 总览", "", "| 序号 | 效果 | 修饰器 | 分类 | 驱动 |", "| --- | --- | --- | --- | --- |"]
    for shader in shaders:
        kind = "交互" if shader["category"] == "触摸交互" else "时间" if shader["timeUsed"] else "参数" if shader["animated"] else "静态"
        capabilities.append(f"| {shader['index']:02} | {shader['name']} / {shader['title']} | `{shader['modifier']}` | {shader['category']} | {kind} |")
    capabilities.extend(["", "## 公共修饰器参数", "",
                         "所有修饰器还接受 `maxSampleOffset: CGSize`，默认 `64×64`，表示向各轴偏移采样的最大距离。强位移需要增大此值；它是 SwiftUI 的采样边界声明。本浏览器预览不模拟 SwiftUI 的采样边界裁剪，使用完整图像采样。", "",
                         "## 完整效果与参数", ""])
    for shader in shaders:
        capabilities.extend([f"### {shader['index']:02} · {shader['name']} / {shader['title']}", "", shader["description"], "",
                             f"原理：{shader['principle']}", "",
                             f"原始实现：[`{shader['metal']}`](upstream/Sources/SwiftUIShaders/Shaders/SwiftUIShaders.metal#L{shader['line']})。", "",
                             "| 参数 | 含义 | 上游默认 | 上游建议范围 |", "| --- | --- | --- | --- |"])
        for param in shader["params"]:
            bounds = "未指定" if param["min"] is None else f"{param['min']} ～ {param['max']}"
            capabilities.append(f"| `{param['label']}` | {param['name']} | `{param['default']}` | {bounds} |")
        notes = [p["label"] + "：" + p["rangeNote"] for p in shader["params"] if p.get("rangeNote")]
        if notes: capabilities.extend(["", " ".join(notes)])
        if shader["id"] == "TouchRipple":
            capabilities.extend(["", "调用方必须在触摸后持续更新 `touchAge`；只设置一个固定值会得到相应时刻的静态波纹。本页支持点击、时间推进和手动调整。"])
        if shader["id"] == "Shatter":
            capabilities.extend(["", "上游以动画包装器传入 `time`，但函数体不使用它。碎片散开程度由 `explode` 控制；只播放时间不会改变画面。"])
        capabilities.append("")
    return {ROOT / "web/shaders.json": json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
            ROOT / "web/LICENSE.upstream.txt": license_text,
            ROOT / "CAPABILITIES.md": "\n".join(capabilities)}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail if generated files are stale")
    args = parser.parse_args()
    for path, content in build().items():
        if args.check:
            assert path.read_text(encoding="utf-8") == content, f"Stale: {path}"
        else:
            path.write_text(content, encoding="utf-8", newline="\n")
    print("41/41 shader algorithms and parameter mappings verified." if args.check else "Generated 41 WebGL shaders with original parameter order and defaults.")
