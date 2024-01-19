# -*- coding: utf-8 -*-

# Copyright (c) 2007 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the Plugin installation dialog.
"""

import os
import sys
import shutil
import zipfile
import compileall
import urlparse

from PyQt4.QtGui import *
from PyQt4.QtCore import *

from KdeQt import KQFileDialog
from KdeQt.KQMainWindow import KQMainWindow

from E4Gui.E4Completers import E4FileCompleter

from PluginManager import PluginManager
from Ui_PluginInstallDialog import Ui_PluginInstallDialog

import Utilities
import Preferences

from Utilities.uic import compileUiFiles

class PluginInstallWidget(QWidget, Ui_PluginInstallDialog):
    """
    Class implementing the Plugin installation dialog.
    """
    def __init__(self, pluginManager, pluginFileNames, parent = None):
        """
        Constructor
        
        @param pluginManager reference to the plugin manager object
        @param pluginFileNames list of plugin files suggested for 
            installation (QStringList)
        @param parent parent of this dialog (QWidget)
        """
        QWidget.__init__(self, parent)
        self.setupUi(self)
        
        if pluginManager is None:
            # started as external plugin installer
            self.__pluginManager = PluginManager(doLoadPlugins = False)
            self.__external = True
        else:
            self.__pluginManager = pluginManager
            self.__external = False
        
        self.__backButton = \
            self.buttonBox.addButton(self.trUtf8("< Back"), QDialogButtonBox.ActionRole)
        self.__nextButton = \
            self.buttonBox.addButton(self.trUtf8("Next >"), QDialogButtonBox.ActionRole)
        self.__finishButton = \
            self.buttonBox.addButton(self.trUtf8("Install"), QDialogButtonBox.ActionRole)
        
        self.__closeButton = self.buttonBox.button(QDialogButtonBox.Close)
        self.__cancelButton = self.buttonBox.button(QDialogButtonBox.Cancel)
        
        userDir = self.__pluginManager.getPluginDir("user")
        if userDir is not None:
            self.destinationCombo.addItem(self.trUtf8("User plugins directory"), 
                QVariant(userDir))
        
        globalDir = self.__pluginManager.getPluginDir("global")
        if globalDir is not None and os.access(globalDir, os.W_OK):
            self.destinationCombo.addItem(self.trUtf8("Global plugins directory"), 
                QVariant(globalDir))
        
        self.__installedDirs = []
        self.__installedFiles = []
        
        self.__restartNeeded = False
        
        downloadDir = QDir(Preferences.getPluginManager("DownloadPath"))
        for pluginFileName in pluginFileNames:
            fi = QFileInfo(pluginFileName)
            if fi.isRelative():
                pluginFileName = QFileInfo(downloadDir, fi.fileName()).absoluteFilePath()
            self.archivesList.addItem(pluginFileName)
            self.archivesList.sortItems()
        
        self.__currentIndex = 0
        self.__selectPage()
    
    def restartNeeded(self):
        """
        Public method to check, if a restart of the IDE is required.
        
        @return flag indicating a restart is required (boolean)
        """
        return self.__restartNeeded
    
    def __createArchivesList(self):
        """
        Private method to create a list of plugin archive names.
        
        @return list of plugin archive names (QStringList)
        """
        archivesList = QStringList()
        for row in range(self.archivesList.count()):
            archivesList.append(self.archivesList.item(row).text())
        return archivesList

    def __selectPage(self):
        """
        Private method to show the right wizard page.
        """
        self.wizard.setCurrentIndex(self.__currentIndex)
        if self.__currentIndex == 0:
            self.__backButton.setEnabled(False)
            self.__nextButton.setEnabled(self.archivesList.count() > 0)
            self.__finishButton.setEnabled(False)
            self.__closeButton.hide()
            self.__cancelButton.show()
        elif self.__currentIndex == 1:
            self.__backButton.setEnabled(True)
            self.__nextButton.setEnabled(self.destinationCombo.count() > 0)
            self.__finishButton.setEnabled(False)
            self.__closeButton.hide()
            self.__cancelButton.show()
        else:
            self.__backButton.setEnabled(True)
            self.__nextButton.setEnabled(False)
            self.__finishButton.setEnabled(True)
            self.__closeButton.hide()
            self.__cancelButton.show()
            
            msg = self.trUtf8("Plugin ZIP-Archives:\n%1\n\nDestination:\n%2 (%3)")\
                .arg(self.__createArchivesList().join("\n"))\
                .arg(self.destinationCombo.currentText())\
                .arg(self.destinationCombo.itemData(self.destinationCombo.currentIndex())\
                     .toString()
                )
            self.summaryEdit.setPlainText(msg)
    
    @pyqtSignature("")
    def on_addArchivesButton_clicked(self):
        """
        Private slot to select plugin ZIP-archives via a file selection dialog.
        """
        dn = Preferences.getPluginManager("DownloadPath")
        archives = KQFileDialog.getOpenFileNames(\
            self,
            self.trUtf8("Select plugin ZIP-archives"),
            dn,
            self.trUtf8("Plugin archive (*.zip)"))
        
        if not archives.isEmpty():
            matchflags = Qt.MatchFixedString
            if not Utilities.isWindowsPlatform():
                matchflags |= Qt.MatchCaseSensitive
            for archive in archives:
                if len(self.archivesList.findItems(archive, matchflags)) == 0:
                    # entry not in list already
                    self.archivesList.addItem(archive)
            self.archivesList.sortItems()
        
        self.__nextButton.setEnabled(self.archivesList.count() > 0)
    
    @pyqtSignature("")
    def on_archivesList_itemSelectionChanged(self):
        """
        Private slot called, when the selection of the archives list changes.
        """
        self.removeArchivesButton.setEnabled(len(self.archivesList.selectedItems()) > 0)
    
    @pyqtSignature("")
    def on_removeArchivesButton_clicked(self):
        """
        Private slot to remove archives from the list.
        """
        for archiveItem in self.archivesList.selectedItems():
            itm = self.archivesList.takeItem(self.archivesList.row(archiveItem))
            del itm
        
        self.__nextButton.setEnabled(self.archivesList.count() > 0)
    
    @pyqtSignature("QAbstractButton*")
    def on_buttonBox_clicked(self, button):
        """
        Private slot to handle the click of a button of the button box.
        """
        if button == self.__backButton:
            self.__currentIndex -= 1
            self.__selectPage()
        elif button == self.__nextButton:
            self.__currentIndex += 1
            self.__selectPage()
        elif button == self.__finishButton:
            self.__installPlugins()
            self.__finishButton.setEnabled(False)
            self.__closeButton.show()
            self.__cancelButton.hide()
    
    def __installPlugins(self):
        """
        Private method to install the selected plugin archives.
        
        @return flag indicating success (boolean)
        """
        res = True
        self.summaryEdit.clear()
        for archive in self.__createArchivesList():
            self.summaryEdit.append(self.trUtf8("Installing %1 ...").arg(archive))
            ok, msg, restart = self.__installPlugin(archive)
            res = res and ok
            if ok:
                self.summaryEdit.append(self.trUtf8("  ok"))
            else:
                self.summaryEdit.append(msg)
            if restart:
                self.__restartNeeded = True
        self.summaryEdit.append("\n")
        if res:
            self.summaryEdit.append(self.trUtf8(\
                """The plugins were installed successfully."""))
        else:
            self.summaryEdit.append(self.trUtf8(\
                """Some plugins could not be installed."""))
        
        return res
    
    def __installPlugin(self, archiveFilename):
        """
        Private slot to install the selected plugin.
        
        @param archiveFilename name of the plugin archive 
            file (string or QString)
        @return flag indicating success (boolean), error message
            upon failure (QString) and flag indicating a restart
            of the IDE is required (boolean)
        """
        installedPluginName = ""
        
        archive = unicode(archiveFilename)
        destination = \
            unicode(self.destinationCombo.itemData(self.destinationCombo.currentIndex())\
                .toString())
        
        # check if archive is a local url
        url = urlparse.urlparse(archive)
        if url[0].lower() == 'file':
            archive = url[2]

        # check, if the archive exists
        if not os.path.exists(archive):
            return False, \
                self.trUtf8("""<p>The archive file <b>%1</b> does not exist. """
                            """Aborting...</p>""").arg(archive), \
                False
        
        # check, if the archive is a valid zip file
        if not zipfile.is_zipfile(archive):
            return False, \
                self.trUtf8("""<p>The file <b>%1</b> is not a valid plugin """
                            """ZIP-archive. Aborting...</p>""").arg(archive), \
                False
        
        # check, if the destination is writeable
        if not os.access(destination, os.W_OK):
            return False, \
                self.trUtf8("""<p>The destination directory <b>%1</b> is not """
                            """writeable. Aborting...</p>""").arg(destination), \
                False
        
        zip = zipfile.ZipFile(archive, "r")
        
        # check, if the archive contains a valid plugin
        pluginFound = False
        pluginFileName = ""
        for name in zip.namelist():
            if self.__pluginManager.isValidPluginName(name):
                installedPluginName = name[:-3]
                pluginFound = True
                pluginFileName = name
                break
        
        if not pluginFound:
            return False, \
                self.trUtf8("""<p>The file <b>%1</b> is not a valid plugin """
                            """ZIP-archive. Aborting...</p>""").arg(archive), \
                False
        
        # parse the plugin module's plugin header
        pluginSource = zip.read(pluginFileName)
        packageName = ""
        internalPackages = []
        needsRestart = False
        for line in pluginSource.splitlines():
            if line.startswith("packageName"):
                tokens = line.split("=")
                if tokens[0].strip() == "packageName" and \
                   tokens[1].strip()[1:-1] != "__core__":
                    if tokens[1].strip()[0] in ['"', "'"]:
                        packageName = tokens[1].strip()[1:-1]
                    else:
                        if tokens[1].strip() == "None":
                            packageName = "None"
            elif line.startswith("internalPackages"):
                tokens = line.split("=")
                token = tokens[1].strip()[1:-1]    # it is a comma separated string
                internalPackages = [p.strip() for p in token.split(",")]
            elif line.startswith("needsRestart"):
                tokens = line.split("=")
                needsRestart = tokens[1].strip() == "True"
            elif line.startswith("# End-Of-Header"):
                break
        
        if not packageName:
            return False, \
                self.trUtf8("""<p>The plugin module <b>%1</b> does not contain """
                            """a 'packageName' attribute. Aborting...</p>""")\
                    .arg(pluginFileName), \
                False
        
        # check, if it is a plugin, that collides with others
        if not os.path.exists(os.path.join(destination, pluginFileName)) and \
           packageName != "None" and \
           os.path.exists(os.path.join(destination, packageName)):
            return False, \
                self.trUtf8("""<p>The plugin package <b>%1</b> exists. """
                            """Aborting...</p>""")\
                    .arg(os.path.join(destination, packageName)), \
                False
        
        if os.path.exists(os.path.join(destination, pluginFileName)) and \
           packageName != "None" and \
           not os.path.exists(os.path.join(destination, packageName)):
            return False, \
                self.trUtf8("""<p>The plugin module <b>%1</b> exists. """
                            """Aborting...</p>""")\
                    .arg(os.path.join(destination, pluginFileName)), \
                False
        
        activatePlugin = False
        if not self.__external:
            activatePlugin = \
                not self.__pluginManager.isPluginLoaded(installedPluginName) or \
                (self.__pluginManager.isPluginLoaded(installedPluginName) and \
                 self.__pluginManager.isPluginActive(installedPluginName))
            # try to unload a plugin with the same name
            self.__pluginManager.unloadPlugin(installedPluginName, destination)
        
        # uninstall existing plugin first to get clean conditions
        self.__uninstallPackage(destination, pluginFileName, packageName)
        
        # clean sys.modules
        reload_ = self.__pluginManager.removePluginFromSysModules(
            installedPluginName, packageName, internalPackages)
        
        # now do the installation
        self.__installedDirs = []
        self.__installedFiles = []
        try:
            if packageName != "None":
                packageDirs = ["%s/" % packageName, "%s\\" % packageName]
                namelist = zip.namelist()
                namelist.sort()
                tot = len(namelist)
                prog = 0
                self.progress.setMaximum(tot)
                QApplication.processEvents()
                for name in namelist:
                    self.progress.setValue(prog)
                    QApplication.processEvents()
                    prog += 1
                    if name == pluginFileName or \
                       name.startswith("%s/" % packageName) or \
                       name.startswith("%s\\" % packageName):
                        outname = name.replace("/", os.sep)
                        outname = os.path.join(destination, outname)
                        if outname.endswith("/") or outname.endswith("\\"):
                            # it is a directory entry
                            outname = outname[:-1]
                            if not os.path.exists(outname):
                                self.__makedirs(outname)
                        else:
                            # it is a file
                            d = os.path.dirname(outname)
                            if not os.path.exists(d):
                                self.__makedirs(d)
                            f = open(outname, "wb")
                            f.write(zip.read(name))
                            f.close()
                            self.__installedFiles.append(outname)
                self.progress.setValue(tot)
                # now compile user interface files
                compileUiFiles(os.path.join(destination, packageName), True)
            else:
                outname = os.path.join(destination, pluginFileName)
                f = open(outname, "wb")
                f.write(pluginSource)
                f.close()
                self.__installedFiles.append(outname)
        except os.error, why:
            self.__rollback()
            return False, \
                self.trUtf8("Error installing plugin. Reason: %1").arg(unicode(why)), \
                False
        except IOError, why:
            self.__rollback()
            return False, \
                self.trUtf8("Error installing plugin. Reason: %1").arg(unicode(why)), \
                False
        except OSError, why:
            self.__rollback()
            return False, \
                self.trUtf8("Error installing plugin. Reason: %1").arg(unicode(why)), \
                False
        except:
            print >>sys.stderr, "Unspecific exception installing plugin."
            self.__rollback()
            return False, \
                self.trUtf8("Unspecific exception installing plugin."), \
                False
        
        # now compile the plugins
        compileall.compile_dir(destination, quiet = True)
        
        if not self.__external:
            # now load and activate the plugin
            self.__pluginManager.loadPlugin(installedPluginName, destination, reload_)
            if activatePlugin:
                self.__pluginManager.activatePlugin(installedPluginName)
        
        return True, QString(""), needsRestart
    
    def __rollback(self):
        """
        Private method to rollback a failed installation.
        """
        for fname in self.__installedFiles:
            if os.path.exists(fname):
                os.remove(fname)
        for dname in self.__installedDirs:
            if os.path.exists(dname):
                shutil.rmtree(dname)
    
    def __makedirs(self, name, mode = 0777):
        """
        Private method to create a directory and all intermediate ones.
        
        This is an extended version of the Python one in order to
        record the created directories.
        
        @param name name of the directory to create (string)
        @param mode permission to set for the new directory (integer)
        """
        head, tail = os.path.split(name)
        if not tail:
            head, tail = os.path.split(head)
        if head and tail and not os.path.exists(head):
            self.__makedirs(head, mode)
            if tail == os.curdir:           # xxx/newdir/. exists if xxx/newdir exists
                return
        os.mkdir(name, mode)
        self.__installedDirs.append(name)
    
    def __uninstallPackage(self, destination, pluginFileName, packageName):
        """
        Private method to uninstall an already installed plugin to prepare
        the update.
        
        @param destination name of the plugin directory (string)
        @param pluginFileName name of the plugin file (string)
        @param packageName name of the plugin package (string)
        """
        if packageName == "" or packageName == "None":
            packageDir = None
        else:
            packageDir = os.path.join(destination, packageName)
        pluginFile = os.path.join(destination, pluginFileName)
        
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
        except (IOError, OSError, os.error):
            # ignore some exceptions
            pass

class PluginInstallDialog(QDialog):
    """
    Class for the dialog variant.
    """
    def __init__(self, pluginManager, pluginFileNames, parent = None):
        """
        Constructor
        
        @param pluginManager reference to the plugin manager object
        @param pluginFileNames list of plugin files suggested for 
            installation (QStringList)
        @param parent reference to the parent widget (QWidget)
        """
        QDialog.__init__(self, parent)
        self.setSizeGripEnabled(True)
        
        self.__layout = QVBoxLayout(self)
        self.__layout.setMargin(0)
        self.setLayout(self.__layout)
        
        self.cw = PluginInstallWidget(pluginManager, pluginFileNames, self)
        size = self.cw.size()
        self.__layout.addWidget(self.cw)
        self.resize(size)
        
        self.connect(self.cw.buttonBox, SIGNAL("accepted()"), self.accept)
        self.connect(self.cw.buttonBox, SIGNAL("rejected()"), self.reject)
    
    def restartNeeded(self):
        """
        Public method to check, if a restart of the IDE is required.
        
        @return flag indicating a restart is required (boolean)
        """
        return self.cw.restartNeeded()

class PluginInstallWindow(KQMainWindow):
    """
    Main window class for the standalone dialog.
    """
    def __init__(self, pluginFileNames, parent = None):
        """
        Constructor
        
        @param pluginFileNames list of plugin files suggested for 
            installation (QStringList)
        @param parent reference to the parent widget (QWidget)
        """
        KQMainWindow.__init__(self, parent)
        self.cw = PluginInstallWidget(None, pluginFileNames, self)
        size = self.cw.size()
        self.setCentralWidget(self.cw)
        self.resize(size)
        
        self.connect(self.cw.buttonBox, SIGNAL("accepted()"), self.close)
        self.connect(self.cw.buttonBox, SIGNAL("rejected()"), self.close)
