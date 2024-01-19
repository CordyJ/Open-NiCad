# -*- coding: utf-8 -*-

# Copyright (c) 2007 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a subclass of E4GraphicsView for our diagrams.
"""

import sys

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from E4Graphics.E4GraphicsView import E4GraphicsView

from KdeQt import KQFileDialog, KQMessageBox
import KdeQt.KQPrinter
from KdeQt.KQPrintDialog import KQPrintDialog

from UMLItem import UMLItem
from UMLSceneSizeDialog import UMLSceneSizeDialog
from ZoomDialog import ZoomDialog

import UI.Config
import UI.PixmapCache

import Preferences

class UMLGraphicsView(E4GraphicsView):
    """
    Class implementing a specialized E4GraphicsView for our diagrams.
    
    @signal relayout() emitted to indicate a relayout of the diagram
        is requested
    """
    def __init__(self, scene, diagramName = "Unnamed", parent = None, name = None):
        """
        Constructor
        
        @param scene reference to the scene object (QGraphicsScene)
        @param diagramName name of the diagram (string or QString)
        @param parent parent widget of the view (QWidget)
        @param name name of the view widget (QString or string)
        """
        E4GraphicsView.__init__(self, scene, parent)
        if name:
            self.setObjectName(name)
        
        self.diagramName = diagramName
        
        self.border = 10
        self.deltaSize = 100.0
        
        self.__initActions()
        
        self.connect(scene, SIGNAL("changed(const QList<QRectF> &)"), self.__sceneChanged)
        
    def __initActions(self):
        """
        Private method to initialize the view actions.
        """
        self.deleteShapeAct = \
            QAction(UI.PixmapCache.getIcon("deleteShape.png"),
                    self.trUtf8("Delete shapes"), self)
        self.connect(self.deleteShapeAct, SIGNAL("triggered()"), self.__deleteShape)
        
        self.saveAct = \
            QAction(UI.PixmapCache.getIcon("fileSave.png"),
                    self.trUtf8("Save as PNG"), self)
        self.connect(self.saveAct, SIGNAL("triggered()"), self.__saveImage)
        
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
        self.connect(self.zoomInAct, SIGNAL("triggered()"), self.zoomIn)
        
        self.zoomOutAct = \
            QAction(UI.PixmapCache.getIcon("zoomOut.png"),
                    self.trUtf8("Zoom out"), self)
        self.connect(self.zoomOutAct, SIGNAL("triggered()"), self.zoomOut)
        
        self.zoomAct = \
            QAction(UI.PixmapCache.getIcon("zoomTo.png"),
                    self.trUtf8("Zoom..."), self)
        self.connect(self.zoomAct, SIGNAL("triggered()"), self.__zoom)
        
        self.zoomResetAct = \
            QAction(UI.PixmapCache.getIcon("zoomReset.png"),
                    self.trUtf8("Zoom reset"), self)
        self.connect(self.zoomResetAct, SIGNAL("triggered()"), self.zoomReset)
        
        self.incWidthAct = \
            QAction(UI.PixmapCache.getIcon("sceneWidthInc.png"),
                    self.trUtf8("Increase width by %1 points").arg(self.deltaSize), self)
        self.connect(self.incWidthAct, SIGNAL("triggered()"), self.__incWidth)
        
        self.incHeightAct = \
            QAction(UI.PixmapCache.getIcon("sceneHeightInc.png"),
                    self.trUtf8("Increase height by %1 points").arg(self.deltaSize), self)
        self.connect(self.incHeightAct, SIGNAL("triggered()"), self.__incHeight)
        
        self.decWidthAct = \
            QAction(UI.PixmapCache.getIcon("sceneWidthDec.png"),
                    self.trUtf8("Decrease width by %1 points").arg(self.deltaSize), self)
        self.connect(self.decWidthAct, SIGNAL("triggered()"), self.__decWidth)
        
        self.decHeightAct = \
            QAction(UI.PixmapCache.getIcon("sceneHeightDec.png"),
                    self.trUtf8("Decrease height by %1 points").arg(self.deltaSize), self)
        self.connect(self.decHeightAct, SIGNAL("triggered()"), self.__decHeight)
        
        self.setSizeAct = \
            QAction(UI.PixmapCache.getIcon("sceneSize.png"),
                    self.trUtf8("Set size"), self)
        self.connect(self.setSizeAct, SIGNAL("triggered()"), self.__setSize)
        
        self.relayoutAct = \
            QAction(UI.PixmapCache.getIcon("reload.png"),
                    self.trUtf8("Re-Layout"), self)
        self.connect(self.relayoutAct, SIGNAL("triggered()"), self.__relayout)
        
        self.alignLeftAct = \
            QAction(UI.PixmapCache.getIcon("shapesAlignLeft"), 
                    self.trUtf8("Align Left"), self)
        self.connect(self.alignLeftAct, SIGNAL("triggered()"), 
            lambda align=Qt.AlignLeft: self.__alignShapes(align))
        
        self.alignHCenterAct = \
            QAction(UI.PixmapCache.getIcon("shapesAlignHCenter"), 
                    self.trUtf8("Align Center Horizontal"), self)
        self.connect(self.alignHCenterAct, SIGNAL("triggered()"), 
            lambda align=Qt.AlignHCenter: self.__alignShapes(align))
        
        self.alignRightAct = \
            QAction(UI.PixmapCache.getIcon("shapesAlignRight"), 
                    self.trUtf8("Align Right"), self)
        self.connect(self.alignRightAct, SIGNAL("triggered()"), 
            lambda align=Qt.AlignRight: self.__alignShapes(align))
        
        self.alignTopAct = \
            QAction(UI.PixmapCache.getIcon("shapesAlignTop"), 
                    self.trUtf8("Align Top"), self)
        self.connect(self.alignTopAct, SIGNAL("triggered()"), 
            lambda align=Qt.AlignTop: self.__alignShapes(align))
        
        self.alignVCenterAct = \
            QAction(UI.PixmapCache.getIcon("shapesAlignVCenter"), 
                    self.trUtf8("Align Center Vertical"), self)
        self.connect(self.alignVCenterAct, SIGNAL("triggered()"), 
            lambda align=Qt.AlignVCenter: self.__alignShapes(align))
        
        self.alignBottomAct = \
            QAction(UI.PixmapCache.getIcon("shapesAlignBottom"), 
                    self.trUtf8("Align Bottom"), self)
        self.connect(self.alignBottomAct, SIGNAL("triggered()"), 
            lambda align=Qt.AlignBottom: self.__alignShapes(align))
        
    def __checkSizeActions(self):
        """
        Private slot to set the enabled state of the size actions.
        """
        diagramSize = self._getDiagramSize(10)
        sceneRect = self.scene().sceneRect()
        if (sceneRect.width() - self.deltaSize) <= diagramSize.width():
            self.decWidthAct.setEnabled(False)
        else:
            self.decWidthAct.setEnabled(True)
        if (sceneRect.height() - self.deltaSize) <= diagramSize.height():
            self.decHeightAct.setEnabled(False)
        else:
            self.decHeightAct.setEnabled(True)
        
    def __sceneChanged(self, areas):
        """
        Private slot called when the scene changes.
        
        @param areas list of rectangles that contain changes (list of QRectF)
        """
        if len(self.scene().selectedItems()) > 0:
            self.deleteShapeAct.setEnabled(True)
        else:
            self.deleteShapeAct.setEnabled(False)
        
    def initToolBar(self):
        """
        Public method to populate a toolbar with our actions.
        
        @return the populated toolBar (QToolBar)
        """
        toolBar = QToolBar(self.trUtf8("Graphics"), self)
        toolBar.setIconSize(UI.Config.ToolBarIconSize)
        toolBar.addAction(self.deleteShapeAct)
        toolBar.addSeparator()
        toolBar.addAction(self.saveAct)
        toolBar.addSeparator()
        toolBar.addAction(self.printPreviewAct)
        toolBar.addAction(self.printAct)
        toolBar.addSeparator()
        toolBar.addAction(self.zoomInAct)
        toolBar.addAction(self.zoomOutAct)
        toolBar.addAction(self.zoomAct)
        toolBar.addAction(self.zoomResetAct)
        toolBar.addSeparator()
        toolBar.addAction(self.alignLeftAct)
        toolBar.addAction(self.alignHCenterAct)
        toolBar.addAction(self.alignRightAct)
        toolBar.addAction(self.alignTopAct)
        toolBar.addAction(self.alignVCenterAct)
        toolBar.addAction(self.alignBottomAct)
        toolBar.addSeparator()
        toolBar.addAction(self.incWidthAct)
        toolBar.addAction(self.incHeightAct)
        toolBar.addAction(self.decWidthAct)
        toolBar.addAction(self.decHeightAct)
        toolBar.addAction(self.setSizeAct)
        toolBar.addSeparator()
        toolBar.addAction(self.relayoutAct)
        
        return toolBar
        
    def filteredItems(self, items):
        """
        Public method to filter a list of items.
        
        @param items list of items as returned by the scene object
            (QGraphicsItem)
        @return list of interesting collision items (QGraphicsItem)
        """
        return [itm for itm in items if isinstance(itm, UMLItem)]
        
    def selectItems(self, items):
        """
        Public method to select the given items.
        
        @param items list of items to be selected (list of QGraphicsItemItem)
        """
        # step 1: deselect all items
        self.unselectItems()
        
        # step 2: select all given items
        for itm in items:
            if isinstance(itm, UMLWidget):
                itm.setSelected(True)
        
    def selectItem(self, item):
        """
        Public method to select an item.
        
        @param item item to be selected (QGraphicsItemItem)
        """
        if isinstance(item, UMLWidget):
            item.setSelected(not item.isSelected())
        
    def __deleteShape(self):
        """
        Private method to delete the selected shapes from the display.
        """
        for item in self.scene().selectedItems():
            item.removeAssociations()
            item.setSelected(False)
            self.scene().removeItem(item)
            del item
        
    def __incWidth(self):
        """
        Private method to handle the increase width context menu entry.
        """
        self.resizeScene(self.deltaSize, True)
        self.__checkSizeActions()
        
    def __incHeight(self):
        """
        Private method to handle the increase height context menu entry.
        """
        self.resizeScene(self.deltaSize, False)
        self.__checkSizeActions()
        
    def __decWidth(self):
        """
        Private method to handle the decrease width context menu entry.
        """
        self.resizeScene(-self.deltaSize, True)
        self.__checkSizeActions()
        
    def __decHeight(self):
        """
        Private method to handle the decrease height context menu entry.
        """
        self.resizeScene(-self.deltaSize, False)
        self.__checkSizeActions()
        
    def __setSize(self):
        """
        Private method to handle the set size context menu entry.
        """
        rect = self._getDiagramRect(10)
        sceneRect = self.scene().sceneRect()
        dlg = UMLSceneSizeDialog(sceneRect.width(), sceneRect.height(),
                                  rect.width(), rect.height(), self)
        if dlg.exec_() == QDialog.Accepted:
            width, height = dlg.getData()
            self.setSceneSize(width, height)
        self.__checkSizeActions()
        
    def __saveImage(self):
        """
        Private method to handle the save context menu entry.
        """
        selectedFilter = QString('')
        fname = KQFileDialog.getSaveFileName(\
            self,
            self.trUtf8("Save Diagram"),
            QString(),
            self.trUtf8("Portable Network Graphics (*.png);;"
                        "Scalable Vector Graphics (*.svg)"),
            selectedFilter,
            QFileDialog.Options(QFileDialog.DontConfirmOverwrite))
        if not fname.isEmpty():
            ext = QFileInfo(fname).suffix()
            if ext.isEmpty():
                ex = selectedFilter.section('(*',1,1).section(')',0,0)
                if not ex.isEmpty():
                    fname.append(ex)
            if QFileInfo(fname).exists():
                res = KQMessageBox.warning(self,
                    self.trUtf8("Save Diagram"),
                    self.trUtf8("<p>The file <b>%1</b> already exists.</p>")
                        .arg(fname),
                    QMessageBox.StandardButtons(\
                        QMessageBox.Abort | \
                        QMessageBox.Save),
                    QMessageBox.Abort)
                if res == QMessageBox.Abort or res == QMessageBox.Cancel:
                    return
            
            success = self.saveImage(fname, QFileInfo(fname).suffix().toUpper())
            if not success:
                KQMessageBox.critical(None,
                    self.trUtf8("Save Diagram"),
                    self.trUtf8("""<p>The file <b>%1</b> could not be saved.</p>""")
                        .arg(fname))
        
    def __relayout(self):
        """
        Private method to handle the re-layout context menu entry.
        """
        scene = self.scene()
        for itm in scene.items()[:]:
            if itm.scene() == scene:
                scene.removeItem(itm)
        self.emit(SIGNAL("relayout()"))
        
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
            self.printDiagram(printer, self.diagramName)
        
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
        self.connect(preview, SIGNAL("paintRequested(QPrinter*)"), self.printDiagram)
        preview.exec_()
        
    def __zoom(self):
        """
        Private method to handle the zoom context menu action.
        """
        dlg = ZoomDialog(self.zoom(), self)
        if dlg.exec_() == QDialog.Accepted:
            zoom = dlg.getZoomSize()
            self.setZoom(zoom)
        
    def setDiagramName(self, name):
        """
        Public slot to set the diagram name.
        
        @param name diagram name (string or QString)
        """
        self.diagramName = name
        
    def __alignShapes(self, alignment):
        """
        Private slot to align the selected shapes.
        
        @param alignment alignment type (Qt.AlignmentFlag)
        """
        # step 1: get all selected items
        items = self.scene().selectedItems()
        if len(items) <= 1:
            return
        
        # step 2: find the index of the item to align in relation to
        amount = None
        for i, item in enumerate(items):
            rect = item.sceneBoundingRect()
            if alignment == Qt.AlignLeft:
                if amount is None or rect.x() < amount:
                    amount = rect.x()
                    index = i
            elif alignment == Qt.AlignRight:
                if amount is None or rect.x() + rect.width() > amount:
                    amount = rect.x() + rect.width()
                    index = i
            elif alignment == Qt.AlignHCenter:
                if amount is None or rect.width() > amount:
                    amount = rect.width()
                    index = i
            elif alignment == Qt.AlignTop:
                if amount is None or rect.y() < amount:
                    amount = rect.y()
                    index = i
            elif alignment == Qt.AlignBottom:
                if amount is None or rect.y() + rect.height() > amount:
                    amount = rect.y() + rect.height()
                    index = i
            elif alignment == Qt.AlignVCenter:
                if amount is None or rect.height() > amount:
                    amount = rect.height()
                    index = i
        rect = items[index].sceneBoundingRect()
        
        # step 3: move the other items
        for i, item in enumerate(items):
            if i == index:
                continue
            itemrect = item.sceneBoundingRect()
            xOffset = yOffset = 0
            if alignment == Qt.AlignLeft:
                xOffset = rect.x() - itemrect.x()
            elif alignment == Qt.AlignRight:
                xOffset = (rect.x() + rect.width()) - \
                          (itemrect.x() + itemrect.width())
            elif alignment == Qt.AlignHCenter:
                xOffset = (rect.x() + rect.width() / 2) - \
                          (itemrect.x() + itemrect.width() / 2)
            elif alignment == Qt.AlignTop:
                yOffset = rect.y() - itemrect.y()
            elif alignment == Qt.AlignBottom:
                yOffset = (rect.y() + rect.height()) - \
                          (itemrect.y() + itemrect.height())
            elif alignment == Qt.AlignVCenter:
                yOffset = (rect.y() + rect.height() / 2) - \
                          (itemrect.y() + itemrect.height() / 2)
            item.moveBy(xOffset, yOffset)
        
        self.scene().update()
