# -*- coding: utf-8 -*-

# Copyright (c) 2002 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a special QextScintilla lexer to handle the preferences.
"""

import sys

from PyQt4.QtCore import *
from PyQt4.QtGui import QColor, QFont, QApplication
from PyQt4.Qsci import QsciLexer, QsciScintilla

import QScintilla.Lexers

import Preferences

class PreferencesLexerError(Exception):
    """
    Class defining a special error for the PreferencesLexer class.
    """
    def __init__(self):
        """
        Constructor
        """
        self._errorMessage = \
            QApplication.translate("PreferencesLexerError", 
                "Unspecific PreferencesLexer error.")
        
    def __repr__(self):
        """
        Private method returning a representation of the exception.
        
        @return string representing the error message
        """
        return unicode(self._errorMessage)
        
    def __str__(self):
        """
        Private method returning a string representation of the exception.
        
        @return string representing the error message
        """
        return str(self._errorMessage)

class PreferencesLexerLanguageError(PreferencesLexerError):
    """
    Class defining a special error for the PreferencesLexer class.
    """
    def __init__(self, language):
        """
        Constructor
        """
        PreferencesLexerError.__init__(self)
        self._errorMessage = \
            QApplication.translate("PreferencesLexerError",
                'Unsupported Lexer Language: %1').arg(language)

class PreferencesLexer(QsciLexer):
    """ 
    Subclass of QsciLexer to implement preferences specific lexer methods.
    """
    def __init__(self, language, parent=None):
        """
        Constructor
        
        @param language The lexer language. (string or QString)
        @param parent The parent widget of this lexer. (QextScintilla)
        """
        QsciLexer.__init__(self, parent)
        
        # instantiate a lexer object for the given language
        language = unicode(language)
        lex = QScintilla.Lexers.getLexer(language)
        if lex is None:
            raise PreferencesLexerLanguageError(language)
        
        # define the local store
        self.colours = {}
        self.defaultColours = {}
        self.papers = {}
        self.defaultPapers = {}
        self.eolFills = {}
        self.defaultEolFills = {}
        self.fonts = {}
        self.defaultFonts = {}
        self.descriptions = {}
        self.ind2style = {}
        self.styles = QStringList()
        
        # fill local store with default values from lexer
        # and built up styles list and conversion table from index to style
        self.__language = lex.language()
        
        index = 0
        for i in range(128):
            desc = lex.description(i)
            if not desc.isEmpty():
                self.descriptions[i] = desc
                self.styles.append(desc)
                
                self.colours[i] = lex.defaultColor(i)
                self.papers[i] = lex.defaultPaper(i)
                self.eolFills[i] = lex.defaultEolFill(i)
                self.fonts[i] = lex.defaultFont(i)
                
                self.defaultColours[i] = lex.defaultColor(i)
                self.defaultPapers[i] = lex.defaultPaper(i)
                self.defaultEolFills[i] = lex.defaultEolFill(i)
                self.defaultFonts[i] = lex.defaultFont(i)
                
                self.ind2style[index] = i
                index += 1
        
        self.connect(self, SIGNAL("colorChanged (const QColor&, int)"), 
                     self.setColor)
        self.connect(self, SIGNAL("eolFillChanged (bool, int)"), 
                     self.setEolFill)
        self.connect(self, SIGNAL("fontChanged (const QFont&, int)"), 
                     self.setFont)
        self.connect(self, SIGNAL("paperChanged (const QColor&, int )"), 
                     self.setPaper)
        
        # read the last stored values from preferences file
        self.readSettings(Preferences.Prefs.settings, "Scintilla")
        
    def defaultColor(self, style):
        """
        Public method to get the default colour of a style.
        
        @param style the style number (int)
        @return colour
        """
        return self.defaultColours[style]
        
    def color(self, style):
        """
        Public method to get the colour of a style.
        
        @param style the style number (int)
        @return colour
        """
        return self.colours[style]
        
    def setColor(self, c, style):
        """
        Public method to set the colour for a style.
        
        @param c colour (int)
        @param style the style number (int)
        """
        self.colours[style] = QColor(c)
        
    def defaultPaper(self, style):
        """
        Public method to get the default background for a style.
        
        @param style the style number (int)
        @return colour
        """
        return self.defaultPapers[style]
        
    def paper(self, style):
        """
        Public method to get the background for a style.
        
        @param style the style number (int)
        @return colour
        """
        return self.papers[style]
        
    def setPaper(self, c, style):
        """
        Public method to set the background for a style.
        
        @param c colour (int)
        @param style the style number (int)
        """
        self.papers[style] = QColor(c)
        
    def defaulEolFill(self, style):
        """
        Public method to get the default eolFill flag for a style.
        
        @param style the style number (int)
        @return eolFill flag
        """
        return self.defaultEolFills[style]
        
    def eolFill(self, style):
        """
        Public method to get the eolFill flag for a style.
        
        @param style the style number (int)
        @return eolFill flag
        """
        return self.eolFills[style]
        
    def setEolFill(self, eolfill, style):
        """
        Public method to set the eolFill flag for a style.
        
        @param eolfill eolFill flag (boolean)
        @param style the style number (int)
        """
        self.eolFills[style] = eolfill
        
    def defaultFont(self, style):
        """
        Public method to get the default font for a style.
        
        @param style the style number (int)
        @return font
        """
        return self.defaultFonts[style]
        
    def font(self, style):
        """
        Public method to get the font for a style.
        
        @param style the style number (int)
        @return font
        """
        return self.fonts[style]
        
    def setFont(self, f, style):
        """
        Public method to set the font for a style.
        
        @param f font
        @param style the style number (int)
        """
        self.fonts[style] = QFont(f)
        
    def language(self):
        """
        Public method to get the lexers programming language.
        
        @return language
        """
        return self.__language
        
    def description(self, style):
        """
        Public method to get a descriptive string for a style.
        
        @param style the style number (int)
        @return description of the style (QString)
        """
        if self.descriptions.has_key(style):
            return self.descriptions[style]
        else:
            return QString()
