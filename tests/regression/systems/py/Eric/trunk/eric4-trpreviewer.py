#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2004 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Eric4 TR Previewer

This is the main Python script that performs the necessary initialization
of the tr previewer and starts the Qt event loop. This is a standalone version
of the integrated tr previewer.
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

from Tools.TRSingleApplication import TRSingleApplicationClient
from Utilities import Startup

def createMainWidget(argv):
    """
    Function to create the main widget.
    
    @param argv list of commandline parameters (list of strings)
    @return reference to the main widget (QWidget)
    """
    from Tools.TRPreviewer import TRPreviewer
    
    if len(argv) > 1:
        files = argv[1:]
    else:
        files = []
    
    previewer = TRPreviewer(files, None, 'TRPreviewer')
    return previewer

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
        ("!+file","")
    ]
    appinfo = Startup.makeAppInfo(sys.argv,
                                  "Eric4 TR Previewer",
                                  "file",
                                  "TR file previewer",
                                  options)
    
    client = TRSingleApplicationClient()
    res = client.connect()
    if res > 0:
        if len(sys.argv) > 1:
            client.processArgs(sys.argv[1:])
        sys.exit(0)
    elif res < 0:
        print "eric4-trpreviewer: %s" % client.errstr()
        sys.exit(res)
    else:
        res = Startup.simpleAppStartup(sys.argv,
                                       appinfo,
                                       createMainWidget,
                                       kqOptions)
        sys.exit(res)

if __name__ == '__main__':
    main()
