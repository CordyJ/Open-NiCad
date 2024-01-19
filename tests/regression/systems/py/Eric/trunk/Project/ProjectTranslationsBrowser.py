# -*- coding: utf-8 -*-

# Copyright (c) 2002 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a class used to display the translations part of the project.
"""

import os
import sys
import shutil
import fnmatch

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from KdeQt import KQMessageBox
from KdeQt.KQApplication import e4App

from ProjectBrowserModel import ProjectBrowserFileItem, \
    ProjectBrowserSimpleDirectoryItem, ProjectBrowserDirectoryItem, \
    ProjectBrowserTranslationType
from ProjectBaseBrowser import ProjectBaseBrowser

from UI.DeleteFilesConfirmationDialog import DeleteFilesConfirmationDialog
import UI.PixmapCache

import Preferences
import Utilities

class ProjectTranslationsBrowser(ProjectBaseBrowser):
    """
    A class used to display the translations part of the project. 
    
    @signal linguistFile(string) emitted to open a translation file with
            Qt-Linguist
    @signal appendStdout(string) emitted after something was received from
            a QProcess on stdout
    @signal appendStderr(string) emitted after something was received from
            a QProcess on stderr
    @signal sourceFile(string) emitted to open a translation file in an editor
    @signal closeSourceWindow(string) emitted after a file has been removed/deleted 
            from the project
    @signal trpreview(string list) emitted to preview translations in the 
            translations previewer
    @signal showMenu(string, QMenu) emitted when a menu is about to be shown. The name
            of the menu and a reference to the menu are given.
    """
    def __init__(self, project, parent=None):
        """
        Constructor
        
        @param project reference to the project object
        @param parent parent widget of this browser (QWidget)
        """
        ProjectBaseBrowser.__init__(self, project, ProjectBrowserTranslationType, parent)
        self.isTranslationsBrowser = True
        
        self.selectedItemsFilter = \
            [ProjectBrowserFileItem, ProjectBrowserSimpleDirectoryItem]
        
        self.setWindowTitle(self.trUtf8('Translations'))

        self.setWhatsThis(self.trUtf8(
            """<b>Project Translations Browser</b>"""
            """<p>This allows to easily see all translations contained in the current"""
            """ project. Several actions can be executed via the context menu.</p>"""
        ))
        
        self.lreleaseProc = None
        self.lreleaseProcRunning = False
        self.pylupdateProc = None
        self.pylupdateProcRunning = False
        
    def _createPopupMenus(self):
        """
        Protected overloaded method to generate the popup menu.
        """
        self.menuActions = []
        self.multiMenuActions = []
        self.dirMenuActions = []
        self.dirMultiMenuActions = []
        
        self.tsMenuActions = []
        self.qmMenuActions = []
        self.tsprocMenuActions = []
        self.qmprocMenuActions = []
        
        self.tsMultiMenuActions = []
        self.qmMultiMenuActions = []
        self.tsprocMultiMenuActions = []
        self.qmprocMultiMenuActions = []
        
        self.tsprocDirMenuActions = []
        self.qmprocDirMenuActions = []
        
        self.tsprocBackMenuActions = []
        self.qmprocBackMenuActions = []
        
        self.menu = QMenu(self)
        if self.project.getProjectType() in \
                ["Qt4", "Qt4C", "E4Plugin", "PySide", "PySideC"]:
            act = self.menu.addAction(self.trUtf8('Generate translation'), 
                self.__generateSelected)
            self.tsMenuActions.append(act)
            self.tsprocMenuActions.append(act)
            act = self.menu.addAction(\
                self.trUtf8('Generate translation (with obsolete)'), 
                self.__generateObsoleteSelected)
            self.tsMenuActions.append(act)
            self.tsprocMenuActions.append(act)
            act = self.menu.addAction(self.trUtf8('Generate all translations'), 
                self.__generateAll)
            self.tsprocMenuActions.append(act)
            act = self.menu.addAction(\
                self.trUtf8('Generate all translations (with obsolete)'), 
                self.__generateObsoleteAll)
            self.tsprocMenuActions.append(act)
            self.menu.addSeparator()
            act = self.menu.addAction(self.trUtf8('Open in Qt-Linguist'), 
                self._openItem)
            self.tsMenuActions.append(act)
            act = self.menu.addAction(self.trUtf8('Open in Editor'), 
                self.__openFileInEditor)
            self.tsMenuActions.append(act)
            self.menu.addSeparator()
            act = self.menu.addAction(self.trUtf8('Release translation'), 
                self.__releaseSelected)
            self.tsMenuActions.append(act)
            self.qmprocMenuActions.append(act)
            act = self.menu.addAction(self.trUtf8('Release all translations'), 
                self.__releaseAll)
            self.qmprocMenuActions.append(act)
            self.menu.addSeparator()
            act = self.menu.addAction(self.trUtf8('Preview translation'), 
                self.__TRPreview)
            self.qmMenuActions.append(act)
            act = self.menu.addAction(self.trUtf8('Preview all translations'), 
                self.__TRPreviewAll)
            self.menu.addSeparator()
        else:
            if self.hooks["extractMessages"] is not None:
                act = self.menu.addAction(
                    self.hooksMenuEntries.get("extractMessages", 
                        self.trUtf8('Extract messages')), 
                    self.__extractMessages)
                self.menuActions.append(act)
                self.menu.addSeparator()
            if self.hooks["generateSelected"] is not None:
                act = self.menu.addAction(
                    self.hooksMenuEntries.get("generateSelected", 
                        self.trUtf8('Generate translation')), 
                    self.__generateSelected)
                self.tsMenuActions.append(act)
                self.tsprocMenuActions.append(act)
            if self.hooks["generateSelectedWithObsolete"] is not None:
                act = self.menu.addAction(
                    self.hooksMenuEntries.get("generateSelectedWithObsolete", 
                        self.trUtf8('Generate translation (with obsolete)')), 
                    self.__generateObsoleteSelected)
                self.tsMenuActions.append(act)
                self.tsprocMenuActions.append(act)
            if self.hooks["generateAll"] is not None:
                act = self.menu.addAction(
                    self.hooksMenuEntries.get("generateAll", 
                        self.trUtf8('Generate all translations')), 
                    self.__generateAll)
                self.tsprocMenuActions.append(act)
            if self.hooks["generateAllWithObsolete"] is not None:
                act = self.menu.addAction(
                    self.hooksMenuEntries.get("generateAllWithObsolete", 
                        self.trUtf8('Generate all translations (with obsolete)')), 
                    self.__generateObsoleteAll)
                self.tsprocMenuActions.append(act)
            self.menu.addSeparator()
            act = self.menu.addAction(self.trUtf8('Open in Editor'), 
                self.__openFileInEditor)
            self.tsMenuActions.append(act)
            self.menu.addSeparator()
            if self.hooks["releaseSelected"] is not None:
                act = self.menu.addAction(
                    self.hooksMenuEntries.get("releaseSelected", 
                        self.trUtf8('Release translation')), 
                    self.__releaseSelected)
                self.tsMenuActions.append(act)
                self.qmprocMenuActions.append(act)
            if self.hooks["releaseAll"] is not None:
                act = self.menu.addAction(
                    self.hooksMenuEntries.get("releaseAll", 
                        self.trUtf8('Release all translations')), 
                    self.__releaseAll)
                self.qmprocMenuActions.append(act)
            self.menu.addSeparator()
        act = self.menu.addAction(self.trUtf8('Remove from project'), 
            self.__removeLanguageFile)
        self.menuActions.append(act)
        act = self.menu.addAction(self.trUtf8('Delete'), self.__deleteLanguageFile)
        self.menuActions.append(act)
        self.menu.addSeparator()
        self.menu.addAction(self.trUtf8('Add translation...'), self.project.addLanguage)
        self.menu.addAction(self.trUtf8('Add translation files...'), 
            self.__addTranslationFiles)
        self.menu.addSeparator()
        self.menu.addAction(self.trUtf8('Copy Path to Clipboard'), 
            self._copyToClipboard)
        self.menu.addSeparator()
        self.menu.addAction(self.trUtf8('Configure...'), self._configure)
        
        self.backMenu = QMenu(self)
        if self.project.getProjectType() in \
                ["Qt4", "Qt4C", "E4Plugin", "PySide", "PySideC"]:
            act = self.backMenu.addAction(self.trUtf8('Generate all translations'), 
                self.__generateAll)
            self.tsprocBackMenuActions.append(act)
            act = self.backMenu.addAction(\
                self.trUtf8('Generate all translations (with obsolete)'), 
                self.__generateObsoleteAll)
            self.tsprocBackMenuActions.append(act)
            act = self.backMenu.addAction(self.trUtf8('Release all translations'), 
                self.__releaseAll)
            self.qmprocBackMenuActions.append(act)
            self.backMenu.addSeparator()
            act = self.backMenu.addAction(self.trUtf8('Preview all translations'), 
                self.__TRPreview)
        else:
            if self.hooks["extractMessages"] is not None:
                act = self.backMenu.addAction(
                    self.hooksMenuEntries.get("extractMessages", 
                        self.trUtf8('Extract messages')), 
                    self.__extractMessages)
                self.backMenu.addSeparator()
            if self.hooks["generateAll"] is not None:
                act = self.backMenu.addAction(
                    self.hooksMenuEntries.get("generateAll", 
                        self.trUtf8('Generate all translations')), 
                    self.__generateAll)
                self.tsprocBackMenuActions.append(act)
            if self.hooks["generateAllWithObsolete"] is not None:
                act = self.backMenu.addAction(
                    self.hooksMenuEntries.get("generateAllWithObsolete", 
                        self.trUtf8('Generate all translations (with obsolete)')), 
                    self.__generateObsoleteAll)
                self.tsprocBackMenuActions.append(act)
            if self.hooks["releaseAll"] is not None:
                act = self.backMenu.addAction(
                    self.hooksMenuEntries.get("releaseAll", 
                        self.trUtf8('Release all translations')), 
                    self.__releaseAll)
                self.qmprocBackMenuActions.append(act)
        self.backMenu.addSeparator()
        self.backMenu.addAction(self.trUtf8('Add translation...'), 
            self.project.addLanguage)
        self.backMenu.addAction(self.trUtf8('Add translation files...'), 
            self.__addTranslationFiles)
        self.backMenu.addSeparator()
        self.backMenu.addAction(self.trUtf8('Configure...'), self._configure)
        self.backMenu.setEnabled(False)

        # create the menu for multiple selected files
        self.multiMenu = QMenu(self)
        if self.project.getProjectType() in \
                ["Qt4", "Qt4C", "E4Plugin", "PySide", "PySideC"]:
            act = self.multiMenu.addAction(self.trUtf8('Generate translations'), 
                self.__generateSelected)
            self.tsMultiMenuActions.append(act)
            self.tsprocMultiMenuActions.append(act)
            act = self.multiMenu.addAction(\
                self.trUtf8('Generate translations (with obsolete)'),
                self.__generateObsoleteSelected)
            self.tsMultiMenuActions.append(act)
            self.tsprocMultiMenuActions.append(act)
            self.multiMenu.addSeparator()
            act = self.multiMenu.addAction(\
                self.trUtf8('Open in Qt-Linguist'), self._openItem)
            self.tsMultiMenuActions.append(act)
            act = self.multiMenu.addAction(self.trUtf8('Open in Editor'), 
                self.__openFileInEditor)
            self.tsMultiMenuActions.append(act)
            self.multiMenu.addSeparator()
            act = self.multiMenu.addAction(self.trUtf8('Release translations'), 
                self.__releaseSelected)
            self.tsMultiMenuActions.append(act)
            self.qmprocMultiMenuActions.append(act)
            self.multiMenu.addSeparator()
            act = self.multiMenu.addAction(self.trUtf8('Preview translations'), 
                self.__TRPreview)
            self.qmMultiMenuActions.append(act)
        else:
            if self.hooks["extractMessages"] is not None:
                act = self.multiMenu.addAction(
                    self.hooksMenuEntries.get("extractMessages", 
                        self.trUtf8('Extract messages')), 
                    self.__extractMessages)
                self.multiMenuActions.append(act)
                self.multiMenu.addSeparator()
            if self.hooks["generateSelected"] is not None:
                act = self.multiMenu.addAction(
                    self.hooksMenuEntries.get("generateSelected", 
                        self.trUtf8('Generate translations')), 
                    self.__generateSelected)
                self.tsMultiMenuActions.append(act)
                self.tsprocMultiMenuActions.append(act)
            if self.hooks["generateSelectedWithObsolete"] is not None:
                act = self.multiMenu.addAction(
                    self.hooksMenuEntries.get("generateSelectedWithObsolete", 
                        self.trUtf8('Generate translations (with obsolete)')),
                    self.__generateObsoleteSelected)
                self.tsMultiMenuActions.append(act)
                self.tsprocMultiMenuActions.append(act)
            self.multiMenu.addSeparator()
            act = self.multiMenu.addAction(self.trUtf8('Open in Editor'), 
                self.__openFileInEditor)
            self.tsMultiMenuActions.append(act)
            self.multiMenu.addSeparator()
            if self.hooks["releaseSelected"] is not None:
                act = self.multiMenu.addAction(
                    self.hooksMenuEntries.get("releaseSelected", 
                        self.trUtf8('Release translations')), 
                    self.__releaseSelected)
                self.tsMultiMenuActions.append(act)
                self.qmprocMultiMenuActions.append(act)
        self.multiMenu.addSeparator()
        act = self.multiMenu.addAction(self.trUtf8('Remove from project'), 
            self.__removeLanguageFile)
        self.multiMenuActions.append(act)
        act = self.multiMenu.addAction(self.trUtf8('Delete'), self.__deleteLanguageFile)
        self.multiMenuActions.append(act)
        self.multiMenu.addSeparator()
        self.multiMenu.addAction(self.trUtf8('Configure...'), self._configure)

        self.dirMenu = QMenu(self)
        if self.project.getProjectType() in \
                ["Qt4", "Qt4C", "E4Plugin", "PySide", "PySideC"]:
            act = self.dirMenu.addAction(self.trUtf8('Generate all translations'), 
                self.__generateAll)
            self.tsprocDirMenuActions.append(act)
            act = self.dirMenu.addAction(\
                self.trUtf8('Generate all translations (with obsolete)'), 
                self.__generateObsoleteAll)
            self.tsprocDirMenuActions.append(act)
            act = self.dirMenu.addAction(self.trUtf8('Release all translations'), 
                self.__releaseAll)
            self.qmprocDirMenuActions.append(act)
            self.dirMenu.addSeparator()
            act = self.dirMenu.addAction(self.trUtf8('Preview all translations'), 
                self.__TRPreview)
        else:
            if self.hooks["extractMessages"] is not None:
                act = self.dirMenu.addAction(
                    self.hooksMenuEntries.get("extractMessages", 
                        self.trUtf8('Extract messages')), 
                    self.__extractMessages)
                self.dirMenuActions.append(act)
                self.dirMenu.addSeparator()
            if self.hooks["generateAll"] is not None:
                act = self.dirMenu.addAction(
                    self.hooksMenuEntries.get("generateAll", 
                        self.trUtf8('Generate all translations')), 
                    self.__generateAll)
                self.tsprocDirMenuActions.append(act)
            if self.hooks["generateAllWithObsolete"] is not None:
                act = self.dirMenu.addAction(
                    self.hooksMenuEntries.get("generateAllWithObsolete", 
                        self.trUtf8('Generate all translations (with obsolete)')), 
                    self.__generateObsoleteAll)
                self.tsprocDirMenuActions.append(act)
            if self.hooks["releaseAll"] is not None:
                act = self.dirMenu.addAction(
                    self.hooksMenuEntries.get("releaseAll", 
                        self.trUtf8('Release all translations')), 
                    self.__releaseAll)
                self.qmprocDirMenuActions.append(act)
        self.dirMenu.addSeparator()
        self.dirMenu.addAction(self.trUtf8('Add translation...'), 
            self.project.addLanguage)
        self.dirMenu.addAction(self.trUtf8('Add translation files...'), 
            self.__addTranslationFiles)
        self.dirMenu.addSeparator()
        self.dirMenu.addAction(self.trUtf8('Copy Path to Clipboard'), 
            self._copyToClipboard)
        self.dirMenu.addSeparator()
        self.dirMenu.addAction(self.trUtf8('Configure...'), self._configure)
        
        self.dirMultiMenu = None
        
        self.connect(self.menu, SIGNAL('aboutToShow()'),
            self.__showContextMenu)
        self.connect(self.multiMenu, SIGNAL('aboutToShow()'),
            self.__showContextMenuMulti)
        self.connect(self.dirMenu, SIGNAL('aboutToShow()'),
            self.__showContextMenuDir)
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
        if self.project.getProjectType() in \
                ["Qt4", "Qt4C", "E4Plugin", "PySide", "PySideC"]:
            tsFiles = 0
            qmFiles = 0
            itmList = self.getSelectedItems()
            for itm in itmList[:]:
                if itm.fileName().endswith('.ts'):
                    tsFiles += 1
                elif itm.fileName().endswith('.qm'):
                    qmFiles += 1
            if (tsFiles > 0 and qmFiles > 0) or \
               (tsFiles == 0 and qmFiles == 0):
                for act in self.tsMenuActions + self.qmMenuActions:
                    act.setEnabled(False)
            elif tsFiles > 0:
                for act in self.tsMenuActions:
                    act.setEnabled(True)
                for act in self.qmMenuActions:
                    act.setEnabled(False)
            elif qmFiles > 0:
                for act in self.tsMenuActions:
                    act.setEnabled(False)
                for act in self.qmMenuActions:
                    act.setEnabled(True)
            if self.pylupdateProcRunning:
                for act in self.tsprocMenuActions:
                    act.setEnabled(False)
            if self.lreleaseProcRunning:
                for act in self.qmprocMenuActions:
                    act.setEnabled(True)
        
        ProjectBaseBrowser._showContextMenu(self, self.menu)
        
        self.emit(SIGNAL("showMenu"), "Main", self.menu)
        
    def __showContextMenuMulti(self):
        """
        Private slot called by the multiMenu aboutToShow signal.
        """
        if self.project.getProjectType() in \
                ["Qt4", "Qt4C", "E4Plugin", "PySide", "PySideC"]:
            tsFiles = 0
            qmFiles = 0
            itmList = self.getSelectedItems()
            for itm in itmList[:]:
                if itm.fileName().endswith('.ts'):
                    tsFiles += 1
                elif itm.fileName().endswith('.qm'):
                    qmFiles += 1
            if (tsFiles > 0 and qmFiles > 0) or \
               (tsFiles == 0 and qmFiles == 0):
                for act in self.tsMultiMenuActions + self.qmMultiMenuActions:
                    act.setEnabled(False)
            elif tsFiles > 0:
                for act in self.tsMultiMenuActions:
                    act.setEnabled(True)
                for act in self.qmMultiMenuActions:
                    act.setEnabled(False)
            elif qmFiles > 0:
                for act in self.tsMultiMenuActions:
                    act.setEnabled(False)
                for act in self.qmMultiMenuActions:
                    act.setEnabled(True)
            if self.pylupdateProcRunning:
                for act in self.tsprocMultiMenuActions:
                    act.setEnabled(False)
            if self.lreleaseProcRunning:
                for act in self.qmprocMultiMenuActions:
                    act.setEnabled(True)
        
        ProjectBaseBrowser._showContextMenuMulti(self, self.multiMenu)
        
        self.emit(SIGNAL("showMenu"), "MainMulti", self.multiMenu)
        
    def __showContextMenuDir(self):
        """
        Private slot called by the dirMenu aboutToShow signal.
        """
        if self.project.getProjectType() in \
                ["Qt4", "Qt4C", "E4Plugin", "PySide", "PySideC"]:
            if self.pylupdateProcRunning:
                for act in self.tsprocDirMenuActions:
                    act.setEnabled(False)
            if self.lreleaseProcRunning:
                for act in self.qmprocDirMenuActions:
                    act.setEnabled(True)
        
        ProjectBaseBrowser._showContextMenuDir(self, self.dirMenu)
        
        self.emit(SIGNAL("showMenu"), "MainDir", self.dirMenu)
        
    def __showContextMenuBack(self):
        """
        Private slot called by the backMenu aboutToShow signal.
        """
        if self.project.getProjectType() in \
                ["Qt4", "Qt4C", "E4Plugin", "PySide", "PySideC"]:
            if self.pylupdateProcRunning:
                for act in self.tsprocBackMenuActions:
                    act.setEnabled(False)
            if self.lreleaseProcRunning:
                for act in self.qmprocBackMenuActions:
                    act.setEnabled(True)
        
        self.emit(SIGNAL("showMenu"), "MainBack", self.backMenu)
        
    def __addTranslationFiles(self):
        """
        Private method to add translation files to the project.
        """
        itm = self.model().item(self.currentIndex())
        if isinstance(itm, ProjectBrowserFileItem):
            dn = os.path.dirname(unicode(itm.fileName()))
        elif isinstance(itm, ProjectBrowserSimpleDirectoryItem) or \
             isinstance(itm, ProjectBrowserDirectoryItem):
            dn = unicode(itm.dirName())
        else:
            dn = None
        self.project.addFiles('translation', dn)
        
    def _openItem(self):
        """
        Protected slot to handle the open popup menu entry.
        """
        itmList = self.getSelectedItems()
        for itm in itmList:
            if isinstance(itm, ProjectBrowserFileItem):
                if itm.isLinguistFile():
                    if itm.fileExt() == '.ts':
                        self.emit(SIGNAL('linguistFile'), itm.fileName())
                    else:
                        self.emit(SIGNAL('trpreview'), [itm.fileName()])
                else:
                    self.emit(SIGNAL('sourceFile'), itm.fileName())
        
    def __openFileInEditor(self):
        """
        Private slot to handle the Open in Editor menu action.
        """
        itmList = self.getSelectedItems()
        for itm in itmList[:]:
            self.emit(SIGNAL('sourceFile'), itm.fileName())
        
    def __removeLanguageFile(self):
        """
        Private method to remove a translation from the project.
        """
        itmList = self.getSelectedItems()
        
        for itm in itmList[:]:
            fn = unicode(itm.fileName())
            self.emit(SIGNAL('closeSourceWindow'), fn)
            self.project.removeLanguageFile(fn)
        
    def __deleteLanguageFile(self):
        """
        Private method to delete a translation file from the project.
        """
        itmList = self.getSelectedItems()
        
        translationFiles = [unicode(itm.fileName()) for itm in itmList]
        
        dlg = DeleteFilesConfirmationDialog(self.parent(),
            self.trUtf8("Delete translation files"),
            self.trUtf8("Do you really want to delete these translation files"
                " from the project?"),
            translationFiles)
        
        if dlg.exec_() == QDialog.Accepted:
            for fn in translationFiles:
                self.emit(SIGNAL('closeSourceWindow'), fn)
                self.project.deleteLanguageFile(fn)
        
    def __TRPreview(self, previewAll = False):
        """
        Private slot to handle the Preview translations action.
        
        @param previewAll flag indicating, that all translations
            should be previewed (boolean)
        """
        fileNames = []
        itmList = self.getSelectedItems()
        if itmList and not previewAll:
            for itm in itmList:
                if isinstance(itm, ProjectBrowserSimpleDirectoryItem):
                    dname = unicode(itm.dirName()).replace(self.project.ppath+os.sep, '')
                    trfiles = self.project.pdata["TRANSLATIONS"][:]
                    trfiles.sort()
                    for trfile in trfiles:
                        if trfile.startswith(dname):
                            if trfile not in fileNames:
                                fileNames.append(os.path.join(self.project.ppath, trfile))
                else:
                    fn = unicode(itm.fileName())
                    if fn not in fileNames:
                        fileNames.append(os.path.join(self.project.ppath, fn))
        else:
            trfiles = self.project.pdata["TRANSLATIONS"][:]
            trfiles.sort()
            fileNames.extend([os.path.join(self.project.ppath, trfile) \
                              for trfile in trfiles \
                              if trfile.endswith('.qm')])
        self.emit(SIGNAL('trpreview'), fileNames, True)
        
    def __TRPreviewAll(self):
        """
        Private slot to handle the Preview all translations action.
        """
        self.__TRPreview(True)
    
    ############################################################################
    ##  Methods to support the generation and release commands
    ############################################################################
    
    def __writeTempProjectFile(self, langs, filter):
        """
        Private method to write a temporary project file suitable for pylupdate and
        lrelease.
        
        @param langs list of languages to include in the process. An empty list (default) 
            means that all translations should be included. 
            (list of ProjectBrowserFileItem)
        @param filter list of source file extension that should be considered
            (list of strings)
        @return flag indicating success
        """
        path, ext = os.path.splitext(self.project.pfile)
        pfile = '%s_e4x.pro' % path
        
        # only consider files satisfying the filter criteria
        _sources = [s for s in self.project.pdata["SOURCES"] \
                   if os.path.splitext(s)[1] in filter]
        sources = []
        for s in _sources:
            addIt = True
            for transExcept in self.project.pdata["TRANSLATIONEXCEPTIONS"]:
                if s.startswith(transExcept):
                    addIt = False
                    break
            if addIt:
                sources.append(s)
        sections = [("SOURCES", sources)]
        
        _forms = [f for f in self.project.pdata["FORMS"] if f.endswith('.ui')]
        forms = []
        for f in _forms:
            addIt = True
            for transExcept in self.project.pdata["TRANSLATIONEXCEPTIONS"]:
                if f.startswith(transExcept):
                    addIt = False
                    break
            if addIt:
                forms.append(f)
        sections.append(("FORMS", forms))
        
        if langs:
            l = [lang.fileName().replace(self.project.ppath+os.sep, '') \
                 for lang in langs if lang.fileName().endswith('.ts')]
        else:
            try:
                pattern = unicode(self.project.pdata["TRANSLATIONPATTERN"][0])\
                          .replace("%language%", "*")
                l = [lang for lang in self.project.pdata["TRANSLATIONS"] \
                     if fnmatch.fnmatch(lang, pattern)]
            except IndexError:
                l = []
        if l:
            sections.append(("TRANSLATIONS", l))
        else:
            KQMessageBox.warning(None,
                self.trUtf8("Write temporary project file"),
                self.trUtf8("""No translation files (*.ts) selected."""),
                QMessageBox.StandardButtons(\
                    QMessageBox.Abort))
            return False
        
        try:
            pf = open(pfile, "wb")
            for key, list in sections:
                if len(list) > 0:
                    pf.write('%s = ' % key)
                    last = len(list) - 1
                    if last > 0:
                        pf.write('%s \\%s' % \
                            (list[0].replace(os.sep, '/'), os.linesep))
                        for i in range(1, last):
                            pf.write('\t%s \\%s' % \
                                (list[i].replace(os.sep, '/'), os.linesep))
                        pf.write('\t%s %s%s' % \
                            (list[last].replace(os.sep, '/'), os.linesep, os.linesep))
                    else:
                        pf.write('%s %s%s' % \
                            (list[0].replace(os.sep, '/'), os.linesep, os.linesep))
                
            pf.close()
            self.tmpProject = pfile
            return True
        except IOError:
            KQMessageBox.critical(None,
                self.trUtf8("Write temporary project file"),
                self.trUtf8("<p>The temporary project file <b>%1</b> could not"
                    " be written.</p>").arg(pfile),
                QMessageBox.StandardButtons(\
                    QMessageBox.Abort))
            self.tmpProject = None
            return False
        
    def __readStdoutLupdate(self):
        """
        Private slot to handle the readyReadStandardOutput signal of the 
        pylupdate process.
        """
        if self.pylupdateProc is not None:
            self.__readStdout(self.pylupdateProc, '%s: ' % self.pylupdate)
        else:
            return
        
    def __readStdoutLrelease(self):
        """
        Private slot to handle the readyReadStandardOutput signal of the 
        lrelease process.
        """
        if self.lreleaseProc is not None:
            self.__readStdout(self.lreleaseProc, 'lrelease: ')
        else:
            return
        
    def __readStdout(self, proc, ps):
        """
        Private method to read from a process' stdout channel.
        
        @param proc process to read from (QProcess)
        @param ps propmt string (string or QString)
        """
        ioEncoding = str(Preferences.getSystem("IOEncoding"))
        
        proc.setReadChannel(QProcess.StandardOutput)
        while proc and proc.canReadLine():
            s = QString(ps)
            output = unicode(proc.readLine(), ioEncoding, 'replace')
            s.append(output)
            self.emit(SIGNAL('appendStdout'), s)
        
    def __readStderrLupdate(self):
        """
        Private slot to handle the readyReadStandardError signal of the 
        pylupdate process.
        """
        if self.pylupdateProc is not None:
            self.__readStderr(self.pylupdateProc, '%s: ' % self.pylupdate)
        else:
            return
        
    def __readStderrLrelease(self):
        """
        Private slot to handle the readyReadStandardError signal of the 
        lrelease process.
        """
        if self.lreleaseProc is not None:
            self.__readStderr(self.lreleaseProc, 'lrelease: ')
        else:
            return
        
    def __readStderr(self, proc, ps):
        """
        Private method to read from a process' stderr channel.
        
        @param proc process to read from (QProcess)
        @param ps propmt string (string or QString)
        """
        ioEncoding = str(Preferences.getSystem("IOEncoding"))
        
        proc.setReadChannel(QProcess.StandardError)
        while proc and proc.canReadLine():
            s = QString(ps)
            error = unicode(proc.readLine(), ioEncoding, 'replace')
            s.append(error)
            self.emit(SIGNAL('appendStderr'), s)
    
    ############################################################################
    ##  Methods for the generation commands
    ############################################################################
    
    def __extractMessages(self):
        """
        Private slot to extract the messages to form a messages template file.
        """
        if self.hooks["extractMessages"] is not None:
            self.hooks["extractMessages"]()
        
    def __generateTSFileDone(self, exitCode, exitStatus):
        """
        Private slot to handle the finished signal of the pylupdate process.
        
        @param exitCode exit code of the process (integer)
        @param exitStatus exit status of the process (QProcess.ExitStatus)
        """
        self.pylupdateProcRunning = False
        if exitStatus == QProcess.NormalExit and exitCode == 0:
            KQMessageBox.information(None,
                self.trUtf8("Translation file generation"),
                self.trUtf8("The generation of the translation files (*.ts)"
                    " was successful."))
        else:
            KQMessageBox.critical(None,
                self.trUtf8("Translation file generation"),
                self.trUtf8("The generation of the translation files (*.ts) has failed."))
        self.pylupdateProc = None
        self.pylupdate = ""
        try:
            os.remove(self.tmpProject)
        except EnvironmentError:
            pass
        self.tmpProject = None
        
    def __generateTSFile(self, noobsolete = False, generateAll = True):
        """
        Private method used to run pylupdate/pylupdate4 to generate the .ts files.
        
        @param noobsolete flag indicating whether obsolete entries should be 
            kept (boolean)
        @param generateAll flag indicating whether all translations should be 
            generated (boolean)
        """
        if generateAll:
            langs = []
        else:
            langs = self.getSelectedItems()
        
        # Hook support
        if generateAll:
            if noobsolete:
                if self.hooks["generateAll"] is not None:
                    self.hooks["generateAll"](self.project.pdata["TRANSLATIONS"])
                    return
            else:
                if self.hooks["generateAllWithObsolete"] is not None:
                    self.hooks["generateAllWithObsolete"](
                        self.project.pdata["TRANSLATIONS"])
                    return
        else:
            if noobsolete:
                if self.hooks["generateSelected"] is not None:
                    l = [lang.fileName().replace(self.project.ppath+os.sep, '') \
                         for lang in langs]
                    self.hooks["generateSelected"](l)
                    return
            else:
                if self.hooks["generateSelectedWithObsolete"] is not None:
                    l = [lang.fileName().replace(self.project.ppath+os.sep, '') \
                         for lang in langs]
                    self.hooks["generateSelectedWithObsolete"](l)
                    return
        
        # generate a minimal temporary projectfile suitable for pylupdate
        if self.project.pdata["PROGLANGUAGE"][0] in ["Python", "Python3"]:
            ok = self.__writeTempProjectFile(langs, [".py"])
        else:
            ok = False
        if not ok:
            return
        
        self.pylupdateProc = QProcess()
        args = QStringList()
        
        if self.project.getProjectType() in ["Qt4", "Qt4C", "E4Plugin"]:
            self.pylupdate = 'pylupdate4'
        elif self.project.getProjectType() in ["PySide", "PySideC"]:
            self.pylupdate = 'pyside-lupdate'
        else:
            return
        if Utilities.isWindowsPlatform():
            self.pylupdate = self.pylupdate + '.exe'
        
        if noobsolete:
            args.append('-noobsolete')
        
        args.append('-verbose')
        args.append(self.tmpProject)
        self.pylupdateProc.setWorkingDirectory(self.project.ppath)
        self.connect(self.pylupdateProc, SIGNAL('finished(int, QProcess::ExitStatus)'), 
            self.__generateTSFileDone)
        self.connect(self.pylupdateProc, SIGNAL('readyReadStandardOutput()'), 
            self.__readStdoutLupdate)
        self.connect(self.pylupdateProc, SIGNAL('readyReadStandardError()'), 
            self.__readStderrLupdate)
        
        self.pylupdateProc.start(self.pylupdate, args)
        procStarted = self.pylupdateProc.waitForStarted()
        if procStarted:
            self.pylupdateProcRunning = True
        else:
            KQMessageBox.critical(self,
                self.trUtf8('Process Generation Error'),
                self.trUtf8(
                    'Could not start %1.<br>'
                    'Ensure that it is in the search path.'
                ).arg(self.pylupdate))
        
    def __generateAll(self):
        """
        Private method to generate all translation files (.ts) for Qt Linguist.
        
        All obsolete strings are removed from the .ts file.
        """
        self.__generateTSFile(noobsolete = True, generateAll = True)
        
    def __generateObsoleteAll(self):
        """
        Private method to generate all translation files (.ts) for Qt Linguist.
        
        Obsolete strings are kept.
        """
        self.__generateTSFile(noobsolete = False, generateAll = True)
        
    def __generateSelected(self):
        """
        Private method to generate selected translation files (.ts) for Qt Linguist.
        
        All obsolete strings are removed from the .ts file.
        """
        self.__generateTSFile(noobsolete = True, generateAll = False)
        
    def __generateObsoleteSelected(self):
        """
        Private method to generate selected translation files (.ts) for Qt Linguist.
        
        Obsolete strings are kept.
        """
        self.__generateTSFile(noobsolete = False, generateAll = False)
    
    ############################################################################
    ##  Methods for the release commands
    ############################################################################
    
    def __releaseTSFileDone(self, exitCode, exitStatus):
        """
        Private slot to handle the finished signal of the lrelease process.
        """
        self.lreleaseProcRunning = False
        if exitStatus == QProcess.NormalExit and exitCode == 0:
            KQMessageBox.information(None,
                self.trUtf8("Translation file release"),
                self.trUtf8("The release of the translation files (*.qm)"
                    " was successful."))
            if self.project.pdata["TRANSLATIONSBINPATH"]:
                target = os.path.join(self.project.ppath, 
                                      self.project.pdata["TRANSLATIONSBINPATH"][0])
                for langFile in self.project.pdata["TRANSLATIONS"][:]:
                    if langFile.endswith('.ts'):
                        qmFile = os.path.join(self.project.ppath,
                                              langFile.replace('.ts', '.qm'))
                        if os.path.exists(qmFile):
                            shutil.move(qmFile, target)
        else:
            KQMessageBox.critical(None,
                self.trUtf8("Translation file release"),
                self.trUtf8("The release of the translation files (*.qm) has failed."))
        self.lreleaseProc = None
        try:
            os.remove(self.tmpProject)
        except EnvironmentError:
            pass
        self.tmpProject = None
        self.project.checkLanguageFiles()
        
    def __releaseTSFile(self, generateAll = False):
        """
        Private method to run lrelease to release the translation files (.qm).
        
        @param generateAll flag indicating whether all translations should be
            released (boolean)
        """
        if generateAll:
            langs = []
        else:
            langs = self.getSelectedItems()
        
        # Hooks support
        if generateAll:
            if self.hooks["releaseAll"] is not None:
                self.hooks["releaseAll"](self.project.pdata["TRANSLATIONS"])
                return
        else:
            if self.hooks["releaseSelected"] is not None:
                l = [lang.fileName().replace(self.project.ppath+os.sep, '') \
                     for lang in langs]
                self.hooks["releaseSelected"](l)
                return
        
        # generate a minimal temporary projectfile suitable for lrelease
        if self.project.pdata["PROGLANGUAGE"][0] in ["Python", "Python3"]:
            ok = self.__writeTempProjectFile(langs, [".py"])
        else:
            ok = False
        if not ok:
            return
        
        self.lreleaseProc = QProcess()
        args = QStringList()
        
        if self.project.getProjectType() in \
                ["Qt4", "Qt4C", "E4Plugin", "PySide", "PySideC"]:
            lrelease = Utilities.generateQtToolName("lrelease")
        else:
            return
        if Utilities.isWindowsPlatform():
            lrelease = lrelease + '.exe'
        
        args.append('-verbose')
        args.append(self.tmpProject)
        self.lreleaseProc.setWorkingDirectory(self.project.ppath)
        self.connect(self.lreleaseProc, SIGNAL('finished(int, QProcess::ExitStatus)'), 
            self.__releaseTSFileDone)
        self.connect(self.lreleaseProc, SIGNAL('readyReadStandardOutput()'), 
            self.__readStdoutLrelease)
        self.connect(self.lreleaseProc, SIGNAL('readyReadStandardError()'), 
            self.__readStderrLrelease)
        
        self.lreleaseProc.start(lrelease, args)
        procStarted = self.lreleaseProc.waitForStarted()
        if procStarted:
            self.lreleaseProcRunning = True
        else:
            KQMessageBox.critical(self,
                self.trUtf8('Process Generation Error'),
                self.trUtf8(
                    '<p>Could not start lrelease.<br>'
                    'Ensure that it is available as <b>%1</b>.</p>'
                ).arg(lrelease))
        
    def __releaseSelected(self):
        """
        Private method to release the translation files (.qm).
        """
        self.__releaseTSFile(generateAll = False)
        
    def __releaseAll(self):
        """
        Private method to release the translation files (.qm).
        """
        self.__releaseTSFile(generateAll = True)
    
    ############################################################################
    ## Support for hooks below
    ############################################################################
    
    def _initHookMethods(self):
        """
        Protected method to initialize the hooks dictionary.
        
        Supported hook methods are:
        <ul>
        <li>extractMessages: takes no parameters</li>
        <li>generateAll: takes list of filenames as parameter</li>
        <li>generateAllWithObsolete: takes list of filenames as parameter</li>
        <li>generateSelected: takes list of filenames as parameter</li>
        <li>generateSelectedWithObsolete: takes list of filenames as parameter</li>
        <li>releaseAll: takes list of filenames as parameter</li>
        <li>releaseSelected: takes list of filenames as parameter</li>
        </ul>
        
        <b>Note</b>: Filenames are relative to the project directory.
        """
        self.hooks = {
            "extractMessages"               : None, 
            "generateAll"                   : None, 
            "generateAllWithObsolete"       : None, 
            "generateSelected"              : None, 
            "generateSelectedWithObsolete"  : None, 
            "releaseAll"                    : None, 
            "releaseSelected"               : None, 
        }
