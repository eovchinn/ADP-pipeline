Abductive discourse processing pipelines
===

This directory contains semantic parsing pipelines, converters into Henry format, 
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

The pipelines output logical forms for the input text fragments. A logical form (LF) 
is a conjunction of propositions, which have generalized eventuality arguments that can be used for 
showing relationships among the propositions. We use logical representations of natural language texts as 
described in [[Hobbs, 1995]](http://www.isi.edu/~hobbs/op-acl85.pdf).

Output example

```
[2003]:for-p(e18,x0,x1) & [2005]:begin-v(x5,x0,u16,u17) & [2008]:fight-n(e15,x4) & [2010]:labor-n(e14,x2) & []:nn(e13,x3,x2) & [2011]:rights-n(e12,x3) & [2009]:over-p(e11,x4,x3) & [2006]:as-p(e10,x5,x4) & [2004]:wisconsin-n(e8,x1) & [2004]:org(e9,x1) & [2002]:war-n(e6,x0) & [2002]:org(e7,x0)
```

---

