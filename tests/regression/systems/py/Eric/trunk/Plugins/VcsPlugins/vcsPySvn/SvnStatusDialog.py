# -*- coding: utf-8 -*-

# Copyright (c) 2003 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a dialog to show the output of the svn status command process.
"""

import types
import os

import pysvn

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from KdeQt import KQMessageBox
from KdeQt.KQApplication import e4App

from SvnConst import svnStatusMap
from SvnDialogMixin import SvnDialogMixin
from Ui_SvnStatusDialog import Ui_SvnStatusDialog

import Preferences

class SvnStatusDialog(QWidget, SvnDialogMixin, Ui_SvnStatusDialog):
    """
    Class implementing a dialog to show the output of the svn status command process.
    """
    def __init__(self, vcs, parent = None):
        """
        Constructor
        
        @param vcs reference to the vcs object
        @param parent parent widget (QWidget)
        """
        QWidget.__init__(self, parent)
        self.setupUi(self)
        SvnDialogMixin.__init__(self)
        
        self.__changelistColumn = 0
        self.__statusColumn = 1
        self.__propStatusColumn = 2
        self.__lockinfoColumn = 6
        self.__pathColumn = 11
        self.__lastColumn = self.statusList.columnCount()
        
        self.refreshButton = \
            self.buttonBox.addButton(self.trUtf8("Refresh"), QDialogButtonBox.ActionRole)
        self.refreshButton.setToolTip(self.trUtf8("Press to refresh the status display"))
        self.refreshButton.setEnabled(False)
        self.buttonBox.button(QDialogButtonBox.Close).setEnabled(False)
        self.buttonBox.button(QDialogButtonBox.Cancel).setDefault(True)
        
        self.vcs = vcs
        self.connect(self.vcs, SIGNAL("committed()"), self.__committed)
        
        self.statusList.headerItem().setText(self.__lastColumn, "")
        self.statusList.header().setSortIndicator(self.__pathColumn, Qt.AscendingOrder)
        if pysvn.svn_version < (1, 5, 0) or pysvn.version < (1, 6, 0):
            self.statusList.header().hideSection(self.__changelistColumn)
        
        self.menuactions = []
        self.menu = QMenu()
        self.menuactions.append(self.menu.addAction(\
            self.trUtf8("Commit changes to repository..."), self.__commit))
        self.menu.addSeparator()
        self.menuactions.append(self.menu.addAction(\
            self.trUtf8("Add to repository"), self.__add))
        self.menuactions.append(self.menu.addAction(\
            self.trUtf8("Revert changes"), self.__revert))
        if pysvn.svn_version >= (1, 5, 0) and pysvn.version >= (1, 6, 0):
            self.menu.addSeparator()
            self.menuactions.append(self.menu.addAction(
                self.trUtf8("Add to Changelist"), self.__addToChangelist))
            self.menuactions.append(self.menu.addAction(
                self.trUtf8("Remove from Changelist"), self.__removeFromChangelist))
        if self.vcs.versionStr >= '1.2.0':
            self.menu.addSeparator()
            self.menuactions.append(self.menu.addAction(self.trUtf8("Lock"),
                self.__lock))
            self.menuactions.append(self.menu.addAction(self.trUtf8("Unlock"),
                self.__unlock))
            self.menuactions.append(self.menu.addAction(self.trUtf8("Break lock"),
                self.__breakLock))
            self.menuactions.append(self.menu.addAction(self.trUtf8("Steal lock"),
                self.__stealLock))
        self.menu.addSeparator()
        self.menuactions.append(self.menu.addAction(self.trUtf8("Adjust column sizes"),
            self.__resizeColumns))
        for act in self.menuactions:
            act.setEnabled(False)
        
        self.statusList.setContextMenuPolicy(Qt.CustomContextMenu)
        self.connect(self.statusList, 
                     SIGNAL("customContextMenuRequested(const QPoint &)"),
                     self.__showContextMenu)
        
        self.modifiedIndicators = QStringList()
        self.modifiedIndicators.append(\
            self.trUtf8(svnStatusMap[pysvn.wc_status_kind.added]))
        self.modifiedIndicators.append(\
            self.trUtf8(svnStatusMap[pysvn.wc_status_kind.deleted]))
        self.modifiedIndicators.append(\
            self.trUtf8(svnStatusMap[pysvn.wc_status_kind.modified]))
        
        self.unversionedIndicators = QStringList()
        self.unversionedIndicators.append(\
            self.trUtf8(svnStatusMap[pysvn.wc_status_kind.unversioned]))
        
        self.lockedIndicators = QStringList()
        self.lockedIndicators.append(self.trUtf8('locked'))
        
        self.stealBreakLockIndicators = QStringList()
        self.stealBreakLockIndicators.append(self.trUtf8('other lock'))
        self.stealBreakLockIndicators.append(self.trUtf8('stolen lock'))
        self.stealBreakLockIndicators.append(self.trUtf8('broken lock'))
        
        self.unlockedIndicators = QStringList()
        self.unlockedIndicators.append(self.trUtf8('not locked'))
        
        self.lockinfo = {
            ' ' : self.trUtf8('not locked'),
            'L' : self.trUtf8('locked'),
            'O' : self.trUtf8('other lock'),
            'S' : self.trUtf8('stolen lock'),
            'B' : self.trUtf8('broken lock'),
        }
        self.yesno = [self.trUtf8('no'), self.trUtf8('yes')]
        
        self.client = self.vcs.getClient()
        self.client.callback_cancel = \
            self._clientCancelCallback
        self.client.callback_get_login = \
            self._clientLoginCallback
        self.client.callback_ssl_server_trust_prompt = \
            self._clientSslServerTrustPromptCallback
        
        self.show()
        QApplication.processEvents()
        
    def __resort(self):
        """
        Private method to resort the tree.
        """
        self.statusList.sortItems(self.statusList.sortColumn(), 
            self.statusList.header().sortIndicatorOrder())
        
    def __resizeColumns(self):
        """
        Private method to resize the list columns.
        """
        self.statusList.header().resizeSections(QHeaderView.ResizeToContents)
        self.statusList.header().setStretchLastSection(True)
        
    def __generateItem(self, changelist, status, propStatus, locked, history, switched, 
                       lockinfo, uptodate, revision, change, author, path):
        """
        Private method to generate a status item in the status list.
        
        @param changelist name of the changelist (string)
        @param status text status (pysvn.wc_status_kind)
        @param propStatus property status (pysvn.wc_status_kind)
        @param locked locked flag (boolean)
        @param history history flag (boolean)
        @param switched switched flag (boolean)
        @param lockinfo lock indicator (string)
        @param uptodate up to date flag (boolean)
        @param revision revision (integer)
        @param change revision of last change (integer)
        @param author author of the last change (string or QString)
        @param path path of the file or directory (string or QString)
        """
        itm = QTreeWidgetItem(self.statusList, 
            QStringList() \
            << changelist \
            << self.trUtf8(svnStatusMap[status]) \
            << self.trUtf8(svnStatusMap[propStatus]) \
            << self.yesno[locked] \
            << self.yesno[history] \
            << self.yesno[switched] \
            << self.lockinfo[lockinfo] \
            << self.yesno[uptodate] \
            << "%7s" % str(revision) \
            << "%7s" % str(change) \
            << author \
            << path
        )
        
        itm.setTextAlignment(0, Qt.AlignLeft)
        itm.setTextAlignment(1, Qt.AlignHCenter)
        itm.setTextAlignment(2, Qt.AlignHCenter)
        itm.setTextAlignment(3, Qt.AlignHCenter)
        itm.setTextAlignment(4, Qt.AlignHCenter)
        itm.setTextAlignment(5, Qt.AlignHCenter)
        itm.setTextAlignment(6, Qt.AlignHCenter)
        itm.setTextAlignment(7, Qt.AlignHCenter)
        itm.setTextAlignment(8, Qt.AlignRight)
        itm.setTextAlignment(9, Qt.AlignRight)
        itm.setTextAlignment(10, Qt.AlignLeft)
        itm.setTextAlignment(11, Qt.AlignLeft)
        
    def start(self, fn):
        """
        Public slot to start the svn status command.
        
        @param fn filename(s)/directoryname(s) to show the status of
            (string or list of strings)
        """
        self.errorGroup.hide()
        
        QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
        QApplication.processEvents()
        
        self.args = fn
        
        self.setWindowTitle(self.trUtf8('Subversion Status'))
        self.activateWindow()
        self.raise_()
        
        if type(fn) is types.ListType:
            self.dname, fnames = self.vcs.splitPathList(fn)
        else:
            self.dname, fname = self.vcs.splitPath(fn)
            fnames = [fname]
        
        opts = self.vcs.options['global'] + self.vcs.options['status']
        verbose = "--verbose" in opts
        recurse = "--non-recursive" not in opts
        ignore = True # "--ignore" not in opts
        update = "--show-updates" in opts
        
        locker = QMutexLocker(self.vcs.vcsExecutionMutex)
        cwd = os.getcwd()
        os.chdir(self.dname)
        try:
            for name in fnames:
                # step 1: determine changelists and their files
                changelistsDict = {}
                if hasattr(self.client, 'get_changelist'):
                    if recurse:
                        depth = pysvn.depth.infinity
                    else:
                        depth = pysvn.depth.immediate
                    changelists = self.client.get_changelist(name, depth = depth)
                    for entry in changelists:
                        changelistsDict[entry[0]] = entry[1]
                self.statusList.setColumnHidden(self.__changelistColumn, 
                                                len(changelistsDict) == 0)
                
                # step 2: determine status of files
                allFiles = self.client.status(name, recurse = recurse, get_all = verbose, 
                                              ignore = ignore, update = update)
                counter = 0
                for file in allFiles:
                    uptodate = True
                    if file.repos_text_status != pysvn.wc_status_kind.none:
                        uptodate = uptodate and file.repos_text_status == file.text_status
                    if file.repos_prop_status != pysvn.wc_status_kind.none:
                        uptodate = uptodate and file.repos_prop_status == file.prop_status
                    
                    lockState = " "
                    if file.entry is not None and \
                       hasattr(file.entry, 'lock_token') and \
                       file.entry.lock_token is not None:
                        lockState = "L"
                    if hasattr(file, 'repos_lock') and update:
                        if lockState == "L" and file.repos_lock is None:
                            lockState = "B"
                        elif lockState == " " and file.repos_lock is not None:
                            lockState = "O"
                        elif lockState == "L" and file.repos_lock is not None and \
                             file.entry.lock_token != file.repos_lock["token"]:
                            lockState = "S"
                    
                    if file.path in changelistsDict:
                        changelist = changelistsDict[file.path]
                    else:
                        changelist = ""
                    
                    self.__generateItem(\
                        changelist, 
                        file.text_status, 
                        file.prop_status,
                        file.is_locked,
                        file.is_copied,
                        file.is_switched,
                        lockState,
                        uptodate,
                        file.entry and file.entry.revision.number or "",
                        file.entry and file.entry.commit_revision.number or "",
                        file.entry and file.entry.commit_author or "",
                        file.path
                    )
                    counter += 1
                    if counter == 30:
                        # check for cancel every 30 items
                        counter = 0
                        if self._clientCancelCallback():
                            break
                if self._clientCancelCallback():
                    break
        except pysvn.ClientError, e:
            self.__showError(e.args[0]+'\n')
        locker.unlock()
        self.__finish()
        os.chdir(cwd)
        
    def __finish(self):
        """
        Private slot called when the process finished or the user pressed the button.
        """
        QApplication.restoreOverrideCursor()
        
        self.buttonBox.button(QDialogButtonBox.Close).setEnabled(True)
        self.buttonBox.button(QDialogButtonBox.Cancel).setEnabled(False)
        self.buttonBox.button(QDialogButtonBox.Close).setDefault(True)
        
        self.refreshButton.setEnabled(True)
        
        for act in self.menuactions:
            act.setEnabled(True)
        
        self.statusList.doItemsLayout()
        self.__resizeColumns()
        self.__resort()
        
        self._cancel()
        
    def on_buttonBox_clicked(self, button):
        """
        Private slot called by a button of the button box clicked.
        
        @param button button that was clicked (QAbstractButton)
        """
        if button == self.buttonBox.button(QDialogButtonBox.Close):
            self.close()
        elif button == self.buttonBox.button(QDialogButtonBox.Cancel):
            self.__finish()
        elif button == self.refreshButton:
            self.on_refreshButton_clicked()
        
    @pyqtSignature("")
    def on_refreshButton_clicked(self):
        """
        Private slot to refresh the status display.
        """
        self.buttonBox.button(QDialogButtonBox.Close).setEnabled(False)
        self.buttonBox.button(QDialogButtonBox.Cancel).setEnabled(True)
        self.buttonBox.button(QDialogButtonBox.Cancel).setDefault(True)
        
        self.refreshButton.setEnabled(False)
        
        for act in self.menuactions:
            act.setEnabled(False)
        
        self.statusList.clear()
        
        self.shouldCancel = False
        self.start(self.args)
        
    def __showError(self, msg):
        """
        Private slot to show an error message.
        
        @param msg error message to show (string or QString)
        """
        self.errorGroup.show()
        self.errors.insertPlainText(msg)
        self.errors.ensureCursorVisible()
    
    ############################################################################
    ## Context menu handling methods
    ############################################################################
    
    def __showContextMenu(self, coord):
        """
        Protected slot to show the context menu of the status list.
        
        @param coord the position of the mouse pointer (QPoint)
        """
        self.menu.popup(self.mapToGlobal(coord))
        
    def __commit(self):
        """
        Private slot to handle the Commit context menu entry.
        """
        names = [os.path.join(self.dname, unicode(itm.text(self.__pathColumn))) \
                 for itm in self.__getModifiedItems()]
        if not names:
            KQMessageBox.information(self,
                self.trUtf8("Commit"),
                self.trUtf8("""There are no uncommitted changes available/selected."""))
            return
        
        if Preferences.getVCS("AutoSaveFiles"):
            vm = e4App().getObject("ViewManager")
            for name in names:
                vm.saveEditor(name)
        self.vcs.vcsCommit(names, '')
       
    def __committed(self):
        """
        Private slot called after the commit has finished.
        """
        if self.isVisible():
            self.on_refreshButton_clicked()
            self.vcs.checkVCSStatus()
        
    def __add(self):
        """
        Private slot to handle the Add context menu entry.
        """
        names = [os.path.join(self.dname, unicode(itm.text(self.__pathColumn))) \
                 for itm in self.__getUnversionedItems()]
        if not names:
            KQMessageBox.information(self,
                self.trUtf8("Add"),
                self.trUtf8("""There are no unversioned entries available/selected."""))
            return
        
        self.vcs.vcsAdd(names)
        self.on_refreshButton_clicked()
        
        project = e4App().getObject("Project")
        for name in names:
            project.getModel().updateVCSStatus(name)

    def __revert(self):
        """
        Private slot to handle the Revert context menu entry.
        """
        names = [os.path.join(self.dname, unicode(itm.text(self.__pathColumn))) \
                 for itm in self.__getModifiedItems()]
        if not names:
            KQMessageBox.information(self,
                self.trUtf8("Revert"),
                self.trUtf8("""There are no uncommitted changes available/selected."""))
            return
        
        self.vcs.vcsRevert(names)
        self.on_refreshButton_clicked()
        self.vcs.checkVCSStatus()
        
    def __lock(self):
        """
        Private slot to handle the Lock context menu entry.
        """
        names = [os.path.join(self.dname, unicode(itm.text(self.__pathColumn))) \
                 for itm in self.__getLockActionItems(self.unlockedIndicators)]
        if not names:
            KQMessageBox.information(self,
                self.trUtf8("Lock"),
                self.trUtf8("""There are no unlocked files available/selected."""))
            return
        
        self.vcs.svnLock(names, parent = self)
        self.on_refreshButton_clicked()
        
    def __unlock(self):
        """
        Private slot to handle the Unlock context menu entry.
        """
        names = [os.path.join(self.dname, unicode(itm.text(self.__pathColumn))) \
                 for itm in self.__getLockActionItems(self.lockedIndicators)]
        if not names:
            KQMessageBox.information(self,
                self.trUtf8("Unlock"),
                self.trUtf8("""There are no locked files available/selected."""))
            return
        
        self.vcs.svnUnlock(names, parent = self)
        self.on_refreshButton_clicked()
        
    def __breakLock(self):
        """
        Private slot to handle the Break Lock context menu entry.
        """
        names = [os.path.join(self.dname, unicode(itm.text(self.__pathColumn))) \
                 for itm in self.__getLockActionItems(self.stealBreakLockIndicators)]
        if not names:
            KQMessageBox.information(self,
                self.trUtf8("Break Lock"),
                self.trUtf8("""There are no locked files available/selected."""))
            return
        
        self.vcs.svnUnlock(names, parent = self, breakIt = True)
        self.on_refreshButton_clicked()

    def __stealLock(self):
        """
        Private slot to handle the Break Lock context menu entry.
        """
        names = [os.path.join(self.dname, unicode(itm.text(self.__pathColumn))) \
                 for itm in self.__getLockActionItems(self.stealBreakLockIndicators)]
        if not names:
            KQMessageBox.information(self,
                self.trUtf8("Steal Lock"),
                self.trUtf8("""There are no locked files available/selected."""))
            return
        
        self.vcs.svnLock(names, parent=self, stealIt=True)
        self.on_refreshButton_clicked()

    def __addToChangelist(self):
        """
        Private slot to add entries to a changelist.
        """
        names = [os.path.join(self.dname, unicode(itm.text(self.__pathColumn))) \
                 for itm in self.__getNonChangelistItems()]
        if not names:
            KQMessageBox.information(self,
                self.trUtf8("Remove from Changelist"),
                self.trUtf8(
                    """There are no files available/selected not """
                    """belonging to a changelist."""
                )
            )
            return
        self.vcs.svnAddToChangelist(names)
        self.on_refreshButton_clicked()

    def __removeFromChangelist(self):
        """
        Private slot to remove entries from their changelists.
        """
        names = [os.path.join(self.dname, unicode(itm.text(self.__pathColumn))) \
                 for itm in self.__getChangelistItems()]
        if not names:
            KQMessageBox.information(self,
                self.trUtf8("Remove from Changelist"),
                self.trUtf8(
                    """There are no files available/selected belonging to a changelist."""
                )
            )
            return
        self.vcs.svnRemoveFromChangelist(names)
        self.on_refreshButton_clicked()

    def __getModifiedItems(self):
        """
        Private method to retrieve all entries, that have a modified status.
        
        @return list of all items with a modified status
        """
        modifiedItems = []
        for itm in self.statusList.selectedItems():
            if self.modifiedIndicators.contains(itm.text(self.__statusColumn)) or \
               self.modifiedIndicators.contains(itm.text(self.__propStatusColumn)):
                modifiedItems.append(itm)
        return modifiedItems
        
    def __getUnversionedItems(self):
        """
        Private method to retrieve all entries, that have an unversioned status.
        
        @return list of all items with an unversioned status
        """
        unversionedItems = []
        for itm in self.statusList.selectedItems():
            if self.unversionedIndicators.contains(itm.text(self.__statusColumn)):
                unversionedItems.append(itm)
        return unversionedItems
        
    def __getLockActionItems(self, indicators):
        """
        Private method to retrieve all entries, that have a locked status.
        
        @return list of all items with a locked status
        """
        lockitems = []
        for itm in self.statusList.selectedItems():
            if indicators.contains(itm.text(self.__lockinfoColumn)):
                lockitems.append(itm)
        return lockitems
        
    def __getChangelistItems(self):
        """
        Private method to retrieve all entries, that are members of a changelist.
        
        @return list of all items belonging to a changelist
        """
        clitems = []
        for itm in self.statusList.selectedItems():
            if not itm.text(self.__changelistColumn).isEmpty():
                clitems.append(itm)
        return clitems
        
    def __getNonChangelistItems(self):
        """
        Private method to retrieve all entries, that are not members of a changelist.
        
        @return list of all items not belonging to a changelist
        """
        clitems = []
        for itm in self.statusList.selectedItems():
            if itm.text(self.__changelistColumn).isEmpty():
                clitems.append(itm)
        return clitems
