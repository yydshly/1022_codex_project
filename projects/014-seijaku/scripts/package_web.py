"""Copy research media and generation provenance into the publishing directory."""
from pathlib import Path
import argparse
import hashlib
import json
import shutil

ROOT = Path(__file__).resolve().parents[1]
FILES = ('overview.svg', 'residence-journey.jpg', 'research-summary.png', 'research-summary-prompt.txt')

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    for name in FILES:
        source, target = ROOT / 'assets' / name, ROOT / 'web' / 'assets' / name
        if not source.is_file():
            raise SystemExit(f'Missing original: {source}')
        if args.check:
            if not target.is_file() or target.read_bytes() != source.read_bytes():
                raise SystemExit(f'Publish copy differs: {name}')
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
    manifest = ROOT / 'SOURCE.json'
    if manifest.is_file():
        for item in json.loads(manifest.read_text(encoding='utf-8'))['local_media']:
            actual = hashlib.sha256((ROOT / item['path']).read_bytes()).hexdigest()
            if actual != item['sha256']:
                raise SystemExit(f'Media digest changed; update provenance: {item["path"]}')
    print(f'{"Checked" if args.check else "Packaged"} {len(FILES)} research media/provenance files; no upstream assets copied.')

if __name__ == '__main__':
    main()
