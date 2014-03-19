#!/usr/bin/python
# -*- coding: utf-8 -*-

import argparse
import json
import re

grow_set = set([u'THING-INCREASING', u'CAUSE-INCREASE-AMOUNT'])
game_set = set([u'GAME-STAKES', u'CAUSE-BINARY-OUTCOME'])
no_stakes_game_set = set([u'CAUSE-BINARY-OUTCOME'])
play_game_set = set([u'CAUSE-BINARY-OUTCOME',u'ATTEMPT-AGENT',u'CAUSE-ATTEMPT-POSITIVE-OUTCOME'])
play_set = set([u'ATTEMPT-AGENT',u'CAUSE-ATTEMPT-POSITIVE-OUTCOME'])
flow_set = set([u'LIQUID-THING', u'LIQUID-MOVE-FREELY'])
no_liquid_flow_set = set([u'LIQUID-MOVE-FREELY'])
no_agent_play_game_set = set([u'CAUSE-ATTEMPT-POSITIVE-OUTCOME', u'CAUSE-BINARY-OUTCOME'])
eradicate_set =set([u'THING-NOT-EXISTING', u'CAUSE-NOT-EXIST', u'THING-CAUSING-NOT-EXIST'])
no_agent_eradicate_set=set([u'THING-NOT-EXISTING', u'CAUSE-NOT-EXIST'])
taste_set =set([u'THING-BEING-EXPERIENCED', u'CAUSE-EXPERIENCE', u'THING-CAUSING-EXPERIENCE'])
no_agent_taste_set=set([u'THING-BEING-EXPERIENCED', u'CAUSE-EXPERIENCE'])
exit_abyss_set = set([u'THING-THAT-LIMITED-OPTIONS', u'CAUSE-INCREASE-OPTIONS', u'THING-THAT-STOPPED-FUNCTION', u'CAUSE-RESUME-FUNCTION'])
deep_abyss_set = set([u'CAUSE-SEVERE-NOT-FUNCTION',u'CAUSE-SEVERE-REDUCE-OPTIONS'])
harvest_crop_seed_set = set([u'CAUSE-OUTCOME-OF-ACTION', u'CAUSE-REALIZE-OUTCOME', u'PREPARATION-FOR-OUTCOME', u'THING-REALIZING',u'OUTCOME-OF-ACTION']) 
crop_outcome_set = set([u'CAUSE-OUTCOME-OF-ACTION',u'OUTCOME-OF-ACTION']) 
crop_set = set([u'CAUSE-OUTCOME-OF-ACTION']) 
victory_set = set([u'ACHIEVEMENT-OF-GOAL']) 
crime_set = set([u'AGAINST-SOCIETY-ACTION']) 
resource_set = set([u'CAUSE-FUNCTION']) 
terror_set = set([u'CAUSE-NOT-FUNCTION']) 
disease_set = set([u'CAUSE-NOT-FUNCTION','THING-NOT-FUNCTIONING']) 
drug_set = set([u'CAUSE-NOT-FUNCTION','CAUSE-BAD-JUDGEMENT']) 
addiction_set = set([u'CAUSE-NOT-FUNCTION','CAUSE-BAD-JUDGEMENT','CAUSE-OBSESSION']) 
medicine_set = set([u'CAUSE-PROBLEM-NOT-EXIST']) 
treatment_set = set([u'CAUSE-PROBLEM-NOT-EXIST','CAUSE-NOT-FUNCTION']) 
blood_set = set([u'CAUSE-FUNCTION', u'THING-FUNCTIONING'])
protect_set = set([u'CAUSE-ALLOW-FUNCTION', u'THING-ALLOWING',u'THING-FUNCTIONING'])
protection_set = set([u'CAUSE-ALLOW-FUNCTION'])
cost_set = set([u'CAUSE-DRAIN-RESOURCES', u'THING-DRAINING'])
price_set = set([u'THING-DESIRED', u'CAUSE-NEGATIVE-CONSEQUENCE-OF-DESIRED-THING'])
no_desire_price_set = set([u'CAUSE-NEGATIVE-CONSEQUENCE-OF-DESIRED-THING'])
pay_set = set([u'THING-DESIRED', u'CAUSE-NEGATIVE-CONSEQUENCE-OF-DESIRED-THING','CAUSE-EXCHANGE-NEGATIVE-POSITIVE'])
live_in_set = set([u'CAUSE-EXPERIENCE-SOMETHING',u'EXPERIENCER','THING-EXPERIENCED'])
rule_set = set([u'PROVIDE-CONTROL'])
head_set = set([u'INDICATE-IMPORTANCE'])
body_set = set([u'LARGE-AMOUNT',u'THING-LARGE-AMOUNT'])
hand_set = set([u'CAUSE-LOSE-SELF-CONTROL',u'THING-GAINING-CONTROL'])

def lm_category(log):
    lm_type = ''
    if re.search(u"^CAUSE-INCREASE-AMOUNT",log):
        lm_type = "cause-inc-am"
    elif re.search(u"^CAUSE-LOSE-SELF-CONTROL",log):
        lm_type = "cause-lose-control"
    elif re.search(u"^CAUSE-NOT-EXIST",log):
        lm_type = "cause-not-exist"
    elif re.search(u"^CAUSE-BAD-JUDGEMENT",log):
        lm_type = "cause-bad-judgement"
    elif re.search(u"^CAUSE-OBSESSION",log):
        lm_type = "cause-obsession"
    elif re.search(u"^CAUSE-EXPERIENCE",log):
        lm_type = "cause-experience"
    elif re.search(u"^CAUSE-PROBLEM-NOT-EXIST",log):
        lm_type = "cause-problem-not-exist"        
    elif re.search(u"^CAUSE-NOT-FUNCTION",log):
        lm_type = "cause-not-function"           
    elif re.search(u"^CAUSE-ALLOW-FUNCTION",log):
        lm_type = "cause-allow-function"           
    elif re.search(u"^CAUSE-FUNCTION",log):
        lm_type = "cause-function"           
    elif re.search(u"^CAUSE-RESUME-FUNCTION",log):
        lm_type = "cause-resume-function"   
    elif re.search(u"^CAUSE-INCREASE-OPTIONS",log):
        lm_type = "cause-increase-options"  
    elif re.search(u"^CAUSE-LIMIT-OPTIONS",log):
        lm_type = "cause-limit-options"          
    elif re.search(u"^CAUSE-DRAIN-RESOURCES",log):
        lm_type = "cause-drain-resources"          
    elif re.search(u"^CAUSE-BINARY-OUTCOME",log):
        lm_type = "cause-binary-outcome"          
    elif re.search(u"^CAUSE-ATTEMPT-POSITIVE-OUTCOME",log):
        lm_type = "cause-attempt-outcome"          


    elif re.search(u"^CAUSE-REALIZE-OUTCOME",log):
        lm_type = "cause-realize-outcome"
    elif re.search(u"^CAUSE-OUTCOME-OF-ACTION",log):
        lm_type = "cause-outcome"  
    elif re.search(u"^CAUSE-EXPERIENCE-SOMETHING",log):
        lm_type = "cause-experience"          
    elif re.search(u"^CAUSE-SEVERE-NOT-FUNCTION",log):
        lm_type = "cause-sev-not-function"  
    elif re.search(u"^CAUSE-SEVERE-REDUCE-OPTIONS",log):
        lm_type = "cause-sev-reduce-options"
    elif re.search(u"^CAUSE-NEGATIVE-CONSEQUENCE-OF-DESIRED-THING",log):
        lm_type = "cause-neg-consequence"        
    elif re.search(u"^CAUSE-EXCHANGE-NEGATIVE-POSITIVE",log):
        lm_type = "cause-exchange"        
             
    elif re.search(u"^PROVIDE-CONTROL",log):
        lm_type = "give-control"          
    elif re.search(u"^AGAINST-SOCIETY-ACTION",log):
        lm_type = "against-society-action"          
    elif re.search(u"^GAME-STAKES",log):
        lm_type = "game-stakes"          

    elif re.search(u"^THING-CAUSING-NOT-EXIST",log):
        lm_type = "agent-not-exist"
    elif re.search(u"^THING-CAUSING-EXPERIENCE",log):
        lm_type = "agent-experience"
    elif re.search(u"^THING-THAT-LIMITED-OPTIONS",log):
        lm_type = "agent-limit-options" 
    elif re.search(u"^THING-THAT-STOPPED-FUNCTION",log):
        lm_type = "agent-stop-function" 
    elif re.search(u"^THING-ALLOWING",log):
        lm_type = "agent-allow-function" 
    elif re.search(u"^THING-REALIZING",log):
        lm_type = "agent-realize"
    elif re.search(u"^THING-DRAINING",log):
        lm_type = "agent-drain"
    elif re.search(u"^ATTEMPT-AGENT",log):
        lm_type = "agent-attempt"


        
    elif re.search(u"^EXPERIENCER",log):
        lm_type = "patient-experience"        
    elif re.search(u"^THING-BEING-EXPERIENCED",log):
        lm_type = "thing-experience"
    elif re.search(u"^THING-INCREASING",log):
        lm_type = "patient-increase"
    elif re.search(u"^THING-FUNCTIONING",log):
        lm_type = "patient-function"
    elif re.search(u"^THING-NOT-FUNCTIONING",log):
        lm_type = "patient-not-function"
    elif re.search(u"^THING-NOT-EXISTING",log):
        lm_type = "patient-not-exist"
    elif re.search(u"^THING-DESIRED",log):
        lm_type = "patient-desire" 

    elif re.search(u"^THING-EXPERIENCED",log):
        lm_type = "experience-event" 
    elif re.search(u"^THING-GAINING-CONTROL",log):
        lm_type = "controller" 
 
    elif re.search(u"^OUTCOME-OF-ACTION",log):
        lm_type = "outcome"
    elif re.search(u"^PREPARATION-FOR-OUTCOME",log):
        lm_type = "preparation"

    elif re.search(u"^LIQUID-MOVE-FREELY",log):
        lm_type = "liquid-move"
    elif re.search(u"^LIQUID-THING",log):
        lm_type = "liquid"

    elif re.search(u"^ACHIEVEMENT-OF-GOAL",log):
        lm_type = "acheivement"

    elif re.search(u"^LARGE-AMOUNT",log):
        lm_type = "imply-large-amount"
    elif re.search(u"^INDICATE-IMPORTANCE",log):
        lm_type = "important"
    elif re.search(u"^THING-LARGE-AMOUNT",log):
        lm_type = "thing-large-amount"



    return lm_type


def prune_lm_list(lm_list,lm_type,target_lms,source_lms):
    source_lms.discard(u'person')
    if len(target_lms) > 1:
        target_lms.discard(u'person')
    if lm_type == "cause-neg-consequence":
        for dup in set(lm_list).difference(source_lms):
            lm_list.remove(dup)
    if lm_type == "cause-function":
        for dup in set(lm_list).difference(source_lms):
            lm_list.remove(dup)
    if lm_type == "cause-not-function":
        for dup in set(lm_list).difference(source_lms):
            lm_list.remove(dup)
    if lm_type == "give-control":
        for dup in set(lm_list).difference(source_lms):
            lm_list.remove(dup)
    if lm_type == "cause-binary-outcome":
        for dup in set(lm_list).difference(source_lms):
            lm_list.remove(dup)



def process_explanation(exp,s_id,lang,target_sub,target_lms,source_lms):
    logic_list = []
    lms = {}
    unexpressed = re.compile(u"x\d+")
    for e in exp:
        e = e.strip().rstrip("]")
        logic = e.split("[")[0]
        lm_type = lm_category(logic)
	if len(lm_type)==0: continue

        lm_list = e.split("[")[1].rstrip("]").split(",")
        logic_list.append(logic)
        prune_lm_list(lm_list,lm_type,target_lms,source_lms)
        for word in lm_list:
            if unexpressed.search(word):
                word = "some entity"

            lms[lm_type] = word
    logic_set = set(logic_list)  
    #print logic_set
    if logic_set == grow_set:
        print s_id
        if lang=='EN':
		print('"{}" denotes an increased amount of "{}"'.format(lms['cause-inc-an'],lms['patient-increase']))
	else:
		print lms['cause-inc-an'] + u' означает что увеличилось количество ' + lms['patient-increase']
    if logic_set == eradicate_set:
        print s_id
        if lang=='EN':        
        	print('"{}" denotes that "{}" causes "{}" to stop existing'.format(lms['cause-not-exist'],lms['agent-not-exist'],lms['patient-not-exist']))
	else:
		print lms['cause-not-exist'] + u' прекращает существование ' + lms['patient-not-exist']
    if logic_set == no_agent_eradicate_set and target_sub != "WEALTH":
        print s_id    
        if lang=='EN':    
        	print('"{}" denotes that there is an effort to stop the existence of "{}" '.format(lms['cause-not-exist'],lms['patient-not-exist']))
	else:
		print lms['cause-not-exist'] + u' означает что есть попытка избавиться от ' + lms['patient-not-exist']
    elif logic_set == no_agent_eradicate_set and target_sub == "WEALTH":
        print s_id    
        if lang=='EN':    
        	print('"{}" denotes that "{}" does not exist'.format(lms['cause-not-exist'],lms['patient-not-exist']))
	else:
		print lms['cause-not-exist'] + u' означает что есть попытка избавиться от ' + lms['patient-not-exist']
        
    #CROP
    if logic_set == harvest_crop_seed_set:
        print s_id
        if lang=='EN':      
        	print('"{}" denotes that "{}" was a preparation so that "{}" is realizing the outcome, "{}" in this case, of some action, which is denoted by "{}"'.format(lms['cause-realize-outcome'],lms['preparation'],lms['agent-realize'],lms['outcome'],lms['cause-outcome']))


    if logic_set == crop_outcome_set:
        print s_id
        if lang=='EN':      
        	print('"{}" denotes that "{}" is the outcome of some action'.format(lms['cause-outcome'],lms['outcome']))   
    if logic_set == crop_set:
        print s_id
	if lang=='EN':      
        	print('"{}" denotes that poverty is the outcome of some action'.format(lms['cause-outcome']))    
    #ABYSS
    if logic_set == deep_abyss_set:
        print s_id
	if lang=='EN':      
        	print('"{}" implies that the experiencer of poverty has severely limited options and cannot function'.format(lms['cause-sev-not-function']))
	else:
		print lms['cause-sev-not-function'] + u' означает, что тот, кто испытывает бедность, имеет очень ограниченные возможности и не может нормально фунционировать'
    if logic_set == exit_abyss_set:
        print s_id      
        if lang=='EN':      
        	print('"{}" denotes that "{}" had limited options, but options will increase; "{}" denotes that "{}" had caused something not to function, but functionality will resume'.format(lms['cause-increase-options'],lms['agent-limit-options'],lms['cause-resume-function'],lms['agent-stop-function']))    
	else:
		print lms['cause-increase-options'] + u' означает что возможности у ' + lms['agent-limit-options'] + u' ограничены; ' + lms['cause-resume-function'] + u' означает что ' + lms['agent-stop-function'] + u' вызвал ограничение каких-то функций, но эти функции возобновятся'        

    #PRICE
    if logic_set == price_set:
        print s_id
	if lang=='EN':      
        	print('"{}" implies that poverty is a negative consequence that must be accepted to attain "{}"'.format(lms['cause-neg-consequence'],lms['patient-desire']))  
	else:
		print lms['cause-neg-consequence'] + u' означает, что бедность - это негативные последствия достижения ' + lms['patient-desire']
    if logic_set == no_desire_price_set:
        print s_id
	if lang=='EN':      
        	print('"{}" implies that poverty is a negative consequence that must be accepted to attain some entity'.format(lms['cause-neg-consequence']))  
    #PAY
    if logic_set == pay_set:
        print s_id
	if lang=='EN':      
        	print('"{}" implies that poverty is a negative consequence that must be accepted to attain "{}"; "{}" implies that there is a willing exchange'.format(lms['cause-neg-consequence'],lms['patient-desire'],lms['cause-exchange']))  


    if logic_set == live_in_set:
        print s_id
	if lang=='EN':      
        	print('"{}" implies that "{}" experiences "{}"'.format(lms['cause-experience'],lms['patient-experience'],lms['experience-event'])) 
	else:
		print  lms['cause-experience'] + u' означает, что ' + lms['patient-experience'] + u' переживает ' + lms['experience-event']

    #RESOURCE
    if logic_set == resource_set:
        print s_id
	if lang=='EN':      
        	print('"{}" implies that money causes those who have it to function'.format(lms['cause-function']))  

    #BLOOD
    if logic_set == blood_set:
        print s_id
	if lang=='EN':      
        	print('"{}" implies that money causes "{}" to function'.format(lms['cause-function'],lms['patient-function']))  
	else:
		print lms['cause-function'] + u' означает, что деньги позволяют функционировать ' + lms['patient-function']
    #POWER
    if logic_set == rule_set:
        print s_id
	if lang=='EN':      
        	print('"{}" implies that money provides control'.format(lms['give-control'])) 
	else:
		print lms['give-control'] + u' означает, что деньги дают контроль '
    #COST
    if logic_set == cost_set:
        print s_id
	if lang=='EN':      
        	print('"{}" implies that "{}" is using up resources'.format(lms['cause-drain-resources'],lms['agent-drain']))  
    #TERROR
    if logic_set == terror_set:
        print s_id
	if lang=='EN':      
        	print('"{}" implies that poverty is causing some entity not to function'.format(lms['cause-not-function']))  

    #DISEASE
    if logic_set == disease_set:
        print s_id
	if lang=='EN':      
        	print('"{}" implies that poverty is causing "{}" not to function'.format(lms['cause-not-function'],lms['patient-not-function']))  

    #MEDICINE
    if logic_set == medicine_set:
        print s_id
	if lang=='EN':      
        	print('"{}" implies that there is something that can lessen the effects of poverty'.format(lms['cause-problem-not-exist']))  

    #TREATMENT
    if logic_set == treatment_set:
        print s_id
	if lang=='EN':      
        	print('"{}" implies that poverty causes some entity to not function; "{}" implies that there is something that can cause poverty to not exist'.format(lms['cause-not-function'],lms['cause-problem-not-exist']))  

    #CRIME
    if logic_set == crime_set:
        print s_id
	if lang=='EN':      
        	print('"{}" implies that poverty is a deliberate act that harms society'.format(lms['against-society-action']))

    #VICTORY
    if logic_set == victory_set:
        print s_id
	if lang=='EN':      
        	print('"{}" implies that some entity has acheived a goal'.format(lms['acheivement']))

    #BODY
    if logic_set == body_set:
        print s_id
	if lang=='EN':      
        	print('"{}" implies that there is a large amount of "{}"'.format(lms['imply-large-amount'],lms['thing-large-amount']))
	else:
		print lms['imply-large-amount'] + u' означает что есть большое количество ' + lms['thing-large-amount']

    #HAND
    if logic_set == hand_set:
        print s_id
	if lang=='EN':      
        	print('"{}" implies that someone has lost self-control due to the influence of "{}"'.format(lms['cause-lose-control'],lms['controller']))

    #HEAD
    if logic_set == head_set:
        print s_id
	if lang=='EN':      
        	print('"{}" implies that money has become an important factor'.format(lms['important']))

    #PROTECT
    if logic_set == protect_set:
        print s_id
	if lang=='EN':      
        	print('"{}" implies that "{}" allows "{}" to function'.format(lms['cause-allow-function'],lms['agent-allow-function'],lms['patient-function']))

    #PROTECTION
    if logic_set == protection_set:
        print s_id
	if lang=='EN':      
        	print('"{}" implies that the possessor of "{}" is able to function'.format(lms['cause-allow-function'],",".join(target_lms)))

    #HEAD
    if logic_set == head_set:
        print s_id
	if lang=='EN':      
        	print('"{}" implies that money has become an important factor'.format(lms['important']))

    #DRUG
    if logic_set == drug_set:
        print s_id
	if lang=='EN':      
        	print('"{}" implies that some entity has reduced functionality due to "{}"'.format(lms['cause-bad-judgement'],",".join(target_lms)))

    #ADDICTION
    if logic_set == addiction_set:
        print s_id
	if lang=='EN':      
        	print('"{}" implies that some entity has reduced functionality and is preoccupied with "{}"'.format(lms['cause-obsession'],",".join(target_lms)))

    #FLOW
    if logic_set == flow_set:
        print s_id
	if lang=='EN':      
        	print('"{}" implies that "{}" is available for transfer and use'.format(lms['liquid-move'],lms['liquid']))
	else:
		print lms['liquid-move'] + u' означает что ' + lms['liquid'] + u' может перемещаться и использоваться'

    #FLOW-NO-LIQUID
    if logic_set == no_liquid_flow_set:
        print s_id
	if lang=='EN':      
        	print('"{}" implies that some entity is available for transfer and use'.format(lms['liquid-move']))
	else:
		print lms['liquid-move'] + u' означает что некий объект может перемещаться и использоваться'

    #TASTE
    if logic_set == taste_set:
        print s_id
	if lang=='EN':      
        	print('"{}" implies that "{}" is experiencing "{}"'.format(lms['cause-experience'],lms['agent-experience'],lms['thing-experience']))

    #NO-AGENT-TASTE
    if logic_set == no_agent_taste_set:
        print s_id
	if lang=='EN':      
        	print('"{}" implies that some entity is experiencing "{}"'.format(lms['cause-experience'],lms['thing-experience']))

    #GAME
    if logic_set == game_set:
        print s_id
	if lang=='EN':      
        	print('"{}" implies that there are two possible outcomes, one positive and one negative, associated with the idea of "{}"'.format(lms['cause-binary-outcome'],lms['game-stakes']))
	else:
		print  lms['cause-binary-outcome'] + u' означает, что есть два возможных исхода: положительный и отрицательный, связанные с идеей' + lms['game-stakes'] 
        

    #GAME
    if logic_set == no_stakes_game_set:
        print s_id
	if lang=='EN':      
        	print('"{}" implies that there are two possible outcomes, one positive and one negative'.format(lms['cause-binary-outcome']))
	else:
		print  lms['cause-binary-outcome'] + u' означает, что есть два возможных исхода: положительный и отрицательный'

    #PLAY-GAME
    if logic_set == play_game_set:
        print s_id
	if lang=='EN':      
        	print('"{}" implies that there are two possible outcomes, one positive and one negative; "{}" implies that "{}" is attempting to achieve a positive outcome'.format(lms['cause-binary-outcome'],lms['cause-attempt-outcome'],lms['agent-attempt']))
	else:
		print  lms['cause-binary-outcome'] + u' означает, что есть два возможных исхода: положительный и отрицательный; ' + lms['cause-attempt-outcome'] + u' означает, что ' + lms['agent-attempt'] +  u' старается достичь положительного исхода'

    #PLAY
    if logic_set == play_set:
        print s_id
	if lang=='EN':      
        	print('"{}" implies that "{}" is attempting to achieve a positive outcome'.format(lms['cause-attempt-outcome'],lms['agent-attempt']))
	else:
		print  lms['cause-attempt-outcome'] + u' означает, что ' + lms['agent-attempt'] +  u' старается достичь положительного исхода'

def generate_language(data,lang):
    for jline in data:
        mappings = jline["annotationMappings"][0]
	if len(mappings["explanation"])>0:
            exp_list = mappings["explanation"].split("],")
            source_lms = set(mappings["source"].split(","))
            target_lms = set(mappings["target"].split(","))
            target_sub = jline["targetConceptSubDomain"]
            sent_id = jline["sid"]
            process_explanation(exp_list,sent_id,lang,target_sub,target_lms,source_lms)

def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Generate natural language from metaphor system output.")
    parser.add_argument(
        "-i",
        "--input",
        help="Input file of axioms.",
        required=True,
        default=None)  
    parser.add_argument(
        "-l",
        "--lang",
        help="Input language.",
        required=False,
        default="EN") 
    pa = parser.parse_args()  
    return pa

def main(pa_input,lang):
    infile = open(pa_input,"r")
    json_data = json.load(infile)
    generate_language(json_data,lang)

if __name__ == "__main__":
    pa = parse_arguments()
    pa_infile = pa.input
    lang = pa.lang
    main(pa_infile,lang)
