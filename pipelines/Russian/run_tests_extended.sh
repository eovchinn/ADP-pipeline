#! /bin/bash
# Pipeline debugging script.
# Reads text from:
#   $METAPHOR_DIR/pipelines/Russian/examples/raw_text_input.txt
# writes output to stdout.
# Variable $METAPHOR_DIR should point to the root of 
# Metaphor-ADP directory (e.g. ~/code/Metaphor-ADP directory)

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


IFILE=$RU_PIPELINE_DIR/test_data/input_economics.txt
OMALT=$RU_PIPELINE_DIR/test_data/omalt_economics.txt
OLF=$RU_PIPELINE_DIR/test_data/olf_economics.txt


CURRENT_DIR=`pwd`
cd $MALT_RU_DIR

if [[ $PLATFORM == "linux" ]]; then
    python $TOKENIZER_BIN --treebank 0 < $IFILE |
    $TAGGER_BIN $TREE_TAGGER_OPT $TAGGER_PAR |
    $LEMMATIZER_BIN -l $MALT_RU_DIR/msd-ru-lemma.lex.gz -p $MALT_RU_DIR/wform2011.ptn1 -c $MALT_RU_DIR/cstlemma |
    $MALT_IFORMAT | 
    java -Xmx16g -jar $MALT_BIN -c $MALT_MODEL -m parse -v off >/dev/stdout | tee > $OMALT
    python $RU_PIPELINE_DIR/malt_ru.py < $OMALT > $OLF
elif [[ $PLATFORM == "darwin" ]]; then
    python $TOKENIZER_BIN --treebank 0  < $IFILE |
    $TAGGER_BIN $TREE_TAGGER_OPT $TAGGER_PAR |
    $MALT_IFORMAT | 
    java -Xmx16g -jar $MALT_BIN -c $MALT_MODEL -m parse -v off | tee > $OMALT
    python $RU_PIPELINE_DIR/malt_ru.py < $OMALT > $OLF
else
    echo "Unsupported platform $OSTYPE"
fi

IFILE=$RU_PIPELINE_DIR/test_data/input_elections.txt
OMALT=$RU_PIPELINE_DIR/test_data/omalt_elections.txt
OLF=$RU_PIPELINE_DIR/test_data/olf_elections.txt


if [[ $PLATFORM == "linux" ]]; then
    python $TOKENIZER_BIN --treebank 0 < $IFILE |
    $TAGGER_BIN $TREE_TAGGER_OPT $TAGGER_PAR |
    $LEMMATIZER_BIN -l $MALT_RU_DIR/msd-ru-lemma.lex.gz -p $MALT_RU_DIR/wform2011.ptn1 -c $MALT_RU_DIR/cstlemma |
    $MALT_IFORMAT | 
    java -Xmx16g -jar $MALT_BIN -c $MALT_MODEL -m parse -v off >/dev/stdout | tee > $OMALT
    python $RU_PIPELINE_DIR/malt_ru.py < $OMALT > $OLF
elif [[ $PLATFORM == "darwin" ]]; then
    python $TOKENIZER_BIN --treebank 0 < $IFILE |
    $TAGGER_BIN $TREE_TAGGER_OPT $TAGGER_PAR |
    $MALT_IFORMAT | 
    java -Xmx16g -jar $MALT_BIN -c $MALT_MODEL -m parse -v off | tee > $OMALT
    python $RU_PIPELINE_DIR/malt_ru.py < $OMALT > $OLF
else
    echo "Unsupported platform $OSTYPE"
fi

IFILE=$RU_PIPELINE_DIR/test_data/input_government.txt
OMALT=$RU_PIPELINE_DIR/test_data/omalt_government.txt
OLF=$RU_PIPELINE_DIR/test_data/olf_government.txt

if [[ $PLATFORM == "linux" ]]; then
    python $TOKENIZER_BIN --treebank 0 < $IFILE |
    $TAGGER_BIN $TREE_TAGGER_OPT $TAGGER_PAR |
    $LEMMATIZER_BIN -l $MALT_RU_DIR/msd-ru-lemma.lex.gz -p $MALT_RU_DIR/wform2011.ptn1 -c $MALT_RU_DIR/cstlemma |
    $MALT_IFORMAT | 
    java -Xmx16g -jar $MALT_BIN -c $MALT_MODEL -m parse -v off >/dev/stdout | tee > $OMALT
    python $RU_PIPELINE_DIR/malt_ru.py < $OMALT > $OLF
elif [[ $PLATFORM == "darwin" ]]; then
    python $TOKENIZER_BIN --treebank 0 < $IFILE |
    $TAGGER_BIN $TREE_TAGGER_OPT $TAGGER_PAR |
    $MALT_IFORMAT | 
    java -Xmx16g -jar $MALT_BIN -c $MALT_MODEL -m parse -v off | tee > $OMALT
    python $RU_PIPELINE_DIR/malt_ru.py < $OMALT > $OLF
else
    echo "Unsupported platform $OSTYPE"
fi

IFILE=$RU_PIPELINE_DIR/test_data/input_politics.txt
OMALT=$RU_PIPELINE_DIR/test_data/omalt_politics.txt
OLF=$RU_PIPELINE_DIR/test_data/olf_politics.txt

if [[ $PLATFORM == "linux" ]]; then
    python $TOKENIZER_BIN --treebank 0 < $IFILE |
    $TAGGER_BIN $TREE_TAGGER_OPT $TAGGER_PAR |
    $LEMMATIZER_BIN -l $MALT_RU_DIR/msd-ru-lemma.lex.gz -p $MALT_RU_DIR/wform2011.ptn1 -c $MALT_RU_DIR/cstlemma |
    $MALT_IFORMAT | 
    java -Xmx16g -jar $MALT_BIN -c $MALT_MODEL -m parse -v off >/dev/stdout | tee > $OMALT
    python $RU_PIPELINE_DIR/malt_ru.py < $OMALT > $OLF
elif [[ $PLATFORM == "darwin" ]]; then
    python $TOKENIZER_BIN --treebank 0 < $IFILE |
    $TAGGER_BIN $TREE_TAGGER_OPT $TAGGER_PAR |
    $MALT_IFORMAT | 
    java -Xmx16g -jar $MALT_BIN -c $MALT_MODEL -m parse -v off | tee > $OMALT
    python $RU_PIPELINE_DIR/malt_ru.py < $OMALT > $OLF
else
    echo "Unsupported platform $OSTYPE"
fi

IFILE=$RU_PIPELINE_DIR/test_data/special_cases/big_text.txt
OMALT=$RU_PIPELINE_DIR/test_data/special_cases/omalt_big_text.txta
OLF=$RU_PIPELINE_DIR/test_data/special_cases/olf_big_text.txt

if [[ $PLATFORM == "linux" ]]; then
    python $TOKENIZER_BIN --treebank 0 < $IFILE |
    $TAGGER_BIN $TREE_TAGGER_OPT $TAGGER_PAR |
    $LEMMATIZER_BIN -l $MALT_RU_DIR/msd-ru-lemma.lex.gz -p $MALT_RU_DIR/wform2011.ptn1 -c $MALT_RU_DIR/cstlemma |
    $MALT_IFORMAT | 
    java -Xmx16g -jar $MALT_BIN -c $MALT_MODEL -m parse -v off >/dev/stdout | tee > $OMALT
    python $RU_PIPELINE_DIR/malt_ru.py < $OMALT > $OLF
elif [[ $PLATFORM == "darwin" ]]; then
    python $TOKENIZER_BIN --treebank 0 < $IFILE |
    $TAGGER_BIN $TREE_TAGGER_OPT $TAGGER_PAR |
    $MALT_IFORMAT | 
    java -Xmx16g -jar $MALT_BIN -c $MALT_MODEL -m parse -v off | tee > $OMALT
    python $RU_PIPELINE_DIR/malt_ru.py < $OMALT > $OLF
else
    echo "Unsupported platform $OSTYPE"
fi

IFILE=$RU_PIPELINE_DIR/test_data/special_cases/broken_encoding.txt
OMALT=$RU_PIPELINE_DIR/test_data/special_cases/omalt_broken_encoding.txt
OLF=$RU_PIPELINE_DIR/test_data/special_cases/olf_broken_encoding.txt

if [[ $PLATFORM == "linux" ]]; then
    python $TOKENIZER_BIN --treebank 0 < $IFILE |
    $TAGGER_BIN $TREE_TAGGER_OPT $TAGGER_PAR |
    $LEMMATIZER_BIN -l $MALT_RU_DIR/msd-ru-lemma.lex.gz -p $MALT_RU_DIR/wform2011.ptn1 -c $MALT_RU_DIR/cstlemma |
    $MALT_IFORMAT | 
    java -Xmx16g -jar $MALT_BIN -c $MALT_MODEL -m parse -v off >/dev/stdout | tee > $OMALT
    python $RU_PIPELINE_DIR/malt_ru.py < $OMALT > $OLF
elif [[ $PLATFORM == "darwin" ]]; then
    python $TOKENIZER_BIN --treebank 0 < $IFILE |
    $TAGGER_BIN $TREE_TAGGER_OPT $TAGGER_PAR |
    $MALT_IFORMAT | 
    java -Xmx16g -jar $MALT_BIN -c $MALT_MODEL -m parse -v off | tee > $OMALT
    python $RU_PIPELINE_DIR/malt_ru.py < $OMALT > $OLF
else
    echo "Unsupported platform $OSTYPE"
fi

cd $CURRENT_DIR