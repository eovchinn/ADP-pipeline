#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
from collections import defaultdict
import json
import nltk
from nltk.tokenize import word_tokenize

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


# find index of SubStr in MainStr
def findIndexes(SubStr,MainStr):
	if len(SubStr)==0: return []

	inds = []
	ss_toks=nltk.word_tokenize(SubStr.rstrip().lower())
	ms_toks=nltk.word_tokenize(MainStr.rstrip().lower())

	#print ss_toks
	#print ms_toks

	for mi, mt in enumerate(ms_toks):
		if ss_toks[0] == mt and len(ms_toks)>=mi+len(ss_toks)-1:
			inds.append(mi)
			found = True
			if len(ss_toks)>1:
				for si in range(1,len(ss_toks)):
					if ss_toks[si] != ms_toks[mi+si]:
						found = False
						break
					else:
						inds.append(mi+si)
			if found:
				#print inds
				return inds
			else: 
				inds = []

	return inds

# process parse output and generate index->argument dict
def extractWordsIds(parse):
	Wids = dict()
	obs_pattern = re.compile('\(([^\s\()]+)([^:\()]+):[^:]+:[^:]+:\[([\d,]+)\]\)')

	snumb = 1

	for match in obs_pattern.finditer(parse):
		pname = match.group(1)
		args = match.group(2).strip().split()
		pids = match.group(3).split(',')

		for pid in pids:
			if not pid.startswith(str(snumb)):
				snumb += 1
			tid = int(pid) - snumb * 1000

			if pname.endswith('-vb') or pname.endswith('-rb') or pname.endswith('-adj') and len(args)>0:
				Wids[tid] = [args[0]] 
			elif pname.endswith('-nn') and len(args)>1: 
				Wids[tid] = [args[0],args[1]]

	#print json.dumps(Wids, ensure_ascii=False)
	return Wids

# find prop arguments for input IDs
def findArgs(inputIDs,wordIDs):
	oArgs = []

	for iid in inputIDs:
		wid = iid+1
		if wordIDs.has_key(wid):
			oArgs += wordIDs[wid]

	#print json.dumps(oArgs, ensure_ascii=False)
	return oArgs

def wordStr2print(Args,WordProps,Equalities):
	output_str = ''

	words = []
	for arg in Args:
		newwords = findWords(arg,WordProps,Equalities,False)
		for word in newwords:
			if not word in words: 
				words.append(word)

	for word in words:
			output_str += word + ','
			
	if len(output_str)>0: return output_str[:-1]
	return ''

def wordStr2print_Mapping(mappings,WordProps,Equalities):
	output_str = ''

	for propName in mappings.keys():
		words = []

		for args in mappings[propName]:	
			#for arg in args:	
			#output only first ARG instead of all
			newwords = findWords(args[0],WordProps,Equalities,True)
			for word in newwords:
				if not word in words: words.append(word)

		output_str += ', ' + propName + '['
		for word in words:
			output_str += word + ','

		output_str = output_str[:-1] + ']' 

	#print json.dumps(output_str[2:], ensure_ascii=False)
	return output_str[2:]

def findWords(ARG,WordProps,Equalities,isMapping):
	all_args = []
	if isMapping and Equalities.has_key(ARG): all_args = Equalities[ARG].keys()

	all_args.append(ARG)

	words = []
	for arg in all_args:
		if not arg.startswith('_') and not arg.startswith('u'):
			for (propName,args) in WordProps:
				if arg == args[0] and (propName.endswith('-vb') or propName.endswith('-rb') or propName.endswith('-adj') or propName.endswith('-nn')):
					if propName.endswith('-adj'): 
						if not propName[:-4] in words: words.append(propName[:-4])
					else: 
						if not propName[:-3] in words: words.append(propName[:-3])
				elif len(args)>1 and arg ==args[1] :
					if propName.endswith('-nn'): 
						if not propName[:-3] in words: words.append(propName[:-3])
					elif propName=='person': 
						if not 'person' in words: words.append('person')
				#TODO: enable when Boxer starts working correctly
				#elif propName=='subset-of' and arg==args[2] :
				#	output_str += ',' + findWords(args[1],WordProps,Equalities,isMapping)
	
	if len(words)==0 and isMapping: return [ARG]
		
	return words

def createDStruc(superD,subD,inputVars,checkVars):
	outputstrucs = defaultdict(dict)

	for superd in superD:
		for superArgs in superD[superd]:
			includeD = True
			if checkVars: 
				if not superArgs[0] in inputVars: 
					includeD = False
			
			if includeD and (not outputstrucs.has_key(superd) or not outputstrucs[superd].has_key(superArgs[0])): outputstrucs[superd][superArgs[0]] = []

			for subd in subD:
				for subArgs in subD[subd]:
					if len(subArgs)>1 and superArgs[0]==subArgs[1]:
						if checkVars:
							if subArgs[0] in inputVars:
								if not includeD:
									if not outputstrucs.has_key(superd) or not outputstrucs[superd].has_key(superArgs[0]): outputstrucs[superd][superArgs[0]] = []
									includeD = True
								outputstrucs[superd][superArgs[0]].append((subd,subArgs[0]))
						else: outputstrucs[superd][superArgs[0]].append((subd,subArgs[0]))

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

def filterMappings(BestArgs,mappings):
	bestMapping = dict()
	toremove = dict()

	for predName in mappings:
		for args in mappings[predName]:
			included = False
			for arg in args:
				if arg in BestArgs:
					included = True
					break
			if included:
				if not bestMapping.has_key(predName): bestMapping[predName] = []
				bestMapping[predName].append(args)
			else:
				if not toremove.has_key(predName): toremove[predName] = []
				toremove[predName].append(args)

	for predName in toremove:
		for args in toremove[predName]:
			included = False
			for arg in args:
				for predName2 in bestMapping:
					for args2 in bestMapping[predName2]:
						if arg in args2:
							included = True
							break
					if included: break
				if included: break
			if included:
				if not bestMapping.has_key(predName): bestMapping[predName] = []
				bestMapping[predName].append(args)

	return bestMapping

def transitive_closure(A):

	while True:
		newlink = False

		newA = defaultdict(dict)
		for x in A.keys():
			for y in A[x].keys():
				for z in A[y].keys():
					if x!=z and not A[x].has_key(z): 
						newA[x][z]=1
						newA[z][x]=1
						newlink = True

		if newlink:
			for x in newA.keys():
				for y in newA[x].keys():
					A[x][y]=1
		else:
			break

	return A

def extract_CM_mapping(sid,inputString,parse,DESCRIPTION,LCCannotation):
	targets = dict()	
	subtargets = dict()
	subsubtargets = dict()
	sources = dict()
	subsources = dict()
	mappings = dict()
	roles = []
	word_props = []
	equalities = defaultdict(dict)

	sourceTask = False
	if LCCannotation:
		if "sourceFrame" in LCCannotation and "targetFrame" in LCCannotation and "targetConceptSubDomain" in LCCannotation:
			if LCCannotation["sourceFrame"] and len(LCCannotation["sourceFrame"])>0:
				if LCCannotation["targetConceptSubDomain"] and len(LCCannotation["targetConceptSubDomain"])>0:
					if LCCannotation["targetConceptSubDomain"] == 'DEBT':
						LCCannotation["targetConceptSubDomain"] = 'POVERTY'
					elif LCCannotation["targetConceptSubDomain"] == 'MONEY':
						LCCannotation["targetConceptSubDomain"] = 'WEALTH'					
					if LCCannotation["targetFrame"] and len(LCCannotation["targetFrame"])>0:
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
				if args not in targets[prop_name[2:]]: targets[prop_name[2:]].append(args)
			elif prop_name.startswith('TS#'):
				dname = prop_name[3:]
				if not sourceTask or dname == LCCannotation["targetConceptSubDomain"]:
					if not subtargets.has_key(dname): subtargets[dname] = []
					if args not in subtargets[dname]: subtargets[dname].append(args)
			elif prop_name.startswith('TSS#'):
				dname = prop_name[4:]
				if not sourceTask or dname == LCCannotation["targetFrame"]:
					if not subsubtargets.has_key(dname): subsubtargets[dname] = []
					if args not in subsubtargets[dname]: subsubtargets[dname].append(args)
			elif prop_name.startswith('S#'):
				dname = prop_name[2:]
				if not sourceTask or dname == LCCannotation["sourceFrame"]:
					if not sources.has_key(dname): sources[dname] = []
					if args not in sources[dname]: sources[dname].append(args)
			elif prop_name.startswith('SS#'):
				ss_data = prop_name[3:].split('%')
				if len(ss_data)>1: prop_name = ss_data[1]
				else: prop_name = ss_data[0]

				if not subsources.has_key(prop_name): subsources[prop_name] = []
				if args not in subsources[prop_name]:  subsources[prop_name].append(args)
			elif prop_name.startswith('M#'):
				mname = prop_name[2:]
				if not mappings.has_key(mname): mappings[mname] = []
				if args not in mappings[mname]: mappings[mname].append(args)
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

	#print json.dumps(targets, ensure_ascii=False)
	#print json.dumps(subtargets, ensure_ascii=False)
	#print json.dumps(sources, ensure_ascii=False)
	#print json.dumps(subsources, ensure_ascii=False)
	#print json.dumps(word_props, ensure_ascii=False)
	#print json.dumps(mappings, ensure_ascii=False)
	#exit(0)

	#print json.dumps(equalities, ensure_ascii=False)

	# transitive closure of equalities
	equalities = transitive_closure(equalities)

	# find arguments for the input target and source words
	inputTargetArgs = []
	inputSourceArgs = []
	checkVars = False
	if LCCannotation and 'annotationMappings' in LCCannotation and len(LCCannotation['annotationMappings'])>0:
		firstAnn = LCCannotation['annotationMappings'][0]
		if 'target' in firstAnn and 'source' in firstAnn:
			checkVars = True
			inputSourceIds = findIndexes(firstAnn['source'],LCCannotation['linguisticMetaphor'])
			inputTargetIds = findIndexes(firstAnn['target'],LCCannotation['linguisticMetaphor'])

			# extract words with ids from parse
			Wids = extractWordsIds(parse)
			# find arguments for input and source target words
			inputTargetArgs = findArgs(inputTargetIds,Wids)
			inputSourceArgs = findArgs(inputSourceIds,Wids)
			
	#print json.dumps(inputTargetArgs, ensure_ascii=False)
	#print json.dumps(inputSourceArgs, ensure_ascii=False)

	target_strucs = createDStruc(subtargets,subsubtargets,inputTargetArgs,checkVars)
	source_strucs = createDStruc(sources,subsources,inputSourceArgs,checkVars)

	#print json.dumps(target_strucs, ensure_ascii=False)
	#print json.dumps(source_strucs, ensure_ascii=False)

	#print json.dumps(equalities, ensure_ascii=False)
	#exit(0)

	output_struct_item = {}
	if not LCCannotation: output_struct_item["sid"] = sid
	output_struct_item["isiDescription"] = DESCRIPTION
	output_struct_item["targetConceptDomain"] = "ECONOMIC_INEQUALITY"	

	bestCM = ''
	bestlink = 0

	Tdomains = []
	Sdomains = []

	CMs = dict()

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
		bestSVars = []
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
							if newlink<link: 
								link=newlink
								if newlink<2:
									break
						if link<2: break
					Sdomains.append((sourceS,ssubS,(1-0.05-0.1*link)))
					#print "%s,%s,%s" % (sourceS,ssubS,(1-0.05-0.1*link))
					#exit(0)

					for (t,ts) in Tdomains:
						for (s,ss,c) in Sdomains:
								#explanationAppendix += "ECONOMIC_INEQUALITY,%s,%s,%s,%s,%s\n" % (t,ts,s,ss,c)

								TSpair = "%s,%s,%s,%s" % (t,ts,s,ss)
								if CMs.has_key(TSpair):
									if CMs[TSpair] < c: CMs[TSpair] = c
								else: CMs[TSpair] = c

								if c>bestlink:
									bestlink = c
									bestCM = "%s,%s,%s,%s" % (t,ts,s,ss)

	#print 'BEST: ' + bestCM
	#exit(0)

	if len(Tdomains)==0 or len(Sdomains)==0:
		if len(Tdomains)==0:
			if sourceTask:
				Tdomains.append((LCCannotation["targetConceptSubDomain"],LCCannotation["targetFrame"]))
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
				#explanationAppendix += "ECONOMIC_INEQUALITY,%s,%s,%s,%s,%s\n" % (t,ts,s,ss,c)
				TSpair = "%s,%s,%s,%s" % (t,ts,s,ss)
				if CMs.has_key(TSpair):
					if CMs[TSpair] < c: CMs[TSpair] = c
				else: CMs[TSpair] = c
				bestCM = "%s,%s,%s,%s" % (t,ts,s,ss)

	#print bestCM

	explanationAppendix = "\n%%BEGIN_CM_LIST\n"
	for TSpair in CMs.keys():
		explanationAppendix += "ECONOMIC_INEQUALITY,%s,%s\n" % (TSpair,CMs[TSpair]) 
	explanationAppendix += "%%END_CM_LIST"

	output_struct_item['isiAbductiveExplanation'] = inputString + explanationAppendix.encode("utf-8")
	output_struct_item["targetConceptDomain"] = 'ECONOMIC_INEQUALITY'
	data = bestCM.split(',')
	output_struct_item["targetConceptSubDomain"] = data[0]
	output_struct_item["targetFrame"] = data[1]
	output_struct_item["sourceFrame"] = data[2]
	if data[3]=='-': output_struct_item["sourceConceptSubDomain"] = 'TYPE'
	else: output_struct_item["sourceConceptSubDomain"] = data[3]

	targetArgs = collectVars2(target_strucs,data[0],data[1])
	sourceArgs = collectVars2(source_strucs,data[2],data[3])

	mappings = filterMappings(targetArgs.keys()+sourceArgs.keys(),mappings)
	#print json.dumps(mappings, ensure_ascii=False)
	mapping_str = wordStr2print_Mapping(mappings,word_props,equalities)

	annotationMappings_struc = dict()
	annotationMappings_struc['explanation'] = mapping_str

	if not checkVars:
		targetWords = wordStr2print(targetArgs,word_props,())
		sourceWords = wordStr2print(sourceArgs,word_props,())
		annotationMappings_struc['target'] = targetWords
		annotationMappings_struc['source'] = sourceWords
		if len(targetWords)>0: annotationMappings_struc['targetInLm'] = True
		else: annotationMappings_struc['targetInLm'] = False
		if len(sourceWords)>0: annotationMappings_struc['sourceInLm'] = True
		else: annotationMappings_struc['sourceInLm'] = False

	output_struct_item['annotationMappings'] = [annotationMappings_struc]

	#print json.dumps(output_struct_item, ensure_ascii=False)

	return output_struct_item
