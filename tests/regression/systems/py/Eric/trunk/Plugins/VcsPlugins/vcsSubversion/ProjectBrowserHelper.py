# -*- coding: utf-8 -*-

# Copyright (c) 2005 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the VCS project browser helper for subversion.
"""

import os

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from KdeQt.KQApplication import e4App

from VCS.ProjectBrowserHelper import VcsProjectBrowserHelper

from Project.ProjectBrowserModel import ProjectBrowserFileItem

import UI.PixmapCache

class SvnProjectBrowserHelper(VcsProjectBrowserHelper):
    """
    Class implementing the VCS project browser helper for subversion.
    """
    def __init__(self, vcsObject, browserObject, projectObject, isTranslationsBrowser,
        parent = None, name = None):
        """
        Constructor
        
        @param vcsObject reference to the vcs object
        @param browserObject reference to the project browser object
        @param projectObject reference to the project object
        @param isTranslationsBrowser flag indicating, the helper is requested for the
            translations browser (this needs some special treatment)
        @param parent parent widget (QWidget)
        @param name name of this object (string or QString)
        """
        VcsProjectBrowserHelper.__init__(self, vcsObject, browserObject, projectObject,
            isTranslationsBrowser, parent, name)
    
    def showContextMenu(self, menu, standardItems):
        """
        Slot called before the context menu is shown. 
        
        It enables/disables the VCS menu entries depending on the overall 
        VCS status and the file status.
        
        @param menu reference to the menu to be shown
        @param standardItems array of standard items that need activation/deactivation
            depending on the overall VCS status
        """
        if unicode(self.browser.currentItem().data(1)) == self.vcs.vcsName():
            for act in self.vcsMenuActions:
                act.setEnabled(True)
            for act in self.vcsAddMenuActions:
                act.setEnabled(False)
            for act in standardItems:
                act.setEnabled(False)
            if not hasattr(self.browser.currentItem(), 'fileName'):
                self.blameAct.setEnabled(False)
        else:
            for act in self.vcsMenuActions:
                act.setEnabled(False)
            for act in self.vcsAddMenuActions:
                act.setEnabled(True)
            if 1 in self.browser.specialMenuEntries:
                try:
                    name = unicode(self.browser.currentItem().fileName())
                except AttributeError:
                    name = unicode(self.browser.currentItem().dirName())
                if not os.path.isdir(name):
                    self.vcsMenuAddTree.setEnabled(False)
            for act in standardItems:
                act.setEnabled(True)
    
    def showContextMenuMulti(self, menu, standardItems):
        """
        Slot called before the context menu (multiple selections) is shown. 
        
        It enables/disables the VCS menu entries depending on the overall 
        VCS status and the files status.
        
        @param menu reference to the menu to be shown
        @param standardItems array of standard items that need activation/deactivation
            depending on the overall VCS status
        """
        vcsName = self.vcs.vcsName()
        items = self.browser.getSelectedItems()
        vcsItems = 0
        # determine number of selected items under VCS control
        for itm in items:
            if unicode(itm.data(1)) == vcsName:
                vcsItems += 1
        
        if vcsItems > 0:
            if vcsItems != len(items):
                for act in self.vcsMultiMenuActions:
                    act.setEnabled(False)
            else:
                for act in self.vcsMultiMenuActions:
                    act.setEnabled(True)
            for act in self.vcsAddMultiMenuActions:
                act.setEnabled(False)
            for act in standardItems:
                act.setEnabled(False)
        else:
            for act in self.vcsMultiMenuActions:
                act.setEnabled(False)
            for act in self.vcsAddMultiMenuActions:
                act.setEnabled(True)
            if 1 in self.browser.specialMenuEntries and \
               self.__itemsHaveFiles(items):
                self.vcsMultiMenuAddTree.setEnabled(False)
            for act in standardItems:
                act.setEnabled(True)
    
    def showContextMenuDir(self, menu, standardItems):
        """
        Slot called before the context menu is shown. 
        
        It enables/disables the VCS menu entries depending on the overall 
        VCS status and the directory status.
        
        @param menu reference to the menu to be shown
        @param standardItems array of standard items that need activation/deactivation
            depending on the overall VCS status
        """
        if unicode(self.browser.currentItem().data(1)) == self.vcs.vcsName():
            for act in self.vcsDirMenuActions:
                act.setEnabled(True)
            for act in self.vcsAddDirMenuActions:
                act.setEnabled(False)
            for act in standardItems:
                act.setEnabled(False)
        else:
            for act in self.vcsDirMenuActions:
                act.setEnabled(False)
            for act in self.vcsAddDirMenuActions:
                act.setEnabled(True)
            for act in standardItems:
                act.setEnabled(True)
    
    def showContextMenuDirMulti(self, menu, standardItems):
        """
        Slot called before the context menu is shown. 
        
        It enables/disables the VCS menu entries depending on the overall 
        VCS status and the directory status.
        
        @param menu reference to the menu to be shown
        @param standardItems array of standard items that need activation/deactivation
            depending on the overall VCS status
        """
        vcsName = self.vcs.vcsName()
        items = self.browser.getSelectedItems()
        vcsItems = 0
        # determine number of selected items under VCS control
        for itm in items:
            if unicode(itm.data(1)) == vcsName:
                vcsItems += 1
        
        if vcsItems > 0:
            if vcsItems != len(items):
                for act in self.vcsDirMultiMenuActions:
                    act.setEnabled(False)
            else:
                for act in self.vcsDirMultiMenuActions:
                    act.setEnabled(True)
            for act in self.vcsAddDirMultiMenuActions:
                act.setEnabled(False)
            for act in standardItems:
                act.setEnabled(False)
        else:
            for act in self.vcsDirMultiMenuActions:
                act.setEnabled(False)
            for act in self.vcsAddDirMultiMenuActions:
                act.setEnabled(True)
            for act in standardItems:
                act.setEnabled(True)

    ############################################################################
    # Protected menu generation methods below
    ############################################################################

    def _addVCSMenu(self, mainMenu):
        """
        Protected method used to add the VCS menu to all project browsers.
        
        @param mainMenu reference to the menu to be amended
        """
        self.vcsMenuActions = []
        self.vcsAddMenuActions = []
        
        menu = QMenu(self.trUtf8("Version Control"))
        
        act = menu.addAction(
            UI.PixmapCache.getIcon(
                os.path.join("VcsPlugins", "vcsSubversion", "icons", "subversion.png")), 
            self.vcs.vcsName(), self._VCSInfoDisplay)
        font = act.font()
        font.setBold(True)
        act.setFont(font)
        menu.addSeparator()
        
        act = menu.addAction(UI.PixmapCache.getIcon("vcsUpdate.png"),
            self.trUtf8('Update from repository'), self._VCSUpdate)
        self.vcsMenuActions.append(act)
        act = menu.addAction(UI.PixmapCache.getIcon("vcsCommit.png"),
            self.trUtf8('Commit changes to repository...'), 
            self._VCSCommit)
        self.vcsMenuActions.append(act)
        menu.addSeparator()
        act = menu.addAction(UI.PixmapCache.getIcon("vcsAdd.png"),
            self.trUtf8('Add to repository'), 
            self._VCSAdd)
        self.vcsAddMenuActions.append(act)
        if 1 in self.browser.specialMenuEntries:
            self.vcsMenuAddTree = menu.addAction(UI.PixmapCache.getIcon("vcsAdd.png"),
                self.trUtf8('Add tree to repository'), 
                self._VCSAddTree)
            self.vcsAddMenuActions.append(self.vcsMenuAddTree)
        act = menu.addAction(UI.PixmapCache.getIcon("vcsRemove.png"),
            self.trUtf8('Remove from repository (and disk)'), 
            self._VCSRemove)
        self.vcsMenuActions.append(act)
        menu.addSeparator()
        act = menu.addAction(self.trUtf8('Copy in repository'), self.__SVNCopy)
        self.vcsMenuActions.append(act)
        act = menu.addAction(self.trUtf8('Move in repository'), self.__SVNMove)
        self.vcsMenuActions.append(act)
        if self.vcs.versionStr >= '1.5.0':
            menu.addSeparator()
            act = menu.addAction(self.trUtf8("Add to Changelist"), 
                self.__SVNAddToChangelist)
            self.vcsMenuActions.append(act)
            act = menu.addAction(self.trUtf8("Remove from Changelist"), 
                self.__SVNRemoveFromChangelist)
            self.vcsMenuActions.append(act)
        menu.addSeparator()
        act = menu.addAction(UI.PixmapCache.getIcon("vcsLog.png"),
            self.trUtf8('Show log'), self._VCSLog)
        self.vcsMenuActions.append(act)
        if self.vcs.versionStr >= '1.2.0':
            act = menu.addAction(UI.PixmapCache.getIcon("vcsLog.png"),
                self.trUtf8('Show limited log'), self.__SVNLogLimited)
            self.vcsMenuActions.append(act)
        act = menu.addAction(UI.PixmapCache.getIcon("vcsLog.png"),
            self.trUtf8('Show log browser'), self.__SVNLogBrowser)
        self.vcsMenuActions.append(act)
        menu.addSeparator()
        act = menu.addAction(UI.PixmapCache.getIcon("vcsStatus.png"),
            self.trUtf8('Show status'), self._VCSStatus)
        self.vcsMenuActions.append(act)
        menu.addSeparator()
        act = menu.addAction(UI.PixmapCache.getIcon("vcsDiff.png"),
            self.trUtf8('Show difference'), self._VCSDiff)
        self.vcsMenuActions.append(act)
        act = menu.addAction(UI.PixmapCache.getIcon("vcsDiff.png"),
            self.trUtf8('Show difference (extended)'), 
            self.__SVNExtendedDiff)
        self.vcsMenuActions.append(act)
        act = menu.addAction(UI.PixmapCache.getIcon("vcsDiff.png"),
            self.trUtf8('Show difference (URLs)'), 
            self.__SVNUrlDiff)
        self.vcsMenuActions.append(act)
        self.blameAct = menu.addAction(self.trUtf8('Show annotated file'), 
            self.__SVNBlame)
        self.vcsMenuActions.append(self.blameAct)
        menu.addSeparator()
        act = menu.addAction(UI.PixmapCache.getIcon("vcsRevert.png"),
            self.trUtf8('Revert changes'), self._VCSRevert)
        self.vcsMenuActions.append(act)
        act = menu.addAction(UI.PixmapCache.getIcon("vcsMerge.png"),
            self.trUtf8('Merge changes'), self._VCSMerge)
        self.vcsMenuActions.append(act)
        act = menu.addAction(self.trUtf8('Resolve conflict'), self.__SVNResolve)
        self.vcsMenuActions.append(act)
        if self.vcs.versionStr >= '1.2.0':
            menu.addSeparator()
            act = menu.addAction(UI.PixmapCache.getIcon("vcsLock.png"),
                self.trUtf8('Lock'), self.__SVNLock)
            self.vcsMenuActions.append(act)
            act = menu.addAction(UI.PixmapCache.getIcon("vcsUnlock.png"),
                self.trUtf8('Unlock'), self.__SVNUnlock)
            self.vcsMenuActions.append(act)
            act = menu.addAction(UI.PixmapCache.getIcon("vcsUnlock.png"),
                self.trUtf8('Break Lock'), self.__SVNBreakLock)
            self.vcsMenuActions.append(act)
            act = menu.addAction(UI.PixmapCache.getIcon("vcsUnlock.png"),
                self.trUtf8('Steal Lock'), self.__SVNStealLock)
            self.vcsMenuActions.append(act)
        menu.addSeparator()
        act = menu.addAction(self.trUtf8('Set Property'), self.__SVNSetProp)
        self.vcsMenuActions.append(act)
        act = menu.addAction(self.trUtf8('List Properties'), self.__SVNListProps)
        self.vcsMenuActions.append(act)
        act = menu.addAction(self.trUtf8('Delete Property'), self.__SVNDelProp)
        self.vcsMenuActions.append(act)
        menu.addSeparator()
        menu.addAction(self.trUtf8('Select all local file entries'),
                        self.browser.selectLocalEntries)
        menu.addAction(self.trUtf8('Select all versioned file entries'),
                        self.browser.selectVCSEntries)
        menu.addAction(self.trUtf8('Select all local directory entries'),
                        self.browser.selectLocalDirEntries)
        menu.addAction(self.trUtf8('Select all versioned directory entries'),
                        self.browser.selectVCSDirEntries)
        menu.addSeparator()
        menu.addAction(self.trUtf8("Configure..."), self.__SVNConfigure)
        
        mainMenu.addSeparator()
        mainMenu.addMenu(menu)
        self.menu = menu
        
    def _addVCSMenuMulti(self, mainMenu):
        """
        Protected method used to add the VCS menu for multi selection to all 
        project browsers.
        
        @param mainMenu reference to the menu to be amended
        """
        self.vcsMultiMenuActions = []
        self.vcsAddMultiMenuActions = []
        
        menu = QMenu(self.trUtf8("Version Control"))
        
        act = menu.addAction(
            UI.PixmapCache.getIcon(
                os.path.join("VcsPlugins", "vcsSubversion", "icons", "subversion.png")), 
            self.vcs.vcsName(), self._VCSInfoDisplay)
        font = act.font()
        font.setBold(True)
        act.setFont(font)
        menu.addSeparator()
        
        act = menu.addAction(UI.PixmapCache.getIcon("vcsUpdate.png"),
            self.trUtf8('Update from repository'), self._VCSUpdate)
        self.vcsMultiMenuActions.append(act)
        act = menu.addAction(UI.PixmapCache.getIcon("vcsCommit.png"),
            self.trUtf8('Commit changes to repository...'), 
            self._VCSCommit)
        self.vcsMultiMenuActions.append(act)
        menu.addSeparator()
        act = menu.addAction(UI.PixmapCache.getIcon("vcsAdd.png"),
            self.trUtf8('Add to repository'), self._VCSAdd)
        self.vcsAddMultiMenuActions.append(act)
        if 1 in self.browser.specialMenuEntries:
            self.vcsMultiMenuAddTree = \
                menu.addAction(UI.PixmapCache.getIcon("vcsAdd.png"),
                self.trUtf8('Add tree to repository'), self._VCSAddTree)
            self.vcsAddMultiMenuActions.append(self.vcsMultiMenuAddTree)
        act = menu.addAction(UI.PixmapCache.getIcon("vcsRemove.png"),
            self.trUtf8('Remove from repository (and disk)'), 
            self._VCSRemove)
        self.vcsMultiMenuActions.append(act)
        self.vcsRemoveMultiMenuItem = act
        if self.vcs.versionStr >= '1.5.0':
            menu.addSeparator()
            act = menu.addAction(self.trUtf8("Add to Changelist"), 
                self.__SVNAddToChangelist)
            self.vcsMenuActions.append(act)
            act = menu.addAction(self.trUtf8("Remove from Changelist"), 
                self.__SVNRemoveFromChangelist)
            self.vcsMenuActions.append(act)
        menu.addSeparator()
        act = menu.addAction(UI.PixmapCache.getIcon("vcsStatus.png"),
            self.trUtf8('Show status'), self._VCSStatus)
        self.vcsMultiMenuActions.append(act)
        menu.addSeparator()
        act = menu.addAction(UI.PixmapCache.getIcon("vcsDiff.png"),
            self.trUtf8('Show difference'), self._VCSDiff)
        self.vcsMultiMenuActions.append(act)
        act = menu.addAction(UI.PixmapCache.getIcon("vcsDiff.png"),
            self.trUtf8('Show difference (extended)'), 
            self.__SVNExtendedDiff)
        self.vcsMultiMenuActions.append(act)
        act = menu.addAction(UI.PixmapCache.getIcon("vcsDiff.png"),
            self.trUtf8('Show difference (URLs)'), 
            self.__SVNUrlDiff)
        self.vcsMultiMenuActions.append(act)
        menu.addSeparator()
        act = menu.addAction(UI.PixmapCache.getIcon("vcsRevert.png"),
            self.trUtf8('Revert changes'), self._VCSRevert)
        self.vcsMultiMenuActions.append(act)
        act = menu.addAction(self.trUtf8('Resolve conflict'), self.__SVNResolve)
        self.vcsMultiMenuActions.append(act)
        if self.vcs.versionStr >= '1.2.0':
            menu.addSeparator()
            act = menu.addAction(UI.PixmapCache.getIcon("vcsLock.png"),
                self.trUtf8('Lock'), self.__SVNLock)
            self.vcsMultiMenuActions.append(act)
            act = menu.addAction(UI.PixmapCache.getIcon("vcsUnlock.png"),
                self.trUtf8('Unlock'), self.__SVNUnlock)
            self.vcsMultiMenuActions.append(act)
            act = menu.addAction(UI.PixmapCache.getIcon("vcsUnlock.png"),
                self.trUtf8('Break Lock'), self.__SVNBreakLock)
            self.vcsMultiMenuActions.append(act)
            act = menu.addAction(UI.PixmapCache.getIcon("vcsUnlock.png"),
                self.trUtf8('Steal Lock'), self.__SVNStealLock)
            self.vcsMultiMenuActions.append(act)
        menu.addSeparator()
        act = menu.addAction(self.trUtf8('Set Property'), self.__SVNSetProp)
        self.vcsMultiMenuActions.append(act)
        act = menu.addAction(self.trUtf8('List Properties'), self.__SVNListProps)
        self.vcsMultiMenuActions.append(act)
        act = menu.addAction(self.trUtf8('Delete Property'), self.__SVNDelProp)
        self.vcsMultiMenuActions.append(act)
        menu.addSeparator()
        menu.addAction(self.trUtf8('Select all local file entries'),
                        self.browser.selectLocalEntries)
        menu.addAction(self.trUtf8('Select all versioned file entries'),
                        self.browser.selectVCSEntries)
        menu.addAction(self.trUtf8('Select all local directory entries'),
                        self.browser.selectLocalDirEntries)
        menu.addAction(self.trUtf8('Select all versioned directory entries'),
                        self.browser.selectVCSDirEntries)
        menu.addSeparator()
        menu.addAction(self.trUtf8("Configure..."), self.__SVNConfigure)
        
        mainMenu.addSeparator()
        mainMenu.addMenu(menu)
        self.menuMulti = menu
        
    def _addVCSMenuBack(self, mainMenu):
        """
        Protected method used to add the VCS menu to all project browsers.
        
        @param mainMenu reference to the menu to be amended
        """
        menu = QMenu(self.trUtf8("Version Control"))
        
        act = menu.addAction(
            UI.PixmapCache.getIcon(
                os.path.join("VcsPlugins", "vcsSubversion", "icons", "subversion.png")), 
            self.vcs.vcsName(), self._VCSInfoDisplay)
        font = act.font()
        font.setBold(True)
        act.setFont(font)
        menu.addSeparator()
        
        menu.addAction(self.trUtf8('Select all local file entries'),
                        self.browser.selectLocalEntries)
        menu.addAction(self.trUtf8('Select all versioned file entries'),
                        self.browser.selectVCSEntries)
        menu.addAction(self.trUtf8('Select all local directory entries'),
                        self.browser.selectLocalDirEntries)
        menu.addAction(self.trUtf8('Select all versioned directory entries'),
                        self.browser.selectVCSDirEntries)
        menu.addSeparator()
        menu.addAction(self.trUtf8("Configure..."), self.__SVNConfigure)
        
        mainMenu.addSeparator()
        mainMenu.addMenu(menu)
        self.menuBack = menu
        
    def _addVCSMenuDir(self, mainMenu):
        """
        Protected method used to add the VCS menu to all project browsers.
        
        @param mainMenu reference to the menu to be amended
        """
        if mainMenu is None:
            return
        
        self.vcsDirMenuActions = []
        self.vcsAddDirMenuActions = []
        
        menu = QMenu(self.trUtf8("Version Control"))
        
        act = menu.addAction(
            UI.PixmapCache.getIcon(
                os.path.join("VcsPlugins", "vcsSubversion", "icons", "subversion.png")), 
            self.vcs.vcsName(), self._VCSInfoDisplay)
        font = act.font()
        font.setBold(True)
        act.setFont(font)
        menu.addSeparator()
        
        act = menu.addAction(UI.PixmapCache.getIcon("vcsUpdate.png"),
            self.trUtf8('Update from repository'), self._VCSUpdate)
        self.vcsDirMenuActions.append(act)
        act = menu.addAction(UI.PixmapCache.getIcon("vcsCommit.png"),
            self.trUtf8('Commit changes to repository...'), 
            self._VCSCommit)
        self.vcsDirMenuActions.append(act)
        menu.addSeparator()
        act = menu.addAction(UI.PixmapCache.getIcon("vcsAdd.png"),
            self.trUtf8('Add to repository'), self._VCSAdd)
        self.vcsAddDirMenuActions.append(act)
        act = menu.addAction(UI.PixmapCache.getIcon("vcsRemove.png"),
            self.trUtf8('Remove from repository (and disk)'), 
            self._VCSRemove)
        self.vcsDirMenuActions.append(act)
        menu.addSeparator()
        act = menu.addAction(self.trUtf8('Copy in repository'), self.__SVNCopy)
        self.vcsDirMenuActions.append(act)
        act = menu.addAction(self.trUtf8('Move in repository'), self.__SVNMove)
        self.vcsDirMenuActions.append(act)
        if self.vcs.versionStr >= '1.5.0':
            menu.addSeparator()
            act = menu.addAction(self.trUtf8("Add to Changelist"), 
                self.__SVNAddToChangelist)
            self.vcsMenuActions.append(act)
            act = menu.addAction(self.trUtf8("Remove from Changelist"), 
                self.__SVNRemoveFromChangelist)
            self.vcsMenuActions.append(act)
        menu.addSeparator()
        act = menu.addAction(UI.PixmapCache.getIcon("vcsLog.png"),
            self.trUtf8('Show log'), self._VCSLog)
        self.vcsDirMenuActions.append(act)
        if self.vcs.versionStr >= '1.2.0':
            act = menu.addAction(UI.PixmapCache.getIcon("vcsLog.png"),
                self.trUtf8('Show limited log'), self.__SVNLogLimited)
            self.vcsDirMenuActions.append(act)
        act = menu.addAction(UI.PixmapCache.getIcon("vcsLog.png"),
            self.trUtf8('Show log browser'), self.__SVNLogBrowser)
        self.vcsDirMenuActions.append(act)
        menu.addSeparator()
        act = menu.addAction(UI.PixmapCache.getIcon("vcsStatus.png"),
            self.trUtf8('Show status'), self._VCSStatus)
        self.vcsDirMenuActions.append(act)
        menu.addSeparator()
        act = menu.addAction(UI.PixmapCache.getIcon("vcsDiff.png"),
            self.trUtf8('Show difference'), self._VCSDiff)
        self.vcsDirMenuActions.append(act)
        act = menu.addAction(UI.PixmapCache.getIcon("vcsDiff.png"),
            self.trUtf8('Show difference (extended)'), 
            self.__SVNExtendedDiff)
        self.vcsDirMenuActions.append(act)
        act = menu.addAction(UI.PixmapCache.getIcon("vcsDiff.png"),
            self.trUtf8('Show difference (URLs)'), 
            self.__SVNUrlDiff)
        self.vcsDirMenuActions.append(act)
        menu.addSeparator()
        act = menu.addAction(UI.PixmapCache.getIcon("vcsRevert.png"),
            self.trUtf8('Revert changes'), self._VCSRevert)
        self.vcsDirMenuActions.append(act)
        act = menu.addAction(UI.PixmapCache.getIcon("vcsMerge.png"),
            self.trUtf8('Merge changes'), self._VCSMerge)
        self.vcsDirMenuActions.append(act)
        act = menu.addAction(self.trUtf8('Resolve conflict'), self.__SVNResolve)
        self.vcsDirMenuActions.append(act)
        menu.addSeparator()
        act = menu.addAction(self.trUtf8('Set Property'), self.__SVNSetProp)
        self.vcsDirMenuActions.append(act)
        act = menu.addAction(self.trUtf8('List Properties'), self.__SVNListProps)
        self.vcsDirMenuActions.append(act)
        act = menu.addAction(self.trUtf8('Delete Property'), self.__SVNDelProp)
        self.vcsDirMenuActions.append(act)
        menu.addSeparator()
        menu.addAction(self.trUtf8('Select all local file entries'),
                        self.browser.selectLocalEntries)
        menu.addAction(self.trUtf8('Select all versioned file entries'),
                        self.browser.selectVCSEntries)
        menu.addAction(self.trUtf8('Select all local directory entries'),
                        self.browser.selectLocalDirEntries)
        menu.addAction(self.trUtf8('Select all versioned directory entries'),
                        self.browser.selectVCSDirEntries)
        menu.addSeparator()
        menu.addAction(self.trUtf8("Configure..."), self.__SVNConfigure)
        
        mainMenu.addSeparator()
        mainMenu.addMenu(menu)
        self.menuDir = menu
        
    def _addVCSMenuDirMulti(self, mainMenu):
        """
        Protected method used to add the VCS menu to all project browsers.
        
        @param mainMenu reference to the menu to be amended
        """
        if mainMenu is None:
            return
        
        self.vcsDirMultiMenuActions = []
        self.vcsAddDirMultiMenuActions = []
        
        menu = QMenu(self.trUtf8("Version Control"))
        
        act = menu.addAction(
            UI.PixmapCache.getIcon(
                os.path.join("VcsPlugins", "vcsSubversion", "icons", "subversion.png")), 
            self.vcs.vcsName(), self._VCSInfoDisplay)
        font = act.font()
        font.setBold(True)
        act.setFont(font)
        menu.addSeparator()
        
        act = menu.addAction(UI.PixmapCache.getIcon("vcsUpdate.png"),
            self.trUtf8('Update from repository'), self._VCSUpdate)
        self.vcsDirMultiMenuActions.append(act)
        act = menu.addAction(UI.PixmapCache.getIcon("vcsCommit.png"),
            self.trUtf8('Commit changes to repository...'),    
            self._VCSCommit)
        self.vcsDirMultiMenuActions.append(act)
        menu.addSeparator()
        act = menu.addAction(UI.PixmapCache.getIcon("vcsAdd.png"),
            self.trUtf8('Add to repository'), self._VCSAdd)
        self.vcsAddDirMultiMenuActions.append(act)
        act = menu.addAction(UI.PixmapCache.getIcon("vcsRemove.png"),
            self.trUtf8('Remove from repository (and disk)'), 
            self._VCSRemove)
        self.vcsDirMultiMenuActions.append(act)
        if self.vcs.versionStr >= '1.5.0':
            menu.addSeparator()
            act = menu.addAction(self.trUtf8("Add to Changelist"), 
                self.__SVNAddToChangelist)
            self.vcsMenuActions.append(act)
            act = menu.addAction(self.trUtf8("Remove from Changelist"), 
                self.__SVNRemoveFromChangelist)
            self.vcsMenuActions.append(act)
        menu.addSeparator()
        act = menu.addAction(UI.PixmapCache.getIcon("vcsStatus.png"),
            self.trUtf8('Show status'), self._VCSStatus)
        self.vcsDirMultiMenuActions.append(act)
        menu.addSeparator()
        act = menu.addAction(UI.PixmapCache.getIcon("vcsDiff.png"),
            self.trUtf8('Show difference'), self._VCSDiff)
        self.vcsDirMultiMenuActions.append(act)
        act = menu.addAction(UI.PixmapCache.getIcon("vcsDiff.png"),
            self.trUtf8('Show difference (extended)'), 
            self.__SVNExtendedDiff)
        self.vcsDirMultiMenuActions.append(act)
        act = menu.addAction(UI.PixmapCache.getIcon("vcsDiff.png"),
            self.trUtf8('Show difference (URLs)'), 
            self.__SVNUrlDiff)
        self.vcsDirMultiMenuActions.append(act)
        menu.addSeparator()
        act = menu.addAction(UI.PixmapCache.getIcon("vcsRevert.png"),
            self.trUtf8('Revert changes'), self._VCSRevert)
        self.vcsDirMenuActions.append(act)
        act = menu.addAction(UI.PixmapCache.getIcon("vcsMerge.png"),
            self.trUtf8('Merge changes'), self._VCSMerge)
        self.vcsDirMenuActions.append(act)
        act = menu.addAction(self.trUtf8('Resolve conflict'), self.__SVNResolve)
        self.vcsDirMultiMenuActions.append(act)
        menu.addSeparator()
        act = menu.addAction(self.trUtf8('Set Property'), self.__SVNSetProp)
        self.vcsDirMultiMenuActions.append(act)
        act = menu.addAction(self.trUtf8('List Properties'), self.__SVNListProps)
        self.vcsDirMultiMenuActions.append(act)
        act = menu.addAction(self.trUtf8('Delete Property'), self.__SVNDelProp)
        self.vcsDirMultiMenuActions.append(act)
        menu.addSeparator()
        menu.addAction(self.trUtf8('Select all local file entries'),
                        self.browser.selectLocalEntries)
        menu.addAction(self.trUtf8('Select all versioned file entries'),
                        self.browser.selectVCSEntries)
        menu.addAction(self.trUtf8('Select all local directory entries'),
                        self.browser.selectLocalDirEntries)
        menu.addAction(self.trUtf8('Select all versioned directory entries'),
                        self.browser.selectVCSDirEntries)
        menu.addSeparator()
        menu.addAction(self.trUtf8("Configure..."), self.__SVNConfigure)
        
        mainMenu.addSeparator()
        mainMenu.addMenu(menu)
        self.menuDirMulti = menu
    
    ############################################################################
    # Menu handling methods below
    ############################################################################
    
    def __SVNCopy(self):
        """
        Private slot called by the context menu to copy the selected file.
        """
        itm = self.browser.currentItem()
        try:
            fn = unicode(itm.fileName())
        except AttributeError:
            fn = unicode(itm.dirName())
        self.vcs.svnCopy(fn, self.project)
        
    def __SVNMove(self):
        """
        Private slot called by the context menu to move the selected file.
        """
        itm = self.browser.currentItem()
        try:
            fn = unicode(itm.fileName())
        except AttributeError:
            fn = unicode(itm.dirName())
        isFile = os.path.isfile(fn)
        movefiles = self.browser.project.getFiles(fn)
        if self.vcs.vcsMove(fn, self.project):
            if isFile:
                self.browser.emit(SIGNAL('closeSourceWindow'), fn)
            else:
                for mf in movefiles:
                    self.browser.emit(SIGNAL('closeSourceWindow'), mf)
        
    def __SVNResolve(self):
        """
        Private slot called by the context menu to resolve conflicts of a file.
        """
        names = []
        for itm in self.browser.getSelectedItems():
            try:
                names.append(unicode(itm.fileName()))
            except AttributeError:
                names.append(unicode(itm.dirName()))
        self.vcs.svnResolve(names)
        
    def __SVNListProps(self):
        """
        Private slot called by the context menu to list the subversion properties of
        a file.
        """
        names = []
        for itm in self.browser.getSelectedItems():
            try:
                names.append(unicode(itm.fileName()))
            except AttributeError:
                names.append(unicode(itm.dirName()))
        self.vcs.svnListProps(names)
        
    def __SVNSetProp(self):
        """
        Private slot called by the context menu to set a subversion property of a file.
        """
        names = []
        for itm in self.browser.getSelectedItems():
            try:
                names.append(unicode(itm.fileName()))
            except AttributeError:
                names.append(unicode(itm.dirName()))
        self.vcs.svnSetProp(names)
        
    def __SVNDelProp(self):
        """
        Private slot called by the context menu to delete a subversion property of a file.
        """
        names = []
        for itm in self.browser.getSelectedItems():
            try:
                names.append(unicode(itm.fileName()))
            except AttributeError:
                names.append(unicode(itm.dirName()))
        self.vcs.svnDelProp(names)
        
    def __SVNExtendedDiff(self):
        """
        Private slot called by the context menu to show the difference of a file to
        the repository.
        
        This gives the chance to enter the revisions to compare.
        """
        names = []
        for itm in self.browser.getSelectedItems():
            try:
                names.append(unicode(itm.fileName()))
            except AttributeError:
                names.append(unicode(itm.dirName()))
        self.vcs.svnExtendedDiff(names)
        
    def __SVNUrlDiff(self):
        """
        Private slot called by the context menu to show the difference of a file of
        two repository URLs.
        
        This gives the chance to enter the repository URLs to compare.
        """
        names = []
        for itm in self.browser.getSelectedItems():
            try:
                names.append(unicode(itm.fileName()))
            except AttributeError:
                names.append(unicode(itm.dirName()))
        self.vcs.svnUrlDiff(names)
        
    def __SVNLogLimited(self):
        """
        Private slot called by the context menu to show the limited log of a file.
        """
        itm = self.browser.currentItem()
        try:
            fn = unicode(itm.fileName())
        except AttributeError:
            fn = unicode(itm.dirName())
        self.vcs.svnLogLimited(fn)
        
    def __SVNLogBrowser(self):
        """
        Private slot called by the context menu to show the log browser for a file.
        """
        itm = self.browser.currentItem()
        try:
            fn = unicode(itm.fileName())
        except AttributeError:
            fn = unicode(itm.dirName())
        self.vcs.svnLogBrowser(fn)
        
    def __SVNBlame(self):
        """
        Private slot called by the context menu to show the blame of a file.
        """
        itm = self.browser.currentItem()
        fn = unicode(itm.fileName())
        self.vcs.svnBlame(fn)
        
    def __SVNLock(self):
        """
        Private slot called by the context menu to lock files in the repository.
        """
        names = []
        for itm in self.browser.getSelectedItems():
            try:
                names.append(unicode(itm.fileName()))
            except AttributeError:
                names.append(unicode(itm.dirName()))
        self.vcs.svnLock(names)
        
    def __SVNUnlock(self):
        """
        Private slot called by the context menu to unlock files in the repository.
        """
        names = []
        for itm in self.browser.getSelectedItems():
            try:
                names.append(unicode(itm.fileName()))
            except AttributeError:
                names.append(unicode(itm.dirName()))
        self.vcs.svnUnlock(names)
        
    def __SVNBreakLock(self):
        """
        Private slot called by the context menu to break lock files in the repository.
        """
        names = []
        for itm in self.browser.getSelectedItems():
            try:
                names.append(unicode(itm.fileName()))
            except AttributeError:
                names.append(unicode(itm.dirName()))
        self.vcs.svnUnlock(names, breakIt = True)
        
    def __SVNStealLock(self):
        """
        Private slot called by the context menu to steal lock files in the repository.
        """
        names = []
        for itm in self.browser.getSelectedItems():
            try:
                names.append(unicode(itm.fileName()))
            except AttributeError:
                names.append(unicode(itm.dirName()))
        self.vcs.svnLock(names, stealIt = True)
        
    def __SVNConfigure(self):
        """
        Private method to open the configuration dialog.
        """
        e4App().getObject("UserInterface").showPreferences("zzz_subversionPage")
        
    def __SVNAddToChangelist(self):
        """
        Private slot called by the context menu to add files to a changelist.
        """
        names = []
        for itm in self.browser.getSelectedItems():
            try:
                names.append(unicode(itm.fileName()))
            except AttributeError:
                names.append(unicode(itm.dirName()))
        self.vcs.svnAddToChangelist(names)
        
    def __SVNRemoveFromChangelist(self):
        """
        Private slot called by the context menu to remove files from their changelist.
        """
        names = []
        for itm in self.browser.getSelectedItems():
            try:
                names.append(unicode(itm.fileName()))
            except AttributeError:
                names.append(unicode(itm.dirName()))
        self.vcs.svnRemoveFromChangelist(names)

    ############################################################################
    # Some private utility methods below
    ############################################################################
    
    def __itemsHaveFiles(self, items):
        """
        Private method to check, if items contain file type items.
        
        @param items items to check (list of QTreeWidgetItems)
        @return flag indicating items contain file type items (boolean)
        """
        for itm in items:
            if isinstance(itm, ProjectBrowserFileItem):
                return True
        return False
