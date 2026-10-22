"""Preserve the two upstream repositories and verify independent offline recovery.

Only Git data is inspected; no upstream code, hooks or installation scripts run.
Existing dated backups are never updated or removed.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path, PurePosixPath
import stat
import subprocess


ROOT = Path(__file__).resolve().parents[1]
UPSTREAMS = {
    "jianying-headless": "https://github.com/mcncarl/jianying-headless.git",
    "yichen-skills": "https://github.com/mcncarl/yichen-skills.git",
}


def run(*args: str, cwd: Path | None = None) -> str:
    result = subprocess.run(args, cwd=cwd, capture_output=True, check=True)
    return result.stdout.decode("utf-8", errors="strict").strip()


def git(repository: Path, *args: str) -> str:
    return run("git", f"--git-dir={repository}", *args)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(path: Path, value: object) -> None:
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write("\n")


def references(repository: Path) -> dict[str, str]:
    lines = git(repository, "for-each-ref", "--format=%(refname) %(objectname)")
    return dict(line.split(" ", 1) for line in lines.splitlines())


def archive_files(repository: Path, commit: str, destination: Path) -> list[dict]:
    """Materialize exact Git blobs, retaining a ZIP for original mode metadata."""
    listing = subprocess.run(
        ["git", f"--git-dir={repository}", "ls-tree", "-rz", commit],
        capture_output=True, check=True,
    ).stdout
    destination.mkdir(parents=True, exist_ok=False)
    files = []
    for entry in listing.split(b"\0"):
        if not entry:
            continue
        metadata, raw_path = entry.split(b"\t", 1)
        mode, kind, object_id = metadata.decode("ascii").split()
        relative = raw_path.decode("utf-8")
        parts = PurePosixPath(relative)
        if parts.is_absolute() or ".." in parts.parts or "\\" in relative or ":" in relative:
            raise ValueError(f"Unsafe Git path: {relative}")
        if kind != "blob" or mode not in {"100644", "100755"}:
            raise ValueError(f"Submodule/symlink needs separate preservation: {relative}")
        target = destination.joinpath(*parts.parts)
        if not target.resolve().is_relative_to(destination.resolve()):
            raise ValueError(f"Git path escapes destination: {relative}")
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("xb") as stream:
            subprocess.run(
                ["git", f"--git-dir={repository}", "cat-file", "blob", object_id],
                stdout=stream, check=True,
            )
        if mode == "100755":
            target.chmod(target.stat().st_mode | stat.S_IXUSR)
        files.append({"path": relative, "git_mode": mode, "git_blob": object_id,
                      "bytes": target.stat().st_size, "sha256": sha256(target)})
    return files


def verify(directory: Path) -> dict:
    for line in (directory / "SHA256SUMS.txt").read_text(encoding="utf-8").splitlines():
        expected, filename = line.split("  ", 1)
        artifact = directory / filename
        if artifact.parent != directory or sha256(artifact) != expected:
            raise ValueError(f"Checksum mismatch: {filename}")
    manifest = json.loads((directory / "manifest.json").read_text(encoding="utf-8"))
    if manifest.get("schema") != "jianying-upstream-backup/v1":
        raise ValueError("Unsupported backup manifest")
    results = []
    for record in manifest["repositories"]:
        for filename, expected in record["artifacts"].items():
            path = directory / filename
            if path.parent != directory or sha256(path) != expected["sha256"]:
                raise ValueError(f"Backup artifact changed: {filename}")
        for entry in record["source_files"]:
            path = ROOT / record["source_directory"] / entry["path"]
            if sha256(path) != entry["sha256"]:
                raise ValueError(f"Source snapshot changed: {path}")
        restored = ROOT / record["restored_mirror"]
        if references(restored) != record["refs"]:
            raise ValueError(f"Restored refs differ: {record['name']}")
        if git(restored, "rev-parse", "HEAD") != record["head_commit"]:
            raise ValueError(f"Restored HEAD differs: {record['name']}")
        git(restored, "fsck", "--full", "--strict")
        git(restored, "bundle", "verify", str(directory / record["bundle"]))
        results.append({"name": record["name"], "head_commit": record["head_commit"],
                        "refs": len(record["refs"]), "source_files": len(record["source_files"]),
                        "offline_restored_refs_match": True, "fsck_passed": True,
                        "sha256_passed": True})
    return {"status": "verified", "network_used": False, "repositories": results}


def create() -> Path:
    if (ROOT / "backup-record.json").exists():
        raise ValueError("A backup record already exists; use --verify for this preserved snapshot")
    now = datetime.now(timezone(timedelta(hours=8)))
    stamp = now.strftime("%Y%m%dT%H%M%S%z")
    directory = ROOT / "backups" / stamp
    directory.mkdir(parents=True, exist_ok=False)
    manifest = {
        "schema": "jianying-upstream-backup/v1", "created_at": now.isoformat(),
        "git_version": run("git", "--version"),
        "scope": "All locally mirrored advertised Git refs, reachable history, and HEAD source trees",
        "excludes": ["GitHub issues/comments", "release attachments", "unadvertised/deleted objects",
                     "Jianying application binaries", "external runtime and third-party services"],
        "repositories": [],
    }
    for name, url in UPSTREAMS.items():
        mirror = ROOT / "_upstream" / f"{name}.git"
        if not mirror.exists():
            mirror.parent.mkdir(parents=True, exist_ok=True)
            run("git", "clone", "--mirror", url, str(mirror))
        if git(mirror, "remote", "get-url", "origin") != url:
            raise ValueError(f"Unexpected mirror origin: {mirror}")
        if git(mirror, "rev-parse", "--is-shallow-repository") != "false":
            raise ValueError(f"Shallow repository is not a full backup: {name}")
        git(mirror, "fsck", "--full", "--strict")
        refs = references(mirror)
        head_ref = git(mirror, "symbolic-ref", "HEAD")
        commit = git(mirror, "rev-parse", "HEAD")
        # LFS objects and submodules are outside ordinary Git object preservation.
        lfs = json.loads(git(mirror, "lfs", "ls-files", "--all", "--json") or "[]")
        lfs_files = lfs.get("files") if isinstance(lfs, dict) else lfs
        if lfs_files:
            raise ValueError(f"LFS content requires separate object archival: {name}")
        if git(mirror, "log", "--all", "--format=", "--name-only", "--", ".gitmodules"):
            raise ValueError(f"Submodule history requires separate archival: {name}")

        bundle = directory / f"{name}.bundle"
        git(mirror, "bundle", "create", str(bundle), "--all")
        git(mirror, "bundle", "verify", str(bundle))
        archive = directory / f"{name}-{commit[:12]}.zip"
        git(mirror, "archive", "--format=zip", f"--output={archive}", commit)
        source = ROOT / "_upstream" / "sources" / stamp / name
        files = archive_files(mirror, commit, source)
        # A separate repository is restored only from the portable bundle.
        restored = ROOT / "_upstream" / "restore-checks" / stamp / f"{name}.git"
        restored.parent.mkdir(parents=True, exist_ok=True)
        run("git", "clone", "--mirror", str(bundle), str(restored))
        if references(mirror) != refs or git(mirror, "rev-parse", "HEAD") != commit:
            raise ValueError(f"Mirror changed during backup: {name}")
        refs_path = directory / f"{name}-refs.json"
        write_json(refs_path, {"HEAD": head_ref, "refs": refs})
        records = [bundle, archive, refs_path]
        artifacts = {p.name: {"sha256": sha256(p), "bytes": p.stat().st_size} for p in records}
        manifests = {entry["path"]: entry for entry in files}
        license_paths = [path for path in manifests if "license" in path.lower()
                         or "notice" in path.lower()]
        record = {
            "name": name, "origin": url, "head_ref": head_ref, "head_commit": commit,
            "head_commit_time": git(mirror, "show", "-s", "--format=%cI", commit),
            "reachable_commits": int(git(mirror, "rev-list", "--all", "--count")),
            "branches": sum(ref.startswith("refs/heads/") for ref in refs),
            "tags": sum(ref.startswith("refs/tags/") for ref in refs),
            "pull_refs": sum(ref.startswith("refs/pull/") for ref in refs),
            "refs": refs, "lfs_objects": 0, "submodule_history": False,
            "mirror": mirror.relative_to(ROOT).as_posix(), "bundle": bundle.name,
            "source_directory": source.relative_to(ROOT).as_posix(),
            "restored_mirror": restored.relative_to(ROOT).as_posix(),
            "source_files": files, "license_files": license_paths, "artifacts": artifacts,
        }
        manifest["repositories"].append(record)
        print(f"Archived {name}: {len(refs)} refs, {record['reachable_commits']} commits, {len(files)} files", flush=True)
    write_json(directory / "manifest.json", manifest)
    artifacts = sorted(p for p in directory.iterdir() if p.is_file())
    with (directory / "SHA256SUMS.txt").open("x", encoding="utf-8", newline="\n") as stream:
        for path in artifacts:
            stream.write(f"{sha256(path)}  {path.name}\n")
    result = verify(directory)
    write_json(directory / "verification.json", result)
    # This compact index is safe to retain with our own research documentation.
    public_record = {key: value for key, value in manifest.items() if key != "repositories"}
    public_record["backup_directory"] = directory.relative_to(ROOT).as_posix()
    public_record["manifest_sha256"] = sha256(directory / "manifest.json")
    public_record["repositories"] = [
        {key: value for key, value in record.items() if key not in {"source_files", "refs"}}
        | {"ref_count": len(record["refs"]), "source_file_count": len(record["source_files"])}
        for record in manifest["repositories"]
    ]
    public_record["verification"] = result
    output = ROOT / "backup-record.json"
    if output.exists():
        raise ValueError("backup-record.json already exists; existing records were not overwritten")
    write_json(output, public_record)
    print(json.dumps({"status": "verified", "backup_directory": str(directory)}, ensure_ascii=False))
    return directory


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify", type=Path, help="Verify an existing dated backup offline")
    args = parser.parse_args()
    if args.verify:
        path = args.verify.resolve(strict=True)
        if not path.is_relative_to((ROOT / "backups").resolve()):
            raise ValueError("Choose a backup directory inside this project")
        print(json.dumps(verify(path), ensure_ascii=False, indent=2))
    else:
        create()


if __name__ == "__main__":
    main()
