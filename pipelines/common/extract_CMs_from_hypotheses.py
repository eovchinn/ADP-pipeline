#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
from collections import defaultdict
import json

def wordStr2print(labeledProps,WordProps,Equalities):
	# remove duplicates
	no_duplicates_labeledProps = []
	for (propName,args) in labeledProps:
		found = False
		for (propName2,args2) in no_duplicates_labeledProps:		
			if propName2 == propName:
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

	output_str = ''
	for (propName,args) in no_duplicates_labeledProps:
		output_str += ', ' + propName + '['
		words_str = ''
		for arg in args:
			words = findWords(arg,WordProps,Equalities)
			words_str += '; ' + words


		output_str += words_str[2:] + ']' 

	#print json.dumps(output_str[2:], ensure_ascii=False)
	return output_str[2:]

def findWords(ARG,WordProps,Equalities):
	all_args = []
	if Equalities.has_key(ARG): all_args = Equalities[ARG].keys()

	all_args.append(ARG)

	output_str = ''
	for arg in all_args:
		if not arg.startswith('_') and not arg.startswith('u'):
			for (propName,args) in WordProps:
				if arg == args[0] and (propName.endswith('-vb') or propName.endswith('-rb') or propName.endswith('-adj')):
					output_str += ', ' + propName
				elif arg ==args[1] and (propName.endswith('-nn') or propName.endswith('-adj')):
					output_str += ', ' + propName
	if len(output_str)>0:
		return output_str[2:]
	return ARG		

def extract_CM_mapping(id,inputString):
	#print inputString
	targetsN = []	
	targetsE = []
	subtargetsN = []
	subtargetsE = []
	sourcesN = []
	sourcesE = []
	subsourcesN = []
	subsourcesE = []
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

			if prop_name.startswith('TN#'):
				targetsN.append((prop_name[3:],args))
			elif prop_name.startswith('TE#'):
				targetsE.append((prop_name[3:],args))
			elif prop_name.startswith('TSN#'):
				subtargetsN.append((prop_name[4:],args))
			elif prop_name.startswith('TSE#'):
				subtargetsE.append((prop_name[4:],args))
			elif prop_name.startswith('SN#'):
				sourcesN.append((prop_name[3:],args))
			elif prop_name.startswith('SE#'):
				sourcesE.append((prop_name[3:],args))
			elif prop_name.startswith('SSN#'):
				subsourcesN.append((prop_name[4:],args))
			elif prop_name.startswith('SSE#'):
				subsourcesE.append((prop_name[4:],args))
			elif prop_name.startswith('M#'):
				mappings.append((prop_name[2:],args))
			elif prop_name.startswith('R#'):
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
				word_props.append((prop_name,args))

	#print word_props
	output_struct_item = {}
	output_struct_item["id"] = id
	
	output_struct_item["isiTargetDomainNativeLanguage"] = wordStr2print(targetsN,word_props,equalities)
	output_struct_item["isiTargetSubdomainNativeLanguage"] = wordStr2print(subtargetsN,word_props,equalities)
	output_struct_item["isiSourceDomainNativeLanguage"] = wordStr2print(sourcesN,word_props,equalities)
	output_struct_item["isiSourceSubdomainNativeLanguage"] = wordStr2print(subsourcesN,word_props,equalities)
	output_struct_item["isiTargetDomainEnglish"] = wordStr2print(targetsE,word_props,equalities)
	output_struct_item["isiTargetSubdomainEnglish"] = wordStr2print(subtargetsE,word_props,equalities)
	output_struct_item["isiSourceDomainEnglish"] = wordStr2print(sourcesE,word_props,equalities)
	output_struct_item["isiSourceSubdomainEnglish"] = wordStr2print(subsourcesE,word_props,equalities)

	if len(targetsE)>0 and len(sourcesE)>0:
		output_struct_item["isiMetaphorConfirmed"] = 'YES'
		output_struct_item["isiTargetSourceMapping"] = wordStr2print(mappings,word_props,equalities)
	else:
		output_struct_item["isiMetaphorConfirmed"] = 'NO'
		output_struct_item["isiTargetSourceMapping"] = ''

	#print json.dumps(output_struct_item, ensure_ascii=False)
	return output_struct_item
