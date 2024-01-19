# -*- coding: utf-8 -*-

# Copyright (c) 2005 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a TabWidget class substituting QTabWidget.
"""

from PyQt4.QtGui import QTabWidget, QTabBar, QApplication, QDrag, QStyle, QLabel, QMovie
from PyQt4.QtCore import Qt, SIGNAL, QPoint, QMimeData, QByteArray

class E4WheelTabBar(QTabBar):
    """
    Class implementing a tab bar class substituting QTabBar to support wheel events.
    """
    def __init__(self, parent = None):
        """
        Constructor
        
        @param parent reference to the parent widget (QWidget)
        """
        QTabBar.__init__(self, parent)
        self._tabWidget = parent
    
    def wheelEvent(self, event):
        """
        Protected slot to support wheel events.
        
        @param reference to the wheel event (QWheelEvent)
        """
        try:
            if event.delta() > 0:
                self._tabWidget.prevTab()
            else:
                self._tabWidget.nextTab()
            
            event.accept()
        except AttributeError:
            pass

class E4DnDTabBar(E4WheelTabBar):
    """
    Class implementing a tab bar class substituting QTabBar.
    
    @signal tabMoveRequested(int, int) emitted to signal a tab move request giving
        the old and new index position
    """
    def __init__(self, parent = None):
        """
        Constructor
        
        @param parent reference to the parent widget (QWidget)
        """
        E4WheelTabBar.__init__(self, parent)
        self.setAcceptDrops(True)
        
        self.__dragStartPos = QPoint()
    
    def mousePressEvent(self, event):
        """
        Protected method to handle mouse press events.
        
        @param event reference to the mouse press event (QMouseEvent)
        """
        if event.button() == Qt.LeftButton:
            self.__dragStartPos = QPoint(event.pos())
        E4WheelTabBar.mousePressEvent(self, event)
    
    def mouseMoveEvent(self, event):
        """
        Protected method to handle mouse move events.
        
        @param event reference to the mouse move event (QMouseEvent)
        """
        if event.buttons() == Qt.MouseButtons(Qt.LeftButton) and \
           (event.pos() - self.__dragStartPos).manhattanLength() > \
                QApplication.startDragDistance():
            drag = QDrag(self)
            mimeData = QMimeData()
            index = self.tabAt(event.pos())
            mimeData.setText(self.tabText(index))
            mimeData.setData("action", "tab-reordering")
            mimeData.setData("tabbar-id", QByteArray.number(id(self)))
            drag.setMimeData(mimeData)
            drag.exec_()
        E4WheelTabBar.mouseMoveEvent(self, event)
    
    def dragEnterEvent(self, event):
        """
        Protected method to handle drag enter events.
        
        @param event reference to the drag enter event (QDragEnterEvent)
        """
        mimeData = event.mimeData()
        formats = mimeData.formats()
        if formats.contains("action") and \
           mimeData.data("action") == "tab-reordering" and \
           formats.contains("tabbar-id") and \
           mimeData.data("tabbar-id").toLong()[0] == id(self):
            event.acceptProposedAction()
        E4WheelTabBar.dragEnterEvent(self, event)
    
    def dropEvent(self, event):
        """
        Protected method to handle drop events.
        
        @param event reference to the drop event (QDropEvent)
        """
        fromIndex = self.tabAt(self.__dragStartPos)
        toIndex = self.tabAt(event.pos())
        if fromIndex != toIndex:
            self.emit(SIGNAL("tabMoveRequested(int, int)"), fromIndex, toIndex)
            event.acceptProposedAction()
        E4WheelTabBar.dropEvent(self, event)

class E4TabWidget(QTabWidget):
    """
    Class implementing a tab widget class substituting QTabWidget.
    
    It provides slots to show the previous and next tab and give
    them the input focus and it allows to have a context menu for the tabs.
    
    @signal customTabContextMenuRequested(const QPoint & point, int index) emitted when
        a context menu for a tab is requested
    """
    def __init__(self, parent = None, dnd = False):
        """
        Constructor
        
        @param parent reference to the parent widget (QWidget)
        @keyparam dnd flag indicating the support for Drag & Drop (boolean)
        """
        QTabWidget.__init__(self, parent)
        
        if dnd:
            if not hasattr(self, 'setMovable'):
                self.__tabBar = E4DnDTabBar(self)
                self.connect(self.__tabBar, SIGNAL("tabMoveRequested(int, int)"), 
                             self.moveTab)
                self.setTabBar(self.__tabBar)
            else:
                self.__tabBar = E4WheelTabBar(self)
                self.setTabBar(self.__tabBar)
                self.setMovable(True)
        else:
            self.__tabBar = E4WheelTabBar(self)
            self.setTabBar(self.__tabBar)
        
        self.__lastCurrentIndex = -1
        self.__currentIndex = -1
        self.connect(self, SIGNAL("currentChanged(int)"), self.__currentChanged)
    
    def __currentChanged(self, index):
        """
        Private slot to handle the currentChanged signal.
        
        @param index index of the current tab
        """
        if index == -1:
            self.__lastCurrentIndex = -1
        else:
            self.__lastCurrentIndex = self.__currentIndex
        self.__currentIndex = index
        
    def switchTab(self):
        """
        Public slot used to switch between the current and the previous current tab.
        """
        if self.__lastCurrentIndex == -1 or self.__currentIndex == -1:
            return
        
        self.setCurrentIndex(self.__lastCurrentIndex)
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

    def prevTab(self):
        """
        Public slot used to show the previous tab.
        """
        ind = self.currentIndex() - 1
        if ind == -1:
            ind = self.count() - 1
            
        self.setCurrentIndex(ind)
        self.currentWidget().setFocus()

    def setTabContextMenuPolicy(self, policy):
        """
        Public method to set the context menu policy of the tab.
        
        @param policy context menu policy to set (Qt.ContextMenuPolicy)
        """
        self.tabBar().setContextMenuPolicy(policy)
        if policy == Qt.CustomContextMenu:
            self.connect(self.tabBar(), 
                SIGNAL("customContextMenuRequested(const QPoint &)"),
                self.__handleTabCustomContextMenuRequested)
        else:
            self.disconnect(self.tabBar(), 
                SIGNAL("customContextMenuRequested(const QPoint &)"),
                self.__handleTabCustomContextMenuRequested)

    def __handleTabCustomContextMenuRequested(self, point):
        """
        Private slot to handle the context menu request for the tabbar.
        
        @param point point the context menu was requested (QPoint)
        """
        _tabbar = self.tabBar()
        for index in range(_tabbar.count()):
            rect = _tabbar.tabRect(index)
            if rect.contains(point):
                self.emit(SIGNAL("customTabContextMenuRequested(const QPoint &, int)"), 
                          _tabbar.mapToParent(point), index)
                break
    
    def selectTab(self, pos):
        """
        Public method to get the index of a tab given a position.
        
        @param pos position determining the tab index (QPoint)
        @return index of the tab (integer)
        """
        _tabbar = self.tabBar()
        for index in range(_tabbar.count()):
            rect = _tabbar.tabRect(index)
            if rect.contains(pos):
                return index
        
        return -1

    def moveTab(self, curIndex, newIndex):
        """
        Public method to move a tab to a new index.
        
        @param curIndex index of tab to be moved (integer)
        @param newIndex index the tab should be moved to (integer)
        """
        # step 1: save the tab data of tab to be moved
        toolTip = self.tabToolTip(curIndex)
        text = self.tabText(curIndex)
        icon = self.tabIcon(curIndex)
        whatsThis = self.tabWhatsThis(curIndex)
        widget = self.widget(curIndex)
        curWidget = self.currentWidget()
        
        # step 2: move the tab
        self.removeTab(curIndex)
        self.insertTab(newIndex, widget, icon, text)
        
        # step 3: set the tab data again
        self.setTabToolTip(newIndex, toolTip)
        self.setTabWhatsThis(newIndex, whatsThis)
        
        # step 4: set current widget
        self.setCurrentWidget(curWidget)
    
    def __freeSide(self):
        """
        Private method to determine the free side of a tab.
        
        @return free side (QTabBar.ButtonPosition)
        """
        side = self.__tabBar.style().styleHint(QStyle.SH_TabBar_CloseButtonPosition)
        if side == QTabBar.LeftSide:
            side = QTabBar.RightSide
        else:
            side = QTabBar.LeftSide
        return side
    
    def animationLabel(self, index, animationFile):
        """
        Public slot to set an animated icon.
        
        @param index tab index (integer)
        @param animationFile name of the file containing the animation (string)
        @return reference to the created label (QLabel)
        """
        if index == -1:
            return None
        
        if hasattr(self.__tabBar, 'setTabButton'):
            side = self.__freeSide()
            animation = QLabel(self)
            if animationFile and not animation.movie():
                movie = QMovie(animationFile, QByteArray(), animation)
                movie.setSpeed(50)
                animation.setMovie(movie)
                movie.start()
            self.__tabBar.setTabButton(index, side, None)
            self.__tabBar.setTabButton(index, side, animation)
            return animation
        else:
            return None
    
    def resetAnimation(self, index):
        """
        Public slot to reset an animated icon.
        
        @param index tab index (integer)
        """
        if index == -1:
            return None
        
        if hasattr(self.__tabBar, 'tabButton'):
            side = self.__freeSide()
            animation = self.__tabBar.tabButton(index, side)
            if animation is not None:
                animation.movie().stop()
                self.__tabBar.setTabButton(index, side, None)
                del animation
