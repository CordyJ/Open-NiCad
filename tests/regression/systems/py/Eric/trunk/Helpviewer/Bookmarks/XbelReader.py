# -*- coding: utf-8 -*-

# Copyright (c) 2009 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a class to read XBEL bookmark files.
"""

from PyQt4.QtCore import *

from BookmarkNode import BookmarkNode

class XmlEntityResolver(QXmlStreamEntityResolver):
    """
    Class implementing an XML entity resolver for bookmark files.
    """
    def resolveUndeclaredEntity(self, entity):
        """
        Public method to resolve undeclared entities.
        
        @param entity entity to be resolved (string or QString)
        @return resolved entity (QString)
        """
        if entity == "nbsp":
            return QString(" ")
        return QString()

class XbelReader(QXmlStreamReader):
    """
    Class implementing a reader object for XBEL bookmark files.
    """
    def __init__(self):
        """
        Constructor
        """
        QXmlStreamReader.__init__(self)
        
        self.__resolver = XmlEntityResolver()
        self.setEntityResolver(self.__resolver)
    
    def read(self, fileNameOrDevice):
        """
        Public method to read an XBEL bookmark file.
        
        @param fileNameOrDevice name of the file to read (string or QString)
            or reference to the device to read (QIODevice)
        @return reference to the root node (BookmarkNode)
        """
        if not isinstance(fileNameOrDevice, QIODevice):
            f = QFile(fileNameOrDevice)
            if not f.exists():
                return BookmarkNode(BookmarkNode.Root)
            f.open(QFile.ReadOnly)
            self.setDevice(f)
        else:
            self.setDevice(fileNameOrDevice)
        
        root = BookmarkNode(BookmarkNode.Root)
        while not self.atEnd():
            self.readNext()
            if self.isStartElement():
                version = self.attributes().value("version").toString()
                if self.name() == "xbel" and \
                   (version.isEmpty() or version == "1.0"):
                    self.__readXBEL(root)
                else:
                    self.raiseError(QCoreApplication.translate(
                        "XbelReader", "The file is not an XBEL version 1.0 file."))
        
        return root
    
    def __readXBEL(self, node):
        """
        Private method to read and parse the XBEL file.
        
        @param node reference to the node to attach to (BookmarkNode)
        """
        if not self.isStartElement() and self.name() != "xbel":
            return
        
        while not self.atEnd():
            self.readNext()
            if self.isEndElement():
                break
            
            if self.isStartElement():
                if self.name() == "folder":
                    self.__readFolder(node)
                elif self.name() == "bookmark":
                    self.__readBookmarkNode(node)
                elif self.name() == "separator":
                    self.__readSeparator(node)
                else:
                    self.__skipUnknownElement()
    
    def __readFolder(self, node):
        """
        Private method to read and parse a folder subtree.
        
        @param node reference to the node to attach to (BookmarkNode)
        """
        if not self.isStartElement() and self.name() != "folder":
            return
        
        folder = BookmarkNode(BookmarkNode.Folder, node)
        folder.expanded = self.attributes().value("folded") == "no"
        
        while not self.atEnd():
            self.readNext()
            if self.isEndElement():
                break
            
            if self.isStartElement():
                if self.name() == "title":
                    self.__readTitle(folder)
                elif self.name() == "desc":
                    self.__readDescription(folder)
                elif self.name() == "folder":
                    self.__readFolder(folder)
                elif self.name() == "bookmark":
                    self.__readBookmarkNode(folder)
                elif self.name() == "separator":
                    self.__readSeparator(folder)
                else:
                    self.__skipUnknownElement()
    
    def __readTitle(self, node):
        """
        Private method to read the title element.
        
        @param node reference to the bookmark node title belongs to (BookmarkNode)
        """
        if not self.isStartElement() and self.name() != "title":
            return
        
        node.title = self.readElementText()
    
    def __readDescription(self, node):
        """
        Private method to read the desc element.
        
        @param node reference to the bookmark node desc belongs to (BookmarkNode)
        """
        if not self.isStartElement() and self.name() != "desc":
            return
        
        node.desc = self.readElementText()
    
    def __readSeparator(self, node):
        """
        Private method to read a separator element.
        
        @param node reference to the bookmark node the separator belongs to (BookmarkNode)
        """
        BookmarkNode(BookmarkNode.Separator, node)
        # empty elements have a start and end element
        self.readNext()
    
    def __readBookmarkNode(self, node):
        """
        Private method to read and parse a bookmark subtree.
        
        @param node reference to the node to attach to (BookmarkNode)
        """
        if not self.isStartElement() and self.name() != "bookmark":
            return
        
        bookmark = BookmarkNode(BookmarkNode.Bookmark, node)
        bookmark.url = self.attributes().value("href").toString()
        
        while not self.atEnd():
            self.readNext()
            if self.isEndElement():
                break
            
            if self.isStartElement():
                if self.name() == "title":
                    self.__readTitle(bookmark)
                elif self.name() == "desc":
                    self.__readDescription(bookmark)
                else:
                    self.__skipUnknownElement()
        
        if bookmark.title.isEmpty():
            bookmark.title = QCoreApplication.translate("XbelReader", "Unknown title")
    
    def __skipUnknownElement(self):
        """
        Private method to skip over all unknown elements.
        """
        if not self.isStartElement():
            return
        
        while not self.atEnd():
            self.readNext()
            if self.isEndElement():
                break
            
            if self.isStartElement():
                self.__skipUnknownElement()
