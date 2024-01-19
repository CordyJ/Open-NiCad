#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2002-2010 Detlev Offenbach <detlev@die-offenbachs.de>
#
# This is the uninstall script for eric4.

"""
Uninstallation script for the eric4 IDE and all eric4 related tools.
"""

import sys
import os
import shutil
import glob
import distutils.sysconfig

from eric4config import getConfig

# Define the globals.
progName = None
pyModDir = None

def usage(rcode = 2):
    """Display a usage message and exit.

    rcode is the return code passed back to the calling process.
    """
    global progName

    print "Usage:"
    print "    %s [-h]" % (progName)
    print "where:"
    print "    -h             display this help message"

    sys.exit(rcode)


def initGlobals():
    """
    Sets the values of globals that need more than a simple assignment.
    """
    global pyModDir

    pyModDir = distutils.sysconfig.get_python_lib(True)


def wrapperName(dname,wfile):
    """Create the platform specific name for the wrapper script.
    """
    if sys.platform.startswith("win"):
        wname = dname + "\\" + wfile + ".bat"
    else:
        wname = dname + "/" + wfile

    return wname


def uninstallEric():
    """
    Uninstall the eric files.
    """
    global pyModDir
    
    # Remove the wrapper scripts
    rem_wnames = [
        "eric4-api", "eric4-compare",
        "eric4-configure", "eric4-diff",
        "eric4-doc", "eric4-helpviewer",
        "eric4-qregexp", "eric4-re", 
        "eric4-trpreviewer", "eric4-uipreviewer",
        "eric4-unittest", "eric4",
        "eric4-tray", "eric4-editor", 
        "eric4-plugininstall", "eric4-pluginuninstall", 
        "eric4-pluginrepository", "eric4-sqlbrowser", 
        "eric4-webbrowser", 
    ]
    for rem_wname in rem_wnames:
        rwname = wrapperName(getConfig('bindir'),rem_wname)
        if os.path.exists(rwname):
            os.remove(rwname)
    
    # Cleanup our config file
    for name in ['eric4config.py', 'eric4config.pyc']:
        e4cfile = os.path.join(pyModDir, name)
        if os.path.exists(e4cfile):
            os.remove(e4cfile)
    
    # Cleanup the install directories
    for name in ['ericExamplesDir', 'ericDocDir', 'ericDTDDir', 'ericCSSDir',
                 'ericIconDir', 'ericPixDir', 'ericDir', 'ericTemplatesDir',
                 'ericCodeTemplatesDir', 'ericOthersDir', 'ericStylesDir']:
        dirpath = getConfig(name)
        if os.path.exists(dirpath):
            shutil.rmtree(dirpath, True)
    
    # Cleanup translations
    for name in glob.glob(os.path.join(getConfig('ericTranslationsDir'), 'eric4_*.qm')):
        if os.path.exists(name):
            os.remove(name)
    
    # Cleanup API files
    apidir = getConfig('apidir')
    for name in getConfig('apis'):
        apiname = os.path.join(apidir, name)
        if os.path.exists(apiname):
            os.remove(apiname)
    
def main(argv):
    """The main function of the script.

    argv is the list of command line arguments.
    """
    import getopt

    initGlobals()

    # Parse the command line.
    global progName
    progName = os.path.basename(argv[0])

    try:
        optlist, args = getopt.getopt(argv[1:],"h")
    except getopt.GetoptError:
        usage()

    global platBinDir

    for opt, arg in optlist:
        if opt == "-h":
            usage(0)
    
    try:
        uninstallEric()
    except IOError, msg:
        sys.stderr.write('IOError: %s\nTry uninstall as root.\n' % msg)
    
    
if __name__ == "__main__":
    try:
        main(sys.argv)
    except SystemExit:
        raise
    except:
        print \
"""An internal error occured.  Please report all the output of the program,
including the following traceback, to eric4-bugs@eric-ide.python-projects.org.
"""
        raise
