#! /usr/bin/python
# -*- coding: utf-8 -*-
import re
import sys
import optparse
import logging

def to_sents(infile):
    words = []
    sentence = []
    full_sents = []
    all_words = []
    sent_count = 1
    IDflag = False
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
            outID = wordID
            if IDflag:
                newIter +=IDiter
                outID +=newIter           
            if date.match(wordLemma):
                wordLemma = wordText
            elif wordLemma == "<unknown>":
                wordLemma = wordText
            info = [longID,wordText,wordLemma,wordPOS,wordHead,wordRel,wordID,sent_count]
            sentence.append(wordText)
            words.append(info)
        else:
            full_sents.append(sentence)
            all_words.append(words)
            sent_count += 1
            if sentence == ['.'] or sentIDre.search(sentence[0]):
                sent_count -=1
            sentence = []
            new_prop_sent = []
            words = []
            IDFlag = False
    infile.close()
    return full_sents,all_words

def createLongID(wordID,token):
    if token.count("_") == 0:
        longID = '%0*d' % (3, wordID)
        IDflag = False
    else:
        allIDs = []
        for word in token.split("_"):
            singleID = '%0*d' % (3, wordID)
            wordID+=1
            allIDs.append(singleID)
        longID = ",".join(allIDs)
        IDflag = True
    return longID,IDflag,token.count("_")
        
def prop_to_dict(props,eCount,xCount,uCount):
    sent_dict = {}    
    new_prop_sent = []
    question = False
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
        if re.search(",",ID):
            multiple = ID.split(",")
            joinedIDs = []
            for oneID in multiple:
                singleID = str(sent_count)+str(oneID)
                joinedIDs.append(singleID)
            propID = ",".join(joinedIDs)
        if not re.search(",",ID):
            propID = str(sent_count)+str(ID)
        if propTags.match(pos):
            args,tag,eCount,xCount,uCount,question = build_predicate(pos,eCount,xCount,uCount,lemma,question,token)
            new_prop.extend([token,lemma,pos,head,rel,shortID,args,tag,propID])
            sent_dict[shortID]=[token,lemma,pos,head,rel,shortID,args,tag,propID]
            new_prop_sent.append(new_prop)
        elif token == "¿":
            args = ["R","R"]
            tag = ""
            new_prop.extend([token,lemma,pos,head,rel,shortID,args,tag,propID])
            sent_dict[shortID]=[token,lemma,pos,head,rel,shortID,args,tag,propID]
            new_prop_sent.append(new_prop)
            question = True
    return new_prop_sent,sent_dict,eCount,xCount,uCount

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
        if lemma in thingProList and realHead(sent_dict,head):
            sent_dict = det_to_pr(head,wordID,sent_dict)       
        if ((rel == "suj") or (rel == "spec")) and (tag != "NULL") and (realHead(sent_dict,head)):
            sent_dict = insert_suj(head,wordID,sent_dict)
        if tag == "vb" and realHead(sent_dict,head) and rel in inheritingVbs:
            sent_dict = inherit_args(head,wordID,sent_dict)
            sent_dict = insert_prep_Vcomp(head,wordID,sent_dict)
        #Look for auxiliary verbs (passive)
        if (tag == "vb" and rel == "v" and lemma in passivesList) and realHead(sent_dict,head) and int(sent_dict[head][8]) == int(sent_dict[wordID][8])+1:
            sent_dict = process_passive(head,wordID,sent_dict)
        if rel == "v" and lemma not in passivesList and tag != "" and realHead(sent_dict,head):
            sent_dict = process_aux(head,wordID,sent_dict)            
        if rel in prepRels and pos == "s" and realHead(sent_dict,head):
            sent_dict = insert_prepHead(head,wordID,sent_dict)
        if (rel == "sn" or rel == "spec") and predicate[-1] != "R" and realHead(sent_dict,head): # or rel == "grup.nom" - taken from first if
            sent_dict = insert_sn(head,wordID,sent_dict)
        if rel == "grup.nom" and predicate[-1] != "R" and realHead(sent_dict,head): # 
            sent_dict = insert_grup_nom(head,wordID,sent_dict)            
        if ((rel in adjectiveRels and (pos == "a")) or (lemma in quantifierList)) and realHead(sent_dict,head):
            sent_dict = insert_adjHead(head,wordID,sent_dict)          
        if rel == "cc" and pos == "r" and lemma not in whWords and realHead(sent_dict,head):
            sent_dict = insert_cc(head,wordID,sent_dict)
        if rel == "cd" and predicate[-1] != "R" and realHead(sent_dict,head):
            sent_dict = insert_cd(head,wordID,sent_dict)
        if rel == "ci" and predicate[-1] != "R" and realHead(sent_dict,head):
            sent_dict = insert_ci(head,wordID,sent_dict)            
        if rel == "atr" and realHead(sent_dict,head):
            sent_dict = inherit_atr(head,wordID,sent_dict)
        if rel == "morfema.pronominal" and pos == "p" and realHead(sent_dict,head):
            sent_dict = insert_m_p(head,wordID,sent_dict)
        if tag == "in" and realHead(sent_dict,head):
            sent_dict = insert_prepHead(head,wordID,sent_dict)
        if tag == "card" and realHead(sent_dict,head):
            sent_dict = insert_adjHead(head,wordID,sent_dict)
        if rel == "cpred" and realHead(sent_dict,head):
            sent_dict = insert_cpred(head,wordID,sent_dict)
        if tag == "rb" and (rel == "spec" or rel == "mod") and realHead(sent_dict,head):
            sent_dict = insert_rb_spec(head,wordID,sent_dict)
        if tag in proTagList and (rel == "spec") and realHead(sent_dict,head):
            sent_dict = insert_pro_spec(head,wordID,sent_dict)
        if lemma in subConList and realHead(sent_dict,head) and len(predicate) > 2 :
            sent_dict = insert_subCon_head(head,wordID,sent_dict)
        if lemma == "no" and realHead(sent_dict,head):
            sent_dict = handle_negation(head,wordID,sent_dict)
        if ((tag == "wh") or (tag == "whq")) and realHead(sent_dict,head):
            sent_dict = handle_wh(head,wordID,sent_dict)
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
        if lemma == "@card@":
            lemma = ""
            tag = "card"
        if "R" in predicate:
            predicate = []
        if len(predicate) > 0:
            prop_dict[propID]=[propID,lemma.lower(),tag,predicate,head]
    return prop_dict

def realHead(sent_dict,head):
    if sent_dict.has_key(head):
        return True
    return False

def handle_negation(head,wordID,sent_dict):
    sent_dict[wordID][7] = "not"
    if sent_dict[head][7] == "nn":
        sent_dict[wordID][6][1] = sent_dict[head][6][1]
    else:
        sent_dict[wordID][6][1] = sent_dict[head][6][0]
    return sent_dict

def handle_wh(head,wordID,sent_dict):
    """Handle all wh words"""
    extra = determine_wh_helper(sent_dict[wordID][1])
    sent_dict[wordID][1] = ""
    first_key = int(re.split("[a-z]",str(sorted(sent_dict.items())[0][0]))[0])
    if sent_dict[head][7] == "vb" or sent_dict[head][7] == "in":  
        headHead = sent_dict[head][3]
        if headHead == 0:
            sent_dict[head][6][2] = sent_dict[wordID][6][0]
            for key, values in sent_dict.items():
            #look for the direct object with the same head as the current word
                if (values[4] == "cd") and (values[3] == sent_dict[wordID][3]):
                    if values[7] == "vb":
                        sent_dict,newKey = add_new_entry(sent_dict,extra,sent_dict[wordID][6][1],sent_dict[values[5]][6][0],sent_dict[wordID][8])
                    else:
                        sent_dict,newKey = add_new_entry(sent_dict,extra,sent_dict[wordID][6][1],sent_dict[head][6][0],sent_dict[wordID][8])
                    return sent_dict
            sent_dict,newKey = add_new_entry(sent_dict,extra,sent_dict[wordID][6][1],sent_dict[head][6][0],sent_dict[wordID][8])
            return sent_dict
        elif realHead(sent_dict,headHead):
            if (sent_dict[headHead][7] == "vb" or sent_dict[headHead][7] == "in"):
                sent_dict[headHead][6][2] = sent_dict[wordID][6][0]
                sent_dict,newKey = add_new_entry(sent_dict,extra,sent_dict[wordID][6][1],sent_dict[head][6][0],sent_dict[wordID][8])
                return sent_dict
            elif sent_dict[headHead][7] == "nn" and realHead(sent_dict,headHead):
                sent_dict[wordID][6].append("R")
                sent_dict,NewKey = add_new_entry(sent_dict,extra,sent_dict[headHead][6][1],sent_dict[head][6][0],sent_dict[wordID][8])
                return sent_dict
    return sent_dict


def det_to_pr(head,wordID,sent_dict):
    headHead = sent_dict[head][3]
    if sent_dict[wordID][1] in thingProList and sent_dict[head][7] != "nn" and sent_dict[wordID][2] != "p":
        sent_dict[wordID][7] = "thing"
        sent_dict[wordID][2] = "p"
        last_e = int(find_last_e(sent_dict))
        newE = "e"+str(last_e+1)
        newX = "x"+str(last_e+1)        
        sent_dict[wordID][6] = [newE,newX]
        last_key = int(re.split("[a-z]",str(sorted(sent_dict.items())[-1][0]))[0])
        newKey = str(last_key)+"b"
        if sent_dict.has_key(newKey):
            newKey = str(last_key+1)+"b"
        args = [newE,newX,"R"]
        propID = str(wordID)+"b"
        sent_dict[newKey]=["","","",0,"",0,args,"",propID]
    return sent_dict
  
def find_last_e(sent_dict):
    for entry in reversed(sent_dict.items()):
        if re.search("e",entry[1][6][0]):
            return entry[1][6][0].split("e")[1]

def determine_wh_helper(lemma):
    if lemma == "dónde" or lemma == "donde":
        return "loc"
    if lemma == "cómo":
        return "manner"
    if lemma == "cuando" or lemma == "cuándo":
        return "time"
    if lemma ==  "por_qué":
        return "reason"
    if lemma == "quién" or lemma == "Quién":
        return "person"
    if lemma == "qué":
        return "thing"

def insert_suj(head,wordID,sent_dict):
    """Insert the subject of a verb as its first argument"""
    if sent_dict[wordID][4] == "spec" and sent_dict[wordID][1] not in thingProList:
        return sent_dict
    if sent_dict[wordID][4] == "spec" and sent_dict[head][7] != "vb":
        return sent_dict
    if sent_dict[head][7] == "vb" and sent_dict[wordID][2] in nominalList:
        sent_dict[head][6][1] = sent_dict[wordID][6][1]
    elif sent_dict[head][7] == "vb" and sent_dict[wordID][7] != "nn" and sent_dict[wordID][6][0] != "R":
        sent_dict[head][6][1] = sent_dict[wordID][6][0]
    return sent_dict

def process_passive(head,wordID,sent_dict):
    """Remove the passive verb, and move the subject to the object place (2nd arg) in the head verb"""
    sent_dict[wordID][6].append("R")
    if nounArg.search(sent_dict[head][6][1]) and sent_dict[head][7] == "vb":
        replace = sent_dict[head][6][2]
        sent_dict[head][6][2] = sent_dict[head][6][1]
        sent_dict[head][6][1] = replace
    return sent_dict

def process_aux(head,wordID,sent_dict):
    """Deal with verbs designated auxiliary by the parser"""
    if sent_dict[head][7] == "vb" and sent_dict[wordID][7] == "vb":
        sent_dict[wordID][6][2] = sent_dict[head][6][0]
    return sent_dict


def inherit_args(head,wordID,sent_dict):
    """Inherit the arguments of a head verb"""
    #if the current verb doesn't already have a subject
    if sent_dict[head][7] == "vb" and not nounArg.search(sent_dict[wordID][6][1]):
        previous = sent_dict[wordID][6][1]
        #inherit the subject of the head
        sent_dict[wordID][6][1] = sent_dict[head][6][1]
        #hack to replace subject of linked verbs that occur previously, since my code is slop
        if variableArg.search(previous):
            for key, values in sent_dict.items():
                if values[6][1] == previous:
                    values[6][1] = sent_dict[head][6][1]        
        #if the current word doesn't already have an object #taken out 12/4/12 after talking with Katya
        #if not nounArg.search(sent_dict[wordID][6][2]) and nounArg.search(sent_dict[head][6][2]):
            #inherit the object of the head
            #sent_dict[wordID][6][2] = sent_dict[head][6][2]
    ######## removed following block 12/6/12 - it seemed to hurt more than help                    
    #if the current word has a clause deprel
    # if sent_dict[wordID][4] == "S":
    #     for key, values in sent_dict.items():
    #         #look for a conjunction with the same head as the current word
    #         if (values[4] == "conj") and (values[3] == sent_dict[wordID][3]) and values[1] in andOrList:
    #             conjHead = values[3]
    #             headHead = sent_dict[conjHead][3]
    #             if headHead != 0 and sent_dict[headHead][7]:
    #                 sent_dict = add_new_verb(sent_dict,sent_dict[headHead][1],sent_dict[headHead][7],sent_dict[headHead][6],sent_dict[wordID][6][0],sent_dict[headHead][8],sent_dict[head][8],wordID,head)
    #              #if the conjuction is "o" add an "or" proposition
    #             if (values[1] == "o"):
    #                 sent_dict,newKey = add_new_entry(sent_dict,"or",sent_dict[head][6][0],sent_dict[wordID][6][0],sent_dict[wordID][8])
    return sent_dict

def inherit_atr(head,wordID,sent_dict):
    if sent_dict[head][7] == "vb" and not nounArg.search(sent_dict[wordID][6][1]):
        sent_dict[wordID][6][1] = sent_dict[head][6][1]
    if sent_dict[head][1] in copulaList:
        headHead = sent_dict[head][3]
        if sent_dict[wordID][7] == "adj":
            sent_dict[head][6].append("R")
        if sent_dict[wordID][7] == "nn":
            sent_dict[head][6].append("R")
            sent_dict,newKey = add_new_entry(sent_dict,"equal",sent_dict[head][6][1],sent_dict[wordID][6][1],sent_dict[wordID][8])
            sent_dict = replace_old_args(sent_dict,sent_dict[head][6][0],newKey)
        if sent_dict[wordID][7] == "vb":
            sent_dict[head][6].append("R")
            sent_dict,newKey = add_new_entry(sent_dict,"be",sent_dict[head][6][1],sent_dict[wordID][6][0],sent_dict[wordID][8])            
    return sent_dict

def replace_old_args(sent_dict,headE,newKey):
    """If a copula has been removed and replaced with 'equal', replace any arguments based on the copula entity with the new equal entity """
    newE = sent_dict[newKey][6][0]
    for key, values in sent_dict.items():
        for i in range(len(values[6])):
            if values[6][i] == headE:
                values[6][i] = newE
    return sent_dict

def add_new_entry(sent_dict,tag,arg1,arg2,currID):
    """Add a new entry to the sentence dictionary for items that aren't explicit in the surface form"""
    last_key = int(re.split("[a-z]",str(sorted(sent_dict.items())[-1][0]))[0])
    last_e = int(find_last_e(sent_dict))
    newE = "e"+str(last_e+1)
    if tag == "person":
        args = [newE,arg1]
    else:
        args = [newE,arg1,arg2]
    propID = currID+"b"
    newKey = str(last_key)+"b"
    if sent_dict.has_key(newKey):
        newKey = str(last_key+1)+"b"
    sent_dict[newKey]=["","","",0,"",0,args,tag,propID]
    return sent_dict,newKey

def add_new_verb(sent_dict,token,tag,hhargs,arg2,verbID,currID,wordID,head):
    """Add a new verb entry to the sentence dictionary for items that aren't explicit in the surface form"""
    last_key = int(re.split("[a-z]",str(sorted(sent_dict.items())[-1][0]))[0])
    last_e = int(find_last_e(sent_dict))#int(sorted(sent_dict.items())[-1][1][6][0].split("e")[1])
    newE = "e"+str(last_e+1)
    arg1 = hhargs[1]
    args = [newE,arg1,arg2]
    if tag == "vb":
        args.append(hhargs[3])
    newKey = str(last_key)+"b"
    newID = currID+"b"
    if sent_dict.has_key(newKey):
        newKey = str(last_key+1)+"b"
    headHead = sent_dict[head][3]
    if sent_dict[headHead][1] == "ser":
        sent_dict,newKey = add_new_entry(sent_dict,"equal",arg1,arg2,sent_dict[wordID][8])
    else:
        sent_dict[newKey]=[token,token,"",verbID,"",0,args,tag,newID]
    return sent_dict

def insert_cd(head,wordID,sent_dict):
    """Insert the direct object as the head verb's second argument"""
    if sent_dict[wordID][2] in nominalList and sent_dict[head][7] == "vb":
        sent_dict[head][6][2] = sent_dict[wordID][6][1]
    if sent_dict[wordID][2] == "v" and sent_dict[head][7] == "vb" and not nounArg.search(sent_dict[head][6][2]) and not nounArg.search(sent_dict[wordID][6][1]):
        if not entityArg.search(sent_dict[head][6][2]):
            sent_dict[head][6][2] = sent_dict[wordID][6][0]
        sent_dict[wordID][6][1] = sent_dict[head][6][1]    
    return sent_dict

def insert_ci(head,wordID,sent_dict):
    """Insert the indirect object as the head verb's third argument"""
    if sent_dict[wordID][2] in nominalList and sent_dict[head][7] == "vb":
        sent_dict[head][6][3] = sent_dict[wordID][6][1]
    if sent_dict[wordID][2] == "v" and sent_dict[head][7] == "vb":
        sent_dict[head][6][2] = sent_dict[wordID][6][0]        
    return sent_dict

def insert_prepHead(head,wordID,sent_dict):
    """Insert the head of a preposition as its first argument"""
    if sent_dict[head][7] == "vb":
        if sent_dict[head][1] == "estar":
            sent_dict[wordID][6][1] = sent_dict[head][6][1]
            sent_dict[head][6][3] = "R"
        else:
            sent_dict[wordID][6][1] = sent_dict[head][6][0]    
    if sent_dict[head][7] == "nn" and head < wordID:
        sent_dict[wordID][6][1] = sent_dict[head][6][1]
    if sent_dict[head][7] == "nn" and head > wordID:
        sent_dict[wordID][6][2] = sent_dict[head][6][1]        
    if sent_dict[head][7] == "rb" or sent_dict[head][7] == "adj":
        sent_dict[wordID][6][1] = sent_dict[head][6][0]
    if sent_dict[head][7] == "in":
        sent_dict[wordID][6][1] = sent_dict[head][6][0]
    return sent_dict

def insert_subCon_head(head,wordID,sent_dict):
    """Find the head of a subconjugating conjunction"""
    if sent_dict[head][7] == "vb" and sent_dict[head][4] not in rootList:#(sent_dict[head][4] == "cd" or sent_dict[head][4] == "ao"):
        if sent_dict[head][1] == "estar":
            sent_dict[wordID][6][2] = sent_dict[head][6][1]
            sent_dict[head][6][3] = "R"
        else:
            sent_dict[wordID][6][2] = sent_dict[head][6][0]
        headHead = sent_dict[head][3] 
        if realHead(sent_dict,headHead) and sent_dict[headHead][7] == "vb":
            sent_dict[wordID][6][1] = sent_dict[headHead][6][0]
        if (sent_dict[head][7] == "vb") and sent_dict[head][4] in rootList:
            sent_dict[wordID][6][1] = sent_dict[head][6][0]
    return sent_dict

def insert_sn(head,wordID,sent_dict):
    if sent_dict[wordID][4] == "spec" and sent_dict[wordID][1] not in thingProList:
        return sent_dict
    if sent_dict[wordID][4] == "spec" and sent_dict[head][7] != "in":
        return sent_dict     
    if sent_dict[head][7] == "in" and sent_dict[wordID][7] == "nn":
        sent_dict[head][6][2] = sent_dict[wordID][6][1]
    if sent_dict[head][7] == "in" and sent_dict[wordID][7] != "nn":
        sent_dict[head][6][2] = sent_dict[wordID][6][0]        
    elif sent_dict[head][7] == "vb":
        sent_dict[head][6][2] = sent_dict[wordID][6][1]
    elif (sent_dict[head][7] == "nn" and sent_dict[wordID][7] == "nn") and (int(sent_dict[head][8]) == int(sent_dict[wordID][8])+1):
        if int(sent_dict[head][6][1].split("x")[1]) == int(sent_dict[wordID][6][1].split("x")[1])-1:
            sent_dict[wordID][6][1] = sent_dict[head][6][1]
        for key, values in sent_dict.items():
            #look for a conjunction with the same head as the current word
            if (values[4] == "conj") and (values[3] == sent_dict[wordID][3]):
                conjHead = values[3]
                headHead = sent_dict[conjHead][3]
                if realHead(sent_dict,headHead):# != 0:
                    sent_dict = add_new_verb(sent_dict,sent_dict[headHead][1],sent_dict[headHead][7],sent_dict[headHead][6],sent_dict[wordID][6][1],sent_dict[headHead][8],sent_dict[head][8],wordID,head)
                 #if the conjuction is "o" add an "or" proposition
                if (values[1] == "o"):
                    sent_dict,newKey = add_new_entry(sent_dict,"or",sent_dict[head][6][0],sent_dict[wordID][6][0],sent_dict[wordID][8])        
    return sent_dict

def insert_grup_nom(head,wordID,sent_dict):
    if sent_dict[wordID][4] == "spec" and sent_dict[wordID][1] not in thingProList:
        return sent_dict
    if sent_dict[wordID][4] == "spec" and sent_dict[head][7] != "in":
        return sent_dict     
    if sent_dict[head][7] == "in" and sent_dict[wordID][7] == "nn":
        sent_dict[head][6][2] = sent_dict[wordID][6][1]
    if sent_dict[head][7] == "in" and sent_dict[wordID][7] != "nn":
        sent_dict[head][6][2] = sent_dict[wordID][6][0]        
    elif sent_dict[head][7] == "vb":
        sent_dict[head][6][2] = sent_dict[wordID][6][1]
    elif sent_dict[head][7] == "nn" and sent_dict[wordID][7] == "nn":
        for key, values in sent_dict.items():
            #look for a conjunction with the same head as the current word
            if (values[4] == "conj") and (values[3] == sent_dict[wordID][3]):
                conjHead = values[3]
                headHead = sent_dict[conjHead][3]
                if realHead(sent_dict,headHead):#headHead != 0:
                    sent_dict = add_new_verb(sent_dict,sent_dict[headHead][1],sent_dict[headHead][7],sent_dict[headHead][6],sent_dict[wordID][6][1],sent_dict[headHead][8],sent_dict[head][8],wordID,head)
                 #if the conjuction is "o" add an "or" proposition
                if (values[1] == "o"):
                    sent_dict,newKey = add_new_entry(sent_dict,"or",sent_dict[head][6][0],sent_dict[wordID][6][0],sent_dict[wordID][8])        
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
    if sent_dict[head][7] == "vb" and sent_dict[wordID][7] != "nn":
        sent_dict[wordID][6][1] = sent_dict[head][6][0]
    return sent_dict

def insert_adjHead(head,wordID,sent_dict):
    #when the head is a noun, simply insert the first argument of the head
    if sent_dict[head][7] == "nn":
        sent_dict[wordID][6][1] = sent_dict[head][6][1]
    elif sent_dict[head][7] == "card":
        sent_dict[wordID][6][1] = sent_dict[head][6][0]
        #when the head is an adj, insert the first argument of the head of the head
    elif sent_dict[head][2] == "a":
        sent_dict[wordID][6][1] = sent_dict[head][6][1]
    elif sent_dict[wordID][7] == "card":
        sent_dict[wordID][1] = ""
        sent_dict[wordID][8] = sent_dict[head][8]+"b"
    elif sent_dict[head][7] == "in":
        sent_dict[head][6][2] = sent_dict[wordID][6][0]
    else:
        sent_dict[wordID][6].append("R")
    return sent_dict

def insert_atr(head,wordID,sent_dict):
    if sent_dict[head][7] == "vb":
        sent_dict[head][6][2] = sent_dict[wordID][6][0]
    return sent_dict

def insert_rb_spec(head,wordID,sent_dict):
    sent_dict[wordID][6][1] = sent_dict[head][6][0]    
    return sent_dict

def insert_pro_spec(head,wordID,sent_dict):
    if sent_dict[wordID][0] in possessiveProList:
        if sent_dict[head][7] == "nn":
            sent_dict,newKey = add_new_entry(sent_dict,"of-in",sent_dict[head][6][1],sent_dict[wordID][6][1],sent_dict[wordID][8])
        else:
            sent_dict,newKey = add_new_entry(sent_dict,"of-in",sent_dict[head][6][1],sent_dict[wordID][6][0],sent_dict[wordID][8])          
    return sent_dict

def insert_cc(head,wordID,sent_dict):    
    if sent_dict[head][7] == "vb":
        sent_dict[wordID][6][1] = sent_dict[head][6][0]
    return sent_dict

def insert_m_p(head,wordID,sent_dict):
    if sent_dict[head][7] == "vb":
        sent_dict[head][6][2] = sent_dict[head][6][1]
    return sent_dict

def build_predicate(pos,eCount,xCount,uCount,lemma,question,token):
    pred = []
    tag = ""
    if not re.search("\w",lemma):
        return ["R","R"],"",eCount,xCount,uCount,question        
    if lemma in whWords:
        if not question:
            tag = "wh"
            pos = "wh"
        else:
            tag = "whq"
            pos = "whq"
            question = False
        pred.append("e"+str(eCount))
        eCount+=1
        pred.append("x"+str(xCount))
        xCount+=1
        return pred,tag,eCount,xCount,uCount,question
    if question:
        if lemma == "qué":
            tag = "whq"
            pos = "wh"
            pred.append("e"+str(eCount))
            eCount+=1
            pred.append("x"+str(xCount))
            xCount+=1
            question = False
            return pred,tag,eCount,xCount,uCount,question
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
        return pred,tag,eCount,xCount,uCount,question
    if nounTag.match(pos): 
        tag="nn"
        pred.append("e"+str(eCount))
        eCount+=1
        pred.append("x"+str(xCount))
        xCount+=1
        return pred,tag,eCount,xCount,uCount,question
    if pronounTag.match(pos):
        tag = pronoun_tag(lemma)
        if tag != "NULL":
            pred.append("e"+str(eCount))
            eCount+=1
            pred.append("x"+str(xCount))
            xCount+=1
        else:
            pred.append("u"+str(uCount))
            uCount+=1
            pred.append("u"+str(uCount))
            uCount+=1             
            pred.append("R")
        return pred,tag,eCount,xCount,uCount,question
    if adjectiveTag.match(pos):
        tag="adj"
        pred.append("e"+str(eCount))
        eCount+=1
        pred.append("u"+str(uCount))
        uCount+=1        
        return pred,tag,eCount,xCount,uCount,question
    if lemma in subConList:
        tag="in"
        pred.append("e"+str(eCount))
        eCount+=1
        pred.append("u"+str(uCount))
        uCount+=1
        pred.append("u"+str(uCount))
        uCount+=1
        return pred,tag,eCount,xCount,uCount,question    
    if adverbTag.match(pos):
        tag="rb"
        pred.append("e"+str(eCount))
        eCount+=1
        pred.append("u"+str(uCount))
        uCount+=1        
        return pred,tag,eCount,xCount,uCount,question
    if prepositionTag.match(pos):
        tag="in"
        pred.append("e"+str(eCount))
        eCount+=1
        pred.append("u"+str(uCount))
        uCount+=1
        pred.append("u"+str(uCount))
        uCount+=1        
        return pred,tag,eCount,xCount,uCount,question
    if cardTag.match(pos):
        tag="card"
        if lemma == "@card@":
            lemma = token
        pred.append("e"+str(eCount))
        eCount+=1
        pred.append("u"+str(uCount))
        uCount+=1
        number = cardinal_number(lemma)
        pred.append(number)
        return pred,tag,eCount,xCount,uCount,question
    if detTag.match(pos) and lemma in quantifierList:
        tag="adj"
        pred.append("e"+str(eCount))
        eCount+=1
        pred.append("u"+str(uCount))
        uCount+=1        
        return pred,tag,eCount,xCount,uCount,question
    if conjTag.match(pos) and lemma not in noPropConjList:
        tag="in"
        pred.append("e"+str(eCount))
        eCount+=1
        pred.append("u"+str(uCount))
        uCount+=1
        pred.append("u"+str(uCount))
        uCount+=1
        return pred,tag,eCount,xCount,uCount,question
    else:
        return ["R","R"],"",eCount,xCount,uCount,question

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

    #if tagset == "ancora":
nounTag = re.compile("^n$")
verbTag = re.compile("^v$")
adjectiveTag = re.compile("^a$")
adverbTag = re.compile("^r$")
prepositionTag = re.compile("^s$")
pronounTag = re.compile("^p$")
cardTag = re.compile("^z$")
detTag = re.compile("^d$")
conjTag = re.compile("^c$")    
propTags = re.compile("^(n|v|a|r|s|p|z|c|d)$")

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
personProList = ["yo","me","nos","nosotros","usted","ustedes","mi","mis","su","sus","suyo","nuestro","nuestros","nuestra","nuestras","quién","tu","tú","quien","tus","mío"]
thingProList = ["ellos","ellas","él","este","ese","suyo","aquel"]
reflexProList = ["se"]
possessiveProList = ["mi","mis","tu","tus","su","sus","nuestro","nuestros","nuestra","nuestras","suyo","mío"]
proTagList = ["male","female","person","thing"]
quantifierList = ["todo","poco","otro"]
noPropConjList = ["y","o","ni","que"]
andOrList = ["y","o"]

nominalList = ["n","p"]
noTokenList = ["male","female","person","thing","reflexive"]
insertList = ["equal","card","or","be","loc","manner","time","nn","reason","of-in","person"]
inheritingVbs = ["S","v"]
adjectiveRels = ["s.a","cn","grup.a","S"]
rootList = ["ROOT","sentence"]
prepRels = ["sp","cn"]
whWords = ["dónde","cómo","donde","cuando","cuándo","por_qué","quién","Quién"]
subConList = ["porque","mientras_que","siempre_que","puesto_que","ya_que","pues"]

passivesList = ["haber","deber","tener","estar"]
copulaList = ["ser","estar"]

nounArg = re.compile("x\d")
entityArg = re.compile("e\d")
variableArg = re.compile("u\d")

nounPred = re.compile("nn\(e\d*,[ux]\d*\)")
pronounPred = re.compile("p\(e\d*,[ux]\d*\)")
date = re.compile("\[\?\?\:\?\?\/\?\?\/\d\d\d\d\:\?\?\.\?\?\]")
puncts = re.compile("[\.,\?\!{}()\[\]:;¿¡\"]")

sentIDre = re.compile("{{{.*}}}!!!")

def nextMeta(nextSentenceW1):
    if sentIDre.search(nextSentenceW1):
        return True
    return False

def to_print(prop_dict,sent):
    prop_count = 0
    printable = ""
    for key,prop in sorted(prop_dict.items()):
        prop_count+=1
        if prop[1] == "" and prop[2] in insertList:
            printable += (prop[2]+"("+",".join(prop[3])+")")
        elif prop[2] in noTokenList:
            printable += ("["+prop[0]+"]"+":"+prop[2]+"("+",".join(prop[3])+")")
        elif prop[2] == "not" or prop[2] =="wh" or prop[2] =="whq":
            printable += ("["+prop[0]+"]"+":"+prop[2]+"("+",".join(prop[3])+")")
        elif re.search("[a-z]",prop[0]):                
            printable += ("["+prop[4]+"]"+":"+prop[1]+"-"+prop[2]+"("+",".join(prop[3])+")")
        else:
            printable += ("["+prop[0]+"]"+":"+prop[1]+"-"+prop[2]+"("+",".join(prop[3])+")")
        if prop_count < len(prop_dict.items()):
            printable += (" & ")
    return printable


def main():
    ##################### I/O ##################################
    usage = "usage: %prog [options] <input_file>"
    parser = optparse.OptionParser(usage=usage)
    parser.add_option("-i", "--inFile", dest="input",
                      action="store", help="read from FILE", metavar="FILE")
    (options, args) = parser.parse_args()

    lines = open(options.input, "r") if options.input else sys.stdin
    
    logfile = '/tmp/malt_to_prop_log.txt'
    logging.basicConfig(filename=logfile,level=logging.DEBUG)
    #logging.error("this is an error message")
    
    full_sents,all_words = to_sents(lines)
    sent_count = 0
    parse_count = 0
    metaFound = False
    prevmeta = "prev"
    metastring = "meta"
    meta_sentences = []
    meta_props = []
    eCount = 1
    xCount = 1
    uCount = 1    
    for sent,words in zip(full_sents,all_words):
        parse_count+=1
        if sentIDre.search(sent[0]):
            metastring = str(re.sub("\W","",sent[0]))
            if meta_sentences != []:
                print "% "+" ".join(meta_sentences)
                print "id("+str(prevmetastring)+")."
                print " & ".join(meta_props)
                print ""
                eCount = 1
                xCount = 1
                uCount = 1                
            meta_sentences = []
            meta_props = []
            metaFound = True
            prevmetastring = metastring
         
        if metaFound and not sentIDre.search(sent[0]) and (sent != ['.']):
            try:
                meta_sentences.append(" ".join(sent))
                prop_sent,prop_dict,eCount,xCount,uCount = prop_to_dict(words,eCount,xCount,uCount)
                prop_dict = replace_args(prop_sent,prop_dict)
                printable_props = to_print(prop_dict,sent)
                meta_props.append(printable_props)
            except Exception,err:
                logging.exception(" ".join(sent))
                logging.exception(str(err))

         

        if metastring != "meta" and parse_count == len(full_sents):
            print "% "+" ".join(meta_sentences)            
            print "id("+str(prevmetastring)+")."
            print " & ".join(meta_props)
            print ""
            eCount = 1
            xCount = 1
            uCount = 1               
            
        if (not sentIDre.search(sent[0])) and (not metaFound) and (sent != ['.']):
            sent_count += 1
            print "% "+" ".join(sent)
            print "id("+str(sent_count)+")."
            try:
                prop_sent,prop_dict,eCount,xCount,uCount = prop_to_dict(words,eCount,xCount,uCount)
                prop_dict = replace_args(prop_sent,prop_dict)
                print to_print(prop_dict,sent)
                print ""
            except Exception,err:
                logging.exception(" ".join(sent))                
                logging.exception(str(err))
            # prop_sent,prop_dict,eCount,xCount,uCount = prop_to_dict(words,eCount,xCount,uCount)
            # prop_dict = replace_args(prop_sent,prop_dict)
            # print to_print(prop_dict,sent)
            # print ""
            eCount = 1
            xCount = 1
            uCount = 1            

if __name__ == "__main__":
    main()
