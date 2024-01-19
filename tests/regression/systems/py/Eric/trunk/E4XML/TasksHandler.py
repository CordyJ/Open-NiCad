# -*- coding: utf-8 -*-

# Copyright (c) 2005 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the handler class for reading an XML tasks file.
"""

import os
import time

from KdeQt.KQApplication import e4App

from Config import tasksFileFormatVersion
from XMLHandlerBase import XMLHandlerBase

import Utilities

class TasksHandler(XMLHandlerBase):
    """
    Class implementing a sax handler to read an XML tasks file.
    """
    def __init__(self, forProject = False, taskViewer=None):
        """
        Constructor
        
        @param forProject flag indicating project related mode (boolean)
        @param taskViewer reference to the task viewer object
        """
        XMLHandlerBase.__init__(self)
        
        self.startDocumentSpecific = self.startDocumentTasks
        
        self.elements.update({
            'Tasks' : (self.startTasks, self.defaultEndElement),
            'Summary' : (self.defaultStartElement, self.endSummary),
            'Description' : (self.defaultStartElement, self.endDescription),
            'Created' : (self.defaultStartElement, self.endCreated),
            'Dir' : (self.defaultStartElement, self.endDir),
            'Name' : (self.defaultStartElement, self.endName),
            'Filename' : (self.startFilename, self.endFilename),
            'Linenumber' : (self.defaultStartElement, self.endLinenumber),
            'Task' : (self.startTask, self.endTask),
        })
    
        self.forProject = forProject
        if taskViewer:
            self.taskViewer = taskViewer
        else:
            self.taskViewer = e4App().getObject("TaskViewer")
        
    def startDocumentTasks(self):
        """
        Handler called, when the document parsing is started.
        """
        self.version = ''
        self.pathStack = []
        
    ###################################################
    ## below follow the individual handler functions
    ###################################################
    
    def startTask(self, attrs):
        """
        Handler method for the "Task" start tag.
        
        @param attrs list of tag attributes
        """
        self.task = {"summary"     : "",
                     "priority"    : 1,
                     "completed"   : False,
                     "created"     : 0,
                     "filename"    : "",
                     "linenumber"  : 0,
                     "bugfix"      : False,
                     "description" : "",
                    }
        self.task["priority"] = int(attrs.get("priority", "1"))
        
        val = attrs.get("completed", "False")
        if val in ["True", "False"]:
            val = (val == "True")
        else:
            val = bool(int(val))
        self.task["completed"] = val
        
        val = attrs.get("bugfix", "False")
        if val in ["True", "False"]:
            val = (val == "True")
        else:
            val = bool(int(val))
        self.task["bugfix"] = val
    
    def endTask(self):
        """
        Handler method for the "Task" end tag.
        """
        self.taskViewer.addTask(self.task["summary"], priority = self.task["priority"],
            filename = self.task["filename"], lineno = self.task["linenumber"], 
            completed = self.task["completed"],
            _time = self.task["created"], isProjectTask = self.forProject,
            isBugfixTask = self.task["bugfix"], longtext = self.task["description"])
        
    def endSummary(self):
        """
        Handler method for the "Summary" end tag.
        """
        self.task["summary"] = self.unescape(self.utf8_to_code(self.buffer))
        
    def endDescription(self):
        """
        Handler method for the "Description" end tag.
        """
        if self.version < '4.1':
            self.task["summary"] = self.unescape(self.utf8_to_code(self.buffer))
        elif self.version == '4.1':
            self.task["description"] = self.unescape(self.utf8_to_code(self.buffer))
        else:
            self.buffer = self.unescape(self.utf8_to_code(self.buffer))
            self.task["description"] = self.decodedNewLines(self.buffer)
        
    def endCreated(self):
        """
        Handler method for the "Created" end tag.
        """
        self.buffer = self.utf8_to_code(self.buffer)
        self.task["created"] = \
            time.mktime(time.strptime(self.buffer, "%Y-%m-%d, %H:%M:%S"))
    
    def endDir(self):
        """
        Handler method for the "Dir" end tag.
        """
        self.buffer = self.utf8_to_code(self.buffer)
        self.pathStack.append(self.buffer)
        
    def endName(self):
        """
        Handler method for the "Name" end tag.
        """
        self.buffer = self.utf8_to_code(self.buffer)
        self.pathStack.append(self.buffer)
        
    def endLinenumber(self):
        """
        Handler method for the "Linenumber" end tag.
        """
        try:
            self.task["linenumber"] = int(self.buffer)
        except ValueError:
            pass
    
    def startFilename(self, attrs):
        """
        Handler method for the "Filename" start tag.
        
        @param attrs list of tag attributes
        """
        self.pathStack = []
        self.buffer = ""
        
    def endFilename(self):
        """
        Handler method for the "Filename" end tag.
        """
        if self.version >= '4.2':
            self.task["filename"] = \
                unicode(Utilities.toNativeSeparators(self.utf8_to_code(self.buffer)))
        else:
            self.task["filename"] = self.__buildPath()
        
    def __buildPath(self):
        """
        Private method to assemble a path.
        
        @return The ready assembled path. (string)
        """
        path = ""
        if self.pathStack and not self.pathStack[0]:
            self.pathStack[0] = os.sep
        for p in self.pathStack:
            path = os.path.join(path, p)
        return path
        
    def startTasks(self, attrs):
        """
        Handler method for the "Tasks" start tag.
        
        @param attrs list of tag attributes
        """
        self.version = attrs.get('version', tasksFileFormatVersion)
        
    def getVersion(self):
        """
        Public method to retrieve the version of the tasks file.
        
        @return String containing the version number.
        """
        return self.version
