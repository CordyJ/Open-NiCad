# -*- coding: utf-8 -*-

# Copyright (c) 2008 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a horizontal and a vertical toolbox class.
"""

from PyQt4.QtCore import QString
from PyQt4.QtGui import QToolBox, QTabWidget

from E4TabWidget import E4TabWidget

class E4VerticalToolBox(QToolBox):
    """
    Class implementing a ToolBox class substituting QToolBox to support wheel events.
    """
    def __init__(self, parent = None):
        """
        Constructor
        
        @param parent reference to the parent widget (QWidget)
        """
        QToolBox.__init__(self, parent)
    
    def wheelEvent(self, event):
        """
        Protected slot to support wheel events.
        
        @param reference to the wheel event (QWheelEvent)
        """
        index = self.currentIndex()
        if event.delta() > 0:
            index -= 1
        else:
            index += 1
        if index < 0:
            index = self.count() - 1
        elif index == self.count():
            index = 0
        
        self.setCurrentIndex(index)
        
        event.accept()

class E4HorizontalToolBox(E4TabWidget):
    """
    Class implementing a vertical QToolBox like widget.
    """
    def __init__(self, parent = None):
        """
        Constructor
        
        @param parent reference to the parent widget (QWidget)
        """
        E4TabWidget.__init__(self, parent)
        self.setTabPosition(QTabWidget.West)
    
    def addItem(self, widget, icon, text):
        """
        Public method to add a widget to the toolbox.
        
        @param widget reference to the widget to be added (QWidget)
        @param icon the icon to be shown (QIcon)
        @param text the text to be shown (QString)
        @return index of the added widget (integer)
        """
        index = self.addTab(widget, icon, QString())
        self.setTabToolTip(index, text)
        return index
    
    def insertItem(self, index, widget, icon, text):
        """
        Public method to add a widget to the toolbox.
        
        @param index position at which the widget should be inserted (integer)
        @param widget reference to the widget to be added (QWidget)
        @param icon the icon to be shown (QIcon)
        @param text the text to be shown (QString)
        @return index of the added widget (integer)
        """
        index = self.insertTab(index, widget, icon, QString())
        self.setTabToolTip(index, text)
        return index
    
    def setItemToolTip(self, index, toolTip):
        """
        Public method to set the tooltip of an item.
        
        @param index index of the item (integer)
        @param toolTip tooltip text to be set (QString)
        """
        self.setTabToolTip(index, toolTip)
    
    def setItemEnabled(self, index, enabled):
        """
        Public method to set the enabled state of an item.
        
        @param index index of the item (integer)
        @param enabled flag indicating the enabled state (boolean)
        """
        self.setTabEnabled(index, enabled)
