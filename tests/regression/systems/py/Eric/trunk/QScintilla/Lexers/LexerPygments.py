# -*- coding: utf-8 -*-

# Copyright (c) 2008 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a custom lexer using pygments.
"""

import sys

from pygments.token import Token
from pygments.lexers import guess_lexer_for_filename, guess_lexer, find_lexer_class
from pygments.util import ClassNotFound

from PyQt4.QtCore import QString
from PyQt4.QtGui import QColor, QFont

from QScintilla.Lexers.LexerContainer import LexerContainer

import Utilities

PYGMENTS_DEFAULT, \
PYGMENTS_COMMENT, \
PYGMENTS_PREPROCESSOR, \
PYGMENTS_KEYWORD, \
PYGMENTS_PSEUDOKEYWORD, \
PYGMENTS_TYPEKEYWORD, \
PYGMENTS_OPERATOR, \
PYGMENTS_WORD, \
PYGMENTS_BUILTIN, \
PYGMENTS_FUNCTION, \
PYGMENTS_CLASS, \
PYGMENTS_NAMESPACE, \
PYGMENTS_EXCEPTION, \
PYGMENTS_VARIABLE, \
PYGMENTS_CONSTANT, \
PYGMENTS_LABEL, \
PYGMENTS_ENTITY, \
PYGMENTS_ATTRIBUTE, \
PYGMENTS_TAG, \
PYGMENTS_DECORATOR, \
PYGMENTS_STRING, \
PYGMENTS_DOCSTRING, \
PYGMENTS_SCALAR, \
PYGMENTS_ESCAPE, \
PYGMENTS_REGEX, \
PYGMENTS_SYMBOL, \
PYGMENTS_OTHER, \
PYGMENTS_NUMBER, \
PYGMENTS_HEADING, \
PYGMENTS_SUBHEADING, \
PYGMENTS_DELETED, \
PYGMENTS_INSERTED           = range(32)
# 32 to 39 are reserved for QScintilla internal styles
PYGMENTS_GENERIC_ERROR, \
PYGMENTS_EMPHASIZE, \
PYGMENTS_STRONG, \
PYGMENTS_PROMPT, \
PYGMENTS_OUTPUT, \
PYGMENTS_TRACEBACK, \
PYGMENTS_ERROR              = range(40, 47)

#-----------------------------------------------------------------------------#

TOKEN_MAP = {
    Token.Comment:                   PYGMENTS_COMMENT,
    Token.Comment.Preproc:           PYGMENTS_PREPROCESSOR,

    Token.Keyword:                   PYGMENTS_KEYWORD,
    Token.Keyword.Pseudo:            PYGMENTS_PSEUDOKEYWORD,
    Token.Keyword.Type:              PYGMENTS_TYPEKEYWORD,

    Token.Operator:                  PYGMENTS_OPERATOR,
    Token.Operator.Word:             PYGMENTS_WORD,

    Token.Name.Builtin:              PYGMENTS_BUILTIN,
    Token.Name.Function:             PYGMENTS_FUNCTION,
    Token.Name.Class:                PYGMENTS_CLASS,
    Token.Name.Namespace:            PYGMENTS_NAMESPACE,
    Token.Name.Exception:            PYGMENTS_EXCEPTION,
    Token.Name.Variable:             PYGMENTS_VARIABLE,
    Token.Name.Constant:             PYGMENTS_CONSTANT,
    Token.Name.Label:                PYGMENTS_LABEL,
    Token.Name.Entity:               PYGMENTS_ENTITY,
    Token.Name.Attribute:            PYGMENTS_ATTRIBUTE,
    Token.Name.Tag:                  PYGMENTS_TAG,
    Token.Name.Decorator:            PYGMENTS_DECORATOR,

    Token.String:                    PYGMENTS_STRING,
    Token.String.Doc:                PYGMENTS_DOCSTRING,
    Token.String.Interpol:           PYGMENTS_SCALAR,
    Token.String.Escape:             PYGMENTS_ESCAPE,
    Token.String.Regex:              PYGMENTS_REGEX,
    Token.String.Symbol:             PYGMENTS_SYMBOL,
    Token.String.Other:              PYGMENTS_OTHER,
    Token.Number:                    PYGMENTS_NUMBER,

    Token.Generic.Heading:           PYGMENTS_HEADING,
    Token.Generic.Subheading:        PYGMENTS_SUBHEADING,
    Token.Generic.Deleted:           PYGMENTS_DELETED,
    Token.Generic.Inserted:          PYGMENTS_INSERTED,
    Token.Generic.Error:             PYGMENTS_GENERIC_ERROR,
    Token.Generic.Emph:              PYGMENTS_EMPHASIZE,
    Token.Generic.Strong:            PYGMENTS_STRONG,
    Token.Generic.Prompt:            PYGMENTS_PROMPT,
    Token.Generic.Output:            PYGMENTS_OUTPUT,
    Token.Generic.Traceback:         PYGMENTS_TRACEBACK,

    Token.Error:                     PYGMENTS_ERROR, 
}

#-----------------------------------------------------------------------------#

class LexerPygments(LexerContainer):
    """ 
    Class implementing a custom lexer using pygments.
    """
    def __init__(self, parent = None, name = ""):
        """
        Constructor
        
        @param parent parent widget of this lexer
        @keyparam name name of the pygments lexer to use (string)
        """
        LexerContainer.__init__(self, parent)
        
        self.__pygmentsName = name
        
        self.descriptions = {
            PYGMENTS_DEFAULT       : self.trUtf8("Default"), 
            PYGMENTS_COMMENT       : self.trUtf8("Comment"), 
            PYGMENTS_PREPROCESSOR  : self.trUtf8("Preprocessor"), 
            PYGMENTS_KEYWORD       : self.trUtf8("Keyword"), 
            PYGMENTS_PSEUDOKEYWORD : self.trUtf8("Pseudo Keyword"), 
            PYGMENTS_TYPEKEYWORD   : self.trUtf8("Type Keyword"), 
            PYGMENTS_OPERATOR      : self.trUtf8("Operator"), 
            PYGMENTS_WORD          : self.trUtf8("Word"), 
            PYGMENTS_BUILTIN       : self.trUtf8("Builtin"), 
            PYGMENTS_FUNCTION      : self.trUtf8("Function or method name"), 
            PYGMENTS_CLASS         : self.trUtf8("Class name"), 
            PYGMENTS_NAMESPACE     : self.trUtf8("Namespace"), 
            PYGMENTS_EXCEPTION     : self.trUtf8("Exception"), 
            PYGMENTS_VARIABLE      : self.trUtf8("Identifier"), 
            PYGMENTS_CONSTANT      : self.trUtf8("Constant"), 
            PYGMENTS_LABEL         : self.trUtf8("Label"), 
            PYGMENTS_ENTITY        : self.trUtf8("Entity"), 
            PYGMENTS_ATTRIBUTE     : self.trUtf8("Attribute"), 
            PYGMENTS_TAG           : self.trUtf8("Tag"), 
            PYGMENTS_DECORATOR     : self.trUtf8("Decorator"), 
            PYGMENTS_STRING        : self.trUtf8("String"), 
            PYGMENTS_DOCSTRING     : self.trUtf8("Documentation string"), 
            PYGMENTS_SCALAR        : self.trUtf8("Scalar"), 
            PYGMENTS_ESCAPE        : self.trUtf8("Escape"), 
            PYGMENTS_REGEX         : self.trUtf8("Regular expression"), 
            PYGMENTS_SYMBOL        : self.trUtf8("Symbol"), 
            PYGMENTS_OTHER         : self.trUtf8("Other string"), 
            PYGMENTS_NUMBER        : self.trUtf8("Number"), 
            PYGMENTS_HEADING       : self.trUtf8("Heading"), 
            PYGMENTS_SUBHEADING    : self.trUtf8("Subheading"), 
            PYGMENTS_DELETED       : self.trUtf8("Deleted"), 
            PYGMENTS_INSERTED      : self.trUtf8("Inserted"), 
            PYGMENTS_GENERIC_ERROR : self.trUtf8("Generic error"), 
            PYGMENTS_EMPHASIZE     : self.trUtf8("Emphasized text"), 
            PYGMENTS_STRONG        : self.trUtf8("Strong text"), 
            PYGMENTS_PROMPT        : self.trUtf8("Prompt"), 
            PYGMENTS_OUTPUT        : self.trUtf8("Output"), 
            PYGMENTS_TRACEBACK     : self.trUtf8("Traceback"), 
            PYGMENTS_ERROR         : self.trUtf8("Error"), 
        }
        
        self.defaultColors = {
            PYGMENTS_DEFAULT       : QColor("#000000"), 
            PYGMENTS_COMMENT       : QColor("#408080"), 
            PYGMENTS_PREPROCESSOR  : QColor("#BC7A00"), 
            PYGMENTS_KEYWORD       : QColor("#008000"), 
            PYGMENTS_PSEUDOKEYWORD : QColor("#008000"), 
            PYGMENTS_TYPEKEYWORD   : QColor("#B00040"), 
            PYGMENTS_OPERATOR      : QColor("#666666"), 
            PYGMENTS_WORD          : QColor("#AA22FF"), 
            PYGMENTS_BUILTIN       : QColor("#008000"), 
            PYGMENTS_FUNCTION      : QColor("#0000FF"), 
            PYGMENTS_CLASS         : QColor("#0000FF"), 
            PYGMENTS_NAMESPACE     : QColor("#0000FF"), 
            PYGMENTS_EXCEPTION     : QColor("#D2413A"), 
            PYGMENTS_VARIABLE      : QColor("#19177C"), 
            PYGMENTS_CONSTANT      : QColor("#880000"), 
            PYGMENTS_LABEL         : QColor("#A0A000"), 
            PYGMENTS_ENTITY        : QColor("#999999"), 
            PYGMENTS_ATTRIBUTE     : QColor("#7D9029"), 
            PYGMENTS_TAG           : QColor("#008000"), 
            PYGMENTS_DECORATOR     : QColor("#AA22FF"), 
            PYGMENTS_STRING        : QColor("#BA2121"), 
            PYGMENTS_DOCSTRING     : QColor("#BA2121"), 
            PYGMENTS_SCALAR        : QColor("#BB6688"), 
            PYGMENTS_ESCAPE        : QColor("#BB6622"), 
            PYGMENTS_REGEX         : QColor("#BB6688"), 
            PYGMENTS_SYMBOL        : QColor("#19177C"), 
            PYGMENTS_OTHER         : QColor("#008000"), 
            PYGMENTS_NUMBER        : QColor("#666666"), 
            PYGMENTS_HEADING       : QColor("#000080"), 
            PYGMENTS_SUBHEADING    : QColor("#800080"), 
            PYGMENTS_DELETED       : QColor("#A00000"), 
            PYGMENTS_INSERTED      : QColor("#00A000"), 
            PYGMENTS_GENERIC_ERROR : QColor("#FF0000"), 
            PYGMENTS_PROMPT        : QColor("#000080"), 
            PYGMENTS_OUTPUT        : QColor("#808080"), 
            PYGMENTS_TRACEBACK     : QColor("#0040D0"), 
        }
        
        self.defaultPapers = {
            PYGMENTS_ERROR         : QColor("#FF0000"), 
        }
    
    def language(self):
        """
        Public method returning the language of the lexer.
        
        @return language of the lexer (string)
        """
        return "Guessed"
    
    def description(self, style):
        """
        Public method returning the descriptions of the styles supported
        by the lexer.
        
        @param style style number (integer)
        """
        try:
            return self.descriptions[style]
        except KeyError:
            return QString()
    
    def defaultColor(self, style):
        """
        Public method to get the default foreground color for a style.
        
        @param style style number (integer)
        @return foreground color (QColor)
        """
        try:
            return self.defaultColors[style]
        except KeyError:
            return LexerContainer.defaultColor(self, style)
    
    def defaultPaper(self, style):
        """
        Public method to get the default background color for a style.
        
        @param style style number (integer)
        @return background color (QColor)
        """
        try:
            return self.defaultPapers[style]
        except KeyError:
            return LexerContainer.defaultPaper(self, style)
    
    def defaultFont(self, style):
        """
        Public method to get the default font for a style.
        
        @param style style number (integer)
        @return font (QFont)
        """
        if style in [PYGMENTS_COMMENT, PYGMENTS_PREPROCESSOR]:
            if Utilities.isWindowsPlatform():
                f = QFont("Comic Sans MS", 9)
            else:
                f = QFont("Bitstream Vera Serif", 9)
            if style == PYGMENTS_PREPROCESSOR:
                f.setItalic(True)
            return f
        
        if style in [PYGMENTS_STRING]:
            if Utilities.isWindowsPlatform():
                return QFont("Comic Sans MS", 10)
            else:
                return QFont("Bitstream Vera Serif", 10)
        
        if style in [PYGMENTS_KEYWORD, PYGMENTS_OPERATOR, PYGMENTS_WORD, PYGMENTS_BUILTIN,
                     PYGMENTS_ATTRIBUTE, PYGMENTS_FUNCTION, PYGMENTS_CLASS, 
                     PYGMENTS_NAMESPACE, PYGMENTS_EXCEPTION, PYGMENTS_ENTITY, 
                     PYGMENTS_TAG, PYGMENTS_SCALAR, PYGMENTS_ESCAPE, PYGMENTS_HEADING, 
                     PYGMENTS_SUBHEADING, PYGMENTS_STRONG, PYGMENTS_PROMPT]:
            f = LexerContainer.defaultFont(self, style)
            f.setBold(True)
            return f
        
        if style in [PYGMENTS_DOCSTRING, PYGMENTS_EMPHASIZE]:
            f = LexerContainer.defaultFont(self, style)
            f.setItalic(True)
            return f
        
        return LexerContainer.defaultFont(self, style)
    
    def styleBitsNeeded(self):
        """
        Public method to get the number of style bits needed by the lexer.
        
        @return number of style bits needed (integer)
        """
        return 6
    
    def __guessLexer(self, text):
        """
        Private method to guess a pygments lexer.
        
        @param text text to base guessing on (string)
        @return reference to the guessed lexer (pygments.lexer)
        """
        lexer = None
        
        if self.__pygmentsName:
            lexerClass = find_lexer_class(self.__pygmentsName)
            if lexerClass is not None:
                lexer = lexerClass()
        
        elif text:
            # step 1: guess based on filename and text
            if self.editor is not None:
                fn = self.editor.getFileName()
                try:
                    lexer = guess_lexer_for_filename(fn, text)
                except ClassNotFound:
                    pass
            
            # step 2: guess on text only
            if lexer is None:
                try:
                    lexer = guess_lexer(text)
                except ClassNotFound:
                    pass
        
        return lexer
    
    def canStyle(self):
        """
        Public method to check, if the lexer is able to style the text.
        
        @return flag indicating the lexer capability (boolean)
        """
        if self.editor is None:
            return True
        
        text = unicode(self.editor.text()).encode('utf-8')
        self.__lexer = self.__guessLexer(text)
        
        return self.__lexer is not None
    
    def name(self):
        """
        Public method to get the name of the pygments lexer.
        
        @return name of the pygments lexer (string)
        """
        if self.__lexer is None:
            return ""
        else:
            return self.__lexer.name
    
    def styleText(self, start, end):
        """
        Public method to perform the styling.
        
        @param start position of first character to be styled (integer)
        @param end position of last character to be styled (integer)
        """
        text = unicode(self.editor.text())[:end + 1].encode('utf-8')
        self.__lexer = self.__guessLexer(text)
        
        cpos = 0
        self.editor.startStyling(cpos, 0x3f)
        if self.__lexer is None:
            self.editor.setStyling(len(text), PYGMENTS_DEFAULT)
        else:
            eolLen = len(self.editor.getLineSeparator())
            for token, txt in self.__lexer.get_tokens(text):
                style = TOKEN_MAP.get(token, PYGMENTS_DEFAULT)
                
                tlen = len(txt)
                if eolLen > 1:
                    tlen += txt.count('\n')
                if tlen:
                    self.editor.setStyling(tlen, style)
                cpos += tlen
            self.editor.startStyling(cpos, 0x3f)
    
    def isCommentStyle(self, style):
        """
        Public method to check, if a style is a comment style.
        
        @return flag indicating a comment style (boolean)
        """
        return style in [PYGMENTS_COMMENT]
    
    def isStringStyle(self, style):
        """
        Public method to check, if a style is a string style.
        
        @return flag indicating a string style (boolean)
        """
        return style in [PYGMENTS_STRING, PYGMENTS_DOCSTRING, PYGMENTS_OTHER, 
                         PYGMENTS_HEADING, PYGMENTS_SUBHEADING, PYGMENTS_EMPHASIZE, 
                         PYGMENTS_STRONG]
