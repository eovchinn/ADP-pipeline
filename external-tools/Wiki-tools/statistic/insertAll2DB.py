#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys

def main():
    from optparse import OptionParser
    #option
    usage = "usage: %prog [options]"
    parser = OptionParser(usage=usage)
    parser.add_option("-d","--dir", dest="dirPath",help="the *.nt files dir path")
    (options,args) = parser.parse_args()
    
    dirPath = options.dirPath
    langs = ['EN','ES',"RU"]
    type_names = ['instance_types_en.nt','instance_types_es.nt','instance_types_ru.nt']
    property_names= ['mappingbased_properties_en.nt','mappingbased_properties_es.nt','mappingbased_properties_ru.nt']
    for i in range(3):
        lang = langs[i]
        type_name = type_names[i]
        property_name = property_names[i]
        command = 'python insertFile2DB.py -t __type_name__ -p __property_name__ -d -l __lang__'
        command = command.replace('__type_name__',dirPath + '/' + type_name)
        command = command.replace('__property_name__',dirPath + '/' + property_name)
        command = command.replace('__lang__',lang)
        out = os.system(command)
    
if __name__ == '__main__':
    main()
