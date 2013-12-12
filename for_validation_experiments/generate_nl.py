#! /usr/bin/python

import argparse
import json
import re

grow_set = set([u'THING-INCREASING', u'CAUSE-INCREASE-AMOUNT'])

def lm_category(log):
    if re.search(u"^CAUSE",log):
        lm_type = "causer"
    elif re.search(u"^THING",log):
        lm_type = "thing"
    return lm_type

def process_explanation(exp):
    log_list = []
    lms = {}
    for e in exp:
        e = e.strip()
        logic = e.split("[")[0]
        lm = e.split("[")[1].rstrip("]")
        log_list.append(logic)
        lm_type = lm_category(logic)
        lms[lm_type] = lm
    log_set = set(log_list)
    if log_set == grow_set:
        print('{} causes an increased amount of {}'.format(lms['causer'],lms['thing']))
        

def generate_language(data):
    for jline in data:
        mappings = jline["annotationMappings"][0]
        exp_list = mappings["explanation"].split(",")
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
