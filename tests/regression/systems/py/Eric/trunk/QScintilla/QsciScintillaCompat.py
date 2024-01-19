# -*- coding: utf-8 -*-

# Copyright (c) 2004 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a compatability interface class to QsciScintilla.
"""

import sys

from PyQt4.QtCore import Qt, SIGNAL, QString
from PyQt4.QtGui import QApplication, QPalette
from PyQt4.Qsci import QsciScintilla, \
    QSCINTILLA_VERSION as QsciQSCINTILLA_VERSION, QSCINTILLA_VERSION_STR


#####################################################################################

def QSCINTILLA_VERSION():
    """
    Module function to return the QScintilla version.
    
    If the installed QScintilla is a snapshot version, then assume it is
    of the latest release and return a version number of 0x99999.
    
    @return QScintilla version (integer)
    """
    if '-snapshot-' in QSCINTILLA_VERSION_STR:
        return 0x99999
    else:
        return QsciQSCINTILLA_VERSION
    
#####################################################################################

class QsciScintillaCompat(QsciScintilla):
    """
    Class implementing a compatability interface to QsciScintilla.
    
    This class implements all the functions, that were added to
    QsciScintilla incrementally. This class ensures compatibility
    to older versions of QsciScintilla.
    """
    def __init__(self, parent = None):
        """
        Constructor
        
        @param parent parent widget (QWidget)
        @param name name of this instance (string or QString)
        @param flags window flags
        """
        QsciScintilla.__init__(self, parent)
        
        self.zoom = 0
        
        self.__targetSearchFlags = 0
        self.__targetSearchExpr = QString()
        self.__targetSearchStart = 0
        self.__targetSearchEnd = -1
        self.__targetSearchActive = False
    
    def setLexer(self, lex = None):
        """
        Public method to set the lexer.
        
        @param lex the lexer to be set or None to reset it.
        """
        QsciScintilla.setLexer(self, lex)
        if lex is None:
            self.clearStyles()
    
    def clearStyles(self):
        """
        Public method to set the styles according the selected Qt style.
        """
        palette = QApplication.palette()
        self.SendScintilla(QsciScintilla.SCI_STYLESETFORE,
            QsciScintilla.STYLE_DEFAULT, palette.color(QPalette.Text))
        self.SendScintilla(QsciScintilla.SCI_STYLESETBACK,
            QsciScintilla.STYLE_DEFAULT, palette.color(QPalette.Base))
        self.SendScintilla(QsciScintilla.SCI_STYLECLEARALL)
        self.SendScintilla(QsciScintilla.SCI_CLEARDOCUMENTSTYLE)
    
    def monospacedStyles(self, font):
        """
        Public method to set the current style to be monospaced.
        
        @param font font to be used (QFont)
        """
        try:
            rangeLow = range(self.STYLE_DEFAULT)
        except AttributeError:
            rangeLow = range(32)
        try:
            rangeHigh = range(self.STYLE_LASTPREDEFINED + 1,
                              self.STYLE_MAX + 1)
        except AttributeError:
            rangeHigh = range(40, 128)
        
        f = str(font.family())
        ps = font.pointSize()
        for style in rangeLow + rangeHigh:
            self.SendScintilla(QsciScintilla.SCI_STYLESETFONT, style, f)
            self.SendScintilla(QsciScintilla.SCI_STYLESETSIZE, style, ps)
    
    def linesOnScreen(self):
        """
        Public method to get the amount of visible lines.
        
        @return amount of visible lines (integer)
        """
        return self.SendScintilla(QsciScintilla.SCI_LINESONSCREEN)
    
    def lineAt(self, pos):
        """
        Public method to calculate the line at a position.
        
        This variant is able to calculate the line for positions in the
        margins and for empty lines.
        
        @param pos position to calculate the line for (integer or QPoint)
        @return linenumber at position or -1, if there is no line at pos
            (integer, zero based)
        """
        if type(pos) == type(1):
            scipos = pos
        else:
            scipos = \
                self.SendScintilla(QsciScintilla.SCI_POSITIONFROMPOINT, pos.x(), pos.y())
        line = self.SendScintilla(QsciScintilla.SCI_LINEFROMPOSITION, scipos)
        if line >= self.lines():
            line = -1
        return line
    
    def currentPosition(self):
        """
        Public method to get the current position.
        
        @return absolute position of the cursor (integer)
        """
        return self.SendScintilla(QsciScintilla.SCI_GETCURRENTPOS)
    
    def styleAt(self, pos):
        """
        Public method to get the style at a position in the text.
        
        @param pos position in the text (integer)
        @return style at the requested position or 0, if the position
            is negative or past the end of the document (integer)
        """
        return self.SendScintilla(QsciScintilla.SCI_GETSTYLEAT, pos)
    
    def currentStyle(self):
        """
        Public method to get the style at the current position.
        
        @return style at the current position (integer)
        """
        return self.styleAt(self.currentPosition())
    
    def getEndStyled(self):
        """
        Public method to get the last styled position.
        """
        return self.SendScintilla(QsciScintilla.SCI_GETENDSTYLED)
    
    def startStyling(self, pos, mask):
        """
        Public method to prepare styling.
        
        @param pos styling positition to start at (integer)
        @param mask mask of bits to use for styling (integer)
        """
        self.SendScintilla(QsciScintilla.SCI_STARTSTYLING, pos, mask)
    
    def setStyling(self, length, style):
        """
        Public method to style some text.
        
        @param length length of text to style (integer)
        @param style style to set for text (integer)
        """
        self.SendScintilla(QsciScintilla.SCI_SETSTYLING, length, style)
    
    def setStyleBits(self, bits):
        """
        Public method to set the number of bits to be used for styling.
        """
        self.SendScintilla(QsciScintilla.SCI_SETSTYLEBITS, bits)
    
    def charAt(self, pos):
        """
        Public method to get the character at a position in the text observing 
        multibyte characters.
        
        @param pos position in the text (integer)
        @return raw character at the requested position or empty string, if the position
            is negative or past the end of the document (string)
        """
        ch = self.rawCharAt(pos)
        if ch and ord(ch) > 127 and self.isUtf8():
            if (ord(ch[0]) & 0xF0) == 0xF0:
                utf8Len = 4
            elif (ord(ch[0]) & 0xE0) == 0xE0:
                utf8Len = 3
            elif (ord(ch[0]) & 0xC0) == 0xC0:
                utf8Len = 2
            while len(ch) < utf8Len:
                pos += 1
                ch += self.rawCharAt(pos)
            return ch.decode('utf8')
        else:
            return ch
    
    def rawCharAt(self, pos):
        """
        Public method to get the raw character at a position in the text.
        
        @param pos position in the text (integer)
        @return raw character at the requested position or empty string, if the position
            is negative or past the end of the document (string)
        """
        char = self.SendScintilla(QsciScintilla.SCI_GETCHARAT, pos)
        if char == 0:
            return ""
        elif char < 0:
            return chr(char + 256)
        else:
            return chr(char)
    
    def foldLevelAt(self, line):
        """
        Public method to get the fold level of a line of the document.
        
        @param line line number (integer)
        @return fold level of the given line (integer)
        """
        lvl = self.SendScintilla(QsciScintilla.SCI_GETFOLDLEVEL, line)
        return \
            (lvl & QsciScintilla.SC_FOLDLEVELNUMBERMASK) - QsciScintilla.SC_FOLDLEVELBASE
    
    def foldFlagsAt(self, line):
        """
        Public method to get the fold flags of a line of the document.
        
        @param line line number (integer)
        @return fold flags of the given line (integer)
        """
        lvl = self.SendScintilla(QsciScintilla.SCI_GETFOLDLEVEL, line)
        return lvl & ~QsciScintilla.SC_FOLDLEVELNUMBERMASK
    
    def foldHeaderAt(self, line):
        """
        Public method to determine, if a line of the document is a fold header line.
        
        @param line line number (integer)
        @return flag indicating a fold header line (boolean)
        """
        lvl = self.SendScintilla(QsciScintilla.SCI_GETFOLDLEVEL, line)
        return lvl & QsciScintilla.SC_FOLDLEVELHEADERFLAG
    
    def foldExpandedAt(self, line):
        """
        Public method to determine, if a fold is expanded.
        
        @param line line number (integer)
        @return flag indicating the fold expansion state of the line (boolean)
        """
        return self.SendScintilla(QsciScintilla.SCI_GETFOLDEXPANDED, line)
    
    def setIndentationGuideView(self, view):
        """
        Public method to set the view of the indentation guides.
        
        @param view view of the indentation guides (SC_IV_NONE, SC_IV_REAL,
            SC_IV_LOOKFORWARD or SC_IV_LOOKBOTH)
        """
        self.SendScintilla(QsciScintilla.SCI_SETINDENTATIONGUIDES, view)
    
    def indentationGuideView(self):
        """
        Public method to get the indentation guide view.
        
        @return indentation guide view (SC_IV_NONE, SC_IV_REAL,
            SC_IV_LOOKFORWARD or SC_IV_LOOKBOTH)
        """
        return self.SendScintilla(QsciScintilla.SCI_GETINDENTATIONGUIDES)
    
    #####################################################################################
    # methods below are missing from QScintilla
    #####################################################################################

    def zoomIn(self, zoom = 1):
        """
        Public method used to increase the zoom factor.
        
        @param zoom zoom factor increment
        """
        self.zoom += zoom
        QsciScintilla.zoomIn(self, zoom)
    
    def zoomOut(self, zoom = 1):
        """
        Public method used to decrease the zoom factor.
        
        @param zoom zoom factor decrement
        """
        self.zoom -= zoom
        QsciScintilla.zoomOut(self, zoom)
    
    def zoomTo(self, zoom):
        """
        Public method used to zoom to a specific zoom factor.
        
        @param zoom zoom factor
        """
        self.zoom = zoom
        QsciScintilla.zoomTo(self, zoom)
    
    def getZoom(self):
        """
        Public method used to retrieve the current zoom factor.
        
        @return zoom factor (int)
        """
        return self.zoom
    
    def editorCommand(self, cmd):
        """
        Public method to perform a simple editor command.
        
        @param cmd the scintilla command to be performed
        """
        self.SendScintilla(cmd)
    
    def scrollVertical(self, lines):
        """
        Public method to scroll the text area.
        
        @param lines number of lines to scroll (negative scrolls up,
            positive scrolls down) (integer)
        """
        self.SendScintilla(QsciScintilla.SCI_LINESCROLL, 0, lines)
    
    def moveCursorToEOL(self):
        """
        Public method to move the cursor to the end of line.
        """
        self.SendScintilla(QsciScintilla.SCI_LINEEND)
    
    def moveCursorLeft(self):
        """
        Public method to move the cursor left.
        """
        self.SendScintilla(QsciScintilla.SCI_CHARLEFT)
    
    def moveCursorRight(self):
        """
        Public method to move the cursor right.
        """
        self.SendScintilla(QsciScintilla.SCI_CHARRIGHT)
    
    def moveCursorWordLeft(self):
        """
        Public method to move the cursor left one word.
        """
        self.SendScintilla(QsciScintilla.SCI_WORDLEFT)
    
    def moveCursorWordRight(self):
        """
        Public method to move the cursor right one word.
        """
        self.SendScintilla(QsciScintilla.SCI_WORDRIGHT)
    
    def newLineBelow(self):
        """
        Public method to insert a new line below the current one.
        """
        self.SendScintilla(QsciScintilla.SCI_LINEEND)
        self.SendScintilla(QsciScintilla.SCI_NEWLINE)
    
    def deleteBack(self):
        """
        Public method to delete the character to the left of the cursor.
        """
        self.SendScintilla(QsciScintilla.SCI_DELETEBACK)
    
    def delete(self):
        """
        Public method to delete the character to the right of the cursor.
        """
        self.SendScintilla(QsciScintilla.SCI_CLEAR)
    
    def deleteWordLeft(self):
        """
        Public method to delete the word to the left of the cursor.
        """
        self.SendScintilla(QsciScintilla.SCI_DELWORDLEFT)
    
    def deleteWordRight(self):
        """
        Public method to delete the word to the right of the cursor.
        """
        self.SendScintilla(QsciScintilla.SCI_DELWORDRIGHT)
    
    def deleteLineLeft(self):
        """
        Public method to delete the line to the left of the cursor.
        """
        self.SendScintilla(QsciScintilla.SCI_DELLINELEFT)
    
    def deleteLineRight(self):
        """
        Public method to delete the line to the right of the cursor.
        """
        self.SendScintilla(QsciScintilla.SCI_DELLINERIGHT)
    
    def extendSelectionLeft(self):
        """
        Public method to extend the selection one character to the left.
        """
        self.SendScintilla(QsciScintilla.SCI_CHARLEFTEXTEND)
    
    def extendSelectionRight(self):
        """
        Public method to extend the selection one character to the right.
        """
        self.SendScintilla(QsciScintilla.SCI_CHARRIGHTEXTEND)
    
    def extendSelectionWordLeft(self):
        """
        Public method to extend the selection one word to the left.
        """
        self.SendScintilla(QsciScintilla.SCI_WORDLEFTEXTEND)
    
    def extendSelectionWordRight(self):
        """
        Public method to extend the selection one word to the right.
        """
        self.SendScintilla(QsciScintilla.SCI_WORDRIGHTEXTEND)
    
    def extendSelectionToBOL(self):
        """
        Public method to extend the selection to the beginning of the line.
        """
        self.SendScintilla(QsciScintilla.SCI_VCHOMEEXTEND)
    
    def extendSelectionToEOL(self):
        """
        Public method to extend the selection to the end of the line.
        """
        self.SendScintilla(QsciScintilla.SCI_LINEENDEXTEND)
    
    def getLineSeparator(self):
        """
        Public method to get the line separator for the current eol mode.
        
        @return eol string (string)
        """
        m = self.eolMode()
        if m == QsciScintilla.EolWindows:
            eol = '\r\n'
        elif m == QsciScintilla.EolUnix:
            eol = '\n'
        elif m == QsciScintilla.EolMac:
            eol = '\r'
        else:
            eol = ''
        return eol
    
    def getEolIndicator(self):
        """
        Public method to get the eol indicator for the current eol mode.
        
        @return eol indicator (string)
        """
        m = self.eolMode()
        if m == QsciScintilla.EolWindows:
            eol = 'CRLF'
        elif m == QsciScintilla.EolUnix:
            eol = 'LF'
        elif m == QsciScintilla.EolMac:
            eol = 'CR'
        else:
            eol = ''
        return eol
    
    def setEolModeByEolString(self, eolStr):
        """
        Public method to set the eol mode given the eol string.
        
        @param eolStr eol string (string)
        """
        if eolStr == '\r\n':
            self.setEolMode(QsciScintilla.EolMode(QsciScintilla.EolWindows))
        elif eolStr == '\n':
            self.setEolMode(QsciScintilla.EolMode(QsciScintilla.EolUnix))
        elif eolStr == '\r':
            self.setEolMode(QsciScintilla.EolMode(QsciScintilla.EolMac))
    
    def detectEolString(self, txt):
        """
        Public method to determine the eol string used.
        
        @param txt text from which to determine the eol string (string)
        @return eol string (string)
        """
        utxt = unicode(txt)
        if len(utxt.split("\r\n", 1)) == 2:
            return '\r\n'
        elif len(utxt.split("\n", 1)) == 2:
            return '\n'
        elif len(utxt.split("\r", 1)) == 2:
            return '\r'
        else:
            return None
    
    #####################################################################################
    # methods to perform searches in target range
    #####################################################################################
    
    def positionFromPoint(self, point):
        """
        Public method to calculate the scintilla position from a point in the window.
        
        @param point point in the window (QPoint)
        @return scintilla position (integer) or -1 to indicate, that the point is not
            near any character
        """
        return self.SendScintilla(QsciScintilla.SCI_POSITIONFROMPOINTCLOSE, 
                                  point.x(), point.y())
    
    def positionBefore(self, pos):
        """
        Public method to get the position before the given position taking into account
        multibyte characters.
        
        @param pos position (integer)
        @return position before the given one (integer)
        """
        return self.SendScintilla(QsciScintilla.SCI_POSITIONBEFORE, pos)
    
    def positionAfter(self, pos):
        """
        Public method to get the position after the given position taking into account
        multibyte characters.
        
        @param pos position (integer)
        @return position after the given one (integer)
        """
        return self.SendScintilla(QsciScintilla.SCI_POSITIONAFTER, pos)
    
    def positionFromLineIndex(self, line, index):
        """
        Public method to convert line and index to an absolute position.
        
        @param line line number (integer)
        @param index index number (integer)
        @return absolute position in the editor (integer)
        """
        pos = self.SendScintilla(QsciScintilla.SCI_POSITIONFROMLINE, line)
        
        # Allow for multi-byte characters
        for i in range(index):
            pos = self.positionAfter(pos)
        
        return pos
    
    def lineIndexFromPosition(self, pos):
        """
        Public method to convert an absolute position to line and index.
        
        @param pos absolute position in the editor (integer)
        @return tuple of line number (integer) and index number (integer)
        """
        lin = self.SendScintilla(QsciScintilla.SCI_LINEFROMPOSITION, pos)
        linpos = self.SendScintilla(QsciScintilla.SCI_POSITIONFROMLINE, lin)
        indx = 0
        
        # Allow for multi-byte characters.
        while linpos < pos:
            new_linpos = self.positionAfter(linpos)
            
            # If the position hasn't moved then we must be at the end of the text
            # (which implies that the position passed was beyond the end of the
            # text).
            if new_linpos == linpos:
                break
            
            linpos = new_linpos
            indx += 1
        
        return lin, indx
    
    def lineEndPosition(self, line):
        """
        Public method to determine the line end position of the given line.
        
        @param line line number (integer)
        @return position of the line end disregarding line end characters (integer)
        """
        return self.SendScintilla(QsciScintilla.SCI_GETLINEENDPOSITION, line)
    
    def __doSearchTarget(self):
        """
        Private method to perform the search in target.
        
        @return flag indicating a successful search (boolean)
        """
        if self.__targetSearchStart == self.__targetSearchEnd:
            self.__targetSearchActive = False
            return False
        
        self.SendScintilla(QsciScintilla.SCI_SETTARGETSTART, self.__targetSearchStart)
        self.SendScintilla(QsciScintilla.SCI_SETTARGETEND, self.__targetSearchEnd)
        self.SendScintilla(QsciScintilla.SCI_SETSEARCHFLAGS, self.__targetSearchFlags)
        pos = self.SendScintilla(QsciScintilla.SCI_SEARCHINTARGET, 
                                 len(self.__targetSearchExpr), 
                                 self.__targetSearchExpr)
        
        if pos == -1:
            self.__targetSearchActive = False
            return False
        
        targend = self.SendScintilla(QsciScintilla.SCI_GETTARGETEND)
        self.__targetSearchStart = targend
        
        return True
    
    def getFoundTarget(self):
        """
        Public method to get the recently found target.
        
        @return found target as a tuple of starting position and target length
            (integer, integer)
        """
        if self.__targetSearchActive:
            spos = self.SendScintilla(QsciScintilla.SCI_GETTARGETSTART)
            epos = self.SendScintilla(QsciScintilla.SCI_GETTARGETEND)
            return (spos, epos - spos)
        else:
            return (0, 0)
    
    def findFirstTarget(self, expr_, re_, cs_, wo_, 
            begline = -1, begindex = -1, endline = -1, endindex = -1, 
            ws_ = False):
        """
        Public method to search in a specified range of text without
        setting the selection.
        
        @param expr_ search expression (string or QString)
        @param re_ flag indicating a regular expression (boolean)
        @param cs_ flag indicating a case sensitive search (boolean)
        @param wo_ flag indicating a word only search (boolean)
        @keyparam begline line number to start from (-1 to indicate current
            position) (integer)
        @keyparam begindex index to start from (-1 to indicate current
            position) (integer)
        @keyparam endline line number to stop at (-1 to indicate end of
            document) (integer)
        @keyparam endindex index number to stop at (-1 to indicate end of
            document) (integer)
        @keyparam ws_ flag indicating a word start search (boolean) 
        @return flag indicating a successful search (boolean)
        """
        self.__targetSearchFlags = 0
        if re_:
            self.__targetSearchFlags |= QsciScintilla.SCFIND_REGEXP
        if cs_:
            self.__targetSearchFlags |= QsciScintilla.SCFIND_MATCHCASE
        if wo_:
            self.__targetSearchFlags |= QsciScintilla.SCFIND_WHOLEWORD
        if ws_:
            self.__targetSearchFlags |= QsciScintilla.SCFIND_WORDSTART
        
        if begline < 0 or begindex < 0:
            self.__targetSearchStart = self.SendScintilla(QsciScintilla.SCI_GETCURRENTPOS)
        else:
            self.__targetSearchStart = self.positionFromLineIndex(begline, begindex)
        
        if endline < 0 or endindex < 0:
            self.__targetSearchEnd = self.SendScintilla(QsciScintilla.SCI_GETTEXTLENGTH)
        else:
            self.__targetSearchEnd = self.positionFromLineIndex(endline, endindex)
        
        if self.isUtf8():
            self.__targetSearchExpr = unicode(expr_).encode("utf-8")
        else:
            self.__targetSearchExpr = unicode(expr_).encode("latin1")
        
        if self.__targetSearchExpr:
            self.__targetSearchActive = True
            
            return self.__doSearchTarget()
        
        return False
    
    def findNextTarget(self):
        """
        Public method to find the next occurrence in the target range.
        
        @return flag indicating a successful search (boolean)
        """
        if not self.__targetSearchActive:
            return False
        
        return self.__doSearchTarget()
    
    def replaceTarget(self, replaceStr):
        """
        Public method to replace the string found by the last search in target.
        
        @param replaceStr replacement string or regexp (string or QString)
        """
        if not self.__targetSearchActive:
            return
        
        if self.__targetSearchFlags & QsciScintilla.SCFIND_REGEXP:
            cmd = QsciScintilla.SCI_REPLACETARGETRE
        else:
            cmd = QsciScintilla.SCI_REPLACETARGET
        
        start = self.SendScintilla(QsciScintilla.SCI_GETTARGETSTART)
        
        if self.isUtf8():
            r = replaceStr.encode("utf-8")
        else:
            r = replaceStr.encode("latin1")
        
        self.SendScintilla(cmd, len(r), r)
        
        self.__targetSearchStart = start + len(replaceStr)
    
    #####################################################################################
    # indicator handling methods
    #####################################################################################
    
    def indicatorDefine(self, indicator, style, color):
        """
        Public method to define the appearance of an indicator.
        
        @param indicator number of the indicator (integer, 
            QsciScintilla.INDIC_CONTAINER .. QsciScintilla.INDIC_MAX)
        @param style style to be used for the indicator (QsciScintilla.INDIC_PLAIN,
            QsciScintilla.INDIC_SQUIGGLE, QsciScintilla.INDIC_TT,
            QsciScintilla.INDIC_DIAGONAL, QsciScintilla.INDIC_STRIKE,
            QsciScintilla.INDIC_HIDDEN, QsciScintilla.INDIC_BOX,
            QsciScintilla.INDIC_ROUNDBOX)
        @param color color to be used by the indicator (QColor)
        @exception ValueError the indicator or style are not valid
        """
        if indicator < QsciScintilla.INDIC_CONTAINER or \
           indicator > QsciScintilla.INDIC_MAX:
            raise ValueError("indicator number out of range")
        
        if style < QsciScintilla.INDIC_PLAIN or style > QsciScintilla.INDIC_ROUNDBOX:
            raise ValueError("style out of range")
        
        self.SendScintilla(QsciScintilla.SCI_INDICSETSTYLE, indicator, style)
        self.SendScintilla(QsciScintilla.SCI_INDICSETFORE, indicator, color)
    
    def setCurrentIndicator(self, indicator):
        """
        Public method to set the current indicator.
        
        @param indicator number of the indicator (integer, 
            QsciScintilla.INDIC_CONTAINER .. QsciScintilla.INDIC_MAX)
        @exception ValueError the indicator or style are not valid
        """
        if indicator < QsciScintilla.INDIC_CONTAINER or \
           indicator > QsciScintilla.INDIC_MAX:
            raise ValueError("indicator number out of range")
        
        self.SendScintilla(QsciScintilla.SCI_SETINDICATORCURRENT, indicator)
    
    def setIndicatorRange(self, indicator, spos, length):
        """
        Public method to set an indicator for the given range.
        
        @param indicator number of the indicator (integer, 
            QsciScintilla.INDIC_CONTAINER .. QsciScintilla.INDIC_MAX)
        @param spos position of the indicator start (integer)
        @param length length of the indicator (integer)
        @exception ValueError the indicator or style are not valid
        """
        self.setCurrentIndicator(indicator)
        self.SendScintilla(QsciScintilla.SCI_INDICATORFILLRANGE, spos, length)
    
    def setIndicator(self, indicator, sline, sindex, eline, eindex):
        """
        Public method to set an indicator for the given range.
        
        @param indicator number of the indicator (integer, 
            QsciScintilla.INDIC_CONTAINER .. QsciScintilla.INDIC_MAX)
        @param sline line number of the indicator start (integer)
        @param sindex index of the indicator start (integer)
        @param eline line number of the indicator end (integer)
        @param eindex index of the indicator end (integer)
        @exception ValueError the indicator or style are not valid
        """
        spos = self.positionFromLineIndex(sline, sindex)
        epos = self.positionFromLineIndex(eline, eindex)
        self.setIndicatorRange(indicator, spos, epos - spos)
    
    def clearIndicatorRange(self, indicator, spos, length):
        """
        Public method to clear an indicator for the given range.
        
        @param indicator number of the indicator (integer, 
            QsciScintilla.INDIC_CONTAINER .. QsciScintilla.INDIC_MAX)
        @param spos position of the indicator start (integer)
        @param length length of the indicator (integer)
        """
        self.setCurrentIndicator(indicator)
        self.SendScintilla(QsciScintilla.SCI_INDICATORCLEARRANGE, spos, length)
    
    def clearIndicator(self, indicator, sline, sindex, eline, eindex):
        """
        Public method to clear an indicator for the given range.
        
        @param indicator number of the indicator (integer, 
            QsciScintilla.INDIC_CONTAINER .. QsciScintilla.INDIC_MAX)
        @param sline line number of the indicator start (integer)
        @param sindex index of the indicator start (integer)
        @param eline line number of the indicator end (integer)
        @param eindex index of the indicator end (integer)
        """
        spos = self.positionFromLineIndex(sline, sindex)
        epos = self.positionFromLineIndex(eline, eindex)
        self.clearIndicatorRange(indicator, spos, epos - spos)
    
    def clearAllIndicators(self, indicator):
        """
        Public method to clear all occurrences of an indicator.
        
        @param indicator number of the indicator (integer, 
            QsciScintilla.INDIC_CONTAINER .. QsciScintilla.INDIC_MAX)
        """
        self.clearIndicatorRange(indicator, 0, self.length())
    
    def hasIndicator(self, indicator, pos):
        """
        Public method to test for the existence of an indicator.
        
        @param indicator number of the indicator (integer, 
            QsciScintilla.INDIC_CONTAINER .. QsciScintilla.INDIC_MAX)
        @param pos position to test (integer)
        @return flag indicating the existence of the indicator (boolean)
        """
        res = self.SendScintilla(QsciScintilla.SCI_INDICATORVALUEAT, indicator, pos)
        return res
    
    #####################################################################################
    # interface methods to the standard keyboard command set
    #####################################################################################
    
    def clearKeys(self):
        """
        Protected method to clear the key commands.
        """
        # call into the QsciCommandSet
        self.standardCommands().clearKeys()
        
    def clearAlternateKeys(self):
        """
        Protected method to clear the alternate key commands.
        """
        # call into the QsciCommandSet
        self.standardCommands().clearAlternateKeys()
    
    #####################################################################################
    # interface methods to the mini editor
    #####################################################################################

    def getFileName(self):
        """
        Public method to return the name of the file being displayed.
        
        @return filename of the displayed file (QString)
        """
        p = self.parent()
        if p is None:
            return QString()
        else:
            try:
                return p.getFileName()
            except AttributeError:
                return QString()
    
##    #####################################################################################
##    # methods below have been added to QScintilla starting with version after 2.x
##    #####################################################################################
##    
##    if "newMethod" not in QsciScintilla.__dict__:
##        def newMethod(self, param):
##            """
##            Public method to do something.
##            
##            @param param parameter for method
##            """
##            pass
##
