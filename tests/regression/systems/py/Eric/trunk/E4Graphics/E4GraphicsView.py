# -*- coding: utf-8 -*-

# Copyright (c) 2007 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a canvas view class.
"""

import sys

from PyQt4.QtCore import *
from PyQt4.QtGui import *

import Preferences

class E4GraphicsView(QGraphicsView):
    """
    Class implementing a graphics view.
    """
    def __init__(self, scene, parent = None):
        """
        Constructor
        
        @param scene reference to the scene object (QGraphicsScene)
        @param parent parent widget (QWidget)
        """
        QGraphicsView.__init__(self, scene, parent)
        self.setObjectName("E4GraphicsView")
        
        self.setBackgroundBrush(QBrush(Qt.white))
        self.setRenderHint(QPainter.Antialiasing, True)
        self.setDragMode(QGraphicsView.RubberBandDrag)
        self.setAlignment(Qt.Alignment(Qt.AlignLeft | Qt.AlignTop))
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        
        # available as of Qt 4.3
        try:
            self.setViewportUpdateMode(QGraphicsView.SmartViewportUpdate)
        except AttributeError:
            pass
        
        self.setWhatsThis(self.trUtf8("<b>Graphics View</b>\n"
            "<p>This graphics view is used to show a diagram. \n"
            "There are various actions available to manipulate the \n"
            "shown items.</p>\n"
            "<ul>\n"
            "<li>Clicking on an item selects it.</li>\n"
            "<li>Ctrl-clicking adds an item to the selection.</li>\n"
            "<li>Ctrl-clicking a selected item deselects it.</li>\n"
            "<li>Clicking on an empty spot of the canvas resets the selection.</li>\n"
            "<li>Dragging the mouse over the canvas spans a rubberband to \n"
            "select multiple items.</li>\n"
            "<li>Dragging the mouse over a selected item moves the \n"
            "whole selection.</li>\n"
            "</ul>\n"
        ))
        
    def zoomIn(self):
        """
        Public method to zoom in.
        """
        self.scale(1.25, 1.25)
        
    def zoomOut(self):
        """
        Public method to zoom out.
        """
        self.scale(0.8, 0.8)
    
    def zoomReset(self):
        """
        Public method to handle the reset zoom context menu entry.
        """
        self.resetMatrix()
        
    def setZoom(self, zoomFactor):
        """
        Public method to set the zoom factor.
        
        @param zoomFactor new zoom factor (float)
        """
        self.zoomReset()
        self.scale(zoomFactor, zoomFactor)
        
    def zoom(self):
        """
        Public method to get the current zoom factor.
        
        @return current zoom factor (float)
        """
        return self.matrix().m11()
       
    def resizeScene(self, amount, isWidth = True):
        """
        Public method to resize the scene.
        
        @param isWidth flag indicating width is to be resized (boolean)
        @param amount size increment (integer)
        """
        sceneRect = self.scene().sceneRect()
        width = sceneRect.width()
        height = sceneRect.height()
        if isWidth:
            width += amount
        else:
            height += amount
        rect = self._getDiagramRect(10)
        if width < rect.width():
            width = rect.width()
        if height < rect.height():
            height = rect.height()
        
        self.setSceneSize(width, height)
        
    def setSceneSize(self, width, height):
        """
        Public method to set the scene size.
        
        @param width width for the scene (integer)
        @param height height for the scene (integer)
        """
        rect = self.scene().sceneRect()
        rect.setHeight(height)
        rect.setWidth(width)
        self.setSceneRect(rect)
        
    def _getDiagramRect(self, border = 0):
        """
        Protected method to calculate the minimum rectangle fitting the diagram.
        
        @param border border width to include in the calculation (integer)
        @return the minimum rectangle (QRectF)
        """
        startx = sys.maxint
        starty = sys.maxint
        endx = 0
        endy = 0
        items = self.filteredItems(self.scene().items())
        for itm in items:
            rect = itm.sceneBoundingRect()
            itmEndX = rect.x() + rect.width()
            itmEndY = rect.y()+ rect.height()
            itmStartX = rect.x()
            itmStartY = rect.y()
            if startx >= itmStartX:
                startx = itmStartX
            if starty >= itmStartY:
                starty = itmStartY
            if endx <= itmEndX:
                endx = itmEndX
            if endy <= itmEndY:
                endy = itmEndY
        if border:
            startx -= border
            starty -= border
            endx += border
            endy += border
            
        return QRectF(startx, starty, endx - startx + 1, endy - starty + 1)
        
    def _getDiagramSize(self, border = 0):
        """
        Protected method to calculate the minimum size fitting the diagram.
        
        @param border border width to include in the calculation (integer)
        @return the minimum size (QSizeF)
        """
        endx = 0
        endy = 0
        items = self.filteredItems(self.scene().items())
        for itm in items:
            rect = itm.sceneBoundingRect()
            itmEndX = rect.x() + rect.width()
            itmEndY = rect.y()+ rect.height()
            if endx <= itmEndX:
                endx = itmEndX
            if endy <= itmEndY:
                endy = itmEndY
        if border:
            endx += border
            endy += border
            
        return QSizeF(endx + 1, endy + 1)
        
    def __getDiagram(self, rect, format = "PNG", filename = None):
        """
        Private method to retrieve the diagram from the scene fitting it 
        in the minimum rectangle.
        
        @param rect minimum rectangle fitting the diagram (QRectF)
        @param format format for the image file (string or QString)
        @param filename name of the file for non pixmaps (string or QString)
        @return diagram pixmap to receive the diagram (QPixmap)
        """
        selectedItems = self.scene().selectedItems()
        
        # step 1: deselect all widgets
        if selectedItems:
            for item in selectedItems:
                item.setSelected(False)
            
        # step 2: grab the diagram
        if format == "PNG":
            paintDevice = QPixmap(int(rect.width()), int(rect.height()))
            paintDevice.fill(self.backgroundBrush().color())
        else:
            from PyQt4.QtSvg import QSvgGenerator
            paintDevice = QSvgGenerator()
            paintDevice.setResolution(100)  # 100 dpi
            paintDevice.setSize(QSize(int(rect.width()), int(rect.height())))
            paintDevice.setFileName(filename)
        painter = QPainter(paintDevice)
        painter.setRenderHint(QPainter.Antialiasing, True)
        self.scene().render(painter, QRectF(), rect)
        
        # step 3: reselect the widgets
        if selectedItems:
            for item in selectedItems:
                item.setSelected(True)
        
        return paintDevice
        
    def saveImage(self, filename, format = "PNG"):
        """
        Public method to save the scene to a file.
        
        @param filename name of the file to write the image to (string or QString)
        @param format format for the image file (string or QString)
        @return flag indicating success (boolean)
        """
        rect = self._getDiagramRect(self.border)
        if format == "SVG":
            svg = self.__getDiagram(rect, format = format, filename = filename)
            return True
        else:
            pixmap = self.__getDiagram(rect)
            return pixmap.save(filename, format)
        
    def printDiagram(self, printer, diagramName = ""):
        """
        Public method to print the diagram.
        
        @param printer reference to a ready configured printer object (QPrinter)
        @param diagramName name of the diagram (string or QString)
        """
        painter = QPainter()
        painter.begin(printer)
        offsetX = 0
        offsetY = 0
        widthX = 0
        heightY = 0
        font = QFont("times", 10)
        painter.setFont(font)
        fm = painter.fontMetrics()
        fontHeight = fm.lineSpacing()
        marginX = printer.pageRect().x() - printer.paperRect().x()
        marginX = \
            Preferences.getPrinter("LeftMargin") * int(printer.resolution() / 2.54) \
            - marginX
        marginY = printer.pageRect().y() - printer.paperRect().y()
        marginY = \
            Preferences.getPrinter("TopMargin") * int(printer.resolution() / 2.54) \
            - marginY
        
        width = printer.width() - marginX \
            - Preferences.getPrinter("RightMargin") * int(printer.resolution() / 2.54)
        height = printer.height() - fontHeight - 4 - marginY \
            - Preferences.getPrinter("BottomMargin") * int(printer.resolution() / 2.54)
        
        border = self.border == 0 and 5 or self.border
        rect = self._getDiagramRect(border)
        diagram = self.__getDiagram(rect)
        
        finishX = False
        finishY = False
        page = 0
        pageX = 0
        pageY = 1
        while not finishX or not finishY:
            if not finishX:
                offsetX = pageX * width
                pageX += 1
            elif not finishY:
                offsetY = pageY * height
                offsetX = 0
                pageY += 1
                finishX = False
                pageX = 1
            if (width + offsetX) > diagram.width():
                finishX = True
                widthX = diagram.width() - offsetX
            else:
                widthX = width
            if diagram.width() < width:
                widthX = diagram.width()
                finishX = True
                offsetX = 0
            if (height + offsetY) > diagram.height():
                finishY = True
                heightY = diagram.height() - offsetY
            else:
                heightY = height
            if diagram.height() < height:
                finishY = True
                heightY = diagram.height()
                offsetY = 0
            
            painter.drawPixmap(marginX, marginY, diagram,
                               offsetX, offsetY, widthX, heightY)
            # write a foot note
            s = QString(self.trUtf8("Diagram: %1, Page %2")
                .arg(diagramName).arg(page + 1))
            tc = QColor(50, 50, 50)
            painter.setPen(tc)
            painter.drawRect(marginX, marginY, width, height)
            painter.drawLine(marginX, marginY + height + 2, 
                       marginX + width, marginY + height + 2)
            painter.setFont(font)
            painter.drawText(marginX, marginY + height + 4, width,
                       fontHeight, Qt.AlignRight, s)
            if not finishX or not finishY:
                printer.newPage()
                page += 1
        
        painter.end()
    
    ############################################################################
    ## The methods below should be overridden by subclasses to get special
    ## behavior.
    ############################################################################
    
    def filteredItems(self, items):
        """
        Public method to filter a list of items.
        
        @param items list of items as returned by the scene object
            (QGraphicsItem)
        @return list of interesting collision items (QGraphicsItem)
        """
        # just return the list unchanged
        return items
