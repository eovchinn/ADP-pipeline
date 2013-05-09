#!/usr/bin/python
# -*- coding: utf-8 -*-

# Contributors:
#   * Vladimir Zaytsev <vzaytsev@isi.edu> (2013)

import re


class POSHelper(object):

    def __init__(self, word):
        self.word = word

    def __nonzero__(self):
        return True


class VBHelper(POSHelper):

    @property
    def subj(self):
        return self.word.pred.args[1]

    @subj.setter
    def subj(self, value):
        self.word.pred.args[1] = value

    @property
    def d_obj(self):
        return self.word.pred.args[2]

    @d_obj.setter
    def d_obj(self, value):
        self.word.pred.args[2] = value

    @property
    def i_obj(self):
        return self.word.pred.args[3]

    @d_obj.setter
    def iobj(self, value):
        self.word.pred.args[3] = value


class ADJHelper(POSHelper):
    pass


class NNHelper(POSHelper):
    pass


class RBHelper(POSHelper):
    pass


class INHelper(POSHelper):
    pass


class PRHelper(POSHelper):
    pass


class NUMHelper(POSHelper):
    pass


class CNJHelper(POSHelper):
    pass


class PARHelper(POSHelper):
    pass

class WordToken(object):
    postag_map = dict(V=("vb", 4, VBHelper), A=("adj", 2, ADJHelper),
                      N=("nn", 2, NNHelper), R=("rb", 2, RBHelper),
                      S=("in", 3, INHelper), P=("pr", 2, PRHelper),
                      M=("num", -1, NUMHelper), C=("cnj", 2, CNJHelper),
                      Q=("par", 2, PARHelper))

    def __init__(self, line=None, word=None):

        self.vb = False
        self.adj = False
        self.nn = False
        self.rb = False
        self.prep = False
        self.pr = False
        self.num = False
        self.cnj = False
        self.par = False

        self.pred = None
        self.important = True
        self.confirm_remove = False
        self.__deps = None
        self.__head = None

        if not line and word:
            self.id = word.id
            self.form = word.form
            self.lemma = word.lemma
            self.cpostag = word.cpostag
            self.feats = word.feats
            self.head_id = word.head
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
        self.head_id = int(line[6]) # HEAD. language HEAD. Head of the current
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
            self.cpostag, self.args, helper_cls = self.postag_map.get(cpostag)
            if self.cpostag != "in":
                setattr(self, self.cpostag, helper_cls(self))
            else:
                setattr(self, "prep", helper_cls(self))
        else:
            self.cpostag, self.args = None, -1

        if self.lemma == "<unknown>":
            self.lemma = self.form

    @property
    def head(self):
        return self.__head

    def set_head(self, new_head):
        self.__head = new_head

    def deps(self, filtr=None):
        """
        Return deps. <filtr> could be a list of allowed cpostags: ["nn", "vb"]
        """
        if not filtr:
            return self.__deps[:]
        return filter(lambda d: d.cpostag in filtr, self.__deps)

    def set_deps(self, new_deps):
        self.__deps = new_deps

    def contains(self, lemma):
        """
        Do DFS to check if deps contains a given lemma.
        """
        deps = self.__deps[:]
        while deps:
            new_deps = []
            for d in deps:
                if d.lemma == lemma:
                    return True
                else:
                    new_deps.extend(d.deps())
            deps = new_deps
        return False

    def unfold_dep(self, until_tag="nn"):
        if len(self.__deps) != 1:
            return None
        if self.__deps[0].cpostag == until_tag:
            return self.__deps[0]
        return self.__deps[0].unfold_dep(until_tag)

    def __repr__(self):
        return u"<WordToken(%s)>" \
            % (self.id, )


class ConLLTab(object):

    def __init__(self, ifile):
        self.ifile = ifile
        self.last_id = None
        self.row_splitter = re.compile("\s+")

    def find_textid(self, row):
        wt = WordToken(row)
        if wt.form[0:3] == "{{{" and \
           wt.form[len(wt.form) - 6:len(wt.form)] == "}}}!!!":
            return wt.form[3:len(wt.form) - 6]
        else:
            return None

    def __iter__(self):
        for line in self.ifile:
            line = line.decode("utf-8")
            row = self.row_splitter.split(line)
            if len(row) > 2:
                textid = self.find_textid(row)
                if textid is None:
                    self.last_id = None
                    yield row
                else:
                    self.last_id = textid
                    yield None
            else:
                yield None


class CoNLLReader(object):

    def __init__(self, ifile):
        self.conll_tab = ConLLTab(ifile)
        self.textid_found = False
        self.last_textid = None
        self.sent_count = 1
        self.last_sent = None
        self.__init_sents__()

    def __init_sents__(self):
        self.last_sent = []
        self.sentences = [self.last_sent]

    def __add_empty_sent__(self):
        self.sentences.append([])
        self.last_sent = self.sentences[-1]

    def __add_row__(self, row):
        self.last_sent.append(row)

    def flush_sents(self):
        sents = []
        textid = self.last_textid if self.last_textid else str(self.sent_count)
        for sent in self.sentences:
            if len(sent) > 0:
                sents.append((self.sent_count, sent))
                self.sent_count += 1
        self.__init_sents__()
        return textid, sents

    def filter_empties(self, snts):
        textid = snts[0]
        snts = snts[1]
        return textid, filter(lambda s: len(s[1]) > 1, snts)

    def __iter__(self):
        for row in self.conll_tab:
            if row:
                self.__add_row__(row)
            else:
                if self.conll_tab.last_id:
                    if self.textid_found:
                        snts = self.flush_sents()
                        self.last_textid = self.conll_tab.last_id
                        snts = self.filter_empties(snts)
                        if len(snts[1]) > 0:
                            yield snts
                    else:
                        self.textid_found = True
                        self.last_textid = self.conll_tab.last_id
                else:
                    if self.textid_found:
                        self.__add_empty_sent__()
                    else:
                        snts = self.filter_empties(self.flush_sents())
                        if len(snts[1]) > 0:
                            yield snts
        snts = self.filter_empties(self.flush_sents())
        if len(snts[1]) > 0:
            yield snts
