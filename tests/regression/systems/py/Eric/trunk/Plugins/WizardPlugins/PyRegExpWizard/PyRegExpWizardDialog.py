# -*- coding: utf-8 -*-

# Copyright (c) 2004 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the Python re wizard dialog.
"""

import sys
import os
import re

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from KdeQt import KQMessageBox, KQInputDialog, KQFileDialog
from KdeQt.KQMainWindow import KQMainWindow

from Ui_PyRegExpWizardDialog import Ui_PyRegExpWizardDialog

from PyRegExpWizardRepeatDialog import PyRegExpWizardRepeatDialog
from PyRegExpWizardCharactersDialog import PyRegExpWizardCharactersDialog

import UI.PixmapCache

import Utilities

class PyRegExpWizardWidget(QWidget, Ui_PyRegExpWizardDialog):
    """
    Class implementing the Python re wizard dialog.
    """
    def __init__(self, parent = None, fromEric = True):
        """
        Constructor
        
        @param parent parent widget (QWidget)
        @param fromEric flag indicating a call from within eric4
        """
        QWidget.__init__(self,parent)
        self.setupUi(self)
        
        # initialize icons of the tool buttons
        self.commentButton.setIcon(UI.PixmapCache.getIcon("comment.png"))
        self.charButton.setIcon(UI.PixmapCache.getIcon("characters.png"))
        self.anycharButton.setIcon(UI.PixmapCache.getIcon("anychar.png"))
        self.repeatButton.setIcon(UI.PixmapCache.getIcon("repeat.png"))
        self.nonGroupButton.setIcon(UI.PixmapCache.getIcon("nongroup.png"))
        self.groupButton.setIcon(UI.PixmapCache.getIcon("group.png"))
        self.namedGroupButton.setIcon(UI.PixmapCache.getIcon("namedgroup.png"))
        self.namedReferenceButton.setIcon(UI.PixmapCache.getIcon("namedreference.png"))
        self.altnButton.setIcon(UI.PixmapCache.getIcon("altn.png"))
        self.beglineButton.setIcon(UI.PixmapCache.getIcon("begline.png"))
        self.endlineButton.setIcon(UI.PixmapCache.getIcon("endline.png"))
        self.wordboundButton.setIcon(UI.PixmapCache.getIcon("wordboundary.png"))
        self.nonwordboundButton.setIcon(UI.PixmapCache.getIcon("nonwordboundary.png"))
        self.poslookaheadButton.setIcon(UI.PixmapCache.getIcon("poslookahead.png"))
        self.neglookaheadButton.setIcon(UI.PixmapCache.getIcon("neglookahead.png"))
        self.poslookbehindButton.setIcon(UI.PixmapCache.getIcon("poslookbehind.png"))
        self.neglookbehindButton.setIcon(UI.PixmapCache.getIcon("neglookbehind.png"))
        self.undoButton.setIcon(UI.PixmapCache.getIcon("editUndo.png"))
        self.redoButton.setIcon(UI.PixmapCache.getIcon("editRedo.png"))
        
        self.namedGroups = re.compile(r"""\(?P<([^>]+)>""").findall
        
        self.saveButton = \
            self.buttonBox.addButton(self.trUtf8("Save"), QDialogButtonBox.ActionRole)
        self.saveButton.setToolTip(self.trUtf8("Save the regular expression to a file"))
        self.loadButton = \
            self.buttonBox.addButton(self.trUtf8("Load"), QDialogButtonBox.ActionRole)
        self.loadButton.setToolTip(self.trUtf8("Load a regular expression from a file"))
        self.validateButton = \
            self.buttonBox.addButton(self.trUtf8("Validate"), QDialogButtonBox.ActionRole)
        self.validateButton.setToolTip(self.trUtf8("Validate the regular expression"))
        self.executeButton = \
            self.buttonBox.addButton(self.trUtf8("Execute"), QDialogButtonBox.ActionRole)
        self.executeButton.setToolTip(self.trUtf8("Execute the regular expression"))
        self.nextButton = \
            self.buttonBox.addButton(self.trUtf8("Next match"), 
                                     QDialogButtonBox.ActionRole)
        self.nextButton.setToolTip(\
            self.trUtf8("Show the next match of the regular expression"))
        self.nextButton.setEnabled(False)
        
        if fromEric:
            self.buttonBox.button(QDialogButtonBox.Close).hide()
            self.copyButton = None
        else:
            self.copyButton = \
                self.buttonBox.addButton(self.trUtf8("Copy"), QDialogButtonBox.ActionRole)
            self.copyButton.setToolTip(\
                self.trUtf8("Copy the regular expression to the clipboard"))
            self.buttonBox.button(QDialogButtonBox.Ok).hide()
            self.buttonBox.button(QDialogButtonBox.Cancel).hide()
            self.variableLabel.hide()
            self.variableLineEdit.hide()
            self.variableLine.hide()
            self.importCheckBox.hide()
            self.regexpTextEdit.setFocus()

    def __insertString(self, s, steps = 0):
        """
        Private method to insert a string into line edit and move cursor.
        
        @param s string to be inserted into the regexp line edit
            (string or QString)
        @param steps number of characters to move the cursor (integer).
            Negative steps moves cursor back, positives forward.
        """
        self.regexpTextEdit.insertPlainText(s)
        tc = self.regexpTextEdit.textCursor()
        if steps != 0:
            if steps < 0:
                act = QTextCursor.Left
                steps = abs(steps)
            else:
                act = QTextCursor.Right
            for i in range(steps):
                tc.movePosition(act)
        self.regexpTextEdit.setTextCursor(tc)
        
    @pyqtSignature("")
    def on_commentButton_clicked(self):
        """
        Private slot to handle the comment toolbutton.
        """
        self.__insertString("(?#)", -1)
        
    @pyqtSignature("")
    def on_anycharButton_clicked(self):
        """
        Private slot to handle the any character toolbutton.
        """
        self.__insertString(".")
        
    @pyqtSignature("")
    def on_nonGroupButton_clicked(self):
        """
        Private slot to handle the non group toolbutton.
        """
        self.__insertString("(?:)", -1)
        
    @pyqtSignature("")
    def on_groupButton_clicked(self):
        """
        Private slot to handle the group toolbutton.
        """
        self.__insertString("()", -1)
        
    @pyqtSignature("")
    def on_namedGroupButton_clicked(self):
        """
        Private slot to handle the named group toolbutton.
        """
        self.__insertString("(?P<>)", -2)
        
    @pyqtSignature("")
    def on_namedReferenceButton_clicked(self):
        """
        Private slot to handle the named reference toolbutton.
        """
        # determine cursor position as length into text
        length = self.regexpTextEdit.textCursor().position()
        
        # only present group names that occur before the current cursor position
        regex = unicode(self.regexpTextEdit.toPlainText().left(length))
        names = self.namedGroups(regex)
        if not names:
            KQMessageBox.information(None,
                self.trUtf8("Named reference"),
                self.trUtf8("""No named groups have been defined yet."""))
            return
            
        qs = QStringList()
        for name in names:
            qs.append(name)
        groupName, ok = KQInputDialog.getItem(\
            None,
            self.trUtf8("Named reference"),
            self.trUtf8("Select group name:"),
            qs,
            0, True)
        if ok and not groupName.isEmpty():
            self.__insertString("(?P=%s)" % groupName)
        
    @pyqtSignature("")
    def on_altnButton_clicked(self):
        """
        Private slot to handle the alternatives toolbutton.
        """
        self.__insertString("(|)", -2)
        
    @pyqtSignature("")
    def on_beglineButton_clicked(self):
        """
        Private slot to handle the begin line toolbutton.
        """
        self.__insertString("^")
        
    @pyqtSignature("")
    def on_endlineButton_clicked(self):
        """
        Private slot to handle the end line toolbutton.
        """
        self.__insertString("$")
        
    @pyqtSignature("")
    def on_wordboundButton_clicked(self):
        """
        Private slot to handle the word boundary toolbutton.
        """
        self.__insertString("\\b")
        
    @pyqtSignature("")
    def on_nonwordboundButton_clicked(self):
        """
        Private slot to handle the non word boundary toolbutton.
        """
        self.__insertString("\\B")
        
    @pyqtSignature("")
    def on_poslookaheadButton_clicked(self):
        """
        Private slot to handle the positive lookahead toolbutton.
        """
        self.__insertString("(?=)", -1)
        
    @pyqtSignature("")
    def on_neglookaheadButton_clicked(self):
        """
        Private slot to handle the negative lookahead toolbutton.
        """
        self.__insertString("(?!)", -1)
        
    @pyqtSignature("")
    def on_poslookbehindButton_clicked(self):
        """
        Private slot to handle the positive lookbehind toolbutton.
        """
        self.__insertString("(?<=)", -1)
        
    @pyqtSignature("")
    def on_neglookbehindButton_clicked(self):
        """
        Private slot to handle the negative lookbehind toolbutton.
        """
        self.__insertString("(?<!)", -1)
        
    @pyqtSignature("")
    def on_repeatButton_clicked(self):
        """
        Private slot to handle the repeat toolbutton.
        """
        dlg = PyRegExpWizardRepeatDialog(self)
        if dlg.exec_() == QDialog.Accepted:
            self.__insertString(dlg.getRepeat())
        
    @pyqtSignature("")
    def on_charButton_clicked(self):
        """
        Private slot to handle the characters toolbutton.
        """
        dlg = PyRegExpWizardCharactersDialog(self)
        if dlg.exec_() == QDialog.Accepted:
            self.__insertString(dlg.getCharacters())
        
    @pyqtSignature("")
    def on_undoButton_clicked(self):
        """
        Private slot to handle the undo action.
        """
        self.regexpTextEdit.document().undo()
        
    @pyqtSignature("")
    def on_redoButton_clicked(self):
        """
        Private slot to handle the redo action.
        """
        self.regexpTextEdit.document().redo()
    
    def on_buttonBox_clicked(self, button):
        """
        Private slot called by a button of the button box clicked.
        
        @param button button that was clicked (QAbstractButton)
        """
        if button == self.validateButton:
            self.on_validateButton_clicked()
        elif button == self.executeButton:
            self.on_executeButton_clicked()
        elif button == self.saveButton:
            self.on_saveButton_clicked()
        elif button == self.loadButton:
            self.on_loadButton_clicked()
        elif button == self.nextButton:
            self.on_nextButton_clicked()
        elif self.copyButton and button == self.copyButton:
            self.on_copyButton_clicked()
    
    @pyqtSignature("")
    def on_saveButton_clicked(self):
        """
        Private slot to save the regexp to a file.
        """
        selectedFilter = QString("")
        fname = KQFileDialog.getSaveFileName(\
            self,
            self.trUtf8("Save regular expression"),
            QString(),
            self.trUtf8("RegExp Files (*.rx);;All Files (*)"),
            selectedFilter,
            QFileDialog.Options(QFileDialog.DontConfirmOverwrite))
        if not fname.isEmpty():
            ext = QFileInfo(fname).suffix()
            if ext.isEmpty():
                ex = selectedFilter.section('(*', 1, 1).section(')', 0, 0)
                if not ex.isEmpty():
                    fname.append(ex)
            if QFileInfo(fname).exists():
                res = KQMessageBox.warning(self,
                    self.trUtf8("Save regular expression"),
                    self.trUtf8("<p>The file <b>%1</b> already exists.</p>")
                        .arg(fname),
                    QMessageBox.StandardButtons(\
                        QMessageBox.Abort | \
                        QMessageBox.Save),
                    QMessageBox.Abort)
                if res == QMessageBox.Abort or res == QMessageBox.Cancel:
                    return
            
            try:
                f=open(unicode(Utilities.toNativeSeparators(fname)), "wb")
                f.write(unicode(self.regexpTextEdit.toPlainText()))
                f.close()
            except IOError, err:
                KQMessageBox.information(self,
                    self.trUtf8("Save regular expression"),
                    self.trUtf8("""<p>The regular expression could not be saved.</p>"""
                                """<p>Reason: %1</p>""").arg(unicode(err)))
    
    @pyqtSignature("")
    def on_loadButton_clicked(self):
        """
        Private slot to load a regexp from a file.
        """
        fname = KQFileDialog.getOpenFileName(\
            self,
            self.trUtf8("Load regular expression"),
            QString(),
            self.trUtf8("RegExp Files (*.rx);;All Files (*)"),
            None)
        if not fname.isEmpty():
            try:
                f=open(unicode(Utilities.toNativeSeparators(fname)), "rb")
                regexp = f.read()
                f.close()
                self.regexpTextEdit.setPlainText(regexp)
            except IOError, err:
                KQMessageBox.information(self,
                    self.trUtf8("Save regular expression"),
                    self.trUtf8("""<p>The regular expression could not be saved.</p>"""
                                """<p>Reason: %1</p>""").arg(unicode(err)))

    @pyqtSignature("")
    def on_copyButton_clicked(self):
        """
        Private slot to copy the regexp string into the clipboard.
        
        This slot is only available, if not called from within eric4.
        """
        escaped = self.regexpTextEdit.toPlainText()
        if not escaped.isEmpty():
            escaped = escaped.replace("\\", "\\\\")
            cb = QApplication.clipboard()
            cb.setText(escaped, QClipboard.Clipboard)
            if cb.supportsSelection():
                cb.setText(escaped, QClipboard.Selection)

    @pyqtSignature("")
    def on_validateButton_clicked(self):
        """
        Private slot to validate the entered regexp.
        """
        regex = self.regexpTextEdit.toPlainText()
        if not regex.isEmpty():
            try:
                if self.py2Button.isChecked():
                    regobj = re.compile(unicode(regex),
                        (not self.caseSensitiveCheckBox.isChecked() and re.IGNORECASE or 0) | \
                        self.multilineCheckBox.isChecked() and re.MULTILINE or 0 | \
                        self.dotallCheckBox.isChecked() and re.DOTALL or 0 | \
                        self.verboseCheckBox.isChecked() and re.VERBOSE or 0 | \
                        self.localeCheckBox.isChecked() and re.LOCALE or 0 | \
                        self.unicodeCheckBox.isChecked() and re.UNICODE or 0)
                else:
                    regobj = re.compile(unicode(regex),
                        (not self.caseSensitiveCheckBox.isChecked() and re.IGNORECASE or 0) | \
                        self.multilineCheckBox.isChecked() and re.MULTILINE or 0 | \
                        self.dotallCheckBox.isChecked() and re.DOTALL or 0 | \
                        self.verboseCheckBox.isChecked() and re.VERBOSE or 0 | \
                        (not self.unicodeCheckBox.isChecked() and re.UNICODE or 0))
                KQMessageBox.information(None,
                    self.trUtf8(""),
                    self.trUtf8("""The regular expression is valid."""))
            except re.error, e:
                KQMessageBox.critical(None,
                    self.trUtf8("Error"),
                    self.trUtf8("""Invalid regular expression: %1""")
                        .arg(unicode(e)))
                return
            except IndexError:
                KQMessageBox.critical(None,
                    self.trUtf8("Error"),
                    self.trUtf8("""Invalid regular expression: missing group name"""))
                return
        else:
            KQMessageBox.critical(None,
                self.trUtf8("Error"),
                self.trUtf8("""A regular expression must be given."""))

    @pyqtSignature("")
    def on_executeButton_clicked(self, startpos = 0):
        """
        Private slot to execute the entered regexp on the test text.
        
        This slot will execute the entered regexp on the entered test
        data and will display the result in the table part of the dialog.
        
        @param startpos starting position for the regexp matching
        """
        regex = self.regexpTextEdit.toPlainText()
        text = self.textTextEdit.toPlainText()
        if not regex.isEmpty() and not text.isEmpty():
            try:
                if self.py2Button.isChecked():
                    regobj = re.compile(unicode(regex),
                        (not self.caseSensitiveCheckBox.isChecked() and re.IGNORECASE or 0) | \
                        self.multilineCheckBox.isChecked() and re.MULTILINE or 0 | \
                        self.dotallCheckBox.isChecked() and re.DOTALL or 0 | \
                        self.verboseCheckBox.isChecked() and re.VERBOSE or 0 | \
                        self.localeCheckBox.isChecked() and re.LOCALE or 0 | \
                        self.unicodeCheckBox.isChecked() and re.UNICODE or 0)
                else:
                    regobj = re.compile(unicode(regex),
                        (not self.caseSensitiveCheckBox.isChecked() and re.IGNORECASE or 0) | \
                        self.multilineCheckBox.isChecked() and re.MULTILINE or 0 | \
                        self.dotallCheckBox.isChecked() and re.DOTALL or 0 | \
                        self.verboseCheckBox.isChecked() and re.VERBOSE or 0 | \
                        (not self.unicodeCheckBox.isChecked() and re.UNICODE or 0))
                matchobj = regobj.search(unicode(text), startpos)
                if matchobj is not None:
                    captures = len(matchobj.groups())
                    if captures is None:
                        captures = 0
                else:
                    captures = 0
                row = 0
                OFFSET = 5
                
                self.resultTable.setColumnCount(0)
                self.resultTable.setColumnCount(3)
                self.resultTable.setRowCount(0)
                self.resultTable.setRowCount(OFFSET)
                self.resultTable.setItem(row, 0, QTableWidgetItem(self.trUtf8("Regexp")))
                self.resultTable.setItem(row, 1, QTableWidgetItem(regex))
                
                if matchobj is not None:
                    offset = matchobj.start()
                    self.lastMatchEnd = matchobj.end()
                    self.nextButton.setEnabled(True)
                    row += 1
                    self.resultTable.setItem(row, 0, 
                        QTableWidgetItem(self.trUtf8("Offset")))
                    self.resultTable.setItem(row, 1, 
                        QTableWidgetItem(QString.number(matchobj.start(0))))
                    
                    row += 1
                    self.resultTable.setItem(row, 0, 
                        QTableWidgetItem(self.trUtf8("Captures")))
                    self.resultTable.setItem(row, 1, 
                        QTableWidgetItem(QString.number(captures)))
                    row += 1
                    self.resultTable.setItem(row, 1, 
                        QTableWidgetItem(self.trUtf8("Text")))
                    self.resultTable.setItem(row, 2, 
                        QTableWidgetItem(self.trUtf8("Characters")))
                    
                    row += 1
                    self.resultTable.setItem(row, 0, 
                        QTableWidgetItem(self.trUtf8("Match")))
                    self.resultTable.setItem(row, 1, 
                        QTableWidgetItem(matchobj.group(0)))
                    self.resultTable.setItem(row, 2, 
                        QTableWidgetItem(QString.number(len(matchobj.group(0)))))
                    
                    for i in range(1, captures + 1):
                        if matchobj.group(i) is not None:
                            row += 1
                            self.resultTable.insertRow(row)
                            self.resultTable.setItem(row, 0, 
                                QTableWidgetItem(self.trUtf8("Capture #%1").arg(i)))
                            self.resultTable.setItem(row, 1, 
                                QTableWidgetItem(matchobj.group(i)))
                            self.resultTable.setItem(row, 2, 
                                QTableWidgetItem(QString.number(len(matchobj.group(i)))))
                    
                    # highlight the matched text
                    tc = self.textTextEdit.textCursor()
                    tc.setPosition(offset)
                    tc.setPosition(self.lastMatchEnd, QTextCursor.KeepAnchor)
                    self.textTextEdit.setTextCursor(tc)
                else:
                    self.nextButton.setEnabled(False)
                    self.resultTable.setRowCount(2)
                    row += 1
                    if startpos > 0:
                        self.resultTable.setItem(row, 0, 
                            QTableWidgetItem(self.trUtf8("No more matches")))
                    else:
                        self.resultTable.setItem(row, 0, 
                            QTableWidgetItem(self.trUtf8("No matches")))
                    
                    # remove the highlight
                    tc = self.textTextEdit.textCursor()
                    tc.setPosition(0)
                    self.textTextEdit.setTextCursor(tc)
                
                self.resultTable.resizeColumnsToContents()
                self.resultTable.resizeRowsToContents()
                self.resultTable.verticalHeader().hide()
                self.resultTable.horizontalHeader().hide()
            except re.error, e:
                KQMessageBox.critical(None,
                    self.trUtf8("Error"),
                    self.trUtf8("""Invalid regular expression: %1""")
                        .arg(unicode(e)))
                return
            except IndexError:
                KQMessageBox.critical(None,
                    self.trUtf8("Error"),
                    self.trUtf8("""Invalid regular expression: missing group name"""))
                return
        else:
            KQMessageBox.critical(None,
                self.trUtf8("Error"),
                self.trUtf8("""A regular expression and a text must be given."""))
        
    @pyqtSignature("")
    def on_nextButton_clicked(self):
        """
        Private slot to find the next match.
        """
        self.on_executeButton_clicked(self.lastMatchEnd)
        
    @pyqtSignature("")
    def on_regexpTextEdit_textChanged(self):
        """
        Private slot called when the regexp changes.
        """
        self.nextButton.setEnabled(False)
        
    @pyqtSignature("bool")
    def on_py2Button_toggled(self, checked):
        """
        Private slot called when the Python version was selected.
        
        @param checked state of the Python 2 button (boolean)
        """
        # set the checkboxes
        self.localeCheckBox.setHidden(not checked)
        if checked:
            self.unicodeCheckBox.setText(self.trUtf8("Unicode"))
        else:
            self.unicodeCheckBox.setText(self.trUtf8("ASCII"))
        self.unicodeCheckBox.setChecked(not self.unicodeCheckBox.isChecked())
        
        # clear the result table
        self.resultTable.clear()
        self.resultTable.setColumnCount(0)
        self.resultTable.setRowCount(0)
        
        # remove the highlight
        tc = self.textTextEdit.textCursor()
        tc.setPosition(0)
        self.textTextEdit.setTextCursor(tc)
        
    def getCode(self, indLevel, indString):
        """
        Public method to get the source code.
        
        @param indLevel indentation level (int)
        @param indString string used for indentation (space or tab) (string)
        @return generated code (string)
        """
        # calculate the indentation string
        istring = indLevel * indString
        i1string = (indLevel + 1) * indString
        
        # now generate the code
        reVar = unicode(self.variableLineEdit.text())
        if not reVar:
            reVar = "regexp"
            
        regexp = unicode(self.regexpTextEdit.toPlainText())
        
        flags = []
        if not self.caseSensitiveCheckBox.isChecked():
            flags.append('re.IGNORECASE')
        if self.multilineCheckBox.isChecked():
            flags.append('re.MULTILINE')
        if self.dotallCheckBox.isChecked():
            flags.append('re.DOTALL')
        if self.verboseCheckBox.isChecked():
            flags.append('re.VERBOSE')
        if self.localeCheckBox.isChecked() and \
           self.py2Button.isChecked():
            flags.append('re.LOCALE')
        if self.unicodeCheckBox.isChecked():
            if self.py2Button.isChecked():
                flags.append('re.UNICODE')
            else:
                flags.append('re.ASCII')
        flags = " | ".join(flags)
        
        code = ''
        if self.importCheckBox.isChecked():
            code += 'import re%s%s' % (os.linesep, istring)
        code += '%s = re.compile(r"""%s"""' % \
            (reVar, regexp.replace('"', '\\"'))
        if flags:
            code += ', \\%s%s%s' % (os.linesep, i1string, flags)
        code += ')%s' % os.linesep
        return code

class PyRegExpWizardDialog(QDialog):
    """
    Class for the dialog variant.
    """
    def __init__(self, parent = None, fromEric = True):
        """
        Constructor
        
        @param parent parent widget (QWidget)
        @param fromEric flag indicating a call from within eric4
        """
        QDialog.__init__(self, parent)
        self.setModal(fromEric)
        self.setSizeGripEnabled(True)
        
        self.__layout = QVBoxLayout(self)
        self.__layout.setMargin(0)
        self.setLayout(self.__layout)
        
        self.cw = PyRegExpWizardWidget(self, fromEric)
        size = self.cw.size()
        self.__layout.addWidget(self.cw)
        self.resize(size)
        
        self.connect(self.cw.buttonBox, SIGNAL("accepted()"), self.accept)
        self.connect(self.cw.buttonBox, SIGNAL("rejected()"), self.reject)
    
    def getCode(self, indLevel, indString):
        """
        Public method to get the source code.
        
        @param indLevel indentation level (int)
        @param indString string used for indentation (space or tab) (string)
        @return generated code (string)
        """
        return self.cw.getCode(indLevel, indString)

class PyRegExpWizardWindow(KQMainWindow):
    """
    Main window class for the standalone dialog.
    """
    def __init__(self, parent = None):
        """
        Constructor
        
        @param parent reference to the parent widget (QWidget)
        """
        KQMainWindow.__init__(self, parent)
        self.cw = PyRegExpWizardWidget(self, fromEric = False)
        size = self.cw.size()
        self.setCentralWidget(self.cw)
        self.resize(size)
        
        self.connect(self.cw.buttonBox, SIGNAL("accepted()"), self.close)
        self.connect(self.cw.buttonBox, SIGNAL("rejected()"), self.close)
