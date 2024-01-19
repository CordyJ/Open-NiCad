# -*- coding: utf-8 -*-

# Copyright (c) 2002 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a browser with class browsing capabilities.
"""

import sys
import os
import mimetypes

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from KdeQt import KQFileDialog
from KdeQt.KQApplication import e4App

from BrowserModel import BrowserModel, \
    BrowserDirectoryItem, BrowserFileItem, BrowserClassItem, BrowserMethodItem, \
    BrowserClassAttributeItem
from BrowserSortFilterProxyModel import BrowserSortFilterProxyModel

import UI.PixmapCache
import Preferences
import Utilities

class Browser(QTreeView):
    """
    Class used to display a file system tree. 
    
    Via the context menu that
    is displayed by a right click the user can select various actions on
    the selected file.
    
    @signal sourceFile(string, int, string) emitted to open a Python file at a line 
    @signal designerFile(string) emitted to open a Qt-Designer file
    @signal linguistFile(string) emitted to open a Qt-Linguist (*.ts) file
    @signal trpreview(string list) emitted to preview a Qt-Linguist (*.qm) file
    @signal projectFile(string) emitted to open an eric4 project file
    @signal multiProjectFile(string) emitted to open an eric4 multi project file
    @signal pixmapFile(string) emitted to open a pixmap file
    @signal pixmapEditFile(string) emitted to edit a pixmap file
    @signal svgFile(string) emitted to open a SVG file
    @signal unittestOpen(string) emitted to open a Python file for a unittest
    """
    def __init__(self, parent = None):
        """
        Constructor
        
        @param parent parent widget (QWidget)
        """
        QTreeView.__init__(self, parent)
        
        self.setWindowTitle(QApplication.translate('Browser', 'File-Browser'))
        self.setWindowIcon(UI.PixmapCache.getIcon("eric.png"))
        
        self.__embeddedBrowser = Preferences.getUI("LayoutFileBrowserEmbedded")
        
        self.__model = BrowserModel()
        self.__sortModel = BrowserSortFilterProxyModel()
        self.__sortModel.setSourceModel(self.__model)
        self.setModel(self.__sortModel)
        
        self.selectedItemsFilter = [BrowserFileItem]
        
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.connect(self, SIGNAL("customContextMenuRequested(const QPoint &)"),
                     self._contextMenuRequested)
        self.connect(self, SIGNAL("activated(const QModelIndex &)"), self._openItem)
        self.connect(self, SIGNAL("expanded(const QModelIndex &)"), self._resizeColumns)
        self.connect(self, SIGNAL("collapsed(const QModelIndex &)"), self._resizeColumns)
        
        self.setWhatsThis(QApplication.translate('Browser', 
            """<b>The Browser Window</b>"""
            """<p>This allows you to easily navigate the hierachy of directories and"""
            """ files on your system, identify the Python programs and open them up in"""
            """ a Source Viewer window. The window displays several separate"""
            """ hierachies.</p>"""
            """<p>The first hierachy is only shown if you have opened a program for"""
            """ debugging and it's root is the directory containing that program."""
            """ Usually all of the separate files that make up a Python application are"""
            """ held in the same directory, so this hierachy gives you easy access to"""
            """ most of what you will need.</p>"""
            """<p>The next hierachy is used to easily navigate the directories that are"""
            """ specified in the Python <tt>sys.path</tt> variable.</p>"""
            """<p>The remaining hierachies allow you navigate your system as a whole."""
            """ On a UNIX system there will be a hierachy with <tt>/</tt> at its"""
            """ root and another with the user home directory."""
            """ On a Windows system there will be a hierachy for each drive on the"""
            """ system.</p>"""
            """<p>Python programs (i.e. those with a <tt>.py</tt> file name suffix)"""
            """ are identified in the hierachies with a Python icon."""
            """ The right mouse button will popup a menu which lets you"""
            """ open the file in a Source Viewer window,"""
            """ open the file for debugging or use it for a unittest run.</p>"""
            """<p>The context menu of a class, function or method allows you to open"""
            """ the file defining this class, function or method and will ensure, that"""
            """ the correct source line is visible.</p>"""
            """<p>Qt-Designer files (i.e. those with a <tt>.ui</tt> file name suffix)"""
            """ are shown with a Designer icon. The context menu of these files"""
            """ allows you to start Qt-Designer with that file.</p>"""
            """<p>Qt-Linguist files (i.e. those with a <tt>.ts</tt> file name suffix)"""
            """ are shown with a Linguist icon. The context menu of these files"""
            """ allows you to start Qt-Linguist with that file.</p>"""
        ))
        
        self.__createPopupMenus()
        
        self._init()    # perform common initialization tasks
        
    def _init(self):
        """
        Protected method to perform initialization tasks common to this
        base class and all derived classes.
        """
        self.setRootIsDecorated(True)
        self.setAlternatingRowColors(True)
        
        header = self.header()
        header.setSortIndicator(0, Qt.AscendingOrder)
        header.setSortIndicatorShown(True)
        header.setClickable(True)
        
        self.setSortingEnabled(True)
        
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        
        self.header().setStretchLastSection(True)
        self.headerSize0 = 0
        self.layoutDisplay()
        
    def layoutDisplay(self):
        """
        Public slot to perform a layout operation.
        """
        self.doItemsLayout()
        self._resizeColumns(QModelIndex())
        self._resort()
        
    def _resizeColumns(self, index):
        """
        Protected slot to resize the view when items get expanded or collapsed.
        
        @param index index of item (QModelIndex)
        """
        w = max(100, self.sizeHintForColumn(0))
        if w != self.headerSize0:
            self.header().resizeSection(0, w)
            self.headerSize0 = w
    
    def _resort(self):
        """
        Protected slot to resort the tree.
        """
        self.model().sort(self.header().sortIndicatorSection(), 
                          self.header().sortIndicatorOrder())
        
    def __createPopupMenus(self):
        """
        Private method to generate the various popup menus.
        """
        # create the popup menu for source files
        self.sourceMenu = QMenu(self)
        self.sourceMenu.addAction(QApplication.translate('Browser', 'Open'), 
            self._openItem)
        self.unittestAct = self.sourceMenu.addAction(\
            QApplication.translate('Browser', 'Run unittest...'), self.handleUnittest)
        self.sourceMenu.addAction(
            QApplication.translate('Browser', 'Copy Path to Clipboard'), 
            self._copyToClipboard)
        
        # create the popup menu for general use
        self.menu = QMenu(self)
        self.menu.addAction(QApplication.translate('Browser', 'Open'), self._openItem)
        self.editPixmapAct = \
            self.menu.addAction(QApplication.translate('Browser', 'Open in Icon Editor'), 
            self._editPixmap)
        self.menu.addAction(
            QApplication.translate('Browser', 'Copy Path to Clipboard'), 
            self._copyToClipboard)
        if self.__embeddedBrowser in [1, 2]:
            self.menu.addSeparator()
            self.menu.addAction(QApplication.translate('Browser', 'Configure...'), 
                                self.__configure)

        # create the menu for multiple selected files
        self.multiMenu = QMenu(self)
        self.multiMenu.addAction(QApplication.translate('Browser', 'Open'), 
            self._openItem)
        if self.__embeddedBrowser in [1, 2]:
            self.multiMenu.addSeparator()
            self.multiMenu.addAction(QApplication.translate('Browser', 'Configure...'), 
                                     self.__configure)
        
        # create the directory menu
        self.dirMenu = QMenu(self)
        self.dirMenu.addAction(QApplication.translate('Browser', 
            'New toplevel directory...'), 
            self.__newToplevelDir)
        self.addAsTopLevelAct = self.dirMenu.addAction(\
            QApplication.translate('Browser', 'Add as toplevel directory'),
            self.__addAsToplevelDir)
        self.removeFromToplevelAct = self.dirMenu.addAction(\
            QApplication.translate('Browser', 'Remove from toplevel'),
            self.__removeToplevel)
        self.dirMenu.addSeparator()
        self.dirMenu.addAction(QApplication.translate('Browser', 
            'Find in this directory'),
            self.__findInDirectory)
        self.dirMenu.addAction(QApplication.translate('Browser', 
            'Find&&Replace in this directory'),
            self.__replaceInDirectory)
        self.dirMenu.addAction(
            QApplication.translate('Browser', 'Copy Path to Clipboard'), 
            self._copyToClipboard)
        if self.__embeddedBrowser in [1, 2]:
            self.dirMenu.addSeparator()
            self.dirMenu.addAction(QApplication.translate('Browser', 'Configure...'), 
                                   self.__configure)
        
        # create the background menu
        self.backMenu = QMenu(self)
        self.backMenu.addAction(QApplication.translate('Browser', 
            'New toplevel directory...'), 
            self.__newToplevelDir)
        if self.__embeddedBrowser in [1, 2]:
            self.backMenu.addSeparator()
            self.backMenu.addAction(QApplication.translate('Browser', 'Configure...'), 
                                    self.__configure)

    def mouseDoubleClickEvent(self, mouseEvent):
        """
        Protected method of QAbstractItemView. 
        
        Reimplemented to disable expanding/collapsing
        of items when double-clicking. Instead the double-clicked entry is opened.
        
        @param mouseEvent the mouse event (QMouseEvent)
        """
        index = self.indexAt(mouseEvent.pos())
        if index.isValid():
            self._openItem()

    def _contextMenuRequested(self, coord):
        """
        Protected slot to show the context menu of the listview.
        
        @param coord the position of the mouse pointer (QPoint)
        """
        categories = self.getSelectedItemsCountCategorized(\
            [BrowserDirectoryItem, BrowserFileItem, 
             BrowserClassItem, BrowserMethodItem])
        cnt = categories["sum"]
        bfcnt = categories[unicode(BrowserFileItem)]
        if cnt > 1 and cnt == bfcnt:
            self.multiMenu.popup(self.mapToGlobal(coord))
        else:
            index = self.indexAt(coord)
            
            if index.isValid():
                self.setCurrentIndex(index)
                flags = QItemSelectionModel.SelectionFlags(\
                    QItemSelectionModel.ClearAndSelect | QItemSelectionModel.Rows)
                self.selectionModel().select(index, flags)
                
                itm = self.model().item(index)
                coord = self.mapToGlobal(coord)
                if isinstance(itm, BrowserFileItem):
                    if itm.isPythonFile():
                        if itm.fileName().endswith('.py'):
                            self.unittestAct.setEnabled(True)
                        else:
                            self.unittestAct.setEnabled(False)
                        self.sourceMenu.popup(coord)
                    else:
                        self.editPixmapAct.setVisible(itm.isPixmapFile())
                        self.menu.popup(coord)
                elif isinstance(itm, BrowserClassItem) or \
                        isinstance(itm, BrowserMethodItem):
                    self.menu.popup(coord)
                elif isinstance(itm, BrowserDirectoryItem):
                    if not index.parent().isValid():
                        self.removeFromToplevelAct.setEnabled(True)
                        self.addAsTopLevelAct.setEnabled(False)
                    else:
                        self.removeFromToplevelAct.setEnabled(False)
                        self.addAsTopLevelAct.setEnabled(True)
                    self.dirMenu.popup(coord)
                else:
                    self.backMenu.popup(coord)
            else:
                self.backMenu.popup(self.mapToGlobal(coord))
        
    def handlePreferencesChanged(self):
        """
        Public slot used to handle the preferencesChanged signal.
        """
        self.model().preferencesChanged()
        self._resort()
        
    def _openItem(self):
        """
        Protected slot to handle the open popup menu entry.
        """
        itmList = self.getSelectedItems(\
            [BrowserFileItem, BrowserClassItem, 
             BrowserMethodItem, BrowserClassAttributeItem])
        
        for itm in itmList:
            if isinstance(itm, BrowserFileItem):
                if itm.isPythonFile():
                    self.emit(SIGNAL('sourceFile'), itm.fileName(), 1, "Python")
                elif itm.isPython3File():
                    self.emit(SIGNAL('sourceFile'), itm.fileName(), 1, "Python3")
                elif itm.isRubyFile():
                    self.emit(SIGNAL('sourceFile'), itm.fileName(), 1, "Ruby")
                elif itm.isDFile():
                    self.emit(SIGNAL('sourceFile'), itm.fileName(), 1, "D")
                elif itm.isDesignerFile():
                    self.emit(SIGNAL('designerFile'), itm.fileName())
                elif itm.isDesignerHeaderFile():
                    self.emit(SIGNAL('sourceFile'), itm.fileName())
                elif itm.isLinguistFile():
                    if itm.fileExt() == '.ts':
                        self.emit(SIGNAL('linguistFile'), itm.fileName())
                    else:
                        self.emit(SIGNAL('trpreview'), [itm.fileName()])
                elif itm.isProjectFile():
                    self.emit(SIGNAL('projectFile'), itm.fileName())
                elif itm.isMultiProjectFile():
                    self.emit(SIGNAL('multiProjectFile'), itm.fileName())
                elif itm.isIdlFile():
                    self.emit(SIGNAL('sourceFile'), itm.fileName())
                elif itm.isResourcesFile():
                    self.emit(SIGNAL('sourceFile'), itm.fileName())
                elif itm.isPixmapFile():
                    self.emit(SIGNAL('pixmapFile'), itm.fileName())
                elif itm.isSvgFile():
                    self.emit(SIGNAL('svgFile'), itm.fileName())
                else:
                    type_ = mimetypes.guess_type(itm.fileName())[0]
                    if type_ is None or type_.split("/")[0] == "text":
                        self.emit(SIGNAL('sourceFile'), itm.fileName())
                    else:
                        QDesktopServices.openUrl(QUrl(itm.fileName()))
            elif isinstance(itm, BrowserClassItem):
                self.emit(SIGNAL('sourceFile'), itm.fileName(), 
                    itm.classObject().lineno)
            elif isinstance(itm, BrowserMethodItem):
                self.emit(SIGNAL('sourceFile'), itm.fileName(), 
                    itm.functionObject().lineno)
            elif isinstance(itm, BrowserClassAttributeItem):
                self.emit(SIGNAL('sourceFile'), itm.fileName(), 
                    itm.attributeObject().lineno)
        
    def _editPixmap(self):
        """
        Protected slot to handle the open in icon editor popup menu entry.
        """
        itmList = self.getSelectedItems([BrowserFileItem])
        
        for itm in itmList:
            if isinstance(itm, BrowserFileItem):
                if itm.isPixmapFile():
                    self.emit(SIGNAL('pixmapEditFile'), itm.fileName())
        
    def _copyToClipboard(self):
        """
        Protected method to copy the text shown for an entry to the clipboard.
        """
        itm = self.model().item(self.currentIndex())
        try:
            fn = unicode(itm.fileName())
        except AttributeError:
            try:
                fn = unicode(itm.dirName())
            except AttributeError:
                fn = ""
        
        if fn:
            cb = QApplication.clipboard()
            cb.setText(fn)
        
    def handleUnittest(self):
        """
        Public slot to handle the unittest popup menu entry.
        """
        try:
            index = self.currentIndex()
            itm = self.model().item(index)
            pyfn = itm.fileName()
        except AttributeError:
            pyfn = None

        if pyfn is not None:
            self.emit(SIGNAL('unittestOpen'), pyfn)
        
    def __newToplevelDir(self):
        """
        Private slot to handle the New toplevel directory popup menu entry.
        """
        dname = KQFileDialog.getExistingDirectory(\
            None,
            QApplication.translate('Browser', "New toplevel directory"),
            QString(),
            QFileDialog.Options(QFileDialog.ShowDirsOnly))
        if not dname.isEmpty():
            dname = os.path.abspath(unicode(Utilities.toNativeSeparators(dname)))
            self.__model.addTopLevelDir(dname)
        
    def __removeToplevel(self):
        """
        Private slot to handle the Remove from toplevel popup menu entry.
        """
        index = self.currentIndex()
        sindex = self.model().mapToSource(index)
        self.__model.removeToplevelDir(sindex)
        
    def __addAsToplevelDir(self):
        """
        Private slot to handle the Add as toplevel directory popup menu entry.
        """
        index = self.currentIndex()
        dname = self.model().item(index).dirName()
        self.__model.addTopLevelDir(dname)
        
    def __findInDirectory(self):
        """
        Private slot to handle the Find in directory popup menu entry.
        """
        index = self.currentIndex()
        searchDir = self.model().item(index).dirName()
        
        findFilesDialog = e4App().getObject("FindFilesDialog")
        findFilesDialog.setSearchDirectory(searchDir)
        findFilesDialog.show()
        findFilesDialog.raise_()
        findFilesDialog.activateWindow()
        
    def __replaceInDirectory(self):
        """
        Private slot to handle the Find&Replace in directory popup menu entry.
        """
        index = self.currentIndex()
        searchDir = self.model().item(index).dirName()
        
        replaceFilesDialog = e4App().getObject("ReplaceFilesDialog")
        replaceFilesDialog.setSearchDirectory(searchDir)
        replaceFilesDialog.show()
        replaceFilesDialog.raise_()
        replaceFilesDialog.activateWindow()
        
    def handleProgramChange(self,fn):
        """
        Public slot to handle the programChange signal.
        """
        self.__model.programChange(os.path.dirname(fn))
        
    def wantedItem(self, itm, filter=None):
        """
        Public method to check type of an item.
        
        @param itm the item to check (BrowserItem)
        @param filter list of classes to check against
        @return flag indicating item is a valid type (boolean)
        """
        if filter is None:
            filter = self.selectedItemsFilter
        for typ in filter:
            if isinstance(itm, typ):
                return True
        return False
        
    def getSelectedItems(self, filter=None):
        """
        Public method to get the selected items.
        
        @param filter list of classes to check against
        @return list of selected items (list of BroweserItem)
        """
        selectedItems = []
        indexes = self.selectedIndexes()
        for index in indexes:
            if index.column() == 0:
                itm = self.model().item(index)
                if self.wantedItem(itm, filter):
                    selectedItems.append(itm)
        return selectedItems
        
    def getSelectedItemsCount(self, filter=None):
        """
        Public method to get the count of items selected.
        
        @param filter list of classes to check against
        @return count of items selected (integer)
        """
        count = 0
        indexes = self.selectedIndexes()
        for index in indexes:
            if index.column() == 0:
                itm = self.model().item(index)
                if self.wantedItem(itm, filter):
                    count += 1
        return count
        
    def getSelectedItemsCountCategorized(self, filter=None):
        """
        Public method to get a categorized count of selected items.
        
        @param filter list of classes to check against
        @return a dictionary containing the counts of items belonging
            to the individual filter classes. The keys of the dictionary
            are the unicode representation of the classes given in the
            filter (i.e. unicode(filterClass)). The dictionary contains
            an additional entry with key "sum", that stores the sum of
            all selected entries fulfilling the filter criteria.
        """
        if filter is None:
            filter = self.selectedItemsFilter
        categories = {}
        categories["sum"] = 0
        for typ in filter:
            categories[unicode(typ)] = 0
        
        indexes = self.selectedIndexes()
        for index in indexes:
            if index.column() == 0:
                itm = self.model().item(index)
                for typ in filter:
                    if isinstance(itm, typ):
                        categories["sum"] += 1
                        categories[unicode(typ)] += 1
        
        return categories
        
    def saveToplevelDirs(self):
        """
        Public slot to save the toplevel directories.
        """
        self.__model.saveToplevelDirs()
    
    def __configure(self):
        """
        Private method to open the configuration dialog.
        """
        if self.__embeddedBrowser == 1:
            e4App().getObject("UserInterface").showPreferences("debuggerGeneralPage")
        elif self.__embeddedBrowser == 2:
            e4App().getObject("UserInterface").showPreferences("projectBrowserPage")
