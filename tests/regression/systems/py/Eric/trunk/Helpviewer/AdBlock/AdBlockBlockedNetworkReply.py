# -*- coding: utf-8 -*-

# Copyright (c) 2009 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a QNetworkReply subclass reporting a blocked request.
"""

from PyQt4.QtCore import *
from PyQt4.QtNetwork import QNetworkReply, QNetworkAccessManager

class AdBlockBlockedNetworkReply(QNetworkReply):
    """
    Class implementing a QNetworkReply subclass reporting a blocked request.
    """
    def __init__(self, request, rule, parent = None):
        """
        Constructor
        
        @param request reference to the request object (QNetworkRequest)
        @param fileData reference to the data buffer (QByteArray)
        @param mimeType for the reply (string)
        """
        QNetworkReply.__init__(self, parent)
        self.setOperation(QNetworkAccessManager.GetOperation)
        self.setRequest(request)
        self.setUrl(request.url())
        self.setError(QNetworkReply.ContentAccessDenied, 
                      self.trUtf8("Blocked by AdBlock rule: %1.").arg(rule.filter()))
        QTimer.singleShot(0, self.__fireSignals)
    
    def __fireSignals(self):
        """
        Private method to send some signals to end the connection.
        """
        self.emit(SIGNAL("error(QNetworkReply::NetworkError)"), 
                         QNetworkReply.ContentAccessDenied)
        self.emit(SIGNAL("finished()"))
    
    def readData(self, maxlen):
        """
        Protected method to retrieve data from the reply object.
        
        @param maxlen maximum number of bytes to read (integer)
        @return string containing the data (string)
        """
        return None
    
    def abort(self):
        """
        Public slot to abort the operation.
        """
        # do nothing
        pass
