#!/usr/bin/python
# -*- coding: utf-8 -*-

# Contributors:
#   * Vladimir Zaytsev <vzaytsev@isi.edu> (2012)

import sys

from nltk.tokenize import PunktSentenceTokenizer, WordPunctTokenizer


if __name__ == "__main__":

    st = PunktSentenceTokenizer()
    wt = WordPunctTokenizer()

    for line in sys.stdin:
        sentences = st.tokenize(line.decode("utf-8"))
        for s in sentences:
            words = wt.tokenize(s)
            for w in words:
                sys.stdout.write(w)
                sys.stdout.write("\n")
            sys.stdout.write("\n")
