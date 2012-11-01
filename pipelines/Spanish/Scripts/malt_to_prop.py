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
    new_prop_sent = []
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
            longID = '%0*d' % (3, wordID)
            prop = [longID,wordText,wordLemma,wordPOS,wordHead,wordRel,wordID]
            sentence.append(wordText)
            props.append(prop)
        else:
            #print sentence
            print "% "+" ".join(sentence)
            #print ID(sentence number)
            print "id("+str(sent_count)+")."
            #loop over stored list of words and print props
            for i in range(len(props)):
                new_prop = []
                ID = props[0][0]
                token = props[0][1]
                lemma = props[0][2]
                pos = props[0][3]
                head = props[0][4]
                rel = props[0][5]
                shortID = props[0][6]
                if date.match(lemma):
                    lemma = token
                if puncts.match(lemma):
                    props.pop(0)
                elif not propTags.match(pos):
                    propID = "["+str(sent_count)+str(ID)+"]"
                    predicate = ""
                    new_prop.extend([token,lemma,pos,head,rel,shortID,predicate,propID])
                    new_prop_sent.append(new_prop)
                    props.pop(0)
                elif propTags.match(pos):
                    predicate,eCount,xCount,uCount = build_predicate(pos,eCount,xCount,uCount)
                    propID = "["+str(sent_count)+str(ID)+"]"
                    new_prop.extend([token,lemma,pos,head,rel,shortID,predicate,propID])
                    new_prop_sent.append(new_prop)
                    props.pop(0)
            position = 0
            for prop in new_prop_sent:
                position +=1
                token = prop[0]
                lemma = prop[1]
                pos = prop[2]
                head = prop[3]
                rel = prop[4]
                wordID = prop[5]
                predicate = prop[6]
                propID = prop[7]
                if nounTag.search(prop[2]):
                    #sys.stdout.write(propID+":"+lemma+"-"+predicate+"\n")
                    sys.stdout.write(propID+":"+lemma+"-"+predicate)
                    # for piece in prop:
                        
                    #     #sys.stdout.write(str(piece)+",")
                    # print ""
                elif prepositionTag.search(prop[2]):
                    predicate = processPrep(prop,new_prop_sent)
                    #sys.stdout.write(propID+":"+lemma+"-"+predicate+"\n")
                    sys.stdout.write(propID+":"+lemma+"-"+predicate)
                else:
                    #sys.stdout.write(propID+":"+lemma+"-"+predicate+"\n")
                    sys.stdout.write(propID+":"+lemma+"-"+predicate)                    
                if position < len(new_prop_sent):
                    sys.stdout.write(" & ")
            print ""
                #if len
            sent_count += 1
            sentence = []
            new_prop_sent = []
            props = []
            eCount = 1
            xCount = 1
            #print sent_count

def processPrep(prop,sent):
    args = []
    token = prop[0]
    lemma = prop[1]
    pos = prop[2]
    head = prop[3]
    rel = prop[4]
    wordID = prop[5]
    predicate = prop[6]
    propID = prop[7]
    predArgs = predicate.split("in(")[1].split(")")[0].split(",")
    eNumber = predicate.split("in(")[1].split(")")[0].split(",")[0]
    #print predicate, predArgs
    for word in sent:
        #print word
        if head == word[5]:
            if word[2] == "n":
                arg1 = word[6].split("nn(")[1].split(",")[1].split(")")[0]
            elif word[2] == "v":
                arg1 = word[6].split("vb(")[1].split(",")[0]
            elif word[2] == "s":
                arg1 = word[6].split("in(")[1].split(",")[0]
            predArgs[1] = arg1
        if wordID == word[3]:
            if word[2] == "n":
                arg2 = word[6].split("nn(")[1].split(",")[1].split(")")[0]
            elif word[2] == "v":
                arg2 = word[6].split("vb(")[1].split(",")[0]
            elif word[2] == "s":
                arg2 = word[6].split("in(")[1].split(",")[0]
            predArgs[2] = arg2
            newPred = pos+"("+eNumber+","+arg1+","+arg2+")"
    return newPred

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
        predicate=tag+"("+",".join(pred)+")"
        return predicate,eCount,xCount,uCount
    if nounTag.match(pos): 
        tag="nn"
        pred.append("e"+str(eCount))
        eCount+=1
        pred.append("x"+str(xCount))
        xCount+=1
        predicate=tag+"("+",".join(pred)+")"
        return predicate,eCount,xCount,uCount
    if pronounTag.match(pos):
        tag="p"
        pred.append("e"+str(eCount))
        eCount+=1
        pred.append("u"+str(uCount))
        uCount+=1
        predicate=tag+"("+",".join(pred)+")"
        return predicate,eCount,xCount,uCount 
    if adjectiveTag.match(pos):
        tag="adj"
        pred.append("e"+str(eCount))
        eCount+=1
        pred.append("u"+str(uCount))
        uCount+=1        
        predicate=tag+"("+",".join(pred)+")"
        return predicate,eCount,xCount,uCount
    if adverbTag.match(pos):
        tag="rb"
        pred.append("e"+str(eCount))
        eCount+=1
        pred.append("u"+str(uCount))
        uCount+=1        
        predicate=tag+"("+",".join(pred)+")"
        return predicate,eCount,xCount,uCount
    if prepositionTag.match(pos):
        tag="in"
        pred.append("e"+str(eCount))
        eCount+=1
        pred.append("u"+str(uCount))
        uCount+=1
        pred.append("u"+str(uCount))
        uCount+=1        
        predicate=tag+"("+",".join(pred)+")"
        return predicate,eCount,xCount,uCount

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

    #[??:??/??/1987:??.??]
date = re.compile("\[\?\?\:\?\?\/\?\?\/\d\d\d\d\:\?\?\.\?\?\]")
puncts = re.compile("[\.,\?\!{}()\[\]:;¿¡]")

def main():
    if options.input_FileName:
        input_file = options.input_FileName
    else:
        input_file = args[0]
    infile = open(input_file,"r")
    to_prop(infile)

if __name__ == "__main__":
    main()
