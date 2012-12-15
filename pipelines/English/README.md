English semantic parsing pipeline
===

**DESCRIPTION**

English semantic parsing pipeline.

* `Boxer_pipeline.py` – running tokenizer, CCG parser and Boxer sematic parser

```
usage: Boxer_pipeline.py [-h] [--input INPUT] [--outputdir OUTPUTDIR] [--tok]
                         [--fname FNAME]
optional arguments:
  -h, --help            show this help message and exit
  --input INPUT         Input file to be processed.
  --outputdir OUTPUTDIR
                        Output directory. Default is the dir of the input
                        file.
  --tok                 Tokenize input text.
  --fname FNAME         File prefix for intermediate output.
```

---

**DEPENDECIES**

* [Boxer](http://svn.ask.it.usyd.edu.au/trac/candc/wiki/boxer)

The pipeline runs with the subversion of Boxer, using '--semantics tacitus' option only

---
