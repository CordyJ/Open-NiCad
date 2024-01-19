# -*- coding: utf-8 -*-

# Copyright (c) 2005 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the writer class for writing an XML templates file.
"""

import os
import time

from XMLWriterBase import XMLWriterBase
from Config import templatesFileFormatVersion

class TemplatesWriter(XMLWriterBase):
    """
    Class implementing the writer class for writing an XML templates file.
    """
    def __init__(self, file, templatesViewer):
        """
        Constructor
        
        @param file open file (like) object for writing
        """
        XMLWriterBase.__init__(self, file)
        
        self.templatesViewer = templatesViewer
        
    def writeXML(self):
        """
        Public method to write the XML to the file.
        """
        XMLWriterBase.writeXML(self)
        
        self._write('<!DOCTYPE Templates SYSTEM "Templates-%s.dtd">' % \
            templatesFileFormatVersion)
        
        # add some generation comments
        self._write("<!-- eric4 templates file -->")
        self._write("<!-- Saved: %s -->" % time.strftime('%Y-%m-%d, %H:%M:%S'))
        
        # add the main tag
        self._write('<Templates version="%s">' % templatesFileFormatVersion)
        
        # do the template groups
        groups = self.templatesViewer.getAllGroups()
        for group in groups:
            self._write('  <TemplateGroup name="%s" language="%s">' % \
                        (group.getName(), group.getLanguage()))
            # do the templates
            templates = group.getAllEntries()
            for template in templates:
                self._write('    <Template name="%s">' % \
                    self.escape(template.getName(), True))
                self._write('      <TemplateDescription>%s</TemplateDescription>' % \
                    self.escape("%s" % template.getDescription()))
                self._write('      <TemplateText>%s</TemplateText>' % \
                    self.escape("%s" % template.getTemplateText()))
                self._write('    </Template>')
            self._write('  </TemplateGroup>')
        
        self._write('</Templates>', newline = False)
