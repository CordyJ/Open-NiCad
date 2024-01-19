# -*- coding: utf-8 -*-

# Copyright (c) 2006 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module defining common data to be used by all modules.
"""

import sys

# names of the various settings objects
settingsNameOrganization = "Eric4"
settingsNameGlobal = "eric4"
settingsNameRecent = "eric4recent"

# key names of the various recent entries
recentNameMultiProject = "MultiProjects"
recentNameProject = "Projects"
recentNameFiles = "Files"

def isWindowsPlatform():
    """
    Function to check, if this is a Windows platform.
    
    @return flag indicating Windows platform (boolean)
    """
    return sys.platform.startswith("win")
