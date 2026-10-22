"""Verify published resource paths, the approved guide and research provenance."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
from datetime import datetime, timezone, timedelta
import hashlib
import json
import struct

PROJECT=Path(__file__).resolve().parents[1]
ROOT=PROJECT.parents[1]
WEB=PROJECT/'web'
checks=[]
def check(name,condition):
    checks.append({'name':name,'passed':bool(condition)})
    if not condition: raise SystemExit('FAILED: '+name)

class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.urls=[]
    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        for key in ('href','src'):
            if key in attrs: self.urls.append(attrs[key])

data=json.loads((WEB/'research.json').read_text(encoding='utf-8'))
catalog=json.loads((ROOT/'projects/catalog.json').read_text(encoding='utf-8'))
entry=next(x for x in catalog['projects'] if x['slug']=='orchard-agentic')
check('Catalog and page have the identical capability/technology/scenario summary',entry['summary']==data['summary'])
check('README includes the full summary',data['summary'] in (PROJECT/'README.md').read_text(encoding='utf-8'))
check('Cover points to the approved guide',entry['cover']==data['guide'])
manifest=json.loads((PROJECT/'assets/guide-manifest.json').read_text(encoding='utf-8'))
for row in manifest['assets']:
    original=(PROJECT/row['path']).read_bytes()
    published=(PROJECT/row['published_copy']).read_bytes()
    check('Approved source identity: '+row['path'],hashlib.sha256(original).hexdigest()==row['sha256'])
    check('Exact published image copy: '+row['published_copy'],original==published)
png=(WEB/data['guide']).read_bytes()
check('PNG dimensions retain the original 2400 x 5480',png[:8]==b'\x89PNG\r\n\x1a\n' and struct.unpack('>II',png[16:24])==(2400,5480))
parser=Links();markup=(WEB/'index.html').read_text(encoding='utf-8');parser.feed(markup)
for url in parser.urls:
    parsed=urlsplit(url)
    if parsed.scheme or not parsed.path or parsed.path=='../': continue
    check('Relative publishing path: '+url,not parsed.path.startswith('/'))
    path=(WEB/unquote(parsed.path)).resolve()
    check('Resource stays inside web: '+url,path.is_relative_to(WEB.resolve()))
    check('Resource exists: '+url,path.is_file())
for key in ['roles','capabilities','techniques','scenarios','metrics','sources']:
    check('Research section exists: '+key,bool(data[key]))
check('Sources point at the reviewed fixed commit',all(data['commit'] in x['url'] for x in data['sources']))
evidence=(PROJECT/'research-evidence.json').read_bytes()
check('Published evidence identity',evidence==(WEB/'research-evidence.json').read_bytes())
e=json.loads(evidence)
check('Evidence commit matches the page',e['commit']==data['commit'])
check('All source files have full SHA-256 hashes',all(len(x['sha256'])==64 and x['bytes']>0 for x in e['files']))
check('License publishing identity',(PROJECT/'LICENSE.upstream.txt').read_bytes()==(WEB/'LICENSE.upstream.txt').read_bytes())
check('MIT notice retained',b'Copyright (c) Microsoft Corporation' in (WEB/'LICENSE.upstream.txt').read_bytes())
check('Editable reuse plan publishing identity',(PROJECT/'REUSE.md').read_bytes()==(WEB/'reuse-plan.md').read_bytes())
check('Metrics disclose reranking and pass@3',any('六候选' in x['condition'] for x in data['metrics']) and any('三次尝试' in x['condition'] for x in data['metrics']))
check('Future snapshot features are labeled as roadmap','仍在上游路线图' in markup)
check('No raw HTML injection from research JSON','innerHTML' not in (WEB/'app.js').read_text(encoding='utf-8'))
report={'verifiedAt':datetime.now(timezone(timedelta(hours=8))).isoformat(),'status':'passed','checks':checks,'scope':'Static links, artifact identity, provenance and research consistency only; browser interactions and public deployment are recorded separately.'}
(PROJECT/'web-verification.json').write_bytes((json.dumps(report,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
print(f'Web verification passed: {len(checks)} checks; guide and provenance retained exactly.')
