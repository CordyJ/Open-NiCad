# -*- coding: utf-8 -*-

# Copyright (c) 2008 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a Pascal lexer with some additional methods.
"""

from PyQt4.Qsci import QsciLexerPascal, QsciScintilla
from PyQt4.QtCore import QString, QStringList

from Lexer import Lexer
import Preferences

class LexerPascal(QsciLexerPascal, Lexer):
    """ 
    Subclass to implement some additional lexer dependant methods.
    """
    def __init__(self, parent = None):
        """
        Constructor
        
        @param parent parent widget of this lexer
        """
        QsciLexerPascal.__init__(self, parent)
        Lexer.__init__(self)
        
        self.commentString = QString("//")
        self.streamCommentString = {
            'start' : QString('{ '),
            'end'   : QString(' }')
        }
    
    def initProperties(self):
        """
        Public slot to initialize the properties.
        """
        self.setFoldComments(Preferences.getEditor("PascalFoldComment"))
        self.setFoldPreprocessor(Preferences.getEditor("PascalFoldPreprocessor"))
        self.setFoldCompact(Preferences.getEditor("AllFoldCompact"))
        try:
            self.setSmartHighlighting(Preferences.getEditor("PascalSmartHighlighting"))
        except AttributeError:
            pass
    
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
        try:
            return style in [QsciLexerPascal.Comment, 
                             QsciLexerPascal.CommentDoc, 
                             QsciLexerPascal.CommentLine]
        except AttributeError:
            return style in [QsciLexerPascal.Comment, 
                             QsciLexerPascal.CommentParenthesis, 
                             QsciLexerPascal.CommentLine]
    
    def isStringStyle(self, style):
        """
        Public method to check, if a style is a string style.
        
        @return flag indicating a string style (boolean)
        """
        return style in [QsciLexerPascal.SingleQuotedString]
