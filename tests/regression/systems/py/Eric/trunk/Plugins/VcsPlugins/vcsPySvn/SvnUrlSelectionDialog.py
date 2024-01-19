# -*- coding: utf-8 -*-

# Copyright (c) 2007 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a dialog to enter the URLs for the svn diff command.
"""

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from KdeQt import KQMessageBox
from KdeQt.KQApplication import e4App

import pysvn

from Ui_SvnUrlSelectionDialog import Ui_SvnUrlSelectionDialog


class SvnUrlSelectionDialog(QDialog, Ui_SvnUrlSelectionDialog):
    """
    Class implementing a dialog to enter the URLs for the svn diff command.
    """
    def __init__(self, vcs, tagsList, branchesList, path, parent = None):
        """
        Constructor
        
        @param vcs reference to the vcs object
        @param tagsList list of tags (QStringList)
        @param branchesList list of branches (QStringList)
        @param path pathname to determine the repository URL from (string or QString)
        @param parent parent widget of the dialog (QWidget)
        """
        QDialog.__init__(self, parent)
        self.setupUi(self)
        
        if not hasattr(pysvn.Client(), 'diff_summarize'):
            self.summaryCheckBox.setEnabled(False)
            self.summaryCheckBox.setChecked(False)
        
        self.vcs = vcs
        self.tagsList = tagsList
        self.branchesList = branchesList
        
        self.typeCombo1.addItems(QStringList() << "trunk/" << "tags/" << "branches/")
        self.typeCombo2.addItems(QStringList() << "trunk/" << "tags/" << "branches/")
        
        reposURL = self.vcs.svnGetReposName(path)
        if reposURL is None:
            KQMessageBox.critical(None,
                self.trUtf8("Subversion Error"),
                self.trUtf8("""The URL of the project repository could not be"""
                    """ retrieved from the working copy. The operation will"""
                    """ be aborted"""))
            self.reject()
            return
        
        if self.vcs.otherData["standardLayout"]:
            # determine the base path of the project in the repository
            rx_base = QRegExp('(.+/)(trunk|tags|branches).*')
            if not rx_base.exactMatch(reposURL):
                KQMessageBox.critical(None,
                    self.trUtf8("Subversion Error"),
                    self.trUtf8("""The URL of the project repository has an"""
                        """ invalid format. The operation will"""
                        """ be aborted"""))
                self.reject()
                return
            
            reposRoot = unicode(rx_base.cap(1))
            self.repoRootLabel1.setText(reposRoot)
            self.repoRootLabel2.setText(reposRoot)
        else:
            ppath = e4App().getObject('Project').getProjectPath()
            if path != ppath:
                path = path.replace(ppath, '')
                reposURL = reposURL.replace(path, '')
            self.repoRootLabel1.hide()
            self.typeCombo1.hide()
            self.labelCombo1.addItems(QStringList(reposURL) + self.vcs.tagsList)
            self.labelCombo1.setEnabled(True)
            self.repoRootLabel2.hide()
            self.typeCombo2.hide()
            self.labelCombo2.addItems(QStringList(reposURL) + self.vcs.tagsList)
            self.labelCombo2.setEnabled(True)
        
    def __changeLabelCombo(self, labelCombo, type_):
        """
        Private method used to change the label combo depending on the 
        selected type.
        
        @param labelCombo reference to the labelCombo object (QComboBox)
        @param type type string (QString)
        """
        if type_ == "trunk/":
            labelCombo.clear()
            labelCombo.setEditText("")
            labelCombo.setEnabled(False)
        elif type_ == "tags/":
            labelCombo.clear()
            labelCombo.clearEditText()
            labelCombo.addItems(self.tagsList)
            labelCombo.setEnabled(True)
        elif type_ == "branches/":
            labelCombo.clear()
            labelCombo.clearEditText()
            labelCombo.addItems(self.branchesList)
            labelCombo.setEnabled(True)
        
    @pyqtSignature("QString")
    def on_typeCombo1_currentIndexChanged(self, type_):
        """
        Private slot called when the selected type was changed.
        
        @param type_ selected type (QString)
        """
        self.__changeLabelCombo(self.labelCombo1, type_)
        
    @pyqtSignature("QString")
    def on_typeCombo2_currentIndexChanged(self, type_):
        """
        Private slot called when the selected type was changed.
        
        @param type_ selected type (QString)
        """
        self.__changeLabelCombo(self.labelCombo2, type_)
        
    def getURLs(self):
        """
        Public method to get the entered URLs.
        
        @return tuple of list of two URL strings (list of strings) and
            a flag indicating a diff summary (boolean)
        """
        if self.vcs.otherData["standardLayout"]:
            url1 = unicode(self.repoRootLabel1.text() + \
                           self.typeCombo1.currentText() + \
                           self.labelCombo1.currentText())
            url2 = unicode(self.repoRootLabel2.text() + \
                           self.typeCombo2.currentText() + \
                           self.labelCombo2.currentText())
        else:
            url1 = unicode(self.labelCombo1.currentText())
            url2 = unicode(self.labelCombo2.currentText())
        
        return [url1, url2], self.summaryCheckBox.isChecked()
