# -*- coding: utf-8 -*-

# Copyright (c) 2005 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the writer class for writing an XML tasks file.
"""

import os
import time

from KdeQt.KQApplication import e4App

from XMLWriterBase import XMLWriterBase
from Config import tasksFileFormatVersion

import Preferences
import Utilities

class TasksWriter(XMLWriterBase):
    """
    Class implementing the writer class for writing an XML tasks file.
    """
    def __init__(self, file, forProject = False, projectName=""):
        """
        Constructor
        
        @param file open file (like) object for writing
        @param forProject flag indicating project related mode (boolean)
        @param projectName name of the project (string)
        """
        XMLWriterBase.__init__(self, file)
        
        self.name = projectName
        self.forProject = forProject
        
    def writeXML(self):
        """
        Public method to write the XML to the file.
        """
        XMLWriterBase.writeXML(self)
        
        self._write('<!DOCTYPE Tasks SYSTEM "Tasks-%s.dtd">' % tasksFileFormatVersion)
        
        # add some generation comments
        if self.forProject:
            self._write("<!-- eric4 tasks file for project %s -->" % self.name)
            if Preferences.getProject("XMLTimestamp"):
                self._write("<!-- Saved: %s -->" % time.strftime('%Y-%m-%d, %H:%M:%S'))
        else:
            self._write("<!-- eric4 tasks file -->")
            self._write("<!-- Saved: %s -->" % time.strftime('%Y-%m-%d, %H:%M:%S'))
        
        # add the main tag
        self._write('<Tasks version="%s">' % tasksFileFormatVersion)
        
        # do the tasks
        if self.forProject:
            tasks = e4App().getObject("TaskViewer").getProjectTasks()
        else:
            tasks = e4App().getObject("TaskViewer").getGlobalTasks()
        for task in tasks:
            self._write('  <Task priority="%d" completed="%s" bugfix="%s">' % \
                        (task.priority, task.completed, task.isBugfixTask))
            self._write('    <Summary>%s</Summary>' % \
                        self.escape("%s" % task.description.strip()))
            self._write('    <Description>%s</Description>' % \
                        self.escape(self.encodedNewLines(task.longtext.strip())))
            self._write('    <Created>%s</Created>' % \
                        time.strftime("%Y-%m-%d, %H:%M:%S", time.localtime(task.created)))
            if task.filename:
                self._write('    <Resource>')
                self._write('      <Filename>%s</Filename>' % \
                    Utilities.fromNativeSeparators(task.filename))
                self._write('      <Linenumber>%d</Linenumber>' % task.lineno)
                self._write('    </Resource>')
            self._write('  </Task>')
        
        self._write('</Tasks>', newline = False)
