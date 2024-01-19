# -*- coding: utf-8 -*-

# Copyright (c) 2003 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a dialog to show the output of the ericapi process.
"""

import os.path

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from KdeQt import KQMessageBox

from Ui_EricapiExecDialog import Ui_EricapiExecDialog

class EricapiExecDialog(QDialog, Ui_EricapiExecDialog):
    """
    Class implementing a dialog to show the output of the ericapi process.
    
    This class starts a QProcess and displays a dialog that
    shows the output of the documentation command process.
    """
    def __init__(self, cmdname, parent = None):
        """
        Constructor
        
        @param cmdname name of the ericapi generator (string)
        @param parent parent widget of this dialog (QWidget)
        """
        QDialog.__init__(self, parent)
        self.setModal(True)
        self.setupUi(self)
        
        self.buttonBox.button(QDialogButtonBox.Close).setEnabled(False)
        self.buttonBox.button(QDialogButtonBox.Cancel).setDefault(True)
        
        self.process = None
        self.cmdname = cmdname
        
    def start(self, args, fn):
        """
        Public slot to start the ericapi command.
        
        @param args commandline arguments for ericapi program (QStringList)
        @param fn filename or dirname to be processed by ericapi program
        @return flag indicating the successful start of the process
        """
        self.errorGroup.hide()
        
        self.filename = unicode(fn)
        if os.path.isdir(self.filename):
            dname = os.path.abspath(self.filename)
            fname = "."
            if os.path.exists(os.path.join(dname, "__init__.py")):
                fname = os.path.basename(dname)
                dname = os.path.dirname(dname)
        else:
            dname = os.path.dirname(self.filename)
            fname = os.path.basename(self.filename)
        
        self.contents.clear()
        self.errors.clear()
        
        program = args[0]
        del args[0]
        args.append(fname)
        
        self.process = QProcess()
        self.process.setWorkingDirectory(dname)
        
        self.connect(self.process, SIGNAL('readyReadStandardOutput()'),
            self.__readStdout)
        self.connect(self.process, SIGNAL('readyReadStandardError()'),
            self.__readStderr)
        self.connect(self.process, SIGNAL('finished(int, QProcess::ExitStatus)'),
            self.__finish)
            
        self.setWindowTitle(self.trUtf8('%1 - %2').arg(self.cmdname).arg(self.filename))
        self.process.start(program, args)
        procStarted = self.process.waitForStarted()
        if not procStarted:
            KQMessageBox.critical(None,
                self.trUtf8('Process Generation Error'),
                self.trUtf8(
                    'The process %1 could not be started. '
                    'Ensure, that it is in the search path.'
                ).arg(program))
        return procStarted
        
    def on_buttonBox_clicked(self, button):
        """
        Private slot called by a button of the button box clicked.
        
        @param button button that was clicked (QAbstractButton)
        """
        if button == self.buttonBox.button(QDialogButtonBox.Close):
            self.accept()
        elif button == self.buttonBox.button(QDialogButtonBox.Cancel):
            self.__finish()
        
    def __finish(self):
        """
        Private slot called when the process finished.
        
        It is called when the process finished or
        the user pressed the button.
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
        
        self.contents.insertPlainText(self.trUtf8('\n%1 finished.\n').arg(self.cmdname))
        self.contents.ensureCursorVisible()
        
    def __readStdout(self):
        """
        Private slot to handle the readyReadStandardOutput signal. 
        
        It reads the output of the process, formats it and inserts it into
        the contents pane.
        """
        self.process.setReadChannel(QProcess.StandardOutput)
        
        while self.process.canReadLine():
            s = QString(self.process.readLine())
            self.contents.insertPlainText(s)
            self.contents.ensureCursorVisible()
        
    def __readStderr(self):
        """
        Private slot to handle the readyReadStandardError signal. 
        
        It reads the error output of the process and inserts it into the
        error pane.
        """
        self.process.setReadChannel(QProcess.StandardError)
        
        while self.process.canReadLine():
            self.errorGroup.show()
            s = QString(self.process.readLine())
            self.errors.insertPlainText(s)
            self.errors.ensureCursorVisible()
