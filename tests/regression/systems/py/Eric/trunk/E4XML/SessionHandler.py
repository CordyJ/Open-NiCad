# -*- coding: utf-8 -*-

# Copyright (c) 2003 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the handler class for reading an XML project session file.
"""

from PyQt4.QtCore import QStringList

from KdeQt.KQApplication import e4App

from Config import sessionFileFormatVersion
from XMLHandlerBase import XMLHandlerBase

class SessionHandler(XMLHandlerBase):
    """
    Class implementing a sax handler to read an XML project session file.
    """
    def __init__(self, project):
        """
        Constructor
        
        @param project Reference to the project object to store the
                information into.
        """
        XMLHandlerBase.__init__(self)
        
        self.startDocumentSpecific = self.startDocumentSession
        
        self.elements.update({
            'Session' : (self.startSession, self.defaultEndElement),
            'MultiProject' : (self.defaultStartElement, self.endMultiProject),
            'Project' : (self.defaultStartElement, self.endProject),
            'Filename' : (self.startFilename, self.endFilename),
            'ActiveWindow' : (self.startFilename, self.endFilename),
            'Breakpoint' : (self.startBreakpoint, self.endBreakpoint),
            'BpFilename' : (self.defaultStartElement, self.endBFilename),
            'Linenumber' : (self.startLinenumber, self.defaultEndElement),
            'Condition' : (self.defaultStartElement, self.endCondition),
            'Enabled' : (self.startEnabled, self.defaultEndElement),
            'Temporary' : (self.startTemporary, self.defaultEndElement),
            'Count' : (self.startCount, self.defaultEndElement),
            'Watchexpression' : (self.startWatchexpression, self.endWatchexpression),
            'Special' : (self.defaultStartElement, self.endSpecial),
            'CommandLine' : (self.defaultStartElement, self.endCommandLine),
            'WorkingDirectory' : (self.defaultStartElement, self.endWorkingDirectory),
            'Environment' : (self.defaultStartElement, self.endEnvironment),
            'ReportExceptions' : (self.startReportExceptions, self.defaultEndElement),
            'Exceptions' : (self.startExceptions, self.endExceptions),
            'Exception' : (self.defaultStartElement, self.endException),
            'IgnoredExceptions' : (self.startIgnoredExceptions, self.endIgnoredExceptions),
            'IgnoredException' : (self.defaultStartElement, self.endIgnoredException),
            'AutoClearShell' : (self.startAutoClearShell, self.defaultEndElement),
            'TracePython' : (self.startTracePython, self.defaultEndElement),
            'AutoContinue' : (self.startAutoContinue, self.defaultEndElement),
            'Bookmark' : (self.startBookmark, self.endBookmark),
            'BmFilename' : (self.defaultStartElement, self.endBFilename),
            
            ####################################################################
            ## backward compatibility
            ####################################################################
            'Watchpoint' : (self.startWatchexpression, self.endWatchexpression),    # 4.0
            'CovexcPattern' : (self.defaultStartElement, self.defaultEndElement),   # 4.3
        })
    
        self.project = project
        self.isGlobal = project is None
        
        self.project = e4App().getObject("Project")
        self.multiProject = e4App().getObject("MultiProject")
        self.vm = e4App().getObject("ViewManager")
        self.dbg = e4App().getObject("DebugUI")
        self.dbs = e4App().getObject("DebugServer")
        
    def startDocumentSession(self):
        """
        Handler called, when the document parsing is started.
        """
        if not self.isGlobal:
            # clear all breakpoints and bookmarks first
            # (in case we are rereading a session file)
            files = self.project.getSources(True)
            for file in files:
                editor = self.vm.getOpenEditor(file)
                if editor is not None:
                    editor.clearBookmarks()
            self.dbs.getBreakPointModel().deleteAll()
        self.version = ''
    
    ###################################################
    ## below follow the individual handler functions
    ###################################################
    
    def endMultiProject(self):
        """
        Handler method for the "MultiProject" end tag.
        """
        self.buffer = self.utf8_to_code(self.buffer)
        self.multiProject.openMultiProject(self.buffer, False)
        
    def endProject(self):
        """
        Handler method for the "Project" end tag.
        """
        self.buffer = self.utf8_to_code(self.buffer)
        self.project.openProject(self.buffer, False)
        
    def startFilename(self, attrs):
        """
        Handler method for the "Filename" start tag.
        
        @param attrs list of tag attributes
        """
        self.buffer = ""
        self.cline = int(attrs.get("cline", "0"))
        self.cindex = int(attrs.get("cindex", "0"))
        
        folds = attrs.get("folds", "")
        if folds:
            self.folds = [int(f) for f in folds.split(',')]
        else:
            self.folds = []
        
    def endFilename(self):
        """
        Handler method for the "Filename" end tag.
        """
        self.buffer = self.utf8_to_code(self.buffer)
        self.vm.openFiles(self.buffer)
        ed = self.vm.getOpenEditor(self.buffer)
        if ed is not None:
            if self.folds:
                ed.recolor()
                for line in self.folds:
                    ed.foldLine(line - 1)
            ed.setCursorPosition(self.cline, self.cindex)
            ed.ensureCursorVisible()
        
    def startBreakpoint(self, attrs):
        """
        Handler method for the "Breakpoint" start tag.
        
        @param attrs list of tag attributes
        """
        self.filename = ""
        self.lineno = 0
        self.bpCond = ""
        self.bpTemp = False
        self.bpEnabled = True
        self.bpCount = 0
        
    def endBreakpoint(self):
        """
        Handler method for the "Breakpoint" end tag.
        """
        self.dbs.getBreakPointModel().addBreakPoint(self.filename, self.lineno,
            (self.bpCond, self.bpTemp, self.bpEnabled, self.bpCount))
        
    def startWatchexpression(self, attrs):
        """
        Handler method for the "Watchexpression" start tag.
        
        @param attrs list of tag attributes
        """
        self.bpCond = ""
        self.bpTemp = False
        self.bpEnabled = True
        self.bpCount = 0
        self.wpSpecialCond = ""
        
    def endWatchexpression(self):
        """
        Handler method for the "Watchexpression" end tag.
        """
        self.dbs.getWatchPointModel().addWatchPoint(self.bpCond, 
            (self.bpTemp, self.bpEnabled, self.bpCount, self.wpSpecialCond))
        
    def endBFilename(self):
        """
        Handler method for the "BFilename" end tag.
        """
        self.filename = self.utf8_to_code(self.buffer)
        
    def startLinenumber(self, attrs):
        """
        Handler method for the "Linenumber" start tag.
        
        @param attrs list of tag attributes
        """
        self.lineno = int(attrs["value"])
        
    def endCondition(self):
        """
        Handler method for the "Condition" end tag.
        """
        cond = self.utf8_to_code(self.buffer)
        cond = self.unescape(cond)
        if cond == 'None':
            self.bpCond = ''
        else:
            self.bpCond = cond
            
    def startEnabled(self, attrs):
        """
        Handler method for the "Enabled" start tag.
        
        @param attrs list of tag attributes
        """
        self.bpEnabled = attrs["value"]
        if self.bpEnabled in ["True", "False"]:
            self.bpEnabled = self.bpEnabled == "True"
        else:
            self.bpEnabled = bool(int(self.bpEnabled))
        
    def startTemporary(self, attrs):
        """
        Handler method for the "Temporary" start tag.
        
        @param attrs list of tag attributes
        """
        self.bpTemp = attrs["value"]
        if self.bpTemp in ["True", "False"]:
            self.bpTemp = self.bpTemp == "True"
        else:
            self.bpTemp = bool(int(self.bpTemp))
        
    def startCount(self, attrs):
        """
        Handler method for the "Count" start tag.
        
        @param attrs list of tag attributes
        """
        self.bpCount = int(attrs["value"])
        
    def endSpecial(self):
        """
        Handler method for the "Special" end tag.
        """
        self.wpSpecialCond = self.utf8_to_code(self.buffer)
        
    def endCommandLine(self):
        """
        Handler method for the "CommandLine" end tag.
        """
        self.buffer = self.utf8_to_code(self.buffer)
        self.buffer = self.unescape(self.buffer)
        self.dbg.setArgvHistory(self.buffer)
        if not self.isGlobal:
            self.project.dbgCmdline = self.buffer
        
    def endWorkingDirectory(self):
        """
        Handler method for the "WorkinDirectory" end tag.
        """
        self.buffer = self.utf8_to_code(self.buffer)
        self.dbg.setWdHistory(self.buffer)
        if not self.isGlobal:
            self.project.dbgWd = self.buffer
        
    def endEnvironment(self):
        """
        Handler method for the "Environment" end tag.
        """
        self.buffer = self.utf8_to_code(self.buffer)
        self.dbg.setEnvHistory(self.buffer)
        if not self.isGlobal:
            self.project.dbgEnv = self.buffer
    
    def startReportExceptions(self, attrs):
        """
        Handler method for the "ReportExceptions" start tag.
        
        @param attrs list of tag attributes
        """
        exc = attrs.get("value", "False")
        if exc in ["True", "False"]:
            if exc == "True":
                exc = True
            else:
                exc = False
        else:
            exc = bool(int(exc))
        self.dbg.setExceptionReporting(exc)
        if not self.isGlobal:
            self.project.dbgReportExceptions = exc
        
    def startExceptions(self, attrs):
        """
        Handler method for the "Exceptions" start tag.
        
        @param attrs list of tag attributes
        """
        self.dbgExcList = QStringList()
        
    def endExceptions(self):
        """
        Handler method for the "Exceptions" end tag.
        """
        self.dbg.setExcList(self.dbgExcList)
        if not self.isGlobal:
            self.project.dbgExcList = self.dbgExcList[:] # keep a copy
        
    def endException(self):
        """
        Handler method for the "Exception" end tag.
        """
        self.buffer = self.utf8_to_code(self.buffer)
        self.dbgExcList.append(self.buffer)
        
    def startIgnoredExceptions(self, attrs):
        """
        Handler method for the "IgnoredExceptions" start tag.
        
        @param attrs list of tag attributes
        """
        self.dbgExcIgnoreList = QStringList()
        
    def endIgnoredExceptions(self):
        """
        Handler method for the "IgnoredExceptions" end tag.
        """
        self.dbg.setExcIgnoreList(self.dbgExcIgnoreList)
        if not self.isGlobal:
            self.project.dbgExcIgnoreList = self.dbgExcIgnoreList[:] # keep a copy
        
    def endIgnoredException(self):
        """
        Handler method for the "IgnoredException" end tag.
        """
        self.buffer = self.utf8_to_code(self.buffer)
        self.dbgExcIgnoreList.append(self.buffer)
        
    def startAutoClearShell(self, attrs):
        """
        Handler method for the "AutoClearShell" start tag.
        
        @param attrs list of tag attributes
        """
        autoClearShell = attrs.get("value", "False")
        if autoClearShell == "True":
            autoClearShell = True
        else:
            autoClearShell = False
        self.dbg.setAutoClearShell(autoClearShell)
        if not self.isGlobal:
            self.project.dbgAutoClearShell = autoClearShell
        
    def startTracePython(self, attrs):
        """
        Handler method for the "TracePython" start tag.
        
        @param attrs list of tag attributes
        """
        tracePython = attrs.get("value", "False")
        if tracePython in ["True", "False"]:
            if tracePython == "True":
                tracePython = True
            else:
                tracePython = False
        else:
            tracePython = bool(int(tracePython))
        self.dbg.setTracePython(tracePython)
        if not self.isGlobal:
            self.project.dbgTracePython = tracePython
        
    def startAutoContinue(self, attrs):
        """
        Handler method for the "AutoContinue" start tag.
        
        @param attrs list of tag attributes
        """
        autoContinue = attrs.get("value", "False")
        if autoContinue == "True":
            autoContinue = True
        else:
            autoContinue = False
        self.dbg.setAutoContinue(autoContinue)
        if not self.isGlobal:
            self.project.dbgAutoContinue = autoContinue
        
    def startBookmark(self, attrs):
        """
        Handler method for the "Bookmark" start tag.
        
        @param attrs list of tag attributes
        """
        self.filename = ""
        self.lineno = 0
        
    def endBookmark(self):
        """
        Handler method for the "Bookmark" end tag.
        """
        editor = self.vm.getOpenEditor(self.filename)
        if editor is not None:
            editor.toggleBookmark(self.lineno)
        
    def startSession(self, attrs):
        """
        Handler method for the "Session" start tag.
        
        @param attrs list of tag attributes
        """
        self.version = attrs.get('version', sessionFileFormatVersion)
        
    def getVersion(self):
        """
        Public method to retrieve the version of the session.
        
        @return String containing the version number.
        """
        return self.version
