# -*- coding: utf-8 -*-

# Copyright (c) 2008 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a dialog showing a SVG graphic.
"""

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtSvg import QSvgWidget

import KdeQt.KQPrinter
from KdeQt.KQMainWindow import KQMainWindow
from KdeQt.KQPrintDialog import KQPrintDialog

from ZoomDialog import ZoomDialog

import UI.Config

import Preferences

class SvgDiagram(KQMainWindow):
    """
    Class implementing a dialog showing a SVG graphic.
    """
    def __init__(self, svgFile, parent = None, name = None):
        """
        Constructor
        
        @param svgFile filename of a SVG graphics file to show (QString or string)
        @param parent parent widget of the view (QWidget)
        @param name name of the view widget (QString or string)
        """
        KQMainWindow.__init__(self, parent)
        if name:
            self.setObjectName(name)
        else:
            self.setObjectName("SvgDiagram")
        self.setWindowTitle(self.trUtf8("SVG-Viewer"))
        
        self.svgWidget = QSvgWidget()
        self.svgWidget.setObjectName("svgWidget")
        self.svgWidget.setBackgroundRole(QPalette.Base)
        self.svgWidget.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        
        self.svgView = QScrollArea()
        self.svgView.setObjectName("svgView")
        self.svgView.setBackgroundRole(QPalette.Dark)
        self.svgView.setWidget(self.svgWidget)
        
        self.setCentralWidget(self.svgView)
        
        # polish up the dialog
        self.resize(QSize(800, 600).expandedTo(self.minimumSizeHint()))
        
        self.zoom = 1.0
        self.svgFile = svgFile
        self.svgWidget.load(self.svgFile)
        self.svgWidget.resize(self.svgWidget.renderer().defaultSize())
        
        self.__initActions()
        self.__initContextMenu()
        self.__initToolBars()
        
    def __initActions(self):
        """
        Private method to initialize the view actions.
        """
        self.closeAct = \
            QAction(UI.PixmapCache.getIcon("close.png"),
                    self.trUtf8("Close"), self)
        self.connect(self.closeAct, SIGNAL("triggered()"), self.close)
        
        self.printAct = \
            QAction(UI.PixmapCache.getIcon("print.png"),
                    self.trUtf8("Print"), self)
        self.connect(self.printAct, SIGNAL("triggered()"), self.__printDiagram)
        
        self.printPreviewAct = \
            QAction(UI.PixmapCache.getIcon("printPreview.png"),
                    self.trUtf8("Print Preview"), self)
        self.connect(self.printPreviewAct, SIGNAL("triggered()"), 
            self.__printPreviewDiagram)
        
        self.zoomInAct = \
            QAction(UI.PixmapCache.getIcon("zoomIn.png"),
                    self.trUtf8("Zoom in"), self)
        self.connect(self.zoomInAct, SIGNAL("triggered()"), self.__zoomIn)
        
        self.zoomOutAct = \
            QAction(UI.PixmapCache.getIcon("zoomOut.png"),
                    self.trUtf8("Zoom out"), self)
        self.connect(self.zoomOutAct, SIGNAL("triggered()"), self.__zoomOut)
        
        self.zoomAct = \
            QAction(UI.PixmapCache.getIcon("zoomTo.png"),
                    self.trUtf8("Zoom..."), self)
        self.connect(self.zoomAct, SIGNAL("triggered()"), self.__zoom)
        
        self.zoomResetAct = \
            QAction(UI.PixmapCache.getIcon("zoomReset.png"),
                    self.trUtf8("Zoom reset"), self)
        self.connect(self.zoomResetAct, SIGNAL("triggered()"), self.__zoomReset)
        
    def __initContextMenu(self):
        """
        Private method to initialize the context menu.
        """
        self.__menu = QMenu(self)
        self.__menu.addAction(self.closeAct)
        self.__menu.addSeparator()
        self.__menu.addAction(self.printPreviewAct)
        self.__menu.addAction(self.printAct)
        self.__menu.addSeparator()
        self.__menu.addAction(self.zoomInAct)
        self.__menu.addAction(self.zoomOutAct)
        self.__menu.addAction(self.zoomAct)
        self.__menu.addAction(self.zoomResetAct)
        
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.connect(self, SIGNAL('customContextMenuRequested(const QPoint &)'),
                     self.__showContextMenu)
        
    def __showContextMenu(self, coord):
        """
        Private slot to show the context menu of the listview.
        
        @param coord the position of the mouse pointer (QPoint)
        """
        self.__menu.popup(self.mapToGlobal(coord))
        
    def __initToolBars(self):
        """
        Private method to populate the toolbars with our actions.
        """
        self.windowToolBar = QToolBar(self.trUtf8("Window"), self)
        self.windowToolBar.setIconSize(UI.Config.ToolBarIconSize)
        self.windowToolBar.addAction(self.closeAct)
        
        self.graphicsToolBar = QToolBar(self.trUtf8("Graphics"), self)
        self.graphicsToolBar.setIconSize(UI.Config.ToolBarIconSize)
        self.graphicsToolBar.addAction(self.printPreviewAct)
        self.graphicsToolBar.addAction(self.printAct)
        self.graphicsToolBar.addSeparator()
        self.graphicsToolBar.addAction(self.zoomInAct)
        self.graphicsToolBar.addAction(self.zoomOutAct)
        self.graphicsToolBar.addAction(self.zoomAct)
        self.graphicsToolBar.addAction(self.zoomResetAct)
        
        self.addToolBar(Qt.TopToolBarArea, self.windowToolBar)
        self.addToolBar(Qt.TopToolBarArea, self.graphicsToolBar)
        
    def getDiagramName(self):
        """
        Method to retrieve a name for the diagram.
        
        @return name for the diagram
        """
        return self.svgFile
    
    ############################################################################
    ## Private menu handling methods below.
    ############################################################################
    
    def __adjustScrollBar(self, scrollBar, factor):
        """
        Private method to adjust a scrollbar by a certain factor.
        
        @param scrollBar reference to the scrollbar object (QScrollBar)
        @param factor factor to adjust by (float)
        """
        scrollBar.setValue(int(factor * scrollBar.value()
                                + ((factor - 1) * scrollBar.pageStep()/2)))
        
    def __doZoom(self, factor):
        """
        Private method to perform the zooming.
        
        @param factor zoom factor (float)
        """
        self.zoom *= factor
        self.svgWidget.resize(self.zoom * self.svgWidget.sizeHint())
        
        self.__adjustScrollBar(self.svgView.horizontalScrollBar(), factor)
        self.__adjustScrollBar(self.svgView.verticalScrollBar(), factor)
        
    def __zoomIn(self):
        """
        Private method to handle the zoom in context menu entry.
        """
        self.__doZoom(1.25)
        
    def __zoomOut(self):
        """
        Private method to handle the zoom out context menu entry.
        """
        self.__doZoom(0.8)
        
    def __zoomReset(self):
        """
        Private method to handle the reset zoom context menu entry.
        """
        self.zoom = 1.0
        self.svgWidget.adjustSize()
        
    def __zoom(self):
        """
        Private method to handle the zoom context menu action.
        """
        dlg = ZoomDialog(self.zoom, self)
        if dlg.exec_() == QDialog.Accepted:
            zoom = dlg.getZoomSize()
            factor = zoom / self.zoom
            self.__doZoom(factor)
        
    def __printDiagram(self):
        """
        Private slot called to print the diagram.
        """
        printer = KdeQt.KQPrinter.KQPrinter(mode = QPrinter.ScreenResolution)
        printer.setFullPage(True)
        if Preferences.getPrinter("ColorMode"):
            printer.setColorMode(KdeQt.KQPrinter.Color)
        else:
            printer.setColorMode(KdeQt.KQPrinter.GrayScale)
        if Preferences.getPrinter("FirstPageFirst"):
            printer.setPageOrder(KdeQt.KQPrinter.FirstPageFirst)
        else:
            printer.setPageOrder(KdeQt.KQPrinter.LastPageFirst)
        printer.setPrinterName(Preferences.getPrinter("PrinterName"))
        
        printDialog = KQPrintDialog(printer, self)
        if printDialog.exec_():
            self.__print(printer)
        
    def __printPreviewDiagram(self):
        """
        Private slot called to show a print preview of the diagram.
        """
        from PyQt4.QtGui import QPrintPreviewDialog
        
        printer = KdeQt.KQPrinter.KQPrinter(mode = QPrinter.ScreenResolution)
        printer.setFullPage(True)
        if Preferences.getPrinter("ColorMode"):
            printer.setColorMode(KdeQt.KQPrinter.Color)
        else:
            printer.setColorMode(KdeQt.KQPrinter.GrayScale)
        if Preferences.getPrinter("FirstPageFirst"):
            printer.setPageOrder(KdeQt.KQPrinter.FirstPageFirst)
        else:
            printer.setPageOrder(KdeQt.KQPrinter.LastPageFirst)
        printer.setPrinterName(Preferences.getPrinter("PrinterName"))
        
        preview = QPrintPreviewDialog(printer, self)
        self.connect(preview, SIGNAL("paintRequested(QPrinter*)"), self.__print)
        preview.exec_()
        
    def __print(self, printer):
        """
        Private slot to the actual printing.
        
        @param printer reference to the printer object (QPrinter)
        """
        painter = QPainter()
        painter.begin(printer)

        # calculate margin and width of printout
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

        # write a foot note
        s = QString(self.trUtf8("Diagram: %1").arg(self.getDiagramName()))
        tc = QColor(50, 50, 50)
        painter.setPen(tc)
        painter.drawRect(marginX, marginY, width, height)
        painter.drawLine(marginX, marginY + height + 2, 
                   marginX + width, marginY + height + 2)
        painter.setFont(font)
        painter.drawText(marginX, marginY + height + 4, width,
                   fontHeight, Qt.AlignRight, s)

        # render the diagram
        painter.setViewport(marginX, marginY, width, height)
        self.svgWidget.renderer().render(painter)
        painter.end()
