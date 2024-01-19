# -*- coding: utf-8 -*-

# Copyright (c) 2003 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the handler class for reading an XML project debugger properties file.
"""

from Config import debuggerPropertiesFileFormatVersion
from XMLHandlerBase import XMLHandlerBase

class DebuggerPropertiesHandler(XMLHandlerBase):
    """
    Class implementing a sax handler to read an XML project debugger properties file.
    """
    def __init__(self, project):
        """
        Constructor
        
        @param project Reference to the project object to store the
                information into.
        """
        XMLHandlerBase.__init__(self)
        
        self.startDocumentSpecific = self.startDocumentDebuggerProperties
        
        self.elements.update({
            'DebuggerProperties' : (self.startDebuggerProperties, self.defaultEndElement),
            'Interpreter' : (self.defaultStartElement, self.endInterpreter),
            'DebugClient' : (self.defaultStartElement, self.endDebugClient),
            'Environment' : (self.startEnvironment, self.endEnvironment),
            'RemoteDebugger' : (self.startRemoteDebugger, self.defaultEndElement),
            'RemoteHost' : (self.defaultStartElement, self.endRemoteHost),
            'RemoteCommand' : (self.defaultStartElement, self.endRemoteCommand),
            'PathTranslation' : (self.startPathTranslation, self.defaultEndElement),
            'RemotePath' : (self.defaultStartElement, self.endRemotePath),
            'LocalPath' : (self.defaultStartElement, self.endLocalPath),
            'ConsoleDebugger' : (self.startConsoleDebugger, self.endConsoleDebugger),
            'Redirect' : (self.startRedirect, self.defaultEndElement),
            'Noencoding' : (self.startNoencoding, self.defaultEndElement),
        })
    
        self.project = project
        
    def startDocumentDebuggerProperties(self):
        """
        Handler called, when the document parsing is started.
        """
        self.version = ''
        
    ###################################################
    ## below follow the individual handler functions
    ###################################################
    
    def endInterpreter(self):
        """
        Handler method for the "Interpreter" end tag.
        """
        self.project.debugProperties["INTERPRETER"] = \
            self.utf8_to_code(self.buffer)
        
    def endDebugClient(self):
        """
        Handler method for the "DebugClient" end tag.
        """
        self.project.debugProperties["DEBUGCLIENT"] = \
            self.utf8_to_code(self.buffer)
        
    def startEnvironment(self, attrs):
        """
        Handler method for the "Environment" start tag.
        """
        self.buffer = ""
        self.project.debugProperties["ENVIRONMENTOVERRIDE"] = \
            int(attrs.get("override", "0"))
        
    def endEnvironment(self):
        """
        Handler method for the "Environment" end tag.
        """
        self.project.debugProperties["ENVIRONMENTSTRING"] = \
            self.unescape(self.utf8_to_code(self.buffer))
        
    def startRemoteDebugger(self, attrs):
        """
        Handler method for the "RemoteDebugger" start tag.
        """
        self.buffer = ""
        self.project.debugProperties["REMOTEDEBUGGER"] = \
            int(attrs.get("on", "0"))
        
    def endRemoteHost(self):
        """
        Handler method for the "RemoteHost" end tag.
        """
        self.project.debugProperties["REMOTEHOST"] = \
            self.utf8_to_code(self.buffer)
        
    def endRemoteCommand(self):
        """
        Handler method for the "RemoteCommand" end tag.
        """
        self.project.debugProperties["REMOTECOMMAND"] = \
            self.unescape(self.utf8_to_code(self.buffer))
        
    def startPathTranslation(self, attrs):
        """
        Handler method for the "PathTranslation" start tag.
        """
        self.buffer = ""
        self.project.debugProperties["PATHTRANSLATION"] = \
            int(attrs.get("on", "0"))
        
    def endRemotePath(self):
        """
        Handler method for the "RemotePath" end tag.
        """
        self.project.debugProperties["REMOTEPATH"] = \
            self.utf8_to_code(self.buffer)
        
    def endLocalPath(self):
        """
        Handler method for the "LocalPath" end tag.
        """
        self.project.debugProperties["LOCALPATH"] = \
            self.utf8_to_code(self.buffer)
        
    def startConsoleDebugger(self, attrs):
        """
        Handler method for the "ConsoleDebugger" start tag.
        """
        self.buffer = ""
        self.project.debugProperties["CONSOLEDEBUGGER"] = \
            int(attrs.get("on", "0"))
        
    def endConsoleDebugger(self):
        """
        Handler method for the "ConsoleDebugger" end tag.
        """
        self.project.debugProperties["CONSOLECOMMAND"] = \
            self.unescape(self.utf8_to_code(self.buffer))
        
    def startRedirect(self, attrs):
        """
        Handler method for the "Redirect" start tag.
        """
        self.project.debugProperties["REDIRECT"] = \
            int(attrs.get("on", "1"))
        
    def startNoencoding(self, attrs):
        """
        Handler method for the "Noencoding" start tag.
        """
        self.project.debugProperties["NOENCODING"] = \
            int(attrs.get("on", "0"))
        
    def startDebuggerProperties(self, attrs):
        """
        Handler method for the "DebuggerProperties" start tag.
        
        @param attrs list of tag attributes
        """
        self.version = attrs.get('version', debuggerPropertiesFileFormatVersion)
        
    def getVersion(self):
        """
        Public method to retrieve the version of the debugger properties.
        
        @return String containing the version number.
        """
        return self.version
