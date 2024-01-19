# -*- coding: utf-8 -*-

# Copyright (c) 2004 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Compatibility module to use KApplication instead of QApplication.
"""

import os
import sys

import Preferences

class KQApplicationMixin(object):
    """
    Private mixin class implementing methods common to both KQApplication bases.
    """
    def __init__(self):
        """
        Constructor
        """
        self.__objectRegistry = {}
        self.__pluginObjectRegistry = {}
        
    def registerObject(self, name, object):
        """
        Public method to register an object in the object registry.
        
        @param name name of the object (string)
        @param object reference to the object
        @exception KeyError raised when the given name is already in use
        """
        if self.__objectRegistry.has_key(name):
            raise KeyError('Object "%s" already registered.' % name)
        else:
            self.__objectRegistry[name] = object
        
    def getObject(self, name):
        """
        Public method to get a reference to a registered object.
        
        @param name name of the object (string)
        @return reference to the registered object
        @exception KeyError raised when the given name is not known
        """
        if self.__objectRegistry.has_key(name):
            return self.__objectRegistry[name]
        else:
            raise KeyError('Object "%s" is not registered.' % name)
        
    def registerPluginObject(self, name, object, pluginType = None):
        """
        Public method to register a plugin object in the object registry.
        
        @param name name of the plugin object (string)
        @param object reference to the plugin object
        @keyparam pluginType type of the plugin object (string)
        @exception KeyError raised when the given name is already in use
        """
        if self.__pluginObjectRegistry.has_key(name):
            raise KeyError('Pluginobject "%s" already registered.' % name)
        else:
            self.__pluginObjectRegistry[name] = (object, pluginType)
        
    def unregisterPluginObject(self, name):
        """
        Public method to unregister a plugin object in the object registry.
        
        @param name name of the plugin object (string)
        """
        if self.__pluginObjectRegistry.has_key(name):
            del self.__pluginObjectRegistry[name]
        
    def getPluginObject(self, name):
        """
        Public method to get a reference to a registered plugin object.
        
        @param name name of the plugin object (string)
        @return reference to the registered plugin object
        @exception KeyError raised when the given name is not known
        """
        if self.__pluginObjectRegistry.has_key(name):
            return self.__pluginObjectRegistry[name][0]
        else:
            raise KeyError('Pluginobject "%s" is not registered.' % name)
        
    def getPluginObjects(self):
        """
        Public method to get a list of (name, reference) pairs of all
        registered plugin objects.
        
        @return list of (name, reference) pairs
        """
        objects = []
        for name in self.__pluginObjectRegistry:
            objects.append((name, self.__pluginObjectRegistry[name][0]))
        return objects
        
    def getPluginObjectType(self, name):
        """
        Public method to get the type of a registered plugin object.
        
        @param name name of the plugin object (string)
        @return type of the plugin object (string)
        @exception KeyError raised when the given name is not known
        """
        if self.__pluginObjectRegistry.has_key(name):
            return self.__pluginObjectRegistry[name][1]
        else:
            raise KeyError('Pluginobject "%s" is not registered.' % name)

if Preferences.getUI("UseKDEDialogs") and not sys.e4nokde:
    try:
        from PyKDE4.kdecore import ki18n, KAboutData, KCmdLineArgs, KCmdLineOptions
        from PyKDE4.kdeui import KApplication
        
        from PyQt4.QtCore import QLocale
        
        from UI.Info import *
        
        import Preferences
        
        def _localeString():
            """
            Protected function to get the string for the configured locale.
            
            @return locale name (string)
            """
            loc = Preferences.getUILanguage()
            if loc is None:
                return "en_US"
        
            if loc == "System":
                loc = str(QLocale.system().name())
            if loc == "C":
                loc = "en_US"
            return loc
            
        class __kdeKQApplication(KApplication, KQApplicationMixin):
            """
            Compatibility class to use KApplication instead of Qt's QApplication.
            """
            def __init__(self, argv, opts):
                """
                Constructor
                
                @param argv command line arguments
                @param opts acceptable command line options
                """
                loc = _localeString()
                os.environ["KDE_LANG"] = loc
                
                aboutData = KAboutData(
                    Program, "kdelibs", ki18n(Program), Version, ki18n(""), 
                    KAboutData.License_GPL, ki18n(Copyright), ki18n ("none"), 
                    Homepage, BugAddress)
                sysargv = argv[:]
                KCmdLineArgs.init(sysargv, aboutData)
                
                if opts:
                    options = KCmdLineOptions()
                    for opt in opts:
                        if len(opt) == 2:
                            options.add(opt[0], ki18n(opt[1]))
                        else:
                            options.add(opt[0], ki18n(opt[1]), opt[2])
                    KCmdLineArgs.addCmdLineOptions(options)
                
                KApplication.__init__(self, True)
                KQApplicationMixin.__init__(self)
        
    except (ImportError, RuntimeError):
        sys.e4nokde = True
    
from PyQt4.QtCore import QEvent, Qt, qVersion
from PyQt4.QtGui import QApplication
class __qtKQApplication(QApplication, KQApplicationMixin):
    """
    Compatibility class to use QApplication.
    """
    def __init__(self, argv, opts):
        """
        Constructor
        
        @param argv command line arguments
        @param opts acceptable command line options (ignored)
        """
        QApplication.__init__(self, argv)
        KQApplicationMixin.__init__(self)

################################################################################

def KQApplication(argv, opts):
    """
    Public function to instantiate an application object.
    
    @param argv command line arguments
    @param opts acceptable command line options
    @return reference to the application object
    """
    if Preferences.getUI("UseKDEDialogs") and not sys.e4nokde:
        return __kdeKQApplication(argv, opts)
    else:
        return __qtKQApplication(argv, opts)

from PyQt4.QtCore import QCoreApplication
e4App = QCoreApplication.instance
