#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2002-2010 Detlev Offenbach <detlev@die-offenbachs.de>
#
# This is the install script for eric4.

"""
Installation script for the eric4 IDE and all eric4 related tools.
"""

import sys
import os
import re
import compileall
import py_compile
import glob
import shutil
import fnmatch
import distutils.sysconfig

# Define the globals.
progName = None
modDir = None
pyModDir = None
platBinDir = None
distDir = None
apisDir = None
doCleanup = True
doCompile = True
cfg = {}
progLanguages = ["Python", "Ruby"]

def usage(rcode = 2):
    """
    Display a usage message and exit.

    @param rcode the return code passed back to the calling process.
    """
    global progName, platBinDir, modDir, distDir, apisDir

    print
    print "Usage:"
    print "    %s [-chxz] [-a dir] [-b dir] [-d dir] [-f file] [-i dir]" % (progName)
    print "where:"
    print "    -h        display this help message"
    print "    -a dir    where the API files will be installed"
    if apisDir:
        print "              (default: %s)" % (apisDir)
    else:
        print "              (no default value)"
    print "    -b dir    where the binaries will be installed"
    print "              (default: %s)" % (platBinDir)
    print "    -d dir    where eric4 python files will be installed"
    print "              (default: %s)" % (modDir)
    print "    -f file   configuration file naming the various installation paths"
    if not sys.platform.startswith("win"):
        print "    -i dir    temporary install prefix"
        print "              (default: %s)" % (distDir)
    print "    -x        don't perform dependency checks (use on your own risk)"
    print "    -c        don't cleanup old installation first"
    print "    -z        don't compile the installed python files"
    print
    print "The file given to the -f option must be valid Python code defining a"
    print "dictionary called 'cfg' with the keys 'ericDir', 'ericPixDir', 'ericIconDir',"
    print "'ericDTDDir', 'ericCSSDir', 'ericStylesDir', 'ericDocDir', 'ericExamplesDir',"
    print "'ericTranslationsDir', 'ericTemplatesDir', 'ericCodeTemplatesDir',"
    print "'ericOthersDir','bindir', 'mdir' and 'apidir."
    print "These define the directories for the installation of the various parts of"\
          " eric4."

    sys.exit(rcode)


def initGlobals():
    """
    Sets the values of globals that need more than a simple assignment.
    """
    global platBinDir, modDir, pyModDir, apisDir

    if sys.platform.startswith("win"):
        platBinDir = sys.exec_prefix
        if platBinDir.endswith("\\"):
            platBinDir = platBinDir[:-1]
    else:
        platBinDir = "/usr/local/bin"

    modDir = distutils.sysconfig.get_python_lib(True)
    pyModDir = modDir
    
    try:
        from PyQt4 import pyqtconfig
        qtDataDir = pyqtconfig._pkg_config["qt_data_dir"]
    except (AttributeError, ImportError):
        qtDataDir = None
    if qtDataDir:
        apisDir = os.path.join(qtDataDir, "qsci", "api")
    else:
        apisDir = None


def copyToFile(name, text):
    """
    Copy a string to a file.

    @param name the name of the file.
    @param text the contents to copy to the file.
    """
    f = open(name,"w")
    f.write(text)
    f.close()


def wrapperName(dname, wfile):
    """
    Create the platform specific name for the wrapper script.
    
    @param dname name of the directory to place the wrapper into
    @param wfile basename (without extension) of the wrapper script
    @return the name of the wrapper script
    """
    if sys.platform.startswith("win"):
        wname = dname + "\\" + wfile + ".bat"
    else:
        wname = dname + "/" + wfile

    return wname


def createPyWrapper(pydir, wfile):
    """
    Create an executable wrapper for a Python script.

    @param pydir the name of the directory where the Python script will eventually
        be installed
    @param wfile the basename of the wrapper
    @return the platform specific name of the wrapper
    """
    # all kinds of Windows systems
    if sys.platform.startswith("win"):
        wname = wfile + ".bat"
        wrapper = \
'''@"%s\\pythonw" "%s\\%s.py" %%1 %%2 %%3 %%4 %%5 %%6 %%7 %%8 %%9
''' % (platBinDir, pydir, wfile)

    # Mac OS X
    elif sys.platform == "darwin":
        wname = wfile
        wrapper = \
'''#!/bin/sh

exec "%s/bin/pythonw" "%s/%s.py" "$@"
''' % (sys.exec_prefix, pydir, wfile)

    # *nix systems
    else:
        wname = wfile
        wrapper = \
'''#!/bin/sh

exec "%s" "%s/%s.py" "$@"
''' % (sys.executable, pydir, wfile)

    copyToFile(wname, wrapper)
    os.chmod(wname, 0755)

    return wname


def copyTree(src, dst, filters, excludeDirs=[]):
    """
    Copy Python, translation, documentation, wizards configuration,
    designer template files and DTDs of a directory tree.
    
    @param src name of the source directory
    @param dst name of the destination directory
    @param filters list of filter pattern determining the files to be copied
    @param excludeDirs list of (sub)directories to exclude from copying
    """
    try:
        names = os.listdir(src)
    except OSError:
        return      # ignore missing directories (most probably the i18n directory)
    
    for name in names:
        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name)
        for filter in filters:
            if fnmatch.fnmatch(srcname, filter):
                if not os.path.isdir(dst):
                    os.makedirs(dst)
                shutil.copy2(srcname, dstname)
                break
        else:
            if os.path.isdir(srcname) and not srcname in excludeDirs:
                copyTree(srcname, dstname, filters)


def createGlobalPluginsDir():
    """
    Create the global plugins directory, if it doesn't exist.
    """
    global cfg, distDir
    
    pdir = os.path.join(cfg['mdir'], "eric4plugins")
    fname = os.path.join(pdir, "__init__.py")
    if not os.path.exists(fname):
        if not os.path.exists(pdir):
            os.mkdir(pdir,  0755)
        f = open(fname, "wb")
        f.write(\
'''# -*- coding: utf-8 -*-

"""
Package containing the global plugins.
"""
'''        
        )
        f.close()


def cleanUp():
    """
    Uninstall the old eric files.
    """
    try:
        from eric4config import getConfig
    except ImportError:
        # eric4 wasn't installed previously
        return
    
    global pyModDir, progLanguages
    
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
        rwname = wrapperName(getConfig('bindir'), rem_wname)
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
        if os.path.exists(getConfig(name)):
            shutil.rmtree(getConfig(name), True)
    
    # Cleanup translations
    for name in glob.glob(os.path.join(getConfig('ericTranslationsDir'), 'eric4_*.qm')):
        if os.path.exists(name):
            os.remove(name)
    
    # Cleanup API files
    try:
        apidir = getConfig('apidir')
        for progLanguage in progLanguages:
            for name in getConfig('apis'):
                apiname = os.path.join(apidir, progLanguage, name)
                if os.path.exists(apiname):
                    os.remove(apiname)
    except AttributeError:
        pass


def installEric():
    """
    Actually perform the installation steps.
    """
    global distDir, doCleanup, cfg, progLanguages
    
    # Create the platform specific wrappers.
    wnames = []
    wnames.append(createPyWrapper(cfg['ericDir'], "eric4-api"))
    wnames.append(createPyWrapper(cfg['ericDir'], "eric4-compare"))
    wnames.append(createPyWrapper(cfg['ericDir'], "eric4-configure"))
    wnames.append(createPyWrapper(cfg['ericDir'], "eric4-diff"))
    wnames.append(createPyWrapper(cfg['ericDir'], "eric4-doc"))
    wnames.append(createPyWrapper(cfg['ericDir'], "eric4-webbrowser"))
    wnames.append(createPyWrapper(cfg['ericDir'], "eric4-qregexp"))
    wnames.append(createPyWrapper(cfg['ericDir'], "eric4-re"))
    wnames.append(createPyWrapper(cfg['ericDir'], "eric4-trpreviewer"))
    wnames.append(createPyWrapper(cfg['ericDir'], "eric4-uipreviewer"))
    wnames.append(createPyWrapper(cfg['ericDir'], "eric4-unittest"))
    wnames.append(createPyWrapper(cfg['ericDir'], "eric4-tray"))
    wnames.append(createPyWrapper(cfg['ericDir'], "eric4-editor"))
    wnames.append(createPyWrapper(cfg['ericDir'], "eric4-plugininstall"))
    wnames.append(createPyWrapper(cfg['ericDir'], "eric4-pluginuninstall"))
    wnames.append(createPyWrapper(cfg['ericDir'], "eric4-pluginrepository"))
    wnames.append(createPyWrapper(cfg['ericDir'], "eric4-sqlbrowser"))
    wnames.append(createPyWrapper(cfg['ericDir'], "eric4"))
    
    # set install prefix, if not None
    if distDir:
        for key in cfg.keys():
            cfg[key] = os.path.normpath(distDir + os.sep + cfg[key])
    
    try:
        # Install the files
        # make the install directories
        for key in cfg.keys():
            if not os.path.isdir(cfg[key]):
                os.makedirs(cfg[key])
        
        # copy the eric4 config file
        if distDir:
            shutil.copy('eric4config.py', cfg['mdir'])
            if os.path.exists('eric4config.pyc'):
                shutil.copy('eric4config.pyc', cfg['mdir'])
        else:
            shutil.copy('eric4config.py', modDir)
            if os.path.exists('eric4config.pyc'):
                shutil.copy('eric4config.pyc', modDir)
        
        # copy the eric4.pth file
        if distDir:
            shutil.copy('eric%seric4.pth' % os.sep, cfg['mdir'])
        else:
            shutil.copy('eric%seric4.pth' % os.sep, modDir)
        
        # copy the various parts of eric4
        copyTree('eric', cfg['ericDir'], ['*.py', '*.pyc', '*.pyo', '*.pyw'], 
            ['eric%sExamples' % os.sep])
        copyTree('eric', cfg['ericDir'], ['*.rb'], 
            ['eric%sExamples' % os.sep])
        copyTree('eric%sPlugins' % os.sep, '%s%sPlugins' % (cfg['ericDir'], os.sep), 
            ['*.png'])
        copyTree('eric%sDocumentation' % os.sep, cfg['ericDocDir'], ['*.html', '*.qch'])
        copyTree('eric%sDTDs' % os.sep, cfg['ericDTDDir'], ['*.dtd'])
        copyTree('eric%sCSSs' % os.sep, cfg['ericCSSDir'], ['*.css'])
        copyTree('eric%sStyles' % os.sep, cfg['ericStylesDir'], ['*.qss'])
        copyTree('eric%si18n' % os.sep, cfg['ericTranslationsDir'], ['*.qm'])
        copyTree('eric%sicons' % os.sep, cfg['ericIconDir'], ['*.png', 'LICENSE*.*'])
        copyTree('eric%spixmaps' % os.sep, cfg['ericPixDir'], ['*.png', '*.xpm', '*.ico'])
        copyTree('eric%sDesignerTemplates' % os.sep, cfg['ericTemplatesDir'], ['*.tmpl'])
        copyTree('eric%sCodeTemplates' % os.sep, cfg['ericCodeTemplatesDir'], ['*.tmpl'])
        copyTree('eric%sExamples' % os.sep, cfg['ericExamplesDir'], 
                 ['*.py', '*.pyc', '*.pyo'])
        
        # copy the wrappers
        for wname in wnames:
            shutil.copy(wname, cfg['bindir'])
        
        # copy the license file
        shutil.copy('eric%sLICENSE.GPL3' % os.sep, cfg['ericDir'])
        
        # create the global plugins directory
        createGlobalPluginsDir()
        
    except IOError, msg:
        sys.stderr.write('IOError: %s\nTry install as root.\n' % msg)
        sys.exit(7)
    
    # copy some text files to the doc area
    for name in ["LICENSE.GPL3", "THANKS", "changelog"]:
        try:
            shutil.copy('eric%s%s' % (os.sep, name), cfg['ericDocDir'])
        except EnvironmentError:
            print "Could not install 'eric%s%s'." % (os.sep, name)
    for name in glob.glob(os.path.join('eric', 'README*.*')):
        try:
            shutil.copy(name, cfg['ericDocDir'])
        except EnvironmentError:
            print "Could not install 'eric%s%s'." % (os.sep, name)
   
    # copy some more stuff
    for name in ['default.e4k']:
        try:
            shutil.copy('eric%s%s' % (os.sep, name), cfg['ericOthersDir'])
        except EnvironmentError:
            print "Could not install 'eric%s%s'." % (os.sep, name)
    
    # install the API file
    for progLanguage in progLanguages:
        apidir = os.path.join(cfg['apidir'], progLanguage.lower())
        if not os.path.exists(apidir):
            os.makedirs(apidir)
        for apiName in glob.glob(os.path.join("eric", "APIs", progLanguage, "*.api")):
            try:
                shutil.copy(apiName, apidir)
            except EnvironmentError:
                print "Could not install '%s'." % apiName


def createInstallConfig():
    """
    Create the installation config dictionary.
    """
    global modDir, platBinDir, cfg, apisDir
        
    ericdir = os.path.join(modDir, "eric4")
    cfg = {
        'ericDir'              : ericdir,
        'ericPixDir'           : os.path.join(ericdir, "pixmaps"),
        'ericIconDir'          : os.path.join(ericdir, "icons"),
        'ericDTDDir'           : os.path.join(ericdir, "DTDs"),
        'ericCSSDir'           : os.path.join(ericdir, "CSSs"),
        'ericStylesDir'        : os.path.join(ericdir, "Styles"),
        'ericDocDir'           : os.path.join(ericdir, "Documentation"),
        'ericExamplesDir'      : os.path.join(ericdir, "Examples"),
        'ericTranslationsDir'  : os.path.join(ericdir, "i18n"),
        'ericTemplatesDir'     : os.path.join(ericdir, "DesignerTemplates"),
        'ericCodeTemplatesDir' : os.path.join(ericdir, 'CodeTemplates'),
        'ericOthersDir'        : ericdir,
        'bindir'               : platBinDir,
        'mdir'                 : modDir,
    }
    if apisDir:
        cfg['apidir'] = apisDir
    else:
        cfg['apidir'] = os.path.join(ericdir, "api")
configLength = 15
    
def createConfig():
    """
    Create a config file with the respective config entries.
    """
    global cfg
    
    apis = []
    for progLanguage in progLanguages:
        for apiName in glob.glob(os.path.join("eric", "APIs", progLanguage, "*.api")):
            apis.append(os.path.basename(apiName))
    
    fn = 'eric4config.py'
    config = \
"""# -*- coding: utf-8 -*-
#
# This module contains the configuration of the individual eric4 installation
#

_pkg_config = {
    'ericDir'              : r'%s',
    'ericPixDir'           : r'%s',
    'ericIconDir'          : r'%s',
    'ericDTDDir'           : r'%s',
    'ericCSSDir'           : r'%s',
    'ericStylesDir'        : r'%s',
    'ericDocDir'           : r'%s',
    'ericExamplesDir'      : r'%s',
    'ericTranslationsDir'  : r'%s',
    'ericTemplatesDir'     : r'%s',
    'ericCodeTemplatesDir' : r'%s',
    'ericOthersDir'        : r'%s',
    'bindir'               : r'%s',
    'mdir'                 : r'%s',
    'apidir'               : r'%s',
    'apis'                 : %s,
}

def getConfig(name):
    '''
    Module function to get a configuration value.

    @param name the name of the configuration value (string).
    '''
    try:
        return _pkg_config[name]
    except KeyError:
        pass

    raise AttributeError, '"%%s" is not a valid configuration value' %% name
""" % (cfg['ericDir'], cfg['ericPixDir'], cfg['ericIconDir'], 
       cfg['ericDTDDir'], cfg['ericCSSDir'], 
       cfg['ericStylesDir'], cfg['ericDocDir'],
       cfg['ericExamplesDir'], cfg['ericTranslationsDir'],
       cfg['ericTemplatesDir'],
       cfg['ericCodeTemplatesDir'], cfg['ericOthersDir'],
       cfg['bindir'], cfg['mdir'], 
       cfg['apidir'], apis)
    copyToFile(fn, config)

def doDependancyChecks():    
    """
    Perform some dependency checks.
    """
    print 'Checking dependencies'
    
    # perform dependency checks
    if sys.version_info < (2, 4, 0):
        print 'Sorry, you must have Python 2.4.0 or higher.'
        sys.exit(5)
    if sys.version_info > (2, 9, 9):
        print 'Sorry, eric4 requires Python 2 for running.'
        sys.exit(5)
    print "Python Version: %d.%d.%d" % sys.version_info[:3]
    
    try:
        from PyQt4.QtCore import qVersion, PYQT_VERSION
    except ImportError, msg:
        print 'Sorry, please install PyQt4.'
        print 'Error: %s' % msg
        sys.exit(1)
    print "Found PyQt"
    
    try:
        from PyQt4 import Qsci
    except ImportError, msg:
        print "Sorry, please install QScintilla2 and"
        print "it's PyQt4 wrapper."
        print 'Error: %s' % msg
        sys.exit(1)
    print "Found QScintilla2"
    
    # check version of Qt
    qtMajor = int(qVersion().split('.')[0])
    qtMinor = int(qVersion().split('.')[1])
    if qtMajor < 4 or (qtMajor == 4 and qtMinor < 4):
        print 'Sorry, you must have Qt version 4.4.0 or higher.'
        sys.exit(2)
    print "Qt Version: %s" % qVersion()
    
    #check version of PyQt
    from PyQt4.QtCore import PYQT_VERSION_STR
    pyqtVersion = PYQT_VERSION_STR
    # always assume, that snapshots are new enough
    if pyqtVersion.find("snapshot-") == -1:
        while pyqtVersion.count('.') < 2:
            pyqtVersion += '.0'
        (maj, min, pat) = pyqtVersion.split('.')
        maj = int(maj)
        min = int(min)
        pat = int(pat)
        if maj < 4 or (maj == 4 and min < 3):
            print 'Sorry, you must have PyQt 4.3.0 or higher or' \
                  ' a recent snapshot release.'
            sys.exit(3)
    print "PyQt Version: ", pyqtVersion
    
    #check version of QScintilla
    from PyQt4.Qsci import QSCINTILLA_VERSION_STR
    scintillaVersion = QSCINTILLA_VERSION_STR
    # always assume, that snapshots are new enough
    if scintillaVersion.find("snapshot-") == -1:
        while scintillaVersion.count('.') < 2:
            scintillaVersion += '.0'
        (maj, min, pat) = scintillaVersion.split('.')
        maj = int(maj)
        min = int(min)
        pat = int(pat)
        if maj < 2 or (maj == 2 and min < 2):
            print 'Sorry, you must have QScintilla 2.2.0 or higher or' \
                  ' a recent snapshot release.'
            sys.exit(4)
    print "QScintilla Version: ", QSCINTILLA_VERSION_STR
    print "All dependencies ok."
    print

def compileUiFiles():
    """
    Compile the .ui files to Python sources.
    """
    try:
        from PyQt4.uic import compileUiDir
    except ImportError:
        from PyQt4.uic import compileUi
        
        def compileUiDir(dir, recurse = False, map = None, **compileUi_args):
            """
            Creates Python modules from Qt Designer .ui files in a directory or
            directory tree.
            
            Note: This function is a modified version of the one found in PyQt4.

            @param dir Name of the directory to scan for files whose name ends with
                '.ui'. By default the generated Python module is created in the same
                directory ending with '.py'.
            @param recurse flag indicating that any sub-directories should be scanned.
            @param map an optional callable that is passed the name of the directory
                containing the '.ui' file and the name of the Python module that will be
                created. The callable should return a tuple of the name of the directory
                in which the Python module will be created and the (possibly modified)
                name of the module.
            @param compileUi_args any additional keyword arguments that are passed to
                the compileUi() function that is called to create each Python module.
            """
            def compile_ui(ui_dir, ui_file):
                """
                Local function to compile a single .ui file.
                
                @param ui_dir directory containing the .ui file (string)
                @param ui_file file name of the .ui file (string)
                """
                # Ignore if it doesn't seem to be a .ui file.
                if ui_file.endswith('.ui'):
                    py_dir = ui_dir
                    py_file = ui_file[:-3] + '.py'

                    # Allow the caller to change the name of the .py file or generate
                    # it in a different directory.
                    if map is not None:
                        py_dir, py_file = map(py_dir, py_file)

                    # Make sure the destination directory exists.
                    try:
                        os.makedirs(py_dir)
                    except:
                        pass

                    ui_path = os.path.join(ui_dir, ui_file)
                    py_path = os.path.join(py_dir, py_file)

                    ui_file = open(ui_path, 'r')
                    py_file = open(py_path, 'w')

                    try:
                        compileUi(ui_file, py_file, **compileUi_args)
                    finally:
                        ui_file.close()
                        py_file.close()

            if recurse:
                for root, _, files in os.walk(dir):
                    for ui in files:
                        compile_ui(root, ui)
            else:
                for ui in os.listdir(dir):
                    if os.path.isfile(os.path.join(dir, ui)):
                        compile_ui(dir, ui)
    
    def pyName(py_dir, py_file):
        """
        Local function to create the Python source file name for the compiled .ui file.
        
        @param py_dir suggested name of the directory (string)
        @param py_file suggested name for the compile source file (string)
        @return tuple of directory name (string) and source file name (string)
        """
        return py_dir, "Ui_%s" % py_file
    
    compileUiDir("eric", True, pyName)

def main(argv):
    """
    The main function of the script.

    @param argv the list of command line arguments.
    """
    import getopt

    # Parse the command line.
    global progName, modDir, doCleanup, doCompile, distDir, cfg, apisDir
    progName = os.path.basename(argv[0])

    initGlobals()

    try:
        if sys.platform.startswith("win"):
            optlist, args = getopt.getopt(argv[1:],"chxza:b:d:f:")
        else:
            optlist, args = getopt.getopt(argv[1:],"chxza:b:d:f:i:")
    except getopt.GetoptError:
        usage()

    global platBinDir
    
    depChecks = True

    for opt, arg in optlist:
        if opt == "-h":
            usage(0)
        elif opt == "-a":
            apisDir = arg
        elif opt == "-b":
            platBinDir = arg
        elif opt == "-d":
            modDir = arg
        elif opt == "-i":
            distDir = os.path.normpath(arg)
        elif opt == "-x":
            depChecks = False
        elif opt == "-c":
            doCleanup = False
        elif opt == "-z":
            doCompile = False
        elif opt == "-f":
            try:
                execfile(arg, globals())
                if len(cfg) != configLength:
                    print "The configuration dictionary in '%s' is incorrect. Aborting"\
                        % arg
                    sys.exit(6)
            except:
                cfg = {}
    
    if len(cfg) == 0:
        createInstallConfig()
    
    if depChecks:
        doDependancyChecks()
    
    # get rid of development config file, if it exists
    try:
        os.remove(os.path.join("eric", "eric4config.py"))
    except EnvironmentError:
        pass
    
    # cleanup old installation
    try:
        if doCleanup:
            if distDir:
                shutil.rmtree(distDir, True)
            else:
                cleanUp()
    except IOError, msg:
        sys.stderr.write('IOError: %s\nTry install as root.\n' % msg)

    # Create a config file and delete the default one
    createConfig()

    # Compile .ui files
    print "Compiling user interface files..."
    compileUiFiles()
    
    if doCompile:
        print "\nCompiling source files..."
        if distDir:
            compileall.compile_dir("eric", 
                                   ddir = os.path.join(distDir, modDir, cfg['ericDir']), 
                                   rx = re.compile("Python3"), 
                                   quiet = True)
            py_compile.compile("eric4config.py", 
                               dfile = os.path.join(distDir, modDir, "eric4config.py"))
        else:
            compileall.compile_dir("eric", 
                                   ddir = os.path.join(modDir, cfg['ericDir']), 
                                   rx = re.compile("Python3"), 
                                   quiet = True)
            py_compile.compile("eric4config.py", 
                               dfile = os.path.join(modDir, "eric4config.py"))
    print "\nInstalling eric4 ..."
    installEric()
    print "\nInstallation complete."
    print
    
    # check PyXML version and output a message for broken PyXML (< 0.8.6)
    try:
        import _xmlplus
        v = _xmlplus.version_info
        if v < (0, 8, 6):
            from eric4.patch_pyxml import isPatched, patchPyXML
            if not isPatched():
                print "NOTE:"
                print "    Found PyXML %d.%d.%d, which needs a patch to work correctly" % \
                    (v[0], v[1], v[2])
                print "    with foreign characters. Please see 'README-PyXML.txt' for"
                print "    details."
                res = raw_input("    Shall pyXML be patched now (y/n)? ")
                if res in ["Y", "y"]:
                    patchPyXML()
    except ImportError:
        pass
    
    #check version of PyQt
    from PyQt4.QtCore import PYQT_VERSION_STR
    pyqtVersion = PYQT_VERSION_STR
    # always assume, that snapshots are new enough
    if pyqtVersion.find("snapshot-") == -1:
        while pyqtVersion.count('.') < 2:
            pyqtVersion += '.0'
        (maj, min, pat) = pyqtVersion.split('.')
        maj = int(maj)
        min = int(min)
        pat = int(pat)
        if min < 5:
            print
            print "You have to patch PyQt QNetworkAccessManager."
            print "See the patches directory for details."
    
    print
    if sys.platform.startswith("win"):
        raw_input("Press enter to continue...")
    
    
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
