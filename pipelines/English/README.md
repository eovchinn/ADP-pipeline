English semantic parsing pipeline
===

**DESCRIPTION**

English semantic parsing pipeline based on [Boxer](http://svn.ask.it.usyd.edu.au/trac/candc/wiki/boxer) semantic parser.

* `Boxer_pipeline.py` – running tokenizer, CCG parser and Boxer sematic parser

```
usage: Boxer_pipeline.py [-h] [--input INPUT] [--outputdir OUTPUTDIR] [--tok]
                         [--fname FNAME]

Boxer pipeline.

optional arguments:
  -h, --help            show this help message and exit
  --input INPUT         The input file to be processed.
  --outputdir OUTPUTDIR The output directory.
  --tok                 Tokenize input text.
  --fname FNAME         File prefix for intermediate output.

```

Alternative: `run_English.sh` runs the full processing pipline for tokenizing and parsing English text:

```
./run_English.sh [<path to input file> [<path to output dir]]
```
