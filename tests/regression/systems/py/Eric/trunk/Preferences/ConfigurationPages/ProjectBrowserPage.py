# -*- coding: utf-8 -*-

# Copyright (c) 2006 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the Project Browser configuration page.
"""

from PyQt4.QtCore import pyqtSignature, QVariant

from KdeQt.KQApplication import e4App

from ConfigurationPageBase import ConfigurationPageBase
from Ui_ProjectBrowserPage import Ui_ProjectBrowserPage

from Project.ProjectBrowserFlags import SourcesBrowserFlag, FormsBrowserFlag, \
    ResourcesBrowserFlag, TranslationsBrowserFlag, InterfacesBrowserFlag, \
    OthersBrowserFlag, AllBrowsersFlag

import Preferences

class ProjectBrowserPage(ConfigurationPageBase, Ui_ProjectBrowserPage):
    """
    Class implementing the Project Browser configuration page.
    """
    def __init__(self):
        """
        Constructor
        """
        ConfigurationPageBase.__init__(self)
        self.setupUi(self)
        self.setObjectName("ProjectBrowserPage")
        
        self.projectBrowserColours = {}
        self.__currentProjectTypeIndex = 0
        
        # set initial values
        self.projectTypeCombo.addItem('', QVariant(''))
        self.__projectBrowserFlags = {'' : 0}
        try:
            projectTypes = e4App().getObject("Project").getProjectTypes()
            for projectType in sorted(projectTypes.keys()):
                self.projectTypeCombo.addItem(projectTypes[projectType], 
                                              QVariant(projectType))
                self.__projectBrowserFlags[projectType] = \
                    Preferences.getProjectBrowserFlags(projectType)
        except KeyError:
            self.pbGroup.setEnabled(False)
        
        self.projectBrowserColours["Highlighted"] = \
            self.initColour("Highlighted", self.pbHighlightedButton, 
                Preferences.getProjectBrowserColour)
        
        self.followEditorCheckBox.setChecked(\
            Preferences.getProject("FollowEditor"))
        self.hideGeneratedCheckBox.setChecked(\
            Preferences.getProject("HideGeneratedForms"))
        
    def save(self):
        """
        Public slot to save the Project Browser configuration.
        """
        for key in self.projectBrowserColours.keys():
            Preferences.setProjectBrowserColour(key, self.projectBrowserColours[key])
        
        Preferences.setProject("FollowEditor", 
            int(self.followEditorCheckBox.isChecked()))
        Preferences.setProject("HideGeneratedForms", 
            int(self.hideGeneratedCheckBox.isChecked()))
        
        if self.pbGroup.isEnabled():
            self.__storeProjectBrowserFlags(\
                self.projectTypeCombo.itemData(self.__currentProjectTypeIndex).toString())
            for projectType, flags in self.__projectBrowserFlags.items():
                if projectType != '':
                    Preferences.setProjectBrowserFlags(projectType, flags)
        
    @pyqtSignature("")
    def on_pbHighlightedButton_clicked(self):
        """
        Private slot to set the colour for highlighted entries of the 
        project others browser.
        """
        self.projectBrowserColours["Highlighted"] = \
            self.selectColour(self.pbHighlightedButton, 
                self.projectBrowserColours["Highlighted"])
    
    def __storeProjectBrowserFlags(self, projectType):
        """
        Private method to store the flags for the selected project type.
        
        @param projectType type of the selected project (QString)
        """
        flags = 0
        if self.sourcesBrowserCheckBox.isChecked():
            flags |= SourcesBrowserFlag
        if self.formsBrowserCheckBox.isChecked():
            flags |= FormsBrowserFlag
        if self.resourcesBrowserCheckBox.isChecked():
            flags |= ResourcesBrowserFlag
        if self.translationsBrowserCheckBox.isChecked():
            flags |= TranslationsBrowserFlag
        if self.interfacesBrowserCheckBox.isChecked():
            flags |= InterfacesBrowserFlag
        if self.othersBrowserCheckBox.isChecked():
            flags |= OthersBrowserFlag
        
        self.__projectBrowserFlags[unicode(projectType)] = flags
    
    def __setProjectBrowsersCheckBoxes(self, projectType):
        """
        Private method to set the checkboxes according to the selected project type.
        
        @param projectType type of the selected project (QString)
        """
        flags = self.__projectBrowserFlags[unicode(projectType)]
        
        self.sourcesBrowserCheckBox.setChecked(flags & SourcesBrowserFlag)
        self.formsBrowserCheckBox.setChecked(flags & FormsBrowserFlag)
        self.resourcesBrowserCheckBox.setChecked(flags & ResourcesBrowserFlag)
        self.translationsBrowserCheckBox.setChecked(flags & TranslationsBrowserFlag)
        self.interfacesBrowserCheckBox.setChecked(flags & InterfacesBrowserFlag)
        self.othersBrowserCheckBox.setChecked(flags & OthersBrowserFlag)
    
    @pyqtSignature("int")
    def on_projectTypeCombo_activated(self, index):
        """
        Private slot to set the browser checkboxes according to the selected
        project type.
        
        @param index index of the selected project type (integer)
        """
        if self.__currentProjectTypeIndex == index:
           return
        
        self.__storeProjectBrowserFlags(\
            self.projectTypeCombo.itemData(self.__currentProjectTypeIndex).toString())
        self.__setProjectBrowsersCheckBoxes(\
            self.projectTypeCombo.itemData(index).toString())
        self.__currentProjectTypeIndex = index
    
def create(dlg):
    """
    Module function to create the configuration page.
    
    @param dlg reference to the configuration dialog
    """
    page = ProjectBrowserPage()
    return page
