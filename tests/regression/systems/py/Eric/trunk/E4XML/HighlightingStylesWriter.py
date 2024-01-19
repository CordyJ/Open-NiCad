# -*- coding: utf-8 -*-

# Copyright (c) 2008 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the writer class for writing a highlighting styles XML file.
"""

import os
import time

from KdeQt.KQApplication import e4App

from XMLWriterBase import XMLWriterBase
from Config import highlightingStylesFileFormatVersion

import Preferences

class HighlightingStylesWriter(XMLWriterBase):
    """
    Class implementing the writer class for writing a highlighting styles XML file.
    """
    def __init__(self, file, lexers):
        """
        Constructor
        
        @param file open file (like) object for writing
        @param lexers list of lexer objects for which to export the styles
        """
        XMLWriterBase.__init__(self, file)
        
        self.lexers = lexers
        self.email = Preferences.getUser("Email")
        
    def writeXML(self):
        """
        Public method to write the XML to the file.
        """
        XMLWriterBase.writeXML(self)
        
        self._write('<!DOCTYPE HighlightingStyles SYSTEM "HighlightingStyles-%s.dtd">' % \
            highlightingStylesFileFormatVersion)
        
        # add some generation comments
        self._write("<!-- Eric4 highlighting styles -->")
        self._write("<!-- Saved: %s -->" % time.strftime('%Y-%m-%d, %H:%M:%S'))
        self._write("<!-- Author: %s -->" % self.escape("%s" % self.email))
        
        # add the main tag
        self._write('<HighlightingStyles version="%s">' % \
            highlightingStylesFileFormatVersion)
        
        for lexer in self.lexers:
            self._write('  <Lexer name="%s">' % lexer.language())
            for style in lexer.descriptions:
                self._write('    <Style style="%d" '
                            'color="%s" paper="%s" font="%s" eolfill="%d">%s</Style>' % \
                            (style, lexer.color(style).name(), lexer.paper(style).name(), 
                             lexer.font(style).toString(), lexer.eolFill(style), 
                             self.escape(lexer.description(style)))
                )
            self._write('  </Lexer>')
        
        self._write("</HighlightingStyles>", newline = False)
