
#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import os

def main():
    
    from optparse import OptionParser
    
    #option
    usage = "usage: %prog [options]"
    parser = OptionParser(usage=usage)
    parser.add_option("-d","--dir", dest="dirPath",help="the *.nt files dir path")
    (options,args) = parser.parse_args()
    
    if not options.dirPath:
        parser.error("Please input the dir path")
    
    dirPath=options.dirPath
        
    files=['long_abstracts_en.nt'\
    #,'long_abstracts_en_uris_es.nt'\
    ,'long_abstracts_es.nt'\
    #,'long_abstracts_en_uris_ru.nt'\
    ,'long_abstracts_ru.nt'\
    #,'long_abstracts_en_uris_fa.nt'\
    ,'long_abstracts_fa.nt']
    
    langs=["EN","ES","RU","FA"]
    suffixes=["E","E","E","E"]
    langdict={"EN":[0],"ES":[1],"RU":[2],"FA":[3]}
    commands=[]
    errorlangs={}

    for i in range(0,len(files)):
        command = 'python insertFile2DB.py -s 1 -l '+langs[i]+' -f '+ dirPath + '/'+files[i]+" -x "+suffixes[i]
        commands.append(command)
        print 'Processing '+files[i]+" ..."
        print command
        out=os.system(command)
        if out == 0:
            print files[i] + ' inserted successful!'
        else:
            print files[i] + ' failed!'
            errorlangs[ langs[i] ]=1

    if len(errorlangs)>0:
        print 'Please drop the following tables:'
        for el in errorlangs:
            print "wiki_"+el.lower()
        print "Please run the following commands:"
        for el in errorlangs:
            for i in langdict[el]:
                print commands[i]
    else:
        print 'All done!'
            
        

if __name__ == '__main__':
    main()
