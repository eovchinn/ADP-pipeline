#! /bin/bash/python
# -*- coding: utf-8 -*-
import re,sys,optparse

##################### I/O ##################################
usage = "usage: %prog [options] <input_file>"
parser = optparse.OptionParser(usage=usage)
parser.add_option("-i", "--inFile", dest="input_FileName",
                  action="store", help="read from FILE", metavar="FILE")
parser.add_option("-t","--tagset",action="store",
                  help="tagset in input file",default="ancora")
(options, args) = parser.parse_args()

def to_prop(infile):
    sent_count = 1
    props = []
    sentence = []
    full_sents = []
    sent_IDs = []
    all_dicts = []
    all_props = []
    for line in infile:
        line = line.strip().split("\t")
        if len(line) > 1:
            wordID = int(line[0])
            wordText = line[1]
            wordLemma = line[2]
            wordPOS = line[3]
            wordHead = int(line[6])
            wordRel = line[7]
            longID = '%0*d' % (3, wordID)
            prop = [longID,wordText,wordLemma,wordPOS,wordHead,wordRel,wordID,sent_count]
            sentence.append(wordText)
            props.append(prop)
        else:
            #print sentence
            #print "% "+" ".join(sentence)
            full_sents.append(sentence)
            #print ID(sentence number)
            #print "id("+str(sent_count)+")."
            sent_IDs.append("id("+str(sent_count)+").")
            all_props.append(props)
            sent_count += 1
            sentence = []
            new_prop_sent = []
            sent_dict = {}
            props = []
            eCount = 1
            xCount = 1
            uCount = 1
            #print sent_count
    infile.close()
    return full_sents,sent_IDs,all_props

def use_props(all_props):
    for prop in all_props:
        prop_sent,prop_dict = prop_to_dict(prop)
        replace_args(prop_sent,prop_dict)
        
def prop_to_dict(props):
    sent_dict = {}    
    new_prop_sent = []
    eCount = 1
    xCount = 1
    uCount = 1
    #loop over stored list of words and save initial props
    for i in range(len(props)):
        new_prop = []
        ID = props[0][0]
        token = props[0][1]
        lemma = props[0][2]
        pos = props[0][3]
        head = props[0][4]
        rel = props[0][5]
        shortID = props[0][6]
        sent_count = props[0][7]        
        if date.match(lemma):
            lemma = token
        if puncts.match(lemma):
            props.pop(0)
        elif not propTags.match(pos):
            propID = "["+str(sent_count)+str(ID)+"]"
            args = []
            tag = ""
            new_prop.extend([token,lemma,pos,head,rel,shortID,args,tag,propID])
            sent_dict[shortID]=[token,lemma,pos,head,rel,shortID,args,tag,propID]
            new_prop_sent.append(new_prop)
            props.pop(0)
        elif propTags.match(pos):
            args,tag,eCount,xCount,uCount = build_predicate(pos,eCount,xCount,uCount)
            propID = "["+str(sent_count)+str(ID)+"]"
            new_prop.extend([token,lemma,pos,head,rel,shortID,args,tag,propID])
            sent_dict[shortID]=[token,lemma,pos,head,rel,shortID,args,tag,propID]
            new_prop_sent.append(new_prop)
            props.pop(0)
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
        #print propID,lemma,tag,predicate,"-",wordID,head,rel
        if rel == "suj" and pos == "n":
            sent_dict = insert_suj(head,predicate,wordID,sent_dict)
        if rel == "sp" and pos == "s":
            sent_dict = insert_sp(head,predicate,wordID,sent_dict)
        if rel == "sn" and pos == "n":
            sent_dict = insert_sn(head,predicate,wordID,sent_dict)
        if rel == "s.a" and pos == "a":
            sent_dict = insert_s_a(head,predicate,wordID,sent_dict)              
        # if position < len(prop_sent):
        #     sys.stdout.write(" & ")
        #print ""
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
        #print propID,lemma,tag,predicate,"-",wordID,head,rel
        if len(predicate) > 0:
            sys.stdout.write(propID+":"+lemma+"-"+tag+"("+",".join(predicate)+")")
        else:
            sys.stdout.write(propID+":"+lemma)
        if position < len(prop_sent):
             sys.stdout.write(" & ")
    print ""

    
def insert_suj(head,predicate,wordID,sent_dict):
    if sent_dict[head][7] == "vb":
        sent_dict[head][6][1] = predicate[1]
    # else:
    #     print "not a verb"
    #     exit()
    return sent_dict

def insert_sp(head,predicate,wordID,sent_dict):
    if sent_dict[head][7] == "nn":
        sent_dict[wordID][6][1] = sent_dict[head][6][1]
    # else:
    #     print "not a noun"
    #     exit()
    return sent_dict

def insert_sn(head,predicate,wordID,sent_dict):
    if sent_dict[head][7] == "in":
        sent_dict[head][6][2] = predicate[1]
    elif sent_dict[head][7] == "nn":
        sent_dict[wordID][6][1] = sent_dict[head][6][1]
    # else:
    #     print "not a prep"
    #     exit()
    return sent_dict

def insert_s_a(head,predicate,wordID,sent_dict):
    if sent_dict[head][7] == "nn":
        sent_dict[wordID][6][1] = sent_dict[head][6][1]
    # else:
    #     print "not a noun"
    #     exit()
    return sent_dict

def build_predicate(pos,eCount,xCount,uCount):
    pred = []
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
        tag="p"
        pred.append("e"+str(eCount))
        eCount+=1
        pred.append("u"+str(uCount))
        uCount+=1
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
    if options.input_FileName:
        input_file = options.input_FileName
    else:
        input_file = args[0]
    infile = open(input_file,"r")
    full_sents,sentIDs,all_props = to_prop(infile)
    for sent,ID,prop in zip(full_sents,sentIDs,all_props):
        print "% "+" ".join(sent)
        print ID
        prop_sent,prop_dict = prop_to_dict(prop)
        replace_args(prop_sent,prop_dict)

if __name__ == "__main__":
    main()
