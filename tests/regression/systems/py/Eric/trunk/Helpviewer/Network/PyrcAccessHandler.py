# -*- coding: utf-8 -*-

# Copyright (c) 2009 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a scheme access handler for Python resources.
"""

from PyQt4.QtCore import QBuffer, QIODevice, QString

from Helpviewer.HTMLResources import startPage_html

from SchemeAccessHandler import SchemeAccessHandler

from NetworkReply import NetworkReply
from NetworkProtocolUnknownErrorReply import NetworkProtocolUnknownErrorReply

import UI.PixmapCache

class PyrcAccessHandler(SchemeAccessHandler):
    """
    Class implementing a scheme access handler for Python resources.
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
        if request.url().toString() == "pyrc:home":
            html = startPage_html
            pixmap = UI.PixmapCache.getPixmap("ericWeb32.png")
            imageBuffer = QBuffer()
            imageBuffer.open(QIODevice.ReadWrite)
            if pixmap.save(imageBuffer, "PNG"):
                html.replace("IMAGE_BINARY_DATA_HERE", 
                             QString(imageBuffer.buffer().toBase64()))
            return NetworkReply(request, html.toUtf8(), "text/html")
        
        return NetworkProtocolUnknownErrorReply("pyrc")
