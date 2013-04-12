#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import re
from nltk.corpus import wordnet as wn

POSMAP = {'vb': wn.VERB, 'nn': wn.NOUN, 'rb': wn.ADV,  'adj': wn.ADJ}


def process_obs(obs,prog):
    results=[]
    list = re.findall(prog,obs)
    ll=[]
    for l in list:
        l = l[1:-1].split()[0]
        if '-' in l:
            ll.append(l)
    for l in ll:
        lll = l.split('-')
        word = lll[0]
        pos = lll[1]
        if not pos in POSMAP:
            continue
        synsets = wn.synsets(word,POSMAP[pos])
        if synsets:
            results.append((word, pos, synsets[0]))
    return results

def similarity(results, tword,tpos ,method):
    tsynset = wn.synsets(tword,POSMAP[tpos])[0]
    print method,':'
    for i in xrange(len(results)):
        similarity = 0.0
        if method == 'path_similarity':
            similarity = tsynset.path_similarity(results[i][2])
        elif method == 'lch_similarity':
            if tpos != results[i][1]:
                similarity = 0.0
            else:
                similarity = tsynset.lch_similarity(results[i][2])
        elif method == 'wup_similarity':
            similarity = tsynset.wup_similarity(results[i][2])
        if not similarity:
            similarity = 0.0
        results[i] = results[i][0:3] + (similarity,)
    rset = {x for x in results}
    results = [x for x in rset]
    results = reversed( sorted(results, key = lambda result: result[3]))
    for r in results:
        print r
    print



def main(tword,tpos):
    input = sys.stdin
    obssB = False
    obss = []
    for line in input:
        if not line:
            break
        if line == '<obss>\n':
            obssB = True
            continue
        if obssB:
            obs = line.strip()
            obss.append(obs)
    results = []
    prog = re.compile(r'\([^\(\)\[\]]+\[[0-9a-zA-Z]+\]\)')
    for obs in obss:
        results += process_obs(obs,prog)
    
    # similarity
   
    similarity(results,tword,tpos,'path_similarity')
    similarity(results,tword,tpos,'lch_similarity')
    similarity(results,tword,tpos,'wup_similarity')
    

if __name__ == '__main__':
    from optparse import OptionParser
    #options
    usage = 'usage : %prog [options]'
    parser = OptionParser(usage = usage)
    parser.add_option('-w',dest = 'word')
    parser.add_option('-p',dest = 'pos')
    (options,args) = parser.parse_args()
    tword = options.word
    tpos = options.pos
    
    main(tword,tpos)

