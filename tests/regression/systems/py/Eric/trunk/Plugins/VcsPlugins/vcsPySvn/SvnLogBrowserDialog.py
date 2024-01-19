# -*- coding: utf-8 -*-

# Copyright (c) 2007 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a dialog to browse the log history.
"""

import os

import pysvn

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from KdeQt import KQMessageBox

from SvnUtilities import formatTime, dateFromTime_t
from SvnDialogMixin import SvnDialogMixin
from SvnDiffDialog import SvnDiffDialog

from Ui_SvnLogBrowserDialog import Ui_SvnLogBrowserDialog

import UI.PixmapCache

class SvnLogBrowserDialog(QDialog, SvnDialogMixin, Ui_SvnLogBrowserDialog):
    """
    Class implementing a dialog to browse the log history.
    """
    def __init__(self, vcs, parent = None):
        """
        Constructor
        
        @param vcs reference to the vcs object
        @param parent parent widget (QWidget)
        """
        QDialog.__init__(self, parent)
        self.setupUi(self)
        SvnDialogMixin.__init__(self)
        
        self.buttonBox.button(QDialogButtonBox.Close).setEnabled(False)
        self.buttonBox.button(QDialogButtonBox.Cancel).setDefault(True)
        
        self.filesTree.headerItem().setText(self.filesTree.columnCount(), "")
        self.filesTree.header().setSortIndicator(0, Qt.AscendingOrder)
        
        self.vcs = vcs
        
        self.__maxDate = QDate()
        self.__minDate = QDate()
        self.__filterLogsEnabled = True
        
        self.fromDate.setDisplayFormat("yyyy-MM-dd")
        self.toDate.setDisplayFormat("yyyy-MM-dd")
        self.fromDate.setDate(QDate.currentDate())
        self.toDate.setDate(QDate.currentDate())
        self.fieldCombo.setCurrentIndex(self.fieldCombo.findText(self.trUtf8("Message")))
        self.clearRxEditButton.setIcon(UI.PixmapCache.getIcon("clearLeft.png"))
        self.limitSpinBox.setValue(self.vcs.getPlugin().getPreferences("LogLimit"))
        self.stopCheckBox.setChecked(self.vcs.getPlugin().getPreferences("StopLogOnCopy"))
        
        self.__messageRole = Qt.UserRole
        self.__changesRole = Qt.UserRole + 1
        
        self.flags = {
            'A' : self.trUtf8('Added'),
            'D' : self.trUtf8('Deleted'),
            'M' : self.trUtf8('Modified')
        }
        
        self.diff = None
        self.__lastRev = 0
        
        self.client = self.vcs.getClient()
        self.client.callback_cancel = \
            self._clientCancelCallback
        self.client.callback_get_login = \
            self._clientLoginCallback
        self.client.callback_ssl_server_trust_prompt = \
            self._clientSslServerTrustPromptCallback
    
    def _reset(self):
        """
        Protected method to reset the internal state of the dialog.
        """
        SvnDialogMixin._reset(self)
        
        self.cancelled = False
        
        self.buttonBox.button(QDialogButtonBox.Close).setEnabled(False)
        self.buttonBox.button(QDialogButtonBox.Cancel).setEnabled(True)
        self.buttonBox.button(QDialogButtonBox.Cancel).setDefault(True)
        QApplication.processEvents()
    
    def __resizeColumnsLog(self):
        """
        Private method to resize the log tree columns.
        """
        self.logTree.header().resizeSections(QHeaderView.ResizeToContents)
        self.logTree.header().setStretchLastSection(True)
    
    def __resortLog(self):
        """
        Private method to resort the log tree.
        """
        self.logTree.sortItems(self.logTree.sortColumn(), 
            self.logTree.header().sortIndicatorOrder())
    
    def __resizeColumnsFiles(self):
        """
        Private method to resize the changed files tree columns.
        """
        self.filesTree.header().resizeSections(QHeaderView.ResizeToContents)
        self.filesTree.header().setStretchLastSection(True)
    
    def __resortFiles(self):
        """
        Private method to resort the changed files tree.
        """
        sortColumn = self.filesTree.sortColumn()
        self.filesTree.sortItems(1, 
            self.filesTree.header().sortIndicatorOrder())
        self.filesTree.sortItems(sortColumn, 
            self.filesTree.header().sortIndicatorOrder())
    
    def __generateLogItem(self, author, date, message, revision, changedPaths):
        """
        Private method to generate a log tree entry.
        
        @param author author info (string or QString)
        @param date date info (integer)
        @param message text of the log message (string or QString)
        @param revision revision info (string or pysvn.opt_revision_kind)
        @param changedPaths list of pysvn dictionary like objects containing
            info about the changed files/directories 
        @return reference to the generated item (QTreeWidgetItem)
        """
        if revision == "":
            rev = ""
            self.__lastRev = 0
        else:
            rev = "%7d" % revision.number
            self.__lastRev = revision.number
        if date == "":
            dt = ""
        else:
            dt = formatTime(date)
        
        itm = QTreeWidgetItem(self.logTree, QStringList() \
            << rev \
            << author \
            << dt \
            << " ".join(message.splitlines())
        )
        
        changes = []
        for changedPath in changedPaths:
            if changedPath["copyfrom_path"] is None:
                copyPath = ""
            else:
                copyPath = changedPath["copyfrom_path"]
            if changedPath["copyfrom_revision"] is None:
                copyRev = ""
            else:
                copyRev = "%7d" % changedPath["copyfrom_revision"].number
            change = {
                "action"            : changedPath["action"], 
                "path"              : changedPath["path"], 
                "copyfrom_path"     : copyPath, 
                "copyfrom_revision" : copyRev, 
            }
            changes.append(change)
        itm.setData(0, self.__messageRole, QVariant(message))
        itm.setData(0, self.__changesRole, QVariant(unicode(changes)))
        
        itm.setTextAlignment(0, Qt.AlignRight)
        itm.setTextAlignment(1, Qt.AlignLeft)
        itm.setTextAlignment(2, Qt.AlignLeft)
        itm.setTextAlignment(3, Qt.AlignLeft)
        itm.setTextAlignment(4, Qt.AlignLeft)
        
        return itm
    
    def __generateFileItem(self, action, path, copyFrom, copyRev):
        """
        Private method to generate a changed files tree entry.
        
        @param action indicator for the change action ("A", "D" or "M")
        @param path path of the file in the repository (string or QString)
        @param copyFrom path the file was copied from (None, string or QString)
        @param copyRev revision the file was copied from (None, string or QString)
        @return reference to the generated item (QTreeWidgetItem)
        """
        itm = QTreeWidgetItem(self.filesTree, QStringList()
            << self.flags[action] \
            << path \
            << copyFrom \
            << copyRev
        )
        
        itm.setTextAlignment(3, Qt.AlignRight)
        
        return itm
    
    def __getLogEntries(self, startRev = None):
        """
        Private method to retrieve log entries from the repository.
        
        @param startRev revision number to start from (integer, string or QString)
        """
        fetchLimit = 10
        self._reset()
        
        QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
        QApplication.processEvents()
        
        limit = self.limitSpinBox.value()
        if startRev is None:
            start = pysvn.Revision(pysvn.opt_revision_kind.head)
        else:
            try:
                start = pysvn.Revision(pysvn.opt_revision_kind.number, int(startRev))
            except TypeError:
                start = pysvn.Revision(pysvn.opt_revision_kind.head)
        
        locker = QMutexLocker(self.vcs.vcsExecutionMutex)
        cwd = os.getcwd()
        os.chdir(self.dname)
        try:
            fetched = 0
            logs = []
            while fetched < limit:
                flimit = min(fetchLimit, limit - fetched)
                if fetched == 0:
                    revstart = start
                else:
                    revstart = pysvn.Revision(\
                        pysvn.opt_revision_kind.number, nextRev)
                allLogs = self.client.log(self.fname, 
                            revision_start = revstart, 
                            discover_changed_paths = True,
                            limit = flimit + 1,
                            strict_node_history = self.stopCheckBox.isChecked())
                if len(allLogs) <= flimit or self._clientCancelCallback():
                    logs.extend(allLogs)
                    break
                else:
                    logs.extend(allLogs[:-1])
                    nextRev = allLogs[-1]["revision"].number
                    fetched += fetchLimit
            locker.unlock()
            
            for log in logs:
                self.__generateLogItem(log["author"], log["date"], 
                    log["message"], log["revision"], log['changed_paths'])
                dt = dateFromTime_t(log["date"])
                if not self.__maxDate.isValid() and not self.__minDate.isValid():
                    self.__maxDate = dt
                    self.__minDate = dt
                else:
                    if self.__maxDate < dt:
                        self.__maxDate = dt
                    if self.__minDate > dt:
                        self.__minDate = dt
            if len(logs) < limit and not self.cancelled:
                self.nextButton.setEnabled(False)
                self.limitSpinBox.setEnabled(False)
            self.__filterLogsEnabled = False
            self.fromDate.setMinimumDate(self.__minDate)
            self.fromDate.setMaximumDate(self.__maxDate)
            self.fromDate.setDate(self.__minDate)
            self.toDate.setMinimumDate(self.__minDate)
            self.toDate.setMaximumDate(self.__maxDate)
            self.toDate.setDate(self.__maxDate)
            self.__filterLogsEnabled = True
            
            self.__resizeColumnsLog()
            self.__resortLog()
            self.__filterLogs()
        except pysvn.ClientError, e:
            locker.unlock()
            self.__showError(e.args[0])
        os.chdir(cwd)
        self.__finish()
    
    def start(self, fn):
        """
        Public slot to start the svn log command.
        
        @param fn filename to show the log for (string)
        """
        self.filename = fn
        self.dname, self.fname = self.vcs.splitPath(fn)
        
        self.activateWindow()
        self.raise_()
        
        self.logTree.clear()
        self.__getLogEntries()
        self.logTree.setCurrentItem(self.logTree.topLevelItem(0))
    
    def __finish(self):
        """
        Private slot called when the user pressed the button.
        """
        QApplication.restoreOverrideCursor()
        
        self.buttonBox.button(QDialogButtonBox.Close).setEnabled(True)
        self.buttonBox.button(QDialogButtonBox.Cancel).setEnabled(False)
        self.buttonBox.button(QDialogButtonBox.Close).setDefault(True)
        
        self._cancel()
    
    def __diffRevisions(self, rev1, rev2, peg_rev):
        """
        Private method to do a diff of two revisions.
        
        @param rev1 first revision number (integer)
        @param rev2 second revision number (integer)
        @param peg_rev revision number to use as a reference (integer)
        """
        if self.diff is None:
            self.diff = SvnDiffDialog(self.vcs)
        self.diff.show()
        QApplication.processEvents()
        self.diff.start(self.filename, [rev1, rev2], pegRev = peg_rev)
    
    def on_buttonBox_clicked(self, button):
        """
        Private slot called by a button of the button box clicked.
        
        @param button button that was clicked (QAbstractButton)
        """
        if button == self.buttonBox.button(QDialogButtonBox.Close):
            self.close()
        elif button == self.buttonBox.button(QDialogButtonBox.Cancel):
            self.cancelled = True
            self.__finish()
    
    @pyqtSignature("QTreeWidgetItem*, QTreeWidgetItem*")
    def on_logTree_currentItemChanged(self, current, previous):
        """
        Private slot called, when the current item of the log tree changes.
        
        @param current reference to the new current item (QTreeWidgetItem)
        @param previous reference to the old current item (QTreeWidgetItem)
        """
        self.messageEdit.setPlainText(current.data(0, self.__messageRole).toString())
        
        self.filesTree.clear()
        changes = eval(unicode(current.data(0, self.__changesRole).toString()))
        if len(changes) > 0:
            for change in changes:
                self.__generateFileItem(change["action"], change["path"], 
                    change["copyfrom_path"], change["copyfrom_revision"])
            self.__resizeColumnsFiles()
            self.__resortFiles()
        
        self.diffPreviousButton.setEnabled(\
            current != self.logTree.topLevelItem(self.logTree.topLevelItemCount() - 1))
    
    @pyqtSignature("")
    def on_logTree_itemSelectionChanged(self):
        """
        Private slot called, when the selection has changed.
        """
        self.diffRevisionsButton.setEnabled(len(self.logTree.selectedItems()) == 2)
    
    @pyqtSignature("")
    def on_nextButton_clicked(self):
        """
        Private slot to handle the Next button.
        """
        if self.__lastRev > 1:
            self.__getLogEntries(self.__lastRev - 1)
    
    @pyqtSignature("")
    def on_diffPreviousButton_clicked(self):
        """
        Private slot to handle the Diff to Previous button.
        """
        itm = self.logTree.topLevelItem(0)
        if itm is None:
            self.diffPreviousButton.setEnabled(False)
            return
        peg_rev = int(itm.text(0))
        
        itm = self.logTree.currentItem()
        if itm is None:
            self.diffPreviousButton.setEnabled(False)
            return
        rev2 = int(itm.text(0))
        
        itm = self.logTree.topLevelItem(self.logTree.indexOfTopLevelItem(itm) + 1)
        if itm is None:
            self.diffPreviousButton.setEnabled(False)
            return
        rev1 = int(itm.text(0))
        
        self.__diffRevisions(rev1, rev2, peg_rev)
    
    @pyqtSignature("")
    def on_diffRevisionsButton_clicked(self):
        """
        Private slot to handle the Compare Revisions button.
        """
        items = self.logTree.selectedItems()
        if len(items) != 2:
            self.diffRevisionsButton.setEnabled(False)
            return
        
        rev2 = int(items[0].text(0))
        rev1 = int(items[1].text(0))
        
        itm = self.logTree.topLevelItem(0)
        if itm is None:
            self.diffPreviousButton.setEnabled(False)
            return
        peg_rev = int(itm.text(0))
        
        self.__diffRevisions(min(rev1, rev2), max(rev1, rev2), peg_rev)
    
    def __showError(self, msg):
        """
        Private slot to show an error message.
        
        @param msg error message to show (string or QString)
        """
        KQMessageBox.critical(self,
            self.trUtf8("Subversion Error"),
            msg)
    
    @pyqtSignature("QDate")
    def on_fromDate_dateChanged(self, date):
        """
        Private slot called, when the from date changes.
        
        @param date new date (QDate)
        """
        self.__filterLogs()
    
    @pyqtSignature("QDate")
    def on_toDate_dateChanged(self, date):
        """
        Private slot called, when the from date changes.
        
        @param date new date (QDate)
        """
        self.__filterLogs()
    
    @pyqtSignature("QString")
    def on_fieldCombo_activated(self, txt):
        """
        Private slot called, when a new filter field is selected.
        
        @param txt text of the selected field (QString)
        """
        self.__filterLogs()
    
    @pyqtSignature("QString")
    def on_rxEdit_textChanged(self, txt):
        """
        Private slot called, when a filter expression is entered.
        
        @param txt filter expression (QString)
        """
        self.__filterLogs()
    
    def __filterLogs(self):
        """
        Private method to filter the log entries.
        """
        if self.__filterLogsEnabled:
            from_ = self.fromDate.date().toString("yyyy-MM-dd")
            to_ = self.toDate.date().addDays(1).toString("yyyy-MM-dd")
            txt = self.fieldCombo.currentText()
            if txt == self.trUtf8("Author"):
                fieldIndex = 1
                searchRx = QRegExp(self.rxEdit.text(), Qt.CaseInsensitive)
            elif txt == self.trUtf8("Revision"):
                fieldIndex = 0
                txt = self.rxEdit.text()
                if txt.startsWith("^"):
                    searchRx = QRegExp("^\s*%s" % txt[1:], Qt.CaseInsensitive)
                else:
                    searchRx = QRegExp(txt, Qt.CaseInsensitive)
            else:
                fieldIndex = 3
                searchRx = QRegExp(self.rxEdit.text(), Qt.CaseInsensitive)
            
            currentItem = self.logTree.currentItem()
            for topIndex in range(self.logTree.topLevelItemCount()):
                topItem = self.logTree.topLevelItem(topIndex)
                if topItem.text(2) <= to_ and topItem.text(2) >= from_ and \
                   topItem.text(fieldIndex).contains(searchRx):
                    topItem.setHidden(False)
                    if topItem is currentItem:
                        self.on_logTree_currentItemChanged(topItem, None)
                else:
                    topItem.setHidden(True)
                    if topItem is currentItem:
                        self.messageEdit.clear()
                        self.filesTree.clear()
    
    @pyqtSignature("")
    def on_clearRxEditButton_clicked(self):
        """
        Private slot called by a click of the clear RX edit button.
        """
        self.rxEdit.clear()
    
    @pyqtSignature("bool")
    def on_stopCheckBox_clicked(self, checked):
        """
        Private slot called, when the stop on copy/move checkbox is clicked
        """
        self.vcs.getPlugin().setPreferences("StopLogOnCopy", 
                                            int(self.stopCheckBox.isChecked()))
        self.nextButton.setEnabled(True)
        self.limitSpinBox.setEnabled(True)
