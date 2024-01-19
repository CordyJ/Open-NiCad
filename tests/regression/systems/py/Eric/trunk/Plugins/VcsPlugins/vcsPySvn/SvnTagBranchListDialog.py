# -*- coding: utf-8 -*-

# Copyright (c) 2003 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a dialog to show a list of tags or branches.
"""

import os

import pysvn

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from KdeQt import KQMessageBox, KQInputDialog

from SvnUtilities import formatTime

from SvnDialogMixin import SvnDialogMixin
from Ui_SvnTagBranchListDialog import Ui_SvnTagBranchListDialog

class SvnTagBranchListDialog(QDialog, SvnDialogMixin, Ui_SvnTagBranchListDialog):
    """
    Class implementing a dialog to show a list of tags or branches.
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
        
        self.tagList.headerItem().setText(self.tagList.columnCount(), "")
        self.tagList.header().setSortIndicator(3, Qt.AscendingOrder)
        
        self.client = self.vcs.getClient()
        self.client.callback_cancel = \
            self._clientCancelCallback
        self.client.callback_get_login = \
            self._clientLoginCallback
        self.client.callback_ssl_server_trust_prompt = \
            self._clientSslServerTrustPromptCallback
        
    def start(self, path, tags = True):
        """
        Public slot to start the svn status command.
        
        @param path name of directory to be listed (string)
        @param tags flag indicating a list of tags is requested
                (False = branches, True = tags)
        """
        self.errorGroup.hide()
        
        if not tags:
            self.setWindowTitle(self.trUtf8("Subversion Branches List"))
        self.activateWindow()
        QApplication.processEvents()
        
        dname, fname = self.vcs.splitPath(path)
        
        reposURL = self.vcs.svnGetReposName(dname)
        if reposURL is None:
            KQMessageBox.critical(None,
                self.trUtf8("Subversion Error"),
                self.trUtf8("""The URL of the project repository could not be"""
                    """ retrieved from the working copy. The list operation will"""
                    """ be aborted"""))
            self.close()
            return False
        
        if self.vcs.otherData["standardLayout"]:
            # determine the base path of the project in the repository
            rx_base = QRegExp('(.+)/(trunk|tags|branches).*')
            if not rx_base.exactMatch(reposURL):
                KQMessageBox.critical(None,
                    self.trUtf8("Subversion Error"),
                    self.trUtf8("""The URL of the project repository has an"""
                        """ invalid format. The list operation will"""
                        """ be aborted"""))
                return False
            
            reposRoot = unicode(rx_base.cap(1))
            
            if tags:
                path = "%s/tags" % reposRoot
            else:
                path = "%s/branches" % reposRoot
        else:
            reposPath, ok = KQInputDialog.getText(\
                self,
                self.trUtf8("Subversion List"),
                self.trUtf8("Enter the repository URL containing the tags or branches"),
                QLineEdit.Normal,
                self.vcs.svnNormalizeURL(reposURL))
            if not ok:
                self.close()
                return False
            if reposPath.isEmpty():
                KQMessageBox.critical(None,
                    self.trUtf8("Subversion List"),
                    self.trUtf8("""The repository URL is empty. Aborting..."""))
                self.close()
                return False
            path = unicode(reposPath)
        
        locker = QMutexLocker(self.vcs.vcsExecutionMutex)
        self.tagsList = QStringList()
        cwd = os.getcwd()
        os.chdir(dname)
        try:
            entries = self.client.list(path, recurse = False)
            for dirent, lock in entries:
                if dirent["path"] != path:
                    name = dirent["path"].replace(path + '/', "")
                    self.__generateItem(dirent["created_rev"].number, 
                                        dirent["last_author"], 
                                        formatTime(dirent["time"]), 
                                        name)
                    if self.vcs.otherData["standardLayout"]:
                        self.tagsList.append(name)
                    else:
                        self.tagsList.append(path + '/' + name)
                    if self._clientCancelCallback():
                        break
            res = True
        except pysvn.ClientError, e:
            self.__showError(e.args[0])
            res = False
        except AttributeError:
            self.__showError(\
                self.trUtf8("The installed version of PySvn should be 1.4.0 or better."))
            res = False
        locker.unlock()
        self.__finish()
        os.chdir(cwd)
        return res
        
    def __finish(self):
        """
        Private slot called when the process finished or the user pressed the button.
        """
        self.buttonBox.button(QDialogButtonBox.Close).setEnabled(True)
        self.buttonBox.button(QDialogButtonBox.Cancel).setEnabled(False)
        self.buttonBox.button(QDialogButtonBox.Close).setDefault(True)
        
        self.tagList.doItemsLayout()
        self.__resizeColumns()
        self.__resort()
        
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
        
    def __showError(self, msg):
        """
        Private slot to show an error message.
        
        @param msg error message to show (string or QString)
        """
        self.errorGroup.show()
        self.errors.insertPlainText(msg)
        self.errors.ensureCursorVisible()
        
    def __resort(self):
        """
        Private method to resort the tree.
        """
        self.tagList.sortItems(self.tagList.sortColumn(), 
            self.tagList.header().sortIndicatorOrder())
        
    def __resizeColumns(self):
        """
        Private method to resize the list columns.
        """
        self.tagList.header().resizeSections(QHeaderView.ResizeToContents)
        self.tagList.header().setStretchLastSection(True)
        
    def __generateItem(self, revision, author, date, name):
        """
        Private method to generate a tag item in the taglist.
        
        @param revision revision number (integer)
        @param author author of the tag (string or QString)
        @param date date of the tag (string or QString)
        @param name name (path) of the tag (string or QString)
        """
        itm = QTreeWidgetItem(self.tagList, 
            QStringList() << "%6d" % revision << author << date << name)
        itm.setTextAlignment(0, Qt.AlignRight)
        
    def getTagList(self):
        """
        Public method to get the taglist of the last run.
        
        @return list of tags (QStringList)
        """
        return self.tagsList
