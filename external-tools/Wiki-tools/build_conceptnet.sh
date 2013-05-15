#!/bin/bash
# change CONCEPTNET_DIR to the dir where you put all .csv files
CONCEPTNET_DIR=./
python concept_insert2DB.py -l ES -d $CONCEPTNET_DIR
python concept_insert2DB.py -l RU -d $CONCEPTNET_DIR
python concept_insert2DB.py -l FA -d $CONCEPTNET_DIR
