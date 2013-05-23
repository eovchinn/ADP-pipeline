#!/usr/bin/python
# -*- coding: utf-8 -*-

# similarity_translation.py
# similarity measurement tool using conceptnet translation and similarity_new.py
# support language: FA,RU,ES
#
# Author: Xing Shi
# contact: xingshi@usc.edu
# 
# see demo() for help
# outside modules should call translation_similarity(word1,pos1,word2,pos2) to calculate similarity


import mydb
import similarity_wordnet as sa


#lang_word -> en_word
data = {}
loaded = False


def mysplit(str,delim=None):
    return [x for x in str.split(delim) if x ]


def loadAll(lang):
    global loaded
    if loaded:
        return
    CONN_STRING = "host='localhost' dbname='conceptnet' user='wiki' password='wiki'"
    con = mydb.getCon(CONN_STRING)
    table_name = 'translation_'+lang
    print table_name
    print 'loading translation from db...'
    sa.loadAll()
    query = 'select * from '+table_name
    records = mydb.executeQueryResult(con,query,False)
    for r in records:
        ll = mysplit(r[1].decode('utf8'),'/')
        word = ll[-1]
        ll = mysplit(r[2].decode('utf8'),'/')
        if len(ll)<3:
            continue
        en_word = ll[2]
        
        if not word in data:
            data[word] = en_word
    print 'loading done!'
    loaded = True

def min_path_words(word1,pos1,word2,pos2,max):
    if type(word1) == type('str'):
        word1 = word1.decode('utf8').lower()
    if type(word2) == type('str'):
        word2 = word2.decode('utf8').lower()
    print word1,word2
    if not (word1 in data and word2 in data):
        return None
    en_word1 = data[word1]
    en_word2 = data[word2]
    print en_word1,en_word2
    return sa.min_path_words(en_word1,pos1,en_word2,pos2,max)


def translation_similarity(word1,pos1,word2,pos2,lang):
    loadAll(lang)
    r = min_path_words(word1,pos1,word2,pos2,1000)
    if r == None or r[0] == -1:
        return None
    else:
        return 1.0/(r[0]+1)


def demo(lang):
    
    loadAll(lang)
    
    if lang == 'ES':
        word1 = 'perr'
        pos1 = 'n'
        word2 = 'gat'
        pos2 = 'n'
        print min_path_words(word1,pos1,word2,pos2,10)

    if lang == 'RU':
        word1 = 'собака' # dog
        word2 = 'кошка' # cat
        pos1 = 'n'
        pos2 = 'n'
        print min_path_words(word1,pos1,word2,pos2,1000)


    if lang == 'FA':
        word1 = 'ساعت' # hour
        word2 = 'دقیقه' # minute
        pos1 = 'n'
        pos2 = 'n'
        print min_path_words(word1,pos1,word2,pos2,1000)



def main():
    from optparse import OptionParser
    usage="usage: %prog [options]"
    parser = OptionParser(usage=usage)
    parser.add_option("-l","--lang", dest='lang',help="language:EN,ES,RU,FA")
    (options,args) = parser.parse_args()
    lang = options.lang

    demo(lang)


if __name__ == '__main__':
    main()
