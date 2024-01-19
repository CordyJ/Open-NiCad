# -*- coding: utf-8 -*-

# Copyright (c) 2005 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the handler class for reading an XML tasks file.
"""

from Config import pluginRepositoryFileFormatVersion
from XMLHandlerBase import XMLHandlerBase

import Preferences

class PluginRepositoryHandler(XMLHandlerBase):
    """
    Class implementing a sax handler to read an XML tasks file.
    """
    def __init__(self, parent):
        """
        Constructor
        
        @param parent reference to the parent dialog (PluginRepositoryDialog)
        """
        XMLHandlerBase.__init__(self)
        
        self.startDocumentSpecific = self.startDocumentPlugins
        
        self.elements.update({
            'Plugins' : (self.startPlugins, self.defaultEndElement),
            'Plugin' : (self.startPlugin, self.endPlugin),
            'Name' : (self.defaultStartElement, self.endName),
            'Short' : (self.defaultStartElement, self.endShort),
            'Description' : (self.defaultStartElement, self.endDescription),
            'Url' : (self.defaultStartElement, self.endUrl),
            'Author' : (self.defaultStartElement, self.endAuthor),
            'Version' : (self.defaultStartElement, self.endVersion),
            'Filename' : (self.defaultStartElement, self.endFilename),
            'RepositoryUrl' : (self.defaultStartElement, self.endRepositoryUrl), 
        })
    
        self.parent = parent
        
    def startDocumentPlugins(self):
        """
        Handler called, when the document parsing is started.
        """
        self.version = ''
        
    ###################################################
    ## below follow the individual handler functions
    ###################################################
    
    def startPlugins(self, attrs):
        """
        Handler method for the "Plugins" start tag.
        
        @param attrs list of tag attributes
        """
        self.version = attrs.get('version', pluginRepositoryFileFormatVersion)
        
    def startPlugin(self, attrs):
        """
        Handler method for the "Plugin" start tag.
        
        @param attrs list of tag attributes
        """
        self.info = {"name"         : "",
                     "short"        : "",
                     "description"  : "",
                     "url"          : "",
                     "author"       : "",
                     "version"      : "", 
                     "filename"     : "",
                    }
        self.info["status"] = attrs.get("status", "unknown")
    
    def endPlugin(self):
        """
        Handler method for the "Plugin" end tag.
        """
        self.parent.addEntry(self.info["name"], self.info["short"], 
                             self.info["description"], self.info["url"], 
                             self.info["author"], self.info["version"],
                             self.info["filename"], self.info["status"])
        
    def endName(self):
        """
        Handler method for the "Name" end tag.
        """
        self.info["name"] = self.unescape(self.utf8_to_code(self.buffer))
        
    def endShort(self):
        """
        Handler method for the "Short" end tag.
        """
        self.info["short"] = self.unescape(self.utf8_to_code(self.buffer))
        
    def endDescription(self):
        """
        Handler method for the "Description" end tag.
        """
        txt = self.unescape(self.utf8_to_code(self.buffer))
        self.info["description"] = [line.strip() for line in txt.splitlines()]
        
    def endUrl(self):
        """
        Handler method for the "Url" end tag.
        """
        self.info["url"] = self.unescape(self.utf8_to_code(self.buffer))
        
    def endAuthor(self):
        """
        Handler method for the "Author" end tag.
        """
        self.info["author"] = self.unescape(self.utf8_to_code(self.buffer))
        
    def endVersion(self):
        """
        Handler method for the "Version" end tag.
        """
        self.info["version"] = self.unescape(self.utf8_to_code(self.buffer))
        
    def endFilename(self):
        """
        Handler method for the "Filename" end tag.
        """
        self.info["filename"] = self.unescape(self.utf8_to_code(self.buffer))
        
    def endRepositoryUrl(self):
        """
        Handler method for the "RepositoryUrl" end tag.
        """
        url = self.unescape(self.utf8_to_code(self.buffer)).strip()
        Preferences.setUI("PluginRepositoryUrl", url)
        
    def getVersion(self):
        """
        Public method to retrieve the version of the tasks file.
        
        @return String containing the version number.
        """
        return self.version
