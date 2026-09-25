#!/usr/bin/env python3
"""Fetch the selected edition's book tree, using an on-disk cache."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.parse import urljoin
import hashlib
import json
import re
import time
import requests
from bs4 import BeautifulSoup
ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://www.eee-learning.com'
CACHE = ROOT / '.cache'
CACHE.mkdir(exist_ok=True)

def fetch(node_id):
    path = CACHE / f'eee-{node_id}.html'
    url = BASE + ('/article/' if node_id == '4531' else '/book/') + node_id
    if not path.exists():
        for attempt in range(4):
            try:
                response = requests.get(url, timeout=60)
                response.raise_for_status()
                assert 'text/html' in response.headers.get('Content-Type', '')
                path.write_bytes(response.content)
                time.sleep(0.25)
                break
            except (requests.RequestException, AssertionError):
                if attempt == 3:
                    raise
                time.sleep(2 ** attempt)
    raw = path.read_bytes()
    soup = BeautifulSoup(raw.decode('utf-8'), 'html.parser')
    title = soup.select_one('h1').get_text(' ', strip=True)
    children = list(dict.fromkeys(
        a['href'].split('/')[-1]
        for a in soup.select('nav.book-navigation ul.menu a[href]')
        if re.fullmatch(r'/book/\d+', a['href'])))
    body = soup.select_one('article.node--type-book .field--name-body')
    text = body.get_text(' ', strip=True) if body else ''
    return {'id': node_id, 'url': url, 'title': title,
            'children': children, 'html_sha256': hashlib.sha256(raw).hexdigest(),
            'text_characters': len(text),
            'volume_markers': re.findall(r'御纂周易折中卷[一二三四五六七八九十首]+', text),
            'image_count': len(body.select('img')) if body else 0}

def main():
    records = {'4531': fetch('4531')}
    pending = records['4531']['children']
    while pending:
        with ThreadPoolExecutor(max_workers=3) as pool:
            for item in pool.map(fetch, pending):
                records[item['id']] = item
                print(item['id'], item['title'], item['text_characters'], flush=True)
        pending = list(dict.fromkeys(c for r in records.values()
                                     for c in r['children'] if c not in records))
    (CACHE / 'tree.json').write_text(json.dumps(records, ensure_ascii=False, indent=2))
    print('TOTAL:', len(records), 'pages including the modern book index', flush=True)

if __name__ == '__main__':
    main()
