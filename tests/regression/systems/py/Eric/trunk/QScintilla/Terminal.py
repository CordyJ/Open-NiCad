# -*- coding: utf-8 -*-

# Copyright (c) 2008 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a simple terminal based on QScintilla.
"""

import sys
import os
import re

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.Qsci import QsciScintilla

from KdeQt import KQInputDialog
from KdeQt.KQApplication import e4App

import Lexers
from QsciScintillaCompat import QsciScintillaCompat, QSCINTILLA_VERSION

import Preferences
import Utilities

import UI.PixmapCache
from Utilities import toUnicode

from ShellHistoryDialog import ShellHistoryDialog

class Terminal(QsciScintillaCompat):
    """
    Class implementing a simple terminal based on QScintilla.
    
    A user can enter commands that are executed by a shell process.  
    """
    def __init__(self, vm, parent = None):
        """
        Constructor
        
        @param vm reference to the viewmanager object
        @param parent parent widget (QWidget)
        """
        QsciScintillaCompat.__init__(self, parent)
        self.setUtf8(True)
        
        self.vm = vm
        
        self.linesepRegExp = QRegExp(r"\r\n|\n|\r")
        
        self.setWindowTitle(self.trUtf8('Terminal'))
        
        self.setWhatsThis(self.trUtf8(
            """<b>The Terminal Window</b>"""
            """<p>This is a very simple terminal like window, that runs a shell"""
            """ process in the background.</p>"""
            """<p>The process can be stopped and started via the context menu. Some"""
            """ Ctrl command may be sent as well. However, the shell may ignore"""
            """ them.</p>"""
            """<p>You can use the cursor keys while entering commands. There is also a"""
            """ history of commands that can be recalled using the up and down cursor"""
            """ keys. Pressing the up or down key after some text has been entered will"""
            """ start an incremental search.</p>"""
        ))
        
        self.ansi_re = re.compile("\033\[\??[\d;]*\w")
        
        # Initialise instance variables.
        self.prline = 0
        self.prcol = 0
        self.inDragDrop = False
        self.lexer_ = None
        
        # Initialize history
        self.maxHistoryEntries = Preferences.getTerminal("MaxHistoryEntries")
        self.history = QStringList()
        self.histidx = -1
        
        # clear QScintilla defined keyboard commands
        # we do our own handling through the view manager
        self.clearAlternateKeys()
        self.clearKeys()
        self.__actionsAdded = False
        
        # Create the history context menu
        self.hmenu = QMenu(self.trUtf8('History'))
        self.hmenu.addAction(self.trUtf8('Select entry'), self.__selectHistory)
        self.hmenu.addAction(self.trUtf8('Show'), self.__showHistory)
        self.hmenu.addAction(self.trUtf8('Clear'), self.__clearHistory)
        
        # Create a little context menu to send Ctrl-C, Ctrl-D or Ctrl-Z
        self.csm = QSignalMapper(self)
        self.connect(self.csm, SIGNAL('mapped(int)'), self.__sendCtrl)
        
        self.cmenu = QMenu(self.trUtf8('Ctrl Commands'))
        act = self.cmenu.addAction(self.trUtf8('Ctrl-C'))
        self.csm.setMapping(act, 3)
        self.connect(act, SIGNAL('triggered()'), self.csm, SLOT('map()'))
        act = self.cmenu.addAction(self.trUtf8('Ctrl-D'))
        self.csm.setMapping(act, 4)
        self.connect(act, SIGNAL('triggered()'), self.csm, SLOT('map()'))
        act = self.cmenu.addAction(self.trUtf8('Ctrl-Z'))
        self.csm.setMapping(act, 26)
        self.connect(act, SIGNAL('triggered()'), self.csm, SLOT('map()'))
        
        # Create a little context menu
        self.menu = QMenu(self)
        self.menu.addAction(self.trUtf8('Cut'), self.cut)
        self.menu.addAction(self.trUtf8('Copy'), self.copy)
        self.menu.addAction(self.trUtf8('Paste'), self.paste)
        self.menu.addMenu(self.hmenu)
        self.menu.addSeparator()
        self.menu.addAction(self.trUtf8('Clear'), self.clear)
        self.__startAct = self.menu.addAction(self.trUtf8("Start"), self.__startShell)
        self.__stopAct = self.menu.addAction(self.trUtf8("Stop"), self.__stopShell)
        self.__resetAct = self.menu.addAction(self.trUtf8('Reset'), self.__reset)
        self.menu.addSeparator()
        self.__ctrlAct = self.menu.addMenu(self.cmenu)
        self.menu.addSeparator()
        self.menu.addAction(self.trUtf8("Configure..."), self.__configure)
        
        self.__bindLexer()
        self.__setTextDisplay()
        self.__setMargin0()
        
        self.setWindowIcon(UI.PixmapCache.getIcon("eric.png"))
        
        self.incrementalSearchString = ""
        self.incrementalSearchActive = False
        
        self.supportedEditorCommands = {
            QsciScintilla.SCI_LINEDELETE   : self.__clearCurrentLine,
            QsciScintilla.SCI_NEWLINE      : self.__QScintillaNewline,
            
            QsciScintilla.SCI_DELETEBACK   : self.__QScintillaDeleteBack,
            QsciScintilla.SCI_CLEAR        : self.__QScintillaDelete,
            QsciScintilla.SCI_DELWORDLEFT  : self.__QScintillaDeleteWordLeft,
            QsciScintilla.SCI_DELWORDRIGHT : self.__QScintillaDeleteWordRight,
            QsciScintilla.SCI_DELLINELEFT  : self.__QScintillaDeleteLineLeft,
            QsciScintilla.SCI_DELLINERIGHT : self.__QScintillaDeleteLineRight,
            
            QsciScintilla.SCI_CHARLEFT     : self.__QScintillaCharLeft,
            QsciScintilla.SCI_CHARRIGHT    : self.__QScintillaCharRight,
            QsciScintilla.SCI_WORDLEFT     : self.__QScintillaWordLeft,
            QsciScintilla.SCI_WORDRIGHT    : self.__QScintillaWordRight,
            QsciScintilla.SCI_VCHOME       : self.__QScintillaVCHome,
            QsciScintilla.SCI_LINEEND      : self.__QScintillaLineEnd,
            QsciScintilla.SCI_LINEUP       : self.__QScintillaLineUp,
            QsciScintilla.SCI_LINEDOWN     : self.__QScintillaLineDown,
            
            QsciScintilla.SCI_CHARLEFTEXTEND  : self.__QScintillaCharLeftExtend,
            QsciScintilla.SCI_CHARRIGHTEXTEND : self.extendSelectionRight,
            QsciScintilla.SCI_WORDLEFTEXTEND  : self.__QScintillaWordLeftExtend,
            QsciScintilla.SCI_WORDRIGHTEXTEND : self.extendSelectionWordRight,
            QsciScintilla.SCI_VCHOMEEXTEND    : self.__QScintillaVCHomeExtend,
            QsciScintilla.SCI_LINEENDEXTEND   : self.extendSelectionToEOL,
        }
        
        self.__ioEncoding = str(Preferences.getSystem("IOEncoding"))
        
        self.__process = QProcess()
        self.__process.setProcessChannelMode(QProcess.MergedChannels)
        self.__process.setReadChannel(QProcess.StandardOutput)
        
        self.connect(self.__process, SIGNAL("readyReadStandardOutput()"), 
                     self.__readOutput)
        self.connect(self.__process, SIGNAL("started()"), self.__started)
        self.connect(self.__process, SIGNAL("finished(int)"), self.__finished)
        
        self.__ctrl = {}
        for ascii_number, letter in enumerate("abcdefghijklmnopqrstuvwxyz"):
            self.__ctrl[letter] = chr(ascii_number + 1)
        
        self.__lastPos = (0, 0)
        
        self.__startShell()
        
    def __readOutput(self):
        """
        Private method to process the output of the shell.
        """
        output = unicode(self.__process.readAllStandardOutput(), 
                         self.__ioEncoding, 'replace')
        self.__write(self.ansi_re.sub("", output))
        self.__lastPos = self.__getEndPos()
        
    def __started(self):
        """
        Private method called, when the shell process has started.
        """
        if not Utilities.isWindowsPlatform():
            QTimer.singleShot(250, self.clear)
        
        self.__startAct.setEnabled(False)
        self.__stopAct.setEnabled(True)
        self.__resetAct.setEnabled(True)
        self.__ctrlAct.setEnabled(True)
        
    def __finished(self):
        """
        Private method called, when the shell process has finished.
        """
        QsciScintilla.clear(self)
        
        self.__startAct.setEnabled(True)
        self.__stopAct.setEnabled(False)
        self.__resetAct.setEnabled(False)
        self.__ctrlAct.setEnabled(False)
        
    def __send(self, data):
        """
        Private method to send data to the shell process.
        
        @param data data to be sent to the shell process (string or QString)
        """
        pdata = QByteArray()
        pdata.append(data)
        self.__process.write(pdata)
        
    def __sendCtrl(self, cmd):
        """
        Private slot to send a control command to the shell process.
        
        @param the control command to be sent (integer)
        """
        self.__send(chr(cmd))
        
    def closeTerminal(self):
        """
        Public method to shutdown the terminal. 
        """
        self.__stopShell()
        self.saveHistory()
        
    def __bindLexer(self):
        """
        Private slot to set the lexer.
        """
        if Utilities.isWindowsPlatform():
            self.language = "Batch"
        else:
            self.language = "Bash"
        if Preferences.getTerminal("SyntaxHighlightingEnabled"):
            self.lexer_ = Lexers.getLexer(self.language, self)
        else:
            self.lexer_ = None
        
        if self.lexer_ is None:
            self.setLexer(None)
            font = Preferences.getTerminal("MonospacedFont")
            self.monospacedStyles(font)
            return
        
        # get the font for style 0 and set it as the default font
        key = 'Scintilla/%s/style0/font' % unicode(self.lexer_.language())
        fontVariant = Preferences.Prefs.settings.value(key)
        if fontVariant.isValid():
            fdesc = fontVariant.toStringList()
            font = QFont(fdesc[0], int(str(fdesc[1])))
            self.lexer_.setDefaultFont(font)
        self.setLexer(self.lexer_)
        self.lexer_.readSettings(Preferences.Prefs.settings, "Scintilla")
        
    def __setMargin0(self):
        """
        Private method to configure margin 0.
        """
        # set the settings for all margins
        self.setMarginsFont(Preferences.getTerminal("MarginsFont"))
        self.setMarginsForegroundColor(Preferences.getEditorColour("MarginsForeground"))
        self.setMarginsBackgroundColor(Preferences.getEditorColour("MarginsBackground"))
        
        # set margin 0 settings
        linenoMargin = Preferences.getTerminal("LinenoMargin")
        self.setMarginLineNumbers(0, linenoMargin)
        if linenoMargin:
            self.setMarginWidth(0, ' ' + '8' * Preferences.getTerminal("LinenoWidth"))
        else:
            self.setMarginWidth(0, 0)
        
        # disable margins 1 and 2
        self.setMarginWidth(1, 0)
        self.setMarginWidth(2, 0)
        
    def __setTextDisplay(self):
        """
        Private method to configure the text display.
        """
        self.setTabWidth(Preferences.getEditor("TabWidth"))
        if Preferences.getEditor("ShowWhitespace"):
            self.setWhitespaceVisibility(QsciScintilla.WsVisible)
        else:
            self.setWhitespaceVisibility(QsciScintilla.WsInvisible)
        self.setEolVisibility(Preferences.getEditor("ShowEOL"))
        if Preferences.getEditor("BraceHighlighting"):
            self.setBraceMatching(QsciScintilla.SloppyBraceMatch)
        else:
            self.setBraceMatching(QsciScintilla.NoBraceMatch)
        self.setMatchedBraceForegroundColor(
            Preferences.getEditorColour("MatchingBrace"))
        self.setMatchedBraceBackgroundColor(
            Preferences.getEditorColour("MatchingBraceBack"))
        self.setUnmatchedBraceForegroundColor(
            Preferences.getEditorColour("NonmatchingBrace"))
        self.setUnmatchedBraceBackgroundColor(
            Preferences.getEditorColour("NonmatchingBraceBack"))
        if Preferences.getEditor("CustomSelectionColours"):
            self.setSelectionBackgroundColor(\
                Preferences.getEditorColour("SelectionBackground"))
        else:
            self.setSelectionBackgroundColor(\
                QApplication.palette().color(QPalette.Highlight))
        if Preferences.getEditor("ColourizeSelText"):
            self.resetSelectionForegroundColor()
        elif Preferences.getEditor("CustomSelectionColours"):
            self.setSelectionForegroundColor(\
                Preferences.getEditorColour("SelectionForeground"))
        else:
            self.setSelectionForegroundColor(\
                QApplication.palette().color(QPalette.HighlightedText))
        self.setSelectionToEol(Preferences.getEditor("ExtendSelectionToEol"))
        self.setCaretForegroundColor(
            Preferences.getEditorColour("CaretForeground"))
        self.setCaretLineBackgroundColor(
            Preferences.getEditorColour("CaretLineBackground"))
        self.setCaretLineVisible(Preferences.getEditor("CaretLineVisible"))
        self.caretWidth = Preferences.getEditor("CaretWidth")
        self.setCaretWidth(self.caretWidth)
        self.setWrapMode(QsciScintilla.WrapNone)
        self.useMonospaced = Preferences.getTerminal("UseMonospacedFont")
        self.__setMonospaced(self.useMonospaced)
        
    def __setMonospaced(self, on):
        """
        Private method to set/reset a monospaced font.
        
        @param on flag to indicate usage of a monospace font (boolean)
        """
        if on:
            f = Preferences.getTerminal("MonospacedFont")
            self.monospacedStyles(f)
        else:
            if not self.lexer_:
                self.clearStyles()
                self.__setMargin0()
            self.setFont(Preferences.getTerminal("MonospacedFont"))
        
        self.useMonospaced = on
        
    def loadHistory(self):
        """
        Public method to load the history.
        """
        hVariant = Preferences.Prefs.settings.value("Terminal/History")
        if hVariant.isValid():
            hl = hVariant.toStringList()
            self.history = hl[-self.maxHistoryEntries:]
        else:
            self.history = QStringList()
        
    def reloadHistory(self):
        """
        Public method to reload the history.
        """
        self.loadHistory(self.clientType)
        self.history = self.historyLists[self.clientType]
        self.histidx = -1
        
    def saveHistory(self):
        """
        Public method to save the history.
        """
        Preferences.Prefs.settings.setValue(\
            "Terminal/History", QVariant(self.history))
        
    def getHistory(self):
        """
        Public method to get the history.
        
        @return reference to the history list (QStringList)
        """
        return self.history
        
    def __clearHistory(self):
        """
        Private slot to clear the current history.
        """
        self.history.clear()
        
    def __selectHistory(self):
        """
        Private slot to select a history entry to execute.
        """
        cmd, ok = KQInputDialog.getItem(\
            self,
            self.trUtf8("Select History"),
            self.trUtf8("Select the history entry to execute (most recent shown last)."),
            self.history,
            0, False)
        if ok:
            self.__insertHistory(cmd)
        
    def __showHistory(self):
        """
        Private slot to show the shell history dialog.
        """
        dlg = ShellHistoryDialog(self.history, self.vm, self)
        if dlg.exec_() == QDialog.Accepted:
            self.history = dlg.getHistory()
            self.histidx = -1
        
    def __getEndPos(self):
        """
        Private method to return the line and column of the last character.
        
        @return tuple of two values (int, int) giving the line and column
        """
        line = self.lines() - 1
        return (line, self.lineLength(line))
        
    def __write(self, s):
        """
        Private method to display some text.
        
        @param s text to be displayed (string or QString)
        """
        line, col = self.__getEndPos()
        self.setCursorPosition(line, col)
        self.insert(toUnicode(s))
        self.prline, self.prcol = self.getCursorPosition()
        self.ensureCursorVisible()
        self.ensureLineVisible(self.prline)
        
    def __clearCurrentLine(self):
        """
        Private method to clear the line containing the cursor.
        """
        line, col = self.getCursorPosition()
        if self.text(line).startsWith(sys.ps1):
            col = len(sys.ps1)
        elif self.text(line).startsWith(sys.ps2):
            col = len(sys.ps2)
        else:
            col = 0
        self.setCursorPosition(line, col)
        self.deleteLineRight()
        
    def __insertText(self, s):
        """
        Private method to insert some text at the current cursor position.
        
        @param s text to be inserted (string or QString)
        """
        line, col = self.getCursorPosition()
        self.insertAt(s, line, col)
        self.setCursorPosition(line, col + len(unicode(s)))
        
    def __insertTextAtEnd(self, s):
        """
        Private method to insert some text at the end of the command line.
        
        @param s text to be inserted (string or QString)
        """
        line, col = self.__getEndPos()
        self.setCursorPosition(line, col)
        self.insert(s)
        self.prline, self.prcol = self.getCursorPosition()
        
    def mousePressEvent(self, event):
        """
        Protected method to handle the mouse press event.
        
        @param event the mouse press event (QMouseEvent)
        """
        self.setFocus()
        QsciScintillaCompat.mousePressEvent(self, event)
        
    def editorCommand(self, cmd):
        """
        Public method to perform an editor command.
        
        @param cmd the scintilla command to be performed
        """
        try:
            self.supportedEditorCommands[cmd]()
        except TypeError:
            self.supportedEditorCommands[cmd](cmd)
        except KeyError:
            pass
        
    def __isCursorOnLastLine(self):
        """
        Private method to check, if the cursor is on the last line.
        """
        cline, ccol = self.getCursorPosition()
        return cline == self.lines() - 1
        
    def keyPressEvent(self, ev):
        """
        Re-implemented to handle the user input a key at a time.
        
        @param ev key event (QKeyEvent)
        """
        txt = ev.text()
        key = ev.key()
        
        # See it is text to insert.
        if txt.length() and txt >= " ":
            if not self.__isCursorOnLastLine():
                line, col = self.__getEndPos()
                self.setCursorPosition(line, col)
                self.prline, self.prcol = self.getCursorPosition()
            QsciScintillaCompat.keyPressEvent(self, ev)
            self.incrementalSearchActive = True
        else:
            ev.ignore()
        
    def __QScintillaLeftDeleteCommand(self, method):
        """
        Private method to handle a QScintilla delete command working to the left.
        
        @param method shell method to execute
        """
        if self.__isCursorOnLastLine():
            line, col = self.getCursorPosition()
            oldLength = self.text(line).length()
            
            if col > self.__lastPos[1]:
                method()
        
    def __QScintillaDeleteBack(self):
        """
        Private method to handle the Backspace key.
        """
        self.__QScintillaLeftDeleteCommand(self.deleteBack)
        
    def __QScintillaDeleteWordLeft(self):
        """
        Private method to handle the Delete Word Left command.
        """
        self.__QScintillaLeftDeleteCommand(self.deleteWordLeft)
        
    def __QScintillaDelete(self):
        """
        Private method to handle the delete command.
        """
        if self.__isCursorOnLastLine():
            if self.hasSelectedText():
                lineFrom, indexFrom, lineTo, indexTo = self.getSelection()
                if indexFrom >= self.__lastPos[1]:
                    self.delete()
                self.setSelection(lineTo, indexTo, lineTo, indexTo)
            else:
                self.delete()
        
    def __QScintillaDeleteLineLeft(self):
        """
        Private method to handle the Delete Line Left command.
        """
        if self.__isCursorOnLastLine():
            if self.isListActive():
                self.cancelList()
            
            line, col = self.getCursorPosition()
            prompt = self.text(line)[:self.__lastPos[1]]
            self.deleteLineLeft()
            self.insertAt(prompt, line, 0)
            self.setCursorPosition(line, len(prompt))
        
    def __QScintillaNewline(self, cmd):
        """
        Private method to handle the Return key.
        
        @param cmd QScintilla command
        """
        if self.__isCursorOnLastLine():
            self.incrementalSearchString = ""
            self.incrementalSearchActive = False
            line, col = self.__getEndPos()
            self.setCursorPosition(line, col)
            self.setSelection(*(self.__lastPos + self.getCursorPosition()))
            buf = unicode(self.selectedText())
            self.setCursorPosition(line, col)   # select nothin
            self.insert('\n')
            self.__executeCommand(buf)
        
    def __QScintillaLeftCommand(self, method, allLinesAllowed = False):
        """
        Private method to handle a QScintilla command working to the left.
        
        @param method shell method to execute
        """
        if self.__isCursorOnLastLine() or allLinesAllowed:
            line, col = self.getCursorPosition()
            if col > self.__lastPos[1]:
                method()
        
    def __QScintillaCharLeft(self):
        """
        Private method to handle the Cursor Left command.
        """
        self.__QScintillaLeftCommand(self.moveCursorLeft)
        
    def __QScintillaWordLeft(self):
        """
        Private method to handle the Cursor Word Left command.
        """
        self.__QScintillaLeftCommand(self.moveCursorWordLeft)
        
    def __QScintillaRightCommand(self, method):
        """
        Private method to handle a QScintilla command working to the right.
        
        @param method shell method to execute
        """
        if self.__isCursorOnLastLine():
            method()
        
    def __QScintillaCharRight(self):
        """
        Private method to handle the Cursor Right command.
        """
        self.__QScintillaRightCommand(self.moveCursorRight)
        
    def __QScintillaWordRight(self):
        """
        Private method to handle the Cursor Word Right command.
        """
        self.__QScintillaRightCommand(self.moveCursorWordRight)
        
    def __QScintillaDeleteWordRight(self):
        """
        Private method to handle the Delete Word Right command.
        """
        self.__QScintillaRightCommand(self.deleteWordRight)
        
    def __QScintillaDeleteLineRight(self):
        """
        Private method to handle the Delete Line Right command.
        """
        self.__QScintillaRightCommand(self.deleteLineRight)
        
    def __QScintillaVCHome(self, cmd):
        """
        Private method to handle the Home key.
        
        @param cmd QScintilla command
        """
        self.setCursorPosition(*self.__lastPos)
        
    def __QScintillaLineEnd(self, cmd):
        """
        Private method to handle the End key.
        
        @param cmd QScintilla command
        """
        self.moveCursorToEOL()
        
    def __QScintillaLineUp(self, cmd):
        """
        Private method to handle the Up key.
        
        @param cmd QScintilla command
        """
        line, col = self.__getEndPos()
        buf = unicode(self.text(line))[self.__lastPos[1]:]
        if buf and self.incrementalSearchActive:
            if self.incrementalSearchString:
                idx = self.__rsearchHistory(self.incrementalSearchString, 
                                            self.histidx)
                if idx >= 0:
                    self.histidx = idx
                    self.__useHistory()
            else:
                idx = self.__rsearchHistory(buf)
                if idx >= 0:
                    self.histidx = idx
                    self.incrementalSearchString = buf
                    self.__useHistory()
        else:
            if self.histidx < 0:
                self.histidx = len(self.history)
            if self.histidx > 0:
                self.histidx = self.histidx - 1
                self.__useHistory()
        
    def __QScintillaLineDown(self, cmd):
        """
        Private method to handle the Down key.
        
        @param cmd QScintilla command
        """
        line, col = self.__getEndPos()
        buf = unicode(self.text(line))[self.__lastPos[1]:]
        if buf and self.incrementalSearchActive:
            if self.incrementalSearchString:
                idx = self.__searchHistory(self.incrementalSearchString, self.histidx)
                if idx >= 0:
                    self.histidx = idx
                    self.__useHistory()
            else:
                idx = self.__searchHistory(buf)
                if idx >= 0:
                    self.histidx = idx
                    self.incrementalSearchString = buf
                    self.__useHistory()
        else:
            if self.histidx >= 0 and self.histidx < len(self.history):
                self.histidx += 1
                self.__useHistory()
        
    def __QScintillaCharLeftExtend(self):
        """
        Private method to handle the Extend Selection Left command.
        """
        self.__QScintillaLeftCommand(self.extendSelectionLeft, True)
        
    def __QScintillaWordLeftExtend(self):
        """
        Private method to handle the Extend Selection Left one word command.
        """
        self.__QScintillaLeftCommand(self.extendSelectionWordLeft, True)
        
    def __QScintillaVCHomeExtend(self):
        """
        Private method to handle the Extend Selection to start of line command.
        """
        col = self.__lastPos[1]
        self.extendSelectionToBOL()
        while col > 0:
            self.extendSelectionRight()
            col -= 1
        
    def __executeCommand(self, cmd):
        """
        Private slot to execute a command.
        
        @param cmd command to be executed by debug client (string)
        """
        if not cmd:
            cmd = ''
        if len(self.history) == 0 or self.history[-1] != cmd:
            if len(self.history) == self.maxHistoryEntries:
                del self.history[0]
            self.history.append(QString(cmd))
        self.histidx = -1
        
        if cmd in ["clear", "cls", "CLS"]:
            self.clear()
            return
        else:
            if not cmd.endswith("\n"):
                cmd = "%s\n" % cmd
            self.__send(cmd)
        
    def __useHistory(self):
        """
        Private method to display a command from the history.
        """
        if self.histidx < len(self.history):
            cmd = self.history[self.histidx]
        else:
            cmd = QString()
            self.incrementalSearchString = ""
            self.incrementalSearchActive = False
        
        self.__insertHistory(cmd)

    def __insertHistory(self, cmd):
        """
        Private method to insert a command selected from the history.
        
        @param cmd history entry to be inserted (string or QString)
        """
        self.setCursorPosition(self.prline, self.prcol)
        self.setSelection(self.prline, self.prcol,\
                          self.prline, self.lineLength(self.prline))
        self.removeSelectedText()
        self.__insertText(cmd)
        
    def __searchHistory(self, txt, startIdx = -1):
        """
        Private method used to search the history.
        
        @param txt text to match at the beginning (string or QString)
        @param startIdx index to start search from (integer)
        @return index of 
        """
        if startIdx == -1:
            idx = 0
        else:
            idx = startIdx + 1
        while idx < len(self.history) and \
              not self.history[idx].startsWith(txt):
            idx += 1
        return idx
        
    def __rsearchHistory(self, txt, startIdx = -1):
        """
        Private method used to reverse search the history.
        
        @param txt text to match at the beginning (string or QString)
        @param startIdx index to start search from (integer)
        @return index of 
        """
        if startIdx == -1:
            idx = len(self.history) - 1
        else:
            idx = startIdx - 1
        while idx >= 0 and \
              not self.history[idx].startsWith(txt):
            idx -= 1
        return idx
        
    def contextMenuEvent(self,ev):
        """
        Reimplemented to show our own context menu.
        
        @param ev context menu event (QContextMenuEvent)
        """
        self.menu.popup(ev.globalPos())
        ev.accept()
        
    def clear(self):
        """
        Public slot to clear the display.
        """
        QsciScintillaCompat.clear(self)
        self.__send("\n")
        
    def __reset(self):
        """
        Private slot to handle the 'reset' context menu entry.
        """
        self.__stopShell()
        self.__startShell()
        
    def __startShell(self):
        """
        Private slot to start the shell process.
        """
        args = QStringList()
        if Utilities.isWindowsPlatform():
            args.append("/Q")
            self.__process.start("cmd.exe", args)
        else:
            shell = Preferences.getTerminal("Shell")
            if shell.isEmpty():
                shell = os.environ.get('SHELL')
                if shell is None:
                    self.__insertText(self.trUtf8("No shell has been configured."))
                    return
            if Preferences.getTerminal("ShellInteractive"):
                args.append("-i")
            self.__process.start(shell,  args)
        
    def __stopShell(self):
        """
        Private slot to stop the shell process.
        """
        self.__process.kill()
        res = self.__process.waitForFinished(3000)
        
    def handlePreferencesChanged(self):
        """
        Public slot to handle the preferencesChanged signal.
        """
        # rebind the lexer
        self.__bindLexer()
        self.recolor()
        
        # set margin 0 configuration
        self.__setTextDisplay()
        self.__setMargin0()
        
        # do the history related stuff
        self.maxHistoryEntries = Preferences.getTerminal("MaxHistoryEntries")
        self.history = self.history[-self.maxHistoryEntries:]
        
        # do the I/O encoding
        self.__ioEncoding = str(Preferences.getSystem("IOEncoding"))
    
    def focusInEvent(self, event):
        """
        Public method called when the shell receives focus.
        
        @param event the event object (QFocusEvent)
        """
        if not self.__actionsAdded:
            self.addActions(self.vm.editorActGrp.actions())
            self.addActions(self.vm.copyActGrp.actions())
            self.addActions(self.vm.viewActGrp.actions())
        
        try:
            self.vm.editActGrp.setEnabled(False)
            self.vm.editorActGrp.setEnabled(True)
            self.vm.copyActGrp.setEnabled(True)
            self.vm.viewActGrp.setEnabled(True)
        except AttributeError:
            pass
        self.setCaretWidth(self.caretWidth)
        QsciScintillaCompat.focusInEvent(self, event)
        
    def focusOutEvent(self, event):
        """
        Public method called when the shell loses focus.
        
        @param event the event object (QFocusEvent)
        """
        try:
            self.vm.editorActGrp.setEnabled(False)
        except AttributeError:
            pass
        self.setCaretWidth(0)
        QsciScintillaCompat.focusOutEvent(self, event)
        
    def insert(self, text):
        """
        Public slot to insert text at the current cursor position.
        
        The cursor is advanced to the end of the inserted text.
        
        @param text text to be inserted (string or QString)
        """
        txt = QString(text)
        l = txt.length()
        line, col = self.getCursorPosition()
        self.insertAt(txt, line, col)
        self.setCursorPosition(\
            line + txt.contains(self.linesepRegExp),
            col  + l)
        
    def __configure(self):
        """
        Private method to open the configuration dialog.
        """
        e4App().getObject("UserInterface").showPreferences("terminalPage")
