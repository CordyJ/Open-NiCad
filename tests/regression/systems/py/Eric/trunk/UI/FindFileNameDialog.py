# -*- coding: utf-8 -*-

# Copyright (c) 2004 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a dialog to search for files.
"""

import os
import sys

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from E4Gui.E4Completers import E4DirCompleter

from Ui_FindFileNameDialog import Ui_FindFileNameDialog
from Utilities import direntries
import Utilities


class FindFileNameDialog(QWidget, Ui_FindFileNameDialog):
    """
    Class implementing a dialog to search for files.
    
    The occurrences found are displayed in a QTreeWidget showing the
    filename and the pathname. The file will be opened upon a double click
    onto the respective entry of the list.
    
    @signal sourceFile(string) emitted to open a file in the editor
    @signal designerFile(string) emitted to open a Qt-Designer file
    """
    def __init__(self, project, parent = None):
        """
        Constructor
        
        @param project reference to the project object
        @param parent parent widget of this dialog (QWidget)
        """
        QWidget.__init__(self, parent)
        self.setupUi(self)
        
        self.searchDirCompleter = E4DirCompleter(self.searchDirEdit)
        
        self.fileList.headerItem().setText(self.fileList.columnCount(), "")
        
        self.stopButton = \
            self.buttonBox.addButton(self.trUtf8("Stop"), QDialogButtonBox.ActionRole)
        self.stopButton.setToolTip(self.trUtf8("Press to stop the search"))
        self.stopButton.setEnabled(False)
        self.buttonBox.button(QDialogButtonBox.Open).setToolTip(\
            self.trUtf8("Opens the selected file"))
        
        self.project = project
        self.extsepLabel.setText(os.extsep)
        
        self.shouldStop = False

    def on_buttonBox_clicked(self, button):
        """
        Private slot called by a button of the button box clicked.
        
        @param button button that was clicked (QAbstractButton)
        """
        if button == self.stopButton:
            self.shouldStop = True
        elif button == self.buttonBox.button(QDialogButtonBox.Open):
            self.__openFile()
    
    def __openFile(self):
        """
        Private slot to open a file. 
        
        It emits the signal
        sourceFile or designerFile depending on the file extension.
        """
        itm = self.fileList.currentItem()
        fileName = unicode(itm.text(0))
        filePath = unicode(itm.text(1))
        
        if fileName.endswith('.ui'):
            self.emit(SIGNAL('designerFile'), os.path.join(filePath, fileName))
        elif fileName.endswith('.ui.h'):
            fn = os.path.splitext(fileName)
            self.emit(SIGNAL('designerFile'), os.path.join(filePath, fn))
        else:
            self.emit(SIGNAL('sourceFile'), os.path.join(filePath, fileName))

    def __searchFile(self):
        """
        Private slot to handle the search.
        """
        fileName = unicode(self.fileNameEdit.text())
        if not fileName:
            return
        fileExt = unicode(self.fileExtEdit.text())
        patternFormat = fileExt and "%s%s%s*" or "%s*%s%s"
        fileNamePattern = patternFormat % (fileName, os.extsep,
            fileExt and fileExt or '*')
            
        searchPaths = []
        if self.searchDirCheckBox.isChecked() and \
           not self.searchDirEdit.text().isEmpty():
            searchPaths.append(unicode(self.searchDirEdit.text()))
        if self.projectCheckBox.isChecked():
            searchPaths.append(self.project.ppath)
        if self.syspathCheckBox.isChecked():
            searchPaths.extend(sys.path)
            
        found = False
        self.fileList.clear()
        locations = {}
        self.shouldStop = False
        self.stopButton.setEnabled(True)
        QApplication.processEvents()
        
        for path in searchPaths:
            if os.path.isdir(path):
                files = direntries(path, True, fileNamePattern, False, self.checkStop)
                if files:
                    found = True
                    for file in files:
                        fp, fn = os.path.split(file)
                        if locations.has_key(fn):
                            if fp in locations[fn]:
                                continue
                            else:
                                locations[fn].append(fp)
                        else:
                            locations[fn] = [fp]
                        QTreeWidgetItem(self.fileList, QStringList() << fn << fp)
                    QApplication.processEvents()
            
        del locations
        self.buttonBox.button(QDialogButtonBox.Open).setEnabled(found)
        self.stopButton.setEnabled(False)
        self.fileList.header().resizeSections(QHeaderView.ResizeToContents)
        self.fileList.header().setStretchLastSection(True)

    def checkStop(self):
        """
        Public method to check, if the search should be stopped.
        
        @return flag indicating the search should be stopped (boolean)
        """
        QApplication.processEvents()
        return self.shouldStop
        
    def on_fileNameEdit_textChanged(self, text):
        """
        Private slot to handle the textChanged signal of the file name edit.
        
        @param text (ignored)
        """
        self.__searchFile()
        
    def on_fileExtEdit_textChanged(self, text):
        """
        Private slot to handle the textChanged signal of the file extension edit.
        
        @param text (ignored)
        """
        self.__searchFile()
        
    def on_searchDirEdit_textChanged(self, text):
        """
        Private slot to handle the textChanged signal of the search directory edit.
        
        @param text (ignored)
        """
        self.searchDirCheckBox.setEnabled(not text.isEmpty())
        if self.searchDirCheckBox.isChecked():
            self.__searchFile()
        
        
    @pyqtSignature("")
    def on_searchDirButton_clicked(self):
        """
        Private slot to handle the clicked signal of the search directory selection button.
        """
        searchDir = QFileDialog.getExistingDirectory(\
            None,
            self.trUtf8("Select search directory"),
            self.searchDirEdit.text(),
            QFileDialog.Options(QFileDialog.ShowDirsOnly))
        
        if not searchDir.isEmpty():
            self.searchDirEdit.setText(Utilities.toNativeSeparators(searchDir))
        
    def on_searchDirCheckBox_toggled(self, checked):
        """
        Private slot to handle the toggled signal of the search directory checkbox.
        
        @param checked flag indicating the state of the checkbox (boolean)
        """
        if not self.searchDirEdit.text().isEmpty():
            self.__searchFile()
        
    def on_projectCheckBox_toggled(self, checked):
        """
        Private slot to handle the toggled signal of the project checkbox.
        
        @param checked flag indicating the state of the checkbox (boolean)
        """
        self.__searchFile()
        
    def on_syspathCheckBox_toggled(self, checked):
        """
        Private slot to handle the toggled signal of the sys.path checkbox.
        
        @param checked flag indicating the state of the checkbox (boolean)
        """
        self.__searchFile()
        
    def on_fileList_itemActivated(self, itm, column):
        """
        Private slot to handle the double click on a file item. 
        
        It emits the signal
        sourceFile or designerFile depending on the file extension.
        
        @param itm the double clicked listview item (QTreeWidgetItem)
        @param column column that was double clicked (integer) (ignored)
        """
        self.__openFile()
        
    def show(self):
        """
        Overwritten method to enable/disable the project checkbox.
        """
        if self.project and self.project.isOpen():
            self.projectCheckBox.setEnabled(True)
            self.projectCheckBox.setChecked(True)
        else:
            self.projectCheckBox.setEnabled(False)
            self.projectCheckBox.setChecked(False)
        
        self.fileNameEdit.selectAll()
        self.fileNameEdit.setFocus()
        
        QWidget.show(self)
