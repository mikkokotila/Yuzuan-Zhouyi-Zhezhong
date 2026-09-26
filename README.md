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

[Juan Six: Release through Oppression](translation/juan-06.md) is translated in full, with 28,316 words of main text and 80 endnotes. It covers 解、損、益、夬、姤、萃、升、困. All 434 source blocks are aligned, including the separately presented portions of Decrease’s Judgment. The Chinese source and previous translations remain unchanged.

[Juan Seven: The Well through Abundance](translation/juan-07.md) is translated in full, with 30,612 words of main text and 87 endnotes. It covers 井、革、鼎、震、艮、漸、歸妹、豐. All 424 source blocks, 56 oracle statements, and eight images are preserved in order. The Chinese source and earlier translations remain unchanged.

[Juan Eight: The Wanderer through Before Completion](translation/juan-08.md) is translated in full, with 28,748 words of main text and 98 endnotes. It covers 旅、巽、兌、渙、節、中孚、小過、既濟、未濟. All 503 source blocks, 63 oracle statements, and nine local images are aligned and validated. The first eight juans cover all sixty-four hexagrams and their line commentaries; progress on the separately treated Wings is recorded below. The preface and preliminary juan remain untranslated. The Chinese source and previous translations are unchanged.

[Juan Nine: Commentary on the Judgments, Upper Part](translation/juan-09.md) is translated in full, with 28,217 words of source-aligned English and 102 endnotes. It covers 乾 through 離 (hexagrams 1–30), preserving all 520 source blocks and 84 Tuan passages. This begins the compilation’s separate treatment of the Wings. The Chinese source, illustrations, and first eight translations remain unchanged.

[Juan Ten: Commentary on the Judgments, Lower Part](translation/juan-10.md) is translated in full, with 26,225 words of source-aligned English and 104 endnotes. It covers 咸 through 未濟 (hexagrams 31–64), preserving all 610 source blocks and 97 Tuan passages. Both parts of the Judgment Commentary are now translated. An editorial passage absent from the base under Abundance is included only in a labeled supplementary endnote. The Chinese source, illustrations, and first nine translations remain unchanged.

[Juan Eleven: Commentary on the Images, Upper Part](translation/juan-11.md) is translated in full, with 35,436 words of source-aligned English and 127 endnotes. It covers 乾 through 離 (hexagrams 1–30), retaining all 1,083 source blocks and 213 primary Image blocks. These include the Great Images, ordinary line Images, and the special Using Images of Qian and Kun. The Chinese source, illustrations, and first ten translations remain unchanged. The preface and preliminary juan remain untranslated.

[Juan Twelve: Commentary on the Images, Lower Part](translation/juan-12.md) is translated in full, with 39,455 words of source-aligned English and 144 endnotes. It covers 咸 through 未濟 (hexagrams 31–64), retaining all 1,206 source blocks and 237 base Image passages. Joy’s missing top-line Image is supplied in a labeled supplementary endnote, not silently inserted into the base-aligned text. Both Image Commentaries are now covered. The Chinese source, illustrations, and first eleven translations remain unchanged.

[Juan Thirteen: Appended Statements, Upper Part, Chapters One–Six](translation/juan-13.md) is translated in full, with 18,142 words of source-aligned English and 82 endnotes. All 316 source blocks are retained, including 35 canonical passages and Zhu Xi’s six separately labeled chapter summaries. A Yu Fan gloss absent from the base is translated only in a supplementary endnote. This completes Juan Thirteen; the upper Appended Statements continues in Juan Fourteen. The Chinese source, illustrations, and first twelve translations remain unchanged. The preface and preliminary juan remain untranslated.

[Juan Fourteen: Appended Statements, Upper Part, Chapters Seven–Twelve](translation/juan-14.md) is translated in full, with 20,616 words of source-aligned English and 78 endnotes. All 373 source blocks are retained, including 46 canonical passages and Zhu Xi’s six separately labeled chapter summaries. The complete supplementary debate on stalk-counting is included, with the different procedures and the compilers’ reconciliation kept distinct. Together with Juan Thirteen, this completes the upper Appended Statements. The Chinese source, illustrations, and first thirteen translations remain unchanged. The preface and preliminary juan remain untranslated.

[Juan Fifteen: Appended Statements, Lower Part](translation/juan-15.md) is translated in full, with 25,857 words of source-aligned English and 83 endnotes. It includes all twelve chapters, all 506 source blocks, 72 canonical passages, and Zhu Xi’s twelve separately labeled chapter summaries. Interpretive disagreements and proposed textual changes are documented rather than silently harmonized. Together with Juans Thirteen and Fourteen, this completes both parts of the Appended Statements. The Chinese source, illustrations, and first fourteen translations remain unchanged. The preface and preliminary juan remain untranslated.

[Juan Sixteen: Commentary on the Words of the Text — Wenyan, Qian and Kun](translation/juan-16.md) is translated in full, with 18,496 words of source-aligned English and 60 endnotes. All 353 source blocks are retained, including 48 canonical Wenyan passages and eight separately identified source summaries. The voices of Zhu Xi, Cheng Yi, collected commentators, and imperial editors remain distinct. Selective textual checks include the parallel Siku transcription, additional primary texts, and four historical page images; independent bilingual review and systematic facsimile collation remain outstanding. The Chinese source, illustrations, and first fifteen translations are unchanged. The preface and preliminary juan remain untranslated.

[Juan Seventeen: Discussion of the Trigrams](translation/juan-17.md) is translated in full, with 14,819 words of source-aligned English and 48 endnotes. All 220 source blocks and 22 canonical paragraphs are included across eleven chapters. The base’s ten summary headings remain distinct; the missing Chapter Six summary appears only in a supplementary endnote. The Earlier Heaven and Later Heaven discussions and the full lists of trigram images retain their disagreements and uncertainties. The Chinese source, illustrations, and first sixteen translations remain unchanged. The preface and preliminary juan remain untranslated.

[Juan Eighteen: Sequence and Miscellaneous Hexagrams](translation/juan-18.md) is translated in full, with 9,071 words of source-aligned English and 40 endnotes. All 230 source blocks and 40 canonical passages are included, with twenty primary passages in each Wing. The complete Cheng essay and the received order of the final eight Miscellaneous hexagrams are retained. Supported corrections, contextual repairs, and unresolved readings are distinguished. This completes the separately arranged Ten Wings commentary section, not the entire compilation; progress on the remaining juans is recorded below. The Chinese source, illustrations, and first seventeen translations are unchanged. The preface and preliminary juan remain untranslated.

[Juan Nineteen: Introduction to the Study of the Changes, Parts One–Two](translation/juan-19.md) is translated in full, with 15,422 words of source-aligned English and 54 endnotes. All 152 source blocks and eleven original images are retained. The embedded primer’s own preface belongs to this juan and is included; the compilation’s imperial preface and preliminary juan remain untranslated. The River Chart, Luo Writing, doubling constructions, Earlier Heaven and Later Heaven accounts retain their disagreements and uncertainties, with supported textual repairs and numerical checks documented. The primer continues in Juan Twenty. The Chinese source, illustrations, and first eighteen translations are unchanged.

[Juan Twenty: Yarrow Stalks, Changing Lines, and Transformation Charts](translation/juan-20.md) is translated in full, with 11,076 words of source-aligned English (7,972 in prose and captions; 3,104 in chart labels) and 33 endnotes. It completes Parts Three–Four of the embedded Introduction and includes all 32 charts, 2,048 displayed entries, and eight stalk diagrams. Twelve wrong chart image references and two names are corrected with explicit notes and manifest records; source files and original assets are unchanged. The primer’s methods and the compilers’ objections remain distinct. Juan Twenty-Two, the compilation’s front matter, and the preliminary juan remain untranslated. Independent bilingual review and systematic facsimile collation remain outstanding.

[Juan Twenty-One: Supplementary Discussions to the Introduction](translation/juan-21.md) is translated in full, with 11,353 words of source-aligned English and 49 endnotes. All 264 source blocks and thirty-seven diagrams are retained, including arithmetic methods, geometric constructions, overlapping-trigram explanations, calendrical arguments, and the final doubling diagram. The compilers’ voice is distinguished from Zhu Xi’s own Introduction. Textual corrections identify their witnesses; mathematical approximations and unresolved or schematic claims are not silently modernized. The Chinese source, original images, and first twenty translations are unchanged. Juan Twenty-Two, front matter, and the preliminary juan remain untranslated. Independent bilingual review and systematic facsimile collation remain outstanding.
