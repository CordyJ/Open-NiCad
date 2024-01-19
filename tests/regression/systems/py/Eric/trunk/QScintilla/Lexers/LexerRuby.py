# -*- coding: utf-8 -*-

# Copyright (c) 2005 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a Ruby lexer with some additional methods.
"""

from PyQt4.Qsci import QsciLexerRuby
from PyQt4.QtCore import QString, QStringList

from Lexer import Lexer

class LexerRuby(QsciLexerRuby, Lexer):
    """ 
    Subclass to implement some additional lexer dependant methods.
    """
    def __init__(self, parent=None):
        """
        Constructor
        
        @param parent parent widget of this lexer
        """
        QsciLexerRuby.__init__(self, parent)
        Lexer.__init__(self)
        
        self.commentString = QString("#")
    
    def autoCompletionWordSeparators(self):
        """
        Public method to return the list of separators for autocompletion.
        
        @return list of separators (QStringList)
        """
        return QStringList() << '.'
    
    def isCommentStyle(self, style):
        """
        Public method to check, if a style is a comment style.
        
        @return flag indicating a comment style (boolean)
        """
        return style in [QsciLexerRuby.Comment]
    
    def isStringStyle(self, style):
        """
        Public method to check, if a style is a string style.
        
        @return flag indicating a string style (boolean)
        """
        return style in [QsciLexerRuby.DoubleQuotedString, 
                         QsciLexerRuby.HereDocument, 
                         QsciLexerRuby.PercentStringQ, 
                         QsciLexerRuby.PercentStringq, 
                         QsciLexerRuby.PercentStringr, 
                         QsciLexerRuby.PercentStringw, 
                         QsciLexerRuby.PercentStringx, 
                         QsciLexerRuby.SingleQuotedString]
