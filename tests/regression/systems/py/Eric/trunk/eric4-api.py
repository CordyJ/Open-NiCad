#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2003 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Eric4 API Generator

This is the main Python script of the API generator. It is
this script that gets called via the API generation interface.
This script can be used via the commandline as well.
"""

import glob
import os
import sys
import fnmatch

sys.e4nokde = True

import Utilities.ModuleParser
from DocumentationTools.APIGenerator import APIGenerator
from UI.Info import Version
import Utilities
import Preferences
import DocumentationTools

def usage():
    """
    Function to print some usage information.
    
    It prints a reference of all commandline parameters that may
    be used and ends the application.
    """
    print "eric4-api"
    print
    print "Copyright (c) 2004 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>."
    print
    print "Usage:"
    print
    print "  eric4-api [options] files..."
    print
    print "where files can be either python modules, package"
    print "directories or ordinary directories."
    print
    print "Options:"
    print
    print "  -b name or --base name"
    print "        Use the given name as the name of the base package."
    print "  -h or --help"
    print "        Show this help and exit."
    print "  -o filename or --output=filename"
    print "        Write the API information to the named file. A '%L' placeholder"
    print "        is replaced by the language of the API file (see --language)."
    print "  --oldstyle"
    print "        Generate API files for QScintilla prior to 1.7."
    print "  -p or --private"
    print "        Include private methods and functions."
    print "  -R, -r or --recursive"
    print "        Perform a recursive search for source files."
    print "  -t ext or --extension=ext"
    print "        Add the given extension to the list of file extensions."
    print "        This option may be given multiple times."
    print "  -V or --version"
    print "        Show version information and exit."
    print "  -x directory or --exclude=directory"
    print "        Specify a directory basename to be excluded."
    print "        This option may be repeated multiple times."
    print "  --exclude-file=pattern"
    print "        Specify a filename pattern of files to be excluded."
    print "        This option may be repeated multiple times."
    print "  -l language or --language=language"
    print "        Generate an API file for the given programming language."
    print "        Supported programming languages are:"
    for lang in sorted(DocumentationTools.supportedExtensionsDictForApis.keys()):
        print "            * %s" % lang
    print "        The default is 'Python'."
    print "        This option may be repeated multiple times."
    sys.exit(1)

def version():
    """
    Function to show the version information.
    """
    print \
"""eric4-api  %s

Eric4 API generator.

Copyright (c) 2004 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
This is free software; see the LICENSE.GPL3 for copying conditions.
There is NO warranty; not even for MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE.""" % Version
    sys.exit(1)

def main():
    """
    Main entry point into the application.
    """
    global supportedExtensions

    import getopt

    try:
        opts, args = getopt.getopt(sys.argv[1:], "b:hl:o:pRrt:Vx:",
            ["base=", "exclude=", "exclude-file=", "extension=", "help",
             "language=", "oldstyle", "output=", "private", "recursive", 
             "version", ])
    except getopt.error:
        usage()

    excludeDirs = ["CVS", ".svn", "_svn", ".ropeproject", "_ropeproject", 
                   ".eric4project", "_eric4project", "dist", "build", "doc", "docs"]
    excludePatterns = []
    outputFileName = ""
    recursive = False
    newStyle = True
    basePackage = ""
    includePrivate = False
    progLanguages = []
    extensions = []

    # Set the applications string encoding
    try:
        sys.setappdefaultencoding(str(Preferences.getSystem("StringEncoding")))
    except AttributeError:
        pass

    for k, v in opts:
        if k in ["-o", "--output"]:
            outputFileName = v
        elif k in ["-R", "-r", "--recursive"]:
            recursive = True
        elif k in ["-x", "--exclude"]:
            excludeDirs.append(v)
        elif k == "--exclude-file":
            excludePatterns.append(v)
        elif k in ["-h", "--help"]:
            usage()
        elif k in ["-V", "--version"]:
            version()
        elif k in ["-t", "--extension"]:
            if not v.startswith("."):
                v = ".%s" % v
            extensions.append(v)
        elif k in ["--oldstyle"]:
            newStyle = False
        elif k in ["-b", "--base"]:
            basePackage = v
        elif k in ["-p", "--private"]:
            includePrivate = True
        elif k in ["-l", "--language"]:
            if v not in progLanguages:
                if v not in DocumentationTools.supportedExtensionsDictForApis.keys():
                    sys.stderr.write("Wrong language given: %s. Aborting\n" % v)
                    sys.exit(1)
                else:
                    progLanguages.append(v)

    if not args:
        usage()

    if outputFileName == "":
        sys.stderr.write("No output file given. Aborting\n")
        sys.exit(1)
    
    if len(progLanguages) == 0:
        progLanguages = ["Python"]
    
    for progLanguage in sorted(progLanguages):
        basename = ""
        apis = []

        supportedExtensions = \
            DocumentationTools.supportedExtensionsDictForApis[progLanguage]
        supportedExtensions.extend(extensions)
        if "%L" in outputFileName:
            outputFile = outputFileName.replace("%L", progLanguage)
        else:
            if len(progLanguages) == 1:
                outputFile = outputFileName
            else:
                root, ext = os.path.splitext(outputFileName)
                outputFile = "%s-%s%s" % (root, progLanguage.lower(), ext)
        
        for arg in args:
            if os.path.isdir(arg):
                if os.path.exists(os.path.join(arg, 
                                               Utilities.joinext("__init__", ".py"))):
                    basename = os.path.dirname(arg)
                    if arg == '.':
                        sys.stderr.write("The directory '.' is a package.\n")
                        sys.stderr.write("Please repeat the call giving its real name.\n")
                        sys.stderr.write("Ignoring the directory.\n")
                        continue
                else:
                    basename = arg
                if basename:
                    basename = "%s%s" % (basename, os.sep)
                    
                if recursive and not os.path.islink(arg):
                    names = [arg] + Utilities.getDirs(arg, excludeDirs)
                else:
                    names = [arg]
            else:
                basename = ""
                names = [arg]
            
            for filename in sorted(names):
                inpackage = False
                if os.path.isdir(filename):
                    files = []
                    for ext in supportedExtensions:
                        files.extend(glob.glob(os.path.join(filename,
                                                            Utilities.joinext("*", ext))))
                        initFile = os.path.join(filename, 
                                                Utilities.joinext("__init__", ext))
                        if initFile in files:
                            inpackage = True
                            files.remove(initFile)
                            files.insert(0, initFile)
                        elif progLanguage != "Python":
                            # assume package
                            inpackage = True
                else:
                    if Utilities.isWindowsPlatform() and glob.has_magic(filename):
                        files = glob.glob(filename)
                    else:
                        files = [filename]
                
                for file in files:
                    skipIt = False
                    for pattern in excludePatterns:
                        if fnmatch.fnmatch(os.path.basename(file), pattern):
                            skipIt = True
                            break
                    if skipIt:
                        continue
                    
                    try:
                        module = Utilities.ModuleParser.readModule(file, 
                            basename = basename, inpackage = inpackage)
                        apiGenerator = APIGenerator(module)
                        api = apiGenerator.genAPI(newStyle, basePackage, includePrivate)
                    except IOError, v:
                        sys.stderr.write("%s error: %s\n" % (file, v[1]))
                        continue
                    except ImportError, v:
                        sys.stderr.write("%s error: %s\n" % (file, v))
                        continue
                    
                    for apiEntry in api:
                        if not apiEntry in apis:
                            apis.append(apiEntry)
                    sys.stdout.write("-- %s -- %s ok\n" % (progLanguage, file))

        outdir = os.path.dirname(outputFile)
        if outdir and not os.path.exists(outdir):
            os.makedirs(outdir)
        try:
            out = open(outputFile, "wb")
            out.write(os.linesep.join(sorted(apis)))
            out.close()
        except IOError, v:
            sys.stderr.write("%s error: %s\n" % (outputFile, v[1]))
            sys.exit(3)
    
    sys.stdout.write('\nDone.\n')
    sys.exit(0)

if __name__ == '__main__':
    main()
