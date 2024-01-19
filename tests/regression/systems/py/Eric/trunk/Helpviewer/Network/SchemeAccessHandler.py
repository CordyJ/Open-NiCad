# -*- coding: utf-8 -*-

# Copyright (c) 2009 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the base class for specific scheme access handlers.
"""

from PyQt4.QtCore import QObject

class SchemeAccessHandler(QObject):
    """
    Clase implementing the base class for specific scheme access handlers.
    """
    def __init__(self, parent = None):
        """
        Constructor
        
        @param parent reference to the parent object (QObject)
        """
        QObject.__init__(self, parent)
    
    def createRequest(self, op, request, outgoingData = None):
        """
        Protected method to create a request.
        
        @param op the operation to be performed (QNetworkAccessManager.Operation)
        @param request reference to the request object (QNetworkRequest)
        @param outgoingData reference to an IODevice containing data to be sent
            (QIODevice)
        @return reference to the created reply object (QNetworkReply)
        """
        raise NotImplementedError()
