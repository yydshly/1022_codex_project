"""Inventory attributed artwork; Pillow is needed only when refreshing this manifest."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from PIL import Image

PROJECT = Path(__file__).resolve().parents[1]
SHA = "12a70f6e4d9200b28a95d1b81c808439a5590c74"
BASE = f"https://github.com/nevertoday/xxd-panel-106/blob/{SHA}"
SAMPLES = [
    (5, "城市与摩天轮", "城市", "left-right", "保留天际线与摩天轮关系；深蓝夜景转为奶油白、淡紫与蜜桃色。"),
    (6, "一盏灯，一杯酒", "生活", "left-right", "灯光、瓶杯与花束成为视觉锚点；光感转成明亮的几何色块。"),
    (7, "蒲公英与落日", "植物", "left-right", "保留放射状花球、竖直花茎与飞散方向，删去石墙与杂草。"),
    (8, "送给你的花束", "植物", "left-right", "保留花束整体轮廓、黑包装与红色系；部分字形并非像素字体。"),
    (9, "城市的灯光记忆", "城市", "top-bottom", "建筑高度与发光道路保留，蓝紫与粉黄像素重构城市节奏。"),
    (10, "石拱门里的花", "植物", "top-bottom", "拱门、斜向枝条和粉色花朵保留，石材与叶片细节大幅简化。"),
    (11, "骑向光里", "动作", "top-bottom", "保留骑手、马匹和弧形运动方向；原图中的光弧转为暖色像素轨迹。"),
    (12, "露营的一杯微光", "生活", "top-bottom", "保留提灯、杯子与倾倒动作，深色背景转为温暖浅底。"),
]
FINALS = [
    ("top-bottom", "上下对照 · 自动英文", "1536x2048", "prompt", 1, "摄影参考区由模型生成；设计区英文为 SOME PLACES STAY SOFT。"),
    ("left-right", "左右对照 · 指定中文", "2048x1152", "exact", 1, "指定中文「把巴黎留在这一刻」正确；分界检测在 x=835，中线为836。"),
    ("design-only", "纯设计海报 · 无文字", "1536x2048", "none", 2, "重试后去除摄影分区；铁塔、河流与桥梁可辨，细节仍偏密。"),
    ("wallpaper-phone", "手机壁纸 · 连贯定调", "1440x3200", "none", 2, "全幅像素，竖向重构；它是其余三端的视觉家族参考。"),
    ("wallpaper-ipad", "平板壁纸 · 连贯", "1536x2048", "none", 1, "同时参考原照与手机定调图，重新安排天空与河面。"),
    ("wallpaper-desktop", "电脑壁纸 · 连贯", "2560x1440", "none", 1, "横向展开河面与桥梁，维持同一柔彩像素语言。"),
    ("wallpaper-watch", "手表壁纸 · 连贯", "1024x1024", "none", 2, "首次比例错误；重试后为正方形。未模拟表盘或验证真机可读性。"),
]


def describe(path: str, **fields: object) -> dict:
    target = PROJECT / path
    with Image.open(target) as bitmap:
        width, height = bitmap.size
    return {"path": path, "width": width, "height": height,
            "sha256": hashlib.sha256(target.read_bytes()).hexdigest(), **fields}


def main() -> None:
    samples = [describe(f"assets/upstream/sample-{number:02}.png", id=f"sample-{number:02}",
                        title=title, category=category, mode=mode, note=note,
                        source=f"{BASE}/assets/examples/sample-{number:02}.png",
                        provenance="upstream", license="PolyForm Noncommercial 1.0.0; no separate sample license found")
               for number, title, category, mode, note in SAMPLES]
    finals = [describe(f"assets/demo/{key}.png", id=key, title=title, requested_pixels=requested,
                      text_mode=text_mode, attempts=attempts, note=note, provenance="generated-in-this-study",
                      prompt=f"prompts/{key}{'-retry' if attempts == 2 else ''}.txt",
                      references=["assets/demo/source-paris.jpg"] +
                      (["assets/demo/wallpaper-phone.png"] if key in ("wallpaper-ipad", "wallpaper-desktop", "wallpaper-watch") else []))
              for key, title, requested, text_mode, attempts, note in FINALS]
    rejected = [describe(f"assets/demo/rejected/{key}-first.png", id=f"{key}-first", title=title,
                         reason=reason, prompt=f"prompts/{key}.txt", provenance="rejected-generation")
                for key, title, reason in (
                    ("design-only", "纯设计首次失败", "错误地保留上下摄影对照分区"),
                    ("wallpaper-phone", "手机壁纸首次失败", "错误地保留上下摄影对照分区"),
                    ("wallpaper-watch", "手表壁纸首次失败", "请求正方形，返回3:4竖版"),
                )]
    source = describe("assets/demo/source-paris.jpg", title="Eiffel Tower, Paris France", photographer="Chris Karidis",
                      source="https://unsplash.com/photos/eiffel-tower-paris-france-nnzkZNYWHaU",
                      download="https://images.unsplash.com/photo-1502602898657-3e91760cbb34?w=2400&q=90&fit=max",
                      license="Unsplash License", license_url="https://unsplash.com/license", provenance="real-photograph")
    guides = [describe("assets/library-overview.png", id="library-overview", title="一图读懂 XXD Panel 106",
                       provenance="generated-explainer", prompt="guides/overview-prompt.txt",
                       generation_calls=1, tool="built-in image_gen.imagegen",
                       references=["assets/demo/source-paris.jpg", "assets/demo/left-right.png"],
                       note="本研究生成的理解总结图：能力、单一风格、提示词、效果差异、意义与边界。图中缩略图为示意，提示词为摘要；完整原文与真实实测另列。")]
    payload = {"study_date": "2026-10-21", "upstream_commit": SHA,
               "execution": {"tool": "built-in image_gen.imagegen", "underlying_model": "not exposed by tool",
                             "total_generation_calls": 10, "retained_outputs": 7, "rejected_outputs": 3,
                             "pixel_preserving_composition": False, "metadata_removed": False,
                             "note": "Executed the pinned style brief and relevant runtime contract manually through the built-in tool. Skill was not installed globally; upstream API bridge was not run."},
               "source": source, "upstream_samples": samples, "demo_outputs": finals, "rejected_outputs": rejected,
               "study_guides": guides,
               "seam_audit": {"tool": f"{BASE}/scripts/compose_panel.py", "top-bottom": {"axis": "y", "midpoint": 724, "detected": 724, "offset_pixels": 0},
                              "left-right": {"axis": "x", "midpoint": 836, "detected": 835, "offset_pixels": -1},
                              "note": "Heuristic strongest luminance transition; not a semantic or aesthetic guarantee."}}
    (PROJECT / "media.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Inventoried {len(samples)} upstream examples, {len(finals)} final outputs, {len(rejected)} rejected outputs and {len(guides)} study guide.")


if __name__ == "__main__":
    main()
