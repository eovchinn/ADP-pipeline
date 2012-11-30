#!/usr/bin/python
# -*- coding: utf-8 -*-

# Contributors:
#   * Vladimir Zaytsev <vzaytsev@isi.edu> (2012)

import sys

from nltk.tokenize import PunktSentenceTokenizer
from nltk.tokenize import WordPunctTokenizer
from nltk.tokenize import TreebankWordTokenizer

if __name__ == "__main__":    
    
    st = PunktSentenceTokenizer()
    wtw = TreebankWordTokenizer()
    wtt = WordPunctTokenizer()

    for line in sys.stdin:
        sentences = st.tokenize(line.decode("utf-8"))
        for s in sentences:
            for w1 in wtw.tokenize(s):
                for w in wtt.tokenize(w1):                
                    sys.stdout.write(w.encode("utf-8"))
                    sys.stdout.write("\n")
    sys.stdout.write("\n")
