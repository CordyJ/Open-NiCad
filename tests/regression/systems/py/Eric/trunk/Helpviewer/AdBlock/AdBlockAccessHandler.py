# -*- coding: utf-8 -*-

# Copyright (c) 2009 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a scheme access handler for AdBlock URLs.
"""

from PyQt4.QtGui import QMessageBox
from PyQt4.QtNetwork import QNetworkAccessManager

from KdeQt import KQMessageBox

from AdBlockSubscription import AdBlockSubscription

import Helpviewer.HelpWindow
from Helpviewer.Network.SchemeAccessHandler import SchemeAccessHandler

class AdBlockAccessHandler(SchemeAccessHandler):
    """
    Class implementing a scheme access handler for AdBlock URLs.
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
        if op != QNetworkAccessManager.GetOperation:
            return None
        
        if request.url().path() != "subscribe":
            return None
        
        subscription = AdBlockSubscription(request.url(), 
                            Helpviewer.HelpWindow.HelpWindow.adblockManager())
        
        res = KQMessageBox.question(None,
            self.trUtf8("Subscribe?"),
            self.trUtf8("""<p>Subscribe to this AdBlock subscription?</p><p>%1</p>""")\
                .arg(subscription.title()),
            QMessageBox.StandardButtons(\
                QMessageBox.No | \
                QMessageBox.Yes))
        if res == QMessageBox.Yes:
            Helpviewer.HelpWindow.HelpWindow.adblockManager()\
                .addSubscription(subscription)
            dlg = Helpviewer.HelpWindow.HelpWindow.adblockManager().showDialog()
            model = dlg.model()
            dlg.setCurrentIndex(model.index(model.rowCount() - 1, 0))
            dlg.setFocus()
        
        return None
