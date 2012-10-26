#!/usr/bin/python
# -*- coding: utf-8 -*-

# Malt Parser output processing pipeline for Russian.
# The script takes the output of the Malt Parser and converts it to <ABC> format.

import os
import re
import sys
import argparse


conll_splitter = re.compile("\s+")
postag_map = {
    "V": ("vb", 4),
    "A": ("adj", 2),
    "N": ("nn", 2),
    "?": ("rb", 2),
    "?": ("in", 3),
}


def conll_mapper(conl_str, sent_i=0):
    cid, form, lemma, cpostag, postag, \
        feats, head, deprel, phead, pdeprel =\
        conll_splitter.split(conl_str)
    return None


def main():
    parser = argparse.ArgumentParser(description="MALT output processing pipeline for Russian.")
    parser.add_argument("--input", help="The input CoNLL file to be processed. Default is stdin.", default=None)
    parser.add_argument("--output", help="Output file. Default is stdout.", default=None)
    pa = parser.parse_args()
    lines = open(pa.input, "r") if pa.input else sys.stdin
    out = open(pa.output, "w") if pa.output else sys.stdout
    
    sent_counter = 1
    for line in lines:
        if line == "\n":
            sent_counter += 1
        else:
            formatted = conll_mapper(line, sent_counter)
            out.write(formatted.encode("utf-8"))


if __name__ == "__main__":
    main()
