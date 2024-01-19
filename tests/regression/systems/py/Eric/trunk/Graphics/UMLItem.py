# -*- coding: utf-8 -*-

# Copyright (c) 2004 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the UMLWidget base class.
"""

from PyQt4.QtCore import *
from PyQt4.QtGui import *

import Preferences

class UMLItem(QGraphicsRectItem):
    """
    Class implementing the UMLItem base class.
    """
    def __init__(self, x = 0, y = 0, rounded = False, parent = None):
        """
        Constructor
        
        @param x x-coordinate (integer)
        @param y y-coordinate (integer)
        @param rounded flag indicating a rounded corner (boolean)
        @keyparam parent reference to the parent object (QGraphicsItem)
        """
        QGraphicsRectItem.__init__(self, parent)
        self.font = Preferences.getGraphics("Font")
        self.margin = 5
        self.associations = []
        self.shouldAdjustAssociations = False
        
        self.setRect(x, y, 60, 30)
        
        if rounded:
            p = self.pen()
            p.setCapStyle(Qt.RoundCap)
            p.setJoinStyle(Qt.RoundJoin)
        
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        
    def setSize(self, width, height):
        """
        Public method to set the rectangles size.
        
        @param width width of the rectangle (float)
        @param height height of the rectangle (float)
        """
        rect = self.rect()
        rect.setSize(QSizeF(width, height))
        self.setRect(rect)
        
    def addAssociation(self, assoc):
        """
        Method to add an association to this widget.
        
        @param assoc association to be added (AssociationWidget)
        """
        if assoc and not assoc in self.associations:
            self.associations.append(assoc)
        
    def removeAssociation(self, assoc):
        """
        Method to remove an association to this widget.
        
        @param assoc association to be removed (AssociationWidget)
        """
        if assoc and assoc in self.associations:
            self.associations.remove(assoc)
        
    def removeAssociations(self):
        """
        Method to remove all associations of this widget.
        """
        for assoc in self.associations[:]:
            assoc.unassociate()
            assoc.hide()
            del assoc
        
    def adjustAssociations(self):
        """
        Method to adjust the associations to widget movements.
        """
        if self.shouldAdjustAssociations:
            for assoc in self.associations:
                assoc.widgetMoved()
            self.shouldAdjustAssociations = False
        
    def moveBy(self, dx, dy):
        """
        Overriden method to move the widget relative.
        
        @param dx relative movement in x-direction (float)
        @param dy relative movement in y-direction (float)
        """
        QGraphicsRectItem.moveBy(self, dx, dy)
        self.adjustAssociations()
        
    def setPos(self, x, y):
        """
        Overriden method to set the items position.
        
        @param x absolute x-position (float)
        @param y absolute y-position (float)
        """
        QGraphicsRectItem.setPos(self, x, y)
        self.adjustAssociations()
        
    def itemChange(self, change, value):
        """
        Protected method called when an items state changes.
        
        @param change the item's change (QGraphicsItem.GraphicsItemChange)
        @param value the value of the change (QVariant)
        @return adjusted values (QVariant)
        """
        if change == QGraphicsItem.ItemPositionChange:
            self.shouldAdjustAssociations = True
        return QGraphicsItem.itemChange(self, change, value)
        
    def paint(self, painter, option, widget = None):
        """
        Public method to paint the item in local coordinates.
        
        @param painter reference to the painter object (QPainter)
        @param option style options (QStyleOptionGraphicsItem)
        @param widget optional reference to the widget painted on (QWidget)
        """
        pen = self.pen()
        if (option.state & QStyle.State_Selected) == QStyle.State(QStyle.State_Selected):
            pen.setWidth(2)
        else:
            pen.setWidth(1)
        
        painter.setPen(pen)
        painter.setBrush(self.brush())
        painter.drawRect(self.rect())
        self.adjustAssociations()
