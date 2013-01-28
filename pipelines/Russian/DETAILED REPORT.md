#DETAILED REPORT

##VERBS
	
**1)** There is an issue with recognising indirect object when pipeline cannot retrieve information about its case (it should be *accusative* or *genitive*) from MALT (usually it happens with foreign words such as *"Мери"*):

*Джон дает Мери книгу.*

```prolog
джон-nn(e1,x1) & давать-vb(e2,x1,x2,u1) & мери-nn(e3,x3) & книга-nn(e4,x2)				
```

MALT output:


```
3	Мери	мери	N	N	Npfsny	2	1-компл	_	_
```

Here the word *Мери* has a nominative case (Npfs ***n*** y).
	
**2)** Implemented. No issues found.

**3)** Implemented handling `instr` predicate rule and handling genetives. No issues found.

**4)** Implemented. Reuires option `--vbtense 1` to be speicied. No issues found.

**5)** Recognises copulas in the following cases:
  
  * If `NN+NN`, no copula verb and cases of the both nouns are the same then produces predicate `equal`.
  * If `NN+[NN | PREP | ADJ]` and copula verb presents then removes copula verb and produces predicate `equal`, `compl` or makes the second argument same for both predicates (depending on dependecy relation type and tree structure).