#! /usr/bin/python
# -*- coding: utf-8 -*-
from re import split as re_split
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
        propID = str(sent_count)+str(ID)
        if not propTags.match(pos) and not puncts.match(lemma):            
            args = ["R"]
            tag = ""
            new_prop.extend([token,lemma,pos,head,rel,shortID,args,tag,propID])
            sent_dict[shortID]=[token,lemma,pos,head,rel,shortID,args,tag,propID]
            new_prop_sent.append(new_prop)
        elif propTags.match(pos):
            args,tag,eCount,xCount,uCount = build_predicate(pos,eCount,xCount,uCount,lemma)
            new_prop.extend([token,lemma,pos,head,rel,shortID,args,tag,propID])
            sent_dict[shortID]=[token,lemma,pos,head,rel,shortID,args,tag,propID]
            new_prop_sent.append(new_prop)
    return new_prop_sent,sent_dict

def replace_args(prop_sent,sent_dict):
    prop_dict = {}
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
        if rel == "suj" and tag != "NULL":
            sent_dict = insert_suj(head,wordID,sent_dict)
        if tag == "vb" and head != 0 and rel in inheritingVbs:
            sent_dict = inherit_args(head,wordID,sent_dict)
            sent_dict = insert_prep_Vcomp(head,wordID,sent_dict)
            #if tag == "vb" and head != 0:
            #sent_dict = 
        if rel in prepRels and pos == "s":
            sent_dict = insert_prepHead(head,wordID,sent_dict)
        if rel == "sn" and pos == "n":
            sent_dict = insert_sn(head,wordID,sent_dict)
        if rel in adjectiveRels and pos == "a":
            sent_dict = insert_adjHead(head,wordID,sent_dict)
        if rel == "cc" and pos == "r":
            sent_dict = insert_cc(head,wordID,sent_dict)
        if rel == "cd":
            sent_dict = insert_cd(head,wordID,sent_dict)
        if rel == "atr":
            sent_dict = inherit_atr(head,wordID,sent_dict)
        # if rel == "cag" and pos == "s":
        #     sent_dict = insert_cag(head,wordID,sent_dict)
        if rel == "morfema.pronominal" and pos == "p":
            sent_dict = insert_m_p(head,wordID,sent_dict)
        if tag == "in" and head != 0:
            sent_dict = insert_prep_head(head,wordID,sent_dict)
        if tag == "card" and head !=0:
            sent_dict = insert_adjHead(head,wordID,sent_dict)
    for key,prop in sent_dict.items():
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
        if predicate[-1] == "R":
            predicate = []
        if len(predicate) > 0:
            #print propID
            prop_dict[propID]=[propID,lemma,tag,predicate,head]
    return prop_dict

    
def insert_suj(head,wordID,sent_dict):
    if sent_dict[head][7] == "vb":
        #print sent_dict[wordID]
        sent_dict[head][6][1] = sent_dict[wordID][6][1]
    return sent_dict

nounArg = re.compile("x\d")

def inherit_args(head,wordID,sent_dict):
    #print sent_dict[wordID][4]
    #if the current verb doesn't already have a subject
    if sent_dict[head][7] == "vb" and not nounArg.search(sent_dict[wordID][6][1]):
        #inherit the subject of the head
        sent_dict[wordID][6][1] = sent_dict[head][6][1]
        #if the current word doesn't already have an object
        if not nounArg.search(sent_dict[wordID][6][2]) and nounArg.search(sent_dict[head][6][2]):
            #inherit the object of the head
            sent_dict[wordID][6][2] = sent_dict[head][6][2]
    #if the current word has a clause deprel
    if sent_dict[wordID][4] == "S":
        for key, values in sent_dict.items():
            #look for the "o" conjunction with the same head as the current word
            if (values[4] == "conj") and (values[3] == sent_dict[wordID][3]) and (values[1] == "o"):
                sent_dict = add_new_entry(sent_dict,"or",sent_dict[head][6][0],sent_dict[wordID][6][0],sent_dict[wordID][8])
    return sent_dict

def inherit_atr(head,wordID,sent_dict,):
    if sent_dict[head][7] == "vb" and not nounArg.search(sent_dict[wordID][6][1]):
        sent_dict[wordID][6][1] = sent_dict[head][6][1]
    if sent_dict[head][1] == "ser":
        if sent_dict[wordID][7] == "adj":
            sent_dict[head][6][3] = "R"
        if sent_dict[wordID][7] == "nn":
            sent_dict[head][6][3] = "R"
            sent_dict = add_new_entry(sent_dict,"equal",sent_dict[head][6][1],sent_dict[wordID][6][1],sent_dict[wordID][8])
        if sent_dict[wordID][7] == "vb":
            sent_dict[head][6][3] = "R"
            sent_dict = add_new_entry(sent_dict,"be",sent_dict[head][6][0],sent_dict[wordID][6][0],sent_dict[wordID][8])            
    return sent_dict

def add_new_entry(dictionary,tag,arg1,arg2,currID):
    """Add a new entry to the sentence dictionary for items that aren't explicit in the surface form"""
    last_key = int(re.split("[a-z]",str(sorted(dictionary.items())[-1][0]))[0])
    last_e = int(sorted(dictionary.items())[-1][1][6][0].split("e")[1])
    newE = "e"+str(last_e+1)
    args = [newE,arg1,arg2]
    propID = currID+"b"
    newKey = str(last_key)+"b"
    if dictionary.has_key(newKey):
        newKey = str(last_key+1)+"b"
    dictionary[newKey]=["","","",0,"",0,args,tag,propID]
    return dictionary

def add_new_verb(dictionary,token,tag,arg1,arg2,verbID,currID):
    """Add a new verb entry to the sentence dictionary for items that aren't explicit in the surface form"""
    last_key = int(re.split("[a-z]",str(sorted(dictionary.items())[-1][0]))[0])
    last_e = int(sorted(dictionary.items())[-1][1][6][0].split("e")[1])
    newE = "e"+str(last_e+1)
    args = [newE,arg1,arg2]
    newKey = str(last_key)+"b"
    newID = currID+"b"
    if dictionary.has_key(newKey):
        newKey = str(last_key+1)+"b"
    dictionary[newKey]=[token,token,"",verbID,"",0,args,tag,newID]
    return dictionary

def insert_prep_head(head,wordID,sent_dict):
    if sent_dict[head][7] == "vb":
        if sent_dict[head][1] == "estar":
            sent_dict[wordID][6][1] = sent_dict[head][6][1]
            sent_dict[head][6][3] = "R"
        else:
            sent_dict[wordID][6][1] = sent_dict[head][6][0]
    return sent_dict

def insert_cd(head,wordID,sent_dict):
    if sent_dict[wordID][2] == "n" and sent_dict[head][7] == "vb":
        sent_dict[head][6][2] = sent_dict[wordID][6][1]
    if sent_dict[wordID][2] == "v" and sent_dict[head][7] == "vb":
        sent_dict[head][6][2] = sent_dict[wordID][6][0]        
    return sent_dict

def insert_prepHead(head,wordID,sent_dict):
    if sent_dict[head][7] == "nn":
        sent_dict[wordID][6][1] = sent_dict[head][6][1]
    return sent_dict

def insert_sn(head,wordID,sent_dict):
    if sent_dict[head][7] == "in":
        sent_dict[head][6][2] = sent_dict[wordID][6][1]
    elif sent_dict[head][7] == "nn":
        for key, values in sent_dict.items():
            #look for the conjunction with the same head as the current word
            if (values[4] == "conj") and (values[3] == sent_dict[wordID][3]):
                conjHead = values[3]
                headHead = sent_dict[conjHead][3]
                sent_dict = add_new_verb(sent_dict,sent_dict[headHead][1],sent_dict[headHead][7],sent_dict[headHead][6][1],sent_dict[wordID][6][1],sent_dict[headHead][8],sent_dict[head][8])
                 #if the conjuction is "o" add an "or" proposition
                if (values[1] == "o"):
                    sent_dict = add_new_entry(sent_dict,"or",sent_dict[head][6][0],sent_dict[wordID][6][0],sent_dict[wordID][8])        
    return sent_dict

def insert_prep_Vcomp(head,wordID,sent_dict):
    if sent_dict[head][7] == "in":
        sent_dict[head][6][2] = sent_dict[wordID][6][0]
    return sent_dict

def insert_cag(head,wordID,sent_dict):
    if sent_dict[head][7] == "vb":
        sent_dict[wordID][6][1] = sent_dict[head][6][0]
    return sent_dict

def insert_cpred(head,wordID,sent_dict):
    if sent_dict[head][7] == "vb":
        sent_dict[wordID][6][1] = sent_dict[head][6][0]
    return sent_dict

def insert_adjHead(head,wordID,sent_dict):
    if sent_dict[head][7] == "nn":
        sent_dict[wordID][6][1] = sent_dict[head][6][1]
    if sent_dict[wordID][7] == "card":
        sent_dict[wordID][8] = sent_dict[head][8]+"b"
    return sent_dict

def insert_atr(head,wordID,sent_dict):
    if sent_dict[head][7] == "vb":
        sent_dict[head][6][2] = sent_dict[wordID][6][0]
    return sent_dict

def insert_cc(head,wordID,sent_dict):
    if sent_dict[head][7] == "vb":
        sent_dict[wordID][6][1] = sent_dict[head][6][0]
    return sent_dict

def insert_m_p(head,wordID,sent_dict):
    if sent_dict[head][7] == "vb":
        sent_dict[head][6][2] = sent_dict[head][6][1]
    return sent_dict

def build_predicate(pos,eCount,xCount,uCount,lemma):
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
        tag = pronoun_tag(lemma)
        if tag != "NULL":
            pred.append("e"+str(eCount))
            eCount+=1
            pred.append("x"+str(xCount))
            xCount+=1
        else:
            pred = ["R"]
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
    if cardTag.match(pos):
        tag="card"
        pred.append("e"+str(eCount))
        eCount+=1
        pred.append("u"+str(uCount))
        uCount+=1
        number = cardinal_number(lemma)
        pred.append(number)
        return pred,tag,eCount,xCount,uCount

def cardinal_number(lemma):
    if card_dict.has_key(lemma):
        lemma = card_dict[lemma]
    return lemma

def add_args(args,arg,count):
    args.append

def pronoun_tag(lemma):
    if lemma in heProList:
        return "male"
    elif lemma in sheProList:
        return "female"
    elif lemma in personProList:
        return "person"
    elif lemma in thingProList:
        return "thing"
    # elif lemma in reflexProList:
    #     return "reflexive"    
    else:
        return "NULL"

if options.tagset == "ancora":
    nounTag = re.compile("^n$")
    verbTag = re.compile("^v$")
    adjectiveTag = re.compile("^a$")
    adverbTag = re.compile("^r$")
    prepositionTag = re.compile("^s$")
    pronounTag = re.compile("^p$")
    cardTag = re.compile("^z$")
    propTags = re.compile("^(n|v|a|r|s|p|z)$")

card_dict={}
card_dict["uno"] = "1"
card_dict["dos"] = "2"
card_dict["tres"] = "3"
card_dict["cuatro"] = "4"
card_dict["cinco"] = "5"
card_dict["seis"] = "6"
card_dict["siete"] = "7"
card_dict["ocho"] = "8"
card_dict["nueve"] = "9"
card_dict["diez"] = "10"

###############
#"he" (ESP: el, lo, se)-> male(e1,x1)
#"she" (ESP: ella, la, sua)->female(e1,x1)
#"it"->neuter(e1,x1)
#"I" (ESP: yo, me)->person(e1,x1)
#"we" (ESP: nosotros, nos)->person(e1,x1) & typelt(e2,x1,s)
#"you"(ESP: usted, ustedes)->person(e1,x1)
#"they"(ESP: ellos, ellas)->thing(e1,x1) & typelt(e2,x1,s)
###############

heProList = ["el","lo"]
sheProList = ["ella","la"]
personProList = ["yo","me","nos","nosotros","usted","ustedes"]
thingProList = ["ellos","ellas","él"]
reflexProList = ["se"]

noTokenList = ["male","female","person","thing","reflexive","equal","card","or","be"]
inheritingVbs = ["S","v"]
adjectiveRels = ["s.a","cn"]
prepRels = ["sp","cn"]

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
        prop_dict = replace_args(prop_sent,prop_dict)
        prop_count = 0
        for key,prop in sorted(prop_dict.items()):
            #print key,prop
            prop_count+=1
            if prop[2] in noTokenList:
                sys.stdout.write(prop[2]+"("+",".join(prop[3])+")")
            elif re.search("[a-z]",prop[0]):# and (prop[2] == "vb" or prop[2] == "in"):
                sys.stdout.write("["+prop[4]+"]"+":"+prop[1]+"-"+prop[2]+"("+",".join(prop[3])+")")
            else:
                sys.stdout.write("["+prop[0]+"]"+":"+prop[1]+"-"+prop[2]+"("+",".join(prop[3])+")")
            if prop_count < len(prop_dict.items()):
                sys.stdout.write(" & ")
        print ""

if __name__ == "__main__":
    main()
