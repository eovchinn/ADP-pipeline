#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import os

if __name__ == "__main__":
	lang = sys.argv[1]	

	en_string = 'Barack Obama'

	es_string = 'Juan Carlos I de España'
	
	ru_string = 'Путин'

	fa_string = ''

	if lang == 'EN': input = en_string 
	elif lang == 'ES': input = es_string
	elif lang == 'RU': input = ru_string 
	elif lang == 'FA': input = fa_string 
	else: print 'Unknown language: '+lang+'\n'

	cmd = 'python get_categories.py "' + input + '" ' + lang
	os.system(cmd)

