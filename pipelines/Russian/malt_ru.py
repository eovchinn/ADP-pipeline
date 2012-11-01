#!/usr/bin/python
# -*- coding: utf-8 -*-

# Malt Parser output processing pipeline for Russian.
# The script takes the output of the Malt Parser and converts it to
# Logical Form format.

import re
import sys
import argparse


class WordToken(object):
    postag_map = {
        "V": ("vb", 4),     # verb - vb/4
        "A": ("adj", 2),    # noun - nn/2
        "N": ("nn", 2),     # adjective - adj/2
        "R": ("rb", 2),     # adverb - rb/2
        "S": ("in", 3),     # preposition - in/3
        "P": ("pr", -1),    # pronoun or demonstrative adjective
        "M": ("num", -1),   # numeral
    }

    def __init__(self, line):
        self.id = int(line[0])      # ID. Token counter, starting at 1 for each
                                    # new sentence.
        self.form = line[1]         # FORM. Word form or punctuation symbol.
        self.lemma = line[2]        # LEMMA. Lemma or stem (depending on
                                    # particular data set) of word form, or an
                                    # underscore if not available.
        cpostag = line[3]           # CPOSTAG. Coarse-grained part-of-speech
                                    # tag, where tagset depends on the language.
        self.feats = line[5]        # FEATS. Unordered set of syntactic and/or
                                    # morphological features (depending on the
                                    # particular language), separated by a
                                    # vertical bar (|), or an underscore if not
                                    # available. See this for more details:
                                    # corpus.leeds.ac.uk/mocky/msd-ru.html
        self.head = int(line[6])    # HEAD. language HEAD. Head of the current
                                    # token, which is either a value of ID or
                                    # zero ('0'). Note that depending on the
                                    # original treebank annotation, there may
                                    # be multiple tokens with an ID of zero.
        self.deprel = line[7]       # DEPREL. Dependency relation to the HEAD.
                                    # The set of dependency relations depends
                                    # on the particular language. Note that
                                    # depending on the original treebank
                                    # annotation, the dependency relation may
                                    # be meaningful or simply 'ROOT'.

        # Deprel types are defined in the following article:
        # http://www.aclweb.org/anthology-new/C/C08/C08-1081.pdf
        #
        # 1. предик (predicative), which, prototypically represents the
        #    relation between the verbal predicate as head and its subject as
        #    dependent;
        # 2. 1-компл (ﬁrst complement), which denotes the relation between a
        #    predicate word as head and its direct complement as dependent;
        # 3. агент (agentive), which introduces the relation between a
        #    predicate word (verbal noun or verb in the passive voice) as head
        #    and its agent in the instrumental case as dependent;
        # 4. квазиагент (quasi-agentive), which relates any predicate noun as
        #    head with its ﬁrst syntactic actant as dependent, if the latter is
        #    not eligible for being qualiﬁed as the noun’s agent;
        # 5. опред (modiﬁer), which connects a noun head with an
        #    adjective/participle dependent if the latter serves as an
        #    adjectival modiﬁer to the noun;
        # 6. предл (prepositional), which accounts for the relation between a
        #    preposition as head and a noun as dependent.

        if cpostag in self.postag_map:
            self.cpostag, self.args = self.postag_map.get(cpostag)
        else:
            self.cpostag, self.args = None, -1

    def __repr__(self):
        return u"<WordToken(%s)>" \
            % (self.id, )


class MaltConverter(object):
    line_splitter = re.compile("\s+")
    punct = re.compile("[\.,\?\!{}()\[\]:;¿¡]")

    def __init__(self):
        # __words = [WordToken]
        self.__words = []
        # __extra_preds = [(prefix, ( x-u args))]
        self.__extra_preds = []

    def add_line(self, line):
        line = self.line_splitter.split(line.decode("utf-8"))
        # print line
        if len(line) > 2:
            self.__words.append(WordToken(line))
            return True  # Line successfully added.
        else:
            return False  # Line was not added (end of sentence).

    def word(self, word_id):
        return self.__words[word_id - 1]

    def __deps(self, word):
        for w in self.__words:
            if w.head == word.id:
                yield w

    def format_output(self, sent_count):

        sent_text = u"% " + u" ".join([w.form for w in self.__words])
        id_text = u"id(%d)." % sent_count
        preds = []
        e_count = 1
        u_count = 1

        for w in self.__words:

            if not w.cpostag or self.punct.match(w.lemma):
                continue
            pred = u"[%d]:" % (1000 * sent_count + w.id)

            if w.lemma == "<unknown>":
                pred += w.form + u"-"
            else:
                pred += w.lemma + u"-"

            if w.cpostag == "vb":
                arg_text, e_count, u_count = \
                    self.__handle_verb(w, e_count, u_count)
            elif w.cpostag == "nn":
                arg_text, e_count, u_count = \
                    self.__handle_noun(w, e_count, u_count)
            elif w.cpostag == "pr":
                arg_text = None
            elif w.args != -1:
                print w.lemma, w.args
                arg_text, e_count, u_count = \
                    self.__handle_generic(w, e_count, u_count)

            if arg_text:
                pred += w.cpostag
                pred += arg_text
                preds.append(pred)
                arg_text = None

        pred_text = u" & ".join(
            preds +
            self.extra_preds(sent_count, e_count, u_count))
        return u"%s\n%s\n%s\n\n" % (sent_text, id_text, pred_text,)

    def __handle_verb(self, word, e_count, u_count):

        # 1. Link arguments: subject - second arg, direct object - third arg,
        #    indirect object - fourth arg. Direct obj can be a clause; then the
        #    head of the clause should be used as the verb argument.

        w_subject = None
        d_object = None
        i_object = None

        for dep in self.__deps(word):
            if dep.deprel == u"предик":
                w_subject = "x%d" % dep.id
            elif dep.deprel == u"1-компл":
                if dep.cpostag == "pr":
                    d_object = "e%d" % dep.id
                else:
                    d_object = "x%d" % dep.id
            elif dep.deprel == u"2-компл":
                if dep.cpostag == "pr":
                    i_object = "e%d" % dep.id
                else:
                    i_object = "x%d" % dep.id

        if not w_subject:
            w_subject = "u%d" % u_count
            u_count += 1

        if not d_object:
            d_object = "u%d" % u_count
            u_count += 1

        if not i_object:
            i_object = "u%d" % u_count
            u_count += 1

        e_arg = "e%d" % e_count
        e_count += 1

        # 2. If in  there are more than 3 cases which can be expressed without
        #    prepositions (e.g. Russian), then introduce additional predicates
        #    expressing these cases is need.

        # TODO(zaytsev@udc.edu): implement this

        # 3. Add tense information if available from the parser.

        # TODO(zaytsev@udc.edu): implement this

        return "(%s,%s,%s,%s)" % (e_arg, w_subject, d_object, i_object), \
            e_count, u_count

    def __handle_noun(self, word, e_count, u_count):

        # 1. Noun compounds: if there are noun compounds in the language you are
        #    working with, use the predicate "nn" to express it.

        # TODO(zaytsev@udc.edu): implement this

        # 2. Genitive: always use the predicate "of-in" for expressing
        #    genitives.

        if word.feats[4] == "g" and self.word(word.head).cpostag == "nn":
            epred = ("of-in", ("x%d" % word.id, "x%d" % word.head,))
            self.__extra_preds.append(epred)

        # 3. Add number information if available from the parser (if plural).

        if word.feats[3] == "p":  # if plural
            for dep in self.__deps(word):
                if dep.cpostag == "num":
                    try:
                        num = dep.form
                    except ValueError:
                        num = "s"
                    epred = ("typelt", ("x%d" % word.id, num))
                    self.__extra_preds.append(epred)

        args_text = "e%d,u%d" % (e_count, u_count)
        u_count += 1
        e_count += 1
        return "(%s)" % args_text, e_count, u_count

    def __handle_generic(self, word, e_count, u_count):
        arg_text = "(e%d" % e_count
        e_count += 1
        for i in xrange(1, word.args):
            arg_text += ",u%d" % u_count
            u_count += 1
        return arg_text + ")", e_count, u_count

    def extra_preds(self, sent_count, e_count, u_count):
        epreds = []
        for tag, x_args in self.__extra_preds:
            epred_str = "%s(e%d" % (tag, e_count,)
            e_count += 1
            for x in x_args:
                if x != None:
                    epred_str += "," + x
                else:
                    epred_str += ",u%d" % u_count
                    u_count += 1
            epred_str += ")"
            epreds.append(epred_str)
        return epreds

    def flush(self, sent_count, ofile):
        output = self.format_output(sent_count)
        ofile.write(output.encode("utf-8"))
        self.__words = []
        self.__extra_preds = []


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
        if mc.add_line(line):
            continue
        else:
            mc.flush(sent_count, ofile)
            sent_count += 1


if __name__ == "__main__":
    main()
