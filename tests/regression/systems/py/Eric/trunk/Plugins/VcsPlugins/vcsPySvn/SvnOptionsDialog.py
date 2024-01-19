# -*- coding: utf-8 -*-

# Copyright (c) 2002 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a dialog to enter options used to start a project in the VCS.
"""

import os

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from KdeQt import KQFileDialog

from E4Gui.E4Completers import E4DirCompleter

from SvnRepoBrowserDialog import SvnRepoBrowserDialog
from Ui_SvnOptionsDialog import Ui_SvnOptionsDialog
from Config import ConfigSvnProtocols

import Utilities

class SvnOptionsDialog(QDialog, Ui_SvnOptionsDialog):
    """
    Class implementing a dialog to enter options used to start a project in the
    repository.
    """
    def __init__(self, vcs, project, parent = None):
        """
        Constructor
        
        @param vcs reference to the version control object
        @param project reference to the project object
        @param parent parent widget (QWidget)
        """
        QDialog.__init__(self, parent)
        self.setupUi(self)
        
        self.vcsDirectoryCompleter = E4DirCompleter(self.vcsUrlEdit)
        
        self.project = project
        
        self.protocolCombo.addItems(ConfigSvnProtocols)
        
        hd = Utilities.toNativeSeparators(QDir.homePath())
        hd = os.path.join(unicode(hd), 'subversionroot')
        self.vcsUrlEdit.setText(hd)
        
        self.vcs = vcs
        
        self.localPath = unicode(hd)
        self.networkPath = "localhost/"
        self.localProtocol = True
        
    @pyqtSignature("")
    def on_vcsUrlButton_clicked(self):
        """
        Private slot to display a selection dialog.
        """
        if self.protocolCombo.currentText() == "file://":
            directory = KQFileDialog.getExistingDirectory(\
                self,
                self.trUtf8("Select Repository-Directory"),
                self.vcsUrlEdit.text(),
                QFileDialog.Options(QFileDialog.ShowDirsOnly))
            
            if not directory.isEmpty():
                self.vcsUrlEdit.setText(Utilities.toNativeSeparators(directory))
        else:
            dlg = SvnRepoBrowserDialog(self.vcs, mode = "select", parent = self)
            dlg.start(self.protocolCombo.currentText() + self.vcsUrlEdit.text())
            if dlg.exec_() == QDialog.Accepted:
                url = dlg.getSelectedUrl()
                if not url.isEmpty():
                    protocol = url.section("://", 0, 0)
                    path = url.section("://", 1, 1)
                    self.protocolCombo.setCurrentIndex(\
                        self.protocolCombo.findText(protocol + "://"))
                    self.vcsUrlEdit.setText(path)
        
    @pyqtSignature("QString")
    def on_protocolCombo_activated(self, protocol):
        """
        Private slot to switch the status of the directory selection button.
        """
        if str(protocol) == "file://":
            self.networkPath = unicode(self.vcsUrlEdit.text())
            self.vcsUrlEdit.setText(self.localPath)
            self.localProtocol = True
        else:
            if self.localProtocol:
                self.localPath = unicode(self.vcsUrlEdit.text())
                self.vcsUrlEdit.setText(self.networkPath)
                self.localProtocol = False
        
    def getData(self):
        """
        Public slot to retrieve the data entered into the dialog.
        
        @return a dictionary containing the data entered
        """
        scheme = str(self.protocolCombo.currentText())
        url = unicode(self.vcsUrlEdit.text())
        if scheme == "file://" and url[0] not in ["\\", "/"]:
            url = "/%s" % url
        vcsdatadict = {
            "url" : '%s%s' % (scheme, url),
            "message" : unicode(self.vcsLogEdit.text()),
            "standardLayout" : self.layoutCheckBox.isChecked(),
        }
        return vcsdatadict
