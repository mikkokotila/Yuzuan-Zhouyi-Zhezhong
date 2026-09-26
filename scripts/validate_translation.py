#!/usr/bin/env python3
"""Validate the structure and integrity of the annotated translations.

This checks coverage and traceability, not the semantic accuracy of English.
Run from any directory with Python 3.10 or later; no external packages needed.
"""
from pathlib import Path
import argparse
import hashlib
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[1]

def sha(text: str) -> str:
    return hashlib.sha256(text.encode('utf-8')).hexdigest()

def words(text: str) -> int:
    text = re.sub(r'!\[[^\]]*\]\([^)]*\)|\[\^[^\]]+\]', '', text)
    return len(re.findall(r"\b[A-Za-z]+(?:['’-][A-Za-z]+)*\b", text))

def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)

def appended_summary_number(original: str):
    """Read Zhu Xi's chapter-summary number from the Chinese source."""
    match = re.match(r'^\*\*(?:○\s*)?此第([一二三四五六七八九十]+)章', original)
    if not match:
        return None
    numeral = match.group(1)
    digits = dict(zip('一二三四五六七八九', range(1, 10)))
    if '十' in numeral:
        before, after = numeral.split('十')
        return digits.get(before, 1) * 10 + digits.get(after, 0)
    return digits[numeral]

def primary_source_block(original: str, kind: str) -> bool:
    """Identify primary passages from the Chinese, not from the English manifest."""
    if kind == 'wenyan_commentary':
        return original.startswith('**') and original != '**文言傳**'
    if kind == 'appended_statements':
        return (original.startswith('**') and appended_summary_number(original) is None
                and not re.fullmatch(r'\*\*繫辭[上下]傳\*\*', original)
                and not original.startswith('**御纂周易折中'))
    if kind in {'tuan_commentary', 'image_commentary'}:
        return original.startswith('**') and re.fullmatch(r'\*\*[彖象][上下]傳\*\*', original) is None
    return original.startswith('**') and '，' in original.split('**')[1]

def validate(juan: str = '01') -> dict:
    require(re.fullmatch(r'\d{2}', juan) is not None, 'Juan must have two digits')
    manifest_path = ROOT / f'provenance/translation-juan-{juan}.json'
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    kind = manifest.get('text_kind', 'hexagram_oracles')
    require(kind in {'hexagram_oracles', 'tuan_commentary', 'image_commentary', 'appended_statements', 'wenyan_commentary'}, 'Unsupported translation text kind')
    is_tuan = kind == 'tuan_commentary'
    is_appended = kind == 'appended_statements'
    is_wenyan = kind == 'wenyan_commentary'
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
    require(len(pairs) == manifest['coverage']['source_blocks'], 'Source block total differs from manifest')
    require(english.count('<!-- BEGIN TRANSLATION:') == len(pairs), 'Unmatched opening marker')
    require(english.count('<!-- END TRANSLATION:') == len(pairs), 'Unmatched closing marker')
    records = manifest['blocks']
    require([r['id'] for r in records] == ids, 'Manifest block order differs')
    roles = [('【本義】', '**Original Meaning.**'), ('【程傳】', "**Cheng's Commentary.**"), ('【集說】', '**Collected Explanations.**'), ('【案】', '**Editorial Judgment.**'), ('【總論】', '**General Discussion')]
    for (identifier, translated), record in zip(pairs, records):
        original = originals[identifier]
        require(sha(original) == record['source_sha256'], f'{identifier}: source block changed')
        require(sha(translated) == record['translation_sha256'], f'{identifier}: English block changed')
        require(bool(translated.strip()), f'{identifier}: empty translation')
        require(words(translated) == record['english_words'], f'{identifier}: word count differs')
        is_primary = primary_source_block(original, kind)
        require(translated.startswith('### ') == is_primary, f'{identifier}: primary text alignment differs')
        for cn_label, en_label in roles:
            if original.startswith(cn_label):
                require(translated.startswith(en_label), f'{identifier}: commentator attribution mismatch')
    main = '\n\n'.join(text for _, text in pairs)
    require(sum(words(text) for _, text in pairs) == manifest['coverage']['main_text_english_words'], 'Total word count differs')
    primary_count = sum(primary_source_block(b, kind) for b in originals.values())
    count_key = {'image_commentary':'image_passages', 'tuan_commentary':'tuan_passages', 'appended_statements':'appended_passages', 'wenyan_commentary':'wenyan_passages'}.get(kind, 'oracle_statements')
    require(len(re.findall(r'^### ', main, re.M)) == primary_count == manifest['coverage'][count_key], 'Missing or extra primary passage')
    page_key = 'source_pages' if is_tuan or is_appended or is_wenyan else 'hexagrams'
    require(len(source_pages) == manifest['coverage'][page_key] == len(manifest['sections']), 'Source page count differs')
    require(not re.search(r'\b(?:TODO|TBD|TRANSLATION_PENDING)\b', english), 'Unresolved placeholder')
    refs = re.findall(r'\[\^([^\]]+)\]', main)
    definitions = re.findall(r'^\[\^([^\]]+)\]:', english, re.M)
    require(len(definitions) == len(set(definitions)) == manifest['coverage']['endnotes'], 'Endnote count or uniqueness differs')
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
        section_words = sum(words(text) for identifier, text in pairs if identifier.startswith(f"eee-{section['page']}:"))
        require(section_words == section['english_words'], f"Section {section['page']} word count differs")
    if is_tuan or is_appended:
        chapters = manifest['chapters']
        section_key = 'chapters' if is_appended else 'hexagrams'
        number_key = 'chapter' if is_appended else 'hexagram'
        require(bool(chapters), 'No chapter divisions')
        require(len(chapters) == manifest['coverage'][section_key], 'Section count differs')
        numbers = [c[number_key] for c in chapters]
        require(numbers == list(range(numbers[0], numbers[0] + len(numbers))), 'Sections are not consecutive')
        covered = list(manifest['introductory_blocks'])
        require(covered == ids[:len(covered)], 'Introductory block order differs')
        locations = {identifier: index for index, identifier in enumerate(ids)}
        for chapter in chapters:
            start, end = locations[chapter['start_id']], locations[chapter['end_id']] + 1
            require(start == len(covered) and end > start, 'Gap, overlap, or reversed chapter range')
            chapter_ids = ids[start:end]
            require(len(chapter_ids) == chapter['blocks'], 'Chapter block count differs')
            require(sum(primary_source_block(originals[i], kind) for i in chapter_ids) == chapter[count_key], 'Chapter primary passage count differs')
            require(sum(words(text) for _, text in pairs[start:end]) == chapter['english_words'], 'Chapter word count differs')
            require(english.count(f'<a id="{chapter["anchor"]}"></a>') == 1, 'Missing or duplicated chapter anchor')
            if is_appended:
                summary_id = chapter['summary_id']
                require(summary_id in chapter_ids, 'Summary lies outside its chapter')
                require(appended_summary_number(originals[summary_id]) == chapter['chapter'], 'Chinese chapter-summary number differs')
            covered.extend(chapter_ids)
        closing = list(manifest.get('closing_blocks', []))
        require(closing == ids[len(covered):], 'Closing block order differs')
        covered.extend(closing)
        require(covered == ids, 'Unaccounted source blocks outside chapter divisions')
    if is_appended:
        summary_ids = [i for i in ids if appended_summary_number(originals[i]) is not None]
        require(summary_ids == manifest['summary_blocks'], 'Source chapter summaries differ')
        require(len(summary_ids) == manifest['coverage']['chapter_summaries'] == len(manifest['chapters']), 'Chapter-summary count differs')
        translated_map = dict(pairs)
        require(all(translated_map[i].startswith('**Original Meaning — Chapter Summary.**') for i in summary_ids), 'Chapter summary mislabeled as canonical text')
    if is_wenyan:
        source_summaries = [i for i in ids if re.search(r'此(?:第[一二三四五六]+節|以上申)', originals[i])]
        embedded = [i for i in source_summaries if originals[i].startswith('【本義】')]
        require(source_summaries == manifest['summary_blocks'], 'Wenyan section summaries differ')
        require(embedded == manifest['embedded_summary_blocks'], 'Embedded Wenyan summaries differ')
        require(len(source_summaries) == manifest['coverage']['section_summaries'], 'Wenyan summary count differs')
        translated_map = dict(pairs)
        for identifier in source_summaries:
            expected = '**Section Summary.**' if identifier in embedded else '**Original Meaning — Section Summary.**'
            require(expected in translated_map[identifier], 'Wenyan summary missing its commentary label')
        require([section['hexagram'] for section in manifest['sections']] == [1, 2], 'Wenyan hexagram order differs')
        for section in manifest['sections']:
            prefix = f"eee-{section['page']}:"
            page_ids = [i for i in ids if i.startswith(prefix)]
            actual_primary = [int(i.rsplit(':', 1)[1]) for i in page_ids if primary_source_block(originals[i], kind)]
            require(actual_primary == section['primary_block_numbers'], 'Wenyan primary-block indices differ')
            require(len(actual_primary) == section['wenyan_passages'], 'Wenyan page primary count differs')
            require([i for i in source_summaries if i.startswith(prefix)] == section['summary_ids'], 'Wenyan page summaries differ')
            require(english.count(f'<a id="eee-{section["page"]}"></a>') == 1, 'Wenyan source-page anchor missing or duplicated')
        for identifier in ids:
            if originals[identifier].startswith('【附錄】'):
                require(translated_map[identifier].startswith('**Supplement.**'), 'Source supplement mislabeled')
    primary_check = ('All Wenyan passages and section summaries present and distinguished' if is_wenyan else
                     'All Appended Statements passages, chapter summaries and divisions present and distinguished' if is_appended else
                     'All Great and Small Image passages present and aligned' if kind == 'image_commentary' else
                     'All Tuan passages and hexagram sections present and aligned' if is_tuan else
                     'All oracle statements present and aligned')
    return {
        'status': 'passed', 'translation': manifest['translation'],
        'translation_sha256': sha(english), 'source_sha256': sha(source),
        **manifest['coverage'], 'local_images': len(english_images),
        'checks': ['Source unchanged', 'All source blocks represented once and in order',
                   'Commentarial role labels aligned',
                   primary_check,
                   'All endnote references resolved', 'Source images retained in order',
                   'Block-level and file-level checksums verified', 'Word counts recomputed'],
        'scope': 'Structural coverage and integrity; not independent bilingual review or full facsimile collation.'
    }

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    available = sorted(p.stem.rsplit('-', 1)[-1] for p in (ROOT / 'provenance').glob('translation-juan-[0-9][0-9].json'))
    parser.add_argument('--juan', default='01', choices=available + ['all'], help='Juan to validate (default: 01); use all for every manifest')
    parser.add_argument('--write-report', action='store_true', help='Write validated JSON reports to provenance/')
    args = parser.parse_args()
    try:
        selected = available if args.juan == 'all' else [args.juan]
        reports = [validate(juan) for juan in selected]
        if args.write_report:
            for juan, report in zip(selected, reports):
                path = ROOT / f'provenance/translation-juan-{juan}-validation.json'
                path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        print(json.dumps(reports[0] if len(reports) == 1 else reports, ensure_ascii=False, indent=2))
    except (OSError, ValueError, KeyError) as error:
        print(f'Validation failed: {error}', file=sys.stderr)
        sys.exit(1)
