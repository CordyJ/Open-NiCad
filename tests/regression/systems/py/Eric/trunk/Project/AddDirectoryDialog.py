# -*- coding: utf-8 -*-

# Copyright (c) 2002 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a dialog to add files of a directory to the project.
"""

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from KdeQt import KQFileDialog

from E4Gui.E4Completers import E4DirCompleter

from Ui_AddDirectoryDialog import Ui_AddDirectoryDialog

import Utilities

class AddDirectoryDialog(QDialog, Ui_AddDirectoryDialog):
    """
    Class implementing a dialog to add files of a directory to the project.
    """
    def __init__(self, pro, filter = 'source', parent = None, name = None, 
                 startdir = None):
        """
        Constructor
        
        @param pro reference to the project object
        @param filter file type filter (string or QString)
        @param parent parent widget of this dialog (QWidget)
        @param name name of this dialog (string or QString)
        @param startdir start directory for the selection dialog
        """
        QDialog.__init__(self,parent)
        if name:
            self.setObjectName(name)
        self.setupUi(self)
        
        self.sourceDirCompleter = E4DirCompleter(self.sourceDirEdit)
        self.targetDirCompleter = E4DirCompleter(self.targetDirEdit)
        
        self.ppath = pro.ppath
        self.targetDirEdit.setText(self.ppath)
        self.startdir = startdir
        self.on_filterComboBox_highlighted(QString('(*.py)')) # enable all dialog elements
        filter = unicode(filter)
        if filter == 'source':  # it is a source file
            self.filterComboBox.addItem(self.trUtf8("Source Files"), 
                                        QVariant("SOURCES"))
        elif filter == 'form':
            self.filterComboBox.addItem(self.trUtf8("Forms Files"), 
                                        QVariant("FORMS"))
        elif filter == 'resource':
            self.filterComboBox.addItem(self.trUtf8("Resource Files"), 
                                        QVariant("RESOURCES"))
        elif filter == 'interface':
            self.filterComboBox.addItem(self.trUtf8("Interface Files"), 
                                        QVariant("INTERFACES"))
        elif filter == 'others':
            self.filterComboBox.addItem(self.trUtf8("Other Files (*)"), 
                                        QVariant("OTHERS"))
            self.on_filterComboBox_highlighted(QString('(*)'))
        else:
            self.filterComboBox.addItem(self.trUtf8("Source Files"), 
                                        QVariant("SOURCES"))
            self.filterComboBox.addItem(self.trUtf8("Forms Files"), 
                                        QVariant("FORMS"))
            self.filterComboBox.addItem(self.trUtf8("Resource Files"), 
                                        QVariant("RESOURCES"))
            self.filterComboBox.addItem(self.trUtf8("Interface Files"), 
                                        QVariant("INTERFACES"))
            self.filterComboBox.addItem(self.trUtf8("Other Files (*)"), 
                                        QVariant("OTHERS"))
        self.filterComboBox.setCurrentIndex(0)
        
    @pyqtSignature("QString")
    def on_filterComboBox_highlighted(self, fileType):
        """
        Private slot to handle the selection of a file type.
        
        @param fileType the selected file type (QString)
        """
        if fileType.endsWith('(*)'):
            self.targetDirLabel.setEnabled(False)
            self.targetDirEdit.setEnabled(False)
            self.targetDirButton.setEnabled(False)
            self.recursiveCheckBox.setEnabled(False)
        else:
            self.targetDirLabel.setEnabled(True)
            self.targetDirEdit.setEnabled(True)
            self.targetDirButton.setEnabled(True)
            self.recursiveCheckBox.setEnabled(True)
        
    def __dirDialog(self, textEdit):
        """
        Private slot to display a directory selection dialog.
        
        @param textEdit field for the display of the selected directory name
                (QLineEdit)
        """
        startdir = textEdit.text()
        if startdir.isEmpty() and self.startdir is not None:
            startdir = self.startdir
        
        directory = KQFileDialog.getExistingDirectory(\
            self,
            self.trUtf8("Select directory"),
            startdir,
            QFileDialog.Options(QFileDialog.Option(0)))
        
        if not directory.isEmpty():
            textEdit.setText(Utilities.toNativeSeparators(directory))
        
    @pyqtSignature("")
    def on_sourceDirButton_clicked(self):
        """
        Private slot to handle the source dir button press.
        """
        self.__dirDialog(self.sourceDirEdit)
        
    @pyqtSignature("")
    def on_targetDirButton_clicked(self):
        """
        Private slot to handle the target dir button press.
        """
        self.__dirDialog(self.targetDirEdit)
        
    @pyqtSignature("QString")
    def on_sourceDirEdit_textChanged(self, dir):
        """
        Private slot to handle the source dir text changed.
        
        If the entered source directory is a subdirectory of the current
        projects main directory, the target directory path is synchronized.
        It is assumed, that the user wants to add a bunch of files to
        the project in place.
        
        @param dir the text of the source directory line edit
        """
        if dir.startsWith(self.ppath):
            self.targetDirEdit.setText(dir)
        
    def getData(self):
        """
        Public slot to retrieve the dialogs data.
        
        @return tuple of four values (string, string, string, boolean) giving
            the selected file type, the source and target directory and
            a flag indicating a recursive add
        """
        filetype = \
            self.filterComboBox.itemData(self.filterComboBox.currentIndex()).toString()
        return (unicode(filetype), unicode(self.sourceDirEdit.text()), 
            unicode(self.targetDirEdit.text()),
            self.recursiveCheckBox.isChecked())
