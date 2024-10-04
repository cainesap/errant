# Resources

## de-stts_map

Mapping the Stuttgart/Tuebinger tagsets (STTS), as used in the [spaCy German news models](https://spacy.io/models/de#de_core_news_sm), to Universal classes.
Source: https://www.ims.uni-stuttgart.de/documents/ressourcen/korpora/tiger-corpus/annotation/tiger_scheme-syntax.pdf (p121)
Not all the spaCy tags (listed under "label scheme" for each model) are included in the STTS tagset from the PDF above. However, they were an "N*" tag and a "V*" tag, therefore easy to map to NOUN and VERB respectively, plus an "_SP" tag which I assumed to map to X (can investigate using `spacy.explain(_SP)` if I know what string might prompt this tag from a spaCy model).
Also: corrections are welcome! For instance, APPRART = Praeposition mit Artikel (e.g. im [Haus], zur [Sache]) is an interesting case of an article-preposition hybrid (I opted to map to ADP but it could equally be DET?)

## wordlist-german.txt

List of German words obtained from https://gist.github.com/MarvinJWendt/2f4f4154b8ae218600eb091a5706b5f4
- An improvement would be to use Hunspell, which involves a dictionary and affix file, e.g. https://github.com/elastic/hunspell/blob/master/dicts/de_DE/README_de_DE.txt

_Note that the support for languages other than English is only approximate (e.g. we are still using the Lancaster stemmer for English, in the absence of knowing about stemmers for other languages. Feel free to inform!)_
