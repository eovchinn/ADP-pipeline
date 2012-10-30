#!/usr/bin/python
# -*- coding: utf-8 -*-

# Malt Parser output processing pipeline for Russian.
# The script takes the output of the Malt Parser and converts it to <ABC> format.

import re
import sys
import argparse


class MaltConverter(object):
    line_splitter = re.compile("\s+")
    punct = re.compile("[\.,\?\!{}()\[\]:;¿¡]")
    postag_map = {
        "V": ("vb", 4),     # verb - vb/4
        "A": ("adj", 2),    # noun - nn/2
        "N": ("nn", 2),     # adjective - adj/2
        "R": ("rb", 2),     # adverb - rb/2
        "S": ("in", 3),     # preposition - in/3
    }

    def __init__(self):
        self.__props = []
        self.__sent = []

    def add_line(self, line):
        """
        """

        line = line.decode("utf-8")
        line = self.line_splitter.split(line)
        self.__prop = []
        self.__sent = []
        if len(line) > 2:
            self.__prop.append((
                line[0],  # ID. Token counter, starting at 1 for each
                          # new sentence.
                line[1],  # FORM. Word form or punctuation symbol.
                line[2],  # LEMMA. Lemma or stem (depending on particular
                          # data set) of word form, or an underscore if not
                          # available.
                line[3],  # CPOSTAG. Coarse-grained part-of-speech tag, where
                          # tagset depends on the language.
                line[6],  # HEAD. Head of the current token, which is either a
                          # value of ID or zero ('0'). Note that depending on
                          # the original treebank annotation, there may be
                          # multiple tokens with an ID of zero.
            ))
            self.__sent.append(line[1])
            return True
        else:
            return False

    def flush(self, ofile):
        output = self.format_output()
        ofile.write(output.encode("utf-8"))
        self.__sent = []
        self.__prop = []


def handle_verb()


def format_sent(sent, prop, sent_count):
    raw_text = u"% " + u" ".join(sent)
    id_text = u"id(%d)." % sent_count
    e_count = 1
    x_count = 1
    preds = []
    for i, (word_id, lemma, cpostag) in enumerate(prop):
        if cpostag not in postag_map or punct.match(lemma):
            continue
        pred = u"[%d]:" % (1000 * sent_count + int(word_id))
        if lemma == "<unknown>":
            pred += sent[i] + u"-"
        else:
            pred += lemma + u"-"
        postag, args = postag_map[cpostag]
        pred += postag + u"(e%d" % e_count
        e_count += 1
        for i in xrange(args - 1):
            pred += u",x%d" % x_count
            x_count += 1
        pred += u")"
        preds.append(pred)
    pred_text = u" & ".join(preds)
    return u"%s\n%s\n%s\n\n" % (raw_text, id_text, pred_text,)


def main():
    parser = argparse.ArgumentParser(
        description="MaltParser output processing pipeline for Russian.")
    parser.add_argument("--input",
        help="The input CoNLL file to be processed. Default is stdin.",
        default=None)
    parser.add_argument("--output",
        help="Output file. Default is stdout.",
        default=None)

    pa = parser.parse_args()
    lines = open(pa.input, "r") if pa.input else sys.stdin
    ofile = open(pa.output, "w") if pa.output else sys.stdout

    sent_count = 1
    mc = MaltConverter()

    for line in lines:
        if mc.add_line(sent_count, line):
            continue
        else:
            mc.flush(ofile)
            sent_count += 1


if __name__ == "__main__":
    main()
