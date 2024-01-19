# -*- coding: utf-8 -*-

# Copyright (c) 2005 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the task properties dialog.
"""

import time

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from E4Gui.E4Completers import E4FileCompleter

from Ui_TaskPropertiesDialog import Ui_TaskPropertiesDialog


class TaskPropertiesDialog(QDialog, Ui_TaskPropertiesDialog):
    """
    Class implementing the task properties dialog.
    """
    def __init__(self, task = None, parent = None, projectOpen = False):
        """
        Constructor
        
        @param task the task object to be shown
        @param parent the parent widget (QWidget)
        @param projectOpen flag indicating status of the project (boolean)
        """
        QDialog.__init__(self, parent)
        self.setupUi(self)
        
        self.filenameCompleter = E4FileCompleter(self.filenameEdit)
        
        if not projectOpen:
            self.projectCheckBox.setEnabled(False)
        if task is not None:
            self.descriptionEdit.setText(task.description)
            self.longtextEdit.setText(task.longtext)
            self.creationLabel.setText(time.strftime("%Y-%m-%d, %H:%M:%S", 
                                                     time.localtime(task.created)))
            self.priorityCombo.setCurrentIndex(task.priority)
            self.projectCheckBox.setChecked(task._isProjectTask)
            self.completedCheckBox.setChecked(task.completed)
            self.filenameEdit.setText(task.filename)
            if task.lineno:
                self.linenoEdit.setText(str(task.lineno))
        else:
            self.projectCheckBox.setChecked(projectOpen)
    
    def setReadOnly(self):
        """
        Public slot to set the dialog to read only mode.
        """
        self.descriptionEdit.setReadOnly(True)
        self.completedCheckBox.setEnabled(False)
        self.priorityCombo.setEnabled(False)
        
    def getData(self):
        """
        Public method to retrieve the dialogs data.
        
        @return tuple of description, priority, completion flag
                and project flag
        """
        return (self.descriptionEdit.text(), self.priorityCombo.currentIndex(),
                self.completedCheckBox.isChecked(), self.projectCheckBox.isChecked(), 
                self.longtextEdit.toPlainText())
