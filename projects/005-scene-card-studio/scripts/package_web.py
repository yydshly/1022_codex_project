"""Package the summarized study page and attributed source files (stdlib only)."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def table_rows(text: str, heading: str) -> list[list[str]]:
    section = text.split(heading, 1)[1].split("\n## ", 1)[0]
    return [[cell.strip().strip("`") for cell in line.strip().strip("|").split("|")]
            for line in section.splitlines() if line.startswith("| `")]


def package(check: bool = False) -> dict:
    rules = json.loads((ROOT / "rules/upstream-rules.json").read_text(encoding="utf-8"))
    guide = (ROOT / "prompts/03-creative-rules.zh-CN.md").read_text(encoding="utf-8")
    systems = []
    for ident, name, summary, mode in table_rows(guide, "## 叙事机制"):
        systems.append({"id": ident, "name": name, "summary": summary, "upstreamMode": mode,
                        "profiles": list(rules["expression_profiles_by_system"][ident])})
    profiles = [{"id": ident, "name": name, "summary": summary}
                for ident, name, summary in table_rows(guide, "## 表达方案")]
    assert {row["id"] for row in systems} == set(rules["narrative_systems"])
    assert {row["id"] for row in profiles} == set(rules["canonical_profile_names"])
    prompt_defs = (
        ("quick", "00-quick-use.zh-CN.txt", "先复制精简版，补上照片和你的要求。"),
        ("full", "01-direct-use.zh-CN.txt", "完整创作规则，适合多轮修改和多图任务。"),
        ("review", "04-review-and-retry.zh-CN.txt", "请同时提供原图、成片和上一轮要求。"),
    )
    prompts = [{"id": ident, "url": f"./prompts/{filename}", "note": note,
                "text": (ROOT / "prompts" / filename).read_text(encoding="utf-8")}
               for ident, filename, note in prompt_defs]
    manifest = json.loads((ROOT / "media.json").read_text(encoding="utf-8"))
    cases = json.loads((ROOT / "cases.json").read_text(encoding="utf-8"))["cases"]
    paths = {record["path"]: record["path"] for record in manifest["assets"]}
    paths["assets/overview.svg"] = "assets/overview.svg"
    paths["media.json"] = "media.json"
    paths["cases.json"] = "cases.json"
    study_guide = json.loads((ROOT / "study-guide.json").read_text(encoding="utf-8"))
    paths["study-guide.json"] = "study-guide.json"
    for key in ("image", "prompt"):
        record = study_guide[key]
        assert hashlib.sha256((ROOT / record["path"]).read_bytes()).hexdigest() == record["sha256"], record["path"]
        paths[record["path"]] = record["path"]
    for record in study_guide["reference_images"]:
        assert hashlib.sha256((ROOT / record["path"]).read_bytes()).hexdigest() == record["sha256"], record["path"]
    for case in cases:
        for record in case["evidence"].values():
            paths[record["path"]] = record["path"]
            assert hashlib.sha256((ROOT / record["path"]).read_bytes()).hexdigest() == record["sha256"]
        story = json.loads((ROOT / case["evidence"]["story.json"]["path"]).read_text(encoding="utf-8"))
        compiled = json.loads((ROOT / case["evidence"]["prompt-manifest.json"]["path"]).read_text(encoding="utf-8"))
        prompt = compiled["prompts"][0]
        assert compiled["system"] == case["system"] and compiled["expression_profile"] == case["expression_profile"]
        assert story[0]["interpretation"]["method"] == case["direction_method"]
        assert hashlib.sha256((ROOT / case["before"]["path"]).read_bytes()).hexdigest() == prompt["sources"][0]["sha256"]
        assert hashlib.sha256((ROOT / case["after"]["path"]).read_bytes()).hexdigest() == prompt["reference_output"]["sha256"]
        case["compiled_prompt"] = (ROOT / case["prompt_path"]).read_text(encoding="utf-8")
        assert case["compiled_prompt"] == prompt["compiled_prompt"] + "\n"
        paths[case["prompt_path"]] = case["prompt_path"]
    for path in sorted((ROOT / "prompts").glob("*")):
        if path.is_file():
            paths[path.relative_to(ROOT).as_posix()] = path.relative_to(ROOT).as_posix()
    for name in ("upstream-rules.json", "compiled-templates.json"):
        paths[f"rules/{name}"] = f"rules/{name}"
    for name in ("NOTICE.md", "LICENSE.scene-card-studio.txt", "SOURCE.json"):
        paths[name] = f"docs/{name}"
    paths["assets/upstream/ASSET_LICENSE.md"] = "assets/upstream/ASSET_LICENSE.md"
    for record in manifest["assets"]:
        assert hashlib.sha256((ROOT / record["path"]).read_bytes()).hexdigest() == record["sha256"], record["path"]
    files = {destination: (ROOT / source).read_bytes() for source, destination in paths.items()}
    files["data.js"] = ("window.SCENE_CARD = " + json.dumps(
        {"systems": systems, "profiles": profiles, "prompts": prompts, "cases": cases},
        ensure_ascii=False, separators=(",", ":")) + ";\n").encode("utf-8")
    for relative, content in files.items():
        target = ROOT / "web" / relative
        if check:
            if not target.is_file() or target.read_bytes() != content:
                raise ValueError(f"Missing or stale packaged file: {relative}")
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(content)
    summary = {"mode": "check" if check else "package", "files": len(files),
               "systems": len(systems), "profiles": len(profiles), "compatibility_pairs": sum(len(s["profiles"]) for s in systems),
               "prompt_tabs": len(prompts), "upstream_images": len(manifest["assets"]), "complete_cases": len(cases), "study_guide_images": 1}
    print(json.dumps(summary, ensure_ascii=False))
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    package(parser.parse_args().check)
