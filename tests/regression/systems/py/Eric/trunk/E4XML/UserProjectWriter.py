# -*- coding: utf-8 -*-

# Copyright (c) 2006 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the writer class for writing an XML user project properties file.
"""

import time

from KdeQt.KQApplication import e4App

from XMLWriterBase import XMLWriterBase
from Config import userProjectFileFormatVersion

import Preferences

class UserProjectWriter(XMLWriterBase):
    """
    Class implementing the writer class for writing an XML user project properties  file.
    """
    def __init__(self, file, projectName):
        """
        Constructor
        
        @param file open file (like) object for writing
        @param projectName name of the project (string)
        """
        XMLWriterBase.__init__(self, file)
        
        self.pudata = e4App().getObject("Project").pudata
        self.pdata = e4App().getObject("Project").pdata
        self.name = projectName
        
    def writeXML(self):
        """
        Public method to write the XML to the file.
        """
        XMLWriterBase.writeXML(self)
        
        self._write('<!DOCTYPE UserProject SYSTEM "UserProject-%s.dtd">' % \
            userProjectFileFormatVersion)
        
        # add some generation comments
        self._write("<!-- eric4 user project file for project %s -->" % self.name)
        if Preferences.getProject("XMLTimestamp"):
            self._write("<!-- Saved: %s -->" % time.strftime('%Y-%m-%d, %H:%M:%S'))
            self._write("<!-- Copyright (C) %s %s, %s -->" % \
                    (time.strftime('%Y'), 
                     self.escape(self.pdata["AUTHOR"][0]), 
                     self.escape(self.pdata["EMAIL"][0])))
        
        # add the main tag
        self._write('<UserProject version="%s">' % userProjectFileFormatVersion)
        
        # do the vcs override stuff
        if self.pudata["VCSOVERRIDE"]:
            self._write("  <VcsType>%s</VcsType>" % self.pudata["VCSOVERRIDE"][0])
        if self.pudata["VCSSTATUSMONITORINTERVAL"]:
            self._write('  <VcsStatusMonitorInterval value="%d" />' % \
                self.pudata["VCSSTATUSMONITORINTERVAL"][0])
        
        self._write("</UserProject>", newline = False)
