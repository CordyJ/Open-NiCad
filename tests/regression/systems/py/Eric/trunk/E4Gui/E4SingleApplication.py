# -*- coding: utf-8 -*-

# Copyright (c) 2004 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the single application server and client.
"""

import sys
import os

from KdeQt.KQApplication import e4App

from Utilities.SingleApplication import SingleApplicationClient, SingleApplicationServer

import Utilities

###########################################################################
# define some module global stuff
###########################################################################

SAFile = "eric4.lck"

# define the protocol tokens
SAOpenFile =        '>OpenFile<'
SAOpenProject =     '>OpenProject<'
SAArguments =       '>Arguments<'

class E4SingleApplicationServer(SingleApplicationServer):
    """
    Class implementing the single application server embedded within the IDE.
    """
    def __init__(self):
        """
        Constructor
        """
        SingleApplicationServer.__init__(self, SAFile)

    def handleCommand(self, cmd, params):
        """
        Public slot to handle the command sent by the client.
        
        @param cmd commandstring (string)
        @param params parameterstring (string)
        """
        if cmd == SAOpenFile:
            self.__saOpenFile(params)
            return

        if cmd == SAOpenProject:
            self.__saOpenProject(params)
            return

        if cmd == SAArguments:
            self.__saArguments(params)
            return

    def __saOpenFile(self, fname):
        """
        Private method used to handle the "Open File" command.
        
        @param fname filename to be opened (string)
        """
        e4App().getObject("ViewManager").openSourceFile(fname)
        
    def __saOpenProject(self, pfname):
        """
        Private method used to handle the "Open Project" command.
        
        @param pfname filename of the project to be opened (string)
        """
        e4App().getObject("Project").openProject(pfname)
        
    def __saArguments(self, argsStr):
        """
        Private method used to handle the "Arguments" command.
        
        @param argsStr space delimited list of command args(string)
        """
        e4App().getObject("DebugUI").setArgvHistory(argsStr)

class E4SingleApplicationClient(SingleApplicationClient):
    """
    Class implementing the single application client of the IDE.
    """
    def __init__(self):
        """
        Constructor
        """
        SingleApplicationClient.__init__(self, SAFile)
        
    def processArgs(self, args):
        """
        Public method to process the command line args passed to the UI.
        
        @param args list of files to open
        """
        # no args, return
        if args is None:
            return
        
        # holds space delimited list of command args, if any
        argsStr = None
        # flag indicating '--' options was found
        ddseen = False
        
        if Utilities.isWindowsPlatform():
            argChars = ['-', '/']
        else:
            argChars = ['-']
        
        for arg in args:
            if arg == '--' and not ddseen:
                ddseen = True
                continue
                
            if arg[0] in argChars or ddseen:
                if argsStr is None:
                    argsStr = arg
                else:
                    argsStr = "%s %s" % (argsStr, arg)
                continue
            
            ext = os.path.splitext(arg)[1]
            ext = os.path.normcase(ext)
            
            if ext in ['.e3p', '.e3pz', '.e4p', '.e4pz']:
                self.__openProject(arg)
            else:
                self.__openFile(arg)
        
        # send any args we had
        if argsStr is not None:
            self.__sendArguments(argsStr)
        
        self.disconnect()
        
    def __openFile(self, fname):
        """
        Private method to open a file in the application server.
        
        @param fname name of file to be opened (string)
        """
        cmd = "%s%s\n" % (SAOpenFile, Utilities.normabspath(fname))
        self.sendCommand(cmd)
        
    def __openProject(self, pfname):
        """
        Private method to open a project in the application server.
        
        @param pfname name of the projectfile to be opened (string)
        """
        cmd = "%s%s\n" % (SAOpenProject, Utilities.normabspath(pfname))
        self.sendCommand(cmd)
        
    def __sendArguments(self, argsStr):
        """
        Private method to set the command arguments in the application server.
        
        @param argsStr space delimited list of command args (string)
        """
        cmd = "%s%s\n" % (SAArguments, argsStr)
        self.sendCommand(cmd)