# -*- coding: utf-8 -*-

# Copyright (c) 2002 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a dialog to search for text in files.
"""

import os
import re

import sys

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from KdeQt import KQFileDialog, KQMessageBox
from KdeQt.KQApplication import e4App

from Ui_FindFileDialog import Ui_FindFileDialog

import Utilities
import Preferences

class FindFileDialog(QDialog, Ui_FindFileDialog):
    """
    Class implementing a dialog to search for text in files.
    
    The occurrences found are displayed in a QTreeWidget showing the filename, the 
    linenumber and the found text. The file will be opened upon a double click onto 
    the respective entry of the list.
    
    @signal sourceFile(string, int, string, (int, int)) emitted to open a 
        source file at a line
    @signal designerFile(string) emitted to open a Qt-Designer file
    """
    lineRole    = Qt.UserRole + 1
    startRole   = Qt.UserRole + 2
    endRole     = Qt.UserRole + 3
    replaceRole = Qt.UserRole + 4
    
    def __init__(self, project, replaceMode = False, parent=None):
        """
        Constructor
        
        @param project reference to the project object
        @param parent parent widget of this dialog (QWidget)
        """
        QDialog.__init__(self, parent)
        self.setupUi(self)
        self.setWindowFlags(Qt.WindowFlags(Qt.Window))
        
        self.__replaceMode = replaceMode
        
        self.stopButton = \
            self.buttonBox.addButton(self.trUtf8("Stop"), QDialogButtonBox.ActionRole)
        self.stopButton.setEnabled(False)
        
        self.findButton = \
            self.buttonBox.addButton(self.trUtf8("Find"), QDialogButtonBox.ActionRole)
        self.findButton.setEnabled(False)
        self.findButton.setDefault(True)
        
        if self.__replaceMode:
            self.replaceButton.setEnabled(False)
            self.setWindowTitle(self.trUtf8("Replace in Files"))
        else:
            self.replaceLabel.hide()
            self.replacetextCombo.hide()
            self.replaceButton.hide()
        
        self.findProgressLabel.setMaximumWidth(550)
        
        self.searchHistory = QStringList()
        self.replaceHistory = QStringList()
        self.project = project
        
        self.findList.headerItem().setText(self.findList.columnCount(), "")
        self.findList.header().setSortIndicator(0, Qt.AscendingOrder)
        self.__section0Size = self.findList.header().sectionSize(0)
        self.findList.setExpandsOnDoubleClick(False)
        if self.__replaceMode:
            font = self.findList.font()
            if Utilities.isWindowsPlatform():
                font.setFamily("Lucida Console")
            else:
                font.setFamily("Monospace")
            self.findList.setFont(font)

        # Qt Designer form files
        self.filterForms = r'.*\.ui$|.*\.ui\.h$'
        self.formsExt = ['*.ui', '*.ui.h']
        
        # Corba interface files
        self.filterInterfaces = r'.*\.idl$'
        self.interfacesExt = ['*.idl']
        
        # Qt resources files
        self.filterResources = r'.*\.qrc$'
        self.resourcesExt = ['*.qrc']
        
        self.__cancelSearch = False
        self.__lastFileItem = None
        self.__populating = False
        
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.connect(self, SIGNAL("customContextMenuRequested(const QPoint &)"), 
                     self.__contextMenuRequested)
        
    def __createItem(self, file, line, text, start, end, replTxt = ""):
        """
        Private method to create an entry in the file list.
        
        @param file filename of file (string or QString)
        @param line line number (integer)
        @param text text found (string or QString)
        @param start start position of match (integer)
        @param end end position of match (integer)
        @param replTxt text with replacements applied (string or QString
        """
        if self.__lastFileItem is None:
            # It's a new file
            self.__lastFileItem = QTreeWidgetItem(self.findList, QStringList(file))
            self.__lastFileItem.setFirstColumnSpanned(True)
            self.__lastFileItem.setExpanded(True)
            if self.__replaceMode:
                self.__lastFileItem.setFlags(self.__lastFileItem.flags() | \
                    Qt.ItemFlags(Qt.ItemIsUserCheckable | Qt.ItemIsTristate))
                # Qt bug: 
                # item is not user checkable if setFirstColumnSpanned is True (< 4.5.0)
        
        itm = QTreeWidgetItem(self.__lastFileItem, [' %5d ' % line, text])
        itm.setTextAlignment(0,  Qt.AlignRight)
        itm.setData(0, self.lineRole, QVariant(line))
        itm.setData(0, self.startRole, QVariant(start))
        itm.setData(0, self.endRole, QVariant(end))
        itm.setData(0, self.replaceRole, QVariant(replTxt))
        if self.__replaceMode:
            itm.setFlags(itm.flags() | Qt.ItemFlags(Qt.ItemIsUserCheckable))
            itm.setCheckState(0, Qt.Checked)
            self.replaceButton.setEnabled(True)
        
    def show(self, txt = ""):
        """
        Overwritten method to enable/disable the project button.
        
        @param txt text to be shown in the searchtext combo (string or QString)
        """
        if self.project and self.project.isOpen():
            self.projectButton.setEnabled(True)
        else:
            self.projectButton.setEnabled(False)
            self.dirButton.setChecked(True)
            
        self.findtextCombo.setEditText(txt)
        self.findtextCombo.lineEdit().selectAll()
        self.findtextCombo.setFocus()
        
        if self.__replaceMode:
            self.findList.clear()
            self.replacetextCombo.setEditText("")
        
        QDialog.show(self)
        
    def on_findtextCombo_editTextChanged(self, text):
        """
        Private slot to handle the editTextChanged signal of the find text combo.
        
        @param text (ignored)
        """
        self.__enableFindButton()
        
    def on_replacetextCombo_editTextChanged(self, text):
        """
        Private slot to handle the editTextChanged signal of the replace text combo.
        
        @param text (ignored)
        """
        self.__enableFindButton()
        
    def on_dirEdit_textChanged(self, text):
        """
        Private slot to handle the textChanged signal of the directory edit.
        
        @param text (ignored)
        """
        self.__enableFindButton()
        
    @pyqtSignature("")
    def on_projectButton_clicked(self):
        """
        Private slot to handle the selection of the project radio button.
        """
        self.__enableFindButton()
        
    @pyqtSignature("")
    def on_dirButton_clicked(self):
        """
        Private slot to handle the selection of the project radio button.
        """
        self.__enableFindButton()
        
    @pyqtSignature("")
    def on_filterCheckBox_clicked(self):
        """
        Private slot to handle the selection of the file filter check box.
        """
        self.__enableFindButton()
        
    @pyqtSignature("QString")
    def on_filterEdit_textEdited(self, p0):
        """
        Private slot to handle the textChanged signal of the file filter edit.
        
        @param text (ignored)
        """
        self.__enableFindButton()
        
    def __enableFindButton(self):
        """
        Private slot called to enable the find button.
        """
        if self.findtextCombo.currentText().isEmpty() or \
           (self.__replaceMode and self.replacetextCombo.currentText().isEmpty()) or \
           (self.dirButton.isChecked() and \
            (self.dirEdit.text().isEmpty() or \
             not os.path.exists(os.path.abspath(unicode(self.dirEdit.text()))))) or \
           (self.filterCheckBox.isChecked() and self.filterEdit.text().isEmpty()):
            self.findButton.setEnabled(False)
            self.buttonBox.button(QDialogButtonBox.Close).setDefault(True)
        else:
            self.findButton.setEnabled(True)
            self.findButton.setDefault(True)
        
    def on_buttonBox_clicked(self, button):
        """
        Private slot called by a button of the button box clicked.
        
        @param button button that was clicked (QAbstractButton)
        """
        if button == self.findButton:
            self.__doSearch()
        elif button == self.stopButton:
            self.__stopSearch()
        
    def __stopSearch(self):
        """
        Private slot to handle the stop button being pressed.
        """
        self.__cancelSearch = True
        
    def __doSearch(self):
        """
        Private slot to handle the find button being pressed.
        """
        if self.__replaceMode and not e4App().getObject("ViewManager").checkAllDirty():
            return
        
        self.__cancelSearch = False
        self.stopButton.setEnabled(True)
        self.stopButton.setDefault(True)
        self.findButton.setEnabled(False)
        
        if self.filterCheckBox.isChecked():
            fileFilter = unicode(self.filterEdit.text())
            fileFilterList = ["^%s$" % filter.replace(".", "\.").replace("*", ".*") \
                              for filter in fileFilter.split(";")]
            filterRe = re.compile("|".join(fileFilterList))
        
        if self.projectButton.isChecked():
            if self.filterCheckBox.isChecked():
                files = [file.replace(self.project.ppath+os.sep, "") \
                         for file in self.__getFileList(self.project.ppath, filterRe)]
            else:
                files = []
                if self.sourcesCheckBox.isChecked():
                    files += self.project.pdata["SOURCES"]
                if self.formsCheckBox.isChecked():
                    files += self.project.pdata["FORMS"] + \
                              ['%s.h' % f for f in self.project.pdata["FORMS"]]
                if self.interfacesCheckBox.isChecked():
                    files += self.project.pdata["INTERFACES"]
                if self.resourcesCheckBox.isChecked():
                    files += self.project.pdata["RESOURCES"]
        elif self.dirButton.isChecked():
            if not self.filterCheckBox.isChecked():
                filters = []
                if self.sourcesCheckBox.isChecked():
                    filters.extend(
                        ["^%s$" % assoc.replace(".", "\.").replace("*", ".*") \
                         for assoc in Preferences.getEditorLexerAssocs().keys() \
                         if assoc not in self.formsExt + self.interfacesExt])
                if self.formsCheckBox.isChecked():
                    filters.append(self.filterForms)
                if self.interfacesCheckBox.isChecked():
                    filters.append(self.filterInterfaces)
                if self.resourcesCheckBox.isChecked():
                    filters.append(self.filterResources)
                filterString = "|".join(filters)
                filterRe = re.compile(filterString)
            files = self.__getFileList(os.path.abspath(unicode(self.dirEdit.text())), 
                                       filterRe)
        elif self.openFilesButton.isChecked():
            files = e4App().getObject("ViewManager").getOpenFilenames()
        
        self.findList.clear()
        QApplication.processEvents()
        QApplication.processEvents()
        self.findProgress.setMaximum(len(files))
        
        # retrieve the values
        reg = self.regexpCheckBox.isChecked() 
        wo = self.wordCheckBox.isChecked()
        cs = self.caseCheckBox.isChecked()
        ct = unicode(self.findtextCombo.currentText())
        if reg:
            txt = ct
        else:
            txt = re.escape(ct)
        if wo:
            txt = "\\b%s\\b" % txt
        flags = re.UNICODE | re.LOCALE
        if not cs:
            flags |= re.IGNORECASE
        try:
            search = re.compile(txt, flags)
        except re.error, why:
            QMessageBox.critical(None,
                self.trUtf8("Invalid search expression"),
                self.trUtf8("""<p>The search expression is not valid.</p>"""
                            """<p>Error: %1</p>""").arg(unicode(why)))
            self.stopButton.setEnabled(False)
            self.findButton.setEnabled(True)
            self.findButton.setDefault(True)
            return
        
        # reset the findtextCombo
        self.searchHistory.removeAll(ct)
        self.searchHistory.prepend(ct)
        self.findtextCombo.clear()
        self.findtextCombo.addItems(self.searchHistory)
        if self.__replaceMode:
            replTxt = unicode(self.replacetextCombo.currentText())
            self.replaceHistory.removeAll(replTxt)
            self.replaceHistory.prepend(replTxt)
            self.replacetextCombo.clear()
            self.replacetextCombo.addItems(self.replaceHistory)
        
        # now go through all the files
        self.__populating = True
        self.findList.setUpdatesEnabled(False)
        progress = 0
        breakSearch = False
        for file in files:
            self.__lastFileItem = None
            if self.__cancelSearch or breakSearch:
                break
            
            self.findProgressLabel.setPath(file)
            
            if self.projectButton.isChecked():
                fn = os.path.join(self.project.ppath, file)
            else:
                fn = file
            # read the file and split it into textlines
            try:
                f = open(fn, 'rb')
                text, encoding = Utilities.decode(f.read())
                lines = text.splitlines()
                f.close()
            except IOError:
                progress += 1
                self.findProgress.setValue(progress)
                continue
            
            # now perform the search and display the lines found
            count = 0
            for line in lines:
                if self.__cancelSearch:
                    break
                
                count += 1
                contains = search.search(line)
                if contains:
                    start = contains.start()
                    end = contains.end()
                    if self.__replaceMode:
                        rline = search.sub(replTxt, line)
                    else:
                        rline = ""
                    if len(line) > 1024:
                        line = "%s ..." % line[:1024]
                    if self.__replaceMode:
                        if len(rline) > 1024:
                            rline = "%s ..." % line[:1024]
                        line = "- %s\n+ %s" % (line, rline)
                    self.__createItem(file, count, line, start, end, rline)
                    
                    if self.feelLikeCheckBox.isChecked():
                        fn = os.path.join(self.project.ppath, unicode(file))
                        self.emit(SIGNAL('sourceFile'), fn, count, "", (start, end))
                        QApplication.processEvents()
                        breakSearch = True
                        break
                
                QApplication.processEvents()
            
            progress += 1
            self.findProgress.setValue(progress)
        
        self.findProgressLabel.setPath("")
        
        self.findList.setUpdatesEnabled(True)
        self.findList.sortItems(self.findList.sortColumn(), 
                                self.findList.header().sortIndicatorOrder())
        self.findList.resizeColumnToContents(1)
        if self.__replaceMode:
            self.findList.header().resizeSection(0, self.__section0Size + 30)
        self.findList.header().setStretchLastSection(True)
        self.__populating = False
        
        self.stopButton.setEnabled(False)
        self.findButton.setEnabled(True)
        self.findButton.setDefault(True)
        
        if breakSearch:
            self.close()
        
    def on_findList_itemDoubleClicked(self, itm, column):
        """
        Private slot to handle the double click on a file item. 
        
        It emits the signal
        sourceFile or designerFile depending on the file extension.
        
        @param itm the double clicked tree item (QTreeWidgetItem)
        @param column column that was double clicked (integer) (ignored)
        """
        if itm.parent():
            file = itm.parent().text(0)
            line = itm.data(0, self.lineRole).toInt()[0]
            start = itm.data(0, self.startRole).toInt()[0]
            end = itm.data(0, self.endRole).toInt()[0]
        else:
            file = itm.text(0)
            line = 1
            start = 0
            end = 0
        
        if self.project:
            fn = os.path.join(self.project.ppath, unicode(file))
        else:
            fn = unicode(file)
        if fn.endswith('.ui'):
            self.emit(SIGNAL('designerFile'), fn)
        elif fn.endswith('.ui.h'):
            fn = os.path.splitext(unicode(file))[0]
            self.emit(SIGNAL('designerFile'), fn)
        else:
            self.emit(SIGNAL('sourceFile'), fn, line, "", (start, end))
        
    @pyqtSignature("")
    def on_dirSelectButton_clicked(self):
        """
        Private slot to display a directory selection dialog.
        """
        directory = KQFileDialog.getExistingDirectory(\
            self,
            self.trUtf8("Select directory"),
            self.dirEdit.text(),
            QFileDialog.Options(QFileDialog.ShowDirsOnly))
            
        if not directory.isEmpty():
            self.dirEdit.setText(Utilities.toNativeSeparators(directory))
        
    def __getFileList(self, path, filterRe):
        """
        Private method to get a list of files to search.
        
        @param path the root directory to search in (string)
        @param filterRe regular expression defining the filter criteria (regexp object)
        @return list of files to be processed (list of strings)
        """
        path = os.path.abspath(path)
        files = []
        for dirname, _, names in os.walk(path):
            files.extend([os.path.join(dirname, f) \
                          for f in names \
                          if re.match(filterRe, f)]
            )
        return files
        
    def setSearchDirectory(self, searchDir):
        """
        Public slot to set the name of the directory to search in.
        
        @param searchDir name of the directory to search in (string or QString)
        """
        self.dirButton.setChecked(True)
        self.dirEdit.setText(Utilities.toNativeSeparators(searchDir))
        
    @pyqtSignature("")
    def on_replaceButton_clicked(self):
        """
        Private slot to perform the requested replace actions.
        """
        self.findProgress.setMaximum(self.findList.topLevelItemCount())
        self.findProgress.setValue(0)
        
        progress = 0
        for index in range(self.findList.topLevelItemCount()):
            itm = self.findList.topLevelItem(index)
            if itm.checkState(0) in [Qt.PartiallyChecked, Qt.Checked]:
                file = unicode(itm.text(0))
                
                self.findProgressLabel.setPath(file)
                
                if self.projectButton.isChecked():
                    fn = os.path.join(self.project.ppath, file)
                else:
                    fn = file
                
                # read the file and split it into textlines
                try:
                    f = open(fn, 'rb')
                    text, encoding = Utilities.decode(f.read())
                    lines = text.splitlines()
                    f.close()
                except IOError, err:
                    KQMessageBox.critical(self,
                        self.trUtf8("Replace in Files"),
                        self.trUtf8("""<p>Could not read the file <b>%1</b>."""
                                    """ Skipping it.</p><p>Reason: %2</p>""")\
                            .arg(fn).arg(unicode(err))
                    )
                    progress += 1
                    self.findProgress.setValue(progress)
                    continue
                
                # replace the lines authorized by the user
                for cindex in range(itm.childCount()):
                    citm = itm.child(cindex)
                    if citm.checkState(0) == Qt.Checked:
                        line = citm.data(0, self.lineRole).toInt()[0]
                        rline = citm.data(0, self.replaceRole).toString()
                        lines[line - 1] = unicode(rline)
                
                # write the file
                txt = Utilities.linesep().join(lines)
                txt, encoding = Utilities.encode(txt, encoding)
                try:
                    f = open(fn, 'wb')
                    f.write(txt)
                    f.close()
                except IOError, err:
                    KQMessageBox.critical(self,
                        self.trUtf8("Replace in Files"),
                        self.trUtf8("""<p>Could not save the file <b>%1</b>."""
                                    """ Skipping it.</p><p>Reason: %2</p>""")\
                            .arg(fn).arg(unicode(err))
                    )
            
            progress += 1
            self.findProgress.setValue(progress)
        
        self.findProgressLabel.setPath("")
        
        self.findList.clear()
        self.replaceButton.setEnabled(False)
        self.findButton.setEnabled(True)
        self.findButton.setDefault(True)
        
    def __contextMenuRequested(self, pos):
        """
        Private slot to handle the context menu request.
        
        @param pos position the context menu shall be shown (QPoint)
        """
        menu = QMenu(self)
        
        menu.addAction(self.trUtf8("Open"), self.__openFile)
        menu.addAction(self.trUtf8("Copy Path to Clipboard"), self.__copyToClipboard)
        
        menu.exec_(QCursor.pos())
        
    def __openFile(self):
        """
        Private slot to open the currently selected entry.
        """
        itm = self.findList.selectedItems()[0]
        self.on_findList_itemDoubleClicked(itm, 0)
        
    def __copyToClipboard(self):
        """
        Private method to copy the path of an entry to the clipboard.
        """
        itm = self.findList.selectedItems()[0]
        if itm.parent():
            fn = itm.parent().text(0)
        else:
            fn = itm.text(0)
        
        cb = QApplication.clipboard()
        cb.setText(fn)
