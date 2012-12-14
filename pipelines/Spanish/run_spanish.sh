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
elif [[ $OSTYPE == "linux" ]]; then
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
MALT_OFORMAT=$ES_PIPELINE_DIR/Scripts/malt_to_prop.py

OPTIONS="-token -lemma -sgml -quiet"

TOKENIZER=$TREE_TAGGER_CMD/utf8-tokenize.perl
NLTK_TOKENIZER_DIR=$METAPHOR_DIR/external-tools/nltk_tokenizer
TOKENIZER_BIN=$NLTK_TOKENIZER_DIR/nltk_tokenizer.py
TOKENIZER_BIN=$NLTK_TOKENIZER_DIR/nltk_rtokenizer.py

MWL=$TREE_TAGGER_CMD/mwl-lookup.perl
TAGGER=$TREE_TAGGER_BIN/tree-tagger
ABBR_LIST=$TREE_TAGGER_LIB/spanish-abbreviations
PARFILE=$TREE_TAGGER_LIB/spanish-utf8.par
MWLFILE=$TREE_TAGGER_LIB/spanish-mwls-utf8

CURRENT_DIR=`pwd`
cd $MALT_DIR

if [[ $PLATFORM == "linux" ]]; then
 if [ -d "$2" ]; then
#    $TOKENIZER -a $ABBR_LIST < "${1:-/dev/stdin}" |
#    tee  $2/tokenizer_o.txt |
    python $TOKENIZER_BIN --sentid 1 --normquotes 1 < "${1:-/dev/stdin}" |
    tee $2/tokenizer_o.txt |
    $MWL -f $MWLFILE |
    $TAGGER $OPTIONS $PARFILE |
    tee $2/tagger_o.txt |
    $MALT_IFORMAT |
    tee $2/conll_o.txt |
    java -Xmx16g -jar $MALT_BIN -c $MALT_MODEL -m parse -v off |
    tee $2/malt_o.txt |
    $MALT_OFORMAT > /dev/stdout
 else
#    $TOKENIZER -a $ABBR_LIST  < "${1:-/dev/stdin}" |
    python $TOKENIZER_BIN --sentid 1 --normquotes 1 < "${1:-/dev/stdin}" |
    $MWL -f $MWLFILE |
    $TAGGER $OPTIONS $PARFILE | 
    $MALT_IFORMAT |
    #cat > temp;
    #java -Xmx16g -jar $MALT_BIN -c $MALT_MODEL -i temp -m parse -v off >temp2;
    java -Xmx16g -jar $MALT_BIN -c $MALT_MODEL -m parse -v off |
    #paste temp2 temp | cut -d "	" -f 1-10,20 |
    $MALT_OFORMAT > "${2:-/dev/stdout}"
 fi
elif [[ $PLATFORM == "darwin" ]]; then
 if [ -d "$2" ]; then
#    $TOKENIZER -a $ABBR_LIST < "${1:-/dev/stdin}" |
#    tee  $2/tokenizer_o.txt |
    python $TOKENIZER_BIN --sentid 1 --normquotes 1 < "${1:-/dev/stdin}" |
    tee $2/tokenizer_o.txt |
    $MWL -f $MWLFILE |
    $TAGGER $OPTIONS $PARFILE |
    tee $2/tagger_o.txt |
    $MALT_IFORMAT |
    tee $2/conll_o.txt |
    java -Xmx16g -jar $MALT_BIN -c $MALT_MODEL -m parse -v off |
    tee $2/malt_o.txt |
    $MALT_OFORMAT > /dev/stdout
 else
#    $TOKENIZER -a $ABBR_LIST  < "${1:-/dev/stdin}" |
    python $TOKENIZER_BIN --sentid 1 --normquotes 1 < "${1:-/dev/stdin}" |
    $MWL -f $MWLFILE |
    $TAGGER $OPTIONS $PARFILE | 
    $MALT_IFORMAT |
    #cat > temp;
    #java -Xmx16g -jar $MALT_BIN -c $MALT_MODEL -i temp -m parse -v off >temp2;
    java -Xmx16g -jar $MALT_BIN -c $MALT_MODEL -m parse -v off |
    #paste temp2 temp | cut -d "	" -f 1-10,20 |
    $MALT_OFORMAT > "${2:-/dev/stdout}"
 fi
else
    echo "Unsupported platform $OSTYPE"
fi
#rm temp temp2
cd $CURRENT_DIR