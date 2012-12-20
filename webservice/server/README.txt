Start server: python adpService.py -p 8080 -g
Send Request (for testing) : python sendRestRequest.py -p 8080 -j testRequest1.json

Change timeout: see below
Change IP address for proofgraphs: see below

What they need to know:
*port - 8080
*IP address of machine 

Set environment variable in ~/.bash_profile
===========================================

export PYTHONPATH=location of ADP pipelines (Metaphor-ADP/pipelines/common)

Start web-service annotateDocument on default port 8000
=======================================================

*if "-g" argument is present, web-service returns proofgraph as
 base-64 string
*if not present only returns URL of proofgraph

python adpService.py -g 

OR ... start on another port
============================
python adpService.py -p 8080 -g

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

Change Timeout
==============
* in /server/restServer.py search for response.timeout and change it's value
(currently set to 15 minutes/default is 10 minutes)

Change IP Address for proofgraph URLs
=====================================
* in NLpipeline_MULT_metaphor.py, go to get_webservice_location:

###currently hostname is used, but during demo you might have to use
###the IP address
	hostname=socket.getfqdn()
#this gives the IP address; you may want to use this during the demo
	#hostname=socket.gethostbyname(hostname)

***if the above doesn't return the correct IP address, just add the IP
address instead of using socket functions
