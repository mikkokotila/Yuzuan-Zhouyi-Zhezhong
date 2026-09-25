# English Translation

[Read Juan One: Qian through The Army](juan-01.md) · [Read Juan Two: Holding Together through Great Possession](juan-02.md)

This folder contains complete annotated translations of the first two numbered juan of the repository’s 易學網 edition of 《御纂周易折中》. Every hexagram statement, line statement, accompanying commentary, collected explanation, and editorial discussion in those juan is represented. **The preface, other front matter, and preliminary juan (卷首) remain untranslated.**

| Juan | Hexagrams | Source blocks | Oracle statements | Endnotes |
|---|---|---:|---:|---:|
| [One · 卷一](juan-01.md) | 1–7: 乾 through 師 | 443 | 51 | 80 |
| [Two · 卷二](juan-02.md) | 8–14: 比 through 大有 | 364 | 49 | 66 |

The block counts include prose paragraphs, oracle statements, attribution headings, and captions; they are not counts of prose paragraphs alone. Juan One includes the two special “Using” statements for Qian and Kun. The main English text contains 33,689 words in Juan One and 27,729 in Juan Two, excluding endnotes and project front matter; the manifests specify the counting method.

The stable bases are [Chinese Juan One](../source/juan-01.md) and [Chinese Juan Two](../source/juan-02.md). Doubtful passages were compared selectively with the parallel *Siku Quanshu* transcriptions: [Juan One, fixed revision 759587](https://zh.wikisource.org/w/index.php?title=御纂周易折中_%28四庫全書本%29/卷01&oldid=759587) and [Juan Two, fixed revision 528525](https://zh.wikisource.org/w/index.php?title=御纂周易折中_%28四庫全書本%29/卷02&oldid=528525). These are translations of the selected base, not newly constituted critical editions. **Independent bilingual review and systematic leaf-by-leaf collation with historical facsimiles have not yet been performed.**

## Reading the voices

| Chinese label | English label | Voice |
|---|---|---|
| 本義 | Original Meaning | Zhu Xi |
| 程傳 | Cheng’s Commentary | Cheng Yi |
| 集說 | Collected Explanations | Individually attributed commentators |
| 案 | Editorial Judgment | The imperial compilers |
| 總論 | General Discussion | The attributed commentator or commentators |
| 附録 | Supplement | The source’s supplementary material |

**“Editorial Judgment” is never the translator’s voice.** Translator’s interventions appear in the numbered endnotes. Disagreements among commentators are preserved, including disagreements over punctuation, the identity of a figure, the use of changing lines, and the meaning of an oracular expression.

The English aims to remain readable without replacing the source’s concrete images, historical institutions, ethical vocabulary, or social assumptions with modern equivalents. “Noble person,” “great person,” and “sage” distinguish 君子, 大人, and 聖人. Firmness, yieldingness, vigor, and compliance distinguish 剛, 柔, 健, and 順. Centeredness and correctness are kept distinct, including when ethical rightness differs from formal correctness of a line’s position.

## Endnotes and textual decisions

The endnotes explain consequential translation choices, technical relationships among lines, classical allusions, and disagreements within the compilation. They document corrections adopted from the parallel text, meaningful variants retained from the base, and interpretive clarifications for which no corrected witness was found. Juan One also includes an explicitly supplementary translation of a Hu Bingwen gloss absent from the base.

Juan Two distinguishes confirmed transcription corrections from unresolved readings. Its notes cover, among other matters, the competing interpretations of returning in Small Restraint, the third and fourth lines of Fellowship, and the final blessing of Great Possession. The latter also explains the apparent discrepancy between the compilers’ description of The Cauldron’s Judgment and its received wording.

**No Chinese source file has been changed.** An attested correction is not silently passed off as the base reading, and an intelligible difference between editions is not automatically treated as a typo. The parallel transcription itself contains apparent errors and has not been followed indiscriminately.

## Coverage and review

Hidden Markdown comments assign each translated block an identifier such as `eee-4542:001` or `eee-4553:001`. The [Juan One manifest](../provenance/translation-juan-01.json) and [Juan Two manifest](../provenance/translation-juan-02.json) record the corresponding source and translation hashes. These markers do not appear in the rendered reading text, but allow later bilingual review to identify a passage precisely without disturbing the source.

Run the structural checks from the repository root:

```sh
python3 scripts/validate_translation.py --juan all
python3 scripts/validate_translation.py --juan 02 --write-report
```

Without `--juan`, the validator continues to check Juan One. It checks source integrity, complete ordered coverage, commentary labels, individual oracle-statement alignment, endnote references, local images, word counts, and block checksums. The recorded reports for [Juan One](../provenance/translation-juan-01-validation.json) and [Juan Two](../provenance/translation-juan-02-validation.json) concern completeness and integrity, **not proof of semantic accuracy or literary quality**.

For an intentional revision, review the changed passage against the Chinese and its endnote, then update the corresponding checksums and word counts in the manifest, including its overall file checksum. Do not refresh checksums merely to suppress an unexplained validation failure. The Chinese source remains the stable reference; proposed changes to it require a separately documented editorial decision.
