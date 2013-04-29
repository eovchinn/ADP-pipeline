#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import re
from nltk.corpus import wordnet as wn
import similarity_new as sn 

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
            results.append((word, POSMAP[pos], synsets[0]))
    return results

def similarity(results, tword,tpos ,method,output):
    tsynset = wn.synsets(tword,POSMAP[tpos])[0]
    
    for i in xrange(len(results)):
        similarity = 0.0
        if method == 'path_similarity':
            similarity = tsynset.path_similarity(results[i][2])
        elif method == 'lch_similarity':
            if (not tpos in POSMAP) or POSMAP[tpos] != results[i][1]:
                similarity = 0.0
            else:
                similarity = tsynset.lch_similarity(results[i][2])
        elif method == 'wup_similarity':
            similarity = tsynset.wup_similarity(results[i][2])
        elif method == 'my_path':
            similarity = sn.my_path_similarity(tword,tpos,results[i][0],results[i][1])
        if not similarity:
            similarity = 0.0
        results[i] = results[i][0:3] + (similarity,)
    rset = {x for x in results}
    results = [x for x in rset]
    results = reversed( sorted(results, key = lambda result: result[3]))

    output.write(method+':\n')
    for r in results:
        output.write(repr(r)+'\n')
    output.write('\n')




def main(tword,tpos,inputFile,output):
    input = open(inputFile,'r')
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
    outputFile = open(output,'w')
    similarity(results,tword,tpos,'path_similarity',outputFile)
    similarity(results,tword,tpos,'lch_similarity',outputFile)
    similarity(results,tword,tpos,'wup_similarity',outputFile)
    similarity(results,tword,tpos,'my_path',outputFile)

    outputFile.flush()
    outputFile.close()
    

if __name__ == '__main__':
    from optparse import OptionParser
    #options
    usage = 'usage : %prog [options]'
    parser = OptionParser(usage = usage)
    parser.add_option('-w',dest = 'word')
    parser.add_option('-p',dest = 'pos')
    parser.add_option('-i',dest = 'input')
    parser.add_option('-o',dest = 'output')
    (options,args) = parser.parse_args()
    tword = options.word
    tpos = options.pos
    output = options.output
    input = options.input
    
    main(tword,tpos,input,output)

