# -*- coding: utf-8 -*-

# Copyright (c) 2007 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a CMake lexer with some additional methods.
"""

from PyQt4.Qsci import QsciLexerCMake
from PyQt4.QtCore import QString

from Lexer import Lexer
import Preferences

class LexerCMake(QsciLexerCMake, Lexer):
    """ 
    Subclass to implement some additional lexer dependant methods.
    """
    def __init__(self, parent=None):
        """
        Constructor
        
        @param parent parent widget of this lexer
        """
        QsciLexerCMake.__init__(self, parent)
        Lexer.__init__(self)
        
        self.commentString = QString("#")
    
    def initProperties(self):
        """
        Public slot to initialize the properties.
        """
        self.setFoldAtElse(Preferences.getEditor("CMakeFoldAtElse"))
    
    def isCommentStyle(self, style):
        """
        Public method to check, if a style is a comment style.
        
        @return flag indicating a comment style (boolean)
        """
        return style in [QsciLexerCMake.Comment]
    
    def isStringStyle(self, style):
        """
        Public method to check, if a style is a string style.
        
        @return flag indicating a string style (boolean)
        """
        return style in [QsciLexerCMake.String]
