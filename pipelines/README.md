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

Example 1 (unrelated sentences)

```
The War for Wisconsin began as a fight over labor rights.
Yet 16 months after Walker launched his attack on unions , just as many people in union households voted for him.
```

Example 2 (coherent text fragments)

```
<META>textID1

Here's the problem: Income exemption levels under the "wealth tax" -- as the AMT is known -- were never adjusted for inflation since it was enacted decades ago. So Congress has regularly passed an AMT "patch" to correct for that by raising the exemption levels. 

<META>textID2

After progress earlier this week in fiscal cliff negotiations, President Barack Obama and House Speaker John Boehner butted heads Wednesday, setting the stage for a showdown as the deadline looms for an agreement.

The negotiations had focused on a $2 trillion package of new revenue, spending cuts and entitlement changes the two sides have shaped into a broad deficit reduction plan.
```
