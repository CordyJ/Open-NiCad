# -*- coding: utf-8 -*-

# Copyright (c) 2007 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a dialog for plugin deinstallation.
"""

import sys
import os
import imp
import shutil

from PyQt4.QtGui import *
from PyQt4.QtCore import *

from KdeQt import KQMessageBox
from KdeQt.KQMainWindow import KQMainWindow

from PluginManager import PluginManager
from Ui_PluginUninstallDialog import Ui_PluginUninstallDialog

class PluginUninstallWidget(QWidget, Ui_PluginUninstallDialog):
    """
    Class implementing a dialog for plugin deinstallation.
    """
    def __init__(self, pluginManager, parent = None):
        """
        Constructor
        
        @param pluginManager reference to the plugin manager object
        @param parent parent of this dialog (QWidget)
        """
        QWidget.__init__(self, parent)
        self.setupUi(self)
        
        if pluginManager is None:
            # started as external plugin deinstaller
            self.__pluginManager = PluginManager(doLoadPlugins = False)
            self.__external = True
        else:
            self.__pluginManager = pluginManager
            self.__external = False
        
        self.pluginDirectoryCombo.addItem(self.trUtf8("User plugins directory"), 
            QVariant(self.__pluginManager.getPluginDir("user")))
        
        globalDir = self.__pluginManager.getPluginDir("global")
        if globalDir is not None and os.access(globalDir, os.W_OK):
            self.pluginDirectoryCombo.addItem(self.trUtf8("Global plugins directory"), 
                QVariant(globalDir))
    
    @pyqtSignature("int")
    def on_pluginDirectoryCombo_currentIndexChanged(self, index):
        """
        Private slot to populate the plugin name combo upon a change of the
        plugin area.
        
        @param index index of the selected item (integer)
        """
        pluginDirectory = unicode(self.pluginDirectoryCombo\
                .itemData(index).toString())
        pluginNames = self.__pluginManager.getPluginModules(pluginDirectory)
        pluginNames.sort()
        self.pluginNameCombo.clear()
        for pluginName in pluginNames:
            fname = "%s.py" % os.path.join(pluginDirectory, pluginName)
            self.pluginNameCombo.addItem(pluginName, QVariant(fname))
        self.buttonBox.button(QDialogButtonBox.Ok)\
            .setEnabled(not self.pluginNameCombo.currentText().isEmpty())
    
    @pyqtSignature("")
    def on_buttonBox_accepted(self):
        """
        Private slot to handle the accepted signal of the button box.
        """
        if self.__uninstallPlugin():
            self.emit(SIGNAL("accepted()"))
    
    def __uninstallPlugin(self):
        """
        Private slot to uninstall the selected plugin.
        
        @return flag indicating success (boolean)
        """
        pluginDirectory = unicode(self.pluginDirectoryCombo\
                .itemData(self.pluginDirectoryCombo.currentIndex())\
                .toString())
        pluginName = unicode(self.pluginNameCombo.currentText())
        pluginFile = unicode(self.pluginNameCombo\
                .itemData(self.pluginNameCombo.currentIndex())\
                .toString())
        
        if not self.__pluginManager.unloadPlugin(pluginName, pluginDirectory):
            KQMessageBox.critical(None,
                self.trUtf8("Plugin Uninstallation"),
                self.trUtf8("""<p>The plugin <b>%1</b> could not be unloaded."""
                            """ Aborting...</p>""").arg(pluginName),
                QMessageBox.StandardButtons(\
                    QMessageBox.Ok))
            return False
        
        if not pluginDirectory in sys.path:
            sys.path.insert(2, pluginDirectory)
        module = imp.load_source(pluginName, pluginFile)
        if not hasattr(module, "packageName"):
            KQMessageBox.critical(None,
                self.trUtf8("Plugin Uninstallation"),
                self.trUtf8("""<p>The plugin <b>%1</b> has no 'packageName' attribute."""
                            """ Aborting...</p>""").arg(pluginName),
                QMessageBox.StandardButtons(\
                    QMessageBox.Ok))
            return False
        
        package = getattr(module, "packageName")
        if package is None:
            package = "None"
            packageDir = ""
        else:
            packageDir = os.path.join(pluginDirectory, package)
        if hasattr(module, "prepareUninstall"):
            module.prepareUninstall()
        internalPackages = []
        if hasattr(module, "internalPackages"):
            # it is a comma separated string
            internalPackages = [p.strip() for p in module.internalPackages.split(",")]
        del module
        
        # clean sys.modules
        self.__pluginManager.removePluginFromSysModules(
            pluginName, package, internalPackages)
        
        try:
            if packageDir and os.path.exists(packageDir):
                shutil.rmtree(packageDir)
            
            fnameo = "%so" % pluginFile
            if os.path.exists(fnameo):
                os.remove(fnameo)
            
            fnamec = "%sc" % pluginFile
            if os.path.exists(fnamec):
                os.remove(fnamec)
            
            os.remove(pluginFile)
        except OSError, err:
            KQMessageBox.critical(None,
                self.trUtf8("Plugin Uninstallation"),
                self.trUtf8("""<p>The plugin package <b>%1</b> could not be"""
                            """ removed. Aborting...</p>"""
                            """<p>Reason: %2</p>""").arg(packageDir).arg(unicode(err)),
                QMessageBox.StandardButtons(\
                    QMessageBox.Ok))
            return False
        
        KQMessageBox.information(None,
            self.trUtf8("Plugin Uninstallation"),
            self.trUtf8("""<p>The plugin <b>%1</b> was uninstalled successfully"""
                        """ from %2.</p>""")\
                .arg(pluginName).arg(pluginDirectory),
            QMessageBox.StandardButtons(\
                QMessageBox.Ok))
        return True

class PluginUninstallDialog(QDialog):
    """
    Class for the dialog variant.
    """
    def __init__(self, pluginManager, parent = None):
        """
        Constructor
        
        @param pluginManager reference to the plugin manager object
        @param parent reference to the parent widget (QWidget)
        """
        QDialog.__init__(self, parent)
        self.setSizeGripEnabled(True)
        
        self.__layout = QVBoxLayout(self)
        self.__layout.setMargin(0)
        self.setLayout(self.__layout)
        
        self.cw = PluginUninstallWidget(pluginManager, self)
        size = self.cw.size()
        self.__layout.addWidget(self.cw)
        self.resize(size)
        
        self.connect(self.cw, SIGNAL("accepted()"), self.accept)
        self.connect(self.cw.buttonBox, SIGNAL("rejected()"), self.reject)

class PluginUninstallWindow(KQMainWindow):
    """
    Main window class for the standalone dialog.
    """
    def __init__(self, parent = None):
        """
        Constructor
        
        @param parent reference to the parent widget (QWidget)
        """
        KQMainWindow.__init__(self, parent)
        self.cw = PluginUninstallWidget(None, self)
        size = self.cw.size()
        self.setCentralWidget(self.cw)
        self.resize(size)
        
        self.connect(self.cw, SIGNAL("accepted()"), self.close)
        self.connect(self.cw.buttonBox, SIGNAL("rejected()"), self.close)
