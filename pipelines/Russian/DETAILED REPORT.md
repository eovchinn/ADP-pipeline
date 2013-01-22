#DETAILED REPORT

* **VERBS**
	
	1. There is an issue with recognising indirect object when pipeline cannot retrieve information about its case (it should be *accusative* or *genitive*) from MALT (usually it happens with foreign words such as *"Мери"*):
	

	```	
	% Джон дает Мери книгу .
	id(1).
	[1001]:джон-nn(e1,x1) & [1002]:давать-vb(e2,x1,x2,u1) &
	[1003]:мери-nn(e3,x3) & [1004]:книга-nn(e4,x2)				
	```
	
	MALT output:
	

	```
	3	Мери	мери	N	N	Npfsny	2	1-компл	_	_

	```
	
	Here the word *Мери* has a nominative case (Npfs***n***y).