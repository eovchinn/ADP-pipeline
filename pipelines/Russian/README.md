Russian semantic parsing pipeline
===

**DESCRIPTION**

Semantic processing pipeline for Russian.

* `malt_ru.py` – converter for Malt parser output to Logical Form format:

```
python malt_ru.py [--input <input file>] [--output <output file>] [--nnnumber 1] [--vbtense 1]
```

Output should be generated using [this](http://corpus.leeds.ac.uk/mocky/msd-ru.html) part of speech tagset.

* `run_russian.sh` – this script runs the full processing pipline for parsing Russian:

```
./run_russian.sh [<absolute path to input> [<absolute path to output>]]
```


Script runs tokenizing (using nltk), lemmatization (using TreeTagger on OS X or [CSTLEMMA](http://cst.dk/online/lemmatiser/uk/) on Linux), POS tagging (usign TreeTagger), converting TreeTagger output to Malt compatible [format](http://nextens.uvt.nl/depparse-wiki/DataFormat) and dependency parsing (using [MaltParser](http://www.maltparser.org/) 1.5 with [these](http://corpus.leeds.ac.uk/mocky/) tools).


---

**DEPENDECIES**

* NLTK – [nltk.org](nltk.org/)

---

**OUTPUT EXAMPLES**

Text:

```
Съешьте еще этих мягких французских булочек, да выпейте же чаю.
```

TreeTagger:

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


MaltParser:

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

`malt_ru.py`:

```
% Съешьте еще этих мягких французских булочек , да выпейте же чаю .
id(1).
[1001]:съесть-vb(e1,x1,x2,x3) & [1002]:еще-rb(e2,x4) & [1004]:мягкий-adj(e3,x5) & [1005]:французский-adj(e4,x6) & [1006]:булочка-nn(e5,x7) & [1009]:выпить-vb(e6,x8,x9,x10) & [1011]:чай-nn(e7,x11)
```
