# -*- coding: utf-8 -*-

# Copyright (c) 2009 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a network reply object for special data.
"""

from PyQt4.QtCore import *
from PyQt4.QtNetwork import QNetworkReply, QNetworkRequest

class NetworkReply(QNetworkReply):
    """
    Class implementing a QNetworkReply subclass for special data.
    """
    def __init__(self, request, fileData, mimeType):
        """
        Constructor
        
        @param request reference to the request object (QNetworkRequest)
        @param fileData reference to the data buffer (QByteArray)
        @param mimeType for the reply (string)
        """
        QNetworkReply.__init__(self)
        
        self.__data = fileData
        
        self.setRequest(request)
        self.setOpenMode(QIODevice.ReadOnly)
        
        self.setHeader(QNetworkRequest.ContentTypeHeader, QVariant(mimeType))
        self.setHeader(QNetworkRequest.ContentLengthHeader, 
                       QVariant(QByteArray.number(fileData.length())))
        QTimer.singleShot(0, self, SIGNAL("metaDataChanged()"))
        QTimer.singleShot(0, self, SIGNAL("readyRead()"))
    
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
        return self.__data.length() + QNetworkReply.bytesAvailable(self)
    
    def readData(self, maxlen):
        """
        Protected method to retrieve data from the reply object.
        
        @param maxlen maximum number of bytes to read (integer)
        @return string containing the data (string)
        """
        len_ = min(maxlen, self.__data.length())
        buffer = str(self.__data[:len_])
        self.__data.remove(0, len_)
        if self.__data.length() == 0:
            QTimer.singleShot(0, self, SIGNAL("finished()"))
        return buffer
