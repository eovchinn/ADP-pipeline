#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
from collections import defaultdict
import json

def removeDuplicates(labeledProps,Equalities):
	no_duplicates_labeledProps = []
	for (propName,args) in labeledProps:
		found = False
		for (propName2,args2) in no_duplicates_labeledProps:		
			if propName2 == propName and len(args)==len(args2):
				argsEqual = True
				for i in range(len(args)):					
					if args[i] == args2[i]: pass
					elif Equalities.has_key(args[i]) and Equalities[args[i]].has_key(args2[i]): pass
					elif Equalities.has_key(args2[i]) and Equalities[args2[i]].has_key(args[i]): pass
					else:
						argsEqual = False
						break
				if argsEqual:
					found = True
					break
		if not found:
			no_duplicates_labeledProps.append((propName,args))
	#print json.dumps(no_duplicates_labeledProps, ensure_ascii=False)
	return no_duplicates_labeledProps

def wordStr2print(labeledProps,WordProps,Equalities):
	domain2words = dict()
	for (propName,args) in labeledProps:
		words_str = ''
		if len(args)>0:
			words_str = findWords(args[0],WordProps,Equalities,False)
		if len(words_str)>0:
			if not domain2words.has_key(propName): domain2words[propName] = words_str
			else: domain2words[propName] += ',' + words_str
	
	output_str = ''		
	for propName in domain2words.keys():
		output_str += ',' + propName + '[' + domain2words[propName] + ']'
	
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
				elif len(args)>1 and arg ==args[1] and propName.endswith('-nn'):
					if propName.endswith('-adj'): output_str += ',' + propName[:-4]
					else: output_str += ',' + propName[:-3]
	if len(output_str)>0:
		return output_str[1:]

	if isMapping:	return ARG		
	return ''

def printPropNames(Props):
	output_str = ''
	been = dict()

	for (propName,args) in Props:
		if not been.has_key(propName):
			output_str += ', ' + propName
			been[propName] = 1
	return output_str[2:]

def extract_CM_mapping(id,inputString,DESCRIPTION):
	#print inputString
	targets = []	
	subtargets = []
	sources = []
	subsources = []
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
				targets.append((prop_name[2:],args))
			elif prop_name.startswith('TS#'):
				subtargets.append((prop_name[3:],args))
			elif prop_name.startswith('S#'):
				sources.append((prop_name[2:],args))
			elif prop_name.startswith('SS#'):
				subsources.append((prop_name[3:],args))
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
				word_props.append((prop_name,args))

	#remove duplicates
	#targets = removeDuplicates(targets,equalities)
	#subtargets = removeDuplicates(subtargets,equalities)
	#sources = removeDuplicates(sources,equalities)
	#subsources = removeDuplicates(subsources,equalities)
	mappings = removeDuplicates(mappings,equalities)

	output_struct_item = {}
	output_struct_item["id"] = id
	output_struct_item["isiDescription"] = DESCRIPTION

	output_struct_item["targetConceptDomain"] = printPropNames(targets)
	output_struct_item["targetConceptSubDomain"] = printPropNames(subtargets)

	output_struct_item["sourceFrame"] = printPropNames(sources)
	output_struct_item["sourceConceptSubDomain"] = printPropNames(subsources)#

	output_struct_item["targetFrame"] = output_struct_item["targetConceptSubDomain"]
	
	targetWords = wordStr2print(targets,word_props,equalities)
	subtargetWords = wordStr2print(subtargets,word_props,equalities)
	if len(targetWords)>0 and len(subtargetWords)>0: targetWords += ',' + subtargetWords
	else: targetWords += subtargetWords

	sourceWords = wordStr2print(sources,word_props,equalities)
	subsourceWords = wordStr2print(subsources,word_props,equalities)
	if len(sourceWords)>0 and len(subsourceWords)>0: sourceWords += ',' + subsourceWords
	else: sourceWords += subsourceWords

	mapping_str = wordStr2print_Mapping(mappings,word_props,equalities)

	output_struct_item["targetFrameElementsSentence"] = targetWords
	output_struct_item["sourceFrameElementsSentence"] = sourceWords

	annotationMappings_struc = dict()
	annotationMappings_struc['explanation'] = mapping_str
	annotationMappings_struc['target'] = targetWords
	annotationMappings_struc['source'] = sourceWords
	annotationMappings_struc['targetInLm'] = False
	annotationMappings_struc['sourceInLm'] = False

	output_struct_item['annotationMappings'] = [annotationMappings_struc]
	output_struct_item['isiAbductiveExplanation'] = mapping_str

	#if len(targets)>0 and len(sources)>0:
	#	output_struct_item["isiMetaphorConfirmed"] = 'YES'
	#	output_struct_item["isiTargetSourceMapping"] = wordStr2print_Mapping(mappings,word_props,equalities)
	#else:
	#	output_struct_item["isiMetaphorConfirmed"] = 'NO'
	#	output_struct_item["isiTargetSourceMapping"] = ''

	#print json.dumps(output_struct_item, ensure_ascii=False)
	return output_struct_item
