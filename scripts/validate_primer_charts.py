"""Source-bound checks for the primer's casting rules and transformation charts.

Called by validate_translation.py. Uses the standard library only; validates
structure, documented image corrections and arithmetic, not scholarly accuracy.
"""
from pathlib import Path
from itertools import combinations, product
from collections import Counter
import hashlib
import re

CN_NAMES = '乾 坤 屯 蒙 需 訟 師 比 小畜 履 泰 否 同人 大有 謙 豫 隨 蠱 臨 觀 噬嗑 賁 剝 復 无妄 大畜 頤 大過 坎 離 咸 恒 遯 大壯 晉 明夷 家人 睽 蹇 解 損 益 夬 姤 萃 升 困 井 革 鼎 震 艮 漸 歸妹 豐 旅 巽 兌 渙 節 中孚 小過 既濟 未濟'.split()
EN_NAMES = 'Qian|Kun|Difficulty at the Beginning|Unformed Understanding|Waiting|Contention|The Army|Holding Together|Small Restraint|Treading|Peace|Obstruction|Fellowship|Great Possession|Modesty|Enthusiasm|Following|Decay|Approach|Viewing|Biting Through|Adornment|Splitting Apart|Return|Without Falsity|Great Restraint|Nourishment|Great Excess|Repeated Danger|Clinging|Influence|Constancy|Retreat|Great Strength|Advance|Darkening of the Light|The Family|Opposition|Limping|Release|Decrease|Increase|Breakthrough|Coming to Meet|Gathering|Pushing Upward|Oppression|The Well|Revolution|The Cauldron|Shock|Keeping Still|Gradual Progress|The Marrying Maiden|Abundance|The Wanderer|Penetration|Joy|Dispersion|Limitation|Inner Sincerity|Small Excess|After Completion|Before Completion'.split('|')
TRIGRAMS = {'乾':(1,1,1), '坤':(0,0,0), '震':(1,0,0), '巽':(0,1,1), '坎':(0,1,0), '離':(1,0,1), '艮':(0,0,1), '兌':(1,1,0)}
PAIRS = '乾乾 坤坤 震坎 坎艮 乾坎 坎乾 坎坤 坤坎 乾巽 兌乾 乾坤 坤乾 離乾 乾離 艮坤 坤震 震兌 巽艮 兌坤 坤巽 震離 離艮 坤艮 震坤 震乾 乾艮 震艮 巽兌 坎坎 離離 艮兌 巽震 艮乾 乾震 坤離 離坤 離巽 兌離 艮坎 坎震 兌艮 震巽 乾兌 巽乾 坤兌 巽坤 坎兌 巽坎 離兌 巽離 震震 艮艮 艮巽 兌震 離震 艮離 巽巽 兌兌 坎巽 兌坎 兌巽 艮震 離坎 坎離'.split()
HEXAGRAMS = {i: TRIGRAMS[p[0]] + TRIGRAMS[p[1]] for i,p in enumerate(PAIRS,1)}
INVERSE = {v:k for k,v in HEXAGRAMS.items()}
NUMBERS = {n:i for i,n in enumerate(CN_NAMES,1)}
MASKS = [c for k in range(7) for c in combinations(range(6),k)]
IMAGE = r'!\[[^\]]*\]\(([^)]+)\)'
SOURCE_ENTRY = re.compile(r'!\[[^\]]*\]\(([^)]+)\)([^!]+)')
ENGLISH_ENTRY = re.compile(r'\*\*(\d+)\.\*\* !\[([^\]]+)\]\(([^)]+)\) ([^\n]*?) \((\d+)\)')

def require(ok, message):
    if not ok:
        raise ValueError(message)

def chinese(text):
    return re.sub(r'[^\u3400-\u9fff]', '', text)

def primary(original):
    excluded = {'明蓍策第三', '考變占第四', '【集說】'}
    text = original.replace('**','').strip()
    return original.startswith('**') and '![' not in original and text not in excluded and not text.startswith('卷內蔡氏說')

def canonical(original):
    prefixes = ('分而為二以象兩',
                '乾之策二百一十有六坤之策', '二篇之策萬有一千五百二十當',
                '是故四營而成易', '顯道神德行', '乾卦用九')
    return primary(original) and (chinese(original) in {'大衍之數五十','其用四十有九'} or chinese(original).startswith(prefixes))

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def validate_images(manifest, originals, translated, target, definitions):
    records = manifest['collation']['image_corrections']
    changes = {(r['id'],r['slot']):r for r in records}
    require(len(records) == len(changes) == 12, 'Expected twelve documented image corrections')
    used, expected, actual = set(), [], []
    assets = {r['path']:r['sha256'] for r in manifest['image_assets']}
    for identifier, original in originals.items():
        old = re.findall(IMAGE,original)
        new = re.findall(IMAGE,translated[identifier])
        require(len(old) == len(new), f'{identifier}: image positions lost or added')
        for slot,(before,after) in enumerate(zip(old,new),1):
            key = (identifier,slot)
            if key in changes:
                record = changes[key]; used.add(key)
                require(before == record['path'] and after == record['english_path'], f'{identifier}: unrecorded image substitution')
                note = record['endnote']
                require(note in definitions and '[^'+note+']' in translated[identifier], 'Image correction lacks a linked endnote')
                require(record['source_image_sha256'] == assets[before] and record['translation_image_sha256'] == assets[after], 'Correction image hashes differ')
            else:
                require(before == after, f'{identifier}: undocumented image change')
            expected.append(record['english_path'] if key in changes else before)
            actual.append(after)
    require(used == set(changes) and expected == actual, 'Image correction coverage or order differs')
    require(set(assets) == set(re.findall(IMAGE,'\n'.join(originals.values()))) | set(actual), 'Image asset inventory differs')
    for path, expected_hash in assets.items():
        require((target.parent/path).is_file() and digest(target.parent/path) == expected_hash, 'Image bytes missing or changed: '+path)
    require(len(actual) == manifest['coverage']['diagram_images'] == 2056, 'Image total differs')
    return actual

def transformed(number):
    return [INVERSE[tuple(1-b if i in mask else b for i,b in enumerate(HEXAGRAMS[number]))] for mask in MASKS]

def arithmetic():
    regular, once, counterfactual = Counter(), Counter(), Counter()
    for a,b,c in product(range(1,5),repeat=3):
        first = 5 if a < 4 else 9
        later = [4 if r < 3 else 8 for r in (b,c)]
        regular[(49-first-sum(later))//4] += 1
        once[(49-first-sum(4 if r < 4 else 8 for r in (b,c)))//4] += 1
        counterfactual[(48-sum(4 if r < 3 else 8 for r in (a,b,c)))//4] += 1
    require(dict(regular) == {9:12,8:28,7:20,6:4}, 'Three-hanging arithmetic failed')
    require(dict(once) == {9:27,8:27,7:9,6:1}, 'Once-hanging arithmetic failed')
    require(dict(counterfactual) == {9:8,8:24,7:24,6:8}, 'Forty-eight-working-stalk arithmetic failed')
    require(192*36 + 192*24 == 192*28 + 192*32 == 11520, 'Combined stalk totals failed')
    require(6*36 + 6*24 == 6*28 + 6*32 == 360, 'Year totals failed')
    return {'three_hangings':{str(k):v for k,v in sorted(regular.items())}, 'first_round_only':{str(k):v for k,v in sorted(once.items())}, 'forty_eight_working_stalks':{str(k):v for k,v in sorted(counterfactual.items())}, 'six_line_choice_counts':[sum(len(m)==k for m in MASKS) for k in range(7)], 'combined_stalk_total':11520, 'year_total':360, 'scope':'Formal remainder-class and line-combination arithmetic; not empirical casting probabilities or proof of divinatory efficacy.'}

def validate(manifest, originals, pairs, english, words):
    ids = list(originals); translated = dict(pairs); coverage = manifest['coverage']
    require([i for i in ids if primary(originals[i])] == manifest['primer_block_ids'], 'Primer passage IDs differ')
    require([i for i in ids if canonical(originals[i])] == manifest['canonical_quotation_ids'], 'Canonical quotation IDs differ')
    require(len(manifest['canonical_quotation_ids']) == coverage['canonical_quotation_blocks'] == 8, 'Canonical quotation count differs')
    require(all(translated[i].startswith('**Primer quotation') for i in manifest['canonical_quotation_ids']), 'Canonical quotation mislabeled')
    require([originals[i].replace('**','') for i in manifest['title_ids']] == ['明蓍策第三','考變占第四'], 'Primer part titles differ')
    require(coverage['parts'] == 2 and manifest['part_numbers'] == [3,4], 'Primer part scope differs')
    require(manifest['embedded_preface_included'] is False, 'Unexpected preface claim')
    gloss_starts = ('五除掛一','九除掛一','不去掛一','掛扐除一','愚案此說','彖辭為卦下','經傳無文','凡三爻變者','經傳亦無文','穆姜往東宮','蔡墨曰','凡言初終上下')
    glosses = [i for i in ids if chinese(originals[i]).startswith(gloss_starts)]
    require(glosses == manifest['primer_gloss_ids'] and len(glosses) == coverage['primer_gloss_blocks'], 'Primer gloss inventory differs')
    require(all(translated[i].startswith('**Primer gloss') for i in glosses), 'Primer gloss mislabeled')
    notes = [i for i in ids if chinese(originals[i]).startswith('卷內蔡氏說')]
    require(notes == manifest['source_note_ids'] and all(translated[i].startswith('**Source note.**') for i in notes), 'Source closing note mislabeled')
    for i in ids:
        if originals[i].replace('**','').startswith('【集說】'):
            require(translated[i].startswith('**Collected Explanations.**'), 'Collected Explanations heading mislabeled')
    rules = [('凡卦六爻皆不變',0),('一爻變',1),('二爻變',2),('三爻變',3),('四爻變',4),('五爻變',5),('六爻變',6)]
    found = [(i,n) for i in ids for prefix,n in rules if primary(originals[i]) and chinese(originals[i]).startswith(prefix)]
    require(found == [(r['id'],r['changing_lines']) for r in manifest['changing_line_rules']], 'Changing-line rule inventory differs')
    require([n for i,n in found] == list(range(7)), 'Not all seven changing-line cases are present')
    diagram_ids = [i for i in ids if re.search(IMAGE,originals[i])]
    require(diagram_ids == manifest['diagram_block_ids'] and len(diagram_ids) == coverage['diagram_blocks'], 'Diagram block count differs')
    require(not re.search(r'^### ',english,re.M) and '⟦PARA⟧' not in english, 'Incorrect heading or paragraph placeholder')
    locations = {i:n for n,i in enumerate(ids)}; covered = []
    for division in manifest['reading_divisions']:
        start,end = locations[division['start_id']],locations[division['end_id']]+1
        require(start == len(covered) and end > start, 'Reading division gap or overlap')
        selected = ids[start:end]
        require(len(selected) == division['blocks'], 'Reading division count differs')
        require(sum(words(translated[i]) for i in selected) == division['english_words'], 'Reading division word count differs')
        require(sum(primary(originals[i]) for i in selected) == division['primer_passages'], 'Division primer count differs')
        require(english.count('<a id="'+division['anchor']+'"></a>') == 1, 'Missing reading anchor')
        covered.extend(selected)
    require(covered == ids, 'Unaccounted source blocks')
    charts = manifest['charts']
    require(len(charts) == coverage['transformation_charts'] == 32, 'Chart count differs')
    changes = {(r['id'],r['slot']):r for r in manifest['collation']['image_corrections']}
    needed_changes, chart_ids, endpoints = set(), [], []
    for number,chart in enumerate(charts,1):
        require(chart['chart'] == number and english.count('<a id="'+chart['anchor']+'"></a>') == 1, 'Chart identity or anchor differs')
        start,end = locations[chart['start_id']],locations[chart['end_id']]+1
        selected = ids[start:end]; chart_ids.extend(selected)
        require(len(selected) == chart['blocks'] == 18, 'Chart row count differs')
        original_entries, english_entries = [], []
        for identifier in selected:
            source_matches = list(SOURCE_ENTRY.finditer(originals[identifier]))
            english_matches = list(ENGLISH_ENTRY.finditer(translated[identifier]))
            require(len(source_matches) == len(english_matches) == len(re.findall(IMAGE,translated[identifier])), 'Chart row entries differ')
            for slot,(sm,em) in enumerate(zip(source_matches,english_matches),1):
                label=sm[2].strip()
                require(label in NUMBERS, 'Unknown source chart label')
                original_entries.append((identifier,slot,sm[1],NUMBERS[label]))
                english_entries.append((int(em[1]),em[2],em[3],em[4],int(em[5])))
        require(len(original_entries) == chart['entries'] == 64, 'Chart does not contain sixty-four entries')
        first,last = original_entries[0][3],original_entries[-1][3]
        require([first,last] == [chart['first_hexagram'],chart['last_hexagram']], 'Chart endpoints differ')
        endpoints.extend([first,last]); wanted = transformed(first)
        require(wanted[-1] == last, 'Chart endpoints are not complementary')
        require(list(reversed(wanted)) == transformed(last), 'Reverse chart traversal failed')
        for position,(original_entry,translated_entry,want) in enumerate(zip(original_entries,english_entries,wanted),1):
            identifier,slot,path,source_number = original_entry
            index,alt,en_path,name,en_number = translated_entry
            require(index == position and en_number == want and name == EN_NAMES[want-1], 'Incorrect translated chart entry')
            require(alt == name+' — hexagram '+str(want), 'Chart image description differs')
            require(int(re.search(r'-yi(\d+)b\.png$',en_path)[1]) == want, 'Translated glyph identity differs')
            source_image_number = int(re.search(r'-yi(\d+)b\.png$',path)[1])
            key = (identifier,slot)
            if source_number != want or source_image_number != want:
                needed_changes.add(key)
                require(key in changes, 'Undocumented source chart error')
                correction = changes[key]
                require(correction['chart'] == number and correction['position'] == position, 'Correction chart position differs')
                require(correction['number'] == source_number and correction['english_number'] == want, 'Correction numbers differ')
                require(correction['label'] == CN_NAMES[source_number-1] and correction['parallel_label'] == CN_NAMES[want-1], 'Correction witness labels differ')
                require(correction['english_name'] == name and correction['english_path'] == en_path, 'Correction translation differs')
        require(sum(words(translated[i]) for i in selected) == chart['english_words'], 'Chart word count differs')
    require(sorted(endpoints) == list(range(1,65)), 'Chart endpoints do not cover all sixty-four originals')
    require(needed_changes == set(changes), 'Unnecessary or missing chart corrections')
    require(sum(r['number'] != r['english_number'] for r in changes.values()) == coverage['corrected_chart_labels'] == 2, 'Corrected label count differs')
    require(len(changes) == coverage['corrected_image_references'] == 12, 'Corrected image count differs')
    require(chart_ids == manifest['chart_block_ids'] and len(chart_ids) == coverage['chart_blocks'] == 576, 'Chart block coverage differs')
    require(coverage['chart_entries'] == 2048 and coverage['encoded_original_result_pairs'] == 4096, 'Chart relationship counts differ')
    require(sum(words(translated[i]) for i in chart_ids) == coverage['chart_label_english_words'], 'Chart-label word count differs')
    require(sum(words(translated[i]) for i in ids if i not in set(chart_ids)) == coverage['prose_english_words'], 'Prose word count differs')
    require(manifest['numeric_checks'] == arithmetic(), 'Stored numerical checks differ')
    for page in ['4715','4716','4717']:
        require(english.count('<a id="eee-'+page+'"></a>') == 1, 'Source-page anchor missing')
