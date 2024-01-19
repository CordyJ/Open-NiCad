# -*- coding: utf-8 -*-

# Copyright (c) 2002 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a class used to display the parts of the project, that don't fit 
the other categories.
"""

import os
import sys
import mimetypes

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from ProjectBrowserModel import ProjectBrowserFileItem, \
    ProjectBrowserSimpleDirectoryItem, ProjectBrowserDirectoryItem, \
    ProjectBrowserOthersType
from ProjectBaseBrowser import ProjectBaseBrowser

from UI.BrowserModel import BrowserClassItem, BrowserMethodItem, \
    BrowserDirectoryItem, BrowserFileItem
from UI.DeleteFilesConfirmationDialog import DeleteFilesConfirmationDialog
import UI.PixmapCache

import Preferences

class ProjectOthersBrowser(ProjectBaseBrowser):
    """
    A class used to display the parts of the project, that don't fit the other categories.
    
    @signal sourceFile(string) emitted to open a file
    @signal pixmapFile(string) emitted to open a pixmap file
    @signal pixmapEditFile(string) emitted to edit a pixmap file
    @signal svgFile(string) emitted to open a SVG file
    @signal closeSourceWindow(string) emitted after a file has been removed/deleted
            from the project
    @signal showMenu(string, QMenu) emitted when a menu is about to be shown. The name
            of the menu and a reference to the menu are given.
    """
    def __init__(self, project, parent=None):
        """
        Constructor
        
        @param project reference to the project object
        @param parent parent widget of this browser (QWidget)
        """
        ProjectBaseBrowser.__init__(self, project, ProjectBrowserOthersType, parent)
    
        self.selectedItemsFilter = [ProjectBrowserFileItem, ProjectBrowserDirectoryItem]
        self.specialMenuEntries = [1]

        self.setWindowTitle(self.trUtf8('Others'))

        self.setWhatsThis(self.trUtf8(
            """<b>Project Others Browser</b>"""
            """<p>This allows to easily see all other files and directories"""
            """ contained in the current project. Several actions can be"""
            """ executed via the context menu. The entry which is registered"""
            """ in the project is shown in a different colour.</p>"""
        ))
        
        self.connect(project, SIGNAL("prepareRepopulateItem"), 
            self._prepareRepopulateItem)
        self.connect(project, SIGNAL("completeRepopulateItem"),
            self._completeRepopulateItem)
        
    def _createPopupMenus(self):
        """
        Protected overloaded method to generate the popup menu.
        """
        ProjectBaseBrowser._createPopupMenus(self)
        
        self.editPixmapAct = \
            self.menu.addAction(self.trUtf8('Open in Icon Editor'), 
            self._editPixmap)
        self.menu.addSeparator()
        self.renameFileAct = self.menu.addAction(self.trUtf8('Rename file'), 
            self._renameFile)
        self.menuActions.append(self.renameFileAct)
        act = self.menu.addAction(self.trUtf8('Remove from project'), self.__removeItem)
        self.menuActions.append(act)
        act = self.menu.addAction(self.trUtf8('Delete'), self.__deleteItem)
        self.menuActions.append(act)
        self.menu.addSeparator()
        self.menu.addAction(self.trUtf8('Add files...'), self.project.addOthersFiles)
        self.menu.addAction(self.trUtf8('Add directory...'), self.project.addOthersDir)
        self.menu.addSeparator()
        self.menu.addAction(self.trUtf8('Refresh'), self.__refreshItem)
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
        self.backMenu.addAction(self.trUtf8('Add files...'), 
            self.project.addOthersFiles)
        self.backMenu.addAction(self.trUtf8('Add directory...'), 
            self.project.addOthersDir)
        self.backMenu.addSeparator()
        self.backMenu.addAction(self.trUtf8('Expand all directories'), 
            self._expandAllDirs)
        self.backMenu.addAction(self.trUtf8('Collapse all directories'), 
            self._collapseAllDirs)
        self.backMenu.addSeparator()
        self.backMenu.addAction(self.trUtf8('Configure...'), self._configure)
        self.backMenu.setEnabled(False)

        self.multiMenu.addSeparator()
        act = self.multiMenu.addAction(self.trUtf8('Remove from project'), 
            self.__removeItem)
        self.multiMenuActions.append(act)
        act = self.multiMenu.addAction(self.trUtf8('Delete'), self.__deleteItem)
        self.multiMenuActions.append(act)
        self.multiMenu.addSeparator()
        self.multiMenu.addAction(self.trUtf8('Expand all directories'), 
            self._expandAllDirs)
        self.multiMenu.addAction(self.trUtf8('Collapse all directories'), 
            self._collapseAllDirs)
        self.multiMenu.addSeparator()
        self.multiMenu.addAction(self.trUtf8('Configure...'), self._configure)
        
        self.connect(self.menu, SIGNAL('aboutToShow()'),
            self.__showContextMenu)
        self.connect(self.multiMenu, SIGNAL('aboutToShow()'),
            self.__showContextMenuMulti)
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
            cnt = self.getSelectedItemsCount()
            if cnt <= 1:
                index = self.indexAt(coord)
                if index.isValid():
                    self._selectSingleItem(index)
                    cnt = self.getSelectedItemsCount()
            
            if cnt > 1:
                self.multiMenu.popup(self.mapToGlobal(coord))
            else:
                index = self.indexAt(coord)
                if cnt == 1 and index.isValid():
                    itm = self.model().item(index)
                    if isinstance(itm, ProjectBrowserFileItem):
                        self.editPixmapAct.setVisible(itm.isPixmapFile())
                        self.menu.popup(self.mapToGlobal(coord))
                    elif isinstance(itm, ProjectBrowserDirectoryItem):
                        self.editPixmapAct.setVisible(False)
                        self.menu.popup(self.mapToGlobal(coord))
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
        self._showContextMenu(self.menu)
        
        self.emit(SIGNAL("showMenu"), "Main", self.menu)
        
    def __showContextMenuMulti(self):
        """
        Private slot called by the multiMenu aboutToShow signal.
        """
        ProjectBaseBrowser._showContextMenuMulti(self, self.multiMenu)
        
        self.emit(SIGNAL("showMenu"), "MainMulti", self.multiMenu)
        
    def __showContextMenuBack(self):
        """
        Private slot called by the backMenu aboutToShow signal.
        """
        ProjectBaseBrowser._showContextMenuBack(self, self.backMenu)
        
        self.emit(SIGNAL("showMenu"), "MainBack", self.backMenu)
        
    def _showContextMenu(self, menu):
        """
        Protected slot called before the context menu is shown. 
        
        It enables/disables the VCS menu entries depending on the overall 
        VCS status and the file status.
        
        @param menu Reference to the popup menu (QPopupMenu)
        """
        if self.project.vcs is None:
            for act in self.menuActions:
                act.setEnabled(True)
            itm = self.model().item(self.currentIndex())
            if isinstance(itm, ProjectBrowserSimpleDirectoryItem) or \
               isinstance(itm, ProjectBrowserDirectoryItem):
                self.renameFileAct.setEnabled(False)
        else:
            self.vcsHelper.showContextMenu(menu, self.menuActions)
        
    def _editPixmap(self):
        """
        Protected slot to handle the open in icon editor popup menu entry.
        """
        itmList = self.getSelectedItems()
        
        for itm in itmList:
            if isinstance(itm, ProjectBrowserFileItem):
                if itm.isPixmapFile():
                    self.emit(SIGNAL('pixmapEditFile'), itm.fileName())
        
    def _openItem(self):
        """
        Protected slot to handle the open popup menu entry.
        """
        itmList = self.getSelectedItems()
        
        for itm in itmList:
            if isinstance(itm, ProjectBrowserFileItem):
                if itm.isPixmapFile():
                    self.emit(SIGNAL('pixmapFile'), itm.fileName())
                elif itm.isSvgFile():
                    self.emit(SIGNAL('svgFile'), itm.fileName())
                else:
                    type_ = mimetypes.guess_type(itm.fileName())[0]
                    if type_ is None or type_.split("/")[0] == "text":
                        self.emit(SIGNAL('sourceFile'), itm.fileName())
                    else:
                        QDesktopServices.openUrl(QUrl(itm.fileName()))
        
    def __removeItem(self):
        """
        Private slot to remove the selected entry from the OTHERS project data area.
        """
        itmList = self.getSelectedItems()
        
        for itm in itmList[:]:
            if isinstance(itm, ProjectBrowserFileItem):
                fn = unicode(itm.fileName())
                self.emit(SIGNAL('closeSourceWindow'), fn)
                self.project.removeFile(fn)
            else:
                dn = unicode(itm.dirName())
                self.project.removeDirectory(dn)
        
    def __deleteItem(self):
        """
        Private method to delete the selected entry from the OTHERS project data area.
        """
        itmList = self.getSelectedItems()
        
        items = []
        names = []
        fullNames = []
        dirItems = []
        dirNames = []
        dirFullNames = []
        for itm in itmList:
            if isinstance(itm, ProjectBrowserFileItem):
                fn2 = unicode(itm.fileName())
                fn = fn2.replace(self.project.ppath+os.sep, '')
                items.append(itm)
                fullNames.append(fn2)
                names.append(fn)
            else:
                dn2 = unicode(itm.dirName())
                dn = dn2.replace(self.project.ppath+os.sep, '')
                dirItems.append(itm)
                dirFullNames.append(dn2)
                dirNames.append(dn)
        items.extend(dirItems)
        fullNames.extend(dirFullNames)
        names.extend(dirNames)
        del itmList
        del dirFullNames
        del dirNames
        
        dlg = DeleteFilesConfirmationDialog(self.parent(),
            self.trUtf8("Delete files/directories"),
            self.trUtf8("Do you really want to delete these entries from the project?"),
            names)
        
        if dlg.exec_() == QDialog.Accepted:
            for itm, fn2, fn in zip(items[:], fullNames, names):
                if isinstance(itm, ProjectBrowserFileItem):
                    self.emit(SIGNAL('closeSourceWindow'), fn2)
                    self.project.deleteFile(fn)
                elif isinstance(itm, ProjectBrowserDirectoryItem):
                    self.project.deleteDirectory(fn2)
        
    def __refreshItem(self):
        """
        Private slot to refresh (repopulate) an item.
        """
        itm = self.model().item(self.currentIndex())
        if isinstance(itm, ProjectBrowserFileItem):
            name = itm.fileName()
        elif isinstance(itm, ProjectBrowserDirectoryItem):
            name = itm.dirName()
        else:
            name = ''
        
        if name:
            self.project.repopulateItem(name)
        self._resizeColumns(QModelIndex())
