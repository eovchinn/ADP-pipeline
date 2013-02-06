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

**3)** Implemented.

* Treats numerals. If option `--nnnumber 1` is speccified then produces predicate `typelt` if noun has plural form. Produces predicate `card` if numerical information is presented, maps numericals from `ноль`/ `нулевой` to `десять` / `десятый` into numerical form, otherwise leaves them as is.

  Known issues:
	
  Depending on the parser's output can sometimes misrecognize numericals:
	
  ```
  % Одна на свете , как она управится со столькими миллионами ?
  миллион-nn(e6,x5) & card(e7,x5,столькими) & typelt(e8,x5,s1)
  ```
  
  ```
  9	столькими	столько	M	M	Mc--i	10	количест	_	_
  10	миллионами	миллион	N	N	Ncmpin	8	предл	_	_
  ```
* Handles genitive cases to produce predicate `of-in` if such feature is presented in the parser's output.

  
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

**1)** Maps pronuouns *"он"*, *"она"*, *"оно"*, *"я"*, *"мы"*, *"ты"*, *"вы"*, *"они"*, *"это"*, *"эти"* into according predicates such as `male`, `female`, `person` etc., then handles them as nouns. Treats any other pronoun, such as *"который"*, *"там"*, *"тут"*, etc. Or does not treats them if any other predicate shares at least one argument with them, for example:

```
% Я его оставил под открытым небом на палубе , возле скамейки , на которой рассчитывал сидеть во время плавания , присматривая за сохранностью багажа .

person(e1,x1) & male(e2,x2) & оставить-vb(e3,x1,x2,u1) &
под-in(e4,e3,x3) & открытый-adj(e5,x3) &
небо-nn(e6,x3) & на-in(e7,e3,x4) &
палуба-nn(e8,x4) & возле-in(e9,e3,x5) &
скамейка-nn(e10,x5) & на-in(e11,e13,x6) &
который-pr(e12,x6) & рассчитывать-vb(e13,x1,e14,u2) &
сидеть-vb(e14,x1,e18,u3) & во-in(e15,e14,x7) &
время-nn(e16,x7) & плавание-nn(e17,x8) &
присматривать-vb(e18,x1,u4,u5) & за-in(e19,e18,x9) &
сохранность-nn(e20,x9) & багаж-nn(e21,x10) &
of-in(e22,x7,x8) & of-in(e23,x9,x10)
```

It's impossible to determine that the word *"которой"* is pointing to *"скамейка"* due to incorrect parser's output, so the pronoun has not been treated.


**2)** Does not handle reflexies. There is no such information from the current parser.

**3)** Not implemented.

##NUMERALS

Implemented. See **NOUNS#3** for details.

##COORDINATIONS
