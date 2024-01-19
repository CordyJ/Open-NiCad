# -*- coding: utf-8 -*-

# Copyright (c) 2005 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the VCS project helper for Subversion.
"""

import os

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from KdeQt.KQApplication import e4App

from VCS.ProjectHelper import VcsProjectHelper

from E4Gui.E4Action import E4Action

import UI.PixmapCache

class SvnProjectHelper(VcsProjectHelper):
    """
    Class implementing the VCS project helper for Subversion.
    """
    def __init__(self, vcsObject, projectObject, parent = None, name = None):
        """
        Constructor
        
        @param vcsObject reference to the vcs object
        @param projectObject reference to the project object
        @param parent parent widget (QWidget)
        @param name name of this object (string or QString)
        """
        VcsProjectHelper.__init__(self, vcsObject, projectObject, parent, name)
        
    def getActions(self):
        """
        Public method to get a list of all actions.
        
        @return list of all actions (list of E4Action)
        """
        return self.actions[:]
        
    def initActions(self):
        """
        Public method to generate the action objects.
        """
        self.vcsNewAct = E4Action(self.trUtf8('New from repository'),
                UI.PixmapCache.getIcon("vcsCheckout.png"),
                self.trUtf8('&New from repository...'), 0, 0, self, 'subversion_new')
        self.vcsNewAct.setStatusTip(self.trUtf8(
            'Create a new project from the VCS repository'
        ))
        self.vcsNewAct.setWhatsThis(self.trUtf8(
            """<b>New from repository</b>"""
            """<p>This creates a new local project from the VCS repository.</p>"""
        ))
        self.connect(self.vcsNewAct, SIGNAL('triggered()'), self._vcsCheckout)
        self.actions.append(self.vcsNewAct)
        
        self.vcsUpdateAct = E4Action(self.trUtf8('Update from repository'),
                UI.PixmapCache.getIcon("vcsUpdate.png"),
                self.trUtf8('&Update from repository'), 0, 0, self,
                'subversion_update')
        self.vcsUpdateAct.setStatusTip(self.trUtf8(
            'Update the local project from the VCS repository'
        ))
        self.vcsUpdateAct.setWhatsThis(self.trUtf8(
            """<b>Update from repository</b>"""
            """<p>This updates the local project from the VCS repository.</p>"""
        ))
        self.connect(self.vcsUpdateAct, SIGNAL('triggered()'), self._vcsUpdate)
        self.actions.append(self.vcsUpdateAct)
        
        self.vcsCommitAct = E4Action(self.trUtf8('Commit changes to repository'),
                UI.PixmapCache.getIcon("vcsCommit.png"),
                self.trUtf8('&Commit changes to repository...'), 0, 0, self,
                'subversion_commit')
        self.vcsCommitAct.setStatusTip(self.trUtf8(
            'Commit changes to the local project to the VCS repository'
        ))
        self.vcsCommitAct.setWhatsThis(self.trUtf8(
            """<b>Commit changes to repository</b>"""
            """<p>This commits changes to the local project to the VCS repository.</p>"""
        ))
        self.connect(self.vcsCommitAct, SIGNAL('triggered()'), self._vcsCommit)
        self.actions.append(self.vcsCommitAct)
        
        self.vcsAddAct = E4Action(self.trUtf8('Add to repository'),
                UI.PixmapCache.getIcon("vcsAdd.png"),
                self.trUtf8('&Add to repository...'), 0, 0, self, 'subversion_add')
        self.vcsAddAct.setStatusTip(self.trUtf8(
            'Add the local project to the VCS repository'
        ))
        self.vcsAddAct.setWhatsThis(self.trUtf8(
            """<b>Add to repository</b>"""
            """<p>This adds (imports) the local project to the VCS repository.</p>"""
        ))
        self.connect(self.vcsAddAct, SIGNAL('triggered()'), self._vcsImport)
        self.actions.append(self.vcsAddAct)
        
        self.vcsRemoveAct = E4Action(self.trUtf8('Remove from repository (and disk)'),
                UI.PixmapCache.getIcon("vcsRemove.png"),
                self.trUtf8('&Remove from repository (and disk)'),
                0, 0, self, 'subversion_remove')
        self.vcsRemoveAct.setStatusTip(self.trUtf8(
            'Remove the local project from the VCS repository (and  disk)'
        ))
        self.vcsRemoveAct.setWhatsThis(self.trUtf8(
            """<b>Remove from repository</b>"""
            """<p>This removes the local project from the VCS repository"""
            """ (and disk).</p>"""
        ))
        self.connect(self.vcsRemoveAct, SIGNAL('triggered()'), self._vcsRemove)
        self.actions.append(self.vcsRemoveAct)
        
        self.vcsLogAct = E4Action(self.trUtf8('Show log'),
                UI.PixmapCache.getIcon("vcsLog.png"),
                self.trUtf8('Show &log'),
                0, 0, self, 'subversion_log')
        self.vcsLogAct.setStatusTip(self.trUtf8(
            'Show the log of the local project'
        ))
        self.vcsLogAct.setWhatsThis(self.trUtf8(
            """<b>Show log</b>"""
            """<p>This shows the log of the local project.</p>"""
        ))
        self.connect(self.vcsLogAct, SIGNAL('triggered()'), self._vcsLog)
        self.actions.append(self.vcsLogAct)
        
        self.svnLogLimitedAct = E4Action(self.trUtf8('Show limited log'),
                UI.PixmapCache.getIcon("vcsLog.png"),
                self.trUtf8('Show limited log'),
                0, 0, self, 'subversion_log_limited')
        self.svnLogLimitedAct.setStatusTip(self.trUtf8(
            'Show a limited log of the local project'
        ))
        self.svnLogLimitedAct.setWhatsThis(self.trUtf8(
            """<b>Show limited log</b>"""
            """<p>This shows the log of the local project limited to a selectable"""
            """ number of entries.</p>"""
        ))
        self.connect(self.svnLogLimitedAct, SIGNAL('triggered()'), self.__svnLogLimited)
        self.actions.append(self.svnLogLimitedAct)
        
        self.svnLogBrowserAct = E4Action(self.trUtf8('Show log browser'),
                UI.PixmapCache.getIcon("vcsLog.png"),
                self.trUtf8('Show log browser'),
                0, 0, self, 'subversion_log_browser')
        self.svnLogBrowserAct.setStatusTip(self.trUtf8(
            'Show a dialog to browse the log of the local project'
        ))
        self.svnLogBrowserAct.setWhatsThis(self.trUtf8(
            """<b>Show log browser</b>"""
            """<p>This shows a dialog to browse the log of the local project."""
            """ A limited number of entries is shown first. More can be"""
            """ retrieved later on.</p>"""
        ))
        self.connect(self.svnLogBrowserAct, SIGNAL('triggered()'), self.__svnLogBrowser)
        self.actions.append(self.svnLogBrowserAct)
        
        self.vcsDiffAct = E4Action(self.trUtf8('Show difference'),
                UI.PixmapCache.getIcon("vcsDiff.png"),
                self.trUtf8('Show &difference'),
                0, 0, self, 'subversion_diff')
        self.vcsDiffAct.setStatusTip(self.trUtf8(
            'Show the difference of the local project to the repository'
        ))
        self.vcsDiffAct.setWhatsThis(self.trUtf8(
            """<b>Show difference</b>"""
            """<p>This shows the difference of the local project to the repository.</p>"""
        ))
        self.connect(self.vcsDiffAct, SIGNAL('triggered()'), self._vcsDiff)
        self.actions.append(self.vcsDiffAct)
        
        self.svnExtDiffAct = E4Action(self.trUtf8('Show difference (extended)'),
                UI.PixmapCache.getIcon("vcsDiff.png"),
                self.trUtf8('Show difference (extended)'),
                0, 0, self, 'subversion_extendeddiff')
        self.svnExtDiffAct.setStatusTip(self.trUtf8(
            'Show the difference of revisions of the project to the repository'
        ))
        self.svnExtDiffAct.setWhatsThis(self.trUtf8(
            """<b>Show difference (extended)</b>"""
            """<p>This shows the difference of selectable revisions of the project.</p>"""
        ))
        self.connect(self.svnExtDiffAct, SIGNAL('triggered()'), self.__svnExtendedDiff)
        self.actions.append(self.svnExtDiffAct)
        
        self.svnUrlDiffAct = E4Action(self.trUtf8('Show difference (URLs)'),
                UI.PixmapCache.getIcon("vcsDiff.png"),
                self.trUtf8('Show difference (URLs)'),
                0, 0, self, 'subversion_urldiff')
        self.svnUrlDiffAct.setStatusTip(self.trUtf8(
            'Show the difference of the project between two repository URLs'
        ))
        self.svnUrlDiffAct.setWhatsThis(self.trUtf8(
            """<b>Show difference (URLs)</b>"""
            """<p>This shows the difference of the project between"""
            """ two repository URLs.</p>"""
        ))
        self.connect(self.svnUrlDiffAct, SIGNAL('triggered()'), self.__svnUrlDiff)
        self.actions.append(self.svnUrlDiffAct)
        
        self.vcsStatusAct = E4Action(self.trUtf8('Show status'),
                UI.PixmapCache.getIcon("vcsStatus.png"),
                self.trUtf8('Show &status'),
                0, 0, self, 'subversion_status')
        self.vcsStatusAct.setStatusTip(self.trUtf8(
            'Show the status of the local project'
        ))
        self.vcsStatusAct.setWhatsThis(self.trUtf8(
            """<b>Show status</b>"""
            """<p>This shows the status of the local project.</p>"""
        ))
        self.connect(self.vcsStatusAct, SIGNAL('triggered()'), self._vcsStatus)
        self.actions.append(self.vcsStatusAct)
        
        self.vcsTagAct = E4Action(self.trUtf8('Tag in repository'), 
                UI.PixmapCache.getIcon("vcsTag.png"),
                self.trUtf8('&Tag in repository...'),
                0, 0, self, 'subversion_tag')
        self.vcsTagAct.setStatusTip(self.trUtf8(
            'Tag the local project in the repository'
        ))
        self.vcsTagAct.setWhatsThis(self.trUtf8(
            """<b>Tag in repository</b>"""
            """<p>This tags the local project in the repository.</p>"""
        ))
        self.connect(self.vcsTagAct, SIGNAL('triggered()'), self._vcsTag)
        self.actions.append(self.vcsTagAct)
        
        self.vcsExportAct = E4Action(self.trUtf8('Export from repository'), 
                UI.PixmapCache.getIcon("vcsExport.png"),
                self.trUtf8('&Export from repository...'),
                0, 0, self, 'subversion_export')
        self.vcsExportAct.setStatusTip(self.trUtf8(
            'Export a project from the repository'
        ))
        self.vcsExportAct.setWhatsThis(self.trUtf8(
            """<b>Export from repository</b>"""
            """<p>This exports a project from the repository.</p>"""
        ))
        self.connect(self.vcsExportAct, SIGNAL('triggered()'), self._vcsExport)
        self.actions.append(self.vcsExportAct)
        
        self.vcsPropsAct = E4Action(self.trUtf8('Command options'),
                self.trUtf8('Command &options...'),0,0,self,
                'subversion_options')
        self.vcsPropsAct.setStatusTip(self.trUtf8('Show the VCS command options'))
        self.vcsPropsAct.setWhatsThis(self.trUtf8(
            """<b>Command options...</b>"""
            """<p>This shows a dialog to edit the VCS command options.</p>"""
        ))
        self.connect(self.vcsPropsAct, SIGNAL('triggered()'), self._vcsCommandOptions)
        self.actions.append(self.vcsPropsAct)
        
        self.vcsRevertAct = E4Action(self.trUtf8('Revert changes'),
                UI.PixmapCache.getIcon("vcsRevert.png"),
                self.trUtf8('Re&vert changes'),
                0, 0, self, 'subversion_revert')
        self.vcsRevertAct.setStatusTip(self.trUtf8(
            'Revert all changes made to the local project'
        ))
        self.vcsRevertAct.setWhatsThis(self.trUtf8(
            """<b>Revert changes</b>"""
            """<p>This reverts all changes made to the local project.</p>"""
        ))
        self.connect(self.vcsRevertAct, SIGNAL('triggered()'), self._vcsRevert)
        self.actions.append(self.vcsRevertAct)
        
        self.vcsMergeAct = E4Action(self.trUtf8('Merge'),
                UI.PixmapCache.getIcon("vcsMerge.png"),
                self.trUtf8('Mer&ge changes...'),
                0, 0, self, 'subversion_merge')
        self.vcsMergeAct.setStatusTip(self.trUtf8(
            'Merge changes of a tag/revision into the local project'
        ))
        self.vcsMergeAct.setWhatsThis(self.trUtf8(
            """<b>Merge</b>"""
            """<p>This merges changes of a tag/revision into the local project.</p>"""
        ))
        self.connect(self.vcsMergeAct, SIGNAL('triggered()'), self._vcsMerge)
        self.actions.append(self.vcsMergeAct)
        
        self.vcsSwitchAct = E4Action(self.trUtf8('Switch'),
                UI.PixmapCache.getIcon("vcsSwitch.png"),
                self.trUtf8('S&witch...'),
                0, 0, self, 'subversion_switch')
        self.vcsSwitchAct.setStatusTip(self.trUtf8(
            'Switch the local copy to another tag/branch'
        ))
        self.vcsSwitchAct.setWhatsThis(self.trUtf8(
            """<b>Switch</b>"""
            """<p>This switches the local copy to another tag/branch.</p>"""
        ))
        self.connect(self.vcsSwitchAct, SIGNAL('triggered()'), self._vcsSwitch)
        self.actions.append(self.vcsSwitchAct)
        
        self.vcsResolveAct = E4Action(self.trUtf8('Resolve conflicts'),
                self.trUtf8('Resolve con&flicts'),
                0, 0, self, 'subversion_resolve')
        self.vcsResolveAct.setStatusTip(self.trUtf8(
            'Resolve all conflicts of the local project'
        ))
        self.vcsResolveAct.setWhatsThis(self.trUtf8(
            """<b>Resolve conflicts</b>"""
            """<p>This resolves all conflicts of the local project.</p>"""
        ))
        self.connect(self.vcsResolveAct, SIGNAL('triggered()'), self.__svnResolve)
        self.actions.append(self.vcsResolveAct)
        
        self.vcsCleanupAct = E4Action(self.trUtf8('Cleanup'),
                self.trUtf8('Cleanu&p'),
                0, 0, self, 'subversion_cleanup')
        self.vcsCleanupAct.setStatusTip(self.trUtf8(
            'Cleanup the local project'
        ))
        self.vcsCleanupAct.setWhatsThis(self.trUtf8(
            """<b>Cleanup</b>"""
            """<p>This performs a cleanup of the local project.</p>"""
        ))
        self.connect(self.vcsCleanupAct, SIGNAL('triggered()'), self._vcsCleanup)
        self.actions.append(self.vcsCleanupAct)
        
        self.vcsCommandAct = E4Action(self.trUtf8('Execute command'),
                self.trUtf8('E&xecute command...'),
                0, 0, self, 'subversion_command')
        self.vcsCommandAct.setStatusTip(self.trUtf8(
            'Execute an arbitrary VCS command'
        ))
        self.vcsCommandAct.setWhatsThis(self.trUtf8(
            """<b>Execute command</b>"""
            """<p>This opens a dialog to enter an arbitrary VCS command.</p>"""
        ))
        self.connect(self.vcsCommandAct, SIGNAL('triggered()'), self._vcsCommand)
        self.actions.append(self.vcsCommandAct)
        
        self.svnTagListAct = E4Action(self.trUtf8('List tags'), 
                self.trUtf8('List tags...'),
                0, 0, self, 'subversion_list_tags')
        self.svnTagListAct.setStatusTip(self.trUtf8(
            'List tags of the project'
        ))
        self.svnTagListAct.setWhatsThis(self.trUtf8(
            """<b>List tags</b>"""
            """<p>This lists the tags of the project.</p>"""
        ))
        self.connect(self.svnTagListAct, SIGNAL('triggered()'), self.__svnTagList)
        self.actions.append(self.svnTagListAct)
        
        self.svnBranchListAct = E4Action(self.trUtf8('List branches'), 
                self.trUtf8('List branches...'),
                0, 0, self, 'subversion_list_branches')
        self.svnBranchListAct.setStatusTip(self.trUtf8(
            'List branches of the project'
        ))
        self.svnBranchListAct.setWhatsThis(self.trUtf8(
            """<b>List branches</b>"""
            """<p>This lists the branches of the project.</p>"""
        ))
        self.connect(self.svnBranchListAct, SIGNAL('triggered()'), self.__svnBranchList)
        self.actions.append(self.svnBranchListAct)
        
        self.svnListAct = E4Action(self.trUtf8('List repository contents'), 
                self.trUtf8('List repository contents...'),
                0, 0, self, 'subversion_contents')
        self.svnListAct.setStatusTip(self.trUtf8(
            'Lists the contents of the repository'
        ))
        self.svnListAct.setWhatsThis(self.trUtf8(
            """<b>List repository contents</b>"""
            """<p>This lists the contents of the repository.</p>"""
        ))
        self.connect(self.svnListAct, SIGNAL('triggered()'), self.__svnTagList)
        self.actions.append(self.svnListAct)
        
        self.svnPropSetAct = E4Action(self.trUtf8('Set Property'),
                self.trUtf8('Set Property...'),
                0, 0, self, 'subversion_property_set')
        self.svnPropSetAct.setStatusTip(self.trUtf8(
            'Set a property for the project files'
        ))
        self.svnPropSetAct.setWhatsThis(self.trUtf8(
            """<b>Set Property</b>"""
            """<p>This sets a property for the project files.</p>"""
        ))
        self.connect(self.svnPropSetAct, SIGNAL('triggered()'), self.__svnPropSet)
        self.actions.append(self.svnPropSetAct)
        
        self.svnPropListAct = E4Action(self.trUtf8('List Properties'),
                self.trUtf8('List Properties...'),
                0, 0, self, 'subversion_property_list')
        self.svnPropListAct.setStatusTip(self.trUtf8(
            'List properties of the project files'
        ))
        self.svnPropListAct.setWhatsThis(self.trUtf8(
            """<b>List Properties</b>"""
            """<p>This lists the properties of the project files.</p>"""
        ))
        self.connect(self.svnPropListAct, SIGNAL('triggered()'), self.__svnPropList)
        self.actions.append(self.svnPropListAct)
        
        self.svnPropDelAct = E4Action(self.trUtf8('Delete Property'),
                self.trUtf8('Delete Property...'),
                0, 0, self, 'subversion_property_delete')
        self.svnPropDelAct.setStatusTip(self.trUtf8(
            'Delete a property for the project files'
        ))
        self.svnPropDelAct.setWhatsThis(self.trUtf8(
            """<b>Delete Property</b>"""
            """<p>This deletes a property for the project files.</p>"""
        ))
        self.connect(self.svnPropDelAct, SIGNAL('triggered()'), self.__svnPropDel)
        self.actions.append(self.svnPropDelAct)
        
        self.svnRelocateAct = E4Action(self.trUtf8('Relocate'),
                UI.PixmapCache.getIcon("vcsSwitch.png"),
                self.trUtf8('Relocate...'),
                0, 0, self, 'subversion_relocate')
        self.svnRelocateAct.setStatusTip(self.trUtf8(
            'Relocate the working copy to a new repository URL'
        ))
        self.svnRelocateAct.setWhatsThis(self.trUtf8(
            """<b>Relocate</b>"""
            """<p>This relocates the working copy to a new repository URL.</p>"""
        ))
        self.connect(self.svnRelocateAct, SIGNAL('triggered()'), self.__svnRelocate)
        self.actions.append(self.svnRelocateAct)
        
        self.svnRepoBrowserAct = E4Action(self.trUtf8('Repository Browser'),
                UI.PixmapCache.getIcon("vcsRepoBrowser.png"),
                self.trUtf8('Repository Browser...'),
                0, 0, self, 'subversion_repo_browser')
        self.svnRepoBrowserAct.setStatusTip(self.trUtf8(
            'Show the Repository Browser dialog'
        ))
        self.svnRepoBrowserAct.setWhatsThis(self.trUtf8(
            """<b>Repository Browser</b>"""
            """<p>This shows the Repository Browser dialog.</p>"""
        ))
        self.connect(self.svnRepoBrowserAct, SIGNAL('triggered()'), self.__svnRepoBrowser)
        self.actions.append(self.svnRepoBrowserAct)
        
        self.svnConfigAct = E4Action(self.trUtf8('Configure'),
                self.trUtf8('Configure...'),
                0, 0, self, 'subversion_configure')
        self.svnConfigAct.setStatusTip(self.trUtf8(
            'Show the configuration dialog with the Subversion page selected'
        ))
        self.svnConfigAct.setWhatsThis(self.trUtf8(
            """<b>Configure</b>"""
            """<p>Show the configuration dialog with the Subversion page selected.</p>"""
        ))
        self.connect(self.svnConfigAct, SIGNAL('triggered()'), self.__svnConfigure)
        self.actions.append(self.svnConfigAct)
    
    def initMenu(self, menu):
        """
        Public method to generate the VCS menu.
        
        @param menu reference to the menu to be populated (QMenu)
        """
        menu.clear()
        
        act = menu.addAction(
            UI.PixmapCache.getIcon(
                os.path.join("VcsPlugins", "vcsSubversion", "icons", "subversion.png")), 
            self.vcs.vcsName(), self._vcsInfoDisplay)
        font = act.font()
        font.setBold(True)
        act.setFont(font)
        menu.addSeparator()
        
        menu.addAction(self.vcsUpdateAct)
        menu.addAction(self.vcsCommitAct)
        menu.addSeparator()
        menu.addAction(self.vcsNewAct)
        menu.addAction(self.vcsExportAct)
        menu.addSeparator()
        menu.addAction(self.vcsAddAct)
        menu.addAction(self.vcsRemoveAct)
        menu.addSeparator()
        menu.addAction(self.vcsTagAct)
        if self.vcs.otherData["standardLayout"]:
            menu.addAction(self.svnTagListAct)
            menu.addAction(self.svnBranchListAct)
        else:
            menu.addAction(self.svnListAct)
        menu.addSeparator()
        menu.addAction(self.vcsLogAct)
        if self.vcs.versionStr >= '1.2.0':
            menu.addAction(self.svnLogLimitedAct)
        menu.addAction(self.svnLogBrowserAct)
        menu.addSeparator()
        menu.addAction(self.vcsStatusAct)
        menu.addSeparator()
        menu.addAction(self.vcsDiffAct)
        menu.addAction(self.svnExtDiffAct)
        menu.addAction(self.svnUrlDiffAct)
        menu.addSeparator()
        menu.addAction(self.vcsRevertAct)
        menu.addAction(self.vcsMergeAct)
        menu.addAction(self.vcsResolveAct)
        menu.addSeparator()
        menu.addAction(self.svnRelocateAct)
        menu.addAction(self.vcsSwitchAct)
        menu.addSeparator()
        menu.addAction(self.svnPropSetAct)
        menu.addAction(self.svnPropListAct)
        menu.addAction(self.svnPropDelAct)
        menu.addSeparator()
        menu.addAction(self.vcsCleanupAct)
        menu.addSeparator()
        menu.addAction(self.vcsCommandAct)
        menu.addAction(self.svnRepoBrowserAct)
        menu.addSeparator()
        menu.addAction(self.vcsPropsAct)
        menu.addSeparator()
        menu.addAction(self.svnConfigAct)
    
    def __svnResolve(self):
        """
        Private slot used to resolve conflicts of the local project.
        """
        self.vcs.svnResolve(self.project.ppath)
        
    def __svnPropList(self):
        """
        Private slot used to list the properties of the project files.
        """
        self.vcs.svnListProps(self.project.ppath, True)
        
    def __svnPropSet(self):
        """
        Private slot used to set a property for the project files.
        """
        self.vcs.svnSetProp(self.project.ppath, True)
        
    def __svnPropDel(self):
        """
        Private slot used to delete a property for the project files.
        """
        self.vcs.svnDelProp(self.project.ppath, True)
        
    def __svnTagList(self):
        """
        Private slot used to list the tags of the project.
        """
        self.vcs.svnListTagBranch(self.project.ppath, True)
        
    def __svnBranchList(self):
        """
        Private slot used to list the branches of the project.
        """
        self.vcs.svnListTagBranch(self.project.ppath, False)
        
    def __svnExtendedDiff(self):
        """
        Private slot used to perform a svn diff with the selection of revisions.
        """
        self.vcs.svnExtendedDiff(self.project.ppath)
        
    def __svnUrlDiff(self):
        """
        Private slot used to perform a svn diff with the selection of repository URLs.
        """
        self.vcs.svnUrlDiff(self.project.ppath)
        
    def __svnLogLimited(self):
        """
        Private slot used to perform a svn log --limit.
        """
        self.vcs.svnLogLimited(self.project.ppath)
        
    def __svnLogBrowser(self):
        """
        Private slot used to browse the log of the current project.
        """
        self.vcs.svnLogBrowser(self.project.ppath)
        
    def __svnRelocate(self):
        """
        Private slot used to relocate the working copy to a new repository URL.
        """
        self.vcs.svnRelocate(self.project.ppath)
        
    def __svnRepoBrowser(self):
        """
        Private slot to open the repository browser.
        """
        self.vcs.svnRepoBrowser(projectPath = self.project.ppath)
        
    def __svnConfigure(self):
        """
        Private method to open the configuration dialog.
        """
        e4App().getObject("UserInterface").showPreferences("zzz_subversionPage")
