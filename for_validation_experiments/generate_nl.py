#! /usr/bin/python

import argparse
import json
import re

grow_set = set([u'THING-INCREASING', u'CAUSE-INCREASE-AMOUNT'])
eradicate_set =set([u'THING-NOT-EXISTING', u'CAUSE-NOT-EXIST', u'THING-CAUSING-NON-EXISTENCE'])
no_agent_eradicate_set=set([u'THING-NOT-EXISTING', u'CAUSE-NOT-EXIST'])
exit_abyss_set = set([u'THING-THAT-LIMITED-OPTIONS', u'CAUSE-INCREASE-OPTIONS', u'THING-THAT-STOPPED-FUNCTION', u'CAUSE-RESUME-FUNCTION'])
deep_abyss_set = set([u'CAUSE-SEVERE-NOT-FUNCTION',u'CAUSE-SEVERE-REDUCE-OPTIONS'])
harvest_crop_seed_set = set([u'CAUSE-OUTCOME-OF-ACTION', u'CAUSE-REALIZE-OUTCOME', u'PREPARATION-FOR-OUTCOME', u'THING-REALIZING',u'OUTCOME-OF-ACTION']) 
crop_outcome_set = set([u'CAUSE-OUTCOME-OF-ACTION',u'OUTCOME-OF-ACTION']) 
crop_set = set([u'CAUSE-OUTCOME-OF-ACTION']) 
price_set = set([u'THING-DESIRED', u'CAUSE-NEGATIVE-CONSEQUENCE-OF-DESIRED-THING'])
live_in_set = set([u'CAUSE-EXPERIENCE-SOMETHING',u'EXPERIENCER','THING-EXPERIENCED'])

def lm_category(log):
    if re.search(u"^CAUSE\-INCREASE\-AMOUNT",log):
        lm_type = "cause_inc_am"
    elif re.search(u"^CAUSE\-NOT-\EXIST",log):
        lm_type = "cause_not_exist"   
    elif re.search(u"^CAUSE-RESUME-FUNCTION",log):
        lm_type = "cause_resume_function"   
    elif re.search(u"^CAUSE-INCREASE-OPTIONS",log):
        lm_type = "cause_increase_options"  
    elif re.search(u"^CAUSE-REALIZE-OUTCOME",log):
        lm_type = "cause_realize_outcome"
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
             
    elif re.search(u"^THING-CAUSING-NON-EXISTING",log):
        lm_type = "agent_not_exist"
    elif re.search(u"^THING-THAT-LIMITED-OPTIONS",log):
        lm_type = "agent_limit_options" 
    elif re.search(u"^THING-THAT-STOPPED-FUNCTION",log):
        lm_type = "agent_stop_function" 
    elif re.search(u"^THING-REALIZING",log):
        lm_type = "agent_realize"


        
    elif re.search(u"^EXPERIENCER",log):
        lm_type = "patient_experience"        
    elif re.search(u"^THING-INCREASING",log):
        lm_type = "patient_increase"
    elif re.search(u"^THING-NOT-EXISTING",log):
        lm_type = "patient_not_exist"
    elif re.search(u"^THING-DESIRED",log):
        lm_type = "patient_desire" 

    elif re.search(u"^THING-EXPERIENCED",log):
        lm_type = "experience-event"  
    elif re.search(u"^OUTCOME-OF-ACTION",log):
        lm_type = "outcome"
    elif re.search(u"^PREPARATION-FOR-OUTCOME",log):
        lm_type = "preparation"
        
    else:
        print log
        
    return lm_type

def process_explanation(exp,s_id):
    logic_list = []
    lms = {}
    for e in exp:
        e = e.strip().rstrip("]")
        #print e
        logic = e.split("[")[0]
        #print logic
        lm_list = e.split("[")[1].rstrip("]").split(",")
        logic_list.append(logic)
        lm_type = lm_category(logic)
        for word in lm_list:
            lms[lm_type] = word
    logic_set = set(logic_list)    
    if logic_set == grow_set:
        print s_id
        print('{} denotes an increased amount of {}'.format(lms['cause_inc_an'],lms['patient_increase']))
    if logic_set == eradicate_set:
        print s_id        
        print('{} denotes that {} causes {} to stop existing'.format(lms['cause_not_exist'],lms['agent_not_exist'],lms['patient_not_exist']))
    if logic_set == no_agent_eradicate_set:
        print s_id        
        print('{} denotes that there is an effort to stop the existence of {} '.format(lms['cause_not_exist'],lms['patient_not_exist']))
    if logic_set == exit_abyss_set:
        print s_id        
        print('{} denotes that {} had limited options, but options will increase; {} denotes that {} had caused something not to function, but functionality will resume'.format(lms['cause_increase_options'],lms['agent_limit_options'],lms['cause_resume_function'],lms['agent_stop_function']))    
    if logic_set == harvest_crop_seed_set:
        print s_id
        print('{} denotes that {} was a preparation so that {} is realizing the outcome, {} in this case, of some action, which is denoted by {}'.format(lms['cause_realize_outcome'],lms['preparation'],lms['agent_realize'],lms['outcome'],lms['cause-outcome']))
    if logic_set == crop_outcome_set:
        print s_id
        print('{} denotes that {} is the outcome of some action'.format(lms['cause-outcome'],lms['outcome']))   
    if logic_set == crop_set:
        print s_id
        print('{} denotes that poverty is the outcome of some action'.format(lms['cause-outcome']))                     
    if logic_set == deep_abyss_set:
        print s_id
        print('{} implies that the experiencer of poverty has severely limited options and cannot function'.format(lms['cause-sev-not-function']))
    if logic_set == price_set:
        print s_id
        print('{} implies that poverty is a negative consequence that must be accepted to attain {}'.format(lms['cause-neg-consequence'],lms['patient_desire']))  
    if logic_set == live_in_set:
        print s_id
        print('{} implies that {} experiences {}'.format(lms['cause-experience'],lms['patient_experience'],lms['experience-event']))                
        

def generate_language(data):
    for jline in data:
        mappings = jline["annotationMappings"][0]
        exp_list = mappings["explanation"].split("],")
        sent_id = jline["sid"]
        process_explanation(exp_list,sent_id)

def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Generate natural language from metaphor system output.")
    parser.add_argument(
        "-i",
        "--input",
        help="Input file of axioms.",
        required=True,
        default=None)  
    pa = parser.parse_args()  
    return pa.input

def main(pa_input):
    infile = open(pa_input,"r")
    json_data = json.load(infile)
    generate_language(json_data)

if __name__ == "__main__":
    pa_infile = parse_arguments()
    main(pa_infile)
