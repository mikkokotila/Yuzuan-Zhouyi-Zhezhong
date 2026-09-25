# English Translation

[Read Juan One: Qian through The Army](juan-01.md)

This folder contains the English translation of the **first numbered juan, 卷一**, of the repository’s YiXueWang edition of 《御纂周易折中》. It includes all seven hexagrams, their hexagram and line statements, both special “Using” statements, and every accompanying commentary and editorial discussion in that juan. The preface, other front matter, and preliminary juan (卷首) have not been translated.

The translation follows [the archived Chinese source](../source/juan-01.md). Difficult passages were compared selectively with the [parallel *Siku Quanshu* transcription](https://zh.wikisource.org/w/index.php?title=御纂周易折中_(四庫全書本)/卷01&oldid=759587). This is a complete annotated translation of the selected base, not a newly constituted critical edition. It has not yet received independent bilingual review or systematic leaf-by-leaf collation with historical facsimiles.

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

Juan One has **80 endnotes**. They explain consequential translation choices, technical relationships among lines, classical allusions, and disagreements within the compilation. They also document corrections adopted from the parallel text, meaningful variants retained from the base, and interpretive clarifications for which no corrected witness was found. An additional Hu Bingwen gloss present in the parallel edition but absent from the base is translated explicitly as a supplementary endnote.

No Chinese source file has been changed. An attested correction is not silently passed off as the base reading, and an intelligible difference between editions is not automatically treated as a typo. The parallel transcription itself contains apparent errors and has not been followed indiscriminately.

## Coverage and review

The main translation contains approximately **33,700 English words**, excluding endnotes and project front matter. All **443 source blocks** are represented once, in order. That count includes prose paragraphs, oracle statements, attribution headings, and captions; it is not a claim that all 443 are prose paragraphs. The juan contains **51 oracle statements**: seven hexagram statements, forty-two ordinary line statements, and the two special “Using” statements for Qian and Kun.

Hidden Markdown comments assign each translated block an identifier such as `eee-4542:001`. The [translation manifest](../provenance/translation-juan-01.json) records the corresponding source and translation hashes. These markers do not appear in the rendered reading text, but allow later bilingual review to identify a passage precisely without disturbing the source.

Run the structural checks from the repository root:

```sh
python3 scripts/validate_translation.py
```

The validator checks source integrity, complete ordered coverage, commentary labels, all 51 oracle statements, endnote references, local images, and block checksums. Its [recorded report](../provenance/translation-juan-01-validation.json) concerns completeness and integrity, not a proof of semantic accuracy or literary quality.

For an intentional revision, review the changed passage against the Chinese and its endnote, then update its corresponding checksum and the overall file checksum in the manifest. Do not refresh checksums merely to suppress an unexplained validation failure. The Chinese source remains the stable reference; proposed changes to that source require a separately documented editorial decision.
