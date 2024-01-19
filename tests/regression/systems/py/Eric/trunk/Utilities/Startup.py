# -*- coding: utf-8 -*-

# Copyright (c) 2002 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing some startup helper funcions
"""

import os
import sys

from PyQt4.QtCore import QTranslator, QTextCodec, QLocale, QDir, SIGNAL, SLOT, \
    QLibraryInfo
from PyQt4.QtGui import QApplication

from KdeQt.KQApplication import KQApplication

import Preferences
import Utilities
from UI.Info import Version

import UI.PixmapCache

from eric4config import getConfig


def makeAppInfo(argv, name, arg, description, options = []):
    """
    Function to generate a dictionary describing the application.
    
    @param argv list of commandline parameters (list of strings)
    @param name name of the application (string)
    @param arg commandline arguments (string)
    @param description text describing the application (string)
    @param options list of additional commandline options
        (list of tuples of two strings (commandline option, option description)).
        The options --version, --help and -h are always present and must not
        be repeated in this list.
    @return dictionary describing the application
    """
    return {
        "bin": argv[0],
        "arg": arg,
        "name": name,
        "description": description,
        "version": Version,
        "options" : options
        }


def usage(appinfo, optlen = 12):
    """
    Function to show the usage information.
    
    @param appinfo dictionary describing the application
    @param optlen length of the field for the commandline option (integer)
    """
    options = [\
        ("--version",  "show the program's version number and exit"),
        ("-h, --help", "show this help message and exit")
    ]
    options.extend(appinfo["options"])
    
    print \
"""
Usage: %(bin)s [OPTIONS] %(arg)s

%(name)s - %(description)s
    
Options:""" % appinfo
    for opt in options:
        print "  %s  %s" % (opt[0].ljust(optlen), opt[1])
    sys.exit(0)


def version(appinfo):
    """
    Function to show the version information.
    
    @param appinfo dictionary describing the application
    """
    print \
"""
%(name)s %(version)s

%(description)s

Copyright (c) 2002 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
This is free software; see LICENSE.GPL3 for copying conditions.
There is NO warranty; not even for MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE.""" % appinfo
    sys.exit(0)


def handleArgs(argv, appinfo):
    """
    Function to handle the always present commandline options.
    
    @param argv list of commandline parameters (list of strings)
    @param appinfo dictionary describing the application
    @return index of the '--' option (integer). This is used to tell
        the application, that all additional option don't belong to
        the application.
    """
    ddindex = 30000     # arbitrarily large number
    args = {
        "--version": version,
        "--help": usage,
        "-h": usage
        }
    if '--' in argv:
        ddindex = argv.index("--")
    for a in args:
        if a in argv and argv.index(a) < ddindex:
            args[a](appinfo)
    return ddindex


def loadTranslatorForLocale(dirs, tn):
    """
    Function to find and load a specific translation.

    @param dirs Searchpath for the translations. (list of strings)
    @param tn The translation to be loaded. (string)
    @return Tuple of a status flag and the loaded translator. (int, QTranslator)
    """
    trans = QTranslator(None)
    for dir in dirs:
        loaded = trans.load(tn, dir)
        if loaded:
            return (trans, True)
    
    print "Warning: translation file '" + tn + "'could not be loaded."
    print "Using default."
    return (None, False)


def initializeResourceSearchPath():
    """
    Function to initialize the default mime source factory.
    """
    defaultIconPath = os.path.join(getConfig('ericIconDir'), "default")
    iconPaths = Preferences.getIcons("Path")
    for iconPath in iconPaths:
        if not iconPath.isEmpty():
            UI.PixmapCache.addSearchPath(iconPath)
    if not defaultIconPath in iconPaths:
        UI.PixmapCache.addSearchPath(defaultIconPath)

# the translator must not be deleted, therefore we save them here
loaded_translators = {}

def loadTranslators(qtTransDir, app, translationFiles = ()):
    """
    Function to load all required translations.
    
    @param qtTransDir directory of the Qt translations files (string)
    @param app reference to the application object (QApplication)
    @param translationFiles tuple of additional translations to
        be loaded (tuple of strings)
    @return the requested locale (string)
    """
    translations = ("qt", "eric4") + translationFiles
    loc = Preferences.getUILanguage()
    if loc is None:
        return

    if loc == "System":
        loc = str(QLocale.system().name())
    if loc != "C":
        dirs = [getConfig('ericTranslationsDir'), Utilities.getConfigDir()]
        if qtTransDir is not None:
            dirs.append(qtTransDir)

        loca = loc
        for tf in ["%s_%s" % (tr, loc) for tr in translations]:
            translator, ok = loadTranslatorForLocale(dirs, tf)
            loaded_translators[tf] = translator
            if ok:
                app.installTranslator(translator)
            else:
                if tf.startswith("eric4"):
                    loca = None
        loc = loca
    else:
        loc = None
    return loc

def simpleAppStartup(argv, appinfo, mwFactory, kqOptions = [], 
                     quitOnLastWindowClosed = True):
    """
    Function to start up an application that doesn't need a specialized start up.
    
    This function is used by all of eric4's helper programs.
    
    @param argv list of commandline parameters (list of strings)
    @param appinfo dictionary describing the application
    @param mwFactory factory function generating the main widget. This
        function must accept the following parameter.
        <dl>
            <dt>argv</dt>
            <dd>list of commandline parameters (list of strings)</dd>
        </dl>
    @keyparam kqOptions list of acceptable command line options. This is only
        used, if the application is running under KDE and pyKDE can be loaded
        successfully.
    @keyparam quitOnLastWindowClosed flag indicating to quit the application,
        if the last window was closed (boolean)
    """
    ddindex = handleArgs(argv, appinfo)
    app = KQApplication(argv, kqOptions)
    app.setQuitOnLastWindowClosed(quitOnLastWindowClosed)
    try:
        sys.setappdefaultencoding(str(Preferences.getSystem("StringEncoding")))
    except AttributeError:
        pass

    initializeResourceSearchPath()
    QApplication.setWindowIcon(UI.PixmapCache.getIcon("eric.png"))
    
    qt4TransDir = Preferences.getQt4TranslationsDir()
    if not qt4TransDir:
        qt4TransDir = QLibraryInfo.location(QLibraryInfo.TranslationsPath)
    loadTranslators(qt4TransDir, app)
    
    QTextCodec.setCodecForCStrings(\
        QTextCodec.codecForName(str(Preferences.getSystem("StringEncoding")))
    )
    
    w = mwFactory(argv)
    app.connect(app, SIGNAL("lastWindowClosed()"), app, SLOT("quit()"))
    w.show()
    
    return app.exec_()
