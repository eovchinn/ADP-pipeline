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
    eCount = 1
    xCount = 1
    for line in infile:
        line = line.strip().split("\t")
        if len(line) > 1:
            wordID = int(line[0])
            wordText = line[1]
            wordLemma = line[2]
            wordPOS = line[3]
            longID = '%0*d' % (3, wordID)
            prop = [longID,wordLemma,wordPOS,wordText]
            sentence.append(wordText)
            props.append(prop)
        else:
            #print sentence
            print "% "+" ".join(sentence)
            #print ID(sentence number)
            print "id("+str(sent_count)+")."
            #loop over stored list of words and print props
            for i in range(len(props)):
                if date.match(props[0][1]):
                    props[0][1] = props[0][3]
                if puncts.match(props[0][1]):
                    props.pop(0)
                elif not propTags.match(props[0][2]):
                    propID = "["+str(sent_count)+str(props[0][0])+"]"
                    sys.stdout.write(propID+":"+props[0][1])
                    props.pop(0)
                    if len(props) > 1:
                        sys.stdout.write(" & ")                   
                elif propTags.match(props[0][2]):
                    predicate,eCount,xCount = build_predicate(props[0][2],eCount,xCount)
                    propID = "["+str(sent_count)+str(props[0][0])+"]"
                    sys.stdout.write(propID+":"+props[0][1]+"-"+predicate)
                    props.pop(0)
                    if len(props) > 1:
                        sys.stdout.write(" & ")
                #place ampersand between words as long as the list of words has another entry
                #                if len(props) > 0:
                #    sys.stdout.write(" & ")
            print ""
            sent_count += 1
            sentence = []
            props = []
            eCount = 1
            xCount = 1
            #print sent_count

def build_predicate(pos,eCount,xCount):
    pred = []
    if verbTag.match(pos):
        tag = "vb"
        pred.append("e"+str(eCount))
        eCount+=1
        pred.append("x"+str(xCount))
        xCount+=1
        pred.append("x"+str(xCount))
        xCount+=1
        pred.append("x"+str(xCount))
        xCount+=1
        predicate=tag+"("+",".join(pred)+")"
        return predicate,eCount,xCount
    if nounTag.match(pos) or pronounTag.match(pos):
        tag="nn"
        pred.append("e"+str(eCount))
        eCount+=1
        pred.append("x"+str(xCount))
        xCount+=1
        predicate=tag+"("+",".join(pred)+")"
        return predicate,eCount,xCount
    if adjectiveTag.match(pos):
        tag="adj"
        pred.append("e"+str(eCount))
        eCount+=1
        pred.append("x"+str(xCount))
        xCount+=1        
        predicate=tag+"("+",".join(pred)+")"
        return predicate,eCount,xCount
    if adverbTag.match(pos):
        tag="rb"
        pred.append("e"+str(eCount))
        eCount+=1
        pred.append("x"+str(xCount))
        xCount+=1        
        predicate=tag+"("+",".join(pred)+")"
        return predicate,eCount,xCount
    if prepositionTag.match(pos):
        tag="in"
        pred.append("e"+str(eCount))
        eCount+=1
        pred.append("x"+str(xCount))
        xCount+=1
        pred.append("x"+str(xCount))
        xCount+=1        
        predicate=tag+"("+",".join(pred)+")"
        return predicate,eCount,xCount

def add_args(args,arg,count):
    args.append

if options.tagset == "ancora":
    nounTag = re.compile("n")
    verbTag = re.compile("v")
    adjectiveTag = re.compile("a")
    adverbTag = re.compile("r")
    prepositionTag = re.compile("s")
    propTags = re.compile("n|v|a|r|s|p")
    pronounTag = re.compile("p")

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
