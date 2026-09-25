#!/usr/bin/env python3
"""Validate the committed source corpus and its assets without network access."""
import argparse
import gzip
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
import markdown
from bs4 import BeautifulSoup
ROOT = Path(__file__).resolve().parents[1]
def sha(data):
    return hashlib.sha256(data if isinstance(data, bytes) else data.encode('utf-8')).hexdigest()
def text_of(html):
    return re.sub(r'\s+', '', BeautifulSoup(html, 'html.parser').get_text())
def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write-report', action='store_true')
    args = parser.parse_args()
    manifest = json.loads((ROOT / 'provenance/manifest.json').read_text())
    raw = (ROOT / 'provenance/edition-snapshot.json.gz').read_bytes()
    assert sha(raw) == manifest['snapshot_sha256'], 'Snapshot checksum mismatch'
    snapshot = json.loads(gzip.decompress(raw))
    pages = {p['id']:p for p in snapshot['pages']}
    records = {p['id']:p for p in manifest['pages']}
    assets = {a['url']:a for a in manifest['assets']}
    expected_files = {'source/front-matter.md'} | {f'source/juan-{n:02d}.md' for n in range(23)}
    assert {f['path'] for f in manifest['files']} == expected_files
    assert {'source/' + p.name for p in (ROOT/'source').glob('*.md')} == expected_files
    nav = {p['id']:p for p in snapshot['excluded_navigation_pages']}
    expected_pages = (set(nav['4531']['children']) | set(nav['4639']['children']) |
                      {str(n) for n in range(4713,4718)}) - {'4639'}
    assert set(pages) == expected_pages == set(records), 'Book-tree coverage mismatch'
    assert sum(len(snapshot['groups'][f'{n:02d}']) for n in range(1,9)) == 64
    assert len(snapshot['groups']['11']) + len(snapshot['groups']['12']) == 64
    seen = []
    for item in manifest['files']:
        data = (ROOT/item['path']).read_bytes()
        assert sha(data) == item['sha256'], f"Changed file: {item['path']}"
        doc = data.decode('utf-8')
        blocks = re.findall(r'<!-- BEGIN SOURCE: eee-(\d+) -->\n(.*?)\n<!-- END SOURCE: eee-\1 -->',
                            doc, flags=re.S)
        assert [node_id for node_id, body in blocks] == item['page_ids']
        for node_id, body in blocks:
            seen.append(node_id)
            page = pages[node_id]
            record = records[node_id]
            original = BeautifulSoup(page['content_html'], 'html.parser')
            rendered = BeautifulSoup(markdown.markdown(body, extensions=['tables']), 'html.parser')
            actual = text_of(str(rendered))
            assert actual == text_of(page['content_html']), f'Text mismatch: {node_id}'
            assert sha(actual) == record['text_sha256']
            assert len(actual) == record['nonspace_characters']
            assert '\ufffd' not in actual, f'Replacement character: {node_id}'
            expected_images = ['../' + assets[i['src']]['path'] for i in original.select('img[src]')]
            actual_images = [i['src'] for i in rendered.select('img[src]')]
            assert actual_images == expected_images, f'Image order/content mismatch: {node_id}'
            assert len(original.select('table')) == len(rendered.select('table'))
            for src in actual_images:
                assert (ROOT/item['path']).parent.joinpath(src).is_file(), src
    assert len(seen) == len(set(seen)) == len(pages), 'Duplicate or missing source page'
    for asset in manifest['assets']:
        data = (ROOT/asset['path']).read_bytes()
        assert len(data) == asset['bytes'] and sha(data) == asset['sha256'], asset['path']
    report = {'status': 'passed', 'checked_at': datetime.now(timezone.utc).isoformat(),
              'numbered_juans': 22, 'preliminary_juan': 1, 'front_matter_files': 1,
              'markdown_files': len(manifest['files']), 'source_pages': len(pages),
              'distinct_images': len(assets),
              'nonspace_characters': sum(p['nonspace_characters'] for p in records.values()),
              'han_characters': sum(p['han_characters'] for p in records.values()),
              'image_occurrences': sum(p['image_occurrences'] for p in records.values()),
              'snapshot_sha256': manifest['snapshot_sha256'],
              'checks': ['All content pages assigned exactly once', 'All 23 juans present',
                         'All front matter retained', 'Text matches archived HTML after rendering',
                         'Image order and local targets preserved', 'File and asset SHA-256 checksums'],
              'scope': 'Complete capture of the selected web transcription, not a critical collation.'}
    if args.write_report:
        (ROOT/'provenance/validation.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps(report, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
