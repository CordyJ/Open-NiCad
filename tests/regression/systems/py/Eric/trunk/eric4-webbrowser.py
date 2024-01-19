#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2002 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Eric4 Web Browser

This is the main Python script that performs the necessary initialization
of the web browser and starts the Qt event loop. This is a standalone version
of the integrated helpviewer.
"""

import sys
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

# make ThirdParty package available as a packages repository
try:
    import pygments
except ImportError:
    sys.path.insert(2, os.path.join(os.path.dirname(__file__), "ThirdParty", "Pygments"))

from Utilities import Startup
import Utilities

def createMainWidget(argv):
    """
    Function to create the main widget.
    
    @param argv list of commandline parameters (list of strings)
    @return reference to the main widget (QWidget)
    """
    from Helpviewer.HelpWindow import HelpWindow
    
    searchWord = None
    for arg in reversed(argv):
        if arg.startswith("--search="):
            searchWord = argv[1].split("=", 1)[1]
            argv.remove(arg)
        elif arg.startswith("--"):
            argv.remove(arg)
    
    try:
        home = argv[1]
    except IndexError:
        home = ""
    
    help = HelpWindow(home, '.', None, 'help viewer', searchWord = searchWord)
    return help

def main():
    """
    Main entry point into the application.
    """
    options = [\
        ("--config=configDir", 
         "use the given directory as the one containing the config files"), 
        ("--nokde" , "don't use KDE widgets"),
        ("--search=word", "search for the given word")
    ]
    kqOptions = [\
        ("config \\", "use the given directory as the one containing the config files"), 
        ("search \\", "search for the given word)"), 
        ("!+file", "")
    ]
    appinfo = Startup.makeAppInfo(sys.argv,
                                  "Eric4 web browser",
                                  "file",
                                  "web browser",
                                  options)
    res = Startup.simpleAppStartup(sys.argv,
                                   appinfo,
                                   createMainWidget,
                                   kqOptions)
    sys.exit(res)

if __name__ == '__main__':
    main()
