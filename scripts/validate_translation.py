#!/usr/bin/env python3
"""Validate the structure and integrity of the annotated Juan One translation.

This checks coverage and traceability, not the semantic accuracy of English.
Run from any directory with Python 3.10 or later; no external packages needed.
"""
from pathlib import Path
import hashlib
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / 'provenance/translation-juan-01.json'

def sha(text: str) -> str:
    return hashlib.sha256(text.encode('utf-8')).hexdigest()

def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)

def validate() -> dict:
    manifest = json.loads(MANIFEST.read_text(encoding='utf-8'))
    source = (ROOT / manifest['source']).read_text(encoding='utf-8')
    target = ROOT / manifest['translation']
    english = target.read_text(encoding='utf-8')
    require(sha(source) == manifest['source_sha256'], 'Chinese source checksum changed')
    require(sha(english) == manifest['translation_sha256'], 'Translation checksum changed; review and update manifest')
    originals = {}
    source_pages = re.findall(r'<!-- BEGIN SOURCE: eee-(\d+) -->(.*?)<!-- END SOURCE: eee-\1 -->', source, re.S)
    for page, body in source_pages:
        blocks = [p.strip() for p in re.split(r'\n\s*\n', body.strip()) if p.strip() and p.strip() != '---']
        for i, block in enumerate(blocks, 1):
            originals[f'eee-{page}:{i:03d}'] = block
    pairs = re.findall(r'<!-- BEGIN TRANSLATION: (eee-\d+:\d{3}) -->\s*(.*?)\s*<!-- END TRANSLATION: \1 -->', english, re.S)
    ids = [identifier for identifier, _ in pairs]
    require(ids == list(originals), 'Missing, duplicated, reordered, or unmatched source block')
    require(len(pairs) == 443, 'Expected 443 source blocks')
    require(english.count('<!-- BEGIN TRANSLATION:') == len(pairs), 'Unmatched opening marker')
    require(english.count('<!-- END TRANSLATION:') == len(pairs), 'Unmatched closing marker')
    records = manifest['blocks']
    require([r['id'] for r in records] == ids, 'Manifest block order differs')
    roles = [('【本義】', '**Original Meaning.**'), ('【程傳】', "**Cheng's Commentary.**"), ('【集說】', '**Collected Explanations.**'), ('【案】', '**Editorial Judgment.**')]
    for (identifier, translated), record in zip(pairs, records):
        original = originals[identifier]
        require(sha(original) == record['source_sha256'], f'{identifier}: source block changed')
        require(sha(translated) == record['translation_sha256'], f'{identifier}: English block changed')
        require(bool(translated.strip()), f'{identifier}: empty translation')
        for cn_label, en_label in roles:
            if original.startswith(cn_label):
                require(translated.startswith(en_label), f'{identifier}: commentator attribution mismatch')
    main = '\n\n'.join(text for _, text in pairs)
    require(len(re.findall(r'^### ', main, re.M)) == 51, 'Expected all 51 oracle statements')
    require(not re.search(r'\b(?:TODO|TBD|TRANSLATION_PENDING)\b', english), 'Unresolved placeholder')
    refs = re.findall(r'\[\^([^\]]+)\]', main)
    definitions = re.findall(r'^\[\^([^\]]+)\]:', english, re.M)
    require(len(definitions) == len(set(definitions)) == 80, 'Expected 80 unique endnotes')
    require(set(refs) == set(definitions), 'Unresolved or unused endnote')
    image_pattern = r'!\[[^\]]*\]\(([^)]+)\)'
    source_images = re.findall(image_pattern, source)
    english_images = re.findall(image_pattern, main)
    require(english_images == source_images, 'Source image order or identities changed')
    for image in english_images:
        require((target.parent / image).is_file(), f'Missing image: {image}')
    for section in manifest['sections']:
        count = sum(identifier.startswith(f"eee-{section['page']}:") for identifier in ids)
        require(count == section['blocks'], f"Section {section['page']} has wrong block count")
    return {
        'status': 'passed', 'translation': manifest['translation'],
        'translation_sha256': sha(english), 'source_sha256': sha(source),
        **manifest['coverage'], 'local_images': len(english_images),
        'checks': ['Source unchanged', 'All source blocks represented once and in order',
                   'Commentarial role labels aligned', 'All oracle statements present',
                   'All endnote references resolved', 'Source images retained in order',
                   'Block-level and file-level checksums verified'],
        'scope': 'Structural coverage and integrity; not independent bilingual review or full facsimile collation.'
    }

if __name__ == '__main__':
    try:
        print(json.dumps(validate(), ensure_ascii=False, indent=2))
    except (OSError, ValueError, KeyError) as error:
        print(f'Validation failed: {error}', file=sys.stderr)
        sys.exit(1)
