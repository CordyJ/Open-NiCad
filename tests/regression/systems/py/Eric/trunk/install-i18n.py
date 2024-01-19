#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2004 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#
# This is the install script for eric4's translation files.

"""
Installation script for the eric4 IDE translation files.
"""

import sys
import os
import shutil
import glob

from PyQt4.QtCore import QDir

try:
    from eric4config import getConfig
except ImportError:
    print "The eric4 IDE doesn't seem to be installed. Aborting."
    sys.exit(1)
    
def getConfigDir():
    """
    Global function to get the name of the directory storing the config data.
    
    @return directory name of the config dir (string)
    """
    if sys.platform.startswith("win"):
        cdn = "_eric4"
    else:
        cdn = ".eric4"
        
    hp = QDir.homePath()
    dn = QDir(hp)
    dn.mkdir(cdn)
    hp.append("/").append(cdn)
    try:
        return unicode(QDir.toNativeSeparators(hp))
    except AttributeError:
        return unicode(QDir.convertSeparators(hp))
    
# Define the globals.
progName = None
configDir = getConfigDir()
privateInstall = False

def usage(rcode = 2):
    """
    Display a usage message and exit.

    @param rcode return code passed back to the calling process (integer)
    """
    global progName, configDir

    print
    print "Usage:"
    print "    %s [-hp]" % (progName)
    print "where:"
    print "    -h        display this help message"
    print "    -p        install into the private area (%s)" % (configDir)

    sys.exit(rcode)

def installTranslations():
    """
    Install the translation files into the right place.
    """
    global privateInstall, configDir
    
    if privateInstall:
        targetDir = configDir
    else:
        targetDir = getConfig('ericDir')
    
    try:
        for fn in glob.glob(os.path.join('eric', 'i18n', '*.qm')):
            shutil.copy2(fn, targetDir)
    except IOError, msg:
        sys.stderr.write('IOError: %s\nTry install-i18n as root.\n' % msg)
    
def main(argv):
    """
    The main function of the script.

    @param argv list of command line arguments (list of strings)
    """
    import getopt

    # Parse the command line.
    global progName, privateInstall
    progName = os.path.basename(argv[0])

    try:
        optlist, args = getopt.getopt(argv[1:],"hp")
    except getopt.GetoptError:
        usage()

    global platBinDir
    
    depChecks = 1

    for opt, arg in optlist:
        if opt == "-h":
            usage(0)
        elif opt == "-p":
            privateInstall = 1
        
    installTranslations()

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
