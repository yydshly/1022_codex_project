"""Export pinned upstream rules and compiler output; --check performs no repo writes."""
from __future__ import annotations

import argparse
from dataclasses import fields
from hashlib import sha256
import importlib
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile

COMMIT = "8ced16f3ebd84be0ce8e29658ffd9d080f5e72ea"
REPO = "https://github.com/swping999/scene-card-studio"
ROOT = Path(__file__).resolve().parents[1]
SNAPSHOTS = [
    "skills/scene-card-studio/SKILL.md",
    *[f"skills/scene-card-studio/references/{name}.md" for name in (
        "scene-card", "systems-and-profiles", "prompt-compiler", "synthesis", "privacy"
    )],
    "DESIGN_PRINCIPLES.md",
]
SELECTED = [
    ("minimal-editorial", "source-led"),
    ("memory-atlas", "watercolor-chronicle"),
    ("memory-atlas", "threaded-landscape"),
    ("memory-atlas", "selective-material-relief"),
    ("memory-atlas", "chinese-ink-poetry"),
]


def git(upstream: Path, *args: str) -> bytes:
    return subprocess.check_output(["git", "-C", str(upstream), *args])


def json_bytes(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def export(upstream: Path) -> tuple[dict[str, bytes], dict]:
    if git(upstream, "rev-parse", "HEAD").decode().strip() != COMMIT:
        raise ValueError(f"Upstream HEAD must be {COMMIT}")
    # Verify every package module before importing upstream code.
    code_records = []
    for path in sorted((upstream / "src/moments_to_pages").glob("*.py")):
        relative = path.relative_to(upstream).as_posix()
        committed = git(upstream, "show", f"{COMMIT}:{relative}")
        if path.read_bytes().replace(b"\r\n", b"\n") != committed.replace(b"\r\n", b"\n"):
            raise ValueError(f"Modified upstream code: {relative}")
        code_records.append({"path": relative, "git_blob_sha256": sha256(committed).hexdigest()})
    sys.path.insert(0, str(upstream / "src"))
    model = importlib.import_module("moments_to_pages.model")
    systems = importlib.import_module("moments_to_pages.narrative_systems")
    profiles = importlib.import_module("moments_to_pages.expression_profiles")
    compiler = importlib.import_module("moments_to_pages.prompt_compiler")
    if compiler.COMPILER_VERSION != "0.7.0":
        raise ValueError("Unexpected compiler version")

    files: dict[str, bytes] = {}
    snapshots = []
    for relative in [*SNAPSHOTS, "LICENSE"]:
        content = git(upstream, "show", f"{COMMIT}:{relative}")
        target = "LICENSE.scene-card-studio.txt" if relative == "LICENSE" else f"upstream/{relative}"
        files[target] = content
        snapshots.append({"source": relative, "local": target, "sha256": sha256(content).hexdigest(),
                          "url": f"{REPO}/blob/{COMMIT}/{relative}"})

    canonical = {}
    aliases = {}
    for system in systems.SUPPORTED_SYSTEMS:
        canonical[system] = {}
        for name, rule in profiles.EXPRESSION_PROFILES[system].items():
            if rule.get("alias_for"):
                aliases[f"{system}/{name}"] = rule["alias_for"]
            else:
                canonical[system][name] = rule
    profile_names = sorted({name for rules in canonical.values() for name in rules})
    if len(canonical) != 11 or len(profile_names) != 24:
        raise ValueError("Unexpected system or canonical profile count")
    common = {"repository": REPO, "commit": COMMIT, "compiler_version": compiler.COMPILER_VERSION,
              "license": "Apache-2.0"}
    files["rules/upstream-rules.json"] = json_bytes({
        "source": common, "narrative_systems": systems.NARRATIVE_SYSTEMS,
        "canonical_profile_names": profile_names, "aliases": aliases,
        "expression_profiles_by_system": canonical, "review_policy": compiler.REVIEW_POLICY,
    })

    block_names = [field.name for field in fields(compiler.PromptBlocks)]
    templates = []
    prompt_count = 0
    with tempfile.TemporaryDirectory(prefix="scene-card-template-") as temp:
        temporary = Path(temp)
        for index in range(2):
            # The compiler only checks file existence and hashes here. These are
            # explicit text placeholders, not photos; source records are discarded.
            (temporary / f"source-{index}.txt").write_text("SYMBOLIC INPUT; NOT A PHOTO", encoding="utf-8")

        def card(index: int, multiple: bool):
            suffix = str(index + 1) if multiple else ""
            token = lambda name: "{{" + name + suffix + "}}"
            return model.SceneCard(
                source=str(temporary / f"source-{index}.txt"), width=1200, height=1500,
                palette=[], brightness=.5, saturation=.3, orientation="portrait", caption="",
                observation=model.Observation([token("subjects")], token("gesture"), [token("quiet_regions")]),
                interpretation=model.Interpretation(token("intent"), [token("tone")], 1., "symbolic-template"),
                direction=model.Direction(
                    story_role=("opening" if index == 0 else "closing") if multiple else "moment",
                    director_note=token("director_note"), layout_emphasis=token("emphasis")),
                transformation=model.TransformationPolicy(
                    must_preserve=[token("must_preserve")], may_transform=[token("may_transform")],
                    must_remove=[token("must_remove")]),
            )

        for system, supported in canonical.items():
            for profile in supported:
                for count in (1, 2):
                    manifest = compiler.compile_manifest(
                        [card(i, count > 1) for i in range(count)], system,
                        aspect_ratio="4:5", expression_profile=profile)
                    expected_count = count if systems.NARRATIVE_SYSTEMS[system]["prompt_mode"] == "per-source" else 1
                    expected_mode = "single-photo" if count == 1 else (
                        "multi-photo-per-source" if expected_count == count else "multi-photo-synthesis")
                    if len(manifest["prompts"]) != expected_count or manifest["source_mode"] != expected_mode:
                        raise ValueError(f"Incorrect source mode or prompt count for {system}/{profile}")
                    prompts = []
                    for prompt in manifest["prompts"]:
                        if list(prompt["blocks"]) != block_names:
                            raise ValueError("Missing or reordered prompt blocks")
                        rebuilt = compiler.PromptBlocks(**prompt["blocks"]).render()
                        if rebuilt != prompt["compiled_prompt"]:
                            raise ValueError("Compiled prompt does not match blocks")
                        if str(temporary) in rebuilt:
                            raise ValueError("Placeholder path leaked into template")
                        prompts.append({key: prompt[key] for key in ("id", "source_indexes", "blocks", "compiled_prompt")})
                    prompt_count += len(prompts)
                    templates.append({"system": system, "expression_profile": profile,
                                      "source_count": count, "source_mode": expected_mode, "prompts": prompts})

    files["rules/compiled-templates.json"] = json_bytes({
        "source": common, "artifact_type": "symbolic-prompt-templates", "not_generation_evidence": True,
        "parameters": {"aspect_ratio": "4:5", "palette": "source-derived fallback", "metadata": "omitted",
                       "preserve_lighting": False, "preserve_perspective": False,
                       "note": "These fixed optional parameters do not cover every possible Scene Card value."},
        "placeholder_fields": ["subjects", "gesture", "quiet_regions", "intent", "tone", "director_note",
                               "emphasis", "must_preserve", "may_transform", "must_remove"],
        "multi_source_suffix": "1 and 2 identify separate source cards; do not merge their constraints blindly.",
        "templates": templates,
    })
    selected_lines = ["# 精选五组上游原始编译模板", "",
                      "英文指令由固定版本原编译器导出。替换全部 `{{字段}}`，并将真实原图作为图像参考。", "",
                      "这些是单图模板，固定画幅 4:5；目标尺寸／格式需结合实际工具设置并核验。", "",
                      "主体、动作、情绪、导演意图、保留／变化／删除字段须据实际照片填写，不凭空补内容。", "",
                      "光线／透视保留等可选开关未全量展开；模板不等于上游完整执行清单。", "",
                      "完整来源与许可见 [NOTICE](../../NOTICE.md)。", ""]
    for system, profile in SELECTED:
        template = next(item for item in templates if item["system"] == system
                        and item["expression_profile"] == profile and item["source_count"] == 1)
        name = f"{system}--{profile}.txt"
        # Keep this body byte-identical to compiled_prompt + a final newline.
        files[f"prompts/extracted/{name}"] = (template["prompts"][0]["compiled_prompt"] + "\n").encode("utf-8")
        selected_lines.append(f"- [{system} + {profile}]({name})")
    files["prompts/extracted/README.md"] = ("\n".join(selected_lines) + "\n").encode("utf-8")

    guide = (ROOT / "prompts/03-creative-rules.zh-CN.md").read_text(encoding="utf-8")
    table = "\n".join(["| 系统 | 可用表达 |", "| --- | --- |", *[
        f"| `{system}` | " + "、".join(f"`{name}`" for name in supported) + " |"
        for system, supported in canonical.items()]])
    guide, replaced = re.subn(r"(?s)(<!-- COMPATIBILITY:START -->).*?(<!-- COMPATIBILITY:END -->)",
                              lambda match: match[1] + "\n" + table + "\n" + match[2], guide)
    if replaced != 1:
        raise ValueError("Missing or duplicated compatibility markers")
    files["prompts/03-creative-rules.zh-CN.md"] = guide.encode("utf-8")
    pair_count = sum(map(len, canonical.values()))
    summary = {"system_count": len(canonical), "canonical_profile_count": len(profile_names),
               "compatible_pair_count": pair_count, "source_mode_template_count": len(templates),
               "compiled_prompt_count": prompt_count, "block_count": len(block_names)}
    files["SOURCE.json"] = json_bytes({
        **common, "recorded_date": "2026-10-21", "snapshots": snapshots,
        "code_git_blobs": code_records, "code_check": "working tree equals commit except CRLF/LF normalization",
        "extraction": summary,
        "compiled_templates_are_placeholders": True, "new_image_generation_performed": False,
    })
    return files, summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--upstream", required=True, type=Path)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    files, summary = export(args.upstream.resolve())
    failures = []
    for relative, content in files.items():
        destination = ROOT / relative
        if args.check:
            if not destination.is_file() or destination.read_bytes() != content:
                failures.append(relative)
        else:
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(content)
    if failures:
        raise ValueError("Missing or changed exports: " + ", ".join(failures))
    print(json.dumps({"mode": "check" if args.check else "export", "files": len(files), **summary}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
