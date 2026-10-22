"""Verify the public release against exact committed bytes, plus its index card."""
from __future__ import annotations
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
import hashlib
from html import escape
import json
from pathlib import Path
import re
import subprocess
import urllib.request

PROJECT = Path(__file__).resolve().parents[1]
REPO = PROJECT.parents[1]
PREFIX = 'projects/013-old-coder/web/'


def git(*arguments):
    return subprocess.check_output(['git', *arguments], cwd=REPO)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--commit', required=True)
    parser.add_argument('--run-url', required=True)
    parser.add_argument('--base', default='https://yydshly.github.io/1022_codex_project/013-old-coder/')
    parser.add_argument('--output', type=Path, default=PROJECT / 'deployment-verification.json')
    args = parser.parse_args()
    if not re.fullmatch('[0-9a-f]{40}', args.commit):
        raise SystemExit('Use an exact 40-character source commit.')
    paths = git('ls-tree', '-r', '--name-only', args.commit, '--', PREFIX).decode('utf-8').splitlines()
    if not paths:
        raise SystemExit('No committed release files.')

    def fetch(url):
        request = urllib.request.Request(url, headers={'User-Agent':'OldCoderResearchVerification/1.0','Cache-Control':'no-cache'})
        with urllib.request.urlopen(request, timeout=45) as response:
            return response.status, response.read(), response.geturl()

    def verify_file(path):
        relative = path.removeprefix(PREFIX)
        url = args.base.rstrip('/') + '/' + relative + '?v=' + args.commit[:12]
        code, actual, final_url = fetch(url)
        expected = git('show', f'{args.commit}:{path}')
        return {'path':relative,'url':final_url,'http':code,'bytes':len(actual),
                'sha256':hashlib.sha256(actual).hexdigest(),
                'expectedSHA256':hashlib.sha256(expected).hexdigest(),
                'identical':actual == expected}

    with ThreadPoolExecutor(max_workers=5) as pool:
        files = list(pool.map(verify_file, paths))
    catalog = json.loads(git('show', f'{args.commit}:projects/catalog.json'))
    entry = next(item for item in catalog['projects'] if item['id'] == '013')
    home = args.base.rstrip('/').rsplit('/',1)[0] + '/'
    status, body, home_url = fetch(home + '?v=' + args.commit[:12])
    markup = body.decode('utf-8')
    cards = [card for card in re.findall(r'<article>.*?</article>', markup, re.S) if './013-old-coder/' in card]
    home_checks = {'status':status,'url':home_url,'oneProjectCard':len(cards)==1,
                   'fullSummary':len(cards)==1 and escape(entry['summary']) in cards[0],
                   'specifiedGuide':len(cards)==1 and './013-old-coder/assets/old-coder-overview.png' in cards[0]}
    passed = all(row['http']==200 and row['identical'] for row in files) and all(home_checks[key] for key in ('oneProjectCard','fullSummary','specifiedGuide'))
    report = {'verifiedAt':datetime.now(timezone(timedelta(hours=8))).isoformat(),
              'contentCommit':args.commit,'actionsRun':args.run_url,'publicURL':args.base,
              'status':'passed' if passed else 'failed','files':files,'homepage':home_checks,
              'scope':'Public HTTP content identity and project index only. Browser interactions recorded separately. No production business services were tested.'}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes((json.dumps(report,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
    print(f"Public release: {len(files)} files; identical {sum(row['identical'] for row in files)}/{len(files)}; index {'pass' if all(home_checks[k] for k in ('oneProjectCard','fullSummary','specifiedGuide')) else 'fail'}")
    if not passed:
        raise SystemExit('Public content does not match the source release.')


if __name__ == '__main__':
    main()
