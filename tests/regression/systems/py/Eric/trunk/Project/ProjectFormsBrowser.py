# -*- coding: utf-8 -*-

# Copyright (c) 2002 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a class used to display the forms part of the project.
"""

import os
import sys
import shutil

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from KdeQt import KQFileDialog, KQMessageBox, KQInputDialog
from KdeQt.KQProgressDialog import KQProgressDialog
from KdeQt.KQApplication import e4App

from ProjectBrowserModel import ProjectBrowserFileItem, \
    ProjectBrowserSimpleDirectoryItem, ProjectBrowserDirectoryItem, \
    ProjectBrowserFormType
from ProjectBaseBrowser import ProjectBaseBrowser

from UI.DeleteFilesConfirmationDialog import DeleteFilesConfirmationDialog
import UI.PixmapCache

import Preferences
import Utilities

from eric4config import getConfig

class ProjectFormsBrowser(ProjectBaseBrowser):
    """
    A class used to display the forms part of the project. 
    
    @signal appendStderr(string) emitted after something was received from
            a QProcess on stderr
    @signal sourceFile(string) emitted to open a forms file in an editor
    @signal uipreview(string) emitted to preview a forms file
    @signal trpreview(string list) emitted to preview form files in the 
            translations previewer
    @signal closeSourceWindow(string) emitted after a file has been removed/deleted 
            from the project
    @signal showMenu(string, QMenu) emitted when a menu is about to be shown. The name
            of the menu and a reference to the menu are given.
    @signal menusAboutToBeCreated emitted when the context menu are about to
            be created. This is the right moment to add or remove hook methods.
    """
    def __init__(self, project, parent = None):
        """
        Constructor
        
        @param project reference to the project object
        @param parent parent widget of this browser (QWidget)
        """
        ProjectBaseBrowser.__init__(self, project, ProjectBrowserFormType, parent)
        
        self.selectedItemsFilter = \
            [ProjectBrowserFileItem, ProjectBrowserSimpleDirectoryItem]
        
        self.setWindowTitle(self.trUtf8('Forms'))

        self.setWhatsThis(self.trUtf8(
            """<b>Project Forms Browser</b>"""
            """<p>This allows to easily see all forms contained in the current"""
            """ project. Several actions can be executed via the context menu.</p>"""
        ))
        
        # templates for Qt3
        # these two lists have to stay in sync
        self.templates = ['dialog.tmpl', 'wizard.tmpl', 'widget.tmpl', \
            'configurationdialog.tmpl', 'dialogbuttonsbottom.tmpl', \
            'dialogbuttonsright.tmpl', 'tabdialog.tmpl']
        self.templateTypes = [ \
            unicode(self.trUtf8("Dialog")),
            unicode(self.trUtf8("Wizard")),
            unicode(self.trUtf8("Widget")),
            unicode(self.trUtf8("Configuration Dialog")),
            unicode(self.trUtf8("Dialog with Buttons (Bottom)")),
            unicode(self.trUtf8("Dialog with Buttons (Right)")),
            unicode(self.trUtf8("Tab Dialog"))
        ]
        self.formTypeList = QStringList()
        for tType in self.templateTypes:
            self.formTypeList.append(tType)
        
        # templates for Qt4
        # these two lists have to stay in sync
        self.templates4 = ['dialog4.tmpl', 'widget4.tmpl', 'mainwindow4.tmpl',
            'dialogbuttonboxbottom4.tmpl', 'dialogbuttonboxright4.tmpl',
            'dialogbuttonsbottom4.tmpl', 'dialogbuttonsbottomcenter4.tmpl',
            'dialogbuttonsright4.tmpl']
        self.templateTypes4 = [ \
            unicode(self.trUtf8("Dialog")),
            unicode(self.trUtf8("Widget")),
            unicode(self.trUtf8("Main Window")),
            unicode(self.trUtf8("Dialog with Buttonbox (Bottom)")),
            unicode(self.trUtf8("Dialog with Buttonbox (Right)")),
            unicode(self.trUtf8("Dialog with Buttons (Bottom)")),
            unicode(self.trUtf8("Dialog with Buttons (Bottom-Center)")),
            unicode(self.trUtf8("Dialog with Buttons (Right)")),
        ]
        self.formTypeList4 = QStringList()
        for tType in self.templateTypes4:
            self.formTypeList4.append(tType)
        
        self.compileProc = None
        
    def _createPopupMenus(self):
        """
        Protected overloaded method to generate the popup menu.
        """
        self.menuActions = []
        self.formActions = []
        self.multiMenuActions = []
        self.multiFormActions = []
        self.dirMenuActions = []
        self.dirMultiMenuActions = []
        
        self.emit(SIGNAL("menusAboutToBeCreated"))
        
        self.menu = QMenu(self)
        if self.project.getProjectType() in ["Qt4", "Kde4", "E4Plugin", "PySide"]:
            act = self.menu.addAction(self.trUtf8('Compile form'), self.__compileForm)
            self.formActions.append(act)
            act = self.menu.addAction(self.trUtf8('Compile all forms'), 
                self.__compileAllForms)
            self.formActions.append(act)
            act = \
                self.menu.addAction(self.trUtf8('Generate Dialog Code...'),
                    self.__generateDialogCode)
            self.formActions.append(act)
            self.menu.addSeparator()
            act = self.menu.addAction(self.trUtf8('Open in Qt-Designer'), self.__openFile)
            self.formActions.append(act)
            self.menu.addAction(self.trUtf8('Open in Editor'), self.__openFileInEditor)
            self.menu.addSeparator()
            self.menu.addAction(self.trUtf8('Preview form'), self.__UIPreview)
            self.menu.addAction(self.trUtf8('Preview translations'), self.__TRPreview)
        else:
            if self.hooks["compileForm"] is not None:
                act = self.menu.addAction(
                    self.hooksMenuEntries.get("compileForm", 
                        self.trUtf8('Compile form')), self.__compileForm)
                self.formActions.append(act)
            if self.hooks["compileAllForms"] is not None:
                act = self.menu.addAction(
                    self.hooksMenuEntries.get("compileAllForms", 
                        self.trUtf8('Compile all forms')), 
                    self.__compileAllForms)
                self.formActions.append(act)
            if self.hooks["generateDialogCode"] is not None:
                act = self.menu.addAction(
                    self.hooksMenuEntries.get("generateDialogCode", 
                        self.trUtf8('Generate Dialog Code...')),
                    self.__generateDialogCode)
                self.formActions.append(act)
            if self.hooks["compileForm"] is not None or \
               self.hooks["compileAllForms"] is not None or \
               self.hooks["generateDialogCode"] is not None:
                self.menu.addSeparator()
            self.menu.addAction(self.trUtf8('Open'), self.__openFileInEditor)
        self.menu.addSeparator()
        act = self.menu.addAction(self.trUtf8('Rename file'), self._renameFile)
        self.menuActions.append(act)
        act = self.menu.addAction(self.trUtf8('Remove from project'), self._removeFile)
        self.menuActions.append(act)
        act = self.menu.addAction(self.trUtf8('Delete'), self.__deleteFile)
        self.menuActions.append(act)
        self.menu.addSeparator()
        if self.project.getProjectType() in ["Qt4", "Kde4", "E4Plugin", "PySide"]:
            self.menu.addAction(self.trUtf8('New form...'), self.__newForm)
        else:
            if self.hooks["newForm"] is not None:
                self.menu.addAction(
                    self.hooksMenuEntries.get("newForm", 
                        self.trUtf8('New form...')), self.__newForm)
        self.menu.addAction(self.trUtf8('Add forms...'), self.__addFormFiles)
        self.menu.addAction(self.trUtf8('Add forms directory...'), 
            self.__addFormsDirectory)
        self.menu.addSeparator()
        self.menu.addAction(self.trUtf8('Copy Path to Clipboard'), 
            self._copyToClipboard)
        self.menu.addSeparator()
        self.menu.addAction(self.trUtf8('Expand all directories'), 
            self._expandAllDirs)
        self.menu.addAction(self.trUtf8('Collapse all directories'), 
            self._collapseAllDirs)
        self.menu.addSeparator()
        self.menu.addAction(self.trUtf8('Configure...'), self._configure)

        self.backMenu = QMenu(self)
        if self.project.getProjectType() in ["Qt4", "Kde4", "E4Plugin", "PySide"] or \
           self.hooks["compileAllForms"] is not None:
            self.backMenu.addAction(self.trUtf8('Compile all forms'), 
                self.__compileAllForms)
            self.backMenu.addSeparator()
            self.backMenu.addAction(self.trUtf8('New form...'), self.__newForm)
        else:
            if self.hooks["newForm"] is not None:
                self.backMenu.addAction(
                    self.hooksMenuEntries.get("newForm", 
                        self.trUtf8('New form...')), self.__newForm)
        self.backMenu.addAction(self.trUtf8('Add forms...'), self.project.addUiFiles)
        self.backMenu.addAction(self.trUtf8('Add forms directory...'), 
            self.project.addUiDir)
        self.backMenu.addSeparator()
        self.backMenu.addAction(self.trUtf8('Expand all directories'), 
            self._expandAllDirs)
        self.backMenu.addAction(self.trUtf8('Collapse all directories'), 
            self._collapseAllDirs)
        self.backMenu.addSeparator()
        self.backMenu.addAction(self.trUtf8('Configure...'), self._configure)
        self.backMenu.setEnabled(False)

        # create the menu for multiple selected files
        self.multiMenu = QMenu(self)
        if self.project.getProjectType() in ["Qt4", "Kde4", "E4Plugin", "PySide"]:
            act = self.multiMenu.addAction(self.trUtf8('Compile forms'), 
                self.__compileSelectedForms)
            self.multiMenu.addSeparator()
            act = self.multiMenu.addAction(self.trUtf8('Open in Qt-Designer'), 
                self.__openFile)
            self.multiFormActions.append(act)
            self.multiMenu.addAction(self.trUtf8('Open in Editor'), 
                self.__openFileInEditor)
            self.multiMenu.addSeparator()
            self.multiMenu.addAction(self.trUtf8('Preview translations'), 
                self.__TRPreview)
        else:
            if self.hooks["compileSelectedForms"] is not None:
                act = self.multiMenu.addAction(
                    self.hooksMenuEntries.get("compileSelectedForms", 
                        self.trUtf8('Compile forms')), 
                    self.__compileSelectedForms)
                self.multiMenu.addSeparator()
            self.multiMenu.addAction(self.trUtf8('Open'), self.__openFileInEditor)
        self.multiMenu.addSeparator()
        act = self.multiMenu.addAction(self.trUtf8('Remove from project'), 
            self._removeFile)
        self.multiMenuActions.append(act)
        act = self.multiMenu.addAction(self.trUtf8('Delete'), self.__deleteFile)
        self.multiMenuActions.append(act)
        self.multiMenu.addSeparator()
        self.multiMenu.addAction(self.trUtf8('Expand all directories'), 
            self._expandAllDirs)
        self.multiMenu.addAction(self.trUtf8('Collapse all directories'), 
            self._collapseAllDirs)
        self.multiMenu.addSeparator()
        self.multiMenu.addAction(self.trUtf8('Configure...'), self._configure)

        self.dirMenu = QMenu(self)
        if self.project.getProjectType() in ["Qt4", "Kde4", "E4Plugin", "PySide"]:
            self.dirMenu.addAction(self.trUtf8('Compile all forms'), 
                self.__compileAllForms)
            self.dirMenu.addSeparator()
        else:
            if self.hooks["compileAllForms"] is not None:
                self.dirMenu.addAction(
                    self.hooksMenuEntries.get("compileAllForms", 
                        self.trUtf8('Compile all forms')), 
                    self.__compileAllForms)
                self.dirMenu.addSeparator()
        act = self.dirMenu.addAction(self.trUtf8('Remove from project'), self._removeDir)
        self.dirMenuActions.append(act)
        self.dirMenu.addSeparator()
        if self.project.getProjectType() in ["Qt4", "Kde4", "E4Plugin", "PySide"]:
            self.dirMenu.addAction(self.trUtf8('New form...'), self.__newForm)
        else:
            if self.hooks["newForm"] is not None:
                self.dirMenu.addAction(
                    self.hooksMenuEntries.get("newForm", 
                        self.trUtf8('New form...')), self.__newForm)
        self.dirMenu.addAction(self.trUtf8('Add forms...'), self.__addFormFiles)
        self.dirMenu.addAction(self.trUtf8('Add forms directory...'), 
            self.__addFormsDirectory)
        self.dirMenu.addSeparator()
        self.dirMenu.addAction(self.trUtf8('Copy Path to Clipboard'), 
            self._copyToClipboard)
        self.dirMenu.addSeparator()
        self.dirMenu.addAction(self.trUtf8('Expand all directories'), 
            self._expandAllDirs)
        self.dirMenu.addAction(self.trUtf8('Collapse all directories'), 
            self._collapseAllDirs)
        self.dirMenu.addSeparator()
        self.dirMenu.addAction(self.trUtf8('Configure...'), self._configure)
        
        self.dirMultiMenu = QMenu(self)
        if self.project.getProjectType() in ["Qt4", "Kde4", "E4Plugin", "PySide"]:
            self.dirMultiMenu.addAction(self.trUtf8('Compile all forms'), 
                self.__compileAllForms)
            self.dirMultiMenu.addSeparator()
        else:
           if self.hooks["compileAllForms"] is not None:
                self.dirMultiMenu.addAction(
                    self.hooksMenuEntries.get("compileAllForms", 
                        self.trUtf8('Compile all forms')), 
                    self.__compileAllForms)
                self.dirMultiMenu.addSeparator()
        self.dirMultiMenu.addAction(self.trUtf8('Add forms...'), 
            self.project.addUiFiles)
        self.dirMultiMenu.addAction(self.trUtf8('Add forms directory...'), 
            self.project.addUiDir)
        self.dirMultiMenu.addSeparator()
        self.dirMultiMenu.addAction(self.trUtf8('Expand all directories'), 
            self._expandAllDirs)
        self.dirMultiMenu.addAction(self.trUtf8('Collapse all directories'), 
            self._collapseAllDirs)
        self.dirMultiMenu.addSeparator()
        self.dirMultiMenu.addAction(self.trUtf8('Configure...'), self._configure)
        
        self.connect(self.menu, SIGNAL('aboutToShow()'),
            self.__showContextMenu)
        self.connect(self.multiMenu, SIGNAL('aboutToShow()'),
            self.__showContextMenuMulti)
        self.connect(self.dirMenu, SIGNAL('aboutToShow()'),
            self.__showContextMenuDir)
        self.connect(self.dirMultiMenu, SIGNAL('aboutToShow()'),
            self.__showContextMenuDirMulti)
        self.connect(self.backMenu, SIGNAL('aboutToShow()'),
            self.__showContextMenuBack)
        self.mainMenu = self.menu
        
    def _contextMenuRequested(self, coord):
        """
        Protected slot to show the context menu.
        
        @param coord the position of the mouse pointer (QPoint)
        """
        if not self.project.isOpen():
            return
        
        try:
            categories = self.getSelectedItemsCountCategorized(\
                [ProjectBrowserFileItem, ProjectBrowserSimpleDirectoryItem])
            cnt = categories["sum"]
            if cnt <= 1:
                index = self.indexAt(coord)
                if index.isValid():
                    self._selectSingleItem(index)
                    categories = self.getSelectedItemsCountCategorized(\
                        [ProjectBrowserFileItem, ProjectBrowserSimpleDirectoryItem])
                    cnt = categories["sum"]
            
            bfcnt = categories[unicode(ProjectBrowserFileItem)]
            sdcnt = categories[unicode(ProjectBrowserSimpleDirectoryItem)]
            if cnt > 1 and cnt == bfcnt:
                self.multiMenu.popup(self.mapToGlobal(coord))
            elif cnt > 1 and cnt == sdcnt:
                self.dirMultiMenu.popup(self.mapToGlobal(coord))
            else:
                index = self.indexAt(coord)
                if cnt == 1 and index.isValid():
                    if bfcnt == 1:
                        self.menu.popup(self.mapToGlobal(coord))
                    elif sdcnt == 1:
                        self.dirMenu.popup(self.mapToGlobal(coord))
                    else:
                        self.backMenu.popup(self.mapToGlobal(coord))
                else:
                    self.backMenu.popup(self.mapToGlobal(coord))
        except:
            pass
        
    def __showContextMenu(self):
        """
        Private slot called by the menu aboutToShow signal.
        """
        itm = self.model().item(self.currentIndex())
        if itm.isDesignerHeaderFile():
            enable = False
        else:
            enable = True
        for act in self.formActions:
            act.setEnabled(enable)
        ProjectBaseBrowser._showContextMenu(self, self.menu)
        
        self.emit(SIGNAL("showMenu"), "Main", self.menu)
        
    def __showContextMenuMulti(self):
        """
        Private slot called by the multiMenu aboutToShow signal.
        """
        items = self.getSelectedItems()
        if self.__itemsHaveDesignerHeaderFiles(items):
            enable = False
        else:
            enable = True
        for act in self.multiFormActions:
            act.setEnabled(enable)
        ProjectBaseBrowser._showContextMenuMulti(self, self.multiMenu)
        
        self.emit(SIGNAL("showMenu"), "MainMulti", self.multiMenu)
        
    def __showContextMenuDir(self):
        """
        Private slot called by the dirMenu aboutToShow signal.
        """
        ProjectBaseBrowser._showContextMenuDir(self, self.dirMenu)
        
        self.emit(SIGNAL("showMenu"), "MainDir", self.dirMenu)
        
    def __showContextMenuDirMulti(self):
        """
        Private slot called by the dirMultiMenu aboutToShow signal.
        """
        ProjectBaseBrowser._showContextMenuDirMulti(self, self.dirMultiMenu)
        
        self.emit(SIGNAL("showMenu"), "MainDirMulti", self.dirMultiMenu)
        
    def __showContextMenuBack(self):
        """
        Private slot called by the backMenu aboutToShow signal.
        """
        ProjectBaseBrowser._showContextMenuBack(self, self.backMenu)
        
        self.emit(SIGNAL("showMenu"), "MainBack", self.backMenu)
        
    def __itemsHaveDesignerHeaderFiles(self, items):
        """
        Private method to check, if items contain designer header files.
        
        @param items items to check (list of ProjectBrowserFileItems)
        @return flag indicating designer header files were found (boolean)
        """
        for itm in items:
            if itm.isDesignerHeaderFile():
                return True
        return False
        
    def __addFormFiles(self):
        """
        Private method to add form files to the project.
        """
        itm = self.model().item(self.currentIndex())
        if isinstance(itm, ProjectBrowserFileItem):
            dn = os.path.dirname(unicode(itm.fileName()))
        elif isinstance(itm, ProjectBrowserSimpleDirectoryItem) or \
             isinstance(itm, ProjectBrowserDirectoryItem):
            dn = unicode(itm.dirName())
        else:
            dn = None
        self.project.addFiles('form', dn)
        
    def __addFormsDirectory(self):
        """
        Private method to add form files of a directory to the project.
        """
        itm = self.model().item(self.currentIndex())
        if isinstance(itm, ProjectBrowserFileItem):
            dn = os.path.dirname(unicode(itm.fileName()))
        elif isinstance(itm, ProjectBrowserSimpleDirectoryItem) or \
             isinstance(itm, ProjectBrowserDirectoryItem):
            dn = unicode(itm.dirName())
        else:
            dn = None
        self.project.addDirectory('form', dn)
        
    def __openFile(self):
        """
        Private slot to handle the Open menu action.
        
        This uses the projects UI type to determine the Qt Designer
        version to use.
        """
        if self.project.getProjectType() in ["Qt4", "Kde4", "E4Plugin", "PySide"]:
            version = 4
        else:
            version = 3
        
        itmList = self.getSelectedItems()
        for itm in itmList[:]:
            try:
                if isinstance(itm, ProjectBrowserFileItem):
                    self.emit(SIGNAL('designerFile'), itm.fileName(), version)
            except:
                pass
        
    def __openFileInEditor(self):
        """
        Private slot to handle the Open in Editor menu action.
        """
        itmList = self.getSelectedItems()
        for itm in itmList[:]:
            self.emit(SIGNAL('sourceFile'), itm.fileName())
        
    def _openItem(self):
        """
        Protected slot to handle the open popup menu entry.
        """
        itmList = self.getSelectedItems()
        
        for itm in itmList:
            if isinstance(itm, ProjectBrowserFileItem):
                if itm.isDesignerFile():
                    self.emit(SIGNAL('designerFile'), itm.fileName())
                else:
                    self.emit(SIGNAL('sourceFile'), itm.fileName())
        
    def __UIPreview(self):
        """
        Private slot to handle the Preview menu action.
        """
        itmList = self.getSelectedItems()
        self.emit(SIGNAL('uipreview'), itmList[0].fileName())
        
    def __TRPreview(self):
        """
        Private slot to handle the Preview translations action.
        """
        fileNames = []
        for itm in self.getSelectedItems():
            fileNames.append(itm.fileName())
        trfiles = self.project.pdata["TRANSLATIONS"][:]
        trfiles.sort()
        fileNames.extend([os.path.join(self.project.ppath, trfile) \
                          for trfile in trfiles \
                          if trfile.endswith('.qm')])
        self.emit(SIGNAL('trpreview'), fileNames)
        
    def __newForm(self):
        """
        Private slot to handle the New Form menu action.
        """
        itm = self.model().item(self.currentIndex())
        if itm is None:
            path = self.project.ppath
        else:
            try:
                path = os.path.dirname(unicode(itm.fileName()))
            except AttributeError:
                path = os.path.join(self.project.ppath, unicode(itm.data(0)))
        
        if self.hooks["newForm"] is not None:
            self.hooks["newForm"](path)
        else:
            if self.project.getProjectType() in ["Qt4", "Kde4", "E4Plugin", "PySide"]:
                self.__newUiForm(path)
        
    def __newUiForm(self, path):
        """
        Private slot to handle the New Form menu action for Qt-related projects.
        
        @param path full directory path for the new form file (string)
        """
        selectedForm, ok = KQInputDialog.getItem(\
            None,
            self.trUtf8("New Form"),
            self.trUtf8("Select a form type:"),
            self.project.getProjectType() in ["Qt4", "Kde4", "E4Plugin", "PySide"] and \
                self.formTypeList4 or self.formTypeList,
            0, False)
        if not ok:
            # user pressed cancel
            return
        
        templateIndex = \
            self.project.getProjectType() in ["Qt4", "Kde4", "E4Plugin", "PySide"] and \
                self.templateTypes4.index(unicode(selectedForm)) or \
                self.templateTypes.index(unicode(selectedForm))
        templateFile = os.path.join(getConfig('ericTemplatesDir'),
            self.project.getProjectType() in ["Qt4", "Kde4", "E4Plugin""PySide"] and \
            self.templates4[templateIndex] or \
            self.templates[templateIndex])
        
        selectedFilter = QString("")
        fname = KQFileDialog.getSaveFileName(\
            self,
            self.trUtf8("New Form"),
            path,
            self.trUtf8("Qt User-Interface Files (*.ui);;All Files (*)"),
            selectedFilter,
            QFileDialog.Options(QFileDialog.DontConfirmOverwrite))
        
        if fname.isEmpty():
            # user aborted or didn't enter a filename
            return
        
        ext = QFileInfo(fname).suffix()
        if ext.isEmpty():
            ex = selectedFilter.section('(*',1,1).section(')',0,0)
            if not ex.isEmpty():
                fname.append(ex)
        
        fname = unicode(fname)
        if os.path.exists(fname):
            res = KQMessageBox.warning(self,
                self.trUtf8("New Form"),
                self.trUtf8("The file already exists! Overwrite it?"),
                QMessageBox.StandardButtons(\
                    QMessageBox.No | \
                    QMessageBox.Yes),
                QMessageBox.No)
            if res != QMessageBox.Yes:
                # user selected to not overwrite
                return
        
        try:
            shutil.copy(templateFile, fname)
        except IOError, e:
            KQMessageBox.critical(self,
                self.trUtf8("New Form"),
                self.trUtf8("<p>The new form file <b>%1</b> could not be created.<br>"
                    "Problem: %2</p>").arg(fname).arg(unicode(e)))
            return
        
        self.project.appendFile(fname)
        self.emit(SIGNAL('designerFile'), fname)
        
    def __deleteFile(self):
        """
        Private method to delete a form file from the project.
        """
        itmList = self.getSelectedItems()
        
        files = []
        fullNames = []
        for itm in itmList:
            fn2 = unicode(itm.fileName())
            fullNames.append(fn2)
            fn = fn2.replace(self.project.ppath+os.sep, '')
            files.append(fn)
        
        dlg = DeleteFilesConfirmationDialog(self.parent(),
            self.trUtf8("Delete forms"),
            self.trUtf8("Do you really want to delete these forms from the project?"),
            files)
        
        if dlg.exec_() == QDialog.Accepted:
            for fn2, fn in zip(fullNames, files):
                self.emit(SIGNAL('closeSourceWindow'), fn2)
                self.project.deleteFile(fn)
    
    ############################################################################
    ##  Methods to handle the various compile commands
    ############################################################################
    
    def __readStdout(self):
        """
        Private slot to handle the readyReadStandardOutput signal of the 
        pyuic/rbuic process.
        """
        if self.compileProc is None:
            return
        self.compileProc.setReadChannel(QProcess.StandardOutput)
        
        while self.compileProc and self.compileProc.canReadLine():
            self.buf.append(self.compileProc.readLine())
        
    def __readStderr(self):
        """
        Private slot to handle the readyReadStandardError signal of the 
        pyuic/rbuic process.
        """
        if self.compileProc is None:
            return
        
        ioEncoding = str(Preferences.getSystem("IOEncoding"))
        
        self.compileProc.setReadChannel(QProcess.StandardError)
        while self.compileProc and self.compileProc.canReadLine():
            s = QString(self.uicompiler + ': ')
            error = unicode(self.compileProc.readLine(), 
                            ioEncoding, 'replace')
            s.append(error)
            self.emit(SIGNAL('appendStderr'), s)
        
    def __compileUIDone(self, exitCode, exitStatus):
        """
        Private slot to handle the finished signal of the pyuic/rbuic process.
        
        @param exitCode exit code of the process (integer)
        @param exitStatus exit status of the process (QProcess.ExitStatus)
        """
        self.compileRunning = False
        e4App().getObject("ViewManager").enableEditorsCheckFocusIn(True)
        if exitStatus == QProcess.NormalExit and exitCode == 0 and self.buf:
            ofn = os.path.join(self.project.ppath, self.compiledFile)
            try:
                f = open(ofn, "wb")
                for line in unicode(self.buf).splitlines():
                    f.write(line.encode("utf8") + os.linesep)
                f.close()
                if self.compiledFile not in self.project.pdata["SOURCES"]:
                    self.project.appendFile(ofn)
                if not self.noDialog:
                    KQMessageBox.information(None,
                        self.trUtf8("Form Compilation"),
                        self.trUtf8("The compilation of the form file"
                            " was successful."))
            except IOError, msg:
                if not self.noDialog:
                    KQMessageBox.information(None,
                        self.trUtf8("Form Compilation"),
                        self.trUtf8("<p>The compilation of the form file failed.</p>"
                            "<p>Reason: %1</p>").arg(unicode(msg)))
        else:
            if not self.noDialog:
                KQMessageBox.information(None,
                    self.trUtf8("Form Compilation"),
                    self.trUtf8("The compilation of the form file failed."))
        self.compileProc = None
        
    def __compileUI(self, fn, noDialog = False, progress = None):
        """
        Privat method to compile a .ui file to a .py/.rb file.
        
        @param fn filename of the .ui file to be compiled
        @param noDialog flag indicating silent operations
        @param progress reference to the progress dialog
        @return reference to the compile process (QProcess)
        """
        self.compileProc = QProcess()
        args = QStringList()
        self.buf = QString("")
        
        if self.project.pdata["PROGLANGUAGE"][0] in ["Python", "Python3"]:
            if self.project.getProjectType() in ["Qt4", "E4Plugin"]:
                self.uicompiler = 'pyuic4'
                if Utilities.isWindowsPlatform():
                    uic = self.uicompiler + '.bat'
                else:
                    uic = self.uicompiler
            elif self.project.getProjectType() == "Kde4":
                self.uicompiler = 'pykdeuic4'
                if Utilities.isWindowsPlatform():
                    uic = self.uicompiler + '.bat'
                else:
                    uic = self.uicompiler
            elif self.project.getProjectType() == "PySide":
                self.uicompiler = 'pyside-uic'
                if Utilities.isWindowsPlatform():
                    uic = self.uicompiler + '.bat'
                else:
                    uic = self.uicompiler
            else:
                return None
        elif self.project.pdata["PROGLANGUAGE"][0] == "Ruby":
            if self.project.getProjectType() == "Qt4":
                self.uicompiler = 'rbuic4'
                if Utilities.isWindowsPlatform():
                    uic = self.uicompiler + '.exe'
                else:
                    uic = self.uicompiler
            else:
                return None
        else:
            return None
        
        ofn, ext = os.path.splitext(fn)
        fn = os.path.join(self.project.ppath, fn)
        
        if self.project.pdata["PROGLANGUAGE"][0] in ["Python", "Python3"]:
            if self.project.getProjectType() in ["Qt4", "Kde4", "E4Plugin", "PySide"]:
                dirname, filename = os.path.split(ofn)
                self.compiledFile = os.path.join(dirname, "Ui_" + filename + ".py")
            else:
                self.compiledFile = ofn + '.py'
            if self.project.getProjectType() == "Kde4":
                args.append("-e")
            else:
                args.append("-x")
        elif self.project.pdata["PROGLANGUAGE"][0] == "Ruby":
            self.compiledFile = ofn + '.rb'
            if self.project.getProjectType() in ["Kde4"]:
                args.append('-kde')
            args.append('-x')
        
        args.append(fn)
        self.connect(self.compileProc, SIGNAL('finished(int, QProcess::ExitStatus)'),
            self.__compileUIDone)
        self.connect(self.compileProc, SIGNAL('readyReadStandardOutput()'), 
            self.__readStdout)
        self.connect(self.compileProc, SIGNAL('readyReadStandardError()'), 
            self.__readStderr)
        
        self.noDialog = noDialog
        self.compileProc.start(uic, args)
        procStarted = self.compileProc.waitForStarted()
        if procStarted:
            self.compileRunning = True
            e4App().getObject("ViewManager").enableEditorsCheckFocusIn(False)
            return self.compileProc
        else:
            self.compileRunning = False
            if progress is not None:
                progress.cancel()
            KQMessageBox.critical(self,
                self.trUtf8('Process Generation Error'),
                self.trUtf8(
                    'Could not start %1.<br>'
                    'Ensure that it is in the search path.'
                ).arg(self.uicompiler))
            return None
        
    def __generateDialogCode(self):
        """
        Private method to generate dialog code for the form (Qt4 only)
        """
        itm = self.model().item(self.currentIndex())
        fn = unicode(itm.fileName())
        
        if self.hooks["generateDialogCode"] is not None:
            self.hooks["generateDialogCode"](filename)
        else:
            from CreateDialogCodeDialog import CreateDialogCodeDialog
            
            # change environment
            sys.path.insert(0, self.project.getProjectPath())
            cwd = os.getcwd()
            os.chdir(os.path.dirname(os.path.abspath(fn)))
            
            dlg = CreateDialogCodeDialog(fn, self.project, self)
            if not dlg.initError():
                dlg.exec_()
            
            # reset the environment
            os.chdir(cwd)
            del sys.path[0]
        
    def __generateSubclass(self):
        """
        Private method to generate a subclass for the form (Qt3 only).
        """
        itm = self.model().item(self.currentIndex())
        fn2 = unicode(itm.fileName())
        fn = fn2.replace(self.project.ppath+os.sep, '')
        self.__compileUI(fn, subclass = True)
        
    def __compileForm(self):
        """
        Private method to compile a form to a source file.
        """
        itm = self.model().item(self.currentIndex())
        fn2 = unicode(itm.fileName())
        fn = fn2.replace(self.project.ppath+os.sep, '')
        if self.hooks["compileForm"] is not None:
            self.hooks["compileForm"](fn)
        else:
            self.__compileUI(fn)
        
    def __compileAllForms(self):
        """
        Private method to compile all forms to source files.
        """
        if self.hooks["compileAllForms"] is not None:
            self.hooks["compileAllForms"](self.project.pdata["FORMS"])
        else:
            numForms = len(self.project.pdata["FORMS"])
            progress = KQProgressDialog(self.trUtf8("Compiling forms..."), 
                self.trUtf8("Abort"), 0, numForms, self)
            progress.setModal(True)
            progress.setMinimumDuration(0)
            i = 0
            
            for fn in self.project.pdata["FORMS"]:
                progress.setValue(i)
                if progress.wasCanceled():
                    break
                if not fn.endswith('.ui.h'):
                    proc = self.__compileUI(fn, True, progress)
                    if proc is not None:
                        while proc.state() == QProcess.Running:
                            QApplication.processEvents()
                            QThread.msleep(300)
                            QApplication.processEvents()
                    else:
                        break
                i += 1
                
            progress.setValue(numForms)
        
    def __compileSelectedForms(self):
        """
        Private method to compile selected forms to source files.
        """
        items = self.getSelectedItems()
        files = [unicode(itm.fileName()).replace(self.project.ppath+os.sep, '') \
                 for itm in items]
        
        if self.hooks["compileSelectedForms"] is not None:
            self.hooks["compileSelectedForms"](files)
        else:
            numForms = len(files)
            progress = KQProgressDialog(self.trUtf8("Compiling forms..."), 
                self.trUtf8("Abort"), 0, numForms, self)
            progress.setModal(True)
            progress.setMinimumDuration(0)
            i = 0
            
            for fn in files:
                progress.setValue(i)
                if progress.wasCanceled():
                    break
                if not fn.endswith('.ui.h'):
                    proc = self.__compileUI(fn, True, progress)
                    if proc is not None:
                        while proc.state() == QProcess.Running:
                            QApplication.processEvents()
                            QThread.msleep(300)
                            QApplication.processEvents()
                    else:
                        break
                i += 1
                
            progress.setValue(numForms)
        
    def compileChangedForms(self):
        """
        Public method to compile all changed forms to source files.
        """
        if self.hooks["compileChangedForms"] is not None:
            self.hooks["compileChangedForms"](self.project.pdata["FORMS"])
        else:
            if self.project.getProjectType() not in \
               ["Qt4", "Qt4C", "E4Plugin", "Kde4", "PySide"]:
                # ignore the request for non Qt/Kde projects
                return
            
            progress = KQProgressDialog(self.trUtf8("Determining changed forms..."), 
                QString(), 0, 100)
            progress.setMinimumDuration(0)
            i = 0
            
            # get list of changed forms
            changedForms = []
            progress.setMaximum(len(self.project.pdata["FORMS"]))
            for fn in self.project.pdata["FORMS"]:
                progress.setValue(i)
                QApplication.processEvents()
                if not fn.endswith('.ui.h'):
                    ifn = os.path.join(self.project.ppath, fn)
                    if self.project.pdata["PROGLANGUAGE"][0] in ["Python", "Python3"]:
                        if self.project.getProjectType() in \
                                ["Qt4", "Kde4", "E4Plugin", "PySide"]:
                            dirname, filename = os.path.split(os.path.splitext(ifn)[0])
                            ofn = os.path.join(dirname, "Ui_" + filename + ".py")
                        else:
                            ofn = os.path.splitext(ifn)[0] + '.py'
                    elif self.project.pdata["PROGLANGUAGE"][0] == "Ruby":
                        ofn = os.path.splitext(ifn)[0] + '.rb'
                    if not os.path.exists(ofn) or \
                       os.stat(ifn).st_mtime > os.stat(ofn).st_mtime:
                        changedForms.append(fn)
                i += 1
            progress.setValue(i)
            QApplication.processEvents()
            
            if changedForms:
                progress.setLabelText(self.trUtf8("Compiling changed forms..."))
                progress.setMaximum(len(changedForms))
                i = 0
                progress.setValue(i)
                QApplication.processEvents()
                for fn in changedForms:
                    progress.setValue(i)
                    proc = self.__compileUI(fn, True, progress)
                    if proc is not None:
                        while proc.state() == QProcess.Running:
                            QApplication.processEvents()
                            QThread.msleep(300)
                            QApplication.processEvents()
                    else:
                        break
                    i += 1
                progress.setValue(len(changedForms))
                QApplication.processEvents()
        
    def handlePreferencesChanged(self):
        """
        Public slot used to handle the preferencesChanged signal.
        """
        ProjectBaseBrowser.handlePreferencesChanged(self)
    
    ############################################################################
    ## Support for hooks below
    ############################################################################
    
    def _initHookMethods(self):
        """
        Protected method to initialize the hooks dictionary.
        
        Supported hook methods are:
        <ul>
        <li>compileForm: takes filename as parameter</li>
        <li>compileAllForms: takes list of filenames as parameter</li>
        <li>compileSelectedForms: takes list of filenames as parameter</li>
        <li>compileChangedForms: takes list of filenames as parameter</li>
        <li>generateDialogCode: takes filename as parameter</li>
        <li>newForm: takes full directory path of new file as parameter</li>
        </ul>
        
        <b>Note</b>: Filenames are relative to the project directory, if not
        specified differently.
        """
        self.hooks = {
            "compileForm"           : None, 
            "compileAllForms"       : None, 
            "compileChangedForms"   : None, 
            "compileSelectedForms"  : None, 
            "generateDialogCode"    : None, 
            "newForm"               : None, 
        }
