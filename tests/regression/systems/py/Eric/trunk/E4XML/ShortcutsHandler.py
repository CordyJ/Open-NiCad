# -*- coding: utf-8 -*-

# Copyright (c) 2003 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the handler class for reading a keyboard shortcuts file.
"""

from Config import shortcutsFileFormatVersion
from XMLHandlerBase import XMLHandlerBase

class ShortcutsHandler(XMLHandlerBase):
    """
    Class implementing a sax handler to read a keyboard shortcuts file.
    """
    def __init__(self):
        """
        Constructor
        """
        XMLHandlerBase.__init__(self)
        
        self.startDocumentSpecific = self.startDocumentShortcuts
        
        self.elements.update({
            'Shortcuts' : (self.startShortcuts, self.defaultEndElement),
            'Shortcut' : (self.startShortcut, self.endShortcut),
            'Name' : (self.defaultStartElement, self.endName),
            'Accel' : (self.defaultStartElement, self.endAccel),
            'AltAccel' : (self.defaultStartElement, self.endAltAccel),
        })
        
    def startDocumentShortcuts(self):
        """
        Handler called, when the document parsing is started.
        """
        self.shortcuts = {}     # dictionary for storing the shortcuts
        self.version = ''
        
    ###################################################
    ## below follow the individual handler functions
    ###################################################
    
    def endName(self):
        """
        Handler method for the "Name" end tag.
        """
        self.name = self.utf8_to_code(self.buffer)
        
    def endAccel(self):
        """
        Handler method for the "Accel" end tag.
        """
        self.accel = self.unescape(self.utf8_to_code(self.buffer))
        
    def endAltAccel(self):
        """
        Handler method for the "AltAccel" end tag.
        """
        self.altAccel = self.unescape(self.utf8_to_code(self.buffer))
        
    def startShortcut(self, attrs):
        """
        Handler method for the "Shortcut" start tag.
        
        @param attrs list of tag attributes
        """
        self.name = ''
        self.accel = ''
        self.altAccel = ''
        self.category = attrs.get('category', '')
        
    def endShortcut(self):
        """
        Handler method for the "Shortcut" end tag.
        """
        if self.category:
            if not self.shortcuts.has_key(self.category):
                self.shortcuts[self.category] = {}
            self.shortcuts[self.category][self.name] = (self.accel, self.altAccel)
        
    def startShortcuts(self, attrs):
        """
        Handler method for the "Shortcuts" start tag.
        
        @param attrs list of tag attributes
        """
        self.version = attrs.get('version', shortcutsFileFormatVersion)
        
    def getShortcuts(self):
        """
        Public method to retrieve the shortcuts.
        
        @return Dictionary of dictionaries of shortcuts. The keys of the
            dictionary are the categories, the values are dictionaries.
            These dictionaries have the shortcut name as their key and
            a tuple of accelerators as their value.
        """
        return self.shortcuts
        
    def getVersion(self):
        """
        Public method to retrieve the version of the shortcuts.
        
        @return String containing the version number.
        """
        return self.version
