import json, logging
from optparse import OptionParser
from restServer import start_server 
from NLPipeline_MULT_metaphor import *

def annotate_document(annotate_document_request_body):
  logging.info("Processing annotateDocument...")

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
  try:
    annotations = ro["annotations"]
  except KeyError:
    logging.info('No annotations available.')
    return json.dumps([])
 
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
      if language=='EN' :
	 #replacing single quote, double quote (start/end), dash
	 ascii_metaphor = metaphor.replace(u'\u2019',u'\u0027').replace(u'\u201c',u'\u0022').replace(u'\u201d',u'\u0022').replace(u'\u2014',u'\u002d')
	 #see unicode chars
	 #input_metaphors[str(annotation_id)]=metaphor
	 #input_metaphors[str(annotation_id)]=metaphor.encode("ascii","ignore")
	 input_metaphors[str(annotation_id)]=ascii_metaphor.encode("utf-8")
      else:
	 input_metaphors[str(annotation_id)]=metaphor.encode("utf-8")
    except KeyError:
      logging.info('No metaphor.Skip it.')

  logging.info("Input metaphors:"+ str(input_metaphors))

  logging.info("Processing " + language + "...")

  # if no metaphors
  if not input_metaphors:
    return json.dumps([])

  adp_return = ADP(input_metaphors,language)
  return adp_return

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

  #set the port as an env var read in NL_pipeline; 
  #necessary when generating proofgraph URIs
  os.environ['ADP_PORT']=str(options.port)

  start_server(options, annotate_document)
