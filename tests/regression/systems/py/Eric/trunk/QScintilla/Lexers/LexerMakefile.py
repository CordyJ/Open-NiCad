# -*- coding: utf-8 -*-

# Copyright (c) 2005 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a Makefile lexer with some additional methods.
"""

from PyQt4.Qsci import QsciLexerMakefile
from PyQt4.QtCore import QString

from Lexer import Lexer

class LexerMakefile(QsciLexerMakefile, Lexer):
    """ 
    Subclass to implement some additional lexer dependant methods.
    """
    def __init__(self, parent=None):
        """
        Constructor
        
        @param parent parent widget of this lexer
        """
        QsciLexerMakefile.__init__(self, parent)
        Lexer.__init__(self)
        
        self.commentString = QString("#")
        self._alwaysKeepTabs = True
    
    def isCommentStyle(self, style):
        """
        Public method to check, if a style is a comment style.
        
        @return flag indicating a comment style (boolean)
        """
        return style in [QsciLexerMakefile.Comment]
    
    def isStringStyle(self, style):
        """
        Public method to check, if a style is a string style.
        
        @return flag indicating a string style (boolean)
        """
        return False
