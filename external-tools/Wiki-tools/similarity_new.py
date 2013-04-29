from nltk.corpus import wordnet as wn

def lemmas_property(syn,func):
    lemmas = syn.lemmas
    result = []
    for l in lemmas:
        result += [ll.synset for ll in func(l)]
    return result

def getNeighbours(syn,seen):
    neightbours = []
    # verb / noun
    # hypernyms / hyponyms / derivationally related form
    if syn.pos == wn.VERB or syn.pos == wn.NOUN:
        neightbours += syn.hypernyms()
        neightbours += syn.hyponyms()
        neightbours += lemmas_property(syn,lambda l:l.derivationally_related_forms())
    # adj
    # similar to / antonyms / derivationally related form
    elif syn.pos == wn.ADJ or syn.pos == wn.ADJ_SAT:
        neightbours += syn.similar_tos()
        neightbours += lemmas_property(syn,lambda l:l.antonyms())
        neightbours += lemmas_property(syn,lambda l:l.derivationally_related_forms())
    # adv
    # antonyms / there is no derivationally related form
    elif syn.pos == wn.ADV:
        neightbours += lemmas_property(syn,lambda l:l.antonyms())
    
    
    neightbours_set = set(neightbours)
    return list(neightbours_set-seen)

def my_path_similarity(word1,pos1,word2,pos2):
    l = min_path_word(word1,pos1,word2,pos2)
    if l == -1:
        syn1 = wn.synsets(word1,pos1)[0]
        syn2 = wn.synsets(word2,pos2)[0]
        l = syn1.path_similarity(syn2)
        if l == None:
            return None
        else:
            return l
    if l == None:
        return None
    else:
        return 1.0/(l+1)

def min_path_word(word1,pos1,word2,pos2):
    max = 8
    syns1 = wn.synsets(word1,pos1)
    syns2 = set(wn.synsets(word2,pos2))
    if syns1==[] or syns2 == []:
        return None
    if set(syns1) & syns2:
        return 0
    length = 0
    seen = set()
    queue = []
    lqueue = []
    queue += syns1
    lqueue += [0 for x in xrange(len(queue))]
    old = 0
    new = 0
    while len(queue)!=0:
        #print lqueue[0]
        new = lqueue[0]
        if new != old:
            #print new
            old = new
            
        if lqueue[0] >= max:
            return -1
        if queue[0] in syns2 :
            length = lqueue[0]
            break
        else:
            seen.add(queue[0])
            c = queue[0]
            cl = lqueue[0]
            del queue[0]
            del lqueue[0]
            neightbours = getNeighbours(c,seen)
            for n in neightbours:
                queue.append(n)
                lqueue.append(cl+1)

    return length

def min_path(syn1,syn2):
    if syn1 == syn2:
        return 0
    length = 0
    seen = set()
    queue = []
    lqueue = []
    queue.append(syn1)
    lqueue.append(0)
    while len(queue)!=0:
        print lqueue[0]
        if queue[0] == syn2:
            length = lqueue[0]
            break
        else:
            seen.add(queue[0])
            c = queue[0]
            cl = lqueue[0]
            del queue[0]
            del lqueue[0]
            neightbours = getNeighbours(c,seen)
            for n in neightbours:
                queue.append(n)
                lqueue.append(cl+1)

    return length

if __name__ == '__main__':
    water = wn.synsets('water','n')[0]
    liquid = wn.synsets('liquid','n')[0]
    l = min_path(water,liquid)
    print l
