"""Bundle four pinned original scenes and their Chinese control bridge."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shutil

from setup_runtime import PROJECT, RUNTIME, THREE, FIBER, run


def build():
    prepared = json.loads((RUNTIME / ".atlas/prepared.json").read_text(encoding="utf-8"))
    for patch in prepared.get("source_patches", []):
        assert hashlib.sha256((RUNTIME / patch["path"]).read_bytes()).hexdigest() == patch["patched_sha256"], f"Runtime patch differs: {patch['path']}"
    for name in ("main.ts", "vite.runtime.config.mjs"):
        shutil.copyfile(PROJECT / "runtime" / name, RUNTIME / ".atlas" / name)
    shutil.copyfile(PROJECT / "runtime/frame.html", RUNTIME / "atlas.html")
    output = (PROJECT / "web/live").resolve()
    # Vite may clear only this dedicated, ignored build output, never another directory.
    assert output == PROJECT.resolve() / "web/live" and output.is_relative_to(PROJECT.resolve())
    run(["node", str(RUNTIME / "node_modules/vite/bin/vite.js"), "build", "--config", ".atlas/vite.runtime.config.mjs"], cwd=RUNTIME, env={**os.environ, "ATLAS_OUTPUT": str(output)})
    (output / "atlas.html").rename(output / "index.html")
    for item in prepared["assets"]:
        target = output / Path(item["path"]).relative_to("public")
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(RUNTIME / item["path"], target)
    licenses = output / "licenses"
    licenses.mkdir(exist_ok=True)
    for checkout, name in ((THREE, "three-MIT.txt"), (FIBER, "react-three-fiber-MIT.txt")):
        shutil.copyfile(checkout / "LICENSE", licenses / name)
    notices = ["Pinned upstream WebGPU renderer, ca576b601bf84527102f1768372aa8cd96a3c55a.\nNo repository-level LICENSE was found in that upstream snapshot.\nhttps://github.com/vibegameengine/web-starter-kit-webgpu-pipline\n", "The scene, render-pipeline, GI and shading code are the upstream implementation.\nThe atlas adds a UI bridge, focused build entry, and a covered-texel guard in the chart fallback sampler (see build-info.json source_patches).\n"]
    lock = json.loads((PROJECT / "runtime/package-lock.json").read_text())
    for relative in sorted(lock["packages"]):
        if not relative.startswith("node_modules/"):
            continue
        root = RUNTIME / relative
        if not root.is_dir():
            continue
        files = [f for f in root.iterdir() if f.is_file() and f.name.upper().startswith(("LICENSE", "LICENCE", "NOTICE", "COPYING"))]
        for file in files:
            notices.append(f"\n{'=' * 72}\n{relative} / {file.name}\n{file.read_text(encoding='utf-8', errors='replace')}\n")
    (licenses / "npm-NOTICES.txt").write_text("\n".join(notices), encoding="utf-8")
    # Keep original material authorship information beside the bundled village textures.
    shutil.copyfile(RUNTIME / 'src/entities/village/assets/README.md', licenses / 'village-texture-sources.md')
    record = {
        **prepared,
        "entry": "original Cornell Box + complete midsee-village + beach + forest + render-pipeline",
        "source_code_changes": "one coverage guard in the lightmap fallback sampler; exact original/patched hashes in source_patches; runtime overlay adds boot, scene switching and controls",
        "profile": {
            "common": "64 maximum lightmap bake passes (minimum 32), 16 rays, FXAA, fixed exposure 1, no grain/fog/reflection pass",
            "cornell": "4s budget, sample 0.25m, lightmap 0.08m/texel, probe spacing 3m, 64 probe passes, camera radius 5–24",
            "midsee-village": "2048 lightmap page side, 6s budget, sample 0.7m, lightmap 0.12m/texel, probe spacing 8m, 32 probe passes, camera radius 8–120, original worker water simulation",
            "beach": "1024 lightmap page side, 6s budget, sample 0.5m, lightmap 0.12m/texel, probe spacing 5m, 32 probe passes, camera radius 0.8–100, original worker water and foliage updates; van=0 because the pinned tree lacks its GLB",
            "forest": "2048 lightmap page side, 6s budget, sample 0.7m, lightmap 0.12m/texel, probe spacing 12m, 32 probe passes, camera radius 0.8–160, original near/distant vegetation and opaque animated stream material",
        },
        "files": [],
    }
    for file in sorted(output.rglob("*")):
        if file.is_file():
            record["files"].append({"path": file.relative_to(output).as_posix(), "sha256": hashlib.sha256(file.read_bytes()).hexdigest(), "bytes": file.stat().st_size})
    (output / "build-info.json").write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (PROJECT / "runtime/SOURCES.json").write_text(json.dumps({key: value for key, value in record.items() if key != "files"}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(output), "files": len(record["files"]) + 1, "asset_bytes_verified": True}))


if __name__ == "__main__":
    build()
