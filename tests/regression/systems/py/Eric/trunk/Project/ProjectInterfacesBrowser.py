# -*- coding: utf-8 -*-

# Copyright (c) 2002 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the a class used to display the interfaces (IDL) part of the project.
"""

import os
import sys
import glob

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from KdeQt import KQMessageBox
from KdeQt.KQProgressDialog import KQProgressDialog
from KdeQt.KQApplication import e4App

from ProjectBrowserModel import ProjectBrowserFileItem, \
    ProjectBrowserSimpleDirectoryItem, ProjectBrowserDirectoryItem, \
    ProjectBrowserInterfaceType
from ProjectBaseBrowser import ProjectBaseBrowser

from UI.BrowserModel import BrowserFileItem, BrowserClassItem, BrowserMethodItem, \
    BrowserClassAttributeItem
from UI.DeleteFilesConfirmationDialog import DeleteFilesConfirmationDialog
import UI.PixmapCache

import Preferences
import Utilities

class ProjectInterfacesBrowser(ProjectBaseBrowser):
    """
    A class used to display the interfaces (IDL) part of the project. 
    
    @signal closeSourceWindow(string) emitted after a file has been removed/deleted 
            from the project
    @signal appendStdout(string) emitted after something was received from
            a QProcess on stdout
    @signal appendStderr(string) emitted after something was received from
            a QProcess on stderr
    @signal showMenu(string, QMenu) emitted when a menu is about to be shown. The name
            of the menu and a reference to the menu are given.
    """
    def __init__(self, project, parent = None):
        """
        Constructor
        
        @param project reference to the project object
        @param parent parent widget of this browser (QWidget)
        """
        self.omniidl = unicode(Preferences.getCorba("omniidl"))
        if self.omniidl == "":
            self.omniidl = Utilities.isWindowsPlatform() and "omniidl.exe" or "omniidl"
        if not Utilities.isinpath(self.omniidl):
            self.omniidl = None
        
        ProjectBaseBrowser.__init__(self, project, ProjectBrowserInterfaceType, parent)
        
        self.selectedItemsFilter = \
            [ProjectBrowserFileItem, ProjectBrowserSimpleDirectoryItem]
        
        self.setWindowTitle(self.trUtf8('Interfaces (IDL)'))
        
        self.setWhatsThis(self.trUtf8(
            """<b>Project Interfaces Browser</b>"""
            """<p>This allows to easily see all interfaces (CORBA IDL files)"""
            """ contained in the current project. Several actions can be executed"""
            """ via the context menu.</p>"""
        ))
        
        self.connect(project, SIGNAL("prepareRepopulateItem"), 
            self._prepareRepopulateItem)
        self.connect(project, SIGNAL("completeRepopulateItem"),
            self._completeRepopulateItem)
        
    def _createPopupMenus(self):
        """
        Protected overloaded method to generate the popup menu.
        """
        self.menuActions = []
        self.multiMenuActions = []
        self.dirMenuActions = []
        self.dirMultiMenuActions = []
        
        self.sourceMenu = QMenu(self)
        if self.omniidl is not None:
            self.sourceMenu.addAction(self.trUtf8('Compile interface'), 
                self.__compileInterface)
            self.sourceMenu.addAction(self.trUtf8('Compile all interfaces'), 
                self.__compileAllInterfaces)
        self.sourceMenu.addAction(self.trUtf8('Open'), self._openItem)
        self.sourceMenu.addSeparator()
        act = self.sourceMenu.addAction(self.trUtf8('Rename file'), self._renameFile)
        self.menuActions.append(act)
        act = self.sourceMenu.addAction(self.trUtf8('Remove from project'), 
            self._removeFile)
        self.menuActions.append(act)
        act = self.sourceMenu.addAction(self.trUtf8('Delete'), self.__deleteFile)
        self.menuActions.append(act)
        self.sourceMenu.addSeparator()
        self.sourceMenu.addAction(self.trUtf8('Add interfaces...'), 
            self.__addInterfaceFiles)
        self.sourceMenu.addAction(self.trUtf8('Add interfaces directory...'), 
            self.__addInterfacesDirectory)
        self.sourceMenu.addSeparator()
        self.sourceMenu.addAction(self.trUtf8('Copy Path to Clipboard'), 
            self._copyToClipboard)
        self.sourceMenu.addSeparator()
        self.sourceMenu.addAction(self.trUtf8('Expand all directories'), 
            self._expandAllDirs)
        self.sourceMenu.addAction(self.trUtf8('Collapse all directories'), 
            self._collapseAllDirs)
        self.sourceMenu.addSeparator()
        self.sourceMenu.addAction(self.trUtf8('Configure...'), self._configure)
        self.sourceMenu.addAction(self.trUtf8('Configure CORBA...'), self.__configureCorba)

        self.menu = QMenu(self)
        if self.omniidl is not None:
            self.menu.addAction(self.trUtf8('Compile interface'), self.__compileInterface)
            self.menu.addAction(self.trUtf8('Compile all interfaces'), 
                self.__compileAllInterfaces)
        self.menu.addAction(self.trUtf8('Open'), self._openItem)
        self.menu.addSeparator()
        self.menu.addAction(self.trUtf8('Add interfaces...'), self.__addInterfaceFiles)
        self.menu.addAction(self.trUtf8('Add interfaces directory...'), 
            self.__addInterfacesDirectory)
        self.menu.addSeparator()
        self.menu.addAction(self.trUtf8('Expand all directories'), 
            self._expandAllDirs)
        self.menu.addAction(self.trUtf8('Collapse all directories'), 
            self._collapseAllDirs)
        self.menu.addSeparator()
        self.menu.addAction(self.trUtf8('Configure...'), self._configure)
        self.menu.addAction(self.trUtf8('Configure CORBA...'), self.__configureCorba)

        self.backMenu = QMenu(self)
        if self.omniidl is not None:
            self.backMenu.addAction(self.trUtf8('Compile all interfaces'), 
                self.__compileAllInterfaces)
            self.backMenu.addSeparator()
        self.backMenu.addAction(self.trUtf8('Add interfaces...'), 
            self.project.addIdlFiles)
        self.backMenu.addAction(self.trUtf8('Add interfaces directory...'), 
            self.project.addIdlDir)
        self.backMenu.addSeparator()
        self.backMenu.addAction(self.trUtf8('Expand all directories'), 
            self._expandAllDirs)
        self.backMenu.addAction(self.trUtf8('Collapse all directories'), 
            self._collapseAllDirs)
        self.backMenu.addSeparator()
        self.backMenu.addAction(self.trUtf8('Configure...'), self._configure)
        self.backMenu.addAction(self.trUtf8('Configure CORBA...'), self.__configureCorba)
        self.backMenu.setEnabled(False)

        # create the menu for multiple selected files
        self.multiMenu = QMenu(self)
        if self.omniidl is not None:
            self.multiMenu.addAction(self.trUtf8('Compile interfaces'),
                self.__compileSelectedInterfaces)
        self.multiMenu.addAction(self.trUtf8('Open'), self._openItem)
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
        self.multiMenu.addAction(self.trUtf8('Configure CORBA...'), self.__configureCorba)

        self.dirMenu = QMenu(self)
        if self.omniidl is not None:
            self.dirMenu.addAction(self.trUtf8('Compile all interfaces'), 
                self.__compileAllInterfaces)
            self.dirMenu.addSeparator()
        act = self.dirMenu.addAction(self.trUtf8('Remove from project'), self._removeFile)
        self.dirMenuActions.append(act)
        self.dirMenu.addSeparator()
        self.dirMenu.addAction(self.trUtf8('Add interfaces...'), self.__addInterfaceFiles)
        self.dirMenu.addAction(self.trUtf8('Add interfaces directory...'), 
            self.__addInterfacesDirectory)
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
        self.dirMenu.addAction(self.trUtf8('Configure CORBA...'), self.__configureCorba)
        
        self.dirMultiMenu = QMenu(self)
        if self.omniidl is not None:
            self.dirMultiMenu.addAction(self.trUtf8('Compile all interfaces'), 
                self.__compileAllInterfaces)
            self.dirMultiMenu.addSeparator()
        self.dirMultiMenu.addAction(self.trUtf8('Add interfaces...'), 
            self.project.addIdlFiles)
        self.dirMultiMenu.addAction(self.trUtf8('Add interfaces directory...'), 
            self.project.addIdlDir)
        self.dirMultiMenu.addSeparator()
        self.dirMultiMenu.addAction(self.trUtf8('Expand all directories'), 
            self._expandAllDirs)
        self.dirMultiMenu.addAction(self.trUtf8('Collapse all directories'), 
            self._collapseAllDirs)
        self.dirMultiMenu.addSeparator()
        self.dirMultiMenu.addAction(self.trUtf8('Configure...'), self._configure)
        self.dirMultiMenu.addAction(self.trUtf8('Configure CORBA...'), 
                                    self.__configureCorba)
        
        self.connect(self.sourceMenu, SIGNAL('aboutToShow()'),
            self.__showContextMenu)
        self.connect(self.multiMenu, SIGNAL('aboutToShow()'),
            self.__showContextMenuMulti)
        self.connect(self.dirMenu, SIGNAL('aboutToShow()'),
            self.__showContextMenuDir)
        self.connect(self.dirMultiMenu, SIGNAL('aboutToShow()'),
            self.__showContextMenuDirMulti)
        self.connect(self.backMenu, SIGNAL('aboutToShow()'),
            self.__showContextMenuBack)
        self.mainMenu = self.sourceMenu
        
    def _contextMenuRequested(self, coord):
        """
        Protected slot to show the context menu.
        
        @param coord the position of the mouse pointer (QPoint)
        """
        if not self.project.isOpen():
            return
        
        try:
            categories = self.getSelectedItemsCountCategorized(\
                [ProjectBrowserFileItem, BrowserClassItem, 
                 BrowserMethodItem, ProjectBrowserSimpleDirectoryItem])
            cnt = categories["sum"]
            if cnt <= 1:
                index = self.indexAt(coord)
                if index.isValid():
                    self._selectSingleItem(index)
                    categories = self.getSelectedItemsCountCategorized(\
                        [ProjectBrowserFileItem, BrowserClassItem, 
                         BrowserMethodItem, ProjectBrowserSimpleDirectoryItem])
                    cnt = categories["sum"]
            
            bfcnt = categories[unicode(ProjectBrowserFileItem)]
            cmcnt = categories[unicode(BrowserClassItem)] + \
                    categories[unicode(BrowserMethodItem)]
            sdcnt = categories[unicode(ProjectBrowserSimpleDirectoryItem)]
            if cnt > 1 and cnt == bfcnt:
                self.multiMenu.popup(self.mapToGlobal(coord))
            elif cnt > 1 and cnt == sdcnt:
                self.dirMultiMenu.popup(self.mapToGlobal(coord))
            else:
                index = self.indexAt(coord)
                if cnt == 1 and index.isValid():
                    if bfcnt == 1 or cmcnt == 1:
                        itm = self.model().item(index)
                        if isinstance(itm, ProjectBrowserFileItem):
                            self.sourceMenu.popup(self.mapToGlobal(coord))
                        elif isinstance(itm, BrowserClassItem) or \
                                isinstance(itm, BrowserMethodItem):
                            self.menu.popup(self.mapToGlobal(coord))
                        else:
                            self.backMenu.popup(self.mapToGlobal(coord))
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
        
    def _openItem(self):
        """
        Protected slot to handle the open popup menu entry.
        """
        itmList = self.getSelectedItems(\
            [BrowserFileItem, BrowserClassItem, BrowserMethodItem, 
             BrowserClassAttributeItem])
        
        for itm in itmList:
            if isinstance(itm, BrowserFileItem):
                self.emit(SIGNAL('sourceFile'), itm.fileName())
            elif isinstance(itm, BrowserClassItem):
                self.emit(SIGNAL('sourceFile'), itm.fileName(), 
                    itm.classObject().lineno)
            elif isinstance(itm,BrowserMethodItem):
                self.emit(SIGNAL('sourceFile'), itm.fileName(), 
                    itm.functionObject().lineno)
            elif isinstance(itm, BrowserClassAttributeItem):
                self.emit(SIGNAL('sourceFile'), itm.fileName(), 
                    itm.attributeObject().lineno)
        
    def __addInterfaceFiles(self):
        """
        Private method to add interface files to the project.
        """
        itm = self.model().item(self.currentIndex())
        if isinstance(itm, ProjectBrowserFileItem) or \
           isinstance(itm, BrowserClassItem) or \
           isinstance(itm, BrowserMethodItem):
            dn = os.path.dirname(unicode(itm.fileName()))
        elif isinstance(itm, ProjectBrowserSimpleDirectoryItem) or \
             isinstance(itm, ProjectBrowserDirectoryItem):
            dn = unicode(itm.dirName())
        else:
            dn = None
        self.project.addFiles('interface', dn)
        
    def __addInterfacesDirectory(self):
        """
        Private method to add interface files of a directory to the project.
        """
        itm = self.model().item(self.currentIndex())
        if isinstance(itm, ProjectBrowserFileItem) or \
           isinstance(itm, BrowserClassItem) or \
           isinstance(itm, BrowserMethodItem):
            dn = os.path.dirname(unicode(itm.fileName()))
        elif isinstance(itm, ProjectBrowserSimpleDirectoryItem) or \
             isinstance(itm, ProjectBrowserDirectoryItem):
            dn = unicode(itm.dirName())
        else:
            dn = None
        self.project.addDirectory('interface', dn)
        
    def __deleteFile(self):
        """
        Private method to delete files from the project.
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
            self.trUtf8("Delete interfaces"),
            self.trUtf8("Do you really want to delete these interfaces from"
                " the project?"),
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
        Private slot to handle the readyReadStandardOutput signal of the omniidl process.
        """
        if self.compileProc is None:
            return
        
        ioEncoding = str(Preferences.getSystem("IOEncoding"))
        
        self.compileProc.setReadChannel(QProcess.StandardOutput)
        while self.compileProc and self.compileProc.canReadLine():
            s = QString('omniidl: ')
            output = unicode(self.compileProc.readLine(), 
                             ioEncoding, 'replace')
            s.append(output)
            self.emit(SIGNAL('appendStdout'), s)
        
    def __readStderr(self):
        """
        Private slot to handle the readyReadStandardError signal of the omniidl process.
        """
        if self.compileProc is None:
            return
        
        ioEncoding = str(Preferences.getSystem("IOEncoding"))
        
        self.compileProc.setReadChannel(QProcess.StandardError)
        while self.compileProc and self.compileProc.canReadLine():
            s = QString('omniidl: ')
            error = unicode(self.compileProc.readLine(), 
                            ioEncoding, 'replace')
            s.append(error)
            self.emit(SIGNAL('appendStderr'), s)
        
    def __compileIDLDone(self, exitCode, exitStatus):
        """
        Private slot to handle the finished signal of the omniidl process.
        
        @param exitCode exit code of the process (integer)
        @param exitStatus exit status of the process (QProcess.ExitStatus)
        """
        self.compileRunning = False
        if exitStatus == QProcess.NormalExit and exitCode == 0:
            path = os.path.dirname(self.idlFile)
            poaList = glob.glob(os.path.join(path, "*__POA"))
            npoaList = [f.replace("__POA", "") for f in poaList]
            fileList = glob.glob(os.path.join(path, "*_idl.py"))
            for dir in poaList + npoaList:
                fileList += Utilities.direntries(dir, True, "*.py")
            for file in fileList:
                self.project.appendFile(file)
            if not self.noDialog:
                KQMessageBox.information(None,
                    self.trUtf8("Interface Compilation"),
                    self.trUtf8("The compilation of the interface file was successful."))
        else:
            if not self.noDialog:
                KQMessageBox.information(None,
                    self.trUtf8("Interface Compilation"),
                    self.trUtf8("The compilation of the interface file failed."))
        self.compileProc = None
        
    def __compileIDL(self, fn, noDialog = False, progress = None):
        """
        Privat method to compile a .idl file to python.

        @param fn filename of the .idl file to be compiled
        @param noDialog flag indicating silent operations
        @param progress reference to the progress dialog
        @return reference to the compile process (QProcess)
        """
        self.compileProc = QProcess()
        args = QStringList()
        
        args.append("-bpython")
        args.append("-I.")
        
        fn = os.path.join(self.project.ppath, fn)
        self.idlFile = fn
        args.append("-C%s" % os.path.dirname(fn))
        args.append(fn)
        
        self.connect(self.compileProc, SIGNAL('finished(int, QProcess::ExitStatus)'), 
            self.__compileIDLDone)
        self.connect(self.compileProc, SIGNAL('readyReadStandardOutput()'), 
            self.__readStdout)
        self.connect(self.compileProc, SIGNAL('readyReadStandardError()'), 
            self.__readStderr)
        
        self.noDialog = noDialog
        self.compileProc.start(self.omniidl, args)
        procStarted = self.compileProc.waitForStarted()
        if procStarted:
            self.compileRunning = True
            return self.compileProc
        else:
            self.compileRunning = False
            if progress is not None:
                progress.cancel()
            KQMessageBox.critical(self,
                self.trUtf8('Process Generation Error'),
                self.trUtf8(
                    '<p>Could not start %1.<br>'
                    'Ensure that it is in the search path.</p>'
                ).arg(self.omniidl))
            return None
        
    def __compileInterface(self):
        """
        Private method to compile an interface to python.
        """
        if self.omniidl is not None:
            itm = self.model().item(self.currentIndex())
            fn2 = unicode(itm.fileName())
            fn = fn2.replace(self.project.ppath+os.sep, '')
            self.__compileIDL(fn)
        
    def __compileAllInterfaces(self):
        """
        Private method to compile all interfaces to python.
        """
        if self.omniidl is not None:
            numIDLs = len(self.project.pdata["INTERFACES"])
            progress = KQProgressDialog(self.trUtf8("Compiling interfaces..."), 
                self.trUtf8("Abort"), 0, numIDLs, self)
            progress.setModal(True)
            progress.setMinimumDuration(0)
            i = 0
            
            for fn in self.project.pdata["INTERFACES"]:
                progress.setValue(i)
                if progress.wasCanceled():
                    break
                proc = self.__compileIDL(fn, True, progress)
                if proc is not None:
                    while proc.state() == QProcess.Running:
                        QApplication.processEvents()
                        QThread.msleep(300)
                        QApplication.processEvents()
                else:
                    break
                i += 1
            
            progress.setValue(numIDLs)
        
    def __compileSelectedInterfaces(self):
        """
        Private method to compile selected interfaces to python.
        """
        if self.omniidl is not None:
            items = self.getSelectedItems()
            
            files = [unicode(itm.fileName()).replace(self.project.ppath+os.sep, '') \
                     for itm in items]
            numIDLs = len(files)
            progress = KQProgressDialog(self.trUtf8("Compiling interfaces..."), 
                self.trUtf8("Abort"), 0, numIDLs, self)
            progress.setModal(True)
            progress.setMinimumDuration(0)
            i = 0
            
            for fn in files:
                progress.setValue(i)
                if progress.wasCanceled():
                    break
                proc = self.__compileIDL(fn, True, progress)
                if proc is not None:
                    while proc.state() == QProcess.Running:
                        QApplication.processEvents()
                        QThread.msleep(300)
                        QApplication.processEvents()
                else:
                    break
                i += 1
                
            progress.setValue(numIDLs)
        
    def __configureCorba(self):
        """
        Private method to open the configuration dialog.
        """
        e4App().getObject("UserInterface").showPreferences("corbaPage")
