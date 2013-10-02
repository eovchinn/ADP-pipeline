#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
from collections import defaultdict
import json

def wordStr2print(Args,WordProps,Equalities):
	output_str = ''

	for arg in Args:
		newwords = findWords(arg,WordProps,Equalities,False)
		if len(newwords)>0:	output_str += ',' + findWords(arg,WordProps,Equalities,False)
	
	return output_str[1:]

def wordStr2print_Mapping(labeledProps,WordProps,Equalities):
	output_str = ''
	for (propName,args) in labeledProps:
		output_str += ', ' + propName + '['
		words_str = ''
		for arg in args:			
			words = findWords(arg,WordProps,Equalities,True)
			words_str += '; ' + words
		if len(words_str)>0:	
			words_str = words_str[2:]

		output_str += words_str + ']' 

	#print json.dumps(output_str[2:], ensure_ascii=False)
	return output_str[2:]

def findWords(ARG,WordProps,Equalities,isMapping):
	all_args = []
	if isMapping and Equalities.has_key(ARG): all_args = Equalities[ARG].keys()

	all_args.append(ARG)

	output_str = ''
	for arg in all_args:
		if not arg.startswith('_') and not arg.startswith('u'):
			for (propName,args) in WordProps:
				if arg == args[0] and (propName.endswith('-vb') or propName.endswith('-rb') or propName.endswith('-adj') or propName.endswith('-nn')):
					if propName.endswith('-adj'): output_str += ',' + propName[:-4]
					else: output_str += ',' + propName[:-3]
				elif len(args)>1 and arg ==args[1] :
					if propName.endswith('-nn'): output_str += ',' + propName[:-3]
					elif propName=='person': output_str += ',person'
				#TODO: enable when Boxer starts working correctly
				#elif propName=='subset-of' and arg==args[2] :
				#	output_str += ',' + findWords(args[1],WordProps,Equalities,isMapping)
	
	if len(output_str)>0: 
		return output_str[1:]

	if isMapping:	return ARG		
	return ''

def createDStruc(superD,subD):
	outputstrucs = defaultdict(dict)

	for superd in superD:
		for superArgs in superD[superd]:
			if not outputstrucs.has_key(superd) or not outputstrucs[superd].has_key(superArgs[0]): outputstrucs[superd][superArgs[0]] = []
			for subd in subD:
				for subArgs in subD[subd]:
					if len(subArgs)>1 and superArgs[0]==subArgs[1]:
						outputstrucs[superd][superArgs[0]].append((subd,subArgs[0]))

	#print json.dumps(outputstrucs, ensure_ascii=False)
	return outputstrucs

def collectVars(struc,superkey):
	output = []

	for arg in struc[superkey]:
		if not arg.startswith('_'): output.append(arg)
		for (subd,subarg) in struc[superkey][arg]:
			if not subarg.startswith('_'): output.append(subarg)
	return output

def isLinkedbyParse(v1,v2,word_props,equalities,been):
	if (v1,v2) in been: return False
	been.append((v1,v2))
	been.append((v2,v1))

	if equalities.has_key(v1) and equalities[v1].has_key(v2): return True

	for (propName,args) in word_props:
		if v1 in args:
			if v2 in args: 
				return True
			else:
				if len(args)>2: 
					i1 = args.index(v1)
					if i1==0: 
						if isLinkedbyParse(args[1],v2,word_props,equalities,been): return True
						if isLinkedbyParse(args[2],v2,word_props,equalities,been): return True
						if len(args)>3 and isLinkedbyParse(args[3],v2,word_props,equalities,been): return True
					elif i1==1:
						if isLinkedbyParse(args[0],v2,word_props,equalities,been): return True
						if isLinkedbyParse(args[2],v2,word_props,equalities,been): return True
						if len(args)>3 and isLinkedbyParse(args[3],v2,word_props,equalities,been): return True
					elif i1==2:
						if isLinkedbyParse(args[0],v2,word_props,equalities,been): return True
						if isLinkedbyParse(args[1],v2,word_props,equalities,been): return True
						if len(args)>3 and isLinkedbyParse(args[3],v2,word_props,equalities,been): return True
					elif i1==3:
						if isLinkedbyParse(args[0],v2,word_props,equalities,been): return True
						if isLinkedbyParse(args[1],v2,word_props,equalities,been): return True
						if isLinkedbyParse(args[2],v2,word_props,equalities,been): return True
		elif v2 in args:
			if len(args)>2: 
				i2 = args.index(v2)
				if i2==0: 
					if isLinkedbyParse(args[1],v1,word_props,equalities,been): return True
					if isLinkedbyParse(args[2],v1,word_props,equalities,been): return True
					if len(args)>3 and isLinkedbyParse(args[3],v1,word_props,equalities,been): return True
				elif i2==1:
					if isLinkedbyParse(args[0],v1,word_props,equalities,been): return True
					if isLinkedbyParse(args[2],v1,word_props,equalities,been): return True
					if len(args)>3 and isLinkedbyParse(args[3],v1,word_props,equalities,been): return True
				elif i2==2:
					if isLinkedbyParse(args[0],v1,word_props,equalities,been): return True
					if isLinkedbyParse(args[1],v1,word_props,equalities,been): return True
					if len(args)>3 and isLinkedbyParse(args[3],v1,word_props,equalities,been): return True
				elif i2==3:
					if isLinkedbyParse(args[0],v1,word_props,equalities,been): return True
					if isLinkedbyParse(args[1],v1,word_props,equalities,been): return True
					if isLinkedbyParse(args[2],v1,word_props,equalities,been): return True

	return False

def extract_CM_mapping(id,inputString,DESCRIPTION):
	#print inputString
	targets = dict()	
	subtargets = dict()
	subsubtargets = dict()
	sources = dict()
	subsources = dict()
	mappings = []
	roles = []
	word_props = []
	equalities = defaultdict(dict)

	prop_pattern = re.compile('([^\(]+)\(([^\)]+)\)')
	
	propositions = inputString.split(' ^ ')
	prop_list = []
	for item in propositions:
		prop_match_obj = prop_pattern.match(item)
		if prop_match_obj:
			prop_name = prop_match_obj.group(1)
			arg_str = prop_match_obj.group(2)
			args = arg_str.split(',')

			if prop_name.startswith('T#'):
				if not targets.has_key(prop_name[2:]): targets[prop_name[2:]] = []
				targets[prop_name[2:]].append(args)
			elif prop_name.startswith('TS#'):
				if not subtargets.has_key(prop_name[3:]): subtargets[prop_name[3:]] = []
				subtargets[prop_name[3:]].append(args)
			elif prop_name.startswith('TSS#'):
				if not subsubtargets.has_key(prop_name[4:]): subsubtargets[prop_name[4:]] = []
				subsubtargets[prop_name[4:]].append(args)
			elif prop_name.startswith('S#'):
				if not sources.has_key(prop_name[2:]): sources[prop_name[2:]] = []
				sources[prop_name[2:]].append(args)
			elif prop_name.startswith('SS#'):
				if not subsources.has_key(prop_name[3:]): subsources[prop_name[3:]] = []
				subsources[prop_name[3:]].append(args)
			elif prop_name.startswith('M#'):
				mappings.append((prop_name[2:],args))
			elif prop_name.startswith('R#'):
				pass
			elif prop_name.startswith('I#'):
				pass
			elif prop_name == '=':
				for i in range(len(args)):
					arg1 = args[i]
					j = i + 1
					while j < len(args):
						arg2 = args[j]  
						equalities[arg1][arg2]=1
						equalities[arg2][arg1]=1
						j += 1
			else:
				#print json.dumps((prop_name,args), ensure_ascii=False) 
				if prop_name == 'equal':
					equalities[args[1]][args[2]]=1
					equalities[args[2]][args[1]]=1
				else: word_props.append((prop_name,args))

	#print json.dumps(sources, ensure_ascii=False)

	target_strucs = createDStruc(subtargets,subsubtargets)
	source_strucs = createDStruc(sources,subsources)

	output_struct_item = {}
	output_struct_item["id"] = id
	output_struct_item["isiDescription"] = DESCRIPTION
	output_struct_item["targetConceptDomain"] = "ECONOMIC_INEQUALITY"

	explanationAppendix = "\n%%BEGIN_CM_LIST\n"

	CMlinked = ''
	CMunlinked = ''

	for targetS in target_strucs:
		tV = collectVars(target_strucs,targetS)

		Tstrings = []

		for targ in target_strucs[targetS]: 
			if len(target_strucs[targetS][targ])==0: 
				Tstrings.append('ECONOMIC_INEQUALITY,' + targetS + ',' + targetS)
			else: 		
				for (tsubd,tsubarg) in target_strucs[targetS][targ]:
					Tstrings.append('ECONOMIC_INEQUALITY,' + targetS + ',' + tsubd)

		for sourceS in source_strucs:
			sV = collectVars(source_strucs,sourceS)
			linked = False
			for tv in tV:
				for sv in sV:
					if isLinkedbyParse(tv,sv,word_props,equalities,[]):
						linked = True
						break
				if linked: break

			Sstrings = []
			for sarg in source_strucs[sourceS]:
				if len(source_strucs[sourceS][sarg])==0:
					Sstrings.append(','+sourceS+',-')
				else:
					for (ssubd,ssubarg) in source_strucs[sourceS][sarg]:
						Sstrings.append(','+sourceS+','+ssubd)

			for ts in Tstrings:
				for ss in Sstrings:
					explanationAppendix += ts+ss
					if linked: 
						explanationAppendix += ',0.9\n'
						CMlinked = ts+ss
					else: 
						explanationAppendix += ',0.3\n'
						CMunlinked = ts+ss

	explanationAppendix+="%%END_CM_LIST"

	output_struct_item['isiAbductiveExplanation'] = inputString + explanationAppendix

	bestCM = CMlinked
	if len(bestCM)==0: bestCM = CMunlinked

	if len(bestCM)==0:
		output_struct_item["targetConceptDomain"] = ''
		output_struct_item["targetFrame"] = ''
		output_struct_item["targetConceptSubDomain"] = ''
		output_struct_item["sourceFrame"] = ''
		output_struct_item["sourceConceptSubDomain"] = ''
		output_struct_item['annotationMappings'] = []
	else:
		data = bestCM.split(',')
		output_struct_item["targetConceptDomain"] = 'ECONOMIC_INEQUALITY'
		output_struct_item["targetFrame"] = data[1]
		output_struct_item["targetConceptSubDomain"] = data[2]
		output_struct_item["sourceFrame"] = data[3]
		if data[4]=='-': output_struct_item["sourceConceptSubDomain"] = ''
		else: output_struct_item["sourceConceptSubDomain"] = data[4]

		targetArgs = dict()
		if subtargets.has_key(data[1]):
			for args in subtargets[data[1]]:
				targetArgs[args[0]]=1
		if subsubtargets.has_key(data[2]):
			for args in subsubtargets[data[2]]:
				targetArgs[args[0]]=1

		sourceArgs = dict()
		if sources.has_key(data[3]):
			for args in sources[data[3]]:
				sourceArgs[args[0]]=1
		if subsources.has_key(data[4]):
			for args in subsources[data[4]]:
				sourceArgs[args[0]]=1

		targetWords = wordStr2print(targetArgs,word_props,equalities)
		sourceWords = wordStr2print(sourceArgs,word_props,equalities)

		mapping_str = wordStr2print_Mapping(mappings,word_props,equalities)

		annotationMappings_struc = dict()
		annotationMappings_struc['explanation'] = mapping_str
		annotationMappings_struc['target'] = targetWords
		annotationMappings_struc['source'] = sourceWords
		annotationMappings_struc['targetInLm'] = False
		annotationMappings_struc['sourceInLm'] = False

		output_struct_item['annotationMappings'] = [annotationMappings_struc]
	

	# #print json.dumps(output_struct_item, ensure_ascii=False)

	return output_struct_item
