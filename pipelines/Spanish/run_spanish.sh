#! /bin/bash
# Variable $METAPHOR_DIR should point to the root of 
# Metaphor-ADP directory (e.g. ~/code/Metaphor-ADP directory)
# usage:
#   $ ./run_spanish.sh <input> <output>
# or
#   $ ./run_spanish.sh <input>
# or
#   $ ./run_spanish.sh
# <input> and <output> should be absolute paths.

# export METAPHOR_DIR=~/code/Metaphor-ADP

if [[ $OSTYPE == "linux-gnu" ]]; then
   PLATFORM="linux"
elif [[ $OSTYPE == "darwin12" ]]; then
   PLATFORM="darwin"
elif [[ $OSTYPE == "darwin11" ]]; then
   PLATFORM="darwin"
elif [[ $OSTYPE == "darwin10" ]]; then
   PLATFORM="darwin"
elif [[ $OSTYPE == "darwin9" ]]; then
   PLATFORM="darwin"
fi

TREE_TAGGER_BIN=$METAPHOR_DIR/external-tools/tree-tagger-3.2/$PLATFORM/bin
TREE_TAGGER_CMD=$METAPHOR_DIR/external-tools/tree-tagger-3.2/$PLATFORM/cmd
TREE_TAGGER_LIB=$METAPHOR_DIR/external-tools/tree-tagger-3.2/$PLATFORM/lib
TREE_TAGGER_OPT="-lemma -token -sgml"

MALT_DIR=$METAPHOR_DIR/external-tools/malt-1.5
#MALT_ES_DIR=$METAPHOR_DIR/external-tools/malt-es

ES_PIPELINE_DIR=$METAPHOR_DIR/pipelines/Spanish

SPANISH_TT=ES_PIPELINE_DIR/tree-tagger-spanish-utf8

MALT_BIN=malt.jar
MALT_MODEL=ancora_model.mco
MALT_IFORMAT=$ES_PIPELINE_DIR/Scripts/to_malt.py

BIN=../../external-tools/tree-tagger-3.2/darwin/bin
CMD=../../external-tools/tree-tagger-3.2/darwin/cmd
LIB=../../external-tools/tree-tagger-3.2/darwin/lib

OPTIONS="-token -lemma -sgml -quiet"

TOKENIZER=$TREE_TAGGER_CMD/utf8-tokenize.perl
MWL=$TREE_TAGGER_CMD/mwl-lookup.perl
TAGGER=$TREE_TAGGER_BIN/tree-tagger
ABBR_LIST=$TREE_TAGGER_LIB/spanish-abbreviations
PARFILE=$TREE_TAGGER_LIB/spanish-utf8.par
MWLFILE=$TREE_TAGGER_LIB/spanish-mwls-utf8

CURRENT_DIR=`pwd`
cd $MALT_DIR

if [[ $PLATFORM == "linux" ]]; then
    $TOKENIZER_BIN < "${1:-/dev/stdin}" | # < $IFILE
    $TAGGER_BIN $TREE_TAGGER_OPT $TAGGER_PAR |
    #$LEMMATIZER_BIN -l $MALT_RU_DIR/msd-ru-lemma.lex.gz -p $MALT_RU_DIR/wform2011.ptn1 -c $MALT_RU_DIR/cstlemma |
    $MALT_IFORMAT #| 
    #java -Xmx16g -jar $MALT_BIN -c $MALT_MODEL -m parse |
    #python $ES_PIPELINE_DIR/malt_ru.py > "${2:-/dev/stdout}" # > $IFILE
elif [[ $PLATFORM == "darwin" ]]; then
    $TOKENIZER -a $ABBR_LIST $* |
    # recognition of MWLs
    $MWL -f $MWLFILE |
    # tagging
    $TAGGER $OPTIONS $PARFILE | 
    $MALT_IFORMAT | 
    java -Xmx16g -jar $MALT_BIN -c $MALT_MODEL -m parse -v off |
    python $ES_PIPELINE_DIR/Scripts/malt_to_prop.py > "${2:-/dev/stdout}"
else
    echo "Unsupported platform $OSTYPE"
fi

cd $CURRENT_DIR