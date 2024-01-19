# -*- coding: utf-8 -*-

# Copyright (c) 2003 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a Java lexer with some additional methods.
"""

from PyQt4.Qsci import QsciLexerJava,  QsciScintilla
from PyQt4.QtCore import QString

from Lexer import Lexer
import Preferences

class LexerJava(QsciLexerJava, Lexer):
    """ 
    Subclass to implement some additional lexer dependant methods.
    """
    def __init__(self, parent=None):
        """
        Constructor
        
        @param parent parent widget of this lexer
        """
        QsciLexerJava.__init__(self, parent)
        Lexer.__init__(self)
        
        self.commentString = QString("//")
        self.streamCommentString = {
            'start' : QString('/* '),
            'end'   : QString(' */')
        }
        self.boxCommentString = {
            'start'  : QString('/* '),
            'middle' : QString(' * '),
            'end'    : QString(' */')
        }

    def initProperties(self):
        """
        Public slot to initialize the properties.
        """
        self.setFoldComments(Preferences.getEditor("CppFoldComment"))
        self.setFoldPreprocessor(Preferences.getEditor("CppFoldPreprocessor"))
        self.setFoldAtElse(Preferences.getEditor("CppFoldAtElse"))
        indentStyle = 0
        if Preferences.getEditor("CppIndentOpeningBrace"):
            indentStyle |= QsciScintilla.AiOpening
        if Preferences.getEditor("CppIndentClosingBrace"):
            indentStyle |= QsciScintilla.AiClosing
        self.setAutoIndentStyle(indentStyle)
        self.setFoldCompact(Preferences.getEditor("AllFoldCompact"))
    
    def isCommentStyle(self, style):
        """
        Public method to check, if a style is a comment style.
        
        @return flag indicating a comment style (boolean)
        """
        return style in [QsciLexerJava.Comment, 
                         QsciLexerJava.CommentDoc, 
                         QsciLexerJava.CommentLine, 
                         QsciLexerJava.CommentLineDoc]
    
    def isStringStyle(self, style):
        """
        Public method to check, if a style is a string style.
        
        @return flag indicating a string style (boolean)
        """
        return style in [QsciLexerJava.DoubleQuotedString, 
                         QsciLexerJava.SingleQuotedString, 
                         QsciLexerJava.UnclosedString, 
                         QsciLexerJava.VerbatimString]
