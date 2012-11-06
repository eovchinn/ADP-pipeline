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
        "P": ("pr", -1),    # pronoun
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

        self.pred = None

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

        if self.lemma == "<unknown>":
            self.lemma = self.form

    def __repr__(self):
        return u"<WordToken(%s)>" \
            % (self.id, )


class Argument(object):

    def __init__(self, arg_type):
        self.type = arg_type
        self.index = None
        self.link = None

    def link_to(self, another_arg):
        if self != another_arg:
            self.link = another_arg

    def resolve_link(self):
        if not self.link:
            return self
        else:
            return self.link.resolve_link()

    @staticmethod
    def arg_link(arg):
        arg = Argument(arg.type)
        arg.link_to(arg)
        return arg

    def __repr__(self):
        arg = self.resolve_link()
        if arg.index:
            return "%s%d" % (arg.type, arg.index, )
        else:
            return "%s" % self.type


class Predicate(object):

    def __init__(self, word, args):
        self.word = word
        self.label = u"%s-%s" % (word.lemma, word.cpostag, )
        self.args = args

    def __repr__(self):
        return u"<Predicate(label=%s, args=%s)>" \
            % (self.label, self.args, )


class EPredicate(Predicate):
    pass


class MaltConverter(object):
    line_splitter = re.compile("\s+")
    punct = re.compile("[\.,\?\!{}()\[\]:;¿¡]")

    def __init__(self):
        self.__words = []
        self.__preds = []
        self.__extra_preds = []

    def assign_indexes(self):

        e_count = 1
        x_count = 1
        u_count = 1

        arg_set = set()
        arg_list = []
        for w in self.__words:
            if w.pred:
                for a in w.pred.args:
                    if a.resolve_link() not in arg_set:
                        arg_set.add(a.resolve_link())
                        arg_list.append(a.resolve_link())

        for ep, ep_args in self.__extra_preds:
            for a in ep_args:
                if a.resolve_link() not in arg_set:
                    arg_set.add(a.resolve_link())
                    arg_list.append(a.resolve_link())

        for a in arg_list:
            if a.type == "e":
                a.index = e_count
                e_count += 1
            elif a.type == "x":
                a.index = x_count
                x_count += 1
            elif a.type == "u":
                a.index = u_count
                u_count += 1

    def add_line(self, line):
        line = self.line_splitter.split(line.decode("utf-8"))
        if len(line) > 2:
            self.__words.append(WordToken(line))
            return True
        else:
            return False

    def word(self, word_id):
        return self.__words[word_id - 1]

    def __deps(self, word):
        for w in self.__words:
            if w.head == word.id:
                yield w

    def format_pred(self, pred, sent_count=None):
        argsf = []
        for a in pred.args:
            argsf.append("%s%d" \
                % (a.resolve_link().type, a.resolve_link().index, ))
        if sent_count is not None:
            id_text = "[%d]:" % (1000 * sent_count + pred.word.id)
        else:
            id_text = ""
        return u"%s%s(%s)" % (id_text, pred.label, ",".join(argsf), )

    def format_epred(self, epred):
        label, args = epred
        argsf = []
        for a in args:
            if a.type in ["e", "x", "u", ]:
                argsf.append("%s%d"\
                             % (a.resolve_link().type,
                                a.resolve_link().index)
                )
            else:
                argsf.append(a.type)
        return u"%s(%s)" % (label, ",".join(argsf), )

    def format_output(self, sent_count):

        for w in self.__words:

            if not w.cpostag or self.punct.match(w.lemma):
                continue

            if w.args != -1:
                pred = self.init_predicate(w)
                self.__preds.append(pred)

        for p in self.__preds:
            if p.word.cpostag == "vb":
                self.apply_vb_rules(p.word)
            if p.word.cpostag == "nn":
                self.apply_nn_rules(p.word)
            if p.word.cpostag == "adj":
                self.apply_adj_rules(p.word)

        self.assign_indexes()

        predf = [self.format_pred(p, sent_count) for p in self.__preds]
        epredf = [self.format_epred(ep) for ep in self.__extra_preds]
        sent_text = u"% " + u" ".join([w.form for w in self.__words])
        id_text = u"id(%d)." % sent_count
        pred_text = " & ".join(predf + epredf)

        return u"%s\n%s\n%s\n\n" % (sent_text, id_text, pred_text)

    def apply_vb_rules(self, word):

        # 1. Link arguments: subject - second arg, direct object - third arg,
        #    indirect object - fourth arg. Direct obj can be a clause; then the
        #    head of the clause should be used as the verb argument.

        w_subject = None
        d_object = None
        i_object = None

        for dep in self.__deps(word):
            ddeps = list(self.__deps(dep))
            if dep.cpostag == "pr" and len(ddeps) > 0:
                dep = ddeps[0]
                if dep.cpostag == "vb" and dep.pred:
                    d_object = dep.pred.args[0]
            elif dep.cpostag == "nn":
                if dep.deprel == u"предик" and dep.pred:
                    w_subject = dep.pred.args[1]
                elif dep.deprel == u"2-компл" and dep.pred:
                    d_object = dep.pred.args[1]
                elif dep.deprel == u"1-компл" and dep.pred:
                    i_object = dep.pred.args[1]

        # 2. Argument control: first arguments of both verbs are the same.

        head = self.word(word.head)
        if head and head.cpostag == "vb":
            # Use VERB#1 rule to find subject of the head
            w_subject = head.pred.args[1]
            head.pred.args[2].link_to(word.pred.args[0])

        # 3. If in  there are more than 3 cases which can be expressed without
        #    prepositions (e.g. Russian), then introduce additional predicates
        #    expressing these cases is need.
        # TODO(zaytsev@udc.edu): implement this
        # 4. Add tense information if available from the parser.

        if word.feats[3] == "s":  # if past
            epred = ("past", [Argument("e"), word.pred.args[0]])
            self.__extra_preds.append(epred)

        if word.feats[3] == "f":  # if furure
            epred = ("future", [Argument("e"), word.pred.args[0]])
            self.__extra_preds.append(epred)

        if w_subject:
            word.pred.args[1].link_to(w_subject)
        else:
            word.pred.args[1] = Argument("u")
        if d_object:
            word.pred.args[2].link_to(d_object)
        else:
            word.pred.args[2] = Argument("u")
        if i_object:
            word.pred.args[3].link_to(i_object)
        else:
            word.pred.args[3] = Argument("u")

    def apply_nn_rules(self, word):

        # 1. Noun compounds: if there are noun compounds in the language you are
        #    working with, use the predicate "nn" to express it.

        # TODO(zaytsev@udc.edu): implement this

        # 2. Genitive: always use the predicate "of-in" for expressing
        #    genitives.

        head = self.word(word.head)
        if word.feats[4] == "g" and head.cpostag == "nn":
            epred = ("of-in",
                        [Argument("e"),
                         head.pred.args[1],
                         word.pred.args[1],
                ])
            self.__extra_preds.append(epred)

        # 3. Add number information if available from the parser (if plural).

        if word.feats[3] == "p":  # if plural
            epred = ("typelt", [
                    word.pred.args[1],
                    Argument("s"),
                ])
            self.__extra_preds.append(epred)
            for dep in self.__deps(word):
                if dep.cpostag == "num":
                    try:
                        num = int(dep.form)
                        epred = ("card", [
                            word.pred.args[1],
                            Argument(str(num)),
                        ])
                        self.__extra_preds.append(epred)
                    except ValueError:
                        # TODO(zaytsev@udc.edu): parse word numeral
                        pass

        # 4. If there is other information available from the parser (e.g. type
        #    of the named entity), please add it.

        # TODO(zaytsev@udc.edu): implement this

    def apply_adj_rules(self, word):

        # 1. Adjectives share the second argument with the noun they are
        #    modifying

        head = self.word(word.head)
        if head and head.cpostag == "nn":
            word.pred.args[1].link_to(head.pred.args[1])

    def init_predicate(self, word):
        args = [Argument("e")]\
             + [Argument("x") for _ in xrange(1, word.args)]
        pred = Predicate(word, args)
        word.pred = pred
        return pred

    def flush(self, sent_count, ofile):
        output = self.format_output(sent_count)
        ofile.write(output.encode("utf-8"))
        self.__words = []
        self.__preds = []
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
    ifile = open(pa.input, "r") if pa.input else sys.stdin
    ofile = open(pa.output, "w") if pa.output else sys.stdout

    sent_count = 1
    mc = MaltConverter()

    for line in ifile:
        if mc.add_line(line):
            continue
        else:
            mc.flush(sent_count, ofile)
            sent_count += 1


if __name__ == "__main__":
    main()
