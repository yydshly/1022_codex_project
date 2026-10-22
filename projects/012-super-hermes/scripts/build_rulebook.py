"""Build an offline rulebook with exact evidence locations from pinned sources."""
from hashlib import sha256
import json
from pathlib import Path
from rulebook_content import GROUPS, RULES, SOURCES

ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / "web"
REVISION = "ffe2d10042041dcc23325f013e8b7e607e069952"


def build():
    manifest = json.loads((ROOT / "SOURCE.json").read_text(encoding="utf-8"))
    hashes = {entry["upstream_path"]: entry["sha256"] for entry in manifest["files"]}
    assert len({rule["id"] for rule in RULES}) == len(RULES)
    sources = {}
    for key, path in SOURCES.items():
        raw = (WEB / "assets/upstream" / path).read_bytes()
        assert sha256(raw).hexdigest() == hashes[path], path
        sources[key] = dict(key=key, path=path, sha256=hashes[path], ruleIds=[])
    for rule in RULES:
        for evidence in rule["sources"]:
            source = sources[evidence["key"]]
            text = (WEB / "assets/upstream" / source["path"]).read_text(encoding="utf-8-sig")
            assert evidence["needle"] in text, (rule["id"], evidence)
            position = text.index(evidence["needle"])
            evidence.update(path=source["path"], line=text[:position].count("\n") + 1)
            if rule["id"] not in source["ruleIds"]:
                source["ruleIds"].append(rule["id"])
    assert all(source["ruleIds"] for key, source in sources.items() if key != "readme")
    report = dict(revision=REVISION, provenance="Research summaries and examples, not an upstream rule count or model transcript.",
                  groups=GROUPS, sources=list(sources.values()), rules=RULES,
                  coverage="Human-reviewed mapping of all 5 skill bodies and 7 reference lenses; metadata and runtime notes are separately identified.")
    body = json.dumps(report, ensure_ascii=False, indent=2)
    (WEB / "rulebook-data.js").write_text("window.RULEBOOK = " + body + ";\n", encoding="utf-8")
    (WEB / "assets/super-hermes-rules.json").write_text(body + "\n", encoding="utf-8")
    lines = ["Super Hermes 通用步骤与规则全表", f"上游版本：{REVISION}",
             f"范围：5 个 Skill + 7 份模板；研究者归纳 {len(RULES)} 条，不是上游自报数量。",
             "每条含原文动作概括、指导作用、产物、教学示例与来源。",
             "这些主要是提示词约定，不是程序硬限制；示例未运行 Hermes。", ""]
    for group, label in GROUPS.items():
        lines.extend([label, "=" * 36])
        for rule in RULES:
            if rule["group"] != group:
                continue
            lines.extend([f'{rule["id"]} · {rule["title"]}', f'类型：{rule["kind"]}',
                          f'原文动作概括：{rule["action"]}', f'如何指导 AI：{rule["how"]}',
                          f'应留下的产物：{rule["output"]}', f'教学示例：{rule["example"]}'])
            if rule["caveat"]:
                lines.append("使用边界（研究解读）：" + rule["caveat"])
            for source in rule["sources"]:
                lines.append(f'来源：https://github.com/Cranot/super-hermes/blob/{REVISION}/{source["path"]}#L{source["line"]}')
            lines.append("")
    (WEB / "assets/super-hermes-rules.txt").write_text("\n".join(lines), encoding="utf-8")
    print(f'Built {len(RULES)} rules; {len(sources) - 1} core documents + README runtime evidence.')
    for group, label in GROUPS.items():
        print(f'{group}: {sum(rule["group"] == group for rule in RULES)}')


if __name__ == "__main__":
    build()
