# -*- coding: utf-8 -*-

# Copyright (c) 2008 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a base class for custom lexers.
"""

from PyQt4.Qsci import QsciLexer
from PyQt4.QtCore import QString

from Lexer import Lexer

class LexerContainer(QsciLexer, Lexer):
    """ 
    Subclass as a base for the implementation of custom lexers.
    """
    def __init__(self, parent = None):
        """
        Constructor
        
        @param parent parent widget of this lexer
        """
        QsciLexer.__init__(self, parent)
        Lexer.__init__(self)
        
        self.editor = parent
    
    def language(self):
        """
        Public method returning the language of the lexer.
        
        @return language of the lexer (string)
        """
        return "Container"
    
    def lexer(self):
        """
        Public method returning the type of the lexer.
        
        @return type of the lexer (string)
        """
        if hasattr(self, 'lexerId'):
            return None
        else:
            return "container"
    
    def description(self, style):
        """
        Public method returning the descriptions of the styles supported
        by the lexer.
        
        <b>Note</b>: This methods needs to be overridden by the lexer class.
        
        @param style style number (integer)
        """
        return QString()
    
    def styleBitsNeeded(self):
        """
        Public method to get the number of style bits needed by the lexer.
        
        @return number of style bits needed (integer)
        """
        return 5
    
    def styleText(self, start, end):
        """
        Public method to perform the styling.
        
        @param start position of first character to be styled (integer)
        @param end position of last character to be styled (integer)
        """
        self.editor.startStyling(start, 0x1f)
        self.editor.setStyling(end - start + 1, 0)
