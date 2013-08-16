#! /usr/bin/python

import json
import sys
import glob

def extract_sents(infile):
    data = json.load(infile)
    sents = data['sentenceList']
    return sents

def printer(sents,outfile):
    for sent in sents:
        outfile.write(sent.encode('utf-8')+"\n")

# GOVERMENT TEST FILES IN DROPBOX AS OF 8/15/2013
# 868526 - 868645 - English
# 869503 - 869622 - Spanish
# 869964 - 870083 - Farsi
# 870569 - 870688 - Russian

def main():
    govt_dir = '/users/raisrael/Dropbox/Metaphor/GovernmentDocuments/'
    files = glob.glob(govt_dir+'*sentences.json')
    
    english_out = open("english_govt_sents.txt","w")
    spanish_out = open("spanish_govt_sents.txt","w")
    farsi_out = open("farsi_govt_sents.txt","w")
    russian_out = open("russian_govt_sents.txt","w")            
    
    for f in files:
        jsonfile = open(f,"r")
        sentences = extract_sents(jsonfile)        
        filename = f.split("/")[-1]
        fileID = int(filename.split("_")[0])
        if fileID < 869503: #English
            printer(sentences,english_out)
        elif fileID < 869964: #Spanish
            printer(sentences,spanish_out)            
        elif fileID < 870569: #Farsi
            printer(sentences,farsi_out)            
        else: #Russian
            printer(sentences,russian_out)            

if __name__ == "__main__":
    main()
