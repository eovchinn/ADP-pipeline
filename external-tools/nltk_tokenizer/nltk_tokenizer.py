#!/usr/bin/python
# -*- coding: utf-8 -*-

# Contributors:
#   * Vladimir Zaytsev <vzaytsev@isi.edu> (2012)

import sys
import argparse

from nltk.tokenize import PunktSentenceTokenizer
from nltk.tokenize import WordPunctTokenizer
from nltk.tokenize import TreebankWordTokenizer

parser = argparse.ArgumentParser()
parser.add_argument("--treebank",
    help="Additionally apply treebank tokenizer.",
    default=1)

pa = parser.parse_args()
treebank = int(pa.treebank)

if __name__ == "__main__":    
    
    st = PunktSentenceTokenizer()
    wtw = TreebankWordTokenizer()
    wtt = WordPunctTokenizer()

    for line in sys.stdin:
        line = line.replace("«", "'")
        line = line.replace("»", "'")
        line = line.replace("“", "'")
        line = line.replace("”", "'")
        line = line.replace("\"", "'")
        sentences = st.tokenize(line.decode("utf-8"))
        for s in sentences:
            if treebank == 0:
                for w in wtw.tokenize(s):
                    sys.stdout.write(w.encode("utf-8"))
                    sys.stdout.write("\n")
            else:
                for w1 in wtw.tokenize(s):
                    for w in wtt.tokenize(w1):
                        sys.stdout.write(w.encode("utf-8"))
                        sys.stdout.write("\n")
    sys.stdout.write("\n")
