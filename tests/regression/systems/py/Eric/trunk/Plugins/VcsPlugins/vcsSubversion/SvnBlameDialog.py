# -*- coding: utf-8 -*-

# Copyright (c) 2003 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a dialog to show the output of the svn blame command.
"""

import sys

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from KdeQt import KQMessageBox

from Ui_SvnBlameDialog import Ui_SvnBlameDialog

import Preferences
import Utilities

class SvnBlameDialog(QDialog, Ui_SvnBlameDialog):
    """
    Class implementing a dialog to show the output of the svn blame command.
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
        
        self.process = QProcess()
        self.vcs = vcs
        
        self.blameList.headerItem().setText(self.blameList.columnCount(), "")
        font = QFont(self.blameList.font())
        if Utilities.isWindowsPlatform():
            font.setFamily("Lucida Console")
        else:
            font.setFamily("Monospace")
        self.blameList.setFont(font)
        
        self.__ioEncoding = str(Preferences.getSystem("IOEncoding"))
        
        self.connect(self.process, SIGNAL('finished(int, QProcess::ExitStatus)'),
            self.__procFinished)
        self.connect(self.process, SIGNAL('readyReadStandardOutput()'),
            self.__readStdout)
        self.connect(self.process, SIGNAL('readyReadStandardError()'),
            self.__readStderr)
        
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
        
        @param fn filename to show the log for (string)
        """
        self.errorGroup.hide()
        self.intercept = False
        self.activateWindow()
        self.lineno = 1
        
        dname, fname = self.vcs.splitPath(fn)
        
        self.process.kill()
        
        args = QStringList()
        args.append('blame')
        self.vcs.addArguments(args, self.vcs.options['global'])
        args.append(fname)
        
        
        self.process.setWorkingDirectory(dname)
        
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
        
        self.process = None
        
        self.blameList.doItemsLayout()
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
        self.__finish()
        
    def __resizeColumns(self):
        """
        Private method to resize the list columns.
        """
        self.blameList.header().resizeSections(QHeaderView.ResizeToContents)
        self.blameList.header().setStretchLastSection(True)
        
    def __generateItem(self, revision, author, text):
        """
        Private method to generate a tag item in the taglist.
        
        @param revision revision string (string or QString)
        @param author author of the tag (string or QString)
        @param date date of the tag (string or QString)
        @param name name (path) of the tag (string or QString)
        """
        itm = QTreeWidgetItem(self.blameList, 
            QStringList() << revision << author << "%d" % self.lineno << text)
        self.lineno += 1
        itm.setTextAlignment(0, Qt.AlignRight)
        itm.setTextAlignment(2, Qt.AlignRight)
        
    def __readStdout(self):
        """
        Private slot to handle the readyReadStdout signal.
        
        It reads the output of the process, formats it and inserts it into
        the contents pane.
        """
        self.process.setReadChannel(QProcess.StandardOutput)
        
        while self.process.canReadLine():
            s = unicode(self.process.readLine(), self.__ioEncoding, 'replace').strip()
            rev, s = s.split(None, 1)
            try:
                author, text = s.split(' ', 1)
            except ValueError:
                author = s.strip()
                text = ""
            self.__generateItem(rev, author, text)
        
    def __readStderr(self):
        """
        Private slot to handle the readyReadStderr signal.
        
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
        QDialog.keyPressEvent(self, evt)
