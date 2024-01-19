# -*- coding: utf-8 -*-

# Copyright (c) 2002 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the UI to the pyunit package.
"""

import unittest
import sys
import traceback
import time
import re
import os

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from KdeQt import KQFileDialog, KQMessageBox
from KdeQt.KQMainWindow import KQMainWindow
from KdeQt.KQApplication import e4App

from E4Gui.E4Completers import E4FileCompleter

from Ui_UnittestDialog import Ui_UnittestDialog
from Ui_UnittestStacktraceDialog import Ui_UnittestStacktraceDialog

from DebugClients.Python.coverage import coverage

import UI.PixmapCache

import Utilities

class UnittestDialog(QWidget, Ui_UnittestDialog):
    """
    Class implementing the UI to the pyunit package.
    
    @signal unittestFile(string,int,int) emitted to show the source of a unittest file
    """
    def __init__(self,prog = None,dbs = None,ui = None,parent = None,name = None):
        """
        Constructor
        
        @param prog filename of the program to open
        @param dbs reference to the debug server object. It is an indication
                whether we were called from within the eric4 IDE
        @param ui reference to the UI object
        @param parent parent widget of this dialog (QWidget)
        @param name name of this dialog (string or QString)
        """
        QWidget.__init__(self,parent)
        if name:
            self.setObjectName(name)
        self.setupUi(self)
        
        self.startButton = self.buttonBox.addButton(\
            self.trUtf8("Start"), QDialogButtonBox.ActionRole)
        self.startButton.setToolTip(self.trUtf8("Start the selected testsuite"))
        self.startButton.setWhatsThis(self.trUtf8(\
            """<b>Start Test</b>"""
            """<p>This button starts the selected testsuite.</p>"""))
        self.stopButton = self.buttonBox.addButton(\
            self.trUtf8("Stop"), QDialogButtonBox.ActionRole)
        self.stopButton.setToolTip(self.trUtf8("Stop the running unittest"))
        self.stopButton.setWhatsThis(self.trUtf8(\
            """<b>Stop Test</b>"""
            """<p>This button stops a running unittest.</p>"""))
        self.stopButton.setEnabled(False)
        self.startButton.setDefault(True)
        
        self.dbs = dbs
        
        self.setWindowFlags(\
            self.windowFlags() | Qt.WindowFlags(Qt.WindowContextHelpButtonHint))
        self.setWindowIcon(UI.PixmapCache.getIcon("eric.png"))
        self.setWindowTitle(self.trUtf8("Unittest"))
        if dbs:
            self.ui = ui
        else:
            self.localCheckBox.hide()
        self.__setProgressColor("green")
        self.progressLed.setDarkFactor(150)
        self.progressLed.off()
        
        self.testSuiteCompleter = E4FileCompleter(self.testsuiteComboBox)
        
        self.fileHistory = QStringList()
        self.testNameHistory = QStringList()
        self.running = False
        self.savedModulelist = None
        self.savedSysPath = sys.path
        if prog:
            self.insertProg(prog)
        
        self.rx1 = QRegExp(self.trUtf8("^Failure: "))
        self.rx2 = QRegExp(self.trUtf8("^Error: "))
        
        # now connect the debug server signals if called from the eric4 IDE
        if self.dbs:
            self.connect(self.dbs, SIGNAL('utPrepared'),
                self.__UTPrepared)
            self.connect(self.dbs, SIGNAL('utFinished'),
                self.__setStoppedMode)
            self.connect(self.dbs, SIGNAL('utStartTest'),
                self.testStarted)
            self.connect(self.dbs, SIGNAL('utStopTest'),
                self.testFinished)
            self.connect(self.dbs, SIGNAL('utTestFailed'),
                self.testFailed)
            self.connect(self.dbs, SIGNAL('utTestErrored'),
                self.testErrored)
        
    def __setProgressColor(self, color):
        """
        Private methode to set the color of the progress color label.
        
        @param color colour to be shown
        """
        self.progressLed.setColor(QColor(color))
        
    def insertProg(self, prog):
        """
        Public slot to insert the filename prog into the testsuiteComboBox object.
        
        @param prog filename to be inserted (string or QString)
        """
        # prepend the selected file to the testsuite combobox
        if prog is None:
            prog = QString()
        self.fileHistory.removeAll(prog)
        self.fileHistory.prepend(prog)
        self.testsuiteComboBox.clear()
        self.testsuiteComboBox.addItems(self.fileHistory)
        
    def insertTestName(self, testName):
        """
        Public slot to insert a test name into the testComboBox object.
        
        @param testName name of the test to be inserted (string or QString)
        """
        # prepend the selected file to the testsuite combobox
        if testName is None:
            testName = QString()
        self.testNameHistory.removeAll(testName)
        self.testNameHistory.prepend(testName)
        self.testComboBox.clear()
        self.testComboBox.addItems(self.testNameHistory)
        
    @pyqtSignature("")
    def on_fileDialogButton_clicked(self):
        """
        Private slot to open a file dialog.
        """
        if self.dbs:
            pyExtensions = \
                ' '.join(["*%s" % ext for ext in self.dbs.getExtensions('Python')])
            py3Extensions = \
                ' '.join(["*%s" % ext for ext in self.dbs.getExtensions('Python3')])
            filter = self.trUtf8("Python Files (%1);;Python3 Files (%2);;All Files (*)")\
                .arg(pyExtensions).arg(py3Extensions)
        else:
            filter = self.trUtf8("Python Files (*.py);;All Files (*)")
        prog = KQFileDialog.getOpenFileName(\
            self,
            QString(),
            self.testsuiteComboBox.currentText(),
            filter)
        
        if prog.isNull():
            return
        
        self.insertProg(Utilities.toNativeSeparators(prog))
        
    @pyqtSignature("QString")
    def on_testsuiteComboBox_editTextChanged(self, txt):
        """
        Private slot to handle changes of the test file name.
        
        @param txt name of the test file (string)
        """
        if self.dbs:
            exts = self.dbs.getExtensions("Python3")
            if unicode(txt).endswith(exts):
                self.coverageCheckBox.setChecked(False)
                self.coverageCheckBox.setEnabled(False)
                self.localCheckBox.setChecked(False)
                self.localCheckBox.setEnabled(False)
                return
        
        self.coverageCheckBox.setEnabled(True)
        self.localCheckBox.setEnabled(True)
        
    def on_buttonBox_clicked(self, button):
        """
        Private slot called by a button of the button box clicked.
        
        @param button button that was clicked (QAbstractButton)
        """
        if button == self.startButton:
            self.on_startButton_clicked()
        elif button == self.stopButton:
            self.on_stopButton_clicked()
        
    @pyqtSignature("")
    def on_startButton_clicked(self):
        """
        Public slot to start the test.
        """
        if self.running:
            return
        
        prog = unicode(self.testsuiteComboBox.currentText())
        if not prog:
            KQMessageBox.critical(self, 
                    self.trUtf8("Unittest"), 
                    self.trUtf8("You must enter a test suite file."))
            return
        
        # prepend the selected file to the testsuite combobox
        self.insertProg(prog)
        self.sbLabel.setText(self.trUtf8("Preparing Testsuite"))
        QApplication.processEvents()
        
        testFunctionName = unicode(self.testComboBox.currentText()) or "suite"
        
        # build the module name from the filename without extension
        self.testName = os.path.splitext(os.path.basename(prog))[0]
        
        if self.dbs and not self.localCheckBox.isChecked():
            # we are cooperating with the eric4 IDE
            project = e4App().getObject("Project")
            if project.isOpen() and project.isProjectSource(prog):
                mainScript = project.getMainScript(True)
            else:
                mainScript = os.path.abspath(prog)
            self.dbs.remoteUTPrepare(prog, self.testName, testFunctionName,
                self.coverageCheckBox.isChecked(), mainScript,
                self.coverageEraseCheckBox.isChecked())
        else:
            # we are running as an application or in local mode
            sys.path = [os.path.dirname(os.path.abspath(prog))] + self.savedSysPath
            
            # clean up list of imported modules to force a reimport upon running the test
            if self.savedModulelist:
                for modname in sys.modules.keys():
                    if not self.savedModulelist.has_key(modname):
                        # delete it
                        del(sys.modules[modname])
            self.savedModulelist = sys.modules.copy()
            
            # now try to generate the testsuite
            try:
                module = __import__(self.testName)
                try:
                    test = unittest.defaultTestLoader.loadTestsFromName(\
                        testFunctionName, module)
                except AttributeError:
                    test = unittest.defaultTestLoader.loadTestsFromModule(module)
            except:
                exc_type, exc_value, exc_tb = sys.exc_info()
                KQMessageBox.critical(self, 
                        self.trUtf8("Unittest"),
                        self.trUtf8("<p>Unable to run test <b>%1</b>.<br>%2<br>%3</p>")
                            .arg(self.testName)
                            .arg(unicode(exc_type))
                            .arg(unicode(exc_value)))
                return
                
            # now set up the coverage stuff
            if self.coverageCheckBox.isChecked():
                if self.dbs:
                    # we are cooperating with the eric4 IDE
                    project = e4App().getObject("Project")
                    if project.isOpen() and project.isProjectSource(prog):
                        mainScript = project.getMainScript(True)
                    else:
                        mainScript = os.path.abspath(prog)
                else:
                    mainScript = os.path.abspath(prog)
                cover = coverage(
                    data_file = "%s.coverage" % os.path.splitext(mainScript)[0])
                cover.use_cache(True)
                if self.coverageEraseCheckBox.isChecked():
                    cover.erase()
            else:
                cover = None
            
            self.testResult = QtTestResult(self)
            self.totalTests = test.countTestCases()
            self.__setRunningMode()
            if cover:
                cover.start()
            test.run(self.testResult)
            if cover:
                cover.stop()
                cover.save()
            self.__setStoppedMode()
            sys.path = self.savedSysPath
        
    def __UTPrepared(self, nrTests, exc_type, exc_value):
        """
        Private slot to handle the utPrepared signal.
        
        If the unittest suite was loaded successfully, we ask the
        client to run the test suite.
        
        @param nrTests number of tests contained in the test suite (integer)
        @param exc_type type of exception occured during preparation (string)
        @param exc_value value of exception occured during preparation (string)
        """
        if nrTests == 0:
            KQMessageBox.critical(self, 
                    self.trUtf8("Unittest"),
                    self.trUtf8("<p>Unable to run test <b>%1</b>.<br>%2<br>%3</p>")
                        .arg(self.testName)
                        .arg(exc_type)
                        .arg(exc_value))
            return
            
        self.totalTests = nrTests
        self.__setRunningMode()
        self.dbs.remoteUTRun()
        
    @pyqtSignature("")
    def on_stopButton_clicked(self):
        """
        Private slot to stop the test.
        """
        if self.dbs and not self.localCheckBox.isChecked():
            self.dbs.remoteUTStop()
        elif self.testResult:
            self.testResult.stop()
            
    def on_errorsListWidget_currentTextChanged(self, text):
        """
        Private slot to handle the highlighted(const QString&) signal.
        """
        if not text.isEmpty():
            text.remove(self.rx1).remove(self.rx2)
            itm = self.testsListWidget.findItems(text, Qt.MatchFlags(Qt.MatchExactly))[0]
            self.testsListWidget.setCurrentItem(itm)
            self.testsListWidget.scrollToItem(itm)
        
    def __setRunningMode(self):
        """
        Private method to set the GUI in running mode.
        """
        self.running = True
        
        # reset counters and error infos
        self.runCount = 0
        self.failCount = 0
        self.errorCount = 0
        self.remainingCount = self.totalTests
        self.errorInfo = []

        # reset the GUI
        self.progressCounterRunCount.setText(str(self.runCount))
        self.progressCounterFailureCount.setText(str(self.failCount))
        self.progressCounterErrorCount.setText(str(self.errorCount))
        self.progressCounterRemCount.setText(str(self.remainingCount))
        self.errorsListWidget.clear()
        self.testsListWidget.clear()
        self.progressProgressBar.setRange(0, self.totalTests)
        self.__setProgressColor("green")
        self.progressProgressBar.reset()
        self.stopButton.setEnabled(True)
        self.startButton.setEnabled(False)
        self.stopButton.setDefault(True)
        self.sbLabel.setText(self.trUtf8("Running"))
        self.progressLed.on()
        QApplication.processEvents()
        
        self.startTime = time.time()
        
    def __setStoppedMode(self):
        """
        Private method to set the GUI in stopped mode.
        """
        self.stopTime = time.time()
        self.timeTaken = float(self.stopTime - self.startTime)
        self.running = False
        
        self.startButton.setEnabled(True)
        self.stopButton.setEnabled(False)
        self.startButton.setDefault(True)
        if self.runCount == 1:
            self.sbLabel.setText(self.trUtf8("Ran %1 test in %2s")
                .arg(self.runCount)
                .arg("%.3f" % self.timeTaken))
        else:
            self.sbLabel.setText(self.trUtf8("Ran %1 tests in %2s")
                .arg(self.runCount)
                .arg("%.3f" % self.timeTaken))
        self.progressLed.off()

    def testFailed(self, test, exc):
        """
        Public method called if a test fails.
        
        @param test name of the failed test (string)
        @param exc string representation of the exception (list of strings)
        """
        self.failCount += 1
        self.progressCounterFailureCount.setText(str(self.failCount))
        self.errorsListWidget.insertItem(0, self.trUtf8("Failure: %1").arg(test))
        self.errorInfo.insert(0, (test, exc))
        
    def testErrored(self, test, exc):
        """
        Public method called if a test errors.
        
        @param test name of the failed test (string)
        @param exc string representation of the exception (list of strings)
        """
        self.errorCount += 1
        self.progressCounterErrorCount.setText(str(self.errorCount))
        self.errorsListWidget.insertItem(0, self.trUtf8("Error: %1").arg(test))
        self.errorInfo.insert(0, (test, exc))
        
    def testStarted(self, test, doc):
        """
        Public method called if a test is about to be run.
        
        @param test name of the started test (string)
        @param doc documentation of the started test (string)
        """
        if doc:
            self.testsListWidget.insertItem(0, "    %s" % doc)
        self.testsListWidget.insertItem(0, unicode(test))
        if self.dbs is None or self.localCheckBox.isChecked():
            QApplication.processEvents()
        
    def testFinished(self):
        """
        Public method called if a test has finished.
        
        <b>Note</b>: It is also called if it has already failed or errored.
        """
        # update the counters
        self.remainingCount -= 1
        self.runCount += 1
        self.progressCounterRunCount.setText(str(self.runCount))
        self.progressCounterRemCount.setText(str(self.remainingCount))
        
        # update the progressbar
        if self.errorCount:
            self.__setProgressColor("red")
        elif self.failCount:
            self.__setProgressColor("orange")
        self.progressProgressBar.setValue(self.runCount)
        
    def on_errorsListWidget_itemDoubleClicked(self, lbitem):
        """
        Private slot called by doubleclicking an errorlist entry.
        
        It will popup a dialog showing the stacktrace.
        If called from eric, an additional button is displayed
        to show the python source in an eric source viewer (in
        erics main window.
        
        @param lbitem the listbox item that was double clicked
        """
        self.errListIndex = self.errorsListWidget.row(lbitem)
        text = lbitem.text()

        # get the error info
        test, tracebackLines = self.errorInfo[self.errListIndex]
        tracebackText = "".join(tracebackLines)

        # now build the dialog
        self.dlg = QDialog()
        ui = Ui_UnittestStacktraceDialog()
        ui.setupUi(self.dlg)
        
        ui.showButton = ui.buttonBox.addButton(\
            self.trUtf8("Show Source"), QDialogButtonBox.ActionRole)
        ui.buttonBox.button(QDialogButtonBox.Close).setDefault(True)
        
        self.dlg.setWindowTitle(text)
        ui.testLabel.setText(test)
        ui.traceback.setPlainText(tracebackText)
        
        # one more button if called from eric
        if self.dbs:
            self.dlg.connect(ui.showButton, SIGNAL("clicked()"),
                            self.__showSource)
        else:
            ui.showButton.hide()

        # and now fire it up
        self.dlg.show()
        self.dlg.exec_()
        
    def __showSource(self):
        """
        Private slot to show the source of a traceback in an eric4 editor.
        """
        if not self.dbs:
            return
            
        # get the error info
        test, tracebackLines = self.errorInfo[self.errListIndex]
        # find the last entry matching the pattern
        for index in range(len(tracebackLines) - 1, -1, -1):
            fmatch = re.search(r'File "(.*?)", line (\d*?),.*', tracebackLines[index])
            if fmatch:
                break
        if fmatch:
            fn, ln = fmatch.group(1, 2)
            self.emit(SIGNAL('unittestFile'), fn, int(ln), 1)

class QtTestResult(unittest.TestResult):
    """
    A TestResult derivative to work with a graphical GUI.
    
    For more details see pyunit.py of the standard python distribution.
    """
    def __init__(self, parent):
        """
        Constructor
        
        @param parent The parent widget.
        """
        unittest.TestResult.__init__(self)
        self.parent = parent
        
    def addFailure(self, test, err):
        """
        Method called if a test failed.
        
        @param test Reference to the test object
        @param err The error traceback
        """
        unittest.TestResult.addFailure(self, test, err)
        tracebackLines = apply(traceback.format_exception, err + (10,))
        self.parent.testFailed(unicode(test), tracebackLines)
        
    def addError(self, test, err):
        """
        Method called if a test errored.
        
        @param test Reference to the test object
        @param err The error traceback
        """
        unittest.TestResult.addError(self, test, err)
        tracebackLines = apply(traceback.format_exception, err + (10,))
        self.parent.testErrored(unicode(test), tracebackLines)
        
    def startTest(self, test):
        """
        Method called at the start of a test.
        
        @param test Reference to the test object
        """
        unittest.TestResult.startTest(self, test)
        self.parent.testStarted(unicode(test), test.shortDescription())

    def stopTest(self, test):
        """
        Method called at the end of a test.
        
        @param test Reference to the test object
        """
        unittest.TestResult.stopTest(self, test)
        self.parent.testFinished()

class UnittestWindow(KQMainWindow):
    """
    Main window class for the standalone dialog.
    """
    def __init__(self, prog = None, parent = None):
        """
        Constructor
        
        @param prog filename of the program to open
        @param parent reference to the parent widget (QWidget)
        """
        KQMainWindow.__init__(self, parent)
        self.cw = UnittestDialog(prog = prog, parent = self)
        self.cw.installEventFilter(self)
        size = self.cw.size()
        self.setCentralWidget(self.cw)
        self.resize(size)
    
    def eventFilter(self, obj, event):
        """
        Public method to filter events.
        
        @param obj reference to the object the event is meant for (QObject)
        @param event reference to the event object (QEvent)
        @return flag indicating, whether the event was handled (boolean)
        """
        if event.type() == QEvent.Close:
            QApplication.exit()
            return True
        
        return False
