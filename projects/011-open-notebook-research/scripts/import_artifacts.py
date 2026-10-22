"""Import only reviewed public research artifacts from study 008 (no network)."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT.parent / "008-auto-paper-digest"


def main():
    metadata = json.loads((SOURCE / "results/aquatic-papers.json").read_text(encoding="utf-8"))
    items = []

    def copy(source: Path, relative: str, expected: str | None = None):
        content = source.read_bytes()
        digest = hashlib.sha256(content).hexdigest()
        if expected is not None and digest != expected:
            raise ValueError(f"SHA256 mismatch: {source.name}")
        dest = ROOT / relative
        dest.parent.mkdir(parents=True, exist_ok=True)
        if dest.exists() and dest.read_bytes() != content:
            raise ValueError(f"Refusing to overwrite changed artifact: {relative}")
        shutil.copyfile(source, dest)
        items.append({"path": relative, "source": source.relative_to(ROOT.parent.parent).as_posix(), "bytes": len(content), "sha256": digest})

    for paper in metadata["papers"]:
        source = SOURCE / paper["pdf_path"]
        if not source.read_bytes().startswith(b"%PDF-"):
            raise ValueError(f"Invalid PDF: {paper['paper_id']}")
        copy(source, f"assets/papers/{paper['paper_id']}.pdf", paper["pdf_sha256"])
    for name in ("open-notebook-single-answer.md", "open-notebook-synthesis-answer.md", "open-notebook-single-truncated.md"):
        copy(SOURCE / "results" / name, "results/answers/" + name)
    for name in ("aquatic-papers.json", "aquatic-search.json", "open-notebook-cloud-check.json", "open-notebook-minimax-check.json"):
        copy(SOURCE / "results" / name, "results/evidence/" + name)
    copy(SOURCE / "deploy/open-notebook/licenses/OpenNotebook-LICENSE", "assets/licenses/OpenNotebook-LICENSE.txt")
    copy(SOURCE / "deploy/open-notebook/licenses/Esperanto-LICENSE", "assets/licenses/Esperanto-LICENSE.txt")
    copy(SOURCE / "deploy/open-notebook/licenses/SurrealDB-LICENSE", "assets/licenses/SurrealDB-LICENSE.txt")
    record = {"schema_version": 1, "imported_on": "2026-10-22", "method": "Allowlisted byte-for-byte copies of saved research outputs; SHA256 checked; no network or model call.", "records": items}
    (ROOT / "results/import-manifest.json").write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Imported {len(items)} artifacts with exact byte hashes.")


if __name__ == "__main__":
    main()
