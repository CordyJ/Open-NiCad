# -*- coding: utf-8 -*-

# Copyright (c) 2002 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a CPP lexer with some additional methods.
"""

from PyQt4.Qsci import QsciLexerCPP,  QsciScintilla
from PyQt4.QtCore import QString, QStringList

from Lexer import Lexer
import Preferences

class LexerCPP(QsciLexerCPP, Lexer):
    """ 
    Subclass to implement some additional lexer dependant methods.
    """
    def __init__(self, parent=None, caseInsensitiveKeywords = False):
        """
        Constructor
        
        @param parent parent widget of this lexer
        """
        QsciLexerCPP.__init__(self, parent, caseInsensitiveKeywords)
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
        try:
            self.setDollarsAllowed(Preferences.getEditor("CppDollarsAllowed"))
        except AttributeError:
            pass
    
    def autoCompletionWordSeparators(self):
        """
        Public method to return the list of separators for autocompletion.
        
        @return list of separators (QStringList)
        """
        return QStringList() << '::' << '->' << '.'
    
    def isCommentStyle(self, style):
        """
        Public method to check, if a style is a comment style.
        
        @return flag indicating a comment style (boolean)
        """
        return style in [QsciLexerCPP.Comment, 
                         QsciLexerCPP.CommentDoc, 
                         QsciLexerCPP.CommentLine, 
                         QsciLexerCPP.CommentLineDoc]
    
    def isStringStyle(self, style):
        """
        Public method to check, if a style is a string style.
        
        @return flag indicating a string style (boolean)
        """
        return style in [QsciLexerCPP.DoubleQuotedString, 
                         QsciLexerCPP.SingleQuotedString, 
                         QsciLexerCPP.UnclosedString, 
                         QsciLexerCPP.VerbatimString]
