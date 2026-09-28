#!/usr/bin/env python3
"""Verify complete coverage of the selected edition, not independent translation accuracy."""
from pathlib import Path
import argparse
import hashlib
import json
import re
import validate_translation as translations

ROOT=Path(__file__).resolve().parents[1]
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def validate():
    selectors=['front-matter']+[f'{n:02}' for n in range(23)]
    reports=[translations.validate(s) for s in selectors]
    units=[]; covered_sources=[]; covered_targets=[]; page_ids=[]
    for s,report in zip(selectors,reports):
        stem='translation-front-matter' if s=='front-matter' else f'translation-juan-{s}'
        mp=ROOT/'provenance'/(stem+'.json')
        m=json.loads(mp.read_text(encoding='utf-8'))
        sp,tp=ROOT/m['source'],ROOT/m['translation']
        covered_sources.append(m['source']); covered_targets.append(m['translation'])
        pages=re.findall(r'<!-- BEGIN SOURCE: eee-(\d+) -->',sp.read_text(encoding='utf-8'))
        page_ids.extend(pages)
        units.append({'unit':s,'source':m['source'],'translation':m['translation'],'manifest':str(mp.relative_to(ROOT)),
            'source_sha256':sha(sp),'translation_sha256':sha(tp),'manifest_sha256':sha(mp),'source_pages':len(pages),
            'source_blocks':report['source_blocks'],'main_text_english_words':report['main_text_english_words'],'endnotes':report['endnotes'],'status':report['status']})
    expected={str(p.relative_to(ROOT)) for p in (ROOT/'source').glob('*.md')}
    translations.require(set(covered_sources)==expected and len(covered_sources)==len(expected)==24,'Missing, extra or duplicate source units')
    translations.require(len(set(covered_targets))==24,'Duplicate English target')
    translations.require(len(page_ids)==len(set(page_ids)),'Duplicated source page across translated units')
    translations.require(all(r['status']=='passed' for r in reports),'Failed constituent validation')
    return {'status':'passed','scope':'Complete source-aligned translation coverage of the selected 易學網 edition; not an independent bilingual review or a critical edition of all witnesses.',
        'source_files':24,'translated_files':24,'numbered_juans':22,'preliminary_juan':True,'front_matter':True,
        'source_pages':len(page_ids),'source_blocks':sum(u['source_blocks'] for u in units),
        'main_text_english_words':sum(u['main_text_english_words'] for u in units),'endnotes':sum(u['endnotes'] for u in units),
        'source_image_positions':sum(r['local_images'] for r in reports),'untranslated_source_files':[],
        'independent_bilingual_review':False,'systematic_facsimile_collation':False,'units':units}

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write-report',action='store_true')
    args=parser.parse_args()
    try:
        report=validate()
        text=json.dumps(report,ensure_ascii=False,indent=2)+'\n'
        if args.write_report: (ROOT/'provenance/translation-completeness.json').write_text(text,encoding='utf-8')
        print(text,end='')
    except (OSError,ValueError,KeyError) as error:
        parser.exit(1,f'Validation failed: {error}\n')
