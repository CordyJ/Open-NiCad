# -*- coding: utf-8 -*-

# Copyright (c) 2009 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a QNetworkReply subclass reporting an unknown protocol error.
"""

from PyQt4.QtCore import *
from PyQt4.QtNetwork import QNetworkReply, QNetworkRequest

class NetworkProtocolUnknownErrorReply(QNetworkReply):
    """
    Class implementing a QNetworkReply subclass reporting an unknown protocol error.
    """
    def __init__(self, protocol, parent = None):
        """
        Constructor
        
        @param protocol protocol name (string or QString)
        @param parent reference to the parent object (QObject)
        """
        QNetworkReply.__init__(self)
        self.setError(QNetworkReply.ProtocolUnknownError, 
                      self.trUtf8("Protocol '%1' not supported.").arg(protocol))
        QTimer.singleShot(0, self.__fireSignals)
    
    def __fireSignals(self):
        """
        Private method to send some signals to end the connection.
        """
        self.emit(SIGNAL("error(QNetworkReply::NetworkError)"), 
                         QNetworkReply.ProtocolUnknownError)
        self.emit(SIGNAL("finished()"))
    
    def abort(self):
        """
        Public slot to abort the operation.
        """
        # do nothing
        pass
    
    def bytesAvailable(self):
        """
        Public method to determined the bytes available for being read.
        
        @return bytes available (integer)
        """
        return 0
