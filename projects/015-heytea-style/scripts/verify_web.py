"""Check self-contained links, attribution, pinned copies, and downloadable pack."""
from hashlib import sha256
from html.parser import HTMLParser
import json
from pathlib import Path
from urllib.parse import unquote, urlsplit
import zipfile
from package_web import package

ROOT = Path(__file__).resolve().parents[1]


class Inventory(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids, self.links = set(), []
        self.images = 0

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "id" in attrs:
            assert attrs["id"] not in self.ids, f"Duplicate id: {attrs['id']}"
            self.ids.add(attrs["id"])
        if tag == "img":
            assert attrs.get("alt"), f"Missing image alternative text: {attrs}"
            self.images += 1
        for name in ("href", "src"):
            if attrs.get(name): self.links.append(attrs[name])


def main():
    files = package(check=True)
    html = (ROOT / "web/index.html").read_text(encoding="utf-8")
    inventory = Inventory()
    inventory.feed(html)
    checked = 0
    for link in inventory.links:
        if link == "#": continue
        if link.startswith("#"):
            assert link[1:] in inventory.ids, f"Broken section anchor: {link}"
        elif not urlsplit(link).scheme:
            target = ROOT / "web" / unquote(urlsplit(link).path)
            assert target.is_file(), f"Broken local resource: {link}"
            checked += 1
    assert {"overview", "effects", "pet-lab", "principles", "value", "boundaries", "sources"} <= inventory.ids
    generation = json.loads((ROOT / "image-generation.json").read_text(encoding="utf-8"))
    assert sha256((ROOT / generation["image"]).read_bytes()).hexdigest() == generation["sha256"]
    with zipfile.ZipFile(ROOT / "web/downloads/example-pet-v3.zip") as archive:
        for path in (ROOT / "assets/upstream/pet-v3").rglob("*"):
            if path.is_file():
                name = "pink-green-flavor-monster-v3/" + path.relative_to(ROOT / "assets/upstream/pet-v3").as_posix()
                assert archive.read(name) == path.read_bytes(), f"ZIP changed original file: {name}"
        assert "heytea-style contributors" in archive.read("pink-green-flavor-monster-v3/ATTRIBUTION.txt").decode()
    result = {"date": "2026-10-22", "status": "passed", "source_commit": "d5125372adcc945c2314cfb649c50407379a18ab",
              "packaged_files": len(files), "html_local_references": checked, "html_images_with_alt": inventory.images,
              "checks": ["all pinned source SHA-256", "all packaged bytes", "section anchors", "local resource links",
                         "original pack bytes and attribution", "upstream player and MIT license included", "generated overview hash and provenance"],
              "pack_sha256": sha256(files["downloads/example-pet-v3.zip"]).hexdigest(),
              "limits": ["AI-generated overview is a research illustration; upstream creative workflows not run", "No Electron runtime installation or execution", "No public deployment"]}
    (ROOT / "verification.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
