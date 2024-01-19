# -*- coding: utf-8 -*-

# Copyright (c) 2004 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a Perl lexer with some additional methods.
"""

from PyQt4.Qsci import QsciLexerPerl
from PyQt4.QtCore import QString, QStringList

from Lexer import Lexer
import Preferences

class LexerPerl(QsciLexerPerl, Lexer):
    """ 
    Subclass to implement some additional lexer dependant methods.
    """
    def __init__(self, parent=None):
        """
        Constructor
        
        @param parent parent widget of this lexer
        """
        QsciLexerPerl.__init__(self, parent)
        Lexer.__init__(self)
        
        self.commentString = QString("#")
    
    def initProperties(self):
        """
        Public slot to initialize the properties.
        """
        self.setFoldComments(Preferences.getEditor("PerlFoldComment"))
        self.setFoldCompact(Preferences.getEditor("AllFoldCompact"))
        try:
            self.setFoldPackages(Preferences.getEditor("PerlFoldPackages"))
            self.setFoldPODBlocks(Preferences.getEditor("PerlFoldPODBlocks"))
        except AttributeError:
            pass
    
    def autoCompletionWordSeparators(self):
        """
        Public method to return the list of separators for autocompletion.
        
        @return list of separators (QStringList)
        """
        return QStringList() << '::' << '->'
    
    def isCommentStyle(self, style):
        """
        Public method to check, if a style is a comment style.
        
        @return flag indicating a comment style (boolean)
        """
        return style in [QsciLexerPerl.Comment]
    
    def isStringStyle(self, style):
        """
        Public method to check, if a style is a string style.
        
        @return flag indicating a string style (boolean)
        """
        return style in [QsciLexerPerl.DoubleQuotedHereDocument, 
                         QsciLexerPerl.DoubleQuotedString, 
                         QsciLexerPerl.QuotedStringQ, 
                         QsciLexerPerl.QuotedStringQQ, 
                         QsciLexerPerl.QuotedStringQR, 
                         QsciLexerPerl.QuotedStringQW, 
                         QsciLexerPerl.QuotedStringQX, 
                         QsciLexerPerl.SingleQuotedHereDocument, 
                         QsciLexerPerl.SingleQuotedString]
