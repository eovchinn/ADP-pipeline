#! /usr/bin/python
# -*- coding: utf-8 -*-
import re,sys,optparse

##################### I/O ##################################
usage = "usage: %prog [options] <input_file>"
parser = optparse.OptionParser(usage=usage)
parser.add_option("-i", "--inFile", dest="input",
                  action="store", help="read from FILE", metavar="FILE")
parser.add_option("-t","--tagset",action="store",
                  help="tagset in input file",default="ancora")
(options, args) = parser.parse_args()

def to_sents(infile):
    words = []
    sentence = []
    full_sents = []
    all_words = []
    sent_count = 1
    eCount = 1
    xCount = 1
    uCount = 1    
    for line in infile:
        line = line.strip().split("\t")
        if len(line) > 1:
            wordID = int(line[0])
            wordText = line[1]
            wordLemma = line[2]
            wordPOS = line[3]
            wordHead = int(line[6])
            wordRel = line[7]
            #wordTPOS = line[10]
            longID = '%0*d' % (3, wordID)
            if date.match(wordLemma):
                wordLemma = wordText
            elif wordLemma == "<unknown>":
                wordLemma = wordText
            info = [longID,wordText,wordLemma,wordPOS,wordHead,wordRel,wordID,sent_count]#,wordTPOS]
            sentence.append(wordText)
            words.append(info)
        else:
            full_sents.append(sentence)
            all_words.append(words)
            sentence = []
            new_prop_sent = []
            words = []
            eCount = 1
            xCount = 1
            uCount = 1
            sent_count += 1
    infile.close()
    return full_sents,all_words
        
def prop_to_dict(props):
    sent_dict = {}    
    new_prop_sent = []
    eCount = 1
    xCount = 1
    uCount = 1
    #loop over stored list of words and save initial props
    for prop in props:
        new_prop = []
        ID = prop[0]
        token = prop[1]
        lemma = prop[2]
        pos = prop[3]
        head = prop[4]
        rel = prop[5]
        shortID = prop[6]
        sent_count = prop[7]
        #finePOS = prop[8]
        propID = "["+str(sent_count)+str(ID)+"]"
        if not propTags.match(pos) and not puncts.match(lemma):            
            args = []
            tag = ""
            new_prop.extend([token,lemma,pos,head,rel,shortID,args,tag,propID])
            sent_dict[shortID]=[token,lemma,pos,head,rel,shortID,args,tag,propID]
            new_prop_sent.append(new_prop)
        elif propTags.match(pos):
            args,tag,eCount,xCount,uCount = build_predicate(pos,eCount,xCount,uCount)
            new_prop.extend([token,lemma,pos,head,rel,shortID,args,tag,propID])
            sent_dict[shortID]=[token,lemma,pos,head,rel,shortID,args,tag,propID]
            new_prop_sent.append(new_prop)
    return new_prop_sent,sent_dict

def replace_args(prop_sent,sent_dict):
    #loop over propositions, fill in variables, and print
    position = 0
    for prop in prop_sent:
        token = prop[0]
        lemma = prop[1]
        pos = prop[2]
        head = prop[3]
        rel = prop[4]
        wordID = prop[5]
        predicate = prop[6]
        tag = prop[7]
        propID = prop[8]
        if rel == "suj":
            sent_dict = insert_suj(head,wordID,sent_dict)
        if tag == "vb" and head != 0:
            sent_dict = inherit_suj(head,wordID,sent_dict)
        if rel == "sp" and pos == "s":
            sent_dict = insert_sp(head,wordID,sent_dict)
        if rel == "sn" and pos == "n":
            sent_dict = insert_sn(head,wordID,sent_dict)
        if rel == "s.a" and pos == "a":
            sent_dict = insert_s_a(head,wordID,sent_dict)
        if rel == "cc" and pos == "r":
            sent_dict = insert_cc(head,wordID,sent_dict)
        if rel == "cd":
            sent_dict = insert_cd(head,wordID,sent_dict)
        if rel == "atr":
            sent_dict = inherit_suj(head,wordID,sent_dict)
        # if rel == "cag" and pos == "s":
        #     sent_dict = insert_cag(head,wordID,sent_dict)
        if rel == "morfema.pronominal" and pos == "p":
            sent_dict = insert_m_p(head,wordID,sent_dict)
        if tag == "in":
            sent_dict = insert_prep_head(head,wordID,sent_dict)
        # if rel == "atr" and pos == "a":
        #     sent_dict = insert_atr(head,wordID,sent_dict)  
            
    for prop in prop_sent:
        position +=1
        token = prop[0]
        lemma = prop[1]
        pos = prop[2]
        head = prop[3]
        rel = prop[4]
        wordID = prop[5]
        predicate = prop[6]
        tag = prop[7]
        propID = prop[8]
        if lemma == "ser":
            predicate = []
        #print propID,lemma,tag,predicate,"-",wordID,head,rel
        if len(predicate) > 0:
            sys.stdout.write(propID+":"+lemma+"-"+tag+"("+",".join(predicate)+")")
        else:
            sys.stdout.write(propID+":"+lemma)
        if position < len(prop_sent):
             sys.stdout.write(" & ")
    print ""

    
def insert_suj(head,wordID,sent_dict):
    if sent_dict[head][7] == "vb":
        sent_dict[head][6][1] = sent_dict[wordID][6][1]
    # else:
    #     print "not a verb"
    #     exit()
    return sent_dict

nounArg = re.compile("x\d")

def inherit_suj(head,wordID,sent_dict):
    if sent_dict[head][7] == "vb" and not nounArg.search(sent_dict[wordID][6][1]):
        sent_dict[wordID][6][1] = sent_dict[head][6][1]
    # else:
    #     print "not a verb"
    #     exit()
    return sent_dict

def insert_prep_head(head,wordID,sent_dict):
    if sent_dict[head][7] == "vb":
        sent_dict[wordID][6][1] = sent_dict[head][6][0]
    # else:
    #     print "not a verb"
    #     exit()
    return sent_dict

def insert_cd(head,wordID,sent_dict):
    if sent_dict[wordID][2] == "n" and sent_dict[head][7] == "vb":
        sent_dict[head][6][2] = sent_dict[wordID][6][1]
    if sent_dict[wordID][2] == "v" and sent_dict[head][7] == "vb":
        sent_dict[head][6][2] = sent_dict[wordID][6][0]        
    # else:
    #     print "not a verb"
    #     exit()
    return sent_dict

def insert_sp(head,wordID,sent_dict):
    if sent_dict[head][7] == "nn":
        sent_dict[wordID][6][1] = sent_dict[head][6][1]
    # else:
    #     print "not a noun"
    #     exit()
    return sent_dict

def insert_sn(head,wordID,sent_dict):
    if sent_dict[head][7] == "in":
        sent_dict[head][6][2] = sent_dict[wordID][6][1]
    elif sent_dict[head][7] == "nn":
        sent_dict[wordID][6][1] = sent_dict[head][6][1]
    # else:
    #     print "not a prep"
    #     exit()
    return sent_dict

def insert_cag(head,wordID,sent_dict):
    if sent_dict[head][7] == "vb":
        sent_dict[wordID][6][1] = sent_dict[head][6][0]
    # else:
    #     print "not a prep"
    #     exit()
    return sent_dict

def insert_cpred(head,wordID,sent_dict):
    if sent_dict[head][7] == "vb":
        sent_dict[wordID][6][1] = sent_dict[head][6][0]
    # else:
    #     print "not a prep"
    #     exit()
    return sent_dict

def insert_s_a(head,wordID,sent_dict):
    if sent_dict[head][7] == "nn":
        sent_dict[wordID][6][1] = sent_dict[head][6][1]
    # else:
    #     print "not a noun"
    #     exit()
    return sent_dict

def insert_atr(head,wordID,sent_dict):
    if sent_dict[head][7] == "vb":
        #sent_dict[wordID][6][1] = sent_dict[head][6][0]
        sent_dict[head][6][2] = sent_dict[wordID][6][0]
    return sent_dict

def insert_cc(head,wordID,sent_dict):
    if sent_dict[head][7] == "vb":
        sent_dict[wordID][6][1] = sent_dict[head][6][0]
    return sent_dict

def insert_m_p(head,wordID,sent_dict):
    if sent_dict[head][7] == "vb":
        sent_dict[head][6][2] = sent_dict[wordID][6][1]
    return sent_dict

def build_predicate(pos,eCount,xCount,uCount):
    pred = []
    tag = ""
    if verbTag.match(pos):
        tag = "vb"
        pred.append("e"+str(eCount))
        eCount+=1
        pred.append("u"+str(uCount))
        uCount+=1
        pred.append("u"+str(uCount))
        uCount+=1
        pred.append("u"+str(uCount))
        uCount+=1
        return pred,tag,eCount,xCount,uCount
    if nounTag.match(pos): 
        tag="nn"
        pred.append("e"+str(eCount))
        eCount+=1
        pred.append("x"+str(xCount))
        xCount+=1
        return pred,tag,eCount,xCount,uCount
    if pronounTag.match(pos):
        tag="pro"
        pred.append("e"+str(eCount))
        eCount+=1
        pred.append("x"+str(xCount))
        xCount+=1
        return pred,tag,eCount,xCount,uCount 
    if adjectiveTag.match(pos):
        tag="adj"
        pred.append("e"+str(eCount))
        eCount+=1
        pred.append("u"+str(uCount))
        uCount+=1        
        return pred,tag,eCount,xCount,uCount
    if adverbTag.match(pos):
        tag="rb"
        pred.append("e"+str(eCount))
        eCount+=1
        pred.append("u"+str(uCount))
        uCount+=1        
        return pred,tag,eCount,xCount,uCount
    if prepositionTag.match(pos):
        tag="in"
        pred.append("e"+str(eCount))
        eCount+=1
        pred.append("u"+str(uCount))
        uCount+=1
        pred.append("u"+str(uCount))
        uCount+=1        
        return pred,tag,eCount,xCount,uCount

def add_args(args,arg,count):
    args.append

if options.tagset == "ancora":
    nounTag = re.compile("^n$")
    verbTag = re.compile("^v$")
    adjectiveTag = re.compile("^a$")
    adverbTag = re.compile("^r$")
    prepositionTag = re.compile("^s$")
    propTags = re.compile("^(n|v|a|r|s|p)$")
    pronounTag = re.compile("^p$")

nounPred = re.compile("nn\(e\d*,[ux]\d*\)")
pronounPred = re.compile("p\(e\d*,[ux]\d*\)")
date = re.compile("\[\?\?\:\?\?\/\?\?\/\d\d\d\d\:\?\?\.\?\?\]")
puncts = re.compile("[\.,\?\!{}()\[\]:;¿¡\"]")

def main():
    lines = open(options.input, "r") if options.input else sys.stdin
    full_sents,all_words = to_sents(lines)
    sent_count = 0
    for sent,word in zip(full_sents,all_words):
        sent_count += 1
        print "% "+" ".join(sent)
        print "id("+str(sent_count)+")."
        prop_sent,prop_dict = prop_to_dict(word)
        replace_args(prop_sent,prop_dict)

if __name__ == "__main__":
    main()
