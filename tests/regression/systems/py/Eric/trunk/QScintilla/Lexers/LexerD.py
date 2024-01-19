# -*- coding: utf-8 -*-

# Copyright (c) 2007 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a D lexer with some additional methods.
"""

from PyQt4.Qsci import QsciLexerD, QsciScintilla
from PyQt4.QtCore import QString, QStringList

from Lexer import Lexer
import Preferences

class LexerD(QsciLexerD, Lexer):
    """ 
    Subclass to implement some additional lexer dependant methods.
    """
    def __init__(self, parent=None):
        """
        Constructor
        
        @param parent parent widget of this lexer
        """
        QsciLexerD.__init__(self, parent)
        Lexer.__init__(self)
        
        self.commentString = QString("//")
        self.streamCommentString = {
            'start' : QString('/+ '),
            'end'   : QString(' +/')
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
        self.setFoldComments(Preferences.getEditor("DFoldComment"))
        self.setFoldAtElse(Preferences.getEditor("DFoldAtElse"))
        indentStyle = 0
        if Preferences.getEditor("DIndentOpeningBrace"):
            indentStyle |= QsciScintilla.AiOpening
        if Preferences.getEditor("DIndentClosingBrace"):
            indentStyle |= QsciScintilla.AiClosing
        self.setAutoIndentStyle(indentStyle)
        self.setFoldCompact(Preferences.getEditor("AllFoldCompact"))
    
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
        return style in [QsciLexerD.Comment, 
                         QsciLexerD.CommentDoc, 
                         QsciLexerD.CommentLine, 
                         QsciLexerD.CommentLineDoc, 
                         QsciLexerD.CommentNested]
    
    def isStringStyle(self, style):
        """
        Public method to check, if a style is a string style.
        
        @return flag indicating a string style (boolean)
        """
        return style in [QsciLexerD.String, 
                         QsciLexerD.UnclosedString]
