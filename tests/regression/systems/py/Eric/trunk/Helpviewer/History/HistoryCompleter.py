# -*- coding: utf-8 -*-

# Copyright (c) 2009 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a special completer for the history.
"""

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from HistoryModel import HistoryModel
from HistoryFilterModel import HistoryFilterModel

class HistoryCompletionView(QTableView):
    """
    Class implementing a special completer view for history based completions.
    """
    def __init__(self, parent = None):
        """
        Constructor
        
        @param parent reference to the parent widget (QWidget)
        """
        QTableView.__init__(self, parent)
        
        self.horizontalHeader().hide()
        self.verticalHeader().hide()
        
        self.setShowGrid(False)
        
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setTextElideMode(Qt.ElideRight)
        
        metrics = self.fontMetrics()
        self.verticalHeader().setDefaultSectionSize(metrics.height())
    
    def resizeEvent(self, evt):
        """
        Protected method handling resize events.
        
        @param evt reference to the resize event (QResizeEvent)
        """
        self.horizontalHeader().resizeSection(0, 0.65 * self.width())
        self.horizontalHeader().setStretchLastSection(True)
        
        QTableView.resizeEvent(self, evt)
    
    def sizeHintForRow(self, row):
        """
        Public method to give a size hint for rows.
        
        @param row row number (integer)
        """
        metrics = self.fontMetrics()
        return metrics.height()

class HistoryCompletionModel(QSortFilterProxyModel):
    """
    Class implementing a special model for history based completions.
    """
    HistoryCompletionRole = HistoryFilterModel.MaxRole + 1
    
    def __init__(self, parent = None):
        """
        Constructor
        
        @param parent reference to the parent object (QObject)
        """
        QSortFilterProxyModel.__init__(self, parent)
        
        self.__searchString = QString()
        self.__searchMatcher = QRegExp(QString(), Qt.CaseInsensitive, QRegExp.FixedString)
        self.__wordMatcher = QRegExp(QString(), Qt.CaseInsensitive)
        self.__isValid = False
        
        self.setDynamicSortFilter(True)
    
    def data(self, index, role = Qt.DisplayRole):
        """
        Public method to get data from the model.
        
        @param index index of history entry to get data for (QModelIndex)
        @param role data role (integer)
        @return history entry data (QVariant)
        """
        # If the model is valid, tell QCompleter that everything we have filtered
        # matches what the user typed; if not, nothing matches
        if role == self.HistoryCompletionRole and index.isValid():
            if self.isValid():
                return QVariant(QString("t"))
            else:
                return QVariant(QString("f"))
        
        if role == Qt.DisplayRole:
            if index.column() == 0:
                role = HistoryModel.UrlStringRole
            else:
                role = HistoryModel.TitleRole
        
        return QSortFilterProxyModel.data(self, index, role)
    
    def searchString(self):
        """
        Public method to get the current search string.
        
        @return current search string (QString)
        """
        return QString(self.__searchString)
    
    def setSearchString(self, string):
        """
        Public method to set the current search string.
        
        @param string new search string (QString)
        """
        if string == self.__searchString:
            return
        
        self.__searchString = QString(string)
        self.__searchMatcher.setPattern(self.__searchString)
        self.__wordMatcher.setPattern("\\b" + QRegExp.escape(self.__searchString))
        self.invalidateFilter()
    
    def isValid(self):
        """
        Public method to check the model for validity.
        
        @param flag indicating a valid status (boolean)
        """
        return self.__isValid
    
    def setValid(self, valid):
        """
        Public method to set the model's validity.
        
        @param valid flag indicating the new valid status (boolean)
        """
        if valid == self.__isValid:
            return
        
        self.__isValid = valid
        
        # tell the history completer that the model has changed
        self.emit(SIGNAL("dataChanged(const QModelIndex&, const QModelIndex&)"), 
                  self.index(0, 0), self.index(0, self.rowCount() - 1))
    
    def filterAcceptsRow(self, sourceRow, sourceParent):
        """
        Protected method to determine, if the row is acceptable.
        
        @param sourceRow row number in the source model (integer)
        @param sourceParent index of the source item (QModelIndex)
        @return flag indicating acceptance (boolean)
        """
        # Do a case-insensitive substring match against both the url and title.
        # It's already ensured, that the user doesn't accidentally use regexp
        # metacharacters (s. setSearchString()).
        idx = self.sourceModel().index(sourceRow, 0, sourceParent)
        
        url = self.sourceModel().data(idx, HistoryModel.UrlStringRole).toString()
        if self.__searchMatcher.indexIn(url) != -1:
            return True
        
        title = self.sourceModel().data(idx, HistoryModel.TitleRole).toString()
        if self.__searchMatcher.indexIn(title) != -1:
            return True
        
        return False
    
    def lessThan(self, left, right):
        """
        Protected method used to sort the displayed items.
        
        It implements a special sorting function based on the history entry's 
        frequency giving a bonus to hits that match on a word boundary so that
        e.g. "dot.python-projects.org" is a better result for typing "dot" than
        "slashdot.org". However, it only looks for the string in the host name,
        not the entire URL, since while it makes sense to e.g. give
        "www.phoronix.com" a bonus for "ph", it does NOT make sense to give
        "www.yadda.com/foo.php" the bonus.
        
        @param left index of left item (QModelIndex)
        @param right index of right item (QModelIndex)
        @return true, if left is less than right (boolean)
        """
        frequency_L = \
            self.sourceModel().data(left, HistoryFilterModel.FrequencyRole).toInt()[0]
        url_L = self.sourceModel().data(left, HistoryModel.UrlRole).toUrl().host()
        title_L = self.sourceModel().data(left, HistoryModel.TitleRole).toString()
        
        if self.__wordMatcher.indexIn(url_L) != -1 or \
           self.__wordMatcher.indexIn(title_L) != -1:
            frequency_L *= 2
        
        frequency_R = \
            self.sourceModel().data(right, HistoryFilterModel.FrequencyRole).toInt()[0]
        url_R = self.sourceModel().data(right, HistoryModel.UrlRole).toUrl().host()
        title_R = self.sourceModel().data(right, HistoryModel.TitleRole).toString()
        
        if self.__wordMatcher.indexIn(url_R) != -1 or \
           self.__wordMatcher.indexIn(title_R) != -1:
            frequency_R *= 2
        
        # Sort results in descending frequency-derived score.
        return frequency_R < frequency_L

class HistoryCompleter(QCompleter):
    def __init__(self, model, parent = None):
        """
        Constructor
        
        @param model reference to the model (QAbstractItemModel)
        @param parent reference to the parent object (QObject)
        """
        QCompleter.__init__(self, model, parent)
        
        self.setPopup(HistoryCompletionView())
        
        # Completion should be against the faked role.
        self.setCompletionRole(HistoryCompletionModel.HistoryCompletionRole)
        
        # Since the completion role is faked, advantage of the sorted-model
        # optimizations in QCompleter can be taken.
        self.setCaseSensitivity(Qt.CaseSensitive)
        self.setModelSorting(QCompleter.CaseSensitivelySortedModel)
        
        self.__searchString = QString()
        self.__filterTimer = QTimer()
        self.__filterTimer.setSingleShot(True)
        self.connect(self.__filterTimer, SIGNAL("timeout()"), self.__updateFilter)
    
    def pathFromIndex(self, idx):
        """
        Public method to get a path for a given index.
        
        @param idx reference to the index (QModelIndex)
        @return the actual URL from the history (QString)
        """
        return self.model().data(idx, HistoryModel.UrlStringRole).toString()
    
    def splitPath(self, path):
        """
        Public method to split the given path into strings, that are used to match
        at each level in the model.
        
        @param path path to be split (QString)
        @return list of path elements (QStringList)
        """
        path = QString(path)
        if path == self.__searchString:
            return QStringList("t")
        
        # Queue an update to the search string. Wait a bit, so that if the user
        # is quickly typing, the completer doesn't try to complete until they pause.
        if self.__filterTimer.isActive():
            self.__filterTimer.stop()
        self.__filterTimer.start(150)
        
        # If the previous search results are not a superset of the current
        # search results, tell the model that it is not valid yet.
        if not path.startsWith(self.__searchString):
            self.model().setValid(False)
        
        self.__searchString = path
        
        # The actual filtering is done by the HistoryCompletionModel. Just
        # return a short dummy here so that QCompleter thinks everything matched.
        return QStringList("t")
    
    def __updateFilter(self):
        """
        Private slot to update the search string.
        """
        completionModel = self.model()
        
        # Tell the HistoryCompletionModel about the new search string.
        completionModel.setSearchString(self.__searchString)
        
        # Sort the model.
        completionModel.sort(0)
        
        # Mark it valid.
        completionModel.setValid(True)
        
        # Now update the QCompleter widget, but only if the user is still typing a URL.
        if self.widget() is not None and self.widget().hasFocus():
            self.complete()
