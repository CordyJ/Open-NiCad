# -*- coding: utf-8 -*-

# Copyright (c) 2007 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a Povray lexer with some additional methods.
"""

from PyQt4.Qsci import QsciLexerPOV
from PyQt4.QtCore import QString

from Lexer import Lexer
import Preferences

class LexerPOV(QsciLexerPOV, Lexer):
    """ 
    Subclass to implement some additional lexer dependant methods.
    """
    def __init__(self, parent=None):
        """
        Constructor
        
        @param parent parent widget of this lexer
        """
        QsciLexerPOV.__init__(self, parent)
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
        self.setFoldComments(Preferences.getEditor("PovFoldComment"))
        self.setFoldDirectives(Preferences.getEditor("PovFoldDirectives"))
        self.setFoldCompact(Preferences.getEditor("AllFoldCompact"))
    
    def isCommentStyle(self, style):
        """
        Public method to check, if a style is a comment style.
        
        @return flag indicating a comment style (boolean)
        """
        return style in [QsciLexerPOV.Comment, 
                         QsciLexerPOV.CommentLine]
    
    def isStringStyle(self, style):
        """
        Public method to check, if a style is a string style.
        
        @return flag indicating a string style (boolean)
        """
        return style in [QsciLexerPOV.String, 
                         QsciLexerPOV.UnclosedString]
