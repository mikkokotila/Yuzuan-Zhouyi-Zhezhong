"""Source-bound checks for front matter and the preliminary juan.

These verify coverage and structural distinctions, not literary or semantic quality.
Only Python's standard library is required.
"""
import hashlib
import re
from validate_primer_charts import CN_NAMES, EN_NAMES, HEXAGRAMS, NUMBERS

def require(ok, message):
    if not ok: raise ValueError(message)
def sha(text): return hashlib.sha256(text.encode('utf-8')).hexdigest()
def chinese(text): return re.sub(r'[^\u3400-\u9fff]', '', text)
def verify_sections(m, originals, translated, english, words):
    ids=list(originals); locations={v:i for i,v in enumerate(ids)}; covered=[]
    for d in m['reading_divisions']:
        a,b=locations[d['start_id']],locations[d['end_id']]+1
        require(a==len(covered) and b>a,'Gap or overlap in remaining-material divisions')
        selected=ids[a:b]
        require(len(selected)==d['blocks'],'Reading division count differs')
        require(sum(words(translated[i]) for i in selected)==d['english_words'],'Reading division word count differs')
        require(english.count('<a id="'+d['anchor']+'"></a>')==1,'Reading anchor missing or duplicated')
        covered.extend(selected)
    require(covered==ids,'Unaccounted remaining material')
    heads=[i for i,t in translated.items() if re.match(r'^#{2,4} ',t)]
    require(heads==m['heading_ids'] and len(heads)==m['coverage']['source_headings'],'Heading coverage differs')
    for s in m['sections']:
        require(english.count('<a id="eee-'+s['page']+'"></a>')==1,'Source-page anchor missing or duplicated')
def front_checks(m, originals, translated, english, target):
    ids=list(originals)
    require(len(ids)==332 and [s['page'] for s in m['sections']]==['4532','4533','4534','4535','4536','4537'],'Front-matter scope differs')
    staff=[i for i in ids if i.startswith('eee-4533:') and re.search(r'臣\s',originals[i])]
    require(staff==m['contributor_ids'] and len(staff)==50,'Contributor count differs')
    for i in staff:
        name=chinese(originals[i].split('臣',1)[1])
        require(name in chinese(translated[i]) and 'your servant' in translated[i],i+': contributor identity or formal designation missing')
    dynasties=['漢','晉','齊','北魏','隋','唐','宋','金','元','明']
    actual=[i for i in ids if i.startswith('eee-4534:') and originals[i].replace('**','').strip() in dynasties]
    require(actual==m['dynasty_heading_ids'],'Dynasty headings differ')
    require([originals[i].replace('**','').strip() for i in actual]==dynasties,'Dynasty order differs')
    authorities=[i for i in ids if i.startswith('eee-4534:') and int(i.rsplit(':',1)[1])>=3 and i not in actual]
    require(authorities==m['authority_ids'] and len(authorities)==218,'Cited-author entries missing')
    articles=[i for i in ids if i.startswith('eee-4535:')][1:]
    require(articles==m['editorial_article_ids'] and len(articles)==8,'Editorial article count differs')
    for i,name in zip(articles,['One','Two','Three','Four','Five','Six','Seven','Eight']):
        require(translated[i].startswith('**Article '+name+'.**'),i+': article label differs')
    contents=[i for i in ids if i.startswith('eee-4536:')][1:]
    require(contents==m['contents_ids'] and len(contents)==23,'Contents count differs')
    for i,n in zip(contents,range(23)):
        path=f'juan-{n:02}.md'
        require(']('+path+')' in translated[i] and (target.parent/path).is_file(),i+': contents link missing')
    pieces=m['continuous_synopsis_ids']
    require(pieces==[f'eee-4537:{i:03}' for i in range(2,6)],'Catalogue fragment identities differ')
    runs=re.findall(r'<p>\s*(.*?)\s*</p>',english,re.S)
    require(any(re.findall(r'BEGIN TRANSLATION: (eee-\d+:\d{3})',p)==pieces for p in runs),'Catalogue opening not rendered continuously')
    require('Qianlong’s thirty-ninth year' in translated[pieces[-1]],'Base synopsis date altered')
    require(not re.search(r'^#{2,4} Sectional [Cc]ompilation',english,re.M),'Supplementary heading silently inserted')
    return {'contributors':50,'authorities':218,'editorial_articles':8,'contents_entries':23,'catalogue_fragments_joined':4}
VOICE_RANGES=[(3,3,'Rites of Zhou'),(4,12,'Lu Deming'),(13,18,'Kong Yingda'),(19,20,'Chao Shuozhi'),(21,22,'Zhu Xi'),(23,24,'Lü Zuqian'),(25,25,'Shui Yuquan'),(26,26,'Wang Yinglin'),(29,29,'Sima Qian'),(30,30,'Ban Gu'),(31,36,'Wang Bi'),(37,37,'Wang Tong'),(38,39,'Kong Yingda'),(40,40,'Master Zhou Dunyi'),(41,42,'Master Shao'),(43,44,'Master Zhang'),(45,50,'Master Cheng'),(51,51,'Cheng Yi'),(52,52,'Master Cheng'),(53,66,'Zhu Xi'),(67,67,'Cai Yuanding'),(68,73,'Xu Heng'),(74,75,'Hu Yigui'),(76,76,'Hu Bingwen'),(77,77,'Wu Cheng'),(78,78,'Xue Xuan'),(79,80,'Cai Qing'),(83,85,'Wang Tong'),(86,86,'Master Shao'),(87,89,'Master Cheng'),(90,94,'Zhu Xi'),(96,96,'Kong Yingda'),(97,97,'Master Cheng'),(98,98,'Yin Tun'),(99,106,'Zhu Xi'),(107,108,'Wang Yinglin')]
RELATIONS=[(120,3,0,4,1,[8,9,20,29,37,42,48,53,57,59,60,61,3,5,39,63]),(121,3,1,4,0,[30,32,35,50,51,14,38,40,54,56,62,16,21,55,34,64]),(122,1,1,4,0,[4,7,11,14,18,19,32,34,38,40,41,46,50,26,54,64]),(123,1,0,4,1,[12,13,17,20,31,3,33,39,63,8,25,37,42,45,49,53])]

def preliminary_checks(m, originals, translated):
    ids=list(originals)
    require(len(ids)==132 and [s['page'] for s in m['sections']]==['4538','4539','4540','4541'],'Preliminary scope differs')
    descriptions=[ids[i-1] for i in (2,28,82)]
    summaries=[ids[i-1] for i in (95,109)]
    require(descriptions==m['source_description_ids'],'Source descriptions differ')
    require(summaries==m['source_summary_ids'],'Source summaries differ')
    require(all(translated[i].startswith('**Source description:') for i in descriptions),'Description misattributed')
    require(all(translated[i].startswith('**Source summary:') for i in summaries),'Summary misattributed')
    for a,b,voice in VOICE_RANGES:
        for n in range(a,b+1):
            require(translated[ids[n-1]].startswith('**'+voice),f'Block {n}: voice label differs')
    for n in [112,114,116]+list(range(118,128))+[129,130,132]:
        require(translated[ids[n-1]].startswith('**Imperial Compilers.**'),f'Block {n}: editorial voice missing')
    list_id=ids[130]
    require(list_id==m['governing_line_list_id'],'Governing-line source block differs')
    cn=originals[list_id].splitlines(); en=translated[list_id].splitlines()
    require(len(cn)==len(en)==len(m['governing_entries'])==64,'Incomplete governing-line list')
    for n,(c,e,r) in enumerate(zip(cn,en,m['governing_entries']),1):
        require(c.replace('**','').startswith('- '+CN_NAMES[n-1]),f'Governing source entry {n} differs')
        prefix=f'- **{EN_NAMES[n-1]} ({n}) · {CN_NAMES[n-1]}.**'
        require(e.startswith(prefix) and len(e)>len(prefix)+20,f'Governing translation {n} missing or mislabeled')
        require(r['number']==n and r['source_item_sha256']==sha(c) and r['translation_item_sha256']==sha(e),'Governing-entry checksum differs')
    for n,a,x,b,y,listed in RELATIONS:
        expected={num for num,bits in HEXAGRAMS.items() if bits[a]==x and bits[b]==y}
        require(set(listed)==expected and len(listed)==16,'Relation-group enumeration differs')
        i=ids[n-1]
        require(all(CN_NAMES[g-1] in originals[i] and EN_NAMES[g-1] in translated[i] for g in listed),f'Block {n}: relation-group member missing')
    return {'governing_line_entries':64,'relation_groups':4,'hexagrams_per_relation_group':16,'attributed_prose_blocks':sum(b-a+1 for a,b,v in VOICE_RANGES),'scope':'Internal coverage and polarity checks; not proof of interpretive judgments or historical transmission.'}

def validate(m, originals, translated, english, target, words):
    require('⟦PARA⟧' not in english,'Unexpanded paragraph separator')
    require(not re.search(r'^### ',english,re.M),'Editorial material mislabeled as canonical text')
    verify_sections(m,originals,translated,english,words)
    for d in m['collation']['decisions']:
        require(d['source_block'] in originals and '[^'+d['endnote']+']:' in english,'Textual decision lacks a source or note')
    if m['text_kind']=='front_matter': return front_checks(m,originals,translated,english,target)
    require(m['text_kind']=='preliminary_juan','Unexpected remaining-material kind')
    return preliminary_checks(m,originals,translated)
