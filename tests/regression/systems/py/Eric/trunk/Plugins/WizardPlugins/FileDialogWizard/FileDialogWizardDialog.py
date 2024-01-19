# -*- coding: utf-8 -*-

# Copyright (c) 2003 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the file dialog wizard dialog.
"""

import os

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from KdeQt.KQApplication import e4App

from E4Gui.E4Completers import E4FileCompleter, E4DirCompleter

from Ui_FileDialogWizardDialog import Ui_FileDialogWizardDialog

class FileDialogWizardDialog(QDialog, Ui_FileDialogWizardDialog):
    """
    Class implementing the color dialog wizard dialog.
    
    It displays a dialog for entering the parameters
    for the QFileDialog code generator.
    """
    def __init__(self, parent=None):
        """
        Constructor
        
        @param parent parent widget (QWidget)
        """
        QDialog.__init__(self, parent)
        self.setupUi(self)
        
        self.eStartWithCompleter = E4FileCompleter(self.eStartWith)
        self.eWorkDirCompleter = E4DirCompleter(self.eWorkDir)
        
        self.connect(self.rSaveFile, SIGNAL("toggled(bool)"), 
            self.__toggleConfirmCheckBox)
        self.connect(self.rDirectory, SIGNAL("toggled(bool)"), 
            self.__toggleGroupsAndTest)
        self.connect(self.cStartWith, SIGNAL("toggled(bool)"), 
            self.__toggleGroupsAndTest)
        self.connect(self.cWorkDir, SIGNAL("toggled(bool)"), 
            self.__toggleGroupsAndTest)
        self.connect(self.cFilters, SIGNAL("toggled(bool)"), 
            self.__toggleGroupsAndTest)
        
        self.bTest = \
            self.buttonBox.addButton(self.trUtf8("Test"), QDialogButtonBox.ActionRole)
        
    def on_buttonBox_clicked(self, button):
        """
        Private slot called by a button of the button box clicked.
        
        @param button button that was clicked (QAbstractButton)
        """
        if button == self.bTest:
            self.on_bTest_clicked()
    
    @pyqtSignature("")
    def on_bTest_clicked(self):
        """
        Private method to test the selected options.
        """
        if self.rOpenFile.isChecked():
            if not self.cSymlinks.isChecked():
                options = QFileDialog.Options(QFileDialog.DontResolveSymlinks)
            else:
                options = QFileDialog.Options()
            QFileDialog.getOpenFileName(\
                None,
                self.eCaption.text(),
                self.eStartWith.text(),
                self.eFilters.text(),
                None,
                options)
        elif self.rOpenFiles.isChecked():
            if not self.cSymlinks.isChecked():
                options = QFileDialog.Options(QFileDialog.DontResolveSymlinks)
            else:
                options = QFileDialog.Options()
            QFileDialog.getOpenFileNames(\
                None,
                self.eCaption.text(),
                self.eStartWith.text(),
                self.eFilters.text(),
                None,
                options)
        elif self.rSaveFile.isChecked():
            if not self.cSymlinks.isChecked():
                options = QFileDialog.Options(QFileDialog.DontResolveSymlinks)
            else:
                options = QFileDialog.Options()
            QFileDialog.getSaveFileName(\
                None,
                self.eCaption.text(),
                self.eStartWith.text(),
                self.eFilters.text(),
                None,
                options)
        elif self.rDirectory.isChecked():
            options = QFileDialog.Options()
            if not self.cSymlinks.isChecked():
                options |= QFileDialog.Options(QFileDialog.DontResolveSymlinks)
            if self.cDirOnly.isChecked():
                options |= QFileDialog.Options(QFileDialog.ShowDirsOnly)
            else:
                options |= QFileDialog.Options(QFileDialog.Option(0))
            QFileDialog.getExistingDirectory(\
                None,
                self.eCaption.text(),
                self.eWorkDir.text(),
                options)
        
    def __toggleConfirmCheckBox(self):
        """
        Private slot to enable/disable the confirmation check box.
        """
        self.cConfirmOverwrite.setEnabled(self.rSaveFile.isChecked())
        
    def __toggleGroupsAndTest(self):
        """
        Private slot to enable/disable certain groups and the test button.
        """
        if self.rDirectory.isChecked():
            self.filePropertiesGroup.setEnabled(False)
            self.dirPropertiesGroup.setEnabled(True)
            self.bTest.setDisabled(self.cWorkDir.isChecked())
        else:
            self.filePropertiesGroup.setEnabled(True)
            self.dirPropertiesGroup.setEnabled(False)
            self.bTest.setDisabled(\
                self.cStartWith.isChecked() or self.cFilters.isChecked())
        
    def __getCode4(self, indLevel, indString):
        """
        Private method to get the source code for Qt4.
        
        @param indLevel indentation level (int)
        @param indString string used for indentation (space or tab) (string)
        @return generated code (string)
        """
        # calculate our indentation level and the indentation string
        il = indLevel + 1
        istring = il * indString
        
        # now generate the code
        code = 'QFileDialog.'
        if self.rOpenFile.isChecked():
            code += 'getOpenFileName(\\%s%s' % (os.linesep, istring)
            code += 'None,%s%s' % (os.linesep, istring)
            if self.eCaption.text().isEmpty():
                code += 'QString(),%s%s' % (os.linesep, istring)
            else:
                code += 'self.trUtf8("%s"),%s%s' % \
                    (unicode(self.eCaption.text()), os.linesep, istring)
            if self.eStartWith.text().isEmpty():
                code += 'QString(),%s%s' % (os.linesep, istring)
            else:
                if self.cStartWith.isChecked():
                    fmt = '%s,%s%s'
                else:
                    fmt = 'self.trUtf8("%s"),%s%s'
                code += fmt % (unicode(self.eStartWith.text()), os.linesep, istring)
            if self.eFilters.text().isEmpty():
                code += 'QString()'
            else:
                if self.cFilters.isChecked(): 
                    fmt = '%s' 
                else: 
                    fmt = 'self.trUtf8("%s")' 
                code += fmt % unicode(self.eFilters.text()) 
            code += ',%s%sNone' % (os.linesep, istring)
            if not self.cSymlinks.isChecked():
                code += ',%s%sQFileDialog.Options(QFileDialog.DontResolveSymlinks)' % \
                        (os.linesep, istring)
            code += ')%s' % os.linesep
        elif self.rOpenFiles.isChecked():
            code += 'getOpenFileNames(\\%s%s' % (os.linesep, istring)
            code += 'None,%s%s' % (os.linesep, istring)
            if self.eCaption.text().isEmpty():
                code += 'QString(),%s%s' % (os.linesep, istring)
            else:
                code += 'self.trUtf8("%s"),%s%s' % \
                    (unicode(self.eCaption.text()), os.linesep, istring)
            if self.eStartWith.text().isEmpty():
                code += 'QString(),%s%s' % (os.linesep, istring)
            else:
                if self.cStartWith.isChecked():
                    fmt = '%s,%s%s'
                else:
                    fmt = 'self.trUtf8("%s"),%s%s'
                code += fmt % (unicode(self.eStartWith.text()), os.linesep, istring)
            if self.eFilters.text().isEmpty():
                code += 'QString()'
            else:
                if self.cFilters.isChecked(): 
                    fmt = '%s' 
                else: 
                    fmt = 'self.trUtf8("%s")' 
                code += fmt % unicode(self.eFilters.text()) 
            code += ',%s%sNone' % (os.linesep, istring)
            if not self.cSymlinks.isChecked():
                code += ',%s%sQFileDialog.Options(QFileDialog.DontResolveSymlinks)' % \
                        (os.linesep, istring)
            code += ')%s' % os.linesep
        elif self.rSaveFile.isChecked():
            code += 'getSaveFileName(\\%s%s' % (os.linesep, istring)
            code += 'None,%s%s' % (os.linesep, istring)
            if self.eCaption.text().isEmpty():
                code += 'QString(),%s%s' % (os.linesep, istring)
            else:
                code += 'self.trUtf8("%s"),%s%s' % \
                    (unicode(self.eCaption.text()), os.linesep, istring)
            if self.eStartWith.text().isEmpty():
                code += 'QString(),%s%s' % (os.linesep, istring)
            else:
                if self.cStartWith.isChecked():
                    fmt = '%s,%s%s'
                else:
                    fmt = 'self.trUtf8("%s"),%s%s'
                code += fmt % (unicode(self.eStartWith.text()), os.linesep, istring)
            if self.eFilters.text().isEmpty():
                code += 'QString()'
            else:
                if self.cFilters.isChecked(): 
                    fmt = '%s' 
                else: 
                    fmt = 'self.trUtf8("%s")' 
                code += fmt % unicode(self.eFilters.text()) 
            code += ',%s%sNone' % (os.linesep, istring)
            if (not self.cSymlinks.isChecked()) or \
               (not self.cConfirmOverwrite.isChecked()):
                code += ',%s%sQFileDialog.Options(' % (os.linesep, istring)
                if not self.cSymlinks.isChecked():
                    code += 'QFileDialog.DontResolveSymlinks'
                if (not self.cSymlinks.isChecked()) and \
                   (not self.cConfirmOverwrite.isChecked()):
                    code += ' | '
                if not self.cConfirmOverwrite.isChecked():
                    code += 'QFileDialog.DontConfirmOverwrite'
                code += ')'
            code += ')%s' % os.linesep
        elif self.rDirectory.isChecked():
            code += 'getExistingDirectory(\\%s%s' % (os.linesep, istring)
            code += 'None,%s%s' % (os.linesep, istring)
            if self.eCaption.text().isEmpty():
                code += 'QString(),%s%s' % (os.linesep, istring)
            else:
                code += 'self.trUtf8("%s"),%s%s' % \
                    (unicode(self.eCaption.text()), os.linesep, istring)
            if self.eWorkDir.text().isEmpty():
                code += 'QString()'
            else:
                if self.cWorkDir.isChecked():
                    fmt = '%s'
                else:
                    fmt = 'self.trUtf8("%s")'
                code += fmt % unicode(self.eWorkDir.text())
            code += ',%s%sQFileDialog.Options(' % (os.linesep, istring)
            if not self.cSymlinks.isChecked():
                code += 'QFileDialog.DontResolveSymlinks | '
            if self.cDirOnly.isChecked():
                code += 'QFileDialog.ShowDirsOnly'
            else:
                code += 'QFileDialog.Option(0)'
            code += '))%s' % os.linesep
            
        return code
        
    def getCode(self, indLevel, indString):
        """
        Public method to get the source code.
        
        @param indLevel indentation level (int)
        @param indString string used for indentation (space or tab) (string)
        @return generated code (string)
        """
        return self.__getCode4(indLevel, indString)
