import json, logging
from optparse import OptionParser
from restServer import start_server 
from NLPipeline_coref_English_metaphor import *

def annotate_document(annotate_document_request_body):
  logging.info("Processing annotateDocumentADP...")

  # The annotate_document_request_body object is a JSON string
  ro = json.loads(annotate_document_request_body)

  # We retrieve some of the fields from the document
  document = ro["document"]
  #document language
  try:
    language = document['language']
  except KeyError:
    print 'No language information available.'
    return json.dumps([])

  # These are the annotations that were given in the web service call
  annotations = ro["annotations"]
 
  #string that contains metaphors&annotation_id; input to English_ADP
  input_metaphors = ""

  annotation_id=0
  for annotation in annotations:
    try:
      metaphor=annotation["metaphor"]
      #annotation_id = annotation["annotation_id"]
      annotation_id=annotation_id+1
      input_metaphors = input_metaphors + "<META>'" + str(annotation_id) + "'\n\n " + metaphor + "\n\n" 
    except KeyError:
      print 'No metaphor or no annotation_id.Skip it.'

  print "Input metaphors:" + input_metaphors

  #eng_adp=English_ADP("<META>'5'\n\n Every student reads.\n\n<META>'3'\n\n This dog runs. The animal is funny.\n\n")
  print "Processing " + language + "..."

  if language=='EN' :
    #English:returns JSON array
    eng_adp=English_ADP(input_metaphors)
    return eng_adp
  elif language=='ES' :
    #Spanish:returns JSON array
    sp_adp=Spanish_ADP(input_metaphors)
    return sp_adp
  if language=='RU' :
    #Russian:returns JSON array
    ru_adp=Russian_ADP(input_metaphors)
    return ru_adp
  if language=='FA' :
    #Farsi:returns JSON array
    fa_adp=Farsi_ADP(input_metaphors)
    return fa_adp

  #unknown language; return empty array
  return json.dumps([])

if __name__ == '__main__':
  # Configure the logger
  logging.basicConfig(level=logging.INFO)

  # Get command-line options
  parser = OptionParser() 
  parser.add_option("-p", "--port", dest="port", type="int",
                    help="TCP port number that the REST server will "
                         "listen on (default %default)",
                    metavar="INT", default=8000)
  (options, args) = parser.parse_args()

  start_server(options, annotate_document)
