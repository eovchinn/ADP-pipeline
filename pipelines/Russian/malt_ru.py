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

        self.lemma = self.lemma.replace(u"«", u"")
        self.lemma = self.lemma.replace(u"»", u"")
        self.form = self.form.replace(u"«", u"")
        self.form = self.form.replace(u"»", u"")

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
                arg_list.append(a.resolve_link())

        for pred in self.__visible_preds:
            for a in pred.args:
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
            elif a.type == "s":
                a.index = s_count
                s_count += 1

    def add_line(self, line):
        line = self.line_splitter.split(line.decode("utf-8"))
        if len(line) > 2:
            self.__words.append(WordToken(line))
            return True
        else:
            return

    def word(self, word_id):
        return self.__words[word_id - 1]

    def deps(self, word, filt=None):
        deps = []
        for w in self.__words:
            if w.head == word.id:
                if filt is None or w.cpostag in filt:
                    deps.append(w)
        return deps

    def remove_pred(self, word):
        for p in self.__visible_preds:
            if p.word.id == word.id:
                self.__visible_preds.remove(p)
                break

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
            argsf.append("%s%d" \
                % (a.resolve_link().type, a.resolve_link().index, ))
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
                argsf.append("%s%d"\
                             % (a.resolve_link().type,
                                a.resolve_link().index)
                )
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
                   deps[0:4].deprel == u"союз":
                    head = self.word(w.head)
                    if head:
                        hdeps = self.deps(head)
                        if len(hdeps) == 1:
                            hhead = head.head
                            head.head = w.id
                            w.head = hhead

        self.__words = words

    def subordinate_relatives(self):
        pass

    def subordinate_whnominals(self):
        pass

    def detect_questions(self):
        pass

    def format_output(self, sent_count):

        self.preprocess()

        for w in self.__words:

            if not w.cpostag or self.punct.match(w.lemma):
                continue

            if w.args != -1:
                pred = self.init_predicate(w)
                self.__initial_preds.append(pred)

        self.__visible_preds = self.__initial_preds[:]

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

        self.assign_indexes()

        predf = [self.format_pred(p, sent_count) for p in self.__visible_preds]
        epredf = [self.format_epred(ep) for ep in self.__extra_preds]
        sent_text = u"% " + u" ".join([w.form for w in self.__words])
        id_text = u"id(%d)." % sent_count
        pred_text = " & ".join(predf + epredf)

        return u"%s\n%s\n%s\n\n" % (sent_text, id_text, pred_text)

    copula_verbs = set([u"быть", u"являться", u"находиться"])

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
                    # print dep.lemma, dep.deprel
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
                    # print word.form, dep.form
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
            self.__visible_preds.remove(word.pred)
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
                # print "TRUE"
                # print nouns, adjs, preps
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

            # print word.form
            # print nouns, adjs, preps

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
                    if w_subject.resolve_link() == \
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

            # print head.lemma, word.lemma, head.feats[4] == word.feats[4]

            if head.feats[4] == word.feats[4]:
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
                            epred = None
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

    def apply_adj_rules(self, word):

        # 1. Adjectives share the second argument with the noun they are
        #    modifying

        head = self.word(word.head)
        if head and head.cpostag == "nn":
            word.pred.args[1].link_to(head.pred.args[1])

    def apply_rb_rules(self, word):

        # 1. Second args of adverbs are verbs they are modifying.

        head = self.word(word.head)
        if head and head.pred:
            word.pred.args[1].link_to(head.pred.args[0])

    def apply_in_rules(self, word):

        head = self.word(word.head)

        # 1. Verb + noun.
        if head.cpostag == "vb":
            word.pred.args[1].link_to(head.pred.args[0])

        # 2. Noun + noun.
        elif head.cpostag == "nn":
            word.pred.args[1].link_to(head.pred.args[1])

        # 5. Adj + noun
        elif head.cpostag == "adj":
            word.pred.args[1].link_to(head.pred.args[0])

        for dep in self.deps(word, filt=["nn"]):
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

        if word.lemma not in self.pronouns_map:
            self.remove_pred(word)
        else:
            word.cpostag = "nn"  # handle assumming that it's a noun
            word.pred.prefix = self.pronouns_map[word.lemma]
            word.pred.show_index = False
            word.pred.show_postag = False
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
        self.__initial_preds = []
        self.__extra_preds = []
        self.__visible_preds = []


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
