#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import re
import time
import thread
import socket

import extract_CMs_from_hypotheses
from extract_CMs_from_hypotheses import *

from subprocess import Popen, PIPE


METAPHOR_DIR = os.environ["METAPHOR_DIR"]
HENRY_DIR = os.environ["HENRY_DIR"]
BOXER_DIR = os.environ["BOXER_DIR"]
TMP_DIR = os.environ["TMP_DIR"]

FARSI_PIPELINE = "%s/pipelines/Farsi/LF_Pipeline" % METAPHOR_DIR
SPANISH_PIPELINE = "%s/pipelines/Spanish/run_spanish.sh" % METAPHOR_DIR
RUSSIAN_PIPELINE = "%s/pipelines/Russian/run_russian.sh" % METAPHOR_DIR

BOXER2HENRY = "%s/pipelines/English/Boxer2Henry.py" % METAPHOR_DIR
PARSER2HENRY = "%s/pipelines/common/IntParser2Henry.py" % METAPHOR_DIR

# Compiled knowledge bases
EN_KBPATH = "%s/KBs/English/English_compiled_KB.da" % METAPHOR_DIR
ES_KBPATH = "%s/KBs/Spanish/Spanish_compiled_KB.da" % METAPHOR_DIR
RU_KBPATH = "%s/KBs/Russian/Russian_compiled_KB_2.da" % METAPHOR_DIR
FA_KBPATH = "%s/KBs/Farsi/Farsi_compiled_KB.da" % METAPHOR_DIR

# switches
kbcompiled = True

DESCRIPTION = "Abductive engine output; isiMetaphorConfirmed: abduction confirmes metaphor;" \
              "isiTargetDomainNativeLanguage: Target domain defined by abduction (in native language); " \
              "isiTargetSubdomainNativeLanguage: Target subdomain defined by abduction (in native language); "\
		"isiTargetDomainEnglish: Target domain defined by abduction (in English); " \
              "isiTargetSubdomainEnglish: Target subdomain defined by abduction (in English); "\
		"isiSourceDomainNativeLanguage: Source domain defined by abduction (in native language); " \
              "isiSourceSubdomainNativeLanguage: Source subdomain defined by abduction (in native language); "\
		"isiSourceDomainEnglish: Source domain defined by abduction (in English); " \
              "isiSourceSubdomainEnglish: Source subdomain defined by abduction (in English); "\
		"isiTargetSourceMapping: Target-Source mapping (metaphor interpretation) in form of logical form found by abduction. "

def extract_hypotheses(inputString):
    output_struct = []
    hypothesis_found = False
    p = re.compile('<result-inference target="(.+)"')
    target = ""
    hypothesis = ""

    for line in inputString.splitlines():

        output_struct_item = {}
        match_obj = p.match(line)

        if match_obj:
            target = match_obj.group(1)

        elif line.startswith("<hypothesis"):
            hypothesis_found = True

        elif line.startswith("</hypothesis>"):
            hypothesis_found = False

        elif hypothesis_found:
            hypothesis = line

        elif line.startswith("<unification"):
            unification = True

        elif line.startswith("<explanation"):
            explanation = True

        elif line.startswith("</result-inference>"):

            output_struct_item = extract_CM_mapping(target,hypothesis)

            output_struct_item["isiDescription"] = DESCRIPTION
            output_struct.append(output_struct_item)
            target = ""

    print json.dumps(output_struct, ensure_ascii=False)
    return output_struct


def generate_text_input(input_metaphors, language):    
    output_str = ""
    for key in input_metaphors.keys():
        output_str += "<META>" + key + "\n\n " + input_metaphors[key] + "\n\n"

    return output_str


# withPDFContent=true; generate graphs and include PDF content
# as base-64 in output

def ADP(request_body_dict, input_metaphors, language, with_pdf_content):


    start_time = time.time()
    input_str = generate_text_input(input_metaphors, language)

    # Parser pipeline
    parser_proc = ""
    if language == "FA":
        parser_proc = FARSI_PIPELINE + " | python " + PARSER2HENRY + " --nonmerge sameid freqpred"
        KBPATH = FA_KBPATH

    elif language == "ES":
        parser_proc = SPANISH_PIPELINE + " | python " + PARSER2HENRY + " --nonmerge sameid freqpred"
        KBPATH = ES_KBPATH

    elif language == "RU":
        parser_proc = RUSSIAN_PIPELINE + " | python " + PARSER2HENRY + " --nonmerge sameid freqpred"
        KBPATH = RU_KBPATH

    elif language == "EN":
        tokenizer = BOXER_DIR + "/bin/tokkie --stdin"
        candcParser = BOXER_DIR + "/bin/candc --models " + BOXER_DIR + "/models/boxer --candc-printer boxer"
        boxer = BOXER_DIR + "/bin/boxer --semantics tacitus --resolve true --stdin"
        b2h = "python " + BOXER2HENRY + " --nonmerge sameid freqpred"
        parser_proc = tokenizer + " | " + candcParser + " | " + boxer + " | " + b2h
        KBPATH = EN_KBPATH


    parser_pipeline = Popen(parser_proc, shell=True, stdin=PIPE, stdout=PIPE,
                            stderr=None, close_fds=True)
    parser_output = parser_pipeline.communicate(input=input_str)[0]

    # Parser processing time in seconds
    parser_time = (time.time() - start_time) * 0.001

    # time to generate final output in seconds
    generate_output_time = 2

    # time left for Henry in seconds
    time_all_henry = 600 - parser_time - generate_output_time

    if with_pdf_content:
        # time for graph generation subtracted from Henry time in seconds
        time_all_henry -= - 3

    # time for one interpretation in Henry in seconds
    time_unit_henry = str(int(time_all_henry / len(input_metaphors)))

    # Henry processing
    if kbcompiled:
        henry_proc = HENRY_DIR + "/bin/henry -m infer -e " + HENRY_DIR + \
                     "/models/h93.py -d 3 -t 4 -O proofgraph,statistics -T " + \
                     time_unit_henry + " -b " + KBPATH
    else:
        henry_proc = HENRY_DIR + "/bin/henry -m infer -e " + HENRY_DIR + \
                     "/models/h93.py -d 3 -t 4 -O proofgraph,statistics -T " + \
                     time_unit_henry

    henry_pipeline = Popen(henry_proc,
                           shell=True,
                           stdin=PIPE,
                           stdout=PIPE,
                           stderr=None,
                           close_fds=True)

    henry_output = henry_pipeline.communicate(input=parser_output)[0]

    

    hypotheses = extract_hypotheses(henry_output)

    # print hypotheses

    # merge ADB result and input json document
    for hyp in hypotheses:
        for ann in request_body_dict["metaphorAnnotationRecords"]:
            if int(ann["id"]) == int(hyp["id"]):
                for key, value in hyp.items():
                    ann[key] = value

    return request_body_dict


def get_webservice_location():

    # this gives the IP address; you may want to use this during the demo
    # hostname=socket.gethostbyname(hostname)

    hostname = socket.getfqdn()
    port = "8000"

    if os.environ.get("ADP_PORT") is not None:
        port = os.environ.get("ADP_PORT")

    return hostname + ":" + port



