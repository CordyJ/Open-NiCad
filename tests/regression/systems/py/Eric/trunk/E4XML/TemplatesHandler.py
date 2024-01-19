# -*- coding: utf-8 -*-

# Copyright (c) 2005 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the handler class for reading an XML templates file.
"""

import os
import time

from KdeQt.KQApplication import e4App

from Config import templatesFileFormatVersion
from XMLHandlerBase import XMLHandlerBase

class TemplatesHandler(XMLHandlerBase):
    """
    Class implementing a sax handler to read an XML templates file.
    """
    def __init__(self, templateViewer=None):
        """
        Constructor
        
        @param templateViewer reference to the template viewer object
        """
        XMLHandlerBase.__init__(self)
        
        self.startDocumentSpecific = self.startDocumentTemplates
        
        self.elements.update({
            'Templates' : (self.startTemplates, self.defaultEndElement),
            'TemplateGroup' : (self.startTemplateGroup, self.defaultEndElement),
            'Template' : (self.startTemplate, self.endTemplate),
            'TemplateDescription' : (self.defaultStartElement, 
                                     self.endTemplateDescription), 
            'TemplateText' : (self.defaultStartElement, self.endTemplateText),
        })
    
        if templateViewer:
            self.viewer = templateViewer
        else:
            self.viewer = e4App().getObject("TemplateViewer")
        
    def startDocumentTemplates(self):
        """
        Handler called, when the document parsing is started.
        """
        self.version = ''
        
    ###################################################
    ## below follow the individual handler functions
    ###################################################
    
    def startTemplateGroup(self, attrs):
        """
        Handler method for the "TemplateGroup" start tag.
        
        @param attrs list of tag attributes
        """
        self.groupName = attrs.get('name', "DEFAULT")
        language = attrs.get('language', "All")
        self.viewer.addGroup(self.groupName, language)

    def startTemplate(self, attrs):
        """
        Handler method for the "Template" start tag.
        
        @param attrs list of tag attributes
        """
        self.templateName = attrs.get('name', '')
        self.templateDescription = ""
        self.templateText = ""

    def endTemplate(self):
        """
        Handler method for the "Template" end tag.
        """
        if self.templateName and self.templateText:
            self.viewer.addEntry(self.groupName, self.templateName, 
                                 self.templateDescription, self.templateText,
                                 quiet=True)

    def endTemplateText(self):
        """
        Handler method for the "TemplateText" end tag.
        """
        self.templateText = self.unescape(self.utf8_to_code(self.buffer))

    def endTemplateDescription(self):
        """
        Handler method for the "TemplateDescription" end tag.
        """
        self.templateDescription = self.unescape(self.utf8_to_code(self.buffer))
    
    def startTemplates(self, attrs):
        """
        Handler method for the "Templates" start tag.
        
        @param attrs list of tag attributes
        """
        self.version = attrs.get('version', templatesFileFormatVersion)
        
    def getVersion(self):
        """
        Public method to retrieve the version of the templates.
        
        @return String containing the version number.
        """
        return self.version
