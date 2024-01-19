# -*- coding: utf-8 -*-

# Copyright (c) 2002 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a tabbed viewmanager class.
"""

import os

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from KdeQt.KQApplication import e4App

from ViewManager.ViewManager import ViewManager

import QScintilla.Editor

import UI.PixmapCache

from E4Gui.E4TabWidget import E4TabWidget, E4WheelTabBar
from E4Gui.E4Led import E4Led

import Preferences

from eric4config import getConfig

class TabBar(E4WheelTabBar):
    """
    Class implementing a customized tab bar supporting drag & drop.
    
    @signal tabMoveRequested(int, int) emitted to signal a tab move request giving
        the old and new index position
    @signal tabRelocateRequested(long, int, int) emitted to signal a tab relocation
        request giving the id of the old tab widget, the index in the old tab widget
        and the new index position
    @signal tabCopyRequested(long, int, int) emitted to signal a clone request
        giving the id of the source tab widget, the index in the source tab widget
        and the new index position
    @signal tabCopyRequested(int, int) emitted to signal a clone request giving
        the old and new index position
    """
    def __init__(self, parent = None):
        """
        Constructor
        
        @param parent reference to the parent widget (QWidget)
        """
        E4WheelTabBar.__init__(self, parent)
        self.setAcceptDrops(True)
        
        self.__dragStartPos = QPoint()
    
    def mousePressEvent(self, event):
        """
        Protected method to handle mouse press events.
        
        @param event reference to the mouse press event (QMouseEvent)
        """
        if event.button() == Qt.LeftButton:
            self.__dragStartPos = QPoint(event.pos())
        E4WheelTabBar.mousePressEvent(self, event)
    
    def mouseMoveEvent(self, event):
        """
        Protected method to handle mouse move events.
        
        @param event reference to the mouse move event (QMouseEvent)
        """
        if event.buttons() == Qt.MouseButtons(Qt.LeftButton) and \
           (event.pos() - self.__dragStartPos).manhattanLength() > \
                QApplication.startDragDistance():
            drag = QDrag(self)
            mimeData = QMimeData()
            index = self.tabAt(event.pos())
            mimeData.setText(self.tabText(index))
            mimeData.setData("action", "tab-reordering")
            mimeData.setData("tabbar-id", QByteArray.number(id(self)))
            mimeData.setData("source-index", 
                             QByteArray.number(self.tabAt(self.__dragStartPos)))
            mimeData.setData("tabwidget-id", QByteArray.number(id(self.parentWidget())))
            drag.setMimeData(mimeData)
            if event.modifiers() == Qt.KeyboardModifiers(Qt.ShiftModifier):
                drag.exec_(Qt.DropActions(Qt.CopyAction))
            elif event.modifiers() == Qt.KeyboardModifiers(Qt.NoModifier):
                drag.exec_(Qt.DropActions(Qt.MoveAction))
        E4WheelTabBar.mouseMoveEvent(self, event)
    
    def dragEnterEvent(self, event):
        """
        Protected method to handle drag enter events.
        
        @param event reference to the drag enter event (QDragEnterEvent)
        """
        mimeData = event.mimeData()
        formats = mimeData.formats()
        if formats.contains("action") and \
           mimeData.data("action") == "tab-reordering" and \
           formats.contains("tabbar-id") and \
           formats.contains("source-index") and \
           formats.contains("tabwidget-id"):
            event.acceptProposedAction()
        E4WheelTabBar.dragEnterEvent(self, event)
    
    def dropEvent(self, event):
        """
        Protected method to handle drop events.
        
        @param event reference to the drop event (QDropEvent)
        """
        mimeData = event.mimeData()
        oldID = mimeData.data("tabbar-id").toLong()[0]
        fromIndex = mimeData.data("source-index").toInt()[0]
        toIndex = self.tabAt(event.pos())
        if oldID != id(self):
            parentID = mimeData.data("tabwidget-id").toLong()[0]
            if event.proposedAction() == Qt.MoveAction:
                self.emit(SIGNAL("tabRelocateRequested(long, int, int)"), 
                          parentID, fromIndex, toIndex)
                event.acceptProposedAction()
            elif event.proposedAction() == Qt.CopyAction:
                self.emit(SIGNAL("tabCopyRequested(long, int, int)"), 
                          parentID, fromIndex, toIndex)
                event.acceptProposedAction()
        else:
            if fromIndex != toIndex:
                if event.proposedAction() == Qt.MoveAction:
                    self.emit(SIGNAL("tabMoveRequested(int, int)"), fromIndex, toIndex)
                    event.acceptProposedAction()
                elif event.proposedAction() == Qt.CopyAction:
                    self.emit(SIGNAL("tabCopyRequested(int, int)"), fromIndex, toIndex)
                    event.acceptProposedAction()
        E4WheelTabBar.dropEvent(self, event)

class TabWidget(E4TabWidget):
    """
    Class implementing a custimized tab widget.
    """
    def __init__(self, vm):
        """
        Constructor
        
        @param vm view manager widget (Tabview)
        """
        E4TabWidget.__init__(self)
        self.setAttribute(Qt.WA_DeleteOnClose, True)
        
        self.__tabBar = TabBar(self)
        self.setTabBar(self.__tabBar)
        
        self.connect(self.__tabBar, SIGNAL("tabMoveRequested(int, int)"), 
                     self.moveTab)
        self.connect(self.__tabBar, SIGNAL("tabRelocateRequested(long, int, int)"), 
                     self.relocateTab)
        self.connect(self.__tabBar, SIGNAL("tabCopyRequested(long, int, int)"), 
                     self.copyTabOther)
        self.connect(self.__tabBar, SIGNAL("tabCopyRequested(int, int)"), 
                     self.copyTab)
        
        self.vm = vm
        self.editors = []
        
        self.indicator = E4Led(self)
        self.setCornerWidget(self.indicator, Qt.TopLeftCorner)
        
        self.rightCornerWidget = QWidget(self)
        self.rightCornerWidgetLayout = QHBoxLayout(self.rightCornerWidget)
        self.rightCornerWidgetLayout.setMargin(0)
        self.rightCornerWidgetLayout.setSpacing(0)
        
        self.__navigationMenu = QMenu(self)
        self.connect(self.__navigationMenu, SIGNAL("aboutToShow()"), 
                     self.__showNavigationMenu)
        self.connect(self.__navigationMenu, SIGNAL("triggered(QAction*)"), 
                     self.__navigationMenuTriggered)
        
        self.navigationButton = QToolButton(self)
        self.navigationButton.setIcon(UI.PixmapCache.getIcon("1downarrow.png"))
        self.navigationButton.setToolTip(self.trUtf8("Show a navigation menu"))
        self.navigationButton.setPopupMode(QToolButton.InstantPopup)
        self.navigationButton.setMenu(self.__navigationMenu)
        self.navigationButton.setEnabled(False)
        self.rightCornerWidgetLayout.addWidget(self.navigationButton)
        
        if Preferences.getUI("SingleCloseButton") or \
           not hasattr(self, 'setTabsClosable'):
            self.closeButton = QToolButton(self)
            self.closeButton.setIcon(UI.PixmapCache.getIcon("close.png"))
            self.closeButton.setToolTip(self.trUtf8("Close the current editor"))
            self.closeButton.setEnabled(False)
            self.connect(self.closeButton, SIGNAL("clicked(bool)"),
                self.__closeButtonClicked)
            self.rightCornerWidgetLayout.addWidget(self.closeButton)
        else:
            self.connect(self, SIGNAL("tabCloseRequested(int)"), 
                self.__closeRequested)
            self.closeButton = None
        
        self.setCornerWidget(self.rightCornerWidget, Qt.TopRightCorner)
        
        self.__initMenu()
        self.contextMenuEditor = None
        self.contextMenuIndex = -1
        
        self.setTabContextMenuPolicy(Qt.CustomContextMenu)
        self.connect(self, SIGNAL('customTabContextMenuRequested(const QPoint &, int)'),
                     self.__showContextMenu)
        
        ericPic = QPixmap(os.path.join(getConfig('ericPixDir'), 'eric_small.png'))
        self.emptyLabel = QLabel()
        self.emptyLabel.setPixmap(ericPic)
        self.emptyLabel.setAlignment(Qt.AlignVCenter | Qt.AlignHCenter)
        E4TabWidget.addTab(self, self.emptyLabel, UI.PixmapCache.getIcon("empty.png"), "")
        
    def __initMenu(self):
        """
        Private method to initialize the tab context menu.
        """
        self.__menu = QMenu(self)
        self.leftMenuAct = \
            self.__menu.addAction(UI.PixmapCache.getIcon("1leftarrow.png"),
            self.trUtf8('Move Left'), self.__contextMenuMoveLeft)
        self.rightMenuAct = \
            self.__menu.addAction(UI.PixmapCache.getIcon("1rightarrow.png"),
            self.trUtf8('Move Right'), self.__contextMenuMoveRight)
        self.firstMenuAct = \
            self.__menu.addAction(UI.PixmapCache.getIcon("2leftarrow.png"),
            self.trUtf8('Move First'), self.__contextMenuMoveFirst)
        self.lastMenuAct = \
            self.__menu.addAction(UI.PixmapCache.getIcon("2rightarrow.png"),
            self.trUtf8('Move Last'), self.__contextMenuMoveLast)
        self.__menu.addSeparator()
        self.__menu.addAction(UI.PixmapCache.getIcon("close.png"),
            self.trUtf8('Close'), self.__contextMenuClose)
        self.closeOthersMenuAct = self.__menu.addAction(self.trUtf8("Close Others"), 
            self.__contextMenuCloseOthers)
        self.__menu.addAction(self.trUtf8('Close All'), self.__contextMenuCloseAll)
        self.__menu.addSeparator()
        self.saveMenuAct = \
            self.__menu.addAction(UI.PixmapCache.getIcon("fileSave.png"),
            self.trUtf8('Save'), self.__contextMenuSave)
        self.__menu.addAction(UI.PixmapCache.getIcon("fileSaveAs.png"),
            self.trUtf8('Save As...'), self.__contextMenuSaveAs)
        self.__menu.addAction(UI.PixmapCache.getIcon("fileSaveAll.png"),
            self.trUtf8('Save All'), self.__contextMenuSaveAll)
        self.projectMenuAct = \
            self.__menu.addAction(UI.PixmapCache.getIcon("fileSaveProject.png"),
                self.trUtf8('Save to Project'), self.__contextMenuSaveToProject)
        self.__menu.addSeparator()
        self.__menu.addAction(UI.PixmapCache.getIcon("print.png"),
            self.trUtf8('Print'), self.__contextMenuPrintFile)
        
    def __showContextMenu(self, coord, index):
        """
        Private slot to show the tab context menu.
        
        @param coord the position of the mouse pointer (QPoint)
        @param index index of the tab the menu is requested for (integer)
        """
        if self.editors:
            self.contextMenuEditor = self.widget(index)
            if self.contextMenuEditor:
                self.saveMenuAct.setEnabled(self.contextMenuEditor.isModified())
            self.projectMenuAct.setEnabled(e4App().getObject("Project").isOpen())
            
            self.contextMenuIndex = index
            self.leftMenuAct.setEnabled(index > 0)
            self.rightMenuAct.setEnabled(index < self.count() - 1)
            self.firstMenuAct.setEnabled(index > 0)
            self.lastMenuAct.setEnabled(index < self.count() - 1)
            
            self.closeOthersMenuAct.setEnabled(self.count() > 1)
            
            coord = self.mapToGlobal(coord)
            self.__menu.popup(coord)
        
    def __showNavigationMenu(self):
        """
        Private slot to show the navigation button menu.
        """
        self.__navigationMenu.clear()
        for index in range(self.count()):
            act = self.__navigationMenu.addAction(self.tabIcon(index), self.tabText(index))
            act.setData(QVariant(index))
        
    def __navigationMenuTriggered(self, act):
        """
        Private slot called to handle the navigation button menu selection.
        
        @param act reference to the selected action (QAction)
        """
        index, ok = act.data().toInt()
        if ok:
            self.setCurrentIndex(index)
        
    def showIndicator(self, on):
        """
        Public slot to set the indicator on or off.
        
        @param on flag indicating the dtate of the indicator (boolean)
        """
        if on:
            self.indicator.setColor(QColor("green"))
        else:
            self.indicator.setColor(QColor("red"))
        
    def addTab(self, editor, title):
        """
        Overwritten method to add a new tab.
        
        @param editor the editor object to be added (QScintilla.Editor.Editor)
        @param title title for the new tab (string or QString)
        """
        E4TabWidget.addTab(self, editor, UI.PixmapCache.getIcon("empty.png"), title)
        if self.closeButton:
            self.closeButton.setEnabled(True)
        else:
            self.setTabsClosable(True)
        self.navigationButton.setEnabled(True)
        
        if not editor in self.editors:
            self.editors.append(editor)
            self.connect(editor, SIGNAL('captionChanged'),
                self.__captionChange)
        
        emptyIndex = self.indexOf(self.emptyLabel)
        if emptyIndex > -1:
            self.removeTab(emptyIndex)
        
    def insertWidget(self, index, editor, title):
        """
        Overwritten method to insert a new tab.
        
        @param index index position for the new tab (integer)
        @param editor the editor object to be added (QScintilla.Editor.Editor)
        @param title title for the new tab (string or QString)
        @return index of the inserted tab (integer)
        """
        newIndex = E4TabWidget.insertTab(self, index, editor, 
                                         UI.PixmapCache.getIcon("empty.png"), 
                                         title)
        if self.closeButton:
            self.closeButton.setEnabled(True)
        else:
            self.setTabsClosable(True)
        self.navigationButton.setEnabled(True)
        
        if not editor in self.editors:
            self.editors.append(editor)
            self.connect(editor, SIGNAL('captionChanged'),
                self.__captionChange)
        
        emptyIndex = self.indexOf(self.emptyLabel)
        if emptyIndex > -1:
            self.removeTab(emptyIndex)
        
        return newIndex
        
    def __captionChange(self, cap, editor):
        """
        Private method to handle Caption change signals from the editor. 
        
        Updates the listview text to reflect the new caption information.
        
        @param cap Caption for the editor
        @param editor Editor to update the caption for
        """
        fn = editor.getFileName()
        if fn:
            if Preferences.getUI("TabViewManagerFilenameOnly"):
                txt = os.path.basename(fn)
            else:
                txt = fn
                ppath = e4App().getObject("Project").getProjectPath()
                if ppath:
                    txt = txt.replace(ppath + os.sep, "")
            
            maxFileNameChars = Preferences.getUI("TabViewManagerFilenameLength")
            if len(txt) > maxFileNameChars:
                txt = "...%s" % txt[-maxFileNameChars:]
            if editor.isReadOnly():
                txt = self.trUtf8("%1 (ro)").arg(txt)
            
            index = self.indexOf(editor)
            if index > -1:
                self.setTabText(index, txt)
                self.setTabToolTip(index, fn)
        
    def removeWidget(self, object):
        """
        Public method to remove a widget.
        
        @param object object to be removed (QWidget)
        """
        index = self.indexOf(object)
        if index > -1:
            self.removeTab(index)
        
        if isinstance(object, QScintilla.Editor.Editor):
            self.disconnect(object, SIGNAL('captionChanged'),
                self.__captionChange)
            self.editors.remove(object)
        
        if not self.editors:
            E4TabWidget.addTab(self, self.emptyLabel, 
                UI.PixmapCache.getIcon("empty.png"), "")
            self.emptyLabel.show()
            if self.closeButton:
                self.closeButton.setEnabled(False)
            else:
                self.setTabsClosable(False)
            self.navigationButton.setEnabled(False)
        
    def relocateTab(self, sourceId, sourceIndex, targetIndex):
        """
        Public method to relocate an editor from another TabWidget.
        
        @param sourceId id of the TabWidget to get the editor from (long)
        @param sourceIndex index of the tab in the old tab widget (integer)
        @param targetIndex index position to place it to (integer)
        """
        tw = self.vm.getTabWidgetById(sourceId)
        if tw is not None:
            # step 1: get data of the tab of the source
            toolTip = tw.tabToolTip(sourceIndex)
            text = tw.tabText(sourceIndex)
            icon = tw.tabIcon(sourceIndex)
            whatsThis = tw.tabWhatsThis(sourceIndex)
            editor = tw.widget(sourceIndex)
            
            # step 2: relocate the tab
            tw.removeWidget(editor)
            self.insertWidget(targetIndex, editor, text)
            
            # step 3: set the tab data again
            self.setTabIcon(targetIndex, icon)
            self.setTabToolTip(targetIndex, toolTip)
            self.setTabWhatsThis(targetIndex, whatsThis)
            
            # step 4: set current widget
            self.setCurrentIndex(targetIndex)
        
    def copyTabOther(self, sourceId, sourceIndex, targetIndex):
        """
        Public method to copy an editor from another TabWidget.
        
        @param sourceId id of the TabWidget to get the editor from (long)
        @param sourceIndex index of the tab in the old tab widget (integer)
        @param targetIndex index position to place it to (integer)
        """
        tw = self.vm.getTabWidgetById(sourceId)
        if tw is not None:
            editor = tw.widget(sourceIndex)
            newEditor = self.vm.cloneEditor(editor, editor.getFileType(), 
                                            editor.getFileName())
            self.vm.insertView(newEditor, self, targetIndex, 
                               editor.getFileName(), editor.getNoName())
        
    def copyTab(self, sourceIndex, targetIndex):
        """
        Public method to copy an editor.
        
        @param sourceIndex index of the tab (integer)
        @param targetIndex index position to place it to (integer)
        """
        editor = self.widget(sourceIndex)
        newEditor = self.vm.cloneEditor(editor, editor.getFileType(), 
                                        editor.getFileName())
        self.vm.insertView(newEditor, self, targetIndex, 
                           editor.getFileName(), editor.getNoName())
        
    def currentWidget(self):
        """
        Overridden method to return a reference to the current page.
        
        @return reference to the current page (QWidget)
        """
        if not self.editors:
            return None
        else:
            return E4TabWidget.currentWidget(self)
        
    def hasEditor(self, editor):
        """
        Public method to check for an editor.
        
        @param editor editor object to check for
        @return flag indicating, whether the editor to be checked belongs
            to the list of editors managed by this tab widget.
        """
        return editor in self.editors
        
    def hasEditors(self):
        """
        Public method to test, if any editor is managed.
        
        @return flag indicating editors are managed
        """
        return len(self.editors) > 0
        
    def __contextMenuClose(self):
        """
        Private method to close the selected tab.
        """
        if self.contextMenuEditor:
            self.vm.closeEditorWindow(self.contextMenuEditor)
        
    def __contextMenuCloseOthers(self):
        """
        Private method to close the other tabs.
        """
        index = self.contextMenuIndex
        for i in range(self.count() - 1, index, -1) + range(index - 1, -1, -1):
            editor = self.widget(i)
            self.vm.closeEditorWindow(editor)
        
    def __contextMenuCloseAll(self):
        """
        Private method to close all tabs.
        """
        savedEditors = self.editors[:]
        for editor in savedEditors:
            self.vm.closeEditorWindow(editor)
        
    def __contextMenuSave(self):
        """
        Private method to save the selected tab.
        """
        if self.contextMenuEditor:
            self.vm.saveEditorEd(self.contextMenuEditor)
        
    def __contextMenuSaveAs(self):
        """
        Private method to save the selected tab to a new file.
        """
        if self.contextMenuEditor:
            self.vm.saveAsEditorEd(self.contextMenuEditor)
        
    def __contextMenuSaveAll(self):
        """
        Private method to save all tabs.
        """
        self.vm.saveEditorsList(self.editors)
        
    def __contextMenuSaveToProject(self):
        """
        Private method to save the selected tab to the current project.
        """
        if self.contextMenuEditor:
            self.vm.saveEditorToProjectEd(self.contextMenuEditor)
        
    def __contextMenuPrintFile(self):
        """
        Private method to print the selected tab.
        """
        if self.contextMenuEditor:
            self.vm.printEditor(self.contextMenuEditor)
        
    def __contextMenuMoveLeft(self):
        """
        Private method to move a tab one position to the left.
        """
        self.moveTab(self.contextMenuIndex, self.contextMenuIndex - 1)
        
    def __contextMenuMoveRight(self):
        """
        Private method to move a tab one position to the right.
        """
        self.moveTab(self.contextMenuIndex, self.contextMenuIndex + 1)
        
    def __contextMenuMoveFirst(self):
        """
        Private method to move a tab to the first position.
        """
        self.moveTab(self.contextMenuIndex, 0)
        
    def __contextMenuMoveLast(self):
        """
        Private method to move a tab to the last position.
        """
        self.moveTab(self.contextMenuIndex, self.count() - 1)
        
    def __closeButtonClicked(self):
        """
        Private method to handle the press of the close button.
        """
        self.vm.closeEditorWindow(self.currentWidget())
        
    def __closeRequested(self, index):
        """
        Private method to handle the press of the individual tab close button.
        
        @param index index of the tab (integer)
        """
        if index >= 0:
            self.vm.closeEditorWindow(self.widget(index))
        
    def mouseDoubleClickEvent(self, event):
        """
        Protected method handling double click events.
        
        @param event reference to the event object (QMouseEvent)
        """
        self.vm.newEditor()

class Tabview(QSplitter, ViewManager):
    """
    Class implementing a tabbed viewmanager class embedded in a splitter.
    
    @signal changeCaption(string) emitted if a change of the caption is necessary
    @signal editorChanged(string) emitted when the current editor has changed
    """
    def __init__(self, parent):
        """
        Constructor
        
        @param parent parent widget (QWidget)
        @param ui reference to the main user interface
        @param dbs reference to the debug server object
        """
        self.tabWidgets = []
        
        QSplitter.__init__(self, parent)
        ViewManager.__init__(self)
        tw = TabWidget(self)
        self.addWidget(tw)
        self.tabWidgets.append(tw)
        self.currentTabWidget = tw
        self.currentTabWidget.showIndicator(True)
        self.connect(tw, SIGNAL('currentChanged(int)'),
            self.__currentChanged)
        tw.installEventFilter(self)
        tw.tabBar().installEventFilter(self)
        self.setOrientation(Qt.Vertical)
        self.__inRemoveView = False
        
        self.maxFileNameChars = Preferences.getUI("TabViewManagerFilenameLength")
        self.filenameOnly = Preferences.getUI("TabViewManagerFilenameOnly")
        
    def canCascade(self):
        """
        Public method to signal if cascading of managed windows is available.
        
        @return flag indicating cascading of windows is available
        """
        return False
        
    def canTile(self):
        """
        Public method to signal if tiling of managed windows is available.
        
        @return flag indicating tiling of windows is available
        """
        return False
        
    def canSplit(self):
        """
        public method to signal if splitting of the view is available.
        
        @return flag indicating splitting of the view is available.
        """
        return True
        
    def tile(self):
        """
        Public method to tile the managed windows.
        """
        pass
        
    def cascade(self):
        """
        Public method to cascade the managed windows.
        """
        pass
        
    def _removeAllViews(self):
        """
        Protected method to remove all views (i.e. windows)
        """
        for win in self.editors:
            self._removeView(win)
        
    def _removeView(self, win):
        """
        Protected method to remove a view (i.e. window)
        
        @param win editor window to be removed
        """
        self.__inRemoveView = True
        for tw in self.tabWidgets:
            if tw.hasEditor(win):
                tw.removeWidget(win)
                break
        win.closeIt()
        self.__inRemoveView = False
        
        # if this was the last editor in this view, switch to the next, that
        # still has open editors
        for i in range(self.tabWidgets.index(tw), -1, -1) + \
                 range(self.tabWidgets.index(tw) + 1, len(self.tabWidgets)):
            if self.tabWidgets[i].hasEditors():
                self.currentTabWidget.showIndicator(False)
                self.currentTabWidget = self.tabWidgets[i]
                self.currentTabWidget.showIndicator(True)
                self.activeWindow().setFocus()
                break
        
        aw = self.activeWindow()
        fn = aw and aw.getFileName() or None
        if fn:
            self.emit(SIGNAL('changeCaption'), unicode(fn))
            self.emit(SIGNAL('editorChanged'), unicode(fn))
        else:
            self.emit(SIGNAL('changeCaption'), "")
        
    def _addView(self, win, fn = None, noName = ""):
        """
        Protected method to add a view (i.e. window)
        
        @param win editor window to be added
        @param fn filename of this editor
        @param noName name to be used for an unnamed editor (string or QString)
        """
        if fn is None:
            if not unicode(noName):
                self.untitledCount += 1
                noName = self.trUtf8("Untitled %1").arg(self.untitledCount)
            self.currentTabWidget.addTab(win, noName)
            win.setNoName(noName)
        else:
            if self.filenameOnly:
                txt = os.path.basename(fn)
            else:
                txt = fn
                ppath = e4App().getObject("Project").getProjectPath()
                if ppath:
                    txt = txt.replace(ppath + os.sep, "")
            if len(txt) > self.maxFileNameChars:
                txt = "...%s" % txt[-self.maxFileNameChars:]
            if not QFileInfo(fn).isWritable():
                txt = self.trUtf8("%1 (ro)").arg(txt)
            self.currentTabWidget.addTab(win, txt)
            index = self.currentTabWidget.indexOf(win)
            self.currentTabWidget.setTabToolTip(index, fn)
        self.currentTabWidget.setCurrentWidget(win)
        win.show()
        win.setFocus()
        if fn:
            self.emit(SIGNAL('changeCaption'), unicode(fn))
            self.emit(SIGNAL('editorChanged'), unicode(fn))
        else:
            self.emit(SIGNAL('changeCaption'), "")
        
    def insertView(self, win, tabWidget, index, fn = None, noName = ""):
        """
        Protected method to add a view (i.e. window)
        
        @param win editor window to be added
        @param tabWidget reference to the tab widget to insert the editor into (TabWidget)
        @param index index position to insert at (integer)
        @param fn filename of this editor
        @param noName name to be used for an unnamed editor (string or QString)
        """
        if fn is None:
            if not unicode(noName):
                self.untitledCount += 1
                noName = self.trUtf8("Untitled %1").arg(self.untitledCount)
            tabWidget.insertWidget(index, win, noName)
            win.setNoName(noName)
        else:
            if self.filenameOnly:
                txt = os.path.basename(fn)
            else:
                txt = fn
                ppath = e4App().getObject("Project").getProjectPath()
                if ppath:
                    txt = txt.replace(ppath + os.sep, "")
            if len(txt) > self.maxFileNameChars:
                txt = "...%s" % txt[-self.maxFileNameChars:]
            if not QFileInfo(fn).isWritable():
                txt = self.trUtf8("%1 (ro)").arg(txt)
            nindex = tabWidget.insertWidget(index, win, txt)
            tabWidget.setTabToolTip(nindex, fn)
        tabWidget.setCurrentWidget(win)
        win.show()
        win.setFocus()
        if fn:
            self.emit(SIGNAL('changeCaption'), unicode(fn))
            self.emit(SIGNAL('editorChanged'), unicode(fn))
        else:
            self.emit(SIGNAL('changeCaption'), "")
        
        self._modificationStatusChanged(win.isModified(), win)
        self._checkActions(win)
        
    def _showView(self, win, fn = None):
        """
        Protected method to show a view (i.e. window)
        
        @param win editor window to be shown
        @param fn filename of this editor
        """
        win.show()
        for tw in self.tabWidgets:
            if tw.hasEditor(win):
                tw.setCurrentWidget(win)
                self.currentTabWidget.showIndicator(False)
                self.currentTabWidget = tw
                self.currentTabWidget.showIndicator(True)
                break
        win.setFocus()
        
    def activeWindow(self):
        """
        Public method to return the active (i.e. current) window.
        
        @return reference to the active editor
        """
        return self.currentTabWidget.currentWidget()
        
    def showWindowMenu(self, windowMenu):
        """
        Public method to set up the viewmanager part of the Window menu.
        
        @param windowMenu reference to the window menu
        """
        pass
        
    def _initWindowActions(self):
        """
        Protected method to define the user interface actions for window handling.
        """
        pass
        
    def setEditorName(self, editor, newName):
        """
        Public method to change the displayed name of the editor.
        
        @param editor editor window to be changed
        @param newName new name to be shown (string or QString)
        """
        if self.filenameOnly:
            tabName = os.path.basename(unicode(newName))
        else:
            tabName = unicode(newName)
            ppath = e4App().getObject("Project").getProjectPath()
            if ppath:
                tabName = tabName.replace(ppath + os.sep, "")
        if len(tabName) > self.maxFileNameChars:
            tabName = "...%s" % tabName[-self.maxFileNameChars:]
        index = self.currentTabWidget.indexOf(editor)
        self.currentTabWidget.setTabText(index, tabName)
        self.currentTabWidget.setTabToolTip(index, newName)
        self.emit(SIGNAL('changeCaption'), unicode(newName))

    def _modificationStatusChanged(self, m, editor):
        """
        Protected slot to handle the modificationStatusChanged signal.
        
        @param m flag indicating the modification status (boolean)
        @param editor editor window changed
        """
        for tw in self.tabWidgets:
            if tw.hasEditor(editor):
                break
        index = tw.indexOf(editor)
        if m:
            tw.setTabIcon(index, UI.PixmapCache.getIcon("fileModified.png"))
        elif editor.hasSyntaxErrors():
            tw.setTabIcon(index, UI.PixmapCache.getIcon("syntaxError.png"))
        else:
            tw.setTabIcon(index, UI.PixmapCache.getIcon("empty.png"))
        self._checkActions(editor)
        
    def _syntaxErrorToggled(self, editor):
        """
        Protected slot to handle the syntaxerrorToggled signal.
        
        @param editor editor that sent the signal
        """
        for tw in self.tabWidgets:
            if tw.hasEditor(editor):
                break
        index = tw.indexOf(editor)
        if editor.hasSyntaxErrors():
            tw.setTabIcon(index, UI.PixmapCache.getIcon("syntaxError.png"))
        else:
            tw.setTabIcon(index, UI.PixmapCache.getIcon("empty.png"))
        
        ViewManager._syntaxErrorToggled(self, editor)
        
    def addSplit(self):
        """
        Public method used to split the current view.
        """
        tw = TabWidget(self)
        tw.show()
        self.addWidget(tw)
        self.tabWidgets.append(tw)
        self.currentTabWidget.showIndicator(False)
        self.currentTabWidget = self.tabWidgets[-1]
        self.currentTabWidget.showIndicator(True)
        self.connect(tw, SIGNAL('currentChanged(int)'),
            self.__currentChanged)
        tw.installEventFilter(self)
        tw.tabBar().installEventFilter(self)
        if self.orientation() == Qt.Horizontal:
            size = self.width()
        else:
            size = self.height()
        self.setSizes([int(size/len(self.tabWidgets))] * len(self.tabWidgets))
        self.splitRemoveAct.setEnabled(True)
        self.nextSplitAct.setEnabled(True)
        self.prevSplitAct.setEnabled(True)
        
    def removeSplit(self):
        """
        Public method used to remove the current split view.
        
        @return flag indicating successfull removal
        """
        if len(self.tabWidgets) > 1:
            tw = self.currentTabWidget
            res = True
            savedEditors = tw.editors[:]
            for editor in savedEditors:
                res &= self.closeEditor(editor)
            if res:
                try:
                    i = self.tabWidgets.index(tw)
                except ValueError:
                    return True
                if i == len(self.tabWidgets) - 1:
                    i -= 1
                self.tabWidgets.remove(tw)
                tw.close()
                self.currentTabWidget = self.tabWidgets[i]
                self.currentTabWidget.showIndicator(True)
                if len(self.tabWidgets) == 1:
                    self.splitRemoveAct.setEnabled(False)
                    self.nextSplitAct.setEnabled(False)
                    self.prevSplitAct.setEnabled(False)
                return True
        
        return False
        
    def setSplitOrientation(self, orientation):
        """
        Public method used to set the orientation of the split view.
        
        @param orientation orientation of the split
                (Qt.Horizontal or Qt.Vertical)
        """
        self.setOrientation(orientation)
        
    def nextSplit(self):
        """
        Public slot used to move to the next split.
        """
        aw = self.activeWindow()
        _hasFocus = aw and aw.hasFocus()
        ind = self.tabWidgets.index(self.currentTabWidget) + 1
        if ind == len(self.tabWidgets):
            ind = 0
        
        self.currentTabWidget.showIndicator(False)
        self.currentTabWidget = self.tabWidgets[ind]
        self.currentTabWidget.showIndicator(True)
        if _hasFocus:
            aw = self.activeWindow()
            if aw:
                aw.setFocus()
        
    def prevSplit(self):
        """
        Public slot used to move to the previous split.
        """
        aw = self.activeWindow()
        _hasFocus = aw and aw.hasFocus()
        ind = self.tabWidgets.index(self.currentTabWidget) - 1
        if ind == -1:
            ind = len(self.tabWidgets) - 1
        
        self.currentTabWidget.showIndicator(False)
        self.currentTabWidget = self.tabWidgets[ind]
        self.currentTabWidget.showIndicator(True)
        if _hasFocus:
            aw = self.activeWindow()
            if aw:
                aw.setFocus()
        
    def __currentChanged(self, index):
        """
        Private slot to handle the currentChanged signal.
        
        @param index index of the current tab
        """
        if index == -1 or not self.editors:
            return
        
        editor = self.activeWindow()
        if editor is None:
            return
        
        self._checkActions(editor)
        editor.setFocus()
        fn = editor.getFileName()
        if fn:
            self.emit(SIGNAL('changeCaption'), unicode(fn))
            if not self.__inRemoveView:
                self.emit(SIGNAL('editorChanged'), unicode(fn))
        else:
            self.emit(SIGNAL('changeCaption'), "")
        
    def eventFilter(self, watched, event):
        """
        Public method called to filter the event queue.
        
        @param watched the QObject being watched
        @param event the event that occurred
        @return always False
        """
        if event.type() == QEvent.MouseButtonPress and \
           not event.button() == Qt.RightButton:
            self.currentTabWidget.showIndicator(False)
            if isinstance(watched, E4TabWidget):
                switched = watched is not self.currentTabWidget
                self.currentTabWidget = watched
            elif isinstance(watched, QTabBar):
                switched = watched.parent() is not self.currentTabWidget
                self.currentTabWidget = watched.parent()
                if switched:
                    index = self.currentTabWidget.selectTab(event.pos())
                    switched = self.currentTabWidget.widget(index) is self.activeWindow()
            elif isinstance(watched, QScintilla.Editor.Editor):
                for tw in self.tabWidgets:
                    if tw.hasEditor(watched):
                        switched = tw is not self.currentTabWidget
                        self.currentTabWidget = tw
                        break
            self.currentTabWidget.showIndicator(True)
            
            aw = self.activeWindow()
            if aw is not None:
                self._checkActions(aw)
                aw.setFocus()
                fn = aw.getFileName()
                if fn:
                    self.emit(SIGNAL('changeCaption'), unicode(fn))
                    if switched:
                        self.emit(SIGNAL('editorChanged'), unicode(fn))
                else:
                    self.emit(SIGNAL('changeCaption'), "")
        
        return False
        
    def preferencesChanged(self):
        """
        Public slot to handle the preferencesChanged signal.
        """
        ViewManager.preferencesChanged(self)
        
        self.maxFileNameChars = Preferences.getUI("TabViewManagerFilenameLength")
        self.filenameOnly = Preferences.getUI("TabViewManagerFilenameOnly")
        
        for tabWidget in self.tabWidgets:
            for index in range(tabWidget.count()):
                editor = tabWidget.widget(index)
                if isinstance(editor, QScintilla.Editor.Editor):
                    fn = editor.getFileName()
                    if fn:
                        if self.filenameOnly:
                            txt = os.path.basename(fn)
                        else:
                            txt = fn
                            ppath = e4App().getObject("Project").getProjectPath()
                            if ppath:
                                txt = txt.replace(ppath + os.sep, "")
                        if len(txt) > self.maxFileNameChars:
                            txt = "...%s" % txt[-self.maxFileNameChars:]
                        if not QFileInfo(fn).isWritable():
                            txt = self.trUtf8("%1 (ro)").arg(txt)
                        tabWidget.setTabText(index, txt)
        
    def getTabWidgetById(self, id_):
        """
        Public method to get a reference to a tab widget knowing it's ID.
        
        @param id_ id of the tab widget (long)
        @return reference to the tab widget (TabWidget)
        """
        for tw in self.tabWidgets:
            if id(tw) == id_:
                return tw
        return None
