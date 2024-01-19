# -*- coding: utf-8 -*-

# Copyright (c) 2005 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the base class of the VCS project helper.
"""

import os
import sys
import shutil
import copy

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from KdeQt import KQMessageBox, KQInputDialog
from KdeQt.KQApplication import e4App

import VCS
from CommandOptionsDialog import vcsCommandOptionsDialog
from RepositoryInfoDialog import VcsRepositoryInfoDialog

from E4Gui.E4Action import E4Action

import Utilities
import Preferences

class VcsProjectHelper(QObject):
    """
    Class implementing the base class of the VCS project helper.
    """
    def __init__(self, vcsObject, projectObject, parent = None, name = None):
        """
        Constructor
        
        @param vcsObject reference to the vcs object
        @param projectObject reference to the project object
        @param parent parent widget (QWidget)
        @param name name of this object (string or QString)
        """
        QObject.__init__(self, parent)
        if name:
            self.setObjectName(name)
        
        self.vcs = vcsObject
        self.project = projectObject
        
        self.actions = []
        
        self.initActions()
        
    def setObjects(self, vcsObject, projectObject):
        """
        Public method to set references to the vcs and project objects.
        
        @param vcsObject reference to the vcs object
        @param projectObject reference to the project object
        """
        self.vcs = vcsObject
        self.project = projectObject
    
    def initActions(self):
        """
        Public method to generate the action objects.
        """
        self.vcsNewAct = E4Action(self.trUtf8('New from repository'),
                self.trUtf8('&New from repository...'), 0, 0, self, 'vcs_new')
        self.vcsNewAct.setStatusTip(self.trUtf8(
            'Create a new project from the VCS repository'
        ))
        self.vcsNewAct.setWhatsThis(self.trUtf8(
            """<b>New from repository</b>"""
            """<p>This creates a new local project from the VCS repository.</p>"""
        ))
        self.connect(self.vcsNewAct, SIGNAL('triggered()'), self._vcsCheckout)
        self.actions.append(self.vcsNewAct)
        
        self.vcsExportAct = E4Action(self.trUtf8('Export from repository'), 
                self.trUtf8('&Export from repository...'), 0, 0, self, 'vcs_export')
        self.vcsExportAct.setStatusTip(self.trUtf8(
            'Export a project from the repository'
        ))
        self.vcsExportAct.setWhatsThis(self.trUtf8(
            """<b>Export from repository</b>"""
            """<p>This exports a project from the repository.</p>"""
        ))
        self.connect(self.vcsExportAct, SIGNAL('triggered()'), self._vcsExport)
        self.actions.append(self.vcsExportAct)
        
        self.vcsAddAct = E4Action(self.trUtf8('Add to repository'),
                self.trUtf8('&Add to repository...'), 0, 0, self, 'vcs_add')
        self.vcsAddAct.setStatusTip(self.trUtf8(
            'Add the local project to the VCS repository'
        ))
        self.vcsAddAct.setWhatsThis(self.trUtf8(
            """<b>Add to repository</b>"""
            """<p>This adds (imports) the local project to the VCS repository.</p>"""
        ))
        self.connect(self.vcsAddAct, SIGNAL('triggered()'), self._vcsImport)
        self.actions.append(self.vcsAddAct)
    
    def initMenu(self, menu):
        """
        Public method to generate the VCS menu.
        
        @param menu reference to the menu to be populated (QMenu)
        """
        menu.clear()
        
        menu.addAction(self.vcsNewAct)
        menu.addAction(self.vcsExportAct)
        menu.addSeparator()
        menu.addAction(self.vcsAddAct)
        menu.addSeparator()

    def showMenu(self):
        """
        Public slot called before the vcs menu is shown.
        """
        self.vcsAddAct.setEnabled(self.project.isOpen())

    def _vcsCheckout(self, export = False):
        """
        Protected slot used to create a local project from the repository.
        
        @param export flag indicating whether an export or a checkout
                should be performed
        """
        if not self.project.checkDirty():
            return
        
        vcsSystemsDict = e4App().getObject("PluginManager")\
            .getPluginDisplayStrings("version_control")
        vcsSystemsDisplay = QStringList()
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
        if not ok:
            return
        for vcsSystem, vcsSystemDisplay in vcsSystemsDict.items():
            if vcsSystemDisplay == vcsSelected:
                break
        
        self.project.pdata["VCS"] = [vcsSystem]
        self.project.vcs = self.project.initVCS(vcsSystem)
        if self.project.vcs is not None:
            vcsdlg = self.project.vcs.vcsNewProjectOptionsDialog()
            if vcsdlg.exec_() == QDialog.Accepted:
                self.project.closeProject()
                projectdir, vcsDataDict = vcsdlg.getData()
                self.project.pdata["VCS"] = [vcsSystem]
                self.project.vcs = self.project.initVCS(vcsSystem)
                # edit VCS command options
                vcores = KQMessageBox.question(None,
                    self.trUtf8("New Project"),
                    self.trUtf8("""Would you like to edit the VCS command options?"""),
                    QMessageBox.StandardButtons(\
                        QMessageBox.No | \
                        QMessageBox.Yes),
                    QMessageBox.No)
                if vcores == QMessageBox.Yes:
                    codlg = vcsCommandOptionsDialog(self.project.vcs)
                    if codlg.exec_() == QDialog.Accepted:
                        self.project.vcs.vcsSetOptions(codlg.getOptions())
                
                # create the project directory if it doesn't exist already
                if not os.path.isdir(projectdir):
                    try:
                        os.makedirs(projectdir)
                    except EnvironmentError:
                        KQMessageBox.critical(None,
                            self.trUtf8("Create project directory"),
                            self.trUtf8("<p>The project directory <b>%1</b> could not"
                                " be created.</p>").arg(projectdir))
                        self.project.pdata["VCS"] = ['None']
                        self.project.vcs = self.project.initVCS()
                        return
                
                # create the project from the VCS
                self.project.vcs.vcsSetDataFromDict(vcsDataDict)
                if export:
                    ok = self.project.vcs.vcsExport(vcsDataDict, projectdir)
                else:
                    ok = self.project.vcs.vcsCheckout(vcsDataDict, projectdir, False)
                if ok:
                    projectdir = os.path.normpath(projectdir)
                    filters = QStringList() << "*.e4p" << "*.e4pz" << "*.e3p" << "*.e3pz"
                    d = QDir(projectdir)
                    plist = d.entryInfoList(filters)
                    if len(plist):
                        if len(plist) == 1:
                            self.project.openProject(plist[0].absoluteFilePath())
                            self.project.emit(SIGNAL('newProject'))
                        else:
                            pfilenamelist = d.entryList(filters)
                            pfilename, ok = KQInputDialog.getItem(
                                None,
                                self.trUtf8("New project from repository"),
                                self.trUtf8("Select a project file to open."),
                                pfilenamelist, 0, False)
                            if ok:
                                self.project.openProject(\
                                    QFileInfo(d, pfilename).absoluteFilePath())
                                self.project.emit(SIGNAL('newProject'))
                        if export:
                            self.project.pdata["VCS"] = ['None']
                            self.project.vcs = self.project.initVCS()
                            self.project.setDirty(True)
                            self.project.saveProject()
                    else:
                        res = KQMessageBox.question(None,
                            self.trUtf8("New project from repository"),
                            self.trUtf8("The project retrieved from the repository"
                                " does not contain an eric project file"
                                " (*.e4p *.e4pz *.e3p *.e3pz)."
                                " Create it?"),
                            QMessageBox.StandardButtons(\
                                QMessageBox.No | \
                                QMessageBox.Yes),
                            QMessageBox.Yes)
                        if res == QMessageBox.Yes:
                            self.project.ppath = projectdir
                            self.project.opened = True
                            
                            from Project.PropertiesDialog import PropertiesDialog
                            dlg = PropertiesDialog(self.project, False)
                            if dlg.exec_() == QDialog.Accepted:
                                dlg.storeData()
                                self.project.initFileTypes()
                                self.project.setDirty(True)
                                try:
                                    ms = os.path.join(self.project.ppath, 
                                                      self.project.pdata["MAINSCRIPT"][0])
                                    if os.path.exists(ms):
                                        self.project.appendFile(ms)
                                except IndexError:
                                    ms = ""
                                self.project.newProjectAddFiles(ms)
                                self.project.saveProject()
                                self.project.openProject(self.project.pfile)
                                if not export:
                                    res = KQMessageBox.question(None,
                                        self.trUtf8("New project from repository"),
                                        self.trUtf8("Shall the project file be added to"
                                            " the repository?"),
                                        QMessageBox.StandardButtons(\
                                            QMessageBox.No | \
                                            QMessageBox.Yes),
                                        QMessageBox.Yes)
                                    if res == QMessageBox.Yes:
                                        self.project.vcs.vcsAdd(self.project.pfile)
                else:
                    KQMessageBox.critical(None,
                        self.trUtf8("New project from repository"),
                        self.trUtf8("""The project could not be retrieved from"""
                            """ the repository."""))
                    self.project.pdata["VCS"] = ['None']
                    self.project.vcs = self.project.initVCS()
            else:
                self.project.pdata["VCS"] = ['None']
                self.project.vcs = self.project.initVCS()

    def _vcsExport(self):
        """
        Protected slot used to export a project from the repository.
        """
        self._vcsCheckout(True)

    def _vcsImport(self):
        """
        Protected slot used to import the local project into the repository.
        
        <b>NOTE</b>: 
            This does not necessarily make the local project a vcs controlled
            project. You may have to checkout the project from the repository in 
            order to accomplish that.
        """
        def revertChanges():
            """
            Local function do revert the changes made to the project object.
            """
            self.project.pdata["VCS"] = pdata_vcs[:]
            self.project.pdata["VCSOPTIONS"] = copy.deepcopy(pdata_vcsoptions)
            self.project.pdata["VCSOTHERDATA"] = copy.deepcopy(pdata_vcsother)
            self.project.vcs = vcs
            self.project.vcsProjectHelper = vcsHelper
            self.project.vcsBasicHelper = vcs is None
            self.initMenu(self.project.vcsMenu)
            self.project.setDirty(True)
            self.project.saveProject()
        
        pdata_vcs = self.project.pdata["VCS"][:]
        pdata_vcsoptions = copy.deepcopy(self.project.pdata["VCSOPTIONS"])
        pdata_vcsother = copy.deepcopy(self.project.pdata["VCSOTHERDATA"])
        vcs = self.project.vcs
        vcsHelper = self.project.vcsProjectHelper
        vcsSystemsDict = e4App().getObject("PluginManager")\
            .getPluginDisplayStrings("version_control")
        vcsSystemsDisplay = QStringList()
        keys = vcsSystemsDict.keys()
        keys.sort()
        for key in keys:
            vcsSystemsDisplay.append(vcsSystemsDict[key])
        vcsSelected, ok = KQInputDialog.getItem(\
            None,
            self.trUtf8("Import Project"),
            self.trUtf8("Select version control system for the project"),
            vcsSystemsDisplay,
            0, False)
        if not ok:
            return
        for vcsSystem, vcsSystemDisplay in vcsSystemsDict.items():
            if vcsSystemDisplay == vcsSelected:
                break
        
        self.project.pdata["VCS"] = [vcsSystem]
        self.project.vcs = self.project.initVCS(vcsSystem)
        if self.project.vcs is not None:
            vcsdlg = self.project.vcs.vcsOptionsDialog(self.project, self.project.name, 1)
            if vcsdlg.exec_() == QDialog.Accepted:
                vcsDataDict = vcsdlg.getData()
                # edit VCS command options
                vcores = KQMessageBox.question(None,
                    self.trUtf8("Import Project"),
                    self.trUtf8("""Would you like to edit the VCS command options?"""),
                    QMessageBox.StandardButtons(\
                        QMessageBox.No | \
                        QMessageBox.Yes),
                    QMessageBox.No)
                if vcores == QMessageBox.Yes:
                    codlg = vcsCommandOptionsDialog(self.project.vcs)
                    if codlg.exec_() == QDialog.Accepted:
                        self.project.vcs.vcsSetOptions(codlg.getOptions())
                self.project.setDirty(True)
                self.project.vcs.vcsSetDataFromDict(vcsDataDict)
                self.project.saveProject()
                isVcsControlled = \
                    self.project.vcs.vcsImport(vcsDataDict, self.project.ppath)[1]
                if isVcsControlled:
                    # reopen the project
                    self.project.openProject(self.project.pfile)
                else:
                    # revert the changes to the local project 
                    # because the project dir is not a VCS directory
                    revertChanges()
            else:
                # revert the changes because user cancelled
                revertChanges()

    def _vcsUpdate(self):
        """
        Protected slot used to update the local project from the repository.
        """
        shouldReopen = self.vcs.vcsUpdate(self.project.ppath)
        if shouldReopen:
            res = KQMessageBox.information(None,
                self.trUtf8("Update"),
                self.trUtf8("""The project should be reread. Do this now?"""),
                QMessageBox.StandardButtons(\
                    QMessageBox.No | \
                    QMessageBox.Yes),
                QMessageBox.Yes)
            if res == QMessageBox.Yes:
                self.project.reopenProject()
        
    def _vcsCommit(self):
        """
        Protected slot used to commit changes to the local project to the repository.
        """
        if Preferences.getVCS("AutoSaveProject"):
            self.project.saveProject()
        if Preferences.getVCS("AutoSaveFiles"):
            self.project.saveAllScripts()
        self.vcs.vcsCommit(self.project.ppath, '')
        
    def _vcsRemove(self):
        """
        Protected slot used to remove the local project from the repository.
        
        Depending on the parameters set in the vcs object the project
        may be removed from the local disk as well.
        """
        res = KQMessageBox.warning(None,
            self.trUtf8("Remove project from repository"),
            self.trUtf8("Dou you really want to remove this project from"
                " the repository (and disk)?"),
            QMessageBox.StandardButtons(\
                QMessageBox.No | \
                QMessageBox.Yes),
            QMessageBox.No)
        if res == QMessageBox.Yes:
            self.vcs.vcsRemove(self.project.ppath, True)
            self._vcsCommit()
            if not os.path.exists(self.project.pfile):
                ppath = self.project.ppath
                self.setDirty(False)
                self.project.closeProject()
                shutil.rmtree(ppath, True)
        
    def _vcsCommandOptions(self):
        """
        Protected slot to edit the VCS command options.
        """
        codlg = vcsCommandOptionsDialog(self.vcs)
        if codlg.exec_() == QDialog.Accepted:
            self.vcs.vcsSetOptions(codlg.getOptions())
            self.project.setDirty(True)
        
    def _vcsLog(self):
        """
        Protected slot used to show the log of the local project.
        """
        self.vcs.vcsLog(self.project.ppath)
        
    def _vcsDiff(self):
        """
        Protected slot used to show the difference of the local project to the repository.
        """
        self.vcs.vcsDiff(self.project.ppath)
        
    def _vcsStatus(self):
        """
        Protected slot used to show the status of the local project.
        """
        self.vcs.vcsStatus(self.project.ppath)
        
    def _vcsTag(self):
        """
        Protected slot used to tag the local project in the repository.
        """
        self.vcs.vcsTag(self.project.ppath)
        
    def _vcsRevert(self):
        """
        Protected slot used to revert changes made to the local project.
        """
        self.vcs.vcsRevert(self.project.ppath)
        
    def _vcsSwitch(self):
        """
        Protected slot used to switch the local project to another tag/branch.
        """
        self.vcs.vcsSwitch(self.project.ppath)
        
    def _vcsMerge(self):
        """
        Protected slot used to merge changes of a tag/revision into the local project.
        """
        self.vcs.vcsMerge(self.project.ppath)
        
    def _vcsCleanup(self):
        """
        Protected slot used to cleanup the local project.
        """
        self.vcs.vcsCleanup(self.project.ppath)
        
    def _vcsCommand(self):
        """
        Protected slot used to execute an arbitrary vcs command.
        """
        self.vcs.vcsCommandLine(self.project.ppath)

    def _vcsInfoDisplay(self):
        """
        Protected slot called to show some vcs information.
        """
        info = self.vcs.vcsRepositoryInfos(self.project.ppath)
        dlg = VcsRepositoryInfoDialog(None, info)
        dlg.exec_()
