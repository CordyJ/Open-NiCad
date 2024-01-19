# -*- coding: utf-8 -*-

# Copyright (c) 2008 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the search and replace widget.
"""

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from KdeQt import KQMessageBox

from Ui_SearchWidget import Ui_SearchWidget
from Ui_ReplaceWidget import Ui_ReplaceWidget

from E4Gui.E4Action import E4Action

import Preferences

import UI.PixmapCache

class SearchReplaceWidget(QWidget):
    """
    Class implementing the search and replace widget.
    
    @signal searchListChanged emitted to indicate a change of the search list
    """
    def __init__(self, replace, vm, parent = None):
        """
        Constructor
        
        @param replace flag indicating a replace widget is called
        @param vm reference to the viewmanager object
        @param parent parent widget of this widget (QWidget)
        """
        QWidget.__init__(self, parent)
        
        self.viewmanager = vm
        self.replace = replace
        
        self.findHistory = vm.getSRHistory('search')
        if replace:
            self.replaceHistory = vm.getSRHistory('replace')
            self.ui = Ui_ReplaceWidget()
            whatsThis = self.trUtf8(r"""
<b>Find and Replace</b>
<p>This dialog is used to find some text and replace it with another text. 
By checking the various checkboxes, the search can be made more specific. The search 
string might be a regular expression. In a regular expression, special characters 
interpreted are:</p>
"""
            )
        else:
            self.ui = Ui_SearchWidget()
            whatsThis = self.trUtf8(r"""
<b>Find</b>
<p>This dialog is used to find some text. By checking the various checkboxes, the search 
can be made more specific. The search string might be a regular expression. In a regular 
expression, special characters interpreted are:</p>
"""
            )
        self.ui.setupUi(self)
        if not replace:
            self.ui.wrapCheckBox.setChecked(True)
        
        whatsThis.append(self.trUtf8(r"""
<table border="0">
<tr><td><code>.</code></td><td>Matches any character</td></tr>
<tr><td><code>\(</code></td><td>This marks the start of a region for tagging a match.</td></tr>
<tr><td><code>\)</code></td><td>This marks the end of a tagged region.</td></tr>
<tr><td><code>\n</code></td>
<td>Where <code>n</code> is 1 through 9 refers to the first through ninth tagged region
when replacing. For example, if the search string was <code>Fred\([1-9]\)XXX</code> and
the replace string was <code>Sam\1YYY</code>, when applied to <code>Fred2XXX</code> this
would generate <code>Sam2YYY</code>.</td></tr>
<tr><td><code>\&lt;</code></td>
<td>This matches the start of a word using Scintilla's definitions of words.</td></tr>
<tr><td><code>\&gt;</code></td>
<td>This matches the end of a word using Scintilla's definition of words.</td></tr>
<tr><td><code>\x</code></td>
<td>This allows you to use a character x that would otherwise have a special meaning. For
example, \[ would be interpreted as [ and not as the start of a character set.</td></tr>
<tr><td><code>[...]</code></td>
<td>This indicates a set of characters, for example, [abc] means any of the characters a,
b or c. You can also use ranges, for example [a-z] for any lower case character.</td></tr>
<tr><td><code>[^...]</code></td>
<td>The complement of the characters in the set. For example, [^A-Za-z] means any
character except an alphabetic character.</td></tr>
<tr><td><code>^</code></td>
<td>This matches the start of a line (unless used inside a set, see above).</td></tr>
<tr><td><code>$</code></td> <td>This matches the end of a line.</td></tr>
<tr><td><code>*</code></td>
<td>This matches 0 or more times. For example, <code>Sa*m</code> matches <code>Sm</code>,
<code>Sam</code>, <code>Saam</code>, <code>Saaam</code> and so on.</td></tr>
<tr><td><code>+</code></td>
<td>This matches 1 or more times. For example, <code>Sa+m</code> matches
<code>Sam</code>, <code>Saam</code>, <code>Saaam</code> and so on.</td></tr>
</table>
"""
        ))
        self.setWhatsThis(whatsThis)
        
        self.ui.closeButton.setIcon(UI.PixmapCache.getIcon("close.png"))
        self.ui.findPrevButton.setIcon(UI.PixmapCache.getIcon("1leftarrow.png"))
        self.ui.findNextButton.setIcon(UI.PixmapCache.getIcon("1rightarrow.png"))
        
        if replace:
            self.ui.replaceButton.setIcon(UI.PixmapCache.getIcon("editReplace.png"))
            self.ui.replaceAllButton.setIcon(UI.PixmapCache.getIcon("editReplaceAll.png"))
        
        self.connect(self.ui.findtextCombo.lineEdit(), SIGNAL("returnPressed()"), 
                     self.__findByReturnPressed)
        if replace:
            self.connect(self.ui.replacetextCombo.lineEdit(), SIGNAL("returnPressed()"), 
                         self.on_replaceButton_clicked)
        
        self.havefound = False
        self.__pos = None
        self.__findBackwards = False
        self.__selection = None
        self.__finding = False

    def on_findtextCombo_editTextChanged(self, txt):
        """
        Private slot to enable/disable the find buttons.
        """
        if txt.isEmpty():
            self.ui.findNextButton.setEnabled(False)
            self.ui.findPrevButton.setEnabled(False)
            if self.replace:
                self.ui.replaceButton.setEnabled(False)
                self.ui.replaceAllButton.setEnabled(False)
        else:
            self.ui.findNextButton.setEnabled(True)
            self.ui.findPrevButton.setEnabled(True)
            if self.replace:
                self.ui.replaceButton.setEnabled(False)
                self.ui.replaceAllButton.setEnabled(True)

    @pyqtSignature("")
    def on_findNextButton_clicked(self):
        """
        Private slot to find the next occurrence of text.
        """
        self.findNext()
    
    def findNext(self):
        """
        Public slot to find the next occurrence of text.
        """
        if not self.havefound or self.ui.findtextCombo.currentText().isEmpty():
            self.show(self.viewmanager.textForFind())
            return
        
        self.__findBackwards = False
        txt = self.ui.findtextCombo.currentText()
        
        # This moves any previous occurrence of this statement to the head
        # of the list and updates the combobox
        self.findHistory.removeAll(txt)
        self.findHistory.prepend(txt)
        self.ui.findtextCombo.clear()
        self.ui.findtextCombo.addItems(self.findHistory)
        self.emit(SIGNAL('searchListChanged'))
        
        ok = self.__findNextPrev(txt, False)
        if ok:
            if self.replace:
                self.ui.replaceButton.setEnabled(True)
        else:
            KQMessageBox.information(self, self.windowTitle(),
                self.trUtf8("'%1' was not found.").arg(txt))

    @pyqtSignature("")
    def on_findPrevButton_clicked(self):
        """
        Private slot to find the previous occurrence of text.
        """
        self.findPrev()
    
    def findPrev(self):
        """
        Public slot to find the next previous of text.
        """
        if not self.havefound or self.ui.findtextCombo.currentText().isEmpty():
            self.show(self.viewmanager.textForFind())
            return
        
        self.__findBackwards = True
        txt = self.ui.findtextCombo.currentText()
        
        # This moves any previous occurrence of this statement to the head
        # of the list and updates the combobox
        self.findHistory.removeAll(txt)
        self.findHistory.prepend(txt)
        self.ui.findtextCombo.clear()
        self.ui.findtextCombo.addItems(self.findHistory)
        self.emit(SIGNAL('searchListChanged'))
        
        ok = self.__findNextPrev(txt, True)
        if ok:
            if self.replace:
                self.ui.replaceButton.setEnabled(True)
        else:
            KQMessageBox.information(self, self.windowTitle(),
                self.trUtf8("'%1' was not found.").arg(txt))
    
    def __findByReturnPressed(self):
        """
        Private slot to handle the returnPressed signal of the findtext combobox.
        """
        if self.__findBackwards:
            self.findPrev()
        else:
            self.findNext()
    
    def __markOccurrences(self, txt):
        """
        Private method to mark all occurrences of the search text.
        
        @param txt text to search for (QString)
        """
        aw = self.viewmanager.activeWindow()
        lineFrom = 0
        indexFrom = 0
        lineTo = -1
        indexTo = -1
        if self.ui.selectionCheckBox.isChecked():
            lineFrom = self.__selection[0]
            indexFrom = self.__selection[1]
            lineTo = self.__selection[2]
            indexTo = self.__selection[3]
        
        aw.clearSearchIndicators()
        ok = aw.findFirstTarget(txt,
                self.ui.regexpCheckBox.isChecked(),
                self.ui.caseCheckBox.isChecked(),
                self.ui.wordCheckBox.isChecked(),
                lineFrom, indexFrom, lineTo, indexTo)
        while ok:
            tgtPos, tgtLen = aw.getFoundTarget()
            aw.setSearchIndicator(tgtPos, tgtLen)
            ok = aw.findNextTarget()
    
    def __findNextPrev(self, txt, backwards):
        """
        Private method to find the next occurrence of the search text.
        
        @param txt text to search for (QString)
        @param backwards flag indicating a backwards search (boolean)
        @return flag indicating success (boolean)
        """
        self.__finding = True
        
        if Preferences.getEditor("SearchMarkersEnabled"):
            self.__markOccurrences(txt)
        
        aw = self.viewmanager.activeWindow()
        cline, cindex = aw.getCursorPosition()
        
        ok = True
        lineFrom, indexFrom, lineTo, indexTo = aw.getSelection()
        if backwards:
            if self.ui.selectionCheckBox.isChecked() and \
               (lineFrom, indexFrom, lineTo, indexTo) == self.__selection:
                # initial call
                line = self.__selection[2]
                index = self.__selection[3]
            else:
                line = lineFrom
                index = indexFrom - 1
            if self.ui.selectionCheckBox.isChecked() and \
               line == self.__selection[0] and \
               index >= 0 and \
               index < self.__selection[1]:
                ok = False
            
            if ok and index < 0:
                line -= 1
                if self.ui.selectionCheckBox.isChecked():
                    if line < self.__selection[0]:
                        if self.ui.wrapCheckBox.isChecked():
                            line = self.__selection[2]
                            index = self.__selection[3]
                        else:
                            ok = False
                    else:
                        index = aw.lineLength(line)
                else:
                    if line < 0:
                        if self.ui.wrapCheckBox.isChecked():
                            line = aw.lines() - 1
                            index = aw.lineLength(line)
                        else:
                            ok = False
                    else:
                        index = aw.lineLength(line)
        else:
            if self.ui.selectionCheckBox.isChecked() and \
               (lineFrom, indexFrom, lineTo, indexTo) == self.__selection:
                # initial call
                line = self.__selection[0]
                index = self.__selection[1]
            else:
                line = lineTo
                index = indexTo
        
        if ok:
            ok = aw.findFirst(txt,
                self.ui.regexpCheckBox.isChecked(),
                self.ui.caseCheckBox.isChecked(),
                self.ui.wordCheckBox.isChecked(),
                self.ui.wrapCheckBox.isChecked(),
                not backwards,
                line, index)
        
        if ok and self.ui.selectionCheckBox.isChecked():
            lineFrom, indexFrom, lineTo, indexTo = aw.getSelection()
            if (lineFrom == self.__selection[0] and indexFrom >= self.__selection[1]) or \
               (lineFrom > self.__selection[0] and lineFrom < self.__selection[2]) or \
               (lineFrom == self.__selection[2] and indexFrom <= self.__selection[3]):
                ok = True
            else:
                if self.ui.wrapCheckBox.isChecked():
                    # try it again
                    if backwards:
                        line = self.__selection[2]
                        index = self.__selection[3]
                    else:
                        line = self.__selection[0]
                        index = self.__selection[1]
                    ok = aw.findFirst(txt,
                        self.ui.regexpCheckBox.isChecked(),
                        self.ui.caseCheckBox.isChecked(),
                        self.ui.wordCheckBox.isChecked(),
                        self.ui.wrapCheckBox.isChecked(),
                        not backwards,
                        line, index)
                    if ok:
                        lineFrom, indexFrom, lineTo, indexTo = aw.getSelection()
                        if (lineFrom == self.__selection[0] and \
                            indexFrom >= self.__selection[1]) or \
                           (lineFrom > self.__selection[0] and \
                            lineFrom < self.__selection[2]) or \
                           (lineFrom == self.__selection[2] \
                            and indexFrom <= self.__selection[3]):
                            ok = True
                        else:
                            ok = False
                            aw.selectAll(False)
                            aw.setCursorPosition(cline, cindex)
                            aw.ensureCursorVisible()
                else:
                    ok = False
                    aw.selectAll(False)
                    aw.setCursorPosition(cline, cindex)
                    aw.ensureCursorVisible()
        
        self.__finding = False
        
        return ok

    def __showFind(self, text = ''):
        """
        Private method to display this widget in find mode.
        
        @param text text to be shown in the findtext edit
        """
        self.replace = False
        
        self.ui.findtextCombo.clear()
        self.ui.findtextCombo.addItems(self.findHistory)
        self.ui.findtextCombo.setEditText(text)
        self.ui.findtextCombo.lineEdit().selectAll()
        self.ui.findtextCombo.setFocus()
        
        self.ui.caseCheckBox.setChecked(False)
        self.ui.wordCheckBox.setChecked(False)
        self.ui.wrapCheckBox.setChecked(True)
        self.ui.regexpCheckBox.setChecked(False)
        
        aw = self.viewmanager.activeWindow()
        self.updateSelectionCheckBox(aw)
        
        self.havefound = True
        self.__findBackwards = False
    
    def selectionChanged(self):
        """
        Public slot tracking changes of selected text.
        """
        aw = self.sender()
        self.updateSelectionCheckBox(aw)
    
    def updateSelectionCheckBox(self, editor):
        """
        Public slot to update the selection check box.
        
        @param editor reference to the editor (Editor)
        """
        if not self.__finding:
            if editor.hasSelectedText():
                line1, index1, line2, index2 = editor.getSelection()
                if line1 != line2:
                    self.ui.selectionCheckBox.setEnabled(True)
                    self.ui.selectionCheckBox.setChecked(True)
                    self.__selection = (line1, index1, line2, index2)
                    return
            
            self.ui.selectionCheckBox.setEnabled(False)
            self.ui.selectionCheckBox.setChecked(False)
            self.__selection = None

    @pyqtSignature("")
    def on_replaceButton_clicked(self):
        """
        Private slot to replace one occurrence of text.
        """
        self.__finding = True
        
        # Check enabled status due to dual purpose usage of this method
        if not self.ui.replaceButton.isEnabled():
            return
        
        ftxt = self.ui.findtextCombo.currentText()
        rtxt = self.ui.replacetextCombo.currentText()
        
        # This moves any previous occurrence of this statement to the head
        # of the list and updates the combobox
        self.replaceHistory.removeAll(rtxt)
        self.replaceHistory.prepend(rtxt)
        self.ui.replacetextCombo.clear()
        self.ui.replacetextCombo.addItems(self.replaceHistory)
        
        aw = self.viewmanager.activeWindow()
        aw.replace(rtxt)
        ok = self.__findNextPrev(ftxt, self.__findBackwards)
        
        if not ok:
            self.ui.replaceButton.setEnabled(False)
            KQMessageBox.information(self, self.windowTitle(),
                self.trUtf8("'%1' was not found.").arg(ftxt))
        
        self.__finding = False
        
    @pyqtSignature("")
    def on_replaceAllButton_clicked(self):
        """
        Private slot to replace all occurrences of text.
        """
        self.__finding = True
        
        replacements = 0
        ftxt = self.ui.findtextCombo.currentText()
        rtxt = self.ui.replacetextCombo.currentText()
        
        # This moves any previous occurrence of this statement to the head
        # of the list and updates the combobox
        self.findHistory.removeAll(ftxt)
        self.findHistory.prepend(ftxt)
        self.ui.findtextCombo.clear()
        self.ui.findtextCombo.addItems(self.findHistory)
        
        self.replaceHistory.removeAll(rtxt)
        self.replaceHistory.prepend(rtxt)
        self.ui.replacetextCombo.clear()
        self.ui.replacetextCombo.addItems(self.replaceHistory)
        
        aw = self.viewmanager.activeWindow()
        cline, cindex = aw.getCursorPosition()
        if self.ui.selectionCheckBox.isChecked():
            line = self.__selection[0]
            index = self.__selection[1]
        else:
            line = 0
            index = 0
        ok = aw.findFirst(ftxt,
                self.ui.regexpCheckBox.isChecked(),
                self.ui.caseCheckBox.isChecked(),
                self.ui.wordCheckBox.isChecked(),
                False, True, line, index)
        
        if ok and self.ui.selectionCheckBox.isChecked():
            lineFrom, indexFrom, lineTo, indexTo = aw.getSelection()
            if (lineFrom == self.__selection[0] and indexFrom >= self.__selection[1]) or \
               (lineFrom > self.__selection[0] and lineFrom < self.__selection[2]) or \
               (lineFrom == self.__selection[2] and indexFrom <= self.__selection[3]):
                ok = True
            else:
                ok = False
                aw.selectAll(False)
                aw.setCursorPosition(cline, cindex)
                aw.ensureCursorVisible()
        
        found = ok
        
        aw.beginUndoAction()
        wordWrap = self.ui.wrapCheckBox.isChecked()
        self.ui.wrapCheckBox.setChecked(False)
        while ok:
            aw.replace(rtxt)
            replacements += 1
            ok = self.__findNextPrev(ftxt, self.__findBackwards)
            self.__finding = True
        aw.endUndoAction()
        if wordWrap:
            self.ui.wrapCheckBox.setChecked(True)
        self.ui.replaceButton.setEnabled(False)
        
        if found:
            KQMessageBox.information(self, self.windowTitle(),
                self.trUtf8("Replaced %1 occurrences.")
                    .arg(replacements))
        else:
            KQMessageBox.information(self, self.windowTitle(),
                self.trUtf8("Nothing replaced because '%1' was not found.")
                    .arg(ftxt))
        
        aw.setCursorPosition(cline, cindex)
        aw.ensureCursorVisible()
        
        self.__finding = False
        
    def __showReplace(self, text=''):
        """
        Private slot to display this widget in replace mode.
        
        @param text text to be shown in the findtext edit
        """
        self.replace = True
        
        self.ui.findtextCombo.clear()
        self.ui.findtextCombo.addItems(self.findHistory)
        self.ui.findtextCombo.setEditText(text)
        self.ui.findtextCombo.lineEdit().selectAll()
        self.ui.findtextCombo.setFocus()
        
        self.ui.replacetextCombo.clear()
        self.ui.replacetextCombo.addItems(self.replaceHistory)
        self.ui.replacetextCombo.setEditText('')
        
        self.ui.caseCheckBox.setChecked(False)
        self.ui.wordCheckBox.setChecked(False)
        self.ui.regexpCheckBox.setChecked(False)
        
        self.havefound = True
        
        aw = self.viewmanager.activeWindow()
        self.updateSelectionCheckBox(aw)
        if aw.hasSelectedText():
            line1, index1, line2, index2 = aw.getSelection()
            if line1 == line2:
                aw.setSelection(line1, index1, line1, index1)
                self.findNext()

    def show(self, text = ''):
        """
        Overridden slot from QWidget.
        
        @param text text to be shown in the findtext edit
        """
        if self.replace:
            self.__showReplace(text)
        else:
            self.__showFind(text)
        QWidget.show(self)
        self.activateWindow()

    @pyqtSignature("")
    def on_closeButton_clicked(self):
        """
        Private slot to close the widget.
        """
        self.close()
    
    def keyPressEvent(self, event):
        """
        Protected slot to handle key press events.
        
        @param event reference to the key press event (QKeyEvent)
        """
        if event.key() == Qt.Key_Escape:
            aw = self.viewmanager.activeWindow()
            if aw:
                aw.setFocus(Qt.ActiveWindowFocusReason)
            event.accept()
            self.close()
