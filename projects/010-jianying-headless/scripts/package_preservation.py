"""Package and verify the preserved upstream snapshots without running upstream code."""
from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
import hashlib
from io import BytesIO
import json
from pathlib import Path, PurePosixPath
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[1]
NAME = "upstream-preservation-20261022.zip"
ARCHIVE = ROOT / "backups" / NAME
CHECKSUM = ARCHIVE.with_suffix(".zip.sha256")
RECORD = ROOT / "preservation-package.json"
PREFIX = "preservation-20261022/"
STAMP = "20261022T135829+0800"
FIXED_TIME = (2026, 10, 22, 13, 58, 28)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def digest(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def json_bytes(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def source_matches(content: bytes, expected: dict) -> bool:
    return len(content) == expected["bytes"] and digest(content) == expected["sha256"]


def source_statistics(manifest: dict, payload: dict[str, bytes]) -> dict:
    repositories = []
    for repository in manifest["repositories"]:
        name = next(name for name in repository["artifacts"] if name.endswith(".zip"))
        files = entries(payload["snapshot/" + name])
        exact = sum(source_matches(files[entry["path"]], entry) for entry in repository["source_files"])
        converted = sum(not source_matches(files[entry["path"]], entry)
                        and source_matches(files[entry["path"]].replace(b"\r\n", b"\n"), entry)
                        for entry in repository["source_files"])
        repositories.append({"name": repository["name"], "files": len(repository["source_files"]),
                             "exact_bytes": exact, "only_crlf_conversion": converted})
    return {"files": sum(item["files"] for item in repositories),
            "exact_bytes": sum(item["exact_bytes"] for item in repositories),
            "only_crlf_conversion": sum(item["only_crlf_conversion"] for item in repositories),
            "repositories": repositories}


def entries(data: bytes) -> dict[str, bytes]:
    with zipfile.ZipFile(BytesIO(data)) as archive:
        names = archive.namelist()
        require(len(names) == len(set(names)), "Duplicate ZIP entries")
        for name in names:
            path = PurePosixPath(name)
            require(not path.is_absolute() and ".." not in path.parts
                    and "\\" not in name and ":" not in name, f"Unsafe ZIP path: {name}")
        require(archive.testzip() is None, "ZIP CRC failure")
        return {name: archive.read(name) for name in names if not name.endswith("/")}


def sources() -> dict[str, bytes]:
    original = ROOT / "backups" / STAMP
    manifest = json.loads((original / "manifest.json").read_text(encoding="utf-8"))
    expected = {"manifest.json", "SHA256SUMS.txt", "verification.json"}
    for repository in manifest["repositories"]:
        expected.update(repository["artifacts"])
    require(expected == {path.name for path in original.iterdir() if path.is_file()},
            "Unexpected files in original dated backup")
    payload = {"snapshot/" + name: (original / name).read_bytes() for name in sorted(expected)}
    payload["README.md"] = (ROOT / "backups/README.md").read_bytes()
    for repository in manifest["repositories"]:
        source_root = ROOT / repository["source_directory"]
        for relative in repository["license_files"]:
            payload[f"licenses/{repository['name']}/{relative}"] = (source_root / relative).read_bytes()
    content_index = {name: {"bytes": len(content), "sha256": digest(content)}
                     for name, content in sorted(payload.items())}
    payload["CONTENTS.json"] = json_bytes({"schema": "jianying-preservation-contents/v1", "files": content_index})
    return payload


def build() -> None:
    payload = sources()
    output = BytesIO()
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name, content in sorted(payload.items()):
            info = zipfile.ZipInfo(PREFIX + name, date_time=FIXED_TIME)
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, content, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
    content = output.getvalue()
    if ARCHIVE.exists():
        require(ARCHIVE.read_bytes() == content, "Existing archive differs; do not overwrite preserved data")
    else:
        ARCHIVE.write_bytes(content)
    checksum = f"{digest(content)}  {NAME}\n".encode("ascii")
    if CHECKSUM.exists():
        require(CHECKSUM.read_bytes() == checksum, "Existing checksum differs")
    else:
        CHECKSUM.write_bytes(checksum)
    if not RECORD.exists():
        manifest = json.loads(payload["snapshot/manifest.json"])
        repositories = [{key: record[key] for key in
                         ("name", "origin", "head_ref", "head_commit", "reachable_commits")}
                        | {"refs": len(record["refs"]), "source_files": len(record["source_files"])}
                        for record in manifest["repositories"]]
        record = {"schema": "jianying-preservation-package/v1",
                  "created_at": datetime.now(timezone(timedelta(hours=8))).isoformat(),
                  "snapshot_created_at": manifest["created_at"],
                  "purpose": "防止上游删除、封禁或访问中断的个人非商业学习研究保全",
                  "archive": "backups/" + NAME, "bytes": len(content), "sha256": digest(content),
                  "archive_files": len(payload), "repositories": repositories,
                  "includes": "两个 bundle、两个主分支源码 ZIP、原引用映射/清单/校验记录、恢复说明、原许可证与第三方声明",
                  "excludes": manifest["excludes"] + ["local mirror configuration", "credentials"],
                  "license": "Personal Learning and Non-Commercial Use License; third-party notices preserved",
                  "source_zip_note": "Original Windows git archive ZIPs are retained byte-for-byte; 249 files have CRLF conversion. Exact Git blobs remain in the bundles and are independently restored and checked.",
                  "source_archive_validation": source_statistics(manifest, payload),
                  "verification": {"status": "archive-and-source-verified", "network_used": False,
                                   "upstream_code_executed": False, "native_jianying_tested": False}}
        RECORD.write_bytes(json_bytes(record))
    check()


def check() -> tuple[dict, dict[str, bytes]]:
    record = json.loads(RECORD.read_text(encoding="utf-8"))
    content = ARCHIVE.read_bytes()
    require(record["archive"] == ARCHIVE.relative_to(ROOT).as_posix(), "Unexpected archive path")
    require(len(content) == record["bytes"] and digest(content) == record["sha256"], "Outer archive hash differs")
    require(CHECKSUM.read_text(encoding="ascii") == f"{digest(content)}  {NAME}\n", "Checksum differs")
    raw = entries(content)
    require(all(name.startswith(PREFIX) for name in raw), "Unexpected archive root")
    payload = {name[len(PREFIX):]: value for name, value in raw.items()}
    require(len(payload) == record["archive_files"], "Archive entry count differs")
    index = json.loads(payload["CONTENTS.json"])["files"]
    require(set(payload) == set(index) | {"CONTENTS.json"}, "Archive entries differ from contents index")
    for name, expected in index.items():
        require(len(payload[name]) == expected["bytes"] and digest(payload[name]) == expected["sha256"],
                f"Archive payload differs: {name}")
    manifest_bytes = payload["snapshot/manifest.json"]
    manifest = json.loads(manifest_bytes)
    require(record["source_archive_validation"] == source_statistics(manifest, payload), "Source validation counts differ")
    for line in payload["snapshot/SHA256SUMS.txt"].decode("utf-8").splitlines():
        expected, name = line.split("  ", 1)
        require(digest(payload["snapshot/" + name]) == expected, f"Original checksum differs: {name}")
    source_count = 0
    converted_count = 0
    for repository, public in zip(manifest["repositories"], record["repositories"]):
        require(repository["name"] == public["name"] and repository["head_commit"] == public["head_commit"],
                "Repository identity differs")
        require(len(repository["refs"]) == public["refs"] and len(repository["source_files"]) == public["source_files"],
                "Repository counts differ")
        for name, expected in repository["artifacts"].items():
            blob = payload["snapshot/" + name]
            require(len(blob) == expected["bytes"] and digest(blob) == expected["sha256"], f"Original artifact differs: {name}")
        source_zip_name = next(name for name in repository["artifacts"] if name.endswith(".zip"))
        files = entries(payload["snapshot/" + source_zip_name])
        require(set(files) == {entry["path"] for entry in repository["source_files"]}, "Source ZIP entries differ")
        for entry in repository["source_files"]:
            blob = files[entry["path"]]
            if not source_matches(blob, entry):
                require(source_matches(blob.replace(b"\r\n", b"\n"), entry), f"Source blob differs beyond CRLF: {entry['path']}")
                converted_count += 1
            source_count += 1
        for relative in repository["license_files"]:
            license_blob = payload[f"licenses/{repository['name']}/{relative}"]
            original = next(entry for entry in repository["source_files"] if entry["path"] == relative)
            require(source_matches(license_blob, original), "Exact license copy differs")
            require(license_blob == files[relative] or license_blob == files[relative].replace(b"\r\n", b"\n"), "License source differs beyond CRLF")
    require(len(manifest["repositories"]) == 2 and source_count == 357, "Expected two repositories and 357 source files")
    require(converted_count == 249, "Unexpected CRLF conversion count")
    print(f"Preservation archive verified: {len(payload)} files, {source_count} source files ({converted_count} CRLF conversions), {len(content)} bytes, SHA-256 {digest(content)}")
    return manifest, payload


def git(*arguments: str) -> str:
    result = subprocess.run(["git", "-c", "core.hooksPath=", *arguments], check=True, capture_output=True)
    return result.stdout.decode("utf-8").strip()


def restore_check(directory: str) -> None:
    manifest, payload = check()
    target = (ROOT / directory).resolve()
    allowed = (ROOT / "_upstream").resolve()
    require(target != allowed and target.is_relative_to(allowed), "Restore target must be inside this project's _upstream/")
    require(not target.exists(), "Restore target must not exist")
    target.mkdir(parents=True)
    results = []
    for repository in manifest["repositories"]:
        bundle = target / repository["bundle"]
        bundle.write_bytes(payload["snapshot/" + repository["bundle"]])
        mirror = target / (repository["name"] + ".git")
        git("clone", "--mirror", str(bundle), str(mirror))
        prefix = f"--git-dir={mirror}"
        refs = dict(line.split(" ", 1) for line in git(prefix, "for-each-ref", "--format=%(refname) %(objectname)").splitlines())
        require(refs == repository["refs"], "Restored refs differ")
        require(git(prefix, "rev-parse", "HEAD") == repository["head_commit"], "Restored HEAD differs")
        require(int(git(prefix, "rev-list", "--all", "--count")) == repository["reachable_commits"], "Restored commit count differs")
        git(prefix, "fsck", "--full", "--strict")
        git(prefix, "bundle", "verify", str(bundle))
        requests = "".join(entry["git_blob"] + "\n" for entry in repository["source_files"]).encode("ascii")
        response = subprocess.run(["git", prefix, "cat-file", "--batch"], input=requests, capture_output=True, check=True)
        stream = BytesIO(response.stdout)
        for entry in repository["source_files"]:
            object_id, kind, length = stream.readline().decode("ascii").strip().split(" ")
            require(object_id == entry["git_blob"] and kind == "blob", "Restored Git object identity differs")
            blob = stream.read(int(length))
            require(stream.read(1) == b"\n" and source_matches(blob, entry), "Restored exact Git blob differs")
        require(stream.read() == b"", "Unexpected batch output")
        results.append({"name": repository["name"], "head_commit": repository["head_commit"],
                        "refs": len(refs), "reachable_commits": repository["reachable_commits"],
                        "exact_source_blobs_verified": len(repository["source_files"]),
                        "refs_match": True, "head_matches": True, "fsck_passed": True, "bundle_verified": True})
    evidence = {"status": "independent-offline-restore-verified", "network_used": False,
                "upstream_code_executed": False, "native_jianying_tested": False,
                "source": "Only bundle bytes extracted from the final outer ZIP; no pre-existing mirrors used",
                "target": target.relative_to(ROOT).as_posix(), "repositories": results}
    record = json.loads(RECORD.read_text(encoding="utf-8"))
    record["verification"] = evidence
    RECORD.write_bytes(json_bytes(record))
    print(json.dumps(evidence, ensure_ascii=False, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--check", action="store_true", help="Verify only the final archive, checksum and record; no source mirrors required")
    group.add_argument("--restore-check", metavar="DIRECTORY", help="Verify by restoring final ZIP bundles into a new project-local _upstream directory")
    args = parser.parse_args()
    if args.restore_check:
        restore_check(args.restore_check)
    elif args.check:
        check()
    else:
        build()


if __name__ == "__main__":
    main()
