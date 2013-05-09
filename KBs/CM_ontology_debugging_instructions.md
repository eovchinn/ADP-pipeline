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

Mapping axioms operate on international or language specific concepts. The make the inference important for metaphor interpretation explicit.

A DISEASE causes a SICK entity not to function.

```
(B (name disease)(=> (^(M#CAUSE-NOT-FUNCTION e0 :0.3)(M#CAUSING-THING_F x e0 :0.3)(M#FUNCTION-AGENT y e0 :0.3)) (^ (I#DISEASE x)(R#SICK y x))))
```


If a CURE-AGENT cures a DISEASE, then it causes the DISEASE not to exist.

```
(B (name cure)(=> (^(M#CAUSE-NOT-EXIST e1 :0.3)(M#CAUSING-THING_E y e1 :0.3)(M#EXISTING-THING x e1 :0.3)) (^ (I#CURE e0)(R#CURE-AGENT y e0)(R#SICK x d)(S#DISEASE d))))
```

NOTE: don’t use general predicates like CAUSE, NOT, because they can be unexpectedly unified during abductive inference.

Total weight of these axioms should be <1. The more predicates there are on the right-hand-side, the lower should be total weight of the axiom be.

Current mapping axioms can be found [here](https://github.com/metaphor-adp/Metaphor-ADP/blob/master/KBs/common/economic_inequality_ontology.txt) 


--

**COMPILING KB**

Compiling KB is a way to find syntactic errors in the axioms.

```
PATH_TO_HENRY/henry -m compile_kb KB_PATH -o KB_COMPILED_PATH

```

--

**RUNNING PIPELINE**

To check how the axioms work, one should run the pipeline. Instructions can be found [here](https://github.com/metaphor-adp/Metaphor-ADP/blob/master/pipelines/common/README.md)
