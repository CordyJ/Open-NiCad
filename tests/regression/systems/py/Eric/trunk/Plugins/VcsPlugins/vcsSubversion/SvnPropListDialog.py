# -*- coding: utf-8 -*-

# Copyright (c) 2003 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a dialog to show the output of the svn proplist command process.
"""

import types

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from KdeQt import KQMessageBox

from Ui_SvnPropListDialog import Ui_SvnPropListDialog

class SvnPropListDialog(QWidget, Ui_SvnPropListDialog):
    """
    Class implementing a dialog to show the output of the svn proplist command process.
    """
    def __init__(self, vcs, parent = None):
        """
        Constructor
        
        @param vcs reference to the vcs object
        @param parent parent widget (QWidget)
        """
        QWidget.__init__(self, parent)
        self.setupUi(self)
        
        self.buttonBox.button(QDialogButtonBox.Close).setEnabled(False)
        self.buttonBox.button(QDialogButtonBox.Cancel).setDefault(True)
        
        self.process = QProcess()
        self.vcs = vcs
        
        self.propsList.headerItem().setText(self.propsList.columnCount(), "")
        self.propsList.header().setSortIndicator(0, Qt.AscendingOrder)
        
        self.connect(self.process, SIGNAL('finished(int, QProcess::ExitStatus)'),
            self.__procFinished)
        self.connect(self.process, SIGNAL('readyReadStandardOutput()'),
            self.__readStdout)
        self.connect(self.process, SIGNAL('readyReadStandardError()'),
            self.__readStderr)
        
        self.rx_path = QRegExp(r"Properties on '([^']+)':\s*")
        self.rx_prop = QRegExp(r"  (.*) : (.*)[\r\n]")
        self.lastPath = None
        self.lastProp = None
        self.propBuffer = QString('')
        
    def __resort(self):
        """
        Private method to resort the tree.
        """
        self.propsList.sortItems(self.propsList.sortColumn(), 
            self.propsList.header().sortIndicatorOrder())
        
    def __resizeColumns(self):
        """
        Private method to resize the list columns.
        """
        self.propsList.header().resizeSections(QHeaderView.ResizeToContents)
        self.propsList.header().setStretchLastSection(True)
        
    def __generateItem(self, path, propName, propValue):
        """
        Private method to generate a properties item in the properties list.
        
        @param path file/directory name the property applies to (string or QString)
        @param propName name of the property (string or QString)
        @param propValue value of the property (string or QString)
        """
        QTreeWidgetItem(self.propsList, QStringList() << path << propName << propValue)
        
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
        
    def start(self, fn, recursive = False):
        """
        Public slot to start the svn status command.
        
        @param fn filename(s) (string or list of string)
        @param recursive flag indicating a recursive list is requested
        """
        self.errorGroup.hide()
        
        self.process.kill()
        
        args = QStringList()
        args.append('proplist')
        self.vcs.addArguments(args, self.vcs.options['global'])
        args.append('--verbose')
        if recursive:
            args.append('--recursive')
        if type(fn) is types.ListType:
            dname, fnames = self.vcs.splitPathList(fn)
            self.vcs.addArguments(args, fnames)
        else:
            dname, fname = self.vcs.splitPath(fn)
            args.append(fname)
        
        self.process.setWorkingDirectory(dname)
        
        self.process.start('svn', args)
        procStarted = self.process.waitForStarted()
        if not procStarted:
            KQMessageBox.critical(None,
                self.trUtf8('Process Generation Error'),
                self.trUtf8(
                    'The process %1 could not be started. '
                    'Ensure, that it is in the search path.'
                ).arg('svn'))
        
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
        
        self.process = None
        if self.lastProp:
            self.__generateItem(self.lastPath, self.lastProp, self.propBuffer)
        
        self.__resort()
        self.__resizeColumns()
        
    def on_buttonBox_clicked(self, button):
        """
        Private slot called by a button of the button box clicked.
        
        @param button button that was clicked (QAbstractButton)
        """
        if button == self.buttonBox.button(QDialogButtonBox.Close):
            self.close()
        elif button == self.buttonBox.button(QDialogButtonBox.Cancel):
            self.__finish()
        
    def __procFinished(self, exitCode, exitStatus):
        """
        Private slot connected to the finished signal.
        
        @param exitCode exit code of the process (integer)
        @param exitStatus exit status of the process (QProcess.ExitStatus)
        """
        if self.lastPath is None:
            self.__generateItem('', 'None', '')
        
        self.__finish()
        
    def __readStdout(self):
        """
        Private slot to handle the readyReadStandardOutput signal.
        
        It reads the output of the process, formats it and inserts it into
        the contents pane.
        """
        self.process.setReadChannel(QProcess.StandardOutput)
        
        while self.process.canReadLine():
            s = QString(self.process.readLine())
            if self.rx_path.exactMatch(s):
                if self.lastProp:
                    self.__generateItem(self.lastPath, self.lastProp, self.propBuffer)
                self.lastPath = self.rx_path.cap(1)
                self.lastProp = None
                self.propBuffer = QString('')
            elif self.rx_prop.exactMatch(s):
                if self.lastProp:
                    self.__generateItem(self.lastPath, self.lastProp, self.propBuffer)
                self.lastProp = self.rx_prop.cap(1)
                self.propBuffer = self.rx_prop.cap(2)
            else:
                self.propBuffer.append(' ')
                self.propBuffer.append(s)
        
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
