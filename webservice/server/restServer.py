# -*- coding: utf-8 -*-

import os
import cherrypy


class AnnotateDocumentResource(object):
    """
    This class wraps a method which is used to handle POST requests
    to the REST service on /annotateDocument
    """
    exposed = True

    def __init__(self, annotation_method):
        self.annotation_method = annotation_method

    def POST(self):
        cherrypy.response.headers["Content-Type"] = "application/json"
        return self.annotation_method(cherrypy.request.body.read())


def start_server(options, annotate_document_post_handler):
    """
    Start the REST server.
  
    The "options" parameter is an object with attributes that correspond
    to various server parameters (like "port").
    """

    #root for images is the TMP_DIR
    img_dir = os.environ["TMP_DIR"]

    # Create the configuration for the server
    conf = {
        "global": {
            "server.socket_host": "0.0.0.0",
            "server.socket_port": options.port,
            "log.screen": False,
        },
        "/": {
            "request.dispatch": cherrypy.dispatch.MethodDispatcher(),
            "response.timeout": 60 * 10,
        },
        "/proofgraphs": {
            "tools.staticdir.root": img_dir,
            "tools.staticdir.dir": "proofgraphs",
            "tools.staticdir.on": True
        },
    }

    # We create a "Root" class which represents the web service URLs which
    # are on the server. We are only creating the URL /annotateDocument.

    class Root(object):

        # Pass the annotate_document method to the AnnotateDocumentResource class

        annotateDocument = AnnotateDocumentResource(
            annotate_document_post_handler)

    # Start the server
    cherrypy.quickstart(Root(), "/", conf)
