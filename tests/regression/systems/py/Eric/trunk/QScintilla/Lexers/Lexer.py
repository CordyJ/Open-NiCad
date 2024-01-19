# -*- coding: utf-8 -*-

# Copyright (c) 2003 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the lexer base class.
"""

from PyQt4.QtCore import QString, QStringList

import Preferences

class Lexer(object):
    """ 
    Class to implement the lexer mixin class.
    """
    def __init__(self):
        """
        Constructor
        """
        self.commentString = QString('')
        self.streamCommentString = {
            'start' : QString(''),
            'end' : QString('')
        }
        self.boxCommentString = {
            'start' : QString(''),
            'middle' : QString(''),
            'end' : QString('')
        }
        
        # last indented line wrapper
        self.lastIndented = -1
        self.lastIndentedIndex = -1
        
        # always keep tabs (for languages where tabs are esential
        self._alwaysKeepTabs = False
    
    def initProperties(self):
        """
        Public slot to initialize the properties.
        """
        # default implementation is a do nothing
        return
        
    def commentStr(self):
        """
        Public method to return the comment string.
        
        @return comment string (QString)
        """
        return self.commentString
        
    def canBlockComment(self):
        """
        Public method to determine, whether the lexer language supports a block comment.
        
        @return flag (boolean)
        """
        return not self.commentString.isEmpty()
        
    def streamCommentStr(self):
        """
        Public method to return the stream comment strings.
        
        @return stream comment strings (dictionary with two QStrings)
        """
        return self.streamCommentString
        
    def canStreamComment(self):
        """
        Public method to determine, whether the lexer language supports a stream comment.
        
        @return flag (boolean)
        """
        return \
            (not self.streamCommentString['start'].isEmpty()) and \
            (not self.streamCommentString['end'].isEmpty())
        
    def boxCommentStr(self):
        """
        Public method to return the box comment strings.
        
        @return box comment strings (dictionary with three QStrings)
        """
        return self.boxCommentString
        
    def canBoxComment(self):
        """
        Public method to determine, whether the lexer language supports a box comment.
        
        @return flag (boolean)
        """
        return \
            (not self.boxCommentString['start'].isEmpty()) and \
            (not self.boxCommentString['middle'].isEmpty()) and \
            (not self.boxCommentString['end'].isEmpty())
        
    def alwaysKeepTabs(self):
        """
        Public method to check, if tab conversion is allowed.
        
        @return flag indicating to keep tabs (boolean)
        """
        return self._alwaysKeepTabs
        
    def hasSmartIndent(self):
        """
        Public method indicating whether lexer can do smart indentation.
        
        @return flag indicating availability of smartIndentLine and
            smartIndentSelection methods (boolean)
        """
        return hasattr(self, 'getIndentationDifference')
        
    def smartIndentLine(self, editor):
        """
        Public method to handle smart indentation for a line.
        
        @param editor reference to the QScintilla editor object
        """
        cline, cindex = editor.getCursorPosition()
        
        # get leading spaces
        lead_spaces = editor.indentation(cline)
        
        # get the indentation difference
        indentDifference = self.getIndentationDifference(cline, editor)
        
        if indentDifference != 0:
            editor.setIndentation(cline, lead_spaces + indentDifference)
            editor.setCursorPosition(cline, cindex + indentDifference)
        
        self.lastIndented = cline
        
    def smartIndentSelection(self, editor):
        """
        Public method to handle smart indentation for a selection of lines.
        
        Note: The assumption is, that the first line determines the new
              indentation level.
        
        @param editor reference to the QScintilla editor object
        """
        if not editor.hasSelectedText():
            return
            
        # get the selection
        lineFrom, indexFrom, lineTo, indexTo = editor.getSelection()
        if lineFrom != self.lastIndented:
            self.lastIndentedIndex = indexFrom
        
        if indexTo == 0:
            endLine = lineTo - 1
        else:
            endLine = lineTo
        
        # get the indentation difference
        indentDifference = self.getIndentationDifference(lineFrom, editor)
        
        editor.beginUndoAction()
        # iterate over the lines
        for line in range(lineFrom, endLine+1):
            editor.setIndentation(line, 
                editor.indentation(line) + indentDifference)
        editor.endUndoAction()
        
        if self.lastIndentedIndex != 0:
            indexStart = indexFrom + indentDifference
        else:
            indexStart = 0
        if indexStart < 0:
            indexStart = 0
        indexEnd = indexTo != 0 and (indexTo + indentDifference) or 0
        if indexEnd < 0:
            indexEnd = 0
        editor.setSelection(lineFrom, indexStart, lineTo, indexEnd)
        
        self.lastIndented = lineFrom
    
    def autoCompletionWordSeparators(self):
        """
        Public method to return the list of separators for autocompletion.
        
        @return list of separators (QStringList)
        """
        return QStringList()
    
    def isCommentStyle(self, style):
        """
        Public method to check, if a style is a comment style.
        
        @return flag indicating a comment style (boolean)
        """
        return True
    
    def isStringStyle(self, style):
        """
        Public method to check, if a style is a string style.
        
        @return flag indicating a string style (boolean)
        """
        return True
