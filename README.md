# 御纂周易折中 · Yuzuan Zhouyi Zhezhong

Chinese source corpus for a translation project: **one Markdown file per juan**,
using [易學網's punctuated transcription](https://www.eee-learning.com/article/4531)
as the sole base text. Other editions are retained as references, not silently mixed in.

## Read the source

[`source/`](source/) contains **24 Markdown files**:

- [`juan-00.md`](source/juan-00.md): 卷首, comprising 綱領 and 義例.
- `juan-01.md` through `juan-22.md`: the 22 numbered juan, in their original order.
- [`front-matter.md`](source/front-matter.md): 序、奉旨開列、引用姓氏、凡例、目錄、提要.

The extra front-matter file is not an invented additional juan. Together these files
capture all 156 substantive pages of the selected online edition. The modern book
landing page and the 象傳 navigation index are excluded; their content-page children
are all included.

See the [complete file index and counts](provenance/coverage.md) and
[juan boundaries](provenance/boundaries.md). The captured body text contains
**591,756 non-whitespace characters**, including **486,067 Han characters**.
Text embedded solely in images is not included in these character counts.

The 127 distinct image files in [`assets/eee-learning/`](assets/eee-learning/) are
referenced locally at all 2,173 original image positions. This includes the repeated
hexagrams in 六十四卦相變圖; diagrams have not been replaced by descriptions or omitted.
Two source tables retain their HTML table structure inside Markdown.

## Editorial status

The site labels this transcription proofread. It is convenient for translation because
it preserves traditional characters, punctuation, paragraphing, and labels such as
【本義】、【程傳】、【集說】、【案】、【總論】. Its own contents page supplies the juan boundaries.
The facsimile linked at the opening of juan 20 identifies itself as 欽定四庫全書薈要.
This repository does not claim that the website transcription has been exhaustively
collated against that facsimile or any other printed witness.

No wording, punctuation, variant character, or suspected textual error has been
silently corrected. Website controls, scan-navigation lists, and redundant cross-links
are removed from reading text and recorded in the manifest. Editorial file headings,
metadata, and source-page markers are distinguishable from the historical text.
See [source policy](SOURCE_POLICY.md), [rights and attribution](RIGHTS.md), and
[reference editions](reference/README.md).

## Provenance and validation

[`provenance/manifest.json`](provenance/manifest.json) records original URLs, retrieval
times, original webpage hashes, facsimile-page links, output assignments, text counts,
and image checksums. [`edition-snapshot.json.gz`](provenance/edition-snapshot.json.gz)
contains the cleaned source HTML needed to rebuild the corpus offline. It does not
contain the website's modern introductory essay, user comments, or surrounding site.

The [validation report](provenance/validation.json) checks every page exactly once,
all required files, rendered-text equality with the archived HTML, image order,
local image targets, table counts, and SHA-256 checksums. This establishes conversion
completeness for the captured transcription, not a critically established text.

## Reproduce the corpus

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
python scripts/validate.py
```

An offline rebuild uses the archived snapshot and local assets:

```sh
python scripts/build.py
python scripts/validate.py
```

**Building overwrites `source/*.md`, the manifest, and coverage report.** Commit or
stash any editorial work first. Rebuilding does not translate or emend the text.
To write a fresh validation report, add `--write-report` to the validation command.

For an intentional new capture of the website, first move or remove the ignored
`.cache/` directory, then run `python scripts/fetch.py` followed by
`python scripts/build.py --capture`. Review all resulting differences before committing.
The fetcher is cached, rate-limited, and restricted to the selected book's navigation tree.

For translation work, keep translated passages separate from this source corpus.
The `eee-<page-id>` anchors and `BEGIN SOURCE` / `END SOURCE` markers provide stable
links back to individual source pages and support alignment without altering the base text.

## English Translation

[**Juan One — Qian through The Army**](translation/juan-01.md) is available as a complete annotated English translation, with approximately 33,700 words of translated text and 80 endnotes. It preserves the distinct commentarial voices and documents textual corrections and significant alternative readings. The preface and preliminary juan have not yet been translated.

See [translation conventions and review status](translation/README.md), the [source-alignment manifest](provenance/translation-juan-01.json), and the [validation report](provenance/translation-juan-01-validation.json). The Chinese source corpus is unchanged.

[Juan Two: Holding Together through Great Possession](translation/juan-02.md) is now also translated in full, with 66 endnotes. It covers 比、小畜、履、泰、否、同人、大有. The Chinese source remains unchanged.

[Juan Three: Modesty through Adornment](translation/juan-03.md) is translated in full, with 28,045 words of translated text and 92 endnotes. It covers 謙、豫、隨、蠱、臨、觀、噬嗑、賁. All 414 source blocks and 56 oracle statements are aligned in the [manifest](provenance/translation-juan-03.json) and checked in the [validation report](provenance/translation-juan-03-validation.json). The Chinese source and earlier translations remain unchanged.

[Juan Four: Splitting Apart through Clinging](translation/juan-04.md) is translated in full, with 27,393 words of main text and 90 endnotes. It covers 剝、復、无妄、大畜、頤、大過、坎、離. The Chinese source, images, and earlier translations remain unchanged.

[Juan Five: Influence through Limping](translation/juan-05.md) is translated in full, with 28,424 words of main text and 91 endnotes. It opens the Lower Classic and covers 咸、恒、遯、大壯、晉、明夷、家人、睽、蹇. The Chinese source and previous translations remain unchanged.
