# -*- coding: utf-8 -*-

# Copyright (c) 2004 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the writer class for writing an XML shortcuts file.
"""

import time

from PyQt4.QtCore import QString

from KdeQt.KQApplication import e4App

from XMLWriterBase import XMLWriterBase
from Config import shortcutsFileFormatVersion

import Preferences

class ShortcutsWriter(XMLWriterBase):
    """
    Class implementing the writer class for writing an XML shortcuts file.
    """
    def __init__(self, file):
        """
        Constructor
        
        @param file open file (like) object for writing
        """
        XMLWriterBase.__init__(self, file)
        
        self.email = Preferences.getUser("Email")
        
    def writeXML(self):
        """
        Public method to write the XML to the file.
        """
        XMLWriterBase.writeXML(self)
        
        self._write('<!DOCTYPE Shortcuts SYSTEM "Shortcuts-%s.dtd">' % \
            shortcutsFileFormatVersion)
        
        # add some generation comments
        self._write("<!-- Eric4 keyboard shortcuts -->")
        self._write("<!-- Saved: %s -->" % time.strftime('%Y-%m-%d, %H:%M:%S'))
        self._write("<!-- Author: %s -->" % self.escape("%s" % self.email))
        
        # add the main tag
        self._write('<Shortcuts version="%s">' % shortcutsFileFormatVersion)
        
        for act in e4App().getObject("Project").getActions():
            self._write('  <Shortcut category="Project">')
            self._write('    <Name>%s</Name>' % act.objectName())
            self._write('    <Accel>%s</Accel>' % \
                self.escape("%s" % QString(act.shortcut())))
            self._write('    <AltAccel>%s</AltAccel>' \
                % self.escape("%s" % QString(act.alternateShortcut())))
            self._write('  </Shortcut>')
        
        for act in e4App().getObject("UserInterface").getActions('ui'):
            self._write('  <Shortcut category="General">')
            self._write('    <Name>%s</Name>' % act.objectName())
            self._write('    <Accel>%s</Accel>' % \
                self.escape("%s" % QString(act.shortcut())))
            self._write('    <AltAccel>%s</AltAccel>' % \
                self.escape("%s" % QString(act.alternateShortcut())))
            self._write('  </Shortcut>')
        
        for act in e4App().getObject("UserInterface").getActions('wizards'):
            self._write('  <Shortcut category="Wizards">')
            self._write('    <Name>%s</Name>' % act.objectName())
            self._write('    <Accel>%s</Accel>' % \
                self.escape("%s" % QString(act.shortcut())))
            self._write('    <AltAccel>%s</AltAccel>' % \
                self.escape("%s" % QString(act.alternateShortcut())))
            self._write('  </Shortcut>')
        
        for act in e4App().getObject("DebugUI").getActions():
            self._write('  <Shortcut category="Debug">')
            self._write('    <Name>%s</Name>' % act.objectName())
            self._write('    <Accel>%s</Accel>' % \
                self.escape("%s" % QString(act.shortcut())))
            self._write('    <AltAccel>%s</AltAccel>' % \
                self.escape("%s" % QString(act.alternateShortcut())))
            self._write('  </Shortcut>')
        
        for act in e4App().getObject("ViewManager").getActions('edit'):
            self._write('  <Shortcut category="Edit">')
            self._write('    <Name>%s</Name>' % act.objectName())
            self._write('    <Accel>%s</Accel>' % \
                self.escape("%s" % QString(act.shortcut())))
            self._write('    <AltAccel>%s</AltAccel>' % \
                self.escape("%s" % QString(act.alternateShortcut())))
            self._write('  </Shortcut>')
        
        for act in e4App().getObject("ViewManager").getActions('file'):
            self._write('  <Shortcut category="File">')
            self._write('    <Name>%s</Name>' % act.objectName())
            self._write('    <Accel>%s</Accel>' % \
                self.escape("%s" % QString(act.shortcut())))
            self._write('    <AltAccel>%s</AltAccel>' % \
                self.escape("%s" % QString(act.alternateShortcut())))
            self._write('  </Shortcut>')
        
        for act in e4App().getObject("ViewManager").getActions('search'):
            self._write('  <Shortcut category="Search">')
            self._write('    <Name>%s</Name>' % act.objectName())
            self._write('    <Accel>%s</Accel>' % \
                self.escape("%s" % QString(act.shortcut())))
            self._write('    <AltAccel>%s</AltAccel>' % \
                self.escape("%s" % QString(act.alternateShortcut())))
            self._write('  </Shortcut>')
        
        for act in e4App().getObject("ViewManager").getActions('view'):
            self._write('  <Shortcut category="View">')
            self._write('    <Name>%s</Name>' % act.objectName())
            self._write('    <Accel>%s</Accel>' % \
                self.escape("%s" % QString(act.shortcut())))
            self._write('    <AltAccel>%s</AltAccel>' % \
                self.escape("%s" % QString(act.alternateShortcut())))
            self._write('  </Shortcut>')
        
        for act in e4App().getObject("ViewManager").getActions('macro'):
            self._write('  <Shortcut category="Macro">')
            self._write('    <Name>%s</Name>' % act.objectName())
            self._write('    <Accel>%s</Accel>' % \
                self.escape("%s" % QString(act.shortcut())))
            self._write('    <AltAccel>%s</AltAccel>' % \
                self.escape("%s" % QString(act.alternateShortcut())))
            self._write('  </Shortcut>')
        
        for act in e4App().getObject("ViewManager").getActions('bookmark'):
            self._write('  <Shortcut category="Bookmarks">')
            self._write('    <Name>%s</Name>' % act.objectName())
            self._write('    <Accel>%s</Accel>' % \
                self.escape("%s" % QString(act.shortcut())))
            self._write('    <AltAccel>%s</AltAccel>' % \
                self.escape("%s" % QString(act.alternateShortcut())))
            self._write('  </Shortcut>')
        
        for act in e4App().getObject("ViewManager").getActions('spelling'):
            self._write('  <Shortcut category="Spelling">')
            self._write('    <Name>%s</Name>' % act.objectName())
            self._write('    <Accel>%s</Accel>' % \
                self.escape("%s" % QString(act.shortcut())))
            self._write('    <AltAccel>%s</AltAccel>' % \
                self.escape("%s" % QString(act.alternateShortcut())))
            self._write('  </Shortcut>')
        
        actions = e4App().getObject("ViewManager").getActions('window')
        for act in actions:
            self._write('  <Shortcut category="Window">')
            self._write('    <Name>%s</Name>' % act.objectName())
            self._write('    <Accel>%s</Accel>' % \
                self.escape("%s" % QString(act.shortcut())))
            self._write('    <AltAccel>%s</AltAccel>' % \
                self.escape("%s" % QString(act.alternateShortcut())))
            self._write('  </Shortcut>')
        
        for category, ref in e4App().getPluginObjects():
            if hasattr(ref, "getActions"):
                actions = ref.getActions()
                for act in actions:
                    if not act.objectName().isEmpty():
                        # shortcuts are only exported, if their objectName is set
                        self._write('  <Shortcut category="%s">' % category)
                        self._write('    <Name>%s</Name>' % act.objectName())
                        self._write('    <Accel>%s</Accel>' % \
                            self.escape("%s" % QString(act.shortcut())))
                        self._write('    <AltAccel>%s</AltAccel>' % \
                            self.escape("%s" % QString(act.alternateShortcut())))
                        self._write('  </Shortcut>')
    
        for act in e4App().getObject("DummyHelpViewer").getActions():
            self._write('  <Shortcut category="HelpViewer">')
            self._write('    <Name>%s</Name>' % act.objectName())
            self._write('    <Accel>%s</Accel>' % \
                self.escape("%s" % QString(act.shortcut())))
            self._write('    <AltAccel>%s</AltAccel>' \
                % self.escape("%s" % QString(act.alternateShortcut())))
            self._write('  </Shortcut>')
    
        # add the main end tag
        self._write("</Shortcuts>", newline = False)
