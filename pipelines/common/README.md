Abductive discource processing pipeline
===

**DESCRIPTION**

Multilingual (English, Spanish, Farsi, Russian) abductive discource processing pipeline.

* `NLPipeline_MULT_stdinout.py` – running tokenizer, lemmatizer, parser, logical form converter, abductive reasoner, proof graph generator

```
usage: NLPipeline_MULT_stdinout.py [-h] [--lang LANG] [--input INPUT]
                                   [--outputdir OUTPUTDIR] [--parse] [--henry]
                                   [--kb KB] [--kbcompiled KBCOMPILED]
                                   [--graph GRAPH] [--textid]
optional arguments:
  -h, --help            show this help message and exit
  --lang LANG           Input language: EN, ES, RU, FA.
  --input INPUT         Input file: plain text (possibly with text ids),
                        observation file, henry file.
  --outputdir OUTPUTDIR
                        Output directory. If input file defined, then default
                        is input file dir. Otherwise its TMP_DIR.
  --parse               Tokenize and parse text, produce logical forms,
                        convert to obeservations.
  --henry               Process observations with Henry.
  --kb KB               Path to noncompiled knowledge base.
  --kbcompiled KBCOMPILED
                        Path to compiled knowledge base.
  --graph GRAPH         ID of text/sentence to vizualize. Possible value:
                        allN, where N is number of sentences to vizualize.
  --textid              Meta text ids.

```

---

**COMPONENTS**

* [English semantic parsing pipeline](https://github.com/metaphor-adp/Metaphor-ADP/tree/master/pipelines/English)
* [Spanish semantic parsing pipeline](https://github.com/metaphor-adp/Metaphor-ADP/tree/master/pipelines/Spanish)
* [Russian semantic parsing pipeline](https://github.com/metaphor-adp/Metaphor-ADP/tree/master/pipelines/Russian)
* [Farsi semantic parsing pipeline](https://github.com/metaphor-adp/Metaphor-ADP/tree/master/pipelines/Farsi)
* [Henry abductive reasoner](https://github.com/naoya-i/henry-n700)
