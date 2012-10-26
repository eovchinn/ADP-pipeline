#!/usr/bin/python
# -*- coding: utf-8 -*-

# This script reproduces full processing pipeline for parsing Russian.
 
import os
import sys
import tempfile
import subprocess

if __name__ == "__main__":
    PLATFORM = None

    if sys.platform == "darwin":
        PLATFORM = "darwin"
    elif sys.platform == "linux2" or \
         sys.platform == "linux3":
        PLATFORM = "linux"

    if not PLATFORM:
        sys.stderr.write("Error: unsopported platform\n")
        exit(1)

    TREE_TAGGER_BIN = "../../external-tools/tree-tagger-3.2/%s/bin" % PLATFORM
    TREE_TAGGER_CMD = "../../external-tools/tree-tagger-3.2/%s/cmd" % PLATFORM
    TREE_TAGGER_LIB = "../../external-tools/tree-tagger-3.2/%s/lib" % PLATFORM
    TREE_TAGGER_OPT = "-lemma -token -sgml"
    MALT_DIR = "../../external-tools/malt-1.5"
    MALT_RU_DIR = "../../external-tools/malt-ru"
    TOKENIZER_BIN = "%s/utf8-tokenize.perl" % TREE_TAGGER_CMD
    TAGGER_BIN = "%s/tree-tagger" % TREE_TAGGER_BIN
    TAGGER_PAR = "%s/russian.par" % MALT_RU_DIR
    LEMMATIZER_BIN = "%s/lemmatiser.pl" % MALT_RU_DIR
    LEMMATIZER_OPT = "-l %s/msd-ru-lemma.lex.gz "\
                     "-p %s/wform2011.ptn1 -c "\
                     "%s/cstlemma-linux-64bit" % \
                     (MALT_RU_DIR, MALT_RU_DIR, MALT_RU_DIR)
    MALT_BIN = "%s/malt.jar" % MALT_DIR
    MALT_MODEL = "rus-test.mco"# % MALT_RU_DIR 
    MALT_IFORMAT = "%s/make-malt.pl" % MALT_RU_DIR
    MALT_COMMAND = "java -Xmx16g -jar %s -c %s "\
                   "-m parse" % \
                   (MALT_BIN, MALT_MODEL)
    MALT_RU_BIN = "malt_ru.py"
    TEST_INPUT_FILE = "samples/raw_text_input.txt"
    TEST_MALT_OUTPUT = os.path.join(tempfile.gettempdir(), "malt_output.conll")
    MALT_OUTPUT_OPT = "-o %s" % TEST_MALT_OUTPUT

    if PLATFORM == "linux":
        shell_cmd = "%s %s | %s %s %s | %s %s | %s | %s %s | %s" % (
            TOKENIZER_BIN, TEST_INPUT_FILE,
            TAGGER_BIN, TREE_TAGGER_OPT, TAGGER_PAR,
            LEMMATIZER_BIN, LEMMATIZER_OPT,
            MALT_IFORMAT,
            MALT_COMMAND, MALT_OUTPUT_OPT,
            MALT_RU_BIN,
        )

    if PLATFORM == "darwin":
        shell_cmd = "%s %s | %s %s %s | %s | %s %s | %s" % (
            TOKENIZER_BIN, TEST_INPUT_FILE,
            TAGGER_BIN, TREE_TAGGER_OPT, TAGGER_PAR,
            MALT_IFORMAT,
            MALT_COMMAND, MALT_OUTPUT_OPT,
            MALT_RU_BIN,
        )

    os.system(shell_cmd)
