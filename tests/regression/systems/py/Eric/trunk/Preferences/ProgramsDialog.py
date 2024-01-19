# -*- coding: utf-8 -*-

# Copyright (c) 2006 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the Programs page.
"""

import os
import sys
import re

from PyQt4.QtCore import pyqtSignature, QString, QStringList, Qt, QProcess
from PyQt4.QtGui import QApplication, QTreeWidgetItem, QHeaderView, QCursor, \
    QDialog, QDialogButtonBox

from KdeQt.KQApplication import e4App

from Ui_ProgramsDialog import Ui_ProgramsDialog

import Preferences
import Utilities

class ProgramsDialog(QDialog, Ui_ProgramsDialog):
    """
    Class implementing the Programs page.
    """
    def __init__(self, parent = None):
        """
        Constructor
        
        @param parent The parent widget of this dialog. (QWidget)
        """
        QDialog.__init__(self, parent)
        self.setupUi(self)
        self.setObjectName("ProgramsDialog")
        
        self.__hasSearched = False
        
        self.programsList.headerItem().setText(self.programsList.columnCount(), "")
        
        self.searchButton = \
            self.buttonBox.addButton(self.trUtf8("Search"), QDialogButtonBox.ActionRole)
        self.searchButton.setToolTip(self.trUtf8("Press to search for programs"))
        
    def show(self):
        """
        Public slot to show the dialog.
        """
        QDialog.show(self)
        if not self.__hasSearched:
            self.on_programsSearchButton_clicked()
        
    def on_buttonBox_clicked(self, button):
        """
        Private slot called by a button of the button box clicked.
        
        @param button button that was clicked (QAbstractButton)
        """
        if button == self.searchButton:
            self.on_programsSearchButton_clicked()
        
    @pyqtSignature("")
    def on_programsSearchButton_clicked(self):
        """
        Private slot to search for all supported/required programs.
        """
        QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
        QApplication.processEvents()
        
        self.programsList.clear()
        header = self.programsList.header()
        header.setSortIndicator(0, Qt.AscendingOrder)
        header.setSortIndicatorShown(False)
        
        # 1. do the Qt4 programs
        # 1a. Translation Converter
        exe = Utilities.isWindowsPlatform() and \
            "%s.exe" % Utilities.generateQtToolName("lrelease") or \
            Utilities.generateQtToolName("lrelease")
        version = self.__createProgramEntry(self.trUtf8("Translation Converter (Qt4)"), 
                    exe, '-version', 'lrelease', -1)
        # 1b. Qt4 Designer
        exe = Utilities.isWindowsPlatform() and \
            "%s.exe" % Utilities.generateQtToolName("designer") or \
            Utilities.generateQtToolName("designer")
        self.__createProgramEntry(self.trUtf8("Qt4 Designer"), exe, version = version)
        # 1c. Qt4 Linguist
        exe = Utilities.isWindowsPlatform() and \
            "%s.exe" % Utilities.generateQtToolName("linguist") or \
            Utilities.generateQtToolName("linguist")
        self.__createProgramEntry(self.trUtf8("Qt4 Linguist"), exe, version = version)
        # 1d. Qt4 Assistant
        exe = Utilities.isWindowsPlatform() and \
            "%s.exe" % Utilities.generateQtToolName("assistant") or \
            Utilities.generateQtToolName("assistant")
        self.__createProgramEntry(self.trUtf8("Qt4 Assistant"), exe, version = version)
        
        # 2. do the PyQt programs
        # 2a. Translation Extractor PyQt4
        self.__createProgramEntry(self.trUtf8("Translation Extractor (Python, Qt4)"), 
            Utilities.isWindowsPlatform() and "pylupdate4.exe" or "pylupdate4", 
            '-version', 'pylupdate', -1)
        # 2b. Forms Compiler PyQt4
        self.__createProgramEntry(self.trUtf8("Forms Compiler (Python, Qt4)"), 
            Utilities.isWindowsPlatform() and "pyuic4.bat" or "pyuic4", 
            '--version', 'Python User', 4)
        # 2c. Resource Compiler PyQt4
        self.__createProgramEntry(self.trUtf8("Resource Compiler (Python, Qt4)"), 
            Utilities.isWindowsPlatform() and "pyrcc4.exe" or "pyrcc4", 
            '-version', 'Resource Compiler', -1)
        
        # 3. do the PySide programs
        # 3a. Translation Extractor PySide
        self.__createProgramEntry(self.trUtf8("Translation Extractor (Python, PySide)"), 
            Utilities.isWindowsPlatform() and "pyside-lupdate.exe" or "pyside-lupdate", 
            '-version', '', -1, versionRe = 'lupdate')
        # 3b. Forms Compiler PySide
        self.__createProgramEntry(self.trUtf8("Forms Compiler (Python, PySide)"), 
            Utilities.isWindowsPlatform() and "pyside-uic.bat" or "pyside-uic", 
            '--version', 'Python User', 4)
        # 3.c Resource Compiler PySide
        self.__createProgramEntry(self.trUtf8("Resource Compiler (Python, PySide)"), 
            Utilities.isWindowsPlatform() and "pyside-rcc4.exe" or "pyside-rcc4", 
            '-version', 'Resource Compiler', -1)
        
        # 4. do the Ruby programs
        # 4a. Forms Compiler for Qt4
        self.__createProgramEntry(self.trUtf8("Forms Compiler (Ruby, Qt4)"), 
            Utilities.isWindowsPlatform() and "rbuic4.exe" or "rbuic4", 
            '-version', 'Qt', -1)
        # 4b. Resource Compiler for Qt4
        self.__createProgramEntry(self.trUtf8("Resource Compiler (Ruby, Qt4)"), 
            Utilities.isWindowsPlatform() and "rbrcc.exe" or "rbrcc", 
            '-version', 'Ruby Resource Compiler', -1)
        
        # 5. do the Eric4 programs
        # 5a. Translation Previewer
        self.__createProgramEntry(self.trUtf8("Eric4 Translation Previewer"), 
            Utilities.isWindowsPlatform() and "eric4-trpreviewer.bat" or "eric4-trpreviewer", 
            '--version', 'Eric4', -2)
        # 5b. Forms Previewer
        self.__createProgramEntry(self.trUtf8("Eric4 Forms Previewer"), 
            Utilities.isWindowsPlatform() and "eric4-uipreviewer.bat" or "eric4-uipreviewer", 
            '--version', 'Eric4', -2)
        
        # 6. do the CORBA programs
        # 6a. omniORB
        exe = unicode(Preferences.getCorba("omniidl"))
        if Utilities.isWindowsPlatform():
            exe += ".exe"
        self.__createProgramEntry(self.trUtf8("CORBA IDL Compiler"), exe,
            '-V', 'omniidl', -1)
        
        # 7. do the spell checking entry
        try:
            import enchant
            try:
                text = os.path.dirname(enchant.__file__)
            except AttributeError:
                text = "enchant"
            try:
                version = enchant.__version__
            except AttributeError:
                version = self.trUtf8("(unknown)")
        except (ImportError, AttributeError, OSError):
            text = "enchant"
            version = ""
        self.__createEntry(self.trUtf8("Spell Checker - PyEnchant"), text, version)
        
        # do the plugin related programs
        pm = e4App().getObject("PluginManager")
        for info in pm.getPluginExeDisplayData():
            if info["programEntry"]:
                self.__createProgramEntry(
                    info["header"], 
                    info["exe"], 
                    versionCommand = info["versionCommand"], 
                    versionStartsWith = info["versionStartsWith"], 
                    versionPosition = info["versionPosition"], 
                    version = info["version"], 
                    versionCleanup = info["versionCleanup"], 
                )
            else:
                self.__createEntry(
                    info["header"], 
                    info["text"], 
                    info["version"]
                )
        
        self.programsList.sortByColumn(0, Qt.AscendingOrder)
        QApplication.restoreOverrideCursor()
        
        self.__hasSearched = True

    def __createProgramEntry(self, description, exe,
                             versionCommand = "", versionStartsWith = "", 
                             versionPosition = 0, version = "",
                             versionCleanup = None, versionRe = None):
        """
        Private method to generate a program entry.
        
        @param description descriptive text (string or QString)
        @param exe name of the executable program (string)
        @param versionCommand command line switch to get the version info (string)
            if this is empty, the given version will be shown.
        @param versionStartsWith start of line identifying version info (string)
        @param versionPosition index of part containing the version info (integer)
        @keyparam version version string to show (string)
        @keyparam versionCleanup tuple of two integers giving string positions
            start and stop for the version string (tuple of integers)
        @keyparam versionRe regexp to determine the line identifying version 
            info (string). Takes precedence over versionStartsWith.
        @return version string of detected or given version (string)
        """
        itm = QTreeWidgetItem(self.programsList, QStringList(description))
        font = itm.font(0)
        font.setBold(True)
        itm.setFont(0, font)
        if not exe:
            itm.setText(1, self.trUtf8("(not configured)"))
        else:
            if os.path.isabs(exe):
                if not Utilities.isExecutable(exe):
                    exe = ""
            else:
                exe = Utilities.getExecutablePath(exe)
            if exe:
                if versionCommand and versionStartsWith and versionPosition:
                    proc = QProcess()
                    proc.setProcessChannelMode(QProcess.MergedChannels)
                    proc.start(exe, QStringList(versionCommand))
                    finished = proc.waitForFinished(10000)
                    if finished:
                        output = \
                            unicode(proc.readAllStandardOutput(), 
                                    str(Preferences.getSystem("IOEncoding")), 
                                    'replace')
                        if versionRe is None:
                            versionRe = "^%s" % re.escape(versionStartsWith)
                        versionRe = re.compile(versionRe, re.UNICODE)
                        for line in output.splitlines():
                            if versionRe.search(line):
                                version = line.split()[versionPosition]
                                if versionCleanup:
                                    version = version[versionCleanup[0]:versionCleanup[1]]
                                break
                    else:
                        version = self.trUtf8("(not executable)")
                itm2 = QTreeWidgetItem(itm, QStringList() << exe << version)
                itm.setExpanded(True)
            else:
                itm.setText(1, self.trUtf8("(not found)"))
        QApplication.processEvents()
        self.programsList.header().resizeSections(QHeaderView.ResizeToContents)
        self.programsList.header().setStretchLastSection(True)
        return version
        
    def __createEntry(self, description, entryText, entryVersion):
        """
        Private method to generate a program entry.
        
        @param description descriptive text (string or QString)
        @param entryText text to show (string or QString)
        @param entryVersion version string to show (string or QString).
        """
        itm = QTreeWidgetItem(self.programsList, QStringList(description))
        font = itm.font(0)
        font.setBold(True)
        itm.setFont(0, font)
        
        if len(entryVersion):
            itm2 = QTreeWidgetItem(itm, QStringList() << entryText << entryVersion)
            itm.setExpanded(True)
        else:
            itm.setText(1, self.trUtf8("(not found)"))
        QApplication.processEvents()
        self.programsList.header().resizeSections(QHeaderView.ResizeToContents)
        self.programsList.header().setStretchLastSection(True)
