# -*- coding: utf-8 -*-

# Copyright (c) 2007 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the subversion repository browser dialog.
"""

import os

from PyQt4.QtGui import *
from PyQt4.QtCore import *

from KdeQt import KQMessageBox

from Ui_SvnRepoBrowserDialog import Ui_SvnRepoBrowserDialog

import UI.PixmapCache

import Preferences

class SvnRepoBrowserDialog(QDialog, Ui_SvnRepoBrowserDialog):
    """
    Class implementing the subversion repository browser dialog.
    """
    def __init__(self, vcs, mode = "browse", parent = None):
        """
        Constructor
        
        @param vcs reference to the vcs object
        @param mode mode of the dialog (string, "browse" or "select")
        @param parent parent widget (QWidget)
        """
        QDialog.__init__(self, parent)
        self.setupUi(self)
        
        self.repoTree.headerItem().setText(self.repoTree.columnCount(), "")
        self.repoTree.header().setSortIndicator(0, Qt.AscendingOrder)
        
        self.process = None
        self.vcs = vcs
        self.mode = mode
        
        if self.mode == "select":
            self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)
            self.buttonBox.button(QDialogButtonBox.Close).hide()
        else:
            self.buttonBox.button(QDialogButtonBox.Ok).hide()
            self.buttonBox.button(QDialogButtonBox.Cancel).hide()
        
        self.__dirIcon = UI.PixmapCache.getIcon("dirClosed.png")
        self.__fileIcon = UI.PixmapCache.getIcon("fileMisc.png")
        
        self.__urlRole = Qt.UserRole
        self.__ignoreExpand = False
        self.intercept = False
        
        self.__rx_dir = \
            QRegExp(r"""\s*([0-9]+)\s+(\w+)\s+((?:\w+\s+\d+|[0-9.]+\s+\w+)\s+[0-9:]+)\s+(.+)\s*""")
        self.__rx_file = \
            QRegExp(r"""\s*([0-9]+)\s+(\w+)\s+([0-9]+)\s((?:\w+\s+\d+|[0-9.]+\s+\w+)\s+[0-9:]+)\s+(.+)\s*""")
    
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
        
    def __resort(self):
        """
        Private method to resort the tree.
        """
        self.repoTree.sortItems(self.repoTree.sortColumn(), 
            self.repoTree.header().sortIndicatorOrder())
    
    def __resizeColumns(self):
        """
        Private method to resize the tree columns.
        """
        self.repoTree.header().resizeSections(QHeaderView.ResizeToContents)
        self.repoTree.header().setStretchLastSection(True)
    
    def __generateItem(self, repopath, revision, author, size, date, 
            nodekind, url):
        """
        Private method to generate a tree item in the repository tree.
        
        @param parent parent of the item to be created (QTreeWidget or QTreeWidgetItem)
        @param repopath path of the item (string or QString)
        @param revision revision info (string or QString)
        @param author author info (string or QString)
        @param size size info (string or QString)
        @param date date info (string or QString)
        @param nodekind node kind info (string, "dir" or "file")
        @param url url of the entry (string or QString)
        @return reference to the generated item (QTreeWidgetItem)
        """
        path = repopath
        
        itm = QTreeWidgetItem(self.parentItem, 
            QStringList() \
            << path \
            << revision \
            << author \
            << size \
            << date
        )
        
        if nodekind == "dir":
            itm.setIcon(0, self.__dirIcon)
            itm.setChildIndicatorPolicy(QTreeWidgetItem.ShowIndicator)
        elif nodekind == "file":
            itm.setIcon(0, self.__fileIcon)
        
        itm.setData(0, self.__urlRole, QVariant(url))
        
        itm.setTextAlignment(0, Qt.AlignLeft)
        itm.setTextAlignment(1, Qt.AlignRight)
        itm.setTextAlignment(2, Qt.AlignLeft)
        itm.setTextAlignment(3, Qt.AlignRight)
        itm.setTextAlignment(4, Qt.AlignLeft)
        
        return itm
    
    def __repoRoot(self, url):
        """
        Private method to get the repository root using the svn info command.
        
        @param url the repository URL to browser (string or QString)
        @return repository root (string)
        """
        ioEncoding = str(Preferences.getSystem("IOEncoding"))
        repoRoot = None
        
        process = QProcess()
        
        args = QStringList()
        args.append('info')
        self.vcs.addArguments(args, self.vcs.options['global'])
        args.append('--xml')
        args.append(url)
        
        process.start('svn', args)
        procStarted = process.waitForStarted()
        if procStarted:
            finished = process.waitForFinished(30000)
            if finished:
                if process.exitCode() == 0:
                    output = unicode(process.readAllStandardOutput(), 
                                     ioEncoding, 'replace')
                    for line in output.splitlines():
                        line = line.strip()
                        if line.startswith('<root>'):
                            repoRoot = line.replace('<root>', '').replace('</root>', '')
                            break
                else:
                    error = QString(process.readAllStandardError())
                    self.errors.insertPlainText(error)
                    self.errors.ensureCursorVisible()
        else:
            QApplication.restoreOverrideCursor()
            KQMessageBox.critical(None,
                self.trUtf8('Process Generation Error'),
                self.trUtf8(
                    'The process %1 could not be started. '
                    'Ensure, that it is in the search path.'
                ).arg('svn'))
        return repoRoot
    
    def __listRepo(self, url, parent = None):
        """
        Private method to perform the svn list command.
        
        @param url the repository URL to browser (string or QString)
        @param parent reference to the item, the data should be appended to
            (QTreeWidget or QTreeWidgetItem)
        """
        QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
        QApplication.processEvents()
        
        self.repoUrl = url
        
        if parent is None:
            self.parentItem = self.repoTree
        else:
            self.parentItem = parent
        
        if self.parentItem == self.repoTree:
            repoRoot = self.__repoRoot(url)
            if repoRoot is None:
                self.__finish()
                return
            self.__ignoreExpand = True
            itm = self.__generateItem(repoRoot, "", "", "", "", "dir", repoRoot)
            itm.setExpanded(True)
            self.parentItem = itm
            urlPart = repoRoot
            for element in unicode(url).replace(repoRoot, "").split("/"):
                if element:
                    urlPart = "%s/%s" % (urlPart, element)
                    itm = self.__generateItem(element, "", "", "", "", "dir", urlPart)
                    itm.setExpanded(True)
                    self.parentItem = itm
            itm.setExpanded(False)
            self.__ignoreExpand = False
            self.__finish()
            return
        
        self.intercept = False
        
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
        args.append('list')
        self.vcs.addArguments(args, self.vcs.options['global'])
        if '--verbose' not in self.vcs.options['global']:
            args.append('--verbose')
        args.append(url)
        
        self.process.start('svn', args)
        procStarted = self.process.waitForStarted()
        if not procStarted:
            self.__finish()
            self.inputGroup.setEnabled(False)
            KQMessageBox.critical(None,
                self.trUtf8('Process Generation Error'),
                self.trUtf8(
                    'The process %1 could not be started. '
                    'Ensure, that it is in the search path.'
                ).arg('svn'))
        else:
            self.inputGroup.setEnabled(True)
    
    def __normalizeUrl(self, url):
        """
        Private method to normalite the url.
        
        @param url the url to normalize (string or QString)
        @return normalized URL (QString)
        """
        url_ = QString(url)
        if url_.endsWith("/"):
            return url_[:-1]
        return url_
    
    def start(self, url):
        """
        Public slot to start the svn info command.
        
        @param url the repository URL to browser (string or QString)
        """
        self.url = ""
        
        self.urlCombo.addItem(self.__normalizeUrl(url))
    
    @pyqtSignature("QString")
    def on_urlCombo_currentIndexChanged(self, text):
        """
        Private slot called, when a new repository URL is entered or selected.
        
        @param text the text of the current item (QString)
        """
        url = self.__normalizeUrl(text)
        if url != self.url:
            self.url = QString(url)
            self.repoTree.clear()
            self.__listRepo(url)
    
    @pyqtSignature("QTreeWidgetItem*")
    def on_repoTree_itemExpanded(self, item):
        """
        Private slot called when an item is expanded.
        
        @param item reference to the item to be expanded (QTreeWidgetItem)
        """
        if not self.__ignoreExpand:
            url = item.data(0, self.__urlRole).toString()
            self.__listRepo(url, item)
    
    @pyqtSignature("QTreeWidgetItem*")
    def on_repoTree_itemCollapsed(self, item):
        """
        Private slot called when an item is collapsed.
        
        @param item reference to the item to be collapsed (QTreeWidgetItem)
        """
        for child in item.takeChildren():
            del child
    
    @pyqtSignature("")
    def on_repoTree_itemSelectionChanged(self):
        """
        Private slot called when the selection changes.
        """
        if self.mode == "select":
            self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(True)
    
    def accept(self):
        """
        Public slot called when the dialog is accepted.
        """
        if self.focusWidget() == self.urlCombo:
            return
        
        QDialog.accept(self)
    
    def getSelectedUrl(self):
        """
        Public method to retrieve the selected repository URL.
        
        @return the selected repository URL (QString)
        """
        items = self.repoTree.selectedItems()
        if len(items) == 1:
            return items[0].data(0, self.__urlRole).toString()
        else:
            return QString()
    
    def __finish(self):
        """
        Private slot called when the process finished or the user pressed the button.
        """
        if self.process is not None and \
           self.process.state() != QProcess.NotRunning:
            self.process.terminate()
            QTimer.singleShot(2000, self.process, SLOT('kill()'))
            self.process.waitForFinished(3000)
        
        self.inputGroup.setEnabled(False)
        
        self.repoTree.doItemsLayout()
        self.__resizeColumns()
        self.__resort()
        QApplication.restoreOverrideCursor()
    
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
                if self.__rx_dir.exactMatch(s):
                    revision = self.__rx_dir.cap(1)
                    author = self.__rx_dir.cap(2)
                    date = self.__rx_dir.cap(3)
                    name = self.__rx_dir.cap(4).trimmed()
                    if name.endsWith("/"):
                        name = name[:-1]
                    size = ""
                    nodekind = "dir"
                elif self.__rx_file.exactMatch(s):
                    revision = self.__rx_file.cap(1)
                    author = self.__rx_file.cap(2)
                    size = self.__rx_file.cap(3)
                    date = self.__rx_file.cap(4)
                    name = self.__rx_file.cap(5).trimmed()
                    nodekind = "file"
                else:
                    continue
                url = "%s/%s" % (self.repoUrl, name)
                self.__generateItem(name, revision, author, size, date, nodekind, url)
   
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
        
