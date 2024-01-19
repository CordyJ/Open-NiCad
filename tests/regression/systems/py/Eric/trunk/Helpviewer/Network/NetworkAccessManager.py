# -*- coding: utf-8 -*-

# Copyright (c) 2009 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a QNetworkAccessManager subclass.
"""

import os

from PyQt4.QtCore import *
from PyQt4.QtGui import QDialog, QMessageBox
from PyQt4.QtNetwork import QNetworkAccessManager, QNetworkRequest, \
    QNetworkProxy
try:
    from PyQt4.QtNetwork import QSsl, QSslCertificate, QSslConfiguration, QSslSocket
    SSL_AVAILABLE = True
except ImportError:
    SSL_AVAILABLE = False

from KdeQt import KQMessageBox

from UI.AuthenticationDialog import AuthenticationDialog
import UI.PixmapCache

from Helpviewer.HelpLanguagesDialog import HelpLanguagesDialog
import Helpviewer.HelpWindow

from NetworkReply import NetworkReply
from NetworkProtocolUnknownErrorReply import NetworkProtocolUnknownErrorReply
from NetworkDiskCache import NetworkDiskCache

from QtHelpAccessHandler import QtHelpAccessHandler
from PyrcAccessHandler import PyrcAccessHandler
from AboutAccessHandler import AboutAccessHandler

from Helpviewer.AdBlock.AdBlockAccessHandler import AdBlockAccessHandler

import Preferences
import Utilities

class NetworkAccessManager(QNetworkAccessManager):
    """
    Class implementing a QNetworkAccessManager subclass.
    
    @signal requestCreated(QNetworkAccessManager::Operation, const QNetworkRequest&, QNetworkReply*)
        emitted after the request has been created
    """
    def __init__(self, engine, parent = None):
        """
        Constructor
        
        @param engine reference to the help engine (QHelpEngine)
        @param parent reference to the parent object (QObject)
        """
        QNetworkAccessManager.__init__(self, parent)
        
        self.__adblockNetwork = None
        
        self.__schemeHandlers = {}  # dictionary of scheme handlers
        
        self.__setAccessManagerProxy()
        self.__setDiskCache()
        self.languagesChanged()
        
        if SSL_AVAILABLE:
            sslCfg = QSslConfiguration.defaultConfiguration()
            caList = sslCfg.caCertificates()
            caNew = QSslCertificate.fromData(Preferences.Prefs.settings\
                .value("Help/CaCertificates").toByteArray())
            for cert in caNew:
                caList.append(cert)
            sslCfg.setCaCertificates(caList)
            QSslConfiguration.setDefaultConfiguration(sslCfg)
            
            self.connect(self, 
                SIGNAL('sslErrors(QNetworkReply *, const QList<QSslError> &)'), 
                self.__sslErrors)
        
        self.connect(self, 
            SIGNAL('proxyAuthenticationRequired(const QNetworkProxy &, QAuthenticator *)'),
            self.__proxyAuthenticationRequired)
        self.connect(self, 
            SIGNAL('authenticationRequired(QNetworkReply *, QAuthenticator *)'), 
            self.__authenticationRequired)
        
        # register scheme handlers
        self.setSchemeHandler("qthelp", QtHelpAccessHandler(engine, self))
        self.setSchemeHandler("pyrc", PyrcAccessHandler(self))
        self.setSchemeHandler("about", AboutAccessHandler(self))
        self.setSchemeHandler("abp", AdBlockAccessHandler(self))
    
    def setSchemeHandler(self, scheme, handler):
        """
        Public method to register a scheme handler.
        
        @param scheme access scheme (string or QString)
        @param handler reference to the scheme handler object (SchemeAccessHandler)
        """
        self.__schemeHandlers[unicode(scheme)] = handler
    
    def createRequest(self, op, request, outgoingData = None):
        """
        Protected method to create a request.
        
        @param op the operation to be performed (QNetworkAccessManager.Operation)
        @param request reference to the request object (QNetworkRequest)
        @param outgoingData reference to an IODevice containing data to be sent
            (QIODevice)
        @return reference to the created reply object (QNetworkReply)
        """
        scheme = request.url().scheme()
        if scheme == "https" and (not SSL_AVAILABLE or not QSslSocket.supportsSsl()):
            return NetworkProtocolUnknownErrorReply(scheme)
        
        if op == QNetworkAccessManager.PostOperation and outgoingData is not None:
            outgoingDataByteArray = outgoingData.peek(1024 * 1024)
            Helpviewer.HelpWindow.HelpWindow.passwordManager().post(
                request, outgoingDataByteArray)
        
        reply = None
        if unicode(scheme) in self.__schemeHandlers:
            reply = self.__schemeHandlers[unicode(scheme)]\
                        .createRequest(op, request, outgoingData)
        if reply is not None:
            return reply
        
        if not self.__acceptLanguage.isEmpty():
            req = QNetworkRequest(request)
            req.setRawHeader("Accept-Language", self.__acceptLanguage)
        else:
            req = request
        
        # AdBlock code
        if op == QNetworkAccessManager.GetOperation:
            if self.__adblockNetwork is None:
                self.__adblockNetwork = \
                    Helpviewer.HelpWindow.HelpWindow.adblockManager().network()
            reply = self.__adblockNetwork.block(req)
            if reply is not None:
                return reply
        
        reply = QNetworkAccessManager.createRequest(self, op, req, outgoingData)
        self.emit(SIGNAL("requestCreated(QNetworkAccessManager::Operation, const QNetworkRequest&, QNetworkReply*)"), 
                  op, req, reply)
        
        return reply
    
    def __setAccessManagerProxy(self):
        """
        Private method  to set the proxy used by the network access manager.
        """
        if Preferences.getUI("UseProxy"):
            host = Preferences.getUI("ProxyHost")
            if host.isEmpty():
                KQMessageBox.critical(None,
                    self.trUtf8("Web Browser"),
                    self.trUtf8("""Proxy usage was activated"""
                                """ but no proxy host configured."""))
                return
            else:
                pProxyType = Preferences.getUI("ProxyType")
                if pProxyType == 0:
                    proxyType = QNetworkProxy.HttpProxy
                elif pProxyType == 1:
                    proxyType = QNetworkProxy.HttpCachingProxy
                elif pProxyType == 2:
                    proxyType = QNetworkProxy.Socks5Proxy
                self.__proxy = QNetworkProxy(proxyType, host, 
                    Preferences.getUI("ProxyPort"),
                    Preferences.getUI("ProxyUser"),
                    Preferences.getUI("ProxyPassword"))
                if qVersion() >= '4.5.0':
                    self.__proxy.setCapabilities(QNetworkProxy.Capabilities(
                        QNetworkProxy.CachingCapability | \
                        QNetworkProxy.HostNameLookupCapability))
        else:
            self.__proxy = QNetworkProxy(QNetworkProxy.NoProxy)
        self.setProxy(self.__proxy)
    
    def __authenticationRequired(self, reply, auth):
        """
        Private slot to handle an authentication request.
        
        @param reply reference to the reply object (QNetworkReply)
        @param auth reference to the authenticator object (QAuthenticator)
        """
        urlRoot = QString("%1://%2")\
            .arg(reply.url().scheme()).arg(reply.url().authority())
        if auth.realm().isEmpty():
            info = self.trUtf8("<b>Enter username and password for '%1'</b>")\
                .arg(urlRoot)
        else:
            info = self.trUtf8("<b>Enter username and password for '%1', realm '%2'</b>")\
                .arg(urlRoot).arg(auth.realm())
        
        dlg = AuthenticationDialog(info, auth.user(), 
                                   Preferences.getHelp("SavePasswords"), 
                                   Preferences.getHelp("SavePasswords"))
        if Preferences.getHelp("SavePasswords"):
            username, password = \
                Helpviewer.HelpWindow.HelpWindow.passwordManager().getLogin(
                    reply.url(), auth.realm())
            if username:
                dlg.setData(username, password)
        if dlg.exec_() == QDialog.Accepted:
            username, password = dlg.getData()
            auth.setUser(username)
            auth.setPassword(password)
            if Preferences.getHelp("SavePasswords"):
                Helpviewer.HelpWindow.HelpWindow.passwordManager().setLogin(
                    reply.url(), auth.realm(), username, password)
    
    def __proxyAuthenticationRequired(self, proxy, auth):
        """
        Private slot to handle a proxy authentication request.
        
        @param proxy reference to the proxy object (QNetworkProxy)
        @param auth reference to the authenticator object (QAuthenticator)
        """
        info = self.trUtf8("<b>Connect to proxy '%1' using:</b>")\
            .arg(Qt.escape(proxy.hostName()))
        
        dlg = AuthenticationDialog(info, proxy.user(), True)
        if dlg.exec_() == QDialog.Accepted:
            username, password = dlg.getData()
            auth.setUser(username)
            auth.setPassword(password)
            if dlg.shallSave():
                Preferences.setUI("ProxyUser", username)
                Preferences.setUI("ProxyPassword", password)
                self.__proxy.setUser(username)
                self.__proxy.setPassword(password)
    
    def __sslErrors(self, reply, errors):
        """
        Private slot to handle SSL errors.
        
        @param reply reference to the reply object (QNetworkReply)
        @param errors list of SSL errors (list of QSslError)
        """
        caMerge = QSslCertificate.fromData(Preferences.Prefs.settings\
            .value("Help/CaCertificates").toByteArray())
        caNew = []
        
        errorStrings = QStringList()
        for err in errors:
            if err.certificate() in caMerge:
                continue
            errorStrings.append(err.errorString())
            if not err.certificate().isNull():
                caNew.append(err.certificate())
        if errorStrings.isEmpty():
            reply.ignoreSslErrors()
            return
        
        errorString = errorStrings.join('.</li><li>')
        ret = KQMessageBox.warning(None,
            self.trUtf8("SSL Errors"),
            self.trUtf8("""<p>SSL Errors for <br /><b>%1</b>"""
                        """<ul><li>%2</li></ul></p>"""
                        """<p>Do you want to ignore these errors?</p>""")\
                .arg(reply.url().toString()).arg(errorString),
            QMessageBox.StandardButtons(
                QMessageBox.No | \
                QMessageBox.Yes),
            QMessageBox.No)
        
        if ret == QMessageBox.Yes:
            if len(caNew) > 0:
                certinfos = QStringList()
                for cert in caNew:
                    certinfos.append(self.__certToString(cert))
                ret = KQMessageBox.question(None,
                    self.trUtf8("Certificates"),
                    self.trUtf8("""<p>Certificates:<br/>%1<br/>"""
                                """Do you want to accept all these certificates?</p>""")\
                        .arg(certinfos.join("")),
                    QMessageBox.StandardButtons(\
                        QMessageBox.No | \
                        QMessageBox.Yes),
                    QMessageBox.No)
                if ret == QMessageBox.Yes:
                    for cert in caNew:
                        caMerge.append(cert)
                    
                    sslCfg = QSslConfiguration.defaultConfiguration()
                    caList = sslCfg.caCertificates()
                    for cert in caNew:
                        caList.append(cert)
                    sslCfg.setCaCertificates(caList)
                    QSslConfiguration.setDefaultConfiguration(sslCfg)
                    reply.setSslConfiguration(sslCfg)
                    
                    pems = QByteArray()
                    for cert in caMerge:
                        pems.append(cert.toPem() + '\n')
                    Preferences.Prefs.settings.setValue("Help/CaCertificates", 
                                                        QVariant(pems))
            
            reply.ignoreSslErrors()
    
    def __certToString(self, cert):
        """
        Private method to convert a certificate to a formatted string.
        
        @param cert certificate to convert (QSslCertificate)
        @return formatted string (QString)
        """
        result = QString("<p>")
        
        result.append(cert.subjectInfo(QSslCertificate.CommonName))
        
        result.append(self.trUtf8("<br/>Issuer: %1")\
            .arg(cert.issuerInfo(QSslCertificate.CommonName)))
        
        result.append(self.trUtf8("<br/>Not valid before: %1<br/>Valid Until: %2")\
            .arg(cert.effectiveDate().toString(Qt.ISODate))\
            .arg(cert.expiryDate().toString(Qt.ISODate)))
        
        names = cert.alternateSubjectNames()
        tmpList = names.get(QSsl.DnsEntry, QStringList())
        if not tmpList.isEmpty():
            result.append(self.trUtf8("<br/>Alternate Names:<ul><li>%1</li></ul>")\
                .arg(tmpList.join("</li><li>")))
        
        result.append("</p>")
        
        return result
    
    def preferencesChanged(self):
        """
        Public slot to signal a change of preferences.
        """
        self.__setAccessManagerProxy()
        self.__setDiskCache()
    
    def languagesChanged(self):
        """
        Public slot to (re-)load the list of accepted languages.
        """
        languages = Preferences.Prefs.settings.value(
            "Help/AcceptLanguages", 
            QVariant(HelpLanguagesDialog.defaultAcceptLanguages()))\
            .toStringList()
        self.__acceptLanguage = HelpLanguagesDialog.httpString(languages)
    
    def __setDiskCache(self):
        """
        Private method to set the disk cache.
        """
        if NetworkDiskCache is not None:
            if Preferences.getHelp("DiskCacheEnabled"):
                diskCache = NetworkDiskCache(self)
                location = os.path.join(Utilities.getConfigDir(), "browser", 'cache')
                size = Preferences.getHelp("DiskCacheSize") * 1024 * 1024
                diskCache.setCacheDirectory(location)
                diskCache.setMaximumCacheSize(size)
            else:
                diskCache = None
            self.setCache(diskCache)
