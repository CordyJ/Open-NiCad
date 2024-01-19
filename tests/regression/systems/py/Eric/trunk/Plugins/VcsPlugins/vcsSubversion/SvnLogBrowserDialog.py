# -*- coding: utf-8 -*-

# Copyright (c) 2007 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a dialog to browse the log history.
"""

import os

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from KdeQt import KQMessageBox

from SvnDiffDialog import SvnDiffDialog

from Ui_SvnLogBrowserDialog import Ui_SvnLogBrowserDialog

import UI.PixmapCache

import Preferences

class SvnLogBrowserDialog(QDialog, Ui_SvnLogBrowserDialog):
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
        
        self.process = QProcess()
        self.connect(self.process, SIGNAL('finished(int, QProcess::ExitStatus)'),
            self.__procFinished)
        self.connect(self.process, SIGNAL('readyReadStandardOutput()'),
            self.__readStdout)
        self.connect(self.process, SIGNAL('readyReadStandardError()'),
            self.__readStderr)
        
        self.rx_sep1 = QRegExp('\\-+\\s*')
        self.rx_sep2 = QRegExp('=+\\s*')
        self.rx_rev1 = QRegExp('rev ([0-9]+):  ([^|]*) \| ([^|]*) \| ([0-9]+) .*')
        # "rev" followed by one or more decimals followed by a colon followed
        # anything up to " | " (twice) followed by one or more decimals followed
        # by anything
        self.rx_rev2 = QRegExp('r([0-9]+) \| ([^|]*) \| ([^|]*) \| ([0-9]+) .*')
        # "r" followed by one or more decimals followed by " | " followed
        # anything up to " | " (twice) followed by one or more decimals followed
        # by anything
        self.rx_flags1 = QRegExp(r"""   ([ADM])\s(.*)\s+\(\w+\s+(.*):([0-9]+)\)\s*""")
        # three blanks followed by A or D or M followed by path followed by
        # path copied from followed by copied from revision
        self.rx_flags2 = QRegExp('   ([ADM]) (.*)\\s*')
        # three blanks followed by A or D or M followed by path
        
        self.flags = {
            'A' : self.trUtf8('Added'),
            'D' : self.trUtf8('Deleted'),
            'M' : self.trUtf8('Modified')
        }
        
        self.buf = QStringList()        # buffer for stdout
        self.diff = None
        self.__started = False
        self.__lastRev = 0
    
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
        @param date date info (string or QString)
        @param message text of the log message (QStringList)
        @param revision revision info (string or QString)
        @param changedPaths list of dictionary objects containing
            info about the changed files/directories 
        @return reference to the generated item (QTreeWidgetItem)
        """
        msg = QStringList()
        for line in message:
            msg.append(line.trimmed())
        
        itm = QTreeWidgetItem(self.logTree, QStringList() \
            << "%7s" % revision \
            << author \
            << date \
            << msg.join(" ")
        )
        
        itm.setData(0, self.__messageRole, QVariant(message))
        itm.setData(0, self.__changesRole, QVariant(repr(changedPaths)))
        
        itm.setTextAlignment(0, Qt.AlignRight)
        itm.setTextAlignment(1, Qt.AlignLeft)
        itm.setTextAlignment(2, Qt.AlignLeft)
        itm.setTextAlignment(3, Qt.AlignLeft)
        itm.setTextAlignment(4, Qt.AlignLeft)
        
        try:
            self.__lastRev = int(revision)
        except ValueError:
            self.__lastRev = 0
        
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
        self.buttonBox.button(QDialogButtonBox.Close).setEnabled(False)
        self.buttonBox.button(QDialogButtonBox.Cancel).setEnabled(True)
        self.buttonBox.button(QDialogButtonBox.Cancel).setDefault(True)
        QApplication.processEvents()
        
        QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
        QApplication.processEvents()
        
        self.intercept = False
        self.process.kill()
        
        self.buf = QStringList()
        self.cancelled = False
        self.errors.clear()
        
        args = QStringList()
        args.append('log')
        self.vcs.addArguments(args, self.vcs.options['global'])
        self.vcs.addArguments(args, self.vcs.options['log'])
        args.append('--verbose')
        args.append('--limit')
        args.append('%d' % self.limitSpinBox.value())
        if startRev is not None:
            args.append('--revision')
            args.append('%s:0' % startRev)
        if self.stopCheckBox.isChecked():
            args.append('--stop-on-copy')
        args.append(self.fname)
        
        self.process.setWorkingDirectory(self.dname)
        
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
        self.__started = True
        self.__getLogEntries()
    
    def __procFinished(self, exitCode, exitStatus):
        """
        Private slot connected to the finished signal.
        
        @param exitCode exit code of the process (integer)
        @param exitStatus exit status of the process (QProcess.ExitStatus)
        """
        self.__processBuffer()
        self.__finish()
    
    def __finish(self):
        """
        Private slot called when the process finished or the user pressed the button.
        """
        if self.process is not None and \
           self.process.state() != QProcess.NotRunning:
            self.process.terminate()
            QTimer.singleShot(2000, self.process, SLOT('kill()'))
            self.process.waitForFinished(3000)
        
        QApplication.restoreOverrideCursor()
        
        self.buttonBox.button(QDialogButtonBox.Close).setEnabled(True)
        self.buttonBox.button(QDialogButtonBox.Cancel).setEnabled(False)
        self.buttonBox.button(QDialogButtonBox.Close).setDefault(True)
        
        self.inputGroup.setEnabled(False)
    
    def __processBuffer(self):
        """
        Private method to process the buffered output of the svn log command.
        """
        ioEncoding = str(Preferences.getSystem("IOEncoding"))
        
        noEntries = 0
        log = {"message" : QStringList()}
        changedPaths = []
        for s in self.buf:
            if self.rx_rev1.exactMatch(s):
                log["revision"] = self.rx_rev.cap(1)
                log["author"]   = self.rx_rev.cap(2)
                log["date"]     = self.rx_rev.cap(3)
                # number of lines is ignored
            elif self.rx_rev2.exactMatch(s):
                log["revision"] = self.rx_rev2.cap(1)
                log["author"]   = self.rx_rev2.cap(2)
                log["date"]     = self.rx_rev2.cap(3)
                # number of lines is ignored
            elif self.rx_flags1.exactMatch(s):
                changedPaths.append({\
                    "action"            : 
                        unicode(self.rx_flags1.cap(1).trimmed(), ioEncoding, 'replace'), 
                    "path"              : 
                        unicode(self.rx_flags1.cap(2).trimmed(), ioEncoding, 'replace'), 
                    "copyfrom_path"     : 
                        unicode(self.rx_flags1.cap(3).trimmed(), ioEncoding, 'replace'), 
                    "copyfrom_revision" : 
                        unicode(self.rx_flags1.cap(4).trimmed(), ioEncoding, 'replace'), 
                })
            elif self.rx_flags2.exactMatch(s):
                changedPaths.append({\
                    "action"            : 
                        unicode(self.rx_flags2.cap(1).trimmed(), ioEncoding, 'replace'), 
                    "path"              : 
                        unicode(self.rx_flags2.cap(2).trimmed(), ioEncoding, 'replace'), 
                    "copyfrom_path"     : "", 
                    "copyfrom_revision" : "", 
                })
            elif self.rx_sep1.exactMatch(s) or self.rx_sep2.exactMatch(s):
                if len(log) > 1:
                    self.__generateLogItem(log["author"], log["date"], 
                        log["message"], log["revision"], changedPaths)
                    dt = QDate.fromString(log["date"], Qt.ISODate)
                    if not self.__maxDate.isValid() and not self.__minDate.isValid():
                        self.__maxDate = dt
                        self.__minDate = dt
                    else:
                        if self.__maxDate < dt:
                            self.__maxDate = dt
                        if self.__minDate > dt:
                            self.__minDate = dt
                    noEntries += 1
                    log = {"message" : QStringList()}
                    changedPaths = []
            else:
                if s.trimmed().endsWith(":") or s.trimmed().isEmpty():
                    continue
                else:
                    log["message"].append(s)
        
        self.logTree.doItemsLayout()
        self.__resizeColumnsLog()
        self.__resortLog()
        
        if self.__started:
            self.logTree.setCurrentItem(self.logTree.topLevelItem(0))
            self.__started = False
        
        if noEntries < self.limitSpinBox.value() and not self.cancelled:
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
        self.__filterLogs()
    
    def __readStdout(self):
        """
        Private slot to handle the readyReadStandardOutput signal. 
        
        It reads the output of the process and inserts it into a buffer.
        """
        self.process.setReadChannel(QProcess.StandardOutput)
        
        while self.process.canReadLine():
            line = QString(self.process.readLine())
            self.buf.append(line)
    
    def __readStderr(self):
        """
        Private slot to handle the readyReadStandardError signal.
        
        It reads the error output of the process and inserts it into the
        error pane.
        """
        if self.process is not None:
            s = QString(self.process.readAllStandardError())
            self.errors.insertPlainText(s)
            self.errors.ensureCursorVisible()
    
    def __diffRevisions(self, rev1, rev2):
        """
        Private method to do a diff of two revisions.
        
        @param rev1 first revision number (integer)
        @param rev2 second revision number (integer)
        """
        if self.diff:
            self.diff.close()
            del self.diff
        self.diff = SvnDiffDialog(self.vcs)
        self.diff.show()
        self.diff.start(self.filename, [rev1, rev2])
    
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
        self.messageEdit.clear()
        for line in current.data(0, self.__messageRole).toStringList():
            self.messageEdit.append(line.trimmed())
        
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
        
        self.__diffRevisions(rev1, rev2)
    
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
        
        self.__diffRevisions(min(rev1, rev2), max(rev1, rev2))
    
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
