#DETAILED REPORT

##VERBS
	
**1)** There is an issue with recognising indirect object when pipeline cannot retrieve information about its case (it should be *accusative* or *genitive*) from MALT (usually it happens with foreign words such as *"Мери"*):

*"Джон дает Мери книгу."*

```prolog
джон-nn(e1,x1) & давать-vb(e2,x1,x2,u1) & мери-nn(e3,x3) & книга-nn(e4,x2)				
```

MALT output:


```
3	Мери	мери	N	N	Npfsny	2	1-компл	_	_
```

Here the word *"Мери"* has a nominative case (Npfs ***n*** y).
	
**2)** Implemented. No issues found.

**3)** Implemented handling `instr` predicate rule and handling genetives. No issues found.

**4)** Implemented. (pipline) Requires option `--vbtense 1` to be speicied. No issues found.

**5)** Implemented. Recognises copulas in the following cases:
  
  * If `NN+NN`, no copula verb and cases of the both nouns are the same then produces predicate `equal`.
  * If `NN+[NN | PREP | ADJ]` and copula verb presents then removes copula verb and produces predicate `equal`, `compl` or makes the second argument same for both predicates (depending on dependecy relation type and tree structure).
 
  **NOTE:** pipeline doesn't remove copula verb (and any other predicate) in cases when at least one another predicate is pointing on it. For example:
  
  *"Все было очень обыкновенно."*
  
  ```prolog
быть-vb(e1,u1,u2,u3) & очень-rb(e2,e3) & обыкновенно-rb(e3,e1)
  ```

**6)** Implemented. Finds passive voices constructed with the verb *был*. No issues found.
  
**7)** Implemented. No issues found.

##NOUNS
	
**1)** Not implemented.

**2)** Implemented. (pipeline) Adds `of-in` predicate when noun has genetive case. Doesn't work when noun is foreign word (e.g. words *"Джон"*, *"Мери"* etc.) and parser is not able to classify case correctly.

**3)** Implemented. Treats numerals. If option `--nnnumber 1` is speccified then produces predicate `typelt` if noun has plural form. Produces predicate `card` if numerical information is presented, maps numericals from `ноль`/ `нулевой` to `десять` / `десятый` into numerical form, otherwise leaves them as is.
  
**4)** Not implemented. There is no such information from the current parser.

**5)** Implemented. No issues found.

##ADVERBS
	
**1)** Implemented. No issues found.

##PREPOSITIONS

**1)** Implemented. No issues found.

**2)** Implemented. No issues found.

**3)** Not implemented. No such constructions in the Russian language.

**4)** Not implemented. No such constructions in the Russian language.

**5)** Implemented. No issues found.

##PRONOUNS

**1)** Maps pronuouns *"он"*, *"она"*, *"оно"*, *"я"*, *"мы"*, *"ты"*, *"вы"*, *"они"*, *"это"*, *"эти"* into according predicates such as `male`, `female`, `person` etc., then handles them as nouns. Treats other predicates, such as *"который"*, or does not treats them if any other predicate shares at least one argument with them, for example:

```prolog
% Я его оставил под открытым небом на палубе , возле скамейки , на которой рассчитывал сидеть во время плавания , присматривая за сохранностью багажа .
id(193).
person(e1,x1) & male(e2,x2) & [193003]:оставить-vb(e3,x1,x2,u1) &
[193004]:под-in(e4,e3,x3) & [193005]:открытый-adj(e5,x3) &
[193006]:небо-nn(e6,x3) & [193007]:на-in(e7,e3,x4) &
[193008]:палуба-nn(e8,x4) & [193010]:возле-in(e9,e3,x5) &
[193011]:скамейка-nn(e10,x5) & [193013]:на-in(e11,e13,x6) &
[193014]:который-pr(e12,x6) & [193015]:рассчитывать-vb(e13,x1,e14,u2) &
[193016]:сидеть-vb(e14,x1,e18,u3) & [193017]:во-in(e15,e14,x7) &
[193018]:время-nn(e16,x7) & [193019]:плавание-nn(e17,x8) &
[193021]:присматривать-vb(e18,x1,u4,u5) & [193022]:за-in(e19,e18,x9) &
[193023]:сохранность-nn(e20,x9) & [193024]:багаж-nn(e21,x10) &
of-in(e22,x7,x8) & of-in(e23,x9,x10)
```
**2)** Does not handle reflexies. There is no such information from the current parser.

**3)** Not implemented.

##NUMERALS

Implemented. See **NOUNS#3** for more details.

##COORDINATIONS
