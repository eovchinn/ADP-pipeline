#!/usr/bin/python
# -*- coding: utf-8 -*-

# Contributors:
#   * Vladimir Zaytsev <vzaytsev@isi.edu> (2013)

import re

from conll import WordToken, NNHelper


class Argument(object):
    """
    Class representing predicate argument.
    """

    def __init__(self, arg_type):
        self.aid = None         # Unique ID of argument
        self.type = arg_type
        self.index = None
        self.link = None

    def link_to(self, another_arg, force=False):
        """
        Make argument pointing to another argument. Needed for processing
        the situations such that:
            % the book is red
            red-adj(e1,x1) & book-nn(e2,x2)
            ->
            red-adj(e1,x1) & book-nn(e2,x1)
        If <force> is True, than link argument to another even in case it's
        already linked.
        """
        if (not self.link or force) and self != another_arg:
            self.link = another_arg

    def resolve_link(self):
        """
        Return argument which this argument is pointing to, otherwise
        return itself.
        """
        if not self.link or self.link == self:
            return self
        else:
            return self.link.resolve_link()

    @staticmethod
    def link(arg):
        """
        Construct an argument instance already linked to another argument.
        """
        new_arg = Argument(arg.type)
        new_arg.link_to(arg)
        return new_arg

    @staticmethod
    def E():
        return Argument("e")

    @staticmethod
    def X():
        return Argument("x")

    @staticmethod
    def U():
        return Argument("u")

    def make_link(self):
        return Argument.link(self)

    def __repr__(self):
        arg = self.resolve_link()
        if arg.index:
            return u"%s%d" % (arg.type, arg.index, )
        else:
            return u"%s" % self.type


class AbsPredicate(object):

    def __init__(self):
        self.args = None
        self.prefix = None

    @property
    def e(self):
        if self.args and self.args[0].type == "e":
            return self.args[0]


class Predicate(AbsPredicate):
    """
    Class representing word predicate.
    """

    def __init__(self, word, args=tuple()):
        super(Predicate, self).__init__()
        self.word = word
        self.prefix = word.lemma
        self.args = list(args) # TODO(zaytsev@usc.edu): remove list call
        self.show_index = True
        self.show_postag = True
        
    def __int__(self):
        return 0 if self.pred is None else 1

    def __repr__(self):
        return u"<Predicate(prefix=%s, args=%r)>" % (self.prefix, self.args, )


class EPredicate(AbsPredicate):

    def __init__(self, prefix, args=tuple()):
        super(EPredicate, self).__init__()
        self.prefix = prefix
        self.args = list(args) # TODO(zaytsev@usc.edu): remove list call

    def __repr__(self):
        return u"<EPredicate(prefix=%s, args=%r)>" % (self.prefix, self.args, )


class MaltConverter(object):
    punct = re.compile("[\.,\?!{}()\[\]:;¿¡]")

    def __init__(self, process_vb_tense=False, process_nn_numbers=False):
        self.words = []
        self.initial_preds = []
        self.extra_preds = []
        self.visible_preds = []
        self.removed_preds = []

        self.e_count = 1
        self.x_count = 1
        self.u_count = 1
        self.s_count = 1

        self.NN_NUMBER = process_nn_numbers
        self.VB_TENSE = process_vb_tense

    def process_arguments(self):
        """
        Compute and assign index for each argument.
        """

        arg_set = set()
        arg_list = []

        for pred in self.visible_preds:
            a = pred.e.resolve_link()
            if a not in arg_set:
                arg_set.add(a.resolve_link())
                arg_list.append((pred, a.resolve_link()))

        for pred in self.visible_preds:
            for a in pred.args:
                if a.resolve_link() not in arg_set:
                    arg_set.add(a.resolve_link())
                    arg_list.append((pred, a.resolve_link()))

        for epred in self.extra_preds:
            for a in epred.args:
                if a.resolve_link() not in arg_set:
                    arg_set.add(a.resolve_link())
                    arg_list.append((epred, a.resolve_link()))

        for pred, a in arg_list:
            if a.type == "e":
                a.index = self.e_count
                self.e_count += 1
            elif a.type == "x":
                a.index = self.x_count
                self.x_count += 1
            elif a.type == "u":
                a.index = self.u_count
                self.u_count += 1
            elif a.type == "s":
                a.index = self.s_count
                self.s_count += 1

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
        argsf = []
        for a in epred.args:
            if a.type in ["e", "x", "u", "s", ]:
                argsf.append("%s%d"
                             % (a.resolve_link().type,
                                a.resolve_link().index))
            else:
                argsf.append(a.type)
        return u"%s(%s)" % (epred.prefix, ",".join(argsf), )

    def initialize_words(self):
        # Assign head and dependent words for each word
        # in the given sentence.
        for w in self.words:
            if w.head_id:
                try:
                    w.set_head(self.words[w.head_id - 1])
                except Exception:
                    pass
            deps = []
            for ww in self.words:
                if ww.head_id == w.id:
                    deps.append(ww)
            w.set_deps(deps)

    def preprocess(self):
        words = self.words[:]

        for i in xrange(0, len(self.words) - 1):
            w1 = self.words[i]
            w2 = self.words[i + 1]

            if w1.lemma == u"а" and w2.lemma == u"также":
                w1.set_head(w2.head)
                w1.lemma = u"и"
                w1.form = u"и"
                words.remove(w2)

        for w in words:
            if w.lemma == u"и":
                deps = w.deps()
                if len(deps) == 1 and\
                   w.deprel[0:4] == u"союз" and\
                   deps[0].deprel[0:4] == u"союз":
                    if w.head:
                        if w.head.deps() == 1:
                            hhead = w.head.head
                            w.head.set_head(w)
                            w.set_head(hhead)
            elif w.lemma == u"нет" or w.lemma == u"не":
                w.cpostag = "par"

        self.words = words

    def init_predicate(self, word):
        args = [Argument.E()]\
               + [Argument.X() for _ in xrange(1, word.args)]
        pred = Predicate(word, args)
        word.pred = pred
        return pred

    def flush(self):
        self.words = []
        self.initial_preds = []
        self.extra_preds = []
        self.visible_preds = []

    def flush_arg_indexes(self):
        self.e_count = 1
        self.x_count = 1
        self.u_count = 1
        self.s_count = 1

    def process(self, sent_count):

        self.initialize_words()
        self.preprocess()

        for w in self.words:

            if not w.cpostag or self.punct.match(w.lemma):
                continue

            if w.args != -1:
                pred = self.init_predicate(w)
                self.initial_preds.append(pred)

        self.visible_preds = self.initial_preds[:]

        self.subordinate_whnominals()
        self.subordinate_relatives()
        self.detect_questions()

        if self.NN_NUMBER:
            for word in self.words:
                if word.num:
                    self.apply_num_rules(word)
        for p in self.initial_preds:
            if p.word.pr:
                self.apply_pr_rules(p.word)
        for p in self.initial_preds:
            if p.word.vb:
                self.apply_vb_rules(p.word)
        for p in self.initial_preds:
            if p.word.nn:
                self.apply_nn_rules(p.word)
        for p in self.initial_preds:
            if p.word.adj:
                self.apply_adj_rules(p.word)
        for p in self.initial_preds:
            if p.word.rb:
                self.apply_rb_rules(p.word)
        for p in self.initial_preds:
            if p.word.prep:
                self.apply_in_rules(p.word)
        for p in self.initial_preds:
            if p.word.cnj:
                self.apply_cnj_rules(p.word)
        for p in self.initial_preds:
            if p.word.par:
                self.apply_par_rules(p.word)
        for p in self.initial_preds:
            if p.word.lemma == u"как":
                self.apply_in2_rules(p.word)

        self.reassign_copulas()

        if self.VB_TENSE:
            self.handle_tense()

        self.remove_preds()
        self.process_arguments()

        predf = [self.format_pred(p, sent_count) for p in self.visible_preds]
        epredf = [self.format_epred(ep) for ep in self.extra_preds]
        pred_text = " & ".join(predf + epredf)

        return pred_text

    def remove_pred(self, word):
        for p in self.visible_preds:
            if p.word.id == word.id:
                self.removed_preds.append(p)
                p.word.important = False
                break

    def remove_preds(self):
        for pred_to_remove in self.removed_preds:
            confirm_remove = True
            word_to_remove = pred_to_remove.word
            word_to_remove_args = [pred_to_remove.e]
            if word_to_remove.vb:
                for another_word in self.words:
                    if another_word.id != word_to_remove.id and \
                       another_word.pred:
                        another_word_args = another_word.pred.args
                        for a1 in word_to_remove_args:
                            for a2 in another_word_args:
                                if a2 != a2.resolve_link() and \
                                   a2.resolve_link() == a1 and \
                                   a1.type != "u":
                                    confirm_remove = False
            else:
                for another_word in self.words:
                    if another_word.id != word_to_remove.id and \
                       another_word.pred:
                        another_word_args = another_word.pred.args
                        for a1 in word_to_remove_args:
                            for a2 in another_word_args:
                                if a2.resolve_link() == a1.resolve_link():
                                    confirm_remove = False
            if confirm_remove:
                pred_to_remove.word.confirm_remove = True
                continue

        self.visible_preds = filter(lambda p: not p.word.confirm_remove,
                                    self.visible_preds[:])
        self.removed_preds = []

    def reassign_copulas(self):
        for w in self.words:

            if w.lemma in self.copula_verbs:
                # remove copula
                w.confirm_remove = True

            if w.vb and w.lemma in self.copula_verbs and \
               w.pred and w.pred.args and w.pred.args[1].type != "u":

                # Replace visible copulas by "exist" predicate:
                #
                # % У меня к нему отеческое чувство.
                #
                #   у-in(e1,x1,x2) & person(e2,x2) & к-in(e3,x1,x3) &
                #   male(e4,x3) & отеческий-adj(e5,x1) & чувство-nn(e6,x1) &
                #   exist(e7,x1)

                e_arg = w.pred.args[0]
                x_arg = w.pred.args[1]
                new_e = Argument.E()

                # if some another word has an arg pointing to copula then
                # redirect it to copula's 2nd arg (nn, adj or pr)

                for ww in self.words:
                    if ww.id != w.id and ww.pred and ww.pred.args:
                        for i, a in enumerate(ww.pred.args):
                            if a.resolve_link() == e_arg.resolve_link():
                                ww.pred.args[i] = Argument.link(x_arg)

                # do the same for the extra predicates

                for ep in self.extra_preds:
                    if ep.args:
                        for i, a in enumerate(ep.args):
                            if a.resolve_link() == e_arg:
                                if ep.prefix == "past":
                                #     ep.args[i] = Argument.link(new_e)
                                # else:
                                        ep.args[i] = Argument.link(x_arg)

                # # finally, add "exist" predicate
                # ep = EPredicate("exist", args=[
                #     new_e,
                #     Argument.link(x_arg),
                # ])
                # self.extra_preds.append(ep)

                # handle tense

                if w.feats[3] == "s":
                    ep = EPredicate("past", args=(
                        Argument.E(),
                        Argument.link(x_arg),
                    ))
                    self.extra_preds.append(ep)

                elif w.feats[3] == "f":
                    ep = EPredicate("future", args=(
                        Argument.E(),
                        Argument.link(x_arg),
                    ))
                    self.extra_preds.append(ep)

        # case with implicit copula verb

        # for w1 in self.words:
        #     if w1.nn:
        #         # check if noun has a verb
        #         has_a_verb = False
        #         x_arg = w1.pred.args[1].resolve_link()
        #         for w2 in self.words:
        #             if w2.vb and w2.pred and w2.pred.args:
        #                 v_args = [a.resolve_link() for a in w2.pred.args]
        #                 if x_arg in v_args:
        #                    has_a_verb = True
        #                    break
        #         if not has_a_verb:
        #             ep = EPredicate("exist", args=[
        #                 Argument.E(),
        #                 Argument.link(w1.pred.args[1]),
        #             ])
        #             self.extra_preds.append(ep)

    def handle_tense(self):

        for w in self.words:
            if w.vb and w.pred and not w.confirm_remove:

                if w.feats[3] == "s":  # if past
                    ep = EPredicate("past", args=(
                        Argument.E(),
                        Argument.link(w.pred.e),
                    ))
                    self.extra_preds.append(ep)

                elif w.feats[3] == "f" and w.pred:  # if furure
                    ep = EPredicate("future", args=(
                        Argument.E(),
                        Argument.link(w.pred.e),
                    ))
                    self.extra_preds.append(ep)


    # TODO(zaytsev@usc.edu): deprecated
    def __reassign_copulas(self):

        copulas = dict()
        other_w = []
        words = self.words[:]
        for w in words:
            if w.vb and w.lemma in self.copula_verbs and \
               w.pred and w.pred.args:
                copulas[w.pred.e.resolve_link()] = w
            else:
                other_w.append(w)
        if not copulas:
            return
        args_list = []
        for w in other_w:
            if w.pred and w.pred.args:
                args_list.append((w.lemma, w.pred.args))
        for ep in self.extra_preds:
            args_list.append((ep.prefix, ep.args, ))

        for prefix, args in args_list:
            for i, a in enumerate(args):
                c = copulas.get(a.resolve_link())
                if c:
                    for d in c.deps(filtr=["nn", "adj", "pr"]):
                        if not d.pred or not d.pred.args or \
                           not d.deprel == u"присвяз":
                            continue
                        if d.nn and d.pred and d.pred.args:
                            args[i] = d.pred.args[1]
                            d.important = True
                        elif d.pr and d.pred and d.pred.args:
                            args[i] = d.pred.e
                            for dd in c.deps(filtr=["nn", "adj", "pr"]):
                                if dd.nn and \
                                   dd.deprel == u"предик":
                                    d.pred.args[1] = dd.pred.args[1]
                            d.pred.show_postag = False
                            d.important = True
                            self.visible_preds.append(d.pred)
                        elif d.adj and d.pred and d.pred.args:
                            args[i] = d.pred.e
                            d.important = True

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

        for w in self.words:

            head = w.head
            if not w.head or not head.pred:
                continue
            hhead = head.head

            if w.pr:
                if not hhead:
                    continue
                if w.lemma in self.person_relative_pr and head.vb and hhead.nn and head.pred:
                    if hhead.feats[5] == "y" and hhead.pred:  # if animate
                        # 1. Person
                        ep = EPredicate("person", args=(
                            Argument.E(),
                            Argument.link(hhead.pred.args[1]),
                        ))
                        self.extra_preds.append(ep)
                        if w.deprel == u"предик":
                            head.pred.args[1].link_to(hhead.pred.args[1])
                        elif w.deprel in [u"1-компл", u"2-комп"]:
                            # 3. Person
                            head.pred.args[2].link_to(hhead.pred.args[1])
                    else:
                        # 2. not Animate
                        if head.lemma == u"быть" and \
                           head.feats[3] == "s":  # looks like passive voice
                            for d in head.deps(filtr=["vb"]):
                                if d.feats[7] == "p":  # yeah, passive voice
                                    d.pred.args[2].link_to(
                                        hhead.pred.args[1]
                                    )
                        elif head.pred and hhead.pred:
                            head.pred.args[2].link_to(
                                hhead.pred.args[1]
                            )

                # 4. Location
                elif w.lemma in self.location_relative_pr and \
                   head.vb and hhead.nn and head.pred and hhead.pred:
                    ep = EPredicate("loc", args=(
                        Argument.E(),
                        Argument.link(hhead.pred.args[1]),
                        Argument.link(head.pred.e),
                    ))
                    self.extra_preds.append(ep)

            # 6. Time

            # 6.1 Cases such "день/месяц/.., когда ..."
            elif w.lemma == u"когда":
                deps = w.deps()
                if len(deps) == 1 and deps[0].vb:
                    verb = deps[0]
                    time_pointer = None
                    if head.pr and hhead and hhead.nn:
                        time_pointer = hhead
                    elif head.nn:
                        time_pointer = head
                    if time_pointer and \
                       time_pointer.lemma in self.time_indicators:
                        ep = EPredicate("time", args=(
                            Argument.E(),
                            Argument.link(time_pointer.pred.args[1]),
                            Argument.link(verb.pred.e),
                        ))
                        self.extra_preds.append(ep)
                        break
            # 6.1 Cases such "день/месяц/.., в который ..."
            elif w.lemma in self.time_indicators and head.vb:
                time_pointer = w
                verb = head
                deps = head.deps()
                clause_detected = False
                for d in deps:
                    if d.lemma == u"в" and d.deprel == u"обст":
                        ddeps = d.deps()
                        for dd in ddeps:
                            if dd.lemma == u"который":
                                clause_detected = True
                if clause_detected:
                    ep = EPredicate("time", args=(
                        Argument.E(),
                        Argument.link(time_pointer.pred.args[1]),
                        Argument.link(verb.pred.e),
                    ))
                    self.extra_preds.append(ep)

            # 7. Manner

            elif w.lemma == u"как" and head.nn:
                deps = w.deps()
                if len(deps) == 1 and deps[0].vb:
                    ep = EPredicate("manner", args=(
                        Argument.E(),
                        Argument.link(head.pred.args[1]),
                        Argument.link(deps[0].pred.e),
                    ))
                    self.extra_preds.append(ep)

    def subordinate_whnominals(self):

        for w in self.words:

            head = w.head
            hhead = head.head if head else None
            deps = w.deps(filtr=("vb",))

            # 1. I know that he comes.
            deps2 = w.deps()
            if w.lemma == u"что" and w.cnj and \
               head and head.vb and head.pred and \
               len(deps2) == 1 and deps2[0].pred and \
               deps2[0].deprel == u"подч-союзн":
                if deps2[0].nn:
                    head.pred.args[2].link_to(deps2[0].pred.args[1])
                elif deps2[0].cpostag in ["vb", "pr", "adj"]:
                    head.pred.args[2].link_to(deps2[0].pred.e)

            # 2. I'm sure (that) he comes.
            if w.adj and w.pred and \
               len(deps) == 1 and deps[0].vb and deps[0].pred:
                ep = EPredicate("compl", args=(
                    Argument.E(),
                    Argument.link(w.pred.e),
                    Argument.link(deps[0].pred.e),
                ))
                self.extra_preds.append(ep)

            # 4. I know whom you saw.
            if (w.lemma == u"кто" or w.lemma == u"что") and \
               w.pr and head and head.pred and head.vb and\
               hhead and hhead.vb and \
               (head.deprel == u"1-компл" or head.deprel == u"2-компл"):
                new_x = Argument.X()
                ep1 = EPredicate("person", args=(
                    Argument.E(),
                    new_x,
                ))
                ep2 = EPredicate("wh", args=(
                    Argument.E(),
                    Argument.link(new_x),
                ))
                self.extra_preds.extend((ep1, ep2, ))
                hhead.pred.args[2].link_to(head.pred.e)
                for d in head.deps(filtr=["pr"]):
                    if d.deprel == u"предик":
                        head.pred.args[1].link_to(d.pred.args[1])
                        head.pred.args[2].link_to(new_x)
                        break

            # 5. I know where you live.
            if w.lemma == u"где" and head and hhead and head.pred and head.vb and hhead.vb:
                for d in head.deps(filtr=["pr"]):
                    if d.deprel == u"предик":
                        new_x = Argument.X()
                        new_e = Argument.E()
                        ep1 = EPredicate("loc", args=(
                            Argument.E(),
                            new_x,
                            head.pred.e,
                        ))
                        ep2 = EPredicate("wh", args=(
                            new_e,
                            Argument.link(new_x),
                        ))
                        self.extra_preds.extend((ep1, ep2, ))
                        hhead.pred.args[2].link_to(new_e)
                        head.pred.args[1].link_to(d.pred.args[1])
                        break

            # 6. I know how you live.
            # 7. I know when you come.
            deps = w.deps()
            if (w.lemma == u"как" or w.lemma == u"когда") \
               and (w.cnj or w.pr) and head and head.vb and head.pred \
               and len(deps) == 1 and deps[0].vb:
                for d in deps[0].deps():
                    if d.pr and d.deprel == u"предик":
                        # 6 or 7 depends on the conjunction lemma
                        literal = "manner" if w.lemma == u"как" else "time"
                        new_x = Argument.X()
                        new_e = Argument.E()
                        ep1 = EPredicate("wh", args=(new_e, new_x, ))
                        ep2 = EPredicate(literal, args=(
                            Argument.E(),
                            Argument.link(new_x),
                            Argument.link(deps[0].pred.e),
                        ))
                        self.extra_preds.extend([ep1, ep2, ])
                        head.pred.args[2].link_to(new_e)

            # 8. I know why you go.
            if (w.lemma == u"зачем" or w.lemma == u"почему") and \
               head and head.vb and head.pred and hhead and hhead.pred and hhead.vb:
                new_x = Argument.X()
                new_e = Argument.E()
                ep1 = EPredicate("wh", args=(new_e, new_x))
                ep2 = EPredicate("reason", args=(
                    Argument.E(),
                    Argument.link(new_x),
                    Argument.link(head.pred.e),
                ))
                hhead.pred.args[2].link_to(new_e)
                self.extra_preds.extend([ep1, ep2, ])

    def detect_questions(self):

        for w in self.words:

            head = w.head
            deps = w.deps(filtr=("vb",))

            # 1. What did you do?
            if w.lemma == u"что" and head and head.vb and\
               head.contains("?") and head.pred:
                hdeps = head.deps(filtr=["pr", "nn"])
                for d in hdeps:
                    if d.deprel == u"предик":
                        new_x = None
                        if w.cnj:
                            new_x = Argument.X()
                            ep = EPredicate("thing", args=(
                                Argument.E(),
                                new_x,
                            ))
                            self.extra_preds.append(ep)
                        elif w.pred is not None:
                            new_x = w.pred.args[1]
                        ep = EPredicate("whq", args=(
                            Argument.E(),
                            Argument.link(new_x),
                        ))
                        self.extra_preds.append(ep)
                        head.pred.args[2].link_to(new_x)

            # 2. Whom did you see?
            if w.lemma == u"кто" and head and head.vb and\
               w.contains("?"):
                hdeps = head.deps(filtr=["pr", "nn"])
                for d in hdeps:
                    if d.deprel == u"предик":
                        new_x = Argument.X()
                        ep1 = EPredicate("person", args=(
                            Argument.E(),
                            new_x,
                        ))
                        ep2 = EPredicate("whq", args=(
                            Argument.E(),
                            Argument.link(new_x),
                        ))
                        self.extra_preds.extend((ep1, ep2, ))
                        head.pred.args[2].link_to(new_x)

            # 3. When did you come?
            if w.lemma == u"когда" and deps:
                for d in deps:
                    if d.deprel == u"подч-союзн" and d.contains("?"):
                        ddeps = d.deps(filtr=["pr", "nn"])
                        for dd in ddeps:
                            if dd.deprel == u"предик":
                                new_x = Argument.X()
                                ep1 = EPredicate("time", args=(
                                    Argument.E(),
                                    new_x,
                                    Argument.link(d.pred.e)
                                ))
                                ep2 = EPredicate("whq", args=(
                                    Argument.E(),
                                    Argument.link(new_x),
                                ))
                                self.extra_preds.extend((ep1, ep2))

            # 4. Why did you come?
            if (w.lemma == u"зачем" or w.lemma == u"почему") and head and \
               head.vb and head.contains("?"):
                hdeps = head.deps(filtr=["pr", "nn"])
                for d in hdeps:
                    if d.deprel == u"предик":
                        new_x = Argument.X()
                        ep1 = EPredicate("reason", args=(
                            Argument.E(),
                            new_x,
                            Argument.link(head.pred.e)
                        ))
                        ep2 = EPredicate("whq", args=(
                            Argument.E(),
                            Argument.link(new_x),
                        ))
                        self.extra_preds.extend((ep1, ep2))

            # 5. How did you come?
            if w.lemma == u"как" and head and head.vb and\
               head.contains("?"):
                hdeps = head.deps(filtr=["pr", "nn"])
                for d in hdeps:
                    if d.deprel == u"предик":
                        new_x = Argument.X()
                        ep1 = EPredicate("manner", args=(
                            Argument.E(),
                            new_x,
                            Argument.link(head.pred.e)
                        ))
                        ep2 = EPredicate("whq", args=(
                            Argument.E(),
                            Argument.link(new_x),
                        ))
                        self.extra_preds.extend((ep1, ep2, ))

            # 7. Where did you come?
            if (w.lemma == u"куда" or w.lemma == u"зачем") and head and \
               head.vb and head.contains("?"):
                hdeps = head.deps(filtr=["pr", "nn"])
                for d in hdeps:
                    if d.deprel == u"предик":
                        new_x = Argument.X()
                        ep1 = EPredicate("loc", args=(
                            Argument.E(),
                            new_x,
                            Argument.link(head.pred.e)
                        ))
                        ep2 = EPredicate("whq", args=(
                            Argument.E(),
                            Argument.link(new_x),
                        ))
                        self.extra_preds.extend((ep1, ep2, ))

    copula_verbs = [u"быть", u"являться", u"находиться"]

    def apply_vb_rules(self, word):

        # 1. Link arguments: subject - second arg, direct object - third arg,
        #    indirect object - fourth arg. Direct obj can be a clause; then the
        #    head of the clause should be used as the verb argument.

        w_subject = None
        d_object = None
        i_object = None

        deps = reversed(sorted(word.deps(), key=lambda d: d.deprel))

        for dep in deps:
            
            if dep.pred:
            
                ddeps = list(dep.deps())

                if dep.pr and len(ddeps) > 0:
                    d_object = dep.pred.e
                elif dep.rb and dep.pred: # TODO(zaytsev@usc.edu): check when it does not have pred
                    d_object = dep.pred.e
                elif not dep.nn:
                    new_dep = dep.unfold_dep(until_tag="nn")
                    if new_dep:
                        dep = new_dep

                if dep.nn and dep.pred:
                    if dep.deprel == u"предик" and dep.pred and dep.pred.args:
                        w_subject = dep.pred.args[1]
                    elif dep.deprel == u"1-компл" or dep.deprel == u"2-компл":
                        if dep.feats[4] in ["a", "g"]:  # not d_object and
                            d_object = dep.pred.args[1]
                        elif dep.feats[4] == "d":  # not i_object and
                            i_object = dep.pred.args[1]

        # 2. Argument control: first arguments of both verbs are the same.

        head = word.head
        if head and head.vb and head.pred and not w_subject \
                and word.deprel != u"обств" and \
                (word.deprel == u"1-компл" or word.deprel == u"2-компл"):
            w_subject = head.pred.args[1]
            head.pred.args[2].link_to(word.pred.e)

        # 3. If in  there are more than 3 cases which can be expressed without
        #    prepositions (e.g. Russian), then introduce additional predicates
        #    expressing these cases is need.

        if word.lemma not in self.copula_verbs:
            for dep in word.deps(filtr=["nn"]):
                if dep.feats[4] == "i" and dep.pred:  # instrumental
                    ep = EPredicate("instr", args=(
                        Argument.E(),
                        Argument.link(word.pred.e),
                        Argument.link(dep.pred.args[1]),
                    ))
                    self.extra_preds.append(ep)

        # 4. Add tense information if available from the parser.

        # See <handle_tense> method

        # 5. Copula expressed with a verb

        if word.lemma in self.copula_verbs:
            self.remove_pred(word)
            nouns = []
            adjs = []
            preps = []
            head_was_used = False
            for dep in word.deps():
                if dep.cpostag not in ["nn", "adj", "in"]:
                    new_dep = dep.unfold_dep("adj")
                    if not new_dep:
                        continue
                    else:
                        dep = new_dep
                if dep.nn:
                    nouns.append(dep)
                elif dep.adj:
                    adjs.append(dep)
                elif dep.prep:
                    preps.append(dep)

            # number of dependents is equal to one
            # try to find use dependents of the head
            if head and len(nouns) + len(adjs) + len(preps) == 1:
                for dep in head.deps(filtr=("nn", "adj", "in")):
                    if dep.nn:
                        nouns.append(dep)
                    elif dep.adj:
                        adjs.append(dep)
                    elif dep.prep:
                        preps.append(dep)

                if len(nouns) + len(adjs) + len(preps) > 1:
                    head_was_used = True

            # a) Noun + noun
            if len(adjs) == 0 and len(nouns) == 2 and \
               nouns[1].pred and nouns[0].pred:
                # TODO: check this
                if nouns[1].feats[4] == "i":
                    ep1 = EPredicate("equal", args=(
                        Argument.E(),
                        Argument.link(nouns[0].pred.args[1]),
                        Argument.link(nouns[1].pred.args[1]),
                    ))
                    self.extra_preds.append(ep1)

                    if head_was_used and head.adj:
                        head.pred.args[1].link_to(nouns[0].pred.args[1])
                        ep2 = EPredicate("compl", args=(
                            Argument.E(),
                            Argument.link(head.pred.e),
                            Argument.link(ep1.e),
                        ))
                        self.extra_preds.append(ep2)

                # else:
                    # ep1 = EPredicate("equal", args=(
                    #     Argument.E(),
                    #     Argument.link(nouns[1].pred.args[1]),
                    #     Argument.link(nouns[0].pred.args[1]),
                    # ))
                    # self.extra_preds.append(ep1)

                    # if head_was_used and head.adj:
                    #     head.pred.args[1].link_to(nouns[1].pred.args[1])
                    #     ep2 = EPredicate("compl", args=(
                    #         Argument.E(),
                    #         Argument.link(head.pred.e),
                    #         Argument.link(ep1.e),
                    #     ))
                    #     self.extra_preds.append(ep2)

            # b) Noun + Adj
            elif len(adjs) >= 1 and len(nouns) == 1:
                for adj in adjs:
                    if nouns[0].pred and adj.pred:
                        adj.pred.args[1].link_to(nouns[0].pred.args[1])

            # c) Nount + Prep
            elif len(nouns) == 1 and len(preps) == 1:
                ddeps = list(preps[0].deps())
                if len(ddeps) == 1 and ddeps[0].nn and \
                   nouns[0].pred and ddeps[0].pred and preps[0].pred:
                    preps[0].pred.args[1].link_to(nouns[0].pred.args[1],
                        force=True)
                    preps[0].pred.args[2].link_to(ddeps[0].pred.args[1],
                        force=True)

        # 6. Passive
        if head and head.vb and \
            head.lemma == u"быть" and head.feats[3] == "s":
            for dep in head.deps(filtr=["nn"]):
                if dep.deprel == u"предик" and dep.pred:
                    word.pred.args[2].link_to(dep.pred.args[1])
                    if w_subject and w_subject.resolve_link() == \
                       dep.pred.args[1].resolve_link():
                        w_subject = None

        if word.deprel == u"опред" and head and head.nn and head.pred and \
           head.pred.args:
            # word.feats[7] == "p" => passive
            if d_object is None and word.feats[7] == "p":
                d_object = Argument.link(head.pred.args[1])
            # word.feats[7] == "a" => active
            elif w_subject is None and word.feats[7] == "a":
                w_subject = Argument.link(head.pred.args[1])
            # word.feats[7] == "m" => medial but systematicly it's active
            elif w_subject is None and word.feats[7] == "m":
                w_subject = Argument.link(head.pred.args[1])

        if w_subject:
            word.pred.args[1].link_to(w_subject)
        elif not word.pred.args[1].link:
            word.pred.args[1] = Argument.U()

        if d_object:
            word.pred.args[2].link_to(d_object)
        elif not word.pred.args[2].link:
            word.pred.args[2] = Argument.U()

        if i_object:
            word.pred.args[3].link_to(i_object)
        elif not word.pred.args[3].link:
            word.pred.args[3] = Argument.U()

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

    def apply_num_rules(self, word):
        head = word.head
        if head and (head.nn or head.adj or head.pr) and head.pred and \
           head.pred.args:
            x_arg = Argument.link(head.pred.args[1])
        else:
            x_arg = Argument.U()
        try:
            num_arg = int(word.lemma)
        except ValueError:
            num_arg = self.numeric_map.get(word.lemma)
            if num_arg is None:
                num_arg = word.lemma

        ep = EPredicate("card", args=(
            Argument.E(),
            x_arg,
            Argument(unicode(num_arg)),
        ))
        self.extra_preds.append(ep)

    genitive_indicators = (
        u"мой",
        u"твой",
        u"ее",
        u"её",
        u"его",
        u"их",
    )

    coference_deprels_1 = [
        u"ROOT",
        u"соч-союзн",
        u"подч-союзн",
        u"предик",
        u"предл",
    ]

    def apply_nn_rules(self, word):

        # 1. Noun compounds: if there are noun compounds in the language you are
        #    working with, use the predicate "nn" to express it.

        # TODO(zaytsev@udc.edu): implement this

        # 2. Genitive: always use the predicate "of-in" for expressing
        #    genitives.

        head = word.head

        if head and head.nn:

            if head.feats[4] == word.feats[4] and word.deprel == u"аппоз":
                pass
            elif word.feats[4] == "g" and head.pred and head.pred.args:  # if genitive case
                ep = EPredicate("of-in", args=(
                    Argument.E(),
                    Argument.link(head.pred.args[1]),
                    Argument.link(word.pred.args[1]),
                ))
                self.extra_preds.append(ep)
            # elif word.lemma in self.genitive_indicators and head.nn:
            #     ep = EPredicate("of-in", args=(
            #         Argument.E(),
            #         Argument.link(word.pred.args[1]),
            #         Argument.link(head.pred.args[1]),
            #     ))
            #     self.extra_preds.append(ep)

        # 3. Add number information if available from the parser (if plural).

        if self.NN_NUMBER:

            if word.feats[3] == "p":  # if plural
                ep = EPredicate("typelt", args=(
                    Argument.E(),
                    Argument.link(word.pred.args[1]),
                    Argument("s"),
                ))
                self.extra_preds.append(ep)

        # 4. If there is other information available from the parser (e.g. type
        #    of the named entity), please add it.

        # TODO(zaytsev@udc.edu): implement this

        # 5. Coreferent Nouns

        if head and head.nn and head.pred and word.feats[4] == head.feats[4]:
            if word.deprel == u"предик" and \
               head.deprel in self.coference_deprels_1:
                ep = EPredicate("equal", args=(
                    Argument.E(),
                    Argument.link(word.pred.args[1]),
                    Argument.link(head.pred.args[1]),
                ))
                self.extra_preds.append(ep)
            elif word.deprel == u"аппоз" and head.pred:
                word.pred.args[1].link_to(head.pred.args[1])

    def apply_adj_rules(self, word):

        # 1. Adjectives share the second argument with the noun they are
        #    modifying

        head = word.head
        if head and (head.nn or head.adj) and word.pred and head.pred:
            word.pred.args[1].link_to(head.pred.args[1])

    def apply_rb_rules(self, word):

        # 1. Second args of adverbs are verbs they are modifying.

        head = word.head
        if head and head.pred:
            word.pred.args[1].link_to(head.pred.e)

    def apply_in_rules(self, word):

        head = word.head

        # 1. Verb + noun.
        if head and head.vb and head.pred:
            word.pred.args[1].link_to(head.pred.e)

        # 2. Noun + noun.
        elif head and head.nn and head.pred and word.pred:
            word.pred.args[1].link_to(head.pred.args[1])

        # 5. Adj + noun
        elif head and head.adj and head.pred:
            word.pred.args[1].link_to(head.pred.e)

        for dep in word.deps(filtr=["nn", "pr"]):
            if word.pred and dep.pred:
                word.pred.args[2].link_to(dep.pred.args[1])
                dep.important = True
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
        u"один": "thing",
        u"другой": "thinkg",
        u"что-то": "thing",
        u"кто-то": "person",
    }

    possessives_map = {
        u"твой": "person",
        u"твоя": "person",
        u"твое": "person",
        u"твоё": "person",
        u"мой": "person",
        u"моя": "person",
        u"мое": "person",
        u"моё": "person",
        u"его": "male",
        u"ее": "female",
        u"её": "female",
        u"их": "thing",
        u"наш": "thing",
        u"наша": "thing",
        u"наше": "thing",
        u"наши": "thing",
        u"ваш": "thing",
        u"ваша": "thing",
        u"ваше": "thing",
        u"ваши": "thing",
    }

    def apply_pr_rules(self, word):

        # 1. Handle personal

        if word.lemma not in self.pronouns_map and word.pr and \
           word.lemma not in self.possessives_map.keys():
            self.remove_pred(word)
        elif word.pr:

            prefix = self.pronouns_map.get(word.lemma)
            if not prefix:
                prefix = self.possessives_map[word.lemma]

            word.pe = False
            word.nn = NNHelper(word)
            word.cpostag = "nn"
            word.pred.prefix = prefix
            word.pred.show_index = False
            word.pred.show_postag = False

            # Update FEATS according to NN specification
            word.feats = "".join((
                word.feats[0],  # 0 Noun
                word.feats[1],  # 1 Type
                word.feats[3],  # 2 Gender
                word.feats[4],  # 3 Number
                word.feats[5],  # 4 Case
                "?",            # 5 Animate
                "?",            # 6 Case2
            ))

            # self.apply_nn_rules(word)

            # if self.NN_NUMBER:
            #     if word.feats[3] == "p":
            #         ep = EPredicate("typelt", args=(
            #             Argument.E(),
            #             Argument.link(word.pred.args[1]),
            #             Argument("s"),
            #         ))
            #         self.extra_preds.append(ep)

        # 2. Handle reflexives

        # 3. Possessive pronouns

        if word.pr and word.lemma in self.possessives_map.keys() and \
           word.head and (word.head.nn or word.head.adj or word.head.pr) \
           and word.head.pred and word.pred:
            ep = EPredicate("of-in", args=(
                Argument.E(),
                Argument.link(word.head.pred.args[1]),
                Argument.link(word.pred.args[1]),
            ))
            self.extra_preds.append(ep)

    def apply_cnj_rules(self, word):
        self.remove_pred(word)

        head = word.head

        # # 1. and, or
        #
        # if word.lemma == u"и" or word.lemma == u"или":
        #     if head and head.vb:
        #         for dep in word.deps():
        #             if dep.vb:
        #                 dep.pred.args[1].link_to(head.pred.args[1])
        #                 if word.lemma == u"или":
        #                     ep = EPredicate("or", args=(
        #                         Argument.E(),
        #                         Argument.link(head.pred.e),
        #                         Argument.link(dep.pred.e),
        #                     ))
        #                     self.extra_preds.append(ep)
        #
        #     elif head and head.nn:
        #         for dep in word.deps():
        #             if dep.nn:
        #                 hhead = head.head
        #                 if hhead and hhead.vb:
        #                     new_word = WordToken(word=hhead)
        #                     vb_pred = Predicate(new_word, (
        #                         Argument.E(),
        #                         Argument.link(hhead.pred.args[1]),
        #                         Argument.link(dep.pred.args[1]),
        #                         Argument.link(hhead.pred.args[3]),
        #                     ))
        #                     self.visible_preds.append(vb_pred)
        #                     if word.lemma == u"или":
        #                         ep = EPredicate("or", args=(
        #                             Argument.E(),
        #                             Argument.link(hhead.pred.e),
        #                             Argument.link(dep.pred.e),
        #                         ))
        #                         self.extra_preds.append(ep)

        # 2. if

        if word.lemma == u"если":
            if head and head.vb:
                for dep in word.deps():
                    if dep.vb and dep.pred and head.pred:
                        ep = EPredicate("imp", args=(
                            Argument.E(),
                            Argument.link(dep.pred.e),
                            Argument.link(head.pred.e),
                        ))
                        self.extra_preds.append(ep)

        # Special case: как should be handled as a pronoun
        if word.lemma == u"как" and head:
            deps = word.deps()
            if len(deps) == 1 and deps[0].pred and head.pred:
                ep = EPredicate(u"in-как", args=(
                    Argument.E(),
                    Argument.link(head.pred.e),
                    Argument.link(deps[0].pred.args[1]),
                ))
                self.extra_preds.append(ep)


        # 3. because, while, when

        # TODO(zaytsev@udc.edu): implement this

    def apply_par_rules(self, word):
        self.remove_pred(word)
        head = word.head

        # 1.

        if word.lemma == u"не":
            if head and head.pred and (head.vb or head.rb):
                ep = EPredicate("not", args=(
                    Argument.E(),
                    Argument.link(head.pred.e),
                ))
                self.extra_preds.append(ep)
            elif head and (head.nn or head.adj or head.pr):
                ep = EPredicate("not", args=(
                    Argument.E(),
                    Argument.link(head.pred.args[1]),
                ))
                self.extra_preds.append(ep)

        if word.lemma == u"нет":
            for dep in word.deps():
                if (dep.nn or dep.adj or dep.pr) and dep.pred:
                    ep1 = EPredicate("be", args=(
                        Argument.E(),
                        Argument.link(dep.pred.args[1]),
                        Argument.U(),
                    ))
                    ep2 = EPredicate("not", args=(
                        Argument.E(),
                        ep1.e,
                    ))
                    self.extra_preds.extend((ep1, ep2, ))

    def apply_in2_rules(self, word):
        if word.deprel != u"сравнит":
            return
        if not word.pred:
            return
        arg_1 = None
        for dep in word.deps():
            if dep.nn:
                arg_1 = dep
        if not arg_1:
            return
        if not word.head or not (word.head.pr or word.head.vb):
            return
        if not word.head.pred:
            return
        arg_2 = None
        if word.head.vb:
            if len(word.head.pred.args) > 1:
                target = word.head.pred.args[1].resolve_link()
                for dep in word.head.deps():
                    if dep.pred and dep.pred.args[1].resolve_link() == target:
                        arg_2 = dep
                        break
            if not arg_2:
                for p in self.initial_preds:
                    if p != word.head.pred and p.word.vb and p.word.pred.args[2].resolve_link() == \
                            word.head.pred.args[0].resolve_link():
                        target = p.args[1].resolve_link()
                        for dep in p.word.deps():
                            if dep.pred and dep.nn and dep.pred.args[1].resolve_link() == target:
                                arg_2 = dep
                                break
        elif word.head.pr:
            if word.head.head and word.head.head.nn and word.head.pred:
                arg_2 = word.head.head

        if arg_1 and arg_2:
            self.extra_preds.append(EPredicate("new_equal", args=(
                Argument.link(arg_1.pred.args[1]),
                Argument.link(arg_2.pred.args[1]),
            )))

    def add_line(self, malt_row):
        wt = WordToken(malt_row)
        self.words.append(wt)


def fol_transform(mc, text_block):
    mc.flush_arg_indexes()
    __textid, sentences = text_block
    processed = []
    for index, sent in sentences:
        for row in sent:
            mc.add_line(row)
        pred_text = mc.process(index)
        mc.flush()
        processed.append(pred_text)
    return processed


class FOLWriter(object):

    def __init__(self, ofile):
        self.ofile = ofile

    def write(self, text_block, fol_sent):
        textid, sents = text_block
        all_tokens = []
        for _, tokens in sents:
            for t in tokens:
                all_tokens.append(t[1])
        self.ofile.write(u"% ")
        self.ofile.write(u" ".join(all_tokens).encode("utf-8"))
        self.ofile.write(u"\n")
        self.ofile.write(u"id(%s).\n" % textid)
        self.ofile.write(u" & ".join(fol_sent).encode("utf-8"))
        self.ofile.write(u"\n\n")
