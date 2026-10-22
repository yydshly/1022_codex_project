"""Build and verify the portable emotion-art-direction Skill; optionally install a new copy.

Only local, attributed research materials are packaged. No generation service is called.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import zipfile

PROJECT = Path(__file__).resolve().parents[1]
NAME = "emotion-art-direction"
SKILL = PROJECT / "skills" / NAME
ASSETS = PROJECT / "assets"
OUTPUT = ASSETS / "skills"
ARCHIVE = OUTPUT / (NAME + ".zip")
MANIFEST = OUTPUT / (NAME + ".json")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(name: str, text: str) -> None:
    path = SKILL / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def build_references() -> list[Path]:
    library_path = ASSETS / "intent/templates.json"
    library = json.loads(library_path.read_text(encoding="utf-8"))
    emotions_path, styles_path = ASSETS / "emotions/profiles.json", ASSETS / "styles/profiles.json"
    emotions = json.loads(emotions_path.read_text(encoding="utf-8"))
    styles = json.loads(styles_path.read_text(encoding="utf-8"))
    assert emotions == library["supporting_libraries"]["emotion_profiles"]["data"], "Run prepare_intent_guide.py first"
    assert styles == library["supporting_libraries"]["style_branches"]["data"], "Run prepare_intent_guide.py first"
    inputs = [Path(__file__).resolve(), library_path, emotions_path, styles_path]
    for key, template in library["templates"].items():
        write("references/" + key + "-template.md", "# " + template["title"] + "\n\n按实际任务裁剪；【】为待填内容。\n\n" + template["text"])

    index = ["# 情绪方向索引", "", "21份档案是创作起点，可以组合或重新定义；不构成封闭分类或心理测量。先选最接近目标的一两份，读取对应文件，按当前任务与风格转译。", "",
             "档案中的标题与数据语言沿用海报研究的母风格。当前任务未选择该风格时，借鉴距离、光色、材质和关系即可；写实无字短片不需要因此添加标题或计算效果。", "",
             "主情绪决定整体，副情绪只补一处关系。表达含蓄、清晰或强烈，与粒子数量分开决定。", ""]
    vocab = emotions["vocabularies"]
    for family in emotions["families"]:
        index += ["## " + family["name"], "", "| 档案 | 目标感受 |", "| --- | --- |"]
        for profile in (row for row in emotions["profiles"] if row["family"] == family["id"]):
            identifier = profile["id"]
            assert re.fullmatch(r"[a-z0-9-]+", identifier)
            index.append(f"| [{profile['name']}](emotions/{identifier}.md) | {profile['goal']} |")
            visual = profile["visual"]
            lines = ["# " + profile["name"], "", "目标：" + profile["goal"], "", "避免：" + profile["avoid"], "",
                     "故事起点：" + profile["story"], "", "用途示例：" + profile["uses"], "", "## 视觉转译起点", "",
                     "- 配色：" + vocab["palette"][visual["palette"]], "- 光线：" + visual["light"],
                     "- 空间：" + visual["space"], "- 材质：" + visual["material"], "",
                     "## 选择海报母风格时可用的语言", "", "- 标题：" + visual["typography"],
                     "- 计算隐喻：" + visual["metaphor"], "- 计算关系：" + vocab["method"][visual["method"]] + " / " + vocab["extension"][visual["extension"]] + "；" + visual["data"], "",
                     "## 校准与返修", "", "常见跑偏：" + profile["drift"]["problem"], "", "返修依据：" + profile["drift"]["repair"], "", "先问：" + profile["check"]]
            write("references/emotions/" + identifier + ".md", "\n".join(lines))
        index.append("")
    write("references/emotion-map.md", "\n".join(index))

    original = library["supporting_libraries"]["original_style"]
    style_index = ["# 定制并延续风格规则", "", "先依据用户的参考与艺术意图选择风格，记录固定规则、可变项、禁用倾向和评审依据。表达形式不在这里时直接定义新规则。", "",
                   "## 原主风格 / " + original["name"], "", "仅在选择该家族时沿用以下关系：", ""]
    style_index += ["- " + rule for rule in original["invariants"]]
    style_index += ["", "保留识别中心及主体与数据的关系，在此基础上定制情绪、光色、画幅与强度。换成水墨或完全不同的视觉语言时，明确进入新风格，而不把旧家族规则全部强加进去。", "", "## 材料与绘画旁支", ""]
    for profile in styles["profiles"]:
        identifier = profile["id"]
        assert re.fullmatch(r"[a-z0-9-]+", identifier)
        style_index += [f"- [{profile['name']}](styles/{identifier}.md)：{profile['summary']}"]
        lines = ["# " + profile["name"], "", profile["summary"], "", "## 固定规则", ""]
        lines += ["- " + row for row in profile["invariants"]]
        lines += ["", "## 可变项", ""] + ["- " + row for row in profile["variables"]]
        lines += ["", "## 避免", ""] + ["- " + row for row in profile["avoid"]]
        lines += ["", "检查：" + profile["check"], "", "取舍：" + profile["tradeoff"]]
        write("references/styles/" + identifier + ".md", "\n".join(lines))
    style_index += ["", "## 自定义或系列风格", "", "从参考中提取可迁移的关系：主体与背景如何组织、光色与材质如何配合、文字是否参与、边界如何转换；分别写出每次保留与本次可变的部分。用认可作品与反例校准，不把某张参考的全部内容复制到每次任务。", "", "[固定研究版本的风格依据](" + original["source"] + ")"]
    write("references/styles.md", "\n".join(style_index))

    media = {
        "warm-bloom-poster.png": "assets/examples/flower.png",
        "validation/00-bottle-reference.png": "assets/examples/product-reference.png",
        "validation/02-bottle-solitude.png": "assets/examples/product-before.png",
        "validation/07-bottle-solitude-repaired.png": "assets/examples/product-after.png",
        "ai-film/shared-space-original.mp4": "assets/examples/shared-space.mp4",
        "ai-film/shared-space-02.jpg": "assets/examples/shared-space-02.jpg",
        "ai-film/shared-space-05.jpg": "assets/examples/shared-space-05.jpg",
        "ai-film/shared-space-08.jpg": "assets/examples/shared-space-08.jpg",
        "warm-bloom-prompt.txt": "references/cases/flower-actual-prompt.txt",
        "validation/02-bottle-solitude-prompt.txt": "references/cases/product-actual-prompt.txt",
        "validation/07-bottle-solitude-repaired-prompt.txt": "references/cases/product-actual-repair.txt",
        "ai-film/shared-space-prompt.txt": "references/cases/video-actual-prompt.txt",
    }
    media_records = []
    for original_path, target_path in media.items():
        source, target = ASSETS / original_path, SKILL / target_path
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        assert sha(source) == sha(target)
        media_records.append({"file": target_path, "source_in_project": "assets/" + original_path, "bytes": source.stat().st_size, "sha256": sha(source)})
        inputs.append(source)

    cases_index = ["# 实际案例索引", "", "按任务只选相关案例阅读。学习意图与具体要求的对应关系，不把花朵、香水瓶或共伞故事变成默认主体。实际历史指令、事后复用方案、实际观察分别标明。", "",
                   "| 案例 | 可学习的关系 | 实际边界 |", "| --- | --- | --- |",
                   "| [温柔花朵](cases/flower.md) | 写实材质、舒缓转化与留白共同支持靠近生命的意图 | 材料旁支；不能证明观众情绪命中 |",
                   "| [孤独产品与尺度返修](cases/product.md) | 小主体与大空间，以及根据具体偏差修尺度 | 孤独与宁静有歧义；字体问题未解决 |",
                   "| [被接纳的短片](cases/video.md) | 用邀请、回应和同行改变人物关系 | 动作提前、背影较多、声音未听审 |", "",
                   "图像工具未提供具体模型版本与种子；视频来自一次Seedance 2.0文字生成。三组均没有独立观众情绪命中率或因果结论。"]
    write("references/cases.md", "\n".join(cases_index))
    flower, product, video = library["cases"]
    write("references/cases/flower.md", "\n".join([
        "# 《风有形》/ 温柔生长", "", "艺术意图：" + flower["intent"], "", "具体转译：" + flower["translation"], "",
        "实际制作：2026-10-21，内置ImageGen一次文字生成，1122×1402；没有参考图片，没有后期，具体模型版本与种子未知。", "",
        "![实际输出的暖纸花朵海报](../../assets/examples/flower.png)", "",
        "[准确历史指令](flower-actual-prompt.txt)", "", "实际观察：" + flower["observation"], "",
        "## 事后整理的中文复用方案", "", flower["briefs"]["image"],
    ]))
    write("references/cases/product.md", "\n".join([
        "# 《之间》/ 距离与尺度返修", "", "艺术意图：" + product["intent"], "", "具体转译：" + product["translation"], "",
        "实际制作：2026-10-21至22，内置ImageGen；首轮和返修分别一次调用，均为1122×1402原件。具体模型版本与种子未知。首轮实际指令使用中性产品身份图，返修以首轮完整海报为编辑目标。", "",
        "[中性主体身份图](../../assets/examples/product-reference.png)", "",
        "![首轮海报](../../assets/examples/product-before.png)", "", "![实际尺度返修结果](../../assets/examples/product-after.png)", "",
        "[准确首轮指令](product-actual-prompt.txt) · [准确返修指令](product-actual-repair.txt)", "",
        "实际观察：" + product["observation"], "", "比例来自人工近似外接框，并非情绪分数。底部接触点略上移，玻璃、反射和计算细节仍有重绘；返修没有解决衬线字体偏差。", "",
        "## 图片复用方案（事后整理）", "", product["briefs"]["image"], "", "## 返修复用方案（事后整理）", "", product["briefs"]["repair"],
    ]))
    write("references/cases/video.md", "\n".join([
        "# 《留一点位置》/ 从疏离到被接纳", "", "艺术意图：" + video["intent"], "", "具体转译：" + video["translation"], "",
        "实际制作：2026-10-22，通过ChatArt调用Seedance 2.0一次文字生成视频；没有输入图片。请求1080p、16:9、10秒、有声；实际返回1902×1092、24fps、10.048秒、H.264/AAC双声道。原件没有重新编码或添加动画和声音。", "",
        "[实际AI原片](../../assets/examples/shared-space.mp4) · [准确历史指令](video-actual-prompt.txt)", "",
        "![原片2秒，撑伞者走近](../../assets/examples/shared-space-02.jpg)", "", "![原片5秒，目光回应与共伞](../../assets/examples/shared-space-05.jpg)", "", "![原片8秒，同伞前行](../../assets/examples/shared-space-08.jpg)", "",
        "实际观察：" + video["observation"], "", "3至5秒已形成邀请与回应，约6.5秒转身，未严格遵守原计划的0–3 / 3–7 / 7–10秒。双脚不在画面中，不能评价完整步态；没有完成听觉审片。被接纳是意图，不是已经得到独立观众验证的结论。", "",
        "## 事后整理的复用方案", "", video["briefs"]["video"],
    ]))
    write("references/media-provenance.json", json.dumps({"date": "2026-10-22", "files": media_records}, ensure_ascii=False, indent=2))
    write("references/provenance.md", "\n".join([
        "# 来源与制作记录", "", "本Skill由本研究原创整理，扩展了以情绪与艺术意图构造图片和视频提示词的方法。它不是上游项目的新版本，不包含模型权重或生成服务。", "",
        "风格研究依据：[algorithmic-sublime-poster固定提交846fac0a9fc247b480f71c9846c83815d2edfe41](https://github.com/xianxie6/algorithmic-sublime-poster/tree/846fac0a9fc247b480f71c9846c83815d2edfe41)。该研究提交没有独立LICENSE；本包没有搬运上游Skill原文、执行代码或第三方示例图片。主风格规则为研究概括。", "",
        "21份情绪档案和3份旁支是本研究的创作起点，按需拆分为独立参考。案例仅使用本研究已有的原创图像和实际AI视频，不包含第三方人物照片、品牌素材或外部音乐采样。生成结果不据此声明具有排他版权或适用于所有商业用途。", "",
        "每条案例标明工具、实际参数、输入角色和偏差。图片具体模型版本与种子未知；视频服务未返回权重版本和种子。人物均为虚构成年人。", "",
        "[原件与准确指令的SHA-256清单](media-provenance.json)。所有媒体与实际指令按字节复制；JPEG为从实际MP4提取的定位帧，不能代替原片。模板和中文复用方案为后续指导材料，不是历史准确指令。", "",
        "本Skill的提示词工作不依赖联网或外部服务；实际图片或视频生成依赖宿主可用的工具及其授权。", "",
    ]))
    return inputs


def skill_files() -> list[Path]:
    return sorted(path for path in SKILL.rglob("*") if path.is_file())


def verify() -> dict:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert ARCHIVE.stat().st_size == manifest["archive"]["bytes"] and sha(ARCHIVE) == manifest["archive"]["sha256"]
    assert set(row["file"] for row in manifest["files"]) == set(path.relative_to(SKILL).as_posix() for path in skill_files())
    with zipfile.ZipFile(ARCHIVE) as archive:
        assert len(archive.namelist()) == len(manifest["files"])
        for record in manifest["files"]:
            source = SKILL / record["file"]
            assert sha(source) == record["sha256"]
            assert hashlib.sha256(archive.read(NAME + "/" + record["file"])).hexdigest() == record["sha256"]
    for record in manifest["build_inputs"]:
        assert sha(PROJECT / record["file"]) == record["sha256"], "Source changed; rebuild the Skill pack"
    for path in SKILL.rglob("*.md"):
        for link in re.findall(r"\[[^\]]*\]\(([^)]+)\)", path.read_text(encoding="utf-8")):
            if link.startswith(("https://", "http://", "#")):
                continue
            target = (path.parent / link.split("#")[0]).resolve()
            assert target.is_relative_to(SKILL.resolve()) and target.is_file(), (path, link)
    return manifest


def install() -> Path:
    home = Path(os.environ["CODEX_HOME"]) if os.environ.get("CODEX_HOME") else Path.home() / ".codex"
    skill_home = (home / "skills").resolve()
    destination = (skill_home / NAME).resolve()
    assert destination.parent == skill_home and destination.name == NAME
    if destination.exists():
        existing = {p.relative_to(destination).as_posix(): sha(p) for p in destination.rglob("*") if p.is_file()}
        expected = {p.relative_to(SKILL).as_posix(): sha(p) for p in skill_files()}
        if existing != expected:
            raise SystemExit("An existing installed Skill differs; review it before updating. No files were overwritten.")
    else:
        skill_home.mkdir(parents=True, exist_ok=True)
        shutil.copytree(SKILL, destination)
    return destination


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Verify the existing portable pack and source inputs")
    parser.add_argument("--install", action="store_true", help="Install a new Skill into CODEX_HOME/skills; preserve differing existing copies")
    args = parser.parse_args()
    if not args.check:
        assert (SKILL / "SKILL.md").is_file() and (SKILL / "agents/openai.yaml").is_file()
        inputs = build_references()
        OUTPUT.mkdir(parents=True, exist_ok=True)
        files = skill_files()
        with zipfile.ZipFile(ARCHIVE, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
            for path in files:
                archive.write(path, NAME + "/" + path.relative_to(SKILL).as_posix())
        manifest = {"name": NAME, "date": "2026-10-22", "source": "skills/" + NAME,
                    "archive": {"file": ARCHIVE.name, "bytes": ARCHIVE.stat().st_size, "sha256": sha(ARCHIVE)},
                    "files": [{"file": path.relative_to(SKILL).as_posix(), "bytes": path.stat().st_size, "sha256": sha(path)} for path in files],
                    "build_inputs": [{"file": path.relative_to(PROJECT).as_posix(), "sha256": sha(path)} for path in inputs],
                    "emotion_profiles": 21, "style_branches": 3, "original_style_rules": 5, "actual_cases": 3,
                    "generation_calls": 0, "media_modified": False}
        MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    manifest = verify()
    destination = install() if args.install else None
    print(json.dumps({"name": NAME, "files": len(manifest["files"]), "archive_bytes": ARCHIVE.stat().st_size,
                      "verified": True, "installed_to": str(destination) if destination else None}, ensure_ascii=False))


if __name__ == "__main__":
    main()
