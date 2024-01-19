#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2003 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Eric4 Documentation Generator

This is the main Python script of the documentation generator. It is
this script that gets called via the source documentation interface.
This script can be used via the commandline as well.
"""

import glob
import os
import sys
import shutil
import fnmatch

sys.e4nokde = True

import Utilities.ModuleParser
from DocumentationTools.ModuleDocumentor import ModuleDocument
from DocumentationTools.IndexGenerator import IndexGenerator
from DocumentationTools.QtHelpGenerator import QtHelpGenerator
from DocumentationTools.Config import eric4docDefaultColors
from UI.Info import Version
import Utilities
import Preferences

# list of supported filename extensions
supportedExtensions = [".py", ".pyw", ".ptl", ".rb"]    

def usage():
    """
    Function to print some usage information.
    
    It prints a reference of all commandline parameters that may
    be used and ends the application.
    """
    print "eric4-doc"
    print
    print "Copyright (c) 2003 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>."
    print
    print "Usage:"
    print
    print "  eric4-doc [options] files..."
    print
    print "where files can be either python modules, package"
    print "directories or ordinary directories."
    print
    print "Options:"
    print
    print "  -c filename or --style-sheet=filename"
    print "        Specify a CSS style sheet file to be used."
    print "  -e or --noempty"
    print "        Don't include empty modules."
    print "  -h or --help"
    print "        Show this help and exit."
    print "  -i or --noindex"
    print "        Don't generate index files."
    print "  -o directory or --outdir=directory"
    print "        Generate files in the named directory."
    print "  -R, -r or --recursive"
    print "        Perform a recursive search for Python files."
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
    print
    print "  --body-color=color"
    print "        Specify the text color."
    print "  --body-background-color=color"
    print "        Specify the text background color."
    print "  --l1header-color=color"
    print "        Specify the text color of level 1 headers."
    print "  --l1header-background-color=color"
    print "        Specify the text background color of level 1 headers."
    print "  --l2header-color=color"
    print "        Specify the text color of level 2 headers."
    print "  --l2header-background-color=color"
    print "        Specify the text background color of level 2 headers."
    print "  --cfheader-color=color"
    print "        Specify the text color of class and function headers."
    print "  --cfheader-background-color=color"
    print "        Specify the text background color of class and function headers."
    print "  --link-color=color"
    print "        Specify the text color of hyperlinks."
    print
    print "  --create-qhp"
    print "        Enable generation of QtHelp files."
    print "  --qhp-outdir=directory"
    print "        Generate QtHelp files in the named directory."
    print "  --qhp-namespace=namespace"
    print "        Use the given namespace (mandatory)."
    print "  --qhp-virtualfolder=folder"
    print "        Use the given virtual folder (mandatory)."
    print "        The virtual folder must not contain '/'."
    print "  --qhp-filtername=name"
    print "        Use the given name for the custom filter."
    print "  --qhp-filterattribs=attributes"
    print "        Add the given attributes to the filter list."
    print "        Attributes must be separated by ':'."
    print "  --qhp-title=title"
    print "        Use this as the title for the generated help (mandatory)."
    print "  --create-qhc"
    print "        Enable generation of QtHelp Collection files."
    sys.exit(1)

def version():
    """
    Function to show the version information.
    """
    print \
"""eric4-doc  %s

Eric4 API documentation generator.

Copyright (c) 2003-2010 Detlev Offenbach <detlev@die-offenbachs.de>
This is free software; see the LICENSE.GPL3 for copying conditions.
There is NO warranty; not even for MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE.""" % Version
    sys.exit(1)

def main():
    """
    Main entry point into the application.
    """

    import getopt

    try:
        opts, args = getopt.getopt(sys.argv[1:], "c:ehio:Rrt:Vx:",
            ["exclude=", "extension=", "help", "noindex", "noempty", "outdir=",
             "recursive", "style-sheet=", "version",
             "exclude-file=",
             "body-color=", "body-background-color=", 
             "l1header-color=", "l1header-background-color=",
             "l2header-color=", "l2header-background-color=",
             "cfheader-color=", "cfheader-background-color=",
             "link-color=",
             "create-qhp", "qhp-outdir=", "qhp-namespace=", 
             "qhp-virtualfolder=", "qhp-filtername=", "qhp-filterattribs=", 
             "qhp-title=", "create-qhc", 
            ])
    except getopt.error, e:
        usage()

    excludeDirs = ["CVS", ".svn", "_svn", ".ropeproject", "_ropeproject", 
                   ".eric4project", "_eric4project", "dist", "build", "doc", "docs"]
    excludePatterns = []
    outputDir = "doc"
    recursive = False
    doIndex = True
    noempty = False
    stylesheetFile = ""
    colors = eric4docDefaultColors.copy()
    
    qtHelpCreation = False
    qtHelpOutputDir = "help"
    qtHelpNamespace = ""
    qtHelpFolder = "source"
    qtHelpFilterName = "unknown"
    qtHelpFilterAttribs = ""
    qtHelpTitle = ""
    qtHelpCreateCollection = False
    
    # Set the applications string encoding
    try:
        sys.setappdefaultencoding(str(Preferences.getSystem("StringEncoding")))
    except AttributeError:
        pass

    for k, v in opts:
        if k in ["-o", "--outdir"]:
            outputDir = v
        elif k in ["-R", "-r", "--recursive"]:
            recursive = True
        elif k in ["-x", "--exclude"]:
            excludeDirs.append(v)
        elif k == "--exclude-file":
            excludePatterns.append(v)
        elif k in ["-i", "--noindex"]:
            doIndex = False
        elif k in ["-e", "--noempty"]:
            noempty = True
        elif k in ["-h", "--help"]:
            usage()
        elif k in ["-V", "--version"]:
            version()
        elif k in ["-c", "--style-sheet"]:
            stylesheetFile = v
        elif k in ["-t", "--extension"]:
            if not v.startswith("."):
                v = ".%s" % v
            supportedExtensions.append(v)
        
        elif k == "--body-color":
            colors['BodyColor'] = v
        elif k == "--body-background-color":
            colors['BodyBgColor'] = v
        elif k == "--l1header-color":
            colors['Level1HeaderColor'] = v
        elif k == "--l1header-background-color":
            colors['Level1HeaderBgColor'] = v
        elif k == "--l2header-color":
            colors['Level2HeaderColor'] = v
        elif k == "--l2header-background-color":
            colors['Level2HeaderBgColor'] = v
        elif k == "--cfheader-color":
            colors['CFColor'] = v
        elif k == "--cfheader-background-color":
            colors['CFBgColor'] = v
        elif k == "--link-color":
            colors['LinkColor'] = v
        
        elif k == "--create-qhp":
            qtHelpCreation = True
        elif k == "--qhp-outdir":
            qtHelpOutputDir = v
        elif k == "--qhp-namespace":
            qtHelpNamespace = v
        elif k == "--qhp-virtualfolder":
            qtHelpFolder = v
        elif k == "--qhp-filtername":
            qtHelpFilterName = v
        elif k == "--qhp-filterattribs":
            qtHelpFilterAttribs = v
        elif k == "--qhp-title":
            qtHelpTitle = v
        elif k == "--create-qhc":
            qtHelpCreateCollection = True

    if not args:
        usage()
    
    if qtHelpCreation and \
       (qtHelpNamespace == "" or \
        qtHelpFolder == "" or '/' in qtHelpFolder or \
        qtHelpTitle == ""):
        usage()

    input = output = 0
    basename = ""

    if outputDir:
        if not os.path.isdir(outputDir):
            try:
                os.makedirs(outputDir)
            except EnvironmentError:
                sys.stderr.write("Could not create output directory %s." % outputDir)
                sys.exit(2)
    else:
        outputDir = os.getcwd()
    outputDir = os.path.abspath(outputDir)

    if stylesheetFile:
        try:
            sf = open(stylesheetFile, "rb")
            stylesheet = sf.read()
            sf.close()
        except IOError:
            sys.stderr.write("The CSS stylesheet '%s' does not exist\n" % stylesheetFile)
            sys.stderr.write("Disabling CSS usage.\n")
            stylesheet = None
    else:
        stylesheet = None
    
    indexGenerator = IndexGenerator(outputDir, colors, stylesheet)
    
    if qtHelpCreation:
        if qtHelpOutputDir:
            if not os.path.isdir(qtHelpOutputDir):
                try:
                    os.makedirs(qtHelpOutputDir)
                except EnvironmentError:
                    sys.stderr.write("Could not create QtHelp output directory %s." % \
                        qtHelpOutputDir)
                    sys.exit(2)
        else:
            qtHelpOutputDir = os.getcwd()
        qtHelpOutputDir = os.path.abspath(qtHelpOutputDir)
        
        qtHelpGenerator = QtHelpGenerator(outputDir, 
                                          qtHelpOutputDir, qtHelpNamespace, qtHelpFolder, 
                                          qtHelpFilterName, qtHelpFilterAttribs, 
                                          qtHelpTitle, qtHelpCreateCollection)
    
    for arg in args:
        if os.path.isdir(arg):
            if os.path.exists(os.path.join(arg, Utilities.joinext("__init__", ".py"))):
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
        
        for filename in names:
            inpackage = False
            if os.path.isdir(filename):
                files = []
                for ext in supportedExtensions:
                    files.extend(glob.glob(os.path.join(filename,
                                                        Utilities.joinext("*", ext))))
                    initFile = os.path.join(filename, Utilities.joinext("__init__", ext))
                    if initFile in files:
                        inpackage = True
                        files.remove(initFile)
                        files.insert(0, initFile)
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
                    module = Utilities.ModuleParser.readModule(file, basename = basename, 
                                inpackage = inpackage, extensions = supportedExtensions)
                    moduleDocument = ModuleDocument(module, colors, stylesheet)
                    doc = moduleDocument.genDocument()
                except IOError, v:
                    sys.stderr.write("%s error: %s\n" % (file, v[1]))
                    continue
                except ImportError, v:
                    sys.stderr.write("%s error: %s\n" % (file, v))
                    continue
                
                input = input + 1
                
                f = Utilities.joinext(os.path.join(outputDir, moduleDocument.name()),
                                      ".html")
                
                # remember for index file generation
                indexGenerator.remember(file, moduleDocument, basename)
                
                # remember for QtHelp generation
                if qtHelpCreation:
                    qtHelpGenerator.remember(file, moduleDocument, basename)
                
                if (noempty or file.endswith('__init__.py')) \
                   and moduleDocument.isEmpty():
                    continue
                
                # generate output
                try:
                    out = open(f, "wb")
                    out.write(doc)
                    out.close()
                except IOError, v:
                    sys.stderr.write("%s error: %s\n" % (file, v[1]))
                else:
                    sys.stdout.write("%s ok\n" % f)
                
                output = output + 1
    sys.stdout.flush()
    sys.stderr.flush()

    # write index files
    if doIndex:
        indexGenerator.writeIndices(basename)
    
    # generate the QtHelp files
    if qtHelpCreation:
        qtHelpGenerator.generateFiles()

    sys.exit(0)

if __name__ == '__main__':
    main()
