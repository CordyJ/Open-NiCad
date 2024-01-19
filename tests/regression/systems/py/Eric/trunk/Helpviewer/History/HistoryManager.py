# -*- coding: utf-8 -*-

# Copyright (c) 2009 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the history manager.
"""

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtWebKit import QWebHistoryInterface, QWebSettings

from KdeQt import KQMessageBox

from HistoryModel import HistoryModel
from HistoryFilterModel import HistoryFilterModel
from HistoryTreeModel import HistoryTreeModel

from Utilities.AutoSaver import AutoSaver
import Utilities
import Preferences

HISTORY_VERSION = 42

class HistoryEntry(object):
    """
    Class implementing a history entry.
    """
    def __init__(self, url = None, dateTime = None, title = None):
        """
        Constructor
        
        @param url URL of the history entry (QString)
        @param dateTime date and time this entry was created (QDateTime)
        @param title title string for the history entry (QString)
        """
        self.url = url and url or QString()
        self.dateTime = dateTime and dateTime or QDateTime()
        self.title = title and title or QString()
    
    def __eq__(self, other):
        """
        Special method determining equality.
        
        @param other reference to the history entry to compare against (HistoryEntry)
        @return flag indicating equality (boolean)
        """
        return other.title == self.title and \
            other.url == self.url and \
            other.dateTime == self.dateTime
    
    def __lt__(self, other):
        """
        Special method determining less relation.
        
        Note: History is sorted in reverse order by date and time
        
        @param other reference to the history entry to compare against (HistoryEntry)
        @return flag indicating less (boolean)
        """
        return self.dateTime > other.dateTime
    
    def userTitle(self):
        """
        Public method to get the title of the history entry.
        
        @return title of the entry (QString)
        """
        if self.title.isEmpty():
            page = QFileInfo(QUrl(self.url).path()).fileName()
            if not page.isEmpty():
                return page
            return self.url
        return self.title

class HistoryManager(QWebHistoryInterface):
    """
    Class implementing the history manager.
    
    @signal historyCleared() emitted after the history has been cleared
    @signal historyReset() emitted after the history has been reset
    @signal entryAdded emitted after a history entry has been added
    @signal entryRemoved emitted after a history entry has been removed
    @signal entryUpdated(int) emitted after a history entry has been updated
    """
    def __init__(self, parent = None):
        """
        Constructor
        
        @param parent reference to the parent object (QObject)
        """
        QWebHistoryInterface.__init__(self, parent)
        
        self.__saveTimer = AutoSaver(self, self.save)
        self.__daysToExpire = Preferences.getHelp("HistoryLimit")
        self.__history = []
        self.__lastSavedUrl = QString()
        
        self.__expiredTimer = QTimer()
        self.__expiredTimer.setSingleShot(True)
        self.connect(self.__expiredTimer, SIGNAL("timeout()"), 
                     self.__checkForExpired)
        
        self.__frequencyTimer = QTimer()
        self.__frequencyTimer.setSingleShot(True)
        self.connect(self.__frequencyTimer, SIGNAL("timeout()"), 
                     self.__refreshFrequencies)
        
        self.connect(self, SIGNAL("entryAdded"), 
                     self.__saveTimer.changeOccurred)
        self.connect(self, SIGNAL("entryRemoved"), 
                     self.__saveTimer.changeOccurred)
        
        self.__load()
        
        self.__historyModel = HistoryModel(self, self)
        self.__historyFilterModel = HistoryFilterModel(self.__historyModel, self)
        self.__historyTreeModel = HistoryTreeModel(self.__historyFilterModel, self)
        
        QWebHistoryInterface.setDefaultInterface(self)
        self.__startFrequencyTimer()
    
    def close(self):
        """
        Public method to close the history manager.
        """
        # remove history items on application exit
        if self.__daysToExpire == -2:
            self.clear()
        self.__saveTimer.saveIfNeccessary()
    
    def history(self):
        """
        Public method to return the history.
        
        @return reference to the list of history entries (list of HistoryEntry)
        """
        return self.__history[:]
    
    def setHistory(self, history, loadedAndSorted = False):
        """
        Public method to set a new history.
        
        @param history reference to the list of history entries to be set
            (list of HistoryEntry)
        @param loadedAndSorted flag indicating that the list is sorted (boolean)
        """
        self.__history = history[:]
        if not loadedAndSorted:
            self.__history.sort()
        
        self.__checkForExpired()
        
        if loadedAndSorted:
            try:
                self.__lastSavedUrl = QString(self.__history[0].url)
            except IndexError:
                self.__lastSavedUrl = QString()
        else:
            self.__lastSavedUrl.clear()
            self.__saveTimer.changeOccurred()
        self.emit(SIGNAL("historyReset()"))
    
    def historyContains(self, url):
        """
        Public method to check the history for an entry.
        
        @param url URL to check for (QString)
        @return flag indicating success (boolean)
        """
        return self.__historyFilterModel.historyContains(url)
    
    def _addHistoryEntry(self, itm):
        """
        Protected method to add a history item.
        
        @param itm reference to the history item to add (HistoryEntry)
        """
        globalSettings = QWebSettings.globalSettings()
        if globalSettings.testAttribute(QWebSettings.PrivateBrowsingEnabled):
            return
        
        self.__history.insert(0, itm)
        self.emit(SIGNAL("entryAdded"), itm)
        if len(self.__history) == 1:
            self.__checkForExpired()
    
    def _removeHistoryEntry(self, itm):
        """
        Protected method to remove a history item.
        
        @param itm reference to the history item to remove (HistoryEntry)
        """
        self.__lastSavedUrl.clear()
        self.__history.remove(itm)
        self.emit(SIGNAL("entryRemoved"), itm)
    
    def addHistoryEntry(self, url):
        """
        Public method to add a history entry.
        
        @param url URL to be added (QString)
        """
        cleanurl = QUrl(url)
        cleanurl.setPassword("")
        cleanurl.setHost(cleanurl.host().toLower())
        itm = HistoryEntry(cleanurl.toString(), QDateTime.currentDateTime())
        self._addHistoryEntry(itm)
    
    def updateHistoryEntry(self, url, title):
        """
        Public method to update a history entry.
        
        @param url URL of the entry to update (QString)
        @param title title of the entry to update (QString)
        """
        for index in range(len(self.__history)):
            if url == self.__history[index].url:
                self.__history[index].title = title
                self.__saveTimer.changeOccurred()
                if self.__lastSavedUrl.isEmpty():
                    self.__lastSavedUrl = QString(self.__history[index].url)
                self.emit(SIGNAL("entryUpdated(int)"), index)
                break
    
    def removeHistoryEntry(self, url, title = QString()):
        """
        Public method to remove a history entry.
        
        @param url URL of the entry to remove (QUrl)
        @param title title of the entry to remove (QString)
        """
        for index in range(len(self.__history)):
            if url == QUrl(self.__history[index].url) and \
               (title.isEmpty() or title == self.__history[index].title):
                self._removeHistoryEntry(self.__history[index])
                break
    
    def historyModel(self):
        """
        Public method to get a reference to the history model.
        
        @return reference to the history model (HistoryModel)
        """
        return self.__historyModel
    
    def historyFilterModel(self):
        """
        Public method to get a reference to the history filter model.
        
        @return reference to the history filter model (HistoryFilterModel)
        """
        return self.__historyFilterModel
    
    def historyTreeModel(self):
        """
        Public method to get a reference to the history tree model.
        
        @return reference to the history tree model (HistoryTreeModel)
        """
        return self.__historyTreeModel
    
    def __checkForExpired(self):
        """
        Private slot to check entries for expiration.
        """
        if self.__daysToExpire < 0 or len(self.__history) == 0:
            return
        
        now = QDateTime.currentDateTime()
        nextTimeout = 0
        
        while self.__history:
            checkForExpired = QDateTime(self.__history[-1].dateTime)
            checkForExpired.setDate(checkForExpired.date().addDays(self.__daysToExpire))
            if now.daysTo(checkForExpired) > 7:
                nextTimeout = 7 * 86400
            else:
                nextTimeout = now.secsTo(checkForExpired)
            if nextTimeout > 0:
                break
            
            itm = self.__history.pop(-1)
            self.__lastSavedUrl.clear()
            self.emit(SIGNAL("entryRemoved"), itm)
        self.__saveTimer.saveIfNeccessary()
        
        if nextTimeout > 0:
            self.__expiredTimer.start(nextTimeout * 1000)
    
    def daysToExpire(self):
        """
        Public method to get the days for entry expiration.
        
        @return days for entry expiration (integer)
        """
        return self.__daysToExpire
    
    def setDaysToExpire(self, limit):
        """
        Public method to set the days for entry expiration.
        
        @param limit days for entry expiration (integer)
        """
        if self.__daysToExpire == limit:
            return
        
        self.__daysToExpire = limit
        self.__checkForExpired()
        self.__saveTimer.changeOccurred()
    
    def preferencesChanged(self):
        """
        Public method to indicate a change of preferences.
        """
        self.setDaysToExpire(Preferences.getHelp("HistoryLimit"))
    
    def clear(self):
        """
        Public slot to clear the complete history.
        """
        self.__history = []
        self.__lastSavedUrl.clear()
        self.__saveTimer.changeOccurred()
        self.__saveTimer.saveIfNeccessary()
        self.emit(SIGNAL("historyReset()"))
        self.emit(SIGNAL("historyCleared()"))
    
    def __load(self):
        """
        Private method to load the saved history entries from disk.
        """
        historyFile = QFile(Utilities.getConfigDir() + "/browser/history")
        if not historyFile.exists():
            return
        if not historyFile.open(QIODevice.ReadOnly):
            KQMessageBox.warning(None,
                self.trUtf8("Loading History"),
                self.trUtf8("""Unable to open history file <b>%1</b>.<br/>Reason: %2""")\
                    .arg(historyFile.fileName).arg(historyFile.errorString()))
            return
        
        history = []
        historyStream = QDataStream(historyFile)
        
        # double check, that the history file is sorted as it is read
        needToSort = False
        lastInsertedItem = HistoryEntry()
        data = QByteArray()
        stream = QDataStream()
        buffer = QBuffer()
        stream.setDevice(buffer)
        while not historyFile.atEnd():
            historyStream >> data
            buffer.close()
            buffer.setBuffer(data)
            buffer.open(QIODevice.ReadOnly)
            ver = stream.readUInt32()
            if ver != HISTORY_VERSION:
                continue
            itm = HistoryEntry()
            stream >> itm.url
            stream >> itm.dateTime
            stream >> itm.title
            
            if not itm.dateTime.isValid():
                continue
            
            if itm == lastInsertedItem:
                if lastInsertedItem.title.isEmpty() and len(history) > 0:
                    history[0].title = itm.title
                continue
            
            if not needToSort and history and lastInsertedItem < itm:
                needToSort = True
            
            history.insert(0, itm)
            lastInsertedItem = itm
        
        if needToSort:
            history.sort()
        
        self.setHistory(history, True)
        
        # if the history had to be sorted, rewrite the history sorted
        if needToSort:
            self.__lastSavedUrl.clear()
            self.__saveTimer.changeOccurred()
    
    def save(self):
        """
        Public slot to save the history entries to disk.
        """
        historyFile = QFile(Utilities.getConfigDir() + "/browser/history")
        if not historyFile.exists():
            self.__lastSavedUrl.clear()
        
        saveAll = self.__lastSavedUrl.isEmpty()
        first = len(self.__history) - 1
        if not saveAll:
            # find the first one to save
            for index in range(len(self.__history)):
                if self.__history[index].url == self.__lastSavedUrl:
                    first = index - 1
                    break
        if first == len(self.__history) - 1:
            saveAll = True
        
        # use a temporary file when saving everything
        tempFile = QTemporaryFile()
        tempFile.setAutoRemove(False)
        if saveAll:
            opened = tempFile.open()
        else:
            opened = historyFile.open(QIODevice.Append)
        
        if not opened:
            if saveAll:
                f = tempFile
            else:
                f = historyFile
            KQMessageBox.warning(None,
                self.trUtf8("Saving History"),
                self.trUtf8("""Unable to open history file <b>%1</b>.<br/>Reason: %2""")\
                    .arg(f.fileName()).arg(f.errorString()))
            return
        
        if saveAll:
            historyStream = QDataStream(tempFile)
        else:
            historyStream = QDataStream(historyFile)
        for index in range(first, -1, -1):
            data = QByteArray()
            stream = QDataStream(data, QIODevice.WriteOnly)
            itm = self.__history[index]
            stream.writeUInt32(HISTORY_VERSION)
            stream << itm.url
            stream << itm.dateTime
            stream << itm.title
            historyStream << data
        
        if saveAll:
            tempFile.close()
            if historyFile.exists() and not historyFile.remove():
                KQMessageBox.warning(None,
                    self.trUtf8("Saving History"),
                    self.trUtf8("""Error removing old history file <b>%1</b>."""
                                """<br/>Reason: %2""")\
                        .arg(historyFile.fileName()).arg(historyFile.errorString()))
            if not tempFile.copy(historyFile.fileName()):
                KQMessageBox.warning(None,
                    self.trUtf8("Saving History"),
                    self.trUtf8("""Error moving new history file over old one """
                                """(<b>%1</b>).<br/>Reason: %2""")\
                        .arg(historyFile.fileName()).arg(tempFile.errorString()))
        else:
            historyFile.close()
        
        try:
            self.__lastSavedUrl = QString(self.__history[0].url)
        except IndexError:
            self.__lastSavedUrl = QString()
    
    def __refreshFrequencies(self):
        """
        Private slot to recalculate the refresh frequencies.
        """
        self.__historyFilterModel.recalculateFrequencies()
        self.__startFrequencyTimer()
    
    def __startFrequencyTimer(self):
        """
        Private method to start the timer to recalculate the frequencies.
        """
        tomorrow = QDateTime(QDate.currentDate().addDays(1), QTime(3, 0))
        self.__frequencyTimer.start(QDateTime.currentDateTime().secsTo(tomorrow) * 1000)
