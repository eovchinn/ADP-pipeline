Abductive discourse processing pipelines
===

This directory contains semantic parsing pipelines, converters into observations, 
and scripts for running the whole abduction-based discrourse processing.

---

**Semantic parsing pipelines**

Semantic parsing pipelines are implemented for 4 languages:
- English
- Spanish
- Russian
- Farsi

The pipelines take unrelated sentences or coherent text as input.

Input example 1 (unrelated sentences)

```
The War for Wisconsin began as a fight over labor rights.
Yet 16 months after Walker launched his attack on unions , just as many people in union households voted for him.
```

Input example 2 (coherent text fragments)

```
<META>textID1

Here's the problem: Income exemption levels under the "wealth tax" -- as the AMT is known -- were never adjusted for inflation since it was enacted decades ago. So Congress has regularly passed an AMT "patch" to correct for that by raising the exemption levels. 

<META>textID2

After progress earlier this week in fiscal cliff negotiations, President Barack Obama and House Speaker John Boehner butted heads Wednesday, setting the stage for a showdown as the deadline looms for an agreement.
The negotiations had focused on a $2 trillion package of new revenue, spending cuts and entitlement changes the two sides have shaped into a broad deficit reduction plan.
```

The pipelines output logical forms for the input text fragments. A logical form 
is a conjunction of propositions, which have generalized eventuality arguments that can be used for 
showing relationships among the propositions. We use logical representations of natural language texts as 
described in [[Hobbs, 1995]](http://www.isi.edu/~hobbs/op-acl85.pdf). The description of the logical form generation
can be found [here](https://github.com/metaphor-adp/Metaphor-ADP/blob/master/pipelines/INSTRUCTIONS.md).

Output example English:

```
%%% The War for Wisconsin began as a fight over labor rights 
id(2,2).
2001 The DT the O 
2002 War NNP War I-ORG 
2003 for IN for I-ORG 
2004 Wisconsin NNP Wisconsin I-ORG 
2005 began VBD begin O 
2006 as IN as O 
2007 a DT a O 
2008 fight NN fight O 
2009 over IN over O 
2010 labor NN labor O 
2011 rights NNS rights O 
[2003]:for-p(e18,x0,x1) & [2005]:begin-v(x5,x0,u16,u17) & [2008]:fight-n(e15,x4) & [2010]:labor-n(e14,x2) & []:nn(e13,x3,x2) & [2011]:rights-n(e12,x3) & [2009]:over-p(e11,x4,x3) & [2006]:as-p(e10,x5,x4) & [2004]:wisconsin-n(e8,x1) & [2004]:org(e9,x1) & [2002]:war-n(e6,x0) & [2002]:org(e7,x0)
```

Output example Russian:

```
% Тем более что многие специалисты прогнозируют в 2012 году новую волну финансового кризиса .
id(1).
[3002]:более-rb(e1,e10) & [3005]:специалист-nn(e2,x1) & [3006]:прогнозировать-vb(e3,x1,u1,u2) & [3007]:в-in(e4,e3,x2) & [3009]:год-nn(e5,x2) & [3010]:новый-adj(e6,x3) & [3011]:волна-nn(e7,x3) & [3012]:финансовый-adj(e8,x4) & [3013]:кризис-nn(e9,x4) & of-in(e11,x3,x4)
```

---

**Converting logical forms into Henry observations**

In order to be processed by the [abductive inference engine](http://code.google.com/p/henry-n700/), 
logical forms of sentences need to be converted into observations.

Observations are generated from logical forms by the following scripts:

- [Boxer2Henry.py][https://github.com/metaphor-adp/Metaphor-ADP/blob/master/pipelines/English/Boxer2Henry.py) (for English)
- [IntParser2Henry.py](https://github.com/metaphor-adp/Metaphor-ADP/blob/master/pipelines/common/IntParser2Henry.py)(for other languages)


The format of an observation is as follows:

```
<observation> ::= "(O (name " <observation id> ") (^" <conjunction of atomic observations> "))" 
<observation id> ::= <ASCII string, no spaces>
<conjunction of atomic observations> ::= <atomic observation> | <atomic observation> " " <conjunction of atomic observations>
<atomic observation> ::= "(" <proposition name> " " <arguments> " :" <proposition cost> ":" <proposition id> ":[" <word ids> "])" | "(!= " <arguments> ")"
<proposition name> ::= <UTF-8 string, no spaces>
<arguments> ::= <argument> | <argument> " " <arguments>
<argument> ::= <ASCII string, no spaces>
<proposition cost> ::= <FLOAT>
<proposition id> ::= <ASCII string, no spaces>
<word id> ::= <INTEGER>
```

Example:

```
(O (name 2) (^ (for-in e18 x0 x1 :1:2-1:[2003]) (begin-vb x5 x0 u16 u17 :1:2-2:[2005]) (fight-nn e15 x4 :1:2-3:[2008]) (labor-nn e14 x2 :1:2-4:[2010]) (nn e13 x3 x2 :1:2-5:[ID5]) (rights-nn e12 x3 :1:2-6:[2011]) (over-in e11 x4 x3 :1:2-7:[2009]) (as-in e10 x5 x4 :1:2-8:[2006]) (wisconsin-nn e8 x1 :1:2-9:[2004]) (org e9 x1 :1:2-10:[2004]) (war-nn e6 x0 :1:2-11:[2002]) (org e7 x0 :1:2-12:[2002]) (!= e6 e7) (!= e8 e9) (!= e9 e7)))
```

---
