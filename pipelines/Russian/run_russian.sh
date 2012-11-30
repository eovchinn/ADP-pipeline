#! /bin/bash
# Variable $METAPHOR_DIR should point to the root of 
# Metaphor-ADP directory (e.g. ~/code/Metaphor-ADP directory)
# usage:
#   $ ./run_russian.sh <input> <output>
# or
#   $ ./run_russian.sh <input>
# or
#   $ ./run_russian.sh
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
TREE_TAGGER_OPT="-lemma -token -sgml -quiet"

NLTK_TOKENIZER_DIR=$METAPHOR_DIR/external-tools/nltk_tokenizer

MALT_DIR=$METAPHOR_DIR/external-tools/malt-1.5
MALT_RU_DIR=$METAPHOR_DIR/external-tools/malt-ru

TOKENIZER_BIN=$NLTK_TOKENIZER_DIR/nltk_tokenizer.py

TAGGER_BIN=$TREE_TAGGER_BIN/tree-tagger
TAGGER_PAR=$MALT_RU_DIR/russian.par
LEMMATIZER_BIN=$MALT_RU_DIR/lemmatiser.pl

RU_PIPELINE_DIR=$METAPHOR_DIR/pipelines/Russian

MALT_BIN=$MALT_DIR/malt.jar
MALT_MODEL=rus-test.mco
MALT_IFORMAT=$MALT_RU_DIR/make-malt.pl


CURRENT_DIR=`pwd`
cd $MALT_RU_DIR

if [[ $PLATFORM == "linux" ]]; then
  if [ -d "$2" ]; then
    python $TOKENIZER_BIN < "${1:-/dev/stdin}" |
    tee $2/tokenizer_o.txt |
    $TAGGER_BIN $TREE_TAGGER_OPT $TAGGER_PAR |
    tee $2/tagger_o.txt |
    $LEMMATIZER_BIN -l $MALT_RU_DIR/msd-ru-lemma.lex.gz -p $MALT_RU_DIR/wform2011.ptn1 -c $MALT_RU_DIR/cstlemma |
    tee $2/lemmatizer_o.txt |
    $MALT_IFORMAT | 
    java -Xmx16g -jar $MALT_BIN -c $MALT_MODEL -m parse -v off |
    tee $2/malt_o.txt |
    python $RU_PIPELINE_DIR/malt_ru.py > /dev/stdout
  else
    python $TOKENIZER_BIN < "${1:-/dev/stdin}" |
    $TAGGER_BIN $TREE_TAGGER_OPT $TAGGER_PAR |
    $LEMMATIZER_BIN -l $MALT_RU_DIR/msd-ru-lemma.lex.gz -p $MALT_RU_DIR/wform2011.ptn1 -c $MALT_RU_DIR/cstlemma |
    $MALT_IFORMAT | 
    java -Xmx16g -jar $MALT_BIN -c $MALT_MODEL -m parse -v off |
    python $RU_PIPELINE_DIR/malt_ru.py > "${2:-/dev/stdout}"
  fi
elif [[ $PLATFORM == "darwin" ]]; then
  if [ -d "$2" ]; then
      python $TOKENIZER_BIN < "${1:-/dev/stdin}" |
      tee $2/tokenizer_o.txt |
      $TAGGER_BIN $TREE_TAGGER_OPT $TAGGER_PAR |
      tee $2/tagger_o.txt |
      $MALT_IFORMAT | 
      java -Xmx16g -jar $MALT_BIN -c $MALT_MODEL -m parse -v off |
      tee $2/malt_o.txt |
      python $RU_PIPELINE_DIR/malt_ru.py > /dev/stdout
  else
      python $TOKENIZER_BIN < "${1:-/dev/stdin}" |
      $TAGGER_BIN $TREE_TAGGER_OPT $TAGGER_PAR |
      $MALT_IFORMAT | 
      java -Xmx16g -jar $MALT_BIN -c $MALT_MODEL -m parse -v off |
      python $RU_PIPELINE_DIR/malt_ru.py > "${2:-/dev/stdout}"
  fi
else
    echo "Unsupported platform $OSTYPE"
fi

cd $CURRENT_DIR