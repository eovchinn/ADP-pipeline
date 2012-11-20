#!/usr/bin/python

import sys
import NLPipeline_MULT_metaphor
from NLPipeline_MULT_metaphor import *

if __name__ == "__main__":
	lang = sys.argv[1]	

	en_metaphors = {'5': 'Few nations have gone through what you have gone through, and few nations in recent history have made the progress you\u2019ve made.', '3': 'This dog runs. The animal is funny.'}

	es_metaphors = {'id2': 'llevándose por delante los andamios del Estado del Bienestar','id4': 'Aquí está el PRI en pie de lucha.  Juárez siempre fue un faro que iluminó el camino de la legalidad y de la justicia.'}
	
	ru_metaphors = {'id2':'Съешьте еще этих мягких французских булочек, да выпейте же чаю.','id4':' Небо было почти черным, а снег при свете луны – ярко-голубым. И еще одно предложение'}

	fa_metaphors = {'id2': 'باراک اوباما، رئیس جمهوری آمریکا، با پیروزی در برابر میت رامنی، رقیب جمهوریخواه خود، چهار سال دیگر در مقام خود باقی می‌ماند. آقای رامنی شکست خود در انتخابات را پذیرفته و به آقای اوباما تبریک گفته است.','id4': 'برخی از وبسایت های خبری گزارش کرده اند که ستار بهشتی، وبلاگ نویسی که گفته می‌شود در هفتم آبان توسط پلیس ایران بازداشت شده بوده، کشته شده است.'}

	if lang == 'EN': print ADP(en_metaphors,'EN',True) 
	elif lang == 'ES': print ADP(es_metaphors,'ES',True)
	elif lang == 'RU': print ADP(ru_metaphors,'RU',True)
	elif lang == 'FA': print ADP(fa_metaphors,'FA',True)
	else: print 'Unknown language: '+lang+'\n'
