# -*- coding: utf-8 -*-

# Copyright (c) 2004 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the UI Previewer main window.
"""

import sys

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4 import uic

from KdeQt import KQFileDialog, KQMessageBox
from KdeQt.KQMainWindow import KQMainWindow
import KdeQt.KQPrinter
from KdeQt.KQPrintDialog import KQPrintDialog
import KdeQt

import Preferences
import UI.PixmapCache
import UI.Config


class UIPreviewer(KQMainWindow):
    """
    Class implementing the UI Previewer main window.
    """
    def __init__(self, filename = None, parent = None, name = None):
        """
        Constructor
        
        @param filename name of a UI file to load
        @param parent parent widget of this window (QWidget)
        @param name name of this window (string or QString)
        """
        self.mainWidget = None
        self.currentFile = QDir.currentPath()
        
        KQMainWindow.__init__(self, parent)
        if not name:
            self.setObjectName("UIPreviewer")
        else:
            self.setObjectName(name)
        self.resize(QSize(600, 480).expandedTo(self.minimumSizeHint()))
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.statusBar()
        
        self.setWindowIcon(UI.PixmapCache.getIcon("eric.png"))
        self.setWindowTitle(self.trUtf8("UI Previewer"))

        self.cw = QWidget(self)
        self.cw.setObjectName("centralWidget")
        
        self.UIPreviewerLayout = QVBoxLayout(self.cw)
        self.UIPreviewerLayout.setMargin(6)
        self.UIPreviewerLayout.setSpacing(6)
        self.UIPreviewerLayout.setObjectName("UIPreviewerLayout")

        self.styleLayout = QHBoxLayout()
        self.styleLayout.setMargin(0)
        self.styleLayout.setSpacing(6)
        self.styleLayout.setObjectName("styleLayout")

        self.styleLabel = QLabel(self.trUtf8("Select GUI Theme"), self.cw)
        self.styleLabel.setObjectName("styleLabel")
        self.styleLayout.addWidget(self.styleLabel)

        self.styleCombo = QComboBox(self.cw)
        self.styleCombo.setObjectName("styleCombo")
        self.styleCombo.setEditable(False)
        self.styleCombo.setToolTip(self.trUtf8("Select the GUI Theme"))
        self.styleLayout.addWidget(self.styleCombo)
        self.styleCombo.addItems(QStyleFactory().keys())
        self.styleCombo.setCurrentIndex(\
            Preferences.Prefs.settings.value('UIPreviewer/style').toInt()[0])
        
        styleSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.styleLayout.addItem(styleSpacer)
        self.UIPreviewerLayout.addLayout(self.styleLayout)

        self.previewSV = QScrollArea(self.cw)
        self.previewSV.setObjectName("preview")
        self.previewSV.setFrameShape(QFrame.NoFrame)
        self.previewSV.setFrameShadow(QFrame.Plain)
        self.previewSV.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.UIPreviewerLayout.addWidget(self.previewSV)

        self.setCentralWidget(self.cw)
        
        self.connect(self.styleCombo, SIGNAL("activated(const QString&)"),
                     self.__guiStyleSelected)
        
        self.__initActions()
        self.__initMenus()
        self.__initToolbars()
        
        self.__updateActions()
        
        # defere loading of a UI file until we are shown
        self.fileToLoad = filename
        
    def show(self):
        """
        Public slot to show this dialog.
        
        This overloaded slot loads a UI file to be previewed after
        the main window has been shown. This way, previewing a dialog
        doesn't interfere with showing the main window.
        """
        QMainWindow.show(self)
        if self.fileToLoad is not None:
            fn, self.fileToLoad = (self.fileToLoad, None)
            self.__loadFile(fn)
            
    def __initActions(self):
        """
        Private method to define the user interface actions.
        """
        self.openAct = QAction(UI.PixmapCache.getIcon("openUI.png"), 
                        self.trUtf8('&Open File'), self)
        self.openAct.setShortcut(QKeySequence(self.trUtf8("Ctrl+O","File|Open")))
        self.openAct.setStatusTip(self.trUtf8('Open a UI file for display'))
        self.openAct.setWhatsThis(self.trUtf8(
                """<b>Open File</b>"""
                """<p>This opens a new UI file for display.</p>"""
        ))
        self.connect(self.openAct, SIGNAL('triggered()'), self.__openFile)
        
        self.printAct = QAction(UI.PixmapCache.getIcon("print.png"), 
                        self.trUtf8('&Print'), self)
        self.printAct.setShortcut(QKeySequence(self.trUtf8("Ctrl+P","File|Print")))
        self.printAct.setStatusTip(self.trUtf8('Print a screen capture'))
        self.printAct.setWhatsThis(self.trUtf8(
                """<b>Print</b>"""
                """<p>Print a screen capture.</p>"""
        ))
        self.connect(self.printAct, SIGNAL('triggered()'), self.__printImage)
        
        self.printPreviewAct = QAction(UI.PixmapCache.getIcon("printPreview.png"), 
                        self.trUtf8('Print Preview'), self)
        self.printPreviewAct.setStatusTip(self.trUtf8(
                'Print preview a screen capture'))
        self.printPreviewAct.setWhatsThis(self.trUtf8(
                """<b>Print Preview</b>"""
                """<p>Print preview a screen capture.</p>"""
        ))
        self.connect(self.printPreviewAct, SIGNAL('triggered()'), 
            self.__printPreviewImage)
        
        self.imageAct = QAction(UI.PixmapCache.getIcon("screenCapture.png"), 
                        self.trUtf8('&Screen Capture'), self)
        self.imageAct.setShortcut(\
            QKeySequence(self.trUtf8("Ctrl+S","File|Screen Capture")))
        self.imageAct.setStatusTip(self.trUtf8('Save a screen capture to an image file'))
        self.imageAct.setWhatsThis(self.trUtf8(
                """<b>Screen Capture</b>"""
                """<p>Save a screen capture to an image file.</p>"""
        ))
        self.connect(self.imageAct, SIGNAL('triggered()'), self.__saveImage)
        
        self.exitAct = QAction(UI.PixmapCache.getIcon("exit.png"), 
                        self.trUtf8('&Quit'), self)
        self.exitAct.setShortcut(QKeySequence(self.trUtf8("Ctrl+Q","File|Quit")))
        self.exitAct.setStatusTip(self.trUtf8('Quit the application'))
        self.exitAct.setWhatsThis(self.trUtf8(
                """<b>Quit</b>"""
                """<p>Quit the application.</p>"""
        ))
        self.connect(self.exitAct, SIGNAL('triggered()'), 
                     qApp, SLOT('closeAllWindows()'))
        
        self.copyAct = QAction(UI.PixmapCache.getIcon("editCopy.png"),
                            self.trUtf8('&Copy'), self)
        self.copyAct.setShortcut(QKeySequence(self.trUtf8("Ctrl+C","Edit|Copy")))
        self.copyAct.setStatusTip(self.trUtf8('Copy screen capture to clipboard'))
        self.copyAct.setWhatsThis(self.trUtf8(
                """<b>Copy</b>"""
                """<p>Copy screen capture to clipboard.</p>"""
        ))
        self.connect(self.copyAct,SIGNAL('triggered()'),self.__copyImageToClipboard)
        
        self.whatsThisAct = QAction(UI.PixmapCache.getIcon("whatsThis.png"),
                                self.trUtf8('&What\'s This?'), self)
        self.whatsThisAct.setShortcut(QKeySequence(self.trUtf8("Shift+F1")))
        self.whatsThisAct.setStatusTip(self.trUtf8('Context sensitive help'))
        self.whatsThisAct.setWhatsThis(self.trUtf8(
                """<b>Display context sensitive help</b>"""
                """<p>In What's This? mode, the mouse cursor shows an arrow with a"""
                """ question mark, and you can click on the interface elements to get"""
                """ a short description of what they do and how to use them. In"""
                """ dialogs, this feature can be accessed using the context help"""
                """ button in the titlebar.</p>"""
        ))
        self.connect(self.whatsThisAct,SIGNAL('triggered()'),self.__whatsThis)

        self.aboutAct = QAction(self.trUtf8('&About'), self)
        self.aboutAct.setStatusTip(self.trUtf8('Display information about this software'))
        self.aboutAct.setWhatsThis(self.trUtf8(
                """<b>About</b>"""
                """<p>Display some information about this software.</p>"""
        ))
        self.connect(self.aboutAct,SIGNAL('triggered()'),self.__about)
                     
        self.aboutQtAct = QAction(self.trUtf8('About &Qt'), self)
        self.aboutQtAct.setStatusTip(\
            self.trUtf8('Display information about the Qt toolkit'))
        self.aboutQtAct.setWhatsThis(self.trUtf8(
                """<b>About Qt</b>"""
                """<p>Display some information about the Qt toolkit.</p>"""
        ))
        self.connect(self.aboutQtAct,SIGNAL('triggered()'),self.__aboutQt)

    def __initMenus(self):
        """
        Private method to create the menus.
        """
        mb = self.menuBar()

        menu = mb.addMenu(self.trUtf8('&File'))
        menu.setTearOffEnabled(True)
        menu.addAction(self.openAct)
        menu.addAction(self.imageAct)
        menu.addSeparator()
        menu.addAction(self.printPreviewAct)
        menu.addAction(self.printAct)
        menu.addSeparator()
        menu.addAction(self.exitAct)
        
        menu = mb.addMenu(self.trUtf8("&Edit"))
        menu.setTearOffEnabled(True)
        menu.addAction(self.copyAct)
        
        mb.addSeparator()
        
        menu = mb.addMenu(self.trUtf8('&Help'))
        menu.setTearOffEnabled(True)
        menu.addAction(self.aboutAct)
        menu.addAction(self.aboutQtAct)
        menu.addSeparator()
        menu.addAction(self.whatsThisAct)

    def __initToolbars(self):
        """
        Private method to create the toolbars.
        """
        filetb = self.addToolBar(self.trUtf8("File"))
        filetb.setIconSize(UI.Config.ToolBarIconSize)
        filetb.addAction(self.openAct)
        filetb.addAction(self.imageAct)
        filetb.addSeparator()
        filetb.addAction(self.printPreviewAct)
        filetb.addAction(self.printAct)
        filetb.addSeparator()
        filetb.addAction(self.exitAct)
        
        edittb = self.addToolBar(self.trUtf8("Edit"))
        edittb.setIconSize(UI.Config.ToolBarIconSize)
        edittb.addAction(self.copyAct)
        
        helptb = self.addToolBar(self.trUtf8("Help"))
        helptb.setIconSize(UI.Config.ToolBarIconSize)
        helptb.addAction(self.whatsThisAct)

    def __whatsThis(self):
        """
        Private slot called in to enter Whats This mode.
        """
        QWhatsThis.enterWhatsThisMode()
        
    def __guiStyleSelected(self, selectedStyle):
        """
        Private slot to handle the selection of a GUI style.
        
        @param selectedStyle name of the selected style (QString)
        """
        if self.mainWidget:
            self.__updateChildren(selectedStyle)
    
    def __about(self):
        """
        Private slot to show the about information.
        """
        KQMessageBox.about(self, self.trUtf8("UI Previewer"), self.trUtf8(
            """<h3> About UI Previewer </h3>"""
            """<p>The UI Previewer loads and displays Qt User-Interface files"""
            """ with various styles, which are selectable via a selection list.</p>"""
        ))
    
    def __aboutQt(self):
        """
        Private slot to show info about Qt.
        """
        QMessageBox.aboutQt(self, self.trUtf8("UI Previewer"))

    def __openFile(self):
        """
        Private slot to load a new file.
        """
        fn = KQFileDialog.getOpenFileName(\
            self, 
            self.trUtf8("Select UI file"),
            self.currentFile,
            self.trUtf8("Qt User-Interface Files (*.ui)"))
        if not fn.isEmpty():
            self.__loadFile(fn)
        
    def __loadFile(self, fn):
        """
        Private slot to load a ui file.
        
        @param fn name of the ui file to be laoded (string or QString)
        """
        if self.mainWidget:
            self.mainWidget.close()
            self.previewSV.takeWidget()
            del self.mainWidget
            self.mainWidget = None
            
        # load the file
        try:
            self.mainWidget = uic.loadUi(fn)
        except:
            pass
        
        if self.mainWidget:
            self.currentFile = fn
            self.__updateChildren(self.styleCombo.currentText())
            if isinstance(self.mainWidget, QDialog) or \
               isinstance(self.mainWidget, QMainWindow):
                self.mainWidget.show()
                self.mainWidget.installEventFilter(self)
            else:
                self.previewSV.setWidget(self.mainWidget)
                self.mainWidget.show()
        else:
            KQMessageBox.warning(None,
                self.trUtf8("Load UI File"),
                self.trUtf8("""<p>The file <b>%1</b> could not be loaded.</p>""")\
                    .arg(fn))
        self.__updateActions()
    
    def __updateChildren(self, sstyle):
        """
        Private slot to change the style of the show UI.
        
        @param sstyle name of the selected style (QString)
        """
        QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
        qstyle = QStyleFactory.create(sstyle)
        self.mainWidget.setStyle(qstyle)
        
        lst = self.mainWidget.findChildren(QWidget)
        for obj in lst:
            try:
                obj.setStyle(qstyle)
            except AttributeError:
                pass
        del lst
        
        self.mainWidget.hide()
        self.mainWidget.show()
        
        self.lastQStyle = qstyle
        self.lastStyle = QString(sstyle)
        Preferences.Prefs.settings.setValue('UIPreviewer/style', 
            QVariant(self.styleCombo.currentIndex()))
        QApplication.restoreOverrideCursor()
    
    def __updateActions(self):
        """
        Private slot to update the actions state.
        """
        if self.mainWidget:
            self.imageAct.setEnabled(True)
            self.printAct.setEnabled(True)
            if self.printPreviewAct:
                self.printPreviewAct.setEnabled(True)
            self.copyAct.setEnabled(True)
            self.styleCombo.setEnabled(True)
        else:
            self.imageAct.setEnabled(False)
            self.printAct.setEnabled(False)
            if self.printPreviewAct:
                self.printPreviewAct.setEnabled(False)
            self.copyAct.setEnabled(False)
            self.styleCombo.setEnabled(False)

    def __handleCloseEvent(self):
        """
        Private slot to handle the close event of a viewed QMainWidget.
        """
        if self.mainWidget:
            self.mainWidget.removeEventFilter(self)
            del self.mainWidget
            self.mainWidget = None
        self.__updateActions()
    
    def eventFilter(self, obj, ev):
        """
        Protected method called to filter an event.
        
        @param object object, that generated the event (QObject)
        @param event the event, that was generated by object (QEvent)
        @return flag indicating if event was filtered out
        """
        if obj == self.mainWidget:
            if ev.type() == QEvent.Close:
                self.__handleCloseEvent()
            return True
        else:
            if isinstance(self.mainWidget, QDialog):
                return QDialog.eventFilter(self, obj, ev)
            elif isinstance(self.mainWidget, QMainWindow):
                return QMainWindow.eventFilter(self, obj, ev)
            else:
                return False
    
    def __saveImage(self):
        """
        Private slot to handle the Save Image menu action.
        """
        if self.mainWidget is None:
            KQMessageBox.critical(None,
                self.trUtf8("Save Image"),
                self.trUtf8("""There is no UI file loaded."""))
            return
        
        defaultExt = "PNG"
        filters = ""
        formats = QImageWriter.supportedImageFormats()
        for format in formats:
            filters = "%s*.%s " % (filters, unicode(QString(format)).lower())
        filter = self.trUtf8("Images (%1)").arg(QString(filters[:-1]))
        
        fname = KQFileDialog.getSaveFileName(\
            self,
            self.trUtf8("Save Image"),
            QString(),
            filter)
        if fname.isEmpty():
            return
            
        ext = QFileInfo(fname).suffix().toUpper()
        if ext.isEmpty():
            ext = defaultExt
            fname.append(".%s" % defaultExt.lower())
        
        pix = QPixmap.grabWidget(self.mainWidget)
        self.__updateChildren(self.lastStyle)
        if not pix.save(fname, str(ext)):
            KQMessageBox.critical(None,
                self.trUtf8("Save Image"),
                self.trUtf8("""<p>The file <b>%1</b> could not be saved.</p>""")
                    .arg(fname))

    def __copyImageToClipboard(self):
        """
        Private slot to handle the Copy Image menu action.
        """
        if self.mainWidget is None:
            KQMessageBox.critical(None,
                self.trUtf8("Save Image"),
                self.trUtf8("""There is no UI file loaded."""))
            return
        
        cb = QApplication.clipboard()
        cb.setPixmap(QPixmap.grabWidget(self.mainWidget))
        self.__updateChildren(self.lastStyle)
    
    def __printImage(self):
        """
        Private slot to handle the Print Image menu action.
        """
        if self.mainWidget is None:
            KQMessageBox.critical(None,
                self.trUtf8("Print Image"),
                self.trUtf8("""There is no UI file loaded."""))
            return
        
        settings = Preferences.Prefs.settings
        printer = KdeQt.KQPrinter.KQPrinter(mode = QPrinter.HighResolution)
        printer.setFullPage(True)
        
        if not KdeQt.isKDE():
            printer.setPrinterName(settings.value("UIPreviewer/printername").toString())
            printer.setPageSize(
                QPrinter.PageSize(settings.value("UIPreviewer/pagesize").toInt()[0]))
            printer.setPageOrder(
                QPrinter.PageOrder(settings.value("UIPreviewer/pageorder").toInt()[0]))
            printer.setOrientation(
                QPrinter.Orientation(settings.value("UIPreviewer/orientation").toInt()[0]))
            printer.setColorMode(
                QPrinter.ColorMode(settings.value("UIPreviewer/colormode").toInt()[0]))
        
        printDialog = KQPrintDialog(printer, self)
        if printDialog.exec_() == QDialog.Accepted:
            self.statusBar().showMessage(self.trUtf8("Printing the image..."))
            self.__print(printer)
            
            if not KdeQt.isKDE():
                settings.setValue("UIPreviewer/printername", 
                    QVariant(printer.printerName()))
                settings.setValue("UIPreviewer/pagesize", QVariant(printer.pageSize()))
                settings.setValue("UIPreviewer/pageorder", QVariant(printer.pageOrder()))
                settings.setValue("UIPreviewer/orientation", 
                    QVariant(printer.orientation()))
                settings.setValue("UIPreviewer/colormode", QVariant(printer.colorMode()))
        
        self.statusBar().showMessage(self.trUtf8("Image sent to printer..."), 2000)

    def __printPreviewImage(self):
        """
        Private slot to handle the Print Preview menu action.
        """
        from PyQt4.QtGui import QPrintPreviewDialog
        
        if self.mainWidget is None:
            KQMessageBox.critical(None,
                self.trUtf8("Print Preview"),
                self.trUtf8("""There is no UI file loaded."""))
            return
        
        settings = Preferences.Prefs.settings
        printer = KdeQt.KQPrinter.KQPrinter(mode = QPrinter.HighResolution)
        printer.setFullPage(True)
        
        if not KdeQt.isKDE():
            printer.setPrinterName(settings.value("UIPreviewer/printername").toString())
            printer.setPageSize(
                QPrinter.PageSize(settings.value("UIPreviewer/pagesize").toInt()[0]))
            printer.setPageOrder(
                QPrinter.PageOrder(settings.value("UIPreviewer/pageorder").toInt()[0]))
            printer.setOrientation(
                QPrinter.Orientation(settings.value("UIPreviewer/orientation").toInt()[0]))
            printer.setColorMode(
                QPrinter.ColorMode(settings.value("UIPreviewer/colormode").toInt()[0]))
        
        preview = QPrintPreviewDialog(printer, self)
        self.connect(preview, SIGNAL("paintRequested(QPrinter*)"), self.__print)
        preview.exec_()
        
    def __print(self, printer):
        """
        Private slot to the actual printing.
        
        @param printer reference to the printer object (QPrinter)
        """
        p = QPainter(printer)
        marginX = (printer.pageRect().x() - printer.paperRect().x()) / 2
        marginY = (printer.pageRect().y() - printer.paperRect().y()) / 2

        # double the margin on bottom of page
        if printer.orientation() == KdeQt.KQPrinter.Portrait:
            width = printer.width() - marginX * 2
            height = printer.height() - marginY * 3
        else:
            marginX *= 2
            width = printer.width() - marginX * 2
            height = printer.height() - marginY * 2
        img = QPixmap.grabWidget(self.mainWidget).toImage()
        self.__updateChildren(self.lastStyle)
        p.drawImage(marginX, marginY, 
                    img.scaled(width, height, 
                               Qt.KeepAspectRatio, Qt.SmoothTransformation))
        p.end()
