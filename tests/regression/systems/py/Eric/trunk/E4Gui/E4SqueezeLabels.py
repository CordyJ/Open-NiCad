# -*- coding: utf-8 -*-

# Copyright (c) 2008 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing labels that squeeze their contents to fit the size of the label.
"""

from PyQt4.QtCore import Qt, QString
from PyQt4.QtGui import QLabel

from Utilities import compactPath

class E4SqueezeLabel(QLabel):
    """
    Class implementing a label that squeezes its contents to fit it's size.
    """
    def __init__(self, parent = None):
        """
        Constructor
        
        @param parent reference to the parent Widget (QWidget)
        """
        QLabel.__init__(self, parent)
        
        self.__text = ''
        self.__elided = ''
    
    def paintEvent(self, event):
        """
        Protected method called when some painting is required.
        
        @param event reference to the paint event (QPaintEvent)
        """
        fm = self.fontMetrics()
        if fm.width(self.__text) > self.contentsRect().width():
            self.__elided = fm.elidedText(self.text(), Qt.ElideMiddle, self.width())
            QLabel.setText(self, self.__elided)
        else:
            QLabel.setText(self, self.__text)
        QLabel.paintEvent(self, event)
    
    def setText(self, txt):
        """
        Public method to set the label's text.
        
        @param txt the text to be shown (string or QString)
        """
        self.__text = txt
        QLabel.setText(self, self.__text)

class E4SqueezeLabelPath(QLabel):
    """
    Class implementing a label showing a file path compacted to fit it's size.
    """
    def __init__(self, parent = None):
        """
        Constructor
        
        @param parent reference to the parent Widget (QWidget)
        """
        QLabel.__init__(self, parent)
        
        self.__path = ''
        self.__surrounding = QString("%1")
    
    def setSurrounding(self, surrounding):
        """
        Public method to set the surrounding of the path string.
        
        @param surrounding the a string containg placeholders for the path (QString)
        """
        self.__surrounding = surrounding
        QLabel.setText(self, self.__surrounding.arg(self.__path))
    
    def setPath(self, path):
        """
        Public method to set the path of the label.
        
        @param path path to be shown (string or QString)
        """
        self.__path = path
        QLabel.setText(self, self.__surrounding.arg(self.__path))
    
    def setTextPath(self, surrounding, path):
        """
        Public method to set the surrounding and the path of the label.
        
        @param surrounding the a string containg placeholders for the path (QString)
        @param path path to be shown (string or QString)
        """
        self.__surrounding = surrounding
        self.__path = path
        QLabel.setText(self, self.__surrounding.arg(self.__path))
    
    def paintEvent(self, event):
        """
        Protected method called when some painting is required.
        
        @param event reference to the paint event (QPaintEvent)
        """
        fm = self.fontMetrics()
        if fm.width(self.__surrounding.arg(self.__path)) > self.contentsRect().width():
            QLabel.setText(self, 
                self.__surrounding.arg(compactPath(unicode(self.__path), 
                                       self.contentsRect().width(), 
                                       self.length))
            )
        else:
            QLabel.setText(self, self.__surrounding.arg(self.__path))
        QLabel.paintEvent(self, event)
    
    def length(self, txt):
        """
        Public method to return the length of a text in pixels.
        
        @param txt text to calculate the length for after wrapped (string or QString)
        @return length of the wrapped text in pixels (integer)
        """
        return self.fontMetrics().width(self.__surrounding.arg(txt))
