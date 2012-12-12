#!/usr/bin/python
# -*- coding: utf-8 -*-

# Contributors:
#   * Vladimir Zaytsev <vzaytsev@isi.edu> (2012)

# Malt Parser output processing pipeline for Russian.
# The script takes the output of the Malt Parser and converts it to
# Logical Form format.

# Options:
#    [--input <input file>]
#    [--output <output file>]
#    [--nnnumber 1] – enables output numbers for nouns
#    [--vbtense 1] – enables output tenses for verbs


import re
import sys
import argparse

global NN_NUMBER
global VB_TENSE


class WordToken(object):
    postag_map = {
        "V": ("vb", 4),     # verb - vb/4
        "A": ("adj", 2),    # adjective - adj/2
        "N": ("nn", 2),     # noun - nn/2
        "R": ("rb", 2),     # adverb - rb/2
        "S": ("in", 3),     # preposition - in/3
        "P": ("pr", 2),     # pronoun
        "M": ("num", -1),   # numeral
        "C": ("cnj", 2),    # conjunction
        "Q": ("par", 2),    # particle
    }

    def __init__(self, line=None, word=None):

        if not line and word:
            self.id = word.id
            self.form = word.form
            self.lemma = word.lemma
            self.cpostag = word.cpostag
            self.feats = word.feats
            self.head = word.head
            self.deprel = word.deprel
            self.pred = None
            self.important = True
            return

        if not line and not word:
            return

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

        self.important = True

    def __repr__(self):
        return u"<WordToken(%s)>" \
            % (self.id, )


class Argument(object):

    def __init__(self, arg_type):
        self.type = arg_type
        self.index = None
        self.link = None

    def link_to(self, another_arg, force=False):
        if not self.link or force:
            if self != another_arg:
                self.link = another_arg

    def resolve_link(self):
        if not self.link:
            return self
        else:
            return self.link.resolve_link()

    @staticmethod
    def arg_link(arg):
        new_arg = Argument(arg.type)
        new_arg.link_to(arg)
        return new_arg

    def __repr__(self):
        arg = self.resolve_link()
        if arg.index:
            return "%s%d" % (arg.type, arg.index, )
        else:
            return "%s" % self.type


class Predicate(object):

    def __init__(self, word, args):
        self.word = word
        self.prefix = word.lemma
        self.args = args
        self.show_index = True
        self.show_postag = True

    def __repr__(self):
        return u"<Predicate(prefix=%s, args=%s)>" \
            % (self.prefix, self.args, )


class EPredicate(object):

    def __init__(self, prefix, args=list()):
        self.prefix = prefix
        self.args = args


class MaltConverter(object):
    line_splitter = re.compile("\s+")
    punct = re.compile("[\.,\?!{}()\[\]:;¿¡]")

    def __init__(self):
        self.__words = []
        self.__initial_preds = []
        self.__extra_preds = []
        self.__visible_preds = []
        self.__removed_preds = []

    def assign_indexes(self):

        e_count = 1
        x_count = 1
        u_count = 1
        s_count = 1

        arg_set = set()
        arg_list = []
        for pred in self.__visible_preds:
            a = pred.args[0].resolve_link()
            if a not in arg_set:
                arg_set.add(a.resolve_link())
                arg_list.append((pred, a.resolve_link()))

        for pred in self.__visible_preds:
            for a in pred.args:
                if a.resolve_link() not in arg_set:
                    arg_set.add(a.resolve_link())
                    arg_list.append((pred, a.resolve_link()))

        for ep, ep_args in self.__extra_preds:
            for a in ep_args:
                if a.resolve_link() not in arg_set:
                    arg_set.add(a.resolve_link())
                    arg_list.append((ep, a.resolve_link()))
        for pred, a in arg_list:
            if a.type == "e":
                a.index = e_count
                e_count += 1
            elif a.type == "x":
                a.index = x_count
                x_count += 1
            elif a.type == "u":
                a.index = u_count
                u_count += 1
            elif a.type == "s":
                a.index = s_count
                s_count += 1

    def word(self, word_id):
        try:
            return self.__words[word_id - 1]
        except:
            pass
#            print word_id, len(self.__words)
#            print "\n\n\n"
#            i = 0
#            for w in self.__words:
#                print i, w.id, w.lemma
#                i += 1
#            print len(self.__words)
#            print "\n\n\n"


    def deps(self, word, filt=None):
        deps = []
        for w in self.__words:
            if w.head == word.id:
                if filt is None or w.cpostag in filt:
                    deps.append(w)
        return deps

    def contains(self, word, lemma):
        deps = self.deps(word)
        new_deps = []
        while deps:
            for d in deps:
                if d.lemma == lemma:
                    return True
                else:
                    new_deps.extend(self.deps(d))
            deps = new_deps
            new_deps = []
        return False

    def remove_pred(self, word):
        for p in self.__visible_preds:
            if p.word.id == word.id:
                self.__removed_preds.append(p)
                p.word.important = False
                break
                #print p.word.lemma, "YES"
#                if p.word.cpostag in ["vb", "adj", "nn", "rb", "in"]:
#                    self.__removed_preds.append(p)
#                else:
#                    self.__visible_preds.remove(p)
#                break

    def remove_preds(self):
        confirnmed = []
        for p in self.__removed_preds:
            confirm_remove = True
            pw = p.word
            if pw.cpostag == "vb":
                for w in self.__words:
                    if w.id != pw.id and w.pred:
                        w_args = [a.resolve_link() for a in w.pred.args]
                        for a in p.args:
                            if a in w_args:
                                confirm_remove = False
#            if confirm_remove:
#                print "TO REMOVE:", w.lemma
            if confirm_remove:
                confirnmed.append(p.word.id)
                continue
        preds = self.__visible_preds[:]
#        print confirnmed
        for wid in confirnmed:
            for p in self.__visible_preds:
                if p.word.id == wid and not p.word.important:
                    preds.remove(p)

#                    print "REMOVED", p.word.lemma, p.word.important
        self.__visible_preds = preds
        self.__removed_preds = []

    def reassign_copulas(self):
        copulas = dict()
        other_w = []
        words = self.__words[:]
        for w in words:
            if w.cpostag == "vb" and w.lemma in self.copula_verbs and \
               w.pred and w.pred.args:
                copulas[w.pred.args[0].resolve_link()] = w
            else:
                other_w.append(w)
        if not copulas:
            return

        args_list = []
        for w in other_w:
            if w.pred and w.pred.args:
                args_list.append((w.lemma, w.pred.args))
        for ep in self.__extra_preds:
            args_list.append(ep)

        for lemma, args in args_list:
            for i, a in enumerate(args):
                c = copulas.get(a.resolve_link())
                if c:
                    for d in self.deps(c, filt=["nn", "adj", "pr"]):
                        if not d.pred or not d.pred.args or \
                           not d.deprel == u"присвяз":
                            continue
                        if d.cpostag == "nn" and d.pred and d.pred.args:
#                            print "YES", d.lemma, c.lemma
                            args[i] = d.pred.args[1]
                            d.important = True
#                            break
                        elif d.cpostag == "pr" and d.pred and d.pred.args:
                            args[i] = d.pred.args[0]
                            for dd in self.deps(c, filt=["nn", "adj", "pr"]):
                                if dd.cpostag == "nn" and \
                                   dd.deprel == u"предик":
                                    d.pred.args[1] = dd.pred.args[1]
#                            print "YES", d.lemma, c.lemma
                            d.pred.show_postag = False
                            d.important = True
                            self.__visible_preds.append(d.pred)
#                            break
                        elif d.cpostag == "adj" and d.pred and d.pred.args:
#                            print "YES", d.lemma, c.lemma
                            args[i] = d.pred.args[0]
                            d.important = True
#                            break


    def unfold_dep(self, word, until_tag="nn"):
        deps = list(self.deps(word))
        if len(deps) != 1:
            return None
        if deps[0].cpostag == until_tag:
            return deps[0]
        return self.unfold_dep(deps[0], until_tag)

    def format_pred(self, pred, sent_count=None):
        argsf = []
        for a in pred.args:
            argsf.append("%s%d" %
                        (a.resolve_link().type, a.resolve_link().index, ))
        if sent_count is not None and pred.show_index:
            id_text = "[%d]:" % (1000 * sent_count + pred.word.id)
        else:
            id_text = ""
        if pred.show_postag:
            cpostag = u"-%s" % pred.word.cpostag
        else:
            cpostag = ""
        return u"%s%s%s(%s)" % (id_text,
                                pred.prefix,
                                cpostag,
                                ",".join(argsf),)

    def format_epred(self, epred):
        prefix, args = epred
        argsf = []
        for a in args:
            if a.type in ["e", "x", "u", "s", ]:
                argsf.append("%s%d"
                             % (a.resolve_link().type,
                                a.resolve_link().index))
            else:
                argsf.append(a.type)
        return u"%s(%s)" % (prefix, ",".join(argsf), )

    def preprocess(self):
        words = self.__words[:]

        for i in xrange(0, len(self.__words) - 1):
            w1 = self.__words[i]
            w2 = self.__words[i + 1]

            if w1.lemma == u"а" and w2.lemma == u"также":
                w1.head = w2.head
                w1.lemma = u"и"
                w1.form = u"и"
                words.remove(w2)

        for w in words:
            if w.lemma == u"и":
                deps = self.deps(w)
                if len(deps) == 1 and \
                   w.deprel[0:4] == u"союз" and \
                   deps[0].deprel[0:4] == u"союз":
                    head = self.word(w.head)
                    if head:
                        hdeps = self.deps(head)
                        if len(hdeps) == 1:
                            hhead = head.head
                            head.head = w.id
                            w.head = hhead
            elif w.lemma == u"нет" or w.lemma == u"не":
                w.cpostag = "par"

        self.__words = words

    person_relative_pr = [
        u"который",
        u"которая",
        u"которое",
        u"кто",
    ]

    location_relative_pr = [
        u"где",
        u"куда",
    ]

    time_indicators = [
        u"год",
        u"месяц",
        u"день",
        u"час",
        u"минута",
        u"секунда",
        u"момент",
        u"период",
    ]

    def subordinate_relatives(self):
        # Relative clauses

        for w in self.__words:

            head = self.word(w.head)
            if not head:
                continue
            hhead = self.word(head.head)

            if w.cpostag == "pr":
                if not hhead:
                    continue
                if w.lemma in self.person_relative_pr and \
                   head.cpostag == "vb" and hhead.cpostag == "nn":
                    if hhead.feats[5] == "y":  # if animate
                        # 1. Person
                        self.__extra_preds.append(("person", [
                            Argument("e"),
                            Argument.arg_link(hhead.pred.args[1]),
                        ]))
                        if w.deprel == u"предик":
                            head.pred.args[1].link_to(hhead.pred.args[1])
                        elif w.deprel in [u"1-компл", u"2-комп"]:
                            # 3. Person
                            head.pred.args[2].link_to(hhead.pred.args[1])
                    else:
                        # 2. not Animate
                        if head.lemma == u"быть" and \
                           head.feats[3] == "s":  # looks like passive voice
                            for d in self.deps(head, filt=["vb"]):
                                if d.feats[7] == "p":  # yeah, passive voice
                                    d.pred.args[2].link_to(
                                        hhead.pred.args[1]
                                    )
                        else:
                            head.pred.args[2].link_to(
                                hhead.pred.args[1]
                            )

                # 4. Location
                elif w.lemma in self.location_relative_pr and \
                   head.cpostag == "vb" and hhead.cpostag == "nn":
                    self.__extra_preds.append(("loc", [
                        Argument("e"),
                        Argument.arg_link(hhead.pred.args[1]),
                        Argument.arg_link(head.pred.args[0]),
                    ]))

                # 5. Reason
#                elif (w.lemma in self.person_relative_pr and
#                      head.deprel == u"обст" and hhead.cpostag == "vb") or\
#                     ((w.lemma == u"почему" or w.lemma == u"зачем") and
#                      w.deprel == u"обст"):
#                elif (w.lemma == u"почему" or w.lemma == u"зачем") and \
#                      w.deprel == u"обст" and head.cpostag == "vb":
#                    if w.lemma in self.person_relative_pr:
#                        h_verb = hhead
#                    else:
#                    h_verb = head
#                    for d in self.deps(h_verb):
#                        if d.cpostag == "nn" and d.deprel == u"предик":
#                            self.__extra_preds.append(("reason", [
#                                Argument("e"),
#                                Argument.arg_link(d.pred.args[1]),
#                                Argument.arg_link(h_verb.pred.args[0]),
#                            ]))
#                            break

            # 6. Time

            # 6.1 Cases such "день/месяц/.., когда ..."
            elif w.lemma == u"когда":
                deps = list(self.deps(w))
                if len(deps) == 1 and deps[0].cpostag == "vb":
                    verb = deps[0]
                    time_pointer = None
                    if head.cpostag == "pr" and hhead and hhead.cpostag == "nn":
                        time_pointer = hhead
                    elif head.cpostag == "nn":
                        time_pointer = head
                    if time_pointer and \
                       time_pointer.lemma in self.time_indicators:
                        self.__extra_preds.append(("time", [
                            Argument("e"),
                            Argument.arg_link(time_pointer.pred.args[1]),
                            Argument.arg_link(verb.pred.args[0]),
                            ]))
                        break
            # 6.1 Cases such "день/месяц/.., в который ..."
            elif w.lemma in self.time_indicators and head.cpostag == "vb":
                time_pointer = w
                verb = head
                deps = self.deps(head)
                clause_detected = False
                for d in deps:
                    if d.lemma == u"в" and d.deprel == u"обст":
                        ddeps = self.deps(d)
                        for dd in ddeps:
                            if dd.lemma == u"который":
                                clause_detected = True
                if clause_detected:
                    self.__extra_preds.append(("time", [
                        Argument("e"),
                        Argument.arg_link(time_pointer.pred.args[1]),
                        Argument.arg_link(verb.pred.args[0]),
                    ]))

            # 7. Manner

            elif w.lemma == u"как" and head.cpostag == "nn":
                deps = self.deps(w)
                if len(deps) == 1 and deps[0].cpostag == "vb":
                    self.__extra_preds.append(("manner", [
                        Argument("e"),
                        Argument.arg_link(head.pred.args[1]),
                        Argument.arg_link(deps[0].pred.args[0]),
                    ]))

    def subordinate_whnominals(self):

        for w in self.__words:

            head = self.word(w.head)
            hhead = None
            if head:
                hhead = self.word(head.head)
            deps = self.deps(w, filt=("vb",))

            # 1. I know that he comes.
            deps2 = self.deps(w)
            if w.lemma == u"что" and w.cpostag == "cnj" and \
               head and head.cpostag == "vb" and \
               len(deps2) == 1 and \
               deps2[0].deprel == u"подч-союзн":
                if deps2[0].cpostag == "nn":
                    head.pred.args[2].link_to(deps2[0].pred.args[1])
                elif deps2[0].cpostag in ["vb", "pr", "adj"]:
                    head.pred.args[2].link_to(deps2[0].pred.args[0])

            # 2. I'm sure (that) he comes.
            if w.cpostag == "adj" and \
               len(deps) == 1 and deps[0].cpostag == "vb":
                self.__extra_preds.append(("compl", [
                    Argument("e"),
                    Argument.arg_link(w.pred.args[0]),
                    Argument.arg_link(deps[0].pred.args[0]),
                ]))

            # 3. I know what you want
            # if w.lemma == u"что" and w.cpostag == "cnj" and \
            #    (w.deprel == u"1-компл" or w.deprel == u"1-компл") and \
            #    head and head.cpostag == "vb" and \
            #    len(deps) == 1 and deps[0].cpostag == "vb" and\
            #    deps[0].deprel == u"подч-союзн":
            #     head.pred.args[2].link_to(deps[0].pred.args[0])

            # 4. I know whom you saw.
            if (w.lemma == u"кто" or w.lemma == u"что") and \
               w.cpostag == "pr" and head and head.cpostag == "vb" and\
               hhead and hhead.cpostag == "vb" and \
               (head.deprel == u"1-компл" or head.deprel == u"2-компл"):
                new_x = Argument("x")
                self.__extra_preds.append(("person", [
                    Argument("e"),
                    new_x,
                ]))
                self.__extra_preds.append(("wh", [
                    Argument("e"),
                    Argument.arg_link(new_x),
                ]))
                hhead.pred.args[2].link_to(head.pred.args[0])
                for d in self.deps(head, filt=["pr"]):
                    if d.deprel == u"предик":
                        head.pred.args[1].link_to(d.pred.args[1])
                        head.pred.args[2].link_to(new_x)
                        break

            # 5. I know where you live.
            if w.lemma == u"где" and head and hhead and \
               head.cpostag == "vb" and hhead.cpostag == "vb":
                for d in self.deps(head, filt=["pr"]):
                    if d.deprel == u"предик":
                        new_x = Argument("x")
                        self.__extra_preds.append(("loc", [
                            Argument("e"),
                            new_x,
                            head.pred.args[0],
                        ]))
                        wh_e = Argument("e")
                        self.__extra_preds.append(("wh", [
                            wh_e,
                            Argument.arg_link(new_x),
                         ]))
                        hhead.pred.args[2].link_to(wh_e)
                        head.pred.args[1].link_to(d.pred.args[1])
                        break

            # 6. I know how you live.
            # 7. I know when you come.
            # 8. I know why you go.
            lemma = w.lemma
            if (lemma == u"как" or lemma == u"когда" or lemma == u"зачем") \
               and w.cpostag == "cnj" and head and head.cpostag == "vb" and \
               len(deps) == 1 and deps[0].cpostag == "vb" and \
               deps[0].deprel == u"подч-союзн":
                for d in self.deps(deps[0]):
                    if d.cpostag == "pr" and d.deprel == u"предик":
                        new_x = Argument("x")
                        wh_e = Argument("e")
                        self.__extra_preds.append(("wh", [
                            wh_e,
                            new_x,
                        ]))
                        # 6, 7 or 8 depends on conjunction lemma
                        if w.lemma == u"как":
                            literal = "manner"
                        elif w.lemma == u"когда":
                            literal = "time"
                        else:
                            literal = "reason"
                        self.__extra_preds.append((literal, [
                            Argument("e"),
                            Argument.arg_link(new_x),
                            Argument.arg_link(deps[0].pred.args[0]),
                        ]))
                        head.pred.args[2].link_to(wh_e)

            # 8.2 I know why you go.
#            if (w.lemma == u"зачем" or w.lemma == u"почему") and head and \
#               head.cpostag == "vb"
#            if (w.lemma == u"почему" or w.lemma == u"зачем") and \
#               head and head.cpostag == "vb" and \
#               hhead and hhead.cpostag == "vb":
#                wh_e = Argument("e")
#                new_x = Argument("x")
#                self.__extra_preds.append(("wh", [
#                    wh_e,
#                    new_x,
#                ]))
#                self.__extra_preds.append(("reason", [
#                    Argument("e"),
#                    Argument.arg_link(new_x),
#                    Argument.arg_link(head.pred.args[0]),
#                ]))
#                hhead.pred.args[2].link_to(wh_e)

    def detect_questions(self):

        for w in self.__words:


            head = self.word(w.head)
            deps = self.deps(w, filt=("vb",))

            # 1. What did you do?
            if w.lemma == u"что" and head and head.cpostag == "vb" and \
               self.contains(head, "?"):
                hdeps = self.deps(head, filt=["pr", "nn"])
                for d in hdeps:
                    if d.deprel == u"предик":
                        if w.cpostag == "cnj":
                            new_x = Argument("x")
                            self.__extra_preds.append(("thing", [
                                Argument("e"),
                                new_x,
                            ]))
                        else:
                            new_x = w.pred.args[1]
                        self.__extra_preds.append(("whq", [
                            Argument("e"),
                            Argument.arg_link(new_x),
                        ]))
                        head.pred.args[2].link_to(new_x)

            # 2. Whom did you see?
            if w.lemma == u"кто" and head and head.cpostag == "vb" and \
               self.contains(w, "?"):
                hdeps = self.deps(head, filt=["pr", "nn"])
                for d in hdeps:
                    if d.deprel == u"предик":
                        new_x = Argument("x")
                        self.__extra_preds.append(("person", [
                            Argument("e"),
                            new_x,
                         ]))
                        self.__extra_preds.append(("whq", [
                            Argument("e"),
                            Argument.arg_link(new_x),
                         ]))
                        head.pred.args[2].link_to(new_x)

            # 3. When did you come?
            if w.lemma == u"когда" and deps:
                for d in deps:
                    if d.deprel == u"подч-союзн" and self.contains(d, "?"):
                        ddeps = self.deps(d, filt=["pr", "nn"])
                        for dd in ddeps:
                            if dd.deprel == u"предик":
                                new_x = Argument("x")
                                self.__extra_preds.append(("time", [
                                    Argument("e"),
                                    new_x,
                                    Argument.arg_link(d.pred.args[0])
                                ]))
                                self.__extra_preds.append(("whq", [
                                    Argument("e"),
                                    Argument.arg_link(new_x),
                                ]))

            # 4. Why did you come?
            if (w.lemma == u"зачем" or w.lemma == u"почему") and head and \
               head.cpostag == "vb" and self.contains(head, "?"):
                hdeps = self.deps(head, filt=["pr", "nn"])
                for d in hdeps:
                    if d.deprel == u"предик":
                        new_x = Argument("x")
                        self.__extra_preds.append(("reason", [
                            Argument("e"),
                            new_x,
                            Argument.arg_link(head.pred.args[0])
                        ]))
                        self.__extra_preds.append(("whq", [
                            Argument("e"),
                            Argument.arg_link(new_x),
                        ]))

            # 5. How did you come?
            if w.lemma == u"как" and head and head.cpostag == "vb" and \
               self.contains(head, "?"):
                hdeps = self.deps(head, filt=["pr", "nn"])
                for d in hdeps:
                    if d.deprel == u"предик":
                        new_x = Argument("x")
                        self.__extra_preds.append(("manner", [
                            Argument("e"),
                            new_x,
                            Argument.arg_link(head.pred.args[0])
                        ]))
                        self.__extra_preds.append(("whq", [
                            Argument("e"),
                            Argument.arg_link(new_x),
                        ]))

            # 7. Where did you come?
            if (w.lemma == u"куда" or w.lemma == u"зачем") and head and \
               head.cpostag == "vb" and self.contains(head, "?"):
                hdeps = self.deps(head, filt=["pr", "nn"])
                for d in hdeps:
                    if d.deprel == u"предик":
                        new_x = Argument("x")
                        self.__extra_preds.append(("loc", [
                            Argument("e"),
                            new_x,
                            Argument.arg_link(head.pred.args[0])
                        ]))
                        self.__extra_preds.append(("whq", [
                            Argument("e"),
                            Argument.arg_link(new_x),
                        ]))

    copula_verbs = [u"быть", u"являться", u"находиться"]

    def apply_vb_rules(self, word):

        # 1. Link arguments: subject - second arg, direct object - third arg,
        #    indirect object - fourth arg. Direct obj can be a clause; then the
        #    head of the clause should be used as the verb argument.

        w_subject = None
        d_object = None
        i_object = None

        deps = reversed(sorted(self.deps(word), key=lambda d: d.deprel))
        for dep in deps:
            ddeps = list(self.deps(dep))

            if dep.cpostag == "pr" and len(ddeps) > 0:
                dep = ddeps[0]
                if dep.cpostag == "vb":
                    d_object = dep.pred.args[0]
            elif dep.cpostag != "nn":
                new_dep = self.unfold_dep(dep, until_tag="nn")
                if new_dep:
                    dep = new_dep

            if dep.cpostag == "nn":
                if dep.deprel == u"предик":
                    w_subject = dep.pred.args[1]
                elif dep.deprel == u"1-компл" or dep.deprel == u"2-компл":
                    if dep.feats[4] in ["a", "g"]:  # not d_object and
                        d_object = dep.pred.args[1]
                    elif dep.feats[4] == "d":  # not i_object and
                        i_object = dep.pred.args[1]

        # 2. Argument control: first arguments of both verbs are the same.

        head = self.word(word.head)
        if head and head.cpostag == "vb" and not w_subject \
                and word.deprel != u"обств":
            # Use VERB#1 rule to find subject of the head
            w_subject = head.pred.args[1]
            head.pred.args[2].link_to(word.pred.args[0])

        # 3. If in  there are more than 3 cases which can be expressed without
        #    prepositions (e.g. Russian), then introduce additional predicates
        #    expressing these cases is need.

        if word.lemma not in self.copula_verbs:
            for dep in self.deps(word, filt=["nn"]):
                if dep.feats[4] == "i":  # instrumental
                    epred = ("instr", [
                            Argument("e"),
                            Argument.arg_link(word.pred.args[0]),
                            Argument.arg_link(dep.pred.args[1]),
                        ])
                    self.__extra_preds.append(epred)

        # 4. Add tense information if available from the parser.

        global VB_TENSE
        if VB_TENSE:
            if word.feats[3] == "s":  # if past
                epred = ("past", [Argument("e"), word.pred.args[0]])
                self.__extra_preds.append(epred)

            if word.feats[3] == "f":  # if furure
                epred = ("future", [Argument("e"), word.pred.args[0]])
                self.__extra_preds.append(epred)

        # 5. Copula expressed with a verb

        if word.lemma in self.copula_verbs:
            # TODO(vladimir@zvm.me): fix this
            self.remove_pred(word)
            # self.__visible_preds.remove(word.pred)
            nouns = []
            adjs = []
            preps = []
            head_was_used = False
            for dep in self.deps(word):
                if dep.cpostag not in ["nn", "adj", "in"]:
                    new_dep = self.unfold_dep(dep, "adj")
                    if not new_dep:
                        continue
                    else:
                        dep = new_dep

                if dep.cpostag == "nn":
                    nouns.append(dep)
                elif dep.cpostag == "adj":
                    adjs.append(dep)
                elif dep.cpostag == "in":
                    preps.append(dep)

            # number of dependents is equal to one
            # try to find use dependents of the head
            if len(nouns) + len(adjs) + len(preps) == 1:
                for dep in self.deps(head, filt=["nn", "adj", "in"]):
                    # if dep.cpostag not in ["nn", "adj", "in"]:
                    #     new_dep = self.unfold_dep(dep, "adj")
                    #     if not new_dep:
                    #         continue
                    #     else:
                    #         dep = new_dep
                    if dep.cpostag == "nn":
                        nouns.append(dep)
                    elif dep.cpostag == "adj":
                        adjs.append(dep)
                    elif dep.cpostag == "in":
                        preps.append(dep)

                if len(nouns) + len(adjs) + len(preps) > 1:
                    head_was_used = True

            # a) Nount + Noun
            if len(adjs) == 0 and len(nouns) == 2:
                if nouns[1].feats[4] == "i":
                    e = Argument("e")
                    self.__extra_preds.append(("equal", [
                            Argument("e"),
                            Argument.arg_link(nouns[0].pred.args[1]),
                            Argument.arg_link(nouns[1].pred.args[1]),
                        ]))

                    if head_was_used and head.cpostag == "adj":
                        head.pred.args[1].link_to(nouns[0].pred.args[1])
                        self.__extra_preds.append(("compl", [
                                e,
                                Argument.arg_link(head.pred.args[0]),
                                Argument.arg_link(e),
                            ]))

                else:
                    e = Argument("e")
                    self.__extra_preds.append(("equal", [
                            e,
                            Argument.arg_link(nouns[1].pred.args[1]),
                            Argument.arg_link(nouns[0].pred.args[1]),
                        ]))
                    if head_was_used and head.cpostag == "adj":
                        head.pred.args[1].link_to(nouns[1].pred.args[1])
                        self.__extra_preds.append(("compl", [
                                Argument("e"),
                                Argument.arg_link(head.pred.args[0]),
                                Argument.arg_link(e),
                            ]))

            # b) Noun + Adj
            elif len(adjs) >= 1 and len(nouns) == 1:
                for adj in adjs:
                    adj.pred.args[1].link_to(nouns[0].pred.args[1])

            # c) Nount + Prep
            elif len(nouns) == 1 and len(preps) == 1:
                ddeps = list(self.deps(preps[0]))
                if len(ddeps) == 1 and ddeps[0].cpostag == "nn":
                    preps[0].pred.args[1].link_to(nouns[0].pred.args[1],
                        force=True)
                    preps[0].pred.args[2].link_to(ddeps[0].pred.args[1],
                        force=True)

        # 6. Passive
        if head and head.cpostag == "vb" and \
            head.lemma == u"быть" and head.feats[3] == "s":
            for dep in self.deps(head, filt=["nn"]):
                if dep.deprel == u"предик":
                    word.pred.args[2].link_to(dep.pred.args[1])
                    if w_subject and w_subject.resolve_link() == \
                       dep.pred.args[1].resolve_link():
                        w_subject = None

        if w_subject:
            word.pred.args[1].link_to(w_subject)
        elif not word.pred.args[1].link:
            word.pred.args[1] = Argument("u")

        if d_object:
            word.pred.args[2].link_to(d_object)
        elif not word.pred.args[2].link:
            word.pred.args[2] = Argument("u")

        if i_object:
            word.pred.args[3].link_to(i_object)
        elif not word.pred.args[3].link:
            word.pred.args[3] = Argument("u")

        # return

    numeric_map = {
        u"ноль": 0,
        u"один": 1,
        u"два": 2,
        u"три": 3,
        u"четыре": 4,
        u"пять": 5,
        u"шесть": 6,
        u"семь": 7,
        u"восемь": 8,
        u"девять": 9,
        u"десять": 10,
        u"нулевой": 0,
        u"первый": 1,
        u"второй": 2,
        u"третий": 3,
        u"четвертый": 4,
        u"пятый": 5,
        u"шестой": 6,
        u"седьмой": 7,
        u"восьмой": 8,
        u"девятый": 9,
        u"десятый": 10,
    }

    def apply_nn_rules(self, word):

        # 1. Noun compounds: if there are noun compounds in the language you are
        #    working with, use the predicate "nn" to express it.

        # TODO(zaytsev@udc.edu): implement this

        # 2. Genitive: always use the predicate "of-in" for expressing
        #    genitives.

        head = self.word(word.head)

        if head.cpostag == "nn":

        #  Copula. Without a verb.

            if head.feats[4] == word.feats[4] and word.deprel == u"аппоз":
                epred = ("equal",
                            [Argument("e"),
                             word.pred.args[1],
                             head.pred.args[1],
                    ])
                self.__extra_preds.append(epred)

            elif word.feats[4] == "g":  # if genetive case
                epred = ("of-in",
                            [Argument("e"),
                             head.pred.args[1],
                             word.pred.args[1],
                    ])
                self.__extra_preds.append(epred)

        # 3. Add number information if available from the parser (if plural).
        global NN_NUMBER

        if NN_NUMBER:
            if word.feats[3] == "p":  # if plural
                epred = ("typelt", [
                        Argument("e"),
                        word.pred.args[1],
                        Argument("s"),
                    ])
                self.__extra_preds.append(epred)
                for dep in self.deps(word):
                    if dep.cpostag == "num":
                        try:
                            num = int(dep.form)
                            epred = ("card", [
                                Argument("e"),
                                word.pred.args[1],
                                Argument(str(num)),
                            ])
                            self.__extra_preds.append(epred)
                        except ValueError:
                            num = self.numeric_map.get(dep.form)
                            if num is not None:
                                epred = ("card", [
                                    Argument("e"),
                                    word.pred.args[1],
                                    Argument(str(num)),
                                ])
                            else:
                                epred = ("card", [
                                    Argument("e"),
                                    word.pred.args[1],
                                    Argument(dep.form),
                                ])
                            self.__extra_preds.append(epred)

        # 4. If there is other information available from the parser (e.g. type
        #    of the named entity), please add it.

        # TODO(zaytsev@udc.edu): implement this

        # 5. Coreferent Nouns

        if head and head.cpostag == "nn" and  word.deprel == u"предик":
            word.pred.args[1].link_to(head.pred.args[1])

    def apply_adj_rules(self, word):

        # 1. Adjectives share the second argument with the noun they are
        #    modifying

        head = self.word(word.head)
        if head and head.cpostag == "nn" and word.pred and head.pred:
            word.pred.args[1].link_to(head.pred.args[1])

    def apply_rb_rules(self, word):

        # 1. Second args of adverbs are verbs they are modifying.

        head = self.word(word.head)
        if head and head.pred:
            word.pred.args[1].link_to(head.pred.args[0])

    def apply_in_rules(self, word):

        head = self.word(word.head)

        # 1. Verb + noun.
        if head and head.cpostag == "vb":
            word.pred.args[1].link_to(head.pred.args[0])

        # 2. Noun + noun.
        elif head and head.cpostag == "nn":
            word.pred.args[1].link_to(head.pred.args[1])

        # 5. Adj + noun
        elif head and head.cpostag == "adj":
            word.pred.args[1].link_to(head.pred.args[0])

        for dep in self.deps(word, filt=["nn"]):
            if word.pred and dep.pred:
                word.pred.args[2].link_to(dep.pred.args[1])
                break

        # 3. Second arg is a prep
        # 4. Verb+verb

    pronouns_map = {
        u"он": "male",
        u"она": "female",
        u"оно": "neuter",
        u"я": "person",
        u"мы": "person",
        u"ты": "person",
        u"вы": "thing",
        u"они": "thing",
        u"это": "thing",
        u"эти": "thing",
    }

    def apply_pr_rules(self, word):

        # 1. Handle personal

        if word.lemma not in self.pronouns_map and word.cpostag == "pr":
            self.remove_pred(word)
        elif word.cpostag == "pr":
            word.cpostag = "nn"  # handle assumming that it's a noun
            word.pred.prefix = self.pronouns_map[word.lemma]
            word.pred.show_index = False
            word.pred.show_postag = False

            # Update FEATS according to NN specification
            word.feats = "".join([
                word.feats[0],  # 0 Noun
                word.feats[1],  # 1 Type
                word.feats[3],  # 2 Gender
                word.feats[4],  # 3 Number
                word.feats[5],  # 4 Case
                "?",            # 5 Animate
                "?",            # 6 Case2
            ])

            self.apply_nn_rules(word)

            global NN_NUMBER
            if NN_NUMBER:
                if word.feats[4] == "p":
                    self.__extra_preds.append(("typelt", [
                        Argument("e"),
                        Argument.arg_link(word.pred.args[1]),
                        Argument("s"),
                    ]))

        # 2. Handle reflexives

    def apply_cnj_rules(self, word):
        self.remove_pred(word)

        head = self.word(word.head)

        # 1. and, or

        if word.lemma == u"и" or word.lemma == u"или":
            if head.cpostag == "vb":
                for dep in self.deps(word):
                    if dep.cpostag == "vb":
                        dep.pred.args[1].link_to(head.pred.args[1])
                        if word.lemma == u"или":
                            self.__extra_preds.append(("or", [
                                    Argument("e"),
                                    Argument.arg_link(head.pred.args[0]),
                                    Argument.arg_link(dep.pred.args[0]),
                                ]))

            elif head.cpostag == "nn":
                for dep in self.deps(word):
                    if dep.cpostag == "nn":
                        hhead = self.word(head.head)
                        if hhead.cpostag == "vb":
                            new_word = WordToken(word=hhead)
                            vb_pred = Predicate(new_word, [
                                    Argument("e"),
                                    Argument.arg_link(hhead.pred.args[1]),
                                    Argument.arg_link(dep.pred.args[1]),
                                    Argument.arg_link(hhead.pred.args[3]),
                                ])
                            self.__visible_preds.append(vb_pred)
                            if word.lemma == u"или":
                                self.__extra_preds.append(("or", [
                                        Argument("e"),
                                        Argument.arg_link(hhead.pred.args[0]),
                                        Argument.arg_link(dep.pred.args[0]),
                                    ]))
        # 2. if

        elif word.lemma == u"если":
            if head.cpostag == "vb":
                for dep in self.deps(word):
                    if dep.cpostag == "vb":
                        self.__extra_preds.append(("imp", [
                            Argument("e"),
                            Argument.arg_link(dep.pred.args[0]),
                            Argument.arg_link(head.pred.args[0]),
                        ]))

        # 3. because, while, when

        # TODO(zaytsev@udc.edu): implement this

    def apply_par_rules(self, word):
        self.remove_pred(word)
        head = self.word(word.head)

        # 1. not

        if word.lemma == u"не":
            if head.cpostag == "vb":
                self.__extra_preds.append(("not", [
                    Argument("e"),
                    Argument.arg_link(head.pred.args[0]),
                ]))
            elif head.cpostag == "nn":
                self.__extra_preds.append(("not", [
                    Argument("e"),
                    Argument.arg_link(head.pred.args[1]),
                ]))

        if word.lemma == u"нет":
            deps = self.deps(word, filt=["nn", "pr"])
            for d in deps:
                new_e = Argument("e")
                self.__extra_preds.append(("be", [
                    new_e,
                    Argument.arg_link(d.pred.args[1]),
                    Argument("u")
                ]))
                self.__extra_preds.append(("not", [
                    Argument("e"),
                    new_e,
                ]))

    def init_predicate(self, word):
        args = [Argument("e")]\
             + [Argument("x") for _ in xrange(1, word.args)]
        pred = Predicate(word, args)
        word.pred = pred
        return pred

    def flush(self):
        self.__words = []
        self.__initial_preds = []
        self.__extra_preds = []
        self.__visible_preds = []

    def format_output(self, sent_count):

        # if self.wordid

        self.preprocess()

        for w in self.__words:

            if not w.cpostag or self.punct.match(w.lemma):
                continue

            if w.args != -1:
                pred = self.init_predicate(w)
                self.__initial_preds.append(pred)

        self.__visible_preds = self.__initial_preds[:]

        self.subordinate_whnominals()
        self.subordinate_relatives()
        self.detect_questions()

        for p in self.__initial_preds:
            if p.word.cpostag == "pr":
                self.apply_pr_rules(p.word)
            elif p.word.cpostag == "vb":
                self.apply_vb_rules(p.word)
            elif p.word.cpostag == "nn":
                self.apply_nn_rules(p.word)
            elif p.word.cpostag == "adj":
                self.apply_adj_rules(p.word)
            elif p.word.cpostag == "rb":
                self.apply_rb_rules(p.word)
            elif p.word.cpostag == "in":
                self.apply_in_rules(p.word)
            elif p.word.cpostag == "cnj":
                self.apply_cnj_rules(p.word)
            elif p.word.cpostag == "par":
                self.apply_par_rules(p.word)

        self.reassign_copulas()
        self.remove_preds()
        self.assign_indexes()

        predf = [self.format_pred(p, sent_count) for p in self.__visible_preds]
        epredf = [self.format_epred(ep) for ep in self.__extra_preds]
        sent_text = u" ".join([w.form for w in self.__words])
        id_text = u"id(%d)." % sent_count
        pred_text = " & ".join(predf + epredf)

        return sent_text, id_text, pred_text

    def sentid(self, wt):
        if wt.form[0:3] == "{{{" and\
           wt.form[len(wt.form) - 6:6] == "}}}!!!":
            return True, wt.form[3:len(wt.form) - 9]
        else:
            return False, None

    def add_line(self, malt_row):
        wt = WordToken(malt_row)
        self.__words.append(wt)


def text_id(malt_row):
    wt = WordToken(malt_row)
    if wt.form[0:3] == "{{{" and\
       wt.form[len(wt.form) - 6:len(wt.form)] == "}}}!!!":
        return True, wt.form[3:len(wt.form) - 6]
    else:
        return False, None


def process_sentences(sentences, mc):
    processed = []
    for sid, sent in sentences:
        for row in sent:
            mc.add_line(row)
        sent_text, id_text, pred_text = mc.format_output(sid)
        processed.append((sent_text, id_text, pred_text))
        mc.flush()
    return processed


def write_sentences(textid, processed_sentences, ofile):
    processed_sentences = filter(lambda s: len(s[2]) > 0, processed_sentences)
    if len(processed_sentences) == 0:
        return
    if not textid:
        for psent in processed_sentences:
            if psent[2]:
                ofile.write(("% " + ("%s\n%s\n%s\n\n" % psent)).encode("utf-8"))
    else:
        text = " ".join(map(lambda s: s[0], processed_sentences))
        preds = " & ".join(map(lambda s: s[2], processed_sentences))
        ofile.write(("% " + text + "\n").encode("utf-8"))
        ofile.write("id(%s).\n" % textid)
        ofile.write((preds + "\n").encode("utf-8"))
        ofile.write("\n")

def main():

    global NN_NUMBER
    global VB_TENSE

    parser = argparse.ArgumentParser(
        description="MaltParser output processing pipeline for Russian.")
    parser.add_argument("--input",
        help="The input CoNLL file to be processed. Default is stdin.",
        default=None)
    parser.add_argument("--output",
        help="Output file. Default is stdout.",
        default=None)
    parser.add_argument("--vbtense",
        help="Output file. Default is stdout.",
        default=False)
    parser.add_argument("--nnnumber",
        help="Output file. Default is stdout.",
        default=False)

    pa = parser.parse_args()

    NN_NUMBER = bool(pa.nnnumber)
    VB_TENSE = bool(pa.vbtense)

    ifile = open(pa.input, "r") if pa.input else sys.stdin
    ofile = open(pa.output, "w") if pa.output else sys.stdout

    mc = MaltConverter()
    line_splitter = re.compile("\s+")
    process_texts = False
    sentence = []
    sentences = []
    sentences_count = 1
    prev_textid = None


    for line in ifile:
        malt_row = line_splitter.split(line.decode("utf-8"))
        if len(malt_row) > 2:
            detected, textid = text_id(malt_row)
            if detected:
                if process_texts:
                    processed = process_sentences(sentences, mc)
                    write_sentences(prev_textid, processed, ofile)
                    sentences = []
                else:
                    processed = \
                        process_sentences([(sentences_count, sentence)], mc)
                    write_sentences(None, processed, ofile)
                    sentences = []
                process_texts = True
                prev_textid = textid
            else:
                sentence.append(malt_row)
        else:
            if sentence:
                if process_texts:
                    sentences.append((sentences_count, sentence))
                else:
                    processed = process_sentences([(sentences_count, sentence)], mc)
                    write_sentences(None, processed, ofile)
            sentence = []
            sentences_count += 1

    if sentences or sentence:
        if process_texts:
            processed = process_sentences(sentences, mc)
            write_sentences(prev_textid, processed, ofile)
        else:
            processed = process_sentences([(sentences_count, sentence)], mc)
            write_sentences(None, processed, ofile)


if __name__ == "__main__":
    main()
