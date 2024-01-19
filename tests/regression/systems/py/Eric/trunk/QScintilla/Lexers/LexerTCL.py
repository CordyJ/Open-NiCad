# -*- coding: utf-8 -*-

# Copyright (c) 2008 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a TCL/Tk lexer with some additional methods.
"""

from PyQt4.Qsci import QsciLexerTCL
from PyQt4.QtCore import QString

from Lexer import Lexer

import Preferences

class LexerTCL(QsciLexerTCL, Lexer):
    """ 
    Subclass to implement some additional lexer dependant methods.
    """
    def __init__(self, parent=None):
        """
        Constructor
        
        @param parent parent widget of this lexer
        """
        QsciLexerTCL.__init__(self, parent)
        Lexer.__init__(self)
        
        self.commentString = QString("#")
    
    def initProperties(self):
        """
        Public slot to initialize the properties.
        """
        self.setFoldCompact(Preferences.getEditor("AllFoldCompact"))
    
    def isCommentStyle(self, style):
        """
        Public method to check, if a style is a comment style.
        
        @return flag indicating a comment style (boolean)
        """
        return style in [QsciLexerTCL.Comment, 
                         QsciLexerTCL.CommentBlock, 
                         QsciLexerTCL.CommentBox, 
                         QsciLexerTCL.CommentLine]
    
    def isStringStyle(self, style):
        """
        Public method to check, if a style is a string style.
        
        @return flag indicating a string style (boolean)
        """
        return style in [QsciLexerTCL.QuotedString]
