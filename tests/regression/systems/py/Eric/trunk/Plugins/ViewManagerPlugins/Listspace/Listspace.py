# -*- coding: utf-8 -*-

# Copyright (c) 2002 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the listspace viewmanager class.
"""

import os

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from KdeQt.KQApplication import e4App

from ViewManager.ViewManager import ViewManager

import QScintilla.Editor

import UI.PixmapCache

class StackedWidget(QStackedWidget):
    """
    Class implementing a custimized StackedWidget.
    """
    def __init__(self, parent):
        """
        Constructor
        
        @param parent parent widget (QWidget)
        """
        QStackedWidget.__init__(self, parent)
        self.setAttribute(Qt.WA_DeleteOnClose, True)
        
        self.editors = []
        
    def addWidget(self, editor):
        """
        Overwritten method to add a new widget.
        
        @param editor the editor object to be added (QScintilla.Editor.Editor)
        """
        QStackedWidget.addWidget(self, editor)
        if not editor in self.editors:
            self.editors.append(editor)
        
    def removeWidget(self, widget):
        """
        Overwritten method to remove a widget.
        
        @param widget widget to be removed (QWidget)
        """
        QStackedWidget.removeWidget(self, widget)
        if isinstance(widget, QScintilla.Editor.Editor):
            self.editors.remove(widget)
        
    def setCurrentWidget(self, widget):
        """
        Overwritten method to set the current widget.
        
        @param widget widget to be made current (QWidget)
        """
        if isinstance(widget, QScintilla.Editor.Editor):
            self.editors.remove(widget)
            self.editors.insert(0, widget)
        QStackedWidget.setCurrentWidget(self, widget)
        
    def setCurrentIndex(self, index):
        """
        Overwritten method to set the current widget by it's index.
        
        @param index index of widget to be made current (integer)
        """
        widget = self.widget(index)
        if widget is not None:
            self.setCurrentWidget(widget)
        
    def nextTab(self):
        """
        Public slot used to show the next tab.
        """
        ind = self.currentIndex() + 1
        if ind == self.count():
            ind = 0
            
        self.setCurrentIndex(ind)
        self.currentWidget().setFocus()

    def prevTab(self):
        """
        Public slot used to show the previous tab.
        """
        ind = self.currentIndex() - 1
        if ind == -1:
            ind = self.count() - 1
            
        self.setCurrentIndex(ind)
        self.currentWidget().setFocus()

    def hasEditor(self, editor):
        """
        Public method to check for an editor.
        
        @param editor editor object to check for
        @return flag indicating, whether the editor to be checked belongs
            to the list of editors managed by this stacked widget.
        """
        return editor in self.editors
        
    def firstEditor(self):
        """
        Public method to retrieve the first editor in the list of managed editors.
        
        @return first editor in list (QScintilla.Editor.Editor)
        """
        return len(self.editors) and self.editors[0] or None

class Listspace(QSplitter, ViewManager):
    """
    Class implementing the listspace viewmanager class.
    
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
        self.stacks = []
        
        QSplitter.__init__(self, parent)
        ViewManager.__init__(self)
        
        self.viewlist = QListWidget(self)
        policy = self.viewlist.sizePolicy()
        policy.setHorizontalPolicy(QSizePolicy.Ignored)
        self.viewlist.setSizePolicy(policy)
        self.addWidget(self.viewlist)
        self.viewlist.setContextMenuPolicy(Qt.CustomContextMenu)
        self.connect(self.viewlist, SIGNAL("itemActivated(QListWidgetItem*)"),
                     self.__showSelectedView)
        self.connect(self.viewlist, SIGNAL("itemClicked(QListWidgetItem*)"),
                     self.__showSelectedView)
        self.connect(self.viewlist, SIGNAL("customContextMenuRequested(const QPoint &)"),
                     self.__showMenu)
        
        self.stackArea = QSplitter(self)
        self.addWidget(self.stackArea)
        self.stackArea.setOrientation(Qt.Vertical)
        stack = StackedWidget(self.stackArea)
        self.stackArea.addWidget(stack)
        self.stacks.append(stack)
        self.currentStack = stack
        self.connect(stack, SIGNAL('currentChanged(int)'),
            self.__currentChanged)
        stack.installEventFilter(self)
        self.setSizes([int(self.width() * 0.2), int(self.width() * 0.8)]) # 20% for viewlist
        self.__inRemoveView = False
        
        self.__initMenu()
        self.contextMenuEditor = None
        
    def __initMenu(self):
        """
        Private method to initialize the viewlist context menu.
        """
        self.__menu = QMenu(self)
        self.__menu.addAction(UI.PixmapCache.getIcon("close.png"),
            self.trUtf8('Close'), self.__contextMenuClose)
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
        
    def __showMenu(self, point):
        """
        Private slot to handle the customContextMenuRequested signal of the viewlist.
        """
        if self.editors:
            itm = self.viewlist.itemAt(point)
            if itm is not None:
                row = self.viewlist.row(itm)
                self.contextMenuEditor = self.editors[row]
                if self.contextMenuEditor:
                    self.saveMenuAct.setEnabled(self.contextMenuEditor.isModified())
                    self.projectMenuAct.setEnabled(e4App().getObject("Project").isOpen())
                    self.__menu.popup(self.viewlist.mapToGlobal(point))
        
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
        self.viewlist.clear()
        for win in self.editors:
            for stack in self.stacks:
                if stack.hasEditor(win):
                    stack.removeWidget(win)
                    break
            win.closeIt()
        
    def _removeView(self, win):
        """
        Protected method to remove a view (i.e. window)
        
        @param win editor window to be removed
        """
        self.__inRemoveView = True
        ind = self.editors.index(win)
        itm = self.viewlist.takeItem(ind)
        if itm:
            del itm
        for stack in self.stacks:
            if stack.hasEditor(win):
                stack.removeWidget(win)
                break
        win.closeIt()
        self.__inRemoveView = False
        if ind > 0:
            ind -= 1
        else:
            if len(self.editors) > 1:
                ind = 1
            else:
                return
        stack.setCurrentWidget(stack.firstEditor())
        self._showView(self.editors[ind])
        
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
            self.viewlist.addItem(noName)
            win.setNoName(noName)
        else:
            txt = os.path.basename(fn)
            if not QFileInfo(fn).isWritable():
                txt = self.trUtf8("%1 (ro)").arg(txt)
            itm = QListWidgetItem(txt)
            itm.setToolTip(fn)
            self.viewlist.addItem(itm)
        self.currentStack.addWidget(win)
        self.currentStack.setCurrentWidget(win)
        self.connect(win, SIGNAL('captionChanged'),
            self.__captionChange)
        
        index = self.editors.index(win)
        self.viewlist.setCurrentRow(index)
        win.setFocus()
        if fn:
            self.emit(SIGNAL('changeCaption'), unicode(fn))
            self.emit(SIGNAL('editorChanged'), unicode(fn))
        else:
            self.emit(SIGNAL('changeCaption'), "")
        
    def __captionChange(self, cap, editor):
        """
        Private method to handle caption change signals from the editor. 
        
        Updates the listwidget text to reflect the new caption information.
        
        @param cap Caption for the editor
        @param editor Editor to update the caption for
        """
        fn = editor.getFileName()
        if fn:
            self.setEditorName(editor, fn)
        
    def _showView(self, win, fn = None):
        """
        Protected method to show a view (i.e. window)
        
        @param win editor window to be shown
        @param fn filename of this editor
        """
        for stack in self.stacks:
            if stack.hasEditor(win):
                stack.setCurrentWidget(win)
                self.currentStack = stack
                break
        index = self.editors.index(win)
        self.viewlist.setCurrentRow(index)
        win.setFocus()
        fn = win.getFileName()
        if fn:
            self.emit(SIGNAL('changeCaption'), unicode(fn))
            self.emit(SIGNAL('editorChanged'), unicode(fn))
        else:
            self.emit(SIGNAL('changeCaption'), "")
        
    def __showSelectedView(self, itm):
        """
        Private slot called to show a view selected in the list by a mouse click.
        
        @param itm item clicked on (QListWidgetItem)
        """
        if itm:
            row = self.viewlist.row(itm)
            self._showView(self.editors[row])
            self._checkActions(self.editors[row])
        
    def activeWindow(self):
        """
        Public method to return the active (i.e. current) window.
        
        @return reference to the active editor
        """
        return self.currentStack.currentWidget()
        
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
        Change the displayed name of the editor.
        
        @param editor editor window to be changed
        @param newName new name to be shown (string or QString)
        """
        currentRow = self.viewlist.currentRow()
        index = self.editors.index(editor)
        txt = os.path.basename(unicode(newName))
        if not QFileInfo(newName).isWritable():
            txt = self.trUtf8("%1 (ro)").arg(txt)
        itm = self.viewlist.item(index)
        itm.setText(txt)
        itm.setToolTip(newName)
        self.viewlist.setCurrentRow(currentRow)
        self.emit(SIGNAL('changeCaption'), unicode(newName))
        
    def _modificationStatusChanged(self, m, editor):
        """
        Protected slot to handle the modificationStatusChanged signal.
        
        @param m flag indicating the modification status (boolean)
        @param editor editor window changed
        """
        currentRow = self.viewlist.currentRow()
        index = self.editors.index(editor)
        if m:
            self.viewlist.item(index).setIcon(UI.PixmapCache.getIcon("fileModified.png"))
        elif editor.hasSyntaxErrors():
            self.viewlist.item(index).setIcon(UI.PixmapCache.getIcon("syntaxError.png"))
        else:
            self.viewlist.item(index).setIcon(UI.PixmapCache.getIcon("empty.png"))
        self.viewlist.setCurrentRow(currentRow)
        self._checkActions(editor)
        
    def _syntaxErrorToggled(self, editor):
        """
        Protected slot to handle the syntaxerrorToggled signal.
        
        @param editor editor that sent the signal
        """
        currentRow = self.viewlist.currentRow()
        index = self.editors.index(editor)
        if editor.hasSyntaxErrors():
            self.viewlist.item(index).setIcon(UI.PixmapCache.getIcon("syntaxError.png"))
        else:
            self.viewlist.item(index).setIcon(UI.PixmapCache.getIcon("empty.png"))
        self.viewlist.setCurrentRow(currentRow)
        
        ViewManager._syntaxErrorToggled(self, editor)
        
    def addSplit(self):
        """
        Public method used to split the current view.
        """
        stack = StackedWidget(self.stackArea)
        stack.show()
        self.stackArea.addWidget(stack)
        self.stacks.append(stack)
        self.currentStack = stack
        self.connect(stack, SIGNAL('currentChanged(int)'),
            self.__currentChanged)
        stack.installEventFilter(self)
        if self.stackArea.orientation() == Qt.Horizontal:
            size = self.stackArea.width()
        else:
            size = self.stackArea.height()
        self.stackArea.setSizes([int(size/len(self.stacks))] * len(self.stacks))
        self.splitRemoveAct.setEnabled(True)
        self.nextSplitAct.setEnabled(True)
        self.prevSplitAct.setEnabled(True)
        
    def removeSplit(self):
        """
        Public method used to remove the current split view.
        
        @return flag indicating successfull removal
        """
        if len(self.stacks) > 1:
            stack = self.currentStack
            res = True
            savedEditors = stack.editors[:]
            for editor in savedEditors:
                res &= self.closeEditor(editor)
            if res:
                try:
                    i = self.stacks.index(stack)
                except ValueError:
                    return True
                if i == len(self.stacks) - 1:
                    i -= 1
                self.stacks.remove(stack)
                stack.close()
                self.currentStack = self.stacks[i]
                if len(self.stacks) == 1:
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
        self.stackArea.setOrientation(orientation)
        
    def nextSplit(self):
        """
        Public slot used to move to the next split.
        """
        aw = self.activeWindow()
        _hasFocus = aw and aw.hasFocus()
        ind = self.stacks.index(self.currentStack) + 1
        if ind == len(self.stacks):
            ind = 0
        
        self.currentStack = self.stacks[ind]
        if _hasFocus:
            aw = self.activeWindow()
            if aw:
                aw.setFocus()
        
        index = self.editors.index(self.currentStack.currentWidget())
        self.viewlist.setCurrentRow(index)
        
    def prevSplit(self):
        """
        Public slot used to move to the previous split.
        """
        aw = self.activeWindow()
        _hasFocus = aw and aw.hasFocus()
        ind = self.stacks.index(self.currentStack) - 1
        if ind == -1:
            ind = len(self.stacks) - 1
        
        self.currentStack = self.stacks[ind]
        if _hasFocus:
            aw = self.activeWindow()
            if aw:
                aw.setFocus()
        index = self.editors.index(self.currentStack.currentWidget())
        self.viewlist.setCurrentRow(index)
        
    def __contextMenuClose(self):
        """
        Private method to close the selected tab.
        """
        if self.contextMenuEditor:
            self.closeEditorWindow(self.contextMenuEditor)
        
    def __contextMenuCloseAll(self):
        """
        Private method to close all tabs.
        """
        savedEditors = self.editors[:]
        for editor in savedEditors:
            self.closeEditorWindow(editor)
        
    def __contextMenuSave(self):
        """
        Private method to save the selected tab.
        """
        if self.contextMenuEditor:
            self.saveEditorEd(self.contextMenuEditor)
        
    def __contextMenuSaveAs(self):
        """
        Private method to save the selected tab to a new file.
        """
        if self.contextMenuEditor:
            self.saveAsEditorEd(self.contextMenuEditor)
        
    def __contextMenuSaveAll(self):
        """
        Private method to save all tabs.
        """
        self.saveEditorsList(self.editors)
        
    def __contextMenuSaveToProject(self):
        """
        Private method to save the selected tab to the current project.
        """
        if self.contextMenuEditor:
            self.saveEditorToProjectEd(self.contextMenuEditor)
        
    def __contextMenuPrintFile(self):
        """
        Private method to print the selected tab.
        """
        if self.contextMenuEditor:
            self.printEditor(self.contextMenuEditor)
        
    def __currentChanged(self, index):
        """
        Private slot to handle the currentChanged signal.
        
        @param index index of the current editor
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
        
        cindex = self.editors.index(editor)
        self.viewlist.setCurrentRow(cindex)
        
    def eventFilter(self, watched, event):
        """
        Method called to filter the event queue.
        
        @param watched the QObject being watched
        @param event the event that occurred
        @return flag indicating, if we handled the event
        """
        if event.type() == QEvent.MouseButtonPress and \
           not event.button() == Qt.RightButton:
            if isinstance(watched, QStackedWidget):
                switched = watched is not self.currentStack
                self.currentStack = watched
            elif isinstance(watched, QScintilla.Editor.Editor):
                for stack in self.stacks:
                    if stack.hasEditor(watched):
                        switched = stack is not self.currentStack
                        self.currentStack = stack
                        break
            currentWidget = self.currentStack.currentWidget()
            if currentWidget:
                index = self.editors.index(currentWidget)
                self.viewlist.setCurrentRow(index)
            
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