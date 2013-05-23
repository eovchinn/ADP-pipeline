#!/usr/bin/python
# -*- coding: utf-8 -*-

# similarity_concept.py
# calculate similarity using pure conceptnet
# support language: FA,ES,RU
#
# Author: Xing Shi
# contact: xingshi@usc.edu
# 
# see demo() for help
# outside modules should call conceptnet_similarity(word1,pos1,word2,pos2) to calculate similarity


import mydb
from collections import deque


# word -> rel+pos -> word
data = {}
loaded = False

def mysplit(str,delim=None):
    return [x for x in str.split(delim) if x ]


def loadAll(lang):
    global loaded
    if loaded == True:
        return 

    #prepare db
    CONN_STRING = "host='localhost' dbname='conceptnet' user='wiki' password='wiki'"
    con = mydb.getCon(CONN_STRING)
    table_name = 'cn_'+lang
    
    print 'load from database...'
    query = 'select * from '+table_name
    records = mydb.executeQueryResult(con,query,False)
    for r in records:

        rel = r[0]
        start = None
        end = None
        pos = ''
        ll = mysplit(r[1].decode('utf8'),'/')

        if len(ll)>=3:
            start = ll[2]
        ll = mysplit(r[2].decode('utf8'),'/')

        if len(ll)>=3:
            end = ll[2]
        if len(ll)>=4:
            pos = ll[3]
        
        rel = rel+pos

        # add start to end's neighbour
        if not end in data:
            data[end] = {}
        if not rel in data[end]:
            data[end][rel] = []
        if not start in data[end][rel]:
            data[end][rel].append(start)

        # add end to start's neighbour
        if not start in data:
            data[start] = {}
        if not rel in data[start]:
            data[start][rel] = []
        if not end in data[start][rel]:
            data[start][rel].append(end)
    print 'loading done!'
    loaded = True

def min_path_synsets(words1,words2,my_max):
    max = my_max
    
    length = -1
    seen = {}
    queue = deque(words1)
    lqueue = deque([0]*len(words1))
    temp_fathers=deque([(-1,'r') for x in words1])
    old = 0
    new = 0

    candidates = []
    fathers = []   
 
    while len(queue)!=0:

        new = lqueue[0]
        if new != old:
            #print new,len(queue)
            old = new
            
        if lqueue[0] >= max:
            break
        else:
                       
            seen[ queue[0] ] = 1
            c = queue[0]
            cl = lqueue[0]
            f = temp_fathers[0]

            queue.popleft()
            lqueue.popleft()
            temp_fathers.popleft()

            candidates.append((c,cl))
            fathers.append(f)

            if c in words2:
                length = cl
                break
                       

            neightbours = getNeighbours(c)
            for series in neightbours:
                ns = series[1]
                relation = series[0]
                for n in ns:
                    if n in seen:
                        continue
                    seen[n] = 1
                    queue.append(n)
                    lqueue.append(cl+1)
                    temp_fathers.append((len(candidates)-1,relation))
        
    # return the length and path information
    father = fathers[-1]
    path = [(candidates[-1][0],'_')]
    while father[0] != -1:
        path.append((candidates[father[0]][0],father[1]))
        father = fathers[father[0]]
    path.reverse()
        
    return (length,path)


def getNeighbours(word,pos=None):
    neighbours = []
    if word in data:
        if pos == None:
            m = {}
            for rel in data[word]:
                if not rel in m:
                    m[rel] = []
                m[rel]+=data[word][rel]
            for rel in m:
                neighbours.append( (rel,list(set(m[rel])) )  )
    return neighbours


# note: pos here is meaningfuless. We won't use any pos information
def min_path_words(word1,pos1,word2,pos2,max):
    if type(word1) == type('str'):
        word1 = word1.decode('utf8').lower()
    if type(word2) == type('str'):
        word2 = word2.decode('utf8').lower()

    r =  min_path_synsets([word1],[word2],max)
    return r


def conceptnet_similarity(word1,pos1,word2,pos2,lang):
    loadAll(lang)
    r = min_path_words(word1,pos1,word2,pos2,1000)
    if r[0] == -1:
        return None
    else:
        return 1.0/(r[0]+1)


def demo(lang):
    
    
    
    # load all data into DB
    loadAll(lang)
    
    if lang == 'ES':
        word1 = 'perr'
        pos1 = None
        word2 = 'gat'
        pos2 = None
        print min_path_words(word1,pos1,word2,pos2,10)

    if lang == 'RU':
        word1 = 'небесный'
        word2 = 'небожитель'
        print word1,word2
        print min_path_words(word1,None,word2,None,10)

    if lang == 'FA':
        word1 = 'گربه' # cat
        word2 = 'سگ' # dog
        print word1,word2
        print min_path_words(word1,None,word2,None,10)


def main():
    #from optparse import OptionParser
    from optparse import OptionParser
    usage="usage: %prog [options]"
    parser = OptionParser(usage=usage)
    parser.add_option("-l","--lang", dest='lang',help="language:EN,ES,RU,FA")
    (options,args) = parser.parse_args()
    lang = options.lang

    demo(lang)
    
    
if __name__ == '__main__':
    main()
