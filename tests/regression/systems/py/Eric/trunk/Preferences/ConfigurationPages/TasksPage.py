# -*- coding: utf-8 -*-

# Copyright (c) 2006 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the Tasks configuration page.
"""

from PyQt4.QtCore import pyqtSignature
from PyQt4.QtGui import QPixmap, QIcon

from ConfigurationPageBase import ConfigurationPageBase
from Ui_TasksPage import Ui_TasksPage

import Preferences

class TasksPage(ConfigurationPageBase, Ui_TasksPage):
    """
    Class implementing the Tasks configuration page.
    """
    def __init__(self):
        """
        Constructor
        """
        ConfigurationPageBase.__init__(self)
        self.setupUi(self)
        self.setObjectName("TasksPage")
        
        self.tasksColours = {}
        
        # set initial values
        self.tasksMarkerEdit.setText(Preferences.getTasks("TasksMarkers"))
        self.tasksMarkerBugfixEdit.setText(\
            Preferences.getTasks("TasksMarkersBugfix"))
        
        self.tasksColours["TasksColour"] = \
            self.initColour("TasksColour", self.tasksColourButton, Preferences.getTasks)
        self.tasksColours["TasksBugfixColour"] = \
            self.initColour("TasksBugfixColour", self.tasksBugfixColourButton, 
                Preferences.getTasks)
        self.tasksColours["TasksBgColour"] = \
            self.initColour("TasksBgColour", self.tasksBgColourButton, 
                Preferences.getTasks)
        self.tasksColours["TasksProjectBgColour"] = \
            self.initColour("TasksProjectBgColour", self.tasksProjectBgColourButton, 
                Preferences.getTasks)
        
    def save(self):
        """
        Public slot to save the Tasks configuration.
        """
        Preferences.setTasks("TasksMarkers", self.tasksMarkerEdit.text())
        Preferences.setTasks("TasksMarkersBugfix",
            self.tasksMarkerBugfixEdit.text())
        for key in self.tasksColours.keys():
            Preferences.setTasks(key, self.tasksColours[key])
        
    @pyqtSignature("")
    def on_tasksColourButton_clicked(self):
        """
        Private slot to set the colour for standard tasks.
        """
        self.tasksColours["TasksColour"] = \
            self.selectColour(self.tasksColourButton, self.tasksColours["TasksColour"])
        
    @pyqtSignature("")
    def on_tasksBugfixColourButton_clicked(self):
        """
        Private slot to set the colour for bugfix tasks.
        """
        self.tasksColours["TasksBugfixColour"] = \
            self.selectColour(self.tasksBugfixColourButton, 
                self.tasksColours["TasksBugfixColour"])
        
    @pyqtSignature("")
    def on_tasksBgColourButton_clicked(self):
        """
        Private slot to set the background colour for global tasks.
        """
        self.tasksColours["TasksBgColour"] = \
            self.selectColour(self.tasksBgColourButton, 
                self.tasksColours["TasksBgColour"])
        
    @pyqtSignature("")
    def on_tasksProjectBgColourButton_clicked(self):
        """
        Private slot to set the backgroundcolour for project tasks.
        """
        self.tasksColours["TasksProjectBgColour"] = \
            self.selectColour(self.tasksProjectBgColourButton, 
                self.tasksColours["TasksProjectBgColour"])
    
def create(dlg):
    """
    Module function to create the configuration page.
    
    @param dlg reference to the configuration dialog
    """
    page = TasksPage()
    return page
