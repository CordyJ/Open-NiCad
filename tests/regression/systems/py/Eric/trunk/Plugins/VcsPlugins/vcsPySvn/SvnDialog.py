# -*- coding: utf-8 -*-

# Copyright (c) 2003 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a dialog to show the output of a pysvn action.
"""

import os

import pysvn

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from SvnConst import svnNotifyActionMap

from SvnDialogMixin import SvnDialogMixin
from Ui_SvnDialog import Ui_SvnDialog

import Preferences

class SvnDialog(QDialog, SvnDialogMixin, Ui_SvnDialog):
    """
    Class implementing a dialog to show the output of a pysvn action.
    """
    def __init__(self, text, command, pysvnClient, parent = None, log = ""):
        """
        Constructor
        
        @param text text to be shown by the label (string or QString)
        @param command svn command to be executed (display purposes only)
            (string or QString)
        @param pysvnClient reference to the pysvn client object (pysvn.Client)
        @keyparam parent parent widget (QWidget)
        @keyparam log optional log message (string or QString)
        """
        QDialog.__init__(self, parent)
        self.setupUi(self)
        SvnDialogMixin.__init__(self, log)
        
        self.buttonBox.button(QDialogButtonBox.Close).setEnabled(False)
        self.buttonBox.button(QDialogButtonBox.Cancel).setDefault(True)
        
        self.outputGroup.setTitle(text)
        self.errorGroup.hide()
        
        pysvnClient.callback_cancel = \
            self._clientCancelCallback
        
        pysvnClient.callback_notify = \
            self._clientNotifyCallback
        pysvnClient.callback_get_login = \
            self._clientLoginCallback
        pysvnClient.callback_ssl_server_trust_prompt = \
            self._clientSslServerTrustPromptCallback
        pysvnClient.callback_get_log_message = \
            self._clientLogCallback
        
        self.__hasAddOrDelete = False
        
        command = unicode(command)
        if command:
            self.resultbox.append(command)
            self.resultbox.append('')
        
        self.show()
        QApplication.processEvents()
        
    def _clientNotifyCallback(self, eventDict):
        """
        Protected method called by the client to send events
        
        @param eventDict dictionary containing the notification event
        """
        msg = QString()
        if eventDict["action"] == pysvn.wc_notify_action.update_completed:
            msg = self.trUtf8("Revision %1.\n").arg(eventDict["revision"].number)
        elif eventDict["path"] != "" and \
             svnNotifyActionMap[eventDict["action"]] is not None:
            mime = eventDict["mime_type"] == "application/octet-stream" and \
                self.trUtf8(" (binary)") or QString("")
            msg = self.trUtf8("%1 %2%3\n")\
                .arg(self.trUtf8(svnNotifyActionMap[eventDict["action"]]))\
                .arg(eventDict["path"])\
                .arg(mime)
            if eventDict["action"] in \
               [pysvn.wc_notify_action.add, pysvn.wc_notify_action.commit_added, 
                pysvn.wc_notify_action.commit_deleted, pysvn.wc_notify_action.delete, 
                pysvn.wc_notify_action.update_add, pysvn.wc_notify_action.update_delete]:
                self.__hasAddOrDelete = True
        if not msg.isEmpty():
            self.showMessage(msg)
        
    def showMessage(self, msg):
        """
        Public slot to show a message.
        
        @param msg message to show (string or QString)
        """
        self.resultbox.insertPlainText(msg)
        self.resultbox.ensureCursorVisible()
        QApplication.processEvents()
        
    def showError(self, msg):
        """
        Public slot to show an error message.
        
        @param msg error message to show (string or QString)
        """
        self.errorGroup.show()
        self.errors.insertPlainText(msg)
        self.errors.ensureCursorVisible()
        QApplication.processEvents()
        
    def finish(self):
        """
        Public slot called when the process finished or the user pressed the button.
        """
        self.buttonBox.button(QDialogButtonBox.Close).setEnabled(True)
        self.buttonBox.button(QDialogButtonBox.Cancel).setEnabled(False)
        self.buttonBox.button(QDialogButtonBox.Close).setDefault(True)
        
        self._cancel()
        
        if Preferences.getVCS("AutoClose"):
            self.accept()
        
    def on_buttonBox_clicked(self, button):
        """
        Private slot called by a button of the button box clicked.
        
        @param button button that was clicked (QAbstractButton)
        """
        if button == self.buttonBox.button(QDialogButtonBox.Close):
            self.close()
        elif button == self.buttonBox.button(QDialogButtonBox.Cancel):
            self.finish()
        
    def hasAddOrDelete(self):
        """
        Public method to check, if the last action contained an add or delete.
        """
        return self.__hasAddOrDelete
