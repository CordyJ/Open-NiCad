# -*- coding: utf-8 -*-

# Copyright (c) 2002 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a Python lexer with some additional methods.
"""

import re

from PyQt4.Qsci import QsciLexerPython,  QsciScintilla
from PyQt4.QtCore import QString, QStringList

from Lexer import Lexer
import Preferences

class LexerPython(QsciLexerPython, Lexer):
    """ 
    Subclass to implement some additional lexer dependant methods.
    """
    def __init__(self, parent=None):
        """
        Constructor
        
        @param parent parent widget of this lexer
        """
        QsciLexerPython.__init__(self, parent)
        Lexer.__init__(self)
        
        self.commentString = QString("#")

    def initProperties(self):
        """
        Public slot to initialize the properties.
        """
        if Preferences.getEditor("PythonBadIndentation"):
            self.setIndentationWarning(QsciLexerPython.Inconsistent)
        else:
            self.setIndentationWarning(QsciLexerPython.NoWarning)
        self.setFoldComments(Preferences.getEditor("PythonFoldComment"))
        self.setFoldQuotes(Preferences.getEditor("PythonFoldString"))
        if not Preferences.getEditor("PythonAutoIndent"):
           self.setAutoIndentStyle(QsciScintilla.AiMaintain)
        try:
            self.setV2UnicodeAllowed(Preferences.getEditor("PythonAllowV2Unicode"))
            self.setV3BinaryOctalAllowed(Preferences.getEditor("PythonAllowV3Binary"))
            self.setV3BytesAllowed(Preferences.getEditor("PythonAllowV3Bytes"))
        except AttributeError:
            pass
        
    def getIndentationDifference(self, line, editor):
        """
        Private method to determine the difference for the new indentation.
        
        @param line line to perform the calculation for (integer)
        @param editor QScintilla editor
        @return amount of difference in indentation (integer)
        """
        indent_width = Preferences.getEditor('IndentWidth')
        
        lead_spaces = editor.indentation(line)
        
        pline = line - 1
        while pline >= 0 and re.match('^\s*(#.*)?$', unicode(editor.text(pline))):
            pline -= 1
        
        if pline < 0:
            last = 0
        else:
            previous_lead_spaces = editor.indentation(pline)
            # trailing spaces
            m = re.search(':\s*(#.*)?$', unicode(editor.text(pline)))
            last = previous_lead_spaces
            if m:
                last += indent_width
            else:
                # special cases, like pass (unindent) or return (also unindent)
                m = re.search('(pass\s*(#.*)?$)|(^[^#]return)', 
                              unicode(editor.text(pline)))
                if m:
                    last -= indent_width
        
        if lead_spaces % indent_width != 0 or lead_spaces == 0 \
           or self.lastIndented != line:
            indentDifference = last - lead_spaces
        else:
            indentDifference = -indent_width
        
        return indentDifference
    
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
        return style in [QsciLexerPython.Comment, 
                         QsciLexerPython.CommentBlock]
    
    def isStringStyle(self, style):
        """
        Public method to check, if a style is a string style.
        
        @return flag indicating a string style (boolean)
        """
        return style in [QsciLexerPython.DoubleQuotedString, 
                         QsciLexerPython.SingleQuotedString, 
                         QsciLexerPython.TripleDoubleQuotedString, 
                         QsciLexerPython.TripleSingleQuotedString, 
                         QsciLexerPython.UnclosedString]
