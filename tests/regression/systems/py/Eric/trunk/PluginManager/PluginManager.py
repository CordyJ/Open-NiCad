# -*- coding: utf-8 -*-

# Copyright (c) 2007 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the Plugin Manager.
"""

import os
import sys
import imp

from PyQt4.QtCore import *
from PyQt4.QtGui import QPixmap

from KdeQt import KQMessageBox

from PluginExceptions import *

import UI.PixmapCache

import Utilities
import Preferences

from eric4config import getConfig

class PluginManager(QObject):
    """
    Class implementing the Plugin Manager.
    
    @signal shutdown() emitted at shutdown of the IDE
    @signal pluginAboutToBeActivated(modulName, pluginObject) emitted just before a
        plugin is activated
    @signal pluginActivated(modulName, pluginObject) emitted just after a plugin
        was activated
    @signal allPlugginsActivated() emitted at startup after all plugins have
        been activated
    @signal pluginAboutToBeDeactivated(modulName, pluginObject) emitted just before a
        plugin is deactivated
    @signal pluginDeactivated(modulName, pluginObject) emitted just after a plugin
        was deactivated
    """
    def __init__(self, parent = None, doLoadPlugins = True, develPlugin = None):
        """
        Constructor
        
        The Plugin Manager deals with three different plugin directories.
        The first is the one, that is part of eric4 (eric4/Plugins). The
        second one is the global plugin directory called 'eric4plugins', 
        which is located inside the site-packages directory. The last one
        is the user plugin directory located inside the .eric4 directory
        of the users home directory.
        
        @param parent reference to the parent object (QObject)
        @keyparam doLoadPlugins flag indicating, that plugins should 
            be loaded (boolean)
        @keyparam develPlugin filename of a plugin to be loaded for 
            development (string)
        """
        QObject.__init__(self, parent)
        
        self.__ui = parent
        self.__develPluginFile = develPlugin
        self.__develPluginName = None
        
        self.__inactivePluginsKey = "PluginManager/InactivePlugins"
        
        self.pluginDirs = {
            "eric4"  : os.path.join(getConfig('ericDir'), "Plugins"), 
            "global" : os.path.join(Utilities.getPythonModulesDirectory(), 
                                    "eric4plugins"), 
            "user"   : os.path.join(Utilities.getConfigDir(), "eric4plugins"), 
        }
        self.__priorityOrder = ["eric4", "global", "user"]
        
        self.__defaultDownloadDir = os.path.join(Utilities.getConfigDir(), "Downloads")
        
        self.__activePlugins = {}
        self.__inactivePlugins = {}
        self.__onDemandActivePlugins = {}
        self.__onDemandInactivePlugins = {}
        self.__activeModules = {}
        self.__inactiveModules = {}
        self.__onDemandActiveModules = {}
        self.__onDemandInactiveModules = {}
        self.__failedModules = {}
        
        self.__foundCoreModules = []
        self.__foundGlobalModules = []
        self.__foundUserModules = []
        
        self.__modulesCount = 0
        
        pdirsExist, msg = self.__pluginDirectoriesExist()
        if not pdirsExist:
            raise PluginPathError(msg)
        
        if doLoadPlugins:
            if not self.__pluginModulesExist():
                raise PluginModulesError
            
            self.__insertPluginsPaths()
            
            self.__loadPlugins()
        
        self.__checkPluginsDownloadDirectory()
    
    def finalizeSetup(self):
        """
        Public method to finalize the setup of the plugin manager.
        """
        for module in self.__onDemandInactiveModules.values() + \
                      self.__onDemandActiveModules.values():
            if hasattr(module, "moduleSetup"):
                module.moduleSetup()
        
    def getPluginDir(self, key):
        """
        Public method to get the path of a plugin directory.
        
        @return path of the requested plugin directory (string)
        """
        if key not in ["global", "user"]:
            return None
        else:
            try:
                return self.pluginDirs[key]
            except KeyError:
                return None
    
    def __pluginDirectoriesExist(self):
        """
        Private method to check, if the plugin folders exist.
        
        If the plugin folders don't exist, they are created (if possible).
        
        @return tuple of a flag indicating existence of any of the plugin 
            directories (boolean) and a message (QString)
        """
        if self.__develPluginFile:
            path = Utilities.splitPath(self.__develPluginFile)[0]
            fname = os.path.join(path, "__init__.py")
            if not os.path.exists(fname):
                try:
                    f = open(fname, "wb")
                    f.close()
                except IOError:
                    return (False, 
                        self.trUtf8("Could not create a package for %1.")\
                            .arg(self.__develPluginFile))
        
        if Preferences.getPluginManager("ActivateExternal"):
            fname = os.path.join(self.pluginDirs["user"], "__init__.py")
            if not os.path.exists(fname):
                if not os.path.exists(self.pluginDirs["user"]):
                    os.mkdir(self.pluginDirs["user"],  0755)
                try:
                    f = open(fname, "wb")
                    f.close()
                except IOError:
                    del self.pluginDirs["user"]
            
            if not os.path.exists(self.pluginDirs["global"]) and \
               os.access(Utilities.getPythonModulesDirectory(), os.W_OK):
                # create the global plugins directory
                os.mkdir(self.pluginDirs["global"], 0755)
                fname = os.path.join(self.pluginDirs["global"], "__init__.py")
                f = open(fname, "wb")
                f.write('# -*- coding: utf-8 -*-' + os.linesep)
                f.write(os.linesep)
                f.write('"""' + os.linesep)
                f.write('Package containing the global plugins.' + os.linesep)
                f.write('"""' + os.linesep)
                f.close()
            if not os.path.exists(self.pluginDirs["global"]):
                del self.pluginDirs["global"]
        else:
            del self.pluginDirs["user"]
            del self.pluginDirs["global"]
        
        if not os.path.exists(self.pluginDirs["eric4"]):
            return (False, 
                self.trUtf8("The internal plugin directory <b>%1</b> does not exits.")\
                    .arg(self.pluginDirs["eric4"]))
        
        return (True, "")
    
    def __pluginModulesExist(self):
        """
        Private method to check, if there are plugins available.
        
        @return flag indicating the availability of plugins (boolean)
        """
        if self.__develPluginFile and not os.path.exists(self.__develPluginFile):
            return False
        
        self.__foundCoreModules = self.getPluginModules(self.pluginDirs["eric4"])
        if self.pluginDirs.has_key("global"):
            self.__foundGlobalModules = \
                self.getPluginModules(self.pluginDirs["global"])
        if self.pluginDirs.has_key("user"):
            self.__foundUserModules = \
                self.getPluginModules(self.pluginDirs["user"])
        
        return len(self.__foundCoreModules + self.__foundGlobalModules + \
                   self.__foundUserModules) > 0
    
    def getPluginModules(self, pluginPath):
        """
        Public method to get a list of plugin modules.
        
        @param pluginPath name of the path to search (string)
        @return list of plugin module names (list of string)
        """
        pluginFiles = [f[:-3] for f in os.listdir(pluginPath) \
                       if self.isValidPluginName(f)]
        return pluginFiles[:]
    
    def isValidPluginName(self, pluginName):
        """
        Public methode to check, if a file name is a valid plugin name.
        
        Plugin modules must start with "Plugin" and have the extension ".py".
        
        @param pluginName name of the file to be checked (string)
        @return flag indicating a valid plugin name (boolean)
        """
        return pluginName.startswith("Plugin") and pluginName.endswith(".py")
    
    def __insertPluginsPaths(self):
        """
        Private method to insert the valid plugin paths intos the search path.
        """
        for key in self.__priorityOrder:
            if self.pluginDirs.has_key(key):
                if not self.pluginDirs[key] in sys.path:
                    sys.path.insert(2, self.pluginDirs[key])
                UI.PixmapCache.addSearchPath(self.pluginDirs[key])
        
        if self.__develPluginFile:
            path = Utilities.splitPath(self.__develPluginFile)[0]
            if not path in sys.path:
                sys.path.insert(2, path)
            UI.PixmapCache.addSearchPath(path)
    
    def __loadPlugins(self):
        """
        Private method to load the plugins found.
        """
        develPluginName = ""
        if self.__develPluginFile:
            develPluginPath, develPluginName = \
                Utilities.splitPath(self.__develPluginFile)
            if self.isValidPluginName(develPluginName):
                develPluginName = develPluginName[:-3]
        
        for pluginName in self.__foundCoreModules:
            # global and user plugins have priority
            if pluginName not in self.__foundGlobalModules and \
               pluginName not in self.__foundUserModules and \
               pluginName != develPluginName:
                self.loadPlugin(pluginName, self.pluginDirs["eric4"])
        
        for pluginName in self.__foundGlobalModules:
            # user plugins have priority
            if pluginName not in self.__foundUserModules and \
               pluginName != develPluginName:
                self.loadPlugin(pluginName, self.pluginDirs["global"])
        
        for pluginName in self.__foundUserModules:
            if pluginName != develPluginName:
                self.loadPlugin(pluginName, self.pluginDirs["user"])
        
        if develPluginName:
            self.loadPlugin(develPluginName, develPluginPath)
            self.__develPluginName = develPluginName
    
    def loadPlugin(self, name, directory, reload_ = False):
        """
        Public method to load a plugin module.
        
        Initially all modules are inactive. Modules that are requested on
        demand are sorted out and are added to the on demand list. Some
        basic validity checks are performed as well. Modules failing these
        checks are added to the failed modules list.
        
        @param name name of the module to be loaded (string)
        @param directory name of the plugin directory (string)
        @param reload_ flag indicating to reload the module (boolean)
        """
        try:
            fname = "%s.py" % os.path.join(directory, name)
            module = imp.load_source(name, fname)
            if not hasattr(module, "autoactivate"):
                module.error = \
                    self.trUtf8("Module is missing the 'autoactivate' attribute.")
                self.__failedModules[name] = module
                raise PluginLoadError(name)
            if getattr(module, "autoactivate"):
                self.__inactiveModules[name] = module
            else:
                if not hasattr(module, "pluginType") or \
                   not hasattr(module, "pluginTypename"):
                    module.error = \
                        self.trUtf8("Module is missing the 'pluginType' "
                                    "and/or 'pluginTypename' attributes.")
                    self.__failedModules[name] = module
                    raise PluginLoadError(name)
                else:
                    self.__onDemandInactiveModules[name] = module
            module.eric4PluginModuleName = name
            module.eric4PluginModuleFilename = fname
            self.__modulesCount += 1
            if reload_:
                reload(module)
        except PluginLoadError:
            print "Error loading plugin module:", name
        except StandardError, err:
            module = imp.new_module(name)
            module.error = \
                self.trUtf8("Module failed to load. Error: %1").arg(unicode(err))
            self.__failedModules[name] = module
            print "Error loading plugin module:",  name
            print unicode(err)
    
    def unloadPlugin(self, name, directory):
        """
        Public method to unload a plugin module.
        
        @param name name of the module to be unloaded (string)
        @param directory name of the plugin directory (string)
        @return flag indicating success (boolean)
        """
        fname = "%s.py" % os.path.join(directory, name)
        if self.__onDemandActiveModules.has_key(name) and \
           self.__onDemandActiveModules[name].eric4PluginModuleFilename == fname:
            # cannot unload an ondemand plugin, that is in use
            return False
        
        if self.__activeModules.has_key(name) and \
           self.__activeModules[name].eric4PluginModuleFilename == fname:
            self.deactivatePlugin(name)
        
        if self.__inactiveModules.has_key(name) and \
           self.__inactiveModules[name].eric4PluginModuleFilename == fname:
            try:
                del self.__inactivePlugins[name]
            except KeyError:
                pass
            del self.__inactiveModules[name]
        elif self.__onDemandInactiveModules.has_key(name) and \
             self.__onDemandInactiveModules[name].eric4PluginModuleFilename == fname:
            try:
                del self.__onDemandInactivePlugins[name]
            except KeyError:
                pass
            del self.__onDemandInactiveModules[name]
        elif self.__failedModules.has_key(name):
            del self.__failedModules[name]
        
        self.__modulesCount -= 1
        return True
    
    def removePluginFromSysModules(self, pluginName, package, internalPackages):
        """
        Public method to remove a plugin and all related modules from sys.modules.
        
        @param pluginName name of the plugin module (string)
        @param package name of the plugin package (string)
        @param internalPackages list of intenal packages (list of string)
        @return flag indicating the plugin module was found in sys.modules (boolean)
        """
        packages = [package] + internalPackages
        found = False
        if not package:
            package = "__None__"
        for moduleName in sys.modules.keys()[:]:
            if moduleName == pluginName or moduleName.split(".")[0] in packages:
                found = True
                del sys.modules[moduleName]
        return found
    
    def initOnDemandPlugins(self):
        """
        Public method to create plugin objects for all on demand plugins.
        
        Note: The plugins are not activated.
        """
        names = sorted(self.__onDemandInactiveModules.keys())
        for name in names:
            self.initOnDemandPlugin(name)
    
    def initOnDemandPlugin(self, name):
        """
        Public method to create a plugin object for the named on demand plugin.
        
        Note: The plugin is not activated.
        """
        try:
            try:
                module = self.__onDemandInactiveModules[name]
            except KeyError:
                return None
            
            if not self.__canActivatePlugin(module):
                raise PluginActivationError(module.eric4PluginModuleName)
            version = getattr(module, "version")
            className = getattr(module, "className")
            pluginClass = getattr(module, className)
            pluginObject = None
            if not self.__onDemandInactivePlugins.has_key(name):
                pluginObject = pluginClass(self.__ui)
                pluginObject.eric4PluginModule = module
                pluginObject.eric4PluginName = className
                pluginObject.eric4PluginVersion = version
                self.__onDemandInactivePlugins[name] = pluginObject
        except PluginActivationError:
            return None
    
    def activatePlugins(self):
        """
        Public method to activate all plugins having the "autoactivate" attribute
        set to True.
        """
        ial = Preferences.Prefs.settings.value(self.__inactivePluginsKey)
        if ial.isValid():
            savedInactiveList = ial.toStringList()
        else:
            savedInactiveList = None
        if self.__develPluginName is not None and savedInactiveList is not None:
            savedInactiveList.removeAll(self.__develPluginName)
        names = self.__inactiveModules.keys()
        names.sort()
        for name in names:
            if savedInactiveList is None or name not in savedInactiveList:
                self.activatePlugin(name)
        self.emit(SIGNAL("allPlugginsActivated()"))
    
    def activatePlugin(self, name, onDemand = False):
        """
        Public method to activate a plugin.
        
        @param name name of the module to be activated
        @keyparam onDemand flag indicating activation of an 
            on demand plugin (boolean)
        @return reference to the initialized plugin object
        """
        try:
            try:
                if onDemand:
                    module = self.__onDemandInactiveModules[name]
                else:
                    module = self.__inactiveModules[name]
            except KeyError:
                return None
            
            if not self.__canActivatePlugin(module):
                raise PluginActivationError(module.eric4PluginModuleName)
            version = getattr(module, "version")
            className = getattr(module, "className")
            pluginClass = getattr(module, className)
            pluginObject = None
            if onDemand and self.__onDemandInactivePlugins.has_key(name):
                pluginObject = self.__onDemandInactivePlugins[name]
            elif not onDemand and self.__inactivePlugins.has_key(name):
                pluginObject = self.__inactivePlugins[name]
            else:
                pluginObject = pluginClass(self.__ui)
            self.emit(SIGNAL("pluginAboutToBeActivated"), name, pluginObject)
            try:
                obj, ok = pluginObject.activate()
            except TypeError:
                module.error = self.trUtf8("Incompatible plugin activation method.")
                obj = None
                ok = True
            except StandardError, err:
                module.error = QString(unicode(err))
                obj = None
                ok = False
            if not ok:
                return None
            
            self.emit(SIGNAL("pluginActivated"), name, pluginObject)
            pluginObject.eric4PluginModule = module
            pluginObject.eric4PluginName = className
            pluginObject.eric4PluginVersion = version
            
            if onDemand:
                self.__onDemandInactiveModules.pop(name)
                try:
                    self.__onDemandInactivePlugins.pop(name)
                except KeyError:
                    pass
                self.__onDemandActivePlugins[name] = pluginObject
                self.__onDemandActiveModules[name] = module
            else:
                self.__inactiveModules.pop(name)
                try:
                    self.__inactivePlugins.pop(name)
                except KeyError:
                    pass
                self.__activePlugins[name] = pluginObject
                self.__activeModules[name] = module
            return obj
        except PluginActivationError:
            return None
    
    def __canActivatePlugin(self, module):
        """
        Private method to check, if a plugin can be activated.
        
        @param module reference to the module to be activated
        @return flag indicating, if the module satisfies all requirements
            for being activated (boolean)
        """
        try:
            if not hasattr(module, "version"):
                raise PluginModuleFormatError(module.eric4PluginModuleName, "version")
            if not hasattr(module, "className"):
                raise PluginModuleFormatError(module.eric4PluginModuleName, "className")
            className = getattr(module, "className")
            if not hasattr(module, className):
                raise PluginModuleFormatError(module.eric4PluginModuleName, className)
            pluginClass = getattr(module, className)
            if not hasattr(pluginClass, "__init__"):
                raise PluginClassFormatError(module.eric4PluginModuleName, 
                    className, "__init__")
            if not hasattr(pluginClass, "activate"):
                raise PluginClassFormatError(module.eric4PluginModuleName, 
                    className, "activate")
            if not hasattr(pluginClass, "deactivate"):
                raise PluginClassFormatError(module.eric4PluginModuleName, 
                    className, "deactivate")
            return True
        except PluginModuleFormatError, e:
            print repr(e)
            return False
        except PluginClassFormatError, e:
            print repr(e)
            return False
    
    def deactivatePlugin(self, name, onDemand = False):
        """
        Public method to deactivate a plugin.
        
        @param name name of the module to be deactivated
        @keyparam onDemand flag indicating deactivation of an 
            on demand plugin (boolean)
        """
        try:
            if onDemand:
                module = self.__onDemandActiveModules[name]
            else:
                module = self.__activeModules[name]
        except KeyError:
            return
        
        if self.__canDeactivatePlugin(module):
            pluginObject = None
            if onDemand and self.__onDemandActivePlugins.has_key(name):
                pluginObject = self.__onDemandActivePlugins[name]
            elif not onDemand and self.__activePlugins.has_key(name):
                pluginObject = self.__activePlugins[name]
            if pluginObject:
                self.emit(SIGNAL("pluginAboutToBeDeactivated"), name, pluginObject)
                pluginObject.deactivate()
                self.emit(SIGNAL("pluginDeactivated"), name, pluginObject)
                
                if onDemand:
                    self.__onDemandActiveModules.pop(name)
                    self.__onDemandActivePlugins.pop(name)
                    self.__onDemandInactivePlugins[name] = pluginObject
                    self.__onDemandInactiveModules[name] = module
                else:
                    self.__activeModules.pop(name)
                    try:
                        self.__activePlugins.pop(name)
                    except KeyError:
                        pass
                    self.__inactivePlugins[name] = pluginObject
                    self.__inactiveModules[name] = module
    
    def __canDeactivatePlugin(self, module):
        """
        Private method to check, if a plugin can be deactivated.
        
        @param module reference to the module to be deactivated
        @return flag indicating, if the module satisfies all requirements
            for being deactivated (boolean)
        """
        return getattr(module, "deactivateable", True)
    
    def getPluginObject(self, type_, typename, maybeActive = False):
        """
        Public method to activate an ondemand plugin given by type and typename.
        
        @param type_ type of the plugin to be activated (string)
        @param typename name of the plugin within the type category (string)
        @keyparam maybeActive flag indicating, that the plugin may be active
            already (boolean)
        @return reference to the initialized plugin object
        """
        for name, module in self.__onDemandInactiveModules.items():
            if getattr(module, "pluginType") == type_ and \
               getattr(module, "pluginTypename") == typename:
                return self.activatePlugin(name, onDemand = True)
        
        if maybeActive:
            for name, module in self.__onDemandActiveModules.items():
                if getattr(module, "pluginType") == type_ and \
                   getattr(module, "pluginTypename") == typename:
                    self.deactivatePlugin(name, onDemand = True)
                    return self.activatePlugin(name, onDemand = True)
        
        return None
    
    def getPluginInfos(self):
        """
        Public method to get infos about all loaded plugins.
        
        @return list of tuples giving module name (string), plugin name (string),
            version (string), autoactivate (boolean), active (boolean), 
            short description (string), error flag (boolean)
        """
        infos = []
        
        for name in self.__activeModules.keys():
            pname,  shortDesc, error, version = \
                self.__getShortInfo(self.__activeModules[name])
            infos.append((name,  pname, version, True, True, shortDesc, error))
        for name in self.__inactiveModules.keys():
            pname,  shortDesc, error, version = \
                self.__getShortInfo(self.__inactiveModules[name])
            infos.append((name,  pname, version, True, False, shortDesc, error))
        for name in self.__onDemandActiveModules.keys():
            pname,  shortDesc, error, version = \
                self.__getShortInfo(self.__onDemandActiveModules[name])
            infos.append((name,  pname, version, False, True, shortDesc, error))
        for name in self.__onDemandInactiveModules.keys():
            pname,  shortDesc, error, version = \
                self.__getShortInfo(self.__onDemandInactiveModules[name])
            infos.append((name,  pname, version, False, False, shortDesc, error))
        for name in self.__failedModules.keys():
            pname,  shortDesc, error, version = \
                self.__getShortInfo(self.__failedModules[name])
            infos.append((name,  pname, version, False, False, shortDesc, error))
        return infos
    
    def __getShortInfo(self, module):
        """
        Private method to extract the short info from a module.
        
        @param module module to extract short info from
        @return short info as a tuple giving plugin name (string), 
            short description (string), error flag (boolean) and
            version (string)
        """
        name = getattr(module, "name", "")
        shortDesc = getattr(module, "shortDescription", "")
        version = getattr(module, "version", "")
        error = not getattr(module, "error", QString("")).isEmpty()
        return name, shortDesc, error, version
    
    def getPluginDetails(self, name):
        """
        Public method to get detailed information about a plugin.
        
        @param name name of the module to get detailed infos about (string)
        @return details of the plugin as a dictionary
        """
        details = {}
        
        autoactivate = True
        active = True
        
        if self.__activeModules.has_key(name):
            module = self.__activeModules[name]
        elif self.__inactiveModules.has_key(name):
            module = self.__inactiveModules[name]
            active = False
        elif self.__onDemandActiveModules.has_key(name):
            module = self.__onDemandActiveModules[name]
            autoactivate = False
        elif self.__onDemandInactiveModules.has_key(name):
            module = self.__onDemandInactiveModules[name]
            autoactivate = False
            active = False
        elif self.__failedModules.has_key(name):
            module = self.__failedModules[name]
            autoactivate = False
            active = False
        else:
            # should not happen
            return None
        
        details["moduleName"] = name
        details["moduleFileName"] = getattr(module, "eric4PluginModuleFilename", "")
        details["pluginName"] = getattr(module, "name", "")
        details["version"] = getattr(module, "version", "")
        details["author"] = getattr(module, "author", "")
        details["description"] = getattr(module, "longDescription", "")
        details["autoactivate"] = autoactivate
        details["active"] = active
        details["error"] = getattr(module, "error", QString(""))
        
        return details
    
    def shutdown(self):
        """
        Public method called to perform actions upon shutdown of the IDE.
        """
        names = QStringList()
        for name in self.__inactiveModules.keys():
            names.append(name)
        Preferences.Prefs.settings.setValue(self.__inactivePluginsKey, QVariant(names))
        
        self.emit(SIGNAL("shutdown()"))

    def getPluginDisplayStrings(self, type_):
        """
        Public method to get the display strings of all plugins of a specific type.
        
        @param type_ type of the plugins (string)
        @return dictionary with name as key and display string as value
            (dictionary of QString)
        """
        pluginDict = {}
        
        for name, module in \
            self.__onDemandActiveModules.items() + self.__onDemandInactiveModules.items():
            if getattr(module, "pluginType") == type_ and \
               getattr(module, "error", QString("")).isEmpty():
                plugin_name = getattr(module, "pluginTypename")
                if hasattr(module, "displayString"):
                    try:
                        disp = module.displayString()
                    except TypeError:
                        disp = getattr(module, "displayString")
                    if disp != "":
                        pluginDict[plugin_name] = disp
                else:
                    pluginDict[plugin_name] = QString(plugin_name)
        
        return pluginDict
        
    def getPluginPreviewPixmap(self, type_, name):
        """
        Public method to get a preview pixmap of a plugin of a specific type.
        
        @param type_ type of the plugin (string)
        @param name name of the plugin type (string)
        @return preview pixmap (QPixmap)
        """
        for modname, module in \
            self.__onDemandActiveModules.items() + self.__onDemandInactiveModules.items():
            if getattr(module, "pluginType") == type_ and \
               getattr(module, "pluginTypename") == name:
                if hasattr(module, "previewPix"):
                    return module.previewPix()
                else:
                    return QPixmap()
        
        return QPixmap()
        
    def getPluginApiFiles(self, language):
        """
        Public method to get the list of API files installed by a plugin.
        
        @param language language of the requested API files (QString)
        @return list of API filenames (list of string)
        """
        apis = []
        
        for module in self.__activeModules.values() + \
                      self.__onDemandActiveModules.values():
            if hasattr(module, "apiFiles"):
                apis.extend(module.apiFiles(language))
        
        return apis
        
    def getPluginExeDisplayData(self):
        """
        Public method to get data to display information about a plugins
        external tool.
        
        @return list of dictionaries containing the data. Each dictionary must
            either contain data for the determination or the data to be displayed.<br />
            A dictionary of the first form must have the following entries:
            <ul>
                <li>programEntry - indicator for this dictionary form (boolean),
                    always True</li>
                <li>header - string to be diplayed as a header (QString)</li>
                <li>exe - the executable (string)</li>
                <li>versionCommand - commandline parameter for the exe (string)</li>
                <li>versionStartsWith - indicator for the output line containing
                    the version (string)</li>
                <li>versionPosition - number of element containing the 
                    version (integer)</li>
                <li>version - version to be used as default (string)</li>
                <li>versionCleanup - tuple of two integers giving string positions
                    start and stop for the version string (tuple of integers)</li>
            </ul>
            A dictionary of the second form must have the following entries:
            <ul>
                <li>programEntry - indicator for this dictionary form (boolean),
                    always False</li>
                <li>header - string to be diplayed as a header (QString)</li>
                <li>text - entry text to be shown (string or QString)</li>
                <li>version - version text to be shown (string or QString)</li>
            </ul>
        """
        infos = []
        
        for module in self.__activeModules.values() + \
                      self.__inactiveModules.values():
            if hasattr(module, "exeDisplayData"):
                infos.append(module.exeDisplayData())
        for module in self.__onDemandActiveModules.values() + \
                      self.__onDemandInactiveModules.values():
            if hasattr(module, "exeDisplayData"):
                infos.append(module.exeDisplayData())
        
        return infos
        
    def getPluginConfigData(self):
        """
        Public method to get the config data of all active, non on-demand plugins
        used by the configuration dialog.
        
        Plugins supporting this functionality must provide the plugin module
        function 'getConfigData' returning a dictionary with unique keys
        of lists with the following list contents:
        <dl>
          <dt>display string</dt>
          <dd>string shown in the selection area of the configuration page.
              This should be a localized string</dd>
          <dt>pixmap name</dt>
          <dd>filename of the pixmap to be shown next to the display string</dd>
          <dt>page creation function</dt>
          <dd>plugin module function to be called to create the configuration
              page. The page must be subclasses from 
              Preferences.ConfigurationPages.ConfigurationPageBase and must
              implement a method called 'save' to save the settings. A parent
              entry will be created in the selection list, if this value is None.</dd>
          <dt>parent key</dt>
          <dd>dictionary key of the parent entry or None, if this defines a 
              toplevel entry.</dd>
          <dt>reference to configuration page</dt>
          <dd>This will be used by the configuration dialog and must always be None</dd>
        </dl>
        """
        configData = {}
        for module in self.__activeModules.values() + \
                      self.__onDemandActiveModules.values() + \
                      self.__onDemandInactiveModules.values():
            if hasattr(module, 'getConfigData'):
                configData.update(module.getConfigData())
        return configData
        
    def isPluginLoaded(self, pluginName):
        """
        Public method to check, if a certain plugin is loaded.
        
        @param pluginName name of the plugin to check for (string or QString)
        @return flag indicating, if the plugin is loaded (boolean)
        """
        return unicode(pluginName) in self.__activeModules.keys() or \
               unicode(pluginName) in self.__inactiveModules.keys() or \
               unicode(pluginName) in self.__onDemandActiveModules.keys() or \
               unicode(pluginName) in self.__onDemandInactiveModules.keys()
        
    def isPluginActive(self, pluginName):
        """
        Public method to check, if a certain plugin is active.
        
        @param pluginName name of the plugin to check for (string or QString)
        @return flag indicating, if the plugin is active (boolean)
        """
        return unicode(pluginName) in self.__activeModules.keys() or \
               unicode(pluginName) in self.__onDemandActiveModules.keys()
    
    ############################################################################
    ## Specialized plugin module handling methods below
    ############################################################################
    
    ############################################################################
    ## VCS related methods below
    ############################################################################
    
    def getVcsSystemIndicators(self):
        """
        Public method to get the Vcs System indicators.
        
        Plugins supporting this functionality must support the module function
        getVcsSystemIndicator returning a dictionary with indicator as key and
        a tuple with the vcs name (string) and vcs display string (QString).
        
        @return dictionary with indicator as key and a list of tuples as values.
            Each tuple contains the vcs name (string) and vcs display string (QString).
        """
        vcsDict = {}
        
        for name, module in \
            self.__onDemandActiveModules.items() + self.__onDemandInactiveModules.items():
            if getattr(module, "pluginType") == "version_control":
                if hasattr(module, "getVcsSystemIndicator"):
                    res = module.getVcsSystemIndicator()
                    for indicator, vcsData in res.items():
                        if vcsDict.has_key(indicator):
                            vcsDict[indicator].append(vcsData)
                        else:
                            vcsDict[indicator] = [vcsData]
        
        return vcsDict
    
    def deactivateVcsPlugins(self):
        """
        Public method to deactivated all activated VCS plugins.
        """
        for name, module in self.__onDemandActiveModules.items():
            if getattr(module, "pluginType") == "version_control":
                self.deactivatePlugin(name, True)

    def __checkPluginsDownloadDirectory(self):
        """
        Private slot to check for the existance of the plugins download directory.
        """
        downloadDir = unicode(Preferences.getPluginManager("DownloadPath"))
        if not downloadDir:
            downloadDir = self.__defaultDownloadDir
        
        if not os.path.exists(downloadDir):
            try:
                os.mkdir(downloadDir, 0755)
            except (OSError, IOError), err:
                # try again with (possibly) new default
                downloadDir = self.__defaultDownloadDir
                if not os.path.exists(downloadDir):
                    try:
                        os.mkdir(downloadDir, 0755)
                    except (OSError, IOError), err:
                        KQMessageBox.critical(self.__ui,
                            self.trUtf8("Plugin Manager Error"),
                            self.trUtf8("""<p>The plugin download directory <b>%1</b> """
                                        """could not be created. Please configure it """
                                        """via the configuration dialog.</p>"""
                                        """<p>Reason: %2</p>""")\
                                .arg(downloadDir).arg(unicode(err)))
                        downloadDir = ""
        
        Preferences.setPluginManager("DownloadPath", downloadDir)
    
    def preferencesChanged(self):
        """
        Public slot to react to changes in configuration.
        """
        self.__checkPluginsDownloadDirectory()
