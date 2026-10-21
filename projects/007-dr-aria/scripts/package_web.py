"""Copy the project-owned overview image into the standalone static website."""
import argparse
from pathlib import Path
import shutil

project = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--check", action="store_true")
args = parser.parse_args()
source = project / "assets/understanding-summary.png"
destination = project / "web/assets/understanding-summary.png"
if args.check:
    if not destination.is_file() or source.read_bytes() != destination.read_bytes():
        parser.error("Overview image is not packaged; run this script without --check.")
    print("Overview image: byte-identical")
else:
    destination.parent.mkdir(exist_ok=True)
    shutil.copyfile(source, destination)
    print("Packaged overview image")
