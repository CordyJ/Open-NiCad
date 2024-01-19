# -*- coding: utf-8 -*-

# Copyright (c) 2004 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a dialog to enter the parameters for eric4-api.
"""

import sys
import os
import copy

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from KdeQt import KQFileDialog

from E4Gui.E4Completers import E4FileCompleter, E4DirCompleter

from Ui_EricapiConfigDialog import Ui_EricapiConfigDialog
import Utilities
import DocumentationTools

from eric4config import getConfig

class EricapiConfigDialog(QDialog, Ui_EricapiConfigDialog):
    """
    Class implementing a dialog to enter the parameters for eric4-api.
    """
    def __init__(self, project, parms = None, parent = None):
        """
        Constructor
        
        @param project reference to the project object (Project.Project)
        @param parms parameters to set in the dialog
        @param parent parent widget of this dialog
        """
        QDialog.__init__(self,parent)
        self.setupUi(self)
        
        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)
        for language in sorted(DocumentationTools.supportedExtensionsDictForApis.keys()):
            self.languagesList.addItem(language)
        
        self.ppath = project.getProjectPath()
        self.project = project
        
        self.__initializeDefaults()
        
        # get a copy of the defaults to store the user settings
        self.parameters = copy.deepcopy(self.defaults)
        
        # combine it with the values of parms
        if parms is not None:
            for key, value in parms.items():
                self.parameters[key] = parms[key]
        
        self.outputFileCompleter = E4FileCompleter(self.outputFileEdit)
        self.ignoreDirCompleter = E4DirCompleter(self.ignoreDirEdit)
        
        self.recursionCheckBox.setChecked(self.parameters['useRecursion'])
        self.oldStyleCheckBox.setChecked(not self.parameters['newStyle'])
        self.includePrivateCheckBox.setChecked(self.parameters['includePrivate'])
        self.outputFileEdit.setText(self.parameters['outputFile'])
        self.baseEdit.setText(self.parameters['basePackage'])
        self.ignoreDirsList.clear()
        for d in self.parameters['ignoreDirectories']:
            self.ignoreDirsList.addItem(d)
        self.sourceExtEdit.setText(", ".join(self.parameters['sourceExtensions']))
        self.excludeFilesEdit.setText(", ".join(self.parameters['ignoreFilePatterns']))
        for language in self.parameters['languages']:
            items = self.languagesList.findItems(language, Qt.MatchFlags(Qt.MatchExactly))
            items[0].setSelected(True)
        
    def __initializeDefaults(self):
        """
        Private method to set the default values. 
        
        These are needed later on to generate the commandline
        parameters.
        """
        self.defaults = {
            'useRecursion' : False,
            'newStyle' : True,
            'includePrivate' : False, 
            'outputFile' : '',
            'basePackage' : '',
            'ignoreDirectories' : [],
            'ignoreFilePatterns' : [],
            'sourceExtensions' : [],
        }
        
        lang = self.project.getProjectLanguage()
        if lang in DocumentationTools.supportedExtensionsDictForApis.keys():
            self.defaults['languages'] = [lang]
        else:
            self.defaults['languages'] = ["Python"]
        
    def generateParameters(self):
        """
        Public method that generates the commandline parameters.
        
        It generates a QStringList to be used
        to set the QProcess arguments for the ericapi call and
        a list containing the non default parameters. The second
        list can be passed back upon object generation to overwrite
        the default settings.
        
        @return a tuple of the commandline parameters and non default parameters
            (QStringList, dictionary)
        """
        parms = {}
        args = QStringList()
        
        # 1. the program name
        args.append(sys.executable)
        args.append(Utilities.normabsjoinpath(getConfig('ericDir'), "eric4-api.py"))
        
        # 2. the commandline options
        if self.parameters['outputFile'] != self.defaults['outputFile']:
            parms['outputFile'] = self.parameters['outputFile']
            args.append('-o')
            if os.path.isabs(self.parameters['outputFile']):
                args.append(self.parameters['outputFile'])
            else:
                args.append(os.path.join(self.ppath, self.parameters['outputFile']))
        if self.parameters['basePackage'] != self.defaults['basePackage']:
            parms['basePackage'] = self.parameters['basePackage']
            args.append('-b')
            args.append(self.parameters['basePackage'])
        if self.parameters['ignoreDirectories'] != self.defaults['ignoreDirectories']:
            parms['ignoreDirectories'] = self.parameters['ignoreDirectories'][:]
            for d in self.parameters['ignoreDirectories']:
                args.append('-x')
                args.append(d)
        if self.parameters['ignoreFilePatterns'] != self.defaults['ignoreFilePatterns']:
            parms['ignoreFilePatterns'] = self.parameters['ignoreFilePatterns'][:]
            for pattern in self.parameters['ignoreFilePatterns']:
                args.append("--exclude-file=%s" % pattern)
        if self.parameters['useRecursion'] != self.defaults['useRecursion']:
            parms['useRecursion'] = self.parameters['useRecursion']
            args.append('-r')
        if self.parameters['sourceExtensions'] != self.defaults['sourceExtensions']:
            parms['sourceExtensions'] = self.parameters['sourceExtensions'][:]
            for ext in self.parameters['sourceExtensions']:
                args.append('-t')
                args.append(ext)
        if self.parameters['newStyle'] != self.defaults['newStyle']:
            parms['newStyle'] = self.parameters['newStyle']
            args.append('--oldstyle')
        if self.parameters['includePrivate'] != self.defaults['includePrivate']:
            parms['includePrivate'] = self.parameters['includePrivate']
            args.append('-p')
        parms['languages'] = self.parameters['languages'][:]
        for lang in self.parameters['languages']:
            args.append('--language=%s' % lang)
        
        return (args, parms)

    @pyqtSignature("")
    def on_outputFileButton_clicked(self):
        """
        Private slot to select the output file.
        
        It displays a file selection dialog to
        select the file the api is written to.
        """
        filename = KQFileDialog.getSaveFileName(\
            self,
            self.trUtf8("Select output file"),
            self.outputFileEdit.text(),
            self.trUtf8("API files (*.api);;All files (*)"))
            
        if not filename.isNull():
            # make it relative, if it is in a subdirectory of the project path 
            fn = unicode(Utilities.toNativeSeparators(filename))
            fn = fn.replace(self.ppath+os.sep, '')
            self.outputFileEdit.setText(fn)

    def on_outputFileEdit_textChanged(self, filename):
        """
        Private slot to enable/disable the "OK" button.
        
        @param filename name of the file (QString)
        """
        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(not filename.isEmpty())

    @pyqtSignature("")
    def on_ignoreDirButton_clicked(self):
        """
        Private slot to select a directory to be ignored.
        
        It displays a directory selection dialog to
        select a directory to be ignored.
        """
        startDir = self.ignoreDirEdit.text()
        if startDir.isEmpty():
            startDir = self.ppath
        directory = KQFileDialog.getExistingDirectory(\
            self,
            self.trUtf8("Select directory to exclude"),
            startDir,
            QFileDialog.Options(QFileDialog.ShowDirsOnly))
            
        if not directory.isNull():
            # make it relative, if it is a subdirectory of the project path 
            dn = unicode(Utilities.toNativeSeparators(directory))
            dn = dn.replace(self.ppath+os.sep, '')
            while dn.endswith(os.sep):
                dn = dn[:-1]
            self.ignoreDirEdit.setText(dn)
        
    @pyqtSignature("")
    def on_addButton_clicked(self):
        """
        Private slot to add the directory displayed to the listview.
        
        The directory in the ignore directories
        line edit is moved to the listbox above and the edit is cleared.
        """
        self.ignoreDirsList.addItem(os.path.basename(unicode(self.ignoreDirEdit.text())))
        self.ignoreDirEdit.clear()

    @pyqtSignature("")
    def on_deleteButton_clicked(self):
        """
        Private slot to delete the currently selected directory of the listbox.
        """
        itm = self.ignoreDirsList.takeItem(self.ignoreDirsList.currentRow())
        del itm

    def accept(self):
        """
        Protected slot called by the Ok button. 
        
        It saves the values in the parameters dictionary.
        """
        self.parameters['useRecursion'] = self.recursionCheckBox.isChecked()
        self.parameters['newStyle'] = not self.oldStyleCheckBox.isChecked()
        self.parameters['includePrivate'] = self.includePrivateCheckBox.isChecked()
        outfile = unicode(self.outputFileEdit.text())
        if outfile != '':
            outfile = os.path.normpath(outfile)
        self.parameters['outputFile'] = outfile
        self.parameters['basePackage'] = unicode(self.baseEdit.text())
        self.parameters['ignoreDirectories'] = []
        for row in range(0, self.ignoreDirsList.count()):
            itm = self.ignoreDirsList.item(row)
            self.parameters['ignoreDirectories'].append(\
                os.path.normpath(unicode(itm.text())))
        extensions = unicode(self.sourceExtEdit.text()).split(',')
        self.parameters['sourceExtensions'] = \
            [ext.strip() for ext in extensions if len(ext) > 0]
        patterns = unicode(self.excludeFilesEdit.text()).split(',')
        self.parameters['ignoreFilePatterns'] = \
            [pattern.strip() for pattern in patterns]
        self.parameters['languages'] = []
        for itm in self.languagesList.selectedItems():
            self.parameters['languages'].append(unicode(itm.text()))
        
        # call the accept slot of the base class
        QDialog.accept(self)
