"""Deterministically package the research page with only Python's standard library."""
from hashlib import sha256
from io import BytesIO
import argparse
import base64
import json
from pathlib import Path
import re
import zipfile

ROOT = Path(__file__).resolve().parents[1]
ATTRIBUTION = """Original pet files: heytea-style contributors, CC BY 4.0.
https://creativecommons.org/licenses/by/4.0/
Source: https://github.com/Hchen1218/heytea-style
Commit: d5125372adcc945c2314cfb649c50407379a18ab
Original files are unchanged. This attribution file is added by the research page.
Import this ZIP into the compatible Doodle Desktop Pet runtime (3.1.0 or newer).
This pack does not contain or install the Electron runtime.
No affiliation with or endorsement by HEYTEA.
"""


def example_zip():
    output = BytesIO()
    files = {path.relative_to(ROOT / "assets/upstream/pet-v3").as_posix(): path.read_bytes()
             for path in (ROOT / "assets/upstream/pet-v3").rglob("*") if path.is_file()}
    files["ATTRIBUTION.txt"] = ATTRIBUTION.encode()
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_STORED) as archive:
        for name, data in sorted(files.items()):
            info = zipfile.ZipInfo("pink-green-flavor-monster-v3/" + name, (2026, 9, 4, 0, 0, 0))
            info.create_system = 3  # Stable Unix ZIP metadata on every build host.
            info.compress_type = zipfile.ZIP_STORED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, data)
    return output.getvalue()


def data_url(name, data):
    # Fixed MIME names keep standalone bytes identical on Windows and Linux.
    mime = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
            ".webp": "image/webp", ".gif": "image/gif", ".json": "application/json",
            ".md": "text/markdown;charset=utf-8", ".txt": "text/plain;charset=utf-8",
            ".zip": "application/zip", ".js": "text/javascript;charset=utf-8"}.get(Path(name).suffix.lower(), "application/octet-stream")
    return f"data:{mime};base64," + base64.b64encode(data).decode("ascii")


def standalone(files):
    html = (ROOT / "web/index.html").read_text(encoding="utf-8")
    html = html.replace('<link rel="stylesheet" href="style.css">', "<style>" + (ROOT / "web/style.css").read_text(encoding="utf-8") + "</style>")
    html = re.sub(r'  <script src="(?:assets/runtime/episode-player.js|app.js)" defer></script>\n', "", html)
    html = re.sub(r'<a\b[^>]*href="standalone.html"[^>]*>[^<]*</a>', '<span class="small-label">离线网页 · 已内嵌素材</span>', html)
    for name, data in files.items():
        if name.startswith("assets/") and Path(name).suffix.lower() in {".png", ".jpg", ".jpeg", ".gif", ".webp"}:
            html = html.replace(f'src="{name}"', f'src="{data_url(name, data)}"')

    def download_anchor(match):
        anchor = match.group(0)
        href = re.search(r'href="([^"]+)"', anchor)
        if not href:
            return anchor
        name = href.group(1)
        if name == "standalone.html":
            return anchor.replace('href="standalone.html"', 'href="#sources"').replace(" download", "")
        if name not in files:
            return anchor
        explicit_download = re.search(r'\sdownload="([^"]+)"', anchor)
        filename = explicit_download.group(1) if explicit_download else Path(name).name
        anchor = anchor.replace(f'href="{name}"', f'href="{data_url(name, files[name])}"').replace(' target="_blank"', "")
        anchor = re.sub(r'\sdownload(?:="[^"]*")?', "", anchor)
        anchor = anchor[:-1] + f' download="{filename}">'
        return anchor

    html = re.sub(r"<a\b[^>]*>", download_anchor, html)
    images = {name.removeprefix("assets/upstream/"): data_url(name, data)
              for name, data in files.items() if name.startswith("assets/upstream/") and Path(name).suffix != ".json"}
    payload = {"images": images, "manifest": json.loads((ROOT / "assets/upstream/pet-v3/pet.json").read_text(encoding="utf-8"))}
    inline = "window.__HEYTEA_RESEARCH_OFFLINE__=" + json.dumps(payload, ensure_ascii=True, sort_keys=True, separators=(",", ":")) + ";\n"
    inline += files["assets/runtime/episode-player.js"].decode("utf-8") + "\n"
    inline += (ROOT / "web/app.js").read_text(encoding="utf-8")
    html = html.replace("</body>", "<script>" + inline.replace("</script", "<\\/script") + "</script></body>")
    return html.encode("utf-8")


def expected_files():
    source = json.loads((ROOT / "SOURCE.json").read_text(encoding="utf-8"))
    for record in source["files"]:
        data = (ROOT / record["local_path"]).read_bytes()
        if sha256(data).hexdigest() != record["sha256"]:
            raise ValueError(f"Source differs from pinned snapshot: {record['local_path']}")
    files = {"assets/" + path.relative_to(ROOT / "assets").as_posix(): path.read_bytes()
             for path in sorted((ROOT / "assets/upstream").rglob("*")) if path.is_file()}
    for name in ("overview.png", "capability-overview.png"):
        if (ROOT / "assets" / name).is_file():
            files["assets/" + name] = (ROOT / "assets" / name).read_bytes()
    files["assets/runtime/episode-player.js"] = (ROOT / "upstream/assets/desktop-pet-runtime/src/core/episode-player.js").read_bytes()
    for source_name, destination in (("notes.md", "research-notes.md"), ("SOURCE.json", "SOURCE.json"),
                                     ("NOTICE.md", "NOTICE.md"), ("LICENSE.upstream.txt", "LICENSE.upstream.txt"),
                                     ("OVERVIEW.md", "overview-guide.md"), ("image-generation.json", "image-generation.json")):
        files["downloads/" + destination] = (ROOT / source_name).read_bytes()
    files["downloads/example-pet-v3.zip"] = example_zip()
    files["standalone.html"] = standalone(files)
    return files


def package(check=False):
    files = expected_files()
    for name, data in files.items():
        target = ROOT / "web" / name
        if check:
            if not target.is_file() or target.read_bytes() != data:
                raise ValueError(f"Missing or outdated published file: {name}")
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
    print(f"{'Verified' if check else 'Packaged'} {len(files)} local files; all source hashes match")
    return files


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    package(args.check)
