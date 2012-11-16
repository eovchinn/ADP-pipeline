Set environment variable in ~/.bash_profile
===========================================

export PYTHONPATH=location of ADP pipelines (Metaphor-ADP/pipelines/English)

Start web-service annotateDocument on default port 8000
=======================================================

python adpService.py 

OR ... start on another port
============================
python adpService.py -p 8080

Send a request
==============

1. Server running on localhost & default port
 python sendRestRequest.py -j testRequest1.json

2. Server running on localhost & specific port
 python sendRestRequest.py -p 8080 -j testRequest1.json

3. Server running on remote host (specify hostname)
 python sendRestRequest.py -s colo-vm19.isi.edu -p 8080 -j
 testRequest1.json

Note:
=====

When starting the web-service, if you see an error stating "No socket
can be created" the process may already be started on that port.

Check with:

ps -ef | grep adpService

You should see something like:

501 84127 84123 0 ... /.../adpService.py

Kill proces:

kill -9 84127 (make sure you use the currend PID)


