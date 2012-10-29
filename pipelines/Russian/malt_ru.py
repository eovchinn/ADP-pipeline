#!/usr/bin/python
# -*- coding: utf-8 -*-

# Malt Parser output processing pipeline for Russian.
# The script takes the output of the Malt Parser and converts it to <ABC> format.

import os
import re
import sys
import argparse


line_splitter = re.compile("\s+")
punct = re.compile("[\.,\?\!{}()\[\]:;¿¡]")
postag_map = {
    "V": ("vb", 4),     # verb - vb/4
    "A": ("adj", 2),    # noun - nn/2
    "N": ("nn", 2),     # adjective - adj/2
    "R": ("rb", 2),     # adverb - rb/2
    "S": ("in", 3),     # preposition - in/3
}


def format_sent(sent, prop, sent_count):
    raw_text = u"% " + u" ".join(sent)
    id_text = u"id(%d)." % sent_count
    e_count = 1
    x_count = 1
    preds = []
    for word_id, lemma, cpostag in prop:
        if cpostag not in postag_map or punct.match(lemma):
            continue
        pred = u"[%d]:" % (1000 * sent_count + int(word_id))
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
    parser = argparse.ArgumentParser(description=\
        "MaltParser output processing pipeline for Russian.")
    parser.add_argument("--input", help=\
        "The input CoNLL file to be processed. Default is stdin.", default=None)
    parser.add_argument("--output", help=\
        "Output file. Default is stdout.", default=None)
    pa = parser.parse_args()
    lines = open(pa.input, "r") if pa.input else sys.stdin
    out = open(pa.output, "w") if pa.output else sys.stdout
    
    sent_count = 1
    sent = []
    prop = []
    for line in lines:
        line = line.decode("utf-8")
        line = line_splitter.split(line)
        if len(line) > 2:
            prop.append((line[0], line[2], line[3],))
            sent.append(line[1])
        else:
            out_line = format_sent(sent, prop, sent_count)
            out.write(out_line.encode("utf-8"))
            sent = []
            prop = []
            sent_count += 1


if __name__ == "__main__":
    main()
