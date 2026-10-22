"""Validate publishing paths, provenance, fixed sources and media copies."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
import json
import re
import subprocess
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / 'web'

class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids, self.urls, self.images = set(), [], []
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'id' in attrs:
            assert attrs['id'] not in self.ids, f'Duplicate id: {attrs["id"]}'
            self.ids.add(attrs['id'])
        self.urls.extend(attrs[key] for key in ('href', 'src') if key in attrs)
        if tag == 'img':
            self.images.append(attrs)

def main():
    page = Page()
    html = (WEB / 'index.html').read_text(encoding='utf-8')
    page.feed(html)
    assert all(image.get('alt') for image in page.images), 'Missing image alternative text'
    for url in page.urls:
        parsed = urlsplit(url)
        if parsed.scheme or parsed.netloc:
            assert parsed.scheme == 'https', f'Unexpected remote protocol: {url}'
            continue
        if parsed.path in ('', './'):
            if parsed.fragment:
                assert parsed.fragment in page.ids, f'Broken page anchor: {url}'
        elif parsed.path != '../':
            target = (WEB / unquote(parsed.path)).resolve()
            assert target.is_relative_to(WEB), f'Publishing boundary escape: {url}'
            assert target.is_file(), f'Missing local publish asset: {url}'
    code = (WEB / 'content.js').read_text(encoding='utf-8')
    scripts = (WEB / 'app.js').read_text(encoding='utf-8')
    for sha in ('e0cb3b5f2d5d034297ef6080961f217242f01aef', '355a1581d9812065d808ec32ea82f956e8da805b', '4399487d2fb42bce39c7b032fbbb50d230bf4f0b'):
        assert sha in code, f'Missing source version: {sha}'
    assert '原库' in html and '原创扩展' in html, 'Missing provenance context'
    assert '尚未' in html and '许可' in html, 'Missing scope and license context'
    for text in (html, code, scripts):
        assert not re.search(r'file://|[A-Z]:[/\\\\]', text), 'Local machine path in public page'
        assert 'data:image/' not in text, 'Unexpected embedded third-party media'
    ET.parse(ROOT / 'assets' / 'overview.svg')
    subprocess.run([sys.executable, str(ROOT / 'scripts' / 'package_web.py'), '--check'], check=True)
    data = json.loads((ROOT / 'SOURCE.json').read_text(encoding='utf-8'))
    assert len(data['upstream']) == 3 and data['analysis_date'] == '2026-10-22'
    print(f'Verified paths, {len(page.ids)} IDs, image alternatives, 3 fixed sources, provenance and original SVG.')

if __name__ == '__main__':
    main()
