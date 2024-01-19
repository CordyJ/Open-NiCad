# -*- coding: utf-8 -*-

# Copyright (c) 2005 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the writer class for writing an XML project debugger properties file.
"""

import os
import time

from KdeQt.KQApplication import e4App

from XMLWriterBase import XMLWriterBase
from Config import debuggerPropertiesFileFormatVersion

import Preferences

class DebuggerPropertiesWriter(XMLWriterBase):
    """
    Class implementing the writer class for writing an XML project debugger properties
    file.
    """
    def __init__(self, file, projectName):
        """
        Constructor
        
        @param file open file (like) object for writing
        @param projectName name of the project (string)
        """
        XMLWriterBase.__init__(self, file)
        
        self.name = projectName
        self.project = e4App().getObject("Project")
        
    def writeXML(self):
        """
        Public method to write the XML to the file.
        """
        XMLWriterBase.writeXML(self)
        
        self._write('<!DOCTYPE DebuggerProperties SYSTEM "DebuggerProperties-%s.dtd">' % \
            debuggerPropertiesFileFormatVersion)
        
        # add some generation comments
        self._write("<!-- eric4 debugger properties file for project %s -->" % self.name)
        self._write("<!-- This file was generated automatically, do not edit. -->")
        if Preferences.getProject("XMLTimestamp"):
            self._write("<!-- Saved: %s -->" % time.strftime('%Y-%m-%d, %H:%M:%S'))
        
        # add the main tag
        self._write('<DebuggerProperties version="%s">' % \
            debuggerPropertiesFileFormatVersion) 
        
        self._write('  <Interpreter>%s</Interpreter>' % \
            self.project.debugProperties["INTERPRETER"])
        
        self._write('  <DebugClient>%s</DebugClient>' % \
            self.project.debugProperties["DEBUGCLIENT"])
        
        self._write('  <Environment override="%d">%s</Environment>' % \
            (self.project.debugProperties["ENVIRONMENTOVERRIDE"],
             self.escape(self.project.debugProperties["ENVIRONMENTSTRING"])))
        
        self._write('  <RemoteDebugger on="%d">' % \
            self.project.debugProperties["REMOTEDEBUGGER"])
        self._write('    <RemoteHost>%s</RemoteHost>' % \
            self.project.debugProperties["REMOTEHOST"])
        self._write('    <RemoteCommand>%s</RemoteCommand>' % \
            self.escape(self.project.debugProperties["REMOTECOMMAND"]))
        self._write('  </RemoteDebugger>')
        
        self._write('  <PathTranslation on="%d">' % \
            self.project.debugProperties["PATHTRANSLATION"])
        self._write('    <RemotePath>%s</RemotePath>' % \
            self.project.debugProperties["REMOTEPATH"])
        self._write('    <LocalPath>%s</LocalPath>' % \
            self.project.debugProperties["LOCALPATH"])
        self._write('  </PathTranslation>')
        
        self._write('  <ConsoleDebugger on="%d">%s</ConsoleDebugger>' % \
            (self.project.debugProperties["CONSOLEDEBUGGER"],
             self.escape(self.project.debugProperties["CONSOLECOMMAND"])))
        
        self._write('  <Redirect on="%d" />' % \
            self.project.debugProperties["REDIRECT"])
        
        self._write('  <Noencoding on="%d" />' % \
            self.project.debugProperties["NOENCODING"])
        
        self._write("</DebuggerProperties>", newline = False)
