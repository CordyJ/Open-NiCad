# -*- coding: utf-8 -*-

# Copyright (c) 2009 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the bookmarks manager.
"""

import os

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtWebKit import QWebPage

from KdeQt import KQMessageBox, KQFileDialog

from BookmarkNode import BookmarkNode
from BookmarksModel import BookmarksModel
from DefaultBookmarks import DefaultBookmarks
from XbelReader import XbelReader
from XbelWriter import XbelWriter

from Utilities.AutoSaver import AutoSaver
import Utilities
import Preferences

BOOKMARKBAR  = QT_TRANSLATE_NOOP("BookmarksManager", "Bookmarks Bar")
BOOKMARKMENU = QT_TRANSLATE_NOOP("BookmarksManager", "Bookmarks Menu")

##########################################################################################

extract_js = r"""
function walk() {
    var parent = arguments[0];
    var indent = arguments[1];

    var result = "";
    var children = parent.childNodes;
    var folderName = "";
    var folded = "";
    for (var i = 0; i < children.length; i++) {
        var object = children.item(i);
        if (object.nodeName == "HR") {
            result += indent + "<separator/>\n";
        }
        if (object.nodeName == "H3") {
            folderName = object.innerHTML;
            folded = object.folded;
            if (object.folded == undefined)
                folded = "false";
            else
                folded = "true";
        }
        if (object.nodeName == "A") {
            result += indent + "<bookmark href=\"" + encodeURI(object.href).replace(/&/g, '&amp;') + "\">\n";
            result += indent + indent + "<title>" + object.innerHTML + "</title>\n";
            result += indent + "</bookmark>\n";
        }

        var currentIndent = indent;
        if (object.nodeName == "DL" && folderName != "") {
            result += indent + "<folder folded=\"" + folded + "\">\n";
            indent += "    ";
            result += indent + "<title>" + folderName + "</title>\n";
        }
        result += walk(object, indent);
        if (object.nodeName == "DL" && folderName != "") {
            result += currentIndent + "</folder>\n";
        }
    }
    return result;
}

var xbel = walk(document, "    ");

if (xbel != "") {
    xbel = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<!DOCTYPE xbel>\n<xbel version=\"1.0\">\n" + xbel + "</xbel>\n";
}

xbel;
"""

##########################################################################################

class BookmarksManager(QObject):
    """
    Class implementing the bookmarks manager.
    
    @signal entryAdded emitted after a bookmark node has been added
    @signal entryRemoved emitted after a bookmark
        node has been removed
    @signal entryChanged emitted after a bookmark node has been changed
    """
    def __init__(self, parent = None):
        """
        Constructor
        
        @param parent reference to the parent object (QObject)
        """
        QObject.__init__(self, parent)
        
        self.__loaded = False
        self.__saveTimer = AutoSaver(self, self.save)
        self.__bookmarkRootNode = None
        self.__toolbar = None
        self.__menu = None
        self.__bookmarksModel = None
        self.__commands = QUndoStack()
        
        self.connect(self, SIGNAL("entryAdded"), 
                     self.__saveTimer.changeOccurred)
        self.connect(self, SIGNAL("entryRemoved"), 
                     self.__saveTimer.changeOccurred)
        self.connect(self, SIGNAL("entryChanged"), 
                     self.__saveTimer.changeOccurred)
    
    def close(self):
        """
        Public method to close the bookmark manager.
        """
        self.__saveTimer.saveIfNeccessary()
    
    def undoRedoStack(self):
        """
        Public method to get a reference to the undo stack.
        
        @return reference to the undo stack (QUndoStack)
        """
        return self.__commands
    
    def changeExpanded(self):
        """
        Public method to handle a change of the expanded state.
        """
        self.__saveTimer.changeOccurred()
    
    def load(self):
        """
        Public method to load the bookmarks.
        """
        if self.__loaded:
            return
        
        self.__loaded = True
        
        bookmarkFile = os.path.join(Utilities.getConfigDir(), "browser", "bookmarks.xbel")
        if not QFile.exists(bookmarkFile):
            ba = QByteArray(DefaultBookmarks)
            bookmarkFile = QBuffer(ba)
            bookmarkFile.open(QIODevice.ReadOnly)
        
        reader = XbelReader()
        self.__bookmarkRootNode = reader.read(bookmarkFile)
        if reader.error() != QXmlStreamReader.NoError:
            KQMessageBox.warning(None,
                self.trUtf8("Loading Bookmarks"),
                self.trUtf8("""Error when loading bookmarks on line %1, column %2:\n"""
                            """%3""")\
                    .arg(reader.lineNumber())\
                    .arg(reader.columnNumber())\
                    .arg(reader.errorString()))
        
        others = []
        for index in range(len(self.__bookmarkRootNode.children()) - 1, -1, -1):
            node = self.__bookmarkRootNode.children()[index]
            if node.type() == BookmarkNode.Folder:
                if (node.title == self.trUtf8("Toolbar Bookmarks") or \
                    node.title == BOOKMARKBAR) and \
                   self.__toolbar is None:
                    node.title = self.trUtf8(BOOKMARKBAR)
                    self.__toolbar = node
                
                if (node.title == self.trUtf8("Menu") or \
                    node.title == BOOKMARKMENU) and \
                   self.__menu is None:
                    node.title = self.trUtf8(BOOKMARKMENU)
                    self.__menu = node
            else:
                others.append(node)
            self.__bookmarkRootNode.remove(node)
            
        if len(self.__bookmarkRootNode.children()) > 0:
            raise RuntimeError("Error loading bookmarks.")
        
        if self.__toolbar is None:
            self.__toolbar = BookmarkNode(BookmarkNode.Folder, self.__bookmarkRootNode)
            self.__toolbar.title = self.trUtf8(BOOKMARKBAR)
        else:
            self.__bookmarkRootNode.add(self.__toolbar)
        
        if self.__menu is None:
            self.__menu = BookmarkNode(BookmarkNode.Folder, self.__bookmarkRootNode)
            self.__menu.title = self.trUtf8(BOOKMARKMENU)
        else:
            self.__bookmarkRootNode.add(self.__menu)
        
        for node in others:
            self.__menu.add(node)
        
        self.__convertFromOldBookmarks()
    
    def save(self):
        """
        Public method to save the bookmarks.
        """
        if not self.__loaded:
            return
        
        writer = XbelWriter()
        bookmarkFile = os.path.join(Utilities.getConfigDir(), "browser", "bookmarks.xbel")
        
        # save root folder titles in English (i.e. not localized)
        self.__menu.title = BOOKMARKMENU
        self.__toolbar.title = BOOKMARKBAR
        if not writer.write(bookmarkFile, self.__bookmarkRootNode):
            KQMessageBox.warning(None,
                self.trUtf8("Saving Bookmarks"),
                self.trUtf8("""Error saving bookmarks to <b>%1</b>.""").arg(bookmarkFile))
        
        # restore localized titles
        self.__menu.title = self.trUtf8(BOOKMARKMENU)
        self.__toolbar.title = self.trUtf8(BOOKMARKBAR)
    
    def addBookmark(self, parent, node, row = -1):
        """
        Public method to add a bookmark.
        
        @param parent reference to the node to add to (BookmarkNode)
        @param node reference to the node to add (BookmarkNode)
        @param row row number (integer)
        """
        if not self.__loaded:
            return
        
        command = InsertBookmarksCommand(self, parent, node, row)
        self.__commands.push(command)
    
    def removeBookmark(self, node):
        """
        Public method to remove a bookmark.
        
        @param node reference to the node to be removed (BookmarkNode)
        """
        if not self.__loaded:
            return
        
        parent = node.parent()
        row = parent.children().index(node)
        command = RemoveBookmarksCommand(self, parent, row)
        self.__commands.push(command)
    
    def setTitle(self, node, newTitle):
        """
        Public method to set the title of a bookmark.
        
        @param node reference to the node to be changed (BookmarkNode)
        @param newTitle title to be set (QString)
        """
        if not self.__loaded:
            return
        
        command = ChangeBookmarkCommand(self, node, newTitle, True)
        self.__commands.push(command)
    
    def setUrl(self, node, newUrl):
        """
        Public method to set the URL of a bookmark.
        
        @param node reference to the node to be changed (BookmarkNode)
        @param newUrl URL to be set (QString)
        """
        if not self.__loaded:
            return
        
        command = ChangeBookmarkCommand(self, node, newUrl, False)
        self.__commands.push(command)
    
    def bookmarks(self):
        """
        Public method to get a reference to the root bookmark node.
        
        @return reference to the root bookmark node (BookmarkNode)
        """
        if not self.__loaded:
            self.load()
        
        return self.__bookmarkRootNode
    
    def menu(self):
        """
        Public method to get a reference to the bookmarks menu node.
        
        @return reference to the bookmarks menu node (BookmarkNode)
        """
        if not self.__loaded:
            self.load()
        
        return self.__menu
    
    def toolbar(self):
        """
        Public method to get a reference to the bookmarks toolbar node.
        
        @return reference to the bookmarks toolbar node (BookmarkNode)
        """
        if not self.__loaded:
            self.load()
        
        return self.__toolbar
    
    def bookmarksModel(self):
        """
        Public method to get a reference to the bookmarks model.
        
        @return reference to the bookmarks model (BookmarksModel)
        """
        if self.__bookmarksModel is None:
            self.__bookmarksModel = BookmarksModel(self, self)
        return self.__bookmarksModel
    
    def importBookmarks(self):
        """
        Public method to import bookmarks.
        """
        supportedFormats = QStringList() \
            << self.trUtf8("XBEL bookmarks").append(" (*.xbel *.xml)") \
            << self.trUtf8("HTML Netscape bookmarks").append(" (*.html)")
        
        fileName = KQFileDialog.getOpenFileName(\
            None,
            self.trUtf8("Import Bookmarks"),
            QString(),
            supportedFormats.join(";;"),
            None)
        if fileName.isEmpty():
            return
        
        reader = XbelReader()
        importRootNode = None
        if fileName.endsWith(".html"):
            inFile = QFile(fileName)
            inFile.open(QIODevice.ReadOnly)
            if inFile.openMode == QIODevice.NotOpen:
                KQMessageBox.warning(None,
                    self.trUtf8("Import Bookmarks"),
                    self.trUtf8("""Error opening bookmarks file <b>%1</b>.""")\
                        .arg(fileName))
                return
            
            webpage = QWebPage()
            webpage.mainFrame().setHtml(QString(inFile.readAll()))
            result = webpage.mainFrame().evaluateJavaScript(extract_js).toByteArray()
            buffer_ = QBuffer(result)
            buffer_.open(QIODevice.ReadOnly)
            importRootNode = reader.read(buffer_)
        else:
            importRootNode = reader.read(fileName)
        
        if reader.error() != QXmlStreamReader.NoError:
            KQMessageBox.warning(None,
                self.trUtf8("Import Bookmarks"),
                self.trUtf8("""Error when importing bookmarks on line %1, column %2:\n"""
                            """%3""")\
                    .arg(reader.lineNumber())\
                    .arg(reader.columnNumber())\
                    .arg(reader.errorString()))
            return
        
        importRootNode.setType(BookmarkNode.Folder)
        importRootNode.title = self.trUtf8("Imported %1")\
            .arg(QDate.currentDate().toString(Qt.SystemLocaleShortDate))
        self.addBookmark(self.menu(), importRootNode)
    
    def exportBookmarks(self):
        """
        Public method to export the bookmarks.
        """
        fileName = KQFileDialog.getSaveFileName(\
            None,
            self.trUtf8("Export Bookmarks"),
            "eric4_bookmarks.xbel",
            self.trUtf8("XBEL bookmarks").append(" (*.xbel, *.xml)"))
        if fileName.isEmpty():
            return
        
        writer = XbelWriter()
        if not writer.write(fileName, self.__bookmarkRootNode):
            KQMessageBox.critical(None,
                self.trUtf8("Exporting Bookmarks"),
                self.trUtf8("""Error exporting bookmarks to <b>%1</b>.""")\
                    .arg(bookmarkFile))
    
    def __convertFromOldBookmarks(self):
        """
        Private method to convert the old bookmarks into the new ones.
        """
        bmNames = Preferences.Prefs.settings.value('Bookmarks/Names')
        bmFiles = Preferences.Prefs.settings.value('Bookmarks/Files')
        
        if bmNames.isValid() and bmFiles.isValid():
            bmNames = bmNames.toStringList()
            bmFiles = bmFiles.toStringList()
            if len(bmNames) == len(bmFiles):
                convertedRootNode = BookmarkNode(BookmarkNode.Folder)
                convertedRootNode.title = self.trUtf8("Converted %1")\
                    .arg(QDate.currentDate().toString(Qt.SystemLocaleShortDate))
                for i in range(len(bmNames)):
                    node = BookmarkNode(BookmarkNode.Bookmark, convertedRootNode)
                    node.title = bmNames[i]
                    url = QUrl(bmFiles[i])
                    if url.scheme().isEmpty():
                        url.setScheme("file")
                    node.url = url.toString()
                self.addBookmark(self.menu(), convertedRootNode)
                
                Preferences.Prefs.settings.remove('Bookmarks')

class RemoveBookmarksCommand(QUndoCommand):
    """
    Class implementing the Remove undo command.
    """
    def __init__(self, bookmarksManager, parent, row):
        """
        Constructor
        
        @param bookmarksManager reference to the bookmarks manager (BookmarksManager)
        @param parent reference to the parent node (BookmarkNode)
        @param row row number of bookmark (integer)
        """
        QUndoCommand.__init__(self, 
            QApplication.translate("BookmarksManager", "Remove Bookmark"))
        
        self._row = row
        self._bookmarksManager = bookmarksManager
        try:
            self._node = parent.children()[row]
        except IndexError:
            self._node = BookmarkNode()
        self._parent = parent
    
    def undo(self):
        """
        Public slot to perform the undo action.
        """
        self._parent.add(self._node, self._row)
        self._bookmarksManager.emit(SIGNAL("entryAdded"), self._node)
    
    def redo(self):
        """
        Public slot to perform the redo action.
        """
        self._parent.remove(self._node)
        self._bookmarksManager.emit(
            SIGNAL("entryRemoved"), 
            self._parent, self._row, self._node)

class InsertBookmarksCommand(RemoveBookmarksCommand):
    """
    Class implementing the Insert undo command.
    """
    def __init__(self, bookmarksManager, parent, node, row):
        """
        Constructor
        
        @param bookmarksManager reference to the bookmarks manager (BookmarksManager)
        @param parent reference to the parent node (BookmarkNode)
        @param node reference to the node to be inserted (BookmarkNode)
        @param row row number of bookmark (integer)
        """
        RemoveBookmarksCommand.__init__(self, bookmarksManager, parent, row)
        self.setText(QApplication.translate("BookmarksManager", "Insert Bookmark"))
        self._node = node
    
    def undo(self):
        """
        Public slot to perform the undo action.
        """
        RemoveBookmarksCommand.redo(self)
    
    def redo(self):
        """
        Public slot to perform the redo action.
        """
        RemoveBookmarksCommand.undo(self)

class ChangeBookmarkCommand(QUndoCommand):
    """
    Class implementing the Insert undo command.
    """
    def __init__(self, bookmarksManager, node, newValue, title):
        """
        Constructor
        
        @param bookmarksManager reference to the bookmarks manager (BookmarksManager)
        @param node reference to the node to be changed (BookmarkNode)
        @param newValue new value to be set (QString)
        @param title flag indicating a change of the title (True) or 
            the URL (False) (boolean)
        """
        QUndoCommand.__init__(self)
        
        self._bookmarksManager = bookmarksManager
        self._title = title
        self._newValue = newValue
        self._node = node
        
        if self._title:
            self._oldValue = self._node.title
            self.setText(QApplication.translate("BookmarksManager", "Name Change"))
        else:
            self._oldValue = self._node.url
            self.setText(QApplication.translate("BookmarksManager", "Address Change"))
    
    def undo(self):
        """
        Public slot to perform the undo action.
        """
        if self._title:
            self._node.title = self._oldValue
        else:
            self._node.url = self._oldValue
        self._bookmarksManager.emit(SIGNAL("entryChanged"), self._node)
    
    def redo(self):
        """
        Public slot to perform the redo action.
        """
        if self._title:
            self._node.title = self._newValue
        else:
            self._node.url = self._newValue
        self._bookmarksManager.emit(SIGNAL("entryChanged"), self._node)
