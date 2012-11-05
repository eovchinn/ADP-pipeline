Start ADP web-service annotateDocument on port 8080
=======================================================

export PYTHONPATH=location of ADP pipelines (Metaphor-ADP/pipelines/English)
python adpService.py -p 8080

Send a request
==============

 #if sending the req from host where service is running (localhost)
 python sendRestRequest.py -p 8080 -j testRequest1.json

 #specify hostname
 python sendRestRequest.py -s colo-vm19.isi.edu -p 8080 -j
 testRequest1.json
