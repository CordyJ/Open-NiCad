# -*- coding: utf-8 -*-

# Copyright (c) 2009 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the AdBlock manager.
"""

import os

from PyQt4.QtCore import *

import Helpviewer.HelpWindow

from AdBlockNetwork import AdBlockNetwork
from AdBlockPage import AdBlockPage
from AdBlockSubscription import AdBlockSubscription
from AdBlockDialog import AdBlockDialog

from Utilities.AutoSaver import AutoSaver
import Utilities
import Preferences

class AdBlockManager(QObject):
    """
    Class implementing the AdBlock manager.
    
    @signal rulesChanged() emitted after some rule has changed
    """
    def __init__(self, parent = None):
        """
        Constructor
        
        @param parent reference to the parent object (QObject)
        """
        QObject.__init__(self, parent)
        
        self.__loaded = False
        self.__enabled = False
        self.__adBlockDialog = None
        self.__adBlockNetwork = None
        self.__adBlockPage = None
        self.__subscriptions = []
        self.__saveTimer = AutoSaver(self, self.save)
        
        self.connect(self, SIGNAL("rulesChanged()"), self.__saveTimer.changeOccurred)
    
    def close(self):
        """
        Public method to close the open search engines manager.
        """
        self.__saveTimer.saveIfNeccessary()
    
    def isEnabled(self):
        """
        Public method to check, if blocking ads is enabled.
        
        @return flag indicating the enabled state (boolean)
        """
        if not self.__loaded:
            self.load()
        
        return self.__enabled
    
    def setEnabled(self, enabled):
        """
        Public slot to set the enabled state.
        
        @param enabled flag indicating the enabled state (boolean)
        """
        if self.isEnabled() == enabled:
            return
        
        self.__enabled = enabled
        self.emit(SIGNAL("rulesChanged()"))
    
    def network(self):
        """
        Public method to get a reference to the network block object.
        
        @return reference to the network block object (AdBlockNetwork)
        """
        if self.__adBlockNetwork is None:
            self.__adBlockNetwork = AdBlockNetwork(self)
        return self.__adBlockNetwork
    
    def page(self):
        """
        Public method to get a reference to the page block object.
        
        @return reference to the page block object (AdBlockPage)
        """
        if self.__adBlockPage is None:
            self.__adBlockPage = AdBlockPage(self)
        return self.__adBlockPage
    
    def __customSubscriptionLocation(self):
        """
        Private method to generate the path for custom subscriptions.
        
        @return URL for custom subscriptions (QUrl)
        """
        dataDir = os.path.join(Utilities.getConfigDir(), "browser", "subscriptions")
        if not os.path.exists(dataDir):
            os.makedirs(dataDir)
        fileName = os.path.join(dataDir, "adblock_subscription_custom")
        return QUrl.fromLocalFile(fileName)
    
    def __customSubscriptionUrl(self):
        """
        Private method to generate the URL for custom subscriptions.
        
        @return URL for custom subscriptions (QUrl)
        """
        location = self.__customSubscriptionLocation()
        encodedUrl = QString.fromUtf8(location.toEncoded())
        url = QUrl("abp:subscribe?location=%s&title=%s" % \
            (encodedUrl, self.trUtf8("Custom Rules")))
        return url
    
    def customRules(self):
        """
        Public method to get a subscription for custom rules.
        
        @return subscription object for custom rules (AdBlockSubscription)
        """
        location = self.__customSubscriptionLocation()
        for subscription in self.__subscriptions:
            if subscription.location() == location:
                return subscription
        
        url = self.__customSubscriptionUrl()
        customAdBlockSubscription = AdBlockSubscription(url, self)
        self.addSubscription(customAdBlockSubscription)
        return customAdBlockSubscription
    
    def subscriptions(self):
        """
        Public method to get all subscriptions.
        
        @return list of subscriptions (list of AdBlockSubscription)
        """
        if not self.__loaded:
            self.load()
        
        return self.__subscriptions[:]
    
    def removeSubscription(self, subscription):
        """
        Public method to remove an AdBlock subscription.
        
        @param subscription AdBlock subscription to be removed (AdBlockSubscription)
        """
        if subscription is None:
            return
        
        try:
            self.__subscriptions.remove(subscription)
            rulesFileName = subscription.rulesFileName()
            if subscription.parent() == self:
                subscription.deleteLater()
            QFile.remove(rulesFileName)
            self.emit(SIGNAL("rulesChanged()"))
        except ValueError:
            pass
    
    def addSubscription(self, subscription):
        """
        Public method to add an AdBlock subscription.
        
        @param subscription AdBlock subscription to be added (AdBlockSubscription)
        """
        if subscription is None:
            return
        
        self.__subscriptions.append(subscription)
        
        self.connect(subscription, SIGNAL("rulesChanged()"), 
                     self, SIGNAL("rulesChanged()"))
        self.connect(subscription, SIGNAL("changed()"), 
                     self, SIGNAL("rulesChanged()"))
        
        self.emit(SIGNAL("rulesChanged()"))
    
    def save(self):
        """
        Public method to save the AdBlock subscriptions.
        """
        if not self.__loaded:
            return
        
        Preferences.setHelp("AdBlockEnabled", int(self.__enabled))
        subscriptions = QStringList()
        for subscription in self.__subscriptions:
            if subscription is None:
                continue
            subscriptions.append(QString.fromUtf8(subscription.url().toEncoded()))
            subscription.saveRules()
        Preferences.setHelp("AdBlockSubscriptions", subscriptions)
    
    def load(self):
        """
        Public method to load the AdBlock subscriptions.
        """
        if self.__loaded:
            return
        
        self.__loaded = True
        
        self.__enabled = bool(Preferences.getHelp("AdBlockEnabled"))
        
        defaultSubscriptions = QStringList()
        defaultSubscriptions.append(
            QString.fromUtf8(self.__customSubscriptionUrl().toEncoded()))
        defaultSubscriptions.append(
            "abp:subscribe?location=http://adblockplus.mozdev.org/easylist/easylist.txt&title=EasyList")
        
        subscriptions = Preferences.getHelp("AdBlockSubscriptions")
        if len(subscriptions) == 0:
            subscriptions = defaultSubscriptions
        for subscription in subscriptions:
            url = QUrl.fromEncoded(subscription.toUtf8())
            adBlockSubscription = AdBlockSubscription(url, self)
            self.connect(adBlockSubscription, SIGNAL("rulesChanged()"), 
                         self, SIGNAL("rulesChanged()"))
            self.connect(adBlockSubscription, SIGNAL("changed()"), 
                         self, SIGNAL("rulesChanged()"))
            self.__subscriptions.append(adBlockSubscription)
    
    def showDialog(self):
        """
        Public slot to show the AdBlock subscription management dialog.
        """
        if self.__adBlockDialog is None:
            self.__adBlockDialog = AdBlockDialog()
        
        self.__adBlockDialog.show()
        return self.__adBlockDialog
