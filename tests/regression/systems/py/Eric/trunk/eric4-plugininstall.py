#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2007 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Eric4 Plugin Installer

This is the main Python script to install eric4 plugins from outside of the IDE.
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

from Utilities import Startup

def createMainWidget(argv):
    """
    Function to create the main widget.
    
    @param argv list of commandline parameters (list of strings)
    @return reference to the main widget (QWidget)
    """
    from PluginManager.PluginInstallDialog import PluginInstallWindow
    return PluginInstallWindow(argv[1:])

def main():
    """
    Main entry point into the application.
    """
    options = [\
        ("--config=configDir", 
         "use the given directory as the one containing the config files"), 
        ("--nokde" , "don't use KDE widgets"),
        ("", "names of plugins to install")
    ]
    kqOptions = [\
        ("config \\", "use the given directory as the one containing the config files"), 
        ("nokde" , "don't use KDE widgets"),
        ("!+file","")
    ]
    appinfo = Startup.makeAppInfo(sys.argv,
                                  "Eric4 Plugin Installer",
                                  "",
                                  "Plugin installation utility for eric4",
                                  options)
    res = Startup.simpleAppStartup(sys.argv,
                                   appinfo,
                                   createMainWidget, 
                                   kqOptions)
    sys.exit(res)

if __name__ == '__main__':
    main()
