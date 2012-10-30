#!/usr/bin/python

import argparse
import os
import re

# paths
parser2henry_path = '/home/ovchinnikova/Metaphor-ADP/pipelines/common/IntParser2Henry.pl'
henrydir = '/home/ovchinnikova/henry-n700/'
tokenizer_path = '/home/ovchinnikova/Metaphor-ADP/external-tools/tree-tagger-3.2/linux/cmd/utf8-tokenize.perl'
tagger_path = '/home/ovchinnikova/Metaphor-ADP/external-tools/tree-tagger-3.2/linux/bin/tree-tagger'
malt_ru_path = '/home/ovchinnikova/Metaphor-ADP/external-tools/malt-ru/'
malt_15_path = '/home/ovchinnikova/Metaphor-ADP/external-tools/malt-1.5/malt.jar'
malt_script_path = '/home/ovchinnikova/Metaphor-ADP/pipelines/Russian/malt_ru.py'

def extract_hypotheses(filepath,outputdir,fname):
	lines = open(filepath, "r")
	fout = open(os.path.join(outputdir,fname+".out"), 'w')

	hypothesis_found = False
	p = re.compile('<result-inference target="(.+)"')
	target = ''

	for line in lines:
		matchObj = p.match(line)
		if matchObj: target = matchObj.group(1)	
		elif line.startswith('<hypothesis'): hypothesis_found = True
		else:
			if hypothesis_found:	
				fout.write(target+': '+line)
				hypothesis_found = False
	fout.close()

def main():
	parser = argparse.ArgumentParser( description="Discource processing pipeline." )
	parser.add_argument( "--input", help="The input file to be processed.", nargs="+", default=["-"] )
	parser.add_argument( "--outputdir", help="The output directory. Default is the dir of the input file.", default='' )
	parser.add_argument( "--kb", help="Path to knowledge base.", default='' )
	
	pa = parser.parse_args()	

	outputdir = pa.outputdir
	for f in pa.input:
		fname = os.path.splitext(os.path.basename(f))[0]
		if len(pa.outputdir) == 0 : outputdir = os.path.dirname(f)

		# Russian dependency parsing
		malt = tokenizer_path + ' ' + f + ' | ' + tagger_path + ' -lemma -token -sgml ' + malt_ru_path + 'russian.par | ' + malt_ru_path + 'lemmatiser.pl -l ' + malt_ru_path + 'msd-ru-lemma.lex.gz -p ' + malt_ru_path + 'wform2011.ptn1 -c ' + malt_ru_path + 'cstlemma-linux-64bit | ' + malt_ru_path + 'make-malt.pl | java -Xmx16g -jar ' + malt_15_path + ' -c rus-test.mco -m parse | python ' + malt_script_path + ' > ' + os.path.join(outputdir,fname+'.malt')  
		os.system(malt) 

		# Parser2Henry processing
		b2h = 'perl ' + parser2henry_path + ' --input ' + os.path.join(outputdir,fname+'.malt') + ' --output ' + os.path.join(outputdir,fname+'.obs') + ' --nonmerge sameargs'
		os.system(b2h)

		# Henry processing
		henry = henrydir + "bin/henry -m infer " + pa.kb + " " + os.path.join(outputdir,fname+".obs") + " -e " + henrydir + "models/h93.py -T 120 -t 4 -O statistics > " + os.path.join(outputdir,fname+'.hyp')
		os.system(henry)

	# extract_hypotheses(os.path.join(outputdir,fname+".hyp"),outputdir,fname)

if "__main__" == __name__: main()