# -*- coding: utf-8 -*-

# Copyright (c) 2004 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing an error handler class.
"""

from xml.sax.handler import ErrorHandler
from xml.sax import SAXParseException

from XMLMessageDialog import XMLMessageDialog

class XMLParseError(Exception):
    """
    Class implementing an exception for recoverable parse errors.
    """
    pass
    
class XMLFatalParseError(XMLParseError):
    """
    Class implementing an exception for recoverable parse errors.
    """
    pass

class XMLErrorHandler(ErrorHandler):
    """
    Class implementing an error handler class.
    """
    def __init__(self):
        """
        Constructor
        """
        self.errors = 0
        self.fatals = 0
        self.warnings = 0
        self.totals = 0
        
        # list of tuples of (message type, system id, line number,
        # column number, message)
        self.msgs = []
        
    def error(self, exception):
        """
        Public method to handle a recoverable error.
        
        @param exception Exception object describing the error (SAXParseException)
        """
        self.errors += 1
        self.totals += 1
        self.msgs.append((\
            "E",
            exception.getSystemId(),
            exception.getLineNumber(),
            exception.getColumnNumber(),
            exception.getMessage()
        ))

    def fatalError(self, exception):
        """
        Public method to handle a non-recoverable error.
        
        @param exception Exception object describing the error (SAXParseException)
        @exception XMLFatalParseError a fatal parse error has occured
        """
        self.fatals += 1
        self.totals += 1
        self.msgs.append((\
            "F",
            exception.getSystemId(),
            exception.getLineNumber(),
            exception.getColumnNumber(),
            exception.getMessage()
        ))
        raise XMLFatalParseError

    def warning(self, exception):
        """
        Public method to handle a warning.
        
        @param exception Exception object describing the error (SAXParseException)
        """
        self.warnings += 1
        self.totals += 1
        self.msgs.append((\
            "W",
            exception.getSystemId(),
            exception.getLineNumber(),
            exception.getColumnNumber(),
            exception.getMessage()
        ))

    def getParseMessages(self):
        """
        Public method to retrieve all messages.
        
        @return list of tuples of (message type, system id, line no, column no,
            message)
        """
        return self.msgs
        
    def showParseMessages(self):
        """
        Public method to show the parse messages (if any) in a dialog.
        """
        if self.totals:
            dlg = XMLMessageDialog(self.msgs, None)
            dlg.exec_()
