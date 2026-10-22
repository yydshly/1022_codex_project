"""Run the pinned upstream CLI, keeping files and login sessions project-local."""
from pathlib import Path
import sys

PROJECT = Path(__file__).resolve().parents[1]
REPOSITORY = PROJECT.parents[1]
UPSTREAM = REPOSITORY / "_upstream" / "008-auto-paper-digest"


def configure():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    if not (UPSTREAM / "apd" / "cli.py").is_file():
        raise SystemExit("Clone the pinned upstream into _upstream/008-auto-paper-digest first.")
    sys.path.insert(0, str(UPSTREAM))
    import apd.config as config
    config.DATA_DIR = PROJECT / ".runtime"
    for key, directory in {
        "PDF_DIR": "pdfs", "VIDEO_DIR": "videos", "SLIDES_DIR": "slides",
        "DIGEST_DIR": "digests", "PROFILE_DIR": "profiles",
    }.items():
        setattr(config, key, config.DATA_DIR / directory)
    config.DB_PATH = config.DATA_DIR / "apd.db"
    config.ensure_directories()
    return config


if __name__ == "__main__":
    configure()
    from apd.cli import main
    main(prog_name="apd")
