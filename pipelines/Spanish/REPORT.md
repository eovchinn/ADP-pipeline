##VERBS

###1) Correctly inserts subjects and  direct objects. The direct object can be a noun or a clause.

```
% Los mexicanos queremos construir un país mejor para nuestros hijos . 
[11002]:mexicano-nn(e1,x1) & [11003]:querer-vb(e2,x1,e3,u3) & [11004]:construir-vb(e3,x1,x2,u6) ...
```

Indirect object nouns are expressed via prepositions. Pronouns can occur as indirect objects, especially with reflexives. These are inserted as the 4th argument of verbs, but we may want to take a closer look at some examples.


###2) Argument control is handled correctly.

```
% Los mexicanos queremos construir un país mejor para nuestros hijos . 
[11002]:mexicano-nn(e1,x1) & [11003]:querer-vb(e2,x1,e3,u3) & [11004]:construir-vb(e3,x1,x2,u6) ...
```

###3) No other arguments are added to verbs

###4) Tense information is not added

###5) Copulas are handled correctly.
######a) Noun+adj

```
% el libro es rojo .
"The book is red."
[15002]:libro-nn(e1,x1) & [15004]:rojo-adj(e3,x1)
```

######b) Noun+noun

```
% México ya no es un país de una sola voz .

[17001]:méxico-nn(e1,x1) & [17002]:ya-rb(e2,e9) & [17003]:not(e3,e9) & [17006]:país-nn(e5,x2) & equal(e9,x1,x2) ...
```

######c) Noun+prep

```
% Juan está en la habitación .

[17001]:Juan-nn(e1,x1) & [17003]:en-in(e3,x1,x2) & [17005]:habitación-nn(e4,x2)
```

######d) Noun+VP

```
% Este personaje es doblado por David Gallagher en la versión americana y europea .
"This character is voiced by David Gallagher in the American and European version."
[43002]:personaje-nn(e1,x1) & [43004]:doblar-vb(e3,x1,u5,u6) & be(e17,x1,e3) ...
```

###6) Passives are handled correctly

```
% La canción está divida en partes .
"The song is divided in parts."
[1247002]:canción-nn(e1,x1) & [1247004]:dividir-vb(e3,u5,x1,u6) & [1247005]:en-in(e4,u7,x2) & [1247006]:parte-nn(e5,x2) 
```

###7) Participles are treated like other verbs


##NOUNS

###1) Compound nouns are often expressed as two nouns joined by the preposition "de".

```
% el piso de concreto 
"the concrete floor"
[3002]:piso-nn(e1,x1) & [3003]:de-in(e2,x1,e3) & [3004]:concreto-adj(e3,u3)
```

###2) Genetive: Possessives in Spanish are either expressed with pronouns or the preposition "de".

###3) The pipeline doesn't currently provide number information.

###4) There is no additional information from the parser.

###5) Coreference is not handled.

##ADJECTIVES
These handled correctly.

##ADVERBS
These are handled correctly.

##PREPOSITIONS

###1) Verb+noun

```
% México no ha logrado *avanzar* a la velocidad necesaria *en* el *combate* a la desigualdad .
"Mexico has failed to progress fast enough in the fight against inequality"
[25001]:méxico-nn(e1,x1) & [25002]:not(e2,e4) & [25004]:lograr-vb(e4,u6,x1,u7) & [25005]:avanzar-vb(e5,u8,u9,u10) 
& [25006]:a-in(e6,e5,x2) & [25008]:velocidad-nn(e7,x2) & [25009]:necesario-adj(e8,x2) & [25010]:en-in(e9,e5,x3) 
& [25012]:combate-nn(e10,x3) & [25013]:a-in(e11,x3,x4) & [25015]:desigualdad-nn(e12,x4)
```

###2) Noun+noun

```
% el sector financiero ya no es un *flanco* vulnerable *de* nuestra *economía* .
"the financial sector is no longer a vulnerable flank of our economy"
[4002]:sector-nn(e1,x1) & [4003]:financiero-adj(e2,x1) & [4004]:ya-rb(e3,e11) & [4005]:not(e4,e11) 
& [4008]:flanco-nn(e6,x2) & equal(e11,x1,x2) & [4009]:vulnerable-adj(e7,x2) & [4010]:de-in(e8,x2,x3) 
& [4011]:nuestra-adj(e9,x3) & [4012]:economía-nn(e10,x3)
```

###3) Second arg is a prep

###4) Verb+Verb

```
% Seguiremos *combatiendo* la inflación *para* *lograr* un crecimiento económico sostenido en provecho de todos .
"We continue to fight inflation to achieve sustained economic growth for the benfit of all."
[6001]:seguir-vb(e1,u4,e2,u3) & *[6002]:combatir-vb(e2,e8,x1,u6)* & [6004]:inflación-nn(e3,x1) 
& [6005]:para-in(e4,e2,e5) & [6006]:lograr-vb(e5,u9,x2,u11) ...
```

###5) Adj+noun

###6) Adj+verb
```
% Su decisión podría ser muy *importante* *para* *determinar** quién gana el estado de Virginia y la Casa Blanca .
"His decision could be very important in determining who wins the state of Virginia and the White House."
[11001]:thing(e1,x1) & [11002]:decisión-nn(e2,x2) & [11003]:poder-vb(e3,x2,e4,u3) & [11005]:muy-rb(e5,e6) 
& [11006]:importante-adj(e6,x2) & [11007]:para-in(e7,e6,e10) & [11008]:determinar-vb(e8,u11,u12,u13)... 
```
## Pronouns
Pronouns are handled correctly for the most part. 
Possessives are tricky due to their connections to reflexives and passives.

```
% Estoy aquí porque , desde que asumí mi tarea en el Sindicato de Actores .
"I'm here because I took my job at the Screen Actors Guild
[625001]:estar-vb(e1,u1,e14,u3) & [625002]:aquí-rb(e2,e1) & [625003]:porque-in(e3,e1,e14) 
& [625005]:desde-in(e4,e14,e5) & [625007]:asumí-vb(e5,x2,u10,u11) & [625008]:person(e6,x1) & of-in(e28,x2,x1) 
& [625009]:tarea-nn(e7,x2) & [625010]:en-in(e8,e5,x3) & [625012]:sindicato-nn(e9,x3) & [625013]:de-in(e10,x3,x4) 
& [625014]:actor-nn(e11,x4) 
```
This case ( _mi_ / _my_ ) is handled well. There is no passive voice or reflexive in the sentence.


## Numerals
Numbers 0-9 are changed into digits, otherwise, lemmas are used.

```
%dos grilletes
"two shackles"
[1009]:dos-card(e8,x3,2) & [1010]:grilletes-nn(e9,x3)

%ochenta
"eighty"
ochenta-card(e11,u15,ochenta)
```

## COORDINATIONS
Dependent heads are correctly duplicated. Commas are not processed as coordinating conjunctions

```
% Sólo el ciudadano organizado puede ser actor *y* constructor de su propio destino .
"Only the organized citizen can be the actor and builder of his/her own destiny."
[24001]:sólo-rb(e1,e4) & [24003]:ciudadano-nn(e2,x1) & [24004]:organizar-vb(e3,x1,e4,u4) 
& [24005]:poder-vb(e4,e5,u6,u7) & [24007]:actor-adj(e6,u8) & [24009]:constructor-nn(e7,x2)
& [24010]:de-in(e8,x2,e12) & [24011]:thing(e12,x12) & [24012]:propio-adj(e10,x2) & [24013]:destino-nn(e11,x4)

% ¿ Cómo puedes saber si estás usando HTTPS *o* HTTP ?
"How can you tell if you are using HTTPS or HTTP?"
[14002]:whq(e1,x1) & manner(e9,x1,e6) & [14003]:poder-vb(e2,u4,e3,u3) & [14004]:saber-vb(e3,u4,e1,u6) 
& [14005]:si-in(e4,e6,u8) & [14007]:usar-vb(e6,u4,x2,u14) & [14008]:https-nn(e7,x2) & [14007]:usar-vb(e10,u4,x3,u14) 
& [14010]:http-nn(e8,x3) & or(e10,e7,e8)

%Procedamos *con* sensatez y valentía 
"Proceed with wisdom and courage"
[12001]:procedamos-vb(e1,u1,u2,u3) & [12002]:con-in(e2,e1,x1) & [12003]:sensatez-nn(e3,x1) 
& [12002]:con-in(e15,e1,x2) & [12005]:valentía-nn(e4,x2)
```

## SUBORDINATE CLAUSES

###1) Relative Clauses
Relative clauses with "que" are not currently supported. 
The main reason that "que" is difficult to process is that it has a variety of functions. 
It can be translated as, at least, "that, which, who, what, whether, because, and why."
The current pipeline does not do a good job of distinguishing which use is which, so any rule that can be written to handle one of the phenomena, will be wrong more often that it is right.
If more than one rule is written, they would overlap and cancel each other out.
The only use currently supported is when "que" means "what" in a question, as the punctuation disambiguates the usage (see section on Questions below).

###2) Wh-nominals

```
% En este punto no sé por *quién* voy a votar .
At this point I do not know who I will vote for.
[10001]:en-in(e1,e4,x1) & [10003]:punto-nn(e2,x1) & [10004]:not(e3,e4) & [10005]:saber-vb(e4,u4,e7,u6) 
& [10006]:por-in(e5,e7,e6) & [10007]:wh(e6,x2) & person(e10,x2) ...

% Lo más emocionante es *cuando* las parejas vienen a comprometerse .
"The most exciting this is when couples come to compromise."
[12003]:más-rb(e1,e2) & [12004]:emocionante-adj(e2,u2) & [12006]:wh(e4,x1) & time(e11,x1,e6) 
& [12008]:pareja-nn(e5,x2) & [12009]:venir-vb(e6,x2,u7,u8) ...
```

###3) because, while, when, after, since, ...

```
% Juan lee , porque tiene tiempo .
"John reads, because he has time."
[30001]:Juan-nn(e1,x1) & [30002]:leer-vb(e2,x1,e5,u3) & [30004]:porque-in(e3,e2,e4) 
& [30005]:tener-vb(e4,x1,x2,u9) & [30006]:tiempo-nn(e5,x2)
```

## NEGATION

```
% Juan *no*
"Not John"
[32001]:Juan-nn(e1,x1) & [32002]:not(e2,x1)

% México ya **no** quiere 
"Mexico does not want"
[33001]:méxico-nn(e1,x1) & [33002]:ya-rb(e2,e4) & [33003]:not(e3,e4) & [33004]:querer-vb(e4,x1,e5,u5) 
```

## QUESTIONS

```
% ¿ *Qué* es el RFC ?
"What is RFC?"
[126002]:whq(e1,x1) & [126002b]:thing(e4,x1,e2) & [126003]:ser-vb(e2,x2,e1,u3) & [126005]:RFC-nn(e3,x2)

% ¿ A *quién* ves ?
"Whom did you see?"
[53002]:a-in(e1,e3,e2) & [53003]:whq(e2,x1) & person(e4,x1) & [53004]:ver-vb(e3,u3,e2,u5)

% ¿ *Cuándo* llegaste ?
"When did you come?"
[54002]:whq(e1,x1) & time(e3,x1,e2) & [54003]:llegar-vb(e2,u1,e1,u3)

% ¿ Por *qué* has venido ?
"Why did you come?"
[55002]:por-in(e1,e4,e2) & [55003]:whq(e2,x1) & [55003b]:thing(e5,x1,e1) & [55005]:venir-vb(e4,u6,e2,u8)
% ¿ Cómo qué has venido ?

% ¿ *Cómo* puedes saber si estás usando HTTPS o HTTP ?
"How can you tell if you are using HTTPS or HTTP?"
[14002]:whq(e1,x1) & manner(e9,x1,e6) & [14003]:poder-vb(e2,u4,e3,u3) & [14004]:saber-vb(e3,u4,e1,u6) 
& [14005]:si-in(e4,e6,u8) & [14007]:usar-vb(e6,u4,x2,u14) & [14008]:https-nn(e7,x2) 
& [14007]:usar-vb(e10,u4,x3,u14) & [14010]:http-nn(e8,x3) & or(e10,e7,e8)

% ¿ De *dónde* vienes ?
"Where did you come?"
[57002]:de-in(e1,e3,u2) & [57003]:whq(e2,x1) & loc(e4,x1,e1) & [57004]:venir-vb(e3,u3,e2,u5)

```


