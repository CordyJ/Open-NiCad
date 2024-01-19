# -*- coding: utf-8 -*-

# Copyright (c) 2008 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a sidebar class.
"""

from PyQt4.QtCore import SIGNAL,  SLOT, QEvent, QSize, Qt, QByteArray, \
                         QDataStream, QIODevice
from PyQt4.QtGui import QTabBar, QWidget, QStackedWidget, QBoxLayout, QToolButton

from KdeQt.KQApplication import e4App

import UI.PixmapCache

class E4SideBar(QWidget):
    """
    Class implementing a sidebar with a widget area, that is hidden or shown, if the
    current tab is clicked again.
    """
    Version = 1
    
    North = 0
    East  = 1
    South = 2
    West  = 3
    
    def __init__(self, orientation = None, parent = None):
        """
        Constructor
        
        @param orientation orientation of the sidebar widget (North, East, South, West)
        @param parent parent widget (QWidget)
        """
        QWidget.__init__(self, parent)
        
        self.__tabBar = QTabBar()
        self.__tabBar.setDrawBase(True)
        self.__tabBar.setShape(QTabBar.RoundedNorth)
        self.__stackedWidget = QStackedWidget(self)
        self.__stackedWidget.setContentsMargins(0, 0, 0, 0)
        self.__autoHideButton = QToolButton()
        self.__autoHideButton.setCheckable(True)
        self.__autoHideButton.setIcon(UI.PixmapCache.getIcon("autoHideOff.png"))
        self.__autoHideButton.setChecked(True)
        self.__autoHideButton.setToolTip(
            self.trUtf8("Deselect to activate automatic collapsing"))
        self.barLayout = QBoxLayout(QBoxLayout.LeftToRight)
        self.barLayout.setMargin(0)
        self.layout = QBoxLayout(QBoxLayout.TopToBottom)
        self.layout.setMargin(0)
        self.layout.setSpacing(0)
        self.barLayout.addWidget(self.__autoHideButton)
        self.barLayout.addWidget(self.__tabBar)
        self.layout.addLayout(self.barLayout)
        self.layout.addWidget(self.__stackedWidget)
        self.setLayout(self.layout)
        
        self.__minimized = False
        self.__minSize = 0
        self.__maxSize = 0
        self.__bigSize = QSize()
        
        self.splitter = None
        self.splitterSizes = []
        
        self.__hasFocus = False # flag storing if this widget or any child has the focus
        self.__autoHide = False
        
        self.__tabBar.installEventFilter(self)
        
        self.__orientation = E4SideBar.North
        if orientation is None:
            orientation = E4SideBar.North
        self.setOrientation(orientation)
        
        self.connect(self.__tabBar, SIGNAL("currentChanged(int)"), 
                     self.__stackedWidget, SLOT("setCurrentIndex(int)"))
        self.connect(e4App(), SIGNAL("focusChanged(QWidget*, QWidget*)"), 
                     self.__appFocusChanged)
        self.connect(self.__autoHideButton, SIGNAL("toggled(bool)"), 
                     self.__autoHideToggled)
    
    def setSplitter(self, splitter):
        """
        Public method to set the splitter managing the sidebar.
        
        @param splitter reference to the splitter (QSplitter)
        """
        self.splitter = splitter
    
    def shrink(self):
        """
        Public method to shrink the sidebar.
        """
        self.__minimized = True
        self.__bigSize = self.size()
        if self.__orientation in [E4SideBar.North, E4SideBar.South]:
            self.__minSize = self.minimumHeight()
            self.__maxSize = self.maximumHeight()
        else:
            self.__minSize = self.minimumWidth()
            self.__maxSize = self.maximumWidth()
        self.splitterSizes = self.splitter.sizes()
        
        self.__stackedWidget.hide()
        
        if self.__orientation in [E4SideBar.North, E4SideBar.South]:
            self.setFixedHeight(self.__tabBar.minimumSizeHint().height())
        else:
            self.setFixedWidth(self.__tabBar.minimumSizeHint().width())
    
    def expand(self):
        """
        Public method to expand the sidebar.
        """
        self.__minimized = False
        self.__stackedWidget.show()
        self.resize(self.__bigSize)
        if self.__orientation in [E4SideBar.North, E4SideBar.South]:
            self.setMinimumHeight(self.__minSize)
            self.setMaximumHeight(self.__maxSize)
        else:
            self.setMinimumWidth(self.__minSize)
            self.setMaximumWidth(self.__maxSize)
        self.splitter.setSizes(self.splitterSizes)
    
    def isMinimized(self):
        """
        Public method to check the minimized state.
        
        @return flag indicating the minimized state (boolean)
        """
        return self.__minimized
    
    def isAutoHiding(self):
        """
        Public method to check, if the auto hide function is active.
        
        @return flag indicating the state of auto hiding (boolean)
        """
        return self.__autoHide
    
    def eventFilter(self, obj, evt):
        """
        Protected method to handle some events for the tabbar.
        
        @param obj reference to the object (QObject)
        @param evt reference to the event object (QEvent)
        @return flag indicating, if the event was handled (boolean)
        """
        if obj == self.__tabBar:
            if evt.type() == QEvent.MouseButtonPress:
                pos = evt.pos()
                index = -1
                for i in range(self.__tabBar.count()):
                    if self.__tabBar.tabRect(i).contains(pos):
                        index = i
                        break
                
                if i == self.__tabBar.currentIndex():
                    if self.isMinimized():
                        self.expand()
                    else:
                        self.shrink()
                    return True
                elif self.isMinimized():
                    self.expand()
            elif evt.type() == QEvent.Wheel and not self.__stackedWidget.isHidden():
                if evt.delta() > 0:
                    self.prevTab()
                else:
                    self.nextTab()
                return True
        
        return QWidget.eventFilter(self, obj, evt)
    
    def addTab(self, widget, iconOrLabel, label = None):
        """
        Public method to add a tab to the sidebar.
        
        @param widget reference to the widget to add (QWidget)
        @param iconOrLabel reference to the icon or the labeltext of the tab
            (QIcon, string or QString)
        @param label the labeltext of the tab (string or QString) (only to be
            used, if the second parameter is a QIcon)
        """
        if label:
            self.__tabBar.addTab(iconOrLabel, label)
        else:
            self.__tabBar.addTab(iconOrLabel)
        self.__stackedWidget.addWidget(widget)
    
    def insertTab(self, index, widget, iconOrLabel, label = None):
        """
        Public method to insert a tab into the sidebar.
        
        @param index the index to insert the tab at (integer)
        @param widget reference to the widget to insert (QWidget)
        @param iconOrLabel reference to the icon or the labeltext of the tab
            (QIcon, string or QString)
        @param label the labeltext of the tab (string or QString) (only to be
            used, if the second parameter is a QIcon)
        """
        if label:
            self.__tabBar.insertTab(index, iconOrLabel, label)
        else:
            self.__tabBar.insertTab(index, iconOrLabel)
        self.__stackedWidget.insertWidget(index, widget)
    
    def removeTab(self, index):
        """
        Public method to remove a tab.
        
        @param index the index of the tab to remove (integer)
        """
        self.__stackedWidget.removeWidget(self.__stackedWidget.widget(index))
        self.__tabBar.removeTab(index)
    
    def clear(self):
        """
        Public method to remove all tabs.
        """
        while self.count() > 0:
            self.removeTab(0)
    
    def prevTab(self):
        """
        Public slot used to show the previous tab.
        """
        ind = self.currentIndex() - 1
        if ind == -1:
            ind = self.count() - 1
            
        self.setCurrentIndex(ind)
        self.currentWidget().setFocus()
    
    def nextTab(self):
        """
        Public slot used to show the next tab.
        """
        ind = self.currentIndex() + 1
        if ind == self.count():
            ind = 0
            
        self.setCurrentIndex(ind)
        self.currentWidget().setFocus()
    
    def count(self):
        """
        Public method to get the number of tabs.
        
        @return number of tabs in the sidebar (integer)
        """
        return self.__tabBar.count()
    
    def currentIndex(self):
        """
        Public method to get the index of the current tab.
        
        @return index of the current tab (integer)
        """
        return self.__stackedWidget.currentIndex()
    
    def setCurrentIndex(self, index):
        """
        Public slot to set the current index.
        
        @param index the index to set as the current index (integer)
        """
        self.__tabBar.setCurrentIndex(index)
        self.__stackedWidget.setCurrentIndex(index)
        if self.isMinimized():
            self.expand()
    
    def currentWidget(self):
        """
        Public method to get a reference to the current widget.
        
        @return reference to the current widget (QWidget)
        """
        return self.__stackedWidget.currentWidget()
    
    def setCurrentWidget(self, widget):
        """
        Public slot to set the current widget.
        
        @param widget reference to the widget to become the current widget (QWidget)
        """
        self.__stackedWidget.setCurrentWidget(widget)
        self.__tabBar.setCurrentIndex(self.__stackedWidget.currentIndex())
        if self.isMinimized():
            self.expand()
    
    def indexOf(self, widget):
        """
        Public method to get the index of the given widget.
        
        @param widget reference to the widget to get the index of (QWidget)
        @return index of the given widget (integer)
        """
        return self.__stackedWidget.indexOf(widget)
    
    def isTabEnabled(self, index):
        """
        Public method to check, if a tab is enabled.
        
        @param index index of the tab to check (integer)
        @return flag indicating the enabled state (boolean)
        """
        return self.__tabBar.isTabEnabled(index)
    
    def setTabEnabled(self, index, enabled):
        """
        Public method to set the enabled state of a tab.
        
        @param index index of the tab to set (integer)
        @param enabled enabled state to set (boolean)
        """
        self.__tabBar.setTabEnabled(index, enabled)
    
    def orientation(self):
        """
        Public method to get the orientation of the sidebar.
        
        @return orientation of the sidebar (North, East, South, West)
        """
        return self.__orientation
    
    def setOrientation(self, orient):
        """
        Public method to set the orientation of the sidebar.
        @param orient orientation of the sidebar (North, East, South, West)
        """
        if orient == E4SideBar.North:
            self.__tabBar.setShape(QTabBar.RoundedNorth)
            self.barLayout.setDirection(QBoxLayout.LeftToRight)
            self.layout.setDirection(QBoxLayout.TopToBottom)
            self.layout.setAlignment(self.barLayout, Qt.AlignLeft)
        elif orient == E4SideBar.East:
            self.__tabBar.setShape(QTabBar.RoundedEast)
            self.barLayout.setDirection(QBoxLayout.TopToBottom)
            self.layout.setDirection(QBoxLayout.RightToLeft)
            self.layout.setAlignment(self.barLayout, Qt.AlignTop)
        elif orient == E4SideBar.South:
            self.__tabBar.setShape(QTabBar.RoundedSouth)
            self.barLayout.setDirection(QBoxLayout.LeftToRight)
            self.layout.setDirection(QBoxLayout.BottomToTop)
            self.layout.setAlignment(self.barLayout, Qt.AlignLeft)
        elif orient == E4SideBar.West:
            self.__tabBar.setShape(QTabBar.RoundedWest)
            self.barLayout.setDirection(QBoxLayout.TopToBottom)
            self.layout.setDirection(QBoxLayout.LeftToRight)
            self.layout.setAlignment(self.barLayout, Qt.AlignTop)
        self.__orientation = orient
    
    def tabIcon(self, index):
        """
        Public method to get the icon of a tab.
        
        @param index index of the tab (integer)
        @return icon of the tab (QIcon)
        """
        return self.__tabBar.tabIcon(index)
    
    def setTabIcon(self, index, icon):
        """
        Public method to set the icon of a tab.
        
        @param index index of the tab (integer)
        @param icon icon to be set (QIcon)
        """
        self.__tabBar.setTabIcon(index, icon)
    
    def tabText(self, index):
        """
        Public method to get the text of a tab.
        
        @param index index of the tab (integer)
        @return text of the tab (QString)
        """
        return self.__tabBar.tabText(index)
    
    def setTabText(self, index, text):
        """
        Public method to set the text of a tab.
        
        @param index index of the tab (integer)
        @param text text to set (QString)
        """
        self.__tabBar.setTabText(index, text)
    
    def tabToolTip(self, index):
        """
        Public method to get the tooltip text of a tab.
        
        @param index index of the tab (integer)
        @return tooltip text of the tab (QString)
        """
        return self.__tabBar.tabToolTip(index)
    
    def setTabToolTip(self, index, tip):
        """
        Public method to set the tooltip text of a tab.
        
        @param index index of the tab (integer)
        @param tooltip text text to set (QString)
        """
        self.__tabBar.setTabToolTip(index, tip)
    
    def tabWhatsThis(self, index):
        """
        Public method to get the WhatsThis text of a tab.
        
        @param index index of the tab (integer)
        @return WhatsThis text of the tab (QString)
        """
        return self.__tabBar.tabWhatsThis(index)
    
    def setTabWhatsThis(self, index, text):
        """
        Public method to set the WhatsThis text of a tab.
        
        @param index index of the tab (integer)
        @param WhatsThis text text to set (QString)
        """
        self.__tabBar.setTabWhatsThis(index, text)
    
    def widget(self, index):
        """
        Public method to get a reference to the widget associated with a tab.
        
        @param index index of the tab (integer)
        @return reference to the widget (QWidget)
        """
        return self.__stackedWidget.widget(index)
    
    def saveState(self):
        """
        Public method to save the state of the sidebar.
        
        @return saved state as a byte array (QByteArray)
        """
        if len(self.splitterSizes) == 0:
            self.splitterSizes = self.splitter.sizes()
            self.__bigSize = self.size()
            if self.__orientation in [E4SideBar.North, E4SideBar.South]:
                self.__minSize = self.minimumHeight()
                self.__maxSize = self.maximumHeight()
            else:
                self.__minSize = self.minimumWidth()
                self.__maxSize = self.maximumWidth()
        
        data = QByteArray()
        stream = QDataStream(data, QIODevice.WriteOnly)
        
        stream.writeUInt16(self.Version)
        stream.writeBool(self.__minimized)
        stream << self.__bigSize
        stream.writeUInt16(self.__minSize)
        stream.writeUInt16(self.__maxSize)
        stream.writeUInt16(len(self.splitterSizes))
        for size in self.splitterSizes:
            stream.writeUInt16(size)
        stream.writeBool(self.__autoHide)
        
        return data
    
    def restoreState(self, state):
        """
        Public method to restore the state of the sidebar.
        
        @param state byte array containing the saved state (QByteArray)
        @return flag indicating success (boolean)
        """
        if state.isEmpty():
            return False
        
        data = QByteArray(state)
        stream = QDataStream(data, QIODevice.ReadOnly)
        version = stream.readUInt16()
        minimized = stream.readBool()
        
        if minimized:
            self.shrink()
        
        stream >> self.__bigSize
        self.__minSize = stream.readUInt16()
        self.__maxSize = stream.readUInt16()
        count = stream.readUInt16()
        self.splitterSizes = []
        for i in range(count):
            self.splitterSizes.append(stream.readUInt16())
        
        self.__autoHide = stream.readBool()
        self.__autoHideButton.setChecked(not self.__autoHide)
        
        if not minimized:
            self.expand()
        
        return True
    
    #######################################################################
    ## methods below implement the autohide functionality
    #######################################################################
    
    def __autoHideToggled(self, checked):
        """
        Private slot to handle the toggling of the autohide button.
        
        @param checked flag indicating the checked state of the button (boolean)
        """
        self.__autoHide = not checked
        if self.__autoHide:
            self.__autoHideButton.setIcon(UI.PixmapCache.getIcon("autoHideOn"))
        else:
            self.__autoHideButton.setIcon(UI.PixmapCache.getIcon("autoHideOff"))
    
    def __appFocusChanged(self, old, now):
        """
        Private slot to handle a change of the focus.
        
        @param old reference to the widget, that lost focus (QWidget or None)
        @param now reference to the widget having the focus (QWidget or None)
        """
        self.__hasFocus = self.isAncestorOf(now)
        if self.__autoHide and not self.__hasFocus and not self.isMinimized():
            self.shrink()
        elif self.__autoHide and self.__hasFocus and self.isMinimized():
            self.expand()
    
    def enterEvent(self, event):
        """
        Protected method to handle the mouse entering this widget.
        
        @param event reference to the event (QEvent)
        """
        if self.__autoHide and self.isMinimized():
            self.expand()
    
    def leaveEvent(self, event):
        """
        Protected method to handle the mouse leaving this widget.
        
        @param event reference to the event (QEvent)
        """
        if self.__autoHide and not self.__hasFocus and not self.isMinimized():
            self.shrink()
