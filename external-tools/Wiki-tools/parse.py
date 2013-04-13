#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import subprocess
import sys

def parse(abstract,commonDir,tempFile,lang,std):
    tempFile = os.path.abspath(tempFile)
    abstract = abstract[1:-4]
    abstract = abstract.replace(r"\"",'"')
    abstract = abstract.replace(r"\'","'")

    obsFile = tempFile+'.obs'
    sentFile = tempFile+'.sent'
    sf = open(tempFile,'w')
    sf.write(abstract)
    sf.close()
    command = "python nltk_tokenizer.py -l __lang__ --input __path__"
    command = command.replace('__lang__',lang)
    command = command.replace('__path__',tempFile)
    subprocess.call(command.split())
    sf = open(sentFile,'r')
    i = 0
    sents = []
    while True:
        line = sf.readline()
        if not line:
            break
        sents.append(line)
        i+=1
        if i == 5:
            break
    sf.close()
    sf = open(sentFile,'w')
    for line in sents:
        sf.write(line)
    sf.close()
    command = 'python __commonDir__/NLPipeline_MULT_stdinout.py --lang __lang__ --input __path__ --parse'
    command = command.replace('__commonDir__',commonDir)
    command = command.replace('__lang__',lang)
    command = command.replace('__path__',sentFile)
    subprocess.call(command.split())
    
    obsf = open(obsFile,'r')
    obss = []
    while True:
        line = obsf.readline()
        if not line:
            break
        obss.append(line)
    obss = ''.join(obss)
    sents = ''.join(sents)
    if std:
        print '<sentences>'
        print sents
        print '<obss>'
        print obss
    
    return (sents,obss)


if __name__ == '__main__':
    from optparse import OptionParser
   
    # option
    usage="usage: %prog [options]"
    parser = OptionParser(usage=usage)
    parser.add_option("-l","--lang", dest='lang',help="language:EN,ES,RU,FA")
    parser.add_option("--common",dest='commonDir',help='the NLPipeline_MULT_stdinout.py folder path')
    parser.add_option("--temp",dest = 'tempFile',help='the temp File path')
    parser.set_defaults(commonDir = '/Users/xingshi/Workspace/isi/Metaphor-ADP/pipelines/common')
    parser.set_defaults(tempFile = 'temp/temp.txt')
    (options,args) = parser.parse_args()
    
    lang = options.lang
    common = options.commonDir
    temp = options.tempFile
    
    input = sys.stdin
    abstract = input.read()
    parse(abstract,common,temp,lang,True)
