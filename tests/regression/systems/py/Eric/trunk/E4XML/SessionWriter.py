# -*- coding: utf-8 -*-

# Copyright (c) 2004 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the writer class for writing an XML project session file.
"""

import os
import time

from KdeQt.KQApplication import e4App

from XMLWriterBase import XMLWriterBase
from Config import sessionFileFormatVersion

import Preferences

class SessionWriter(XMLWriterBase):
    """
    Class implementing the writer class for writing an XML project session file.
    """
    def __init__(self, file, projectName):
        """
        Constructor
        
        @param file open file (like) object for writing
        @param projectName name of the project (string) or None for the
            global session
        """
        XMLWriterBase.__init__(self, file)
        
        self.name = projectName
        self.project = e4App().getObject("Project")
        self.multiProject = e4App().getObject("MultiProject")
        self.vm = e4App().getObject("ViewManager")
        self.dbg = e4App().getObject("DebugUI")
        self.dbs = e4App().getObject("DebugServer")
        
    def writeXML(self):
        """
        Public method to write the XML to the file.
        """
        isGlobal = self.name is None
        
        XMLWriterBase.writeXML(self)
        
        self._write('<!DOCTYPE Session SYSTEM "Session-%s.dtd">' % \
            sessionFileFormatVersion)
        
        # add some generation comments
        if not isGlobal:
            self._write("<!-- eric4 session file for project %s -->" % self.name)
        self._write("<!-- This file was generated automatically, do not edit. -->")
        if Preferences.getProject("XMLTimestamp") or isGlobal:
            self._write("<!-- Saved: %s -->" % time.strftime('%Y-%m-%d, %H:%M:%S'))
        
        # add the main tag
        self._write('<Session version="%s">' % sessionFileFormatVersion) 
        
        # step 0: save open multi project and project for the global session
        if isGlobal:
            if self.multiProject.isOpen():
                self._write('    <MultiProject>%s</MultiProject>' % \
                    self.multiProject.getMultiProjectFile())
            if self.project.isOpen():
                self._write('    <Project>%s</Project>' % \
                    self.project.getProjectFile())
        
        # step 1: save all open (project) filenames and the active window
        allOpenFiles = self.vm.getOpenFilenames()
        self._write("  <Filenames>")
        for of in allOpenFiles:
            if isGlobal or unicode(of).startswith(self.project.ppath):
                ed = self.vm.getOpenEditor(of)
                if ed is not None:
                    line, index = ed.getCursorPosition()
                    folds = ','.join([str(i + 1) for i in ed.getFolds()])
                else:
                    line, index = 0, 0
                    folds = ''
                self._write('    <Filename cline="%d" cindex="%d" folds="%s">%s</Filename>' % \
                    (line, index, folds, of))
        self._write("  </Filenames>")
        
        aw = self.vm.getActiveName()
        if aw and unicode(aw).startswith(self.project.ppath):
            ed = self.vm.getOpenEditor(aw)
            if ed is not None:
                line, index = ed.getCursorPosition()
            else:
                line, index = 0, 0
            self._write('  <ActiveWindow cline="%d" cindex="%d">%s</ActiveWindow>' % \
                (line, index, aw))
        
        # step 2a: save all breakpoints
        allBreaks = Preferences.getProject("SessionAllBreakpoints")
        projectFiles = self.project.getSources(True)
        bpModel = self.dbs.getBreakPointModel()
        self._write("  <Breakpoints>")
        for row in range(bpModel.rowCount()):
            index = bpModel.index(row, 0)
            fname, lineno, cond, temp, enabled, count = \
                bpModel.getBreakPointByIndex(index)[:6]
            if isGlobal or allBreaks or fname in projectFiles:
                self._write("    <Breakpoint>")
                self._write("      <BpFilename>%s</BpFilename>" % fname)
                self._write('      <Linenumber value="%d" />' % lineno)
                self._write("      <Condition>%s</Condition>" % self.escape(str(cond)))
                self._write('      <Temporary value="%s" />' % temp)
                self._write('      <Enabled value="%s" />' % enabled)
                self._write('      <Count value="%d" />' % count)
                self._write("    </Breakpoint>")
        self._write("  </Breakpoints>")
        
        # step 2b: save all watch expressions
        self._write("  <Watchexpressions>")
        wpModel = self.dbs.getWatchPointModel()
        for row in range(wpModel.rowCount()):
            index = wpModel.index(row, 0)
            cond, temp, enabled, count, special = wpModel.getWatchPointByIndex(index)[:5]
            self._write('    <Watchexpression>')
            self._write("      <Condition>%s</Condition>" % self.escape(str(cond)))
            self._write('      <Temporary value="%s" />' % temp)
            self._write('      <Enabled value="%s" />' % enabled)
            self._write('      <Count value="%d" />' % count)
            self._write('      <Special>%s</Special>' % special)
            self._write('    </Watchexpression>')
        self._write('  </Watchexpressions>')
        
        # step 3: save the debug info
        self._write("  <DebugInfo>")
        if isGlobal:
            if len(self.dbg.argvHistory):
                dbgCmdline = str(self.dbg.argvHistory[0])
            else:
                dbgCmdline = ""
            if len(self.dbg.wdHistory):
                dbgWd = self.dbg.wdHistory[0]
            else:
                dbgWd = ""
            if len(self.dbg.envHistory):
                dbgEnv = self.dbg.envHistory[0]
            else:
                dbgEnv = ""
            self._write("    <CommandLine>%s</CommandLine>" % self.escape(dbgCmdline))
            self._write("    <WorkingDirectory>%s</WorkingDirectory>" % dbgWd)
            self._write("    <Environment>%s</Environment>" % dbgEnv)
            self._write('    <ReportExceptions value="%s" />' % self.dbg.exceptions)
            self._write("    <Exceptions>")
            for exc in self.dbg.excList:
                self._write("      <Exception>%s</Exception>" % exc)
            self._write("    </Exceptions>")
            self._write("    <IgnoredExceptions>")
            for iexc in self.dbg.excIgnoreList:
                self._write("      <IgnoredException>%s</IgnoredException>" % iexc)
            self._write("    </IgnoredExceptions>")
            self._write('    <AutoClearShell value="%s" />' % self.dbg.autoClearShell)
            self._write('    <TracePython value="%s" />' % self.dbg.tracePython)
            self._write('    <AutoContinue value="%s" />' % self.dbg.autoContinue)
            self._write("    <CovexcPattern></CovexcPattern>")  # kept for compatibility
        else:
            self._write("    <CommandLine>%s</CommandLine>" % \
                self.escape(str(self.project.dbgCmdline)))
            self._write("    <WorkingDirectory>%s</WorkingDirectory>" % \
                self.project.dbgWd)
            self._write("    <Environment>%s</Environment>" % \
                self.project.dbgEnv)
            self._write('    <ReportExceptions value="%s" />' % \
                self.project.dbgReportExceptions)
            self._write("    <Exceptions>")
            for exc in self.project.dbgExcList:
                self._write("      <Exception>%s</Exception>" % exc)
            self._write("    </Exceptions>")
            self._write("    <IgnoredExceptions>")
            for iexc in self.project.dbgExcIgnoreList:
                self._write("      <IgnoredException>%s</IgnoredException>" % iexc)
            self._write("    </IgnoredExceptions>")
            self._write('    <AutoClearShell value="%s" />' % \
                self.project.dbgAutoClearShell)
            self._write('    <TracePython value="%s" />' % \
                self.project.dbgTracePython)
            self._write('    <AutoContinue value="%s" />' % \
                self.project.dbgAutoContinue)
            self._write("    <CovexcPattern></CovexcPattern>")  # kept for compatibility
        self._write("  </DebugInfo>")
        
        # step 4: save bookmarks of all open (project) files
        self._write("  <Bookmarks>")
        for of in allOpenFiles:
            if isGlobal or unicode(of).startswith(self.project.ppath):
                editor = self.vm.getOpenEditor(of)
                for bookmark in editor.getBookmarks():
                    self._write("    <Bookmark>")
                    self._write("      <BmFilename>%s</BmFilename>" % of)
                    self._write('      <Linenumber value="%d" />' % bookmark)
                    self._write("    </Bookmark>")
        self._write("  </Bookmarks>")
        
        self._write("</Session>", newline = False)
