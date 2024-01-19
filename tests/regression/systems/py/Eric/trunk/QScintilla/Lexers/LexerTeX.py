# -*- coding: utf-8 -*-

# Copyright (c) 2005 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a Tex lexer with some additional methods.
"""

from PyQt4.Qsci import QsciLexerTeX
from PyQt4.QtCore import QString

from Lexer import Lexer

class LexerTeX(QsciLexerTeX, Lexer):
    """ 
    Subclass to implement some additional lexer dependant methods.
    """
    def __init__(self, parent=None):
        """
        Constructor
        
        @param parent parent widget of this lexer
        """
        QsciLexerTeX.__init__(self, parent)
        Lexer.__init__(self)
        
        self.commentString = QString("%")
    
    def isCommentStyle(self, style):
        """
        Public method to check, if a style is a comment style.
        
        @return flag indicating a comment style (boolean)
        """
        return False
    
    def isStringStyle(self, style):
        """
        Public method to check, if a style is a string style.
        
        @return flag indicating a string style (boolean)
        """
        return style in [QsciLexerTeX.Text]
