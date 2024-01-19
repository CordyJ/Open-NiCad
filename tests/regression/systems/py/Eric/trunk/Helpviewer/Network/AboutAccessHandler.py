# -*- coding: utf-8 -*-

# Copyright (c) 2009 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a scheme access handler for about schemes.
"""

from SchemeAccessHandler import SchemeAccessHandler

from NetworkProtocolUnknownErrorReply import NetworkProtocolUnknownErrorReply

class AboutAccessHandler(SchemeAccessHandler):
    """
    Class implementing a scheme access handler for about schemes.
    """
    def createRequest(self, op, request, outgoingData = None):
        """
        Protected method to create a request.
        
        @param op the operation to be performed (QNetworkAccessManager.Operation)
        @param request reference to the request object (QNetworkRequest)
        @param outgoingData reference to an IODevice containing data to be sent
            (QIODevice)
        @return reference to the created reply object (QNetworkReply)
        """
        return NetworkProtocolUnknownErrorReply("about")
