#!/usr/bin/env python3
"""Additional structural and mathematical checks for Juan Twenty-One.

These checks do not establish historical claims, empirical astronomy,
independent semantic accuracy, or literary quality. Standard library only.
"""
from pathlib import Path
from fractions import Fraction
import hashlib
import itertools
import json
import math
import re

HEADS = [1,11,19,28,53,105,115,122,125,128,135,146,149,155,160,163,167,170,173,177,182,209,212,219,226,232,258,261]
TRI = {'乾':(1,1,1),'坤':(0,0,0),'震':(1,0,0),'巽':(0,1,1),
       '坎':(0,1,0),'離':(1,0,1),'艮':(0,0,1),'兌':(1,1,0)}
NAMES = dict(zip(TRI, ('Qian','Kun','Zhen','Xun','Kan','Li','Gen','Dui')))
ENGLISH = {NAMES[k]:v for k,v in TRI.items()}
IMAGE = r'!\[([^\]]*)\]\(([^)]+)\)'

def require(condition, message):
    if not condition:
        raise ValueError(message)

def words(text):
    text = re.sub(IMAGE + r'|\[\^[^\]]+\]', '', text)
    return len(re.findall(r"\b[A-Za-z]+(?:['’-][A-Za-z]+)*\b", text))

def arithmetic_checks(translated):
    ops = {'+':lambda a,b:a+b, '−':lambda a,b:a-b, '×':lambda a,b:a*b}
    expressions = []
    for identifier,text in translated.items():
        for a,op,b,c in re.findall(r'(?<![\d,])(\d+) ([+−×]) (\d+) = (\d+)(?![\d,])',text):
            require(ops[op](int(a),int(b)) == int(c), f'{identifier}: false equation')
            expressions.append((identifier,a,op,b,c))
    require(len(expressions) == 108, 'Explicit arithmetic equation coverage changed')
    initial = [[4*r+c+1 for c in range(4)] for r in range(4)]
    middle_corners = lambda r,c: (r in (1,2) and c in (1,2)) or (r in (0,3) and c in (0,3))
    magic = []
    for reverse in (False,True):
        start = [[17-x if reverse else x for x in row] for row in initial]
        for keep in (True,False):
            a = [[start[r][c] if middle_corners(r,c)==keep else 17-start[r][c] for c in range(4)] for r in range(4)]
            sums = [sum(row) for row in a] + [sum(a[r][c] for r in range(4)) for c in range(4)]
            sums += [sum(a[i][i] for i in range(4)),sum(a[i][3-i] for i in range(4))]
            require(sums == [34]*10, 'Four-by-four diagram arithmetic failed')
            magic.append(a)
    require(magic[0] == magic[3] and magic[1] == magic[2], 'Reverse diagrams do not exchange')
    outer = (1,2,3,4,6,7,8,9)
    require({x*x % 10 for x in outer} == {1,4,6,9}, 'Restricted square last digits differ')
    for a,b in ((1,9),(2,8),(3,7),(4,6),(5,5)):
        require(a*a+2*a*b+b*b == 100, 'Square decomposition failed')
    for k in range(4):
        a,b,c = (x*3**k for x in (3,4,5))
        require(a*a+b*b == c*c, 'Right-triangle scaling failed')
    require(sum(range(1,11))==55 and sum(range(1,10))==45, 'Triangular totals differ')
    require([sum(v) for v in ((9,18,27),(6,12,18),(9,27,45),(6,18,30))]==[54,36,81,54], 'Ring totals differ')
    require(all(sum(range(1,2*n,2))==n*n for n in range(1,10)), 'Odd sums differ')
    rows = [[math.comb(n,k) for k in range(n+1)] for n in range(7)]
    require([sum(r) for r in rows]==[2**n for n in range(7)], 'Doubling totals differ')
    year, month = Fraction(1461,4), Fraction(29)+Fraction(499,940)
    require(year*100/25/30 == Fraction(487,10), '48.7 scaling differs')
    require(12*month == Fraction(354)+Fraction(348,940), 'Lunar-year total differs')
    require(year-12*month == Fraction(10)+Fraction(827,940), 'Solar-lunar difference differs')
    require(Fraction(7,19)*month == year-12*month, 'Lunar divisor identity differs')
    require(Fraction(7,10)*Fraction(15,2) == Fraction(21,4), 'Solar divisor identity differs')
    require(19*year==235*month and 60*(6+Fraction(7,80))==year, 'Calendar cycle identities differ')
    require(216+144==360 and 78+150==228 and 6912+4608==11520, 'Stalk totals differ')
    require(32*30*12==32*360==11520, 'Schematic intercalation totals differ')
    fixed = sum(tuple(reversed(h))==h for h in itertools.product((0,1),repeat=6))
    classes = {0:0,1:0,2:0}
    for h in itertools.product((0,1),repeat=6):
        if h == tuple(reversed(h)): continue
        changes = sum(t != tuple(reversed(t)) for t in (h[:3],h[3:]))
        classes[changes] += 1
    require(fixed==8 and classes=={0:12,1:32,2:12}, 'Reversal classification differs')
    nuclei = {x[:3]+x[1:] for x in itertools.product((0,1),repeat=4)}
    require(len(nuclei)==16, 'Overlapping figure count differs')
    return {'explicit_equations':len(expressions),'four_by_four_arrays':4,'binomial_rows':7,
        'reversal_invariant_hexagrams':fixed,'reversal_classes':classes,'overlapping_figures':16,
        'calendar_model':'Exact rational checks within the stipulated 365¼-day year and 29 + 499/940-day lunation.',
        'scope':'Internal identities only. The circle ratio and 32-month intercalation claim are not certified as exact astronomy or geometry.'}

def validate(manifest, originals, translated, english, target):
    ids = list(originals)
    require(ids == [f'eee-4718:{i:03d}' for i in range(1,265)], 'Supplement source range differs')
    require(manifest['coverage']['canonical_passages'] == 0, 'Supplement counted as new scripture')
    require(not re.search(r'^### ', '\n'.join(translated.values()), re.M), 'Supplement mislabeled as canonical text')
    require('⟦PARA⟧' not in english and not re.search(r'@fig\d+@',english), 'Unexpanded draft marker')
    headings = [f'eee-4718:{i:03d}' for i in HEADS]
    require(headings == manifest['heading_ids'], 'Supplement heading list differs')
    require([i for i in ids if translated[i].startswith('## ')] == headings, 'English source headings differ')
    require(len(headings) == manifest['coverage']['source_headings'], 'Heading count differs')
    locations = {identifier:index for index,identifier in enumerate(ids)}
    covered = []
    require(len(manifest['reading_divisions'])==len(HEADS), 'Reading division total differs')
    for division in manifest['reading_divisions']:
        start,end = locations[division['start_id']],locations[division['end_id']]+1
        require(start==len(covered) and end>start, 'Gap or overlap in supplementary sections')
        section = ids[start:end]
        require(section[0] in headings, 'Section does not begin at a source heading')
        require(originals[section[0]] == division['source_title'], 'Chinese section heading changed')
        require(originals[section[0]].startswith('**'), 'Source heading lacks source emphasis')
        require(translated[section[0]] == '## '+division['title'], 'Translated heading differs from index')
        require(len(section)==division['blocks'], 'Section block count differs')
        require(sum(words(translated[i]) for i in section)==division['english_words'], 'Section word count differs')
        require(english.count(f'<a id="{division["anchor"]}"></a>')==1, 'Section anchor absent or duplicated')
        covered.extend(section)
    require(covered==ids and english.count('<a id="eee-4718"></a>')==1, 'Unaccounted source material')
    image_ids = [i for i in ids if re.search(IMAGE, originals[i])]
    require(image_ids==manifest['diagram_block_ids'], 'Supplement diagram blocks differ')
    require(len(image_ids)==manifest['coverage']['diagram_blocks'], 'Diagram block count differs')
    original_images = [path for i in ids for _,path in re.findall(IMAGE,originals[i])]
    images = [(alt,path) for i in ids for alt,path in re.findall(IMAGE,translated[i])]
    require([p for _,p in images]==original_images, 'Supplement images missing, changed, or reordered')
    require(len(images)==manifest['coverage']['diagram_images']==37, 'Expected thirty-seven images')
    require(len(manifest['source_images'])==len(images), 'Image manifest length differs')
    for (alt,path),item in zip(images,manifest['source_images']):
        require(bool(alt.strip()), 'Untranslated diagram label')
        require(path==item['path'], 'Image manifest order differs')
        require(hashlib.sha256((target.parent/path).read_bytes()).hexdigest()==item['sha256'], 'Diagram bytes changed')
    shifts = [i for i in ids if re.match(r'^\*\*[乾坤震巽坎離艮兌][☰☱☲☳☴☵☶☷]', originals[i])]
    require(shifts==manifest['trigram_shift_ids'] and len(shifts)==manifest['coverage']['trigram_shift_entries']==16, 'Trigram shift coverage differs')
    for identifier in shifts:
        cn,en = originals[identifier],translated[identifier]
        start_name = cn[2]
        r = re.search(r'([上下])去一([陰陽])([上下])生一([陰陽])(?:則|復|仍)?為([乾坤震巽坎離艮兌])',cn)
        require(r is not None, f'{identifier}: unrecognized Chinese shift')
        side,removed,added_side,added,result_name = r.groups()
        bits = TRI[start_name]
        require(side!=added_side and bits[0 if side=='下' else -1]==(removed=='陽'), 'Incorrect removed source line')
        shifted = bits[1:]+(int(added=='陽'),) if side=='下' else (int(added=='陽'),)+bits[:-1]
        require(shifted==TRI[result_name], 'Source shift is inconsistent')
        e = re.search(r'^\*\*(\w+) [☰☱☲☳☴☵☶☷]:\*\* Remove a (yin|yang) line (below|above) and generate a (yin|yang) line (below|above): it (?:becomes|returns to|remains) (\w+)\.',en)
        require(e is not None, f'{identifier}: untranslated shift')
        expected = (NAMES[start_name], 'yang' if removed=='陽' else 'yin', 'below' if side=='下' else 'above', 'yang' if added=='陽' else 'yin', 'below' if added_side=='下' else 'above', NAMES[result_name])
        require(e.groups()==expected, f'{identifier}: English shift differs from Chinese')
    return {**arithmetic_checks(translated), 'source_aligned_trigram_shifts':len(shifts)}
