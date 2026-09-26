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

def shuogua_summary_number(original: str):
    """Accept both bold-marker orders without treating bold bullets as scripture."""
    text = original.replace('**', '').strip()
    text = re.sub(r'^○\s*', '', text)
    return appended_summary_number('**' + text)

def primary_source_block(original: str, kind: str) -> bool:
    """Identify primary passages from the Chinese, not from the English manifest."""
    if kind == 'learning_primer':
        excluded = {'易學啓蒙', '本圖書第一', '原卦畫第二', '淳熙丙午暮春既望', '兩儀生四象', '四象生八卦'}
        return original.startswith('**') and '![' not in original and original.replace('**', '').strip() not in excluded
    if kind == 'sequence_miscellaneous':
        return original.startswith('**') and original not in {'**序卦傳**', '**雜卦傳**'}
    if kind == 'trigram_discussion':
        return (original.startswith('**') and original != '**說卦傳**'
                and not original.startswith('**○**') and shuogua_summary_number(original) is None)
    if kind == 'wenyan_commentary':
        return original.startswith('**') and original != '**文言傳**'
    if kind == 'appended_statements':
        return (original.startswith('**') and appended_summary_number(original) is None
                and not re.fullmatch(r'\*\*繫辭[上下]傳\*\*', original)
                and not original.startswith('**御纂周易折中'))
    if kind in {'tuan_commentary', 'image_commentary'}:
        return original.startswith('**') and re.fullmatch(r'\*\*[彖象][上下]傳\*\*', original) is None
    return original.startswith('**') and '，' in original.split('**')[1]

def primer_canonical_quotation(original: str) -> bool:
    text = re.sub(r'[^\u3400-\u9fff]', '', original)
    prefixes = ('易大傳曰河出圖', '天一地二', '古者包羲氏', '易有太極是生兩儀',
                '天地定位山澤通氣', '雷以動之', '帝出乎震', '乾健也坤順也',
                '乾為馬坤為牛', '乾為首坤為腹', '乾天也故稱乎父')
    return primary_source_block(original, 'learning_primer') and text.startswith(prefixes)

def validate(juan: str = '01') -> dict:
    require(re.fullmatch(r'\d{2}', juan) is not None, 'Juan must have two digits')
    manifest_path = ROOT / f'provenance/translation-juan-{juan}.json'
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    kind = manifest.get('text_kind', 'hexagram_oracles')
    require(kind in {'hexagram_oracles', 'tuan_commentary', 'image_commentary', 'appended_statements', 'wenyan_commentary', 'trigram_discussion', 'sequence_miscellaneous', 'learning_primer'}, 'Unsupported translation text kind')
    is_tuan = kind == 'tuan_commentary'
    is_appended = kind == 'appended_statements'
    is_wenyan = kind == 'wenyan_commentary'
    is_shuogua = kind == 'trigram_discussion'
    is_sequence = kind == 'sequence_miscellaneous'
    is_primer = kind == 'learning_primer'
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
        translated_primary = translated.startswith(('**Primer text', '**Primer quotation', '**Primer Preface')) if is_primer else translated.startswith('### ')
        require(translated_primary == is_primary, f'{identifier}: primary text alignment differs')
        for cn_label, en_label in roles:
            if original.startswith(cn_label):
                require(translated.startswith(en_label), f'{identifier}: commentator attribution mismatch')
    main = '\n\n'.join(text for _, text in pairs)
    require(sum(words(text) for _, text in pairs) == manifest['coverage']['main_text_english_words'], 'Total word count differs')
    primary_count = sum(primary_source_block(b, kind) for b in originals.values())
    count_key = {'image_commentary':'image_passages', 'tuan_commentary':'tuan_passages', 'appended_statements':'appended_passages', 'wenyan_commentary':'wenyan_passages', 'trigram_discussion':'shuogua_passages', 'sequence_miscellaneous':'canonical_passages', 'learning_primer':'primer_passages'}.get(kind, 'oracle_statements')
    translated_primary_count = sum(t.startswith(('**Primer text', '**Primer quotation', '**Primer Preface')) for _, t in pairs) if is_primer else len(re.findall(r'^### ', main, re.M))
    require(translated_primary_count == primary_count == manifest['coverage'][count_key], 'Missing or extra primary passage')
    page_key = 'source_pages' if is_tuan or is_appended or is_wenyan or is_shuogua or is_sequence or is_primer else 'hexagrams'
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
    if is_tuan or is_appended or is_shuogua:
        chapters = manifest['chapters']
        section_key = 'chapters' if is_appended or is_shuogua else 'hexagrams'
        number_key = 'chapter' if is_appended or is_shuogua else 'hexagram'
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
    if is_shuogua:
        actual = [i for i in ids if shuogua_summary_number(originals[i]) is not None]
        require(actual == manifest['summary_blocks'], 'Shuogua source summaries differ')
        require(len(actual) == manifest['coverage']['chapter_summaries'], 'Shuogua summary total differs')
        translated_map = dict(pairs)
        require(all(translated_map[i].startswith('**Original Meaning — Chapter Summary.**') for i in actual), 'Shuogua summary mislabeled')
        supplied = {p['endnote'] for p in manifest['collation']['supplementary_passages']}
        for chapter in manifest['chapters']:
            chapter_ids = ids[locations[chapter['start_id']]:locations[chapter['end_id']]+1]
            expected = [i for i in actual if i in chapter_ids]
            sid = chapter['summary_id']
            if sid is not None:
                require(expected == [sid], 'Shuogua chapter summary coverage differs')
                require(shuogua_summary_number(originals[sid]) == chapter['chapter'], 'Shuogua source chapter number differs')
            else:
                require(not expected, 'Existing source summary incorrectly reported absent')
                evidence = chapter['source_chapter_evidence']
                require(evidence['id'] in chapter_ids and evidence['phrase'] in originals[evidence['id']], 'Unattested Shuogua chapter division')
                require(appended_summary_number('**'+evidence['phrase']) == chapter['chapter'], 'Chapter evidence number differs')
                require(chapter['summary_endnote'] in supplied and chapter['summary_endnote'] in definitions, 'Missing supplementary summary note')
        continuations = manifest['summary_continuation_ids']
        require(len(continuations) == manifest['coverage']['summary_continuation_blocks'], 'Summary continuation count differs')
        require(continuations == [i for c in manifest['chapters'] for i in c.get('summary_continuation_ids', [])], 'Chapter summary continuations differ')
        for identifier in continuations:
            require(ids[locations[identifier]-1] in actual, 'Detached summary continuation')
            require(not primary_source_block(originals[identifier], kind), 'Summary continuation marked canonical')
            require(translated_map[identifier].startswith('**Original Meaning — Chapter Summary, continued.**'), 'Summary continuation mislabeled')
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
    if is_sequence:
        require(manifest['coverage']['wings'] == len(source_pages) == 2, 'Expected both Sequence and Miscellaneous Wings')
        require([s['source_title'] for s in manifest['sections']] == ['序卦傳', '雜卦傳'], 'Wing order differs')
        totals = []
        for section in manifest['sections']:
            page_ids = [i for i in ids if i.startswith(f"eee-{section['page']}:")]
            require(page_ids[0] == section['start_id'] and page_ids[-1] == section['end_id'], 'Wing range differs')
            require(originals[page_ids[0]] == '**'+section['source_title']+'**', 'Chinese Wing heading differs')
            selected = [int(i.rsplit(':',1)[1]) for i in page_ids if primary_source_block(originals[i], kind)]
            require(selected == section['primary_block_numbers'], 'Wing primary-block indices differ')
            require(len(selected) == section['canonical_passages'], 'Wing primary passage count differs')
            for anchor in (section['anchor'], 'eee-'+section['page']):
                require(english.count(f'<a id="{anchor}"></a>') == 1, 'Wing anchor missing or duplicated')
            totals.append(len(selected))
        require(totals == [manifest['coverage']['sequence_passages'], manifest['coverage']['miscellaneous_passages']], 'Wing totals differ')
        require(sum(totals) == manifest['coverage']['canonical_passages'], 'Combined primary total differs')
        locations = {identifier:index for index,identifier in enumerate(ids)}
        covered = []
        for division in manifest['reading_divisions']:
            start,end = locations[division['start_id']],locations[division['end_id']]+1
            require(start == len(covered) and end > start, 'Gap or overlap in reading divisions')
            selected = ids[start:end]
            require(len(selected) == division['blocks'], 'Reading division block total differs')
            require(sum(primary_source_block(originals[i],kind) for i in selected) == division['canonical_passages'], 'Reading division primary total differs')
            require(sum(words(t) for _,t in pairs[start:end]) == division['english_words'], 'Reading division word total differs')
            require(english.count(f'<a id="{division["anchor"]}"></a>') == 1, 'Reading division anchor missing or duplicated')
            covered.extend(selected)
        require(covered == ids, 'Unaccounted blocks outside reading divisions')
    if is_primer:
        translated_map = dict(pairs)
        require(not re.search(r'^### ', main, re.M), 'Primer mislabeled as new canonical passages')
        require('⟦PARA⟧' not in english, 'Unexpanded paragraph marker')
        require([i for i in ids if primary_source_block(originals[i], kind)] == manifest['primer_block_ids'], 'Primer body coverage differs')
        canonical = [i for i in ids if primer_canonical_quotation(originals[i])]
        require(canonical == manifest['canonical_quotation_ids'], 'Canonical quotation coverage differs')
        require(len(canonical) == manifest['coverage']['canonical_quotation_blocks'], 'Canonical quotation count differs')
        require(all(translated_map[i].startswith('**Primer quotation') for i in canonical), 'Canonical citation missing quotation label')
        gloss_prefixes = ('曆法合二始', '州有九井', '以横圖觀之', '震始交陰而陽生，是說', '兌離以下更思之', '○\u3000今按，兌離', '此更宜思', '此言文王改易', '嘗考此圖而更為之說')
        glosses = [i for i in ids if originals[i].startswith(gloss_prefixes)]
        require(glosses == manifest['primer_gloss_ids'] and len(glosses) == manifest['coverage']['primer_gloss_blocks'], 'Primer gloss coverage differs')
        require(all(translated_map[i].startswith('**Primer gloss') for i in glosses), 'Primer gloss misattributed')
        diagram_ids = [i for i in ids if re.search(image_pattern, originals[i])]
        require(diagram_ids == manifest['diagram_block_ids'] and len(diagram_ids) == manifest['coverage']['diagram_blocks'], 'Diagram blocks differ')
        require(len(english_images) == manifest['coverage']['diagram_images'] == len(manifest['source_images']), 'Diagram image count differs')
        for image, item in zip(english_images, manifest['source_images']):
            require(image == item['path'], 'Diagram manifest order differs')
            require(hashlib.sha256((target.parent/image).read_bytes()).hexdigest() == item['sha256'], 'Diagram bytes changed')
        caption_texts = {'易有太極', '是生兩儀', '兩儀生四象', '四象生八卦'}
        captions = [i for i in ids if re.sub(image_pattern, '', originals[i]).replace('**', '').strip() in caption_texts]
        require(captions == manifest['diagram_caption_ids'] and len(captions) == manifest['coverage']['diagram_caption_blocks'], 'Diagram captions differ')
        require(all('**Diagram caption.**' in translated_map[i] for i in captions), 'Diagram caption not translated')
        title_texts = ['易學啓蒙', '本圖書第一', '原卦畫第二']
        titles = [i for i in ids if originals[i].replace('**', '') in title_texts]
        require(titles == manifest['title_ids'], 'Primer source titles differ')
        require([originals[i].replace('**', '') for i in titles] == title_texts, 'Primer part order differs')
        require(manifest['coverage']['parts'] == 2 and manifest['embedded_preface_included'], 'Primer scope differs')
        date_id = manifest['date_id']
        require(originals[date_id] == '**淳熙丙午暮春既望**' and translated_map[date_id].startswith('**Date.**'), 'Primer date omitted or mislabeled')
        locations = {identifier:index for index,identifier in enumerate(ids)}
        covered = []
        for division in manifest['reading_divisions']:
            start,end = locations[division['start_id']],locations[division['end_id']]+1
            require(start == len(covered) and end > start, 'Primer reading division gap or overlap')
            selected = ids[start:end]
            require(len(selected) == division['blocks'], 'Primer division block count differs')
            require(sum(primary_source_block(originals[i], kind) for i in selected) == division['primer_passages'], 'Primer division passage count differs')
            require(sum(words(translated_map[i]) for i in selected) == division['english_words'], 'Primer division word count differs')
            require(english.count(f'<a id="{division["anchor"]}"></a>') == 1, 'Primer navigation anchor missing or duplicated')
            covered.extend(selected)
        require(covered == ids, 'Unaccounted primer blocks')
        require(all(english.count(f'<a id="eee-{page}"></a>') == 1 for page,_ in source_pages), 'Primer page anchor missing')
        for i in ids:
            if originals[i].startswith('【附錄】'):
                require(translated_map[i].startswith('**Supplement.**'), 'Source supplement mislabeled')
    primary_check = ('All primer passages, embedded quotations, glosses, titles, captions and diagrams present and distinguished' if is_primer else
                     'All Sequence and Miscellaneous passages present; both Wings, source headings and reading divisions aligned' if is_sequence else
                     'All Shuogua passages and eleven chapter divisions present; source summaries distinguished from the supplementary summary' if is_shuogua else
                     'All Wenyan passages and section summaries present and distinguished' if is_wenyan else
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
