# -*- coding: utf-8 -*-

# Copyright (c) 2004 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the QRegExp wizard dialog.
"""

import sys
import os

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from KdeQt import KQMessageBox, KQFileDialog
from KdeQt.KQMainWindow import KQMainWindow
from KdeQt.KQApplication import e4App

from Ui_QRegExpWizardDialog import Ui_QRegExpWizardDialog

from QRegExpWizardRepeatDialog import QRegExpWizardRepeatDialog
from QRegExpWizardCharactersDialog import QRegExpWizardCharactersDialog

import UI.PixmapCache

import Utilities

class QRegExpWizardWidget(QWidget, Ui_QRegExpWizardDialog):
    """
    Class implementing the QRegExp wizard dialog.
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
        self.charButton.setIcon(UI.PixmapCache.getIcon("characters.png"))
        self.anycharButton.setIcon(UI.PixmapCache.getIcon("anychar.png"))
        self.repeatButton.setIcon(UI.PixmapCache.getIcon("repeat.png"))
        self.nonGroupButton.setIcon(UI.PixmapCache.getIcon("nongroup.png"))
        self.groupButton.setIcon(UI.PixmapCache.getIcon("group.png"))
        self.altnButton.setIcon(UI.PixmapCache.getIcon("altn.png"))
        self.beglineButton.setIcon(UI.PixmapCache.getIcon("begline.png"))
        self.endlineButton.setIcon(UI.PixmapCache.getIcon("endline.png"))
        self.wordboundButton.setIcon(UI.PixmapCache.getIcon("wordboundary.png"))
        self.nonwordboundButton.setIcon(UI.PixmapCache.getIcon("nonwordboundary.png"))
        self.poslookaheadButton.setIcon(UI.PixmapCache.getIcon("poslookahead.png"))
        self.neglookaheadButton.setIcon(UI.PixmapCache.getIcon("neglookahead.png"))
        self.undoButton.setIcon(UI.PixmapCache.getIcon("editUndo.png"))
        self.redoButton.setIcon(UI.PixmapCache.getIcon("editRedo.png"))
        
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
            uitype = e4App().getObject("Project").getProjectType()
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
            self.regexpLineEdit.setFocus()

    def __insertString(self, s, steps=0):
        """
        Private method to insert a string into line edit and move cursor.
        
        @param s string to be inserted into the regexp line edit
            (string or QString)
        @param steps number of characters to move the cursor (integer).
            Negative steps moves cursor back, positives forward.
        """
        self.regexpLineEdit.insert(s)
        self.regexpLineEdit.cursorForward(False, steps)
        
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
    def on_repeatButton_clicked(self):
        """
        Private slot to handle the repeat toolbutton.
        """
        dlg = QRegExpWizardRepeatDialog(self)
        if dlg.exec_() == QDialog.Accepted:
            self.__insertString(dlg.getRepeat())
        
    @pyqtSignature("")
    def on_charButton_clicked(self):
        """
        Private slot to handle the characters toolbutton.
        """
        dlg = QRegExpWizardCharactersDialog(self)
        if dlg.exec_() == QDialog.Accepted:
            self.__insertString(dlg.getCharacters())
    
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
                f.write(unicode(self.regexpLineEdit.text()))
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
                self.regexpLineEdit.setText(regexp)
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
        escaped = self.regexpLineEdit.text()
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
        regex = self.regexpLineEdit.text()
        if not regex.isEmpty():
            re = QRegExp(regex)
            if self.caseSensitiveCheckBox.isChecked():
                re.setCaseSensitivity(Qt.CaseSensitive)
            else:
                re.setCaseSensitivity(Qt.CaseInsensitive)
            re.setMinimal(self.minimalCheckBox.isChecked())
            if self.wildcardCheckBox.isChecked():
                re.setPatternSyntax(QRegExp.Wildcard)
            else:
                re.setPatternSyntax(QRegExp.RegExp)
            if re.isValid():
                KQMessageBox.information(None,
                    self.trUtf8(""),
                    self.trUtf8("""The regular expression is valid."""))
            else:
                KQMessageBox.critical(None,
                    self.trUtf8("Error"),
                    self.trUtf8("""Invalid regular expression: %1""")
                        .arg(re.errorString()))
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
        regex = self.regexpLineEdit.text()
        text = self.textTextEdit.toPlainText()
        if not regex.isEmpty() and not text.isEmpty():
            re = QRegExp(regex)
            if self.caseSensitiveCheckBox.isChecked():
                re.setCaseSensitivity(Qt.CaseSensitive)
            else:
                re.setCaseSensitivity(Qt.CaseInsensitive)
            re.setMinimal(self.minimalCheckBox.isChecked())
            wildcard = self.wildcardCheckBox.isChecked()
            if wildcard:
                re.setPatternSyntax(QRegExp.Wildcard)
            else:
                re.setPatternSyntax(QRegExp.RegExp)
            if not re.isValid():
                KQMessageBox.critical(None,
                    self.trUtf8("Error"),
                    self.trUtf8("""Invalid regular expression: %1""")
                        .arg(re.errorString()))
                return
            offset = re.indexIn(text, startpos)
            captures = re.numCaptures()
            row = 0
            OFFSET = 5
            
            self.resultTable.setColumnCount(0)
            self.resultTable.setColumnCount(3)
            self.resultTable.setRowCount(0)
            self.resultTable.setRowCount(OFFSET)
            self.resultTable.setItem(row, 0, QTableWidgetItem(self.trUtf8("Regexp")))
            self.resultTable.setItem(row, 1, QTableWidgetItem(regex))
            
            if offset != -1:
                self.lastMatchEnd = offset + re.matchedLength()
                self.nextButton.setEnabled(True)
                row += 1
                self.resultTable.setItem(row, 0, QTableWidgetItem(self.trUtf8("Offset")))
                self.resultTable.setItem(row, 1, QTableWidgetItem(QString.number(offset)))
                
                if not wildcard:
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
                    QTableWidgetItem(re.cap(0)))
                self.resultTable.setItem(row, 2, 
                    QTableWidgetItem(QString.number(re.matchedLength())))
                
                if not wildcard:
                    for i in range(1, captures + 1):
                        if re.cap(i).length() > 0:
                            row += 1
                            self.resultTable.insertRow(row)
                            self.resultTable.setItem(row, 0, 
                                QTableWidgetItem(self.trUtf8("Capture #%1").arg(i)))
                            self.resultTable.setItem(row, 1, 
                                QTableWidgetItem(re.cap(i)))
                            self.resultTable.setItem(row, 2, 
                                QTableWidgetItem(QString.number(re.cap(i).length())))
                else:
                    self.resultTable.setRowCount(3)
                
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
        
    def on_regexpLineEdit_textChanged(self, txt):
        """
        Private slot called when the regexp changes.
        
        @param txt the new text of the line edit (QString)
        """
        self.nextButton.setEnabled(False)
        
    def getCode(self, indLevel, indString):
        """
        Public method to get the source code.
        
        @param indLevel indentation level (int)
        @param indString string used for indentation (space or tab) (string)
        @return generated code (string)
        """
        # calculate the indentation string
        istring = indLevel * indString
        
        # now generate the code
        reVar = unicode(self.variableLineEdit.text())
        if not reVar:
            reVar = "regexp"
            
        regexp = unicode(self.regexpLineEdit.text())
        
        code = '%s = QRegExp(r"""%s""")%s' % \
            (reVar, regexp.replace('"', '\\"'), os.linesep)
        if not self.caseSensitiveCheckBox.isChecked():
            code += '%s%s.setCaseSensitivity(Qt.CaseInsensitive)%s' % \
                    (istring, reVar, os.linesep)
        if self.minimalCheckBox.isChecked():
            code += '%s%s.setMinimal(1)%s' % (istring, reVar, os.linesep)
        if self.wildcardCheckBox.isChecked():
            code += '%s%s.setPatternSyntax(QRegExp.Wildcard)%s' % \
                    (istring, reVar, os.linesep)
        return code

class QRegExpWizardDialog(QDialog):
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
        
        self.cw = QRegExpWizardWidget(self, fromEric)
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

class QRegExpWizardWindow(KQMainWindow):
    """
    Main window class for the standalone dialog.
    """
    def __init__(self, parent = None):
        """
        Constructor
        
        @param parent reference to the parent widget (QWidget)
        """
        KQMainWindow.__init__(self, parent)
        self.cw = QRegExpWizardWidget(self, fromEric = False)
        size = self.cw.size()
        self.setCentralWidget(self.cw)
        self.resize(size)
        
        self.connect(self.cw.buttonBox, SIGNAL("accepted()"), self.close)
        self.connect(self.cw.buttonBox, SIGNAL("rejected()"), self.close)
