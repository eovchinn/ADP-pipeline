CM Ontology Debugging Instructions
===

**TARGET AXIOMS FORMAT**

Each target lexeme evokes a target domain and (possibly) subdomain. Total weight of these axioms should be <1. Non-English lexical axioms should have domain names both in native language and in English.

* `T#` – prefix indicating target domain
* `TS#` – prefix indicating target subdomain

```
(B (name poverty) (=>(^(TS#POVERTY x :0.45)(T#ECONOMIC-INEQUALITY u :0.45))(poverty-nn e0 x)))

(B (name pobreza) (=>(^(TS#POBREZA/POVERTY x :0.45)(T#ECONOMIC-INEQUALITY u :0.45))(pobreza-nn e0 x)))
```

Target axioms are stored under KBs/LANG/LANG_economic_inequality_Targets.txt

---

**SOURCE AXIOMS FORMAT**

Each source lexeme evokes a source domain and (possibly) subdomain. Total weight of these axioms should be <1. Non-English lexical axioms should have domain names both in native language and in English.

* `S#` – prefix indicating source domain
* `SS#` – prefix indicating source subdomain

```
(B (name disease) (=>(^(S#DISEASE x :0.45)(SS#PhysicalAffliction x :0.45)) (disease-nn e0 x)))

(B (name enfermedad) (=>(^(S#ENFERMEDAD/DISEASE x :0.45)(SS#AfflictionFisica/PhysicalAffliction x :0.45)) (enfermedad-nn e0 x)))
```

Source axioms are stored under ./KBs/LANG/LANG_economic_inequality_Sources.txt

List of current sources can be found [here](https://github.com/metaphor-adp/Metaphor-ADP/blob/master/KBs/common/Current_Sources.xlsx).

---

**ROLES**

Sometimes it might be useful to indicate roles in the axioms (if the roles are used in the mapping axioms).

* `R#` – prefix indicating roles

If somebody is sick, then he fills the R#SICK role in the S#DISEASE frame.

```
(B (name sick) (=>(^(S#DISEASE e0 :0.3)(SS#PhysicalAffliction x :0.3)(R#SICK y e0 :0.3)) (sick-adj e0 y)))
```

If somebody cures a disease, then he fills the R#CURE-AGENT role in the S#DISEASE frame.

```
(B (name treat) (=>(^(S#DISEASE x :0.3)(SS#TREATMENT e0 :0.3)(R#CURE-AGENT y e0 :0.3)) (treat-vb e0 y x u2)))
```

---
**ROLE INTRODUCTION AXIOMS FORMAT**

Sometimes syntactic dependencies introduce new roles. Total weight of these axioms should be <1.

If there is an SS#EPIDEMIC of y, then y is a S#DISEASE.

```
(B (name de-epidemia) (=>(S#ENFERMEDAD/DISEASE y :0.9)(^(SS#EPIDEMIA/EPIDEMIC x)(de-in e1 x y))))
```

---

**INTERNATIONAL AXIOMS FORMAT**

Some concepts are more or less equivalent across languages, therefore their language specific labels should be mapped to 
international labels and these international labels should be used  in the mapping axioms. 
Total weight of these axioms should be <1. 

```
(B (name dismap)(=>(I#DISEASE x :0.9)(S#ENFERMEDAD/DISEASE x)))
```

---
**MAPPING AXIOMS FORMAT**

Mapping axioms operate on international or language specific concept labels. They make inferences important for 
metaphor interpretation explicit.

* `M#` – prefix indicating mapping concepts that will appear in the output

A S#DISEASE causes a R#SICK entity not to function.

```
(B (name disease)(=> (^(M#CAUSE-NOT-FUNCTION e0 :0.3)(M#CAUSING-THING_F x e0 :0.3)(M#FUNCTION-AGENT y e0 :0.3)) (^ (I#DISEASE x)(R#SICK y x))))
```


If a R#CURE-AGENT cures a S#DISEASE, then it causes the S#DISEASE not to exist.

```
(B (name cure)(=> (^(M#CAUSE-NOT-EXIST e1 :0.3)(M#CAUSING-THING_E y e1 :0.3)(M#EXISTING-THING x e1 :0.3)) (^ (I#CURE e0)(R#CURE-AGENT y e0)(R#SICK x d)(S#DISEASE d))))
```

NOTE: don’t use general predicates like CAUSE, NOT in isolation (use more complex predicates like CAUSE-NOT-EXIST instead), 
because they can be unexpectedly unified during abductive inference.

Total weight of these axioms should be <1. The more predicates there are on the right-hand-side, the lower should be total weight of the axiom be.

Current mapping axioms can be found [here](https://github.com/metaphor-adp/Metaphor-ADP/blob/master/KBs/common/economic_inequality_ontology.txt).


--

**COMPILING KB**

Compiling KB is a way to find syntactic errors in the axioms.

```
PATH_TO_HENRY/henry -m compile_kb KB_PATH -o KB_COMPILED_PATH
```

--

**RUNNING PIPELINE**

To check how the axioms work, one should run the pipeline. Instructions can be found [here](https://github.com/metaphor-adp/Metaphor-ADP/blob/master/pipelines/common/README.md).

--

**CM OUTPUT FORMAT**

If you run the pipeline using "--CMoutput" flag, then you will see conceptual metaphors detected by our pipeline 
in the input_filename.cm file. The overall output is contained in the specified output folder. 

INPUT TEXT: 

```
Poverty is a bear trap, you struggle and struggle but it can not come off
```

LOGICAL FORM:

```
(O (name 10) (^ (poverty-nn e23 x0 :1:10-1:[11001]) (bear-nn e22 x6 :1:10-2:[11004]) (of-in e21 x7 x6 :1:10-3:[ID3]) (trap-nn e20 x7 :1:10-4:[11005]) (you e19 x4 :1:10-5:[11007]) (struggle-nn e18 x4 :1:10-6:[11008]) (subset_of e17 x4 x5 :1:10-7:[ID7]) (struggle-nn e16 x3 :1:10-8:[11010]) (subset_of e15 x3 x5 :1:10-9:[ID9]) (rel e14 x7 x5 :1:10-10:[11006]) (equal e13 x0 x7 :1:10-11:[11002]) (neuter e12 x0 :1:10-12:[11012]) (not e8 x2 :1:10-13:[11014]) (come-vb x2 x0 u10 u11 :1:10-14:[11015]) (off-rb e9 x2 :1:10-15:[11016]) (!= e17 e15)))
```

HYPOTHESIS:

```
<hypothesis score="-14.5975">
poverty-nn(e23,x0) ^ bear-nn(e22,x6) ^ of-in(e21,x7,x6) ^ trap-nn(e20,x7) ^ you(e19,x4) ^ struggle-nn(e18,x4) ^ subset_of(e17,x4,x5) ^ struggle-nn(e16,x3) ^ subset_of(e15,x3,x5) ^ rel(e14,x7,x5) ^ equal(e13,x0,x7) ^ neuter(e12,x0) ^ not(e8,x2) ^ come-vb(x2,x0,u10,u11) ^ off-rb(e9,x2) ^ !=(e17,e15) ^ TS#POVERTY(x0) ^ T#ECONOMIC-INEQUALITY(_27) ^ S#CONFINEMENT(x7) ^ SS#RESTRAINTS(x7) ^ S#WAR(x4) ^ SS#FIGHT(x4) ^ I#CONFINEMENT(x7) ^ I#FIGHT(x4) ^ M#CAUSE-NOT-FUNCTION(_28) ^ M#CAUSING-THING_F(x7,_28) ^ M#CAUSE-NOT-EXIST(_29) ^ M#CAUSING-THING_E(x4,_29) ^ =(e18,e16) ^ =(x3,x4)
</hypothesis>
```

CM output:

```
{
        "targetConceptDomain": "ECONOMIC-INEQUALITY",
        "annotationMappings": [
            {
                "source": "CONFINEMENT[trap],WAR[struggle],RESTRAINTS[trap],FIGHT[struggle]",
                "explanation": "CAUSE-NOT-FUNCTION[_28], CAUSING-THING_F[poverty,trap; _28], CAUSE-NOT-EXIST[_29], CAUSING-THING_E[struggle,struggle; _29]",
                "sourceInLm": false,
                "target": "POVERTY[poverty]",
                "targetInLm": false
            }
        ],
        "targetFrame": "POVERTY",
        "targetConceptSubDomain": "POVERTY",
        "sourceConceptSubDomain": "RESTRAINTS, FIGHT",
        "sourceFrameElementSentence": "CONFINEMENT[trap],WAR[struggle],RESTRAINTS[trap],FIGHT[struggle]",
        "isiDescription": "",
        "sourceFrame": "CONFINEMENT, WAR",
        "isiAbductiveExplanation": "poverty-nn(e23,x0) ^ bear-nn(e22,x6) ^ of-in(e21,x7,x6) ^ trap-nn(e20,x7) ^ you(e19,x4) ^ struggle-nn(e18,x4) ^ subset_of(e17,x4,x5) ^ struggle-nn(e16,x3) ^ subset_of(e15,x3,x5) ^ rel(e14,x7,x5) ^ equal(e13,x0,x7) ^ neuter(e12,x0) ^ not(e8,x2) ^ come-vb(x2,x0,u10,u11) ^ off-rb(e9,x2) ^ !=(e17,e15) ^ TS#POVERTY(x0) ^ T#ECONOMIC-INEQUALITY(_27) ^ S#CONFINEMENT(x7) ^ SS#RESTRAINTS(x7) ^ S#WAR(x4) ^ SS#FIGHT(x4) ^ I#CONFINEMENT(x7) ^ I#FIGHT(x4) ^ M#CAUSE-NOT-FUNCTION(_28) ^ M#CAUSING-THING_F(x7,_28) ^ M#CAUSE-NOT-EXIST(_29) ^ M#CAUSING-THING_E(x4,_29) ^ =(e18,e16) ^ =(x3,x4)",
        "id": "10",
        "targetFrameElementSentence": "POVERTY[poverty]"
    }, 
```

Currently, some fully processed English examples can be found [here](https://github.com/metaphor-adp/Metaphor-ADP/blob/master/pipelines/English/examples/economic_inequality).
