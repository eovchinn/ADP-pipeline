import sys

#inputFormat: Each sentence is in a line:
#    word1_POS1 word2_POS2 ...
#outputFormat: Each token is in a line. Sentences are separated by a blank line
#    each line contains these 10 items, separated by tab: 
#    (id,word,lemma,CoarsePOS,FinePOS,etc1,dep,rel,etc2,etc3)

inputFile=open(sys.argv[1])
outputFile=open(sys.argv[2],"w")

def getLemma(word):
    return word
line=inputFile.readline()
while line!="":
    words=[]
    POSs=[]
    wordPOSs=line.split()
    for wordPOS in wordPOSs:
        (word,POS)=wordPOS.split("_")
        words+=[word]
        POSs+=[POS]
    for i in range(0,len(words)):
        lemma=getLemma(words[i])
        items=(str(i+1),words[i],lemma,POSs[i],POSs[i],"_","_","_","_","_")
        outputFile.write("%s\n"%"\t".join(items))
    
    outputFile.write("\n")
    line=inputFile.readline()
    
inputFile.close()
outputFile.close()
    


