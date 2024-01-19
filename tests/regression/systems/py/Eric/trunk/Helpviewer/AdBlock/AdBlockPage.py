# -*- coding: utf-8 -*-

# Copyright (c) 2009 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a class to apply AdBlock rules to a web page.
"""

from PyQt4.QtCore import *

import Helpviewer.HelpWindow

class AdBlockPage(QObject):
    """
    Class to apply AdBlock rules to a web page.
    """
    def __checkRule(self, rule, page, host):
        """
        Private method to check, if a rule applies to the given web page and host.
        
        @param rule reference to the rule to check (AdBlockRule)
        @param page reference to the web page (QWebPage)
        @param host host name (string or QString)
        """
        # This is a noop until Qt 4.6 is supported by PyQt4
        return
    
    def applyRulesToPage(self, page):
        """
        Public method to applay AdBlock rules to a web page.
        
        @param page reference to the web page (QWebPage)
        """
        # This is a noop until Qt 4.6 is supported by PyQt4
        return
