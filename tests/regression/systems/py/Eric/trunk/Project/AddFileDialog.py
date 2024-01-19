# -*- coding: utf-8 -*-

# Copyright (c) 2002 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a dialog to add a file to the project.
"""

import os

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from KdeQt import KQFileDialog

from E4Gui.E4Completers import E4DirCompleter

from Ui_AddFileDialog import Ui_AddFileDialog

import Utilities

class AddFileDialog(QDialog, Ui_AddFileDialog):
    """
    Class implementing a dialog to add a file to the project.
    """
    def __init__(self, pro, parent = None, filter = None, name = None,
                 startdir = None):
        """
        Constructor
        
        @param pro reference to the project object
        @param parent parent widget of this dialog (QWidget)
        @param filter filter specification for the file to add (string or QString)
        @param name name of this dialog (string or QString)
        @param startdir start directory for the selection dialog
        """
        QDialog.__init__(self, parent)
        if name:
            self.setObjectName(name)
        self.setupUi(self)
        
        self.targetDirCompleter = E4DirCompleter(self.targetDirEdit)
        
        self.targetDirEdit.setText(pro.ppath)
        self.filter = filter
        self.ppath = pro.ppath
        self.startdir = startdir
        self.filetypes = pro.pdata["FILETYPES"] # save a reference to the filetypes dict
        
        if self.filter is not None and self.filter != 'source':
            self.sourcecodeCheckBox.hide()
        
    @pyqtSignature("")
    def on_targetDirButton_clicked(self):
        """
        Private slot to display a directory selection dialog.
        """
        startdir = self.targetDirEdit.text()
        if startdir.isEmpty() and self.startdir is not None:
            startdir = self.startdir
        directory = KQFileDialog.getExistingDirectory(\
            self,
            self.trUtf8("Select target directory"),
            startdir,
            QFileDialog.Options(QFileDialog.Option(0)))
            
        if not directory.isNull():
            self.targetDirEdit.setText(Utilities.toNativeSeparators(directory))
        
    @pyqtSignature("")
    def on_sourceFileButton_clicked(self):
        """
        Private slot to display a file selection dialog.
        """
        dir = self.sourceFileEdit.text().section(os.pathsep, 0, 0, 
                    QString.SectionFlags(QString.SectionSkipEmpty))
        if dir.isEmpty():
            if self.startdir is not None:
                dir = self.startdir
            else:
                dir = self.targetDirEdit.text()
        if self.filter is None:
            patterns = {
                "SOURCES"      : QStringList(), 
                "FORMS"        : QStringList(), 
                "RESOURCES"    : QStringList(), 
                "INTERFACES"   : QStringList(), 
                "TRANSLATIONS" : QStringList(), 
            }
            for pattern, filetype in self.filetypes.items():
                if patterns.has_key(filetype):
                    patterns[filetype].append(QString(pattern))
            dfilter = self.trUtf8(\
                "Source Files (%1);;"
                "Forms Files (%2);;"
                "Resource Files (%3);;"
                "Interface Files (%4);;"
                "Translation Files (%5);;"
                "All Files (*)")\
                .arg(patterns["SOURCES"].join(" "))\
                .arg(patterns["FORMS"].join(" "))\
                .arg(patterns["RESOURCES"].join(" "))\
                .arg(patterns["INTERFACES"].join(" "))\
                .arg(patterns["TRANSLATIONS"].join(" "))
            caption = self.trUtf8("Select Files")
        elif self.filter == 'form':
            patterns = QStringList()
            for pattern, filetype in self.filetypes.items():
                if filetype == "FORMS":
                    patterns.append(QString(pattern))
            dfilter = self.trUtf8("Forms Files (%1)")\
                .arg(patterns.join(" "))
            caption = self.trUtf8("Select user-interface files")
        elif self.filter == "resource":
            patterns = QStringList()
            for pattern, filetype in self.filetypes.items():
                if filetype == "RESOURCES":
                    patterns.append(QString(pattern))
            dfilter = self.trUtf8("Resource Files (%1)")\
                .arg(patterns.join(" "))
            caption = self.trUtf8("Select resource files")
        elif self.filter == 'source':
            patterns = QStringList()
            for pattern, filetype in self.filetypes.items():
                if filetype == "SOURCES":
                    patterns.append(QString(pattern))
            dfilter = self.trUtf8("Source Files (%1);;All Files (*)")\
                .arg(patterns.join(" "))
            caption = self.trUtf8("Select source files")
        elif self.filter == 'interface':
            patterns = QStringList()
            for pattern, filetype in self.filetypes.items():
                if filetype == "INTERFACES":
                    patterns.append(QString(pattern))
            dfilter = self.trUtf8("Interface Files (%1)")\
                .arg(patterns.join(" "))
            caption = self.trUtf8("Select interface files")
        elif self.filter == 'translation':
            patterns = QStringList()
            for pattern, filetype in self.filetypes.items():
                if filetype == "TRANSLATIONS":
                    patterns.append(QString(pattern))
            dfilter = self.trUtf8("Translation Files (%1)")\
                .arg(patterns.join(" "))
            caption = self.trUtf8("Select translation files")
        elif self.filter == 'others':
            dfilter = self.trUtf8("All Files (*)")
            caption = self.trUtf8("Select files")
        else:
            return
        
        fnames = KQFileDialog.getOpenFileNames(\
            self, caption, dir, dfilter)
        
        if len(fnames):
            self.sourceFileEdit.setText(Utilities.toNativeSeparators(\
                fnames.join(os.pathsep)))
        
    @pyqtSignature("QString")
    def on_sourceFileEdit_textChanged(self, sfile):
        """
        Private slot to handle the source file text changed.
        
        If the entered source directory is a subdirectory of the current
        projects main directory, the target directory path is synchronized.
        It is assumed, that the user wants to add a bunch of files to
        the project in place.
        
        @param sfile the text of the source file line edit
        """
        sfile = sfile.section(os.pathsep, 0, 0,
                    QString.SectionFlags(QString.SectionSkipEmpty))
        if sfile.startsWith(self.ppath):
            if os.path.isdir(unicode(sfile)):
                dir = sfile
            else:
                dir = os.path.dirname(unicode(sfile))
            self.targetDirEdit.setText(dir)
        
    def getData(self):
        """
        Public slot to retrieve the dialogs data.
        
        @return tuple of three values (list of string, string, boolean) giving the 
            source files, the target directory and a flag telling, whether
            the files shall be added as source code
        """
        return (unicode(self.sourceFileEdit.text()).split(os.pathsep), 
            unicode(self.targetDirEdit.text()), self.sourcecodeCheckBox.isChecked())
