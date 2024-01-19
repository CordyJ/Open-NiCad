# -*- coding: utf-8 -*-

# Copyright (c) 2002 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the project management functionality.
"""

import os
import sys
import re
import time
import shutil
import glob
import fnmatch
import copy
import zipfile
import cStringIO

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from KdeQt import KQFileDialog, KQMessageBox, KQInputDialog
from KdeQt.KQApplication import e4App
import KdeQt

from Globals import recentNameProject

from ProjectBrowserModel import ProjectBrowserModel

from AddLanguageDialog import AddLanguageDialog
from AddFileDialog import AddFileDialog
from AddDirectoryDialog import AddDirectoryDialog
from PropertiesDialog import PropertiesDialog
from AddFoundFilesDialog import AddFoundFilesDialog
from DebuggerPropertiesDialog import DebuggerPropertiesDialog
from FiletypeAssociationDialog import FiletypeAssociationDialog
from LexerAssociationDialog import LexerAssociationDialog
from UserPropertiesDialog import UserPropertiesDialog

from E4XML.XMLUtilities import make_parser
from E4XML.XMLErrorHandler import XMLErrorHandler, XMLFatalParseError
from E4XML.XMLEntityResolver import XMLEntityResolver

from E4XML.ProjectHandler import ProjectHandler
from E4XML.ProjectWriter import ProjectWriter
from E4XML.UserProjectHandler import UserProjectHandler
from E4XML.UserProjectWriter import UserProjectWriter
from E4XML.SessionHandler import SessionHandler
from E4XML.SessionWriter import SessionWriter
from E4XML.TasksHandler import TasksHandler
from E4XML.TasksWriter import TasksWriter
from E4XML.DebuggerPropertiesHandler import DebuggerPropertiesHandler
from E4XML.DebuggerPropertiesWriter import DebuggerPropertiesWriter

import VCS
from VCS.CommandOptionsDialog import vcsCommandOptionsDialog
from VCS.ProjectHelper import VcsProjectHelper

from Graphics.ApplicationDiagram import ApplicationDiagram

from DataViews.CodeMetricsDialog import CodeMetricsDialog
from DataViews.PyCoverageDialog import PyCoverageDialog
from DataViews.PyProfileDialog import PyProfileDialog

import UI.PixmapCache

from E4Gui.E4Action import E4Action, createActionGroup

import Preferences
import Utilities

from eric4config import getConfig

class Project(QObject):
    """
    Class implementing the project management functionality.
    
    @signal dirty(int) emitted when the dirty state changes
    @signal projectSessionLoaded() emitted after a project session file was loaded
    @signal projectLanguageAdded(string) emitted after a new language was added
    @signal projectLanguageAddedByCode(string) emitted after a new language was added.
        The language code is sent by this signal.
    @signal projectFormAdded(string) emitted after a new form was added
    @signal projectSourceAdded(string) emitted after a new source file was added
    @signal projectInterfaceAdded(string) emitted after a new IDL file was added
    @signal projectResourceAdded(string) emitted after a new resource file was added
    @signal projectAboutToBeCreated() emitted just before the project will be created
    @signal newProjectHooks() emitted after a new project was generated but before
            the newProject() signal is sent
    @signal newProject() emitted after a new project was generated
    @signal sourceFile(string) emitted after a project file was read to 
            open the main script
    @signal projectOpenedHooks() emitted after a project file was read but before the
            projectOpened() signal is sent
    @signal projectOpened() emitted after a project file was read
    @signal projectClosedHooks() emitted after a project file was clsoed but before the
            projectClosed() signal is sent
    @signal projectClosed() emitted after a project was closed
    @signal projectOthersAdded(string) emitted after a file or directory was added
            to the OTHERS project data area
    @signal projectFileRenamed(string, string) emitted after a file of the project
            has been renamed
    @signal projectPropertiesChanged() emitted after the project properties were changed
    @signal directoryRemoved(string) emitted after a directory has been removed from
            the project
    @signal prepareRepopulateItem(string) emitted before an item of the model is
            repopulated
    @signal completeRepopulateItem(string) emitted after an item of the model was
            repopulated
    @signal vcsStatusMonitorStatus(QString, QString) emitted to signal the status of the
            monitoring thread (ok, nok, op, off) and a status message
    @signal reinitVCS() emitted after the VCS has been reinitialized
    @signal showMenu(string, QMenu) emitted when a menu is about to be shown. The name
            of the menu and a reference to the menu are given.
    @signal lexerAssociationsChanged() emitted after the lexer associations have been
            changed
    """
    keynames = [
        "PROGLANGUAGE", "MIXEDLANGUAGE", "PROJECTTYPE",
        "SPELLLANGUAGE", "SPELLWORDS", "SPELLEXCLUDES", 
        "DESCRIPTION", "VERSION",
        "AUTHOR", "EMAIL",
        "SOURCES", "FORMS", "RESOURCES",
        "TRANSLATIONS", "TRANSLATIONPATTERN", "TRANSLATIONSBINPATH", 
        "TRANSLATIONEXCEPTIONS",
        "MAINSCRIPT",
        "VCS", "VCSOPTIONS", "VCSOTHERDATA",
        "OTHERS", "INTERFACES", 
        "FILETYPES", "LEXERASSOCS", 
        "PROJECTTYPESPECIFICDATA", 
        "DOCUMENTATIONPARMS", 
        "PACKAGERSPARMS",
        "CHECKERSPARMS",
        "OTHERTOOLSPARMS", 
    ]
    
    # the following defines patterns used to perform a security check
    securityCheckPatterns = [
        re.compile(r'os.*\.(exec|popen|spawn|startfile|system)'),
        re.compile(r'os.*\.(remove|rename|rmdir|unlink)'),
        re.compile(r'shutil.*\.rmtree'),
    ]
    
    dbgKeynames = [
        "INTERPRETER", "DEBUGCLIENT",
        "ENVIRONMENTOVERRIDE", "ENVIRONMENTSTRING",
        "REMOTEDEBUGGER", "REMOTEHOST", "REMOTECOMMAND",
        "PATHTRANSLATION", "REMOTEPATH", "LOCALPATH",
        "CONSOLEDEBUGGER", "CONSOLECOMMAND",
        "REDIRECT", "NOENCODING",
    ]
    
    userKeynames = [
        "VCSOVERRIDE", "VCSSTATUSMONITORINTERVAL",
    ]
    
    def __init__(self, parent = None, filename = None):
        """
        Constructor
        
        @param parent parent widget (usually the ui object) (QWidget)
        @param filename optional filename of a project file to open (string)
        """
        QObject.__init__(self, parent)
        
        self.ui = parent
        
        self.sourceExtensions = {\
            "Python"  : ['.py', '.ptl', '.pyw'],
            "Python3" : ['.py', '.pyw'],
            "Ruby"    : ['.rb'],
            "Mixed"   : ['.py', '.ptl', '.rb']
        }
        
        self.dbgFilters = {\
            "Python"  : self.trUtf8(\
                         "Python Files (*.py);;"
                         "Python GUI Files (*.pyw);;"),
            "Python3" : self.trUtf8(\
                         "Python3 Files (*.py3);;"
                         "Python3 GUI Files (*.pyw3);;"),
            "Ruby"    : self.trUtf8("Ruby Files (*.rb);;"),
        }
        
        self.vcsMenu = None
        
        self.__initProjectTypes()
        
        self.__initData()
        
        self.recent = QStringList()
        self.__loadRecent()
        
        if filename is not None:
            self.openProject(filename)
        else:
            self.vcs = self.initVCS()
        
        self.__model = ProjectBrowserModel(self)
        
        self.codemetrics        = None
        self.codecoverage       = None
        self.profiledata        = None
        self.applicationDiagram = None
        
    def __initProjectTypes(self):
        """
        Private method to initialize the list of supported project types.
        """
        self.__projectTypes = {}
        self.__fileTypeCallbacks = {}
        self.__lexerAssociationCallbacks = {}
        self.__binaryTranslationsCallbacks = {}
        self.__projectTypes["Qt4"] = self.trUtf8("Qt4 GUI")
        self.__projectTypes["Qt4C"] = self.trUtf8("Qt4 Console")
        self.__projectTypes["E4Plugin"] = self.trUtf8("Eric4 Plugin")
        self.__projectTypes["Console"] = self.trUtf8("Console")
        self.__projectTypes["Other"] = self.trUtf8("Other")
        if KdeQt.isKDEAvailable():
            self.__projectTypes["Kde4"] = self.trUtf8("KDE 4")
        try:
            import PySide
            self.__projectTypes["PySide"] = self.trUtf8("PySide GUI")
            self.__projectTypes["PySideC"] = self.trUtf8("PySide Console")
            del PySide
        except ImportError:
            pass
        
    def getProjectTypes(self):
        """
        Public method to get the list of supported project types.
        
        @return reference to the dictionary of project types.
        """
        return self.__projectTypes
        
    def hasProjectType(self, type_):
        """
        Public method to check, if a project type is already registered.
        
        @param type_ internal type designator to be unregistered (string)
        """
        return self.__projectTypes.has_key(type_)
        
    def registerProjectType(self, type_, description, fileTypeCallback = None, 
        binaryTranslationsCallback = None, lexerAssociationCallback = None):
        """
        Public method to register a project type.
        
        @param type_ internal type designator to be registered (string)
        @param description more verbose type name (display string) (QString)
        @keyparam fileTypeCallback reference to a method returning a dictionary
            of filetype associations.
        @keyparam binaryTranslationsCallback reference to a method returning the
            name of the binary translation file given the name of the raw 
            translation file
        @keyparam lexerAssociationCallback reference to a method returning the
            lexer type to be used for syntax highlighting given the name of
            a file
        """
        if self.__projectTypes.has_key(type_):
            KQMessageBox.critical(None,
                self.trUtf8("Registering Project Type"),
                self.trUtf8("""<p>The Project type <b>%1</b> already exists.</p>""")\
                    .arg(type_)
            )
        else:
            self.__projectTypes[type_] = description
            self.__fileTypeCallbacks[type_] = fileTypeCallback
            self.__lexerAssociationCallbacks[type_] = lexerAssociationCallback
            self.__binaryTranslationsCallbacks[type_] = binaryTranslationsCallback
        
    def unregisterProjectType(self, type_):
        """
        Public method to unregister a project type.
        
        @param type_ internal type designator to be unregistered (string)
        """
        if type_ in self.__projectTypes:
            del self.__projectTypes[type_]
        if type_ in self.__fileTypeCallbacks:
            del self.__fileTypeCallbacks[type_]
        if type_ in self.__lexerAssociationCallbacks:
            del self.__lexerAssociationCallbacks[type_]
        if type_ in self.__binaryTranslationsCallbacks:
            del self.__binaryTranslationsCallbacks[type_]
        
    def __initData(self):
        """
        Private method to initialize the project data part.
        """
        self.loaded = False     # flag for the loaded status
        self.dirty = False      # dirty flag
        self.pfile = ""         # name of the project file
        self.ppath = ""         # name of the project directory
        self.translationsRoot = ""  # the translations prefix
        self.name = ""
        self.opened = False
        self.subdirs = [""] # record the project dir as a relative path (i.e. empty path)
        self.otherssubdirs = []
        self.vcs = None
        self.dbgCmdline = ''
        self.dbgWd = ''
        self.dbgEnv = ''
        self.dbgReportExceptions = True
        self.dbgExcList = QStringList()
        self.dbgExcIgnoreList = QStringList()
        self.dbgAutoClearShell = True
        self.dbgTracePython = False
        self.dbgAutoContinue = True
        
        self.pdata = {}
        for key in self.__class__.keynames:
            self.pdata[key] = []
        self.pdata["AUTHOR"] = ['']
        self.pdata["EMAIL"] = ['']
        self.pdata["PROGLANGUAGE"] = ["Python"]
        self.pdata["MIXEDLANGUAGE"] = [False]
        self.pdata["PROJECTTYPE"] = ["Qt4"]
        self.pdata["SPELLLANGUAGE"] = \
            [Preferences.getEditor("SpellCheckingDefaultLanguage")]
        self.pdata["SPELLWORDS"] = ['']
        self.pdata["SPELLEXCLUDES"] = ['']
        self.pdata["FILETYPES"] = {}
        self.pdata["LEXERASSOCS"] = {}
        self.pdata["PROJECTTYPESPECIFICDATA"] = {}
        self.pdata["CHECKERSPARMS"] = {}
        self.pdata["PACKAGERSPARMS"] = {}
        self.pdata["DOCUMENTATIONPARMS"] = {}
        self.pdata["OTHERTOOLSPARMS"] = {}
        
        self.__initDebugProperties()
        
        self.pudata = {}
        for key in self.__class__.userKeynames:
            self.pudata[key] = []
        
        self.vcs = self.initVCS()
        
    def getData(self, category, key):
        """
        Public method to get data out of the project data store.
        
        @param category category of the data to get (string, one of
            PROJECTTYPESPECIFICDATA, CHECKERSPARMS, PACKAGERSPARMS, DOCUMENTATIONPARMS
            or OTHERTOOLSPARMS)
        @param key key of the data entry to get (string).
        @return a copy of the requested data or None
        """
        if category in ["PROJECTTYPESPECIFICDATA","CHECKERSPARMS", "PACKAGERSPARMS", 
                        "DOCUMENTATIONPARMS", "OTHERTOOLSPARMS"] and \
           key in self.pdata[category]:
            return copy.deepcopy(self.pdata[category][key])
        else:
            return None
        
    def setData(self, category, key, data):
        """
        Public method to store data in the project data store.
        
        @param category category of the data to get (string, one of
            PROJECTTYPESPECIFICDATA, CHECKERSPARMS, PACKAGERSPARMS, DOCUMENTATIONPARMS
            or OTHERTOOLSPARMS)
        @param key key of the data entry to get (string).
        @param data data to be stored
        @return flag indicating success (boolean)
        """
        if category not in ["PROJECTTYPESPECIFICDATA","CHECKERSPARMS", "PACKAGERSPARMS", 
                            "DOCUMENTATIONPARMS", "OTHERTOOLSPARMS"]:
            return False
        
        # test for changes of data and save them in the project
        # 1. there were none, now there are
        if key not in self.pdata[category] and len(data) > 0:
            self.pdata[category][key] = copy.deepcopy(data)
            self.setDirty(True)
        # 2. there were some, now there aren't
        elif key in self.pdata[category] and len(data) == 0:
            del self.pdata[category][key]
            self.setDirty(True)
        # 3. there were some and still are
        elif key in self.pdata[category] and len(data) > 0:
            if data != self.pdata[category][key]:
                self.pdata[category][key] = copy.deepcopy(data)
                self.setDirty(True)
        # 4. there were none and none are given
        else:
            return False
        return True
        
    def initFileTypes(self):
        """
        Public method to initialize the filetype associations with default values.
        """
        self.pdata["FILETYPES"] = {}
        if self.pdata["MIXEDLANGUAGE"][0]:
            sourceKey = "Mixed"
        else:
            sourceKey = self.pdata["PROGLANGUAGE"][0]
        for ext in self.sourceExtensions[sourceKey]:
            self.pdata["FILETYPES"]["*%s" % ext] = "SOURCES"
        self.pdata["FILETYPES"]["*.idl"] = "INTERFACES"
        if self.pdata["PROJECTTYPE"][0] in ["Qt4", "E4Plugin", "Kde4", "PySide"]:
            self.pdata["FILETYPES"]["*.ui"] = "FORMS"
            self.pdata["FILETYPES"]["*.ui.h"] = "FORMS"
        if self.pdata["PROJECTTYPE"][0] in ["Qt4", "Qt4C", "E4Plugin", "Kde4", 
                                            "PySide", "PySideC"]:
            self.pdata["FILETYPES"]["*.qrc"] = "RESOURCES"
        if self.pdata["PROJECTTYPE"][0] in ["Qt4", "Qt4C", "E4Plugin", 
                                            "PySide", "PySideC"]:
            self.pdata["FILETYPES"]["*.ts"] = "TRANSLATIONS"
            self.pdata["FILETYPES"]["*.qm"] = "TRANSLATIONS"
        try:
            if self.__fileTypeCallbacks[self.pdata["PROJECTTYPE"][0]] is not None:
                ftypes = self.__fileTypeCallbacks[self.pdata["PROJECTTYPE"][0]]()
                self.pdata["FILETYPES"].update(ftypes)
        except KeyError:
            pass
        self.setDirty(True)
        
    def updateFileTypes(self):
        """
        Public method to update the filetype associations with new default values.
        """
        if self.pdata["PROJECTTYPE"][0] in ["Qt4", "Qt4C", "E4Plugin", 
                                            "PySide", "PySideC"]:
            if "*.ts" not in self.pdata["FILETYPES"]:
                self.pdata["FILETYPES"]["*.ts"] = "TRANSLATIONS"
            if "*.qm" not in self.pdata["FILETYPES"]:
                self.pdata["FILETYPES"]["*.qm"] = "TRANSLATIONS"
        try:
            if self.__fileTypeCallbacks[self.pdata["PROJECTTYPE"][0]] is not None:
                ftypes = self.__fileTypeCallbacks[self.pdata["PROJECTTYPE"][0]]()
                for pattern, ftype in ftypes.items():
                    if pattern not in self.pdata["FILETYPES"]:
                        self.pdata["FILETYPES"][pattern] = ftype
                        self.setDirty(True)
        except KeyError:
            pass
        
    def __loadRecent(self):
        """
        Private method to load the recently opened project filenames.
        """
        self.recent.clear()
        Preferences.Prefs.rsettings.sync()
        rp = Preferences.Prefs.rsettings.value(recentNameProject)
        if rp.isValid():
            for f in rp.toStringList():
                if QFileInfo(f).exists():
                    self.recent.append(f)
    
    def __saveRecent(self):
        """
        Private method to save the list of recently opened filenames.
        """
        Preferences.Prefs.rsettings.setValue(recentNameProject, QVariant(self.recent))
        Preferences.Prefs.rsettings.sync()
        
    def getMostRecent(self):
        """
        Public method to get the most recently opened project.
        
        @return path of the most recently opened project (string)
        """
        if len(self.recent):
            return unicode(self.recent[0])
        else:
            return None
        
    def getModel(self):
        """
        Public method to get a reference to the project browser model.
        
        @return reference to the project browser model (ProjectBrowserModel)
        """
        return self.__model
        
    def getVcs(self):
        """
        Public method to get a reference to the VCS object.
        
        @return reference to the VCS object
        """
        return self.vcs
        
    def handlePreferencesChanged(self):
        """
        Public slot used to handle the preferencesChanged signal.
        """
        if self.pudata["VCSSTATUSMONITORINTERVAL"]:
            self.setStatusMonitorInterval(\
                self.pudata["VCSSTATUSMONITORINTERVAL"][0])
        else:
            self.setStatusMonitorInterval(\
                Preferences.getVCS("StatusMonitorInterval"))
        
        self.__model.preferencesChanged()
        
    def setDirty(self, b):
        """
        Public method to set the dirty state.
        
        It emits the signal dirty(int).
        
        @param b dirty state (boolean)
        """
        self.dirty = b
        self.saveAct.setEnabled(b)
        self.emit(SIGNAL("dirty"), bool(b))
        
    def isDirty(self):
        """
        Public method to return the dirty state.
        
        @return dirty state (boolean)
        """
        return self.dirty
        
    def isOpen(self):
        """
        Public method to return the opened state.
        
        @return open state (boolean)
        """
        return self.opened
        
    def __checkFilesExist(self, index):
        """
        Private method to check, if the files in a list exist. 
        
        The files in the indicated list are checked for existance in the
        filesystem. Non existant files are removed from the list and the
        dirty state of the project is changed accordingly.
        
        @param index key of the list to be checked (string)
        """
        removed = False
        removelist = []
        for file in self.pdata[index]:
            if not os.path.exists(os.path.join(self.ppath, file)):
                removelist.append(file)
                removed = True
                
        if removed:
            for file in removelist:
                self.pdata[index].remove(file)
            self.setDirty(True)
        
    def __readProject(self, fn):
        """
        Private method to read in a project (.e4p, .e4pz, .e3p, .e3pz) file.
        
        @param fn filename of the project file to be read (string or QString)
        @return flag indicating success
        """
        fn = unicode(fn)
        try:
            if fn.lower().endswith("e4pz") or fn.lower().endswith("e3pz"):
                try:
                    import gzip
                except ImportError:
                    QApplication.restoreOverrideCursor()
                    KQMessageBox.critical(None,
                        self.trUtf8("Read project file"),
                        self.trUtf8("""Compressed project files not supported."""
                                    """ The compression library is missing."""))
                    return False
                f = gzip.open(fn, "rb")
            else:
                f = open(fn, "rb")
            line = f.readline()
            dtdLine = f.readline()
            f.close()
        except EnvironmentError:
            QApplication.restoreOverrideCursor()
            KQMessageBox.critical(None,
                self.trUtf8("Read project file"),
                self.trUtf8("<p>The project file <b>%1</b> could not be read.</p>")\
                    .arg(fn))
            return False
            
        self.pfile = os.path.abspath(fn)
        self.ppath = os.path.abspath(os.path.dirname(fn))
        
        # insert filename into list of recently opened projects
        self.__syncRecent()
        
        # now read the file
        if not line.startswith('<?xml'):
            QApplication.restoreOverrideCursor()
            KQMessageBox.critical(None,
                self.trUtf8("Read project file"),
                self.trUtf8("<p>The project file <b>%1</b> has an unsupported"
                            " format.</p>").arg(fn))
            return False
            
        res = self.__readXMLProject(fn, dtdLine.startswith("<!DOCTYPE"))
        if res:
            if len(self.pdata["TRANSLATIONPATTERN"]) == 1:
                self.translationsRoot = \
                    self.pdata["TRANSLATIONPATTERN"][0].split("%language%")[0]
            elif len(self.pdata["MAINSCRIPT"]) == 1:
                self.translationsRoot = os.path.splitext(self.pdata["MAINSCRIPT"][0])[0]
            if os.path.isdir(os.path.join(self.ppath, self.translationsRoot)):
                dn = self.translationsRoot
            else:
                dn = os.path.dirname(self.translationsRoot)
            if dn not in self.subdirs:
                self.subdirs.append(dn)
                
            self.name = os.path.splitext(os.path.basename(fn))[0]
            
            # check, if the files of the project still exist in the project directory
            self.__checkFilesExist("SOURCES")
            self.__checkFilesExist("FORMS")
            self.__checkFilesExist("INTERFACES")
            self.__checkFilesExist("TRANSLATIONS")
            self.__checkFilesExist("RESOURCES")
            self.__checkFilesExist("OTHERS")
            
            # get the names of subdirectories the files are stored in
            for fn in self.pdata["SOURCES"] + \
                      self.pdata["FORMS"] + \
                      self.pdata["INTERFACES"] + \
                      self.pdata["RESOURCES"] + \
                      self.pdata["TRANSLATIONS"]:
                dn = os.path.dirname(fn)
                if dn not in self.subdirs:
                    self.subdirs.append(dn)
            
            # get the names of other subdirectories
            for fn in self.pdata["OTHERS"]:
                dn = os.path.dirname(fn)
                if dn not in self.otherssubdirs:
                    self.otherssubdirs.append(dn)
            
            if self.pfile.endswith('e3p') or self.pfile.endswith('e3pz'):
                # needs conversion to new format
                self.setDirty(True)
            
        return res

    def __readXMLProject(self, fn, validating):
        """
        Private method to read the project data from an XML file.
        
        @param fn filename of the project file to be read (string or QString)
        @param validating flag indicating a validation of the XML file is
            requested (boolean)
        @return flag indicating success
        """
        fn = unicode(fn)
        if fn.lower().endswith("e4pz") or fn.lower().endswith("e3pz"):
            # work around for a bug in xmlproc
            validating = False
        
        parser = make_parser(validating)
        handler = ProjectHandler(self)
        er = XMLEntityResolver()
        eh = XMLErrorHandler()
        
        parser.setContentHandler(handler)
        parser.setEntityResolver(er)
        parser.setErrorHandler(eh)
        
        try:
            if fn.lower().endswith("e4pz") or fn.lower().endswith("e3pz"):
                try:
                    import gzip
                except ImportError:
                    QApplication.restoreOverrideCursor()
                    KQMessageBox.critical(None,
                        self.trUtf8("Read project file"),
                        self.trUtf8("""Compressed project files not supported."""
                                    """ The compression library is missing."""))
                    return False
                f = gzip.open(fn, "rb")
            else:
                f = open(fn, "rb")
            try:
                try:
                    parser.parse(f)
                except UnicodeEncodeError:
                    f.seek(0)
                    buf = cStringIO.StringIO(f.read())
                    parser.parse(buf)
            finally:
                f.close()
        except IOError:
            QApplication.restoreOverrideCursor()
            KQMessageBox.critical(None,
                self.trUtf8("Read project file"),
                self.trUtf8("<p>The project file <b>%1</b> could not be read.</p>")\
                    .arg(fn))
            return False
        except XMLFatalParseError:
            QApplication.restoreOverrideCursor()
            KQMessageBox.critical(None,
                self.trUtf8("Read project file"),
                self.trUtf8("<p>The project file <b>%1</b> has invalid contents.</p>")\
                    .arg(fn))
            eh.showParseMessages()
            return False
        
        QApplication.restoreOverrideCursor()
        eh.showParseMessages()
        QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
        QApplication.processEvents()
        return True
        
    def __writeProject(self, fn = None):
        """
        Private method to save the project infos to a project file.
        
        @param fn optional filename of the project file to be written.
                If fn is None, the filename stored in the project object
                is used. This is the 'save' action. If fn is given, this filename
                is used instead of the one in the project object. This is the
                'save as' action.
        @return flag indicating success
        """
        if self.vcs is not None:
            self.pdata["VCSOPTIONS"] = [copy.deepcopy(self.vcs.vcsGetOptions())]
            self.pdata["VCSOTHERDATA"] = [copy.deepcopy(self.vcs.vcsGetOtherData())]
            
        if fn is None:
            fn = self.pfile
            
        res = self.__writeXMLProject(fn)
            
        if res:
            self.pfile = os.path.abspath(fn)
            self.ppath = os.path.abspath(os.path.dirname(fn))
            self.name = os.path.splitext(os.path.basename(fn))[0]
            self.setDirty(False)
            
            # insert filename into list of recently opened projects
            self.__syncRecent()
        
        return res
        
    def __writeXMLProject(self, fn = None):
        """
        Private method to write the project data to an XML file.
        
        @param fn the filename of the project file (string)
        """
        try:
            if fn.lower().endswith("e4pz"):
                try:
                    import gzip
                except ImportError:
                    KQMessageBox.critical(None,
                        self.trUtf8("Save project file"),
                        self.trUtf8("""Compressed project files not supported."""
                                    """ The compression library is missing."""))
                    return False
                f = gzip.open(fn, "wb")
            else:
                f = open(fn, "wb")
            
            ProjectWriter(f, os.path.splitext(os.path.basename(fn))[0]).writeXML()
            
            f.close()
            
        except IOError:
            KQMessageBox.critical(None,
                self.trUtf8("Save project file"),
                self.trUtf8("<p>The project file <b>%1</b> could not be written.</p>")\
                    .arg(fn))
            return False
        
        return True
        
    def __readUserProperties(self):
        """
        Private method to read in the user specific project file (.e4q)
        """
        if self.pfile is None:
            return
        
        fn, ext = os.path.splitext(os.path.basename(self.pfile))
        
        fn = os.path.join(self.getProjectManagementDir(), '%s.e4q' % fn)
        if os.path.exists(fn):
            try:
                f = open(fn, "rb")
                
                parser = make_parser(True)
                handler = UserProjectHandler(self)
                er = XMLEntityResolver()
                eh = XMLErrorHandler()
                
                parser.setContentHandler(handler)
                parser.setEntityResolver(er)
                parser.setErrorHandler(eh)
                
                try:
                    try:
                        parser.parse(f)
                    except UnicodeEncodeError:
                        f.seek(0)
                        buf = cStringIO.StringIO(f.read())
                        parser.parse(buf)
                finally:
                    f.close()
            except IOError:
                KQMessageBox.critical(None,
                    self.trUtf8("Read user project properties"),
                    self.trUtf8("<p>The user specific project properties file <b>%1</b>"
                        " could not be read.</p>").arg(fn))
                return
            except XMLFatalParseError:
                pass
            
            eh.showParseMessages()
        
    def __writeUserProperties(self):
        """
        Private method to write the project data to an XML file.
        """
        if self.pfile is None or \
           self.pfile.endswith('e3p') or \
           self.pfile.endswith('e3pz'):
            return
        
        fn, ext = os.path.splitext(os.path.basename(self.pfile))
        
        fn = os.path.join(self.getProjectManagementDir(), '%s.e4q' % fn)
        
        try:
            f = open(fn, "wb")
            
            UserProjectWriter(f, os.path.splitext(os.path.basename(fn))[0]).writeXML()
            
            f.close()
        except IOError:
            KQMessageBox.critical(None,
                self.trUtf8("Save user project properties"),
                self.trUtf8("<p>The user specific project properties file <b>%1</b>"
                    " could not be written.</p>").arg(fn))
        
    def __readSession(self, quiet = False, indicator = ""):
        """
        Private method to read in the project session file (.e4s, .e3s)
        
        @param quiet flag indicating quiet operations.
                If this flag is true, no errors are reported.
        @keyparam indicator indicator string (string)
        """
        if self.pfile is None:
            if not quiet:
                KQMessageBox.critical(None,
                    self.trUtf8("Read project session"),
                    self.trUtf8("Please save the project first."))
            return
            
        fn, ext = os.path.splitext(os.path.basename(self.pfile))
        
        try:
            if ext.lower() in [".e4pz", ".e3pz"]:
                if ext.lower() == ".e3pz":
                    fn = os.path.join(self.ppath, '%s.e3sz' % fn)
                else:
                    fn = os.path.join(self.getProjectManagementDir(), 
                                      '%s%s.e4sz' % (fn, indicator))
                try:
                    import gzip
                except ImportError:
                    if not quiet:
                        KQMessageBox.critical(None,
                            self.trUtf8("Read project session"),
                            self.trUtf8("""Compressed project session files not"""
                                """ supported. The compression library is missing."""))
                    return
                f = gzip.open(fn, "rb")
            else:
                if ext.lower() == ".e3p":
                    fn = os.path.join(self.ppath, '%s.e3s' % fn)
                else:
                    fn = os.path.join(self.getProjectManagementDir(), 
                                      '%s%s.e4s' % (fn, indicator))
                f = open(fn, "rb")
            line = f.readline()
            dtdLine = f.readline()
            f.close()
        except EnvironmentError:
            if not quiet:
                KQMessageBox.critical(None,
                    self.trUtf8("Read project session"),
                    self.trUtf8("<p>The project session <b>%1</b>"
                                " could not be read.</p>")\
                        .arg(fn))
            return
            
        # now read the file
        if line.startswith('<?xml'):
            res = self.__readXMLSession(fn, dtdLine.startswith("<!DOCTYPE"), quiet)
        else:
            if not quiet:
                KQMessageBox.critical(None,
                    self.trUtf8("Read project session"),
                    self.trUtf8("<p>The project session <b>%1</b> has an unsupported"
                        " format.</p>").arg(fn))
    
    def __readXMLSession(self, fn, validating, quiet):
        """
        Private method to read the session data from an XML file.
        
        The data read is:
            <ul>
            <li>all open source filenames</li>
            <li>the active window</li>
            <li>all breakpoints</li>
            <li>the commandline</li>
            <li>the working directory</li>
            <li>the exception reporting flag</li>
            <li>the list of exception types to be highlighted</li>
            <li>all bookmarks</li>
            </ul>
            
        @param fn filename of the project session file to be read (string or QString)
        @param validating flag indicating a validation of the XML file is
            requested (boolean)
        @param quiet flag indicating quiet operations.
            If this flag is true, no errors are reported.
        """
        fn = unicode(fn)
        if fn.lower().endswith("e4sz") or fn.lower().endswith("e3sz"):
            # work around for a bug in xmlproc
            validating = False
        
        parser = make_parser(validating)
        handler = SessionHandler(self)
        er = XMLEntityResolver()
        eh = XMLErrorHandler()
        
        parser.setContentHandler(handler)
        parser.setEntityResolver(er)
        parser.setErrorHandler(eh)
        
        try:
            if fn.lower().endswith("e4sz") or fn.lower().endswith("e3sz"):
                try:
                    import gzip
                except ImportError:
                    if not quiet:
                        KQMessageBox.critical(None,
                            self.trUtf8("Read project session"),
                            self.trUtf8("<p>The project session <b>%1</b> could not"
                                " be read.</p>").arg(fn))
                    return
                f = gzip.open(fn, "rb")
            else:
                f = open(fn, "rb")
            try:
                try:
                    parser.parse(f)
                except UnicodeEncodeError:
                    f.seek(0)
                    buf = cStringIO.StringIO(f.read())
                    parser.parse(buf)
            finally:
                f.close()
        except IOError:
            if not quiet:
                KQMessageBox.critical(None,
                    self.trUtf8("Read project session"),
                    self.trUtf8("<p>The project session file <b>%1</b> could not be"
                        " read.</p>").arg(fn))
            return
        except XMLFatalParseError:
            pass
        
        if not quiet:
            eh.showParseMessages()
        
    def __writeSession(self, quiet = False, indicator = ""):
        """
        Private method to write the session data to an XML file (.e4s).
        
        The data saved is:
            <ul>
            <li>all open source filenames belonging to the project</li>
            <li>the active window, if it belongs to the project</li>
            <li>all breakpoints</li>
            <li>the commandline</li>
            <li>the working directory</li>
            <li>the exception reporting flag</li>
            <li>the list of exception types to be highlighted</li>
            <li>all bookmarks of files belonging to the project</li>
            </ul>
        
        @param quiet flag indicating quiet operations.
                If this flag is true, no errors are reported.
        @keyparam indicator indicator string (string)
        """
        if self.pfile is None or \
           self.pfile.endswith('e3p') or \
           self.pfile.endswith('e3pz'):
            if not quiet:
                KQMessageBox.critical(None,
                    self.trUtf8("Save project session"),
                    self.trUtf8("Please save the project first."))
            return
            
        fn, ext = os.path.splitext(os.path.basename(self.pfile))
        
        try:
            if ext.lower() == ".e4pz":
                fn = os.path.join(self.getProjectManagementDir(), 
                                  '%s%s.e4sz' % (fn, indicator))
                try:
                    import gzip
                except ImportError:
                    if not quiet:
                        KQMessageBox.critical(None,
                            self.trUtf8("Save project session"),
                            self.trUtf8("""Compressed project session files not"""
                                """ supported. The compression library is missing."""))
                    return
                f = gzip.open(fn, "wb")
            else:
                fn = os.path.join(self.getProjectManagementDir(), 
                                  '%s%s.e4s' % (fn, indicator))
                f = open(fn, "wb")
            
            SessionWriter(f, os.path.splitext(os.path.basename(fn))[0]).writeXML()
            
            f.close()
            
        except IOError:
            if not quiet:
                KQMessageBox.critical(None,
                    self.trUtf8("Save project session"),
                    self.trUtf8("<p>The project session file <b>%1</b> could not be"
                        " written.</p>").arg(fn))
        
    def __deleteSession(self):
        """
        Private method to delete the session file.
        """
        if self.pfile is None:
            if not quiet:
                KQMessageBox.critical(None,
                    self.trUtf8("Delete project session"),
                    self.trUtf8("Please save the project first."))
            return
            
        fname, ext = os.path.splitext(os.path.basename(self.pfile))
        
        for fn in [os.path.join(self.getProjectManagementDir(), "%s.e4sz" % fname), 
                   os.path.join(self.getProjectManagementDir(), "%s.e4s" % fname), 
                   os.path.join(self.ppath, "%s.e3sz" % fname), 
                   os.path.join(self.ppath, "%s.e3s" % fname)]:
            if os.path.exists(fn):
                try:
                    os.remove(fn)
                except OSError:
                    KQMessageBox.critical(None,
                        self.trUtf8("Delete project session"),
                        self.trUtf8("<p>The project session file <b>%1</b> could not be"
                            " deleted.</p>").arg(fn))
        
    def __readTasks(self):
        """
        Private method to read in the project tasks file (.e4t, .e3t)
        """
        if self.pfile is None:
            KQMessageBox.critical(None,
                self.trUtf8("Read tasks"),
                self.trUtf8("Please save the project first."))
            return
            
        fn, ext = os.path.splitext(os.path.basename(self.pfile))
        
        try:
            if ext.lower() in [".e4pz", "*.e3pz"]:
                if ext.lower() == ".e3pz":
                    fn = os.path.join(self.ppath, '%s.e3tz' % fn)
                else:
                    fn = os.path.join(self.getProjectManagementDir(), '%s.e4tz' % fn)
                if not os.path.exists(fn):
                    return
                try:
                    import gzip
                except ImportError:
                    KQMessageBox.critical(None,
                        self.trUtf8("Read tasks"),
                        self.trUtf8("""Compressed tasks files not supported."""
                            """ The compression library is missing."""))
                    return
                f = gzip.open(fn, "rb")
            else:
                if ext.lower() == ".e3p":
                    fn = os.path.join(self.ppath, '%s.e3t' % fn)
                else:
                    fn = os.path.join(self.getProjectManagementDir(), '%s.e4t' % fn)
                if not os.path.exists(fn):
                    return
                f = open(fn, "rb")
            line = f.readline()
            dtdLine = f.readline()
            f.close()
        except EnvironmentError:
            KQMessageBox.critical(None,
                self.trUtf8("Read tasks"),
                self.trUtf8("<p>The tasks file <b>%1</b> could not be read.</p>").arg(fn))
            return
            
        # now read the file
        if line.startswith('<?xml'):
            res = self.__readXMLTasks(fn, dtdLine.startswith("<!DOCTYPE"))
        else:
            KQMessageBox.critical(None,
                self.trUtf8("Read project session"),
                self.trUtf8("<p>The tasks file <b>%1</b> has an unsupported format.</p>")\
                    .arg(fn))
    
    def __readXMLTasks(self, fn, validating):
        """
        Private method to read the project tasks data from an XML file.
        
        @param fn filename of the project tasks file to be read (string or QString)
        @param validating flag indicating a validation of the XML file is
            requested (boolean)
        """
        fn = unicode(fn)
        if fn.lower().endswith("e4tz") or fn.lower().endswith("e3tz"):
            # work around for a bug in xmlproc
            validating = False
        
        parser = make_parser(validating)
        handler = TasksHandler(1)
        er = XMLEntityResolver()
        eh = XMLErrorHandler()
        
        parser.setContentHandler(handler)
        parser.setEntityResolver(er)
        parser.setErrorHandler(eh)
        
        try:
            if fn.lower().endswith("e4tz") or fn.lower().endswith("e3tz"):
                try:
                    import gzip
                except ImportError:
                    KQMessageBox.critical(None,
                        self.trUtf8("Read tasks"),
                        self.trUtf8("""Compressed tasks files not supported."""
                            """ The compression library is missing."""))
                    return
                f = gzip.open(fn, "rb")
            else:
                f = open(fn, "rb")
            try:
                try:
                    parser.parse(f)
                except UnicodeEncodeError:
                    f.seek(0)
                    buf = cStringIO.StringIO(f.read())
                    parser.parse(buf)
            finally:
                f.close()
        except IOError:
            KQMessageBox.critical(None,
                self.trUtf8("Read tasks"),
                self.trUtf8("<p>The tasks file <b>%1</b> could not be read.</p>").arg(fn))
            return
        except XMLFatalParseError:
            pass
            
        eh.showParseMessages()
        
    def __writeTasks(self):
        """
        Private method to write the tasks data to an XML file (.e4t).
        """
        if self.pfile is None:
            return
            
        fn, ext = os.path.splitext(os.path.basename(self.pfile))
        
        try:
            if ext.lower() == ".e4pz":
                fn = os.path.join(self.getProjectManagementDir(), '%s.e4tz' % fn)
                try:
                    import gzip
                except ImportError:
                    KQMessageBox.critical(None,
                        self.trUtf8("Save tasks"),
                        self.trUtf8("""Compressed tasks files not supported."""
                            """ The compression library is missing."""))
                    return
                f = gzip.open(fn, "wb")
            else:
                fn = os.path.join(self.getProjectManagementDir(), '%s.e4t' % fn)
                f = open(fn, "wb")
            
            TasksWriter(f, True, os.path.splitext(os.path.basename(fn))[0]).writeXML()
            
            f.close()
            
        except IOError:
            KQMessageBox.critical(None,
                self.trUtf8("Save tasks"),
                self.trUtf8("<p>The tasks file <b>%1</b> could not be written.</p>")
                    .arg(fn))
        
    def __readDebugProperties(self, quiet=0):
        """
        Private method to read in the project debugger properties file (.e4d, .e3d)
        
        @param quiet flag indicating quiet operations.
                If this flag is true, no errors are reported.
        """
        if self.pfile is None:
            if not quiet:
                KQMessageBox.critical(None,
                    self.trUtf8("Read debugger properties"),
                    self.trUtf8("Please save the project first."))
            return
            
        fn, ext = os.path.splitext(os.path.basename(self.pfile))
        
        try:
            if ext.lower() in [".e4pz", "*.e3pz"]:
                if ext.lower() == ".e3pz":
                    fn = os.path.join(self.ppath, '%s.e3dz' % fn)
                else:
                    fn = os.path.join(self.getProjectManagementDir(), '%s.e4dz' % fn)
                try:
                    import gzip
                except ImportError:
                    if not quiet:
                        KQMessageBox.critical(None,
                            self.trUtf8("Read debugger properties"),
                            self.trUtf8("""Compressed project session files not"""
                                        """ supported. The compression library is"""
                                        """ missing."""))
                    return
                f = gzip.open(fn, "rb")
            else:
                if ext.lower() == ".e3p":
                    fn = os.path.join(self.ppath, '%s.e3d' % fn)
                else:
                    fn = os.path.join(self.getProjectManagementDir(), '%s.e4d' % fn)
                f = open(fn, "rb")
            line = f.readline()
            dtdLine = f.readline()
            f.close()
        except EnvironmentError:
            if not quiet:
                KQMessageBox.critical(None,
                    self.trUtf8("Read debugger properties"),
                    self.trUtf8("<p>The project debugger properties file <b>%1</b> could"
                                " not be read.</p>").arg(fn))
            return
            
        # now read the file
        if line.startswith('<?xml'):
            self.__readXMLDebugProperties(fn, dtdLine.startswith("<!DOCTYPE"), quiet)
        else:
            if not quiet:
                KQMessageBox.critical(None,
                    self.trUtf8("Read debugger properties"),
                    self.trUtf8("<p>The project debugger properties file <b>%1</b> has an"
                                " unsupported format.</p>").arg(fn))
        
    def __readXMLDebugProperties(self, fn, validating, quiet):
        """
        Public method to read the debugger properties from an XML file.
        
        @param fn filename of the project debugger properties file to be read
            (string or QString)
        @param validating flag indicating a validation of the XML file is
            requested (boolean)
        @param quiet flag indicating quiet operations.
            If this flag is true, no errors are reported.
        """
        fn = unicode(fn)
        if fn.lower().endswith("e4dz") or fn.lower().endswith("e3dz"):
            # work around for a bug in xmlproc
            validating = False
        
        parser = make_parser(validating)
        handler = DebuggerPropertiesHandler(self)
        er = XMLEntityResolver()
        eh = XMLErrorHandler()
        
        parser.setContentHandler(handler)
        parser.setEntityResolver(er)
        parser.setErrorHandler(eh)
        
        try:
            if fn.lower().endswith("e4dz") or fn.lower().endswith("e3dz"):
                try:
                    import gzip
                except ImportError:
                    if not quiet:
                        KQMessageBox.critical(None,
                            self.trUtf8("Read debugger properties"),
                            self.trUtf8("<p>The project debugger properties file"
                                        " <b>%1</b> could not be read.</p>").arg(fn))
                    return
                f = gzip.open(fn, "rb")
            else:
                f = open(fn, "rb")
            try:
                try:
                    parser.parse(f)
                except UnicodeEncodeError:
                    f.seek(0)
                    buf = cStringIO.StringIO(f.read())
                    parser.parse(buf)
                if self.debugProperties["INTERPRETER"]:
                    self.debugPropertiesLoaded = True
                else:
                    self.debugPropertiesLoaded = False
            finally:
                f.close()
        except IOError:
            if not quiet:
                KQMessageBox.critical(None,
                    self.trUtf8("Read debugger properties"),
                    self.trUtf8("<p>The project debugger properties file <b>%1</b> could"
                                " not be read.</p>")
                        .arg(fn))
            return
        except XMLFatalParseError:
            pass
            
        if not quiet:
            eh.showParseMessages()
        
    def __writeDebugProperties(self, quiet=0):
        """
        Private method to write the project debugger properties file (.e4d)
        
        @param quiet flag indicating quiet operations.
                If this flag is true, no errors are reported.
        """
        if self.pfile is None or \
           self.pfile.endswith('e3p') or \
           self.pfile.endswith('e3pz'):
            if not quiet:
                KQMessageBox.critical(None,
                    self.trUtf8("Save debugger properties"),
                    self.trUtf8("Please save the project first."))
            return
            
        fn, ext = os.path.splitext(os.path.basename(self.pfile))
        
        try:
            if ext.lower() == ".e4pz":
                fn = os.path.join(self.getProjectManagementDir(), '%s.e4dz' % fn)
                try:
                    import gzip
                except ImportError:
                    if not quiet:
                        KQMessageBox.critical(None,
                            self.trUtf8("Save debugger properties"),
                            self.trUtf8("""Compressed project debugger properties files"""
                                        """ not supported. The compression library is"""
                                        """ missing."""))
                    return
                f = gzip.open(fn, "wb")
            else:
                fn = os.path.join(self.getProjectManagementDir(), '%s.e4d' % fn)
                f = open(fn, "wb")
            
            DebuggerPropertiesWriter(f, os.path.splitext(os.path.basename(fn))[0])\
                .writeXML()
            
            f.close()
            
        except IOError:
            if not quiet:
                KQMessageBox.critical(None,
                    self.trUtf8("Save debugger properties"),
                    self.trUtf8("<p>The project debugger properties file <b>%1</b> could"
                                " not be written.</p>")
                        .arg(fn))
        
    def __deleteDebugProperties(self):
        """
        Private method to delete the project debugger properties file (.e3d)
        """
        if self.pfile is None:
            if not quiet:
                KQMessageBox.critical(None,
                    self.trUtf8("Delete debugger properties"),
                    self.trUtf8("Please save the project first."))
            return
            
        fname, ext = os.path.splitext(os.path.basename(self.pfile))
        
        for fn in [os.path.join(self.getProjectManagementDir(), "%s.e4dz" % fname), 
                   os.path.join(self.getProjectManagementDir(), "%s.e4d" % fname), 
                   os.path.join(self.ppath, "%s.e3dz" % fname), 
                   os.path.join(self.ppath, "%s.e3d" % fname)]:
            if os.path.exists(fn):
                try:
                    os.remove(fn)
                except OSError:
                    KQMessageBox.critical(None,
                        self.trUtf8("Delete debugger properties"),
                        self.trUtf8("<p>The project debugger properties file <b>%1</b>"
                                    " could not be deleted.</p>")
                            .arg(fn))
        
    def __initDebugProperties(self):
        """
        Private method to initialize the debug properties.
        """
        self.debugPropertiesLoaded = 0
        self.debugProperties = {}
        for key in self.__class__.dbgKeynames:
            self.debugProperties[key] = ""
        self.debugProperties["ENVIRONMENTOVERRIDE"] = 0
        self.debugProperties["REMOTEDEBUGGER"] = 0
        self.debugProperties["PATHTRANSLATION"] = 0
        self.debugProperties["CONSOLEDEBUGGER"] = 0
        self.debugProperties["REDIRECT"] = 1
        self.debugProperties["NOENCODING"] = 0
    
    def isDebugPropertiesLoaded(self):
        """
        Public method to return the status of the debug properties.
        
        @return load status of debug properties (boolean)
        """
        return self.debugPropertiesLoaded
        
    def __showDebugProperties(self):
        """
        Private slot to display the debugger properties dialog.
        """
        dlg = DebuggerPropertiesDialog(self)
        if dlg.exec_() == QDialog.Accepted:
            dlg.storeData()
        
    def getDebugProperty(self, key):
        """
        Public method to retrieve a debugger property.
        
        @param key key of the property (string)
        @return value of the property
        """
        return self.debugProperties[key]
        
    def setDbgInfo(self, argv, wd, env, excReporting, excList, excIgnoreList, 
                   autoClearShell, tracePython = None, autoContinue = None):
        """
        Public method to set the debugging information.
        
        @param argv command line arguments to be used (string or QString)
        @param wd working directory (string or QString)
        @param env environment setting (string or QString)
        @param excReporting flag indicating the highlighting of exceptions
        @param excList list of exceptions to be highlighted (QStringList)
        @param excIgnoreList list of exceptions to be ignored (QStringList)
        @param autoClearShell flag indicating, that the interpreter window
            should be cleared (boolean)
        @keyparam tracePython flag to indicate if the Python library should be
            traced as well (boolean)
        @keyparam autoContinue flag indicating, that the debugger should not stop
            at the first executable line (boolean)
        """
        self.dbgCmdline = unicode(argv)
        self.dbgWd = unicode(wd)
        self.dbgEnv = env
        self.dbgReportExceptions = excReporting
        self.dbgExcList = excList[:]                # keep a copy of the list
        self.dbgExcIgnoreList = excIgnoreList[:]    # keep a copy of the list
        self.dbgAutoClearShell = autoClearShell
        if tracePython is not None:
            self.dbgTracePython = tracePython
        if autoContinue is not None:
            self.dbgAutoContinue = autoContinue
    
    def addLanguage(self):
        """
        Public slot used to add a language to the project.
        """
        if self.pdata["PROJECTTYPE"][0] in \
                ["Qt4", "Qt4C", "E4Plugin", "PySide", "PySideC"] and \
           (len(self.pdata["TRANSLATIONPATTERN"]) == 0 or \
            self.pdata["TRANSLATIONPATTERN"][0] == ''):
            KQMessageBox.critical(None,
                self.trUtf8("Add Language"),
                self.trUtf8("You have to specify a translation pattern first."))
            return
        
        dlg = AddLanguageDialog(self.parent())
        if dlg.exec_() == QDialog.Accepted:
            lang = unicode(dlg.getSelectedLanguage())
            if self.pdata["PROJECTTYPE"][0] in \
                    ["Qt4", "Qt4C", "E4Plugin", "PySide", "PySideC"]:
                langFile = self.pdata["TRANSLATIONPATTERN"][0].replace("%language%", lang)
                self.appendFile(langFile)
            self.emit(SIGNAL("projectLanguageAddedByCode"), lang)
        
    def __binaryTranslationFile(self, langFile):
        """
        Private method to calculate the filename of the binary translations file
        given the name of the raw translations file.
        
        @param langFile name of the raw translations file (string)
        @return name of the binary translations file (string)
        """
        qmFile = ""
        try:
            if self.__binaryTranslationsCallbacks[self.pdata["PROJECTTYPE"][0]] \
               is not None:
                qmFile = self.__binaryTranslationsCallbacks\
                         [self.pdata["PROJECTTYPE"][0]](langFile)
        except KeyError:
                qmFile = langFile.replace('.ts', '.qm')
        if qmFile == langFile:
            qmFile = ""
        return qmFile
        
    def checkLanguageFiles(self):
        """
        Public slot to check the language files after a release process.
        """
        tbPath = self.pdata["TRANSLATIONSBINPATH"] and \
                 self.pdata["TRANSLATIONSBINPATH"][0] or ""
        for langFile in self.pdata["TRANSLATIONS"][:]:
            qmFile = self.__binaryTranslationFile(langFile)
            if qmFile:
                if qmFile not in self.pdata["TRANSLATIONS"] and \
                   os.path.exists(os.path.join(self.ppath, qmFile)):
                    self.appendFile(qmFile)
                if tbPath:
                    qmFile = os.path.join(tbPath, os.path.basename(qmFile))
                    if qmFile not in self.pdata["TRANSLATIONS"] and \
                       os.path.exists(os.path.join(self.ppath, qmFile)):
                        self.appendFile(qmFile)
        
    def removeLanguageFile(self, langFile):
        """
        Public slot to remove a translation from the project.
        
        The translation file is not deleted from the project directory.
        
        @param langFile the translation file to be removed (string)
        """
        langFile = langFile.replace(self.ppath+os.sep, '')
        qmFile = self.__binaryTranslationFile(langFile)
        self.pdata["TRANSLATIONS"].remove(langFile)
        self.__model.removeItem(langFile)
        if qmFile:
            try:
                if self.pdata["TRANSLATIONSBINPATH"]:
                    qmFile = os.path.join(self.pdata["TRANSLATIONSBINPATH"][0],
                        os.path.basename(qmFile)).replace(self.ppath+os.sep, '')
                self.pdata["TRANSLATIONS"].remove(qmFile)
                self.__model.removeItem(qmFile)
            except ValueError:
                pass
        self.setDirty(True)
        
    def deleteLanguageFile(self, langFile):
        """
        Public slot to delete a translation from the project directory.
        
        @param langFile the translation file to be removed (string)
        """
        langFile = langFile.replace(self.ppath+os.sep, '')
        qmFile = self.__binaryTranslationFile(langFile)
        
        try:
            fn = os.path.join(self.ppath, langFile)
            if os.path.exists(fn):
                os.remove(fn)
        except IOError:
            KQMessageBox.critical(None,
                self.trUtf8("Delete translation"),
                self.trUtf8("<p>The selected translation file <b>%1</b> could not be"
                    " deleted.</p>").arg(langFile))
            return
        
        self.removeLanguageFile(langFile)
        
        # now get rid of the .qm file
        if qmFile:
            try:
                if self.pdata["TRANSLATIONSBINPATH"]:
                    qmFile = os.path.join(self.pdata["TRANSLATIONSBINPATH"][0],
                        os.path.basename(qmFile)).replace(self.ppath+os.sep, '')
                fn = os.path.join(self.ppath, qmFile)
                if os.path.exists(fn):
                    os.remove(fn)
            except IOError:
                KQMessageBox.critical(None,
                    self.trUtf8("Delete translation"),
                    self.trUtf8("<p>The selected translation file <b>%1</b> could not be"
                        " deleted.</p>").arg(qmFile))
                return
        
    def appendFile(self, fn, isSourceFile = False, updateModel = True):
        """
        Public method to append a file to the project.
        
        @param fn filename to be added to the project (string or QString)
        @param isSourceFile flag indicating that this is a source file
                even if it doesn't have the source extension (boolean)
        @param updateModel flag indicating an update of the model is requested (boolean)
        """
        fn = unicode(fn)
        dirty = False
        
        if os.path.isabs(fn):
            # make it relative to the project root, if it starts with that path
            newfn = fn.replace(self.ppath+os.sep, '')
        else:
            # assume relative paths are relative to the project root
            newfn = fn
        newdir = os.path.dirname(newfn)
        
        if isSourceFile:
            filetype = "SOURCES"
        else:
            filetype = "OTHERS"
            bfn = os.path.basename(newfn)
            if fnmatch.fnmatch(bfn, '*.ts') or fnmatch.fnmatch(bfn, '*.qm'):
                filetype = "TRANSLATIONS"
            else:
                for pattern in reversed(sorted(self.pdata["FILETYPES"].keys())):
                    if fnmatch.fnmatch(bfn, pattern):
                        filetype = self.pdata["FILETYPES"][pattern]
                        break
        
        if filetype == "__IGNORE__":
            return
        
        if filetype in ["SOURCES", "FORMS", "INTERFACES", "RESOURCES"]:
            if filetype == "SOURCES":
                if newfn not in self.pdata["SOURCES"]:
                    self.pdata["SOURCES"].append(newfn)
                    self.emit(SIGNAL('projectSourceAdded'), newfn)
                    updateModel and self.__model.addNewItem("SOURCES", newfn)
                    dirty = True
                else:
                    updateModel and self.repopulateItem(newfn)
            elif filetype == "FORMS":
                if newfn not in self.pdata["FORMS"]:
                    self.pdata["FORMS"].append(newfn)
                    self.emit(SIGNAL('projectFormAdded'), newfn)
                    updateModel and self.__model.addNewItem("FORMS", newfn)
                    dirty = True
                else:
                    updateModel and self.repopulateItem(newfn)
            elif filetype == "INTERFACES":
                if newfn not in self.pdata["INTERFACES"]:
                    self.pdata["INTERFACES"].append(newfn)
                    self.emit(SIGNAL('projectInterfaceAdded'), newfn)
                    updateModel and self.__model.addNewItem("INTERFACES", newfn)
                    dirty = True
                else:
                    updateModel and self.repopulateItem(newfn)
            elif filetype == "RESOURCES":
                if newfn not in self.pdata["RESOURCES"]:
                    self.pdata["RESOURCES"].append(newfn)
                    self.emit(SIGNAL('projectResourceAdded'), newfn)
                    updateModel and self.__model.addNewItem("RESOURCES", newfn)
                    dirty = True
                else:
                    updateModel and self.repopulateItem(newfn)
            if newdir not in self.subdirs:
                self.subdirs.append(newdir)
        elif filetype == "TRANSLATIONS":
            if newfn not in self.pdata["TRANSLATIONS"]:
                self.pdata["TRANSLATIONS"].append(newfn)
                updateModel and self.__model.addNewItem("TRANSLATIONS", newfn)
                self.emit(SIGNAL('projectLanguageAdded'), newfn)
                dirty = True
            else:
                updateModel and self.repopulateItem(newfn)
        else:   # filetype == "OTHERS"
            if newfn not in self.pdata["OTHERS"]:
                self.pdata['OTHERS'].append(newfn)
                self.othersAdded(newfn, updateModel)
                dirty = True
            else:
                updateModel and self.repopulateItem(newfn)
            if newdir not in self.otherssubdirs:
                self.otherssubdirs.append(newdir)
        
        if dirty:
            self.setDirty(True)
        
    def addFiles(self, filter = None, startdir = None):
        """
        Public slot used to add files to the project.
        
        @param filter filter to be used by the add file dialog
            (string out of source, form, resource, interface, others)
        @param startdir start directory for the selection dialog
        """
        if startdir is None:
            startdir = self.ppath
        dlg = AddFileDialog(self, self.parent(), filter, startdir=startdir)
        if dlg.exec_() == QDialog.Accepted:
            fnames, target, isSource = dlg.getData()
            if target != '':
                for fn in fnames:
                    ext = os.path.splitext(fn)[1]
                    targetfile = os.path.join(target, os.path.basename(fn))
                    if not Utilities.samepath(os.path.dirname(fn), target):
                        try:
                            if not os.path.isdir(target):
                                os.makedirs(target)
                                
                            if os.path.exists(targetfile):
                                res = KQMessageBox.warning(None,
                                    self.trUtf8("Add file"),
                                    self.trUtf8("<p>The file <b>%1</b> already"
                                        " exists.</p><p>Overwrite it?</p>")
                                        .arg(targetfile),
                                    QMessageBox.StandardButtons(\
                                        QMessageBox.No | \
                                        QMessageBox.Yes),
                                    QMessageBox.No)
                                if res != QMessageBox.Yes:
                                    return  # don't overwrite
                                    
                            shutil.copy(fn, target)
                            if ext == '.ui' and os.path.isfile(fn+'.h'):
                                shutil.copy(fn+'.h', target)
                        except IOError, why:
                            KQMessageBox.critical(None,
                                self.trUtf8("Add file"),
                                self.trUtf8("<p>The selected file <b>%1</b> could not be"
                                    " added to <b>%2</b>.</p>")
                                    .arg(fn)
                                    .arg(target),
                                QMessageBox.StandardButtons(\
                                    QMessageBox.Abort))
                            return
                            
                    self.appendFile(targetfile, isSource or filter == 'source')
                    if ext == '.ui' and os.path.isfile(targetfile + '.h'):
                        self.appendFile(targetfile + '.h')
            else:
                KQMessageBox.critical(None,
                    self.trUtf8("Add file"),
                    self.trUtf8("The target directory must not be empty."),
                    QMessageBox.StandardButtons(\
                        QMessageBox.Abort))
        
    def __addSingleDirectory(self, filetype, source, target, quiet = False):
        """
        Private method used to add all files of a single directory to the project.
        
        @param filetype type of files to add (string)
        @param source source directory (string)
        @param target target directory (string)
        @param quiet flag indicating quiet operations (boolean)
        """
        # get all relevant filename patterns
        patterns = []
        ignorePatterns = []
        for pattern, patterntype in self.pdata["FILETYPES"].items():
            if patterntype == filetype:
                patterns.append(pattern)
            elif patterntype == "__IGNORE__":
                ignorePatterns.append(pattern)
        
        files = []
        for pattern in patterns:
            sstring = "%s%s%s" % (source, os.sep, pattern)
            files.extend(glob.glob(sstring))
        
        if len(files) == 0:
            if not quiet:
                KQMessageBox.information(None,
                    self.trUtf8("Add directory"),
                    self.trUtf8("<p>The source directory doesn't contain"
                        " any files belonging to the selected category.</p>"))
            return
        
        if not Utilities.samepath(target, source) and not os.path.isdir(target):
            try:
                os.makedirs(target)
            except IOError, why:
                KQMessageBox.critical(None,
                    self.trUtf8("Add directory"),
                    self.trUtf8("<p>The target directory <b>%1</b> could not be"
                        " created.</p>")
                        .arg(target),
                    QMessageBox.StandardButtons(\
                        QMessageBox.Abort))
                return
        
        for file in files:
            for pattern in ignorePatterns:
                if fnmatch.fnmatch(file, pattern):
                    continue
            
            targetfile = os.path.join(target, os.path.basename(file))
            if not Utilities.samepath(target, source):
                try:
                    if os.path.exists(targetfile):
                        res = KQMessageBox.warning(None,
                            self.trUtf8("Add directory"),
                            self.trUtf8("<p>The file <b>%1</b> already exists.</p>"
                                        "<p>Overwrite it?</p>")
                                .arg(targetfile),
                            QMessageBox.StandardButtons(\
                                QMessageBox.No | \
                                QMessageBox.Yes),
                            QMessageBox.No)
                        if res != QMessageBox.Yes:
                            continue  # don't overwrite, carry on with next file
                            
                    shutil.copy(file, target)
                except EnvironmentError:
                    continue
            self.appendFile(targetfile)
        
    def __addRecursiveDirectory(self, filetype, source, target):
        """
        Private method used to add all files of a directory tree.
        
        The tree is rooted at source to another one rooted at target. This
        method decents down to the lowest subdirectory.
        
        @param filetype type of files to add (string)
        @param source source directory (string)
        @param target target directory (string)
        """
        # first perform the addition of source
        self.__addSingleDirectory(filetype, source, target, True)
        
        # now recurse into subdirectories
        for name in os.listdir(source):
            ns = os.path.join(source, name)
            if os.path.isdir(ns):
                nt = os.path.join(target, name)
                self.__addRecursiveDirectory(filetype, ns, nt)
        
    def addDirectory(self, filter = None, startdir = None):
        """
        Public method used to add all files of a directory to the project.
        
        @param filter filter to be used by the add directory dialog
            (string out of source, form, resource, interface, others)
        @param startdir start directory for the selection dialog
        """
        if startdir is None:
            startdir = self.ppath
        dlg = AddDirectoryDialog(self, filter, self.parent(), startdir=startdir)
        if dlg.exec_() == QDialog.Accepted:
            filetype, source, target, recursive = dlg.getData()
            if target == '':
                KQMessageBox.critical(None,
                    self.trUtf8("Add directory"),
                    self.trUtf8("The target directory must not be empty."),
                    QMessageBox.StandardButtons(\
                        QMessageBox.Abort))
                return
            
            if filetype == 'OTHERS':
                self.__addToOthers(QString(source))
                return
            
            if source == '':
                KQMessageBox.critical(None,
                    self.trUtf8("Add directory"),
                    self.trUtf8("The source directory must not be empty."),
                    QMessageBox.StandardButtons(\
                        QMessageBox.Abort))
                return
            
            if recursive:
                self.__addRecursiveDirectory(filetype, source, target)
            else:
                self.__addSingleDirectory(filetype, source, target)
        
    def __addToOthers(self, fn):
        """
        Private method to add file/directory to the OTHERS project data.
        
        @param fn filename or directoryname to add
        """
        if not fn.isEmpty():
            fn = unicode(fn)
            
            # if it is below the project directory, make it relative to that
            fn = fn.replace(self.ppath+os.sep, '')
            
            # if it ends with the directory separator character, remove it
            if fn.endswith(os.sep):
                fn = fn[:-1]
            if fn not in self.pdata["OTHERS"]:
                self.pdata['OTHERS'].append(fn)
                self.othersAdded(fn)
                self.setDirty(True)
            if os.path.isdir(fn) and fn not in self.otherssubdirs:
                self.otherssubdirs.append(fn)
        
    def addSourceFiles(self):
        """
        Public slot to add source files to the current project.
        """
        self.addFiles('source')
        
    def addUiFiles(self):
        """
        Public slot to add forms to the current project.
        """
        self.addFiles('form')
        
    def addIdlFiles(self):
        """
        Public slot to add IDL interfaces to the current project.
        """
        self.addFiles('interface')
        
    def addResourceFiles(self):
        """
        Public slot to add Qt resources to the current project.
        """
        self.addFiles('resource')
        
    def addOthersFiles(self):
        """
        Private slot to add files to the OTHERS project data.
        """
        self.addFiles('others')
        
    def addSourceDir(self):
        """
        Public slot to add all source files of a directory to the current project.
        """
        self.addDirectory('source')
        
    def addUiDir(self):
        """
        Public slot to add all forms of a directory to the current project.
        """
        self.addDirectory('form')
        
    def addIdlDir(self):
        """
        Public slot to add all IDL interfaces of a directory to the current project.
        """
        self.addDirectory('interface')
        
    def addResourceDir(self):
        """
        Public slot to add all Qt resource files of a directory to the current project.
        """
        self.addDirectory('resource')
        
    def addOthersDir(self):
        """
        Private slot to add a directory to the OTHERS project data.
        """
        self.addDirectory('others')
        
    def renameMainScript(self, oldfn, newfn):
        """
        Public method to rename the main script.
        
        @param oldfn old filename (string)
        @param newfn new filename of the main script (string)
        """
        if self.pdata["MAINSCRIPT"]:
            ofn2 = unicode(oldfn)
            ofn = ofn2.replace(self.ppath+os.sep, '')
            if ofn != self.pdata["MAINSCRIPT"][0]:
                return
            
            fn2 = unicode(newfn)
            fn = fn2.replace(self.ppath+os.sep, '')
            self.pdata["MAINSCRIPT"] = [fn]
            self.setDirty(True)
        
    def renameFile(self, oldfn, newfn = None):
        """
        Public slot to rename a file of the project.
        
        @param oldfn old filename of the file (string)
        @param newfn new filename of the file (string)
        @return flag indicating success
        """
        fn2 = unicode(oldfn)
        fn = fn2.replace(self.ppath+os.sep, '')
        isSourceFile = fn in self.pdata["SOURCES"]
        
        if newfn is None:
            newfn = KQFileDialog.getSaveFileName(\
                None,
                self.trUtf8("Rename file"),
                os.path.dirname(oldfn),
                QString(),
                None,
                QFileDialog.Options(QFileDialog.DontConfirmOverwrite))
            if newfn.isEmpty():
                return False
        
        newfn = unicode(newfn)
        if os.path.exists(newfn):
            canceled = KQMessageBox.warning(None,
                self.trUtf8("Rename File"),
                self.trUtf8("""<p>The file <b>%1</b> already exists. Overwrite it?</p>""")
                    .arg(newfn),
                QMessageBox.StandardButtons(\
                    QMessageBox.No | \
                    QMessageBox.Yes),
                QMessageBox.No)
            if canceled != QMessageBox.Yes:
                return False
        
        try:
            os.rename(oldfn, newfn)
        except OSError, msg:
            KQMessageBox.critical(None,
                self.trUtf8("Rename File"),
                self.trUtf8("""<p>The file <b>%1</b> could not be renamed.<br />"""
                    """Reason: %2</p>""").arg(oldfn).arg(unicode(msg)))
            return False

        if fn in self.pdata["SOURCES"] or \
           fn in self.pdata["FORMS"] or \
           fn in self.pdata["TRANSLATIONS"] or \
           fn in self.pdata["INTERFACES"] or \
           fn in self.pdata["RESOURCES"] or \
           fn in self.pdata["OTHERS"]:
            self.renameFileInPdata(oldfn, newfn, isSourceFile)
        
        return True
        
    def renameFileInPdata(self, oldname, newname, isSourceFile = False):
        """
        Public method to rename a file in the pdata structure.
        
        @param oldname old filename (string)
        @param newname new filename (string)
        @param isSourceFile flag indicating that this is a source file
                even if it doesn't have the source extension (boolean)
        """
        fn = oldname.replace(self.ppath+os.sep, '')
        if os.path.dirname(oldname) == os.path.dirname(newname):
            self.removeFile(oldname, False)
            self.appendFile(newname, isSourceFile, False)
            self.__model.renameItem(fn, newname)
        else:
            self.removeFile(oldname)
            self.appendFile(newname, isSourceFile)
        self.emit(SIGNAL('projectFileRenamed'), oldname, newname)
        
        self.renameMainScript(fn, newname)
        
    def getFiles(self, start):
        """
        Public method to get all files starting with a common prefix.
        
        @param start prefix (string or QString)
        """
        filelist = []
        start = unicode(start).replace(self.ppath+os.sep, '')
        for key in ["SOURCES", "FORMS", "INTERFACES", "RESOURCES", "OTHERS"]:
            for entry in self.pdata[key][:]:
                if entry.startswith(start):
                    filelist.append(os.path.join(self.ppath, entry))
        return filelist
        
    def copyDirectory(self, olddn, newdn):
        """
        Public slot to copy a directory.
        
        @param olddn original directory name (string or QString)
        @param newdn new directory name (string or QString)
        """
        olddn = unicode(olddn).replace(self.ppath+os.sep, '')
        newdn = unicode(newdn).replace(self.ppath+os.sep, '')
        for key in ["SOURCES", "FORMS", "INTERFACES", "RESOURCES", "OTHERS"]:
            for entry in self.pdata[key][:]:
                if entry.startswith(olddn):
                    entry = entry.replace(olddn, newdn)
                    self.appendFile(os.path.join(self.ppath, entry), key == "SOURCES")
        self.setDirty(True)
        
    def moveDirectory(self, olddn, newdn):
        """
        Public slot to move a directory.
        
        @param olddn old directory name (string or QString)
        @param newdn new directory name (string or QString)
        """
        olddn = unicode(olddn).replace(self.ppath+os.sep, '')
        newdn = unicode(newdn).replace(self.ppath+os.sep, '')
        typeStrings = []
        for key in ["SOURCES", "FORMS", "INTERFACES", "RESOURCES", "OTHERS"]:
            for entry in self.pdata[key][:]:
                if entry.startswith(olddn):
                    if key not in typeStrings:
                        typeStrings.append(key)
                    self.pdata[key].remove(entry)
                    entry = entry.replace(olddn, newdn)
                    self.pdata[key].append(entry)
            if key == "OTHERS":
                if newdn not in self.otherssubdirs:
                    self.otherssubdirs.append(newdn)
            else:
                if newdn not in self.subdirs:
                    self.subdirs.append(newdn)
        self.setDirty(True)
        typeString = typeStrings[0]
        del typeStrings[0]
        self.__model.removeItem(olddn)
        self.__model.addNewItem(typeString, newdn, typeStrings)
        self.emit(SIGNAL('directoryRemoved'), olddn)
        
    def removeFile(self, fn, updateModel = True):
        """
        Public slot to remove a file from the project.
        
        The file is not deleted from the project directory.
        
        @param fn filename to be removed from the project
        @param updateModel flag indicating an update of the model is requested (boolean)
        """
        fn2 = unicode(fn)
        fn = fn2.replace(self.ppath+os.sep, '')
        dirty = True
        if fn in self.pdata["SOURCES"]:
            self.pdata["SOURCES"].remove(fn)
        elif fn in self.pdata["FORMS"]:
            self.pdata["FORMS"].remove(fn)
        elif fn in self.pdata["INTERFACES"]:
            self.pdata["INTERFACES"].remove(fn)
        elif fn in self.pdata["RESOURCES"]:
            self.pdata["RESOURCES"].remove(fn)
        elif fn in self.pdata["OTHERS"]:
            self.pdata["OTHERS"].remove(fn)
        elif fn in self.pdata["TRANSLATIONS"]:
            self.pdata["TRANSLATIONS"].remove(fn)
        else:
            dirty = False
        updateModel and self.__model.removeItem(fn)
        if dirty:
            self.setDirty(True)
        
    def removeDirectory(self, dn):
        """
        Public slot to remove a directory from the project.
        
        The directory is not deleted from the project directory.
        
        @param dn directory name to be removed from the project
        """
        dirty = False
        dn2 = unicode(dn)
        dn = dn2.replace(self.ppath+os.sep, '')
        for entry in self.pdata["OTHERS"][:]:
            if entry.startswith(dn):
                self.pdata["OTHERS"].remove(entry)
                dirty = True
        if not dn.endswith(os.sep):
            dn2 = dn + os.sep
        else:
            dn2 = dn
        for key in ["SOURCES", "FORMS", "INTERFACES", "RESOURCES", ]:
            for entry in self.pdata[key][:]:
                if entry.startswith(dn2):
                    self.pdata[key].remove(entry)
                    dirty = True
        self.__model.removeItem(dn)
        if dirty:
            self.setDirty(True)
        self.emit(SIGNAL('directoryRemoved'), dn)
        
    def deleteFile(self, fn):
        """
        Public slot to delete a file from the project directory.
        
        @param fn filename to be deleted from the project
        @return flag indicating success
        """
        fn = unicode(fn)
        try:
            os.remove(os.path.join(self.ppath, fn))
            dummy, ext = os.path.splitext(fn)
            if ext == '.ui':
                fn2 = os.path.join(self.ppath, '%s.h' % fn)
                if os.path.isfile(fn2):
                    os.remove(fn2)
        except EnvironmentError:
            KQMessageBox.critical(None,
                self.trUtf8("Delete file"),
                self.trUtf8("<p>The selected file <b>%1</b> could not be deleted.</p>")
                    .arg(fn))
            return False
        
        self.removeFile(fn)
        if ext == '.ui':
            self.removeFile(fn + '.h')
        return True
        
    def deleteDirectory(self, dn):
        """
        Public slot to delete a directory from the project directory.
        
        @param dn directory name to be removed from the project
        @return flag indicating success
        """
        dn = unicode(dn)
        if not os.path.isabs(dn):
            dn = os.path.join(self.ppath, dn)
        try:
            shutil.rmtree(dn, True)
        except EnvironmentError:
            KQMessageBox.critical(None,
                self.trUtf8("Delete directory"),
                self.trUtf8("<p>The selected directory <b>%1</b> could not be"
                    " deleted.</p>").arg(fn))
            return False
        
        self.removeDirectory(dn)
        return True
    
    def hasEntry(self, fn):
        """
        Public method to check the project for a file.
        
        @param fn filename to be checked (string or QString)
        @return flag indicating, if the project contains the file (boolean)
        """
        fn2 = unicode(fn)
        fn = fn2.replace(self.ppath+os.sep, '')
        if fn in self.pdata["SOURCES"] or \
           fn in self.pdata["FORMS"] or \
           fn in self.pdata["INTERFACES"] or \
           fn in self.pdata["RESOURCES"] or \
           fn in self.pdata["OTHERS"]:
            return True
        else:
            return False
        
    def newProject(self):
        """
        Public slot to built a new project.
        
        This method displays the new project dialog and initializes
        the project object with the data entered.
        """
        if not self.checkDirty():
            return
            
        dlg = PropertiesDialog(self, True)
        if dlg.exec_() == QDialog.Accepted:
            self.closeProject()
            dlg.storeData()
            self.pdata["VCS"] = ['None']
            self.opened = True
            if not self.pdata["FILETYPES"]:
                self.initFileTypes()
            self.setDirty(True)
            self.closeAct.setEnabled(True)
            self.saveasAct.setEnabled(True)
            self.actGrp2.setEnabled(True)
            self.propsAct.setEnabled(True)
            self.userPropsAct.setEnabled(True)
            self.filetypesAct.setEnabled(True)
            self.lexersAct.setEnabled(True)
            self.sessActGrp.setEnabled(False)
            self.dbgActGrp.setEnabled(True)
            self.menuDebuggerAct.setEnabled(True)
            self.menuSessionAct.setEnabled(False)
            self.menuCheckAct.setEnabled(True)
            self.menuShowAct.setEnabled(True)
            self.menuDiagramAct.setEnabled(True)
            self.menuApidocAct.setEnabled(True)
            self.menuPackagersAct.setEnabled(True)
            self.pluginGrp.setEnabled(self.pdata["PROJECTTYPE"][0] == "E4Plugin")
            
            self.emit(SIGNAL("projectAboutToBeCreated"))
            
            # create the project directory if it doesn't exist already
            if not os.path.isdir(self.ppath):
                try:
                    os.makedirs(self.ppath)
                except EnvironmentError:
                    KQMessageBox.critical(None,
                        self.trUtf8("Create project directory"),
                        self.trUtf8("<p>The project directory <b>%1</b> could not"
                            " be created.</p>")
                            .arg(self.ppath))
                    self.vcs = self.initVCS()
                    return
                # create an empty __init__.py file to make it a Python package
                # (only for Python and Python3)
                if self.pdata["PROGLANGUAGE"][0] in ["Python", "Python3"]:
                    fn = os.path.join(self.ppath, "__init__.py")
                    f = open(fn, "w")
                    f.close()
                    self.appendFile(fn, True)
                tpd = os.path.join(self.ppath, self.translationsRoot)
                if not self.translationsRoot.endswith(os.sep):
                    tpd = os.path.dirname(tpd)
                if not os.path.isdir(tpd):
                    os.makedirs(tpd)
                if self.pdata["TRANSLATIONSBINPATH"]:
                    tpd = os.path.join(self.ppath, self.pdata["TRANSLATIONSBINPATH"][0])
                    if not os.path.isdir(tpd):
                        os.makedirs(tpd)
                
                # create management directory if not present
                mgmtDir = self.getProjectManagementDir()
                if not os.path.exists(mgmtDir):
                    os.makedirs(mgmtDir)
                
                self.saveProject()
            else:
                # create management directory if not present
                mgmtDir = self.getProjectManagementDir()
                if not os.path.exists(mgmtDir):
                    os.makedirs(mgmtDir)
                
                try:
                    ms = os.path.join(self.ppath, self.pdata["MAINSCRIPT"][0])
                    if os.path.exists(ms):
                        self.appendFile(ms)
                except IndexError:
                    ms = ""
                
                # add existing files to the project
                res = KQMessageBox.question(None,
                    self.trUtf8("New Project"),
                    self.trUtf8("""Add existing files to the project?"""),
                    QMessageBox.StandardButtons(\
                        QMessageBox.No | \
                        QMessageBox.Yes),
                    QMessageBox.Yes)
                if res == QMessageBox.Yes:
                    self.newProjectAddFiles(ms)
                # create an empty __init__.py file to make it a Python package
                # if none exists (only for Python and Python3)
                if self.pdata["PROGLANGUAGE"][0] in ["Python", "Python3"]:
                    fn = os.path.join(self.ppath, "__init__.py")
                    if not os.path.exists(fn):
                        f = open(fn, "w")
                        f.close()
                        self.appendFile(fn, True)
                self.saveProject()
                
                # check, if the existing project directory is already under
                # VCS control
                pluginManager = e4App().getObject("PluginManager")
                for indicator, vcsData in pluginManager.getVcsSystemIndicators().items():
                    if os.path.exists(os.path.join(self.ppath, indicator)):
                        if len(vcsData) > 1:
                            vcsList = QStringList()
                            for vcsSystemStr, vcsSystemDisplay in vcsData:
                                vcsList.append(vcsSystemDisplay)
                            res, vcs_ok = KQInputDialog.getItem(\
                                None,
                                self.trUtf8("New Project"),
                                self.trUtf8("Select Version Control System"),
                                vcsList,
                                0, False)
                            if vcs_ok:
                                for vcsSystemStr, vcsSystemDisplay in vcsData:
                                    if res == vcsSystemDisplay:
                                        vcsSystem = vcsSystemStr
                                        break
                                else:
                                    vcsSystem = "None"
                            else:
                                vcsSystem = "None"
                        else:
                            vcsSystem = vcsData[0][1]
                        self.pdata["VCS"] = [vcsSystem]
                        self.vcs = self.initVCS()
                        self.setDirty(True)
                        if self.vcs is not None:
                            # edit VCS command options
                            vcores = KQMessageBox.question(None,
                                self.trUtf8("New Project"),
                                self.trUtf8("""Would you like to edit the VCS"""
                                    """ command options?"""),
                                QMessageBox.StandardButtons(\
                                    QMessageBox.No | \
                                    QMessageBox.Yes),
                                QMessageBox.No)
                            if vcores == QMessageBox.Yes:
                                codlg = vcsCommandOptionsDialog(self.vcs)
                                if codlg.exec_() == QDialog.Accepted:
                                    self.vcs.vcsSetOptions(codlg.getOptions())
                            # add project file to repository
                            if res == 0:
                                apres = KQMessageBox.question(None,
                                    self.trUtf8("New project"),
                                    self.trUtf8("Shall the project file be added"
                                        " to the repository?"),
                                    QMessageBox.StandardButtons(\
                                        QMessageBox.No | \
                                        QMessageBox.Yes),
                                    QMessageBox.Yes)
                                if apres == QMessageBox.Yes:
                                    self.saveProject()
                                    self.vcs.vcsAdd(self.pfile)
                        else:
                            self.pdata["VCS"] = ['None']
                        self.saveProject()
                        break
            
            # put the project under VCS control
            if self.vcs is None:
                vcsSystemsDict = e4App().getObject("PluginManager")\
                    .getPluginDisplayStrings("version_control")
                vcsSystemsDisplay = QStringList(self.trUtf8("None"))
                keys = vcsSystemsDict.keys()
                keys.sort()
                for key in keys:
                    vcsSystemsDisplay.append(vcsSystemsDict[key])
                vcsSelected, ok = KQInputDialog.getItem(\
                    None,
                    self.trUtf8("New Project"),
                    self.trUtf8("Select version control system for the project"),
                    vcsSystemsDisplay,
                    0, False)
                if ok and vcsSelected != self.trUtf8("None"):
                    for vcsSystem, vcsSystemDisplay in vcsSystemsDict.items():
                        if vcsSystemDisplay == vcsSelected:
                            break
                    else:
                        vcsSystem = "None"
                    self.pdata["VCS"] = [vcsSystem]
                else:
                    self.pdata["VCS"] = ['None']
                self.vcs = self.initVCS()
                if self.vcs is not None:
                    vcsdlg = self.vcs.vcsOptionsDialog(self, self.name)
                    if vcsdlg.exec_() == QDialog.Accepted:
                        vcsDataDict = vcsdlg.getData()
                    else:
                        self.pdata["VCS"] = ['None']
                        self.vcs = self.initVCS()
                self.setDirty(True)
                if self.vcs is not None:
                    # edit VCS command options
                    vcores = KQMessageBox.question(None,
                        self.trUtf8("New Project"),
                        self.trUtf8("""Would you like to edit the VCS command"""
                                    """ options?"""),
                        QMessageBox.StandardButtons(\
                            QMessageBox.No | \
                            QMessageBox.Yes),
                        QMessageBox.No)
                    if vcores == QMessageBox.Yes:
                        codlg = vcsCommandOptionsDialog(self.vcs)
                        if codlg.exec_() == QDialog.Accepted:
                            self.vcs.vcsSetOptions(codlg.getOptions())
                    
                    # create the project in the VCS
                    self.vcs.vcsSetDataFromDict(vcsDataDict)
                    self.saveProject()
                    self.vcs.vcsConvertProject(vcsDataDict, self)
                else:
                    self.emit(SIGNAL('newProjectHooks'))
                    self.emit(SIGNAL('newProject'))
            
            else:
                self.emit(SIGNAL('newProjectHooks'))
                self.emit(SIGNAL('newProject'))
            

    def newProjectAddFiles(self, mainscript):
        """
        Public method to add files to a new project.
        
        @param mainscript name of the mainscript (string)
        """
        QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
        QApplication.processEvents()
        
        # search the project directory for files with known extensions
        filespecs = self.pdata["FILETYPES"].keys()
        for filespec in filespecs:
            files = Utilities.direntries(self.ppath, True, filespec)
            for file in files:
                self.appendFile(file)
        
        # special handling for translation files
        if self.translationsRoot:
            tpd = os.path.join(self.ppath, self.translationsRoot)
            if not self.translationsRoot.endswith(os.sep):
                tpd = os.path.dirname(tpd)
        else:
            tpd = self.ppath
        tslist = []
        if self.pdata["TRANSLATIONPATTERN"]:
            pattern = os.path.basename(self.pdata["TRANSLATIONPATTERN"][0])
            if "%language%" in pattern:
                pattern = pattern.replace("%language%", "*")
            else:
                tpd = self.pdata["TRANSLATIONPATTERN"][0].split("%language%")[0]
        else:
            pattern = "*.ts"
        tslist.extend(Utilities.direntries(tpd, True, pattern))
        pattern = self.__binaryTranslationFile(pattern)
        if pattern:
            tslist.extend(Utilities.direntries(tpd, True, pattern))
        if len(tslist):
            if '_' in os.path.basename(tslist[0]):
                # the first entry determines the mainscript name
                mainscriptname = os.path.splitext(mainscript)[0] or \
                                 os.path.basename(tslist[0]).split('_')[0]
                self.pdata["TRANSLATIONPATTERN"] = \
                    [os.path.join(os.path.dirname(tslist[0]), 
                     "%s_%%language%%%s" % (os.path.basename(tslist[0]).split('_')[0], 
                        os.path.splitext(tslist[0])[1]))]
            else:
                pattern, ok = KQInputDialog.getText(\
                    None,
                    self.trUtf8("Translation Pattern"),
                    self.trUtf8("Enter the path pattern for translation files "
                                "(use '%language%' in place of the language code):"),
                    QLineEdit.Normal, 
                    tslist[0])
                if not pattern.isEmpty:
                    self.pdata["TRANSLATIONPATTERN"] = [unicode(pattern)]
            self.pdata["TRANSLATIONPATTERN"][0] = \
                self.pdata["TRANSLATIONPATTERN"][0].replace(self.ppath+os.sep, "")
            pattern = self.pdata["TRANSLATIONPATTERN"][0].replace("%language%", "*")
            for ts in tslist:
                if fnmatch.fnmatch(ts, pattern):
                    self.pdata["TRANSLATIONS"].append(ts)
                    self.emit(SIGNAL('projectLanguageAdded'), ts)
            if self.pdata["PROGLANGUAGE"][0] in ["Python", "Python3"]:
                self.pdata["MAINSCRIPT"] = ['%s.py' % mainscriptname]
            elif self.pdata["PROGLANGUAGE"][0] == "Ruby":
                self.pdata["MAINSCRIPT"] = ['%s.rb' % mainscriptname]
            if self.pdata["TRANSLATIONSBINPATH"]:
                tpd = os.path.join(self.ppath, 
                                   self.pdata["TRANSLATIONSBINPATH"][0])
                pattern = os.path.splitext(
                    os.path.basename(self.pdata["TRANSLATIONPATTERN"][0]))
                pattern = self.__binaryTranslationFile(pattern)
                qmlist = Utilities.direntries(tpd, True, pattern)
                for qm in qmlist:
                    self.pdata["TRANSLATIONS"].append(qm)
                    self.emit(SIGNAL('projectLanguageAdded'), qm)
        self.setDirty(True)
        QApplication.restoreOverrideCursor()
    
    def __showProperties(self):
        """
        Private slot to display the properties dialog.
        """
        dlg = PropertiesDialog(self, False)
        if dlg.exec_() == QDialog.Accepted:
            projectType = self.pdata["PROJECTTYPE"][0]
            dlg.storeData()
            self.setDirty(True)
            try:
                ms = os.path.join(self.ppath, self.pdata["MAINSCRIPT"][0])
                if os.path.exists(ms):
                    self.appendFile(ms)
            except IndexError:
                pass
            
            if self.pdata["PROJECTTYPE"][0] != projectType:
                # reinitialize filetype associations
                self.initFileTypes()
            
            if self.translationsRoot:
                tp = os.path.join(self.ppath, self.translationsRoot)
                if not self.translationsRoot.endswith(os.sep):
                    tp = os.path.dirname(tp)
            else:
                tp = self.ppath
            if not os.path.isdir(tp):
                os.makedirs(tp)
            if tp != self.ppath and tp not in self.subdirs:
                self.subdirs.append(tp)
            
            if self.pdata["TRANSLATIONSBINPATH"]:
                tp = os.path.join(self.ppath, self.pdata["TRANSLATIONSBINPATH"][0])
                if not os.path.isdir(tp):
                    os.makedirs(tp)
                if tp != self.ppath and tp not in self.subdirs:
                    self.subdirs.append(tp)
            
            self.pluginGrp.setEnabled(self.pdata["PROJECTTYPE"][0] == "E4Plugin")
            
            self.__model.projectPropertiesChanged()
            self.emit(SIGNAL('projectPropertiesChanged'))
        
    def __showUserProperties(self):
        """
        Private slot to display the user specific properties dialog.
        """
        vcsSystem = self.pdata["VCS"] and self.pdata["VCS"][0] or None
        vcsSystemOverride = \
            self.pudata["VCSOVERRIDE"] and self.pudata["VCSOVERRIDE"][0] or None
        
        dlg = UserPropertiesDialog(self)
        if dlg.exec_() == QDialog.Accepted:
            dlg.storeData()
            
            if (self.pdata["VCS"] and \
                self.pdata["VCS"][0] != vcsSystem) or \
               (self.pudata["VCSOVERRIDE"] and \
                self.pudata["VCSOVERRIDE"][0] != vcsSystemOverride) or \
               (vcsSystemOverride is not None and \
                len(self.pudata["VCSOVERRIDE"]) == 0):
                # stop the VCS monitor thread and shutdown VCS
                if self.vcs is not None:
                    self.vcs.stopStatusMonitor()
                    self.disconnect(self.vcs, 
                        SIGNAL("vcsStatusMonitorData(QStringList)"),
                        self.__model.changeVCSStates)
                    self.disconnect(self.vcs, 
                        SIGNAL("vcsStatusMonitorStatus(QString, QString)"),
                        self.__statusMonitorStatus)
                    self.vcs.vcsShutdown()
                    self.vcs = None
                    e4App().getObject("PluginManager").deactivateVcsPlugins()
                # reinit VCS
                self.vcs = self.initVCS()
                # start the VCS monitor thread
                if self.vcs is not None:
                    self.vcs.startStatusMonitor(self)
                    self.connect(self.vcs, 
                         SIGNAL("vcsStatusMonitorData(QStringList)"),
                         self.__model.changeVCSStates)
                    self.connect(self.vcs, 
                         SIGNAL("vcsStatusMonitorStatus(QString, QString)"),
                         self.__statusMonitorStatus)
                self.emit(SIGNAL("reinitVCS"))
            
            if self.pudata["VCSSTATUSMONITORINTERVAL"]:
                self.setStatusMonitorInterval(\
                    self.pudata["VCSSTATUSMONITORINTERVAL"][0])
            else:
                self.setStatusMonitorInterval(\
                    Preferences.getVCS("StatusMonitorInterval"))
        
    def __showFiletypeAssociations(self):
        """
        Public slot to display the filetype association dialog.
        """
        dlg = FiletypeAssociationDialog(self)
        if dlg.exec_() == QDialog.Accepted:
            dlg.transferData()
            self.setDirty(True)
        
    def __showLexerAssociations(self):
        """
        Public slot to display the lexer association dialog.
        """
        dlg = LexerAssociationDialog(self)
        if dlg.exec_() == QDialog.Accepted:
            dlg.transferData()
            self.setDirty(True)
            self.emit(SIGNAL("lexerAssociationsChanged"))
        
    def getEditorLexerAssoc(self, filename):
        """
        Public method to retrieve a lexer association.
        
        @param filename filename used to determine the associated lexer language (string)
        @return the requested lexer language (string)
        """
        # try user settings first
        for pattern, language in self.pdata["LEXERASSOCS"].items():
            if fnmatch.fnmatch(filename, pattern):
                return unicode(language)
        
        # try project type specific defaults next
        projectType = self.pdata["PROJECTTYPE"][0]
        try:
            if self.__lexerAssociationCallbacks[projectType] is not None:
                return self.__lexerAssociationCallbacks[projectType](filename)
        except KeyError:
            pass
        
        # return empty string to signal to use the global setting
        return ""
        
    def checkSecurityString(self, stringToCheck, tag):
        """
        Public method to check a string for security problems.
        
        @param stringToCheck string that should be checked for security problems (string)
        @param tag tag that contained the string (string)
        @return flag indicating a security problem (boolean)
        """
        for r in self.__class__.securityCheckPatterns:
            if r.search(stringToCheck):
                KQMessageBox.warning(None,
                    self.trUtf8("Security Problem"),
                    self.trUtf8("""<p>The <b>%1</b> entry of the project file contains"""
                                """ a security problem.</p>""")\
                        .arg(key))
                return True
        return False
        
    # TO DO: remove method for eric 4.6
    def __migrate(self):
        """
        Private method to migrate the supporting project files to their own
        management directory.
        """
        mgmtDir = self.getProjectManagementDir()
        if not os.path.exists(mgmtDir):
            os.mkdir(mgmtDir)
        
        fn, ext = os.path.splitext(self.pfile)
        
        for file in ['%s.e4q' % fn,                     # user properties file
                     '%s.e4s' % fn, '%s.e4sz' % fn,     # session file
                     '%s.e4t' % fn, '%s.e4tz' % fn,     # task file
                     '%s.e4d' % fn, '%s.e4dz' % fn]:    # debugger properties file
            if os.path.exists(file):
                nfile = file.replace(self.ppath, mgmtDir)
                if os.path.exists(nfile):
                    os.remove(nfile)
                os.rename(file, nfile)
        
    def openProject(self, fn = None, restoreSession = True, reopen = False):
        """
        Public slot to open a project.
        
        @param fn optional filename of the project file to be read
        @param restoreSession flag indicating to restore the project
            session (boolean)
        @keyparam reopen flag indicating a reopening of the project (boolean)
        """
        if not self.checkDirty():
            return
        
        if fn is None:
            fn = KQFileDialog.getOpenFileName(\
                self.parent(),
                self.trUtf8("Open project"),
                QString(),
                self.trUtf8("Project Files (*.e4p *.e4pz *.e3p *.e3pz)"))
            
            if fn.isEmpty():
                fn = None
            else:
                fn = unicode(fn)
        
        QApplication.processEvents()
        
        if fn is not None:
            if self.closeProject():
                QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
                QApplication.processEvents()
                if self.__readProject(fn):
                    self.opened = True
                    if not self.pdata["FILETYPES"]:
                        self.initFileTypes()
                    else:
                        self.updateFileTypes()
                    
                    QApplication.restoreOverrideCursor()
                    QApplication.processEvents()
                    
                    # migrate the project management files
                    self.__migrate()
                    
                    # read a user specific project file
                    self.__readUserProperties()
                    
                    QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
                    QApplication.processEvents()
                    
                    self.vcs = self.initVCS()
                    if self.vcs is None:
                        # check, if project is version controlled
                        pluginManager = e4App().getObject("PluginManager")
                        for indicator, vcsData in \
                                pluginManager.getVcsSystemIndicators().items():
                            if os.path.exists(os.path.join(self.ppath, indicator)):
                                if len(vcsData) > 1:
                                    vcsList = QStringList()
                                    for vcsSystemStr, vcsSystemDisplay in vcsData:
                                        vcsList.append(vcsSystemDisplay)
                                    QApplication.restoreOverrideCursor()
                                    res, vcs_ok = KQInputDialog.getItem(\
                                        None,
                                        self.trUtf8("New Project"),
                                        self.trUtf8("Select Version Control System"),
                                        vcsList,
                                        0, False)
                                    QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
                                    QApplication.processEvents()
                                    if vcs_ok:
                                        for vcsSystemStr, vcsSystemDisplay in vcsData:
                                            if res == vcsSystemDisplay:
                                                vcsSystem = vcsSystemStr
                                                break
                                        else:
                                            vcsSystem = "None"
                                    else:
                                        vcsSystem = "None"
                                else:
                                    vcsSystem = vcsData[0][0]
                                self.pdata["VCS"] = [vcsSystem]
                                self.vcs = self.initVCS()
                                self.setDirty(True)
                    if self.vcs is not None and \
                       self.vcs.vcsRegisteredState(self.ppath) != self.vcs.canBeCommitted:
                        self.pdata["VCS"] = ['None']
                        self.vcs = self.initVCS()
                    self.closeAct.setEnabled(True)
                    self.saveasAct.setEnabled(True)
                    self.actGrp2.setEnabled(True)
                    self.propsAct.setEnabled(True)
                    self.userPropsAct.setEnabled(True)
                    self.filetypesAct.setEnabled(True)
                    self.lexersAct.setEnabled(True)
                    self.sessActGrp.setEnabled(True)
                    self.dbgActGrp.setEnabled(True)
                    self.menuDebuggerAct.setEnabled(True)
                    self.menuSessionAct.setEnabled(True)
                    self.menuCheckAct.setEnabled(True)
                    self.menuShowAct.setEnabled(True)
                    self.menuDiagramAct.setEnabled(True)
                    self.menuApidocAct.setEnabled(True)
                    self.menuPackagersAct.setEnabled(True)
                    self.pluginGrp.setEnabled(self.pdata["PROJECTTYPE"][0] == "E4Plugin")
                    
                    self.__model.projectOpened()
                    self.emit(SIGNAL('projectOpenedHooks'))
                    self.emit(SIGNAL('projectOpened'))
                    
                    QApplication.restoreOverrideCursor()
                    
                    if Preferences.getProject("SearchNewFiles"):
                        self.__doSearchNewFiles()
                    
                    # read a project tasks file
                    self.__readTasks()
                    self.ui.taskViewer.setProjectOpen(True)
                    
                    if restoreSession:
                        # open the main script
                        if len(self.pdata["MAINSCRIPT"]) == 1:
                            self.emit(SIGNAL('sourceFile'), 
                                os.path.join(self.ppath, self.pdata["MAINSCRIPT"][0]))
                        
                        # open a project session file being quiet about errors
                        if reopen:
                            self.__readSession(quiet = True, indicator = "_tmp")
                        elif Preferences.getProject("AutoLoadSession"):
                            self.__readSession(quiet = True)
                    
                    # open a project debugger properties file being quiet about errors
                    if Preferences.getProject("AutoLoadDbgProperties"):
                        self.__readDebugProperties(True)
                    
                    # start the VCS monitor thread
                    if self.vcs is not None:
                        self.vcs.startStatusMonitor(self)
                        self.connect(self.vcs, 
                             SIGNAL("vcsStatusMonitorData(QStringList)"),
                             self.__model.changeVCSStates)
                        self.connect(self.vcs, 
                             SIGNAL("vcsStatusMonitorStatus(QString, QString)"),
                             self.__statusMonitorStatus)
                else:
                    QApplication.restoreOverrideCursor()
        
    def reopenProject(self):
        """
        Public slot to reopen the current project.
        """
        projectFile = self.pfile
        res = self.closeProject(reopen = True)
        if res:
            self.openProject(projectFile, reopen = True)
        
    def saveProject(self):
        """
        Public slot to save the current project.
        
        @return flag indicating success
        """
        if self.isDirty():
            if len(self.pfile) > 0:
                if self.pfile.endswith("e3pz") or self.pfile.endswith("e3p"):
                    ok = self.saveProjectAs()
                else:
                    ok = self.__writeProject()
            else:
                ok = self.saveProjectAs()
        else:
            ok = True
        self.sessActGrp.setEnabled(ok)
        self.menuSessionAct.setEnabled(ok)
        return ok
        
    def saveProjectAs(self):
        """
        Public slot to save the current project to a different file.
        
        @return flag indicating success
        """
        if Preferences.getProject("CompressedProjectFiles"):
            selectedFilter = self.trUtf8("Compressed Project Files (*.e4pz)")
        else:
            selectedFilter = self.trUtf8("Project Files (*.e4p)")
        fn = KQFileDialog.getSaveFileName(\
            self.parent(),
            self.trUtf8("Save project as"),
            self.ppath,
            self.trUtf8("Project Files (*.e4p);;"
                "Compressed Project Files (*.e4pz)"),
            selectedFilter,
            QFileDialog.Options(QFileDialog.DontConfirmOverwrite))
        
        if not fn.isEmpty():
            ext = QFileInfo(fn).suffix()
            if ext.isEmpty():
                ex = selectedFilter.section('(*', 1, 1).section(')', 0, 0)
                if not ex.isEmpty():
                    fn.append(ex)
            if QFileInfo(fn).exists():
                res = KQMessageBox.warning(None,
                    self.trUtf8("Save File"),
                    self.trUtf8("""<p>The file <b>%1</b> already exists.</p>""")
                        .arg(fn),
                    QMessageBox.StandardButtons(\
                        QMessageBox.Abort | \
                        QMessageBox.Save),
                    QMessageBox.Abort)
                if res != QMessageBox.Save:
                    return False
                
            self.name = unicode(QFileInfo(fn).baseName())
            ok = self.__writeProject(unicode(fn))
            
            if ok:
                # now save the tasks
                self.__writeTasks()
            
            self.sessActGrp.setEnabled(ok)
            self.menuSessionAct.setEnabled(ok)
            self.emit(SIGNAL('projectClosedHooks'))
            self.emit(SIGNAL('projectClosed'))
            self.emit(SIGNAL('projectOpenedHooks'))
            self.emit(SIGNAL('projectOpened'))
            return True
        else:
            return False
    
    def checkDirty(self):
        """
        Public method to check dirty status and open a message window.
        
        @return flag indicating whether this operation was successful
        """
        if self.isDirty():
            res = KQMessageBox.warning(self.parent(), 
                self.trUtf8("Close Project"),
                self.trUtf8("The current project has unsaved changes."),
                QMessageBox.StandardButtons(\
                    QMessageBox.Abort | \
                    QMessageBox.Discard | \
                    QMessageBox.Save),
                QMessageBox.Save)
            if res == QMessageBox.Save:
                return self.saveProject()
            elif res == QMessageBox.Discard:
                self.setDirty(False)
                return True
            elif res == QMessageBox.Abort:
                return False
            
        return True
        
    def __closeAllWindows(self):
        """
        Private method to close all project related windows.
        """
        self.codemetrics        and self.codemetrics.close()
        self.codecoverage       and self.codecoverage.close()
        self.profiledata        and self.profiledata.close()
        self.applicationDiagram and self.applicationDiagram.close()
        
    def closeProject(self, reopen = False):
        """
        Public slot to close the current project.
        
        @keyparam reopen flag indicating a reopening of the project (boolean)
        @return flag indicating success (boolean)
        """
        # save the list of recently opened projects
        self.__saveRecent()
        
        if not self.isOpen():
            return True
        
        if not self.checkDirty():
            return False
        
        # save the user project properties
        self.__writeUserProperties()
        
        # save the project session file being quiet about error
        if reopen:
            self.__writeSession(quiet = True, indicator = "_tmp")
        elif Preferences.getProject("AutoSaveSession"):
            self.__writeSession(quiet = True)
        
        # save the project debugger properties file being quiet about error
        if Preferences.getProject("AutoSaveDbgProperties") and \
           self.isDebugPropertiesLoaded():
            self.__writeDebugProperties(True)
        
        # now save all open modified files of the project
        vm = e4App().getObject("ViewManager")
        success = True
        for fn in vm.getOpenFilenames():
            if self.isProjectFile(fn):
                success &= vm.closeWindow(fn)
        
        if not success:
            return False
        
        # stop the VCS monitor thread
        if self.vcs is not None:
            self.vcs.stopStatusMonitor()
            self.disconnect(self.vcs, 
                SIGNAL("vcsStatusMonitorData(QStringList)"),
                self.__model.changeVCSStates)
            self.disconnect(self.vcs, 
                SIGNAL("vcsStatusMonitorStatus(QString, QString)"),
                self.__statusMonitorStatus)
        
        # now save the tasks
        self.__writeTasks()
        self.ui.taskViewer.clearProjectTasks()
        self.ui.taskViewer.setProjectOpen(False)
        
        # now shutdown the vcs interface
        if self.vcs:
            self.vcs.vcsShutdown()
            self.vcs = None
            e4App().getObject("PluginManager").deactivateVcsPlugins()
        
        # now close all project related windows
        self.__closeAllWindows()
        
        self.__initData()
        self.closeAct.setEnabled(False)
        self.saveasAct.setEnabled(False)
        self.saveAct.setEnabled(False)
        self.actGrp2.setEnabled(False)
        self.propsAct.setEnabled(False)
        self.userPropsAct.setEnabled(False)
        self.filetypesAct.setEnabled(False)
        self.lexersAct.setEnabled(False)
        self.sessActGrp.setEnabled(False)
        self.dbgActGrp.setEnabled(False)
        self.menuDebuggerAct.setEnabled(False)
        self.menuSessionAct.setEnabled(False)
        self.menuCheckAct.setEnabled(False)
        self.menuShowAct.setEnabled(False)
        self.menuDiagramAct.setEnabled(False)
        self.menuApidocAct.setEnabled(False)
        self.menuPackagersAct.setEnabled(False)
        self.pluginGrp.setEnabled(False)
        
        self.__model.projectClosed()
        self.emit(SIGNAL('projectClosedHooks'))
        self.emit(SIGNAL('projectClosed'))
        
        return True

    def saveAllScripts(self, reportSyntaxErrors = False):
        """
        Public method to save all scripts belonging to the project.
        
        @keyparam reportSyntaxErrors flag indicating special reporting
            for syntax errors (boolean)
        @return flag indicating success
        """
        vm = e4App().getObject("ViewManager")
        success = True
        filesWithSyntaxErrors = 0
        for fn in vm.getOpenFilenames():
            rfn = fn.replace(self.ppath+os.sep, '') # make relativ to project
            if rfn in self.pdata["SOURCES"] or rfn in self.pdata["OTHERS"]:
                editor = vm.getOpenEditor(fn)
                success &= vm.saveEditorEd(editor)
                if reportSyntaxErrors and editor.hasSyntaxErrors():
                    filesWithSyntaxErrors += 1
        
        if reportSyntaxErrors and filesWithSyntaxErrors > 0:
            KQMessageBox.critical(None,
                self.trUtf8("Syntax errors detected"),
                self.trUtf8("""The project contains %n file(s) with syntax errors.""",
                    "", filesWithSyntaxErrors)
            )
            return False
        else:
            return success
        
    def getMainScript(self, normalized = False):
        """
        Public method to return the main script filename.
        
        @param normalized flag indicating a normalized filename is wanted (boolean)
        @return filename of the projects main script (string)
        """
        if len(self.pdata["MAINSCRIPT"]):
            if normalized:
                return os.path.join(self.ppath, self.pdata["MAINSCRIPT"][0])
            else:
                return self.pdata["MAINSCRIPT"]
        else:
            return None
        
    def getSources(self, normalized = False):
        """
        Public method to return the source script files.
        
        @param normalized flag indicating a normalized filename is wanted (boolean)
        @return list of the projects scripts (list of string)
        """
        if normalized:
            return [os.path.join(self.ppath, fn) for fn in self.pdata["SOURCES"]]
        else:
            return self.pdata["SOURCES"]
        
    def getProjectType(self):
        """
        Public method to get the type of the project.
        
        @return UI type of the project (string)
        """
        return self.pdata["PROJECTTYPE"][0]
        
    def getProjectLanguage(self):
        """
        Public method to get the project's programming language.
        
        @return programming language (string)
        """
        return self.pdata["PROGLANGUAGE"][0]
        
    def getProjectSpellLanguage(self):
        """
        Public method to get the project's programming language.
        
        @return programming language (string)
        """
        return self.pdata["SPELLLANGUAGE"][0]
        
    def getProjectDictionaries(self):
        """
        Public method to get the names of the project specific dictionaries.
        
        @return tuple of two strings giving the absolute path names of the
            project specific word and exclude list
        """
        pwl = ""
        if len(self.pdata["SPELLWORDS"][0]) > 0:
            pwl = os.path.join(self.ppath, self.pdata["SPELLWORDS"][0])
        
        pel = ""
        if len(self.pdata["SPELLEXCLUDES"][0]) > 0:
            pel = os.path.join(self.ppath, self.pdata["SPELLEXCLUDES"][0])
        
        return (pwl, pel)
        
    def getDefaultSourceExtension(self):
        """
        Public method to get the default extension for the project's
        programming language.
        
        @return default extension (including the dot) (string)
        """
        if self.pdata["PROGLANGUAGE"]:
            return self.sourceExtensions[self.pdata["PROGLANGUAGE"][0]][0]
        else:
            return ""
        
    def getProjectPath(self):
        """
        Public method to get the project path.
        
        @return project path (string)
        """
        return self.ppath
        
    def getProjectFile(self):
        """
        Public method to get the path of the project file.
        
        @return path of the project file (string)
        """
        return self.pfile
        
    def getProjectManagementDir(self):
        """
        Public method to get the path of the management directory.
        
        @return path of the management directory (string)
        """
        if Utilities.isWindowsPlatform():
            return os.path.join(self.ppath, "_eric4project")
        else:
            return os.path.join(self.ppath, ".eric4project")
        
    def isProjectFile(self, fn):
        """
        Public method used to check, if the passed in filename belongs to the project.
        
        @param fn filename to be checked (string or QString)
        @return flag indicating membership (boolean)
        """
        newfn = os.path.abspath(unicode(fn))
        newfn = newfn.replace(self.ppath + os.sep, '')
        if newfn in self.pdata["SOURCES"] or \
           newfn in self.pdata["FORMS"] or \
           newfn in self.pdata["INTERFACES"] or \
           newfn in self.pdata["RESOURCES"] or \
           newfn in self.pdata["TRANSLATIONS"] or \
           newfn in self.pdata["OTHERS"]:
            return True
        else:
            for entry in self.pdata["OTHERS"]:
                if newfn.startswith(entry):
                    return True
        return False
        
    def isProjectSource(self, fn):
        """
        Public method used to check, if the passed in filename belongs to the project
        sources.
        
        @param fn filename to be checked (string or QString)
        @return flag indicating membership (boolean)
        """
        newfn = os.path.abspath(unicode(fn))
        newfn = newfn.replace(self.ppath + os.sep, '')
        return newfn in self.pdata["SOURCES"]
        
    def isProjectForm(self, fn):
        """
        Public method used to check, if the passed in filename belongs to the project
        forms.
        
        @param fn filename to be checked (string or QString)
        @return flag indicating membership (boolean)
        """
        newfn = os.path.abspath(unicode(fn))
        newfn = newfn.replace(self.ppath + os.sep, '')
        return newfn in self.pdata["FORMS"]
        
    def isProjectInterface(self, fn):
        """
        Public method used to check, if the passed in filename belongs to the project
        interfaces.
        
        @param fn filename to be checked (string or QString)
        @return flag indicating membership (boolean)
        """
        newfn = os.path.abspath(unicode(fn))
        newfn = newfn.replace(self.ppath + os.sep, '')
        return newfn in self.pdata["INTERFACES"]
        
    def isProjectResource(self, fn):
        """
        Public method used to check, if the passed in filename belongs to the project
        resources.
        
        @param fn filename to be checked (string or QString)
        @return flag indicating membership (boolean)
        """
        newfn = os.path.abspath(unicode(fn))
        newfn = newfn.replace(self.ppath + os.sep, '')
        return newfn in self.pdata["RESOURCES"]
        
    def initActions(self):
        """
        Public slot to initialize the project related actions.
        """
        self.actions = []
        
        self.actGrp1 = createActionGroup(self)
        
        act = E4Action(self.trUtf8('New project'),
                UI.PixmapCache.getIcon("projectNew.png"),
                self.trUtf8('&New...'), 0, 0,
                self.actGrp1,'project_new')
        act.setStatusTip(self.trUtf8('Generate a new project'))
        act.setWhatsThis(self.trUtf8(
            """<b>New...</b>"""
            """<p>This opens a dialog for entering the info for a"""
            """ new project.</p>"""
        ))
        self.connect(act, SIGNAL('triggered()'), self.newProject)
        self.actions.append(act)

        act = E4Action(self.trUtf8('Open project'),
                UI.PixmapCache.getIcon("projectOpen.png"),
                self.trUtf8('&Open...'), 0, 0,
                self.actGrp1,'project_open')
        act.setStatusTip(self.trUtf8('Open an existing project'))
        act.setWhatsThis(self.trUtf8(
            """<b>Open...</b>"""
            """<p>This opens an existing project.</p>"""
        ))
        self.connect(act, SIGNAL('triggered()'), self.openProject)
        self.actions.append(act)

        self.closeAct = E4Action(self.trUtf8('Close project'),
                UI.PixmapCache.getIcon("projectClose.png"),
                self.trUtf8('&Close'), 0, 0, self, 'project_close')
        self.closeAct.setStatusTip(self.trUtf8('Close the current project'))
        self.closeAct.setWhatsThis(self.trUtf8(
            """<b>Close</b>"""
            """<p>This closes the current project.</p>"""
        ))
        self.connect(self.closeAct, SIGNAL('triggered()'), self.closeProject)
        self.actions.append(self.closeAct)

        self.saveAct = E4Action(self.trUtf8('Save project'),
                UI.PixmapCache.getIcon("projectSave.png"),
                self.trUtf8('&Save'), 0, 0, self, 'project_save')
        self.saveAct.setStatusTip(self.trUtf8('Save the current project'))
        self.saveAct.setWhatsThis(self.trUtf8(
            """<b>Save</b>"""
            """<p>This saves the current project.</p>"""
        ))
        self.connect(self.saveAct, SIGNAL('triggered()'), self.saveProject)
        self.actions.append(self.saveAct)

        self.saveasAct = E4Action(self.trUtf8('Save project as'),
                UI.PixmapCache.getIcon("projectSaveAs.png"),
                self.trUtf8('Save &as...'), 0, 0, self, 'project_save_as')
        self.saveasAct.setStatusTip(self.trUtf8('Save the current project to a new file'))
        self.saveasAct.setWhatsThis(self.trUtf8(
            """<b>Save as</b>"""
            """<p>This saves the current project to a new file.</p>"""
        ))
        self.connect(self.saveasAct, SIGNAL('triggered()'), self.saveProjectAs)
        self.actions.append(self.saveasAct)

        self.actGrp2 = createActionGroup(self)
        
        self.addFilesAct = E4Action(self.trUtf8('Add files to project'),
                UI.PixmapCache.getIcon("fileMisc.png"),
                self.trUtf8('Add &files...'), 0, 0,
                self.actGrp2,'project_add_file')
        self.addFilesAct.setStatusTip(self.trUtf8('Add files to the current project'))
        self.addFilesAct.setWhatsThis(self.trUtf8(
            """<b>Add files...</b>"""
            """<p>This opens a dialog for adding files"""
            """ to the current project. The place to add is"""
            """ determined by the file extension.</p>"""
        ))
        self.connect(self.addFilesAct, SIGNAL('triggered()'), self.addFiles)
        self.actions.append(self.addFilesAct)

        self.addDirectoryAct = E4Action(self.trUtf8('Add directory to project'),
                UI.PixmapCache.getIcon("dirOpen.png"),
                self.trUtf8('Add directory...'), 0, 0,
                self.actGrp2,'project_add_directory')
        self.addDirectoryAct.setStatusTip(
            self.trUtf8('Add a directory to the current project'))
        self.addDirectoryAct.setWhatsThis(self.trUtf8(
            """<b>Add directory...</b>"""
            """<p>This opens a dialog for adding a directory"""
            """ to the current project.</p>"""
        ))
        self.connect(self.addDirectoryAct, SIGNAL('triggered()'), self.addDirectory)
        self.actions.append(self.addDirectoryAct)

        self.addLanguageAct = E4Action(self.trUtf8('Add translation to project'),
                UI.PixmapCache.getIcon("linguist4.png"),
                self.trUtf8('Add &translation...'), 0, 0,
                self.actGrp2,'project_add_translation')
        self.addLanguageAct.setStatusTip(
            self.trUtf8('Add a translation to the current project'))
        self.addLanguageAct.setWhatsThis(self.trUtf8(
            """<b>Add translation...</b>"""
            """<p>This opens a dialog for add a translation"""
            """ to the current project.</p>"""
        ))
        self.connect(self.addLanguageAct, SIGNAL('triggered()'), self.addLanguage)
        self.actions.append(self.addLanguageAct)

        act = E4Action(self.trUtf8('Search new files'),
                self.trUtf8('Searc&h new files...'), 0, 0,
                self.actGrp2,'project_search_new_files')
        act.setStatusTip(self.trUtf8('Search new files in the project directory.'))
        act.setWhatsThis(self.trUtf8(
            """<b>Search new files...</b>"""
            """<p>This searches for new files (sources, *.ui, *.idl) in the project"""
            """ directory and registered subdirectories.</p>"""
        ))
        self.connect(act, SIGNAL('triggered()'), self.__searchNewFiles)
        self.actions.append(act)

        self.propsAct = E4Action(self.trUtf8('Project properties'),
                UI.PixmapCache.getIcon("projectProps.png"),
                self.trUtf8('&Properties...'), 0, 0, self, 'project_properties')
        self.propsAct.setStatusTip(self.trUtf8('Show the project properties'))
        self.propsAct.setWhatsThis(self.trUtf8(
            """<b>Properties...</b>"""
            """<p>This shows a dialog to edit the project properties.</p>"""
        ))
        self.connect(self.propsAct, SIGNAL('triggered()'), self.__showProperties)
        self.actions.append(self.propsAct)

        self.userPropsAct = E4Action(self.trUtf8('User project properties'),
                UI.PixmapCache.getIcon("projectUserProps.png"),
                self.trUtf8('&User Properties...'), 0, 0, self, 'project_user_properties')
        self.userPropsAct.setStatusTip(self.trUtf8(
            'Show the user specific project properties'))
        self.userPropsAct.setWhatsThis(self.trUtf8(
            """<b>User Properties...</b>"""
            """<p>This shows a dialog to edit the user specific project properties.</p>"""
        ))
        self.connect(self.userPropsAct, SIGNAL('triggered()'), self.__showUserProperties)
        self.actions.append(self.userPropsAct)

        self.filetypesAct = E4Action(self.trUtf8('Filetype Associations'),
                self.trUtf8('Filetype Associations...'), 0, 0,
                self, 'project_filetype_associatios')
        self.filetypesAct.setStatusTip(\
            self.trUtf8('Show the project filetype associations'))
        self.filetypesAct.setWhatsThis(self.trUtf8(
            """<b>Filetype Associations...</b>"""
            """<p>This shows a dialog to edit the filetype associations of the project."""
            """ These associations determine the type (source, form, interface"""
            """ or others) with a filename pattern. They are used when adding a file"""
            """ to the project and when performing a search for new files.</p>"""
        ))
        self.connect(self.filetypesAct, SIGNAL('triggered()'), 
            self.__showFiletypeAssociations)
        self.actions.append(self.filetypesAct)

        self.lexersAct = E4Action(self.trUtf8('Lexer Associations'),
                self.trUtf8('Lexer Associations...'), 0, 0,
                self, 'project_lexer_associatios')
        self.lexersAct.setStatusTip(\
            self.trUtf8('Show the project lexer associations (overriding defaults)'))
        self.lexersAct.setWhatsThis(self.trUtf8(
            """<b>Lexer Associations...</b>"""
            """<p>This shows a dialog to edit the lexer associations of the project."""
            """ These associations override the global lexer associations. Lexers"""
            """ are used to highlight the editor text.</p>"""
        ))
        self.connect(self.lexersAct, SIGNAL('triggered()'), 
            self.__showLexerAssociations)
        self.actions.append(self.lexersAct)

        self.dbgActGrp = createActionGroup(self)
        
        act = E4Action(self.trUtf8('Debugger Properties'),
                self.trUtf8('Debugger &Properties...'), 0, 0,
                self.dbgActGrp, 'project_debugger_properties')
        act.setStatusTip(self.trUtf8('Show the debugger properties'))
        act.setWhatsThis(self.trUtf8(
            """<b>Debugger Properties...</b>"""
            """<p>This shows a dialog to edit project specific debugger settings.</p>"""
        ))
        self.connect(act, SIGNAL('triggered()'), self.__showDebugProperties)
        self.actions.append(act)
        
        act = E4Action(self.trUtf8('Load'),
                self.trUtf8('&Load'), 0, 0,
                self.dbgActGrp, 'project_debugger_properties_load')
        act.setStatusTip(self.trUtf8('Load the debugger properties'))
        act.setWhatsThis(self.trUtf8(
            """<b>Load Debugger Properties</b>"""
            """<p>This loads the project specific debugger settings.</p>"""
        ))
        self.connect(act, SIGNAL('triggered()'), self.__readDebugProperties)
        self.actions.append(act)
        
        act = E4Action(self.trUtf8('Save'),
                self.trUtf8('&Save'), 0, 0,
                self.dbgActGrp, 'project_debugger_properties_save')
        act.setStatusTip(self.trUtf8('Save the debugger properties'))
        act.setWhatsThis(self.trUtf8(
            """<b>Save Debugger Properties</b>"""
            """<p>This saves the project specific debugger settings.</p>"""
        ))
        self.connect(act, SIGNAL('triggered()'), self.__writeDebugProperties)
        self.actions.append(act)
        
        act = E4Action(self.trUtf8('Delete'),
                self.trUtf8('&Delete'), 0, 0,
                self.dbgActGrp, 'project_debugger_properties_delete')
        act.setStatusTip(self.trUtf8('Delete the debugger properties'))
        act.setWhatsThis(self.trUtf8(
            """<b>Delete Debugger Properties</b>"""
            """<p>This deletes the file containing the project specific"""
            """ debugger settings.</p>"""
        ))
        self.connect(act, SIGNAL('triggered()'), self.__deleteDebugProperties)
        self.actions.append(act)
        
        act = E4Action(self.trUtf8('Reset'),
                self.trUtf8('&Reset'), 0, 0,
                self.dbgActGrp, 'project_debugger_properties_resets')
        act.setStatusTip(self.trUtf8('Reset the debugger properties'))
        act.setWhatsThis(self.trUtf8(
            """<b>Reset Debugger Properties</b>"""
            """<p>This resets the project specific debugger settings.</p>"""
        ))
        self.connect(act, SIGNAL('triggered()'), self.__initDebugProperties)
        self.actions.append(act)
        
        self.sessActGrp = createActionGroup(self)

        act = E4Action(self.trUtf8('Load session'),
                self.trUtf8('Load session'), 0, 0,
                self.sessActGrp, 'project_load_session')
        act.setStatusTip(self.trUtf8('Load the projects session file.'))
        act.setWhatsThis(self.trUtf8(
            """<b>Load session</b>"""
            """<p>This loads the projects session file. The session consists"""
            """ of the following data.<br>"""
            """- all open source files<br>"""
            """- all breakpoint<br>"""
            """- the commandline arguments<br>"""
            """- the working directory<br>"""
            """- the exception reporting flag</p>"""
        ))
        self.connect(act, SIGNAL('triggered()'), self.__readSession)
        self.actions.append(act)

        act = E4Action(self.trUtf8('Save session'),
                self.trUtf8('Save session'), 0, 0,
                self.sessActGrp, 'project_save_session')
        act.setStatusTip(self.trUtf8('Save the projects session file.'))
        act.setWhatsThis(self.trUtf8(
            """<b>Save session</b>"""
            """<p>This saves the projects session file. The session consists"""
            """ of the following data.<br>"""
            """- all open source files<br>"""
            """- all breakpoint<br>"""
            """- the commandline arguments<br>"""
            """- the working directory<br>"""
            """- the exception reporting flag</p>"""
        ))
        self.connect(act, SIGNAL('triggered()'), self.__writeSession)
        self.actions.append(act)
        
        act = E4Action(self.trUtf8('Delete session'),
                self.trUtf8('Delete session'), 0, 0,
                self.sessActGrp, 'project_delete_session')
        act.setStatusTip(self.trUtf8('Delete the projects session file.'))
        act.setWhatsThis(self.trUtf8(
            """<b>Delete session</b>"""
            """<p>This deletes the projects session file</p>"""
        ))
        self.connect(act, SIGNAL('triggered()'), self.__deleteSession)
        self.actions.append(act)
        
        self.chkGrp = createActionGroup(self)

        self.codeMetricsAct = E4Action(self.trUtf8('Code Metrics'),
                self.trUtf8('&Code Metrics...'), 0, 0,
                self.chkGrp,'project_code_metrics')
        self.codeMetricsAct.setStatusTip(\
            self.trUtf8('Show some code metrics for the project.'))
        self.codeMetricsAct.setWhatsThis(self.trUtf8(
            """<b>Code Metrics...</b>"""
            """<p>This shows some code metrics for all Python files in the project.</p>"""
        ))
        self.connect(self.codeMetricsAct, SIGNAL('triggered()'), self.__showCodeMetrics)
        self.actions.append(self.codeMetricsAct)

        self.codeCoverageAct = E4Action(self.trUtf8('Python Code Coverage'),
                self.trUtf8('Code Co&verage...'), 0, 0,
                self.chkGrp,'project_code_coverage')
        self.codeCoverageAct.setStatusTip(\
            self.trUtf8('Show code coverage information for the project.'))
        self.codeCoverageAct.setWhatsThis(self.trUtf8(
            """<b>Code Coverage...</b>"""
            """<p>This shows the code coverage information for all Python files"""
            """ in the project.</p>"""
        ))
        self.connect(self.codeCoverageAct, SIGNAL('triggered()'), self.__showCodeCoverage)
        self.actions.append(self.codeCoverageAct)

        self.codeProfileAct = E4Action(self.trUtf8('Profile Data'),
                self.trUtf8('&Profile Data...'), 0, 0,
                self.chkGrp,'project_profile_data')
        self.codeProfileAct.setStatusTip(\
            self.trUtf8('Show profiling data for the project.'))
        self.codeProfileAct.setWhatsThis(self.trUtf8(
            """<b>Profile Data...</b>"""
            """<p>This shows the profiling data for the project.</p>"""
        ))
        self.connect(self.codeProfileAct, SIGNAL('triggered()'), self.__showProfileData)
        self.actions.append(self.codeProfileAct)

        self.applicationDiagramAct = E4Action(self.trUtf8('Application Diagram'),
                self.trUtf8('&Application Diagram...'), 0, 0,
                self.chkGrp,'project_application_diagram')
        self.applicationDiagramAct.setStatusTip(\
            self.trUtf8('Show a diagram of the project.'))
        self.applicationDiagramAct.setWhatsThis(self.trUtf8(
            """<b>Application Diagram...</b>"""
            """<p>This shows a diagram of the project.</p>"""
        ))
        self.connect(self.applicationDiagramAct, 
            SIGNAL('triggered()'), self.handleApplicationDiagram)
        self.actions.append(self.applicationDiagramAct)

        self.pluginGrp = createActionGroup(self)

        self.pluginPkgListAct = E4Action(self.trUtf8('Create Package List'),
                UI.PixmapCache.getIcon("pluginArchiveList.png"),
                self.trUtf8('Create &Package List'), 0, 0,
                self.pluginGrp,'project_plugin_pkglist')
        self.pluginPkgListAct.setStatusTip(\
            self.trUtf8('Create an initial PKGLIST file for an eric4 plugin.'))
        self.pluginPkgListAct.setWhatsThis(self.trUtf8(
            """<b>Create Package List</b>"""
            """<p>This creates an initial list of files to include in an eric4 """
            """plugin archive. The list is created from the project file.</p>"""
        ))
        self.connect(self.pluginPkgListAct, SIGNAL('triggered()'), 
            self.__pluginCreatePkgList)
        self.actions.append(self.pluginPkgListAct)

        self.pluginArchiveAct = E4Action(self.trUtf8('Create Plugin Archive'),
                UI.PixmapCache.getIcon("pluginArchive.png"),
                self.trUtf8('Create Plugin &Archive'), 0, 0,
                self.pluginGrp,'project_plugin_archive')
        self.pluginArchiveAct.setStatusTip(\
            self.trUtf8('Create an eric4 plugin archive file.'))
        self.pluginArchiveAct.setWhatsThis(self.trUtf8(
            """<b>Create Plugin Archive</b>"""
            """<p>This creates an eric4 plugin archive file using the list of files """
            """given in the PKGLIST file. The archive name is built from the main """
            """script name.</p>"""
        ))
        self.connect(self.pluginArchiveAct, SIGNAL('triggered()'), 
            self.__pluginCreateArchive)
        self.actions.append(self.pluginArchiveAct)
    
        self.pluginSArchiveAct = E4Action(self.trUtf8('Create Plugin Archive (Snapshot)'),
                UI.PixmapCache.getIcon("pluginArchiveSnapshot.png"),
                self.trUtf8('Create Plugin Archive (&Snapshot)'), 0, 0,
                self.pluginGrp,'project_plugin_sarchive')
        self.pluginSArchiveAct.setStatusTip(\
            self.trUtf8('Create an eric4 plugin archive file (snapshot release).'))
        self.pluginSArchiveAct.setWhatsThis(self.trUtf8(
            """<b>Create Plugin Archive (Snapshot)</b>"""
            """<p>This creates an eric4 plugin archive file using the list of files """
            """given in the PKGLIST file. The archive name is built from the main """
            """script name. The version entry of the main script is modified to """
            """reflect a snapshot release.</p>"""
        ))
        self.connect(self.pluginSArchiveAct, SIGNAL('triggered()'), 
            self.__pluginCreateSnapshotArchive)
        self.actions.append(self.pluginSArchiveAct)

        self.closeAct.setEnabled(False)
        self.saveAct.setEnabled(False)
        self.saveasAct.setEnabled(False)
        self.actGrp2.setEnabled(False)
        self.propsAct.setEnabled(False)
        self.userPropsAct.setEnabled(False)
        self.filetypesAct.setEnabled(False)
        self.lexersAct.setEnabled(False)
        self.sessActGrp.setEnabled(False)
        self.dbgActGrp.setEnabled(False)
        self.pluginGrp.setEnabled(False)
        
    def initMenu(self):
        """
        Public slot to initialize the project menu.
        
        @return the menu generated (QMenu)
        """
        menu = QMenu(self.trUtf8('&Project'), self.parent())
        self.recentMenu = QMenu(self.trUtf8('Open &Recent Projects'), menu)
        self.vcsMenu = QMenu(self.trUtf8('&Version Control'), menu)
        self.vcsMenu.setTearOffEnabled(True)
        self.vcsProjectHelper.initMenu(self.vcsMenu)
        self.checksMenu = QMenu(self.trUtf8('Chec&k'), menu)
        self.checksMenu.setTearOffEnabled(True)
        self.showMenu = QMenu(self.trUtf8('Sho&w'), menu)
        self.graphicsMenu = QMenu(self.trUtf8('&Diagrams'), menu)
        self.sessionMenu = QMenu(self.trUtf8('Session'), menu)
        self.apidocMenu = QMenu(self.trUtf8('Source &Documentation'), menu)
        self.apidocMenu.setTearOffEnabled(True)
        self.debuggerMenu = QMenu(self.trUtf8('Debugger'), menu)
        self.packagersMenu = QMenu(self.trUtf8('Pac&kagers'), menu)
        self.packagersMenu.setTearOffEnabled(True)
        
        self.__menus = {
            "Main"      : menu, 
            "Recent"    : self.recentMenu, 
            "VCS"       : self.vcsMenu, 
            "Checks"    : self.checksMenu, 
            "Show"      : self.showMenu, 
            "Graphics"  : self.graphicsMenu, 
            "Session"   : self.sessionMenu, 
            "Apidoc"    : self.apidocMenu, 
            "Debugger"  : self.debuggerMenu, 
            "Packagers" : self.packagersMenu, 
        }
        
        # connect the aboutToShow signals
        self.connect(self.recentMenu, SIGNAL('aboutToShow()'), 
            self.__showContextMenuRecent)
        self.connect(self.recentMenu, SIGNAL('triggered(QAction *)'),
                     self.__openRecent)
        self.connect(self.vcsMenu, SIGNAL('aboutToShow()'), self.__showContextMenuVCS)
        self.connect(self.checksMenu, SIGNAL('aboutToShow()'), 
            self.__showContextMenuChecks)
        self.connect(self.showMenu, SIGNAL('aboutToShow()'), self.__showContextMenuShow)
        self.connect(self.graphicsMenu, SIGNAL('aboutToShow()'), 
            self.__showContextMenuGraphics)
        self.connect(self.apidocMenu, SIGNAL('aboutToShow()'), 
            self.__showContextMenuApiDoc)
        self.connect(self.packagersMenu, SIGNAL('aboutToShow()'), 
            self.__showContextMenuPackagers)
        self.connect(menu, SIGNAL('aboutToShow()'), self.__showMenu)
        
        # build the show menu
        self.showMenu.setTearOffEnabled(True)
        self.showMenu.addAction(self.codeMetricsAct)
        self.showMenu.addAction(self.codeCoverageAct)
        self.showMenu.addAction(self.codeProfileAct)
        
        # build the diagrams menu
        self.graphicsMenu.setTearOffEnabled(True)
        self.graphicsMenu.addAction(self.applicationDiagramAct)
        
        # build the session menu
        self.sessionMenu.setTearOffEnabled(True)
        self.sessionMenu.addActions(self.sessActGrp.actions())
        
        # build the debugger menu
        self.debuggerMenu.setTearOffEnabled(True)
        self.debuggerMenu.addActions(self.dbgActGrp.actions())
        
        # build the packagers menu
        self.packagersMenu.addActions(self.pluginGrp.actions())
        self.packagersMenu.addSeparator()
        
        # build the main menu
        menu.setTearOffEnabled(True)
        menu.addActions(self.actGrp1.actions())
        self.menuRecentAct = menu.addMenu(self.recentMenu)
        menu.addSeparator()
        menu.addAction(self.closeAct)
        menu.addSeparator()
        menu.addAction(self.saveAct)
        menu.addAction(self.saveasAct)
        menu.addSeparator()
        self.menuDebuggerAct = menu.addMenu(self.debuggerMenu)
        self.menuSessionAct = menu.addMenu(self.sessionMenu)
        menu.addSeparator()
        menu.addActions(self.actGrp2.actions())
        menu.addSeparator()
        self.menuDiagramAct = menu.addMenu(self.graphicsMenu)
        menu.addSeparator()
        self.menuCheckAct = menu.addMenu(self.checksMenu)
        menu.addSeparator()
        menu.addMenu(self.vcsMenu)
        menu.addSeparator()
        self.menuShowAct = menu.addMenu(self.showMenu)
        menu.addSeparator()
        self.menuApidocAct = menu.addMenu(self.apidocMenu)
        menu.addSeparator()
        self.menuPackagersAct = menu.addMenu(self.packagersMenu)
        menu.addSeparator()
        menu.addAction(self.propsAct)
        menu.addAction(self.userPropsAct)
        menu.addAction(self.filetypesAct)
        menu.addAction(self.lexersAct)
        
        self.menuCheckAct.setEnabled(False)
        self.menuShowAct.setEnabled(False)
        self.menuDiagramAct.setEnabled(False)
        self.menuSessionAct.setEnabled(False)
        self.menuDebuggerAct.setEnabled(False)
        self.menuApidocAct.setEnabled(False)
        self.menuPackagersAct.setEnabled(False)
        
        self.menu = menu
        return menu
        
    def initToolbar(self, toolbarManager):
        """
        Public slot to initialize the project toolbar.
        
        @param toolbarManager reference to a toolbar manager object (E4ToolBarManager)
        @return the toolbar generated (QToolBar)
        """
        tb = QToolBar(self.trUtf8("Project"), self.parent())
        tb.setIconSize(UI.Config.ToolBarIconSize)
        tb.setObjectName("ProjectToolbar")
        tb.setToolTip(self.trUtf8('Project'))
        
        tb.addActions(self.actGrp1.actions())
        tb.addAction(self.closeAct)
        tb.addSeparator()
        tb.addAction(self.saveAct)
        tb.addAction(self.saveasAct)
        
        toolbarManager.addToolBar(tb, tb.windowTitle())
        toolbarManager.addAction(self.addFilesAct, tb.windowTitle())
        toolbarManager.addAction(self.addDirectoryAct, tb.windowTitle())
        toolbarManager.addAction(self.addLanguageAct, tb.windowTitle())
        toolbarManager.addAction(self.propsAct, tb.windowTitle())
        toolbarManager.addAction(self.userPropsAct, tb.windowTitle())
        
        return tb
        
    def __showMenu(self):
        """
        Private method to set up the project menu.
        """
        self.menuRecentAct.setEnabled(len(self.recent) > 0)
        
        self.emit(SIGNAL("showMenu"), "Main", self.__menus["Main"])
        
    def __syncRecent(self):
        """
        Private method to synchronize the list of recently opened projects
        with the central store.
        """
        self.recent.removeAll(self.pfile)
        self.recent.prepend(self.pfile)
        maxRecent = Preferences.getProject("RecentNumber")
        if len(self.recent) > maxRecent:
            self.recent = self.recent[:maxRecent]
        self.__saveRecent()
        
    def __showContextMenuRecent(self):
        """
        Private method to set up the recent projects menu.
        """
        self.__loadRecent()
        
        self.recentMenu.clear()
        
        idx = 1
        for rp in self.recent:
            if idx < 10:
                formatStr = '&%d. %s'
            else:
                formatStr = '%d. %s'
            act = self.recentMenu.addAction(\
                formatStr % (idx, 
                    Utilities.compactPath(unicode(rp), self.ui.maxMenuFilePathLen)))
            act.setData(QVariant(rp))
            act.setEnabled(QFileInfo(rp).exists())
            idx += 1
        
        self.recentMenu.addSeparator()
        self.recentMenu.addAction(self.trUtf8('&Clear'), self.__clearRecent)
        
    def __openRecent(self, act):
        """
        Private method to open a project from the list of rencently opened projects.
        
        @param act reference to the action that triggered (QAction)
        """
        file = unicode(act.data().toString())
        if file:
            self.openProject(file)
        
    def __clearRecent(self):
        """
        Private method to clear the recent projects menu.
        """
        self.recent.clear()
        
    def __searchNewFiles(self):
        """
        Private slot used to handle the search new files action.
        """
        self.__doSearchNewFiles(False, True)
        
    def __doSearchNewFiles(self, AI = True, onUserDemand = False):
        """
        Private method to search for new files in the project directory.
        
        If new files were found, it shows a dialog listing these files and
        gives the user the opportunity to select the ones he wants to
        include. If 'Automatic Inclusion' is enabled, the new files are
        automatically added to the project.
        
        @param AI flag indicating whether the automatic inclusion should
                be honoured (boolean)
        @param onUserDemand flag indicating whether this method was 
                requested by the user via a menu action (boolean)
        """
        autoInclude = Preferences.getProject("AutoIncludeNewFiles")
        recursiveSearch = Preferences.getProject("SearchNewFilesRecursively")
        newFiles = QStringList()
        
        dirs = self.subdirs[:]
        for dir in dirs:
            curpath = os.path.join(self.ppath, dir)
            try:
                newSources = os.listdir(curpath)
            except OSError:
                newSources = []
            if self.pdata["TRANSLATIONPATTERN"]:
                pattern = self.pdata["TRANSLATIONPATTERN"][0].replace("%language%", "*")
            else:
                pattern = "*.ts"
            binpattern = self.__binaryTranslationFile(pattern)
            for ns in newSources:
                # ignore hidden files and directories
                if ns.startswith('.'):
                    continue
                if Utilities.isWindowsPlatform() and \
                   os.path.isdir(os.path.join(curpath, ns)) and \
                   ns.startswith('_'):
                    # dot net hack
                    continue
                
                # set fn to project relative name
                # then reset ns to fully qualified name for insertion, possibly.
                if dir == "":
                    fn = ns
                else:
                    fn = os.path.join(dir, ns)
                ns = os.path.abspath(os.path.join(curpath, ns))
                
                # do not bother with dirs here...
                if os.path.isdir(ns):
                    if recursiveSearch:
                        d = ns.replace(self.ppath + os.sep, '')
                        if d not in dirs:
                            dirs.append(d)
                    continue
                
                filetype = ""
                bfn = os.path.basename(fn)
                for pattern in reversed(sorted(self.pdata["FILETYPES"].keys())):
                    if fnmatch.fnmatch(bfn, pattern):
                        filetype = self.pdata["FILETYPES"][pattern]
                        break
                
                if (filetype == "SOURCES" and fn not in self.pdata["SOURCES"]) or \
                   (filetype == "FORMS" and fn not in self.pdata["FORMS"]) or \
                   (filetype == "INTERFACES" and fn not in self.pdata["INTERFACES"]) or \
                   (filetype == "RESOURCES" and fn not in self.pdata["RESOURCES"]) or \
                   (filetype == "OTHERS" and fn not in self.pdata["OTHERS"]):
                    if autoInclude and AI:
                        self.appendFile(ns)
                    else:
                        newFiles.append(ns)
                elif filetype == "TRANSLATIONS" and fn not in self.pdata["TRANSLATIONS"]:
                    if fnmatch.fnmatch(ns, pattern) or fnmatch.fnmatch(ns, binpattern):
                        if autoInclude and AI:
                            self.appendFile(ns)
                        else:
                            newFiles.append(ns)
        
        # if autoInclude is set there is no more work left
        if (autoInclude and AI):
            return
        
        # if newfiles is empty, put up message box informing user nothing found
        if newFiles.isEmpty():
            if onUserDemand:
                KQMessageBox.information(None,
                    self.trUtf8("Search New Files"),
                    self.trUtf8("There were no new files found to be added."))
            return
            
        # autoInclude is not set, show a dialog
        dlg = AddFoundFilesDialog(newFiles, self.parent(), None)
        res = dlg.exec_()
        
        # the 'Add All' button was pressed
        if res == 1:
            for file in newFiles:
                file = unicode(file)
                self.appendFile(file)
            
        # the 'Add Selected' button was pressed
        elif res == 2:
            files = dlg.getSelection()
            for file in files:
                file = unicode(file)
                self.appendFile(file)
        
    def othersAdded(self, fn, updateModel = True):
        """
        Public slot to be called, if something was added to the OTHERS project data area.
        
        @param fn filename or directory name added (string or QString)
        @param updateModel flag indicating an update of the model is requested (boolean)
        """
        f = unicode(fn)
        self.emit(SIGNAL('projectOthersAdded'), f)
        updateModel and self.__model.addNewItem("OTHERS", fn)
        
    def getActions(self):
        """
        Public method to get a list of all actions.
        
        @return list of all actions (list of E4Action)
        """
        return self.actions[:]
        
    def addE4Actions(self, actions):
        """
        Public method to add actions to the list of actions.
        
        @param actions list of actions (list of E4Action)
        """
        self.actions.extend(actions)
        
    def removeE4Actions(self, actions):
        """
        Public method to remove actions from the list of actions.
        
        @param actions list of actions (list of E4Action)
        """
        for act in actions:
            try:
                self.actions.remove(act)
            except ValueError:
                pass
        
    def getMenu(self, menuName):
        """
        Public method to get a reference to the main menu or a submenu.
        
        @param menuName name of the menu (string)
        @return reference to the requested menu (QMenu) or None
        """
        try:
            return self.__menus[menuName]
        except KeyError:
            return None
        
    def repopulateItem(self, fullname):
        """
        Public slot to repopulate a named item.
        
        @param fullname full name of the item to repopulate (string or QString)
        """
        if not self.isOpen():
            return
        
        fullname = unicode(fullname)
        name = fullname.replace(self.ppath+os.sep, "")
        self.emit(SIGNAL("prepareRepopulateItem"), name)
        self.__model.repopulateItem(name)
        self.emit(SIGNAL("completeRepopulateItem"), name)
    
    ##############################################################
    ## Below is the VCS interface
    ##############################################################
    
    def initVCS(self, vcsSystem = None, nooverride = False):
        """
        Public method used to instantiate a vcs system.
        
        @param vcsSystem type of VCS to be used
        @param nooverride flag indicating to ignore an override request (boolean)
        @return a reference to the vcs object
        """
        vcs = None
        forProject = True
        override = False
        
        if vcsSystem is None:
            if len(self.pdata["VCS"]):
                if self.pdata["VCS"][0] != 'None':
                    vcsSystem = self.pdata["VCS"][0]
        else:
            vcsSystem = str(vcsSystem)
            forProject = False
        
        if self.pdata["VCS"] and self.pdata["VCS"][0] != 'None':
            if self.pudata["VCSOVERRIDE"] and \
               self.pudata["VCSOVERRIDE"][0] is not None and \
               not nooverride:
                vcsSystem = self.pudata["VCSOVERRIDE"][0]
                override = True
        
        if vcsSystem is not None:
            try:
                vcs = VCS.factory(vcsSystem)
            except ImportError:
                if override:
                    # override failed, revert to original
                    self.pudata["VCSOVERRIDE"] = []
                    return self.initVCS(nooverride = True)
        
        if vcs:
            vcsExists, msg = vcs.vcsExists()
            if not vcsExists:
                if override:
                    # override failed, revert to original
                    QApplication.restoreOverrideCursor()
                    KQMessageBox.critical(None,
                        self.trUtf8("Version Control System"),
                        self.trUtf8("<p>The selected VCS <b>%1</b> could not be found."
                                    "<br/>Reverting override.</p><p>%2</p>")\
                            .arg(vcsSystem).arg(msg))
                    self.pudata["VCSOVERRIDE"] = []
                    return self.initVCS(nooverride = True)
                
                QApplication.restoreOverrideCursor()
                KQMessageBox.critical(None,
                    self.trUtf8("Version Control System"),
                    self.trUtf8("<p>The selected VCS <b>%1</b> could not be found.<br/>"
                                "Disabling version control.</p><p>%2</p>")\
                        .arg(vcsSystem).arg(msg))
                vcs = None
                if forProject:
                    self.pdata["VCS"][0] = 'None'
                    self.setDirty(True)
        
        if vcs and forProject:
            # set the vcs options
            try:
                vcsopt = copy.deepcopy(self.pdata["VCSOPTIONS"][0])
                vcs.vcsSetOptions(vcsopt)
            except LookupError:
                pass
            # set vcs specific data
            try:
                vcsother = copy.deepcopy(self.pdata["VCSOTHERDATA"][0])
                vcs.vcsSetOtherData(vcsother)
            except LookupError:
                pass
        
        if vcs is None:
            self.vcsProjectHelper = VcsProjectHelper(None, self)
            self.vcsBasicHelper = True
        else:
            self.vcsProjectHelper = vcs.vcsGetProjectHelper(self)
            self.vcsBasicHelper = False
        if self.vcsMenu is not None:
            self.vcsProjectHelper.initMenu(self.vcsMenu)
        return vcs
        
    def __showContextMenuVCS(self):
        """
        Private slot called before the vcs menu is shown.
        """
        self.vcsProjectHelper.showMenu()
        if self.vcsBasicHelper:
            self.emit(SIGNAL("showMenu"), "VCS", self.vcsMenu)
    
    #########################################################################
    ## Below is the interface to the checker tools
    #########################################################################
    
    def __showContextMenuChecks(self):
        """
        Private slot called before the checks menu is shown.
        """
        self.emit(SIGNAL("showMenu"), "Checks", self.checksMenu)
    
    #########################################################################
    ## Below is the interface to the packagers tools
    #########################################################################
    
    def __showContextMenuPackagers(self):
        """
        Private slot called before the packagers menu is shown.
        """
        self.emit(SIGNAL("showMenu"), "Packagers", self.packagersMenu)
    
    #########################################################################
    ## Below is the interface to the apidoc tools
    #########################################################################
    
    def __showContextMenuApiDoc(self):
        """
        Private slot called before the apidoc menu is shown.
        """
        self.emit(SIGNAL("showMenu"), "Apidoc", self.apidocMenu)
    
    #########################################################################
    ## Below is the interface to the show tools
    #########################################################################
    
    def __showCodeMetrics(self):
        """
        Private slot used to calculate some code metrics for the project files.
        """
        files = [os.path.join(self.ppath, file) \
            for file in self.pdata["SOURCES"] if file.endswith(".py")]
        self.codemetrics = CodeMetricsDialog()
        self.codemetrics.show()
        self.codemetrics.start(files)

    def __showCodeCoverage(self):
        """
        Private slot used to show the code coverage information for the project files.
        """
        fn = self.getMainScript(True)
        if fn is None:
            KQMessageBox.critical(self.ui,
                self.trUtf8("Coverage Data"),
                self.trUtf8("There is no main script defined for the"
                    " current project. Aborting"))
            return
        
        tfn = Utilities.getTestFileName(fn)
        basename = os.path.splitext(fn)[0]
        tbasename = os.path.splitext(tfn)[0]
        
        # determine name of coverage file to be used
        files = []
        f = "%s.coverage" % basename
        tf = "%s.coverage" % tbasename
        if os.path.isfile(f):
            files.append(f)
        if os.path.isfile(tf):
            files.append(tf)
        
        if files:
            if len(files) > 1:
                filelist = QStringList()
                for f in files:
                    filelist.append(f)
                fn, ok = KQInputDialog.getItem(\
                    None,
                    self.trUtf8("Code Coverage"),
                    self.trUtf8("Please select a coverage file"),
                    filelist,
                    0, False)
                if not ok:
                    return
                fn = unicode(fn)
            else:
                fn = files[0]
        else:
            return
        
        files = [os.path.join(self.ppath, file) \
            for file in self.pdata["SOURCES"] if file.endswith(".py")]
        self.codecoverage = PyCoverageDialog()
        self.codecoverage.show()
        self.codecoverage.start(fn, files)

    def __showProfileData(self):
        """
        Private slot used to show the profiling information for the project.
        """
        fn = self.getMainScript(True)
        if fn is None:
            KQMessageBox.critical(self.ui,
                self.trUtf8("Profile Data"),
                self.trUtf8("There is no main script defined for the"
                    " current project. Aborting"))
            return
        
        tfn = Utilities.getTestFileName(fn)
        basename = os.path.splitext(fn)[0]
        tbasename = os.path.splitext(tfn)[0]
        
        # determine name of profile file to be used
        files = []
        f = "%s.profile" % basename
        tf = "%s.profile" % tbasename
        if os.path.isfile(f):
            files.append(f)
        if os.path.isfile(tf):
            files.append(tf)
        
        if files:
            if len(files) > 1:
                filelist = QStringList()
                for f in files:
                    filelist.append(f)
                fn, ok = KQInputDialog.getItem(\
                    None,
                    self.trUtf8("Profile Data"),
                    self.trUtf8("Please select a profile file"),
                    filelist,
                    0, False)
                if not ok:
                    return
                fn = unicode(fn)
            else:
                fn = files[0]
        else:
            return
        
        self.profiledata = PyProfileDialog()
        self.profiledata.show()
        self.profiledata.start(fn)
        
    def __showContextMenuShow(self):
        """
        Private slot called before the show menu is shown.
        """
        fn = self.getMainScript(True)
        if fn is not None:
            tfn = Utilities.getTestFileName(fn)
            basename = os.path.splitext(fn)[0]
            tbasename = os.path.splitext(tfn)[0]
            self.codeProfileAct.setEnabled(\
                os.path.isfile("%s.profile" % basename) or \
                os.path.isfile("%s.profile" % tbasename))
            self.codeCoverageAct.setEnabled(\
                os.path.isfile("%s.coverage" % basename) or \
                os.path.isfile("%s.coverage" % tbasename))
        else:
            self.codeProfileAct.setEnabled(False)
            self.codeCoverageAct.setEnabled(False)
        
        self.emit(SIGNAL("showMenu"), "Show", self.showMenu)
    
    #########################################################################
    ## Below is the interface to the diagrams
    #########################################################################
    
    def __showContextMenuGraphics(self):
        """
        Private slot called before the graphics menu is shown.
        """
        self.emit(SIGNAL("showMenu"), "Graphics", self.graphicsMenu)
    
    def handleApplicationDiagram(self):
        """
        Private method to handle the application diagram context menu action.
        """
        res = KQMessageBox.question(None,
            self.trUtf8("Application Diagram"),
            self.trUtf8("""Include module names?"""),
            QMessageBox.StandardButtons(\
                QMessageBox.No | \
                QMessageBox.Yes),
            QMessageBox.Yes)
        
        self.applicationDiagram = ApplicationDiagram(self, self.parent(), 
            noModules = (res != QMessageBox.Yes))
        self.applicationDiagram.show()
    
    #########################################################################
    ## Below is the interface to the VCS monitor thread
    #########################################################################
    
    def __statusMonitorStatus(self, status, statusMsg):
        """
        Private method to receive the status monitor status.
        
        It simply reemits the received status.
        
        @param status status of the monitoring thread (QString, ok, nok or off)
        @param statusMsg explanotory text for the signaled status (QString)
        """
        self.emit(SIGNAL("vcsStatusMonitorStatus(QString, QString)"), status, statusMsg)
        
    def setStatusMonitorInterval(self, interval):
        """
        Public method to se the interval of the VCS status monitor thread.
        
        @param interval status monitor interval in seconds (integer)
        """
        if self.vcs is not None:
            self.vcs.setStatusMonitorInterval(interval, self)
        
    def getStatusMonitorInterval(self):
        """
        Public method to get the monitor interval.
        
        @return interval in seconds (integer)
        """
        if self.vcs is not None:
            return self.vcs.getStatusMonitorInterval()
        else:
            return 0
        
    def setStatusMonitorAutoUpdate(self, auto):
        """
        Public method to enable the auto update function.
        
        @param auto status of the auto update function (boolean)
        """
        if self.vcs is not None:
            self.vcs.setStatusMonitorAutoUpdate(auto)
        
    def getStatusMonitorAutoUpdate(self):
        """
        Public method to retrieve the status of the auto update function.
        
        @return status of the auto update function (boolean)
        """
        if self.vcs is not None:
            return self.vcs.getStatusMonitorAutoUpdate()
        else:
            return False
        
    def checkVCSStatus(self):
        """
        Public method to wake up the VCS status monitor thread.
        """
        if self.vcs is not None:
            self.vcs.checkVCSStatus()
        
    def clearStatusMonitorCachedState(self, name):
        """
        Public method to clear the cached VCS state of a file/directory.
        
        @param name name of the entry to be cleared (QString or string)
        """
        if self.vcs is not None:
            self.vcs.clearStatusMonitorCachedState(name)
        
    def startStatusMonitor(self):
        """
        Public method to start the VCS status monitor thread.
        """
        if self.vcs is not None:
            self.vcs.startStatusMonitor(self)
        
    def stopStatusMonitor(self):
        """
        Public method to stop the VCS status monitor thread.
        """
        if self.vcs is not None:
            self.vcs.stopStatusMonitor()
    
    #########################################################################
    ## Below are the plugin development related methods
    #########################################################################
    
    def __pluginCreatePkgList(self):
        """
        Private slot to create a PKGLIST file needed for archive file creation.
        """
        pkglist = os.path.join(self.ppath, "PKGLIST")
        if os.path.exists(pkglist):
            res = KQMessageBox.warning(None,
                self.trUtf8("Create Package List"),
                self.trUtf8("<p>The file <b>PKGLIST</b> already"
                    " exists.</p><p>Overwrite it?</p>"),
                QMessageBox.StandardButtons(\
                    QMessageBox.No | \
                    QMessageBox.Yes),
                QMessageBox.No)
            if res != QMessageBox.Yes:
                return  # don't overwrite
        
        # build the list of entries
        lst = []
        for key in \
            ["SOURCES", "FORMS", "RESOURCES", "TRANSLATIONS", "INTERFACES", "OTHERS"]:
            lst.extend(self.pdata[key])
        lst.sort()
        if "PKGLIST" in lst:
            lst.remove("PKGLIST")
        
        # write the file
        try:
            pkglistFile = open(pkglist, "wb")
            pkglistFile.write("\n".join(lst))
            pkglistFile.close()
        except IOError, why:
            KQMessageBox.critical(None,
                self.trUtf8("Create Package List"),
                self.trUtf8("""<p>The file <b>PKGLIST</b> could not be created.</p>"""
                            """<p>Reason: %1</p>""").arg(unicode(why)),
                QMessageBox.StandardButtons(\
                    QMessageBox.Ok))
            return
        
        if not "PKGLIST" in self.pdata["OTHERS"]:
            self.appendFile("PKGLIST")
        
    def __pluginCreateArchive(self, snapshot = False):
        """
        Private slot to create an eric4 plugin archive.
        
        @param snapshot flag indicating a snapshot archive (boolean)
        """
        pkglist = os.path.join(self.ppath, "PKGLIST")
        if not os.path.exists(pkglist):
            KQMessageBox.critical(None,
                self.trUtf8("Create Plugin Archive"),
                self.trUtf8("""<p>The file <b>PKGLIST</b> does not exist. """
                            """Aborting...</p>"""),
                QMessageBox.StandardButtons(\
                    QMessageBox.Ok))
            return
        
        if len(self.pdata["MAINSCRIPT"]) == 0 or \
           len(self.pdata["MAINSCRIPT"][0]) == 0:
            KQMessageBox.critical(None,
                self.trUtf8("Create Plugin Archive"),
                self.trUtf8("""The project does not have a main script defined. """
                            """Aborting..."""),
                QMessageBox.StandardButtons(\
                    QMessageBox.Ok))
            return
        
        try:
            pkglistFile = open(pkglist, "rb")
            names = pkglistFile.read()
            pkglistFile.close()
            names = names.splitlines()
            names.sort()
        except IOError, why:
            KQMessageBox.critical(None,
                self.trUtf8("Create Plugin Archive"),
                self.trUtf8("""<p>The file <b>PKGLIST</b> could not be read.</p>"""
                            """<p>Reason: %1</p>""").arg(unicode(why)),
                QMessageBox.StandardButtons(\
                    QMessageBox.Ok))
            return
        
        archive = \
            os.path.join(self.ppath, self.pdata["MAINSCRIPT"][0].replace(".py", ".zip"))
        try:
            try:
                archiveFile = zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED)
            except RuntimeError:
                archiveFile = zipfile.ZipFile(archive, "w")
        except IOError, why:
            KQMessageBox.critical(None,
                self.trUtf8("Create Plugin Archive"),
                self.trUtf8("""<p>The eric4 plugin archive file <b>%1</b> could """
                            """not be created.</p>"""
                            """<p>Reason: %2</p>""").arg(archive).arg(unicode(why)),
                QMessageBox.StandardButtons(\
                    QMessageBox.Ok))
            return
        
        for name in names:
            try:
                self.__createZipDirEntries(os.path.split(name)[0], archiveFile)
                if snapshot and name == self.pdata["MAINSCRIPT"][0]:
                    snapshotSource, version = self.__createSnapshotSource(\
                        os.path.join(self.ppath, self.pdata["MAINSCRIPT"][0]))
                    archiveFile.writestr(name, snapshotSource)
                else:
                    archiveFile.write(os.path.join(self.ppath, name), name)
                    if name == self.pdata["MAINSCRIPT"][0]:
                        version = self.__pluginExtractVersion(\
                            os.path.join(self.ppath, self.pdata["MAINSCRIPT"][0]))
            except OSError, why:
                KQMessageBox.critical(None,
                    self.trUtf8("Create Plugin Archive"),
                    self.trUtf8("""<p>The file <b>%1</b> could not be stored """
                                """in the archive. Ignoring it.</p>"""
                                """<p>Reason: %2</p>""")\
                                .arg(os.path.join(self.ppath, name)).arg(unicode(why)),
                    QMessageBox.StandardButtons(\
                        QMessageBox.Ok))
        archiveFile.writestr("VERSION", version)
        archiveFile.close()
        
        if not archive in self.pdata["OTHERS"]:
            self.appendFile(archive)
        
        KQMessageBox.information(None,
            self.trUtf8("Create Plugin Archive"),
            self.trUtf8("""<p>The eric4 plugin archive file <b>%1</b> was """
                        """created successfully.</p>""").arg(archive),
            QMessageBox.StandardButtons(\
                QMessageBox.Ok))
    
    def __pluginCreateSnapshotArchive(self):
        """
        Private slot to create an eric4 plugin archive snapshot release.
        """
        self.__pluginCreateArchive(True)
    
    def __createZipDirEntries(self, path, zipFile):
        """
        Private method to create dir entries in the zip file.
        
        @param path name of the directory entry to create (string)
        @param zipFile open ZipFile object (zipfile.ZipFile)
        """
        if path == "" or path == "/" or path == "\\":
            return
        
        if not path.endswith("/") and not path.endswith("\\"):
            path = "%s/" % path
        
        if not path in zipFile.namelist():
            self.__createZipDirEntries(os.path.split(path[:-1])[0], zipFile)
            zipFile.writestr(path, "")
    
    def __createSnapshotSource(self, filename):
        """
        Private method to create a snapshot plugin version.
        
        The version entry in the plugin module is modified to signify
        a snapshot version. This method appends the string "-snapshot-"
        and date indicator to the version string.
        
        @param filename name of the plugin file to modify (string)
        @return modified source (string), snapshot version string (string)
        """
        try:
            f = open(filename, "r")
            sourcelines = f.readlines()
            f.close()
        except IOError, why:
            KQMessageBox.critical(None,
                self.trUtf8("Create Plugin Archive"),
                self.trUtf8("""<p>The plugin file <b>%1</b> could """
                            """not be read.</p>"""
                            """<p>Reason: %2</p>""").arg(archive).arg(unicode(why)),
                QMessageBox.StandardButtons(\
                    QMessageBox.Ok))
            return ""
        
        lineno = 0
        while lineno < len(sourcelines):
            if sourcelines[lineno].startswith("version = "):
                # found the line to modify
                datestr = time.strftime("%Y%m%d")
                lineend = sourcelines[lineno].replace(sourcelines[lineno].rstrip(), "")
                sversion = "%s-snapshot-%s" % \
                    (sourcelines[lineno].replace("version = ", "").strip()[1:-1], 
                     datestr)
                sourcelines[lineno] = '%s + "-snapshot-%s"%s' % \
                    (sourcelines[lineno].rstrip(), datestr, lineend)
                break
            
            lineno += 1
        
        return "".join(sourcelines), sversion
    
    def __pluginExtractVersion(self, filename):
        """
        Private method to extract the version number entry.
        
        @param filename name of the plugin file to modify (string)
        @return version string (string)
        """
        version = "0.0.0"
        try:
            f = open(filename, "r")
            sourcelines = f.readlines()
            f.close()
        except IOError, why:
            KQMessageBox.critical(None,
                self.trUtf8("Create Plugin Archive"),
                self.trUtf8("""<p>The plugin file <b>%1</b> could """
                            """not be read.</p>"""
                            """<p>Reason: %2</p>""").arg(archive).arg(unicode(why)),
                QMessageBox.StandardButtons(\
                    QMessageBox.Ok))
            return ""
        
        lineno = 0
        while lineno < len(sourcelines):
            if sourcelines[lineno].startswith("version = "):
                version = sourcelines[lineno].replace("version = ", "").strip()[1:-1]
                break
            
            lineno += 1
        
        return version
