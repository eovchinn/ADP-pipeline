#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import re
import json
import time
import thread
import socket
import logging
import extract_CMs_from_hypotheses

from logging.handlers import TimedRotatingFileHandler
from extract_CMs_from_hypotheses import *

from subprocess import Popen, PIPE


logHandler = TimedRotatingFileHandler("logfile", when="midnight")
logFormatter = logging.Formatter("%(asctime)s %(message)s")
logHandler.setFormatter(logFormatter)
logger = logging.getLogger("my_logger")
logger.addHandler(logHandler)
logger.setLevel(logging.INFO)


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
EN_KBPATH = "%s/KBs/English/English_compiled_KB_2.da" % METAPHOR_DIR
ES_KBPATH = "%s/KBs/Spanish/Spanish_compiled_KB_2.da" % METAPHOR_DIR
RU_KBPATH = "%s/KBs/Russian/Russian_compiled_KB_2.da" % METAPHOR_DIR
FA_KBPATH = "%s/KBs/Farsi/Farsi_compiled_KB.da" % METAPHOR_DIR

# switches
kbcompiled = True

# Katya: this should be the new output, when LCC updates their repository and accepts new fields.
#DESCRIPTION = "Abductive engine output; " \
#		"isiMetaphorConfirmed: Abduction confirmes linguistic metaphor;" \
#              "isiTargetDomain: Target domain defined by abduction; " \
#              "isiTargetSubdomain: Target subdomain defined by abduction ; "\
#		"isiSourceDomain: Source domain defined by abduction ; " \
#              "isiSourceSubdomain: Source subdomain defined by abduction ; "\
#		"isiTargetWords: Words from target domain found by abduction ; " \
#              "isiSourceWords: Words from source domain found by abduction ; "\
#		"isiTargetSourceMapping: Target-Source mapping (metaphor interpretation) as logical form found by abduction. "

DESCRIPTION = "Abductive engine output; " \
		"isiAbductiveHypothesis: Abduction detects target and source domains/subdomains" \
              "and words referring to the domains; " \
		"isiTargetSourceMapping: Target-Source mapping as logical form found by abduction " \
		"that explains the methaphor and motivates the domains."

def extract_hypotheses(inputString):
    output_struct = []
    hypothesis_found = False
    p = re.compile('<result-inference target="(.+)"')
    target = ""
    hypothesis = ""
    unification = False
    explanation = False

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
		
            # Katya: new_output_struct_item should be the new output, when LCC updates their repository and accepts new fields.
            new_output_struct_item = extract_CM_mapping(target,hypothesis)
            #print json.dumps(hypothesis, ensure_ascii=False)
            #print json.dumps(new_output_struct_item, ensure_ascii=False)

            output_struct_item["isiAbductiveExplanation"] = new_output_struct_item["isiTargetSourceMapping"]	
            output_struct_item["isiAbductiveHypothesis"] = "TARGET DOMAIN AND SUBDOMAIN[" + new_output_struct_item["isiTargetDomain"] + \
                                                            " " + new_output_struct_item["isiTargetSubdomain"] + "] " + \
                                                            "TARGET WORDS[" +  new_output_struct_item["isiTargetWords"] + "] " + \
                                                            "SOURCE DOMAIN AND SUBDOMAIN[" + new_output_struct_item["isiSourceDomain"] + \
                                                            " " + new_output_struct_item["isiSourceSubdomain"] + "] " + \
                                                            "SOURCE WORDS[" +  new_output_struct_item["isiSourceWords"] + "]"

            output_struct_item["id"] = target
            output_struct_item["isiDescription"] = DESCRIPTION
            output_struct_item["isiAbductiveUnification"] = ''
            output_struct_item["isiAbductiveProofgraph"] = ''

            output_struct.append(output_struct_item)
            target = ""

    #print json.dumps(output_struct, ensure_ascii=False)
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

    processed, failed, empty = 0, 0, 0

    # merge ADB result and input json document
    for hyp in hypotheses:
        for ann in request_body_dict["metaphorAnnotationRecords"]:
            try:
                if int(ann["id"]) == int(hyp["id"]):
                    for key, value in hyp.items():
                        ann[key] = value
                        processed += 1
                    if not hyp["isiAbductiveProofgraph"]:
                        print "proofgraph not found (%d)" % int(ann["id"])
                        fl.write("EMPTY PROOFGRAPH\n")
                        fl = open("/lfs1/vzaytsev/misc/fails/context.%d.txt" % int(ann["id"]), "w")
                        fl.write(ann["context"].encode("utf-8"))
                        fl.close()
                        empty += 1
            except Exception:
                print "proofgraph not found (%d)" % int(ann["id"])
                fl = open("/lfs1/vzaytsev/misc/fails/context.%d.txt" % int(ann["id"]), "w")
                fl.write("FAIL\n")
                fl.write(ann["context"].encode("utf-8"))
                fl.close()
                failed += 1

    logger.info("STAT: {'processed':%d,'failed':%d,'empty':%d}" %  (processed, failed, empty))

    return request_body_dict


def get_webservice_location():

    # this gives the IP address; you may want to use this during the demo
    # hostname=socket.gethostbyname(hostname)

    hostname = socket.getfqdn()
    port = "8000"

    if os.environ.get("ADP_PORT") is not None:
        port = os.environ.get("ADP_PORT")

    return hostname + ":" + port



