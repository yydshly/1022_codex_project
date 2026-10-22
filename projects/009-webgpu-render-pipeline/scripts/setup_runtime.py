"""Prepare isolated pinned upstream/forks and install the recorded npm dependency lock."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import time
from urllib.request import Request, urlopen

PROJECT = Path(__file__).resolve().parents[1]
ROOT = PROJECT.parents[1]
CACHE = ROOT / "_upstream"
RUNTIME = CACHE / "webgpu-runtime-ca576b6"
THREE = CACHE / "webgpu-three-r182"
FIBER = CACHE / "webgpu-fiber"
PINS = {
    "upstream": {"url": "https://github.com/vibegameengine/web-starter-kit-webgpu-pipline.git", "commit": "ca576b601bf84527102f1768372aa8cd96a3c55a"},
    "three": {"url": "https://github.com/vibegameengine/three.js.git", "commit": "7d3343686e52f532e97c67440f55b1adb7aba28c"},
    "fiber": {"url": "https://github.com/vibegameengine/react-three-fiber.git", "commit": "b297b512181dfddbb287f75374223a56ccf1757b"},
}
ASSETS = [
    "public/textures/LDR_RGBA_0.png",
    "public/exr/pizzo_pernice_puresky_2k.hdr",
    "public/textures/rock/Rock030_2K-JPG_Color.jpg",
    "public/textures/rock/Rock030_2K-JPG_NormalGL.jpg",
    "public/textures/rock/Rock030_2K-JPG_Roughness.jpg",
    "public/textures/rock/Rock030_2K-JPG_AmbientOcclusion.jpg",
    "public/textures/dirt/Ground037_2K-JPG_Color.jpg",
    "public/textures/dirt/Ground037_2K-JPG_NormalGL.jpg",
    *[f"public/art/sand/{name}-{kind}.png" for name in ("dry-grain", "wind-ripples", "wet-sand", "shell-litter") for kind in ("surface", "detail")],
    *[f"public/textures/forest/{surface}_{kind}.jpg" for surface in ("moss", "floor", "granite") for kind in ("color", "normal", "roughness")],
]


def run(command, cwd=None, **kwargs):
    return subprocess.run(command, cwd=cwd, check=True, **kwargs)


def checkout(path, pin, sparse=None):
    created = not path.exists()
    if created:
        run(["git", "clone", "--filter=blob:none", "--no-checkout", pin["url"], str(path)])
    assert (path / ".git").exists(), f"Expected an isolated Git checkout: {path}"
    current = run(["git", "rev-parse", "HEAD"], cwd=path, capture_output=True, text=True).stdout.strip()
    if current != pin["commit"]:
        if not created:
            changes = run(["git", "status", "--porcelain", "--untracked-files=no"], cwd=path, capture_output=True, text=True).stdout
            assert not changes, f"Refusing to replace modified upstream files: {path}"
        run(["git", "fetch", "--depth", "1", "origin", pin["commit"]], cwd=path)
    if sparse:
        run(["git", "sparse-checkout", "init", "--cone"], cwd=path)
        run(["git", "sparse-checkout", "set", *sparse], cwd=path)
    if created or current != pin["commit"] or not (path / "package.json").exists():
        run(["git", "checkout", "--detach", pin["commit"]], cwd=path)


def link_directory(path, target):
    if path.exists():
        assert path.resolve() == target.resolve(), f"Unexpected directory at {path}"
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    if os.name == "nt":
        env = {**os.environ, "ATLAS_LINK": str(path), "ATLAS_TARGET": str(target)}
        run(["powershell", "-NoProfile", "-Command", "New-Item -ItemType Junction -Path $env:ATLAS_LINK -Target $env:ATLAS_TARGET | Out-Null"], env=env)
    else:
        path.symlink_to(target, target_is_directory=True)


def blob_sha(data):
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def apply_runtime_fixes():
    # Fallback must claim a covered texel, never an empty chart gutter. The upstream
    # increments the atomic before testing coverage, so an empty texel can consume
    # the only fallback slot and leave a small chart entirely unmeasured.
    relative = "src/shared/gi/bake/lightmapSurfels.ts"
    original = run(["git", "show", f"{PINS['upstream']['commit']}:{relative}"], cwd=RUNTIME, capture_output=True).stdout
    before = b"If(chart.greaterThanEqual(int(0)).and(texelSurfel.element(tid).lessThan(int(0))), () => {"
    after = b"If(posSample.w.greaterThan(0.5).and(chart.greaterThanEqual(int(0))).and(texelSurfel.element(tid).lessThan(int(0))), () => {"
    assert original.count(before) == 1, "Pinned fallback patch no longer applies"
    patched = original.replace(before, after)
    target = RUNTIME / relative
    current = target.read_bytes().replace(b"\r\n", b"\n")
    assert current in (original, patched), f"Unexpected local changes: {relative}"
    target.write_bytes(patched)
    return [{"path": relative, "reason": "Only covered texels may claim a chart fallback sample; preserve empty-chart validation", "original_sha256": hashlib.sha256(original).hexdigest(), "patched_sha256": hashlib.sha256(patched).hexdigest(), "before": before.decode(), "after": after.decode()}]


def prepare(skip_install=False):
    CACHE.mkdir(exist_ok=True)
    checkout(RUNTIME, PINS["upstream"], ["src", "scripts", "docs"])
    checkout(THREE, PINS["three"], ["src", "examples/jsm", "build"])
    checkout(FIBER, PINS["fiber"])
    source_patches = apply_runtime_fixes()
    link_directory(RUNTIME / "vendor/three", THREE)
    link_directory(RUNTIME / "vendor/react-three-fiber", FIBER)
    for name in ("package.json", "package-lock.json"):
        shutil.copyfile(PROJECT / "runtime" / name, RUNTIME / name)
    package = json.loads((RUNTIME / "package.json").read_text())
    original = json.loads(run(["git", "show", f"{PINS['upstream']['commit']}:package.json"], cwd=RUNTIME, capture_output=True, text=True).stdout)
    package["scripts"] = original["scripts"]
    (RUNTIME / "package.json").write_text(json.dumps(package, indent=2) + "\n")
    # Original renderer is r182 plus the author's fixes, at the main repository date.
    assert "typeOf( node )" in (THREE / "src/nodes/core/NodeBuilder.js").read_text(encoding="utf-8")
    lock_hash = hashlib.sha256((RUNTIME / "package-lock.json").read_bytes()).hexdigest()
    marker = RUNTIME / ".atlas-dependencies.sha256"
    installed = marker.exists() and marker.read_text() == lock_hash and (RUNTIME / "node_modules/vite/bin/vite.js").exists()
    if not skip_install and not installed:
        run(["npm.cmd" if os.name == "nt" else "npm", "ci", "--ignore-scripts", "--no-audit", "--no-fund"], cwd=RUNTIME)
    assert (RUNTIME / "node_modules/vite/bin/vite.js").exists(), "Run setup without --skip-install first"
    marker.write_text(lock_hash)
    link_directory(FIBER / "node_modules", RUNTIME / "node_modules")
    link_directory(FIBER / "packages/fiber/node_modules", RUNTIME / "node_modules")
    run(["node", str(RUNTIME / "node_modules/vite/bin/vite.js"), "build"], cwd=FIBER)
    # Use the actual pinned Git tree, independent of the text-only evidence cache.
    entries = run(["git", "ls-tree", "-r", PINS["upstream"]["commit"], "public"], cwd=RUNTIME, capture_output=True, text=True).stdout
    blobs = {line.split("\t", 1)[1]: line.split()[2] for line in entries.splitlines()}
    records = []
    for relative in ASSETS:
        file = RUNTIME / relative
        data = file.read_bytes() if file.exists() else b""
        if blob_sha(data) != blobs[relative]:
            url = f"https://raw.githubusercontent.com/vibegameengine/web-starter-kit-webgpu-pipline/{PINS['upstream']['commit']}/{relative}"
            for attempt in range(3):
                try:
                    data = urlopen(Request(url, headers={"User-Agent": "render-atlas-research"}), timeout=90).read()
                    assert blob_sha(data) == blobs[relative], f"Asset blob differs: {relative}"
                    break
                except Exception:
                    if attempt == 2:
                        raise
                    time.sleep(1)
            file.parent.mkdir(parents=True, exist_ok=True)
            file.write_bytes(data)
        records.append({"path": relative, "git_blob": blobs[relative], "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)})
    overlay = RUNTIME / ".atlas"
    overlay.mkdir(exist_ok=True)
    for name in ("main.ts", "vite.runtime.config.mjs"):
        shutil.copyfile(PROJECT / "runtime" / name, overlay / name)
    shutil.copyfile(PROJECT / "runtime/frame.html", RUNTIME / "atlas.html")
    result = {"repositories": PINS, "assets": records, "source_patches": source_patches, "npm_lock_sha256": lock_hash, "fork_selection": "latest commit not later than the pinned main repository date", "prepared": True}
    (overlay / "prepared.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"runtime": str(RUNTIME), "source_commit": PINS["upstream"]["commit"], "assets": len(records), "dependencies": "prepared"}))
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skip-install", action="store_true", help="Use dependencies already installed with this lock")
    prepare(parser.parse_args().skip_install)
