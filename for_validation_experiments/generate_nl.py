#! /usr/bin/python

import argparse
import json
import re

grow_set = set([u'THING-INCREASING', u'CAUSE-INCREASE-AMOUNT'])
eradicate_set =set([u'THING-NOT-EXISTING', u'CAUSE-NOT-EXIST', u'THING-CAUSING-NON-EXISTENCE'])
no_agent_eradicate_set=set([u'THING-NOT-EXISTING', u'CAUSE-NOT-EXIST'])

def lm_category(log):
    if re.search(u"^CAUSE",log):
        lm_type = "cause"
    elif re.search(u"^THING-CAUSING",log):
        lm_type = "agent"
    elif re.search(u"^THING-",log):
        lm_type = "patient"
    return lm_type

def process_explanation(exp):
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
    #print log_set
    if logic_set == grow_set:
        print('{} denotes an increased amount of {}'.format(lms['cause'],lms['patient']))
    if logic_set == eradicate_set:
        print('{} denotes that {} causes {} to stop existing'.format(lms['cause'],lms['agent'],lms['patient']))
    if logic_set == no_agent_eradicate_set:
        print('{} denotes that there is an effort to stop the existence of {} '.format(lms['cause'],lms['patient']))
        

def generate_language(data):
    for jline in data:
        mappings = jline["annotationMappings"][0]
        exp_list = mappings["explanation"].split("],")
        process_explanation(exp_list)


        
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
