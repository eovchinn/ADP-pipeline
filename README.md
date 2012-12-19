Metaphor-ADP
============

This is a repository of the ISI metaphor project team. Here we store all the resources and tools constituting 
our Natural Language Understanding system based on Abductive Reasoning implemented for 4 languages:

- English
- Spanish
- Russian
- Farsi

The system is largely based on ideas summarized in [[Hobbs, 1993]](http://www.isi.edu/~hobbs/interp-abduct-ai.pdf).

Our abductive Natural Language Understanding pipeline is shown below. 

![Fig.](https://raw.github.com/metaphor-adp/Metaphor-ADP/master/docs/pics/pipeline-pic.png)

Text fragments are given as input to the pipeline. The text fragments are parsed. 
For Russian and Spanish tagging, we use [TreeTagger](http://www.ims.uni-stuttgart.de/projekte/corplex/TreeTagger/). 
For Farsi tagging, we use the [Stanford NLP tagger](http://nlp.stanford.edu/software/tagger.shtml). 
For parsing, we use the dependency parser [Malt](http://www.maltparser.org) for Spanish, Russian, and Farsi. 
For English, the whole processing is performed by the [Boxer](http://svn.ask.it.usyd.edu.au/trac/candc/wiki/boxer) 
semantic parser).  

The parses are input to the module converting them into logical forms. A logical form (LF) 
is a conjunction of propositions, which have generalized eventuality arguments that can be used for 
showing relationships among the propositions. We use logical representations of natural language texts as 
described in [[Hobbs, 1995]](http://www.isi.edu/~hobbs/op-acl85.pdf). For Spanish, Russian, and Farsi, we have developed logical form converters. 
For English, we use the LF converter built in the Boxer semantic parser.

Logical forms and a knowledge base are input to our abductive reasoner based on Integer Linear Programming 
[[Inoue et al., 2012]](http://www.cl.ecei.tohoku.ac.jp/~naoya-i/resources/jelia2012_paper.pdf). The reasoner produces flat first order logic interpretations in the textual format 
and proof graphs in the PDF format.

---

**Installation and running**

1. Clone Metaphor-ADP repository
```
git clone https://github.com/metaphor-adp/Metaphor-ADP
```
2. Install external packages; see instructions [here](https://github.com/metaphor-adp/Metaphor-ADP/tree/master/installation)
3. Run the system; see instructions [here](https://github.com/metaphor-adp/Metaphor-ADP/blob/master/pipelines/common/README.md)

---

**Contact**

- Jerry Hobbs (hobbs-AT-isi.edu)
- Ekaterina Ovchinnikova (katya-AT-isi.edu)
