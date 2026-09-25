#!/usr/bin/env python3
"""Capture the selected source once; rebuild its Markdown offline thereafter."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin, urlparse, unquote
import argparse
import copy
import gzip
import hashlib
import json
import re
import time
import requests
import markdown
from bs4 import BeautifulSoup
from markdownify import MarkdownConverter
ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = ROOT / 'provenance/edition-snapshot.json.gz'
BASE = 'https://www.eee-learning.com'
NUMERALS = ['首','一','二','三','四','五','六','七','八','九','十','十一',
            '十二','十三','十四','十五','十六','十七','十八','十九','二十','二十一','二十二']
def digest(data):
    return hashlib.sha256(data if isinstance(data, bytes) else data.encode('utf-8')).hexdigest()
def compact(text):
    return re.sub(r'\s+', '', text)
def html_text(html):
    return compact(BeautifulSoup(html, 'html.parser').get_text())
def clean_body(raw, page_url=BASE):
    soup = BeautifulSoup(raw.decode('utf-8'), 'html.parser')
    body = soup.select_one('article.node--type-book .field--name-body')
    if body is None:
        raise ValueError('Missing book body')
    scans = [urljoin(BASE, a['href']) for a in body.select('a.colorbox[href]')]
    removed = []
    for p in list(body.find_all('p')):
        scan_nav = bool(p.select('a.colorbox'))
        arrows = p.select('img[src*="arrow3_right"]')
        book_links = p.select('a[href^="/book/"]')
        remainder = copy.deepcopy(p)
        for item in remainder.select('a, img'):
            item.decompose()
        link_nav = arrows and book_links and not re.sub(r'[\s,，|/]+', '', remainder.get_text())
        if scan_nav or link_nav:
            removed.append({'kind': 'scan-navigation' if scan_nav else 'cross-navigation',
                            'text': p.get_text(' ', strip=True)})
            p.decompose()
    for item in list(body.select('script, style, iframe, img[src*="arrow3_right"]')):
        item.decompose()
    for tag in body.find_all(True):
        for attr in list(tag.attrs):
            if attr.startswith('on') or attr in ('class', 'style'):
                del tag.attrs[attr]
        for attr in ('src', 'href'):
            if tag.get(attr):
                tag[attr] = urljoin(page_url, tag[attr])
    return str(body), scans, removed
def volume_groups(tree):
    groups = {'front-matter': [str(n) for n in range(4532, 4538)],
              '00': [str(n) for n in range(4538, 4542)]}
    groups.update({f'{n:02d}': [] for n in range(1, 23)})
    ends = [7, 14, 22, 30, 39, 47, 55, 64]
    for node_id in tree['4531']['children']:
        match = re.match(r'【折中】(\d+)\.', tree[node_id]['title'])
        if match:
            number = int(match[1])
            juan = next(n for n, end in enumerate(ends, 1) if number <= end)
            groups[f'{juan:02d}'].append(node_id)
    groups['09'] = ['4637']
    groups['10'] = ['4638']
    groups['11'] = [str(n) for n in range(4640, 4670)]
    groups['12'] = [str(n) for n in range(4670, 4704)]
    fixed = {13:[4704], 14:[4705], 15:[4706], 16:[4707,4708],
             17:[4709], 18:[4710,4711], 19:[4712,4713,4714],
             20:[4715,4716,4717], 21:[4718], 22:[4719]}
    groups.update({f'{n:02d}': list(map(str, ids)) for n, ids in fixed.items()})
    assigned = [n for ids in groups.values() for n in ids]
    assert len(assigned) == len(set(assigned)), 'Duplicate page assignment'
    assert set(assigned) == set(tree) - {'4531','4639'}, 'Unassigned book pages'
    assert all(groups.values()), 'Empty juan'
    return groups

class Converter(MarkdownConverter):
    def convert_p(self, el, text, parent_tags):
        result = super().convert_p(el, text, parent_tags)
        return re.sub(r'(?m)^([ \t]*\d+)\.([ \t]+)', r'\1\\.\2', result)

    def convert_table(self, el, text, parent_tags):
        return '\n\n' + str(el) + '\n\n'
def capture():
    tree = json.loads((ROOT / '.cache/tree.json').read_text())
    groups = volume_groups(tree)
    pages = []
    for volume, ids in groups.items():
        for node_id in ids:
            path = ROOT / f'.cache/eee-{node_id}.html'
            raw = path.read_bytes()
            html, scans, removed = clean_body(raw, tree[node_id]['url'])
            record = {k: tree[node_id][k] for k in ('id','url','title','html_sha256')}
            record.update(volume=volume, content_html=html,
                          scan_urls=scans, removed_navigation=removed,
                          retrieved_at=datetime.fromtimestamp(path.stat().st_mtime,
                                       timezone.utc).isoformat())
            pages.append(record)
    snapshot = {'edition': '易學網《御纂周易折中》', 'index_url': BASE + '/article/4531',
                'groups': groups, 'pages': pages,
                'excluded_navigation_pages': [tree['4531'], tree['4639']]}
    data = json.dumps(snapshot, ensure_ascii=False, indent=2).encode('utf-8')
    SNAPSHOT.write_bytes(gzip.compress(data, mtime=0))
    return snapshot

def asset_path(url):
    name = re.sub(r'[^A-Za-z0-9._-]', '_', unquote(urlparse(url).path.rsplit('/',1)[-1]))
    return 'assets/eee-learning/' + digest(url)[:12] + '-' + name

def get_asset(url, online):
    relative = asset_path(url)
    path = ROOT / relative
    if not path.exists():
        if not online:
            raise FileNotFoundError(f'Missing archived asset: {relative}')
        assert urlparse(url).hostname in ('www.eee-learning.com', 'eee-learning.com')
        for attempt in range(4):
            try:
                response = requests.get(url, timeout=60)
                response.raise_for_status()
                assert response.headers.get('Content-Type','').startswith('image/'), url
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(response.content)
                time.sleep(0.15)
                break
            except (requests.RequestException, AssertionError):
                if attempt == 3:
                    raise
                time.sleep(2 ** attempt)
    data = path.read_bytes()
    assert len(data) > 20, f'Empty image: {url}'
    return {'url': url, 'path': relative, 'sha256': digest(data), 'bytes': len(data)}

def convert_page(page):
    body = BeautifulSoup(page['content_html'], 'html.parser')
    expected = html_text(str(body))
    for image in body.select('img[src]'):
        image['src'] = '../' + asset_path(image['src'])
    # Flatten redundant nested bold tags; otherwise Markdown emphasis can break.
    for tag in list(body.find_all(['strong', 'b'])):
        if tag.find_parent(['strong', 'b']):
            tag.unwrap()
    converter = Converter(heading_style='ATX', bullets='-',
                          keep_inline_images_in=['p','div','span','strong','h1','h2','h3','td','th'])
    text = converter.convert(str(body)).strip() + '\n'
    rendered = markdown.markdown(text, extensions=['tables'])
    actual = html_text(rendered)
    if actual != expected:
        offset = next((i for i, (a,b) in enumerate(zip(expected, actual)) if a != b),
                      min(len(expected), len(actual)))
        raise ValueError(f"Text mismatch in {page['id']} at {offset}: "
                         f"{expected[max(0,offset-40):offset+100]!r} != "
                         f"{actual[max(0,offset-40):offset+100]!r}")
    rendered_soup = BeautifulSoup(rendered, 'html.parser')
    assert len(body.select('img')) == len(rendered_soup.select('img')), page['id']
    assert len(body.select('table')) == len(rendered_soup.select('table')), page['id']
    assert '\ufffd' not in expected, f"Replacement character in {page['id']}"
    stats = {'text_sha256': digest(expected), 'nonspace_characters': len(expected),
             'han_characters': len(re.findall(r'[\u3400-\u9fff\U00020000-\U000323af]', expected)),
             'image_occurrences': len(body.select('img')),
             'tables': len(body.select('table')), 'conversion_text_match': True}
    return text, stats

def build(snapshot, online=False):
    pages = {p['id']: p for p in snapshot['pages']}
    urls = sorted({img['src'] for page in pages.values()
                   for img in BeautifulSoup(page['content_html'], 'html.parser').select('img[src]')})
    with ThreadPoolExecutor(max_workers=3) as pool:
        assets = list(pool.map(lambda url: get_asset(url, online), urls))
    print('Archived image files:', len(assets), flush=True)
    manifest = {'edition': snapshot['edition'], 'index_url': snapshot['index_url'],
                'snapshot_sha256': digest(SNAPSHOT.read_bytes()),
                'files': [], 'pages': [], 'assets': assets}
    for volume, ids in snapshot['groups'].items():
        filename = 'front-matter.md' if volume == 'front-matter' else f'juan-{volume}.md'
        title = '御纂周易折中 卷前' if volume == 'front-matter' else '御纂周易折中 卷' + NUMERALS[int(volume)]
        relative = 'source/' + filename
        chunks = ['---', 'title: ' + json.dumps(title, ensure_ascii=False),
                  'juan: ' + json.dumps(volume), 'language: lzh-Hant',
                  'edition: 易學網《御纂周易折中》',
                  'provenance: ../provenance/manifest.json', '---', '', '# ' + title, '']
        file_stats = dict(nonspace_characters=0, han_characters=0, image_occurrences=0, tables=0)
        for node_id in ids:
            page = pages[node_id]
            text, stats = convert_page(page)
            chunks.extend([f'<a id="eee-{node_id}"></a>', '', '## ' + page['title'], '',
                           '<!-- Source: ' + page['url'] + ' -->',
                           f'<!-- BEGIN SOURCE: eee-{node_id} -->', text.rstrip(),
                           f'<!-- END SOURCE: eee-{node_id} -->', ''])
            record = {k:v for k,v in page.items() if k != 'content_html'}
            record.update(stats, output_file=relative)
            manifest['pages'].append(record)
            for key in file_stats:
                file_stats[key] += stats[key]
        data = ('\n'.join(chunks).rstrip() + '\n').encode('utf-8')
        (ROOT / relative).write_bytes(data)
        manifest['files'].append(dict(path=relative, title=title, volume=volume,
                                     page_ids=ids, sha256=digest(data), bytes=len(data), **file_stats))
        print(filename, file_stats['nonspace_characters'], 'characters', flush=True)
    (ROOT / 'provenance/manifest.json').write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    lines = ['# Source coverage', '',
             'Counts exclude repository headings and metadata; image-only text is not counted.', '',
             '| File | Source pages | Non-whitespace characters | Han characters | Image occurrences |',
             '| --- | ---: | ---: | ---: | ---: |']
    for item in manifest['files']:
        lines.append(f"| [{item['title']}](../{item['path']}) | {len(item['page_ids'])} | "
                     f"{item['nonspace_characters']:,} | {item['han_characters']:,} | {item['image_occurrences']:,} |")
    totals = {key: sum(f[key] for f in manifest['files']) for key in
              ('nonspace_characters','han_characters','image_occurrences','tables')}
    lines += ['', f"Total: {len(manifest['files'])} Markdown files, {len(pages)} source pages, "
              f"{totals['nonspace_characters']:,} non-whitespace characters, "
              f"{len(assets)} distinct image files, {totals['image_occurrences']:,} image occurrences.", '',
              'Every captured source page passed a Markdown-to-HTML round-trip comparison of its',
              'complete non-whitespace text, image count, and table count. This verifies conversion',
              'coverage, not the philological accuracy of the website transcription.', '']
    (ROOT / 'provenance/coverage.md').write_text('\n'.join(lines), encoding='utf-8')
    print('TOTALS:', totals, flush=True)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--capture', action='store_true',
                        help='Capture downloaded HTML and fetch missing images; overwrites source files.')
    args = parser.parse_args()
    snapshot = capture() if args.capture else json.loads(gzip.decompress(SNAPSHOT.read_bytes()))
    build(snapshot, online=args.capture)

if __name__ == '__main__':
    main()
