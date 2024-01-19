# -*- coding: utf-8 -*-

# Copyright (c) 2002 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a widget containing various debug related views.

The views avaliable are:
<ul>
  <li>variables viewer for global variables</li>
  <li>variables viewer for local variables</li>
  <li>viewer for breakpoints</li>
  <li>viewer for watch expressions</li>
  <li>viewer for exceptions</li>
  <li>viewer for threads</li>
  <li>a file browser (optional)</li>
  <li>an interpreter shell (optional)</li>
</ul>
"""

import os

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from QScintilla.Shell import Shell
from VariablesViewer import VariablesViewer
from ExceptionLogger import ExceptionLogger
from BreakPointViewer import BreakPointViewer
from WatchPointViewer import WatchPointViewer

import Utilities
import UI.PixmapCache

from E4Gui.E4TabWidget import E4TabWidget

class DebugViewer(QWidget):
    """
    Class implementing a widget conatining various debug related views.
    
    The individual tabs contain the interpreter shell (optional), 
    the filesystem browser (optional), the two variables viewers (global and local),
    a breakpoint viewer, a watch expression viewer and the exception logger. Additionally
    a list of all threads is shown.
    
    @signal sourceFile(string, int) emitted to open a source file at a line
    """
    def __init__(self, debugServer, docked, vm, parent = None, 
                 embeddedShell = True, embeddedBrowser = True):
        """
        Constructor
        
        @param debugServer reference to the debug server object
        @param docked flag indicating a dock window
        @param vm reference to the viewmanager object
        @param parent parent widget (QWidget)
        @param embeddedShell flag indicating whether the shell should be included.
                This flag is set to False by those layouts, that have the interpreter
                shell in a separate window.
        @param embeddedBrowser flag indicating whether the file browser should
                be included. This flag is set to False by those layouts, that
                have the file browser in a separate window or embedded
                in the project browser instead.
        """
        QWidget.__init__(self, parent)
        
        self.debugServer = debugServer
        self.debugUI = None
        
        self.setWindowIcon(UI.PixmapCache.getIcon("eric.png"))
        
        self.__mainLayout = QVBoxLayout()
        self.__mainLayout.setMargin(0)
        self.setLayout(self.__mainLayout)
        
        self.__tabWidget = E4TabWidget()
        self.__mainLayout.addWidget(self.__tabWidget)
        
        self.embeddedShell = embeddedShell
        if embeddedShell:
            # add the interpreter shell
            self.shell = Shell(debugServer, vm)
            index = self.__tabWidget.addTab(self.shell, 
                UI.PixmapCache.getIcon("shell.png"), '')
            self.__tabWidget.setTabToolTip(index, self.shell.windowTitle())
        
        self.embeddedBrowser = embeddedBrowser
        if embeddedBrowser:
            from UI.Browser import Browser
            # add the browser
            self.browser = Browser()
            index = self.__tabWidget.addTab(self.browser, 
                UI.PixmapCache.getIcon("browser.png"), '')
            self.__tabWidget.setTabToolTip(index, self.browser.windowTitle())
        
        # add the global variables viewer
        self.glvWidget = QWidget()
        self.glvWidgetVLayout = QVBoxLayout(self.glvWidget)
        self.glvWidgetVLayout.setMargin(0)
        self.glvWidgetVLayout.setSpacing(3)
        self.glvWidget.setLayout(self.glvWidgetVLayout)
        
        self.globalsViewer = VariablesViewer(self.glvWidget, True)
        self.glvWidgetVLayout.addWidget(self.globalsViewer)
        
        self.glvWidgetHLayout = QHBoxLayout()
        self.glvWidgetHLayout.setMargin(3)
        
        self.globalsFilterEdit = QLineEdit(self.glvWidget)
        self.globalsFilterEdit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.glvWidgetHLayout.addWidget(self.globalsFilterEdit)
        self.globalsFilterEdit.setToolTip(\
            self.trUtf8("Enter regular expression patterns separated by ';' to define "
                "variable filters. "))
        self.globalsFilterEdit.setWhatsThis(\
            self.trUtf8("Enter regular expression patterns separated by ';' to define "
                "variable filters. All variables and class attributes matched by one of "
                "the expressions are not shown in the list above."))
        
        self.setGlobalsFilterButton = QPushButton(self.trUtf8('Set'), self.glvWidget)
        self.glvWidgetHLayout.addWidget(self.setGlobalsFilterButton)
        self.glvWidgetVLayout.addLayout(self.glvWidgetHLayout)
        
        index = self.__tabWidget.addTab(self.glvWidget,
            UI.PixmapCache.getIcon("globalVariables.png"), '')
        self.__tabWidget.setTabToolTip(index, self.globalsViewer.windowTitle())
        
        self.connect(self.setGlobalsFilterButton, SIGNAL('clicked()'),
                     self.__setGlobalsFilter)
        self.connect(self.globalsFilterEdit, SIGNAL('returnPressed()'),
                     self.__setGlobalsFilter)
        
        # add the local variables viewer
        self.lvWidget = QWidget()
        self.lvWidgetVLayout = QVBoxLayout(self.lvWidget)
        self.lvWidgetVLayout.setMargin(0)
        self.lvWidgetVLayout.setSpacing(3)
        self.lvWidget.setLayout(self.lvWidgetVLayout)
        
        self.lvWidgetHLayout1 = QHBoxLayout()
        self.lvWidgetHLayout1.setMargin(3)
        
        self.stackComboBox = QComboBox(self.lvWidget)
        self.stackComboBox.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.lvWidgetHLayout1.addWidget(self.stackComboBox)

        self.sourceButton = QPushButton(self.trUtf8('Source'), self.lvWidget)
        self.lvWidgetHLayout1.addWidget(self.sourceButton)
        self.sourceButton.setEnabled(False)
        self.lvWidgetVLayout.addLayout(self.lvWidgetHLayout1)

        self.localsViewer = VariablesViewer(self.lvWidget, False)
        self.lvWidgetVLayout.addWidget(self.localsViewer)
        
        self.lvWidgetHLayout2 = QHBoxLayout()
        self.lvWidgetHLayout2.setMargin(3)
        
        self.localsFilterEdit = QLineEdit(self.lvWidget)
        self.localsFilterEdit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.lvWidgetHLayout2.addWidget(self.localsFilterEdit)
        self.localsFilterEdit.setToolTip(\
            self.trUtf8("Enter regular expression patterns separated by ';' to define "
                "variable filters. "))
        self.localsFilterEdit.setWhatsThis(\
            self.trUtf8("Enter regular expression patterns separated by ';' to define "
                "variable filters. All variables and class attributes matched by one of "
                "the expressions are not shown in the list above."))
        
        self.setLocalsFilterButton = QPushButton(self.trUtf8('Set'), self.lvWidget)
        self.lvWidgetHLayout2.addWidget(self.setLocalsFilterButton)
        self.lvWidgetVLayout.addLayout(self.lvWidgetHLayout2)
        
        index = self.__tabWidget.addTab(self.lvWidget,
            UI.PixmapCache.getIcon("localVariables.png"), '')
        self.__tabWidget.setTabToolTip(index, self.localsViewer.windowTitle())
        
        self.connect(self.sourceButton, SIGNAL('clicked()'), 
                     self.__showSource)
        self.connect(self.stackComboBox, SIGNAL('activated(int)'), 
                     self.__frameSelected)
        self.connect(self.setLocalsFilterButton, SIGNAL('clicked()'),
                     self.__setLocalsFilter)
        self.connect(self.localsFilterEdit, SIGNAL('returnPressed()'),
                     self.__setLocalsFilter)
        
        # add the breakpoint viewer
        self.breakpointViewer = BreakPointViewer()
        self.breakpointViewer.setModel(self.debugServer.getBreakPointModel())
        index = self.__tabWidget.addTab(self.breakpointViewer,
            UI.PixmapCache.getIcon("breakpoints.png"), '')
        self.__tabWidget.setTabToolTip(index, self.breakpointViewer.windowTitle())
        self.connect(self.breakpointViewer, SIGNAL("sourceFile"),
                     self, SIGNAL("sourceFile"))
        
        # add the watch expression viewer
        self.watchpointViewer = WatchPointViewer()
        self.watchpointViewer.setModel(self.debugServer.getWatchPointModel())
        index = self.__tabWidget.addTab(self.watchpointViewer,
            UI.PixmapCache.getIcon("watchpoints.png"), '')
        self.__tabWidget.setTabToolTip(index, self.watchpointViewer.windowTitle())
        
        # add the exception logger
        self.exceptionLogger = ExceptionLogger()
        index = self.__tabWidget.addTab(self.exceptionLogger, 
            UI.PixmapCache.getIcon("exceptions.png"), '')
        self.__tabWidget.setTabToolTip(index, self.exceptionLogger.windowTitle())
        
        if self.embeddedShell:
            self.__tabWidget.setCurrentWidget(self.shell)
        else:
            if self.embeddedBrowser:
                self.__tabWidget.setCurrentWidget(self.browser)
            else:
                self.__tabWidget.setCurrentWidget(self.lvWidget)
        
        # add the threads viewer
        self.__mainLayout.addWidget(QLabel(self.trUtf8("Threads:")))
        self.__threadList = QTreeWidget()
        self.__threadList.setHeaderLabels([self.trUtf8("ID"), self.trUtf8("Name"), 
                                           self.trUtf8("State"), ""])
        self.__threadList.setSortingEnabled(True)
        self.__mainLayout.addWidget(self.__threadList)
        
        self.__doThreadListUpdate = True
        
        self.connect(self.__threadList, 
                     SIGNAL('currentItemChanged(QTreeWidgetItem*, QTreeWidgetItem*)'), 
                     self.__threadSelected)
        
        self.__mainLayout.setStretchFactor(self.__tabWidget, 5)
        self.__mainLayout.setStretchFactor(self.__threadList, 1)
        
        self.currPage = None
        self.currentStack = None
        self.framenr = 0
        
        self.connect(self.debugServer, SIGNAL('clientStack'), self.handleClientStack)
        
    def setDebugger(self, debugUI):
        """
        Public method to set a reference to the Debug UI.
        
        @param debugUI reference to the DebugUI objectTrees
        """
        self.debugUI = debugUI
        self.connect(self.debugUI, SIGNAL('clientStack'), self.handleClientStack)
        
    def handleResetUI(self):
        """
        Public method to reset the SBVviewer.
        """
        self.globalsViewer.handleResetUI()
        self.localsViewer.handleResetUI()
        self.stackComboBox.clear()
        self.sourceButton.setEnabled(False)
        self.currentStack = None
        self.__threadList.clear()
        if self.embeddedShell:
            self.__tabWidget.setCurrentWidget(self.shell)
        else:
            if self.embeddedBrowser:
                self.__tabWidget.setCurrentWidget(self.browser)
            else:
                self.__tabWidget.setCurrentWidget(self.lvWidget)
        self.breakpointViewer.handleResetUI()
        
    def handleRawInput(self):
        """
        Pulic slot to handle the switch to the shell in raw input mode.
        """
        if self.embeddedShell:
            self.saveCurrentPage()
            self.__tabWidget.setCurrentWidget(self.shell)
            
    def showVariables(self, vlist, globals):
        """
        Public method to show the variables in the respective window.
        
        @param vlist list of variables to display
        @param globals flag indicating global/local state
        """
        if globals:
            self.globalsViewer.showVariables(vlist, self.framenr)
        else:
            self.localsViewer.showVariables(vlist, self.framenr)
            
    def showVariable(self, vlist, globals):
        """
        Public method to show the variables in the respective window.
        
        @param vlist list of variables to display
        @param globals flag indicating global/local state
        """
        if globals:
            self.globalsViewer.showVariable(vlist)
        else:
            self.localsViewer.showVariable(vlist)
            
    def showVariablesTab(self, globals):
        """
        Public method to make a variables tab visible.
        
        @param globals flag indicating global/local state
        """
        if globals:
            self.__tabWidget.setCurrentWidget(self.glvWidget)
        else:
            self.__tabWidget.setCurrentWidget(self.lvWidget)
        
    def saveCurrentPage(self):
        """
        Public slot to save the current page.
        """
        self.currPage = self.__tabWidget.currentWidget()
        
    def restoreCurrentPage(self):
        """
        Public slot to restore the previously saved page.
        """
        if self.currPage is not None:
            self.__tabWidget.setCurrentWidget(self.currPage)
            
    def handleClientStack(self, stack):
        """
        Public slot to show the call stack of the program being debugged.
        """
        self.framenr = 0
        self.stackComboBox.clear()
        self.currentStack = stack
        self.sourceButton.setEnabled(len(stack) > 0)
        for s in stack:
            # just show base filename to make it readable
            s = (os.path.basename(s[0]), s[1], s[2])
            self.stackComboBox.addItem('%s:%s:%s' % s)
        
    def setVariablesFilter(self, globalsFilter, localsFilter):
        """
        Public slot to set the local variables filter.
        
        @param globalsFilter filter list for global variable types (list of int)
        @param localsFilter filter list for local variable types (list of int)
        """
        self.globalsFilter = globalsFilter
        self.localsFilter = localsFilter
        
    def __showSource(self):
        """
        Private slot to handle the source button press to show the selected file.
        """
        s = self.currentStack[self.stackComboBox.currentIndex()]
        self.emit(SIGNAL('sourceFile'), s[0], int(s[1]))
        
    def __frameSelected(self, frmnr):
        """
        Private slot to handle the selection of a new stack frame number.
        
        @param frmnr frame number (0 is the current frame) (int)
        """
        self.framenr = frmnr
        self.debugServer.remoteClientVariables(0, self.localsFilter, frmnr)
        
    def __setGlobalsFilter(self):
        """
        Private slot to set the global variable filter
        """
        filter = unicode(self.globalsFilterEdit.text())
        self.debugServer.remoteClientSetFilter(1, filter)
        if self.currentStack:
            self.debugServer.remoteClientVariables(2, self.globalsFilter)
        
    def __setLocalsFilter(self):
        """
        Private slot to set the local variable filter
        """
        filter = unicode(self.localsFilterEdit.text())
        self.debugServer.remoteClientSetFilter(0, filter)
        if self.currentStack:
            self.debugServer.remoteClientVariables(0, self.localsFilter, self.framenr)
        
    def handleDebuggingStarted(self):
        """
        Public slot to handle the start of a debugging session.
        
        This slot sets the variables filter expressions.
        """
        self.__setGlobalsFilter()
        self.__setLocalsFilter()
        self.showVariablesTab(False)
        
    def currentWidget(self):
        """
        Public method to get a reference to the current widget.
        
        @return reference to the current widget (QWidget)
        """
        return self.__tabWidget.currentWidget()
        
    def showThreadList(self, currentID, threadList):
        """
        Public method to show the thread list.
        
        @param currentID id of the current thread (integer)
        @param threadList list of dictionaries containing the thread data
        """
        citm = None
        
        self.__threadList.clear()
        for thread in threadList:
            if thread['broken']:
                state = self.trUtf8("waiting at breakpoint")
            else:
                state = self.trUtf8("running")
            itm = QTreeWidgetItem(self.__threadList, 
                                  ["%d" % thread['id'], thread['name'], state])
            if thread['id'] == currentID:
                citm = itm
        
        self.__threadList.header().resizeSections(QHeaderView.ResizeToContents)
        self.__threadList.header().setStretchLastSection(True)
        
        if citm:
            self.__doThreadListUpdate = False
            self.__threadList.setCurrentItem(citm)
            self.__doThreadListUpdate = True
        
    def __threadSelected(self, current, previous):
        """
        Private slot to handle the selection of a thread in the thread list.
        
        @param current reference to the new current item (QTreeWidgetItem)
        @param previous reference to the previous current item (QTreeWidgetItem)
        """
        if current is not None and self.__doThreadListUpdate:
            tid, ok = current.text(0).toLong()
            if ok:
                self.debugServer.remoteSetThread(tid)
