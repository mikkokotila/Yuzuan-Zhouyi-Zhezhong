"""Source-bound coverage and combinatorial checks for the final explanatory juan.

Validates constructions, not the compilers' historical or moral interpretation.
Uses only the standard library and the repository's fixed hexagram definitions.
"""
import hashlib
import re
from itertools import product
import validate_primer_charts as p

IMAGE = r'!\[[^\]]*\]\(([^)]+)\)'
CN_PATTERN = re.compile('|'.join(sorted(p.CN_NAMES,key=len,reverse=True)))
EN_PATTERN = re.compile(r'(?<![A-Za-z])(?:'+'|'.join(re.escape(n) for n in sorted(p.EN_NAMES,key=len,reverse=True))+r')(?![A-Za-z])')
MISC = [1,2,8,7,19,20,3,4,51,52,41,42,26,25,45,46,15,16,21,22,58,57,17,18,23,24,35,36,48,47,31,32,59,60,40,39,38,37,12,11,34,33,14,13,49,50,62,61,55,56,30,29,9,10,5,6,28,44,53,27,63,54,64,43]
QUOTES = ('乾剛坤柔','比樂師憂','大畜時也','謙輕而豫怠','兌見而巽伏','隨无故也','剝爛也','晉晝也','井通而困','咸速也','渙離也','解緩也','大壯則止','小過過也','小畜寡也','大過顛也')
GROUPS = [[1,2,23,24,28,27,44,43],[40,39,38,37,53,54,63,64],[8,7,19,20,3,4,41,42],[31,32,34,33,14,13,49,50],[26,25,45,46,17,18,12,11],[59,60,62,61,55,56,30,29],[51,52,15,16,21,22,35,36],[58,57,48,47,9,10,5,6]]
DYADS = [('Old yang','太陽',(1,1)),('Young yin','少陰',(1,0)),('Young yang','少陽',(0,1)),('Old yin','太陰',(0,0))]
def require(ok,message):
    if not ok: raise ValueError(message)
def chinese(text): return re.sub(r'[^\u3400-\u9fff]','',text)
def label(n): return f'{n}. {p.EN_NAMES[n-1]} {p.CN_NAMES[n-1]}'
def nuclear(n):
    h=p.HEXAGRAMS[n]
    return p.INVERSE[h[1:4]+h[2:5]]
def source_role(text):
    if re.search(IMAGE,text): return 'diagram'
    if chinese(text).startswith(QUOTES): return 'quotation'
    if text.startswith(('程子有上下篇義','先儒有以雜卦為互卦者')): return 'gloss'
    if text.startswith('御纂周易折中卷'): return 'title'
    if text.startswith('右'): return 'group_caption'
    if text.startswith('**'):
        bare=text.replace('**','').strip()
        names=[s for s in re.split('[、，。\\s]+',bare) if s]
        if len(names)>1 and all(s in p.NUMBERS for s in names): return 'sequence_group'
        if bare.startswith('自'): return 'classification'
        return 'heading'
    return 'discussion'

def validate(manifest, originals, translated, target, english, words):
    ids=list(originals); roles={i:source_role(b) for i,b in originals.items()}
    prefixes={'diagram':'![','quotation':'**Quotation — Miscellaneous Hexagrams.**','gloss':'**Source gloss.**','title':'Imperially Compiled','group_caption':'**Group label.**','sequence_group':'**Sequence group.**','classification':'**Classification.**','discussion':'**Compilers’ Discussion.**'}
    for i,role in roles.items():
        if role=='heading': require(translated[i].startswith(('## ','#### ')),f'{i}: missing source heading')
        else: require(translated[i].startswith(prefixes[role]),f'{i}: wrong source role {role}')
    for role,key in [('heading','heading_ids'),('quotation','miscellaneous_quotation_ids'),('gloss','source_gloss_ids'),('diagram','diagram_block_ids'),('sequence_group','sequence_group_ids'),('group_caption','sequence_group_caption_ids')]:
        require([i for i in ids if roles[i]==role]==manifest[key],f'{role}: manifest differs from Chinese')
    c=manifest['coverage']
    require(c['canonical_passages']==0,'Essay must not add new canonical passages')
    require(len(manifest['heading_ids'])==c['source_headings']==33,'Heading count differs')
    require(len(manifest['miscellaneous_quotation_ids'])==c['miscellaneous_quotation_blocks']==16,'Quotation count differs')
    require(len(manifest['source_gloss_ids'])==c['source_glosses']==2,'Source gloss count differs')
    seen=[]; group_sizes=[]
    for i in manifest['sequence_group_ids']:
        numbers=[p.NUMBERS[n] for n in CN_PATTERN.findall(originals[i])]
        expected='**Sequence group.** '+', '.join(p.EN_NAMES[n-1] for n in numbers)+'.'
        require(re.sub(r'\[\^[^\]]+\]','',translated[i])==expected,f'{i}: sequence names differ')
        group_sizes.append(len(numbers)); seen.extend(numbers)
    require(seen==list(range(1,65)) and group_sizes==[10,6,8,6,10,6,12,6],'Sequence groups incomplete or reordered')
    require(len(group_sizes)==c['sequence_groups']==8,'Group count differs')
    cited=[]
    for i in manifest['miscellaneous_quotation_ids']:
        # In 渙離也, 離 is the verb 'separates', not a second hexagram name.
        quote_text=chinese(originals[i]).replace('渙離也','渙')
        numbers=[p.NUMBERS[n] for n in CN_PATTERN.findall(quote_text)]
        found=[p.EN_NAMES.index(n)+1 for n in EN_PATTERN.findall(translated[i])]
        require(numbers==found,f'{i}: quoted hexagram names differ')
        cited.extend(numbers)
    require(cited==MISC and len(set(cited))==64==c['quoted_miscellaneous_hexagrams'],'Miscellaneous quotation order differs')
    require(sum(n<=30 for n in cited[:28])==18 and sum(n>30 for n in cited[28:56])==18,'Classic memberships differ')
    require(manifest['embedded_appended_quotation_ids']==['eee-4719:043'] and c['embedded_appended_quotation_blocks']==1,'Embedded quotation differs')
    require('孔子《繫辭傳》' in originals['eee-4719:043'],'Embedded quotation lacks source evidence')
    require('virtue’s foundation' in translated['eee-4719:043'],'Embedded quotation absent')
    d=translated['eee-4719:048']; expected=[]
    for e1,c1,a in DYADS:
        for e2,c2,b in DYADS:
            x=a+b; n=p.INVERSE[x[:3]+x[1:]]
            expected.append(f'| {e1} {c1} | {e2} {c2} | {label(n)} |')
    rows=re.findall(r'^\| (?:Old|Young) .+$',d,re.M)
    require(rows==expected,'Four-Image diagram key differs')
    d=translated['eee-4719:052']
    expected=[f'| {g} | {label(n)} | {label(nuclear(n))} |' for g,ns in enumerate(GROUPS,1) for n in ns]
    require(re.findall(r'^\| [1-8] \| .+$',d,re.M)==expected,'Sixty-four-figure diagram key differs')
    sixteen=[1,2,23,24,28,27,44,43,53,54,40,39,38,37,63,64]
    d=translated['eee-4719:054']
    expected=[f'| {label(n)} | {label(nuclear(n))} |' for n in sixteen]
    require(re.findall(r'^\| \d+\. .+$',d,re.M)==expected,'Sixteen-figure diagram key differs')
    require(c['diagram_key_entries']==16+64+16,'Diagram-key entry count differs')
    images=re.findall(IMAGE,'\n'.join(originals.values()))
    require(images==re.findall(IMAGE,'\n'.join(translated.values())),'Images altered or reordered')
    require(len(images)==c['diagram_images']==6 and len(manifest['diagram_block_ids'])==c['diagram_blocks']==6,'Diagram count differs')
    require(len(images)==len(manifest['source_images']),'Image manifest differs')
    for image,item in zip(images,manifest['source_images']):
        require(image==item['path'],'Image path differs')
        require(hashlib.sha256((target.parent/image).read_bytes()).hexdigest()==item['sha256'],'Original image bytes changed')
    require(all('**Diagram key.**' in translated[i] for i in manifest['diagram_block_ids']),'Untranslated diagram labels')
    first={nuclear(n) for n in range(1,65)}
    second={nuclear(n) for n in first}
    require(first==set(sixteen) and second=={1,2,63,64},'Two-stage overlap reduction differs')
    require({n for n in second if nuclear(n)==n}=={1,2},'Fixed points differ')
    require(nuclear(63)==64 and nuclear(64)==63,'Completion cycle differs')
    h=p.HEXAGRAMS[28]; cyclic=[]
    for start in (1,6,5,4,3,2):
        x=tuple(h[(start-1+j)%6] for j in range(4)); n=p.INVERSE[x[:3]+x[1:]]
        cyclic.append(n)
        token=f'line {start} → {p.EN_NAMES[n-1]} {p.CN_NAMES[n-1]}'
        require(token in translated['eee-4719:129'],'Cyclic key differs from construction')
    require(cyclic==[44,53,27,54,43,1],'Cyclic order differs')
    examples=[n for n,h in p.HEXAGRAMS.items() if all(h[1:5])]
    require(examples==[1,28,43,44],'Uniqueness counterexamples differ')
    require('惟大過一卦' in originals['eee-4719:131'] and '[^j22-uniqueness]' in translated['eee-4719:131'],'Unresolved source assertion silently changed')
    locations={i:k for k,i in enumerate(ids)}; covered=[]
    require(len(manifest['reading_divisions'])==c['reading_divisions']==25,'Reading division count differs')
    for division in manifest['reading_divisions']:
        a,b=locations[division['start_id']],locations[division['end_id']]+1
        require(a==len(covered) and b>a,'Gap or overlap in reading divisions')
        selected=ids[a:b]; covered.extend(selected)
        require(len(selected)==division['blocks'],'Division coverage differs')
        require(sum(words(translated[i]) for i in selected)==division['english_words'],'Division word count differs')
        require(english.count(f'<a id="{division["anchor"]}"></a>')==1,'Navigation anchor differs')
    require(covered==ids,'Unaccounted source blocks')
    require(english.count('<a id="eee-4719"></a>')==1,'Source-page anchor differs')
    require(not any(x in english for x in ('⟦PARA⟧','⟦LINE⟧','TABLE39','TABLE40','TABLE41')),'Unexpanded assembly marker')
    return {'sequence_group_sizes':group_sizes,'miscellaneous_groups':[28,28,8],
        'first_overlap_distinct_figures':len(first),'second_overlap_distinct_figures':len(second),
        'diagram_key_entries':96,'cyclic_great_excess_results':cyclic,
        'four_yang_middle_line_counterexamples':examples,
        'scope':'Internal combinatorial checks, not proof of the proposed historical sequence or of the compilers’ relative yin–yang classifications.'}
