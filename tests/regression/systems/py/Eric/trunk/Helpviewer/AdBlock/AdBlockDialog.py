# -*- coding: utf-8 -*-

# Copyright (c) 2009 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the AdBlock configuration dialog.
"""

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from E4Gui.E4TreeSortFilterProxyModel import E4TreeSortFilterProxyModel

import Helpviewer.HelpWindow

from Ui_AdBlockDialog import Ui_AdBlockDialog

from AdBlockModel import AdBlockModel
from AdBlockRule import AdBlockRule

import UI.PixmapCache

class AdBlockDialog(QDialog, Ui_AdBlockDialog):
    """
    Class implementing the AdBlock configuration dialog.
    """
    def __init__(self, parent = None):
        """
        Constructor
        """
        QDialog.__init__(self, parent)
        self.setupUi(self)
        
        self.clearButton.setIcon(UI.PixmapCache.getIcon("clearLeft.png"))
        
        self.__adBlockModel = AdBlockModel(self)
        self.__proxyModel = E4TreeSortFilterProxyModel(self)
        self.__proxyModel.setSourceModel(self.__adBlockModel)
        self.subscriptionsTree.setModel(self.__proxyModel)
        
        self.connect(self.searchEdit, SIGNAL("textChanged(QString)"), 
                     self.__proxyModel.setFilterFixedString)
        
        manager = Helpviewer.HelpWindow.HelpWindow.adblockManager()
        self.adBlockGroup.setChecked(manager.isEnabled())
        self.connect(self.adBlockGroup, SIGNAL("toggled(bool)"), 
                     manager.setEnabled)
        
        menu = QMenu(self)
        self.connect(menu, SIGNAL("aboutToShow()"), self.__aboutToShowActionMenu)
        self.actionButton.setMenu(menu)
        self.actionButton.setIcon(UI.PixmapCache.getIcon("adBlockAction.png"))
        self.actionButton.setPopupMode(QToolButton.InstantPopup)
        
        subscription = manager.customRules()
        subscriptionIndex = self.__adBlockModel.subscriptionIndex(subscription)
        self.subscriptionsTree.expand(self.__proxyModel.mapFromSource(subscriptionIndex))
    
    def model(self):
        """
        Public method to return a reference to the subscriptions tree model.
        """
        return self.subscriptionsTree.model()
    
    def setCurrentIndex(self, index):
        """
        Private slot to set the current index of the subscriptions tree.
        
        @param index index to be set (QModelIndex)
        """
        self.subscriptionsTree.setCurrentIndex(index)
    
    def __aboutToShowActionMenu(self):
        """
        Private slot to show the actions menu.
        """
        menu = self.actionButton.menu()
        menu.clear()
        
        menu.addAction(self.trUtf8("Add Custom Rule"), self.addCustomRule)
        
        menu.addAction(self.trUtf8("Learn more about writing rules..."), 
                       self.__learnAboutWritingFilters)
        
        menu.addSeparator()
        
        idx = self.__proxyModel.mapToSource(self.subscriptionsTree.currentIndex())
        
        act = menu.addAction(self.trUtf8("Update Subscription"), 
                             self.__updateSubscription)
        act.setEnabled(idx.isValid())
        
        menu.addAction(self.trUtf8("Browse Subscriptions..."), self.__browseSubscriptions)
        
        menu.addSeparator()
        
        act = menu.addAction(self.trUtf8("Remove Subscription"), 
                             self.__removeSubscription)
        act.setEnabled(idx.isValid())
    
    def addCustomRule(self, rule = ""):
        """
        Public slot to add a custom AdBlock rule.
        
        @param rule string defining the rule to be added (string or QString)
        """
        manager = Helpviewer.HelpWindow.HelpWindow.adblockManager()
        subscription = manager.customRules()
        assert subscription is not None
        subscription.addRule(AdBlockRule(rule))
        QApplication.processEvents()
        
        parent = self.__adBlockModel.subscriptionIndex(subscription)
        cnt = self.__adBlockModel.rowCount(parent)
        ruleIndex = self.__adBlockModel.index(cnt - 1, 0, parent)
        self.subscriptionsTree.expand(self.__proxyModel.mapFromSource(parent))
        self.subscriptionsTree.edit(self.__proxyModel.mapFromSource(ruleIndex))
    
    def __updateSubscription(self):
        """
        Private slot to update the selected subscription.
        """
        idx = self.__proxyModel.mapToSource(self.subscriptionsTree.currentIndex())
        if not idx.isValid():
            return
        if idx.parent().isValid():
            idx = idx.parent()
        subscription = self.__adBlockModel.subscription(idx)
        subscription.updateNow()
    
    def __browseSubscriptions(self):
        """
        Private slot to browse the list of available AdBlock subscriptions.
        """
        QDesktopServices.openUrl(QUrl("http://adblockplus.org/en/subscriptions"))
    
    def __learnAboutWritingFilters(self):
        """
        Private slot to show the web page about how to write filters.
        """
        QDesktopServices.openUrl(QUrl("http://adblockplus.org/en/filters"))
    
    def __removeSubscription(self):
        """
        Private slot to remove the selected subscription.
        """
        idx = self.__proxyModel.mapToSource(self.subscriptionsTree.currentIndex())
        if not idx.isValid():
            return
        if idx.parent().isValid():
            idx = idx.parent()
        subscription = self.__adBlockModel.subscription(idx)
        manager = Helpviewer.HelpWindow.HelpWindow.adblockManager()
        manager.removeSubscription(subscription)
