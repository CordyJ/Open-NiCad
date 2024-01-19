# -*- coding: utf-8 -*-

# Copyright (c) 2006 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the handler class for reading an XML user project properties file.
"""

import os

from Config import userProjectFileFormatVersion
from XMLHandlerBase import XMLHandlerBase

import Preferences

class UserProjectHandler(XMLHandlerBase):
    """
    Class implementing a sax handler to read an XML user project properties file.
    """
    def __init__(self, project):
        """
        Constructor
        
        @param project Reference to the project object to store the
                information into.
        """
        XMLHandlerBase.__init__(self)
        
        self.startDocumentSpecific = self.startDocumentProject
        
        self.elements.update({
            'UserProject' : (self.startUserProject, self.defaultEndElement),
            'VcsType' : (self.defaultStartElement, self.endVcsType),
            'VcsStatusMonitorInterval' : (self.startVcsStatusMonitorInterval, 
                                          self.defaultEndElement),
        })
    
        self.project = project
        
    def startDocumentProject(self):
        """
        Handler called, when the document parsing is started.
        """
        self.version = ''
        
    ###################################################
    ## below follow the individual handler functions
    ###################################################
    
    def endVcsType(self):
        """
        Handler method for the "VcsType" end tag.
        """
        self.buffer = self.utf8_to_code(self.buffer)
        self.project.pudata["VCSOVERRIDE"] = [self.buffer]
        
    def startVcsStatusMonitorInterval(self, attrs):
        """
        Handler method for the "VcsStatusMonitorInterval" start tag.
        
        @param attrs list of tag attributes
        """
        interval = int(attrs.get("value", Preferences.getVCS("StatusMonitorInterval")))
        self.project.pudata["VCSSTATUSMONITORINTERVAL"] = [interval]
        
    def startUserProject(self, attrs):
        """
        Handler method for the "UserProject" start tag.
        
        @param attrs list of tag attributes
        """
        self.version = attrs.get('version', userProjectFileFormatVersion)
        
    def getVersion(self):
        """
        Public method to retrieve the version of the user project file.
        
        @return String containing the version number.
        """
        return self.version
