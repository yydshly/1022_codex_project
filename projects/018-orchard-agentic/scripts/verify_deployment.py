"""Verify public Pages files against the exact Git source, plus its index card."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime,timezone,timedelta
from html import escape
import argparse
import hashlib
import json
import re
import subprocess
import urllib.request

PROJECT=Path(__file__).resolve().parents[1]
ROOT=PROJECT.parents[1]
PREFIX='projects/018-orchard-agentic/web/'
def git(*args): return subprocess.check_output(['git',*args],cwd=ROOT)
def fetch(url):
    req=urllib.request.Request(url,headers={'User-Agent':'OrchardResearchVerification/1.0','Cache-Control':'no-cache'})
    with urllib.request.urlopen(req,timeout=40) as r: return r.status,r.read(),r.geturl()
def main():
    p=argparse.ArgumentParser()
    p.add_argument('--commit',required=True)
    p.add_argument('--run-url',required=True)
    p.add_argument('--base',default='https://yydshly.github.io/1022_codex_project/018-orchard-agentic/')
    args=p.parse_args()
    if not re.fullmatch('[0-9a-f]{40}',args.commit): raise SystemExit('Use an exact 40-character commit.')
    paths=git('ls-tree','-r','--name-only',args.commit,'--',PREFIX).decode('utf-8').splitlines()
    if not paths: raise SystemExit('No committed publishing files.')
    def verify(path):
        relative=path.removeprefix(PREFIX)
        status,actual,url=fetch(args.base+relative+'?v='+args.commit[:12])
        expected=git('show',args.commit+':'+path)
        return {'path':relative,'url':url,'http':status,'bytes':len(actual),'sha256':hashlib.sha256(actual).hexdigest(),'expectedSHA256':hashlib.sha256(expected).hexdigest(),'identical':actual==expected}
    with ThreadPoolExecutor(max_workers=5) as pool: files=list(pool.map(verify,paths))
    catalog=json.loads(git('show',args.commit+':projects/catalog.json'))
    item=next(x for x in catalog['projects'] if x['slug']=='orchard-agentic')
    home=args.base.rstrip('/').rsplit('/',1)[0]+'/'
    code,body,url=fetch(home+'?v='+args.commit[:12])
    cards=[x for x in re.findall(r'<article>.*?</article>',body.decode('utf-8'),re.S) if './018-orchard-agentic/' in x]
    homepage={'http':code,'url':url,'oneProjectCard':len(cards)==1,'completeSummary':len(cards)==1 and escape(item['summary']) in cards[0],'approvedGuide':len(cards)==1 and './018-orchard-agentic/'+item['cover'] in cards[0]}
    passed=all(x['http']==200 and x['identical'] for x in files) and all(homepage[k] for k in ('oneProjectCard','completeSummary','approvedGuide'))
    report={'verifiedAt':datetime.now(timezone(timedelta(hours=8))).isoformat(),'status':'passed' if passed else 'failed','publicURL':args.base,'contentCommit':args.commit,'actionsRun':args.run_url,'files':files,'homepage':homepage,'scope':'Public HTTP file identity, full index summary and approved guide. Browser interactions are recorded separately. Upstream cluster, inference and training were not run.'}
    (PROJECT/'deployment-verification.json').write_bytes((json.dumps(report,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
    print(f'Public release: {sum(x["identical"] for x in files)}/{len(files)} identical; index '+('passed' if passed else 'failed'))
    if not passed: raise SystemExit('Public content does not match the committed release.')
if __name__=='__main__': main()
