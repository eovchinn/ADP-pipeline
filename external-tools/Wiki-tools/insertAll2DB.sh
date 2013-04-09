#!/bin/bash
DOWNLOAD_DIR=./
python insertFile2DB.py -f $DOWNLOAD_DIR/long_abstracts_en.nt -l EN -s 1 --common $METAPHOR_DIR/pipelines/common/ --temp $DOWNLOAD_DIR/english.txt &
python insertFile2DB.py -f $DOWNLOAD_DIR/long_abstracts_es.nt -l ES -s 1 --common $METAPHOR_DIR/pipelines/common/ --temp $DOWNLOAD_DIR/spanish.txt &
python insertFile2DB.py -f $DOWNLOAD_DIR/long_abstracts_ru.nt -l RU -s 1 --common $METAPHOR_DIR/pipelines/common/ --temp $DOWNLOAD_DIR/russian.txt &
python insertFile2DB.py -f $DOWNLOAD_DIR/long_abstracts_fa.nt -l FA -s 1 --common $METAPHOR_DIR/pipelines/common/ --temp $DOWNLOAD_DIR/farsi.txt &
