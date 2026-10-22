"""Check resources, pinned source integrity, study ZIP and reproduction evidence."""
from hashlib import sha256
from html.parser import HTMLParser
import json
from pathlib import Path
import struct
from urllib.parse import unquote, urlsplit
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / "web"


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.references, self.ids, self.lines, self.memory_lines = [], [], [], []
        self.current_line = None
        self.current_kind = None
        self.inside_number = False

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "id" in attrs:
            self.ids.append(attrs["id"])
        self.references.extend(attrs[key] for key in ("href", "src") if key in attrs)
        if tag == "span" and "line" in attrs.get("class", "").split():
            self.current_line = ""
            self.current_kind = "race"
        if tag == "span" and "memory-code-line" in attrs.get("class", "").split():
            self.current_line = ""
            self.current_kind = "memory"
        if tag == "i" and self.current_line is not None:
            self.inside_number = True

    def handle_endtag(self, tag):
        if tag == "i":
            self.inside_number = False
        if tag == "span" and self.current_line is not None:
            (self.memory_lines if self.current_kind == "memory" else self.lines).append(self.current_line.strip())
            self.current_line = None

    def handle_data(self, data):
        if self.current_line is not None and not self.inside_number:
            self.current_line += data


def main():
    page = Page()
    page.feed((WEB / "index.html").read_text(encoding="utf-8"))
    assert len(page.ids) == len(set(page.ids)), "Duplicate HTML ID"
    checked = 0
    for reference in page.references:
        url = urlsplit(reference)
        if url.scheme or url.netloc:
            continue
        if url.path:
            local = (WEB / unquote(url.path)).resolve()
            assert local.is_relative_to(WEB.resolve()), f"Resource escapes web: {reference}"
            assert local.is_file(), f"Missing local resource: {reference}"
            checked += 1
        if url.fragment and not url.path:
            assert url.fragment in page.ids, f"Missing fragment: {reference}"
    manifest = json.loads((ROOT / "SOURCE.json").read_text(encoding="utf-8"))
    expected_revision = "ffe2d10042041dcc23325f013e8b7e607e069952"
    assert manifest["revision"] == expected_revision
    assert len(manifest["files"]) == 18
    source_js = (WEB / "source-data.js").read_text(encoding="utf-8")
    documents = json.loads(source_js.removeprefix("window.UPSTREAM = ").removesuffix(";\n"))
    assert len(documents) == len(manifest["files"])
    with ZipFile(WEB / "assets/super-hermes-study-kit.zip") as archive:
        for entry in manifest["files"]:
            content = (ROOT / entry["local_path"]).read_bytes()
            assert sha256(content).hexdigest() == entry["sha256"], entry["local_path"]
            assert len(content) == entry["bytes"]
            assert archive.read("super-hermes/" + entry["upstream_path"]) == content
            assert documents[entry["upstream_path"]] == content.decode("utf-8-sig").replace("\r\n", "\n")
        assert "super-hermes/LICENSE" in archive.namelist()
    actual = documents["examples/circuit_breaker.py"].splitlines()[42:51]
    assert page.lines == [line.strip() for line in actual], "Displayed snippet differs from upstream"
    race = json.loads((WEB / "assets/race-reproduction.json").read_text(encoding="utf-8"))
    assert race["upstream_revision"] == expected_revision
    assert race["race_reproduced"] is True
    assert race["state_after_new_failure"] == "open"
    assert race["stale_reader_observed_state"] == "half_open"
    assert race["new_failure_age_seconds"] < race["configured_cooldown_seconds"]
    memory = json.loads((WEB / "assets/memory-reproduction.json").read_text(encoding="utf-8"))
    memory_js = (WEB / "memory-data.js").read_text(encoding="utf-8")
    assert json.loads(memory_js.removeprefix("window.MEMORY_CASE = ").removesuffix(";\n")) == memory
    fixture = (WEB / memory["fixture"]).read_bytes()
    assert sha256(fixture).hexdigest() == memory["fixture_sha256"]
    assert page.memory_lines == [line.strip() for line in fixture.decode("utf-8").splitlines()[17:21]]
    assert memory["model_invoked"] is False
    assert [case["mode"] for case in memory["cases"]] == ["unbounded", "bounded"]
    for case in memory["cases"]:
        assert [sample["requests"] for sample in case["samples"]] == [0, 200, 400, 600, 800]
        for sample in case["samples"]:
            assert sample["entries"] == (sample["requests"] if case["mode"] == "unbounded" else min(32, sample["requests"]))
            expected = sample["entries"] * case["payload_bytes"]
            assert abs(sample["traced_growth_bytes"] - expected) < max(4096, expected * .02)
        assert case["payload_growth_bytes_after_clear"] == 0
        assert case["allocation_growth"][0]["line"] == case["payload_allocation_line"] == 11
    repeated = memory["controls"]["repeated_key"]
    assert repeated["mode"] == "repeated"
    assert repeated["capacity"] is None
    assert repeated["payload_growth_bytes_after_clear"] == 0
    assert [sample["entries"] for sample in repeated["samples"]] == [0, 1, 1, 1, 1]
    assert repeated["samples"][-1]["traced_growth_bytes"] < 2 * repeated["payload_bytes"]
    rulebook = json.loads((WEB / "assets/super-hermes-rules.json").read_text(encoding="utf-8"))
    rulebook_js = (WEB / "rulebook-data.js").read_text(encoding="utf-8")
    assert json.loads(rulebook_js.removeprefix("window.RULEBOOK = ").removesuffix(";\n")) == rulebook
    assert rulebook["revision"] == expected_revision
    rule_ids = [rule["id"] for rule in rulebook["rules"]]
    assert len(rule_ids) == len(set(rule_ids)) == 69
    expected_core = {f"skills/prism-{key}/SKILL.md" for key in ("scan", "full", "3way", "discover", "reflect")}
    expected_core.update(f"skills/prism-scan/references/{key}.md" for key in
                         ("error_resilience", "l12", "optimize", "identity", "deep_scan", "claim", "simulation"))
    assert {source["path"] for source in rulebook["sources"] if source["key"] != "readme"} == expected_core
    exported_rules = (WEB / "assets/super-hermes-rules.txt").read_text(encoding="utf-8")
    mapped = {}
    for rule in rulebook["rules"]:
        assert rule["group"] in rulebook["groups"]
        for field in ("id", "title", "action", "how", "output", "example", "kind"):
            assert isinstance(rule[field], str) and rule[field].strip()
            assert rule[field] in exported_rules, (rule["id"], field)
        assert rule["sources"]
        for evidence in rule["sources"]:
            original = documents[evidence["path"]]
            assert evidence["needle"] in original
            assert original[:original.index(evidence["needle"])].count("\n") + 1 == evidence["line"]
            mapped.setdefault(evidence["path"], set()).add(rule["id"])
    for source in rulebook["sources"]:
        assert source["ruleIds"]
        assert set(source["ruleIds"]) == mapped[source["path"]]
        assert sha256((WEB / "assets/upstream" / source["path"]).read_bytes()).hexdigest() == source["sha256"]
    for record_name in ("overview-image.json", "understanding-image.json", "seven-step-image.json"):
        overview = json.loads((ROOT / record_name).read_text(encoding="utf-8"))
        for image_path in (overview["image"], overview["web_image"]):
            image = (ROOT / image_path).read_bytes()
            assert image.startswith(b"\x89PNG\r\n\x1a\n"), "Invalid overview PNG"
            assert len(image) == overview["bytes"]
            assert sha256(image).hexdigest() == overview["sha256"]
            assert struct.unpack(">II", image[16:24]) == (overview["width"], overview["height"])
        assert (ROOT / overview["prompt_file"]).read_bytes() == (WEB / "assets" / Path(overview["prompt_file"]).name).read_bytes()
    print(f"PASS: {checked} local references, {len(page.ids)} unique IDs, 18 source hashes, ZIP, race/memory evidence, 69 rules, all 3 overview PNGs and prompts.")


if __name__ == "__main__":
    main()
