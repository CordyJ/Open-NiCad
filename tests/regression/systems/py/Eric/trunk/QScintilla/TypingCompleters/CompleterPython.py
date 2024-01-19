# -*- coding: utf-8 -*-

# Copyright (c) 2007 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a typing completer for Python.
"""

from PyQt4.QtCore import QObject, SIGNAL, QRegExp
from PyQt4.Qsci import QsciLexerPython

from CompleterBase import CompleterBase

import Preferences

class CompleterPython(CompleterBase):
    """
    Class implementing typing completer for Python.
    """
    def __init__(self, editor, parent = None):
        """
        Constructor
        
        @param editor reference to the editor object (QScintilla.Editor)
        @param parent reference to the parent object (QObject)
        """
        CompleterBase.__init__(self, editor, parent)
        
        self.__defRX = QRegExp(r"""^[ \t]*def \w+\(""")
        self.__defSelfRX = QRegExp(r"""^[ \t]*def \w+\([ \t]*self[ \t]*[,)]""")
        self.__defClsRX = QRegExp(r"""^[ \t]*def \w+\([ \t]*cls[ \t]*[,)]""")
        self.__classRX = QRegExp(r"""^[ \t]*class \w+\(""")
        self.__importRX = QRegExp(r"""^[ \t]*from [\w.]+ """)
        self.__classmethodRX = QRegExp(r"""^[ \t]*@classmethod""")
        
        self.__defOnlyRX = QRegExp(r"""^[ \t]*def """)
        
        self.__ifRX = QRegExp(r"""^[ \t]*if """)
        self.__elifRX = QRegExp(r"""^[ \t]*elif """)
        self.__elseRX = QRegExp(r"""^[ \t]*else:""")
        
        self.__tryRX = QRegExp(r"""^[ \t]*try:""")
        self.__finallyRX = QRegExp(r"""^[ \t]*finally:""")
        self.__exceptRX = QRegExp(r"""^[ \t]*except """)
        self.__exceptcRX = QRegExp(r"""^[ \t]*except:""")
        
        self.__whileRX = QRegExp(r"""^[ \t]*while """)
        self.__forRX = QRegExp(r"""^[ \t]*for """)
        
        self.readSettings()
    
    def readSettings(self):
        """
        Public slot called to reread the configuration parameters.
        """
        self.setEnabled(Preferences.getEditorTyping("Python/EnabledTypingAids"))
        self.__insertClosingBrace = \
            Preferences.getEditorTyping("Python/InsertClosingBrace")
        self.__indentBrace = \
            Preferences.getEditorTyping("Python/IndentBrace")
        self.__skipBrace = \
            Preferences.getEditorTyping("Python/SkipBrace")
        self.__insertQuote = \
            Preferences.getEditorTyping("Python/InsertQuote")
        self.__dedentElse = \
            Preferences.getEditorTyping("Python/DedentElse")
        self.__dedentExcept = \
            Preferences.getEditorTyping("Python/DedentExcept")
        self.__py24StyleTry = \
            Preferences.getEditorTyping("Python/Py24StyleTry")
        self.__insertImport = \
            Preferences.getEditorTyping("Python/InsertImport")
        self.__insertSelf = \
            Preferences.getEditorTyping("Python/InsertSelf")
        self.__insertBlank = \
            Preferences.getEditorTyping("Python/InsertBlank")
        self.__colonDetection= \
            Preferences.getEditorTyping("Python/ColonDetection")
        self.__dedentDef= \
            Preferences.getEditorTyping("Python/DedentDef")

    def charAdded(self, charNumber):
        """
        Public slot called to handle the user entering a character.
        
        @param charNumber value of the character entered (integer)
        """
        char = unichr(charNumber)
        if char not in ['(', ')', '{', '}', '[', ']', ' ', ',', "'", '"', '\n', ':']:
            return  # take the short route
        
        line, col = self.editor.getCursorPosition()
        
        if self.__inComment(line, col) or \
           (char != '"' and self.__inDoubleQuotedString()) or \
           (char != '"' and self.__inTripleDoubleQuotedString()) or \
           (char != "'" and self.__inSingleQuotedString()) or \
           (char != "'" and self.__inTripleSingleQuotedString()):
            return
        
        # open parenthesis
        # insert closing parenthesis and self
        if char == '(':
            txt = self.editor.text(line).left(col)
            if self.__insertSelf and \
               self.__defRX.exactMatch(txt):
                if self.__isClassmethodDef():
                    self.editor.insert('cls')
                    self.editor.setCursorPosition(line, col + 3)
                elif self.__isClassMethod():
                    self.editor.insert('self')
                    self.editor.setCursorPosition(line, col + 4)
            if self.__insertClosingBrace:
                if self.__defRX.exactMatch(txt) or \
                   self.__classRX.exactMatch(txt):
                    self.editor.insert('):')
                else:
                    self.editor.insert(')')
        
        # closing parenthesis
        # skip matching closing parenthesis
        elif char in [')', '}', ']']:
            if char == self.editor.text(line).mid(col, 1):
                if self.__skipBrace:
                    self.editor.setSelection(line, col, line, col + 1)
                    self.editor.removeSelectedText()
        
        # space
        # insert import, dedent to if for elif, dedent to try for except, dedent def
        elif char == ' ':
            txt = self.editor.text(line).left(col)
            if self.__insertImport and self.__importRX.exactMatch(txt):
                self.editor.insert('import ')
                self.editor.setCursorPosition(line, col + 7)
            elif self.__dedentElse and self.__elifRX.exactMatch(txt):
                self.__dedentToIf()
            elif self.__dedentExcept and self.__exceptRX.exactMatch(txt):
                self.__dedentExceptToTry(False)
            elif self.__dedentDef and self.__defOnlyRX.exactMatch(txt):
                self.__dedentDefStatement()
        
        # comma
        # insert blank
        elif char == ',':
            if self.__insertBlank:
                self.editor.insert(' ')
                self.editor.setCursorPosition(line, col + 1)
        
        # open curly brace
        # insert closing brace
        elif char == '{':
            if self.__insertClosingBrace:
                self.editor.insert('}')
        
        # open bracket
        # insert closing bracket
        elif char == '[':
            if self.__insertClosingBrace:
                self.editor.insert(']')
        
        # double quote
        # insert double quote
        elif char == '"':
            if self.__insertQuote:
                self.editor.insert('"')
        
        # quote
        # insert quote
        elif char == '\'':
            if self.__insertQuote:
                self.editor.insert('\'')
        
        # colon
        # skip colon, dedent to if for else:
        elif char == ':':
            if char == self.editor.text(line).mid(col, 1):
                if self.__colonDetection:
                    self.editor.setSelection(line, col, line, col + 1)
                    self.editor.removeSelectedText()
            else:
                txt = self.editor.text(line).left(col)
                if self.__dedentElse and self.__elseRX.exactMatch(txt):
                    self.__dedentElseToIfWhileForTry()
                elif self.__dedentExcept and self.__exceptcRX.exactMatch(txt):
                    self.__dedentExceptToTry(True)
                elif self.__dedentExcept and self.__finallyRX.exactMatch(txt):
                    self.__dedentFinallyToTry()
        
        # new line
        # indent to opening brace
        elif char == '\n':
            if self.__indentBrace:
                txt = self.editor.text(line - 1)
                if txt.lastIndexOf(QRegExp(":\r?\n")) == -1:
                    openCount = txt.count(QRegExp("[({[]"))
                    closeCount = txt.count(QRegExp("[)}\]]"))
                    if openCount > closeCount:
                        lastOpenIndex = 0
                        openCount = 0
                        closeCount = 0
                        while lastOpenIndex > -1 and openCount == closeCount:
                            lastOpenIndex = \
                                txt.lastIndexOf(QRegExp("[({[]"), lastOpenIndex - 1)
                            txt2 = txt.mid(lastOpenIndex)
                            openCount = txt2.count(QRegExp("[({[]"))
                            closeCount = txt2.count(QRegExp("[)}\]]"))
                        if lastOpenIndex > -1 and lastOpenIndex > col:
                            self.editor.insert(' ' * (lastOpenIndex - col + 1))
                            self.editor.setCursorPosition(line, lastOpenIndex + 1)
    
    def __dedentToIf(self):
        """
        Private method to dedent the last line to the last if statement with
        less (or equal) indentation.
        """
        line, col = self.editor.getCursorPosition()
        indentation = self.editor.indentation(line)
        ifLine = line - 1
        while ifLine >= 0:
            txt = self.editor.text(ifLine)
            edInd = self.editor.indentation(ifLine)
            if txt.indexOf(self.__elseRX) == 0 and edInd <= indentation:
                indentation = edInd - 1
            elif (txt.indexOf(self.__ifRX) == 0 or \
                  txt.indexOf(self.__elifRX) == 0) and edInd <= indentation:
                self.editor.cancelList()
                self.editor.setIndentation(line, edInd)
                break
            ifLine -= 1
    
    def __dedentElseToIfWhileForTry(self):
        """
        Private method to dedent the line of the else statement to the last
        if, while, for or try statement with less (or equal) indentation.
        """
        line, col = self.editor.getCursorPosition()
        indentation = self.editor.indentation(line)
        if line > 0:
            prevInd = self.editor.indentation(line - 1)
        ifLine = line - 1
        while ifLine >= 0:
            txt = self.editor.text(ifLine)
            edInd = self.editor.indentation(ifLine)
            if txt.indexOf(self.__elseRX) == 0 and edInd <= indentation:
                indentation = edInd - 1
            elif txt.indexOf(self.__elifRX) == 0 and \
                 edInd == indentation and \
                 edInd == prevInd:
                    indentation = edInd - 1
            elif (txt.indexOf(self.__ifRX) == 0 or \
                  txt.indexOf(self.__whileRX) == 0 or \
                  txt.indexOf(self.__forRX) == 0 or \
                  txt.indexOf(self.__tryRX) == 0) and \
                 edInd <= indentation:
                self.editor.cancelList()
                self.editor.setIndentation(line, edInd)
                break
            ifLine -= 1
    
    def __dedentExceptToTry(self, hasColon):
        """
        Private method to dedent the line of the except statement to the last 
        try statement with less (or equal) indentation.
        
        @param hasColon flag indicating the except type (boolean)
        """
        line, col = self.editor.getCursorPosition()
        indentation = self.editor.indentation(line)
        tryLine = line - 1
        while tryLine >= 0:
            txt = self.editor.text(tryLine)
            edInd = self.editor.indentation(tryLine)
            if (txt.indexOf(self.__exceptcRX) == 0 or \
                txt.indexOf(self.__finallyRX) == 0) and edInd <= indentation:
                indentation = edInd - 1
            elif (txt.indexOf(self.__exceptRX) == 0 or \
                  txt.indexOf(self.__tryRX) == 0) and edInd <= indentation:
                self.editor.cancelList()
                self.editor.setIndentation(line, edInd)
                break
            tryLine -= 1
    
    def __dedentFinallyToTry(self):
        """
        Private method to dedent the line of the except statement to the last 
        try statement with less (or equal) indentation.
        """
        line, col = self.editor.getCursorPosition()
        indentation = self.editor.indentation(line)
        tryLine = line - 1
        while tryLine >= 0:
            txt = self.editor.text(tryLine)
            edInd = self.editor.indentation(tryLine)
            if self.__py24StyleTry:
                if (txt.indexOf(self.__exceptcRX) == 0 or \
                    txt.indexOf(self.__exceptRX) == 0 or \
                    txt.indexOf(self.__finallyRX) == 0) and edInd <= indentation:
                    indentation = edInd - 1
                elif txt.indexOf(self.__tryRX) == 0 and edInd <= indentation:
                    self.editor.cancelList()
                    self.editor.setIndentation(line, edInd)
                    break
            else:
                if txt.indexOf(self.__finallyRX) == 0 and edInd <= indentation:
                    indentation = edInd - 1
                elif (txt.indexOf(self.__tryRX) == 0 or \
                      txt.indexOf(self.__exceptcRX) == 0 or \
                      txt.indexOf(self.__exceptRX) == 0) and edInd <= indentation:
                    self.editor.cancelList()
                    self.editor.setIndentation(line, edInd)
                    break
            tryLine -= 1
    
    def __dedentDefStatement(self):
        """
        Private method to dedent the line of the def statement to a previous def
        statement or class statement.
        """
        line, col = self.editor.getCursorPosition()
        indentation = self.editor.indentation(line)
        tryLine = line - 1
        while tryLine >= 0:
            txt = self.editor.text(tryLine)
            edInd = self.editor.indentation(tryLine)
            newInd = -1
            if txt.indexOf(self.__defRX) == 0 and edInd < indentation:
                newInd = edInd
            elif txt.indexOf(self.__classRX) == 0 and edInd < indentation:
                newInd = edInd + \
                    (self.editor.indentationWidth() or self.editor.tabWidth())
            if newInd >= 0:
                self.editor.cancelList()
                self.editor.setIndentation(line, newInd)
                break
            tryLine -= 1
    
    def __isClassMethod(self):
        """
        Private method to check, if the user is defining a class method.
        
        @return flag indicating the definition of a class method (boolean)
        """
        line, col = self.editor.getCursorPosition()
        indentation = self.editor.indentation(line)
        curLine = line - 1
        while curLine >= 0:
            if (self.editor.text(curLine).indexOf(self.__defSelfRX) == 0 or \
                self.editor.text(curLine).indexOf(self.__defClsRX) == 0) and \
               self.editor.indentation(curLine) == indentation:
                return True
            elif self.editor.text(curLine).indexOf(self.__classRX) == 0 and \
               self.editor.indentation(curLine) < indentation:
                return True
            elif self.editor.text(curLine).indexOf(self.__defRX) == 0 and \
               self.editor.indentation(curLine) <= indentation:
                return False
            curLine -= 1
        return False
    
    def __isClassmethodDef(self):
        """
        Private method to check, if the user is defing a classmethod 
        (@classmethod) method.
        
        @return flag indicating the definition of a classmethod method (boolean)
        """
        line, col = self.editor.getCursorPosition()
        indentation = self.editor.indentation(line)
        curLine = line - 1
        if self.editor.text(curLine).indexOf(self.__classmethodRX) == 0 and \
           self.editor.indentation(curLine) == indentation:
            return True
        return False
    
    def __inComment(self, line, col):
        """
        Private method to check, if the cursor is inside a comment
        
        @param line current line (integer)
        @param col current position within line (integer)
        @return flag indicating, if the cursor is inside a comment (boolean)
        """
        txt = self.editor.text(line)
        while col >= 0:
            if txt.mid(col, 1) == "#":
                return True
            col -= 1
        return False
    
    def __inDoubleQuotedString(self):
        """
        Private method to check, if the cursor is within a double quoted string.
        
        @return flag indicating, if the cursor is inside a double 
            quoted string (boolean)
        """
        return self.editor.currentStyle() == QsciLexerPython.DoubleQuotedString
    
    def __inTripleDoubleQuotedString(self):
        """
        Private method to check, if the cursor is within a triple double quoted string.
        
        @return flag indicating, if the cursor is inside a triple double 
            quoted string (boolean)
        """
        return self.editor.currentStyle() == QsciLexerPython.TripleDoubleQuotedString
    
    def __inSingleQuotedString(self):
        """
        Private method to check, if the cursor is within a single quoted string.
        
        @return flag indicating, if the cursor is inside a single 
            quoted string (boolean)
        """
        return self.editor.currentStyle() == QsciLexerPython.SingleQuotedString
    
    def __inTripleSingleQuotedString(self):
        """
        Private method to check, if the cursor is within a triple single quoted string.
        
        @return flag indicating, if the cursor is inside a triple single 
            quoted string (boolean)
        """
        return self.editor.currentStyle() == QsciLexerPython.TripleSingleQuotedString
