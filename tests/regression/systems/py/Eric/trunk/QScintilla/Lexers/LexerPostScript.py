# -*- coding: utf-8 -*-

# Copyright (c) 2008 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a PostScript lexer with some additional methods.
"""

from PyQt4.Qsci import QsciLexerPostScript
from PyQt4.QtCore import QString

from Lexer import Lexer
import Preferences

class LexerPostScript(QsciLexerPostScript, Lexer):
    """ 
    Subclass to implement some additional lexer dependant methods.
    """
    def __init__(self, parent = None):
        """
        Constructor
        
        @param parent parent widget of this lexer
        """
        QsciLexerPostScript.__init__(self, parent)
        Lexer.__init__(self)
        
        self.commentString = QString("%")
    
    def initProperties(self):
        """
        Public slot to initialize the properties.
        """
        self.setTokenize(Preferences.getEditor("PostScriptTokenize"))
        self.setLevel(Preferences.getEditor("PostScriptLevel"))
        self.setFoldAtElse(Preferences.getEditor("PostScriptFoldAtElse"))
        self.setFoldCompact(Preferences.getEditor("AllFoldCompact"))
    
    def isCommentStyle(self, style):
        """
        Public method to check, if a style is a comment style.
        
        @return flag indicating a comment style (boolean)
        """
        return style in [QsciLexerPostScript.Comment]
    
    def isStringStyle(self, style):
        """
        Public method to check, if a style is a string style.
        
        @return flag indicating a string style (boolean)
        """
        return False
