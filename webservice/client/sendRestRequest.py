import httplib, urllib
import json, logging
from optparse import OptionParser

# Set up logging for our test code here
logging.basicConfig(level=logging.INFO)

# Get the arguments from the command line
parser = OptionParser() 
parser.add_option("-p", "--port", dest="port", type="int",
  help="TCP port that the REST server is listening on (default %default)",
  metavar="INT", default=8000)
parser.add_option("-s", "--hostname", dest="hostname", 
  help="Host that the REST server is listening on (default %default)",
  metavar="HOSTNAME", default="localhost")
parser.add_option("-j", "--jsonFile", dest="json_filename",
  help="JSON to send to the annotateDocumentADP web service", metavar="JSON_FILE")
(options, args) = parser.parse_args()

# Verify that we have a JSON file to send to the server
if not options.json_filename:
  parser.error("Must supply a JSON file to send to the web service")

# Verify that the JSON file is valid JSON
json_string = None

try:
  with open(options.json_filename, 'r') as json_file:
    json_obj = json.load(json_file)
    json_string = json.dumps(json_obj, indent=3)
except ValueError:
  parser.error("JSON file contained invalid json.")

logging.info("Sending JSON to port {0} on {1}...".format(options.port, options.hostname))

# Create the connection with the neccessary headers
headers = {
  "Accept" : "application/json", 
  "Content-type" : "application/json"
}
conn = httplib.HTTPConnection(options.hostname, options.port)
conn.request("POST", "/annotateDocument", json_string, headers)

# Process the response
response = conn.getresponse()
if response.status != 200:
  logging.error("Returned back a bad response code from the server: {0} {1}".format(
    response.status, response.reason))
else:
  response_body = response.read()

  # Verify that the return JSON is valid JSON
  try:
    json_obj = json.loads(response_body)
    json_string = json.dumps(json_obj, indent=3)
    print json_string
  except ValueError:
    parser.error("The reply JSON was in invalid JSON format.")

# Close off the connection
conn.close()

