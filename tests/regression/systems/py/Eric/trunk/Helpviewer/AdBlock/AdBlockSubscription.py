# -*- coding: utf-8 -*-

# Copyright (c) 2009 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the AdBlock subscription class.
"""

import os

from PyQt4.QtCore import *
from PyQt4.QtNetwork import QNetworkRequest, QNetworkReply

from KdeQt import KQMessageBox

from AdBlockRule import AdBlockRule

import Helpviewer.HelpWindow

import Utilities

class AdBlockSubscription(QObject):
    """
    Class implementing the AdBlock subscription.
    
    @signal changed() emitted after the subscription has changed
    @signal rulesChanged() emitted after the subscription's rules have changed
    """
    def __init__(self, url, parent = None):
        """
        Constructor
        
        @param url AdBlock URL for the subscription (QUrl)
        @param parent reference to the parent object (QObject)
        """
        QObject.__init__(self, parent)
        
        self.__url = url.toEncoded()
        self.__enabled = False
        self.__downloading = None
        
        self.__title = QString()
        self.__location = QByteArray()
        self.__lastUpdate = QDateTime()
        
        self.__rules = []   # list containing all AdBlock rules
        
        self.__networkExceptionRules = []
        self.__networkBlockRules = []
        self.__pageRules = []
        
        self.__parseUrl(url)
    
    def __parseUrl(self, url):
        """
        Private method to parse the AdBlock URL for the subscription.
        
        @param url AdBlock URL for the subscription (QUrl)
        """
        if url.scheme() != "abp":
            return
        
        if url.path() != "subscribe":
            return
        
        self.__title = \
            QUrl.fromPercentEncoding(url.encodedQueryItemValue("title"))
        self.__enabled = \
            QUrl.fromPercentEncoding(url.encodedQueryItemValue("enabled")) != "false"
        self.__location = \
            QUrl.fromPercentEncoding(url.encodedQueryItemValue("location")).toUtf8()
        
        lastUpdateByteArray = url.encodedQueryItemValue("lastUpdate")
        lastUpdateString = QUrl.fromPercentEncoding(lastUpdateByteArray)
        self.__lastUpdate = QDateTime.fromString(lastUpdateString, Qt.ISODate)
        
        self.__loadRules()
    
    def url(self):
        """
        Public method to generate the url for this subscription.
        
        @return AdBlock URL for the subscription (QUrl)
        """
        url = QUrl()
        url.setScheme("abp")
        url.setPath("subscribe")
        
        queryItems = []
        queryItems.append((QString("location"), QString.fromUtf8(self.__location)))
        queryItems.append((QString("title"), self.__title))
        if not self.__enabled:
            queryItems.append((QString("enabled"), QString("false")))
        if self.__lastUpdate.isValid():
            queryItems.append((QString("lastUpdate"), 
                               self.__lastUpdate.toString(Qt.ISODate)))
        url.setQueryItems(queryItems)
        return url
    
    def isEnabled(self):
        """
        Public method to check, if the subscription is enabled.
        
        @return flag indicating the enabled status (boolean)
        """
        return self.__enabled
    
    def setEnabled(self, enabled):
        """
        Public method to set the enabled status.
        
        @param enabled flag indicating the enabled status (boolean)
        """
        if self.__enabled == enabled:
            return
        
        self.__enabled = enabled
        self.__populateCache()
        self.emit(SIGNAL("changed()"))
    
    def title(self):
        """
        Public method to get the subscription title.
        
        @return subscription title (QString)
        """
        return self.__title
    
    def setTitle(self, title):
        """
        Public method to set the subscription title.
        
        @param title subscription title (string or QString)
        """
        if self.__title == title:
            return
        
        self.__title = QString(title)
        self.emit(SIGNAL("changed()"))
    
    def location(self):
        """
        Public method to get the subscription location.
        
        @return URL of the subscription location (QUrl)
        """
        return QUrl.fromEncoded(self.__location)
    
    def setLocation(self, url):
        """
        Public method to set the subscription location.
        
        @param url URL of the subscription location (QUrl)
        """
        if url == self.location():
            return
        
        self.__location = url.toEncoded()
        self.__lastUpdate = QDateTime()
        self.emit(SIGNAL("changed()"))
    
    def lastUpdate(self):
        """
        Public method to get the date and time of the last update.
        
        @return date and time of the last update (QDateTime)
        """
        return self.__lastUpdate
    
    def rulesFileName(self):
        """
        Public method to get the name of the rules file.
        
        @return name of the rules file (QString)
        """
        if self.location().scheme() == "file":
            return self.location().toLocalFile()
        
        if self.__location.isEmpty():
            return QString()
        
        sha1 = QCryptographicHash.hash(self.__location, QCryptographicHash.Sha1).toHex()
        dataDir = os.path.join(Utilities.getConfigDir(), "browser", "subscriptions")
        if not os.path.exists(dataDir):
            os.makedirs(dataDir)
        fileName = QString(os.path.join(dataDir, "adblock_subscription_%s" % sha1))
        return fileName
    
    def __loadRules(self):
        """
        Private method to load the rules of the subscription.
        """
        fileName = self.rulesFileName()
        f = QFile(fileName)
        if f.exists():
            if not f.open(QIODevice.ReadOnly):
                KQMessageBox.warning(None,
                    self.trUtf8("Load subscription rules"),
                    self.trUtf8("""Unable to open adblock file '%1' for reading.""")\
                        .arg(fileName))
            else:
                textStream = QTextStream(f)
                header = textStream.readLine(1024)
                if not header.startsWith("[Adblock"):
                    KQMessageBox.warning(None,
                        self.trUtf8("Load subscription rules"),
                        self.trUtf8("""Adblock file '%1' does not start with [Adblock.""")\
                            .arg(fileName))
                    f.close()
                    f.remove()
                    self.__lastUpdate = QDateTime()
                else:
                    self.__rules = []
                    while not textStream.atEnd():
                        line = textStream.readLine()
                        self.__rules.append(AdBlockRule(line))
                    self.__populateCache()
                    self.emit(SIGNAL("changed()"))
        
        if not self.__lastUpdate.isValid() or \
           self.__lastUpdate.addDays(7) < QDateTime.currentDateTime():
            self.updateNow()
    
    def updateNow(self):
        """
        Public method to update the subscription immediately.
        """
        if self.__downloading is not None:
            return
        
        if not self.location().isValid():
            return
        
        if self.location().scheme() == "file":
            self.__lastUpdate = QDateTime.currentDateTime()
            self.__loadRules()
            self.emit(SIGNAL("changed()"))
            return
        
        request = QNetworkRequest(self.location())
        self.__downloading = \
            Helpviewer.HelpWindow.HelpWindow.networkAccessManager().get(request)
        self.connect(self.__downloading, SIGNAL("finished()"), self.__rulesDownloaded)
    
    def __rulesDownloaded(self):
        """
        Private slot to deal with the downloaded rules.
        """
        reply = self.sender()
        
        response = reply.readAll()
        redirect = reply.attribute(QNetworkRequest.RedirectionTargetAttribute).toUrl()
        reply.close()
        reply.deleteLater()
        
        if reply.error() != QNetworkReply.NoError:
            KQMessageBox.warning(None,
                self.trUtf8("Downloading subscription rules"),
                self.trUtf8("""<p>Subscription rules could not be downloaded.</p>"""
                            """<p>Error: %1</p>""").arg(reply.errorString()))
            return
        
        if redirect.isValid():
            request = QNetworkRequest(redirect)
            self.__downloading = \
                Helpviewer.HelpWindow.HelpWindow.networkAccessManager().get(request)
            self.connect(self.__downloading, SIGNAL("finished()"), self.__rulesDownloaded)
            return
        
        if response.isEmpty():
            KQMessageBox.warning(None,
                self.trUtf8("Downloading subscription rules"),
                self.trUtf8("""Got empty subscription rules."""))
            return
        
        fileName = self.rulesFileName()
        f = QFile(fileName)
        if not f.open(QIODevice.ReadWrite):
            KQMessageBox.warning(None,
                self.trUtf8("Downloading subscription rules"),
                self.trUtf8("""Unable to open adblock file '%1' for writing.""")\
                    .arg(fileName))
            return
        f.write(response)
        self.__lastUpdate = QDateTime.currentDateTime()
        self.__loadRules()
        self.emit(SIGNAL("changed()"))
        self.__downloading = None
    
    def saveRules(self):
        """
        Public method to save the subscription rules.
        """
        fileName = self.rulesFileName()
        if fileName.isEmpty():
            return
        
        f = QFile(fileName)
        if not f.open(QIODevice.ReadWrite | QIODevice.Truncate):
            KQMessageBox.warning(None,
                self.trUtf8("Saving subscription rules"),
                self.trUtf8("""Unable to open adblock file '%1' for writing.""")\
                    .arg(fileName))
            return
        
        textStream = QTextStream(f)
        textStream << QString("[Adblock Plus 0.7.1]\n")
        for rule in self.__rules:
            textStream << rule.filter() << "\n"
    
    def pageRules(self):
        """
        Public method to get the page rules of the subscription.
        
        @return list of rule objects (list of AdBlockRule)
        """
        return self.__pageRules[:]
    
    def allow(self, urlString):
        """
        Public method to check, if the given URL is allowed.
        
        @return reference to the rule object or None (AdBlockRule)
        """
        for rule in self.__networkExceptionRules:
            if rule.networkMatch(urlString):
                return rule
        
        return None
    
    def block(self, urlString):
        """
        Public method to check, if the given URL should be blocked.
        
        @return reference to the rule object or None (AdBlockRule)
        """
        for rule in self.__networkBlockRules:
            if rule.networkMatch(urlString):
                return rule
        
        return None
    
    def allRules(self):
        """
        Public method to get the list of rules.
        
        @return list of rules (list of AdBlockRule)
        """
        return self.__rules[:]
    
    def addRule(self, rule):
        """
        Public method to add a rule.
        
        @param rule reference to the rule to add (AdBlockRule)
        """
        self.__rules.append(rule)
        self.__populateCache()
        self.emit(SIGNAL("rulesChanged()"))
    
    def removeRule(self, offset):
        """
        Public method to remove a rule given the offset.
        
        @param offset offset of the rule to remove (integer)
        """
        if offset < 0 or offset > len(self.__rules):
            return
        
        del self.__rules[offset]
        self.__populateCache()
        self.emit(SIGNAL("rulesChanged()"))
    
    def replaceRule(self, rule, offset):
        """
        Public method to replace a rule given the offset.
        
        @param rule reference to the rule to set (AdBlockRule)
        @param offset offset of the rule to remove (integer)
        """
        self.__rules[offset] = rule
        self.__populateCache()
        self.emit(SIGNAL("rulesChanged()"))
    
    def __populateCache(self):
        """
        Private method to populate the various rule caches.
        """
        self.__networkBlockRules = []
        self.__networkExceptionRules = []
        self.__pageRules = []
        if not self.isEnabled():
            return
        
        for rule in self.__rules:
            if not rule.isEnabled():
                continue
            
            if rule.isCSSRule():
                self.__pageRules.append(rule)
            elif rule.isException():
                self.__networkExceptionRules.append(rule)
            else:
                self.__networkBlockRules.append(rule)
