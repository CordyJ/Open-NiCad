# -*- coding: utf-8 -*-

# Copyright (c) 2007 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a minimalistic editor for simple editing tasks.
"""

import sys
import os
import re

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.Qsci import QsciScintilla

from KdeQt.KQApplication import e4App
from KdeQt import KQFileDialog, KQMessageBox, KQInputDialog
from KdeQt.KQMainWindow import KQMainWindow
from KdeQt.KQPrintDialog import KQPrintDialog
import KdeQt

from E4Gui.E4Action import E4Action, createActionGroup

import Lexers
from QsciScintillaCompat import QsciScintillaCompat, QSCINTILLA_VERSION
from SearchReplaceWidget import SearchReplaceWidget

import UI.PixmapCache
import UI.Config

from Printer import Printer

import Preferences

class MiniScintilla(QsciScintillaCompat):
    """
    Class implementing a QsciScintillaCompat subclass for handling focus events.
    """
    def __init__(self, parent = None):
        """
        Constructor
        
        @param parent parent widget (QWidget)
        @param flags window flags
        """
        QsciScintillaCompat.__init__(self, parent)
        
        self.mw = parent
    
    def getFileName(self):
        """
        Public method to return the name of the file being displayed.
        
        @return filename of the displayed file (string)
        """
        return self.mw.getFileName()
    
    def focusInEvent(self, event):
        """
        Protected method called when the editor receives focus.
        
        This method checks for modifications of the current file and
        rereads it upon request. The cursor is placed at the current position
        assuming, that it is in the vicinity of the old position after the reread.
        
        @param event the event object (QFocusEvent)
        """
        self.mw.editorActGrp.setEnabled(True)
        try:
            self.setCaretWidth(self.mw.caretWidth)
        except AttributeError:
            pass
        
        QsciScintillaCompat.focusInEvent(self, event)
    
    def focusOutEvent(self, event):
        """
        Public method called when the editor loses focus.
        
        @param event the event object (QFocusEvent)
        """
        self.mw.editorActGrp.setEnabled(False)
        self.setCaretWidth(0)
        
        QsciScintillaCompat.focusOutEvent(self, event)

class MiniEditor(KQMainWindow):
    """
    Class implementing a minimalistic editor for simple editing tasks.
    
    @signal editorSaved emitted after the file has been saved
    """
    def __init__(self, filename = "", filetype = "", parent = None, name = None):
        """
        Constructor
        
        @param filename name of the file to open (string or QString)
        @param filetype type of the source file (string)
        @param parent reference to the parent widget (QWidget)
        @param name object name of the window (QString)
        """
        KQMainWindow.__init__(self, parent)
        if name is not None:
            self.setObjectName(name)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setWindowIcon(UI.PixmapCache.getIcon("editor.png"))
        
        self.__textEdit = MiniScintilla(self)
        self.__textEdit.clearSearchIndicators = self.clearSearchIndicators
        self.__textEdit.setSearchIndicator = self.setSearchIndicator
        self.__textEdit.setUtf8(True)
        
        self.srHistory = {
            "search" : QStringList(), 
            "replace" : QStringList()
        }
        self.searchDlg = SearchReplaceWidget(False, self, self)
        self.replaceDlg = SearchReplaceWidget(True, self, self)
        
        centralWidget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(1, 1, 1, 1)
        layout.addWidget(self.__textEdit)
        layout.addWidget(self.searchDlg)
        layout.addWidget(self.replaceDlg)
        centralWidget.setLayout(layout)
        self.setCentralWidget(centralWidget)
        self.searchDlg.hide()
        self.replaceDlg.hide()
        
        self.lexer_ = None
        self.apiLanguage = ""
        self.filetype = ""
        
        self.__createActions()
        self.__createMenus()
        self.__createToolBars()
        self.__createStatusBar()
        
        self.__setTextDisplay()
        self.__setMargins()
        self.__setEolMode()
        
        self.__readSettings()
        
        # clear QScintilla defined keyboard commands
        # we do our own handling through the view manager
        self.__textEdit.clearAlternateKeys()
        self.__textEdit.clearKeys()
        
        # initialise the mark occurrences timer
        self.__markOccurrencesTimer = QTimer(self)
        self.__markOccurrencesTimer.setSingleShot(True)
        self.__markOccurrencesTimer.setInterval(
            Preferences.getEditor("MarkOccurrencesTimeout"))
        self.connect(self.__markOccurrencesTimer, SIGNAL("timeout()"), 
                     self.__markOccurrences)
        self.__markedText = QString()
        
        self.connect(self.__textEdit, SIGNAL("textChanged()"), self.__documentWasModified)
        self.connect(self.__textEdit, SIGNAL('modificationChanged(bool)'), 
                     self.__modificationChanged)
        self.connect(self.__textEdit, SIGNAL('cursorPositionChanged(int, int)'),
                     self.__cursorPositionChanged)
        
        self.__textEdit.setContextMenuPolicy(Qt.CustomContextMenu)
        self.connect(self.__textEdit, 
                     SIGNAL("customContextMenuRequested(const QPoint &)"),
                     self.__contextMenuRequested)
        
        self.connect(self.__textEdit, 
                     SIGNAL("selectionChanged()"), 
                     self.searchDlg.selectionChanged)
        self.connect(self.__textEdit, 
                     SIGNAL("selectionChanged()"), 
                     self.replaceDlg.selectionChanged)
        
        self.__setCurrentFile(QString(""))
        if filename:
            self.__loadFile(QString(filename), filetype)
        
        self.__checkActions()

    def closeEvent(self, event):
        """
        Public method to handle the close event.
        
        @param event close event (QCloseEvent)
        """
        if self.__maybeSave():
            self.__writeSettings()
            event.accept()
        else:
            event.ignore()
    
    def __newFile(self):
        """
        Private slot to create a new file.
        """
        if self.__maybeSave():
            self.__textEdit.clear()
            self.__setCurrentFile(QString(""))
        
        self.__checkActions()
    
    def __open(self):
        """
        Private slot to open a file.
        """
        if self.__maybeSave():
            fileName = KQFileDialog.getOpenFileName(self)
            if not fileName.isEmpty():
                self.__loadFile(fileName)
        self.__checkActions()
    
    def __save(self):
        """
        Private slot to save a file.
        """
        if self.__curFile.isEmpty():
            return self.__saveAs()
        else:
            return self.__saveFile(self.__curFile)
    
    def __saveAs(self):
        """
        Private slot to save a file with a new name.
        """
        fileName = KQFileDialog.getSaveFileName(self)
        if fileName.isEmpty():
            return False
        
        return self.__saveFile(fileName)
    
    def __about(self):
        """
        Private slot to show a little About message.
        """
        KQMessageBox.about(self, self.trUtf8("About eric4 Mini Editor"),
            self.trUtf8("The eric4 Mini Editor is an editor component"
                " based on QScintilla. It may be used for simple"
                " editing tasks, that don't need the power of"
                " a full blown editor."))
    
    def __aboutQt(self):
        """
        Private slot to handle the About Qt dialog.
        """
        QMessageBox.aboutQt(self, "eric4 Mini Editor")
    
    def __aboutKde(self):
        """
        Private slot to handle the About KDE dialog.
        """
        from PyKDE4.kdeui import KHelpMenu
        menu = KHelpMenu(self)
        menu.aboutKDE()
    
    def __whatsThis(self):
        """
        Private slot called in to enter Whats This mode.
        """
        QWhatsThis.enterWhatsThisMode()
    
    def __documentWasModified(self):
        """
        Private slot to handle a change in the documents modification status.
        """
        self.setWindowModified(self.__textEdit.isModified())
    
    def __checkActions(self, setSb = True):
        """
        Private slot to check some actions for their enable/disable status
        and set the statusbar info.
        
        @param setSb flag indicating an update of the status bar is wanted (boolean)
        """
        self.saveAct.setEnabled(self.__textEdit.isModified())
        
        self.undoAct.setEnabled(self.__textEdit.isUndoAvailable())
        self.redoAct.setEnabled(self.__textEdit.isRedoAvailable())
        
        if setSb:
            line, pos = self.__textEdit.getCursorPosition()
            self.__setSbFile(line + 1, pos)
    
    def __setSbFile(self, line = None, pos = None):
        """
        Private method to set the file info in the status bar.
        
        @param line line number to display (int)
        @param pos character position to display (int)
        """
        if self.__curFile.isEmpty():
            writ = '   '
        else:
            if QFileInfo(self.__curFile).isWritable():
                writ = ' rw'
            else:
                writ = ' ro'
        
        self.sbWritable.setText(writ)
        
        if line is None:
            line = ''
        self.sbLine.setText(self.trUtf8('Line: %1').arg(line, 5))
        
        if pos is None:
            pos = ''
        self.sbPos.setText(self.trUtf8('Pos: %1').arg(pos, 5))
    
    def __readShortcut(self, act, category):
        """
        Private function to read a single keyboard shortcut from the settings.
        
        @param act reference to the action object (E4Action)
        @param category category the action belongs to (string or QString)
        @param prefClass preferences class used as the storage area
        """
        if not act.objectName().isEmpty():
            accel = Preferences.Prefs.settings.value(\
                QString("Shortcuts/%1/%2/Accel").arg(category).arg(act.objectName()))
            if accel.isValid():
                act.setShortcut(QKeySequence(accel.toString()))
            accel = Preferences.Prefs.settings.value(\
                QString("Shortcuts/%1/%2/AltAccel").arg(category).arg(act.objectName()))
            if accel.isValid():
                act.setAlternateShortcut(QKeySequence(accel.toString()))
    
    def __createActions(self):
        """
        Private method to create the actions.
        """
        self.fileActions = []
        self.editActions = []
        self.helpActions = []
        self.searchActions = []
        
        self.__createFileActions()
        self.__createEditActions()
        self.__createHelpActions()
        self.__createSearchActions()
        
        # read the keyboard shortcuts and make them identical to the main
        # eric4 shortcuts
        for act in self.helpActions:
            self.__readShortcut(act, "General")
        for act in self.editActions:
            self.__readShortcut(act, "Edit")
        for act in self.fileActions:
            self.__readShortcut(act, "File")
        for act in self.searchActions:
            self.__readShortcut(act, "Search")
    
    def __createFileActions(self):
        """
        Private method to create the File actions.
        """
        self.newAct = E4Action(self.trUtf8('New'),
                UI.PixmapCache.getIcon("new.png"),
                self.trUtf8('&New'),
                QKeySequence(self.trUtf8("Ctrl+N", "File|New")),
                0, self, 'vm_file_new')
        self.newAct.setStatusTip(self.trUtf8('Open an empty editor window'))
        self.newAct.setWhatsThis(self.trUtf8(\
            """<b>New</b>"""
            """<p>An empty editor window will be created.</p>"""
        ))
        self.connect(self.newAct, SIGNAL('triggered()'), self.__newFile)
        self.fileActions.append(self.newAct)
        
        self.openAct = E4Action(self.trUtf8('Open'),
                UI.PixmapCache.getIcon("open.png"),
                self.trUtf8('&Open...'),
                QKeySequence(self.trUtf8("Ctrl+O", "File|Open")), 
                0, self, 'vm_file_open')
        self.openAct.setStatusTip(self.trUtf8('Open a file'))
        self.openAct.setWhatsThis(self.trUtf8(\
            """<b>Open a file</b>"""
            """<p>You will be asked for the name of a file to be opened.</p>"""
        ))
        self.connect(self.openAct, SIGNAL('triggered()'), self.__open)
        self.fileActions.append(self.openAct)
        
        self.saveAct = E4Action(self.trUtf8('Save'),
                UI.PixmapCache.getIcon("fileSave.png"),
                self.trUtf8('&Save'),
                QKeySequence(self.trUtf8("Ctrl+S", "File|Save")), 
                0, self, 'vm_file_save')
        self.saveAct.setStatusTip(self.trUtf8('Save the current file'))
        self.saveAct.setWhatsThis(self.trUtf8(\
            """<b>Save File</b>"""
            """<p>Save the contents of current editor window.</p>"""
        ))
        self.connect(self.saveAct, SIGNAL('triggered()'), self.__save)
        self.fileActions.append(self.saveAct)
        
        self.saveAsAct = E4Action(self.trUtf8('Save as'),
                UI.PixmapCache.getIcon("fileSaveAs.png"),
                self.trUtf8('Save &as...'),
                QKeySequence(self.trUtf8("Shift+Ctrl+S", "File|Save As")), 
                0, self, 'vm_file_save_as')
        self.saveAsAct.setStatusTip(self.trUtf8('Save the current file to a new one'))
        self.saveAsAct.setWhatsThis(self.trUtf8(\
            """<b>Save File as</b>"""
            """<p>Save the contents of current editor window to a new file."""
            """ The file can be entered in a file selection dialog.</p>"""
        ))
        self.connect(self.saveAsAct, SIGNAL('triggered()'), self.__saveAs)
        self.fileActions.append(self.saveAsAct)
        
        self.closeAct = E4Action(self.trUtf8('Close'),
                UI.PixmapCache.getIcon("close.png"),
                self.trUtf8('&Close'),
                QKeySequence(self.trUtf8("Ctrl+W", "File|Close")), 
                0, self, 'vm_file_close')
        self.closeAct.setStatusTip(self.trUtf8('Close the editor window'))
        self.closeAct.setWhatsThis(self.trUtf8(\
            """<b>Close Window</b>"""
            """<p>Close the current window.</p>"""
        ))
        self.connect(self.closeAct, SIGNAL('triggered()'), self.close)
        self.fileActions.append(self.closeAct)
        
        self.printAct = E4Action(self.trUtf8('Print'),
                UI.PixmapCache.getIcon("print.png"),
                self.trUtf8('&Print'),
                QKeySequence(self.trUtf8("Ctrl+P", "File|Print")), 
                0, self, 'vm_file_print')
        self.printAct.setStatusTip(self.trUtf8('Print the current file'))
        self.printAct.setWhatsThis(self.trUtf8( 
            """<b>Print File</b>"""
            """<p>Print the contents of the current file.</p>"""
        ))
        self.connect(self.printAct, SIGNAL('triggered()'), self.__printFile)
        self.fileActions.append(self.printAct)
        
        self.printPreviewAct = \
            E4Action(self.trUtf8('Print Preview'),
                UI.PixmapCache.getIcon("printPreview.png"),
                QApplication.translate('ViewManager', 'Print Preview'),
                0, 0, self, 'vm_file_print_preview')
        self.printPreviewAct.setStatusTip(self.trUtf8(
            'Print preview of the current file'))
        self.printPreviewAct.setWhatsThis(self.trUtf8(
            """<b>Print Preview</b>"""
            """<p>Print preview of the current file.</p>"""
        ))
        self.connect(self.printPreviewAct, SIGNAL('triggered()'), 
            self.__printPreviewFile)
        self.fileActions.append(self.printPreviewAct)
    
    def __createEditActions(self):
        """
        Private method to create the Edit actions.
        """
        self.undoAct = E4Action(self.trUtf8('Undo'),
                UI.PixmapCache.getIcon("editUndo.png"),
                self.trUtf8('&Undo'),
                QKeySequence(self.trUtf8("Ctrl+Z", "Edit|Undo")), 
                QKeySequence(self.trUtf8("Alt+Backspace", "Edit|Undo")), 
                self, 'vm_edit_undo')
        self.undoAct.setStatusTip(self.trUtf8('Undo the last change'))
        self.undoAct.setWhatsThis(self.trUtf8(\
            """<b>Undo</b>"""
            """<p>Undo the last change done in the current editor.</p>"""
        ))
        self.connect(self.undoAct, SIGNAL('triggered()'), self.__undo)
        self.editActions.append(self.undoAct)
        
        self.redoAct = E4Action(self.trUtf8('Redo'),
                UI.PixmapCache.getIcon("editRedo.png"),
                self.trUtf8('&Redo'),
                QKeySequence(self.trUtf8("Ctrl+Shift+Z", "Edit|Redo")), 
                0, self, 'vm_edit_redo')
        self.redoAct.setStatusTip(self.trUtf8('Redo the last change'))
        self.redoAct.setWhatsThis(self.trUtf8(\
            """<b>Redo</b>"""
            """<p>Redo the last change done in the current editor.</p>"""
        ))
        self.connect(self.redoAct, SIGNAL('triggered()'), self.__redo)
        self.editActions.append(self.redoAct)
        
        self.cutAct = E4Action(self.trUtf8('Cut'),
                UI.PixmapCache.getIcon("editCut.png"),
                self.trUtf8('Cu&t'),
                QKeySequence(self.trUtf8("Ctrl+X", "Edit|Cut")),
                QKeySequence(self.trUtf8("Shift+Del", "Edit|Cut")),
                self, 'vm_edit_cut')
        self.cutAct.setStatusTip(self.trUtf8('Cut the selection'))
        self.cutAct.setWhatsThis(self.trUtf8(\
            """<b>Cut</b>"""
            """<p>Cut the selected text of the current editor to the clipboard.</p>"""
        ))
        self.connect(self.cutAct, SIGNAL('triggered()'), self.__textEdit.cut)
        self.editActions.append(self.cutAct)
        
        self.copyAct = E4Action(self.trUtf8('Copy'),
                UI.PixmapCache.getIcon("editCopy.png"),
                self.trUtf8('&Copy'),
                QKeySequence(self.trUtf8("Ctrl+C", "Edit|Copy")), 
                QKeySequence(self.trUtf8("Ctrl+Ins", "Edit|Copy")), 
                self, 'vm_edit_copy')
        self.copyAct.setStatusTip(self.trUtf8('Copy the selection'))
        self.copyAct.setWhatsThis(self.trUtf8(\
            """<b>Copy</b>"""
            """<p>Copy the selected text of the current editor to the clipboard.</p>"""
        ))
        self.connect(self.copyAct, SIGNAL('triggered()'), self.__textEdit.copy)
        self.editActions.append(self.copyAct)
        
        self.pasteAct = E4Action(self.trUtf8('Paste'),
                UI.PixmapCache.getIcon("editPaste.png"),
                self.trUtf8('&Paste'),
                QKeySequence(self.trUtf8("Ctrl+V", "Edit|Paste")), 
                QKeySequence(self.trUtf8("Shift+Ins", "Edit|Paste")), 
                self, 'vm_edit_paste')
        self.pasteAct.setStatusTip(self.trUtf8('Paste the last cut/copied text'))
        self.pasteAct.setWhatsThis(self.trUtf8(\
            """<b>Paste</b>"""
            """<p>Paste the last cut/copied text from the clipboard to"""
            """ the current editor.</p>"""
        ))
        self.connect(self.pasteAct, SIGNAL('triggered()'), self.__textEdit.paste)
        self.editActions.append(self.pasteAct)
        
        self.deleteAct = E4Action(self.trUtf8('Clear'),
                UI.PixmapCache.getIcon("editDelete.png"),
                self.trUtf8('Cl&ear'),
                QKeySequence(self.trUtf8("Alt+Shift+C", "Edit|Clear")), 
                0,
                self, 'vm_edit_clear')
        self.deleteAct.setStatusTip(self.trUtf8('Clear all text'))
        self.deleteAct.setWhatsThis(self.trUtf8(\
            """<b>Clear</b>"""
            """<p>Delete all text of the current editor.</p>"""
        ))
        self.connect(self.deleteAct, SIGNAL('triggered()'), self.__textEdit.clear)
        self.editActions.append(self.deleteAct)
        
        self.cutAct.setEnabled(False);
        self.copyAct.setEnabled(False);
        self.connect(self.__textEdit, SIGNAL("copyAvailable(bool)"),
                self.cutAct, SLOT("setEnabled(bool)"))
        self.connect(self.__textEdit, SIGNAL("copyAvailable(bool)"),
                self.copyAct, SLOT("setEnabled(bool)"))
        
        ####################################################################
        ## Below follow the actions for qscintilla standard commands.
        ####################################################################
        
        self.esm = QSignalMapper(self)
        self.connect(self.esm, SIGNAL('mapped(int)'), self.__textEdit.editorCommand)
        
        self.editorActGrp = createActionGroup(self)
        
        act = E4Action(QApplication.translate('ViewManager', 'Move left one character'), 
                      QApplication.translate('ViewManager', 'Move left one character'), 
                      QKeySequence(QApplication.translate('ViewManager', 'Left')), 0,
                      self.editorActGrp, 'vm_edit_move_left_char')
        self.esm.setMapping(act, QsciScintilla.SCI_CHARLEFT)
        self.connect(act, SIGNAL('triggered()'), self.esm, SLOT('map()'))
        self.editActions.append(act)
        
        act = E4Action(QApplication.translate('ViewManager', 'Move right one character'), 
                      QApplication.translate('ViewManager', 'Move right one character'), 
                      QKeySequence(QApplication.translate('ViewManager', 'Right')), 0,
                      self.editorActGrp, 'vm_edit_move_right_char')
        self.esm.setMapping(act, QsciScintilla.SCI_CHARRIGHT)
        self.connect(act, SIGNAL('triggered()'), self.esm, SLOT('map()'))
        self.editActions.append(act)
        
        act = E4Action(QApplication.translate('ViewManager', 'Move up one line'), 
                      QApplication.translate('ViewManager', 'Move up one line'), 
                      QKeySequence(QApplication.translate('ViewManager', 'Up')), 0,
                      self.editorActGrp, 'vm_edit_move_up_line')
        self.esm.setMapping(act, QsciScintilla.SCI_LINEUP)
        self.connect(act, SIGNAL('triggered()'), self.esm, SLOT('map()'))
        self.editActions.append(act)
        
        act = E4Action(QApplication.translate('ViewManager', 'Move down one line'), 
                      QApplication.translate('ViewManager', 'Move down one line'), 
                      QKeySequence(QApplication.translate('ViewManager', 'Down')), 0,
                      self.editorActGrp, 'vm_edit_move_down_line')
        self.esm.setMapping(act, QsciScintilla.SCI_LINEDOWN)
        self.connect(act, SIGNAL('triggered()'), self.esm, SLOT('map()'))
        self.editActions.append(act)
        
        act = E4Action(QApplication.translate('ViewManager', 'Move left one word part'), 
                      QApplication.translate('ViewManager', 'Move left one word part'), 
                      QKeySequence(QApplication.translate('ViewManager', 'Alt+Left')), 0,
                      self.editorActGrp, 'vm_edit_move_left_word_part')
        self.esm.setMapping(act, QsciScintilla.SCI_WORDPARTLEFT)
        self.connect(act, SIGNAL('triggered()'), self.esm, SLOT('map()'))
        self.editActions.append(act)
        
        act = E4Action(QApplication.translate('ViewManager', 'Move right one word part'), 
                      QApplication.translate('ViewManager', 'Move right one word part'), 
                      QKeySequence(QApplication.translate('ViewManager', 'Alt+Right')), 0,
                      self.editorActGrp, 'vm_edit_move_right_word_part')
        self.esm.setMapping(act, QsciScintilla.SCI_WORDPARTRIGHT)
        self.connect(act, SIGNAL('triggered()'), self.esm, SLOT('map()'))
        self.editActions.append(act)
        
        act = E4Action(QApplication.translate('ViewManager', 'Move left one word'), 
                      QApplication.translate('ViewManager', 'Move left one word'), 
                      QKeySequence(QApplication.translate('ViewManager', 'Ctrl+Left')), 0,
                      self.editorActGrp, 'vm_edit_move_left_word')
        self.esm.setMapping(act, QsciScintilla.SCI_WORDLEFT)
        self.connect(act, SIGNAL('triggered()'), self.esm, SLOT('map()'))
        self.editActions.append(act)
        
        act = E4Action(QApplication.translate('ViewManager', 'Move right one word'), 
                      QApplication.translate('ViewManager', 'Move right one word'), 
                      QKeySequence(QApplication.translate('ViewManager', 'Ctrl+Right')), 
                      0,
                      self.editorActGrp, 'vm_edit_move_right_word')
        self.esm.setMapping(act, QsciScintilla.SCI_WORDRIGHT)
        self.connect(act, SIGNAL('triggered()'), self.esm, SLOT('map()'))
        self.editActions.append(act)
        
        act = E4Action(QApplication.translate('ViewManager', 
                        'Move to first visible character in line'), 
                      QApplication.translate('ViewManager', 
                        'Move to first visible character in line'), 
                      QKeySequence(QApplication.translate('ViewManager', 'Home')), 0,
                      self.editorActGrp, 'vm_edit_move_first_visible_char')
        self.esm.setMapping(act, QsciScintilla.SCI_VCHOME)
        self.connect(act, SIGNAL('triggered()'), self.esm, SLOT('map()'))
        self.editActions.append(act)
        
        act = E4Action(QApplication.translate('ViewManager', 
                        'Move to start of displayed line'), 
                      QApplication.translate('ViewManager', 
                        'Move to start of displayed line'), 
                      QKeySequence(QApplication.translate('ViewManager', 'Alt+Home')), 0,
                      self.editorActGrp, 'vm_edit_move_start_line')
        self.esm.setMapping(act, QsciScintilla.SCI_HOMEDISPLAY)
        self.connect(act, SIGNAL('triggered()'), self.esm, SLOT('map()'))
        self.editActions.append(act)
        
        act = E4Action(QApplication.translate('ViewManager', 'Move to end of line'), 
                      QApplication.translate('ViewManager', 'Move to end of line'), 
                      QKeySequence(QApplication.translate('ViewManager', 'End')), 0,
                      self.editorActGrp, 'vm_edit_move_end_line')
        self.esm.setMapping(act, QsciScintilla.SCI_LINEEND)
        self.connect(act, SIGNAL('triggered()'), self.esm, SLOT('map()'))
        self.editActions.append(act)
        
        act = E4Action(QApplication.translate('ViewManager', 'Scroll view down one line'),
                      QApplication.translate('ViewManager', 'Scroll view down one line'), 
                      QKeySequence(QApplication.translate('ViewManager', 'Ctrl+Down')), 0,
                      self.editorActGrp, 'vm_edit_scroll_down_line')
        self.esm.setMapping(act, QsciScintilla.SCI_LINESCROLLDOWN)
        self.connect(act, SIGNAL('triggered()'), self.esm, SLOT('map()'))
        self.editActions.append(act)
        
        act = E4Action(QApplication.translate('ViewManager', 'Scroll view up one line'), 
                      QApplication.translate('ViewManager', 'Scroll view up one line'), 
                      QKeySequence(QApplication.translate('ViewManager', 'Ctrl+Up')), 0,
                      self.editorActGrp, 'vm_edit_scroll_up_line')
        self.esm.setMapping(act, QsciScintilla.SCI_LINESCROLLUP)
        self.connect(act, SIGNAL('triggered()'), self.esm, SLOT('map()'))
        self.editActions.append(act)
        
        act = E4Action(QApplication.translate('ViewManager', 'Move up one paragraph'), 
                      QApplication.translate('ViewManager', 'Move up one paragraph'), 
                      QKeySequence(QApplication.translate('ViewManager', 'Alt+Up')), 0,
                      self.editorActGrp, 'vm_edit_move_up_para')
        self.esm.setMapping(act, QsciScintilla.SCI_PARAUP)
        self.connect(act, SIGNAL('triggered()'), self.esm, SLOT('map()'))
        self.editActions.append(act)
        
        act = E4Action(QApplication.translate('ViewManager', 'Move down one paragraph'), 
                      QApplication.translate('ViewManager', 'Move down one paragraph'), 
                      QKeySequence(QApplication.translate('ViewManager', 'Alt+Down')), 0,
                      self.editorActGrp, 'vm_edit_move_down_para')
        self.esm.setMapping(act, QsciScintilla.SCI_PARADOWN)
        self.connect(act, SIGNAL('triggered()'), self.esm, SLOT('map()'))
        self.editActions.append(act)
        
        act = E4Action(QApplication.translate('ViewManager', 'Move up one page'), 
                      QApplication.translate('ViewManager', 'Move up one page'), 
                      QKeySequence(QApplication.translate('ViewManager', 'PgUp')), 0,
                      self.editorActGrp, 'vm_edit_move_up_page')
        self.esm.setMapping(act, QsciScintilla.SCI_PAGEUP)
        self.connect(act, SIGNAL('triggered()'), self.esm, SLOT('map()'))
        self.editActions.append(act)
        
        act = E4Action(QApplication.translate('ViewManager', 'Move down one page'), 
                      QApplication.translate('ViewManager', 'Move down one page'), 
                      QKeySequence(QApplication.translate('ViewManager', 'PgDown')), 0,
                      self.editorActGrp, 'vm_edit_move_down_page')
        self.esm.setMapping(act, QsciScintilla.SCI_PAGEDOWN)
        self.connect(act, SIGNAL('triggered()'), self.esm, SLOT('map()'))
        self.editActions.append(act)
        
        act = E4Action(QApplication.translate('ViewManager', 'Move to start of text'), 
                      QApplication.translate('ViewManager', 'Move to start of text'), 
                      QKeySequence(QApplication.translate('ViewManager', 'Ctrl+Home')), 0,
                      self.editorActGrp, 'vm_edit_move_start_text')
        self.esm.setMapping(act, QsciScintilla.SCI_DOCUMENTSTART)
        self.connect(act, SIGNAL('triggered()'), self.esm, SLOT('map()'))
        self.editActions.append(act)
        
        act = E4Action(QApplication.translate('ViewManager', 'Move to end of text'), 
                      QApplication.translate('ViewManager', 'Move to end of text'), 
                      QKeySequence(QApplication.translate('ViewManager', 'Ctrl+End')), 0,
                      self.editorActGrp, 'vm_edit_move_end_text')
        self.esm.setMapping(act, QsciScintilla.SCI_DOCUMENTEND)
        self.connect(act, SIGNAL('triggered()'), self.esm, SLOT('map()'))
        self.editActions.append(act)
        
        act = E4Action(QApplication.translate('ViewManager', 'Indent one level'), 
                      QApplication.translate('ViewManager', 'Indent one level'), 
                      QKeySequence(QApplication.translate('ViewManager', 'Tab')), 0,
                      self.editorActGrp, 'vm_edit_indent_one_level')
        self.esm.setMapping(act, QsciScintilla.SCI_TAB)
        self.connect(act, SIGNAL('triggered()'), self.esm, SLOT('map()'))
        self.editActions.append(act)
        
        act = E4Action(QApplication.translate('ViewManager', 'Unindent one level'), 
                      QApplication.translate('ViewManager', 'Unindent one level'), 
                      QKeySequence(QApplication.translate('ViewManager', 'Shift+Tab')), 0,
                      self.editorActGrp, 'vm_edit_unindent_one_level')
        self.esm.setMapping(act, QsciScintilla.SCI_BACKTAB)
        self.connect(act, SIGNAL('triggered()'), self.esm, SLOT('map()'))
        self.editActions.append(act)
        
        act = E4Action(QApplication.translate('ViewManager', 
                        'Extend selection left one character'), 
                      QApplication.translate('ViewManager', 
                        'Extend selection left one character'), 
                      QKeySequence(QApplication.translate('ViewManager', 'Shift+Left')), 
                      0,
                      self.editorActGrp, 'vm_edit_extend_selection_left_char')
        self.esm.setMapping(act, QsciScintilla.SCI_CHARLEFTEXTEND)
        self.connect(act, SIGNAL('triggered()'), self.esm, SLOT('map()'))
        self.editActions.append(act)
        
        act = E4Action(QApplication.translate('ViewManager', 
                        'Extend selection right one character'), 
                      QApplication.translate('ViewManager', 
                        'Extend selection right one character'), 
                      QKeySequence(QApplication.translate('ViewManager', 'Shift+Right')), 
                      0,
                      self.editorActGrp, 'vm_edit_extend_selection_right_char')
        self.esm.setMapping(act, QsciScintilla.SCI_CHARRIGHTEXTEND)
        self.connect(act, SIGNAL('triggered()'), self.esm, SLOT('map()'))
        self.editActions.append(act)
        
        act = E4Action(QApplication.translate('ViewManager', 
                        'Extend selection up one line'), 
                      QApplication.translate('ViewManager', 
                        'Extend selection up one line'), 
                      QKeySequence(QApplication.translate('ViewManager', 'Shift+Up')), 0,
                      self.editorActGrp, 'vm_edit_extend_selection_up_line')
        self.esm.setMapping(act, QsciScintilla.SCI_LINEUPEXTEND)
        self.connect(act, SIGNAL('triggered()'), self.esm, SLOT('map()'))
        self.editActions.append(act)
        
        act = E4Action(QApplication.translate('ViewManager', 
                        'Extend selection down one line'), 
                      QApplication.translate('ViewManager', 
                        'Extend selection down one line'), 
                      QKeySequence(QApplication.translate('ViewManager', 'Shift+Down')), 
                      0,
                      self.editorActGrp, 'vm_edit_extend_selection_down_line')
        self.esm.setMapping(act, QsciScintilla.SCI_LINEDOWNEXTEND)
        self.connect(act, SIGNAL('triggered()'), self.esm, SLOT('map()'))
        self.editActions.append(act)
        
        act = E4Action(QApplication.translate('ViewManager', 
                        'Extend selection left one word part'), 
                      QApplication.translate('ViewManager', 
                        'Extend selection left one word part'), 
                      QKeySequence(QApplication.translate('ViewManager', 
                        'Alt+Shift+Left')), 
                      0,
                      self.editorActGrp, 'vm_edit_extend_selection_left_word_part')
        self.esm.setMapping(act, QsciScintilla.SCI_WORDPARTLEFTEXTEND)
        self.connect(act, SIGNAL('triggered()'), self.esm, SLOT('map()'))
        self.editActions.append(act)
        
        act = E4Action(QApplication.translate('ViewManager', 
                        'Extend selection right one word part'), 
                      QApplication.translate('ViewManager', 
                        'Extend selection right one word part'), 
                      QKeySequence(QApplication.translate('ViewManager', 
                        'Alt+Shift+Right')), 
                      0,
                      self.editorActGrp, 'vm_edit_extend_selection_right_word_part')
        self.esm.setMapping(act, QsciScintilla.SCI_WORDPARTRIGHTEXTEND)
        self.connect(act, SIGNAL('triggered()'), self.esm, SLOT('map()'))
        self.editActions.append(act)
        
        act = E4Action(QApplication.translate('ViewManager', 
                        'Extend selection left one word'), 
                      QApplication.translate('ViewManager', 
                        'Extend selection left one word'), 
                      QKeySequence(QApplication.translate('ViewManager', 
                        'Ctrl+Shift+Left')), 
                      0,
                      self.editorActGrp, 'vm_edit_extend_selection_left_word')
        self.esm.setMapping(act, QsciScintilla.SCI_WORDLEFTEXTEND)
        self.connect(act, SIGNAL('triggered()'), self.esm, SLOT('map()'))
        self.editActions.append(act)
        
        act = E4Action(QApplication.translate('ViewManager', 
                        'Extend selection right one word'), 
                      QApplication.translate('ViewManager', 
                        'Extend selection right one word'), 
                      QKeySequence(QApplication.translate('ViewManager', 
                        'Ctrl+Shift+Right')), 
                      0,
                      self.editorActGrp, 'vm_edit_extend_selection_right_word')
        self.esm.setMapping(act, QsciScintilla.SCI_WORDRIGHTEXTEND)
        self.connect(act, SIGNAL('triggered()'), self.esm, SLOT('map()'))
        self.editActions.append(act)
        
        act = E4Action(QApplication.translate('ViewManager', 
                        'Extend selection to first visible character in line'),
                      QApplication.translate('ViewManager', 
                        'Extend selection to first visible character in line'), 
                      QKeySequence(QApplication.translate('ViewManager', 'Shift+Home')), 
                      0,
                      self.editorActGrp, 'vm_edit_extend_selection_first_visible_char')
        self.esm.setMapping(act, QsciScintilla.SCI_VCHOMEEXTEND)
        self.connect(act, SIGNAL('triggered()'), self.esm, SLOT('map()'))
        self.editActions.append(act)
        
        act = E4Action(QApplication.translate('ViewManager', 
                        'Extend selection to start of line'), 
                      QApplication.translate('ViewManager', 
                        'Extend selection to start of line'), 
                      QKeySequence(QApplication.translate('ViewManager', 
                        'Alt+Shift+Home')), 
                      0,
                      self.editorActGrp, 'vm_edit_extend_selection_start_line')
        self.esm.setMapping(act, QsciScintilla.SCI_HOMEDISPLAYEXTEND)
        self.connect(act, SIGNAL('triggered()'), self.esm, SLOT('map()'))
        self.editActions.append(act)
        
        act = E4Action(QApplication.translate('ViewManager', 
                        'Extend selection to end of line'), 
                      QApplication.translate('ViewManager', 
                        'Extend selection to end of line'), 
                      QKeySequence(QApplication.translate('ViewManager', 'Shift+End')), 0,
                      self.editorActGrp, 'vm_edit_extend_selection_end_line')
        self.esm.setMapping(act, QsciScintilla.SCI_LINEENDEXTEND)
        self.connect(act, SIGNAL('triggered()'), self.esm, SLOT('map()'))
        self.editActions.append(act)
        
        act = E4Action(QApplication.translate('ViewManager', 
                        'Extend selection up one paragraph'), 
                      QApplication.translate('ViewManager', 
                        'Extend selection up one paragraph'), 
                      QKeySequence(QApplication.translate('ViewManager', 'Alt+Shift+Up')),
                      0,
                      self.editorActGrp, 'vm_edit_extend_selection_up_para')
        self.esm.setMapping(act, QsciScintilla.SCI_PARAUPEXTEND)
        self.connect(act, SIGNAL('triggered()'), self.esm, SLOT('map()'))
        self.editActions.append(act)
        
        act = E4Action(QApplication.translate('ViewManager', 
                        'Extend selection down one paragraph'), 
                      QApplication.translate('ViewManager', 
                        'Extend selection down one paragraph'), 
                      QKeySequence(QApplication.translate('ViewManager', 
                        'Alt+Shift+Down')), 
                      0,
                      self.editorActGrp, 'vm_edit_extend_selection_down_para')
        self.esm.setMapping(act, QsciScintilla.SCI_PARADOWNEXTEND)
        self.connect(act, SIGNAL('triggered()'), self.esm, SLOT('map()'))
        self.editActions.append(act)
        
        act = E4Action(QApplication.translate('ViewManager', 
                        'Extend selection up one page'), 
                      QApplication.translate('ViewManager', 
                        'Extend selection up one page'), 
                      QKeySequence(QApplication.translate('ViewManager', 'Shift+PgUp')), 
                      0,
                      self.editorActGrp, 'vm_edit_extend_selection_up_page')
        self.esm.setMapping(act, QsciScintilla.SCI_PAGEUPEXTEND)
        self.connect(act, SIGNAL('triggered()'), self.esm, SLOT('map()'))
        self.editActions.append(act)
        
        act = E4Action(QApplication.translate('ViewManager', 
                        'Extend selection down one page'), 
                      QApplication.translate('ViewManager', 
                        'Extend selection down one page'), 
                      QKeySequence(QApplication.translate('ViewManager', 'Shift+PgDown')),
                      0,
                      self.editorActGrp, 'vm_edit_extend_selection_down_page')
        self.esm.setMapping(act, QsciScintilla.SCI_PAGEDOWNEXTEND)
        self.connect(act, SIGNAL('triggered()'), self.esm, SLOT('map()'))
        self.editActions.append(act)
        
        act = E4Action(QApplication.translate('ViewManager', 
                        'Extend selection to start of text'), 
                      QApplication.translate('ViewManager', 
                        'Extend selection to start of text'), 
                      QKeySequence(QApplication.translate('ViewManager', 
                        'Ctrl+Shift+Home')),
                      0,
                      self.editorActGrp, 'vm_edit_extend_selection_start_text')
        self.esm.setMapping(act, QsciScintilla.SCI_DOCUMENTSTARTEXTEND)
        self.connect(act, SIGNAL('triggered()'), self.esm, SLOT('map()'))
        self.editActions.append(act)
        
        act = E4Action(QApplication.translate('ViewManager', 
                        'Extend selection to end of text'), 
                      QApplication.translate('ViewManager', 
                        'Extend selection to end of text'), 
                      QKeySequence(QApplication.translate('ViewManager', 
                        'Ctrl+Shift+End')), 
                      0,
                      self.editorActGrp, 'vm_edit_extend_selection_end_text')
        self.esm.setMapping(act, QsciScintilla.SCI_DOCUMENTENDEXTEND)
        self.connect(act, SIGNAL('triggered()'), self.esm, SLOT('map()'))
        self.editActions.append(act)
        
        act = E4Action(QApplication.translate('ViewManager', 
                        'Delete previous character'), 
                      QApplication.translate('ViewManager', 'Delete previous character'), 
                      QKeySequence(QApplication.translate('ViewManager', 'Backspace')), 
                      QKeySequence(QApplication.translate('ViewManager', 
                        'Shift+Backspace')), 
                      self.editorActGrp, 'vm_edit_delete_previous_char')
        self.esm.setMapping(act, QsciScintilla.SCI_DELETEBACK)
        self.connect(act, SIGNAL('triggered()'), self.esm, SLOT('map()'))
        self.editActions.append(act)
        
        act = E4Action(QApplication.translate('ViewManager', 
                        'Delete previous character if not at line start'), 
                      QApplication.translate('ViewManager', 
                        'Delete previous character if not at line start'), 
                      0, 0,
                      self.editorActGrp, 'vm_edit_delet_previous_char_not_line_start')
        self.esm.setMapping(act, QsciScintilla.SCI_DELETEBACKNOTLINE)
        self.connect(act, SIGNAL('triggered()'), self.esm, SLOT('map()'))
        self.editActions.append(act)
        
        act = E4Action(QApplication.translate('ViewManager', 'Delete current character'), 
                      QApplication.translate('ViewManager', 'Delete current character'), 
                      QKeySequence(QApplication.translate('ViewManager', 'Del')), 0,
                      self.editorActGrp, 'vm_edit_delete_current_char')
        self.esm.setMapping(act, QsciScintilla.SCI_CLEAR)
        self.connect(act, SIGNAL('triggered()'), self.esm, SLOT('map()'))
        self.editActions.append(act)
        
        act = E4Action(QApplication.translate('ViewManager', 'Delete word to left'), 
                      QApplication.translate('ViewManager', 'Delete word to left'), 
                      QKeySequence(QApplication.translate('ViewManager', 
                        'Ctrl+Backspace')), 
                      0,
                      self.editorActGrp, 'vm_edit_delete_word_left')
        self.esm.setMapping(act, QsciScintilla.SCI_DELWORDLEFT)
        self.connect(act, SIGNAL('triggered()'), self.esm, SLOT('map()'))
        self.editActions.append(act)
        
        act = E4Action(QApplication.translate('ViewManager', 'Delete word to right'), 
                      QApplication.translate('ViewManager', 'Delete word to right'), 
                      QKeySequence(QApplication.translate('ViewManager', 'Ctrl+Del')), 0,
                      self.editorActGrp, 'vm_edit_delete_word_right')
        self.esm.setMapping(act, QsciScintilla.SCI_DELWORDRIGHT)
        self.connect(act, SIGNAL('triggered()'), self.esm, SLOT('map()'))
        self.editActions.append(act)
        
        act = E4Action(QApplication.translate('ViewManager', 'Delete line to left'), 
                      QApplication.translate('ViewManager', 'Delete line to left'), 
                      QKeySequence(QApplication.translate('ViewManager', 
                        'Ctrl+Shift+Backspace')), 
                      0,
                      self.editorActGrp, 'vm_edit_delete_line_left')
        self.esm.setMapping(act, QsciScintilla.SCI_DELLINELEFT)
        self.connect(act, SIGNAL('triggered()'), self.esm, SLOT('map()'))
        self.editActions.append(act)
        
        act = E4Action(QApplication.translate('ViewManager', 'Delete line to right'), 
                      QApplication.translate('ViewManager', 'Delete line to right'), 
                      QKeySequence(QApplication.translate('ViewManager', 
                        'Ctrl+Shift+Del')), 
                      0,
                      self.editorActGrp, 'vm_edit_delete_line_right')
        self.esm.setMapping(act, QsciScintilla.SCI_DELLINERIGHT)
        self.connect(act, SIGNAL('triggered()'), self.esm, SLOT('map()'))
        self.editActions.append(act)
        
        act = E4Action(QApplication.translate('ViewManager', 'Insert new line'), 
                      QApplication.translate('ViewManager', 'Insert new line'), 
                      QKeySequence(QApplication.translate('ViewManager', 'Return')), 
                      QKeySequence(QApplication.translate('ViewManager', 'Enter')), 
                      self.editorActGrp, 'vm_edit_insert_line')
        self.esm.setMapping(act, QsciScintilla.SCI_NEWLINE)
        self.connect(act, SIGNAL('triggered()'), self.esm, SLOT('map()'))
        self.editActions.append(act)
        
        act = E4Action(QApplication.translate('ViewManager', 
                                              'Insert new line below current line'), 
                      QApplication.translate('ViewManager', 
                                             'Insert new line below current line'), 
                      QKeySequence(QApplication.translate('ViewManager', 'Shift+Return')),
                      QKeySequence(QApplication.translate('ViewManager', 'Shift+Enter')), 
                      self.editorActGrp, 'vm_edit_insert_line_below')
        self.connect(act, SIGNAL('triggered()'), self.__textEdit.newLineBelow)
        self.editActions.append(act)
        
        act = E4Action(QApplication.translate('ViewManager', 'Delete current line'), 
                      QApplication.translate('ViewManager', 'Delete current line'), 
                      QKeySequence(QApplication.translate('ViewManager', 'Ctrl+U')), 
                      QKeySequence(QApplication.translate('ViewManager', 'Ctrl+Shift+L')),
                      self.editorActGrp, 'vm_edit_delete_current_line')
        self.esm.setMapping(act, QsciScintilla.SCI_LINEDELETE)
        self.connect(act, SIGNAL('triggered()'), self.esm, SLOT('map()'))
        self.editActions.append(act)
        
        act = E4Action(QApplication.translate('ViewManager', 'Duplicate current line'), 
                      QApplication.translate('ViewManager', 'Duplicate current line'), 
                      QKeySequence(QApplication.translate('ViewManager', 'Ctrl+D')), 0,
                      self.editorActGrp, 'vm_edit_duplicate_current_line')
        self.esm.setMapping(act, QsciScintilla.SCI_LINEDUPLICATE)
        self.connect(act, SIGNAL('triggered()'), self.esm, SLOT('map()'))
        self.editActions.append(act)
        
        act = E4Action(QApplication.translate('ViewManager', 
                        'Swap current and previous lines'), 
                      QApplication.translate('ViewManager', 
                        'Swap current and previous lines'), 
                      QKeySequence(QApplication.translate('ViewManager', 'Ctrl+T')), 0,
                      self.editorActGrp, 'vm_edit_swap_current_previous_line')
        self.esm.setMapping(act, QsciScintilla.SCI_LINETRANSPOSE)
        self.connect(act, SIGNAL('triggered()'), self.esm, SLOT('map()'))
        self.editActions.append(act)
        
        act = E4Action(QApplication.translate('ViewManager', 'Cut current line'), 
                      QApplication.translate('ViewManager', 'Cut current line'), 
                      QKeySequence(QApplication.translate('ViewManager', 'Alt+Shift+L')),
                      0,
                      self.editorActGrp, 'vm_edit_cut_current_line')
        self.esm.setMapping(act, QsciScintilla.SCI_LINECUT)
        self.connect(act, SIGNAL('triggered()'), self.esm, SLOT('map()'))
        self.editActions.append(act)
        
        act = E4Action(QApplication.translate('ViewManager', 'Copy current line'), 
                      QApplication.translate('ViewManager', 'Copy current line'), 
                      QKeySequence(QApplication.translate('ViewManager', 'Ctrl+Shift+T')),
                      0,
                      self.editorActGrp, 'vm_edit_copy_current_line')
        self.esm.setMapping(act, QsciScintilla.SCI_LINECOPY)
        self.connect(act, SIGNAL('triggered()'), self.esm, SLOT('map()'))
        self.editActions.append(act)
        
        act = E4Action(QApplication.translate('ViewManager', 'Toggle insert/overtype'), 
                      QApplication.translate('ViewManager', 'Toggle insert/overtype'), 
                      QKeySequence(QApplication.translate('ViewManager', 'Ins')), 0,
                      self.editorActGrp, 'vm_edit_toggle_insert_overtype')
        self.esm.setMapping(act, QsciScintilla.SCI_EDITTOGGLEOVERTYPE)
        self.connect(act, SIGNAL('triggered()'), self.esm, SLOT('map()'))
        self.editActions.append(act)
        
        act = E4Action(QApplication.translate('ViewManager', 
                        'Convert selection to lower case'), 
                      QApplication.translate('ViewManager', 
                        'Convert selection to lower case'), 
                      QKeySequence(QApplication.translate('ViewManager', 'Alt+Shift+U')),
                      0,
                      self.editorActGrp, 'vm_edit_convert_selection_lower')
        self.esm.setMapping(act, QsciScintilla.SCI_LOWERCASE)
        self.connect(act, SIGNAL('triggered()'), self.esm, SLOT('map()'))
        self.editActions.append(act)
        
        act = E4Action(QApplication.translate('ViewManager', 
                        'Convert selection to upper case'), 
                      QApplication.translate('ViewManager', 
                        'Convert selection to upper case'), 
                      QKeySequence(QApplication.translate('ViewManager', 'Ctrl+Shift+U')),
                      0,
                      self.editorActGrp, 'vm_edit_convert_selection_upper')
        self.esm.setMapping(act, QsciScintilla.SCI_UPPERCASE)
        self.connect(act, SIGNAL('triggered()'), self.esm, SLOT('map()'))
        self.editActions.append(act)
        
        act = E4Action(QApplication.translate('ViewManager', 
                        'Move to end of displayed line'), 
                      QApplication.translate('ViewManager', 
                        'Move to end of displayed line'), 
                      QKeySequence(QApplication.translate('ViewManager', 'Alt+End')), 0,
                      self.editorActGrp, 'vm_edit_move_end_displayed_line')
        self.esm.setMapping(act, QsciScintilla.SCI_LINEENDDISPLAY)
        self.connect(act, SIGNAL('triggered()'), self.esm, SLOT('map()'))
        self.editActions.append(act)
        
        act = E4Action(QApplication.translate('ViewManager', 
                        'Extend selection to end of displayed line'), 
                      QApplication.translate('ViewManager', 
                        'Extend selection to end of displayed line'), 
                      0, 0,
                      self.editorActGrp, 'vm_edit_extend_selection_end_displayed_line')
        self.esm.setMapping(act, QsciScintilla.SCI_LINEENDDISPLAYEXTEND)
        self.connect(act, SIGNAL('triggered()'), self.esm, SLOT('map()'))
        self.editActions.append(act)
        
        act = E4Action(QApplication.translate('ViewManager', 'Formfeed'), 
                      QApplication.translate('ViewManager', 'Formfeed'), 
                      0, 0,
                      self.editorActGrp, 'vm_edit_formfeed')
        self.esm.setMapping(act, QsciScintilla.SCI_FORMFEED)
        self.connect(act, SIGNAL('triggered()'), self.esm, SLOT('map()'))
        self.editActions.append(act)
        
        act = E4Action(QApplication.translate('ViewManager', 'Escape'), 
                      QApplication.translate('ViewManager', 'Escape'), 
                      QKeySequence(QApplication.translate('ViewManager', 'Esc')), 0,
                      self.editorActGrp, 'vm_edit_escape')
        self.esm.setMapping(act, QsciScintilla.SCI_CANCEL)
        self.connect(act, SIGNAL('triggered()'), self.esm, SLOT('map()'))
        self.editActions.append(act)
        
        act = E4Action(QApplication.translate('ViewManager', 
                        'Extend rectangular selection down one line'), 
                      QApplication.translate('ViewManager', 
                        'Extend rectangular selection down one line'), 
                      QKeySequence(QApplication.translate('ViewManager', 
                        'Alt+Ctrl+Down')), 
                      0,
                      self.editorActGrp, 'vm_edit_extend_rect_selection_down_line')
        self.esm.setMapping(act, QsciScintilla.SCI_LINEDOWNRECTEXTEND)
        self.connect(act, SIGNAL('triggered()'), self.esm, SLOT('map()'))
        self.editActions.append(act)
        
        act = E4Action(QApplication.translate('ViewManager', 
                        'Extend rectangular selection up one line'), 
                      QApplication.translate('ViewManager', 
                        'Extend rectangular selection up one line'), 
                      QKeySequence(QApplication.translate('ViewManager', 'Alt+Ctrl+Up')),
                      0,
                      self.editorActGrp, 'vm_edit_extend_rect_selection_up_line')
        self.esm.setMapping(act, QsciScintilla.SCI_LINEUPRECTEXTEND)
        self.connect(act, SIGNAL('triggered()'), self.esm, SLOT('map()'))
        self.editActions.append(act)
        
        act = E4Action(QApplication.translate('ViewManager', 
                        'Extend rectangular selection left one character'), 
                      QApplication.translate('ViewManager', 
                        'Extend rectangular selection left one character'), 
                      QKeySequence(QApplication.translate('ViewManager', 
                        'Alt+Ctrl+Left')), 
                      0,
                      self.editorActGrp, 'vm_edit_extend_rect_selection_left_char')
        self.esm.setMapping(act, QsciScintilla.SCI_CHARLEFTRECTEXTEND)
        self.connect(act, SIGNAL('triggered()'), self.esm, SLOT('map()'))
        self.editActions.append(act)
        
        act = E4Action(QApplication.translate('ViewManager', 
                        'Extend rectangular selection right one character'), 
                      QApplication.translate('ViewManager', 
                        'Extend rectangular selection right one character'), 
                      QKeySequence(QApplication.translate('ViewManager', 
                        'Alt+Ctrl+Right')), 
                      0,
                      self.editorActGrp, 'vm_edit_extend_rect_selection_right_char')
        self.esm.setMapping(act, QsciScintilla.SCI_CHARRIGHTRECTEXTEND)
        self.connect(act, SIGNAL('triggered()'), self.esm, SLOT('map()'))
        self.editActions.append(act)
        
        act = E4Action(QApplication.translate('ViewManager', 
                        'Extend rectangular selection to first'
                        ' visible character in line'), 
                      QApplication.translate('ViewManager', 
                        'Extend rectangular selection to first'
                        ' visible character in line'), 
                      QKeySequence(QApplication.translate('ViewManager', 
                        'Alt+Ctrl+Home')), 
                      0,
                      self.editorActGrp, 
                      'vm_edit_extend_rect_selection_first_visible_char')
        self.esm.setMapping(act, QsciScintilla.SCI_VCHOMERECTEXTEND)
        self.connect(act, SIGNAL('triggered()'), self.esm, SLOT('map()'))
        self.editActions.append(act)
        
        act = E4Action(QApplication.translate('ViewManager', 
                        'Extend rectangular selection to end of line'), 
                      QApplication.translate('ViewManager', 
                        'Extend rectangular selection to end of line'), 
                      QKeySequence(QApplication.translate('ViewManager', 'Alt+Ctrl+End')),
                      0,
                      self.editorActGrp, 'vm_edit_extend_rect_selection_end_line')
        self.esm.setMapping(act, QsciScintilla.SCI_LINEENDRECTEXTEND)
        self.connect(act, SIGNAL('triggered()'), self.esm, SLOT('map()'))
        self.editActions.append(act)
        
        act = E4Action(QApplication.translate('ViewManager', 
                        'Extend rectangular selection up one page'), 
                      QApplication.translate('ViewManager', 
                        'Extend rectangular selection up one page'), 
                      QKeySequence(QApplication.translate('ViewManager', 
                        'Alt+Ctrl+PgUp')), 
                      0,
                      self.editorActGrp, 'vm_edit_extend_rect_selection_up_page')
        self.esm.setMapping(act, QsciScintilla.SCI_PAGEUPRECTEXTEND)
        self.connect(act, SIGNAL('triggered()'), self.esm, SLOT('map()'))
        self.editActions.append(act)
        
        act = E4Action(QApplication.translate('ViewManager', 
                        'Extend rectangular selection down one page'), 
                      QApplication.translate('ViewManager', 
                        'Extend rectangular selection down one page'), 
                      QKeySequence(QApplication.translate('ViewManager', 
                        'Alt+Ctrl+PgDown')), 
                      0,
                      self.editorActGrp, 'vm_edit_extend_rect_selection_down_page')
        self.esm.setMapping(act, QsciScintilla.SCI_PAGEDOWNRECTEXTEND)
        self.connect(act, SIGNAL('triggered()'), self.esm, SLOT('map()'))
        self.editActions.append(act)
        
        act = E4Action(QApplication.translate('ViewManager', 
                        'Duplicate current selection'), 
                      QApplication.translate('ViewManager', 
                        'Duplicate current selection'), 
                      QKeySequence(QApplication.translate('ViewManager', 'Ctrl+Shift+D')),
                      0,
                      self.editorActGrp, 'vm_edit_duplicate_current_selection')
        self.esm.setMapping(act, QsciScintilla.SCI_SELECTIONDUPLICATE)
        self.connect(act, SIGNAL('triggered()'), self.esm, SLOT('map()'))
        self.editActions.append(act)
        
        self.__textEdit.addActions(self.editorActGrp.actions())
    
    def __createSearchActions(self):
        """
        Private method defining the user interface actions for the search commands.
        """
        self.searchAct = E4Action(QApplication.translate('ViewManager', 'Search'),
                UI.PixmapCache.getIcon("find.png"),
                QApplication.translate('ViewManager', '&Search...'),
                QKeySequence(QApplication.translate('ViewManager', 
                    "Ctrl+F", "Search|Search")), 
                0,
                self, 'vm_search')
        self.searchAct.setStatusTip(QApplication.translate('ViewManager', 
            'Search for a text'))
        self.searchAct.setWhatsThis(QApplication.translate('ViewManager', 
            """<b>Search</b>"""
            """<p>Search for some text in the current editor. A"""
            """ dialog is shown to enter the searchtext and options"""
            """ for the search.</p>"""
        ))
        self.connect(self.searchAct, SIGNAL('triggered()'), self.__search)
        self.searchActions.append(self.searchAct)
        
        self.searchNextAct = E4Action(QApplication.translate('ViewManager', 
                    'Search next'),
                UI.PixmapCache.getIcon("findNext.png"),
                QApplication.translate('ViewManager', 'Search &next'),
                QKeySequence(QApplication.translate('ViewManager', 
                    "F3", "Search|Search next")), 
                0,
                self, 'vm_search_next')
        self.searchNextAct.setStatusTip(QApplication.translate('ViewManager', 
            'Search next occurrence of text'))
        self.searchNextAct.setWhatsThis(QApplication.translate('ViewManager', 
            """<b>Search next</b>"""
            """<p>Search the next occurrence of some text in the current editor."""
            """ The previously entered searchtext and options are reused.</p>"""
        ))
        self.connect(self.searchNextAct, SIGNAL('triggered()'), self.searchDlg.findNext)
        self.searchActions.append(self.searchNextAct)
        
        self.searchPrevAct = E4Action(QApplication.translate('ViewManager', 
                    'Search previous'),
                UI.PixmapCache.getIcon("findPrev.png"),
                QApplication.translate('ViewManager', 'Search &previous'),
                QKeySequence(QApplication.translate('ViewManager', 
                    "Shift+F3", "Search|Search previous")), 
                0,
                self, 'vm_search_previous')
        self.searchPrevAct.setStatusTip(QApplication.translate('ViewManager', 
            'Search previous occurrence of text'))
        self.searchPrevAct.setWhatsThis(QApplication.translate('ViewManager', 
            """<b>Search previous</b>"""
            """<p>Search the previous occurrence of some text in the current editor."""
            """ The previously entered searchtext and options are reused.</p>"""
        ))
        self.connect(self.searchPrevAct, SIGNAL('triggered()'), self.searchDlg.findPrev)
        self.searchActions.append(self.searchPrevAct)
        
        self.searchClearMarkersAct = E4Action(QApplication.translate('ViewManager', 
                    'Clear search markers'),
                UI.PixmapCache.getIcon("findClear.png"),
                QApplication.translate('ViewManager', 'Clear search markers'),
                QKeySequence(QApplication.translate('ViewManager', 
                    "Ctrl+3", "Search|Clear search markers")), 
                0,
                self, 'vm_clear_search_markers')
        self.searchClearMarkersAct.setStatusTip(QApplication.translate('ViewManager', 
            'Clear all displayed search markers'))
        self.searchClearMarkersAct.setWhatsThis(QApplication.translate('ViewManager', 
            """<b>Clear search markers</b>"""
            """<p>Clear all displayed search markers.</p>"""
        ))
        self.connect(self.searchClearMarkersAct, SIGNAL('triggered()'), 
            self.__searchClearMarkers)
        self.searchActions.append(self.searchClearMarkersAct)
        
        self.replaceAct = E4Action(QApplication.translate('ViewManager', 'Replace'),
                QApplication.translate('ViewManager', '&Replace...'),
                QKeySequence(QApplication.translate('ViewManager', 
                    "Ctrl+R", "Search|Replace")), 
                0,
                self, 'vm_search_replace')
        self.replaceAct.setStatusTip(QApplication.translate('ViewManager', 
            'Replace some text'))
        self.replaceAct.setWhatsThis(QApplication.translate('ViewManager', 
            """<b>Replace</b>"""
            """<p>Search for some text in the current editor and replace it. A"""
            """ dialog is shown to enter the searchtext, the replacement text"""
            """ and options for the search and replace.</p>"""
        ))
        self.connect(self.replaceAct, SIGNAL('triggered()'), self.__replace)
        self.searchActions.append(self.replaceAct)
    
    def __createHelpActions(self):
        """
        Private method to create the Help actions.
        """
        self.aboutAct = E4Action(self.trUtf8('About'),
                self.trUtf8('&About'),
                0, 0, self, 'about_eric')
        self.aboutAct.setStatusTip(self.trUtf8('Display information about this software'))
        self.aboutAct.setWhatsThis(self.trUtf8(
            """<b>About</b>"""
            """<p>Display some information about this software.</p>"""))
        self.connect(self.aboutAct, SIGNAL('triggered()'), self.__about)
        self.helpActions.append(self.aboutAct)
        
        self.aboutQtAct = E4Action(self.trUtf8('About Qt'),
                self.trUtf8('About &Qt'), 0, 0, self, 'about_qt')
        self.aboutQtAct.setStatusTip(\
            self.trUtf8('Display information about the Qt toolkit'))
        self.aboutQtAct.setWhatsThis(self.trUtf8(
            """<b>About Qt</b>"""
            """<p>Display some information about the Qt toolkit.</p>"""
        ))
        self.connect(self.aboutQtAct, SIGNAL('triggered()'), self.__aboutQt)
        self.helpActions.append(self.aboutQtAct)
        
        if KdeQt.isKDE():
            self.aboutKdeAct = E4Action(self.trUtf8('About KDE'),
                    self.trUtf8('About &KDE'), 0, 0, self, 'about_kde')
            self.aboutKdeAct.setStatusTip(self.trUtf8('Display information about KDE'))
            self.aboutKdeAct.setWhatsThis(self.trUtf8(
                """<b>About KDE</b>"""
                """<p>Display some information about KDE.</p>"""
            ))
            self.connect(self.aboutKdeAct, SIGNAL('triggered()'), self.__aboutKde)
            self.helpActions.append(self.aboutKdeAct)
        else:
            self.aboutKdeAct = None
        
        self.whatsThisAct = E4Action(self.trUtf8('What\'s This?'), 
            UI.PixmapCache.getIcon("whatsThis.png"),
            self.trUtf8('&What\'s This?'), 
            QKeySequence(self.trUtf8("Shift+F1","Help|What's This?'")), 
            0, self, 'help_help_whats_this')
        self.whatsThisAct.setStatusTip(self.trUtf8('Context sensitive help'))
        self.whatsThisAct.setWhatsThis(self.trUtf8(
                """<b>Display context sensitive help</b>"""
                """<p>In What's This? mode, the mouse cursor shows an arrow with a"""
                """ question mark, and you can click on the interface elements to get"""
                """ a short description of what they do and how to use them. In"""
                """ dialogs, this feature can be accessed using the context help button"""
                """ in the titlebar.</p>"""
        ))
        self.connect(self.whatsThisAct, SIGNAL('triggered()'), self.__whatsThis)
        self.helpActions.append(self.whatsThisAct)
    
    def __createMenus(self):
        """
        Private method to create the menus of the menu bar.
        """
        self.fileMenu = self.menuBar().addMenu(self.trUtf8("&File"))
        self.fileMenu.addAction(self.newAct)
        self.fileMenu.addAction(self.openAct)
        self.fileMenu.addAction(self.saveAct)
        self.fileMenu.addAction(self.saveAsAct)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.printPreviewAct)
        self.fileMenu.addAction(self.printAct)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.closeAct)
        
        self.editMenu = self.menuBar().addMenu(self.trUtf8("&Edit"));
        self.editMenu.addAction(self.undoAct)
        self.editMenu.addAction(self.redoAct)
        self.editMenu.addSeparator()
        self.editMenu.addAction(self.cutAct)
        self.editMenu.addAction(self.copyAct)
        self.editMenu.addAction(self.pasteAct)
        self.editMenu.addAction(self.deleteAct)
        self.editMenu.addSeparator()
        self.editMenu.addAction(self.searchAct)
        self.editMenu.addAction(self.searchNextAct)
        self.editMenu.addAction(self.searchPrevAct)
        self.editMenu.addAction(self.searchClearMarkersAct)
        self.editMenu.addAction(self.replaceAct)
        
        self.menuBar().addSeparator()
        
        self.helpMenu = self.menuBar().addMenu(self.trUtf8("&Help"))
        self.helpMenu.addAction(self.aboutAct)
        self.helpMenu.addAction(self.aboutQtAct)
        if self.aboutKdeAct is not None:
            self.helpMenu.addAction(self.aboutKdeAct)
        self.helpMenu.addSeparator()
        self.helpMenu.addAction(self.whatsThisAct)
        
        self.__initContextMenu()
    
    def __createToolBars(self):
        """
        Private method to create the various toolbars.
        """
        filetb = self.addToolBar(self.trUtf8("File"))
        filetb.setIconSize(UI.Config.ToolBarIconSize)
        filetb.addAction(self.newAct)
        filetb.addAction(self.openAct)
        filetb.addAction(self.saveAct)
        filetb.addAction(self.saveAsAct)
        filetb.addSeparator()
        filetb.addAction(self.printPreviewAct)
        filetb.addAction(self.printAct)
        filetb.addSeparator()
        filetb.addAction(self.closeAct)
        
        edittb = self.addToolBar(self.trUtf8("Edit"))
        edittb.setIconSize(UI.Config.ToolBarIconSize)
        edittb.addAction(self.undoAct)
        edittb.addAction(self.redoAct)
        edittb.addSeparator()
        edittb.addAction(self.cutAct)
        edittb.addAction(self.copyAct)
        edittb.addAction(self.pasteAct)
        edittb.addAction(self.deleteAct)
        
        findtb = self.addToolBar(self.trUtf8("Find"))
        findtb.setIconSize(UI.Config.ToolBarIconSize)
        findtb.addAction(self.searchAct)
        findtb.addAction(self.searchNextAct)
        findtb.addAction(self.searchPrevAct)
        findtb.addAction(self.searchClearMarkersAct)
        
        helptb = self.addToolBar(self.trUtf8("Help"))
        helptb.setIconSize(UI.Config.ToolBarIconSize)
        helptb.addAction(self.whatsThisAct)
    
    def __createStatusBar(self):
        """
        Private method to initialize the status bar.
        """
        self.__statusBar = self.statusBar()
        self.__statusBar.setSizeGripEnabled(True)

        self.sbWritable = QLabel(self.__statusBar)
        self.__statusBar.addPermanentWidget(self.sbWritable)
        self.sbWritable.setWhatsThis(self.trUtf8(
            """<p>This part of the status bar displays an indication of the"""
            """ editors files writability.</p>"""
        ))

        self.sbLine = QLabel(self.__statusBar)
        self.__statusBar.addPermanentWidget(self.sbLine)
        self.sbLine.setWhatsThis(self.trUtf8(
            """<p>This part of the status bar displays the line number of the"""
            """ editor.</p>"""
        ))

        self.sbPos = QLabel(self.__statusBar)
        self.__statusBar.addPermanentWidget(self.sbPos)
        self.sbPos.setWhatsThis(self.trUtf8(
            """<p>This part of the status bar displays the cursor position of"""
            """ the editor.</p>"""
        ))
        
        self.__statusBar.showMessage(self.trUtf8("Ready"))
    
    def __readSettings(self):
        """
        Private method to read the settings remembered last time.
        """
        settings = Preferences.Prefs.settings
        pos = settings.value("MiniEditor/Position", QVariant(QPoint(0, 0))).toPoint()
        size = settings.value("MiniEditor/Size", QVariant(QSize(800, 600))).toSize()
        self.resize(size)
        self.move(pos)
    
    def __writeSettings(self):
        """
        Private method to write the settings for reuse.
        """
        settings = Preferences.Prefs.settings
        settings.setValue("MiniEditor/Position", QVariant(self.pos()))
        settings.setValue("MiniEditor/Size", QVariant(self.size()))
    
    def __maybeSave(self):
        """
        Private method to ask the user to save the file, if it was modified.
        
        @return flag indicating, if it is ok to continue (boolean)
        """
        if self.__textEdit.isModified():
            ret = KQMessageBox.warning(self, 
                    self.trUtf8("eric4 Mini Editor"),
                    self.trUtf8("The document has been modified.\n"
                            "Do you want to save your changes?"),
                    QMessageBox.StandardButtons(\
                        QMessageBox.Cancel | \
                        QMessageBox.No | \
                        QMessageBox.Yes),
                    QMessageBox.Cancel)
            if ret == QMessageBox.Yes:
                return self.__save()
            elif ret == QMessageBox.Cancel:
                return False
        return True
    
    def __loadFile(self, fileName, filetype = None):
        """
        Private method to load the given file.
        
        @param fileName name of the file to load (QString)
        @param filetype type of the source file (string)
        """
        file= QFile(fileName)
        if not file.open(QFile.ReadOnly):
            KQMessageBox.warning(self, self.trUtf8("eric4 Mini Editor"),
                                 self.trUtf8("Cannot read file %1:\n%2.")\
                                    .arg(fileName)\
                                    .arg(file.errorString()))
            return
        
        input = QTextStream(file)
        QApplication.setOverrideCursor(Qt.WaitCursor)
        txt = input.readAll()
        self.__textEdit.setText(txt)
        QApplication.restoreOverrideCursor()
        
        if filetype is None:
            self.filetype = ""
        else:
            self.filetype = filetype
        self.__setCurrentFile(fileName)
        
        fileEol = self.__textEdit.detectEolString(txt)
        self.__textEdit.setEolModeByEolString(fileEol)
        
        self.__statusBar.showMessage(self.trUtf8("File loaded"), 2000)

    def __saveFile(self, fileName):
        """
        Private method to save to the given file.
        
        @param fileName name of the file to save to (QString)
        @return flag indicating success (boolean)
        """
        file = QFile(fileName)
        if not file.open(QFile.WriteOnly):
            KQMessageBox.warning(self, self.trUtf8("eric4 Mini Editor"),
                                 self.trUtf8("Cannot write file %1:\n%2.")\
                                 .arg(fileName)\
                                 .arg(file.errorString()))
        
            self.__checkActions()
            
            return False
        
        out = QTextStream(file)
        QApplication.setOverrideCursor(Qt.WaitCursor)
        out << self.__textEdit.text()
        QApplication.restoreOverrideCursor()
        self.emit(SIGNAL("editorSaved"))
        
        self.__setCurrentFile(fileName)
        self.__statusBar.showMessage(self.trUtf8("File saved"), 2000)
        
        self.__checkActions()
        
        return True

    def __setCurrentFile(self, fileName):
        """
        Private method to register the file name of the current file.
        
        @param fileName name of the file to register (string or QString)
        """
        self.__curFile = QString(fileName)
        
        if self.__curFile.isEmpty():
            shownName = self.trUtf8("Untitled")
        else:
            shownName = self.__strippedName(self.__curFile)
        
        self.setWindowTitle(self.trUtf8("%1[*] - %2")\
                            .arg(shownName)\
                            .arg(self.trUtf8("Mini Editor")))
        
        self.__textEdit.setModified(False)
        self.setWindowModified(False)
        
        try:
            line0 = self.readLine0(self.__curFile)
        except IOError:
            line0 = ""
        self.setLanguage(self.__bindName(line0))

    def getFileName(self):
        """
        Public method to return the name of the file being displayed.
        
        @return filename of the displayed file (string)
        """
        return unicode(self.__curFile)
    
    def __strippedName(self, fullFileName):
        """
        Private method to return the filename part of the given path.
        
        @param fullFileName full pathname of the given file (QString)
        @return filename part (QString)
        """
        return QFileInfo(fullFileName).fileName()

    def __modificationChanged(self, m):
        """
        Private slot to handle the modificationChanged signal. 
        
        @param m modification status
        """
        self.setWindowModified(m)
        self.__checkActions()
    
    def __cursorPositionChanged(self, line, pos):
        """
        Private slot to handle the cursorPositionChanged signal. 
        
        @param line line number of the cursor
        @param pos position in line of the cursor
        """
        self.__setSbFile(line + 1, pos)
        
        if Preferences.getEditor("MarkOccurrencesEnabled"):
            self.__markOccurrencesTimer.stop()
            self.__markOccurrencesTimer.start()
    
    def __undo(self):
        """
        Public method to undo the last recorded change.
        """
        self.__textEdit.undo()
        self.__checkActions()
    
    def __redo(self):
        """
        Public method to redo the last recorded change.
        """
        self.__textEdit.redo()
        self.__checkActions()
    
    def __selectAll(self):
        """
        Private slot handling the select all context menu action.
        """
        self.__textEdit.selectAll(True)
    
    def __deselectAll(self):
        """
        Private slot handling the deselect all context menu action.
        """
        self.__textEdit.selectAll(False)
    
    def __setMargins(self):
        """
        Private method to configure the margins.
        """
        # set the settings for all margins
        self.__textEdit.setMarginsFont(Preferences.getEditorOtherFonts("MarginsFont"))
        self.__textEdit.setMarginsForegroundColor(
            Preferences.getEditorColour("MarginsForeground"))
        self.__textEdit.setMarginsBackgroundColor(
            Preferences.getEditorColour("MarginsBackground"))
        
        # set margin 0 settings
        linenoMargin = Preferences.getEditor("LinenoMargin")
        self.__textEdit.setMarginLineNumbers(0, linenoMargin)
        if linenoMargin:
            self.__textEdit.setMarginWidth(0, 
                ' ' + '8' * Preferences.getEditor("LinenoWidth"))
        else:
            self.__textEdit.setMarginWidth(0, 16)
        
        # set margin 1 settings
        self.__textEdit.setMarginWidth(1, 0)
        
        # set margin 2 settings
        self.__textEdit.setMarginWidth(2, 16)
        if Preferences.getEditor("FoldingMargin"):
            folding = Preferences.getEditor("FoldingStyle")
            try:
                folding = QsciScintilla.FoldStyle(folding)
            except AttributeError:
                pass
            self.__textEdit.setFolding(folding)
            self.__textEdit.setFoldMarginColors(
                Preferences.getEditorColour("FoldmarginBackground"), 
                Preferences.getEditorColour("FoldmarginBackground"))
        else:
            self.__textEdit.setFolding(QsciScintilla.NoFoldStyle)
    
    def __setTextDisplay(self):
        """
        Private method to configure the text display.
        """
        self.__textEdit.setTabWidth(Preferences.getEditor("TabWidth"))
        self.__textEdit.setIndentationWidth(Preferences.getEditor("IndentWidth"))
        if self.lexer_ and self.lexer_.alwaysKeepTabs():
            self.__textEdit.setIndentationsUseTabs(True)
        else:
            self.__textEdit.setIndentationsUseTabs(\
                Preferences.getEditor("TabForIndentation"))
        self.__textEdit.setTabIndents(Preferences.getEditor("TabIndents"))
        self.__textEdit.setBackspaceUnindents(Preferences.getEditor("TabIndents"))
        self.__textEdit.setIndentationGuides(Preferences.getEditor("IndentationGuides"))
        if Preferences.getEditor("ShowWhitespace"):
            self.__textEdit.setWhitespaceVisibility(QsciScintilla.WsVisible)
        else:
            self.__textEdit.setWhitespaceVisibility(QsciScintilla.WsInvisible)
        self.__textEdit.setEolVisibility(Preferences.getEditor("ShowEOL"))
        self.__textEdit.setAutoIndent(Preferences.getEditor("AutoIndentation"))
        if Preferences.getEditor("BraceHighlighting"):
            self.__textEdit.setBraceMatching(QsciScintilla.SloppyBraceMatch)
        else:
            self.__textEdit.setBraceMatching(QsciScintilla.NoBraceMatch)
        self.__textEdit.setMatchedBraceForegroundColor(
            Preferences.getEditorColour("MatchingBrace"))
        self.__textEdit.setMatchedBraceBackgroundColor(
            Preferences.getEditorColour("MatchingBraceBack"))
        self.__textEdit.setUnmatchedBraceForegroundColor(
            Preferences.getEditorColour("NonmatchingBrace"))
        self.__textEdit.setUnmatchedBraceBackgroundColor(
            Preferences.getEditorColour("NonmatchingBraceBack"))
        if Preferences.getEditor("CustomSelectionColours"):
            self.__textEdit.setSelectionBackgroundColor(\
                Preferences.getEditorColour("SelectionBackground"))
        else:
            self.__textEdit.setSelectionBackgroundColor(\
                QApplication.palette().color(QPalette.Highlight))
        if Preferences.getEditor("ColourizeSelText"):
            self.__textEdit.resetSelectionForegroundColor()
        elif Preferences.getEditor("CustomSelectionColours"):
            self.__textEdit.setSelectionForegroundColor(\
                Preferences.getEditorColour("SelectionForeground"))
        else:
            self.__textEdit.setSelectionForegroundColor(\
                QApplication.palette().color(QPalette.HighlightedText))
        self.__textEdit.setSelectionToEol(Preferences.getEditor("ExtendSelectionToEol"))
        self.__textEdit.setCaretForegroundColor(
            Preferences.getEditorColour("CaretForeground"))
        self.__textEdit.setCaretLineBackgroundColor(
            Preferences.getEditorColour("CaretLineBackground"))
        self.__textEdit.setCaretLineVisible(Preferences.getEditor("CaretLineVisible"))
        self.caretWidth = Preferences.getEditor("CaretWidth")
        self.__textEdit.setCaretWidth(self.caretWidth)
        self.useMonospaced = Preferences.getEditor("UseMonospacedFont")
        self.__setMonospaced(self.useMonospaced)
        edgeMode = Preferences.getEditor("EdgeMode")
        edge = QsciScintilla.EdgeMode(edgeMode)
        self.__textEdit.setEdgeMode(edge)
        if edgeMode:
            self.__textEdit.setEdgeColumn(Preferences.getEditor("EdgeColumn"))
            self.__textEdit.setEdgeColor(Preferences.getEditorColour("Edge"))
        
        if Preferences.getEditor("WrapLongLines"):
            self.__textEdit.setWrapMode(QsciScintilla.WrapWord)
            self.__textEdit.setWrapVisualFlags(\
                QsciScintilla.WrapFlagByBorder, QsciScintilla.WrapFlagByBorder)
        else:
            self.__textEdit.setWrapMode(QsciScintilla.WrapNone)
            self.__textEdit.setWrapVisualFlags(\
                QsciScintilla.WrapFlagNone, QsciScintilla.WrapFlagNone)
        
        self.searchIndicator = QsciScintilla.INDIC_CONTAINER
        self.__textEdit.indicatorDefine(self.searchIndicator, QsciScintilla.INDIC_BOX, 
            Preferences.getEditorColour("SearchMarkers"))
    
    def __setEolMode(self):
        """
        Private method to configure the eol mode of the editor.
        """
        eolMode = Preferences.getEditor("EOLMode")
        eolMode = QsciScintilla.EolMode(eolMode)
        self.__textEdit.setEolMode(eolMode)
        
    def __setMonospaced(self, on):
        """
        Private method to set/reset a monospaced font.
        
        @param on flag to indicate usage of a monospace font (boolean)
        """
        if on:
            f = Preferences.getEditorOtherFonts("MonospacedFont")
            self.__textEdit.monospacedStyles(f)
        else:
            if not self.lexer_:
                self.__textEdit.clearStyles()
                self.__setMargins()
            self.__textEdit.setFont(Preferences.getEditorOtherFonts("DefaultFont"))
        
        self.useMonospaced = on
    
    def __printFile(self):
        """
        Private slot to print the text.
        """
        printer = Printer(mode = QPrinter.HighResolution)
        sb = self.statusBar()
        printDialog = KQPrintDialog(printer, self)
        if self.__textEdit.hasSelectedText():
            printDialog.addEnabledOption(QAbstractPrintDialog.PrintSelection)
        if printDialog.exec_() == QDialog.Accepted:
            sb.showMessage(self.trUtf8('Printing...'))
            QApplication.processEvents()
            if not self.__curFile.isEmpty():
                printer.setDocName(QFileInfo(self.__curFile).fileName())
            else:
                printer.setDocName(self.trUtf8("Untitled"))
            if printDialog.printRange() == QAbstractPrintDialog.Selection:
                # get the selection
                fromLine, fromIndex, toLine, toIndex = self.__textEdit.getSelection()
                if toIndex == 0:
                    toLine -= 1
                # Qscintilla seems to print one line more than told
                res = printer.printRange(self.__textEdit, fromLine, toLine-1)
            else:
                res = printer.printRange(self.__textEdit)
            if res:
                sb.showMessage(self.trUtf8('Printing completed'), 2000)
            else:
                sb.showMessage(self.trUtf8('Error while printing'), 2000)
            QApplication.processEvents()
        else:
            sb.showMessage(self.trUtf8('Printing aborted'), 2000)
            QApplication.processEvents()
    
    def __printPreviewFile(self):
        """
        Private slot to show a print preview of the text.
        """
        from PyQt4.QtGui import QPrintPreviewDialog
        
        printer = Printer(mode = QPrinter.HighResolution)
        if not self.__curFile.isEmpty():
            printer.setDocName(QFileInfo(self.__curFile).fileName())
        else:
            printer.setDocName(self.trUtf8("Untitled"))
        preview = QPrintPreviewDialog(printer, self)
        self.connect(preview, SIGNAL("paintRequested(QPrinter*)"), self.__printPreview)
        preview.exec_()
    
    def __printPreview(self, printer):
        """
        Private slot to generate a print preview.
        
        @param printer reference to the printer object (QScintilla.Printer.Printer)
        """
        printer.printRange(self.__textEdit)
    
    #########################################################
    ## Methods needed by the context menu
    #########################################################
    
    def __contextMenuRequested(self, coord):
        """
        Private slot to show the context menu.
        
        @param coord the position of the mouse pointer (QPoint)
        """
        self.contextMenu.popup(self.mapToGlobal(coord))
    
    def __initContextMenu(self):
        """
        Private method used to setup the context menu
        """
        self.contextMenu = QMenu()
        
        self.languagesMenu = self.__initContextMenuLanguages()
        
        self.contextMenu.addAction(self.undoAct)
        self.contextMenu.addAction(self.redoAct)
        self.contextMenu.addSeparator()
        self.contextMenu.addAction(self.cutAct)
        self.contextMenu.addAction(self.copyAct)
        self.contextMenu.addAction(self.pasteAct)
        self.contextMenu.addSeparator()
        self.contextMenu.addAction(self.trUtf8('Select all'), self.__selectAll)
        self.contextMenu.addAction(self.trUtf8('Deselect all'), self.__deselectAll)
        self.contextMenu.addSeparator()
        self.languagesMenuAct = self.contextMenu.addMenu(self.languagesMenu)
        self.contextMenu.addSeparator()
        self.contextMenu.addAction(self.printPreviewAct)
        self.contextMenu.addAction(self.printAct)
    
    def __initContextMenuLanguages(self):
        """
        Private method used to setup the Languages context sub menu.
        """
        menu = QMenu(self.trUtf8("Languages"))
        
        self.languagesActGrp = QActionGroup(self)
        self.noLanguageAct = menu.addAction(self.trUtf8("No Language"))
        self.noLanguageAct.setCheckable(True)
        self.noLanguageAct.setData(QVariant("None"))
        self.languagesActGrp.addAction(self.noLanguageAct)
        menu.addSeparator()
        
        self.supportedLanguages = {}
        supportedLanguages = Lexers.getSupportedLanguages()
        languages = supportedLanguages.keys()
        languages.sort()
        for language in languages:
            if language != "Guessed":
                self.supportedLanguages[language] = supportedLanguages[language][:]
                act = menu.addAction(self.supportedLanguages[language][0])
                act.setCheckable(True)
                act.setData(QVariant(language))
                self.supportedLanguages[language].append(act)
                self.languagesActGrp.addAction(act)
        
        menu.addSeparator()
        self.pygmentsAct = menu.addAction(self.trUtf8("Guessed"))
        self.pygmentsAct.setCheckable(True)
        self.pygmentsAct.setData(QVariant("Guessed"))
        self.languagesActGrp.addAction(self.pygmentsAct)
        self.pygmentsSelAct = menu.addAction(self.trUtf8("Alternatives"))
        self.pygmentsSelAct.setData(QVariant("Alternatives"))
        
        self.connect(menu, SIGNAL('triggered(QAction *)'), self.__languageMenuTriggered)
        self.connect(menu, SIGNAL('aboutToShow()'), self.__showContextMenuLanguages)
        
        return menu
    
    def __showContextMenuLanguages(self):
        """
        Private slot handling the aboutToShow signal of the languages context menu.
        """
        if self.apiLanguage.startswith("Pygments|"):
            self.pygmentsSelAct.setText(
                self.trUtf8("Alternatives (%1)").arg(self.getLanguage()))
        else:
            self.pygmentsSelAct.setText(self.trUtf8("Alternatives"))
    
    def __selectPygmentsLexer(self):
        """
        Private method to select a specific pygments lexer.
        
        @return name of the selected pygments lexer (string)
        """
        from pygments.lexers import get_all_lexers
        lexerList = sorted([l[0] for l in get_all_lexers()])
        try:
            lexerSel = lexerList.index(self.getLanguage())
        except ValueError:
            lexerSel = 0
        lexerName, ok = KQInputDialog.getItem(\
            self,
            self.trUtf8("Pygments Lexer"),
            self.trUtf8("Select the Pygments lexer to apply."),
            lexerList,
            lexerSel, 
            False)
        if ok and not lexerName.isEmpty():
            return unicode(lexerName)
        else:
            return ""
    
    def __languageMenuTriggered(self, act):
        """
        Private method to handle the selection of a lexer language.
        
        @param act reference to the action that was triggered (QAction)
        """
        if act == self.noLanguageAct:
            self.__resetLanguage()
        elif act == self.pygmentsAct:
            self.setLanguage("dummy.pygments")
        elif act == self.pygmentsSelAct:
            language = self.__selectPygmentsLexer()
            if language:
                self.setLanguage("dummy.pygments", pyname = language)
        else:
            language = unicode(act.data().toString())
            if language:
                self.setLanguage(self.supportedLanguages[language][1])
        
    def __resetLanguage(self):
        """
        Private method used to reset the language selection.
        """
        if self.lexer_ is not None and \
           (self.lexer_.lexer() == "container" or self.lexer_.lexer() is None):
            self.disconnect(self.__textEdit, SIGNAL("SCN_STYLENEEDED(int)"), 
                            self.__styleNeeded)
        
        self.apiLanguage = ""
        self.lexer_ = None
        self.__textEdit.setLexer()
        self.__setMonospaced(self.useMonospaced)
        
    def setLanguage(self, filename, initTextDisplay = True, pyname = ""):
        """
        Public method to set a lexer language.
        
        @param filename filename used to determine the associated lexer language (string)
        @param initTextDisplay flag indicating an initialization of the text display
            is required as well (boolean)
        @keyparam pyname name of the pygments lexer to use (string)
        """
        self.__bindLexer(filename, pyname = pyname)
        self.__textEdit.recolor()
        self.__checkLanguage()
        
        # set the text display
        if initTextDisplay:
            self.__setTextDisplay()
            self.__setMargins()

    def getLanguage(self):
        """
        Public method to retrieve the language of the editor.
        
        @return language of the editor (QString)
        """
        if self.apiLanguage == "Guessed" or self.apiLanguage.startswith("Pygments|"):
            return QString(self.lexer_.name())
        else:
            return QString(self.apiLanguage)
    
    def __checkLanguage(self):
        """
        Private method to check the selected language of the language submenu.
        """
        if self.apiLanguage == "":
            self.noLanguageAct.setChecked(True)
        elif self.apiLanguage == "Guessed":
            self.pygmentsAct.setChecked(True)
        elif self.apiLanguage.startswith("Pygments|"):
            act = self.languagesActGrp.checkedAction()
            if act:
                act.setChecked(False)
        else:
            self.supportedLanguages[self.apiLanguage][2].setChecked(True)
    
    def __bindLexer(self, filename, pyname = ""):
        """
        Private slot to set the correct lexer depending on language.
        
        @param filename filename used to determine the associated lexer language
            (string or QString)
        @keyparam pyname name of the pygments lexer to use (string)
        """
        filename = unicode(filename)
        if self.lexer_ is not None and \
           (self.lexer_.lexer() == "container" or self.lexer_.lexer() is None):
            self.disconnect(self.__textEdit, SIGNAL("SCN_STYLENEEDED(int)"), 
                            self.__styleNeeded)
        
        filename = os.path.basename(unicode(filename))
        language = Preferences.getEditorLexerAssoc(filename)
        if language.startswith("Pygments|"):
            pyname = language.split("|", 1)[1]
            language = ""
        
        self.lexer_ = Lexers.getLexer(language, self.__textEdit, pyname = pyname)
        if self.lexer_ is None:
            self.__textEdit.setLexer()
            self.apiLanguage = ""
            return
        
        if pyname:
            self.apiLanguage = "Pygments|%s" % pyname
        else:
            self.apiLanguage = self.lexer_.language()
        self.__textEdit.setLexer(self.lexer_)
        if self.lexer_.lexer() == "container" or self.lexer_.lexer() is None:
            self.__textEdit.setStyleBits(self.lexer_.styleBitsNeeded())
            self.connect(self.__textEdit, SIGNAL("SCN_STYLENEEDED(int)"), 
                         self.__styleNeeded)
        
        # get the font for style 0 and set it as the default font
        key = 'Scintilla/%s/style0/font' % unicode(self.lexer_.language())
        fontVariant = Preferences.Prefs.settings.value(key)
        if fontVariant.isValid():
            fdesc = fontVariant.toStringList()
            font = QFont(fdesc[0], int(str(fdesc[1])))
            self.lexer_.setDefaultFont(font)
        self.lexer_.readSettings(Preferences.Prefs.settings, "Scintilla")
        
        # now set the lexer properties
        self.lexer_.initProperties()
        
        # initialize the auto indent style of the lexer
        ais = self.lexer_.autoIndentStyle()
        
    def __styleNeeded(self, position):
        """
        Private slot to handle the need for more styling.
        
        @param position end position, that needs styling (integer)
        """
        self.lexer_.styleText(self.__textEdit.getEndStyled(), position)
    
    def __bindName(self, txt):
        """
        Private method to generate a dummy filename for binding a lexer.
        
        @param txt first line of text to use in the generation process (QString or string)
        """
        line0 = QString(txt)
        bindName = self.__curFile
        
        if line0.startsWith("<?xml"):
            # override extension for XML files
            bindName = "dummy.xml"
        
        # check filetype
        if self.filetype == "Python":
            bindName = "dummy.py"
        elif self.filetype == "Ruby":
            bindName = "dummy.rb"
        elif self.filetype == "D":
            bindName = "dummy.d"
        elif self.filetype == "Properties":
            bindName = "dummy.ini"
        
        # #! marker detection
        if line0.startsWith("#!"):
            if line0.contains("python"):
                bindName = "dummy.py"
                self.filetype = "Python"
            elif (line0.contains("/bash") or line0.contains("/sh")):
                bindName = "dummy.sh"
            elif line0.contains("ruby"):
                bindName = "dummy.rb"
                self.filetype = "Ruby"
            elif line0.contains("perl"):
                bindName = "dummy.pl"
            elif line0.contains("lua"):
                bindName = "dummy.lua"
            elif line0.contains("dmd"):
                bindName = "dummy.d"
                self.filetype = "D"
        return bindName
    
    def readLine0(self, fn, createIt = False):
        """
        Public slot to read the first line from a file.
        
        @param fn filename to read from (string or QString)
        @param createIt flag indicating the creation of a new file, if the given
            one doesn't exist (boolean)
        @return first line of the file (string)
        """
        fn = unicode(fn)
        if not fn:
            return ""
        
        try:
            if createIt and not os.path.exists(fn):
                f = open(fn, "wb")
                f.close()
            f = open(fn, 'rb')
        except IOError:
            KQMessageBox.critical(self, self.trUtf8('Open File'),
                self.trUtf8('<p>The file <b>%1</b> could not be opened.</p>')
                    .arg(fn))
            raise
        
        txt = f.readline()
        f.close()
        return txt
    
    ##########################################################
    ## Methods needed for the search functionality
    ##########################################################
    
    def getSRHistory(self, key):
        """
        Public method to get the search or replace history list.
        
        @param key list to return (must be 'search' or 'replace')
        @return the requested history list (QStringList)
        """
        return self.srHistory[key]
    
    def textForFind(self):
        """
        Public method to determine the selection or the current word for the next 
        find operation.
        
        @return selection or current word (QString)
        """
        if self.__textEdit.hasSelectedText():
            text = self.__textEdit.selectedText()
            if text.contains('\r') or text.contains('\n'):
                # the selection contains at least a newline, it is
                # unlikely to be the expression to search for
                return QString('')
            
            return text
        
        # no selected text, determine the word at the current position
        return self.__getCurrentWord()
    
    def __getWord(self, line, index):
        """
        Private method to get the word at a position.
        
        @param line number of line to look at (int)
        @param index position to look at (int)
        @return the word at that position
        """
        text = self.__textEdit.text(line)
        if self.__textEdit.caseSensitive():
            cs = Qt.CaseSensitive
        else:
            cs = Qt.CaseInsensitive
        wc = self.__textEdit.wordCharacters()
        if wc is None:
            regExp = QRegExp('[^\w_]', cs)
        else:
            regExp = QRegExp('[^%s]' % re.escape(wc), cs)
        start = text.lastIndexOf(regExp, index) + 1
        end = text.indexOf(regExp, index)
        if start == end + 1 and index > 0:
            # we are on a word boundary, try again
            start = text.lastIndexOf(regExp, index - 1) + 1
        if start == -1:
            start = 0
        if end == -1:
            end = text.length()
        if end > start:
            word = text.mid(start, end - start)
        else:
            word = QString('')
        return word
    
    def __getCurrentWord(self):
        """
        Private method to get the word at the current position.
        
        @return the word at that current position
        """
        line, index = self.__textEdit.getCursorPosition()
        return self.__getWord(line, index)
    
    def __search(self):
        """
        Private method to handle the search action.
        """
        self.replaceDlg.close()
        self.searchDlg.show(self.textForFind())
    
    def __searchClearMarkers(self):
        """
        Private method to clear the search markers of the active window.
        """
        self.clearSearchIndicators()
    
    def __replace(self):
        """
        Private method to handle the replace action.
        """
        self.searchDlg.close()
        self.replaceDlg.show(self.textForFind())
    
    def activeWindow(self):
        """
        Public method to fulfill the ViewManager interface.
        
        @return reference to the text edit component (QsciScintillaCompat)
        """
        return self.__textEdit
    
    def setSearchIndicator(self, startPos, indicLength):
        """
        Public method to set a search indicator for the given range.
        
        @param startPos start position of the indicator (integer)
        @param indicLength length of the indicator (integer)
        """
        self.__textEdit.setIndicatorRange(self.searchIndicator, startPos, indicLength)
    
    def clearSearchIndicators(self):
        """
        Public method to clear all search indicators.
        """
        self.__textEdit.clearAllIndicators(self.searchIndicator)
        self.__markedText = QString()
    
    def __markOccurrences(self):
        """
        Private method to mark all occurrences of the current word.
        """
        word = self.__getCurrentWord()
        if word.isEmpty():
            self.clearSearchIndicators()
            return
        
        if self.__markedText == word:
            return
        
        self.clearSearchIndicators()
        ok = self.__textEdit.findFirstTarget(word, 
            False, self.__textEdit.caseSensitive(), True, 
            0, 0)
        while ok:
            tgtPos, tgtLen = self.__textEdit.getFoundTarget()
            self.setSearchIndicator(tgtPos, tgtLen)
            ok = self.__textEdit.findNextTarget()
        self.__markedText = word
    
    ##########################################################
    ## Methods exhibiting some QScintilla API methods
    ##########################################################
    
    def setText(self, txt, filetype = None):
        """
        Public method to set the text programatically.
        
        @param txt text to be set (string or QString)
        @param filetype type of the source file (string)
        """
        self.__textEdit.setText(txt)
        
        if filetype is None:
            self.filetype = ""
        else:
            self.filetype = filetype
        
        fileEol = self.__textEdit.detectEolString(txt)
        self.__textEdit.setEolModeByEolString(fileEol)
        
        self.__textEdit.setModified(False)
