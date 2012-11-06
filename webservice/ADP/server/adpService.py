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
    logging.info('No language information available.')
    return json.dumps([])

  # These are the annotations that were given in the web service call
  annotations = ro["annotations"]
 
  #dict that contains metaphors&annotation_id
  input_metaphors = {}

  annotation_id_index=0
  for annotation in annotations:

    try:
      annotation_id = annotation["annotation_id"]
    except KeyError:
      logging.info('No annotation_id.Set one.')
      annotation_id_index=annotation_id_index+1
      annotation_id=annotation_id_index

    try:
      metaphor=annotation["metaphor"]
      input_metaphors[str(annotation_id)]=metaphor
    except KeyError:
      logging.info('No metaphor.Skip it.')

  logging.info("Input metaphors:"+ str(input_metaphors))

  logging.info("Processing " + language + "...")

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
