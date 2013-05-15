#!/usr/bin/python
# -*- coding: utf-8 -*-

# similarity_wordnet.py
# similarity measurement tool using wordnet incorporated with Derivationally-Related-Form (DRF)
# support language: EN,FA,ES,RU
#
# Author: Xing Shi
# contact: xingshi@usc.edu
# 
# see demo() for help
# outside modules should call path_similarity(word1,pos1,word2,pos2) to calculate similarity


from nltk.corpus import wordnet as wn
from collections import deque
import pickle


loaded = False


def extract_pos_offset(fileName):
    f = open(fileName,'w')
    items = wn._lemma_pos_offset_map.items()
    pos_offset_map = set()
    for item in items:
        lemma = item[0]
        for pos in item[1]:
            offsets = item[1][pos]
            for offset in offsets:
                pos_offset_map.add( (pos,offset) )
    for pair in pos_offset_map:
        f.write(pair[0]+' '+str(pair[1])+'\n')
    f.close()
    print len(pos_offset_map)


def loadAll():
    global loaded
    if loaded:
        return
    index = wn._lemma_pos_offset_map
    print 'loading wordnet into cache... '
    cache = wn._synset_offset_cache
    f = open('pos_offset.txt','r')
    for line in f:
        ll = line.split()
        pos = ll[0]
        offset = int(ll[1])
        wn._synset_from_pos_and_offset(pos,offset)
    print 'Done: '+str(sum([len(cache[x]) for x in cache]))+'/'+str(len(index))
    loaded = True


def print2file(synset,array,fathers,fileName):
    file = open(fileName,'w')
    for i in xrange(len(array)):
        s = array[i]
        file.write(str(synset.offset)+'\t'+str(s[0].offset)+'\t'+str(s[1])+'\t')
        # get father chain
        father = fathers[i]
        while father[0] != -1:
            file.write( str( array[father[0]][0].offset )+'-'+father[1]+' ')
            father = fathers[father[0]]
        file.write('\n')
    file.close()


def pickleResult(synsets,fathers):
    offsets = [(s[0].offset,s[1]) for s in synsets]
    pickle.dump((offsets,fathers),'list.pickle')


def lemmas_property(syn,func):
    lemmas = syn.lemmas
    result = []
    for l in lemmas:
        result += [ll.synset for ll in func(l)]
    return result


def getNeighboursL(syn):
    neightbours = []
    # hyper:e / hypon:o / drf:d / similar to:s / antonym: a
    # verb / noun
    # hypernyms / hyponyms / derivationally related form
    if syn.pos == wn.VERB or syn.pos == wn.NOUN:
        neightbours += [(syn.hypernyms(),'e')]
        neightbours += [(syn.hyponyms(),'o')]
        neightbours += [(lemmas_property(syn,lambda l:l.derivationally_related_forms()),'d')]
    # adj
    # similar to / antonyms / derivationally related form
    elif syn.pos == wn.ADJ or syn.pos == wn.ADJ_SAT:
        neightbours += [(syn.similar_tos(),'s')]
        neightbours += [(lemmas_property(syn,lambda l:l.antonyms()),'a')]
        neightbours += [(lemmas_property(syn,lambda l:l.derivationally_related_forms()),'d')]
    # adv
    # antonyms / there is no derivationally related form
    elif syn.pos == wn.ADV:
        neightbours += [(lemmas_property(syn,lambda l:l.antonyms()),'a')]
    
    return neightbours


# provide all the neighbours around a certain synset
#
# Input:
#   synset : the root synset
#   my_max : the limitation of deepth
# Output:
#   candidates: the neighbours
#   fathers: a array to record the path from synset to the neighbour.
# should call print2file(synset,candidates,fathers,'file.txt') to get the formated output to file.txt
def min_path_range(synset,my_max):
    max = my_max
    
    seen = {}
    queue = deque([synset])
    lqueue = deque([0])
    temp_fathers=deque([(-1,'r')])

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
            return (candidates,fathers)

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

            neightbours = getNeighboursL(c)
            for series in neightbours:
                ns = series[0]
                relation = series[1]
                for n in ns:
                    if n in seen:
                        continue
                    seen[n] = 1
                    queue.append(n)
                    lqueue.append(cl+1)
                    temp_fathers.append((len(candidates)-1,relation))
            
    return (candidates,fathers)


def min_path_synsets(synsets1,synsets2,my_max):
    max = my_max
    
    length = -1
    seen = {}
    queue = deque(synsets1)
    lqueue = deque([0]*len(synsets1))
    temp_fathers=deque([(-1,'r') for x in synsets1])
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

            if c in synsets2:
                length = cl
                break
                       

            neightbours = getNeighboursL(c)
            for series in neightbours:
                ns = series[0]
                relation = series[1]
                for n in ns:
                    if n in seen:
                        continue
                    seen[n] = 1
                    queue.append(n)
                    lqueue.append(cl+1)
                    temp_fathers.append((len(candidates)-1,relation))
        
    # return the length and path information
    father = fathers[-1]
    path = [(candidates[-1][0].name,'_')]
    while father[0] != -1:
        path.append((candidates[father[0]][0].name,father[1]))
        father = fathers[father[0]]
    path.reverse()
        
    return (length,path)

    
def min_path_words(word1,pos1,word2,pos2,max):
    synsets1 = wn.synsets(word1,pos1)
    synsets2 = wn.synsets(word2,pos2)
    if len(synsets1)== 0 or len(synsets2) == 0:
        return None
    else:
        return min_path_synsets(synsets1,synsets2,max)


#outside module should call this function
def path_similarity(word1,pos1,word2,pos2):
    if loaded == False:
        loadAll()
        loaded = True

    r = min_path_words(word1,pos1,word2,pos2,1000)
    if r==None or r[0]==-1:
        return None
    else:
        return 1.0/(r[0]+1)


def demo():
    # load all synsets into RAM
    loadAll()

    # similarity between two words:
    a = min_path_words('water','n','liquid','a',1000)
    
    # similarity between two synset:
    water = wn.synsets('water','n')[0]
    liquid = wn.synsets('liquid','n')[0]
    a = min_path_synsets(water,liquid,1000)

    # similarity between one synset and the rest synsets
    a = min_path_range(water,1000)


if __name__ == '__main__':
    demo()
