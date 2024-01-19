# -*- coding: utf-8 -*-

# Copyright (c) 2003 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a dialog to show the output of the svn diff command process.
"""

import os
import sys
import types

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from KdeQt import KQFileDialog, KQMessageBox
from KdeQt.KQApplication import e4App

from Ui_SvnDiffDialog import Ui_SvnDiffDialog

import Utilities

class SvnDiffDialog(QWidget, Ui_SvnDiffDialog):
    """
    Class implementing a dialog to show the output of the svn diff command process.
    """
    def __init__(self, vcs, parent = None):
        """
        Constructor
        
        @param vcs reference to the vcs object
        @param parent parent widget (QWidget)
        """
        QWidget.__init__(self, parent)
        self.setupUi(self)
        
        self.buttonBox.button(QDialogButtonBox.Save).setEnabled(False)
        self.buttonBox.button(QDialogButtonBox.Close).setDefault(True)
        
        self.process = QProcess()
        self.vcs = vcs
        
        if Utilities.isWindowsPlatform():
            self.contents.setFontFamily("Lucida Console")
        else:
            self.contents.setFontFamily("Monospace")
        
        self.cNormalFormat = self.contents.currentCharFormat()
        self.cAddedFormat = self.contents.currentCharFormat()
        self.cAddedFormat.setBackground(QBrush(QColor(190, 237, 190)))
        self.cRemovedFormat = self.contents.currentCharFormat()
        self.cRemovedFormat.setBackground(QBrush(QColor(237, 190, 190)))
        self.cLineNoFormat = self.contents.currentCharFormat()
        self.cLineNoFormat.setBackground(QBrush(QColor(255, 220, 168)))
        
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
        
    def __getVersionArg(self, version):
        """
        Private method to get a svn revision argument for the given revision.
        
        @param version revision (integer or string)
        @return version argument (string)
        """
        if version == "WORKING":
            return None
        else:
            return str(version)
        
    def start(self, fn, versions = None, urls = None, summary = False):
        """
        Public slot to start the svn diff command.
        
        @param fn filename to be diffed (string)
        @param versions list of versions to be diffed (list of up to 2 QString or None)
        @keyparam urls list of repository URLs (list of 2 strings)
        @keyparam summary flag indicating a summarizing diff 
            (only valid for URL diffs) (boolean)
        """
        self.errorGroup.hide()
        self.intercept = False
        self.filename = fn
        
        self.process.kill()
        
        self.contents.clear()
        self.paras = 0
        
        args = QStringList()
        args.append('diff')
        self.vcs.addArguments(args, self.vcs.options['global'])
        self.vcs.addArguments(args, self.vcs.options['diff'])
        if '--diff-cmd' in self.vcs.options['diff']:
            self.buttonBox.button(QDialogButtonBox.Save).hide()
        
        if versions is not None:
            self.raise_()
            self.activateWindow()
            
            rev1 = self.__getVersionArg(versions[0])
            rev2 = None
            if len(versions) == 2:
                rev2 = self.__getVersionArg(versions[1])
            
            if rev1 is not None or rev2 is not None:
                args.append('-r')
                if rev1 is not None and rev2 is not None:
                    args.append('%s:%s' % (rev1, rev2))
                elif rev2 is None:
                    args.append(rev1)
                elif rev1 is None:
                    args.append(rev2)
        
        self.summaryPath = None
        if urls is not None:
            if summary:
                args.append("--summarize")
                self.summaryPath = urls[0]
            args.append("--old=%s" % urls[0])
            args.append("--new=%s" % urls[1])
            if type(fn) is types.ListType:
                dname, fnames = self.vcs.splitPathList(fn)
            else:
                dname, fname = self.vcs.splitPath(fn)
                fnames = [fname]
            ppath = e4App().getObject('Project').getProjectPath()
            if dname == ppath:
                path = ""
            else:
                path = dname.replace(ppath+os.sep, '')
            if path:
                path += "/"
            for fname in fnames:
                args.append(path + fname)
        else:
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
            self.inputGroup.setEnabled(False)
            KQMessageBox.critical(None,
                self.trUtf8('Process Generation Error'),
                self.trUtf8(
                    'The process %1 could not be started. '
                    'Ensure, that it is in the search path.'
                ).arg('svn'))
        
    def __procFinished(self, exitCode, exitStatus):
        """
        Private slot connected to the finished signal.
        
        @param exitCode exit code of the process (integer)
        @param exitStatus exit status of the process (QProcess.ExitStatus)
        """
        self.inputGroup.setEnabled(False)
        
        if self.paras == 0:
            self.contents.insertPlainText(\
                self.trUtf8('There is no difference.'))
            return
            
        self.buttonBox.button(QDialogButtonBox.Save).setEnabled(True)
        tc = self.contents.textCursor()
        tc.movePosition(QTextCursor.Start)
        self.contents.setTextCursor(tc)
        self.contents.ensureCursorVisible()
        
    def __appendText(self, txt, format):
        """
        Private method to append text to the end of the contents pane.
        
        @param txt text to insert (QString)
        @param format text format to be used (QTextCharFormat)
        """
        tc = self.contents.textCursor()
        tc.movePosition(QTextCursor.End)
        self.contents.setTextCursor(tc)
        self.contents.setCurrentCharFormat(format)
        self.contents.insertPlainText(txt)
        
    def __readStdout(self):
        """
        Private slot to handle the readyReadStandardOutput signal. 
        
        It reads the output of the process, formats it and inserts it into
        the contents pane.
        """
        self.process.setReadChannel(QProcess.StandardOutput)
        
        while self.process.canReadLine():
            line = QString(self.process.readLine())
            if self.summaryPath:
                line = line.replace(self.summaryPath + '/', '')
                line = line.split(" ", QString.SkipEmptyParts).join(" ")
            if line.startsWith('+') or line.startsWith('>') or line.startsWith('A '):
                format = self.cAddedFormat
            elif line.startsWith('-') or line.startsWith('<') or line.startsWith('D '):
                format = self.cRemovedFormat
            elif line.startsWith('@@'):
                format = self.cLineNoFormat
            else:
                format = self.cNormalFormat
            self.__appendText(line, format)
            self.paras += 1
        
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
        
    def on_buttonBox_clicked(self, button):
        """
        Private slot called by a button of the button box clicked.
        
        @param button button that was clicked (QAbstractButton)
        """
        if button == self.buttonBox.button(QDialogButtonBox.Save):
            self.on_saveButton_clicked()
        
    @pyqtSignature("")
    def on_saveButton_clicked(self):
        """
        Private slot to handle the Save button press.
        
        It saves the diff shown in the dialog to a file in the local
        filesystem.
        """
        if type(self.filename) is types.ListType:
            if len(self.filename) > 1:
                fname = self.vcs.splitPathList(self.filename)[0]
            else:
                dname, fname = self.vcs.splitPath(self.filename[0])
                if fname != '.':
                    fname = "%s.diff" % self.filename[0]
                else:
                    fname = dname
        else:
            fname = self.vcs.splitPath(self.filename)[0]
        
        selectedFilter = QString("")
        fname = KQFileDialog.getSaveFileName(\
            self,
            self.trUtf8("Save Diff"),
            fname,
            self.trUtf8("Patch Files (*.diff)"),
            selectedFilter,
            QFileDialog.Options(QFileDialog.DontConfirmOverwrite))
        
        if fname.isEmpty():
            return
        
        ext = QFileInfo(fname).suffix()
        if ext.isEmpty():
            ex = selectedFilter.section('(*',1,1).section(')',0,0)
            if not ex.isEmpty():
                fname.append(ex)
        if QFileInfo(fname).exists():
            res = KQMessageBox.warning(self,
                self.trUtf8("Save Diff"),
                self.trUtf8("<p>The patch file <b>%1</b> already exists.</p>")
                    .arg(fname),
                QMessageBox.StandardButtons(\
                    QMessageBox.Abort | \
                    QMessageBox.Save),
                QMessageBox.Abort)
            if res != QMessageBox.Save:
                return
        fname = unicode(Utilities.toNativeSeparators(fname))
        
        try:
            f = open(fname, "wb")
            f.write(unicode(self.contents.toPlainText()))
            f.close()
        except IOError, why:
            KQMessageBox.critical(self, self.trUtf8('Save Diff'),
                self.trUtf8('<p>The patch file <b>%1</b> could not be saved.'
                    '<br>Reason: %2</p>')
                    .arg(unicode(fname)).arg(unicode(why)))
        
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