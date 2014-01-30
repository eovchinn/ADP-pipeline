#! /usr/bin/python

import argparse
import json
import re

grow_set = set([u'THING-INCREASING', u'CAUSE-INCREASE-AMOUNT'])
eradicate_set =set([u'THING-NOT-EXISTING', u'CAUSE-NOT-EXIST', u'THING-CAUSING-NON-EXISTENCE'])
no_agent_eradicate_set=set([u'THING-NOT-EXISTING', u'CAUSE-NOT-EXIST'])
exit_abyss_set = set([u'THING-THAT-LIMITED-OPTIONS', u'CAUSE-INCREASE-OPTIONS', u'THING-THAT-STOPPED-FUNCTION', u'CAUSE-RESUME-FUNCTION'])

def lm_category(log):
    if re.search(u"^CAUSE\-INCREASE\-AMOUNT",log):
        lm_type = "cause_inc_am"
    elif re.search(u"^CAUSE\-NOT-\EXIST",log):
        lm_type = "cause_not_exist"   
    elif re.search(u"^CAUSE-RESUME-FUNCTION",log):
        lm_type = "cause_resume_function"   
    elif re.search(u"^CAUSE-INCREASE-OPTIONS",log):
        lm_type = "cause_increase_options"                   
             
    elif re.search(u"^THING-CAUSING-NON-EXISTING",log):
        lm_type = "agent_not_exist"
    elif re.search(u"^THING-THAT-LIMITED-OPTIONS",log):
        lm_type = "agent_limit_options" 
    elif re.search(u"^THING-THAT-STOPPED-FUNCTION",log):
        lm_type = "agent_stop_function" 

        
    elif re.search(u"^THING-INCREASING",log):
        lm_type = "patient_increase"
    elif re.search(u"^THING-NOT-EXISTING",log):
        lm_type = "patient_not_exist"
               
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
        

def generate_language(data):
    for jline in data:
        #print jline
        mappings = jline["annotationMappings"][0]
        exp_list = mappings["explanation"].split("],")
        sent_id = jline["sid"]
        process_explanation(exp_list,sent_id)


        
def main():
    parser = argparse.ArgumentParser(
        description="Generate natural language from metaphor system output.")
    parser.add_argument(
        "-i",
        "--input",
        help="Input file of axioms.",
        required=True,
        default=None)  
    pa = parser.parse_args()    

    infile = open(pa.input,"r")
    json_data = json.load(infile)
    generate_language(json_data)
    #print data[0]["annotationMappings"][0]
    #mappings = data[0]["annotationMappings"][0]
    #print mappings["explanation"]
if __name__ == "__main__":
    main()
