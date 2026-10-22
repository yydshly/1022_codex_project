"""Prepare and record an actual emotion-art-direction image trial; no model calls."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil

from PIL import Image

PROJECT = Path(__file__).resolve().parents[1]
ASSETS = PROJECT / "assets" / "skill-trial"
SKILL = PROJECT / "skills" / "emotion-art-direction"

REFERENCE = """Use case: product-mockup.
Asset type: neutral subject identity reference for an art-direction study, one portrait 4:5 image.
Create one photorealistic, unbranded vermilion-red wooden side chair, fully visible in a front three-quarter view, standing on a seamless light neutral-gray studio floor with a neutral-gray background. The chair has a gently arched top back rail, three vertical wooden back slats, a solid square seat with softly rounded corners, four straight wooden legs and low wooden stretchers. It has no arms, cushion, upholstery, wheels, metal or ornament. The red paint is matte with fine wood grain and very subtle natural edge wear; the structure is sound and usable.
Use even neutral studio light, a modest contact shadow, realistic joinery, normal perspective, and accurate proportions. The chair fills about 65 percent of the image height; keep every leg, the back and all the seat inside the image. This image is only a clear identity plate, not an emotional finished scene or an artistic control baseline.
No people, extra chairs, props, branding, captions, typography, swatches, frames or watermark. Produce one complete image, not a collage or contact sheet.
"""

COMMON = """Use case: stylized-concept.
Asset type: one finished portrait 4:5 fine-art photographic image for an exhibition concept study, without typography.
Input image 1 is the SUBJECT IDENTITY REFERENCE only: the red wooden chair. It is not an edit target whose gray backdrop or framing must be preserved. Recreate this same recognizable chair in the new art-directed scene, maintaining its arched top rail, back-slat arrangement, square seat, four straight legs, low stretchers, matte vermilion-red paint and wood texture. Keep it structurally complete and usable, with credible perspective, physical support and contact shadows. Do not change the chair into a different furniture design. There is exactly one chair and no person.
Shared visual family: photorealistic constructed scenes, tactile real materials, restrained film grain, clear spatial hierarchy and deliberate camera composition. The artistic direction can change the environment, camera distance, composition, light and spatial relationship. The feeling must be supported by those relationships as well as color.
"""

PROMPTS = {
    "reference": REFERENCE,
    "safe": COMMON + """
Artistic intent: safety and belonging, a place where one could comfortably pause. Let the empty chair feel available and supported, not abandoned. Avoid confinement, forced cheerfulness, glossy luxury advertising and sterile furniture catalog display.
Art direction: quiet, tactile editorial interior photography. Place the chair beside a softly lit window in a modest, uncluttered room with warm off-white lime-plaster walls and a honey-toned wooden floor. A simple off-white linen curtain at the edge of the window supports the natural texture; no other furniture or decorative objects.
Composition: a human-height front three-quarter medium view; the complete chair occupies about half the frame height and sits naturally a little off-center. Maintain stable verticals, generous breathing room around the back, an open empty seat angled slightly toward the viewer, and clearly grounded feet. The surrounding wall and floor should form a reliable, welcoming corner rather than a rigidly symmetrical box.
Light and palette: soft, broad morning window light, gentle penumbra, warm neutral plaster and natural wood, with the chair retaining its red identity. Expose real paint, wood grain and linen without smoothing away texture. Warmth stays modest; the sense of safety comes from open access, support, balanced space and a usable seat.
No text, logo, watermark, people, additional seating, particles, HUD, fragmentation, dramatic shafts of light or surreal distortions. Produce one complete artwork, not a split comparison.
""",
    "solitude": COMMON + """
Artistic intent: solitude, quiet distance and a presence that has not yet been answered. Keep dignity and a small trace of life; avoid misery, horror, punishment, collapse or a dead-looking object.
Art direction: minimalist architectural photographic poetry. Put the chair alone in a very large, unoccupied pale blue-gray concrete hall with a subtly visible floor-to-wall boundary. There are no doors, posters, windows in view, people, additional furniture or symbolic props. Matte concrete has faint genuine texture and a believable scale, not a featureless synthetic gradient.
Composition: a distant, level view with a modestly long photographic lens; the complete chair is a small but legible presence, about 15–18 percent of image height, placed low in the frame with substantial unoccupied space around and above it. Ground it with a small soft contact shadow and preserve the actual chair structure. Let the viewer feel the distance between their position and the chair; do not fill the silence with decoration.
Light and palette: diffuse overcast daylight, low-saturation gray-blue space with a restrained tonal range. Keep the chair's matte vermilion red as one small warm presence, not a neon spotlight. The art should feel expansive, patient and unresolved rather than ominous.
No text, logo, watermark, fragments, particles, HUD, fog, ruined walls, chains or harsh theatrical beams. Produce one complete artwork, not a split comparison.
""",
    "unease": COMMON + """
Artistic intent: controlled unease and pressure, as if space were encroaching on a small usable place. Make the source of pressure visually clear while the chair remains intact. Avoid gore, jump-scare symbols, broken furniture and visual noise.
Art direction: a restrained surreal brutalist installation photographed as a tangible real set. Place the chair between two enormous heavy charcoal-blue concrete wall planes that converge toward it in perspective; a low massive horizontal slab occupies part of the upper frame. Leave a visible gap between the concrete and the chair: it is not being physically crushed. Build tension through mass, proximity and narrowed access.
Composition: a close, slightly low front three-quarter view. The chair occupies around 40–45 percent of image height, fully visible with every foot grounded. Large architectural masses crop at the image edges and dominate the available headroom. Converging lines and an oblique hard shadow direct attention toward the empty seat; retain one legible silhouette and a clear physical floor.
Light and palette: one directional hard side light catches the red seat and part of the back, while the concrete retains layered dark slate-blue tones. Shadows are deep but still reveal the chair's joinery and the gaps around it. Preserve matte red paint, concrete pores and realistic edges. The tension comes from restricted space and the weight of surrounding structures, not from changing the chair's color or adding effects.
No text, logo, watermark, people, extra chairs, neon, eyes, chains, particles, HUD, debris, deformed geometry or a comic-book horror look. Produce one complete artwork, not a split comparison.
""",
}

BRIEFS = [
    {"id": "safe", "code": "A", "title": "安心 / 可以停留的角落", "emotion_profile": "safe", "intent": "让人感到稳定、被容纳，空座位仍可进入与停留。", "avoid": "封闭、沉闷、过度甜美或奢华广告感", "art_direction": "有触感的生活编辑摄影", "translation": "中景与可进入的座面、稳定支撑关系、均衡留白、柔窗光和真实材料。", "planned_scale": "椅子约占画幅高度一半", "checks": ["空座位是否显得可进入、可停留？", "安心是否有空间与落点支持，而非只因为暖色？", "有没有变成普通家具目录或过度甜美？"]},
    {"id": "solitude", "code": "B", "title": "孤独 / 没有等到的入座者", "emotion_profile": "solitude", "intent": "在大空间里保留一处尚未得到回应的存在，安静且有距离。", "avoid": "悲惨、恐怖、破败或惩罚感", "art_direction": "极简建筑摄影诗", "translation": "远距离、小主体、大留白、灰青漫射光与少量主体暖色。", "planned_scale": "椅子约占画幅高度15–18%", "checks": ["观看距离与无回应的空白是否清楚？", "孤独是否仍可能被读成宁静或等待？", "小主体还保留可辨认的结构吗？"]},
    {"id": "unease", "code": "C", "title": "不安 / 被挤压的位置", "emotion_profile": "unease", "intent": "让人感到空间正在逼近，座位仍完整而可用。", "avoid": "廉价恐怖、破坏主体、满屏噪声", "art_direction": "超现实粗野建筑装置摄影", "translation": "巨大近墙、低顶板、收窄的进入路径和硬斜影，形成可辨认的压力来源。", "planned_scale": "椅子约占画幅高度40–45%", "checks": ["压力具体来自哪一处空间关系？", "椅子有没有被变形或真的压坏？", "画面是否也可能被读成庄严或力量？"]},
]


def write(name: str, value: dict) -> None:
    (ASSETS / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def initialize() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    if (ASSETS / "protocol.json").exists():
        raise SystemExit("An existing trial protocol is preserved; use a new trial for changed prompts.")
    reads = ["SKILL.md", "references/emotion-map.md", "references/image-template.md", "references/emotions/safe.md", "references/emotions/solitude.md", "references/emotions/unease.md", "references/styles.md", "references/cases/product.md"]
    hashes = [{"file": file, "sha256": hashlib.sha256((SKILL / file).read_bytes()).hexdigest()} for file in reads]
    for identifier, prompt in PROMPTS.items():
        (ASSETS / (identifier + "-prompt.txt")).write_text(prompt, encoding="utf-8")
    write("protocol.json", {"version": 1, "id": "red-chair-skill-trial", "date": "2026-10-22", "status": "planned", "generated": False,
        "skill": {"name": "emotion-art-direction", "invocation": "Read and applied the installed Skill and selected references in this conversation", "snapshot": hashes},
        "subject": "一把无品牌朱红色木椅，弧形顶梁、竖向椅背条、方形坐面、四条直腿和低横撑，无扶手",
        "method": "先生成中性身份参考，再以同一参考分别生成三种完整艺术方向；每方向一次调用、保存全部结果、原图不加工。",
        "common_rules": ["同一身份参考、同一4:5目标画幅、完整可用红椅", "摄影写实材料与可辨认的空间层级", "没有画内文字、人物、数据粒子或HUD"],
        "varied": ["目标感受与避免感受", "艺术方向", "主体尺度、观看距离、空间关系、光色与构图"],
        "cases": BRIEFS, "planned_calls": 4, "generation_tool": "Built-in image_gen", "model_version": None, "seed": None,
        "limitation": "中性图仅作主体身份参考；本轮不是有无Skill、仅情绪词或单变量因果实验。每方向一张，观众情绪仍需反馈。",
        "actual_results": []})
    print("Prepared exact prompts and pre-generation protocol for one identity plate and three directions.")


def record(results: list[str]) -> None:
    protocol = json.loads((ASSETS / "protocol.json").read_text(encoding="utf-8"))
    executed = json.loads((ASSETS / "execution.json").read_text(encoding="utf-8"))
    for identifier, prompt in executed["prompts"].items():
        # Preserve the exact string actually passed, including its line endings.
        (ASSETS / (identifier + "-prompt.txt")).write_bytes(prompt.encode("utf-8"))
    mapping = dict(value.split("=", 1) for value in results)
    assert set(mapping) == set(PROMPTS), "Record all four actual outputs"
    records = []
    for identifier in PROMPTS:
        source = Path(mapping[identifier]).resolve()
        assert source.is_file() and source.suffix.lower() == ".png"
        target = ASSETS / (identifier + ".png")
        if target.exists():
            assert target.read_bytes() == source.read_bytes(), "Existing original differs; do not overwrite"
        else:
            shutil.copyfile(source, target)
        with Image.open(target) as picture:
            picture.verify()
        with Image.open(target) as picture:
            width, height = picture.size
        records.append({"id": identifier, "file": target.name, "prompt": identifier + "-prompt.txt", "width": width, "height": height,
                        "bytes": target.stat().st_size, "sha256": hashlib.sha256(target.read_bytes()).hexdigest(),
                        "prompt_sha256": hashlib.sha256((ASSETS / (identifier + "-prompt.txt")).read_bytes()).hexdigest(),
                        "input": None if identifier == "reference" else "reference.png", "input_role": None if identifier == "reference" else "subject identity reference only",
                        "tool": "Built-in image_gen", "model_version": None, "seed": None, "calls": 1, "revisions": 0,
                        "original_tool_path": str(source), "postprocessing": "none"})
    protocol["status"] = "generated"
    protocol["generated"] = True
    protocol["actual_results"] = records
    write("protocol.json", protocol)
    write("manifest.json", {"date": "2026-10-22", "tool": "Built-in image_gen", "skill": "emotion-art-direction", "calls": 4, "outputs": records})
    print(json.dumps({"recorded": len(records), "outputs": [{k: row[k] for k in ("id", "width", "height", "bytes")} for row in records]}, ensure_ascii=False))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--init", action="store_true")
    parser.add_argument("--result", action="append", help="Actual tool output as id=absolute-path, repeated for all four images")
    parser.add_argument("--finalize", action="store_true", help="Combine actual outputs with the author's completed review")
    args = parser.parse_args()
    if args.init:
        initialize()
    elif args.result:
        record(args.result)
    elif args.finalize:
        protocol = json.loads((ASSETS / "protocol.json").read_text(encoding="utf-8"))
        review = json.loads((ASSETS / "review.json").read_text(encoding="utf-8"))
        execution = json.loads((ASSETS / "execution.json").read_text(encoding="utf-8"))
        assert protocol["generated"] and len(protocol["actual_results"]) == 4
        outputs = {row["id"]: row for row in protocol["actual_results"]}
        reviews = {row["id"]: row for row in review["cases"]}
        cases = []
        for brief in protocol["cases"]:
            row = {**brief, **reviews[brief["id"]], "actual": outputs[brief["id"]], "prompt": execution["prompts"][brief["id"]]}
            box = row["bbox"]
            row["approximate_height_fraction"] = (box[3] - box[1]) / row["actual"]["height"]
            assert row["prompt"].encode("utf-8") == (ASSETS / row["actual"]["prompt"]).read_bytes()
            cases.append(row)
        protocol["status"] = "completed"
        write("protocol.json", protocol)
        study = {"version": 1, "id": protocol["id"], "date": protocol["date"], "status": "completed", "generated": True,
            "skill": protocol["skill"], "subject": protocol["subject"], "method": protocol["method"], "common_rules": protocol["common_rules"],
            "varied": protocol["varied"], "actual_calls": 4, "reference": {**outputs["reference"], **review["reference"]}, "cases": cases,
            "review_method": review["method"], "findings": review["findings"], "limits": review["limits"], "independent_audience_evaluation": False,
            "model_version": None, "seed": None, "postprocessing": "none", "repair_executed": False}
        write("study.json", study)
        files = ["protocol.json", "execution.json", "review.json", "study.json"] + [name + ext for name in PROMPTS for ext in (".png", "-prompt.txt")]
        records = [{"file": file, "bytes": (ASSETS / file).stat().st_size, "sha256": hashlib.sha256((ASSETS / file).read_bytes()).hexdigest()} for file in files]
        write("manifest.json", {"date": protocol["date"], "tool": "Built-in image_gen", "skill": protocol["skill"], "calls": 4,
            "model_version": None, "seed": None, "outputs": protocol["actual_results"], "files": records, "postprocessing": "none"})
        print(json.dumps({"cases": len(cases), "asset_files": len(files) + 1, "actual_calls": 4, "approximate_height_fractions": {row["id"]: round(row["approximate_height_fraction"], 3) for row in cases}}, ensure_ascii=False))
    else:
        parser.error("Use --init before generation or --result to record actual originals")


if __name__ == "__main__":
    main()
