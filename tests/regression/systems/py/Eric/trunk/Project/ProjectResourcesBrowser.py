# -*- coding: utf-8 -*-

# Copyright (c) 2002 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a class used to display the resources part of the project.
"""

import os
import sys
import shutil

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from KdeQt import KQFileDialog, KQMessageBox
from KdeQt.KQProgressDialog import KQProgressDialog
from KdeQt.KQApplication import e4App

from ProjectBrowserModel import ProjectBrowserFileItem, \
    ProjectBrowserSimpleDirectoryItem, ProjectBrowserDirectoryItem, \
    ProjectBrowserResourceType
from ProjectBaseBrowser import ProjectBaseBrowser

from UI.DeleteFilesConfirmationDialog import DeleteFilesConfirmationDialog
import UI.PixmapCache

import Preferences
import Utilities

from eric4config import getConfig

class ProjectResourcesBrowser(ProjectBaseBrowser):
    """
    A class used to display the resources part of the project. 
    
    @signal appendStderr(string) emitted after something was received from
            a QProcess on stderr
    @signal sourceFile(string) emitted to open a resources file in an editor
    @signal closeSourceWindow(string) emitted after a file has been removed/deleted 
            from the project
    @signal showMenu(string, QMenu) emitted when a menu is about to be shown. The name
            of the menu and a reference to the menu are given.
    """
    RCFilenameFormatPython = "%s_rc.py"
    RCFilenameFormatRuby = "%s_rc.rb"
    
    def __init__(self, project, parent = None):
        """
        Constructor
        
        @param project reference to the project object
        @param parent parent widget of this browser (QWidget)
        """
        ProjectBaseBrowser.__init__(self, project, ProjectBrowserResourceType, parent)
        
        self.selectedItemsFilter = \
            [ProjectBrowserFileItem, ProjectBrowserSimpleDirectoryItem]
        
        self.setWindowTitle(self.trUtf8('Resources'))

        self.setWhatsThis(self.trUtf8(
            """<b>Project Resources Browser</b>"""
            """<p>This allows to easily see all resources contained in the current"""
            """ project. Several actions can be executed via the context menu.</p>"""
        ))
        
        self.compileProc = None
        
    def _createPopupMenus(self):
        """
        Protected overloaded method to generate the popup menu.
        """
        self.menuActions = []
        self.multiMenuActions = []
        self.dirMenuActions = []
        self.dirMultiMenuActions = []
        
        self.menu = QMenu(self)
        if self.project.getProjectType() in ["Qt4", "E4Plugin", "Kde4", "PySide"]:
            self.menu.addAction(self.trUtf8('Compile resource'), 
                self.__compileResource)
            self.menu.addAction(self.trUtf8('Compile all resources'), 
                self.__compileAllResources)
            self.menu.addSeparator()
        else:
            if self.hooks["compileResource"] is not None:
                self.menu.addAction(
                    self.hooksMenuEntries.get("compileResource", 
                        self.trUtf8('Compile resource')), 
                    self.__compileResource)
            if self.hooks["compileAllResources"] is not None:
                self.menu.addAction(
                    self.hooksMenuEntries.get("compileAllResources", 
                        self.trUtf8('Compile all resources')), 
                    self.__compileAllResources)
            if self.hooks["compileResource"] is not None or \
               self.hooks["compileAllResources"] is not None:
                self.menu.addSeparator()
        self.menu.addAction(self.trUtf8('Open'), self.__openFile)
        self.menu.addSeparator()
        act = self.menu.addAction(self.trUtf8('Rename file'), self._renameFile)
        self.menuActions.append(act)
        act = self.menu.addAction(self.trUtf8('Remove from project'), self._removeFile)
        self.menuActions.append(act)
        act = self.menu.addAction(self.trUtf8('Delete'), self.__deleteFile)
        self.menuActions.append(act)
        self.menu.addSeparator()
        if self.project.getProjectType() in ["Qt4", "E4Plugin", "Kde4", "PySide"]:
            self.menu.addAction(self.trUtf8('New resource...'), self.__newResource)
        else:
            if self.hooks["newResource"] is not None:
                self.menu.addAction(
                    self.hooksMenuEntries.get("newResource", 
                        self.trUtf8('New resource...')), self.__newResource)
        self.menu.addAction(self.trUtf8('Add resources...'), self.__addResourceFiles)
        self.menu.addAction(self.trUtf8('Add resources directory...'), 
            self.__addResourcesDirectory)
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
        if self.project.getProjectType() in ["Qt4", "E4Plugin", "Kde4", "PySide"]:
            self.backMenu.addAction(self.trUtf8('Compile all resources'), 
                self.__compileAllResources)
            self.backMenu.addSeparator()
            self.backMenu.addAction(self.trUtf8('New resource...'), self.__newResource)
        else:
            if self.hooks["compileAllResources"] is not None:
                self.backMenu.addAction(
                    self.hooksMenuEntries.get("compileAllResources", 
                        self.trUtf8('Compile all resources')), 
                    self.__compileAllResources)
                self.backMenu.addSeparator()
            if self.hooks["newResource"] is not None:
                self.backMenu.addAction(
                    self.hooksMenuEntries.get("newResource", 
                        self.trUtf8('New resource...')), self.__newResource)
        self.backMenu.addAction(self.trUtf8('Add resources...'), 
            self.project.addResourceFiles)
        self.backMenu.addAction(self.trUtf8('Add resources directory...'), 
            self.project.addResourceDir)
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
        if self.project.getProjectType() in ["Qt4", "E4Plugin", "Kde4", "PySide"]:
            act = self.multiMenu.addAction(self.trUtf8('Compile resources'), 
                self.__compileSelectedResources)
            self.multiMenu.addSeparator()
        else:
            if self.hooks["compileSelectedResources"] is not None:
                act = self.multiMenu.addAction(
                    self.hooksMenuEntries.get("compileSelectedResources", 
                        self.trUtf8('Compile resources')), 
                    self.__compileSelectedResources)
                self.multiMenu.addSeparator()
        self.multiMenu.addAction(self.trUtf8('Open'), self.__openFile)
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
        if self.project.getProjectType() in ["Qt4", "E4Plugin", "Kde4", "PySide"]:
            self.dirMenu.addAction(self.trUtf8('Compile all resources'), 
                self.__compileAllResources)
            self.dirMenu.addSeparator()
        else:
            if self.hooks["compileAllResources"] is not None:
                self.dirMenu.addAction(
                    self.hooksMenuEntries.get("compileAllResources", 
                        self.trUtf8('Compile all resources')), 
                    self.__compileAllResources)
                self.dirMenu.addSeparator()
        act = self.dirMenu.addAction(self.trUtf8('Remove from project'), self._removeDir)
        self.dirMenuActions.append(act)
        self.dirMenu.addSeparator()
        self.dirMenu.addAction(self.trUtf8('New resource...'), self.__newResource)
        self.dirMenu.addAction(self.trUtf8('Add resources...'), self.__addResourceFiles)
        self.dirMenu.addAction(self.trUtf8('Add resources directory...'), 
            self.__addResourcesDirectory)
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
        if self.project.getProjectType() in ["Qt4", "E4Plugin", "Kde4", "PySide"]:
            self.dirMultiMenu.addAction(self.trUtf8('Compile all resources'), 
                self.__compileAllResources)
            self.dirMultiMenu.addSeparator()
        else:
            if self.hooks["compileAllResources"] is not None:
                self.dirMultiMenu.addAction(
                    self.hooksMenuEntries.get("compileAllResources", 
                        self.trUtf8('Compile all resources')), 
                    self.__compileAllResources)
                self.dirMultiMenu.addSeparator()
        self.dirMultiMenu.addAction(self.trUtf8('Add resources...'), 
            self.project.addResourceFiles)
        self.dirMultiMenu.addAction(self.trUtf8('Add resources directory...'), 
            self.project.addResourceDir)
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
        ProjectBaseBrowser._showContextMenu(self, self.menu)
        
        self.emit(SIGNAL("showMenu"), "Main", self.menu)
        
    def __showContextMenuMulti(self):
        """
        Private slot called by the multiMenu aboutToShow signal.
        """
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
        
    def __addResourceFiles(self):
        """
        Private method to add resource files to the project.
        """
        itm = self.model().item(self.currentIndex())
        if isinstance(itm, ProjectBrowserFileItem):
            dn = os.path.dirname(unicode(itm.fileName()))
        elif isinstance(itm, ProjectBrowserSimpleDirectoryItem) or \
             isinstance(itm, ProjectBrowserDirectoryItem):
            dn = unicode(itm.dirName())
        else:
            dn = None
        self.project.addFiles('resource', dn)
        
    def __addResourcesDirectory(self):
        """
        Private method to add resource files of a directory to the project.
        """
        itm = self.model().item(self.currentIndex())
        if isinstance(itm, ProjectBrowserFileItem):
            dn = os.path.dirname(unicode(itm.fileName()))
        elif isinstance(itm, ProjectBrowserSimpleDirectoryItem) or \
             isinstance(itm, ProjectBrowserDirectoryItem):
            dn = unicode(itm.dirName())
        else:
            dn = None
        self.project.addDirectory('resource', dn)
        
    def _openItem(self):
        """
        Protected slot to handle the open popup menu entry.
        """
        self.__openFile()
        
    def __openFile(self):
        """
        Private slot to handle the Open menu action.
        """
        itmList = self.getSelectedItems()
        for itm in itmList[:]:
            if isinstance(itm, ProjectBrowserFileItem):
                self.emit(SIGNAL('sourceFile'), itm.fileName())
        
    def __newResource(self):
        """
        Private slot to handle the New Resource menu action.
        """
        itm = self.model().item(self.currentIndex())
        if itm is None:
            path = self.project.ppath
        else:
            try:
                path = os.path.dirname(unicode(itm.fileName()))
            except AttributeError:
                path = os.path.join(self.project.ppath, unicode(itm.data(0)))
        
        if self.hooks["newResource"] is not None:
            self.hooks["newResource"](path)
        else:
            selectedFilter = QString("")
            fname = KQFileDialog.getSaveFileName(\
                self,
                self.trUtf8("New Resource"),
                path,
                self.trUtf8("Qt Resource Files (*.qrc)"),
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
                    self.trUtf8("New Resource"),
                    self.trUtf8("The file already exists! Overwrite it?"),
                    QMessageBox.StandardButtons(\
                        QMessageBox.No | \
                        QMessageBox.Yes),
                    QMessageBox.No)
                if res != QMessageBox.Yes:
                    # user selected to not overwrite
                    return
            
            try:
                rcfile = open(fname, 'wb')
                rcfile.write('<!DOCTYPE RCC>\n')
                rcfile.write('<RCC version="1.0">\n')
                rcfile.write('<qresource>\n')
                rcfile.write('</qresource>\n')
                rcfile.write('</RCC>\n')
                rcfile.close()
            except IOError, e:
                KQMessageBox.critical(self,
                    self.trUtf8("New Resource"),
                    self.trUtf8("<p>The new resource file <b>%1</b> could not be created.<br>"
                        "Problem: %2</p>").arg(fname).arg(unicode(e)))
                return
            
            self.project.appendFile(fname)
            self.emit(SIGNAL('sourceFile'), fname)
        
    def __deleteFile(self):
        """
        Private method to delete a resource file from the project.
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
            self.trUtf8("Delete resources"),
            self.trUtf8("Do you really want to delete these resources from the project?"),
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
        pyrcc4/rbrcc process.
        """
        if self.compileProc is None:
            return
        self.compileProc.setReadChannel(QProcess.StandardOutput)
        
        while self.compileProc and self.compileProc.canReadLine():
            self.buf.append(self.compileProc.readLine())
        
    def __readStderr(self):
        """
        Private slot to handle the readyReadStandardError signal of the 
        pyrcc4/rbrcc process.
        """
        if self.compileProc is None:
            return
        
        ioEncoding = str(Preferences.getSystem("IOEncoding"))
        
        self.compileProc.setReadChannel(QProcess.StandardError)
        while self.compileProc and self.compileProc.canReadLine():
            s = QString(self.rccCompiler + ': ')
            error = unicode(self.compileProc.readLine(), 
                            ioEncoding, 'replace')
            s.append(error)
            self.emit(SIGNAL('appendStderr'), s)
        
    def __compileQRCDone(self, exitCode, exitStatus):
        """
        Private slot to handle the finished signal of the compile process.
        
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
                        self.trUtf8("Resource Compilation"),
                        self.trUtf8("The compilation of the resource file"
                            " was successful."))
            except IOError, msg:
                if not self.noDialog:
                    KQMessageBox.information(None,
                        self.trUtf8("Resource Compilation"),
                        self.trUtf8("<p>The compilation of the resource file failed.</p>"
                            "<p>Reason: %1</p>").arg(unicode(msg)))
        else:
            if not self.noDialog:
                KQMessageBox.information(None,
                    self.trUtf8("Resource Compilation"),
                    self.trUtf8("The compilation of the resource file failed."))
        self.compileProc = None
        
    def __compileQRC(self, fn, noDialog = False, progress = None):
        """
        Privat method to compile a .qrc file to a .py file.
        
        @param fn filename of the .ui file to be compiled
        @param noDialog flag indicating silent operations
        @param progress reference to the progress dialog
        @return reference to the compile process (QProcess)
        """
        self.compileProc = QProcess()
        args = QStringList()
        self.buf = QString("")
        
        if self.project.pdata["PROGLANGUAGE"][0] in ["Python", "Python3"]:
            if self.project.getProjectType() in ["Qt4", "E4Plugin", "Kde4"]:
                self.rccCompiler = 'pyrcc4'
                if PYQT_VERSION >= 0x040500:
                    if self.project.pdata["PROGLANGUAGE"][0] == "Python":
                        args.append("-py2")
                    else:
                        args.append("-py3")
            elif self.project.getProjectType() == "PySide":
                self.rccCompiler = 'pyside-rcc4'
                if self.project.pdata["PROGLANGUAGE"][0] == "Python":
                    args.append("-py2")
                else:
                    args.append("-py3")
            else:
                return None
        elif self.project.pdata["PROGLANGUAGE"][0] == "Ruby":
            if self.project.getProjectType() == "Qt4":
                self.rccCompiler = 'rbrcc'
            else:
                return None
        else:
            return None
        
        rcc = self.rccCompiler
        if Utilities.isWindowsPlatform():
            rcc = rcc + '.exe'
        
        ofn, ext = os.path.splitext(fn)
        fn = os.path.join(self.project.ppath, fn)
        
        dirname, filename = os.path.split(ofn)
        if self.project.pdata["PROGLANGUAGE"][0] in ["Python", "Python3"]:
            self.compiledFile = os.path.join(dirname, 
                                self.RCFilenameFormatPython % filename)
        elif self.project.pdata["PROGLANGUAGE"][0] == "Ruby":
            self.compiledFile = os.path.join(
                                dirname, self.RCFilenameFormatRuby % filename)
        
        args.append(fn)
        self.connect(self.compileProc, SIGNAL('finished(int, QProcess::ExitStatus)'),
            self.__compileQRCDone)
        self.connect(self.compileProc, SIGNAL('readyReadStandardOutput()'), 
            self.__readStdout)
        self.connect(self.compileProc, SIGNAL('readyReadStandardError()'), 
            self.__readStderr)
        
        self.noDialog = noDialog
        self.compileProc.start(rcc, args)
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
                ).arg(self.rccCompiler))
            return None
        
    def __compileResource(self):
        """
        Private method to compile a resource to a source file.
        """
        itm = self.model().item(self.currentIndex())
        fn2 = unicode(itm.fileName())
        fn = fn2.replace(self.project.ppath+os.sep, '')
        if self.hooks["compileResource"] is not None:
            self.hooks["compileResource"](fn)
        else:
            self.__compileQRC(fn)
        
    def __compileAllResources(self):
        """
        Private method to compile all resources to source files.
        """
        if self.hooks["compileAllResources"] is not None:
            self.hooks["compileAllResources"](self.project.pdata["RESOURCES"])
        else:
            numResources = len(self.project.pdata["RESOURCES"])
            progress = KQProgressDialog(self.trUtf8("Compiling resources..."), 
                self.trUtf8("Abort"), 0, numResources, self)
            progress.setModal(True)
            progress.setMinimumDuration(0)
            i = 0
            
            for fn in self.project.pdata["RESOURCES"]:
                progress.setValue(i)
                if progress.wasCanceled():
                    break
                proc = self.__compileQRC(fn, True, progress)
                if proc is not None:
                    while proc.state() == QProcess.Running:
                        QApplication.processEvents()
                        QThread.msleep(300)
                        QApplication.processEvents()
                else:
                    break
                i += 1
                
            progress.setValue(numResources)
        
    def __compileSelectedResources(self):
        """
        Private method to compile selected resources to source files.
        """
        items = self.getSelectedItems()
        files = [unicode(itm.fileName()).replace(self.project.ppath+os.sep, '') \
                 for itm in items]
        
        if self.hooks["compileSelectedResources"] is not None:
            self.hooks["compileSelectedResources"](files)
        else:
            numResources = len(files)
            progress = KQProgressDialog(self.trUtf8("Compiling resources..."), 
                self.trUtf8("Abort"), 0, numResources, self)
            progress.setModal(True)
            progress.setMinimumDuration(0)
            i = 0
            
            for fn in files:
                progress.setValue(i)
                if progress.wasCanceled():
                    break
                if not fn.endswith('.ui.h'):
                    proc = self.__compileQRC(fn, True, progress)
                    if proc is not None:
                        while proc.state() == QProcess.Running:
                            QApplication.processEvents()
                            QThread.msleep(300)
                            QApplication.processEvents()
                    else:
                        break
                i += 1
                
            progress.setValue(numResources)
        
    def __checkResourcesNewer(self, filename, mtime):
        """
        Private method to check, if any file referenced in a resource
        file is newer than a given time.
        
        @param filename filename of the resource file (string)
        @param mtime modification time to check against
        @return flag indicating some file is newer (boolean)
        """
        try:
            f = open(filename, "r")
            buf = f.read()
            f.close()
        except IOError:
            return False
        
        lbuf = ""
        for line in buf.splitlines():
            line = line.strip()
            if line.lower().startswith("<file>") or line.lower().startswith("<file "):
                lbuf = line
            elif lbuf:
                lbuf = "%s%s" % (lbuf, line)
            if lbuf.lower().endswith("</file>"):
                rfile = lbuf.split(">", 1)[1].split("<", 1)[0]
                if not os.path.isabs(rfile):
                    rfile = os.path.join(self.project.ppath, rfile)
                if os.path.exists(rfile) and \
                   os.stat(rfile).st_mtime > mtime:
                       return True
                
                lbuf = ""
        
        return False
        
    def compileChangedResources(self):
        """
        Public method to compile all changed resources to source files.
        """
        if self.hooks["compileChangedResources"] is not None:
            self.hooks["compileChangedResources"](self.project.pdata["RESOURCES"])
        else:
            progress = KQProgressDialog(self.trUtf8("Determining changed resources..."), 
                QString(), 0, 100)
            progress.setMinimumDuration(0)
            i = 0
            
            # get list of changed resources
            changedResources = []
            progress.setMaximum(len(self.project.pdata["RESOURCES"]))
            for fn in self.project.pdata["RESOURCES"]:
                progress.setValue(i)
                QApplication.processEvents()
                ifn = os.path.join(self.project.ppath, fn)
                if self.project.pdata["PROGLANGUAGE"][0] in ["Python", "Python3"]:
                    dirname, filename = os.path.split(os.path.splitext(ifn)[0])
                    ofn = os.path.join(dirname, 
                                       self.RCFilenameFormatPython % filename)
                elif self.project.pdata["PROGLANGUAGE"][0] == "Ruby":
                    dirname, filename = os.path.split(os.path.splitext(ifn)[0])
                    ofn = os.path.join(dirname, 
                                       self.RCFilenameFormatRuby % filename)
                else:
                    return
                if not os.path.exists(ofn) or \
                   os.stat(ifn).st_mtime > os.stat(ofn).st_mtime:
                    changedResources.append(fn)
                elif self.__checkResourcesNewer(ifn, os.stat(ofn).st_mtime):
                    changedResources.append(fn)
                i += 1
            progress.setValue(i)
            QApplication.processEvents()
            
            if changedResources:
                progress.setLabelText(self.trUtf8("Compiling changed resources..."))
                progress.setMaximum(len(changedResources))
                i = 0
                progress.setValue(i)
                QApplication.processEvents()
                for fn in changedResources:
                    progress.setValue(i)
                    proc = self.__compileQRC(fn, True, progress)
                    if proc is not None:
                        while proc.state() == QProcess.Running:
                            QApplication.processEvents()
                            QThread.msleep(300)
                            QApplication.processEvents()
                    else:
                        break
                    i += 1
                progress.setValue(len(changedResources))
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
        <li>compileResource: takes filename as parameter</li>
        <li>compileAllResources: takes list of filenames as parameter</li>
        <li>compileChangedResources: takes list of filenames as parameter</li>
        <li>compileSelectedResources: takes list of all form filenames as parameter</li>
        <li>newResource: takes full directory path of new file as parameter</li>
        </ul>
        
        <b>Note</b>: Filenames are relative to the project directory, if not
        specified differently.
        """
        self.hooks = {
            "compileResource"           : None, 
            "compileAllResources"       : None, 
            "compileChangedResources"   : None, 
            "compileSelectedResources"  : None, 
            "newResource"               : None, 
        }
