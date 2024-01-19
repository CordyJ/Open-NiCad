# -*- coding: utf-8 -*-

# Copyright (c) 2009 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the network block class.
"""

from PyQt4.QtCore import *

import Helpviewer.HelpWindow

from AdBlockBlockedNetworkReply import AdBlockBlockedNetworkReply

class AdBlockNetwork(QObject):
    """
    Class implementing a network block.
    """
    def block(self, request):
        """
        Public method to check for a network block.
        
        @return reply object (QNetworkReply) or None
        """
        url = request.url()
        
        if url.scheme() in ["data", "pyrc", "qthelp"]:
            return None
        
        manager = Helpviewer.HelpWindow.HelpWindow.adblockManager()
        if not manager.isEnabled():
            return None
        
        urlString = QString.fromUtf8(url.toEncoded())
        blockedRule = None
        blockingSubscription = None
        
        for subscription in manager.subscriptions():
            if subscription.allow(urlString):
                return None
            
            rule = subscription.block(urlString)
            if rule is not None:
                blockedRule = rule
                blockingSubscription = subscription
                break
        
        if blockedRule is not None:
            reply = AdBlockBlockedNetworkReply(request, blockedRule, self)
            return reply
        
        return None
