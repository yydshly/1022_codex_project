"""Generate the research atlas and verify its pinned source references (stdlib only)."""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import importlib.util
import json
from pathlib import Path
import re

PROJECT = Path(__file__).resolve().parents[1]
ROOT = PROJECT.parents[1]
COMMIT = "ca576b601bf84527102f1768372aa8cd96a3c55a"
UPSTREAM = f"https://github.com/vibegameengine/web-starter-kit-webgpu-pipline/blob/{COMMIT}/"
CACHE = ROOT / "_upstream" / f"webgpu-{COMMIT[:7]}"


def encoded(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2) + "\n"


def generate(check: bool = False) -> dict:
    spec = importlib.util.spec_from_file_location("research_catalog", PROJECT / "research_catalog.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    source = json.loads((PROJECT / "SOURCE.json").read_text(encoding="utf-8"))
    assert source["commit"] == COMMIT and not source["fetch_errors"]
    manifest = {item["path"]: item for item in source["files"]}
    evidence_path = PROJECT / "evidence.json"
    saved = json.loads(evidence_path.read_text(encoding="utf-8")) if evidence_path.exists() else {}
    capabilities, evidence = [], {}
    scene_ids = {item["id"] for item in module.SCENES}
    for group, text in module.ROWS.items():
        for line in text.strip().splitlines():
            fields = line.split("|")
            assert len(fields) == 9, (group, fields)
            title, effect, mechanism, status, boundary, path, needle, scenes, params = fields
            assert path in manifest, f"Source absent from manifest: {path}"
            item_id = f"{group}-{sum(item['category'] == group for item in capabilities) + 1:02d}"
            cached = CACHE / path
            if cached.exists():
                content = cached.read_bytes()
                assert hashlib.sha256(content).hexdigest() == manifest[path]["sha256"], path
                lines = content.decode("utf-8").splitlines()
                positions = [i + 1 for i, value in enumerate(lines) if needle in value]
                assert positions, f"Anchor missing: {path}: {needle}"
                line_number = positions[0]
            else:
                old = saved[item_id]
                assert old["path"] == path and old["needle"] == needle
                assert old["sha256"] == manifest[path]["sha256"]
                line_number = old["line"]
            assert 0 < line_number <= manifest[path]["lines"]
            evidence[item_id] = {"path": path, "needle": needle, "line": line_number, "sha256": manifest[path]["sha256"]}
            scene_list = scenes.split(",") if scenes else []
            assert all(scene == "all" or scene in scene_ids for scene in scene_list), item_id
            capabilities.append({"id": item_id, "category": group, "title": title, "effect": effect, "mechanism": mechanism, "availability": status, "boundary": boundary, "scenes": scene_list, "parameters": params, "source": {"path": path, "line": line_number, "url": UPSTREAM + path + f"#L{line_number}"}, "verification": "source_review"})

    parameter_file = PROJECT / "parameters.json"
    if CACHE.exists() and all((CACHE / file).exists() for file in manifest):
        discovered = {}
        pattern = re.compile(r"\b(?:url|params|query|search)\.(get|num|flag)\(\s*['\"]([^'\"]+)['\"]")
        for path in sorted(manifest):
            if not path.startswith("src/"):
                continue
            for number, line in enumerate((CACHE / path).read_text(encoding="utf-8").splitlines(), 1):
                active_pattern = re.compile(r"\.(get|num|flag)\(\s*['\"]([^'\"]+)['\"]") if "URLSearchParams" in line else pattern
                for match in active_pattern.finditer(line):
                    name = match[2]
                    found = {"path": path, "line": number, "accessor": match[1], "url": UPSTREAM + path + f"#L{number}"}
                    discovered.setdefault(name, []).append(found)
        parameters = [{"name": key, "occurrences": value} for key, value in sorted(discovered.items())]
    else:
        parameters = json.loads(parameter_file.read_text(encoding="utf-8"))
    parameter_names = {item["name"] for item in parameters}
    for item in capabilities:
        for pair in item["parameters"].split("&"):
            if pair:
                assert pair.split("=")[0] in parameter_names, f"Parameter not found: {pair} ({item['id']})"

    counts = Counter(item["category"] for item in capabilities)
    categories = [{"id": key, "name": name, "description": description, "count": counts[key]} for key, name, description in module.CATEGORIES]
    scenes = [{**item, "url": UPSTREAM + item["source"]} for item in module.SCENES]
    data = {"meta": {"name": "WebGPU Render Pipeline", "commit": COMMIT, "reviewDate": source["review_date"], "sourceFiles": source["text_file_count"], "capabilityCount": len(capabilities), "sceneCount": len(scenes), "parameterCount": len(parameters), "verification": "源码核实；上游运行未实测；本地静态展示另行验证。"}, "categories": categories, "capabilities": capabilities, "scenes": scenes, "pipeline": module.PIPELINE, "limitations": module.LIMITATIONS, "parameters": parameters}

    md = ["# 能力清单", "", f"本清单把固定版本分解为 **{len(capabilities)} 项研究条目、{len(categories)} 类能力**。计数是本研究的信息组织方式，不是上游官方功能数量。", "", "每项均核对源码存在与接入条件；现已运行 Cornell Box、完整村庄、海滩与森林的指定主管线配置，仍不能据此声明全部能力、画质或性能已验收。`主管线` 表示主路径有接入；`按场景` 表示依赖场景配置；`可选` 需启用；`实验室` 为独立实现；`历史路径` 与 `集成待补` 不应作为默认交付能力。", "", "[交互检索](web/index.html#capabilities) · [场景地图](SCENES.md) · [技术原理](ARCHITECTURE.md) · [全部参数定位](PARAMETERS.md)"]
    for category in categories:
        md += ["", f"## {category['name']}（{category['count']} 项）", "", category["description"], ""]
        for item in capabilities:
            if item["category"] != category["id"]:
                continue
            md += [f"### {item['id']} · {item['title']}", "", f"- **画面或使用效果**：{item['effect']}。", f"- **原理**：{item['mechanism']}。", f"- **接入状态**：{item['availability']}；**边界**：{item['boundary']}。", f"- **适用入口**：{', '.join(item['scenes'])}。", f"- **源码证据**：[{item['source']['path']}:{item['source']['line']}]({item['source']['url']})。"]
            if item["parameters"]:
                md += [f"- **参数示例**：`?{item['parameters']}`（需接在正确场景路径后，不会在本研究页执行）。"]
            md += [""]
    scene_md = ["# 场景与观察路线", "", f"共 {len(scenes)} 个研究入口：主场景、测试夹具、独立实验室及阅读页分开登记。这里给出上游服务启动后的相对路由，不是已部署演示链接。", "", "本地图来自固定版本场景入口及 `src/app/home/catalog.ts`。相机名以各场景实际支持为准，不把共享的 `cam` 参数当作所有场景都支持相同机位。", ""]
    for scene in scenes:
        scene_md += [f"## {scene['title']} · {scene['kind']}", "", f"- 入口：`{scene['route']}`。", f"- 看什么：{scene['focus']}。", f"- 相机：{', '.join(scene['cameras']) or '使用默认相机或实验室内置控制'}。", f"- 建议观察：{scene['checks']}", f"- 范围：{scene['note']}", f"- [固定版本源码]({scene['url']})。", ""]
    param_md = ["# URL 参数源码索引", "", f"共发现 **{len(parameters)} 个不同的参数名**。以源码中的 `url.get/num/flag` 与 `params.get` 等字面量访问自动提取，给出定位；**它不是逐项验证过的稳定 API，也不包含所有动态构造的键名**。", "", "同名参数可能分属不同入口。默认值、取值范围、单位和可达性必须看对应上下文；实验室参数不能无条件用于主场景。本研究页支持查找，完整数据在 [parameters.json](parameters.json)。", "", "| 参数名 | 首个源码位置 | 源码出现次数 |", "| --- | --- | --- |"]
    for item in parameters:
        first = item["occurrences"][0]
        param_md.append(f"| `{item['name']}` | [{first['path']}:{first['line']}]({first['url']}) | {len(item['occurrences'])} |")

    outputs = {"evidence.json": encoded(evidence), "capabilities.json": encoded(capabilities), "scenes.json": encoded(scenes), "parameters.json": encoded(parameters), "CAPABILITIES.md": "\n".join(md).rstrip() + "\n", "SCENES.md": "\n".join(scene_md).rstrip() + "\n", "PARAMETERS.md": "\n".join(param_md).rstrip() + "\n", "web/data.js": "window.RESEARCH = " + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + ";\n"}
    for relative, content in outputs.items():
        target = PROJECT / relative
        if check:
            assert target.is_file() and target.read_text(encoding="utf-8") == content, f"Generated output differs: {relative}"
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8", newline="\n")
    return {"capabilities": len(capabilities), "categories": len(categories), "scenes": len(scenes), "parameters": len(parameters), "source_files": source["text_file_count"], "mode": "check" if check else "write"}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    print(json.dumps(generate(args.check), ensure_ascii=False))
