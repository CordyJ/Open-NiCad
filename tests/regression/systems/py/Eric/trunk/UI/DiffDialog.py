# -*- coding: utf-8 -*-

# Copyright (c) 2004 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a dialog to compare two files.
"""

import os
import sys
import time

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from KdeQt import KQFileDialog, KQMessageBox
from KdeQt.KQMainWindow import KQMainWindow

from E4Gui.E4Completers import E4FileCompleter

from Ui_DiffDialog import Ui_DiffDialog
import Utilities

from difflib import SequenceMatcher

# This function is copied from python 2.3 and slightly modified.
# The header lines contain a tab after the filename.
def unified_diff(a, b, fromfile='', tofile='', fromfiledate='',
                 tofiledate='', n=3, lineterm='\n'):
    """
    Compare two sequences of lines; generate the delta as a unified diff.

    Unified diffs are a compact way of showing line changes and a few
    lines of context.  The number of context lines is set by 'n' which
    defaults to three.

    By default, the diff control lines (those with ---, +++, or @@) are
    created with a trailing newline.  This is helpful so that inputs
    created from file.readlines() result in diffs that are suitable for
    file.writelines() since both the inputs and outputs have trailing
    newlines.

    For inputs that do not have trailing newlines, set the lineterm
    argument to "" so that the output will be uniformly newline free.

    The unidiff format normally has a header for filenames and modification
    times.  Any or all of these may be specified using strings for
    'fromfile', 'tofile', 'fromfiledate', and 'tofiledate'.  The modification
    times are normally expressed in the format returned by time.ctime().

    Example:

    <pre>
    &gt;&gt;&gt; for line in unified_diff('one two three four'.split(),
    ...             'zero one tree four'.split(), 'Original', 'Current',
    ...             'Sat Jan 26 23:30:50 1991', 'Fri Jun 06 10:20:52 2003',
    ...             lineterm=''):
    ...     print line
    --- Original Sat Jan 26 23:30:50 1991
    +++ Current Fri Jun 06 10:20:52 2003
    @@ -1,4 +1,4 @@
    +zero
     one
    -two
    -three
    +tree
     four
    </pre>
    
    @param a first sequence of lines (list of strings)
    @param b second sequence of lines (list of strings)
    @param fromfile filename of the first file (string)
    @param tofile filename of the second file (string)
    @param fromfiledate modification time of the first file (string)
    @param tofiledate modification time of the second file (string)
    @param n number of lines of context (integer)
    @param lineterm line termination string (string)
    @return a generator yielding lines of differences
    """
    started = False
    for group in SequenceMatcher(None,a,b).get_grouped_opcodes(n):
        if not started:
            yield '--- %s\t%s%s' % (fromfile, fromfiledate, lineterm)
            yield '+++ %s\t%s%s' % (tofile, tofiledate, lineterm)
            started = True
        i1, i2, j1, j2 = group[0][1], group[-1][2], group[0][3], group[-1][4]
        yield "@@ -%d,%d +%d,%d @@%s" % (i1+1, i2-i1, j1+1, j2-j1, lineterm)
        for tag, i1, i2, j1, j2 in group:
            if tag == 'equal':
                for line in a[i1:i2]:
                    yield ' ' + line
                continue
            if tag == 'replace' or tag == 'delete':
                for line in a[i1:i2]:
                    yield '-' + line
            if tag == 'replace' or tag == 'insert':
                for line in b[j1:j2]:
                    yield '+' + line

# This function is copied from python 2.3 and slightly modified.
# The header lines contain a tab after the filename.
def context_diff(a, b, fromfile='', tofile='',
                 fromfiledate='', tofiledate='', n=3, lineterm='\n'):
    """
    Compare two sequences of lines; generate the delta as a context diff.

    Context diffs are a compact way of showing line changes and a few
    lines of context.  The number of context lines is set by 'n' which
    defaults to three.

    By default, the diff control lines (those with *** or ---) are
    created with a trailing newline.  This is helpful so that inputs
    created from file.readlines() result in diffs that are suitable for
    file.writelines() since both the inputs and outputs have trailing
    newlines.

    For inputs that do not have trailing newlines, set the lineterm
    argument to "" so that the output will be uniformly newline free.

    The context diff format normally has a header for filenames and
    modification times.  Any or all of these may be specified using
    strings for 'fromfile', 'tofile', 'fromfiledate', and 'tofiledate'.
    The modification times are normally expressed in the format returned
    by time.ctime().  If not specified, the strings default to blanks.

    Example:

    <pre>
    &gt;&gt;&gt; print ''.join(context_diff('one\ntwo\nthree\nfour\n'.splitlines(1),
    ...       'zero\none\ntree\nfour\n'.splitlines(1), 'Original', 'Current',
    ...       'Sat Jan 26 23:30:50 1991', 'Fri Jun 06 10:22:46 2003')),
    *** Original Sat Jan 26 23:30:50 1991
    --- Current Fri Jun 06 10:22:46 2003
    ***************
    *** 1,4 ****
      one
    ! two
    ! three
      four
    --- 1,4 ----
    + zero
      one
    ! tree
      four
    </pre>
    
    @param a first sequence of lines (list of strings)
    @param b second sequence of lines (list of strings)
    @param fromfile filename of the first file (string)
    @param tofile filename of the second file (string)
    @param fromfiledate modification time of the first file (string)
    @param tofiledate modification time of the second file (string)
    @param n number of lines of context (integer)
    @param lineterm line termination string (string)
    @return a generator yielding lines of differences
    """

    started = False
    prefixmap = {'insert':'+ ', 'delete':'- ', 'replace':'! ', 'equal':'  '}
    for group in SequenceMatcher(None,a,b).get_grouped_opcodes(n):
        if not started:
            yield '*** %s\t%s%s' % (fromfile, fromfiledate, lineterm)
            yield '--- %s\t%s%s' % (tofile, tofiledate, lineterm)
            started = True

        yield '***************%s' % (lineterm,)
        if group[-1][2] - group[0][1] >= 2:
            yield '*** %d,%d ****%s' % (group[0][1]+1, group[-1][2], lineterm)
        else:
            yield '*** %d ****%s' % (group[-1][2], lineterm)
        visiblechanges = [e for e in group if e[0] in ('replace', 'delete')]
        if visiblechanges:
            for tag, i1, i2, _, _ in group:
                if tag != 'insert':
                    for line in a[i1:i2]:
                        yield prefixmap[tag] + line

        if group[-1][4] - group[0][3] >= 2:
            yield '--- %d,%d ----%s' % (group[0][3]+1, group[-1][4], lineterm)
        else:
            yield '--- %d ----%s' % (group[-1][4], lineterm)
        visiblechanges = [e for e in group if e[0] in ('replace', 'insert')]
        if visiblechanges:
            for tag, _, _, j1, j2 in group:
                if tag != 'delete':
                    for line in b[j1:j2]:
                        yield prefixmap[tag] + line

class DiffDialog(QWidget, Ui_DiffDialog):
    """
    Class implementing a dialog to compare two files.
    """
    def __init__(self,parent = None):
        """
        Constructor
        """
        QWidget.__init__(self,parent)
        self.setupUi(self)
        
        self.file1Completer = E4FileCompleter(self.file1Edit)
        self.file2Completer = E4FileCompleter(self.file2Edit)
        
        self.diffButton = \
            self.buttonBox.addButton(self.trUtf8("Compare"), QDialogButtonBox.ActionRole)
        self.diffButton.setToolTip(\
            self.trUtf8("Press to perform the comparison of the two files"))
        self.saveButton = \
            self.buttonBox.addButton(self.trUtf8("Save"), QDialogButtonBox.ActionRole)
        self.saveButton.setToolTip(self.trUtf8("Save the output to a patch file"))
        self.diffButton.setEnabled(False)
        self.saveButton.setEnabled(False)
        self.diffButton.setDefault(True)
        
        self.filename1 = ''
        self.filename2 = ''
        
        self.updateInterval = 20    # update every 20 lines
        
        if Utilities.isWindowsPlatform():
            self.contents.setFontFamily("Lucida Console")
        else:
            self.contents.setFontFamily("Monospace")
        
        self.cNormalFormat = self.contents.currentCharFormat()
        self.cAddedFormat = self.contents.currentCharFormat()
        self.cAddedFormat.setBackground(QBrush(QColor(190, 237, 190)))
        self.cRemovedFormat = self.contents.currentCharFormat()
        self.cRemovedFormat.setBackground(QBrush(QColor(237, 190, 190)))
        self.cReplacedFormat = self.contents.currentCharFormat()
        self.cReplacedFormat.setBackground(QBrush(QColor(190, 190, 237)))
        self.cLineNoFormat = self.contents.currentCharFormat()
        self.cLineNoFormat.setBackground(QBrush(QColor(255, 220, 168)))
        
        # connect some of our widgets explicitly
        self.connect(self.file1Edit, SIGNAL("textChanged(const QString &)"), 
                     self.__fileChanged)
        self.connect(self.file2Edit, SIGNAL("textChanged(const QString &)"), 
                     self.__fileChanged)
        
    def show(self, filename = None):
        """
        Public slot to show the dialog.
        
        @param filename name of a file to use as the first file (string or QString)
        """
        if filename:
            self.file1Edit.setText(filename)
        QWidget.show(self)
        
    def on_buttonBox_clicked(self, button):
        """
        Private slot called by a button of the button box clicked.
        
        @param button button that was clicked (QAbstractButton)
        """
        if button == self.diffButton:
            self.on_diffButton_clicked()
        elif button == self.saveButton:
            self.on_saveButton_clicked()
        
    @pyqtSignature("")
    def on_saveButton_clicked(self):
        """
        Private slot to handle the Save button press.
        
        It saves the diff shown in the dialog to a file in the local
        filesystem.
        """
        dname, fname = Utilities.splitPath(self.filename2)
        if fname != '.':
            fname = "%s.diff" % self.filename2
        else:
            fname = dname
            
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
            txt = self.contents.toPlainText()
            try:
                f.write(unicode(txt))
            except UnicodeError:
                pass
            f.close()
        except IOError, why:
            KQMessageBox.critical(self, self.trUtf8('Save Diff'),
                self.trUtf8('<p>The patch file <b>%1</b> could not be saved.<br />'
                            'Reason: %2</p>')
                    .arg(unicode(fname)).arg(unicode(why)))

    @pyqtSignature("")
    def on_diffButton_clicked(self):
        """
        Private slot to handle the Compare button press.
        """
        self.filename1 = unicode(Utilities.toNativeSeparators(self.file1Edit.text()))
        try:
            filemtime1 = time.ctime(os.stat(self.filename1).st_mtime)
        except IOError:
            filemtime1 = ""
        try:
            f1 = open(self.filename1, "rb")
            lines1 = f1.readlines()
            f1.close()
        except IOError:
            KQMessageBox.critical(self,
                self.trUtf8("Compare Files"),
                self.trUtf8("""<p>The file <b>%1</b> could not be read.</p>""")
                    .arg(self.filename1))
            return

        self.filename2 = unicode(Utilities.toNativeSeparators(self.file2Edit.text()))
        try:
            filemtime2 = time.ctime(os.stat(self.filename2).st_mtime)
        except IOError:
            filemtime2 = ""
        try:
            f2 = open(self.filename2, "rb")
            lines2 = f2.readlines()
            f2.close()
        except IOError:
            KQMessageBox.critical(self,
                self.trUtf8("Compare Files"),
                self.trUtf8("""<p>The file <b>%1</b> could not be read.</p>""")
                    .arg(self.filename2))
            return
        
        self.contents.clear()
        self.saveButton.setEnabled(False)
        
        if self.unifiedRadioButton.isChecked():
            self.__generateUnifiedDiff(lines1, lines2, self.filename1, self.filename2,
                                filemtime1, filemtime2)
        else:
            self.__generateContextDiff(lines1, lines2, self.filename1, self.filename2,
                                filemtime1, filemtime2)
        
        tc = self.contents.textCursor()
        tc.movePosition(QTextCursor.Start)
        self.contents.setTextCursor(tc)
        self.contents.ensureCursorVisible()
        
        self.saveButton.setEnabled(True)

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
        
    def __generateUnifiedDiff(self, a, b, fromfile, tofile,
                            fromfiledate, tofiledate):
        """
        Private slot to generate a unified diff output.
        
        @param a first sequence of lines (list of strings)
        @param b second sequence of lines (list of strings)
        @param fromfile filename of the first file (string)
        @param tofile filename of the second file (string)
        @param fromfiledate modification time of the first file (string)
        @param tofiledate modification time of the second file (string)
        """
        paras = 0
        for line in unified_diff(a, b, fromfile, tofile,
                            fromfiledate, tofiledate):
            if line.startswith('+') or line.startswith('>'):
                format = self.cAddedFormat
            elif line.startswith('-') or line.startswith('<'):
                format = self.cRemovedFormat
            elif line.startswith('@@'):
                format = self.cLineNoFormat
            else:
                format = self.cNormalFormat
            self.__appendText(line, format)
            paras += 1
            if not (paras % self.updateInterval):
                QApplication.processEvents()
            
        if paras == 0:
            self.__appendText(self.trUtf8('There is no difference.'), self.cNormalFormat)

    def __generateContextDiff(self, a, b, fromfile, tofile,
                            fromfiledate, tofiledate):
        """
        Private slot to generate a context diff output.
        
        @param a first sequence of lines (list of strings)
        @param b second sequence of lines (list of strings)
        @param fromfile filename of the first file (string)
        @param tofile filename of the second file (string)
        @param fromfiledate modification time of the first file (string)
        @param tofiledate modification time of the second file (string)
        """
        paras = 0
        for line in context_diff(a, b, fromfile, tofile,
                            fromfiledate, tofiledate):
            if line.startswith('+ '):
                format = self.cAddedFormat
            elif line.startswith('- '):
                format = self.cRemovedFormat
            elif line.startswith('! '):
                format = self.cReplacedFormat
            elif (line.startswith('*** ') or line.startswith('--- ')) and paras > 1:
                format = self.cLineNoFormat
            else:
                format = self.cNormalFormat
            self.__appendText(line, format)
            paras += 1
            if not (paras % self.updateInterval):
                QApplication.processEvents()
            
        if paras == 0:
            self.__appendText(self.trUtf8('There is no difference.'), self.cNormalFormat)

    def __fileChanged(self):
        """
        Private slot to enable/disable the Compare button.
        """
        if self.file1Edit.text().isEmpty() or \
           self.file2Edit.text().isEmpty():
            self.diffButton.setEnabled(False)
        else:
            self.diffButton.setEnabled(True)

    def __selectFile(self, lineEdit):
        """
        Private slot to display a file selection dialog.
        
        @param lineEdit field for the display of the selected filename
                (QLineEdit)
        """
        filename = KQFileDialog.getOpenFileName(\
            self,
            self.trUtf8("Select file to compare"),
            lineEdit.text(),
            QString())
            
        if not filename.isEmpty():
            lineEdit.setText(Utilities.toNativeSeparators(filename))

    @pyqtSignature("")
    def on_file1Button_clicked(self):
        """
        Private slot to handle the file 1 file selection button press.
        """
        self.__selectFile(self.file1Edit)

    @pyqtSignature("")
    def on_file2Button_clicked(self):
        """
        Private slot to handle the file 2 file selection button press.
        """
        self.__selectFile(self.file2Edit)

class DiffWindow(KQMainWindow):
    """
    Main window class for the standalone dialog.
    """
    def __init__(self, parent = None):
        """
        Constructor
        
        @param parent reference to the parent widget (QWidget)
        """
        KQMainWindow.__init__(self, parent)
        self.cw = DiffDialog(self)
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