# -*- coding: utf-8 -*-

# Copyright (c) 2009 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a network access manager proxy for web pages.
"""

from PyQt4.QtCore import SIGNAL
from PyQt4.QtNetwork import QNetworkAccessManager

class NetworkAccessManagerProxy(QNetworkAccessManager):
    """
    Class implementing a network access manager proxy for web pages.
    """
    primaryManager = None
    
    def __init__(self, parent = None):
        """
        Constructor
        
        @param parent reference to the parent object (QObject)
        """
        QNetworkAccessManager.__init__(self, parent)
        self.__webPage = None
    
    def setWebPage(self, page):
        """
        Public method to set the reference to a web page.
        
        @param page reference to the web page object (HelpWebPage)
        """
        assert page is not None
        self.__webPage = page
    
    def setPrimaryNetworkAccessManager(self, manager):
        """
        Public method to set the primary network access manager.
        
        @param manager reference to the network access manager object
            (QNetworkAccessManager)
        """
        assert manager is not None
        if self.__class__.primaryManager is None:
            self.__class__.primaryManager = manager
        self.setCookieJar(self.__class__.primaryManager.cookieJar())
        # do not steal ownership
        self.cookieJar().setParent(self.__class__.primaryManager)
        
        self.connect(self, 
            SIGNAL('sslErrors(QNetworkReply *, const QList<QSslError> &)'), 
            self.__class__.primaryManager, 
            SIGNAL('sslErrors(QNetworkReply *, const QList<QSslError> &)'))
        self.connect(self, 
            SIGNAL('proxyAuthenticationRequired(const QNetworkProxy &, QAuthenticator *)'),
            self.__class__.primaryManager, 
            SIGNAL('proxyAuthenticationRequired(const QNetworkProxy &, QAuthenticator *)'))
        self.connect(self, 
            SIGNAL('authenticationRequired(QNetworkReply *, QAuthenticator *)'), 
            self.__class__.primaryManager, 
            SIGNAL('authenticationRequired(QNetworkReply *, QAuthenticator *)'))
        self.connect(self, SIGNAL("finished(QNetworkReply *)"), 
            self.__class__.primaryManager, SIGNAL("finished(QNetworkReply *)"))
    
    def createRequest(self, op, request, outgoingData = None):
        """
        Protected method to create a request.
        
        @param op the operation to be performed (QNetworkAccessManager.Operation)
        @param request reference to the request object (QNetworkRequest)
        @param outgoingData reference to an IODevice containing data to be sent
            (QIODevice)
        @return reference to the created reply object (QNetworkReply)
        """
        if self.primaryManager is not None and \
           self.__webPage is not None:
            pageRequest = request
            self.__webPage.populateNetworkRequest(pageRequest)
            return self.primaryManager.createRequest(op, request, outgoingData)
            
        return QNetworkAccessManager.createRequest(self, op, request, outgoingData)
