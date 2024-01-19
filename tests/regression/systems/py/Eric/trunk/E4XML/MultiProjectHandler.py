# -*- coding: utf-8 -*-

# Copyright (c) 2008 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the handler class for reading an XML multi project file.
"""

from Config import multiProjectFileFormatVersion
from XMLHandlerBase import XMLHandlerBase

import Utilities

class MultiProjectHandler(XMLHandlerBase):
    """
    Class implementing a sax handler to read an XML multi project file.
    """
    def __init__(self, multiProject):
        """
        Constructor
        
        @param multiProject Reference to the multi project object to store the
                information into.
        """
        XMLHandlerBase.__init__(self)
        
        self.startDocumentSpecific = self.startDocumentMultiProject
        
        self.elements.update({
            'MultiProject' : (self.startMultiProject, self.defaultEndElement),
            'Description' : (self.defaultStartElement, self.endDescription),
            'Project' : (self.startProject, self.endProject), 
            'ProjectName' : (self.defaultStartElement, self.endProjectName), 
            'ProjectFile' : (self.defaultStartElement, self.endProjectFile), 
            'ProjectDescription' : (self.defaultStartElement, self.endProjectDescription),
        })
        
        self.multiProject = multiProject
    
    def startDocumentMultiProject(self):
        """
        Handler called, when the document parsing is started.
        """
        self.version = ''
    
    ###################################################
    ## below follow the individual handler functions
    ###################################################
    
    def startMultiProject(self, attrs):
        """
        Handler method for the "MultiProject" start tag.
        
        @param attrs list of tag attributes
        """
        self.version = attrs.get('version', multiProjectFileFormatVersion)
    
    def endDescription(self):
        """
        Handler method for the "Description" end tag.
        """
        self.buffer = self.unescape(self.utf8_to_code(self.buffer))
        self.multiProject.description = self.decodedNewLines(self.buffer)
    
    def startProject(self, attrs):
        """
        Handler method for the "Project" start tag.
        
        @param attrs list of tag attributes
        """
        self.project = {}
        isMaster = attrs.get('isMaster', "False")
        self.project["master"] = isMaster == "True"
    
    def endProject(self):
        """
        Handler method for the "Project" end tag.
        """
        self.multiProject.projects.append(self.project)
    
    def endProjectName(self):
        """
        Handler method for the "ProjectName" end tag.
        """
        self.project["name"] = self.unescape(self.utf8_to_code(self.buffer))
    
    def endProjectFile(self):
        """
        Handler method for the "ProjectFile" end tag.
        """
        filename = self.utf8_to_code(self.buffer)
        self.project["file"] = unicode(Utilities.toNativeSeparators(filename))
    
    def endProjectDescription(self):
        """
        Handler method for the "ProjectDescription" end tag.
        """
        self.buffer = self.unescape(self.utf8_to_code(self.buffer))
        self.project["description"] = self.decodedNewLines(self.buffer)
    
    def getVersion(self):
        """
        Public method to retrieve the version of the project.
        
        @return String containing the version number.
        """
        return self.version
    
