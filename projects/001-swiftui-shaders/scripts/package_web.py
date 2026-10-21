"""Build a self-contained offline HTML and optional GitHub Pages directory."""
from __future__ import annotations
import argparse
import base64
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / "web"


def standalone() -> str:
    html = (WEB / "index.html").read_text(encoding="utf-8")
    css = (WEB / "style.css").read_text(encoding="utf-8")
    renderer = (WEB / "renderer.js").read_text(encoding="utf-8").replace("export class", "class")
    app = (WEB / "app.js").read_text(encoding="utf-8").replace("import { ShaderRenderer } from './renderer.js';", "")
    data = (WEB / "shaders.json").read_text(encoding="utf-8")
    def asset_uri(path: Path) -> str:
        mime = 'image/svg+xml' if path.suffix == '.svg' else 'image/png'
        return 'data:' + mime + ';base64,' + base64.b64encode(path.read_bytes()).decode('ascii')
    visual_assets = {path.stem: asset_uri(path) for path in sorted((WEB / 'assets/effects').glob('*.png')) if path.stem != 'Original'}
    visual_assets.update(Overview=asset_uri(WEB / 'assets/understanding-overview.png'), Atlas=asset_uri(WEB / 'assets/effect-atlas.png'))
    html = html.replace('src="./assets/understanding-overview.svg"', 'src="' + asset_uri(WEB / 'assets/understanding-overview.svg') + '"')
    html = html.replace('src="./assets/effect-atlas.png"', 'src="' + visual_assets['Atlas'] + '"')
    html = html.replace('<link rel="stylesheet" href="./style.css">', f"<style>{css}</style>")
    script = f"globalThis.SHADER_MANIFEST = {data};\nglobalThis.SHADER_VISUAL_ASSETS = {json.dumps(visual_assets)};\n{renderer}\n{app}"
    html = html.replace('<script type="module" src="./app.js"></script>', "<script type=\"module\">" + script.replace("</script", "<\\/script") + "</script>")
    for name in ("cover", "flower", "type"):
        raw = (WEB / f"assets/sample-{name}.svg").read_bytes()
        uri = "data:image/svg+xml;base64," + base64.b64encode(raw).decode("ascii")
        # Handle both the initial material and material switching template.
        html = html.replace(f"'./assets/sample-{name}.svg'", repr(uri))
        html = html.replace("`./assets/sample-${key}.svg`", "({" + ",".join(
            f"'{n}':'data:image/svg+xml;base64,{base64.b64encode((WEB / f'assets/sample-{n}.svg').read_bytes()).decode('ascii')}'"
            for n in ("cover", "flower", "type")) + "})[key]")
    favicon = base64.b64encode((WEB / "assets/favicon.svg").read_bytes()).decode("ascii")
    return html.replace('./assets/favicon.svg', 'data:image/svg+xml;base64,' + favicon)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="copy deployable web files to an empty output directory")
    args = parser.parse_args()
    (WEB / "standalone.html").write_text(standalone(), encoding="utf-8", newline="\n")
    if args.output:
        target = args.output.resolve()
        if target.exists() and any(target.iterdir()):
            parser.error("Output directory must be empty; no existing files will be removed.")
        shutil.copytree(WEB, target, dirs_exist_ok=True)
        print(f"Static site copied to {target}")
    print("Generated web/standalone.html (all shaders, code, styles and test artwork embedded).")
