#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
from collections import defaultdict
import json

SSforS = {
'ANIMAL': 'ACTION', 
'BODY_OF_WATER': 'MOVEMENT', 
'CONFINEMENT': 'EXIT',
'ENSLAVEMENT': 'OPRESSION',
'MAZE': 'OBSTRUCTION',
'PARASITE': 'DESTRUCTUVE_BEING',
'PHYSICAL_BURDEN': 'RELIEF',
'PHYSICAL_LOCATION': 'DEFINED_REGION',
'DARKNESS': 'DARK_END_OF_RANGE_OF_DARKNESS_LIGHT',
'LOW_POINT': 'MOVEMENT_DOWNWARD',
'BUILDING': 'CREATION_DESTRUCTION',
'MEDICINE': 'ADMINISTRATION',
'MORAL_DUTY': 'REMUNERATION',
'VERTICAL_SCALE': 'MOVEMENT_ON_THE_SCALE',
'DESTROYER': 'DESTRUCTIVE_FORCE',
'ENABLER': 'LUBRICANT',
'OBESITY': 'EXCESS_CONSUMPTION',
'RESOURCE': 'QUANTITY_SIZE',
'VISION': 'SEEING',
'HIGH_POINT': 'TOP_OF_ECONOMIC_SCALE',
'LIGHT': 'LIGHT_END_OF_RANGE_OF_DARKNESS_LIGHT',
'BLOOD_SYSTEM': 'MOVEMENT',
'CROP': 'PLANTING',
'MOVEMENT': 'MOVEMENT',
'FOOD': 'CONSUMPTION',
'GAME': 'ACTIONS',
'PLANT': 'CHANGE_OF_STATE',
'PORTAL': 'MEANS_OF_ENTRY',
'MOVEMENT_ON_A_VERTICAL_SCALE': 'MOVEMENT',
'COMPETITION': 'COMPONENT',
'HUMAN_BODY': 'COMPONENT',
'MOVEMENT': 'MOVEMENT'}

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

def collectVars(struc,superkey,equalities):
	output = []

	for arg in struc[superkey]:
		if not arg.startswith('_') and not arg in output: 
			output.append(arg)
			if equalities.has_key(arg):
				for a in equalities[arg]: output.append(a)
		for (subd,subarg) in struc[superkey][arg]:
			if not subarg.startswith('_') and not subarg in output: 
				output.append(subarg)
				if equalities.has_key(subarg):
					for a in equalities[subarg]: output.append(a)
	return output

def collectVars2(struc,domain,subdomain):
	output = dict()

	for arg in struc[domain]:
		if not arg.startswith('_'): 
			output[arg]=1

		for (subd,subarg) in struc[domain][arg]:
			if not subarg.startswith('_'): 
				output[subarg]=1

	return output

def isLinkedbyParse(v1,v2,word_props,equalities,input_been,pathlength):
	if v1==v2: return pathlength

	pathlength += 1
	if pathlength == 9: return pathlength

	been = list(input_been)
	if (v1,v2) in been: return 9
	been.append((v1,v2))
	been.append((v2,v1))

	#print (v1,v2,pathlength)

	#if equalities.has_key(v1) and equalities[v1].has_key(v2): return 2

	nbrs = []
	for (propName,args) in word_props:
		if v1 in args:
			if v2 in args: return pathlength

			for a in args:
				if a!=v1: nbrs.append(a)

	pl = 9
	for n in nbrs:
		npl = isLinkedbyParse(n,v2,word_props,equalities,been,pathlength)
		if npl<pl: pl = npl
	return pl


def extract_CM_mapping(id,inputString,DESCRIPTION,LCCannotation):
	targets = dict()	
	subtargets = dict()
	subsubtargets = dict()
	sources = dict()
	subsources = dict()
	mappings = []
	roles = []
	word_props = []
	equalities = defaultdict(dict)

	sourceTask = False
	if LCCannotation:
		if "sourceFrame" in LCCannotation and "targetFrame" in LCCannotation and "targetConceptSubDomain" in LCCannotation:
			if LCCannotation["sourceFrame"] and len(LCCannotation["sourceFrame"])>0:
				if LCCannotation["targetFrame"] and len(LCCannotation["targetFrame"])>0:
					if LCCannotation["targetFrame"] == 'DEBT':
						LCCannotation["targetFrame"] = 'POVERTY'
					elif LCCannotation["targetFrame"] == 'MONEY':
						LCCannotation["targetFrame"] = 'WEALTH'
					if LCCannotation["targetConceptSubDomain"] and len(LCCannotation["targetConceptSubDomain"])>0:
						sourceTask = True

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
				dname = prop_name[3:]
				if not sourceTask or dname == LCCannotation["targetFrame"]:
					if not subtargets.has_key(dname): subtargets[dname] = []
					subtargets[dname].append(args)
			elif prop_name.startswith('TSS#'):
				dname = prop_name[4:]
				if not sourceTask or dname == LCCannotation["targetConceptSubDomain"]:
					if not subsubtargets.has_key(dname): subsubtargets[dname] = []
					subsubtargets[dname].append(args)
			elif prop_name.startswith('S#'):
				dname = prop_name[2:]
				if not sourceTask or dname == LCCannotation["sourceFrame"]:
					if not sources.has_key(dname): sources[dname] = []
					sources[dname].append(args)
			elif prop_name.startswith('SS#'):
				ss_data = prop_name[3:].split('%')
				if len(ss_data)>1: prop_name = ss_data[1]
				else: prop_name = ss_data[0]

				if not subsources.has_key(prop_name): subsources[prop_name] = []
				subsources[prop_name].append(args)
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
			elif prop_name == '!=': continue
			elif prop_name == 'equal':
				equalities[args[1]][args[2]]=1
				equalities[args[2]][args[1]]=1
			else: word_props.append((prop_name,args))

	#print json.dumps(subtargets, ensure_ascii=False)
	#print json.dumps(sources, ensure_ascii=False)
	#print json.dumps(subsources, ensure_ascii=False)
	#print json.dumps(word_props, ensure_ascii=False)
	#exit(0)

	for el1 in equalities.keys():
		for el2 in equalities[el1].keys():
			for el3 in equalities[el2].keys():
				if el1 != el3:
					equalities[el1][el3]=1
					equalities[el3][el1]=1

	target_strucs = createDStruc(subtargets,subsubtargets)
	source_strucs = createDStruc(sources,subsources)

	#print json.dumps(target_strucs, ensure_ascii=False)
	#print json.dumps(source_strucs, ensure_ascii=False)
	#print json.dumps(equalities, ensure_ascii=False)
	#exit(0)

	output_struct_item = {}
	if not LCCannotation: output_struct_item["id"] = id
	output_struct_item["isiDescription"] = DESCRIPTION
	output_struct_item["targetConceptDomain"] = "ECONOMIC_INEQUALITY"	

	explanationAppendix = "\n%%BEGIN_CM_LIST\n"
	bestCM = ''
	bestlink = 0

	Tdomains = []
	Sdomains = []

	for targetS in target_strucs:

		tV = collectVars(target_strucs,targetS,equalities)
		Tdomains = []

		for targ in target_strucs[targetS]: 			
			if len(target_strucs[targetS][targ])==0 and (targetS,targetS) not in Tdomains: 
				Tdomains.append((targetS,targetS))
			else: 		
				for (tsubd,tsubarg) in target_strucs[targetS][targ]:
					if (targetS,tsubd) not in Tdomains: Tdomains.append((targetS,tsubd))

		#print "Tdomans:"
		#print json.dumps(Tdomains, ensure_ascii=False)
		#print json.dumps(tV, ensure_ascii=False)
		
		Sdomains = []
		for sourceS in source_strucs:
			for sarg in source_strucs[sourceS]:
				for (ssubS,ssarg) in source_strucs[sourceS][sarg]:
					sargs = [ssarg]
					sargs += equalities[ssarg].keys()
					link = 9
					#print (sourceS,ssubS,sargs)
					for tv in tV:
						for sv in sargs:
							newlink = isLinkedbyParse(tv,sv,word_props,equalities,[],0)
							#print "%s,%s,%s,%s,%s,%s" % (targetS,sourceS,ssubS,tv,sv,newlink)
							if newlink<2:
								link=newlink
								break
							elif newlink<link: link=newlink
						if link<2: break
					Sdomains.append((sourceS,ssubS,(1-0.05-0.1*link)))
					#print "%s,%s,%s" % (sourceS,ssubS,(1-0.05-0.1*link))
					#exit(0)

					for (t,ts) in Tdomains:
						for (s,ss,c) in Sdomains:
								explanationAppendix += "ECONOMIC_INEQUALITY,%s,%s,%s,%s,%s\n" % (t,ts,s,ss,c)
								if c>bestlink:
									bestlink = c
									bestCM = "ECONOMIC_INEQUALITY,%s,%s,%s,%s,%s\n" % (t,ts,s,ss,c)

	#print 'BEST: ' + bestCM
	#exit(0)

	if len(Tdomains)==0 or len(Sdomains)==0:
		if len(Tdomains)==0:
			if sourceTask:
				Tdomains.append((LCCannotation["targetFrame"],LCCannotation["targetConceptSubDomain"]))
			else:
				Tdomains.append(('POVERTY','POVERTY'))

			if len(source_strucs)>0:
				for sourceS in source_strucs:
					if sourceTask and sourceS != LCCannotation["sourceFrame"]: continue

					for sarg in source_strucs[sourceS]:
						for (ssubS,ssarg) in source_strucs[sourceS][sarg]:
							Sdomains.append((sourceS,ssubS,0.001))

		if len(Sdomains)==0:
			if sourceTask:
				if SSforS.has_key(LCCannotation["sourceFrame"]):
					Sdomains.append((LCCannotation["sourceFrame"],SSforS[LCCannotation["sourceFrame"]],0.001))
				else:
					Sdomains.append((LCCannotation["sourceFrame"],'TYPE',0.001))
			else:
				Sdomains.append(('STRUGGLE','TYPE',0.001))

		for (t,ts) in Tdomains:
			for (s,ss,c) in Sdomains:
				explanationAppendix += "ECONOMIC_INEQUALITY,%s,%s,%s,%s,%s\n" % (t,ts,s,ss,c)
				bestCM = "ECONOMIC_INEQUALITY,%s,%s,%s,%s,%s\n" % (t,ts,s,ss,c)


	explanationAppendix += "%%END_CM_LIST"

	output_struct_item['isiAbductiveExplanation'] = inputString + explanationAppendix.encode("utf-8")
	output_struct_item["targetConceptDomain"] = 'ECONOMIC_INEQUALITY'
	data = bestCM.split(',')
	output_struct_item["targetFrame"] = data[1]
	output_struct_item["targetConceptSubDomain"] = data[2]
	output_struct_item["sourceFrame"] = data[3]
	if data[4]=='-': output_struct_item["sourceConceptSubDomain"] = 'TYPE'
	else: output_struct_item["sourceConceptSubDomain"] = data[4]

	targetArgs = dict()
	sourceArgs = dict()

	targetArgs = collectVars2(target_strucs,data[1],data[2])
	sourceArgs = collectVars2(source_strucs,data[3],data[4])

	targetWords = wordStr2print(targetArgs,word_props,())
	sourceWords = wordStr2print(sourceArgs,word_props,())

	mapping_str = wordStr2print_Mapping(mappings,word_props,equalities)

	annotationMappings_struc = dict()
	annotationMappings_struc['explanation'] = mapping_str
	annotationMappings_struc['target'] = targetWords
	annotationMappings_struc['source'] = sourceWords
	if len(targetWords)>0: annotationMappings_struc['targetInLm'] = True
	else: annotationMappings_struc['targetInLm'] = False
	if len(sourceWords)>0: annotationMappings_struc['sourceInLm'] = True
	else: annotationMappings_struc['sourceInLm'] = False

	output_struct_item['annotationMappings'] = [annotationMappings_struc]

	#print json.dumps(output_struct_item, ensure_ascii=False)

	return output_struct_item
