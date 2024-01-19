# -*- coding: utf-8 -*-

# Copyright (c) 2002 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the workspace viewmanager class.
"""

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from ViewManager.ViewManager import ViewManager

import QScintilla.Editor

import UI.PixmapCache

from E4Gui.E4Action import E4Action, addActions

import Utilities

class Workspace(QWorkspace, ViewManager):
    """
    Class implementing the workspace viewmanager class.
    
    @signal editorChanged(string) emitted when the current editor has changed
    """
    def __init__(self, parent):
        """
        Constructor
        
        @param parent parent widget (QWidget)
        @param ui reference to the main user interface
        @param dbs reference to the debug server object
        """
        QWorkspace.__init__(self, parent)
        ViewManager.__init__(self)
        self.setScrollBarsEnabled(True)
        self.lastFN = ''
        
        self.__windowMapper = QSignalMapper(self)
        
        self.connect(self.__windowMapper, SIGNAL('mapped(QWidget*)'), 
            self.setActiveWindow)
        self.connect(self, SIGNAL('windowActivated(QWidget*)'),
            self.__windowActivated)
        
    def canCascade(self):
        """
        Public method to signal if cascading of managed windows is available.
        
        @return flag indicating cascading of windows is available
        """
        return True
        
    def canTile(self):
        """
        Public method to signal if tiling of managed windows is available.
        
        @return flag indicating tiling of windows is available
        """
        return True
    
    def canSplit(self):
        """
        public method to signal if splitting of the view is available.
        
        @return flag indicating splitting of the view is available.
        """
        return False
        
    def tile(self):
        """
        Public method to tile the managed windows.
        """
        QWorkspace.tile(self)
        
    def cascade(self):
        """
        Public method to cascade the managed windows.
        """
        QWorkspace.cascade(self)
        
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
        self.lastFN = ''
        win.removeEventFilter(self)
        win.closeIt()
        
    def _addView(self, win, fn = None, noName = ""):
        """
        Protected method to add a view (i.e. window)
        
        @param win editor window to be added
        @param fn filename of this editor
        @param noName name to be used for an unnamed editor (string or QString)
        """
        self.addWindow(win)
        if fn is None:
            if not unicode(noName):
                self.untitledCount += 1
                noName = self.trUtf8("Untitled %1").arg(self.untitledCount)
            win.setWindowTitle(noName)
            win.setNoName(noName)
        else:
            if self.lastFN != fn:
                self.lastFN = fn
                # QWorkspace is a little bit tricky
                win.hide()
        win.show()
        
        # Make the editor window a little bit smaller to make the whole
        # window with all decorations visible. This is not the most elegant
        # solution but more of a workaround for another QWorkspace strangeness.
        # 25 points are subtracted to give space for the scrollbars
        pw = win.parentWidget()
        sz = QSize(self.width() - 25, self.height() - 25)
        pw.resize(sz)
        
        win.setFocus()
        win.installEventFilter(self)
        
    def _showView(self, win, fn = None):
        """
        Private method to show a view (i.e. window)
        
        @param win editor window to be shown
        @param fn filename of this editor
        """
        if fn is not None and self.lastFN != fn:
            self.lastFN = fn
            # QWorkspace is a little bit tricky
            win.hide()
        win.show()
        win.setFocus()
        
    def activeWindow(self):
        """
        Private method to return the active (i.e. current) window.
        
        @return reference to the active editor
        """
        return QWorkspace.activeWindow(self)
        
    def showWindowMenu(self, windowMenu):
        """
        Public method to set up the viewmanager part of the Window menu.
        
        @param windowMenu reference to the window menu
        """
        self.windowsMenu = QMenu(self.trUtf8('&Windows'))
        
        menu = self.windowsMenu
        idx = 1
        for sv in self.editors:
            if idx == 10:
                menu.addSeparator()
                menu = menu.addMenu(self.trUtf8("&More"))
            fn = sv.fileName
            if fn:
                txt = Utilities.compactPath(unicode(fn), self.ui.maxMenuFilePathLen)
            else:
                txt = sv.windowTitle()
            accel = ""
            if idx < 10:
                accel = "&%d. " % idx
            elif idx < 36:
                accel = "&%c. " % chr(idx - 9 + ord("@"))
            act = menu.addAction("%s%s" % (accel, txt))
            self.connect(act, SIGNAL("triggered()"), 
                         self.__windowMapper, SLOT("map()"))
            self.__windowMapper.setMapping(act, sv)
            idx += 1
        
        addActions(windowMenu, 
                   [None, self.nextChildAct, self.prevChildAct, 
                    self.tileAct, self.cascadeAct, 
                    self.restoreAllAct, self.iconizeAllAct, 
                    self.arrangeIconsAct, None])
        act = windowMenu.addMenu(self.windowsMenu)
        if len(self.editors) == 0:
            act.setEnabled(False)
        
    def _initWindowActions(self):
        """
        Protected method to define the user interface actions for window handling.
        """
        self.tileAct = E4Action(self.trUtf8('Tile'),
            self.trUtf8('&Tile'), 0, 0, self, 'vm_window_tile')
        self.tileAct.setStatusTip(self.trUtf8('Tile the windows'))
        self.tileAct.setWhatsThis(self.trUtf8(
            """<b>Tile the windows</b>"""
            """<p>Rearrange and resize the windows so that they are tiled.</p>"""
        ))
        self.connect(self.tileAct, SIGNAL('triggered()'), self.tile)
        self.windowActions.append(self.tileAct)
        
        self.cascadeAct = E4Action(self.trUtf8('Cascade'),
            self.trUtf8('&Cascade'), 0, 0, self, 'vm_window_cascade')
        self.cascadeAct.setStatusTip(self.trUtf8('Cascade the windows'))
        self.cascadeAct.setWhatsThis(self.trUtf8(
            """<b>Cascade the windows</b>"""
            """<p>Rearrange and resize the windows so that they are cascaded.</p>"""
        ))
        self.connect(self.cascadeAct, SIGNAL('triggered()'), self.cascade)
        self.windowActions.append(self.cascadeAct)
        
        self.nextChildAct = E4Action(self.trUtf8('Next'),
            self.trUtf8('&Next'), 0, 0, self, 'vm_window_next')
        self.nextChildAct.setStatusTip(self.trUtf8('Activate next window'))
        self.nextChildAct.setWhatsThis(self.trUtf8(
            """<b>Next</b>"""
            """<p>Activate the next window of the list of open windows.</p>"""
        ))
        self.connect(self.nextChildAct, SIGNAL('triggered()'), self.activateNextWindow)
        self.windowActions.append(self.nextChildAct)
        
        self.prevChildAct = E4Action(self.trUtf8('Previous'),
            self.trUtf8('&Previous'), 0, 0, self, 'vm_window_previous')
        self.prevChildAct.setStatusTip(self.trUtf8('Activate previous window'))
        self.prevChildAct.setWhatsThis(self.trUtf8(
            """<b>Previous</b>"""
            """<p>Activate the previous window of the list of open windows.</p>"""
        ))
        self.connect(self.prevChildAct, SIGNAL('triggered()'), 
            self.activatePreviousWindow)
        self.windowActions.append(self.prevChildAct)
        
        self.restoreAllAct = E4Action(self.trUtf8('Restore All'),
            self.trUtf8('&Restore All'), 0, 0, self, 'vm_window_restore_all')
        self.restoreAllAct.setStatusTip(self.trUtf8('Restore all windows'))
        self.restoreAllAct.setWhatsThis(self.trUtf8(
            """<b>Restore All</b>"""
            """<p>Restores all windows to their original size.</p>"""
        ))
        self.connect(self.restoreAllAct, SIGNAL('triggered()'), self.__restoreAllWindows)
        self.windowActions.append(self.restoreAllAct)
        
        self.iconizeAllAct = E4Action(self.trUtf8('Iconize All'),
            self.trUtf8('&Iconize All'), 0, 0, self, 'vm_window_iconize_all')
        self.iconizeAllAct.setStatusTip(self.trUtf8('Iconize all windows'))
        self.iconizeAllAct.setWhatsThis(self.trUtf8(
            """<b>Iconize All</b>"""
            """<p>Iconizes all windows.</p>"""
        ))
        self.connect(self.iconizeAllAct, SIGNAL('triggered()'), self.__iconizeAllWindows)
        self.windowActions.append(self.iconizeAllAct)
        
        self.arrangeIconsAct = E4Action(self.trUtf8('Arrange Icons'),
            self.trUtf8('&Arrange Icons'), 0, 0, self, 'vm_window_iconize_all')
        self.arrangeIconsAct.setStatusTip(self.trUtf8('Arrange all icons'))
        self.arrangeIconsAct.setWhatsThis(self.trUtf8(
            """<b>Arrange Icons</b>"""
            """<p>Arranges all icons.</p>"""
        ))
        self.connect(self.arrangeIconsAct, SIGNAL('triggered()'), self.arrangeIcons)
        self.windowActions.append(self.arrangeIconsAct)
        
    def setEditorName(self, editor, newName):
        """
        Public method to change the displayed name of the editor.
        
        @param editor editor window to be changed
        @param newName new name to be shown (string or QString)
        """
        pass
        
    def _modificationStatusChanged(self, m, editor):
        """
        Protected slot to handle the modificationStatusChanged signal.
        
        @param m flag indicating the modification status (boolean)
        @param editor editor window changed
        """
        if m:
            editor.setWindowIcon(UI.PixmapCache.getIcon("fileModified.png"))
        elif editor.hasSyntaxErrors():
            editor.setWindowIcon(UI.PixmapCache.getIcon("syntaxError.png"))
        else:
            editor.setWindowIcon(UI.PixmapCache.getIcon("empty.png"))
        self._checkActions(editor)
        
    def _syntaxErrorToggled(self, editor):
        """
        Protected slot to handle the syntaxerrorToggled signal.
        
        @param editor editor that sent the signal
        """
        if editor.hasSyntaxErrors():
            editor.setWindowIcon(UI.PixmapCache.getIcon("syntaxError.png"))
        else:
            editor.setWindowIcon(UI.PixmapCache.getIcon("empty.png"))
                
        ViewManager._syntaxErrorToggled(self, editor)
        
    def __windowActivated(self, editor):
        """
        Private slot to handle the windowActivated signal.
        
        @param editor the activated editor window
        """
        self._checkActions(editor)
        if editor is not None:
            fn = editor.getFileName()
            self.emit(SIGNAL('editorChanged'), unicode(fn))
        
    def eventFilter(self, watched, event):
        """
        Public method called to filter the event queue.
        
        @param watched the QObject being watched
        @param event the event that occurred
        @return always False
        """
        if event.type() == QEvent.Close and isinstance(watched, QScintilla.Editor.Editor):
            watched.close()
        
        return False
        
    def __restoreAllWindows(self):
        """
        Private slot to restore all windows.
        """
        for win in self.windowList():
            win.showNormal()
        
    def __iconizeAllWindows(self):
        """
        Private slot to iconize all windows.
        """
        for win in self.windowList():
            win.showMinimized()
        self.arrangeIcons()
