# -*- coding: utf-8 -*-

# Copyright (c) 2004 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the TR Previewer main window.
"""

import sys

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4 import uic

from KdeQt import KQFileDialog, KQMessageBox
from KdeQt.KQMainWindow import KQMainWindow
import KdeQt

from TRSingleApplication import TRSingleApplicationServer

import Preferences
import UI.PixmapCache
import UI.Config


noTranslationName = QApplication.translate("TRPreviewer", "<No translation>")

class TRPreviewer(KQMainWindow):
    """
    Class implementing the UI Previewer main window.
    """
    def __init__(self, filenames = [], parent = None, name = None):
        """
        Constructor
        
        @param filenames filenames of form and/or translation files to load
        @param parent parent widget of this window (QWidget)
        @param name name of this window (string or QString)
        """
        self.mainWidget = None
        self.currentFile = QDir.currentPath()
        
        KQMainWindow.__init__(self, parent)
        if not name:
            self.setObjectName("TRPreviewer")
        else:
            self.setObjectName(name)
        self.resize(QSize(800, 600).expandedTo(self.minimumSizeHint()))
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.statusBar()
        
        self.setWindowIcon(UI.PixmapCache.getIcon("eric.png"))
        self.setWindowTitle(self.trUtf8("Translations Previewer"))

        self.cw = QWidget(self)
        self.cw.setObjectName("qt_central_widget")
        
        self.TRPreviewerLayout = QVBoxLayout(self.cw)
        self.TRPreviewerLayout.setMargin(6)
        self.TRPreviewerLayout.setSpacing(6)
        self.TRPreviewerLayout.setObjectName("TRPreviewerLayout")

        self.languageLayout = QHBoxLayout()
        self.languageLayout.setMargin(0)
        self.languageLayout.setSpacing(6)
        self.languageLayout.setObjectName("languageLayout")

        self.languageLabel = QLabel(self.trUtf8("Select language file"), self.cw)
        self.languageLabel.setObjectName("languageLabel")
        self.languageLayout.addWidget(self.languageLabel)

        self.languageCombo = QComboBox(self.cw)
        self.languageCombo.setObjectName("languageCombo")
        self.languageCombo.setEditable(False)
        self.languageCombo.setToolTip(self.trUtf8("Select language file"))
        self.languageLayout.addWidget(self.languageCombo)
        
        languageSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.languageLayout.addItem(languageSpacer)
        self.TRPreviewerLayout.addLayout(self.languageLayout)

        self.preview = WidgetWorkspace(self.cw)
        self.preview.setObjectName("preview")
        self.TRPreviewerLayout.addWidget(self.preview)
        self.connect(self.preview, SIGNAL('lastWidgetClosed'), self.__updateActions)

        self.setCentralWidget(self.cw)
        
        self.connect(self.languageCombo,SIGNAL("activated(const QString&)"),
                     self.setTranslation)
        
        self.translations = TranslationsDict(self.languageCombo, self)
        self.connect(self.translations, SIGNAL('translationChanged'),
                     self.preview, SIGNAL('rebuildWidgets'))
        
        self.__initActions()
        self.__initMenus()
        self.__initToolbars()
        
        self.__updateActions()
        
        # fire up the single application server
        self.SAServer = TRSingleApplicationServer(self)
        self.connect(self.SAServer, SIGNAL('loadForm'), self.preview.loadWidget)
        self.connect(self.SAServer, SIGNAL('loadTranslation'), self.translations.add)
        
        # defere loading of a UI file until we are shown
        self.filesToLoad = filenames[:]
        
    def show(self):
        """
        Public slot to show this dialog.
        
        This overloaded slot loads a UI file to be previewed after
        the main window has been shown. This way, previewing a dialog
        doesn't interfere with showing the main window.
        """
        QMainWindow.show(self)
        if self.filesToLoad:
            filenames, self.filesToLoad = (self.filesToLoad[:], [])
            first = True
            for fn in filenames:
                fi = QFileInfo(fn)
                if fi.suffix().toLower().compare('ui') == 0:
                    self.preview.loadWidget(fn)
                elif fi.suffix().toLower().compare('qm') == 0:
                    self.translations.add(fn, first)
                    first = False
            
            self.__updateActions()
        
    def closeEvent(self, event):
        """
        Private event handler for the close event.
        
        @param event close event (QCloseEvent)
        """
        if self.SAServer is not None:
            self.SAServer.shutdown()
            self.SAServer = None
        event.accept()
        
    def __initActions(self):
        """
        Private method to define the user interface actions.
        """
        self.openUIAct = QAction(UI.PixmapCache.getIcon("openUI.png"), 
                        self.trUtf8('&Open UI Files...'), self)
        self.openUIAct.setStatusTip(self.trUtf8('Open UI files for display'))
        self.openUIAct.setWhatsThis(self.trUtf8(
                """<b>Open UI Files</b>"""
                """<p>This opens some UI files for display.</p>"""
        ))
        self.connect(self.openUIAct, SIGNAL('triggered()'), self.__openWidget)
        
        self.openQMAct = QAction(UI.PixmapCache.getIcon("openQM.png"), 
                        self.trUtf8('Open &Translation Files...'), self)
        self.openQMAct.setStatusTip(self.trUtf8('Open Translation files for display'))
        self.openQMAct.setWhatsThis(self.trUtf8(
                """<b>Open Translation Files</b>"""
                """<p>This opens some translation files for display.</p>"""
        ))
        self.connect(self.openQMAct, SIGNAL('triggered()'), self.__openTranslation)
        
        self.reloadAct = QAction(UI.PixmapCache.getIcon("reload.png"), 
                        self.trUtf8('&Reload Translations'), self)
        self.reloadAct.setStatusTip(self.trUtf8('Reload the loaded translations'))
        self.reloadAct.setWhatsThis(self.trUtf8(
                """<b>Reload Translations</b>"""
                """<p>This reloads the translations for the loaded languages.</p>"""
        ))
        self.connect(self.reloadAct, SIGNAL('triggered()'), self.translations.reload)
        
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
        
        self.tileAct = QAction(self.trUtf8('&Tile'), self)
        self.tileAct.setStatusTip(self.trUtf8('Tile the windows'))
        self.tileAct.setWhatsThis(self.trUtf8(
                """<b>Tile the windows</b>"""
                """<p>Rearrange and resize the windows so that they are tiled.</p>"""
        ))
        self.connect(self.tileAct, SIGNAL('triggered()'),self.preview.tile)
        
        self.cascadeAct = QAction(self.trUtf8('&Cascade'), self)
        self.cascadeAct.setStatusTip(self.trUtf8('Cascade the windows'))
        self.cascadeAct.setWhatsThis(self.trUtf8(
                """<b>Cascade the windows</b>"""
                """<p>Rearrange and resize the windows so that they are cascaded.</p>"""
        ))
        self.connect(self.cascadeAct, SIGNAL('triggered()'),self.preview.cascade)
        
        self.closeAct = QAction(UI.PixmapCache.getIcon("close.png"),
                            self.trUtf8('&Close'), self)
        self.closeAct.setShortcut(QKeySequence(self.trUtf8("Ctrl+W","File|Close")))
        self.closeAct.setStatusTip(self.trUtf8('Close the current window'))
        self.closeAct.setWhatsThis(self.trUtf8(
                """<b>Close Window</b>"""
                """<p>Close the current window.</p>"""
        ))
        self.connect(self.closeAct, SIGNAL('triggered()'),self.preview.closeWidget)
        
        self.closeAllAct = QAction(self.trUtf8('Clos&e All'), self)
        self.closeAllAct.setStatusTip(self.trUtf8('Close all windows'))
        self.closeAllAct.setWhatsThis(self.trUtf8(
                """<b>Close All Windows</b>"""
                """<p>Close all windows.</p>"""
        ))
        self.connect(self.closeAllAct, SIGNAL('triggered()'),
                     self.preview.closeAllWidgets)

    def __initMenus(self):
        """
        Private method to create the menus.
        """
        mb = self.menuBar()

        menu = mb.addMenu(self.trUtf8('&File'))
        menu.setTearOffEnabled(True)
        menu.addAction(self.openUIAct)
        menu.addAction(self.openQMAct)
        menu.addAction(self.reloadAct)
        menu.addSeparator()
        menu.addAction(self.closeAct)
        menu.addAction(self.closeAllAct)
        menu.addSeparator()
        menu.addAction(self.exitAct)
        
        self.windowMenu = mb.addMenu(self.trUtf8('&Window'))
        self.windowMenu.setTearOffEnabled(True)
        self.connect(self.windowMenu, SIGNAL('aboutToShow()'), self.__showWindowMenu)
        self.connect(self.windowMenu, SIGNAL('triggered(QAction *)'),
                     self.preview.toggleSelectedWidget)
        
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
        filetb.addAction(self.openUIAct)
        filetb.addAction(self.openQMAct)
        filetb.addAction(self.reloadAct)
        filetb.addSeparator()
        filetb.addAction(self.closeAct)
        filetb.addSeparator()
        filetb.addAction(self.exitAct)
        
        helptb = self.addToolBar(self.trUtf8("Help"))
        helptb.setIconSize(UI.Config.ToolBarIconSize)
        helptb.addAction(self.whatsThisAct)
    
    def __whatsThis(self):
        """
        Private slot called in to enter Whats This mode.
        """
        QWhatsThis.enterWhatsThisMode()
        
    def __updateActions(self):
        """
        Private slot to update the actions state.
        """
        if self.preview.hasWidgets():
            self.closeAct.setEnabled(True)
            self.closeAllAct.setEnabled(True)
            self.tileAct.setEnabled(True)
            self.cascadeAct.setEnabled(True)
        else:
            self.closeAct.setEnabled(False)
            self.closeAllAct.setEnabled(False)
            self.tileAct.setEnabled(False)
            self.cascadeAct.setEnabled(False)
        
        if self.translations.hasTranslations():
            self.reloadAct.setEnabled(True)
        else:
            self.reloadAct.setEnabled(False)

    def __about(self):
        """
        Private slot to show the about information.
        """
        KQMessageBox.about(self, self.trUtf8("TR Previewer"), self.trUtf8(
            """<h3> About TR Previewer </h3>"""
            """<p>The TR Previewer loads and displays Qt User-Interface files"""
            """ and translation files and shows dialogs for a selected language.</p>"""
        ))
    
    def __aboutQt(self):
        """
        Private slot to show info about Qt.
        """
        QMessageBox.aboutQt(self, self.trUtf8("TR Previewer"))
    
    def __openWidget(self):
        """
        Private slot to handle the Open Dialog action.
        """
        fileNameList = KQFileDialog.getOpenFileNames(\
            None,
            self.trUtf8("Select UI files"),
            QString(),
            self.trUtf8("Qt User-Interface Files (*.ui)"))
        
        for fileName in fileNameList:
            self.preview.loadWidget(fileName)
        
        self.__updateActions()
    
    def __openTranslation(self):
        """
        Private slot to handle the Open Translation action.
        """
        fileNameList = KQFileDialog.getOpenFileNames(\
            None,
            self.trUtf8("Select translation files"),
            QString(),
            self.trUtf8("Qt Translation Files (*.qm)"))
        
        first = True
        for fileName in fileNameList:
            self.translations.add(fileName, first)
            first = False
        
        self.__updateActions()
    
    def setTranslation(self, name):
        """
        Public slot to activate a translation.
        
        @param name name (language) of the translation (string or QString)
        """
        self.translations.set(name)
    
    def __showWindowMenu(self):
        """
        Private slot to handle the aboutToShow signal of the window menu.
        """
        self.windowMenu.clear()
        self.windowMenu.addAction(self.tileAct)
        self.windowMenu.addAction(self.cascadeAct)
        self.windowMenu.addSeparator()

        self.preview.showWindowMenu(self.windowMenu)
    
    def reloadTranslations(self):
        """
        Public slot to reload all translations.
        """
        self.translations.reload()

class Translation(object):
    """
    Class to store the properties of a translation
    """
    def __init__(self):
        """
        Constructor
        """
        self.fileName = None
        self.name = None
        self.translator = None

class TranslationsDict(QObject):
    """
    Class to store all loaded translations.
    
    @signal translationChanged() emit after a translator was set
    """
    def __init__(self, selector, parent):
        """
        Constructor
        
        @param selector reference to the QComboBox used to show the
            available languages (QComboBox)
        @param parent parent widget (QWidget)
        """
        QObject.__init__(self, parent)
        
        self.selector = selector
        self.currentTranslator = None
        self.selector.addItem(noTranslationName)
        self.translations = [] # list of Translation objects
    
    def add(self, transFileName, setTranslation = True):
        """
        Public method to add a translation to the list.
        
        If the translation file (*.qm) has not been loaded yet, it will
        be loaded automatically.
        
        @param transFileName name of the translation file to be added (string or QString)
        @param setTranslation flag indicating, if this should be set as the active
            translation (boolean)
        """
        fileName = QString(transFileName)
        if not self.__haveFileName(fileName):
            ntr = Translation()
            ntr.fileName = fileName
            ntr.name = self.__uniqueName(fileName)
            if ntr.name.isNull():
                KQMessageBox.warning(None,
                    self.trUtf8("Set Translator"),
                    self.trUtf8("""<p>The translation filename <b>%1</b>"""
                        """ is invalid.</p>""").arg(fileName))
                return
            
            ntr.translator = self.loadTransFile(fileName)
            if ntr.translator is None:
                return
            
            self.selector.addItem(ntr.name)
            self.translations.append(ntr)
        
        if setTranslation:
            tr = self.__findFileName(fileName)
            self.set(tr.name)
    
    def set(self, name):
        """
        Public slot to set a translator by name.
        
        @param name name (language) of the translator to set (string or QString)
        """
        name = QString(name)
        nTranslator = None
        
        if name.compare(noTranslationName) != 0:
            trans = self.__findName(name)
            if trans is None:
                KQMessageBox.warning(None,
                    self.trUtf8("Set Translator"),
                    self.trUtf8("""<p>The translator <b>%1</b> is not known.</p>""")\
                        .arg(name))
                return
                
            nTranslator = trans.translator
        
        if nTranslator == self.currentTranslator:
            return
        
        if self.currentTranslator is not None:
            QApplication.removeTranslator(self.currentTranslator)
        if nTranslator is not None:
            QApplication.installTranslator(nTranslator)
        self.currentTranslator = nTranslator
        
        self.selector.blockSignals(True)
        self.selector.setCurrentIndex(self.selector.findText(name))
        self.selector.blockSignals(False)
        
        self.emit(SIGNAL('translationChanged'))
    
    def reload(self):
        """
        Public method to reload all translators.
        """
        cname = self.selector.currentText()
        if self.currentTranslator is not None:
            QApplication.removeTranslator(self.currentTranslator)
            self.currentTranslator = None
        
        fileNames = QStringList()
        for trans in self.translations:
            trans.translator = None
            fileNames.append(trans.fileName)
        self.translations = []
        self.selector.clear()
        
        self.selector.addItem(noTranslationName)
        
        for fileName in fileNames:
            self.add(fileName, False)
        
        if self.__haveName(cname):
            self.set(cname)
        else:
            self.set(noTranslationName)
    
    def __findFileName(self, transFileName):
        """
        Private method to find a translation by file name.
        
        @param transFileName file name of the translation file (string or QString)
        @return reference to a translation object or None
        """
        for trans in self.translations:
            if trans.fileName.compare(transFileName) == 0:
                return trans
        return None
    
    def __findName(self, name):
        """
        Private method to find a translation by name.
        
        @param name name (language) of the translation (string or QString)
        @return reference to a translation object or None
        """
        for trans in self.translations:
            if trans.name.compare(name) == 0:
                return trans
        return None
    
    def __haveFileName(self, transFileName):
        """
        Private method to check for the presence of a translation.
        
        @param transFileName file name of the translation file (string or QString)
        @return flag indicating the presence of the translation (boolean)
        """
        return self.__findFileName(transFileName) is not None
    
    def __haveName(self, name):
        """
        Private method to check for the presence of a named translation.
        
        @param name name (language) of the translation (string or QString)
        @return flag indicating the presence of the translation (boolean)
        """
        return self.__findName(name) is not None
    
    def __uniqueName(self, transFileName):
        """
        Private method to generate a unique name.
        
        @param transFileName file name of the translation file (string or QString)
        @return unique name (QString)
        """
        name = _filename(transFileName)
        if name.isNull():
            return QString()
        
        uname = QString(name)
        cnt = 1
        while self.__haveName(uname):
            cnt += 1
            uname = QString("%1 <%2>").arg(name).arg(cnt)
        
        return uname
    
    def __del(self, name):
        """
        Private method to delete a translator from the list of available translators.
        
        @param name name of the translator to delete (string or QString)
        """
        name = QString(name)
        if name.compare(noTranslationName) == 0:
            return
        
        trans = self.__findName(name)
        if trans is None:
            return
        
        if self.selector().currentText().compare(name) == 0:
            self.set(noTranslationName)
        
        self.translations.remove(trans)
        del trans
    
    def loadTransFile(self, transFileName):
        """
        Public slot to load a translation file.
        
        @param transFileName file name of the translation file (string or QString)
        @return reference to the new translator object (QTranslator)
        """
        tr = QTranslator()
        if tr.load(transFileName):
            return tr
        
        KQMessageBox.warning(None,
            self.trUtf8("Load Translator"),
            self.trUtf8("""<p>The translation file <b>%1</b> could not be loaded.</p>""")\
                .arg(transFileName))
        return None

    def hasTranslations(self):
        """
        Public method to check for loaded translations.
        
        @return flag signaling if any translation was loaded (boolean)
        """
        return len(self.translations) > 0

class WidgetView(QWidget):
    """
    Class to show a dynamically loaded widget (or dialog).
    """
    def __init__(self, uiFileName, parent = None, name = None):
        """
        Constructor
        
        @param uiFileName name of the UI file to load (string or QString)
        @param parent parent widget (QWidget)
        @param name name of this widget (string)
        """
        QWidget.__init__(self, parent)
        if name:
            self.setObjectName(name)
            self.setWindowTitle(name)
        self.setAttribute(Qt.WA_DeleteOnClose)
        
        self.__widget = None
        self.__uiFileName = uiFileName
        self.__layout = QHBoxLayout(self)
        self.__valid = False
        self.__timer = QTimer(self)
        self.__timer.setSingleShot(True)
        self.connect(self.__timer, SIGNAL('timeout()'), self.buildWidget)
    
    def isValid(self):
        """
        Public method to return the validity of this widget view.
        
        @return flag indicating the validity (boolean)
        """
        return self.__valid
    
    def uiFileName(self):
        """
        Public method to retrieve the name of the UI file.
        
        @return filename of the loaded UI file (QString)
        """
        return QString(self.__uiFileName)
    
    def buildWidget(self):
        """
        Public slot to load a UI file.
        """
        if self.__widget:
            self.__widget.close()
            self.__layout.removeWidget(self.__widget)
            del self.__widget
            self.__widget = None
        
        try:
            self.__widget = uic.loadUi(self.__uiFileName)
        except:
            pass
        
        if not self.__widget:
            KQMessageBox.warning(None,
                self.trUtf8("Load UI File"),
                self.trUtf8("""<p>The file <b>%1</b> could not be loaded.</p>""")\
                    .arg(self.__uiFileName))
            self.__valid = False
            return
        
        self.__widget.setParent(self)
        self.__layout.addWidget(self.__widget)
        self.__widget.show()
        self.__valid = True
        self.adjustSize()
        
        self.__timer.stop()
    
    def __rebuildWidget(self):
        """
        Private method to schedule a rebuild of the widget.
        """
        self.__timer.start(0)

class WidgetWorkspace(QWorkspace):
    """
    Specialized workspace to show the loaded widgets.
    
    @signal lastWidgetClosed() emitted after last widget was closed
    """
    def __init__(self, parent = None):
        """
        Constructor
        
        @param parent parent widget (QWidget)
        """
        QWorkspace.__init__(self, parent)
        
        self.setScrollBarsEnabled(True)
        
        self.widgets = []
    
    def loadWidget(self, uiFileName):
        """
        Public slot to load a UI file.
        
        @param uiFileName name of the UI file to load (string or QString)
        """
        widget = self.__findWidget(uiFileName)
        if widget is None:
            name = _filename(uiFileName)
            if name.isEmpty():
                KQMessageBox.warning(None,
                    self.trUtf8("Load UI File"),
                    self.trUtf8("""<p>The file <b>%1</b> could not be loaded.</p>""")\
                        .arg(uiFileName))
                return
            
            uname = QString(name)
            cnt = 1
            while self.findChild(WidgetView, uname) is not None:
                cnt += 1
                uname = QString("%1 <%2>").arg(name).arg(cnt)
            name = QString(uname)
            
            wview = WidgetView(uiFileName, self, name)
            wview.buildWidget()
            if not wview.isValid():
                del wview
                return
            
            self.connect(self, SIGNAL("rebuildWidgets"), wview.buildWidget)
            wview.installEventFilter(self)
            
            self.addWindow(wview)
            self.widgets.append(wview)
        
        wview.showNormal()
    
    def eventFilter(self, obj, ev):
        """
        Protected method called to filter an event.
        
        @param object object, that generated the event (QObject)
        @param event the event, that was generated by object (QEvent)
        @return flag indicating if event was filtered out
        """
        if not isinstance(obj, QWidget):
            return False
        
        if not obj in self.widgets:
            return False
            
        if ev.type() == QEvent.Close:
            try:
                self.widgets.remove(obj)
                if len(self.widgets) == 0:
                    self.emit(SIGNAL('lastWidgetClosed'))
            except ValueError:
                pass
        
        return False
    
    def __findWidget(self, uiFileName):
        """
        Private method to find a specific widget view.
        
        @param uiFileName filename of the loaded UI file (string or QString)
        @return reference to the widget (WidgetView) or None
        """
        wviewList = self.findChildren(WidgetView)
        if wviewList is None:
            return None
        
        for wview in wviewList:
            if wview.uiFileName().compare(uiFileName) == 0:
                return wview
        
        return None
    
    def closeWidget(self):
        """
        Public slot to close the active window.
        """
        aw = self.activeWindow()
        if aw is not None:
            aw.close()
    
    def closeAllWidgets(self):
        """
        Public slot to close all windows.
        """
        for w in self.widgets[:]:
            w.close()
    
    def showWindowMenu(self, windowMenu):
        """
        Public method to set up the widgets part of the Window menu.
        
        @param windowMenu reference to the window menu
        """
        idx = 0
        for wid in self.widgets:
            act = windowMenu.addAction(wid.windowTitle())
            act.setData(QVariant(idx))
            act.setCheckable(True)
            act.setChecked(not wid.isHidden())
            idx = idx + 1
    
    def toggleSelectedWidget(self, act):
        """
        Public method to handle the toggle of a window.
        
        @param act reference to the action that triggered (QAction)
        """
        idx, ok = act.data().toInt()
        if ok:
            self.__toggleWidget(self.widgets[idx])
    
    def __toggleWidget(self, w):
        """
        Private method to toggle a workspace window.
        
        @param w window to be toggled
        """
        if w.isHidden():
            w.show()
        else:
            w.hide()
    
    def hasWidgets(self):
        """
        Public method to check for loaded widgets.
        
        @return flag signaling if any widget was loaded (boolean)
        """
        return len(self.widgets) > 0

def _filename(path):
    """
    Protected module function to chop off the path.
    
    @param path path to extract the filename from (string or QString)
    @return extracted filename (QString)
    """
    path = QString(path)
    idx = path.lastIndexOf("/")
    if idx == -1:
        idx = path.lastIndexOf(QDir.separator())
    if idx == -1:
        return path
    else:
        return path.mid(idx + 1)
