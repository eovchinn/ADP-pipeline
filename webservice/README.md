ADP Web-Service
===============

#### Install CherryPy Web-Server

* Download CherryPy Web-Server from: `http://www.cherrypy.org`
* Install CherryPy:

```
cd CherryPy-3.2.2
sudo python setup.py install
```

#### Quick Start

* Start server: `python adpService.py -p 8080 -g`
* Send Request (for testing) : `python sendRestRequest.py -p 8080 -j testRequest1.json`

#### Set environment variable in ~/.bash_profile
```
export PYTHONPATH=location of ADP pipelines (Metaphor-ADP/pipelines/common:Metaphor-ADP/pipelines/English:Metaphor-ADP/pipelines/Farsi:Metaphor-ADP/pipelines/Spanish:Metaphor-ADP/pipelines/Russian)
```

#### Start web-service (`cd server`)

```
python adpService.py <-p port> <-g> 
```
* -p: port number (default 8000)
* -g: web-service returns proofgraph as base-64 string; if not present only returns URL of proofgraph

Example:
```
python adpService.py -p 8080 -g 
```

#### Send a request (`cd client`)

```
 python sendRestRequest.py <-s hostname> <-p port> <-j json_document>
```
* -s: hostname (default localhost)
* -p: port number (default 8000)
* -j: input json document
 
Example:

```
 python sendRestRequest.py -s colo-vm19.isi.edu -p 8080 -j testRequest1.json
```

#### Troubleshooting

When starting the web-service, if you see an error stating "No socket
can be created" the process may already be started on that port.

* Check with:
```
ps -ef | grep adpService
```
* You should see something like:
```
501 84127 84123 0 ... /.../adpService.py
```
* Kill process:
```
kill -9 84127 (make sure you use the currend PID)
```

#### Change Timeout

* in /server/restServer.py search for response.timeout and change it's value
(currently set to 15 minutes/default is 10 minutes)

#### Change IP Address for proofgraph URLs

* in NLpipeline_MULT_metaphor.py, go to get_webservice_location:
```
###currently hostname is used, but during demo you might have to use
###the IP address
	hostname=socket.getfqdn()
#this gives the IP address; you may want to use this during the demo
	#hostname=socket.gethostbyname(hostname)
```

* if the above doesn't return the correct IP address, just add the IP
address instead of using socket functions

#### Start Web-Service on colo-vm19

* Log into colo-vm19 (if you don't have root access ask Richard)
* Go to /opt/RestWebServer/ADP
* Check if there is a process running and kill it
```
 ps -ef | grep adp
 root      2555 19952  1 10:07 pts/0    00:00:00 python adpService.py -p 8080 -g

 kill it : sudo kill -9 2555
```

* Start web-service
```
nohup sudo python adpService.py -p 8080 -g &
```
* Check it
```
python sendRestRequest.py -p 8080 -j testRequest1.json
```
