"""Extract only dr-aria's art, palette and renderer from a pinned local checkout."""
import argparse
import hashlib
import json
import subprocess
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("checkout", type=Path)
args = parser.parse_args()
expected = "ff26c94cf1d6879ad98838df9c50104d06419eb6"
actual = subprocess.check_output(["git", "-C", str(args.checkout), "rev-parse", "HEAD"], text=True).strip()
if actual != expected:
    parser.error(f"Expected upstream {expected}, got {actual}")
project = Path(__file__).resolve().parents[1]
web = project / "web"
web.mkdir(exist_ok=True)
source = (args.checkout / "build/page.html").read_text(encoding="utf-8")
art = (args.checkout / "build/art.json").read_text(encoding="utf-8")
constants = source.split("const AsciiTherapist = (() => {\n", 1)[1].split("  class Therapist", 1)[0]
renderer = source.split("    /* ---------------- marker substitution ---------------- */", 1)[1].split("    setState(s)", 1)[0]
palette = source.split("  /* ---- palette ---- */", 1)[1].split("  .nameplate", 1)[0]
header = "// Derived from MPMyburgh/dr-aria @ ff26c94; MIT, (c) 2026 Michael Myburgh.\n// See LICENSE.dr-aria.txt and ../NOTICE.md.\n"
(web / "upstream-art.js").write_text(header + "export const ART = " + art.strip() + ";\n", encoding="utf-8")
(web / "upstream-renderer.js").write_text(header + "import { ART } from './upstream-art.js';\n" + constants + "\nexport class AriaRenderer {\n" + renderer + "}\nexport { MOODS };\nexport const PALETTE = " + json.dumps(palette) + ";\n", encoding="utf-8")
(web / "LICENSE.dr-aria.txt").write_bytes((args.checkout / "LICENSE").read_bytes())
(project / "assets/upstream-aria.png").write_bytes((args.checkout / "docs/aria.png").read_bytes())
files = ["build/page.html", "build/art.json", "LICENSE", "docs/aria.png"]
(project / "SOURCE.json").write_text(json.dumps({
    "repository": "https://github.com/MPMyburgh/dr-aria",
    "commit": "ff26c94cf1d6879ad98838df9c50104d06419eb6",
    "license": "MIT", "retrieved": "2026-10-21",
    "files": {name: hashlib.sha256((args.checkout / name).read_bytes()).hexdigest() for name in files},
}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("Extracted art, renderer, palette, license and screenshot.")
