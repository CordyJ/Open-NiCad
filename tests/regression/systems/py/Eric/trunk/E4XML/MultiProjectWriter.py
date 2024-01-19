# -*- coding: utf-8 -*-

# Copyright (c) 2008 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the writer class for writing an XML multi project file.
"""

import os
import time

from KdeQt.KQApplication import e4App

from XMLWriterBase import XMLWriterBase
from Config import multiProjectFileFormatVersion

import Preferences
import Utilities

class MultiProjectWriter(XMLWriterBase):
    """
    Class implementing the writer class for writing an XML project file.
    """
    def __init__(self, multiProject, file, multiProjectName):
        """
        Constructor
        
        @param multiProject Reference to the multi project object
        @param file open file (like) object for writing
        @param projectName name of the project (string)
        """
        XMLWriterBase.__init__(self, file)
        
        self.name = multiProjectName
        self.multiProject = multiProject
    
    def writeXML(self):
        """
        Public method to write the XML to the file.
        """
        XMLWriterBase.writeXML(self)
        
        self._write('<!DOCTYPE MultiProject SYSTEM "MultiProject-%s.dtd">' % \
            multiProjectFileFormatVersion)
        
        # add some generation comments
        self._write("<!-- eric4 multi project file for multi project %s -->" % self.name)
        if Preferences.getMultiProject("XMLTimestamp"):
            self._write("<!-- Saved: %s -->" % time.strftime('%Y-%m-%d, %H:%M:%S'))
            self._write("<!-- Copyright (C) %s -->" % time.strftime('%Y'))
        
        # add the main tag
        self._write('<MultiProject version="%s">' % multiProjectFileFormatVersion)
        
        # do description
        self._write("  <Description>%s</Description>" % \
            self.escape(self.encodedNewLines(self.multiProject.description)))
        
        # do the projects
        self._write("  <Projects>")
        for project in self.multiProject.getProjects():
            self._write('    <Project isMaster="%s">' % project['master'])
            self._write("      <ProjectName>%s</ProjectName>" % \
                self.escape(project['name']))
            self._write("      <ProjectFile>%s</ProjectFile>" % \
                Utilities.fromNativeSeparators(project['file']))
            self._write("      <ProjectDescription>%s</ProjectDescription>" % \
                self.escape(self.encodedNewLines(project['name'])))
            self._write("    </Project>")
        self._write("  </Projects>")
        
        self._write("</MultiProject>", newline = False)
