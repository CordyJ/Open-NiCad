# -*- coding: utf-8 -*-

# Copyright (c) 2009 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a class to write XBEL bookmark files.
"""

from PyQt4.QtCore import *

from BookmarkNode import BookmarkNode

class XbelWriter(QXmlStreamWriter):
    """
    Class implementing a writer object to generate XBEL bookmark files.
    """
    def __init__(self):
        """
        Constructor
        """
        QXmlStreamWriter.__init__(self)
        
        self.setAutoFormatting(True)
    
    def write(self, fileNameOrDevice, root):
        """
        Public method to write an XBEL bookmark file.
        
        @param fileNameOrDevice name of the file to write (string or QString)
            or device to write to (QIODevice)
        @param root root node of the bookmark tree (BookmarkNode)
        """
        if isinstance(fileNameOrDevice, QIODevice):
            f = fileNameOrDevice
        else:
            f = QFile(fileNameOrDevice)
            if root is None or not f.open(QFile.WriteOnly):
                return False
        
        self.setDevice(f)
        return self.__write(root)
    
    def __write(self, root):
        """
        Private method to write an XBEL bookmark file.
        
        @param root root node of the bookmark tree (BookmarkNode)
        """
        self.writeStartDocument()
        self.writeDTD("<!DOCTYPE xbel>")
        self.writeStartElement("xbel")
        self.writeAttribute("version", "1.0")
        if root.type() == BookmarkNode.Root:
            for child in root.children():
                self.__writeItem(child)
        else:
            self.__writeItem(root)
        
        self.writeEndDocument()
        return True
    
    def __writeItem(self, node):
        """
        Private method to write an entry for a node.
        
        @param node reference to the node to be written (BookmarkNode)
        """
        if node.type() == BookmarkNode.Folder:
            self.writeStartElement("folder")
            self.writeAttribute("folded", node.expanded and "no" or "yes")
            self.writeTextElement("title", node.title)
            for child in node.children():
                self.__writeItem(child)
            self.writeEndElement()
        elif node.type() == BookmarkNode.Bookmark:
            self.writeStartElement("bookmark")
            if not node.url.isEmpty():
                self.writeAttribute("href", node.url)
            self.writeTextElement("title", node.title)
            if not node.desc.isEmpty():
                self.writeTextElement("desc", node.desc)
            self.writeEndElement()
        elif node.type() == BookmarkNode.Separator:
            self.writeEmptyElement("separator")
