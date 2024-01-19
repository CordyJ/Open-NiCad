# -*- coding: utf-8 -*-

# Copyright (c) 2009 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a scheme access handler for QtHelp.
"""

from SchemeAccessHandler import SchemeAccessHandler

from NetworkReply import NetworkReply

class QtHelpAccessHandler(SchemeAccessHandler):
    """
    Class implementing a scheme access handler for QtHelp.
    """
    def __init__(self, engine, parent = None):
        """
        Constructor
        
        @param engine reference to the help engine (QHelpEngine)
        @param parent reference to the parent object (QObject)
        """
        SchemeAccessHandler.__init__(self, parent)
        
        self.__engine = engine
    
    def createRequest(self, op, request, outgoingData = None):
        """
        Protected method to create a request.
        
        @param op the operation to be performed (QNetworkAccessManager.Operation)
        @param request reference to the request object (QNetworkRequest)
        @param outgoingData reference to an IODevice containing data to be sent
            (QIODevice)
        @return reference to the created reply object (QNetworkReply)
        """
        url = request.url()
        strUrl = url.toString()
        
        if strUrl.endsWith(".svg") or strUrl.endsWith(".svgz"):
            mimeType = "image/svg+xml"
        elif strUrl.endsWith(".css"):
            mimeType = "text/css"
        elif strUrl.endsWith(".js"):
            mimeType = "text/javascript"
        else:
            mimeType = "text/html"
        return NetworkReply(request, self.__engine.fileData(url), mimeType)
