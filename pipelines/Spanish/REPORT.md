11/6/2012 - Pipeline fully functional
./run_spanish.sh < examples/spanish_text.txt
OR
./run_spanish.sh < examples/spanish_translations.txt

Test Input file:
pipelines/Spanish/examples/spanish_text.conll.malt
OR
pipelines/Spanish/examples/spanish_translations.conll.malt

To run only proposition building: 
pipelines/Spanish/Scripts/malt_to_prop.py  pipelines/Spanish/examples/spanish_text.conll.malt
OR
pipelines/Spanish/Scripts/malt_to_prop.py  pipelines/Spanish/examples/spanish_translations.conll.malt


Test output file:
pipelines/Spanish/examples/spanish_text.props



Functions Implemented:

Verbs:
Find subject (nn with relation "suj")
Find direct object (dependent word)
Inherit head verb's sbj if no sbj is found
Handling copulas in different sentence structures

Adjectives:
Find head noun
Inherit sbj from copula "ser"

Adverb:
Find head

Prepositions:
find head noun
find complement noun
find head verb 

Nouns:
Link coreferent nouns (e.g. ministro <=> Josep_Piqué in Test output file)

Pronouns:
Find head verb for reflexive pronominal morphemes  (e.g. se esta recuperando)
Assign specific tags to male, female, person, etc...

Conjunctions:
Inherit verb/prep arguments and add "or" proposition if necessary
For nouns, copy verb and replace arguments, and add "or" proposition if necessary

Numbers:
link cardinal number to head noun
 "uno"-"diez" translated to 1-10

Negation

Relative Clauses:
"when"
"how"
"where"
"why"

WH-nominals:
"when"
"how"
"where"

~~~~~~~~~~~~~~~~~~~~~~
ISSUES:
Juan da a María un libro.
In Spanish, the patient or recipient is always marked with a preposition. So, should the third argument of the verb remain empty?

Juan preguntó dónde María leyo.
"For now, leave "where" out." (from pipelines/readme)
     - "donde" is tagged as an adverb, and thus is marked as modifying "leyo"

The two word sentences ("Juan correro", etc.) do not parse correctly

Verb tense is not currently made explicit by the tools in the pipeline
Number (plurality) is not currently made explicit by the tools in the pipeline

Treetagger tags "newspaper" as an ADJ -> changing readme sentences to use the word "magazine"