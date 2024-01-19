#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2009 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Eric4 SQL Browser

This is the main Python script that performs the necessary initialization
of the SQL browser and starts the Qt event loop.
"""

import sys, os
import os

# disable the usage of KDE widgets, if requested
sys.e4nokde = False
if "--nokde" in sys.argv:
    del sys.argv[sys.argv.index("--nokde")]
    sys.e4nokde = True
else:
    sys.e4nokde = os.getenv("e4nokde") is not None and os.getenv("e4nokde") == "1"

for arg in sys.argv:
    if arg.startswith("--config="):
        import Utilities
        configDir = arg.replace("--config=", "")
        Utilities.setConfigDir(configDir)
        sys.argv.remove(arg)
        break

from Utilities import Startup

def createMainWidget(argv):
    """
    Function to create the main widget.
    
    @param argv list of commandline parameters (list of strings)
    @return reference to the main widget (QWidget)
    """
    from SqlBrowser.SqlBrowser import SqlBrowser
    
    if len(argv) > 1:
        connections = argv[1:]
    else:
        connections = []
    
    browser = SqlBrowser(connections)
    return browser

def main():
    """
    Main entry point into the application.
    """
    options = [\
        ("--config=configDir", 
         "use the given directory as the one containing the config files"), 
        ("--nokde" , "don't use KDE widgets"),
    ]
    kqOptions = [\
        ("config \\", "use the given directory as the one containing the config files"), 
        ("nokde" , "don't use KDE widgets"),
        ("!+connection", "")
    ]
    appinfo = Startup.makeAppInfo(sys.argv,
                                  "Eric4 SQL Browser",
                                  "connection",
                                  "SQL browser",
                                  options)
    res = Startup.simpleAppStartup(sys.argv,
                                   appinfo,
                                   createMainWidget,
                                   kqOptions)
    sys.exit(res)

if __name__ == '__main__':
    main()
