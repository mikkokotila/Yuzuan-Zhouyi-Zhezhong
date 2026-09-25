# Source policy

## Base text and scope

Use only the [易學網 transcription](https://www.eee-learning.com/article/4531) for the
reading text in `source/`. The 22 numbered juan follow its [contents page](https://www.eee-learning.com/book/4536).
The formal 卷首 is `juan-00.md`; six preceding sections are in `front-matter.md`.
Do not insert passages or variant readings from Wikisource, Waseda, or other witnesses
without identifying them as a separate editorial intervention.

## What the import changes

The importer extracts the article's book-body field, not its surrounding navigation,
author profile, comments, advertisements, or footer. It removes scan-thumbnail
navigation and navigation-only cross-reference paragraphs. Their text and the scan
URLs remain in the provenance manifest. The modern introductory landing page and
the navigation-only 象傳 index are excluded, but every substantive child is retained.

HTML presentation becomes Markdown. Redundant nested bold tags are flattened;
numbered paragraph openings are escaped to prevent accidental Markdown lists.
Whitespace and layout formatting can change, but a round-trip comparison requires
the complete non-whitespace source text to remain identical. Source tables keep their
HTML structure. Every substantive image remains at its corresponding point in the
text and is backed by a local file. No optical character recognition is used.

## What is not changed

Traditional and variant characters, punctuation, commentator labels, quoted names,
and apparent transcription mistakes are retained as found. Repository titles,
YAML metadata, page anchors, and HTML comments are editorial navigation aids.
