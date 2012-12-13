#!/usr/bin/python
# -*- coding: utf-8 -*-

# Contributors:
#   * Vladimir Zaytsev <vzaytsev@isi.edu> (2012)
#
# python nltk_rtokenizer.py --sentid 1 --normquotes 1 --wptokenizer 0 < test

import sys
import argparse
import re

textid_re = re.compile("\s*"+ re.escape("<META>") +"(.+)+\s*$")

from nltk.tokenize import PunktSentenceTokenizer
from nltk.tokenize import WordPunctTokenizer
from nltk.tokenize import TreebankWordTokenizer

parser = argparse.ArgumentParser()

parser.add_argument("--sentid",
    help="Hanle specific sentence IDs.",
    default=0)
parser.add_argument("--normquotes",
    help="Normalize any quotes to quote single type.",
    default=1)
parser.add_argument("--wptokenizer",
    help="Additionally apply treebank tokenizer.",
    default=1)

pa = parser.parse_args()
sentid = int(pa.sentid)
normquotes = int(pa.normquotes)
wptokenizer = int(pa.wptokenizer)

if __name__ == "__main__":
    
    st = PunktSentenceTokenizer()
    wtw = WordPunctTokenizer() if wptokenizer == 1 else None
    wtt = TreebankWordTokenizer()
    
    for line in sys.stdin:
        
        line = line.decode("utf-8")
        
        if sentid == 1:
            m = textid_re.search(line)
            if m:
                sys.stdout.write(u".\n{{{%s}}}!!!\n" % m.group(1))
                continue
            if line == "\n":
                continue
    
        if normquotes == 1:
            line = line.replace(u"«", " ' ")
            line = line.replace(u"»", " ' ")
            line = line.replace(u"“", " ' ")
            line = line.replace(u"”", " ' ")
            line = line.replace(u"\"", " ' ")


        sentences = st.tokenize(line)

        for s in sentences:
            if wptokenizer == 1:
                for w1 in wtt.tokenize(s):
                    for w in wtw.tokenize(w1):
                        sys.stdout.write(w.encode("utf-8"))
                        sys.stdout.write("\n")
            else:
                for w in wtt.tokenize(s):
                    sys.stdout.write(w.encode("utf-8"))
                    sys.stdout.write("\n")

    sys.stdout.write("\n")