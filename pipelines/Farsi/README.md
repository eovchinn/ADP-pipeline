===========
Farsi semantic parsing pipeline
===========

A pipeline that tokenizes, POS tags, parses and creates logical form for Farsi sentences.

###Running the pipeline

```
./LF_Pipeline [<input file>][<output file>]
```
To run the pipeline, call run_spanish.sh with the absolute path to the input file as an argument. By default the system outputs the logical forms of the sentences in the input file to stdout. The second (optional) argument can be a file or a directory. If the optional argument is a file, the system output will be redirected there. If it is a directory, the intermediate files (tokenized, tagged, etc.) will be put into that directory, and the final output will go to stdout.

Running tokenizer

```
./tokenize [<input file>][<output file>]
```

Running tagger

```
./tag [<input file>][<output file>]
```

Running parser

```
./parse [<input file>][<output file>]
```

Running logical form generator
```
./createLF [<input file>][<output file>]
```

###External Tools & Resources

- Tokenization
 - [utf-8 tokenizer]( http://corpus.leeds.ac.uk/tools/utf8-tokenize.pl)
- POS Tagging
 - [Stanford's tagger](http://nlp.stanford.edu/software/tagger.shtml)
- Parsing
 - [MaltParser 1.5](http://www.maltparser.org)
     - training corpus: [Persian dependency treebank](http://dadegan.ir/en)


