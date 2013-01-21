#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import os

if __name__ == "__main__":
	lang = sys.argv[1]

	# default is exact match
	substring = ''
	if len(sys.argv)==3:
		#substring match
		if sys.argv[2]=='-s': substring=" -s"

	en_string = 'Barack Obama'

	es_string = 'Juan Carlos I de España'
	
	ru_string = 'Путин'

	fa_string = 'محمود احمدی‌نژاد'

	if lang == 'EN': input = en_string 
	elif lang == 'ES': input = es_string
	elif lang == 'RU': input = ru_string 
	elif lang == 'FA': input = fa_string 
	else: print 'Unknown language: '+lang+'\n'

	cmd = 'python get_categories.py "' + input + '" ' + lang + substring
	os.system(cmd)

