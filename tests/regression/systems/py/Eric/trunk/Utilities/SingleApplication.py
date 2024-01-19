# -*- coding: utf-8 -*-

# Copyright (c) 2004 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the single application server and client.
"""

import os
import socket

from PyQt4.QtCore import SIGNAL, QString
from PyQt4.QtNetwork import QTcpServer, QTcpSocket, QHostAddress

import Utilities

###########################################################################
# define some module global stuff
###########################################################################

SAAddress = "127.0.0.1"     # the address to be used

# define the lock file tokens
SALckSocket =       'Socket'
SALckPID =          'PID'

class SingleApplicationServer(QTcpServer):
    """
    Class implementing the single application server base class.
    """
    def __init__(self, pidFile):
        """
        Constructor
        
        @param pidFile filename of the PID file used to record some interface
            informations
        """
        addr = QHostAddress()
        addr.setAddress(SAAddress)
        QTcpServer.__init__(self)
        
        self.saFile = os.path.join(Utilities.getConfigDir(), pidFile)
        if self.listen(addr, 0):
            try:
                f = open(self.saFile, "wb")
                
                try:
                    f.write("%s = %d%s" % \
                        (SALckPID, os.getpid(), os.linesep))
                except AttributeError:
                    pass
                
                f.write("%s = %d%s" % \
                    (SALckSocket, self.serverPort(), os.linesep))
                
                f.close()
            except IOError, msg:
                print "Error writing Lockfile: %s\n" % msg
            self.connect(self, SIGNAL("newConnection()"), self.__newConnection)

        self.qsock = None

    def __newConnection(self):
        """
        Private slot to handle a new connection.
        """
        sock = self.nextPendingConnection()

        # If we already have a connection, refuse this one.  It will be closed
        # automatically.
        if self.qsock is not None:
            return

        self.qsock = sock

        self.connect(self.qsock, SIGNAL('readyRead()'), self.__parseLine)
        self.connect(self.qsock, SIGNAL('disconnected()'), self.__disconnected)

    def __parseLine(self):
        """
        Private method to handle data from the client.
        """
        while self.qsock and self.qsock.canReadLine():
            line = unicode(self.qsock.readLine())
            
##            print line          ##debug
            
            eoc = line.find('<') + 1
            
            boc = line.find('>')
            if boc >= 0 and eoc > boc:
                # handle the command sent by the client.
                cmd = line[boc:eoc]
                params = line[eoc:-1]
                
                self.handleCommand(cmd, params)
    
    def __disconnected(self):
        """
        Private method to handle the closure of the socket.
        """
        self.qsock = None
    
    def shutdown(self):
        """
        Public method used to shut down the server.
        """
        try:
            os.remove(self.saFile)
        except EnvironmentError:
            pass
            
        if self.qsock is not None:
            self.disconnect(self.qsock, SIGNAL('readyRead()'), self.__parseLine)
            self.disconnect(self.qsock, SIGNAL('disconnected()'), self.__disconnected)
        
        self.qsock = None

    def handleCommand(self, cmd, params):
        """
        Public slot to handle the command sent by the client.
        
        <b>Note</b>: This method must be overridden by subclasses.
        
        @param cmd commandstring (string)
        @param params parameterstring (string)
        """
        raise RuntimeError("'handleCommand' must be overridden")

class SingleApplicationClient(object):
    """
    Class implementing the single application client base class.
    """
    def __init__(self, pidFile):
        """
        Constructor
        
        @param pidFile filename of the PID file used to get some interface
            informations
        """
        self.pidFile = pidFile
        self.connected = False
        self.errno = 0
        
    def connect(self):
        """
        Public method to connect the single application client to its server.
        
        @return value indicating success or an error number. Value is one of:
            <table>
                <tr><td>0</td><td>No application is running</td></tr>
                <tr><td>1</td><td>Application is already running</td></tr>
                <tr><td>-1</td><td>The lock file could not be read</td></tr>
                <tr><td>-2</td><td>The lock file is corrupt</td></tr>
            </table>
        """
        saFile = os.path.join(Utilities.getConfigDir(), self.pidFile)
        
        if not os.path.exists(saFile):
            return 0
            
        try:
            f = open(saFile, 'rb')
            lines = f.readlines()
            f.close()
        except IOError:
            self.errno = -1
            return -1
            
        for line in lines:
            key, value = line.split(' = ')
            if key == SALckSocket:
                port = int(value.strip())
                break
        else:
            self.errno = -2
            return -2

        self.sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        try:
            self.sock.connect((SAAddress,port))
        except socket.error:
            # if we cannot connect, we assume, that the port was
            # read from a stall lock file and is no longer valid
            return 0
        self.sock.setblocking(0)
        self.connected = True
        return 1
        
    def disconnect(self):
        """
        Public method to disconnect from the Single Appliocation server.
        """
        self.sock.close()
        self.connected = False
    
    def processArgs(self, args):
        """
        Public method to process the command line args passed to the UI.
        
        <b>Note</b>: This method must be overridden by subclasses.
        
        @param args command line args (list of strings)
        """
        raise RuntimeError("'processArgs' must be overridden")
    
    def sendCommand(self, cmd):
        """
        Public method to send the command to the application server.
        
        @param cmd command to be sent (string)
        """
        if self.connected:
            self.sock.send(cmd)
        
    def errstr(self):
        """
        Public method to return a meaningful error string for the last error.
        
        @return error string for the last error (string)
        """
        if self.errno == -1:
            s = "Error reading lock file."
        elif self.errno == -2:
            s = "Lock file does not contain a socket line."
        return s
