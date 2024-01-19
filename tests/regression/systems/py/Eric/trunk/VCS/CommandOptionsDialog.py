# -*- coding: utf-8 -*-

# Copyright (c) 2002 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the VCS command options dialog.
"""

import sys

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from Ui_CommandOptionsDialog import Ui_vcsCommandOptionsDialog

import Utilities

class vcsCommandOptionsDialog(QDialog, Ui_vcsCommandOptionsDialog):
    """
    Class implementing the VCS command options dialog.
    """
    def __init__(self, vcs, parent=None):
        """
        Constructor
        
        @param vcs reference to the vcs object
        @param parent parent widget (QWidget)
        """
        QDialog.__init__(self, parent)
        self.setupUi(self)
        
        if Utilities.isWindowsPlatform():
            self.optionChars = ['-', '/']
        else:
            self.optionChars = ['-']
        
        opt = vcs.vcsGetOptions()
        self.globalEdit.setText(" ".join(opt['global']))
        self.commitEdit.setText(" ".join(opt['commit']))
        self.checkoutEdit.setText(" ".join(opt['checkout']))
        self.updateEdit.setText(" ".join(opt['update']))
        self.addEdit.setText(" ".join(opt['add']))
        self.removeEdit.setText(" ".join(opt['remove']))
        self.diffEdit.setText(" ".join(opt['diff']))
        self.logEdit.setText(" ".join(opt['log']))
        self.historyEdit.setText(" ".join(opt['history']))
        self.statusEdit.setText(" ".join(opt['status']))
        self.tagEdit.setText(" ".join(opt['tag']))
        self.exportEdit.setText(" ".join(opt['export']))
        
        # modify the what's this help
        for widget in [self.globalEdit, self.commitEdit, self.checkoutEdit,
                  self.updateEdit, self.addEdit, self.removeEdit,
                  self.diffEdit, self.logEdit, self.historyEdit,
                  self.statusEdit, self.tagEdit, self.exportEdit]:
            t = widget.whatsThis()
            if not t.isEmpty():
                t = t.append(Utilities.getPercentReplacementHelp())
                widget.setWhatsThis(t)
        
    def getOptions(self):
        """
        Public method used to retrieve the entered options.
        
        @return dictionary of strings giving the options for each supported vcs command
        """
        opt = {}
        opt['global'] = Utilities.parseOptionString(self.globalEdit.text())
        opt['commit'] = Utilities.parseOptionString(self.commitEdit.text())
        opt['checkout'] = Utilities.parseOptionString(self.checkoutEdit.text())
        opt['update'] = Utilities.parseOptionString(self.updateEdit.text())
        opt['add'] = Utilities.parseOptionString(self.addEdit.text())
        opt['remove'] = Utilities.parseOptionString(self.removeEdit.text())
        opt['diff'] = Utilities.parseOptionString(self.diffEdit.text())
        opt['log'] = Utilities.parseOptionString(self.logEdit.text())
        opt['history'] = Utilities.parseOptionString(self.historyEdit.text())
        opt['status'] = Utilities.parseOptionString(self.statusEdit.text())
        opt['tag'] = Utilities.parseOptionString(self.tagEdit.text())
        opt['export'] = Utilities.parseOptionString(self.exportEdit.text())
        return opt
