#!/usr/bin/python
# -*- coding: utf-8 -*-

# Contributors:
#   * Vladimir Zaytsev <vzaytsev@isi.edu> (2012, 2013)

# Malt Parser output processing pipeline for Russian.
# The script takes the output of the Malt Parser and converts it to
# Logical Form format.

# Options:
#    [--input <input file>]
#    [--output <output file>]
#    [--nnnumber 1] – enables output numbers for nouns
#    [--vbtense 1] – enables output tenses for verbs

import sys
import argparse

from conll import CoNLLReader
from fol import FOLWriter, MaltConverter, fol_transform


def main():

    parser = argparse.ArgumentParser(
        description="MaltParser output processing pipeline for Russian.")
    parser.add_argument(
        "--input",
        help="The input CoNLL file to be processed. Default is stdin.",
        default=None)
    parser.add_argument(
        "--output",
        help="Output file. Default is stdout.",
        default=None)
    parser.add_argument(
        "--vbtense",
        help="Output file. Default is stdout.",
        default=True)
    parser.add_argument(
        "--nnnumber",
        help="Output file. Default is stdout.",
        default=True)

    pa = parser.parse_args()

    nn_number = bool(pa.nnnumber)
    vb_tense = bool(pa.vbtense)

    ifile = open(pa.input, "r") if pa.input else sys.stdin
    ofile = open(pa.output, "w") if pa.output else sys.stdout
    mc = MaltConverter(vb_tense, nn_number)

    conll_file = CoNLLReader(ifile)
    writer = FOLWriter(ofile)

    for text_block in conll_file:
        fol_sentence = fol_transform(mc, text_block)
        writer.write(text_block, fol_sentence)

    ifile.close()
    ofile.close()


if __name__ == "__main__":
    main()
