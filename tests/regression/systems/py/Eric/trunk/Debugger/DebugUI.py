# -*- coding: utf-8 -*-

# Copyright (c) 2002 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the debugger UI.
"""

import os

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from KdeQt import KQMessageBox, KQInputDialog

from UI.Info import *
from VariablesFilterDialog import *
from ExceptionsFilterDialog import *
from StartDialog import *
from EditBreakpointDialog import EditBreakpointDialog

from DebugClientCapabilities import *
import Preferences
import Utilities
import UI.PixmapCache
import UI.Config

from E4Gui.E4Action import E4Action, createActionGroup

from eric4config import getConfig

class DebugUI(QObject):
    """
    Class implementing the debugger part of the UI.
    
    @signal clientStack(stack) emitted at breaking after a reported exception
    @signal compileForms() emitted if changed project forms should be compiled
    @signal compileResources() emitted if changed project resources should be compiled
    @signal debuggingStarted(filename) emitted when a debugging session was started
    @signal resetUI() emitted to reset the UI
    @signal exceptionInterrupt() emitted after the execution was interrupted by an
        exception and acknowledged by the user
    """
    def __init__(self, ui, vm, debugServer, debugViewer, project):
        """
        Constructor
        
        @param ui reference to the main UI
        @param vm reference to the viewmanager
        @param debugServer reference to the debug server
        @param debugViewer reference to the debug viewer widget
        @param project reference to the project object
        """
        QObject.__init__(self, ui)
        
        self.ui = ui
        self.viewmanager = vm
        self.debugServer = debugServer
        self.debugViewer = debugViewer
        self.project = project
        
        # Clear some variables
        self.projectOpen = False
        self.editorOpen = False
        
        # Generate the variables filter dialog
        self.dbgFilterDialog = VariablesFilterDialog(self.ui, 'Filter Dialog', True)

        # read the saved debug info values
        self.argvHistory = \
            Preferences.Prefs.settings \
            .value('DebugInfo/ArgumentsHistory').toStringList()
        self.wdHistory = \
            Preferences.Prefs.settings \
            .value('DebugInfo/WorkingDirectoryHistory').toStringList()
        self.envHistory = \
            Preferences.Prefs.settings \
            .value('DebugInfo/EnvironmentHistory').toStringList()
        self.excList = \
            Preferences.Prefs.settings \
            .value('DebugInfo/Exceptions').toStringList()
        self.excIgnoreList = \
            Preferences.Prefs.settings \
            .value('DebugInfo/IgnoredExceptions').toStringList()
        self.exceptions = \
            Preferences.Prefs.settings.value('DebugInfo/ReportExceptions', 
            QVariant(True)).toBool()
        self.autoClearShell = Preferences.Prefs.settings.value('DebugInfo/AutoClearShell',
            QVariant(True)).toBool()
        self.tracePython = Preferences.Prefs.settings.value('DebugInfo/TracePython', 
            QVariant(False)).toBool()
        self.autoContinue = Preferences.Prefs.settings.value('DebugInfo/AutoContinue', 
            QVariant(True)).toBool()
        self.forkAutomatically = Preferences.Prefs.settings.value(
            'DebugInfo/ForkAutomatically', QVariant(False)).toBool()
        self.forkIntoChild = Preferences.Prefs.settings.value('DebugInfo/ForkIntoChild', 
            QVariant(False)).toBool()
        
        self.evalHistory = QStringList()
        self.execHistory = QStringList()
        self.lastDebuggedFile = None
        self.lastStartAction = 0    # 0=None, 1=Script, 2=Project
        self.lastAction = -1
        self.debugActions = [self.__continue, self.__step,\
                        self.__stepOver, self.__stepOut,\
                        self.__stepQuit, self.__runToCursor]
        self.localsVarFilter, self.globalsVarFilter = Preferences.getVarFilters()
        self.debugViewer.setVariablesFilter(self.globalsVarFilter, self.localsVarFilter)
        
        # Connect the signals emitted by the debug-server
        self.connect(debugServer, SIGNAL('clientGone'), self.__clientGone)
        self.connect(debugServer, SIGNAL('clientLine'), self.__clientLine)
        self.connect(debugServer, SIGNAL('clientExit(int)'), self.__clientExit)
        self.connect(debugServer, SIGNAL('clientSyntaxError'), self.__clientSyntaxError)
        self.connect(debugServer, SIGNAL('clientException'), self.__clientException)
        self.connect(debugServer, SIGNAL('clientVariables'), self.__clientVariables)
        self.connect(debugServer, SIGNAL('clientVariable'), self.__clientVariable)
        self.connect(debugServer, SIGNAL('clientBreakConditionError'),
            self.__clientBreakConditionError)
        self.connect(debugServer, SIGNAL('clientWatchConditionError'),
            self.__clientWatchConditionError)
        self.connect(debugServer, SIGNAL('passiveDebugStarted'),
            self.__passiveDebugStarted)
        self.connect(debugServer, SIGNAL('clientThreadSet'), self.__clientThreadSet)
        
        self.connect(debugServer, SIGNAL('clientRawInput'), debugViewer.handleRawInput)
        self.connect(debugServer, SIGNAL('clientRawInputSent'),
            debugViewer.restoreCurrentPage)
        self.connect(debugServer, SIGNAL('clientThreadList'), debugViewer.showThreadList)
        
        # Connect the signals emitted by the viewmanager
        self.connect(vm, SIGNAL('editorOpened'), self.__editorOpened)
        self.connect(vm, SIGNAL('lastEditorClosed'), self.__lastEditorClosed)
        self.connect(vm, SIGNAL('checkActions'), self.__checkActions)
        self.connect(vm, SIGNAL('cursorChanged'), self.__cursorChanged)
        self.connect(vm, SIGNAL('breakpointToggled'), self.__cursorChanged)
        
        # Connect the signals emitted by the project
        self.connect(project, SIGNAL('projectOpened'), self.__projectOpened)
        self.connect(project, SIGNAL('newProject'), self.__projectOpened)
        self.connect(project, SIGNAL('projectClosed'), self.__projectClosed)
        self.connect(project, SIGNAL('projectSessionLoaded'),
            self.__projectSessionLoaded)
        
        # Set a flag for the passive debug mode
        self.passive = Preferences.getDebugger("PassiveDbgEnabled")
        
    def variablesFilter(self, scope):
        """
        Public method to get the variables filter for a scope.
        
        @param scope flag indicating global (True) or local (False) scope
        """
        if scope:
            return self.globalsVarFilter[:]
        else:
            return self.localsVarFilter[:]
        
    def initActions(self):
        """
        Method defining the user interface actions.
        """
        self.actions = []
        
        self.runAct = E4Action(self.trUtf8('Run Script'),
                UI.PixmapCache.getIcon("runScript.png"),
                self.trUtf8('&Run Script...'),Qt.Key_F2,0,self,'dbg_run_script')
        self.runAct.setStatusTip(self.trUtf8('Run the current Script'))
        self.runAct.setWhatsThis(self.trUtf8(
            """<b>Run Script</b>"""
            """<p>Set the command line arguments and run the script outside the"""
            """ debugger. If the file has unsaved changes it may be saved first.</p>"""
        ))
        self.connect(self.runAct, SIGNAL('triggered()'), self.__runScript)
        self.actions.append(self.runAct)

        self.runProjectAct = E4Action(self.trUtf8('Run Project'),
                UI.PixmapCache.getIcon("runProject.png"),
                self.trUtf8('Run &Project...'),Qt.SHIFT + Qt.Key_F2,0,self,
                'dbg_run_project')
        self.runProjectAct.setStatusTip(self.trUtf8('Run the current Project'))
        self.runProjectAct.setWhatsThis(self.trUtf8(
            """<b>Run Project</b>"""
            """<p>Set the command line arguments and run the current project"""
            """ outside the debugger."""
            """ If files of the current project have unsaved changes they may"""
            """ be saved first.</p>"""
        ))
        self.connect(self.runProjectAct, SIGNAL('triggered()'), self.__runProject)
        self.actions.append(self.runProjectAct)

        self.coverageAct = E4Action(self.trUtf8('Coverage run of Script'),
                UI.PixmapCache.getIcon("coverageScript.png"),
                self.trUtf8('Coverage run of Script...'),0,0,self,'dbg_coverage_script')
        self.coverageAct.setStatusTip(\
            self.trUtf8('Perform a coverage run of the current Script'))
        self.coverageAct.setWhatsThis(self.trUtf8(
            """<b>Coverage run of Script</b>"""
            """<p>Set the command line arguments and run the script under the control"""
            """ of a coverage analysis tool. If the file has unsaved changes it may be"""
            """ saved first.</p>"""
        ))
        self.connect(self.coverageAct, SIGNAL('triggered()'), self.__coverageScript)
        self.actions.append(self.coverageAct)

        self.coverageProjectAct = E4Action(self.trUtf8('Coverage run of Project'),
                UI.PixmapCache.getIcon("coverageProject.png"),
                self.trUtf8('Coverage run of Project...'),0,0,self,'dbg_coverage_project')
        self.coverageProjectAct.setStatusTip(\
            self.trUtf8('Perform a coverage run of the current Project'))
        self.coverageProjectAct.setWhatsThis(self.trUtf8(
            """<b>Coverage run of Project</b>"""
            """<p>Set the command line arguments and run the current project"""
            """ under the control of a coverage analysis tool."""
            """ If files of the current project have unsaved changes they may"""
            """ be saved first.</p>"""
        ))
        self.connect(self.coverageProjectAct, SIGNAL('triggered()'), self.__coverageProject)
        self.actions.append(self.coverageProjectAct)

        self.profileAct = E4Action(self.trUtf8('Profile Script'),
                UI.PixmapCache.getIcon("profileScript.png"),
                self.trUtf8('Profile Script...'),0,0,self,'dbg_profile_script')
        self.profileAct.setStatusTip(self.trUtf8('Profile the current Script'))
        self.profileAct.setWhatsThis(self.trUtf8(
            """<b>Profile Script</b>"""
            """<p>Set the command line arguments and profile the script."""
            """ If the file has unsaved changes it may be saved first.</p>"""
        ))
        self.connect(self.profileAct, SIGNAL('triggered()'), self.__profileScript)
        self.actions.append(self.profileAct)

        self.profileProjectAct = E4Action(self.trUtf8('Profile Project'),
                UI.PixmapCache.getIcon("profileProject.png"),
                self.trUtf8('Profile Project...'),0,0,self,'dbg_profile_project')
        self.profileProjectAct.setStatusTip(self.trUtf8('Profile the current Project'))
        self.profileProjectAct.setWhatsThis(self.trUtf8(
            """<b>Profile Project</b>"""
            """<p>Set the command line arguments and profile the current project."""
            """ If files of the current project have unsaved changes they may"""
            """ be saved first.</p>"""
        ))
        self.connect(self.profileProjectAct, SIGNAL('triggered()'), self.__profileProject)
        self.actions.append(self.profileProjectAct)

        self.debugAct = E4Action(self.trUtf8('Debug Script'),
                UI.PixmapCache.getIcon("debugScript.png"),
                self.trUtf8('&Debug Script...'),Qt.Key_F5,0,self,'dbg_debug_script')
        self.debugAct.setStatusTip(self.trUtf8('Debug the current Script'))
        self.debugAct.setWhatsThis(self.trUtf8(
            """<b>Debug Script</b>"""
            """<p>Set the command line arguments and set the current line to be the"""
            """ first executable Python statement of the current editor window."""
            """ If the file has unsaved changes it may be saved first.</p>"""
        ))
        self.connect(self.debugAct, SIGNAL('triggered()'), self.__debugScript)
        self.actions.append(self.debugAct)

        self.debugProjectAct = E4Action(self.trUtf8('Debug Project'),
                UI.PixmapCache.getIcon("debugProject.png"),
                self.trUtf8('Debug &Project...'),Qt.SHIFT + Qt.Key_F5,0,self,
                'dbg_debug_project')
        self.debugProjectAct.setStatusTip(self.trUtf8('Debug the current Project'))
        self.debugProjectAct.setWhatsThis(self.trUtf8(
            """<b>Debug Project</b>"""
            """<p>Set the command line arguments and set the current line to be the"""
            """ first executable Python statement of the main script of the current"""
            """ project. If files of the current project have unsaved changes they may"""
            """ be saved first.</p>"""
        ))
        self.connect(self.debugProjectAct, SIGNAL('triggered()'), self.__debugProject)
        self.actions.append(self.debugProjectAct)

        self.restartAct = E4Action(self.trUtf8('Restart Script'),
                UI.PixmapCache.getIcon("restart.png"),
                self.trUtf8('Restart Script'),Qt.Key_F4,0,self,'dbg_restart_script')
        self.restartAct.setStatusTip(self.trUtf8('Restart the last debugged script'))
        self.restartAct.setWhatsThis(self.trUtf8(
            """<b>Restart Script</b>"""
            """<p>Set the command line arguments and set the current line to be the"""
            """ first executable Python statement of the script that was debugged last."""
            """ If there are unsaved changes, they may be saved first.</p>"""
        ))
        self.connect(self.restartAct, SIGNAL('triggered()'), self.__doRestart)
        self.actions.append(self.restartAct)

        self.stopAct = E4Action(self.trUtf8('Stop Script'),
                UI.PixmapCache.getIcon("stopScript.png"),
                self.trUtf8('Stop Script'),Qt.SHIFT + Qt.Key_F10,0,
                self,'dbg_stop_script')
        self.stopAct.setStatusTip(self.trUtf8("""Stop the running script."""))
        self.stopAct.setWhatsThis(self.trUtf8(
            """<b>Stop Script</b>"""
            """<p>This stops the script running in the debugger backend.</p>"""
        ))
        self.connect(self.stopAct, SIGNAL('triggered()'), self.__stopScript)
        self.actions.append(self.stopAct)

        self.debugActGrp = createActionGroup(self)

        act = E4Action(self.trUtf8('Continue'),
                UI.PixmapCache.getIcon("continue.png"),
                self.trUtf8('&Continue'),Qt.Key_F6,0,
                self.debugActGrp,'dbg_continue')
        act.setStatusTip(\
            self.trUtf8('Continue running the program from the current line'))
        act.setWhatsThis(self.trUtf8(
            """<b>Continue</b>"""
            """<p>Continue running the program from the current line. The program will"""
            """ stop when it terminates or when a breakpoint is reached.</p>"""
        ))
        self.connect(act, SIGNAL('triggered()'), self.__continue)
        self.actions.append(act)

        act = E4Action(self.trUtf8('Continue to Cursor'),
                UI.PixmapCache.getIcon("continueToCursor.png"),
                self.trUtf8('Continue &To Cursor'),Qt.SHIFT + Qt.Key_F6,0,
                self.debugActGrp,'dbg_continue_to_cursor')
        act.setStatusTip(self.trUtf8("""Continue running the program from the"""
            """ current line to the current cursor position"""))
        act.setWhatsThis(self.trUtf8(
            """<b>Continue To Cursor</b>"""
            """<p>Continue running the program from the current line to the"""
            """ current cursor position.</p>"""
        ))
        self.connect(act, SIGNAL('triggered()'), self.__runToCursor)
        self.actions.append(act)

        act = E4Action(self.trUtf8('Single Step'),
                UI.PixmapCache.getIcon("step.png"),
                self.trUtf8('Sin&gle Step'),Qt.Key_F7,0,
                self.debugActGrp,'dbg_single_step')
        act.setStatusTip(self.trUtf8('Execute a single Python statement'))
        act.setWhatsThis(self.trUtf8(
            """<b>Single Step</b>"""
            """<p>Execute a single Python statement. If the statement"""
            """ is an <tt>import</tt> statement, a class constructor, or a"""
            """ method or function call then control is returned to the debugger at"""
            """ the next statement.</p>"""
        ))
        self.connect(act, SIGNAL('triggered()'), self.__step)
        self.actions.append(act)

        act = E4Action(self.trUtf8('Step Over'),
                UI.PixmapCache.getIcon("stepOver.png"),
                self.trUtf8('Step &Over'),Qt.Key_F8,0,
                self.debugActGrp,'dbg_step_over')
        act.setStatusTip(self.trUtf8("""Execute a single Python statement staying"""
            """ in the current frame"""))
        act.setWhatsThis(self.trUtf8(
            """<b>Step Over</b>"""
            """<p>Execute a single Python statement staying in the same frame. If"""
            """ the statement is an <tt>import</tt> statement, a class constructor,"""
            """ or a method or function call then control is returned to the debugger"""
            """ after the statement has completed.</p>"""
        ))
        self.connect(act, SIGNAL('triggered()'), self.__stepOver)
        self.actions.append(act)

        act = E4Action(self.trUtf8('Step Out'),
                UI.PixmapCache.getIcon("stepOut.png"),
                self.trUtf8('Step Ou&t'),Qt.Key_F9,0,
                self.debugActGrp,'dbg_step_out')
        act.setStatusTip(self.trUtf8("""Execute Python statements until leaving"""
            """ the current frame"""))
        act.setWhatsThis(self.trUtf8(
            """<b>Step Out</b>"""
            """<p>Execute Python statements until leaving the current frame. If"""
            """ the statements are inside an <tt>import</tt> statement, a class"""
            """ constructor, or a method or function call then control is returned"""
            """ to the debugger after the current frame has been left.</p>"""
        ))
        self.connect(act, SIGNAL('triggered()'), self.__stepOut)
        self.actions.append(act)

        act = E4Action(self.trUtf8('Stop'),
                UI.PixmapCache.getIcon("stepQuit.png"),
                self.trUtf8('&Stop'),Qt.Key_F10,0,
                self.debugActGrp,'dbg_stop')
        act.setStatusTip(self.trUtf8('Stop debugging'))
        act.setWhatsThis(self.trUtf8(
            """<b>Stop</b>"""
            """<p>Stop the running debugging session.</p>"""
        ))
        self.connect(act, SIGNAL('triggered()'), self.__stepQuit)
        self.actions.append(act)
        
        self.debugActGrp2 = createActionGroup(self)

        act = E4Action(self.trUtf8('Evaluate'),
                self.trUtf8('E&valuate...'),
                0,0,self.debugActGrp2,'dbg_evaluate')
        act.setStatusTip(self.trUtf8('Evaluate in current context'))
        act.setWhatsThis(self.trUtf8(
            """<b>Evaluate</b>"""
            """<p>Evaluate an expression in the current context of the"""
            """ debugged program. The result is displayed in the"""
            """ shell window.</p>"""
        ))
        self.connect(act, SIGNAL('triggered()'), self.__eval)
        self.actions.append(act)
        
        act = E4Action(self.trUtf8('Execute'),
                self.trUtf8('E&xecute...'),
                0,0,self.debugActGrp2,'dbg_execute')
        act.setStatusTip(\
            self.trUtf8('Execute a one line statement in the current context'))
        act.setWhatsThis(self.trUtf8(
            """<b>Execute</b>"""
            """<p>Execute a one line statement in the current context"""
            """ of the debugged program.</p>"""
        ))
        self.connect(act, SIGNAL('triggered()'), self.__exec)
        self.actions.append(act)
        
        self.dbgFilterAct = E4Action(self.trUtf8('Variables Type Filter'),
                self.trUtf8('Varia&bles Type Filter...'), 0, 0, self, 
                'dbg_variables_filter')
        self.dbgFilterAct.setStatusTip(self.trUtf8('Configure variables type filter'))
        self.dbgFilterAct.setWhatsThis(self.trUtf8(
            """<b>Variables Type Filter</b>"""
            """<p>Configure the variables type filter. Only variable types that are not"""
            """ selected are displayed in the global or local variables window"""
            """ during a debugging session.</p>"""
        ))
        self.connect(self.dbgFilterAct, SIGNAL('triggered()'), 
                     self.__configureVariablesFilters)
        self.actions.append(self.dbgFilterAct)

        self.excFilterAct = E4Action(self.trUtf8('Exceptions Filter'),
                self.trUtf8('&Exceptions Filter...'), 0, 0, self, 'dbg_exceptions_filter')
        self.excFilterAct.setStatusTip(self.trUtf8('Configure exceptions filter'))
        self.excFilterAct.setWhatsThis(self.trUtf8(
            """<b>Exceptions Filter</b>"""
            """<p>Configure the exceptions filter. Only exception types that are"""
            """ listed are highlighted during a debugging session.</p>"""
            """<p>Please note, that all unhandled exceptions are highlighted"""
            """ indepent from the filter list.</p>"""
        ))
        self.connect(self.excFilterAct, SIGNAL('triggered()'), 
                     self.__configureExceptionsFilter)
        self.actions.append(self.excFilterAct)
        
        self.excIgnoreFilterAct = E4Action(self.trUtf8('Ignored Exceptions'),
                self.trUtf8('&Ignored Exceptions...'), 0, 0, 
                self, 'dbg_ignored_exceptions')
        self.excIgnoreFilterAct.setStatusTip(self.trUtf8('Configure ignored exceptions'))
        self.excIgnoreFilterAct.setWhatsThis(self.trUtf8(
            """<b>Ignored Exceptions</b>"""
            """<p>Configure the ignored exceptions. Only exception types that are"""
            """ not listed are highlighted during a debugging session.</p>"""
            """<p>Please note, that unhandled exceptions cannot be ignored.</p>"""
        ))
        self.connect(self.excIgnoreFilterAct, SIGNAL('triggered()'), 
                     self.__configureIgnoredExceptions)
        self.actions.append(self.excIgnoreFilterAct)

        self.dbgSetBpActGrp = createActionGroup(self)

        self.dbgToggleBpAct = E4Action(self.trUtf8('Toggle Breakpoint'),
                UI.PixmapCache.getIcon("breakpointToggle.png"),
                self.trUtf8('Toggle Breakpoint'), 
                QKeySequence(self.trUtf8("Shift+F11","Debug|Toggle Breakpoint")), 0, 
                self.dbgSetBpActGrp, 'dbg_toggle_breakpoint')
        self.dbgToggleBpAct.setStatusTip(self.trUtf8('Toggle Breakpoint'))
        self.dbgToggleBpAct.setWhatsThis(self.trUtf8(
            """<b>Toggle Breakpoint</b>"""
            """<p>Toggles a breakpoint at the current line of the"""
            """ current editor.</p>"""
        ))
        self.connect(self.dbgToggleBpAct, SIGNAL('triggered()'), self.__toggleBreakpoint)
        self.actions.append(self.dbgToggleBpAct)
        
        self.dbgEditBpAct = E4Action(self.trUtf8('Edit Breakpoint'),
                UI.PixmapCache.getIcon("cBreakpointToggle.png"),
                self.trUtf8('Edit Breakpoint...'),
                QKeySequence(self.trUtf8("Shift+F12","Debug|Edit Breakpoint")), 0, 
                self.dbgSetBpActGrp, 'dbg_edit_breakpoint')
        self.dbgEditBpAct.setStatusTip(self.trUtf8('Edit Breakpoint'))
        self.dbgEditBpAct.setWhatsThis(self.trUtf8(
            """<b>Edit Breakpoint</b>"""
            """<p>Opens a dialog to edit the breakpoints properties."""
            """ It works at the current line of the current editor.</p>"""
        ))
        self.connect(self.dbgEditBpAct, SIGNAL('triggered()'), self.__editBreakpoint)
        self.actions.append(self.dbgEditBpAct)

        self.dbgNextBpAct = E4Action(self.trUtf8('Next Breakpoint'),
                UI.PixmapCache.getIcon("breakpointNext.png"),
                self.trUtf8('Next Breakpoint'),
                QKeySequence(self.trUtf8("Ctrl+Shift+PgDown","Debug|Next Breakpoint")), 0,
                self.dbgSetBpActGrp, 'dbg_next_breakpoint')
        self.dbgNextBpAct.setStatusTip(self.trUtf8('Next Breakpoint'))
        self.dbgNextBpAct.setWhatsThis(self.trUtf8(
            """<b>Next Breakpoint</b>"""
            """<p>Go to next breakpoint of the current editor.</p>"""
        ))
        self.connect(self.dbgNextBpAct, SIGNAL('triggered()'), self.__nextBreakpoint)
        self.actions.append(self.dbgNextBpAct)

        self.dbgPrevBpAct = E4Action(self.trUtf8('Previous Breakpoint'),
                UI.PixmapCache.getIcon("breakpointPrevious.png"),
                self.trUtf8('Previous Breakpoint'),
                QKeySequence(self.trUtf8("Ctrl+Shift+PgUp","Debug|Previous Breakpoint")), 
                0, self.dbgSetBpActGrp, 'dbg_previous_breakpoint')
        self.dbgPrevBpAct.setStatusTip(self.trUtf8('Previous Breakpoint'))
        self.dbgPrevBpAct.setWhatsThis(self.trUtf8(
            """<b>Previous Breakpoint</b>"""
            """<p>Go to previous breakpoint of the current editor.</p>"""
        ))
        self.connect(self.dbgPrevBpAct, SIGNAL('triggered()'), self.__previousBreakpoint)
        self.actions.append(self.dbgPrevBpAct)

        act = E4Action(self.trUtf8('Clear Breakpoints'),
                self.trUtf8('Clear Breakpoints'),
                QKeySequence(self.trUtf8("Ctrl+Shift+C","Debug|Clear Breakpoints")), 0,
                self.dbgSetBpActGrp, 'dbg_clear_breakpoint')
        act.setStatusTip(self.trUtf8('Clear Breakpoints'))
        act.setWhatsThis(self.trUtf8(
            """<b>Clear Breakpoints</b>"""
            """<p>Clear breakpoints of all editors.</p>"""
        ))
        self.connect(act, SIGNAL('triggered()'), self.__clearBreakpoints)
        self.actions.append(act)

        self.debugActGrp.setEnabled(False)
        self.debugActGrp2.setEnabled(False)
        self.dbgSetBpActGrp.setEnabled(False)
        self.runAct.setEnabled(False)
        self.runProjectAct.setEnabled(False)
        self.profileAct.setEnabled(False)
        self.profileProjectAct.setEnabled(False)
        self.coverageAct.setEnabled(False)
        self.coverageProjectAct.setEnabled(False)
        self.debugAct.setEnabled(False)
        self.debugProjectAct.setEnabled(False)
        self.restartAct.setEnabled(False)
        self.stopAct.setEnabled(False)
        
    def initMenus(self):
        """
        Public slot to initialize the project menu.
        
        @return the generated menu
        """
        dmenu = QMenu(self.trUtf8('&Debug'), self.parent())
        dmenu.setTearOffEnabled(True)
        smenu = QMenu(self.trUtf8('&Start'), self.parent())
        smenu.setTearOffEnabled(True)
        self.breakpointsMenu = QMenu(self.trUtf8('&Breakpoints'), dmenu)
        
        smenu.addAction(self.restartAct)
        smenu.addAction(self.stopAct)
        smenu.addSeparator()
        smenu.addAction(self.runAct)
        smenu.addAction(self.runProjectAct)
        smenu.addSeparator()
        smenu.addAction(self.debugAct)
        smenu.addAction(self.debugProjectAct)
        smenu.addSeparator()
        smenu.addAction(self.profileAct)
        smenu.addAction(self.profileProjectAct)
        smenu.addSeparator()
        smenu.addAction(self.coverageAct)
        smenu.addAction(self.coverageProjectAct)
        
        dmenu.addActions(self.debugActGrp.actions())
        dmenu.addSeparator()
        dmenu.addActions(self.debugActGrp2.actions())
        dmenu.addSeparator()
        dmenu.addActions(self.dbgSetBpActGrp.actions())
        self.menuBreakpointsAct = dmenu.addMenu(self.breakpointsMenu)
        dmenu.addSeparator()
        dmenu.addAction(self.dbgFilterAct)
        dmenu.addAction(self.excFilterAct)
        dmenu.addAction(self.excIgnoreFilterAct)
        
        self.connect(self.breakpointsMenu, SIGNAL('aboutToShow()'),
            self.__showBreakpointsMenu)
        self.connect(self.breakpointsMenu, SIGNAL('triggered(QAction *)'),
            self.__breakpointSelected)
        self.connect(dmenu, SIGNAL('aboutToShow()'), self.__showDebugMenu)
        
        return smenu, dmenu
        
    def initToolbars(self, toolbarManager):
        """
        Public slot to initialize the debug toolbars.
        
        @param toolbarManager reference to a toolbar manager object (E4ToolBarManager)
        @return the generated toolbars (list of QToolBar)
        """
        starttb = QToolBar(self.trUtf8("Start"), self.parent())
        starttb.setIconSize(UI.Config.ToolBarIconSize)
        starttb.setObjectName("StartToolbar")
        starttb.setToolTip(self.trUtf8('Start'))
        
        starttb.addAction(self.restartAct)
        starttb.addAction(self.stopAct)
        starttb.addSeparator()
        starttb.addAction(self.runAct)
        starttb.addAction(self.runProjectAct)
        starttb.addSeparator()
        starttb.addAction(self.debugAct)
        starttb.addAction(self.debugProjectAct)
        
        debugtb = QToolBar(self.trUtf8("Debug"), self.parent())
        debugtb.setIconSize(UI.Config.ToolBarIconSize)
        debugtb.setObjectName("DebugToolbar")
        debugtb.setToolTip(self.trUtf8('Debug'))
        
        debugtb.addActions(self.debugActGrp.actions())
        debugtb.addSeparator()
        debugtb.addAction(self.dbgToggleBpAct)
        debugtb.addAction(self.dbgEditBpAct)
        debugtb.addAction(self.dbgNextBpAct)
        debugtb.addAction(self.dbgPrevBpAct)
        
        toolbarManager.addToolBar(starttb, starttb.windowTitle())
        toolbarManager.addToolBar(debugtb, debugtb.windowTitle())
        toolbarManager.addAction(self.profileAct, starttb.windowTitle())
        toolbarManager.addAction(self.profileProjectAct, starttb.windowTitle())
        toolbarManager.addAction(self.coverageAct, starttb.windowTitle())
        toolbarManager.addAction(self.coverageProjectAct, starttb.windowTitle())
        
        return [starttb, debugtb]
        
    def setArgvHistory(self, argsStr, clearHistories = False):
        """
        Public slot to initialize the argv history.
        
        @param argsStr the commandline arguments (string or QString)
        @param clearHistories flag indicating, that the list should
            be cleared (boolean)
        """
        if clearHistories:
            self.argvHistory.clear()
        else:
            self.argvHistory.removeAll(argsStr)
        self.argvHistory.prepend(argsStr)

    def setWdHistory(self, wdStr, clearHistories = False):
        """
        Public slot to initialize the wd history.
        
        @param wdStr the working directory (string or QString)
        @param clearHistories flag indicating, that the list should
            be cleared (boolean)
        """
        if clearHistories:
            self.wdHistory.clear()
        else:
            self.wdHistory.removeAll(wdStr)
        self.wdHistory.prepend(wdStr)
        
    def setEnvHistory(self, envStr, clearHistories = False):
        """
        Public slot to initialize the env history.
        
        @param envStr the environment settings (string or QString)
        @param clearHistories flag indicating, that the list should
            be cleared (boolean)
        """
        if clearHistories:
            self.envHistory.clear()
        else:
            self.envHistory.removeAll(envStr)
        self.envHistory.prepend(envStr)
        
    def setExceptionReporting(self, exceptions):
        """
        Public slot to initialize the exception reporting flag.
        
        @param exceptions flag indicating exception reporting status (boolean)
        """
        self.exceptions = exceptions

    def setExcList(self, excList):
        """
        Public slot to initialize the exceptions type list.
        
        @param excList list of exception types (QStringList)
        """
        self.excList = excList[:]   # keep a copy
        
    def setExcIgnoreList(self, excIgnoreList):
        """
        Public slot to initialize the ignored exceptions type list.
        
        @param excIgnoreList list of ignored exception types (QStringList)
        """
        self.excIgnoreList = excIgnoreList[:]   # keep a copy
        
    def setAutoClearShell(self, autoClearShell):
        """
        Public slot to initialize the autoClearShell flag.
        
        @param autoClearShell flag indicating, that the interpreter window
            should be cleared (boolean)
        """
        self.autoClearShell = autoClearShell

    def setTracePython(self, tracePython):
        """
        Public slot to initialize the trace Python flag.
        
        @param tracePython flag indicating if the Python library should be
            traced as well (boolean)
        """
        self.tracePython = tracePython

    def setAutoContinue(self, autoContinue):
        """
        Public slot to initialize the autoContinue flag.
        
        @param autoContinue flag indicating, that the debugger should not stop at
            the first executable line (boolean)
        """
        self.autoContinue = autoContinue

    def __editorOpened(self, fn):
        """
        Private slot to handle the editorOpened signal.
        
        @param fn filename of the opened editor
        """
        self.editorOpen = True
        
        if fn:
            editor = self.viewmanager.getOpenEditor(fn)
        else:
            editor = None
        self.__checkActions(editor)
        
    def __lastEditorClosed(self):
        """
        Private slot to handle the closeProgram signal.
        """
        self.editorOpen = False
        self.debugAct.setEnabled(False)
        self.runAct.setEnabled(False)
        self.profileAct.setEnabled(False)
        self.coverageAct.setEnabled(False)
        self.debugActGrp.setEnabled(False)
        self.debugActGrp2.setEnabled(False)
        self.dbgSetBpActGrp.setEnabled(False)
        self.lastAction = -1
        if not self.projectOpen:
            self.restartAct.setEnabled(False)
            self.lastDebuggedFile = None
            self.lastStartAction = 0
        
    def __checkActions(self, editor):
        """
        Private slot to check some actions for their enable/disable status.
        
        @param editor editor window
        """
        if editor:
            fn = editor.getFileName()
        else:
            fn = None
        
        cap = 0
        if fn:
            for language in self.debugServer.getSupportedLanguages():
                exts = self.debugServer.getExtensions(language)
                if fn.endswith(exts):
                    cap = self.debugServer.getClientCapabilities(language)
                    break
            else:
                if editor.isPyFile():
                    cap = self.debugServer.getClientCapabilities('Python')
                elif editor.isPy3File():
                    cap = self.debugServer.getClientCapabilities('Python3')
                elif editor.isRubyFile():
                    cap = self.debugServer.getClientCapabilities('Ruby')
        
            if not self.passive:
                self.runAct.setEnabled(cap & HasInterpreter)
                self.coverageAct.setEnabled(cap & HasCoverage)
                self.profileAct.setEnabled(cap & HasProfiler)
                self.debugAct.setEnabled(cap & HasDebugger)
            self.dbgSetBpActGrp.setEnabled(cap & HasDebugger)
            if editor.curLineHasBreakpoint():
                self.dbgEditBpAct.setEnabled(True)
            else:
                self.dbgEditBpAct.setEnabled(False)
            if editor.hasBreakpoints():
                self.dbgNextBpAct.setEnabled(True)
                self.dbgPrevBpAct.setEnabled(True)
            else:
                self.dbgNextBpAct.setEnabled(False)
                self.dbgPrevBpAct.setEnabled(False)
        else:
            self.runAct.setEnabled(False)
            self.coverageAct.setEnabled(False)
            self.profileAct.setEnabled(False)
            self.debugAct.setEnabled(False)
            self.dbgSetBpActGrp.setEnabled(False)
        
    def __cursorChanged(self, editor):
        """
        Private slot handling the cursorChanged signal of the viewmanager.
        
        @param editor editor window
        """
        if editor is None:
            return
        
        if editor.isPyFile() or editor.isPy3File() or editor.isRubyFile():
            if editor.curLineHasBreakpoint():
                self.dbgEditBpAct.setEnabled(True)
            else:
                self.dbgEditBpAct.setEnabled(False)
            if editor.hasBreakpoints():
                self.dbgNextBpAct.setEnabled(True)
                self.dbgPrevBpAct.setEnabled(True)
            else:
                self.dbgNextBpAct.setEnabled(False)
                self.dbgPrevBpAct.setEnabled(False)
        
    def __projectOpened(self):
        """
        Private slot to handle the projectOpened signal.
        """
        self.projectOpen = True
        cap = self.debugServer.getClientCapabilities(\
            self.project.pdata["PROGLANGUAGE"][0])
        if not self.passive:
            self.debugProjectAct.setEnabled(cap & HasDebugger)
            self.runProjectAct.setEnabled(cap & HasInterpreter)
            self.profileProjectAct.setEnabled(cap & HasProfiler)
            self.coverageProjectAct.setEnabled(cap & HasCoverage)
        
    def __projectClosed(self):
        """
        Private slot to handle the projectClosed signal.
        """
        self.projectOpen = False
        self.runProjectAct.setEnabled(False)
        self.profileProjectAct.setEnabled(False)
        self.coverageProjectAct.setEnabled(False)
        self.debugProjectAct.setEnabled(False)
        
        if not self.editorOpen:
            self.restartAct.setEnabled(False)
            self.lastDebuggedFile = None
            self.lastStartAction = 0
        
    def __projectSessionLoaded(self):
        """
        Private slot to handle the projectSessionLoaded signal.
        """
        fn = self.project.getMainScript(True)
        if fn is not None:
            self.lastStartAction = 2
            self.lastDebuggedFile = fn
            self.restartAct.setEnabled(True)
        
    def shutdown(self):
        """
        Public method to perform shutdown actions.
        """
        # Just save the 10 most recent entries
        del self.argvHistory[10:]
        del self.wdHistory[10:]
        del self.envHistory[10:]
        
        Preferences.Prefs.settings.setValue('DebugInfo/ArgumentsHistory', 
            QVariant(self.argvHistory))
        Preferences.Prefs.settings.setValue('DebugInfo/WorkingDirectoryHistory', 
            QVariant(self.wdHistory))
        Preferences.Prefs.settings.setValue('DebugInfo/EnvironmentHistory', 
            QVariant(self.envHistory))
        Preferences.Prefs.settings.setValue('DebugInfo/Exceptions', 
            QVariant(self.excList))
        Preferences.Prefs.settings.setValue('DebugInfo/IgnoredExceptions', 
            QVariant(self.excIgnoreList))
        Preferences.Prefs.settings.setValue('DebugInfo/ReportExceptions', 
            QVariant(self.exceptions))
        Preferences.Prefs.settings.setValue('DebugInfo/AutoClearShell', 
            QVariant(self.autoClearShell))
        Preferences.Prefs.settings.setValue('DebugInfo/TracePython', 
            QVariant(self.tracePython))
        Preferences.Prefs.settings.setValue('DebugInfo/AutoContinue', 
            QVariant(self.autoContinue))
        Preferences.Prefs.settings.setValue('DebugInfo/ForkAutomatically', 
            QVariant(self.forkAutomatically))
        Preferences.Prefs.settings.setValue('DebugInfo/ForkIntoChild', 
            QVariant(self.forkIntoChild))
        
    def shutdownServer(self):
        """
        Public method to shut down the debug server.
        
        This is needed to cleanly close the sockets on Win OS.
        
        @return always true
        """
        self.debugServer.shutdownServer()
        return True
        
    def __resetUI(self):
        """
        Private slot to reset the user interface.
        """
        self.lastAction = -1
        self.debugActGrp.setEnabled(False)
        self.debugActGrp2.setEnabled(False)
        if not self.passive:
            if self.editorOpen:
                editor = self.viewmanager.activeWindow()
            else:
                editor = None
            self.__checkActions(editor)
            
            self.debugProjectAct.setEnabled(self.projectOpen)
            self.runProjectAct.setEnabled(self.projectOpen)
            self.profileProjectAct.setEnabled(self.projectOpen)
            self.coverageProjectAct.setEnabled(self.projectOpen)
            if self.lastDebuggedFile is not None and \
                (self.editorOpen or self.projectOpen):
                self.restartAct.setEnabled(True)
            else:
                self.restartAct.setEnabled(False)
            self.stopAct.setEnabled(False)
        self.emit(SIGNAL('resetUI'))
        
    def __clientLine(self, fn, line, forStack):
        """
        Private method to handle a change to the current line.
        
        @param fn filename (string)
        @param line linenumber (int)
        @param forStack flag indicating this is for a stack dump (boolean)
        """
        self.ui.raise_()
        self.ui.activateWindow()
        if self.ui.getViewProfile() != "debug":
            self.ui.setDebugProfile()
        self.viewmanager.setFileLine(fn, line)
        if not forStack:
            self.__getThreadList()
            self.__getClientVariables()

    def __clientExit(self, status):
        """
        Private method to handle the debugged program terminating.
        
        @param status exit code of the debugged program (int)
        """
        self.viewmanager.exit()

        self.__resetUI()
        
        if not Preferences.getDebugger("SuppressClientExit") or status != 0:
            if self.ui.currentProg is None:
                KQMessageBox.information(self.ui,Program,
                    self.trUtf8('<p>The program has terminated with an exit'
                                ' status of %1.</p>').arg(status))
            else:
                KQMessageBox.information(self.ui,Program,
                    self.trUtf8('<p><b>%1</b> has terminated with an exit'
                                ' status of %2.</p>')
                        .arg(Utilities.normabspath(self.ui.currentProg))
                        .arg(status))

    def __clientSyntaxError(self, message, filename, lineNo, characterNo):
        """
        Private method to handle a syntax error in the debugged program.
        
        @param message message of the syntax error (string)
        @param filename translated filename of the syntax error position (string)
        @param lineNo line number of the syntax error position (integer)
        @param characterNo character number of the syntax error position (integer)
        """
        self.__resetUI()
        self.ui.raise_()
        self.ui.activateWindow()
        
        if message is None:
            KQMessageBox.critical(self.ui,Program,
                self.trUtf8('The program being debugged contains an unspecified'
                            ' syntax error.'))
            return
            
        self.viewmanager.setFileLine(filename, lineNo, True, True)
        KQMessageBox.critical(self.ui,Program,
            self.trUtf8('<p>The file <b>%1</b> contains the syntax error'
                        ' <b>%2</b> at line <b>%3</b>, character <b>%4</b>.</p>')
                .arg(filename)
                .arg(message)
                .arg(lineNo)
                .arg(characterNo))
        
    def __clientException(self, exceptionType, exceptionMessage, stackTrace):
        """
        Private method to handle an exception of the debugged program.
        
        @param exceptionType type of exception raised (string)
        @param exceptionMessage message given by the exception (string)
        @param stackTrace list of stack entries.
        """
        self.ui.raise_()
        self.ui.activateWindow()
        QApplication.processEvents()
        if exceptionType is None:
            KQMessageBox.critical(self.ui,Program,
                self.trUtf8('An unhandled exception occured.'
                            ' See the shell window for details.'))
            return
        
        if (self.exceptions and \
            exceptionType not in self.excIgnoreList and \
            (not len(self.excList) or \
            (len(self.excList) and exceptionType in self.excList)))\
           or exceptionType.startswith('unhandled'):
            if stackTrace:
                self.viewmanager.setFileLine(stackTrace[0][0], stackTrace[0][1], True)
            if Preferences.getDebugger("BreakAlways"):
                res = QMessageBox.Yes
            else:
                if stackTrace:
                    if exceptionType.startswith('unhandled'):
                        buttons = QMessageBox.StandardButtons(\
                            QMessageBox.No | \
                            QMessageBox.Yes)
                    else:
                        buttons = QMessageBox.StandardButtons(\
                            QMessageBox.No | \
                            QMessageBox.Yes | \
                            QMessageBox.Ignore)
                    res = KQMessageBox.critical(self.ui, Program,
                        self.trUtf8('<p>The debugged program raised the exception'
                                    ' <b>%1</b><br>"<b>%2</b>"<br>File: <b>%3</b>,'
                                    ' Line: <b>%4</b></p><p>Break here?</p>')
                            .arg(exceptionType)
                            .arg(Utilities.html_encode(exceptionMessage))
                            .arg(stackTrace[0][0])
                            .arg(stackTrace[0][1]),
                        buttons,
                        QMessageBox.No)
                else:
                    res = KQMessageBox.critical(self.ui, Program,
                        self.trUtf8('<p>The debugged program raised the exception'
                                    ' <b>%1</b><br>"<b>%2</b>"</p>')
                            .arg(exceptionType)
                            .arg(Utilities.html_encode(exceptionMessage)))
            if res == QMessageBox.Yes:
                self.emit(SIGNAL('exceptionInterrupt'))
                stack = []
                for fn, ln in stackTrace:
                    stack.append((fn, ln, ''))
                self.emit(SIGNAL('clientStack'), stack)
                self.__getClientVariables()
                self.ui.setDebugProfile()
                return
            elif res == QMessageBox.Ignore:
                if exceptionType not in self.excIgnoreList:
                    self.excIgnoreList.append(exceptionType)
        
        if self.lastAction != -1:
            if self.lastAction == 2:
                self.__specialContinue()
            else:
                self.debugActions[self.lastAction]()
        else:
            self.__continue()
        
    def __clientGone(self,unplanned):
        """
        Private method to handle the disconnection of the debugger client.
        
        @param unplanned 1 if the client died, 0 otherwise
        """
        self.__resetUI()
        if unplanned:
            KQMessageBox.information(self.ui,Program,
                self.trUtf8('The program being debugged has terminated unexpectedly.'))
        
    def __getThreadList(self):
        """
        Private method to get the list of threads from the client.
        """
        self.debugServer.remoteThreadList()
        
    def __clientThreadSet(self):
        """
        Private method to handle a change of the client's current thread.
        """
        self.debugServer.remoteClientVariables(0, self.localsVarFilter)
        
    def __getClientVariables(self):
        """
        Private method to request the global and local variables.
        
        In the first step, the global variables are requested from the client.
        Once these have been received, the local variables are requested.
        This happens in the method '__clientVariables'.
        """
        # get globals first
        self.debugServer.remoteClientVariables(1, self.globalsVarFilter)
        # the local variables are requested once we have received the globals
        
    def __clientVariables(self, scope, variables):
        """
        Private method to write the clients variables to the user interface.
        
        @param scope scope of the variables (-1 = empty global, 1 = global, 0 = local)
        @param variables the list of variables from the client
        """
        if scope > 0:
            self.debugViewer.showVariables(variables, True)
            if scope == 1:
                # now get the local variables
                self.debugServer.remoteClientVariables(0, self.localsVarFilter)
        elif scope == 0:
            self.debugViewer.showVariables(variables, False)
        elif scope == -1:
            vlist = [('None','','')]
            self.debugViewer.showVariables(vlist, False)
        
        if scope < 1:
            self.debugActGrp.setEnabled(True)
            self.debugActGrp2.setEnabled(True)
        
    def __clientVariable(self, scope, variables):
        """
        Private method to write the contents of a clients classvariable to the user
        interface.
        
        @param scope scope of the variables (-1 = empty global, 1 = global, 0 = local)
        @param variables the list of members of a classvariable from the client
        """
        if scope == 1:
            self.debugViewer.showVariable(variables, 1)
        elif scope == 0:
            self.debugViewer.showVariable(variables, 0)
            
    def __clientBreakConditionError(self, filename, lineno):
        """
        Private method to handle a condition error of a breakpoint.
        
        @param filename filename of the breakpoint
        @param lineno linenumber of the breakpoint
        """
        KQMessageBox.critical(None,
            self.trUtf8("Breakpoint Condition Error"),
            self.trUtf8("""<p>The condition of the breakpoint <b>%1, %2</b>"""
                        """ contains a syntax error.</p>""")\
                        .arg(filename).arg(lineno))
        
        model = self.debugServer.getBreakPointModel()
        index = model.getBreakPointIndex(filename, lineno)
        if not index.isValid():
            return
        
        bp = model.getBreakPointByIndex(index)
        if not bp:
            return
        
        fn, line, cond, temp, enabled, count = bp[:6]
        
        dlg = EditBreakpointDialog((fn, line), (cond, temp, enabled, count),
            QStringList(), self.ui, modal = True)
        if dlg.exec_() == QDialog.Accepted:
            cond, temp, enabled, count = dlg.getData()
            model.setBreakPointByIndex(index, fn, line, (cond, temp, enabled, count))
        
    def __clientWatchConditionError(self, cond):
        """
        Public method to handle a expression error of a watch expression.
        
        Note: This can only happen for normal watch expressions
        
        @param cond expression of the watch expression (string or QString)
        """
        KQMessageBox.critical(None,
            self.trUtf8("Watch Expression Error"),
            self.trUtf8("""<p>The watch expression <b>%1</b>"""
                        """ contains a syntax error.</p>""")\
                        .arg(cond))
        
        model = self.debugServer.getWatchPointModel()
        index = model.getWatchPointIndex(cond)
        if not index.isValid():
            return
        
        wp = model.getWatchPointByIndex(index)
        if not wp:
            return
        
        cond, special, temp, enabled, count = wp[:5]
        
        dlg = EditWatchpointDialog(\
            (QString(cond), temp, enabled, count, QString(special)), self)
        if dlg.exec_() == QDialog.Accepted:
            cond, temp, enabled, count, special = dlg.getData()
            
            # check for duplicates
            idx = self.__model.getWatchPointIndex(cond, special)
            duplicate = idx.isValid() and idx.internalPointer() != index.internalPointer()
            if duplicate:
                if special.isEmpty():
                    msg = self.trUtf8("""<p>A watch expression '<b>%1</b>'"""
                                      """ already exists.</p>""")\
                            .arg(Utilities.html_encode(unicode(cond)))
                else:
                    msg = self.trUtf8("""<p>A watch expression '<b>%1</b>'"""
                                """ for the variable <b>%2</b> already exists.</p>""")\
                            .arg(special)\
                            .arg(Utilities.html_encode(unicode(cond)))
                KQMessageBox.warning(None,
                    self.trUtf8("Watch expression already exists"),
                    msg)
                model.deleteWatchPointByIndex(index)
            else:
                model.setWatchPointByIndex(index, unicode(cond), unicode(special), 
                                                  (temp, enabled, count))
        
    def __configureVariablesFilters(self):
        """
        Private slot for displaying the variables filter configuration dialog.
        """
        result = self.dbgFilterDialog.exec_()
        if result == QDialog.Accepted:
            self.localsVarFilter, self.globalsVarFilter = \
                self.dbgFilterDialog.getSelection()
        else:
            self.dbgFilterDialog.setSelection(
                self.localsVarFilter, self.globalsVarFilter)
        self.debugViewer.setVariablesFilter(self.globalsVarFilter, self.localsVarFilter)

    def __configureExceptionsFilter(self):
        """
        Private slot for displaying the exception filter dialog.
        """
        dlg = ExceptionsFilterDialog(self.excList, ignore = False)
        if dlg.exec_() == QDialog.Accepted:
            self.excList = dlg.getExceptionsList()[:]   # keep a copy
        
    def __configureIgnoredExceptions(self):
        """
        Private slot for displaying the ignored exceptions dialog.
        """
        dlg = ExceptionsFilterDialog(self.excIgnoreList, ignore = True)
        if dlg.exec_() == QDialog.Accepted:
            self.excIgnoreList = dlg.getExceptionsList()[:]   # keep a copy
        
    def __toggleBreakpoint(self):
        """
        Private slot to handle the 'Set/Reset breakpoint' action.
        """
        self.viewmanager.activeWindow().menuToggleBreakpoint()
        
    def __editBreakpoint(self):
        """
        Private slot to handle the 'Edit breakpoint' action.
        """
        self.viewmanager.activeWindow().menuEditBreakpoint()
        
    def __nextBreakpoint(self):
        """
        Private slot to handle the 'Next breakpoint' action.
        """
        self.viewmanager.activeWindow().menuNextBreakpoint()
        
    def __previousBreakpoint(self):
        """
        Private slot to handle the 'Previous breakpoint' action.
        """
        self.viewmanager.activeWindow().menuPreviousBreakpoint()
        
    def __clearBreakpoints(self):
        """
        Private slot to handle the 'Clear breakpoints' action.
        """
        self.debugServer.getBreakPointModel().deleteAll()
        
    def __showDebugMenu(self):
        """
        Private method to set up the debug menu.
        """
        bpCount = self.debugServer.getBreakPointModel().rowCount()
        self.menuBreakpointsAct.setEnabled(bpCount > 0)
        
    def __showBreakpointsMenu(self):
        """
        Private method to handle the show breakpoints menu signal.
        """
        self.breakpointsMenu.clear()
        
        model = self.debugServer.getBreakPointModel()
        for row in range(model.rowCount()):
            index = model.index(row, 0)
            filename, line, cond = model.getBreakPointByIndex(index)[:3]
            if not cond:
                formattedCond = ""
            else:
                formattedCond = " : %s" % unicode(cond)[:20]
            bpSuffix = " : %d%s" % (line, formattedCond)
            act = self.breakpointsMenu.addAction(\
                "%s%s" % (\
                    Utilities.compactPath(\
                        filename,
                        self.ui.maxMenuFilePathLen - len(bpSuffix)), 
                    bpSuffix))
            act.setData(QVariant([QVariant(filename), QVariant(line)]))
    
    def __breakpointSelected(self, act):
        """
        Private method to handle the breakpoint selected signal.
        
        @param act reference to the action that triggered (QAction)
        """
        try:
            qvList = act.data().toPyObject()
            filename = unicode(qvList[0])
            line = qvList[1]
        except AttributeError:
            qvList = act.data().toList()
            filename = unicode(qvList[0].toString())
            line = qvList[1].toInt()[0]
        self.viewmanager.openSourceFile(filename, line)
        
    def __compileChangedProjectFiles(self):
        """
        Private method to signal compilation of changed forms and resources
        is wanted.
        """
        if Preferences.getProject("AutoCompileForms"):
            self.emit(SIGNAL('compileForms'))
        if Preferences.getProject("AutoCompileResources"):
            self.emit(SIGNAL('compileResources'))
        QApplication.processEvents()
        
    def __coverageScript(self):
        """
        Private slot to handle the coverage of script action.
        """
        self.__doCoverage(False)
        
    def __coverageProject(self):
        """
        Private slot to handle the coverage of project action.
        """
        self.__compileChangedProjectFiles()
        self.__doCoverage(True)
        
    def __doCoverage(self, runProject):
        """
        Private method to handle the coverage actions.
        
        @param runProject flag indicating coverage of the current project (True)
                or script (false)
        """
        self.__resetUI()
        doNotStart = False
        
        # Get the command line arguments, the working directory and the
        # exception reporting flag.
        if runProject:
            cap = self.trUtf8("Coverage of Project")
        else:
            cap = self.trUtf8("Coverage of Script")
        dlg = StartDialog(cap, self.argvHistory, self.wdHistory, self.envHistory,
            self.exceptions, self.ui, 2, autoClearShell = self.autoClearShell)
        if dlg.exec_() == QDialog.Accepted:
            argv, wd, env, exceptions, clearShell, clearHistories, console = dlg.getData()
            eraseCoverage = dlg.getCoverageData()
            
            if runProject:
                fn = self.project.getMainScript(1)
                if fn is None:
                    KQMessageBox.critical(self.ui,
                        self.trUtf8("Coverage of Project"),
                        self.trUtf8("There is no main script defined for the"
                            " current project. Aborting"))
                    return
                    
                if Preferences.getDebugger("Autosave") and \
                   not self.project.saveAllScripts(reportSyntaxErrors = True):
                    doNotStart = True
                
                # save the info for later use
                self.project.setDbgInfo(argv, wd, env, exceptions, self.excList, 
                    self.excIgnoreList, clearShell)
                
                self.lastStartAction = 6
            else:
                editor = self.viewmanager.activeWindow()
                if editor is None:
                    return
                
                if not self.viewmanager.checkDirty(editor, 
                   Preferences.getDebugger("Autosave")) or \
                   editor.getFileName() is None:
                    return
                    
                fn = editor.getFileName()
                self.lastStartAction = 5
                
            # save the filename for use by the restart method
            self.lastDebuggedFile = fn
            self.restartAct.setEnabled(True)
            
            # This moves any previous occurrence of these arguments to the head
            # of the list.
            self.setArgvHistory(argv, clearHistories)
            self.setWdHistory(wd, clearHistories)
            self.setEnvHistory(env, clearHistories)
            
            # Save the exception flags
            self.exceptions = exceptions
            
            # Save the erase coverage flag
            self.eraseCoverage = eraseCoverage
            
            # Save the clear interpreter flag
            self.autoClearShell = clearShell
            
            # Save the run in console flag
            self.runInConsole = console
            
            # Hide all error highlights
            self.viewmanager.unhighlight()
            
            if not doNotStart:
                if runProject and self.project.getProjectType() == "E4Plugin":
                    argv.insert(0, "--plugin=%s " % fn)
                    fn = os.path.join(getConfig('ericDir'), "eric4.py")
                
                # Ask the client to open the new program.
                self.debugServer.remoteCoverage(fn, argv, wd, env, 
                    autoClearShell = self.autoClearShell, erase = eraseCoverage,
                    forProject = runProject, runInConsole = console)
                
                self.stopAct.setEnabled(True)
            
    def __profileScript(self):
        """
        Private slot to handle the profile script action.
        """
        self.__doProfile(False)
        
    def __profileProject(self):
        """
        Private slot to handle the profile project action.
        """
        self.__compileChangedProjectFiles()
        self.__doProfile(True)
        
    def __doProfile(self, runProject):
        """
        Private method to handle the profile actions.
        
        @param runProject flag indicating profiling of the current project (True)
                or script (False)
        """
        self.__resetUI()
        doNotStart = False
        
        # Get the command line arguments, the working directory and the
        # exception reporting flag.
        if runProject:
            cap = self.trUtf8("Profile of Project")
        else:
            cap = self.trUtf8("Profile of Script")
        dlg = StartDialog(cap, self.argvHistory, self.wdHistory, self.envHistory,
            self.exceptions, self.ui, 3,
            autoClearShell = self.autoClearShell)
        if dlg.exec_() == QDialog.Accepted:
            argv, wd, env, exceptions, clearShell, clearHistories, console = dlg.getData()
            eraseTimings = dlg.getProfilingData()
            
            if runProject:
                fn = self.project.getMainScript(1)
                if fn is None:
                    KQMessageBox.critical(self.ui,
                        self.trUtf8("Profile of Project"),
                        self.trUtf8("There is no main script defined for the"
                            " current project. Aborting"))
                    return
                    
                if Preferences.getDebugger("Autosave") and \
                   not self.project.saveAllScripts(reportSyntaxErrors = True):
                    doNotStart = True
                
                # save the info for later use
                self.project.setDbgInfo(argv, wd, env, exceptions, self.excList,
                    self.excIgnoreList, clearShell)
                
                self.lastStartAction = 8
            else:
                editor = self.viewmanager.activeWindow()
                if editor is None:
                    return
                
                if not self.viewmanager.checkDirty(editor, 
                   Preferences.getDebugger("Autosave")) or \
                   editor.getFileName() is None:
                    return
                    
                fn = editor.getFileName()
                self.lastStartAction = 7
                
            # save the filename for use by the restart method
            self.lastDebuggedFile = fn
            self.restartAct.setEnabled(True)
            
            # This moves any previous occurrence of these arguments to the head
            # of the list.
            self.setArgvHistory(argv, clearHistories)
            self.setWdHistory(wd, clearHistories)
            self.setEnvHistory(env, clearHistories)
            
            # Save the exception flags
            self.exceptions = exceptions
            
            # Save the erase timing flag
            self.eraseTimings = eraseTimings
            
            # Save the clear interpreter flag
            self.autoClearShell = clearShell
            
            # Save the run in console flag
            self.runInConsole = console
            
            # Hide all error highlights
            self.viewmanager.unhighlight()
            
            if not doNotStart:
                if runProject and self.project.getProjectType() == "E4Plugin":
                    argv.insert(0, "--plugin=%s " % fn)
                    fn = os.path.join(getConfig('ericDir'), "eric4.py")
                
                # Ask the client to open the new program.
                self.debugServer.remoteProfile(fn, argv, wd, env,
                    autoClearShell = self.autoClearShell, erase = eraseTimings,
                    forProject = runProject, runInConsole = console)
                
                self.stopAct.setEnabled(True)
            
    def __runScript(self):
        """
        Private slot to handle the run script action.
        """
        self.__doRun(False)
        
    def __runProject(self):
        """
        Private slot to handle the run project action.
        """
        self.__compileChangedProjectFiles()
        self.__doRun(True)
        
    def __doRun(self, runProject):
        """
        Private method to handle the run actions.
        
        @param runProject flag indicating running the current project (True)
                or script (False)
        """
        self.__resetUI()
        doNotStart = False
        
        # Get the command line arguments, the working directory and the
        # exception reporting flag.
        if runProject:
            cap = self.trUtf8("Run Project")
        else:
            cap = self.trUtf8("Run Script")
        dlg = StartDialog(cap, self.argvHistory, self.wdHistory, self.envHistory, 
            self.exceptions, self.ui, 1,
            autoClearShell = self.autoClearShell)
        if dlg.exec_() == QDialog.Accepted:
            argv, wd, env, exceptions, clearShell, clearHistories, console = dlg.getData()
            
            if runProject:
                fn = self.project.getMainScript(1)
                if fn is None:
                    KQMessageBox.critical(self.ui,
                        self.trUtf8("Run Project"),
                        self.trUtf8("There is no main script defined for the"
                            " current project. Aborting"))
                    return
                    
                if Preferences.getDebugger("Autosave") and \
                   not self.project.saveAllScripts(reportSyntaxErrors = True):
                    doNotStart = True
                
                # save the info for later use
                self.project.setDbgInfo(argv, wd, env, exceptions, self.excList,
                    self.excIgnoreList, clearShell)
                
                self.lastStartAction = 4
            else:
                editor = self.viewmanager.activeWindow()
                if editor is None:
                    return
                
                if not self.viewmanager.checkDirty(editor, 
                   Preferences.getDebugger("Autosave")) or \
                   editor.getFileName() is None:
                    return
                    
                fn = editor.getFileName()
                self.lastStartAction = 3
                
            # save the filename for use by the restart method
            self.lastDebuggedFile = fn
            self.restartAct.setEnabled(True)
            
            # This moves any previous occurrence of these arguments to the head
            # of the list.
            self.setArgvHistory(argv, clearHistories)
            self.setWdHistory(wd, clearHistories)
            self.setEnvHistory(env, clearHistories)
            
            # Save the exception flags
            self.exceptions = exceptions
            
            # Save the clear interpreter flag
            self.autoClearShell = clearShell
            
            # Save the run in console flag
            self.runInConsole = console
            
            # Hide all error highlights
            self.viewmanager.unhighlight()
            
            if not doNotStart:
                if runProject and self.project.getProjectType() == "E4Plugin":
                    argv.insert(0, "--plugin=%s " % fn)
                    fn = os.path.join(getConfig('ericDir'), "eric4.py")
                
                # Ask the client to open the new program.
                self.debugServer.remoteRun(fn, argv, wd, env,
                    autoClearShell = self.autoClearShell, forProject = runProject, 
                    runInConsole = console)
                
                self.stopAct.setEnabled(True)
        
    def __debugScript(self):
        """
        Private slot to handle the debug script action.
        """
        self.__doDebug(False)
        
    def __debugProject(self):
        """
        Private slot to handle the debug project action.
        """
        self.__compileChangedProjectFiles()
        self.__doDebug(True)
        
    def __doDebug(self, debugProject):
        """
        Private method to handle the debug actions.
        
        @param debugProject flag indicating debugging the current project (True)
                or script (False)
        """
        self.__resetUI()
        doNotStart = False
        
        # Get the command line arguments, the working directory and the
        # exception reporting flag.
        if debugProject:
            cap = self.trUtf8("Debug Project")
        else:
            cap = self.trUtf8("Debug Script")
        dlg = StartDialog(cap, self.argvHistory, self.wdHistory, self.envHistory, 
            self.exceptions, self.ui, 0, tracePython = self.tracePython,
            autoClearShell = self.autoClearShell, autoContinue = self.autoContinue, 
            autoFork = self.forkAutomatically, forkChild = self.forkIntoChild)
        if dlg.exec_() == QDialog.Accepted:
            argv, wd, env, exceptions, clearShell, clearHistories, console = dlg.getData()
            tracePython, autoContinue, forkAutomatically, forkIntoChild = \
                dlg.getDebugData()
            
            if debugProject:
                fn = self.project.getMainScript(True)
                if fn is None:
                    KQMessageBox.critical(self.ui,
                        self.trUtf8("Debug Project"),
                        self.trUtf8("There is no main script defined for the"
                            " current project. No debugging possible."))
                    return
                    
                if Preferences.getDebugger("Autosave") and \
                   not self.project.saveAllScripts(reportSyntaxErrors = True):
                    doNotStart = True
                
                # save the info for later use
                self.project.setDbgInfo(argv, wd, env, exceptions, self.excList,
                    self.excIgnoreList, clearShell, tracePython = tracePython,
                    autoContinue = self.autoContinue)
                
                self.lastStartAction = 2
            else:
                editor = self.viewmanager.activeWindow()
                if editor is None:
                    return
                
                if not self.viewmanager.checkDirty(editor, 
                   Preferences.getDebugger("Autosave")) or \
                   editor.getFileName() is None:
                    return
                    
                fn = editor.getFileName()
                self.lastStartAction = 1
                
            # save the filename for use by the restart method
            self.lastDebuggedFile = fn
            self.restartAct.setEnabled(True)
            
            # This moves any previous occurrence of these arguments to the head
            # of the list.
            self.setArgvHistory(argv, clearHistories)
            self.setWdHistory(wd, clearHistories)
            self.setEnvHistory(env, clearHistories)
            
            # Save the exception flags
            self.exceptions = exceptions
            
            # Save the tracePython flag
            self.tracePython = tracePython
            
            # Save the clear interpreter flag
            self.autoClearShell = clearShell
            
            # Save the run in console flag
            self.runInConsole = console
            
            # Save the auto continue flag
            self.autoContinue = autoContinue
            
            # Save the forking flags
            self.forkAutomatically = forkAutomatically
            self.forkIntoChild = forkIntoChild
            
            # Hide all error highlights
            self.viewmanager.unhighlight()
            
            if not doNotStart:
                if debugProject and self.project.getProjectType() == "E4Plugin":
                    argv.insert(0, "--plugin=%s " % fn)
                    fn = os.path.join(getConfig('ericDir'), "eric4.py")
                    tracePython = True # override flag because it must be true
                
                # Ask the client to open the new program.
                self.debugServer.remoteLoad(fn, argv, wd, env, 
                    autoClearShell = self.autoClearShell, tracePython = tracePython,
                    autoContinue = autoContinue, forProject = debugProject, 
                    runInConsole = console, autoFork = forkAutomatically, 
                    forkChild = forkIntoChild)
                
                # Signal that we have started a debugging session
                self.emit(SIGNAL('debuggingStarted'), fn)
                
                self.stopAct.setEnabled(True)
        
    def __doRestart(self):
        """
        Private slot to handle the restart action to restart the last debugged file.
        """
        self.__resetUI()
        doNotStart = False
        
        # first save any changes
        if self.lastStartAction in [1, 3, 5, 7, 9]:
            editor = self.viewmanager.getOpenEditor(self.lastDebuggedFile)
            if editor and \
               not self.viewmanager.checkDirty(editor, 
               Preferences.getDebugger("Autosave")):
                return
            forProject = False
        elif self.lastStartAction in [2, 4, 6, 8, 10]:
            if Preferences.getDebugger("Autosave") and \
               not self.project.saveAllScripts(reportSyntaxErrors = True):
                doNotStart = True
            self.__compileChangedProjectFiles()
            forProject = True
        else:
            return      # should not happen
                    
        # get the saved stuff
        wd = self.wdHistory[0]
        argv = self.argvHistory[0]
        fn = self.lastDebuggedFile
        env = self.envHistory[0]
        
        # Hide all error highlights
        self.viewmanager.unhighlight()
        
        if not doNotStart:
            if forProject and self.project.getProjectType() == "E4Plugin":
                argv.insert(0, "--plugin=%s " % fn)
                fn = os.path.join(getConfig('ericDir'), "eric4.py")
            
            if self.lastStartAction in [1, 2]:
                # Ask the client to debug the new program.
                self.debugServer.remoteLoad(fn, argv, wd, env,  
                    autoClearShell = self.autoClearShell, tracePython = self.tracePython,
                    autoContinue = self.autoContinue, forProject = forProject, 
                    runInConsole = self.runInConsole)
                
                # Signal that we have started a debugging session
                self.emit(SIGNAL('debuggingStarted'), fn)
            elif self.lastStartAction in [3, 4]:
                # Ask the client to run the new program.
                self.debugServer.remoteRun(fn, argv, wd, env, 
                    autoClearShell = self.autoClearShell, forProject = forProject, 
                    runInConsole = self.runInConsole)
            elif self.lastStartAction in [5, 6]:
                # Ask the client to coverage run the new program.
                self.debugServer.remoteCoverage(fn, argv, wd, env, 
                    autoClearShell = self.autoClearShell, erase = self.eraseCoverage,
                    forProject = forProject, runInConsole = self.runInConsole)
            elif self.lastStartAction in [7, 8]:
                # Ask the client to profile run the new program.
                self.debugServer.remoteProfile(fn, argv, wd, env, 
                    autoClearShell = self.autoClearShell, erase = self.eraseTimings,
                    forProject = forProject, runInConsole = self.runInConsole)
            
            self.stopAct.setEnabled(True)
        
    def __stopScript(self):
        """
        Private slot to stop the running script.
        """
        self.debugServer.startClient(False)
        
    def __passiveDebugStarted(self, fn, exc):
        """
        Private slot to handle a passive debug session start.
        
        @param fn filename of the debugged script
        @param exc flag to enable exception reporting of the IDE (boolean)
        """
        # Hide all error highlights
        self.viewmanager.unhighlight()
        
        # Set filename of script being debugged
        self.ui.currentProg = fn
        
        # Set exception reporting
        self.setExceptionReporting(exc)
        
        # Signal that we have started a debugging session
        self.emit(SIGNAL('debuggingStarted'), fn)
        
    def __continue(self):
        """
        Private method to handle the Continue action.
        """
        self.lastAction = 0
        self.__enterRemote()
        self.debugServer.remoteContinue()

    def __specialContinue(self):
        """
        Private method to handle the Special Continue action.
        """
        self.lastAction = 2
        self.__enterRemote()
        self.debugServer.remoteContinue(1)

    def __step(self):
        """
        Private method to handle the Step action.
        """
        self.lastAction = 1
        self.__enterRemote()
        self.debugServer.remoteStep()

    def __stepOver(self):
        """
        Private method to handle the Step Over action.
        """
        self.lastAction = 2
        self.__enterRemote()
        self.debugServer.remoteStepOver()

    def __stepOut(self):
        """
        Private method to handle the Step Out action.
        """
        self.lastAction = 3
        self.__enterRemote()
        self.debugServer.remoteStepOut()

    def __stepQuit(self):
        """
        Private method to handle the Step Quit action.
        """
        self.lastAction = 4
        self.__enterRemote()
        self.debugServer.remoteStepQuit()
        self.__resetUI()

    def __runToCursor(self):
        """
        Private method to handle the Run to Cursor action.
        """
        self.lastAction = 0
        aw = self.viewmanager.activeWindow()
        line = aw.getCursorPosition()[0] + 1
        self.__enterRemote()
        self.debugServer.remoteBreakpoint(aw.getFileName(), 
            line, 1, None, 1)
        self.debugServer.remoteContinue()
    
    def __eval(self):
        """
        Private method to handle the Eval action.
        """
        # Get the command line arguments.
        if len(self.evalHistory) > 0:
            curr = 0
        else:
            curr = -1

        arg, ok = KQInputDialog.getItem(\
                            self.ui,
                            self.trUtf8("Evaluate"),
                            self.trUtf8("Enter the statement to evaluate"),
                            self.evalHistory,
                            curr, True)

        if ok:
            if arg.isNull():
                return

            # This moves any previous occurrence of this expression to the head
            # of the list.
            self.evalHistory.removeAll(arg)
            self.evalHistory.prepend(arg)
            
            self.debugServer.remoteEval(arg)
            
    def __exec(self):
        """
        Private method to handle the Exec action.
        """
        # Get the command line arguments.
        if len(self.execHistory) > 0:
            curr = 0
        else:
            curr = -1

        stmt, ok = KQInputDialog.getItem(\
                            self.ui,
                            self.trUtf8("Execute"),
                            self.trUtf8("Enter the statement to execute"),
                            self.execHistory,
                            curr, True)

        if ok:
            if stmt.isNull():
                return

            # This moves any previous occurrence of this statement to the head
            # of the list.
            self.execHistory.removeAll(stmt)
            self.execHistory.prepend(stmt)
            
            self.debugServer.remoteExec(stmt)
            
    def __enterRemote(self):
        """
        Private method to update the user interface.

        This method is called just prior to executing some of
        the program being debugged.
        """
        # Disable further debug commands from the user.
        self.debugActGrp.setEnabled(False)
        self.debugActGrp2.setEnabled(False)
        
        self.viewmanager.unhighlight(True)

    def getActions(self):
        """
        Public method to get a list of all actions.
        
        @return list of all actions (list of E4Action)
        """
        return self.actions[:]
