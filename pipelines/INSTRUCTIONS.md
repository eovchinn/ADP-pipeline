===============
VERBS
===============

1) Link arguments: subject - second arg, direct object - third arg, indirect object - fourth arg

```
% John gives Mary a book.
john-nn(e1,x1) & give-vb(e2,x1,x2,x3) & mary-nn(e3,x3) & book-nn(e4,x2)
```

Direct obj can be a clause; then the head of the clause should be used as the verb argument.

```
% John said that Mary read.
john-nn(e1,x1) & say-vb(e2,x1,e3,u1) & mary-nn(e4,x2) & read-vb(e3,x2,u2,u3)
```

Note that there is no "that" in the logical form above.

2) Argument control: first arguments of both verbs are the same

```
% John tried to go.
john-nn(e1,x1) & try-vb(e2,x1,e3,u1) & go-vb(e3,x1,u2,u3)
```

3) Other arguments

If in the language you are working with there are more than 3 cases which can be expressed without prepositions (e.g. Russian), then introduce additional predicates expressing these cases is need.
Use compl if you don't know how to call the additional predicates.

For example, in English

```
% John makes this house a home
john-nn(e1,x1) & make-vb(e2,x1,x2,u2) & house-nn(e3,x2) & home-nn(e4,x3) & compl(e5,e2,x3)
```

One more example, Russian instrumental

```
% Я пишу карандашом (I write with a pencil)
писать-vb(e1,x1,u1,u2) & карандаш-nn(e2,x2) & instr(e3,e1,x2)
```

Note that Russian genitive, if coming after a verb, indicates direct object

```
% Я боюсь высоты (I am afraid of heights)
бояться-vb(e2,x1,x2,u1) & высота-nn(e2,x2)
```

4) Add tense information if available from the parser (if past or future)

```
% John runs.
john-nn(e1,x1) & run-vb(e2,x1,u1,u2)

% John ran.
john-nn(e1,x1) & run-vb(e2,x1,u1,u2) & past(e3,e2)

% John will run.
john-nn(e1,x1) & run-vb(e2,x1,u1,u2) & future(e3,e2)
```

5) Copula

a) Noun+adj

```
% the book is red
red-adj(e1,x1) & book-nn(e2,x1)
```

b) Noun+noun

```
% John is my brother
john-nn(e1,x1) & brother(e2,x2) & equal(e3,x1,x2)
```

c) Noun+prep

```
% John is in the room
john-nn(e1,x1) & in-in(e2,x1,x2) & room-nn(e3,x2)
```

d) Noun+verb phrase/clause

```
% My intension is to leave/that you leave
intension-nn(e1,x1) & leave(e2,x2,u1,u2) & be(e3,x1,e2)
```

6) Passive

Subj in a passive construction is the third arg of the corresponding verb

```
% John was born in London.
john-nn(e1,x) & bear-vb(e2,u1,x,u2)
```

7) Participle

Participles should be treated as normal verbs

a) active

```
% The man building a house
man-nn(e1,x1) & build-vb(e2,x1,x2,u) & house-nn(e3,x2)
```

b) passive

```
% The house built here
build-vb(e1,u1,x1,u2) & house-nn(e2,x1)
```

============
NOUNS
============

1) Noun compounds: if there are noun compounds in the language you are working with, use the predicate "nn" to express it

```
% book store
book-nn(e1,x1) & store-nn(e2,x2) & nn(e1,x1,x2)
```

2) Genitive: always use the predicate "of-in" for expressing genitives

```
% John's book
john-nn(e1,x1) & book-nn(e2,x2) & of-in(e3,x2,x1)
```
3) Add number information if available from the parser (if plural)

```
% books
book-nn(e1,x1) & typelt(e2,x1,s)
```

4) If there is other information available from the parser (e.g. type of the named entity), please add it

```
% John went to London.
john-nn(e1,x1) & per(e2,x1) & go-vb(e3,x1,u1,u2) & to-in(e4,e3,x2) & london-nn(e5,x2) & loc(e6,x2)
```

5) Coreferent Nouns

```
%Barrack_Obama, the president, said ...
Barrack_Obama-nn(e1,x1) & president-nn(e2,x1) & said-vb(e3,x1,u1,u2)
```

==============
ADJECTIVES
==============

Adjectives share the second argument with the noun they are modifying

```
% red book
red-adj(e1,x1) & book-nn(e2,x1)
```

Russian: adj + verb

```
% должен идти
должен-adj(e1,x1) & идти-vb(e2,x1,u1,u2) & compl(e3,e1,e2)
```

Russian: adj + noun dat

```
% близкий мне
близкий-adj(e1,x1)& person(e2,x2) & compl(e3,e1,x2)
```

==============
ADVERBS
==============

Second args of adverbs are preds they are modifying

```
% John runs fast.
run-vb(e1,x1,u1,u2) & fast-rb(e2,e1)

& still obvious
still-rb(e1,e2) & obvious-adj(e1,e3)

& very fast 
very-rb(e1,e2) & fast-rb(e1,e3)
```

==============
PREPOSITIONS
==============

1) Verb+noun

```
% John goes to school.
go-vb(e1,x1,u1,u2) & to-in(e2,e1,x2) & school-nn(e3,x2)
```

2) Noun+noun

```
% book for Mary
book-nn(e1,x1) & for-in(e2,x1,x2) & mary-nn(e2,x2)
```

3) Second arg is a prep

```
% John goes out of the store.
go-vb(e1,x1,u1,u2) & out-in(e2,e1,u3) & of-in(e3,e2,x2) & store-nn(e4,x2) 
```


4) Verb+verb

```
% Thank you for not smoking.
thank-vb(e1,u1,x1,u2) & person(e1,x1) & for-in(e3,e1,e4) & not(e4,e5) & smoke-vb(e5,u3,u4,u5)
```

5) Adj+noun

```
% This solution is good for John.
solution-nn(e1,x1) & good-adj(e2,x1) & for-in(e3,e2,x2) & john-nn(e4,x2)
```

=====================
PRONOUNS
=====================

```
"he" -> male(e1,x1)
"she"->female(e1,x1)
"it"->neuter(e1,x1)
"I"->person(e1,x1)
"we"->person(e1,x1) & typelt(e2,x1,s)
"you"->person(e1,x1)
"they"->thing(e1,x1) & typelt(e2,x1,s)
"this","that" -> thing(e1,x1)
```

Reflexives:

```
% John washed himself
john-nn(e1,x1) & wash-vb(e2,x1,x1,u)
```

Please don't forget possessive pronouns:

```
% his book
book-nn(e1,x1) & male(e2,x2) & of-in(e3,x1,x2)
```

=====================
NUMERALS
=====================

Use card/3 predicate to express numerals (third argument is a number)

```
% John has two books.
have-vb(e1,x1,x2,u1) & book-nn(e2,x2) & card(e3,x2,2)
```

Convert numbers from 0 to 9 into digits, otherwise use lemmas as third args of card

=====================
COORDINATIONS
=====================

Coordinative conjuctions (except for "and") are 3-place predicates.

```
% John sits and reads.
john-nn(e1,x1) & sit-vb(e2,x1,u1,u2) & read-vb(e3,x1,u1,u2)

% House as a Mirror of Self
house-nn(e1,x1) & as(e2,x1,x2) & mirror-nn(e3,x2)
```

If a dependent of a head (it can be any POS, although examples below include verbs only) is a coordination, then this head needs to be duplicated; both duplicates should be assigned the same word ID. Note that there can be more than two coordinated elements and sometimes "and" and "or" can be expressed by a comma. 

```
% John sits or runs.
john-nn(e1,x1) & sit-vb(e2,x1,u1,u2) & run-vb(e3,x1,u1,u2) & or(e4,e2,e3)

% John and Mary run.
john-nn(e1,x1) & run-vb(e2,x1,u1,u2) & mary-nn(e3,x2) & run-vb(e4,x2,u3,u4)

% John reads a book and a newspaper
john-nn(e1,x1) & read-vb(e2,x1,x3,u2) & book-nn(e3,x2) & read-vb(e4,x1,x4,u2) & newspaper-nn(e5,x4)

% John reads a book or a newspaper
john-nn(e1,x1) & read-vb(e2,x1,x3,u2) & book-nn(e3,x2) & read-vb(e4,x1,x4,u2) & newspaper-nn(e5,x4) & or(e6,e2,e4)
```

=====================
SUBORDINATE CLAUSES
=====================

1) Relative clauses

```
% The man who lives in this house
man-nn(e1,x1) & live-vb(e2,x1,u1,u2) & person(e3,x1)

% The house that/which was built
house-nn(e1,x1) & build-vb(e2,u1,x1,u2)

% the man whom I saw
man-nn(e1,x1) & see-vb(e3,x2,x1,u1) & person(e4,x1) & person(e5,x2)

% the place where I live
place-nn(e1,x1) & live-vb(e2,x2,u1,u2) & loc(e3,x1,e2) & person(e5,x2)

% the reason why I leave
reason-nn(e1,x1) & live-vb(e2,x2,u1,u2) & reason(e3,x1,e2) & person(e5,x2)

% the day when I left
day-nn(e1,x1) & leave-vb(e2,x2,u1,u2) & time(e3,x1,e2) & person(e5,x2)

% the way how I left
way-nn(e1,x1) & leave-vb(e2,x2,u1,u2) & manner(e3,x1,e2) & person(e5,x2)

% the place I live
place-nn(e1,x1) & live-vb(e2,x2,u1,u2) & compl(e3,x1,e2) & person(e5,x2)

% the reason I leave
reason-nn(e1,x1) & leave-vb(e2,x2,u1,u2) & compl(e3,x1,e2) & person(e5,x2)
```

2) WH-nominals (noun clauses)

```
% I know that he comes
know-vb(e1,x1,e2,u1) & come-vb(e2,x2,u2,u3) & male(e3,x2) & person(e5,x1)

% I'm sure (that) he comes
sure-adj(e1,x1) & come-vb(e2,x2,u1,u2) & compl(e3,e1,e2) & male(e4,x2) & person(e5,x1)

% I know what you want
know-vb(e1,x1,e3,u2) & want-vb(e2,x2,x3,u4) & wh(e3,x3) & thing(e4,x3) & person(e5,x2) & person(e6,x1)

% I know whom you saw
know-vb(e1,x1,e3,u2) & saw-vb(e2,x2,x3,u4) & wh(e3,x3) & person(e4,x3) & person(e5,x2) & person(e6,x1)

% I know where you live
know-vb(e1,x1,e3,u2) & live-vb(e2,x2,u3,u4) & wh(e3,x3) & loc(e4,x3,e2) & person(e5,x2)& person(e6,x1)

% I know how you live
know-vb(e1,x1,e3,u2) & live-vb(e2,x2,u3,u4) & wh(e3,x3) & manner(e4,x3,e2) & person(e5,x2) & person(e6,x1)

% I know when you come
know-vb(e1,x1,e3,u2) & come-vb(e2,x2,u3,u4) & wh(e3,x3) & time(e4,x3,e2) & person(e5,x2) & person(e6,x1)

% I know why you go
know-vb(e1,x1,e3,u2) & go-vb(e2,x2,u3,u4) & wh(e3,x3) & reason(e4,x3,e2) & person(e5,x2) & person(e6,x1)

% Whatever you do
do-vb(e1,x1,x2,u1) & thing(e2,x2) & person(e3,x1)

% Wherever you go
go-vb(e1,x1,u1,u2) & loc(e2,x2,e1) & person(e3,x1)
```

The same treatment for: whoever, whenever, however

3) because, while, when, as, after, since...

```
% John reads , because he has time .
read-vb(e1,x1,u1,u2) & have-vb(e2,x2,u3,u4) & because-in(e3,e1,e2) & male(e4,x2)
```

4) if ... then

```
% If John comes then I meet him .
john-nn(e1,x1) & come-vb(e2,x1,u1,u1) & person(e3,x2) & meet-vb(e4,x2,x3,u3) & male(e5,x3) & imp(e6,e2,e4)
```

=====================
NEGATION
=====================

Represent all negation using the predicate not/2

```
% John does not read
read-vb(e1,x1,u1,u2) & not(e2,e1)

% not John
not(e1,x1) & john-nn(e2,x1)
```

Russian: нет + genitive

```
% нет меня
not(e1,e2) & be(e2,x1,u) & person(e3,x1)
```

=====================
QUESTIONS
=====================

```
% What did you do?
do-vb(e1,x1,x2,u2) & whq(e2,x2) & thing(e3,x2) & person(e4,x1)

% Whom did you see?
see-vb(e1,x1,x2,u2) & whq(e2,x2) & person (e3,x2) & person(e4,x1)

% When did you come?
come-vb(e1,x1,u1,u2) & whq(e2,x2) & time(e3,x2,e1) & person(e4,x1)

% Why did you come?
come-vb(e1,x1,u1,u2) & whq(e2,x2) & reason(e3,x2,e1) & person(e4,x1)

% How did you come?
come-vb(e1,x1,u1,u2) & whq(e2,x2) & manner(e3,x2,e1) & person(e4,x1)

% Where did you come?
come-vb(e1,x1,u1,u2) & whq(e2,x2) & loc(e3,x2,e1) & person(e4,x1)
```
