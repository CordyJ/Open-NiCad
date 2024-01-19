# -*- coding: utf-8 -*-

# Copyright (c) 2008 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the handler class for handling a highlighting styles XML file.
"""

from PyQt4.QtGui import QColor, QFont

from Config import highlightingStylesFileFormatVersion
from XMLHandlerBase import XMLHandlerBase

class HighlightingStylesHandler(XMLHandlerBase):
    """
    Class implementing a sax handler to read a highlighting styles file.
    """
    def __init__(self, lexers):
        """
        Constructor
        
        @param lexers dictionary of lexer objects for which to import the styles
        """
        XMLHandlerBase.__init__(self)
        
        self.lexers = lexers
        self.lexer = None
        
        self.startDocumentSpecific = self.startDocumentHighlightingStyles
        
        self.elements.update({
            'HighlightingStyles' : (self.startHighlightingStyles, self.defaultEndElement),
            'Lexer' : (self.startLexer, self.defaultEndElement),
            'Style' : (self.startStyle, self.defaultEndElement),
        })
        
    def startDocumentHighlightingStyles(self):
        """
        Handler called, when the document parsing is started.
        """
        self.version = ''
        
    ###################################################
    ## below follow the individual handler functions
    ###################################################
    
    def startHighlightingStyles(self, attrs):
        """
        Handler method for the "HighlightingStyles" start tag.
        
        @param attrs list of tag attributes
        """
        self.version = attrs.get('version', highlightingStylesFileFormatVersion)
        
    def startLexer(self, attrs):
        """
        Handler method for the "Lexer" start tag.
        
        @param attrs list of tag attributes
        """
        language = attrs.get("name", "")
        if language and language in self.lexers:
            self.lexer = self.lexers[language]
        else:
            self.lexer = None
        
    def startStyle(self, attrs):
        """
        Handler method for the "Style" start tag.
        
        @param attrs list of tag attributes
        """
        self.buffer = ""
        
        if self.lexer is not None:
            style = attrs.get("style")
            if style is not None:
                style = int(style)
                
                color = attrs.get("color")
                if color is None:
                    color = self.lexer.defaultColor(style)
                else:
                    color = QColor(color)
                self.lexer.setColor(color, style)
                
                paper = attrs.get("paper")
                if paper is None:
                    paper = self.lexer.defaultPaper(style)
                else:
                    paper = QColor(paper)
                self.lexer.setPaper(paper, style)
                
                fontStr = attrs.get("font")
                if fontStr is None:
                    font = self.lexer.defaultFont(style)
                else:
                    font = QFont()
                    font.fromString(fontStr)
                self.lexer.setFont(font, style)
                
                eolfill = attrs.get("eolfill")
                if eolfill is None:
                    eolfill = self.lexer.defaulEolFill(style)
                else:
                    eolfill = int(eolfill)
                self.lexer.setEolFill(eolfill, style)
        
    def getVersion(self):
        """
        Public method to retrieve the version of the shortcuts.
        
        @return String containing the version number.
        """
        return self.version
