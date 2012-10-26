import sys

inputFile=open(sys.argv[1])
outputFile=open(sys.argv[2],"w")

line=inputFile.readline()
while line!="":
    words=[]
    POSs=[]
    labels=[]
    deps=[]
    wordPOSs=line.split()
    for wordPOS in wordPOSs:
        (word,POS)=wordPOS.split("_")
        words+=[word]
        POSs+=[POS]
        labels+=["LAB"]
        deps+=["0"]
    
    outputFile.write("%s\n"%"\t".join(words))
    outputFile.write("%s\n"%"\t".join(POSs))
    outputFile.write("%s\n"%"\t".join(labels))
    outputFile.write("%s\n"%"\t".join(deps))
    outputFile.write("\n")
    
    line=inputFile.readline()
    
inputFile.close()
outputFile.close()
    


