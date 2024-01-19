# -*- coding: utf-8 -*-

# Copyright (c) 2003 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a dialog to display profile data.
"""

import sys
import os
import pickle

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from KdeQt import KQMessageBox

from Ui_PyProfileDialog import Ui_PyProfileDialog
import Utilities

from eric4config import getConfig

class ProfileTreeWidgetItem(QTreeWidgetItem):
    """
    Class implementing a custom QTreeWidgetItem to allow sorting on numeric values.
    """
    def __getNC(self, itm):
        """
        Private method to get the value to compare on for the first column.
        
        @param itm item to operate on (ProfileTreeWidgetItem)
        """
        s = str(itm.text(0))
        return int(s.split('/')[0])
        
    def __lt__(self, other):
        """
        Public method to check, if the item is less than the other one.
        
        @param other reference to item to compare against (ProfileTreeWidgetItem)
        @return true, if this item is less than other (boolean)
        """
        column = self.treeWidget().sortColumn()
        if column == 0:
            return self.__getNC(self) < self.__getNC(other)
        if column == 6:
            return int(str(self.text(column))) < int(str(other.text(column)))
        return self.text(column) < other.text(column)
        
class PyProfileDialog(QDialog, Ui_PyProfileDialog):
    """
    Class implementing a dialog to display the results of a syntax check run.
    """
    def __init__(self, parent = None):
        """
        Constructor
        
        @param parent parent widget (QWidget)
        """
        QDialog.__init__(self, parent)
        self.setupUi(self)
        
        self.buttonBox.button(QDialogButtonBox.Close).setEnabled(False)
        self.buttonBox.button(QDialogButtonBox.Cancel).setDefault(True)
        
        self.cancelled = False
        self.exclude = True
        self.ericpath = getConfig('ericDir')
        self.pyLibPath = Utilities.getPythonLibPath()
        
        self.summaryList.headerItem().setText(self.summaryList.columnCount(), "")
        self.resultList.headerItem().setText(self.resultList.columnCount(), "")
        self.resultList.header().setSortIndicator(0, Qt.DescendingOrder)
        
        self.__menu = QMenu(self)
        self.filterItm = self.__menu.addAction(self.trUtf8('Exclude Python Library'), 
            self.__filter)
        self.__menu.addSeparator()
        self.__menu.addAction(self.trUtf8('Erase Profiling Info'), 
            self.__eraseProfile)
        self.__menu.addAction(self.trUtf8('Erase Timing Info'), self.__eraseTiming)
        self.__menu.addSeparator()
        self.__menu.addAction(self.trUtf8('Erase All Infos'), self.__eraseAll)
        self.resultList.setContextMenuPolicy(Qt.CustomContextMenu)
        self.connect(self.resultList, 
                     SIGNAL('customContextMenuRequested(const QPoint &)'),
                     self.__showContextMenu)
        self.summaryList.setContextMenuPolicy(Qt.CustomContextMenu)
        self.connect(self.summaryList, 
                     SIGNAL('customContextMenuRequested(const QPoint &)'),
                     self.__showContextMenu)
        
    def __createResultItem(self, calls, totalTime, totalTimePerCall, cumulativeTime, 
                           cumulativeTimePerCall, file, line, functionName):
        """
        Private method to create an entry in the result list.
        
        @param calls number of calls (integer)
        @param totalTime total time (double)
        @param totalTimePerCall total time per call (double)
        @param cumulativeTime cumulative time (double)
        @param cumulativeTimePerCall cumulative time per call (double)
        @param file filename of file (string or QString)
        @param line linenumber (integer)
        @param functionName function name (string or QString)
        """
        itm = ProfileTreeWidgetItem(self.resultList, QStringList() \
            << calls << "% 8.3f" % totalTime << totalTimePerCall \
            << "% 8.3f" % cumulativeTime << cumulativeTimePerCall \
            << file << str(line) << functionName)
        for col in [0, 1, 2, 3, 4, 6]:
            itm.setTextAlignment(col, Qt.AlignRight)
        
    def __createSummaryItem(self, label, contents):
        """
        Private method to create an entry in the summary list.
        
        @param label text of the first column (string or QString)
        @param contents text of the second column (string or QString)
        """
        itm = QTreeWidgetItem(self.summaryList, QStringList() << label << contents)
        itm.setTextAlignment(1, Qt.AlignRight)
        
    def __resortResultList(self):
        """
        Private method to resort the tree.
        """
        self.resultList.sortItems(self.resultList.sortColumn(), 
                                  self.resultList.header().sortIndicatorOrder())
        
    def __populateLists(self, exclude = False):
        """
        Private method used to populate the listviews.
        
        @param exclude flag indicating whether files residing in the
                Python library should be excluded
        """
        self.resultList.clear()
        self.summaryList.clear()
        
        self.checkProgress.setMaximum(len(self.stats))
        QApplication.processEvents()
        
        progress = 0
        total_calls = 0
        prim_calls  = 0
        total_tt    = 0
        
        try:
            # disable updates of the list for speed
            self.resultList.setUpdatesEnabled(False)
            self.resultList.setSortingEnabled(False)
            
            # now go through all the files
            for func, (cc, nc, tt, ct, callers) in self.stats.items():
                if self.cancelled:
                    return
                
                if not (self.ericpath and func[0].startswith(self.ericpath)) and \
                   not (exclude and func[0].startswith(self.pyLibPath)):
                    if self.file is None or func[0].startswith(self.file) or \
                       func[0].startswith(self.pyLibPath):
                        # calculate the totals
                        total_calls += nc
                        prim_calls  += cc
                        total_tt    += tt
                        
                        if nc != cc:
                            c = "%d/%d" % (nc, cc)
                        else:
                            c = str(nc)
                        if nc == 0:
                            tpc = "% 8.3f" % 0.0
                        else:
                            tpc = "% 8.3f" % (tt/nc,)
                        if cc == 0:
                            cpc = "% 8.3f" % 0.0
                        else:
                            cpc = "% 8.3f" % (ct/cc,)
                        self.__createResultItem(c, tt, tpc, ct, cpc, func[0], 
                                                func[1], func[2])
                    
                progress += 1
                self.checkProgress.setValue(progress)
                QApplication.processEvents()
        finally:
            # reenable updates of the list
            self.resultList.setSortingEnabled(True)
            self.resultList.setUpdatesEnabled(True)
        self.__resortResultList()
        
        # now do the summary stuff
        self.__createSummaryItem(self.trUtf8("function calls"), str(total_calls))
        if total_calls != prim_calls:
            self.__createSummaryItem(self.trUtf8("primitive calls"), str(prim_calls))
        self.__createSummaryItem(self.trUtf8("CPU seconds"), "%.3f" % total_tt)
        
    def start(self, pfn, fn=None):
        """
        Public slot to start the calculation of the profile data.
        
        @param pfn basename of the profiling file (string)
        @param fn file to display the profiling data for (string)
        """
        self.basename = os.path.splitext(pfn)[0]
        
        fname = "%s.profile" % self.basename
        if not os.path.exists(fname):
            KQMessageBox.warning(None,
                self.trUtf8("Profile Results"),
                self.trUtf8("""<p>There is no profiling data"""
                            """ available for <b>%1</b>.</p>""")
                    .arg(pfn))
            self.close()
            return
        try:
            f = open(fname, 'rb')
            self.stats = pickle.load(f)
            f.close()
        except (EnvironmentError, pickle.PickleError):
            KQMessageBox.critical(None,
                self.trUtf8("Loading Profiling Data"),
                self.trUtf8("""<p>The profiling data could not be"""
                            """ read from file <b>%1</b>.</p>""")
                    .arg(fname))
            self.close()
            return
        
        self.file = fn
        self.__populateLists()
        self.__finish()
        
    def __finish(self):
        """
        Private slot called when the action finished or the user pressed the button.
        """
        self.cancelled = True
        self.buttonBox.button(QDialogButtonBox.Close).setEnabled(True)
        self.buttonBox.button(QDialogButtonBox.Cancel).setEnabled(False)
        self.buttonBox.button(QDialogButtonBox.Close).setDefault(True)
        QApplication.processEvents()
        self.resultList.header().resizeSections(QHeaderView.ResizeToContents)
        self.resultList.header().setStretchLastSection(True)
        self.summaryList.header().resizeSections(QHeaderView.ResizeToContents)
        self.summaryList.header().setStretchLastSection(True)
        
    def __unfinish(self):
        """
        Private slot called to revert the effects of the __finish slot.
        """
        self.cancelled = False
        self.buttonBox.button(QDialogButtonBox.Close).setEnabled(False)
        self.buttonBox.button(QDialogButtonBox.Cancel).setEnabled(True)
        self.buttonBox.button(QDialogButtonBox.Cancel).setDefault(True)
        
    def on_buttonBox_clicked(self, button):
        """
        Private slot called by a button of the button box clicked.
        
        @param button button that was clicked (QAbstractButton)
        """
        if button == self.buttonBox.button(QDialogButtonBox.Close):
            self.close()
        elif button == self.buttonBox.button(QDialogButtonBox.Cancel):
            self.__finish()
        
    def __showContextMenu(self, coord):
        """
        Private slot to show the context menu of the listview.
        
        @param coord the position of the mouse pointer (QPoint)
        """
        self.__menu.popup(self.mapToGlobal(coord))
        
    def __eraseProfile(self):
        """
        Private slot to handle the Erase Profile context menu action.
        """
        fname = "%s.profile" % self.basename
        if os.path.exists(fname):
            os.remove(fname)
        
    def __eraseTiming(self):
        """
        Private slot to handle the Erase Timing context menu action.
        """
        fname = "%s.timings" % self.basename
        if os.path.exists(fname):
            os.remove(fname)
        
    def __eraseAll(self):
        """
        Private slot to handle the Erase All context menu action.
        """
        self.__eraseProfile()
        self.__eraseTiming()
        
    def __filter(self):
        """
        Private slot to handle the Exclude/Include Python Library context menu action.
        """
        self.__unfinish()
        if self.exclude:
            self.exclude = False
            self.filterItm.setText(self.trUtf8('Include Python Library'))
            self.__populateLists(True)
        else:
            self.exclude = True
            self.filterItm.setText(self.trUtf8('Exclude Python Library'))
            self.__populateLists(False)
        self.__finish()
