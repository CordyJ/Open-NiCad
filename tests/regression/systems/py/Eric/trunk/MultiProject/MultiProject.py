# -*- coding: utf-8 -*-

# Copyright (c) 2008 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the multi project management functionality.
"""

import os
import sys
import cStringIO

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from KdeQt import KQFileDialog, KQMessageBox
from KdeQt.KQApplication import e4App

from Globals import recentNameMultiProject

from PropertiesDialog import PropertiesDialog
from AddProjectDialog import AddProjectDialog

from E4XML.XMLUtilities import make_parser
from E4XML.XMLErrorHandler import XMLErrorHandler, XMLFatalParseError
from E4XML.XMLEntityResolver import XMLEntityResolver

from E4XML.MultiProjectHandler import MultiProjectHandler
from E4XML.MultiProjectWriter import MultiProjectWriter

import UI.PixmapCache

from E4Gui.E4Action import E4Action, createActionGroup

import Preferences
import Utilities

class MultiProject(QObject):
    """
    Class implementing the project management functionality.
    
    @signal dirty(int) emitted when the dirty state changes
    @signal newMultiProject() emitted after a new multi project was generated
    @signal multiProjectOpened() emitted after a multi project file was read
    @signal multiProjectClosed() emitted after a multi project was closed
    @signal multiProjectPropertiesChanged() emitted after the multi project 
            properties were changed
    @signal showMenu(string, QMenu) emitted when a menu is about to be shown. 
            The name of the menu and a reference to the menu are given.
    @signal projectDataChanged(project data dict) emitted after a project entry
            has been changed
    @signal projectAdded(project data dict) emitted after a project entry
            has been added
    @signal projectRemoved(project data dict) emitted after a project entry
            has been removed
    @signal projectOpened(filename) emitted after the project has been opened
    """
    def __init__(self, project, parent = None, filename = None):
        """
        Constructor
        
        @param project reference to the project object (Project.Project)
        @param parent parent widget (usually the ui object) (QWidget)
        @param filename optional filename of a multi project file to open (string)
        """
        QObject.__init__(self, parent)
        
        self.ui = parent
        self.projectObject = project
        
        self.__initData()
        
        self.recent = QStringList()
        self.__loadRecent()
        
        if filename is not None:
            self.openMultiProject(filename)
    
    def __initData(self):
        """
        Private method to initialize the multi project data part.
        """
        self.loaded = False     # flag for the loaded status
        self.dirty = False      # dirty flag
        self.pfile = ""         # name of the multi project file
        self.ppath = ""         # name of the multi project directory
        self.description = ""   # description of the multi project
        self.name = ""
        self.opened = False
        self.projects = []      # list of project info; each info entry is a dictionary
                                # 'name'        : Name of the project
                                # 'file'        : project filename
                                # 'master'      : flag indicating the master project
                                # 'description' : description of the project
    
    def __loadRecent(self):
        """
        Private method to load the recently opened multi project filenames.
        """
        self.recent.clear()
        Preferences.Prefs.rsettings.sync()
        rp = Preferences.Prefs.rsettings.value(recentNameMultiProject)
        if rp.isValid():
            for f in rp.toStringList():
                if QFileInfo(f).exists():
                    self.recent.append(f)
    
    def __saveRecent(self):
        """
        Private method to save the list of recently opened filenames.
        """
        Preferences.Prefs.rsettings.setValue(recentNameMultiProject, 
                                             QVariant(self.recent))
        Preferences.Prefs.rsettings.sync()
    
    def getMostRecent(self):
        """
        Public method to get the most recently opened multiproject.
        
        @return path of the most recently opened multiproject (string)
        """
        if len(self.recent):
            return unicode(self.recent[0])
        else:
            return None
        
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
    
    def getMultiProjectPath(self):
        """
        Public method to get the multi project path.
        
        @return multi project path (string)
        """
        return self.ppath
    
    def getMultiProjectFile(self):
        """
        Public method to get the path of the multi project file.
        
        @return path of the multi project file (string)
        """
        return self.pfile
    
    def __checkFilesExist(self):
        """
        Private method to check, if the files in a list exist. 
        
        The project files are checked for existance in the
        filesystem. Non existant projects are removed from the list and the
        dirty state of the multi project is changed accordingly.
        """
        removed = False
        removelist = []
        for project in self.projects:
            if not os.path.exists(project['file']):
                removelist.append(project)
                removed = True
        
        if removed:
            for project in removelist:
                self.projects.remove(project)
            self.setDirty(True)
    
    def __readMultiProject(self, fn):
        """
        Private method to read in a multi project (.e4m, .e4mz) file.
        
        @param fn filename of the multi project file to be read (string or QString)
        @return flag indicating success
        """
        fn = unicode(fn)
        try:
            if fn.lower().endswith("e4mz"):
                try:
                    import gzip
                except ImportError:
                    QApplication.restoreOverrideCursor()
                    KQMessageBox.critical(None,
                        self.trUtf8("Read multiproject file"),
                        self.trUtf8("""Compressed multiproject files not supported."""
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
                self.trUtf8("Read multiproject file"),
                self.trUtf8("<p>The multiproject file <b>%1</b> could not be read.</p>")\
                    .arg(fn))
            return False
            
        self.pfile = os.path.abspath(fn)
        self.ppath = os.path.abspath(os.path.dirname(fn))
        
        # now read the file
        if not line.startswith('<?xml'):
            QApplication.restoreOverrideCursor()
            KQMessageBox.critical(None,
                self.trUtf8("Read multiproject file"),
                self.trUtf8("<p>The multiproject file <b>%1</b> has an unsupported"
                            " format.</p>").arg(fn))
            return False
            
        # insert filename into list of recently opened multi projects
        self.__syncRecent()
        
        res = self.__readXMLMultiProject(fn, dtdLine.startswith("<!DOCTYPE"))
        if res:
            self.name = os.path.splitext(os.path.basename(fn))[0]
            
            # check, if the files of the multi project still exist
            self.__checkFilesExist()
            
        return res

    def __readXMLMultiProject(self, fn, validating):
        """
        Private method to read the multi project data from an XML file.
        
        @param fn filename of the multi project file to be read (string or QString)
        @param validating flag indicating a validation of the XML file is
            requested (boolean)
        @return flag indicating success
        """
        fn = unicode(fn)
        if fn.lower().endswith("e4mz"):
            # work around for a bug in xmlproc
            validating = False
        
        parser = make_parser(validating)
        handler = MultiProjectHandler(self)
        er = XMLEntityResolver()
        eh = XMLErrorHandler()
        
        parser.setContentHandler(handler)
        parser.setEntityResolver(er)
        parser.setErrorHandler(eh)
        
        try:
            if fn.lower().endswith("e4mz"):
                try:
                    import gzip
                except ImportError:
                    QApplication.restoreOverrideCursor()
                    KQMessageBox.critical(None,
                        self.trUtf8("Read multiproject file"),
                        self.trUtf8("""Compressed multiproject files not supported."""
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
                self.trUtf8("Read multiproject file"),
                self.trUtf8("<p>The multiproject file <b>%1</b> could not be read.</p>")\
                    .arg(fn))
            return False
        except XMLFatalParseError:
            QApplication.restoreOverrideCursor()
            KQMessageBox.critical(None,
                self.trUtf8("Read multiproject file"),
                self.trUtf8("<p>The multiproject file <b>%1</b> has invalid "
                    "contents.</p>").arg(fn))
            eh.showParseMessages()
            return False
        
        QApplication.restoreOverrideCursor()
        eh.showParseMessages()
        QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
        QApplication.processEvents()
        return True
    
    def __writeMultiProject(self, fn = None):
        """
        Private method to save the multi project infos to a multi project file.
        
        @param fn optional filename of the multi project file to be written.
                If fn is None, the filename stored in the multi project object
                is used. This is the 'save' action. If fn is given, this filename
                is used instead of the one in the multi project object. This is the
                'save as' action.
        @return flag indicating success
        """
        if fn is None:
            fn = self.pfile
        
        res = self.__writeXMLMultiProject(fn)
        
        if res:
            self.pfile = os.path.abspath(fn)
            self.ppath = os.path.abspath(os.path.dirname(fn))
            self.name = os.path.splitext(os.path.basename(fn))[0]
            self.setDirty(False)
            
            # insert filename into list of recently opened projects
            self.__syncRecent()
        
        return res
    
    def __writeXMLMultiProject(self, fn = None):
        """
        Private method to write the multi project data to an XML file.
        
        @param fn the filename of the multi project file (string)
        """
        try:
            if fn.lower().endswith("e4mz"):
                try:
                    import gzip
                except ImportError:
                    KQMessageBox.critical(None,
                        self.trUtf8("Save multiproject file"),
                        self.trUtf8("""Compressed multiproject files not supported."""
                                    """ The compression library is missing."""))
                    return False
                f = gzip.open(fn, "wb")
            else:
                f = open(fn, "wb")
            
            MultiProjectWriter(self, f, os.path.splitext(os.path.basename(fn))[0])\
                .writeXML()
            
            f.close()
            
        except IOError:
            KQMessageBox.critical(None,
                self.trUtf8("Save multiproject file"),
                self.trUtf8("<p>The multiproject file <b>%1</b> could not be "
                    "written.</p>").arg(fn))
            return False
        
        return True
    
    def addProject(self, startdir = None):
        """
        Public slot used to add files to the project.
        
        @param startdir start directory for the selection dialog
        """
        if startdir is None:
            startdir = self.ppath
        dlg = AddProjectDialog(self.ui, startdir=startdir)
        if dlg.exec_() == QDialog.Accepted:
            name, filename, isMaster, description = dlg.getData()
            
            # step 1: check, if project was already added
            for project in self.projects:
                if project['file'] == filename:
                    return
            
            # step 2: check, if master should be changed
            if isMaster:
                for project in self.projects:
                    if project['master']:
                        project['master'] = False
                        self.emit(SIGNAL("projectDataChanged"), project)
                        self.setDirty(True)
                        break
            
            # step 3: add the project entry
            project = {
                'name'        : name, 
                'file'        : filename, 
                'master'      : isMaster, 
                'description' : description, 
            }
            self.projects.append(project)
            self.emit(SIGNAL("projectAdded"), project)
            self.setDirty(True)
    
    def changeProjectProperties(self, pro):
        """
        Public method to change the data of a project entry.
        
        @param pro dictionary with the project data
        """
        # step 1: check, if master should be changed
        if pro['master']:
            for project in self.projects:
                if project['master']:
                    if project['file'] != pro['file']:
                        project['master'] = False
                        self.emit(SIGNAL("projectDataChanged"), project)
                        self.setDirty(True)
                    break
        
        # step 2: change the entry
        for project in self.projects:
            if project['file'] == pro['file']:
                # project filename is not changeable via interface
                project['name'] = pro['name']
                project['master'] = pro['master']
                project['description'] = pro['description']
                self.emit(SIGNAL("projectDataChanged"), project)
                self.setDirty(True)
    
    def getProjects(self):
        """
        Public method to get all project entries.
        """
        return self.projects
    
    def getProject(self, fn):
        """
        Public method to get a reference to a project entry.
        
        @param fn filename of the project to be removed from the multi project
        @return dictionary containing the project data
        """
        for project in self.projects:
            if project['file'] == fn:
                return project
        
        return None
    
    def removeProject(self, fn):
        """
        Public slot to remove a project from the multi project.
        
        @param fn filename of the project to be removed from the multi project
        """
        for project in self.projects:
            if project['file'] == fn:
                self.projects.remove(project)
                self.emit(SIGNAL("projectRemoved"), project)
                self.setDirty(True)
                break
    
    def newMultiProject(self):
        """
        Public slot to build a new multi project.
        
        This method displays the new multi project dialog and initializes
        the multi project object with the data entered.
        """
        if not self.checkDirty():
            return
            
        dlg = PropertiesDialog(self, True)
        if dlg.exec_() == QDialog.Accepted:
            self.closeMultiProject()
            dlg.storeData()
            self.opened = True
            self.setDirty(True)
            self.closeAct.setEnabled(True)
            self.saveasAct.setEnabled(True)
            self.addProjectAct.setEnabled(True)
            self.propsAct.setEnabled(True)
            self.emit(SIGNAL('newMultiProject'))
    
    def __showProperties(self):
        """
        Private slot to display the properties dialog.
        """
        dlg = PropertiesDialog(self, False)
        if dlg.exec_() == QDialog.Accepted:
            dlg.storeData()
            self.setDirty(True)
            self.emit(SIGNAL('multiProjectPropertiesChanged'))
    
    def openMultiProject(self, fn = None, openMaster = True):
        """
        Public slot to open a multi project.
        
        @param fn optional filename of the multi project file to be read
        @param openMaster flag indicating, that the master project 
            should be opened depending on the configuration(boolean)
        """
        if not self.checkDirty():
            return
        
        if fn is None:
            fn = KQFileDialog.getOpenFileName(\
                self.parent(),
                self.trUtf8("Open multiproject"),
                QString(),
                self.trUtf8("Multiproject Files (*.e4m *.e4mz)"))
            
            if fn.isEmpty():
                fn = None
            else:
                fn = unicode(fn)
        
        QApplication.processEvents()
        
        if fn is not None:
            QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
            QApplication.processEvents()
            self.closeMultiProject()
            if self.__readMultiProject(fn):
                self.opened = True
                QApplication.restoreOverrideCursor()
                QApplication.processEvents()
                
                self.closeAct.setEnabled(True)
                self.saveasAct.setEnabled(True)
                self.addProjectAct.setEnabled(True)
                self.propsAct.setEnabled(True)
                
                self.emit(SIGNAL('multiProjectOpened'))
                
                if openMaster and Preferences.getMultiProject("OpenMasterAutomatically"):
                    self.__openMasterProject(False)
            else:
                QApplication.restoreOverrideCursor()
    
    def saveMultiProject(self):
        """
        Public slot to save the current multi project.
        
        @return flag indicating success
        """
        if self.isDirty():
            if len(self.pfile) > 0:
                ok = self.__writeMultiProject()
            else:
                ok = self.saveMultiProjectAs()
        else:
            ok = True
        return ok
    
    def saveMultiProjectAs(self):
        """
        Public slot to save the current multi project to a different file.
        
        @return flag indicating success
        """
        if Preferences.getProject("CompressedProjectFiles"):
            selectedFilter = self.trUtf8("Compressed Multiproject Files (*.e4mz)")
        else:
            selectedFilter = self.trUtf8("Multiproject Files (*.e4m)")
        fn = KQFileDialog.getSaveFileName(\
            self.parent(),
            self.trUtf8("Save multiproject as"),
            self.ppath,
            self.trUtf8("Multiproject Files (*.e4m);;"
                "Compressed Multiproject Files (*.e4mz)"),
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
            ok = self.__writeMultiProject(unicode(fn))
            
            self.emit(SIGNAL('multiProjectClosed'))
            self.emit(SIGNAL('multiProjectOpened'))
            return True
        else:
            return False
    
    def checkDirty(self):
        """
        Public method to check the dirty status and open a message window.
        
        @return flag indicating whether this operation was successful
        """
        if self.isDirty():
            res = KQMessageBox.warning(self.parent(), 
                self.trUtf8("Close Multiproject"),
                self.trUtf8("The current multiproject has unsaved changes."),
                QMessageBox.StandardButtons(\
                    QMessageBox.Abort | \
                    QMessageBox.Discard | \
                    QMessageBox.Save),
                QMessageBox.Save)
            if res == QMessageBox.Save:
                return self.saveMultiProject()
            elif res == QMessageBox.Discard:
                self.setDirty(False)
                return True
            elif res == QMessageBox.Abort:
                return False
            
        return True
    
    def closeMultiProject(self):
        """
        Public slot to close the current multi project.
        
        @return flag indicating success (boolean)
        """
        # save the list of recently opened projects
        self.__saveRecent()
        
        if not self.isOpen():
            return True
        
        if not self.checkDirty():
            return False
        
        # now close the current project, if it belongs to the multi project
        pfile = self.projectObject.getProjectFile()
        if pfile:
            for project in self.projects:
                if project['file'] == pfile:
                    if not self.projectObject.closeProject():
                        return False
                    break
        
        self.__initData()
        self.closeAct.setEnabled(False)
        self.saveasAct.setEnabled(False)
        self.saveAct.setEnabled(False)
        self.addProjectAct.setEnabled(False)
        self.propsAct.setEnabled(False)
        
        self.emit(SIGNAL('multiProjectClosed'))
        
        return True

    def initActions(self):
        """
        Public slot to initialize the multi project related actions.
        """
        self.actions = []
        
        self.actGrp1 = createActionGroup(self)
        
        act = E4Action(self.trUtf8('New multiproject'),
                UI.PixmapCache.getIcon("multiProjectNew.png"),
                self.trUtf8('&New...'), 0, 0,
                self.actGrp1,'multi_project_new')
        act.setStatusTip(self.trUtf8('Generate a new multiproject'))
        act.setWhatsThis(self.trUtf8(
            """<b>New...</b>"""
            """<p>This opens a dialog for entering the info for a"""
            """ new multiproject.</p>"""
        ))
        self.connect(act, SIGNAL('triggered()'), self.newMultiProject)
        self.actions.append(act)

        act = E4Action(self.trUtf8('Open multiproject'),
                UI.PixmapCache.getIcon("multiProjectOpen.png"),
                self.trUtf8('&Open...'), 0, 0,
                self.actGrp1,'multi_project_open')
        act.setStatusTip(self.trUtf8('Open an existing multiproject'))
        act.setWhatsThis(self.trUtf8(
            """<b>Open...</b>"""
            """<p>This opens an existing multiproject.</p>"""
        ))
        self.connect(act, SIGNAL('triggered()'), self.openMultiProject)
        self.actions.append(act)

        self.closeAct = E4Action(self.trUtf8('Close multiproject'),
                UI.PixmapCache.getIcon("multiProjectClose.png"),
                self.trUtf8('&Close'), 0, 0, self, 'multi_project_close')
        self.closeAct.setStatusTip(self.trUtf8('Close the current multiproject'))
        self.closeAct.setWhatsThis(self.trUtf8(
            """<b>Close</b>"""
            """<p>This closes the current multiproject.</p>"""
        ))
        self.connect(self.closeAct, SIGNAL('triggered()'), self.closeMultiProject)
        self.actions.append(self.closeAct)

        self.saveAct = E4Action(self.trUtf8('Save multiproject'),
                UI.PixmapCache.getIcon("multiProjectSave.png"),
                self.trUtf8('&Save'), 0, 0, self, 'multi_project_save')
        self.saveAct.setStatusTip(self.trUtf8('Save the current multiproject'))
        self.saveAct.setWhatsThis(self.trUtf8(
            """<b>Save</b>"""
            """<p>This saves the current multiproject.</p>"""
        ))
        self.connect(self.saveAct, SIGNAL('triggered()'), self.saveMultiProject)
        self.actions.append(self.saveAct)

        self.saveasAct = E4Action(self.trUtf8('Save multiproject as'),
                UI.PixmapCache.getIcon("multiProjectSaveAs.png"),
                self.trUtf8('Save &as...'), 0, 0, self, 'multi_project_save_as')
        self.saveasAct.setStatusTip(self.trUtf8(
            'Save the current multiproject to a new file'))
        self.saveasAct.setWhatsThis(self.trUtf8(
            """<b>Save as</b>"""
            """<p>This saves the current multiproject to a new file.</p>"""
        ))
        self.connect(self.saveasAct, SIGNAL('triggered()'), self.saveMultiProjectAs)
        self.actions.append(self.saveasAct)

        self.addProjectAct = E4Action(self.trUtf8('Add project to multiproject'),
                UI.PixmapCache.getIcon("fileProject.png"),
                self.trUtf8('Add &project...'), 0, 0,
                self,'multi_project_add_project')
        self.addProjectAct.setStatusTip(self.trUtf8(
            'Add a project to the current multiproject'))
        self.addProjectAct.setWhatsThis(self.trUtf8(
            """<b>Add project...</b>"""
            """<p>This opens a dialog for adding a project"""
            """ to the current multiproject.</p>"""
        ))
        self.connect(self.addProjectAct, SIGNAL('triggered()'), self.addProject)
        self.actions.append(self.addProjectAct)

        self.propsAct = E4Action(self.trUtf8('Multiproject properties'),
                UI.PixmapCache.getIcon("multiProjectProps.png"),
                self.trUtf8('&Properties...'), 0, 0, self, 'multi_project_properties')
        self.propsAct.setStatusTip(self.trUtf8('Show the multiproject properties'))
        self.propsAct.setWhatsThis(self.trUtf8(
            """<b>Properties...</b>"""
            """<p>This shows a dialog to edit the multiproject properties.</p>"""
        ))
        self.connect(self.propsAct, SIGNAL('triggered()'), self.__showProperties)
        self.actions.append(self.propsAct)

        self.closeAct.setEnabled(False)
        self.saveAct.setEnabled(False)
        self.saveasAct.setEnabled(False)
        self.addProjectAct.setEnabled(False)
        self.propsAct.setEnabled(False)
    
    def initMenu(self):
        """
        Public slot to initialize the multi project menu.
        
        @return the menu generated (QMenu)
        """
        menu = QMenu(self.trUtf8('&Multiproject'), self.parent())
        self.recentMenu = QMenu(self.trUtf8('Open &Recent Multiprojects'), menu)
        
        self.__menus = {
            "Main"      : menu, 
            "Recent"    : self.recentMenu, 
        }
        
        # connect the aboutToShow signals
        self.connect(self.recentMenu, SIGNAL('aboutToShow()'), 
            self.__showContextMenuRecent)
        self.connect(self.recentMenu, SIGNAL('triggered(QAction *)'),
                     self.__openRecent)
        self.connect(menu, SIGNAL('aboutToShow()'), self.__showMenu)
        
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
        menu.addAction(self.addProjectAct)
        menu.addSeparator()
        menu.addAction(self.propsAct)
        
        self.menu = menu
        return menu
    
    def initToolbar(self, toolbarManager):
        """
        Public slot to initialize the multi project toolbar.
        
        @param toolbarManager reference to a toolbar manager object (E4ToolBarManager)
        @return the toolbar generated (QToolBar)
        """
        tb = QToolBar(self.trUtf8("Multiproject"), self.parent())
        tb.setIconSize(UI.Config.ToolBarIconSize)
        tb.setObjectName("MultiProjectToolbar")
        tb.setToolTip(self.trUtf8('Multiproject'))
        
        tb.addActions(self.actGrp1.actions())
        tb.addAction(self.closeAct)
        tb.addSeparator()
        tb.addAction(self.saveAct)
        tb.addAction(self.saveasAct)
        
        toolbarManager.addToolBar(tb, tb.windowTitle())
        toolbarManager.addAction(self.addProjectAct, tb.windowTitle())
        toolbarManager.addAction(self.propsAct, tb.windowTitle())
        
        return tb
    
    def __showMenu(self):
        """
        Private method to set up the multi project menu.
        """
        self.menuRecentAct.setEnabled(len(self.recent) > 0)
        
        self.emit(SIGNAL("showMenu"), "Main", self.__menus["Main"])
    
    def __syncRecent(self):
        """
        Private method to synchronize the list of recently opened multi projects
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
        Private method to set up the recent multi projects menu.
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
        Private method to open a multi project from the list of rencently 
        opened multi projects.
        
        @param act reference to the action that triggered (QAction)
        """
        file = unicode(act.data().toString())
        if file:
            self.openMultiProject(file)
    
    def __clearRecent(self):
        """
        Private method to clear the recent multi projects menu.
        """
        self.recent.clear()
    
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
    
    def openProject(self, filename):
        """
        Public slot to open a project.
        
        @param filename filename of the project file (string)
        """
        self.projectObject.openProject(filename)
        self.emit(SIGNAL('projectOpened'), filename)
    
    def __openMasterProject(self, reopen = True):
        """
        Public slot to open the master project.
        
        @param reopen flag indicating, that the master project should be
            reopened, if it has been opened already (boolean)
        """
        for project in self.projects:
            if project['master']:
                if reopen or \
                   not self.projectObject.isOpen() or \
                   self.projectObject.getProjectFile() != project['file']:
                    self.openProject(project['file'])
                    return
    
    def getMasterProjectFile(self):
        """
        Public method to get the filename of the master project.
        
        @return name of the master project file (string)
        """
        for project in self.projects:
            if project['master']:
                return project['file']
        
        return None
    
    def getDependantProjectFiles(self):
        """
        Public method to get the filenames of the dependant projects.
        
        @return names of the dependant project files (list of strings)
        """
        files = []
        for project in self.projects:
            if not project['master']:
                files.append(project['file'])
        return files
