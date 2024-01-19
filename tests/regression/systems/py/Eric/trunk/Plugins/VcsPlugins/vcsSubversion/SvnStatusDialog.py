# -*- coding: utf-8 -*-

# Copyright (c) 2003 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a dialog to show the output of the svn status command process.
"""

import types
import os

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from KdeQt import KQMessageBox
from KdeQt.KQApplication import e4App

from Ui_SvnStatusDialog import Ui_SvnStatusDialog

import Preferences

class SvnStatusDialog(QWidget, Ui_SvnStatusDialog):
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
        
        self.process = None
        self.vcs = vcs
        self.connect(self.vcs, SIGNAL("committed()"), self.__committed)
        
        self.statusList.headerItem().setText(self.__lastColumn, "")
        self.statusList.header().setSortIndicator(self.__pathColumn, Qt.AscendingOrder)
        if self.vcs.versionStr < '1.5.0':
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
        if self.vcs.versionStr >= '1.5.0':
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
        self.modifiedIndicators.append(self.trUtf8('added'))
        self.modifiedIndicators.append(self.trUtf8('deleted'))
        self.modifiedIndicators.append(self.trUtf8('modified'))
        
        self.unversionedIndicators = QStringList()
        self.unversionedIndicators.append(self.trUtf8('unversioned'))
        
        self.lockedIndicators = QStringList()
        self.lockedIndicators.append(self.trUtf8('locked'))
        
        self.stealBreakLockIndicators = QStringList()
        self.stealBreakLockIndicators.append(self.trUtf8('other lock'))
        self.stealBreakLockIndicators.append(self.trUtf8('stolen lock'))
        self.stealBreakLockIndicators.append(self.trUtf8('broken lock'))
        
        self.unlockedIndicators = QStringList()
        self.unlockedIndicators.append(self.trUtf8('not locked'))
        
        self.status = {
            ' ' : self.trUtf8('normal'),
            'A' : self.trUtf8('added'),
            'D' : self.trUtf8('deleted'),
            'M' : self.trUtf8('modified'),
            'R' : self.trUtf8('replaced'),
            'C' : self.trUtf8('conflict'),
            'X' : self.trUtf8('external'),
            'I' : self.trUtf8('ignored'),
            '?' : self.trUtf8('unversioned'),
            '!' : self.trUtf8('missing'),
            '~' : self.trUtf8('type error')
        }
        self.propStatus = {
            ' ' : self.trUtf8('normal'),
            'M' : self.trUtf8('modified'),
            'C' : self.trUtf8('conflict')
        }
        self.locked = {
            ' ' : self.trUtf8('no'),
            'L' : self.trUtf8('yes')
        }
        self.history = {
            ' ' : self.trUtf8('no'),
            '+' : self.trUtf8('yes')
        }
        self.switched = {
            ' ' : self.trUtf8('no'),
            'S' : self.trUtf8('yes')
        }
        self.lockinfo = {
            ' ' : self.trUtf8('not locked'),
            'K' : self.trUtf8('locked'),
            'O' : self.trUtf8('other lock'),
            'T' : self.trUtf8('stolen lock'),
            'B' : self.trUtf8('broken lock'),
        }
        self.uptodate = {
            ' ' : self.trUtf8('yes'),
            '*' : self.trUtf8('no')
        }
        
        self.rx_status = \
            QRegExp('(.{8})\\s+([0-9-]+)\\s+([0-9?]+)\\s+([\\w?]+)\\s+(.+)\\s*')
            # flags (8 anything), revision, changed rev, author, path
        self.rx_status2 = \
            QRegExp('(.{8})\\s+(.+)\\s*')
            # flags (8 anything), path
        self.rx_changelist = \
            QRegExp('--- \\S+ .([\\w\\s]+).:\\s+')
            # three dashes, Changelist (translated), quote, changelist name, quote, :
        
        self.__nonverbose = True
        
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
        
    def __generateItem(self, status, propStatus, locked, history, switched, lockinfo,
                       uptodate, revision, change, author, path):
        """
        Private method to generate a status item in the status list.
        
        @param status status indicator (string)
        @param propStatus property status indicator (string)
        @param locked locked indicator (string)
        @param history history indicator (string)
        @param switched switched indicator (string)
        @param lockinfo lock indicator (string)
        @param uptodate up to date indicator (string)
        @param revision revision string (string or QString)
        @param change revision of last change (string or QString)
        @param author author of the last change (string or QString)
        @param path path of the file or directory (string or QString)
        """
        if self.__nonverbose and \
           status == " " and \
           propStatus == " " and \
           locked == " " and \
           history == " " and \
           switched == " " and \
           lockinfo == " " and \
           uptodate == " " and \
           self.currentChangelist == "":
            return
        
        itm = QTreeWidgetItem(self.statusList, 
            QStringList() \
            << self.currentChangelist \
            << self.status[status] \
            << self.propStatus[propStatus] \
            << self.locked[locked] \
            << self.history[history] \
            << self.switched[switched] \
            << self.lockinfo[lockinfo] \
            << self.uptodate[uptodate] \
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
        
    def closeEvent(self, e):
        """
        Private slot implementing a close event handler.
        
        @param e close event (QCloseEvent)
        """
        if self.process is not None and \
           self.process.state() != QProcess.NotRunning:
            self.process.terminate()
            QTimer.singleShot(2000, self.process, SLOT('kill()'))
            self.process.waitForFinished(3000)
        
        e.accept()
        
    def start(self, fn):
        """
        Public slot to start the svn status command.
        
        @param fn filename(s)/directoryname(s) to show the status of
            (string or list of strings)
        """
        self.errorGroup.hide()
        self.intercept = False
        self.args = fn
        self.currentChangelist = ""
        self.changelistFound = False
        
        if self.process:
            self.process.kill()
        else:
            self.process = QProcess()
            self.connect(self.process, SIGNAL('finished(int, QProcess::ExitStatus)'),
                self.__procFinished)
            self.connect(self.process, SIGNAL('readyReadStandardOutput()'),
                self.__readStdout)
            self.connect(self.process, SIGNAL('readyReadStandardError()'),
                self.__readStderr)
        
        args = QStringList()
        args.append('status')
        self.vcs.addArguments(args, self.vcs.options['global'])
        self.vcs.addArguments(args, self.vcs.options['status'])
        if '--verbose' not in self.vcs.options['global'] and \
           '--verbose' not in self.vcs.options['status']:
            args.append('--verbose')
            self.__nonverbose = True
        else:
            self.__nonverbose = False
        if '--show-updates' in self.vcs.options['status'] or \
           '-u' in self.vcs.options['status']:
            self.activateWindow()
            self.raise_()
        if type(fn) is types.ListType:
            self.dname, fnames = self.vcs.splitPathList(fn)
            self.vcs.addArguments(args, fnames)
        else:
            self.dname, fname = self.vcs.splitPath(fn)
            args.append(fname)
        
        self.process.setWorkingDirectory(self.dname)
        
        self.setWindowTitle(self.trUtf8('Subversion Status'))
        
        self.process.start('svn', args)
        procStarted = self.process.waitForStarted()
        if not procStarted:
            self.inputGroup.setEnabled(False)
            KQMessageBox.critical(None,
                self.trUtf8('Process Generation Error'),
                self.trUtf8(
                    'The process %1 could not be started. '
                    'Ensure, that it is in the search path.'
                ).arg('svn'))
        else:
            self.inputGroup.setEnabled(True)
        
    def __finish(self):
        """
        Private slot called when the process finished or the user pressed the button.
        """
        if self.process is not None and \
           self.process.state() != QProcess.NotRunning:
            self.process.terminate()
            QTimer.singleShot(2000, self.process, SLOT('kill()'))
            self.process.waitForFinished(3000)
        
        self.buttonBox.button(QDialogButtonBox.Close).setEnabled(True)
        self.buttonBox.button(QDialogButtonBox.Cancel).setEnabled(False)
        self.buttonBox.button(QDialogButtonBox.Close).setDefault(True)
        
        self.inputGroup.setEnabled(False)
        self.refreshButton.setEnabled(True)
        
        for act in self.menuactions:
            act.setEnabled(True)
        
        self.process = None
        
        self.statusList.doItemsLayout()
        self.__resort()
        self.__resizeColumns()
        self.statusList.setColumnHidden(self.__changelistColumn, not self.changelistFound)
        
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
        
    def __procFinished(self, exitCode, exitStatus):
        """
        Private slot connected to the finished signal.
        
        @param exitCode exit code of the process (integer)
        @param exitStatus exit status of the process (QProcess.ExitStatus)
        """
        self.__finish()
        
    def __readStdout(self):
        """
        Private slot to handle the readyReadStandardOutput signal.
        
        It reads the output of the process, formats it and inserts it into
        the contents pane.
        """
        if self.process is not None:
            self.process.setReadChannel(QProcess.StandardOutput)
            
            while self.process.canReadLine():
                s = QString(self.process.readLine())
                if self.rx_status.exactMatch(s):
                    flags = str(self.rx_status.cap(1))
                    rev = self.rx_status.cap(2)
                    change = self.rx_status.cap(3)
                    author = self.rx_status.cap(4)
                    path = self.rx_status.cap(5).trimmed()
                    
                    self.__generateItem(flags[0], flags[1], flags[2], flags[3], flags[4], 
                                        flags[5], flags[7], rev, change, author, path)
                elif self.rx_status2.exactMatch(s):
                    flags = str(self.rx_status2.cap(1))
                    path = self.rx_status2.cap(2).trimmed()
                    
                    self.__generateItem(flags[0], flags[1], flags[2], flags[3], flags[4], 
                                        flags[5], flags[7], "", "", "", path)
                elif self.rx_changelist.exactMatch(s):
                    self.currentChangelist = self.rx_changelist.cap(1)
                    self.changelistFound = True
        
    def __readStderr(self):
        """
        Private slot to handle the readyReadStandardError signal.
        
        It reads the error output of the process and inserts it into the
        error pane.
        """
        if self.process is not None:
            self.errorGroup.show()
            s = QString(self.process.readAllStandardError())
            self.errors.insertPlainText(s)
            self.errors.ensureCursorVisible()
        
    def on_passwordCheckBox_toggled(self, isOn):
        """
        Private slot to handle the password checkbox toggled.
        
        @param isOn flag indicating the status of the check box (boolean)
        """
        if isOn:
            self.input.setEchoMode(QLineEdit.Password)
        else:
            self.input.setEchoMode(QLineEdit.Normal)
        
    @pyqtSignature("")
    def on_sendButton_clicked(self):
        """
        Private slot to send the input to the subversion process.
        """
        input = self.input.text()
        input.append(os.linesep)
        
        if self.passwordCheckBox.isChecked():
            self.errors.insertPlainText(os.linesep)
            self.errors.ensureCursorVisible()
        else:
            self.errors.insertPlainText(input)
            self.errors.ensureCursorVisible()
        
        self.process.write(input.toLocal8Bit())
        
        self.passwordCheckBox.setChecked(False)
        self.input.clear()
        
    def on_input_returnPressed(self):
        """
        Private slot to handle the press of the return key in the input field.
        """
        self.intercept = True
        self.on_sendButton_clicked()
        
    def keyPressEvent(self, evt):
        """
        Protected slot to handle a key press event.
        
        @param evt the key press event (QKeyEvent)
        """
        if self.intercept:
            self.intercept = False
            evt.accept()
            return
        QWidget.keyPressEvent(self, evt)
        
    @pyqtSignature("")
    def on_refreshButton_clicked(self):
        """
        Private slot to refresh the status display.
        """
        self.buttonBox.button(QDialogButtonBox.Close).setEnabled(False)
        self.buttonBox.button(QDialogButtonBox.Cancel).setEnabled(True)
        self.buttonBox.button(QDialogButtonBox.Cancel).setDefault(True)
        
        self.inputGroup.setEnabled(True)
        self.refreshButton.setEnabled(False)
        
        for act in self.menuactions:
            act.setEnabled(False)
        
        self.statusList.clear()
        
        self.start(self.args)
    
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
        Private method to retrieve all emtries, that have a locked status.
        
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
