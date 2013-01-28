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

**4)** Implemented. Reuires option `--vbtense 1` to be speicied. No issues found.

**5)** Implemented. Recognises copulas in the following cases:
  
  * If `NN+NN`, no copula verb and cases of the both nouns are the same then produces predicate `equal`.
  * If `NN+[NN | PREP | ADJ]` and copula verb presents then removes copula verb and produces predicate `equal`, `compl` or makes the second argument same for both predicates (depending on dependecy relation type and tree structure).
 
  **NOTE:** pipeline doesn't remove copula verb (and any other predicate) in cases when at least one another predicate is pointing on it. For example:
  
  *"Все было очень обыкновенно."*
  
  ```prolog
быть-vb(e1,u1,u2,u3) & очень-rb(e2,e3) & обыкновенно-rb(e3,e1)
  ```

**6)** Implemented. Finds passive voices constructed with the verb *был*. No issues found.
  
**7)** Not implemented.

##NOUNS
	
**1)** Not implemented.

**2)** Implemented. Adds `of-in` predicate when noun has genetive case. Doesn't work when noun is foreign word (e.g. words *"Джон"*, *"Мери"* etc.) and parser is not able to classify case correctly.

**3)** Implemented. If option `--nnnumber 1` is speccified then produces predicate `typelt` if noun has plural form. Produces predicate `card` if numerical information is presented, parses numericals from `0` to `10`.
    
  * **BUG:** sometimes produces dublicates (`typelt(e, x, s) & typelt(e, x, s)`).
  
**4)** Not implemented. There is no such information from the current parser.

**5)** Implemented. No issues found.

##ADVERBS
	
**1)** Implemented. No issues found.
