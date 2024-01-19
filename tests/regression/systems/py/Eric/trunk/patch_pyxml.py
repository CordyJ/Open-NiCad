# -*- coding: utf-8 -*-

# Copyright (c) 2007 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#
# This is a  script to patch pyxml to correct a bug. 

"""
Script to patch pyXML to correct a bug.
"""

import sys
import os
import shutil
import py_compile
import distutils.sysconfig

# Define the globals.
progName = None
pyxmlModDir = None

def usage(rcode = 2):
    """
    Display a usage message and exit.

    rcode is the return code passed back to the calling process.
    """
    global progName, pyxmlModDir
    
    print "Usage:"
    print "    %s [-h] [-d dir]" % (progName)
    print "where:"
    print "    -h             display this help message"
    print "    -d dir         where pyXML is installed [default %s]" % \
        (pyxmlModDir)
    print
    print "This script patches the file _xmlplus/parsers/xmlproc/xmlutils.py"
    print "of the pyXML distribution to fix a bug causing it to fail"
    print "for XML files containing non ASCII characters."
    print

    sys.exit(rcode)


def initGlobals():
    """
    Sets the values of globals that need more than a simple assignment.
    """
    global pyxmlModDir

    pyxmlModDir = os.path.join(distutils.sysconfig.get_python_lib(True), "_xmlplus")

def isPatched():
    """
    Function to check, if pyXML is already patched.
    
    @return flag indicating patch status (boolean)
    """
    global pyxmlModDir
    
    initGlobals()

    try:
        filename = \
            os.path.join(pyxmlModDir, "parsers", "xmlproc", "xmlutils.py")
        f = open(filename, "r")
    except EnvironmentError:
        print "Could not find the pyXML distribution. Please use the patch_pyxml.py"
        print "script to apply a patch needed to fix a bug causing it to fail for"
        print "XML files containing non ASCII characters."
        return True # fake a found patch
    
    lines = f.readlines()
    f.close()
    
    patchPositionFound = False
    
    for line in lines:
        if patchPositionFound and \
            (line.startswith(\
                "                # patched by eric4 install script.") or \
             line.startswith(\
                "                self.datasize = len(self.data)")):
                return True
        if line.startswith(\
              "                self.data = self.charset_converter(self.data)"):
            patchPositionFound = True
            continue
    
    return False
    
def patchPyXML():
    """
    The patch function.
    """
    global pyxmlModDir
    
    initGlobals()

    try:
        filename = \
            os.path.join(pyxmlModDir, "parsers", "xmlproc", "xmlutils.py")
        f = open(filename, "r")
    except EnvironmentError:
        print "The file %s does not exist. Aborting." % filename
        sys.exit(1)
    
    lines = f.readlines()
    f.close()
    
    patchPositionFound = False
    patched = False
    
    sn = "xmlutils.py"
    s = open(sn, "w")
    for line in lines:
        if patchPositionFound:
            if not line.startswith(\
                    "                # patched by eric4 install script.") and \
               not line.startswith(\
                    "                self.datasize = len(self.data)"):
                s.write("                # patched by eric4 install script.\n")
                s.write("                self.datasize = len(self.data)\n")
                patched = True
            patchPositionFound = False
        s.write(line)
        if line.startswith(\
              "                self.data = self.charset_converter(self.data)"):
            patchPositionFound = True
            continue
    s.close()
    
    if not patched:
        print "xmlutils.py is already patched."
        os.remove(sn)
    else:
        try:
            py_compile.compile(sn)
        except py_compile.PyCompileError, e:
            print "Error compiling %s. Aborting" % sn
            print e
            os.remove(sn)
            sys.exit(1)
        except SyntaxError, e:
            print "Error compiling %s. Aborting" % sn
            print e
            os.remove(sn)
            sys.exit(1)
        
        shutil.copy(filename, "%s.orig" % filename)
        shutil.copy(sn, filename)
        os.remove(sn)
        if os.path.exists("%sc" % sn):
            shutil.copy("%sc" % sn, "%sc" % filename)
            os.remove("%sc" % sn)
        if os.path.exists("%so" % sn):
            shutil.copy("%so" % sn, "%so" % filename)
            os.remove("%so" % sn)
            
        print "xmlutils.py patched successfully."
        print "Unpatched file copied to %s.orig." % filename
    
def main(argv):
    """
    The main function of the script.

    argv is the list of command line arguments.
    """
    import getopt

    # Parse the command line.
    global progName, pyxmlModDir
    progName = os.path.basename(argv[0])

    initGlobals()

    try:
        optlist, args = getopt.getopt(argv[1:],"hd:")
    except getopt.GetoptError:
        usage()

    for opt, arg in optlist:
        if opt == "-h":
            usage(0)
        elif opt == "-d":
            global pyxmlModDir
            pyxmlModDir = arg
    
    patchPyXML()
    
if __name__ == "__main__":
    main()
