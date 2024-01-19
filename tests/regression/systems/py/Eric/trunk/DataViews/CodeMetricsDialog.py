# -*- coding: utf-8 -*-

# Copyright (c) 2003 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a code metrics dialog.
"""

import sys
import os
import types

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from Ui_CodeMetricsDialog import Ui_CodeMetricsDialog
import CodeMetrics
import Utilities

class CodeMetricsDialog(QDialog, Ui_CodeMetricsDialog):
    """
    Class implementing a dialog to display the code metrics.
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
        
        self.summaryList.headerItem().setText(self.summaryList.columnCount(), "")
        self.summaryList.header().resizeSection(0, 200)
        self.summaryList.header().resizeSection(1, 100)
        
        self.resultList.headerItem().setText(self.resultList.columnCount(), "")
        
        self.cancelled = False
        
        self.__menu = QMenu(self)
        self.__menu.addAction(self.trUtf8("Collapse all"), self.__resultCollapse)
        self.__menu.addAction(self.trUtf8("Expand all"), self.__resultExpand)
        self.resultList.setContextMenuPolicy(Qt.CustomContextMenu)
        self.connect(self.resultList, 
                     SIGNAL('customContextMenuRequested(const QPoint &)'),
                     self.__showContextMenu)
        
    def __resizeResultColumns(self):
        """
        Private method to resize the list columns.
        """
        self.resultList.header().resizeSections(QHeaderView.ResizeToContents)
        self.resultList.header().setStretchLastSection(True)
        
    def __createResultItem(self, parent, strings):
        """
        Private slot to create a new item in the result list.
        
        @param parent parent of the new item (QTreeWidget or QTreeWidgetItem)
        @param strings strings to be displayed (QStringList)
        @return the generated item
        """
        itm = QTreeWidgetItem(parent, strings)
        for col in range(1,7):
            itm.setTextAlignment(col, Qt.Alignment(Qt.AlignRight))
        return itm
        
    def __resizeSummaryColumns(self):
        """
        Private method to resize the list columns.
        """
        self.summaryList.doItemsLayout()
        self.summaryList.header().resizeSections(QHeaderView.ResizeToContents)
        self.summaryList.header().setStretchLastSection(True)
        
    def __createSummaryItem(self, col0, col1):
        """
        Private slot to create a new item in the summary list.
        
        @param col0 string for column 0 (string or QString)
        @param col1 string for column 1 (string or QString)
        """
        itm = QTreeWidgetItem(self.summaryList, QStringList() << col0 << col1)
        itm.setTextAlignment(1, Qt.Alignment(Qt.AlignRight))
        
    def start(self, fn):
        """
        Public slot to start the code metrics determination.
        
        @param fn file or list of files or directory to be show
                the code metrics for (string or list of strings)
        """
        loc = QLocale()
        if type(fn) is types.ListType:
            files = fn
        elif os.path.isdir(fn):
            files = Utilities.direntries(fn, True, '*.py', False)
        else:
            files = [fn]
        files.sort()
        # check for missing files
        for f in files[:]:
            if not os.path.exists(f):
                files.remove(f)
        
        self.checkProgress.setMaximum(len(files))
        QApplication.processEvents()
        
        total = {}
        CodeMetrics.summarize(total, 'files', len(files))
        
        progress = 0
        
        try:
            # disable updates of the list for speed
            self.resultList.setUpdatesEnabled(False)
            self.resultList.setSortingEnabled(False)
            
            # now go through all the files
            for file in files:
                if self.cancelled:
                    return
                
                stats = CodeMetrics.analyze(file, total)
                
                v = self.__getValues(loc, stats, 'TOTAL ')
                fitm = self.__createResultItem(self.resultList, QStringList(file) + v)
                
                identifiers = stats.identifiers
                for identifier in identifiers:
                    v = self.__getValues(loc, stats, identifier)
                    
                    self.__createResultItem(fitm, QStringList(identifier) + v)
                self.resultList.expandItem(fitm)
                
                progress += 1
                self.checkProgress.setValue(progress)
                QApplication.processEvents()
        finally:
            # reenable updates of the list
            self.resultList.setSortingEnabled(True)
            self.resultList.setUpdatesEnabled(True)
        self.__resizeResultColumns()
        
        # now do the summary stuff
        docstrings = total['lines'] - total['comments'] - \
                     total['empty lines'] - total['non-commentary lines']
        self.__createSummaryItem(self.trUtf8("files"), loc.toString(total['files']))
        self.__createSummaryItem(self.trUtf8("lines"), loc.toString(total['lines']))
        self.__createSummaryItem(self.trUtf8("bytes"), loc.toString(total['bytes']))
        self.__createSummaryItem(self.trUtf8("comments"), loc.toString(total['comments']))
        self.__createSummaryItem(self.trUtf8("empty lines"), 
                                 loc.toString(total['empty lines']))
        self.__createSummaryItem(self.trUtf8("non-commentary lines"), 
                                 loc.toString(total['non-commentary lines']))
        self.__createSummaryItem(self.trUtf8("documentation lines"), 
                                 loc.toString(docstrings))
        self.__resizeSummaryColumns()
        self.__finish()
        
    def __getValues(self, loc, stats, identifier):
        """
        Private method to extract the code metric values.
        
        @param loc reference to the locale object (QLocale)
        @param stats reference to the code metric statistics object
        @param identifier identifier to get values for
        @return list of values suitable for display (QStringList)
        """
        counters = stats.counters.get(identifier, {})
        v = QStringList()
        for key in ('start', 'end', 'lines', 'nloc', 'comments', 'empty'):
            if counters.get(key, 0):
                v.append(QString("%1").arg(loc.toString(counters[key]), 7, QChar(' ')))
            else:
                v.append('')
        return v
        
    def __finish(self):
        """
        Private slot called when the action finished or the user pressed the button.
        """
        self.cancelled = True
        self.buttonBox.button(QDialogButtonBox.Close).setEnabled(True)
        self.buttonBox.button(QDialogButtonBox.Cancel).setEnabled(False)
        self.buttonBox.button(QDialogButtonBox.Close).setDefault(True)
        
        self.resultList.header().setResizeMode(QHeaderView.Interactive)
        self.summaryList.header().setResizeMode(QHeaderView.Interactive)
        
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
        if self.resultList.topLevelItemCount() > 0:
            self.__menu.popup(self.mapToGlobal(coord))
        
    def __resultCollapse(self):
        """
        Private slot to collapse all entries of the resultlist.
        """
        for index in range(self.resultList.topLevelItemCount()):
            self.resultList.topLevelItem(index).setExpanded(False)
        
    def __resultExpand(self):
        """
        Private slot to expand all entries of the resultlist.
        """
        for index in range(self.resultList.topLevelItemCount()):
            self.resultList.topLevelItem(index).setExpanded(True)
