MALT pipline for Russian
===

**DESCRIPTION**

Processing pipeline for Russian.

* `malt_ru.py` – converter for Malt parser output. Reads MALT output from stdin and write to stdout.
* `malt_ru_test.py` – test script which reproduces full processing pipline for parsing Russian. This includes: tokenizing (using `utf8-tokenize.perl` from [TreeTagger](http://www.ims.uni-stuttgart.de/projekte/corplex/TreeTagger/) package), lemmatization (using TreeTagger on OS X or [CSTLEMMA](http://cst.dk/online/lemmatiser/uk/) on Linux), POS tagging (usign TreeTagger), converting TreeTagger output to Malt compatible format ([CoNLL](http://nextens.uvt.nl/depparse-wiki/DataFormat)), dependency parsing (using [MaltParser](http://www.maltparser.org/) 1.5 with [these](http://corpus.leeds.ac.uk/mocky/) tools).
* `rus-test.mco` – MALT model for Russian.

===


**PIPELINING COMMAND EXAMPLES**

The following command reads text from file `input.txt`, performs dependency parsing and prints dependency tree to stdout. The difference between Linux and OS X versions is that Linux version uses additional lemmatizer *CSTLEMMA* which is not ported to OS X. Both scrips assume to be called from the *current* directory.

OS X:

```
../../external-tools/tree-tagger-3.2/darwin/cmd/utf8-tokenize.perl test_input.txt |
../../external-tools/tree-tagger-3.2/darwin/bin/tree-tagger -lemma -token -sgml ../../external-tools/malt-ru/russian.par |
../../external-tools/malt-ru/make-malt.pl |
java -Xmx16g -jar ../../external-tools/malt-1.5/malt.jar -c rus-test.mco -m parse |
malt_ru.py
```

Linux:

```
../../external-tools/tree-tagger-3.2/darwin/cmd/utf8-tokenize.perl test_input.txt |
../../external-tools/tree-tagger-3.2/darwin/bin/tree-tagger -lemma -token -sgml ../../external-tools/malt-ru/russian.par |
../../external-tools/malt-ru/lemmatiser.pl -l ../../external-tools/malt-ru/msd-ru-lemma.lex.gz -p ../../external-tools/malt-ru/wform2011.ptn1 -c ../../external-tools/malt-ru/cstlemma-linux-64bit |
../../external-tools/malt-ru/make-malt.pl |
java -Xmx16g -jar ../../external-tools/malt-1.5/malt.jar -c rus-test.mco -m parse |
malt_ru.py
```

===

**OUTPUT SAMPLES**

Text:

```
Съешьте еще этих мягких французских булочек, да выпейте же чаю.
```

TreeTagger output, converted to CoNLL:

```
1	Съешьте	съесть	V	V	Vmm-2p-a-p
1	еще	еще	R	R	R
1	этих	этот	P	P	P---pga
1	мягких	мягкий	A	A	Afpmpgf
1	французских	французский	A	A	Afpmpgf
1	булочек	булочка	N	N	Ncfpgn
1	,	,	,	,	,
1	да	да	C	C	C
1	выпейте	выпить	V	V	Vmm-2p-a-p
1	же	же	Q	Q	Q
1	чаю	чай	N	N	Ncmsnnp
1	.	.	S	S	SENT
```


MaltParser output:

```
1	Съешьте	съесть	V	V	Vmm-2p-a-p	0	ROOT	_	_
2	еще	еще	R	R	R	3	огранич	_	_
3	этих	этот	P	P	P---pga	6	опред	_	_
4	мягких	мягкий	A	A	Afpmpgf	6	опред	_	_
5	французских	французский	A	A	Afpmpgf	6	опред	_	_
6	булочек	булочка	N	N	Ncfpgn	1	1-компл	_	_
7	,	,	,	,	,	6	PUNC	_	_
8	да	да	C	C	C	1	сент-соч	_	_
9	выпейте	выпить	V	V	Vmm-2p-a-p	8	соч-союзн	_	_
10	же	же	Q	Q	Q	9	огранич	_	_
11	чаю	чай	N	N	Ncmsnnp	9	1-компл	_	_
12	.	.	S	S	SENT	11	PUNC	_	_
```

`malt_ru.py` output:

```
TODO
```