# -*- coding: utf-8 -*-

# Copyright (c) 2003 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a dialog to show the output of the svn blame command.
"""

import os
import sys

import pysvn

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from SvnDialogMixin import SvnDialogMixin
from Ui_SvnBlameDialog import Ui_SvnBlameDialog

import Utilities

class SvnBlameDialog(QDialog, SvnDialogMixin, Ui_SvnBlameDialog):
    """
    Class implementing a dialog to show the output of the svn blame command.
    """
    def __init__(self, vcs, parent = None):
        """
        Constructor
        
        @param vcs reference to the vcs object
        @param parent parent widget (QWidget)
        """
        QDialog.__init__(self, parent)
        self.setupUi(self)
        SvnDialogMixin.__init__(self)
        
        self.buttonBox.button(QDialogButtonBox.Close).setEnabled(False)
        self.buttonBox.button(QDialogButtonBox.Cancel).setDefault(True)
        
        self.vcs = vcs
        
        self.blameList.headerItem().setText(self.blameList.columnCount(), "")
        font = QFont(self.blameList.font())
        if Utilities.isWindowsPlatform():
            font.setFamily("Lucida Console")
        else:
            font.setFamily("Monospace")
        self.blameList.setFont(font)
        
        self.client = self.vcs.getClient()
        self.client.callback_cancel = \
            self._clientCancelCallback
        self.client.callback_get_login = \
            self._clientLoginCallback
        self.client.callback_ssl_server_trust_prompt = \
            self._clientSslServerTrustPromptCallback
        
    def start(self, fn):
        """
        Public slot to start the svn status command.
        
        @param fn filename to show the log for (string)
        """
        self.errorGroup.hide()
        self.activateWindow()
        
        dname, fname = self.vcs.splitPath(fn)
        
        locker = QMutexLocker(self.vcs.vcsExecutionMutex)
        cwd = os.getcwd()
        os.chdir(dname)
        try:
            annotations = self.client.annotate(fname)
            locker.unlock()
            for annotation in annotations:
                self.__generateItem(annotation["revision"].number,
                    annotation["author"], annotation["number"] + 1, annotation["line"])
        except pysvn.ClientError, e:
            locker.unlock()
            self.__showError(e.args[0]+'\n')
        self.__finish()
        os.chdir(cwd)
        
    def __finish(self):
        """
        Private slot called when the process finished or the user pressed the button.
        """
        self.buttonBox.button(QDialogButtonBox.Close).setEnabled(True)
        self.buttonBox.button(QDialogButtonBox.Cancel).setEnabled(False)
        self.buttonBox.button(QDialogButtonBox.Close).setDefault(True)
        
        self.blameList.doItemsLayout()
        self.__resizeColumns()
        
        self._cancel()
        
    def on_buttonBox_clicked(self, button):
        """
        Private slot called by a button of the button box clicked.
        
        @param button button that was clicked (QAbstractButton)
        """
        if button == self.buttonBox.button(QDialogButtonBox.Close):
            self.close()
        elif button == self.buttonBox.button(QDialogButtonBox.Cancel):
            self.__finish()
        
    def __resizeColumns(self):
        """
        Private method to resize the list columns.
        """
        self.blameList.header().resizeSections(QHeaderView.ResizeToContents)
        self.blameList.header().setStretchLastSection(True)
        
    def __generateItem(self, revision, author, lineno, text):
        """
        Private method to generate a tag item in the taglist.
        
        @param revision revision string (integer)
        @param author author of the tag (string or QString)
        @param lineno line number (integer)
        @param text text of the line (string or QString)
        """
        itm = QTreeWidgetItem(self.blameList, 
            QStringList() << "%d" % revision << author << "%d" % lineno << text)
        itm.setTextAlignment(0, Qt.AlignRight)
        itm.setTextAlignment(2, Qt.AlignRight)
        
    def __showError(self, msg):
        """
        Private slot to show an error message.
        
        @param msg error message to show (string or QString)
        """
        self.errorGroup.show()
        self.errors.insertPlainText(msg)
        self.errors.ensureCursorVisible()
