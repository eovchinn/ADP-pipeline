#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import re
import time
import thread
import socket

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
RU_KBPATH = "%s/KBs/Russian/Russian_compiled_KB.da" % METAPHOR_DIR
FA_KBPATH = "%s/KBs/Farsi/Farsi_compiled_KB.da" % METAPHOR_DIR

# switches
kbcompiled = True

DESCRIPTION = "Abductive engine output; abductive_hypothesis: metaphor " \
              "interpretation; abductive_unification: unifications " \
              "happened or not; abductive_explanation: axioms applied or not"


# unique_id used for proofgraph name (annotation_id may not be enough, as
# different docs may have same annotation_ids)
# withPDFContent=true; generate graphs and include PDF content
# as base-64 in output

def extract_hypotheses(inputString, unique_id, with_pdf_content):
    print unique_id
    output_struct = []
    hypothesis_found = False
    p = re.compile('<result-inference target="(.+)"')
    target = ""
    hypothesis = ""
    unification = False
    explanation = False

    # for generating proofgraph URIs
    webservice = get_webservice_location()

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

            output_struct_item["id"] = target
            output_struct_item["isiAbductiveHypothesis"] = hypothesis
            output_struct_item["isiAbductiveUnification"] = unification
            output_struct_item["isiAbductiveExplanation"] = explanation
            output_struct_item["isiAbductiveProofgraph"] = \
                "http://%s/proofgraphs/%s_%s.pdf" % \
                (webservice, unique_id, target, )

            if with_pdf_content:
                base_64_str = get_base64("%s/proofgraphs/%s_%s.pdf" %
                                         (TMP_DIR, unique_id, target, ))
                output_struct_item["isiAbductiveProofgraphStr"] = base_64_str

            output_struct_item["isiDescription"] = DESCRIPTION
            output_struct.append(output_struct_item)
            target = ""
            unification = False
            explanation = False

    # return json.dumps(output_struct, ensure_ascii=False)
    return output_struct


def generate_text_input(input_metaphors, language):
    
    output_str = ""

    for key in input_metaphors.keys():
        #if language == "EN" or language == "RU":
        #    output_str += "<META>" + key + "\n\n " + input_metaphors[key] + "\n\n"
        #else:
        #    output_str += ".TEXTID(" + key + ").\n\n" + input_metaphors[key] + "\n\n"
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

    # unique id used for proofgraph name
    unique_id = get_unique_id()

    if with_pdf_content:
        # generate graphs so we can return them with output
        generate_graph(input_metaphors, henry_output, unique_id)
    else:
        # start graphical generation in thread; don't wait for it to finish
        thread.start_new_thread(generate_graph,
                                (input_metaphors, henry_output, unique_id))


    hypotheses = extract_hypotheses(henry_output, unique_id, with_pdf_content)

    # print hypotheses

    # merge ADB result and input json document
    for hyp in hypotheses:
        for ann in request_body_dict["metaphorAnnotationRecords"]:
            try:
                if int(ann["id"]) == int(hyp["id"]):
                    for key, value in hyp.items():
                        ann[key] = value
            except Exception:
                pass

    return request_body_dict


def get_webservice_location():

    # this gives the IP address; you may want to use this during the demo
    # hostname=socket.gethostbyname(hostname)

    hostname = socket.getfqdn()
    port = "8000"

    if os.environ.get("ADP_PORT") is not None:
        port = os.environ.get("ADP_PORT")

    return hostname + ":" + port


def get_unique_id():
    current_time = int(time.time())
    unique_id = str(current_time)[5:]
    return unique_id


def generate_graph(input_dict, henry_output, unique_id):

    # create proofgraphs directory if it doesn't exist
    graph_dir = TMP_DIR + "/proofgraphs"
    
    if not os.path.exists(graph_dir):
        os.makedirs(graph_dir)

    for key in input_dict.keys():
        print "Generating a proofgraph for " + key
        graph_output = os.path.join(graph_dir, unique_id + "_" + key + ".pdf")

        viz = "python " + HENRY_DIR + "/tools/proofgraph.py --graph " + key + \
              " | dot -T pdf > " + graph_output

        graphical_processing = Popen(viz, shell=True, stdin=PIPE, stdout=PIPE,
                                     stderr=None, close_fds=True)

        graphical_processing.communicate(input=henry_output)
        #print "sleep"
        #time.sleep(3)

    print "Done generating proof graphs."


# returns contents of PDF file in base-64
def get_base64(pdf_file_path):
    f = open(pdf_file_path, "rb")
    binary_str = f.read()
    f.close()
    encoded_str = binary_str.encode("base64")
    return encoded_str


# if "__main__" == __name__:
#     main()
