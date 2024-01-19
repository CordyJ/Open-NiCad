# -*- coding: utf-8 -*-

# Copyright (c) 2002 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the helpviewer main window.
"""

import os

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtNetwork import QNetworkProxy
from PyQt4.QtWebKit import QWebSettings
from PyQt4.QtHelp import QHelpEngine, QHelpEngineCore, QHelpSearchQuery

from KdeQt import KQFileDialog, KQMessageBox
from KdeQt.KQMainWindow import KQMainWindow
import KdeQt.KQPrinter
from KdeQt.KQPrintDialog import KQPrintDialog

from SearchWidget import SearchWidget
from HelpBrowserWV import HelpBrowser
from HelpTocWidget import HelpTocWidget
from HelpIndexWidget import HelpIndexWidget
from HelpSearchWidget import HelpSearchWidget
from HelpTopicDialog import HelpTopicDialog
from QtHelpDocumentationDialog import QtHelpDocumentationDialog
from QtHelpFiltersDialog import QtHelpFiltersDialog
from HelpDocsInstaller import HelpDocsInstaller
from HelpWebSearchWidget import HelpWebSearchWidget
from HelpClearPrivateDataDialog import HelpClearPrivateDataDialog
from HelpLanguagesDialog import HelpLanguagesDialog
from CookieJar.CookieJar import CookieJar
from CookieJar.CookiesConfigurationDialog import CookiesConfigurationDialog
from Bookmarks.BookmarksManager import BookmarksManager
from Bookmarks.BookmarksMenu import BookmarksMenuBarMenu
from Bookmarks.BookmarksToolBar import BookmarksToolBar
from Bookmarks.BookmarkNode import BookmarkNode
from Bookmarks.AddBookmarkDialog import AddBookmarkDialog
from Bookmarks.BookmarksDialog import BookmarksDialog
from History.HistoryManager import HistoryManager
from History.HistoryMenu import HistoryMenu
from History.HistoryCompleter import HistoryCompletionModel, HistoryCompleter
from Passwords.PasswordManager import PasswordManager
from Network.NetworkAccessManager import NetworkAccessManager
from AdBlock.AdBlockManager import AdBlockManager

from E4Gui.E4TabWidget import E4TabWidget
from E4Gui.E4Action import E4Action

from E4Network.E4NetworkMonitor import E4NetworkMonitor

import Preferences
from Preferences import Shortcuts
from Preferences.ConfigurationDialog import ConfigurationDialog

import Utilities

import UI.PixmapCache
import UI.Config

from eric4config import getConfig

class HelpWindow(KQMainWindow):
    """
    Class implementing the web browser main window.
    
    @signal helpClosed() emitted after the window was requested to close down
    @signal zoomTextOnlyChanged(bool) emitted after the zoom text only setting was
            changed
    """
    helpwindows = []

    maxMenuFilePathLen = 75
    
    _networkAccessManager = None
    _cookieJar = None
    _helpEngine = None
    _bookmarksManager = None
    _historyManager = None
    _passwordManager = None
    _adblockManager = None
    
    def __init__(self, home, path, parent, name, fromEric = False, 
                 initShortcutsOnly = False, searchWord = None):
        """
        Constructor
        
        @param home the URL to be shown (string or QString)
        @param path the path of the working dir (usually '.') (string or QString)
        @param parent parent widget of this window (QWidget)
        @param name name of this window (string or QString)
        @param fromEric flag indicating whether it was called from within eric4 (boolean)
        @keyparam initShortcutsOnly flag indicating to just initialize the keyboard
            shortcuts (boolean)
        @keyparam searchWord word to search for (string or QString)
        """
        KQMainWindow.__init__(self, parent)
        self.setObjectName(name)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setWindowTitle(self.trUtf8("eric4 Web Browser"))
        
        self.fromEric = fromEric
        self.initShortcutsOnly = initShortcutsOnly
        self.setWindowIcon(UI.PixmapCache.getIcon("eric.png"))

        self.mHistory = QStringList()
        self.pathCombo = None
        
        if self.initShortcutsOnly:
            self.__initActions()
        else:
            self.__helpEngine = \
                QHelpEngine(os.path.join(Utilities.getConfigDir(), 
                                         "browser", "eric4help.qhc"), self)
            self.connect(self.__helpEngine, SIGNAL("warning(const QString&)"), 
                         self.__warning)
            self.__helpInstaller = None
            
            # Attributes for WebKit based browser
            self.__progressBar = None
            
            self.__removeOldHistory()
            
            self.tabContextMenuIndex = -1
            self.tabWidget = E4TabWidget(self, dnd = True)
            self.connect(self.tabWidget, SIGNAL('currentChanged(int)'),
                self.__currentChanged)
            self.tabWidget.setTabContextMenuPolicy(Qt.CustomContextMenu)
            self.connect(self.tabWidget, 
                         SIGNAL('customTabContextMenuRequested(const QPoint &, int)'),
                         self.__showContextMenu)
            
            self.findDlg = SearchWidget(self, self)
            centralWidget = QWidget()
            layout = QVBoxLayout()
            layout.setContentsMargins(1, 1, 1, 1)
            layout.addWidget(self.tabWidget)
            layout.addWidget(self.findDlg)
            self.tabWidget.setSizePolicy(
                QSizePolicy.Preferred, QSizePolicy.Expanding)
            centralWidget.setLayout(layout)
            self.setCentralWidget(centralWidget)
            self.findDlg.hide()
            
            # setup the TOC widget
            self.__tocWindow = HelpTocWidget(self.__helpEngine, self)
            self.__tocDock = QDockWidget(self.trUtf8("Contents"), self)
            self.__tocDock.setObjectName("TocWindow")
            self.__tocDock.setWidget(self.__tocWindow)
            self.addDockWidget(Qt.LeftDockWidgetArea, self.__tocDock)
            
            # setup the index widget
            self.__indexWindow = HelpIndexWidget(self.__helpEngine, self)
            self.__indexDock = QDockWidget(self.trUtf8("Index"), self)
            self.__indexDock.setObjectName("IndexWindow")
            self.__indexDock.setWidget(self.__indexWindow)
            self.addDockWidget(Qt.LeftDockWidgetArea, self.__indexDock)
            
            # setup the search widget
            self.__searchWord = searchWord
            self.__indexing = False
            self.__indexingProgress = None
            self.__searchEngine = self.__helpEngine.searchEngine()
            self.connect(self.__searchEngine, SIGNAL("indexingStarted()"), 
                         self.__indexingStarted)
            self.connect(self.__searchEngine, SIGNAL("indexingFinished()"), 
                         self.__indexingFinished)
            self.__searchWindow = HelpSearchWidget(self.__searchEngine, self)
            self.__searchDock = QDockWidget(self.trUtf8("Search"), self)
            self.__searchDock.setObjectName("SearchWindow")
            self.__searchDock.setWidget(self.__searchWindow)
            self.addDockWidget(Qt.LeftDockWidgetArea, self.__searchDock)
            
            self.rightCornerWidget = QWidget(self)
            self.rightCornerWidgetLayout = QHBoxLayout(self.rightCornerWidget)
            self.rightCornerWidgetLayout.setMargin(0)
            self.rightCornerWidgetLayout.setSpacing(0)
            
            self.__navigationMenu = QMenu(self)
            self.connect(self.__navigationMenu, SIGNAL("aboutToShow()"), 
                         self.__showNavigationMenu)
            self.connect(self.__navigationMenu, SIGNAL("triggered(QAction*)"), 
                         self.__navigationMenuTriggered)
            
            self.navigationButton = QToolButton(self.tabWidget)
            self.navigationButton.setIcon(UI.PixmapCache.getIcon("1downarrow.png"))
            self.navigationButton.setToolTip(self.trUtf8("Show a navigation menu"))
            self.navigationButton.setPopupMode(QToolButton.InstantPopup)
            self.navigationButton.setMenu(self.__navigationMenu)
            self.navigationButton.setEnabled(False)
            self.rightCornerWidgetLayout.addWidget(self.navigationButton)
            
            if Preferences.getUI("SingleCloseButton") or \
               not hasattr(self.tabWidget, 'setTabsClosable'):
                self.closeButton = QToolButton(self.tabWidget)
                self.closeButton.setIcon(UI.PixmapCache.getIcon("close.png"))
                self.closeButton.setToolTip(self.trUtf8("Close the current help window"))
                self.closeButton.setEnabled(False)
                self.connect(self.closeButton, SIGNAL("clicked(bool)"), self.__close)
                self.rightCornerWidgetLayout.addWidget(self.closeButton)
            else:
                self.tabWidget.setTabsClosable(True)
                self.connect(self.tabWidget, SIGNAL("tabCloseRequested(int)"), 
                    self.__closeAt)
                self.closeButton = None
            
            self.tabWidget.setCornerWidget(self.rightCornerWidget, Qt.TopRightCorner)
            
            self.newTabButton = QToolButton(self.tabWidget)
            self.newTabButton.setIcon(UI.PixmapCache.getIcon("new.png"))
            self.newTabButton.setToolTip(self.trUtf8("Open a new help window tab"))
            self.tabWidget.setCornerWidget(self.newTabButton, Qt.TopLeftCorner)
            self.connect(self.newTabButton, SIGNAL("clicked(bool)"), self.newTab)
            
            if Preferences.getHelp("SaveGeometry"):
                g = Preferences.getGeometry("HelpViewerGeometry")
            else:
                g = QByteArray()
            if g.isEmpty():
                s = QSize(800, 800)
                self.resize(s)
            else:
                self.restoreGeometry(g)
            
            self.__setIconDatabasePath()
            self.__initWebSettings()
            
            self.__initActions()
            self.__initMenus()
            self.__initToolbars()
            self.__initTabContextMenu()
            
            self.historyManager()
            
            self.newBrowser(home)
            self.currentBrowser().setFocus()
            
            self.__class__.helpwindows.append(self)
            
            QDesktopServices.setUrlHandler("http", self.__linkActivated)
            
            # setup connections
            # TOC window
            self.connect(self.__tocWindow, SIGNAL("linkActivated(const QUrl&)"), 
                         self.__linkActivated)
            self.connect(self.__tocWindow, SIGNAL("escapePressed()"), 
                         self.__activateCurrentBrowser)
            # index window
            self.connect(self.__indexWindow, SIGNAL("linkActivated(const QUrl&)"), 
                         self.__linkActivated)
            self.connect(self.__indexWindow, 
                         SIGNAL("linksActivated(const QMap<QString, QUrl>&, const QString&)"),
                         self.__linksActivated)
            self.connect(self.__indexWindow, SIGNAL("escapePressed()"), 
                         self.__activateCurrentBrowser)
            # search window
            self.connect(self.__searchWindow, SIGNAL("linkActivated(const QUrl&)"), 
                         self.__linkActivated)
            self.connect(self.__searchWindow, SIGNAL("escapePressed()"), 
                         self.__activateCurrentBrowser)
            
            state = Preferences.getHelp("HelpViewerState")
            self.restoreState(state)
            
            self.__initHelpDb()
            
            QTimer.singleShot(0, self.__lookForNewDocumentation)
            if self.__searchWord is not None:
                QTimer.singleShot(0, self.__searchForWord)

    def __setIconDatabasePath(self, enable = True):
        """
        Private method to set the favicons path.
        
        @param enable flag indicating to enabled icon storage
        """
        if enable:
            iconDatabasePath = os.path.join(Utilities.getConfigDir(), 
                                            "browser", "favicons")
            if not os.path.exists(iconDatabasePath):
                os.makedirs(iconDatabasePath)
        else:
            iconDatabasePath = ""   # setting an empty path disables it
        QWebSettings.setIconDatabasePath(iconDatabasePath)
        
    def __initWebSettings(self):
        """
        Private method to set the global web settings.
        """
        standardFont = Preferences.getHelp("StandardFont")
        fixedFont = Preferences.getHelp("FixedFont")

        settings = QWebSettings.globalSettings()
        settings.setAttribute(QWebSettings.DeveloperExtrasEnabled, True)
        
        settings.setFontFamily(QWebSettings.StandardFont, standardFont.family())
        settings.setFontSize(QWebSettings.DefaultFontSize, standardFont.pointSize())
        settings.setFontFamily(QWebSettings.FixedFont, fixedFont.family())
        settings.setFontSize(QWebSettings.DefaultFixedFontSize, fixedFont.pointSize())
        
        styleSheet = Preferences.getHelp("UserStyleSheet")
        if not styleSheet.isEmpty():
            settings.setUserStyleSheetUrl(QUrl(styleSheet))
        
        settings.setAttribute(QWebSettings.AutoLoadImages, 
            Preferences.getHelp("AutoLoadImages"))
        settings.setAttribute(QWebSettings.JavaEnabled, 
            Preferences.getHelp("JavaEnabled"))
        settings.setAttribute(QWebSettings.JavascriptEnabled, 
            Preferences.getHelp("JavaScriptEnabled"))
        settings.setAttribute(QWebSettings.JavascriptCanOpenWindows, 
            Preferences.getHelp("JavaScriptCanOpenWindows"))
        settings.setAttribute(QWebSettings.JavascriptCanAccessClipboard, 
            Preferences.getHelp("JavaScriptCanAccessClipboard"))
        settings.setAttribute(QWebSettings.PluginsEnabled, 
            Preferences.getHelp("PluginsEnabled"))
        
        if hasattr(QWebSettings, "PrintElementBackgrounds"):
            settings.setAttribute(QWebSettings.PrintElementBackgrounds, 
                Preferences.getHelp("PrintBackgrounds"))
        
    def __initActions(self):
        """
        Private method to define the user interface actions.
        """
        # list of all actions
        self.__actions = []
        
        self.newTabAct = E4Action(self.trUtf8('New Tab'), 
            UI.PixmapCache.getIcon("new.png"),
            self.trUtf8('&New Tab'), 
            QKeySequence(self.trUtf8("Ctrl+T","File|New Tab")), 
            0, self, 'help_file_new_tab')
        self.newTabAct.setStatusTip(self.trUtf8('Open a new help window tab'))
        self.newTabAct.setWhatsThis(self.trUtf8(
                """<b>New Tab</b>"""
                """<p>This opens a new help window tab.</p>"""
        ))
        self.connect(self.newTabAct, SIGNAL('triggered()'), self.newTab)
        self.__actions.append(self.newTabAct)
        
        self.newAct = E4Action(self.trUtf8('New Window'), 
            UI.PixmapCache.getIcon("newWindow.png"),
            self.trUtf8('New &Window'), 
            QKeySequence(self.trUtf8("Ctrl+N","File|New Window")), 
            0, self, 'help_file_new_window')
        self.newAct.setStatusTip(self.trUtf8('Open a new help browser window'))
        self.newAct.setWhatsThis(self.trUtf8(
                """<b>New Window</b>"""
                """<p>This opens a new help browser window.</p>"""
        ))
        self.connect(self.newAct, SIGNAL('triggered()'), self.newWindow)
        self.__actions.append(self.newAct)
        
        self.openAct = E4Action(self.trUtf8('Open File'), 
            UI.PixmapCache.getIcon("open.png"),
            self.trUtf8('&Open File'), 
            QKeySequence(self.trUtf8("Ctrl+O","File|Open")), 
            0, self, 'help_file_open')
        self.openAct.setStatusTip(self.trUtf8('Open a help file for display'))
        self.openAct.setWhatsThis(self.trUtf8(
                """<b>Open File</b>"""
                """<p>This opens a new help file for display."""
                """ It pops up a file selection dialog.</p>"""
        ))
        self.connect(self.openAct, SIGNAL('triggered()'), self.__openFile)
        self.__actions.append(self.openAct)
        
        self.openTabAct = E4Action(self.trUtf8('Open File in New Tab'), 
            UI.PixmapCache.getIcon("openNewTab.png"),
            self.trUtf8('Open File in New &Tab'), 
            QKeySequence(self.trUtf8("Shift+Ctrl+O","File|Open in new tab")), 
            0, self, 'help_file_open_tab')
        self.openTabAct.setStatusTip(\
            self.trUtf8('Open a help file for display in a new tab'))
        self.openTabAct.setWhatsThis(self.trUtf8(
                """<b>Open File in New Tab</b>"""
                """<p>This opens a new help file for display in a new tab."""
                """ It pops up a file selection dialog.</p>"""
        ))
        self.connect(self.openTabAct, SIGNAL('triggered()'), self.__openFileNewTab)
        self.__actions.append(self.openTabAct)
        
        self.saveAsAct = E4Action(self.trUtf8('Save As '), 
            UI.PixmapCache.getIcon("fileSaveAs.png"),
            self.trUtf8('&Save As...'), 
            QKeySequence(self.trUtf8("Shift+Ctrl+S","File|Save As")), 
            0, self, 'help_file_save_as')
        self.saveAsAct.setStatusTip(\
            self.trUtf8('Save the current page to disk'))
        self.saveAsAct.setWhatsThis(self.trUtf8(
                """<b>Save As...</b>"""
                """<p>Saves the current page to disk.</p>"""
        ))
        self.connect(self.saveAsAct, SIGNAL('triggered()'), self.__savePageAs)
        self.__actions.append(self.saveAsAct)
        
        bookmarksManager = self.bookmarksManager()
        self.importBookmarksAct = E4Action(self.trUtf8('Import Bookmarks'), 
            self.trUtf8('&Import Bookmarks...'), 
            0, 0, self, 'help_file_import_bookmarks')
        self.importBookmarksAct.setStatusTip(\
            self.trUtf8('Import bookmarks from other browsers'))
        self.importBookmarksAct.setWhatsThis(self.trUtf8(
                """<b>Import Bookmarks</b>"""
                """<p>Import bookmarks from other browsers.</p>"""
        ))
        self.connect(self.importBookmarksAct, SIGNAL('triggered()'), 
                     bookmarksManager.importBookmarks)
        self.__actions.append(self.importBookmarksAct)
        
        self.exportBookmarksAct = E4Action(self.trUtf8('Export Bookmarks'), 
            self.trUtf8('&Export Bookmarks...'), 
            0, 0, self, 'help_file_export_bookmarks')
        self.exportBookmarksAct.setStatusTip(\
            self.trUtf8('Export the bookmarks into a file'))
        self.exportBookmarksAct.setWhatsThis(self.trUtf8(
                """<b>Export Bookmarks</b>"""
                """<p>Export the bookmarks into a file.</p>"""
        ))
        self.connect(self.exportBookmarksAct, SIGNAL('triggered()'), 
                     bookmarksManager.exportBookmarks)
        self.__actions.append(self.exportBookmarksAct)
        
        self.printAct = E4Action(self.trUtf8('Print'), 
            UI.PixmapCache.getIcon("print.png"),
            self.trUtf8('&Print'), 
            QKeySequence(self.trUtf8("Ctrl+P","File|Print")), 
            0, self, 'help_file_print')
        self.printAct.setStatusTip(self.trUtf8('Print the displayed help'))
        self.printAct.setWhatsThis(self.trUtf8(
                """<b>Print</b>"""
                """<p>Print the displayed help text.</p>"""
        ))
        self.connect(self.printAct, SIGNAL('triggered()'), self.__printFile)
        self.__actions.append(self.printAct)
        
        self.printPreviewAct = E4Action(self.trUtf8('Print Preview'), 
            UI.PixmapCache.getIcon("printPreview.png"),
            self.trUtf8('Print Preview'), 
            0, 0, self, 'help_file_print_preview')
        self.printPreviewAct.setStatusTip(self.trUtf8(
                'Print preview of the displayed help'))
        self.printPreviewAct.setWhatsThis(self.trUtf8(
                """<b>Print Preview</b>"""
                """<p>Print preview of the displayed help text.</p>"""
        ))
        self.connect(self.printPreviewAct, SIGNAL('triggered()'), 
            self.__printPreviewFile)
        self.__actions.append(self.printPreviewAct)
        
        self.closeAct = E4Action(self.trUtf8('Close'), 
            UI.PixmapCache.getIcon("close.png"),
            self.trUtf8('&Close'), 
            QKeySequence(self.trUtf8("Ctrl+W","File|Close")), 
            0, self, 'help_file_close')
        self.closeAct.setStatusTip(self.trUtf8('Close the current help window'))
        self.closeAct.setWhatsThis(self.trUtf8(
                """<b>Close</b>"""
                """<p>Closes the current help window.</p>"""
        ))
        self.connect(self.closeAct, SIGNAL('triggered()'), self.__close)
        self.__actions.append(self.closeAct)
        
        self.closeAllAct = E4Action(self.trUtf8('Close All'), 
            self.trUtf8('Close &All'), 
            0, 0, self, 'help_file_close_all')
        self.closeAllAct.setStatusTip(self.trUtf8('Close all help windows'))
        self.closeAllAct.setWhatsThis(self.trUtf8(
                """<b>Close All</b>"""
                """<p>Closes all help windows except the first one.</p>"""
        ))
        self.connect(self.closeAllAct, SIGNAL('triggered()'), self.__closeAll)
        self.__actions.append(self.closeAllAct)
        
        self.privateBrowsingAct = E4Action(self.trUtf8('Private Browsing'), 
            UI.PixmapCache.getIcon("privateBrowsing.png"),
            self.trUtf8('Private &Browsing'), 
            0, 0, self, 'help_file_private_browsing')
        self.privateBrowsingAct.setStatusTip(self.trUtf8('Private Browsing'))
        self.privateBrowsingAct.setWhatsThis(self.trUtf8(
                """<b>Private Browsing</b>"""
                """<p>Enables private browsing. In this mode no history is"""
                """ recorded anymore.</p>"""
        ))
        self.connect(self.privateBrowsingAct, SIGNAL('triggered()'), 
                     self.__privateBrowsing)
        self.privateBrowsingAct.setCheckable(True)
        self.__actions.append(self.privateBrowsingAct)
        
        self.exitAct = E4Action(self.trUtf8('Quit'), 
            UI.PixmapCache.getIcon("exit.png"),
            self.trUtf8('&Quit'), 
            QKeySequence(self.trUtf8("Ctrl+Q","File|Quit")), 
            0, self, 'help_file_quit')
        self.exitAct.setStatusTip(self.trUtf8('Quit the web browser'))
        self.exitAct.setWhatsThis(self.trUtf8(
                """<b>Quit</b>"""
                """<p>Quit the web browser.</p>"""
        ))
        if self.fromEric:
            self.connect(self.exitAct, SIGNAL('triggered()'), self, SLOT('close()'))
        else:
            self.connect(self.exitAct, SIGNAL('triggered()'), 
                         qApp, SLOT('closeAllWindows()'))
        self.__actions.append(self.exitAct)
        
        self.backAct = E4Action(self.trUtf8('Backward'), 
            UI.PixmapCache.getIcon("back.png"),
            self.trUtf8('&Backward'), 
            QKeySequence(self.trUtf8("Alt+Left","Go|Backward")), 
            QKeySequence(self.trUtf8("Backspace","Go|Backward")), 
            self, 'help_go_backward')
        self.backAct.setStatusTip(self.trUtf8('Move one help screen backward'))
        self.backAct.setWhatsThis(self.trUtf8(
                """<b>Backward</b>"""
                """<p>Moves one help screen backward. If none is"""
                """ available, this action is disabled.</p>"""
        ))
        self.connect(self.backAct, SIGNAL('triggered()'), self.__backward)
        self.__actions.append(self.backAct)
        
        self.forwardAct = E4Action(self.trUtf8('Forward'), 
            UI.PixmapCache.getIcon("forward.png"),
            self.trUtf8('&Forward'), 
            QKeySequence(self.trUtf8("Alt+Right","Go|Forward")), 
            QKeySequence(self.trUtf8("Shift+Backspace","Go|Forward")), 
            self, 'help_go_foreward')
        self.forwardAct.setStatusTip(self.trUtf8('Move one help screen forward'))
        self.forwardAct.setWhatsThis(self.trUtf8(
                """<b>Forward</b>"""
                """<p>Moves one help screen forward. If none is"""
                """ available, this action is disabled.</p>"""
        ))
        self.connect(self.forwardAct, SIGNAL('triggered()'), self.__forward)
        self.__actions.append(self.forwardAct)
        
        self.homeAct = E4Action(self.trUtf8('Home'), 
            UI.PixmapCache.getIcon("home.png"),
            self.trUtf8('&Home'), 
            QKeySequence(self.trUtf8("Ctrl+Home","Go|Home")), 
            0, self, 'help_go_home')
        self.homeAct.setStatusTip(self.trUtf8('Move to the initial help screen'))
        self.homeAct.setWhatsThis(self.trUtf8(
                """<b>Home</b>"""
                """<p>Moves to the initial help screen.</p>"""
        ))
        self.connect(self.homeAct, SIGNAL('triggered()'), self.__home)
        self.__actions.append(self.homeAct)
        
        self.reloadAct = E4Action(self.trUtf8('Reload'), 
            UI.PixmapCache.getIcon("reload.png"),
            self.trUtf8('&Reload'), 
            QKeySequence(self.trUtf8("Ctrl+R","Go|Reload")), 
            QKeySequence(self.trUtf8("F5","Go|Reload")), 
            self, 'help_go_reload')
        self.reloadAct.setStatusTip(self.trUtf8('Reload the current help screen'))
        self.reloadAct.setWhatsThis(self.trUtf8(
                """<b>Reload</b>"""
                """<p>Reloads the current help screen.</p>"""
        ))
        self.connect(self.reloadAct, SIGNAL('triggered()'), self.__reload)
        self.__actions.append(self.reloadAct)
        
        self.stopAct = E4Action(self.trUtf8('Stop'), 
            UI.PixmapCache.getIcon("stopLoading.png"),
            self.trUtf8('&Stop'), 
            QKeySequence(self.trUtf8("Ctrl+.","Go|Stop")), 
            QKeySequence(self.trUtf8("Esc","Go|Stop")), 
            self, 'help_go_stop')
        self.stopAct.setStatusTip(self.trUtf8('Stop loading'))
        self.stopAct.setWhatsThis(self.trUtf8(
                """<b>Stop</b>"""
                """<p>Stops loading of the current tab.</p>"""
        ))
        self.connect(self.stopAct, SIGNAL('triggered()'), self.__stopLoading)
        self.__actions.append(self.stopAct)
        
        self.copyAct = E4Action(self.trUtf8('Copy'), 
            UI.PixmapCache.getIcon("editCopy.png"),
            self.trUtf8('&Copy'), 
            QKeySequence(self.trUtf8("Ctrl+C","Edit|Copy")), 
            0, self, 'help_edit_copy')
        self.copyAct.setStatusTip(self.trUtf8('Copy the selected text'))
        self.copyAct.setWhatsThis(self.trUtf8(
                """<b>Copy</b>"""
                """<p>Copy the selected text to the clipboard.</p>"""
        ))
        self.connect(self.copyAct, SIGNAL('triggered()'), self.__copy)
        self.__actions.append(self.copyAct)
        
        self.findAct = E4Action(self.trUtf8('Find...'), 
            UI.PixmapCache.getIcon("find.png"),
            self.trUtf8('&Find...'), 
            QKeySequence(self.trUtf8("Ctrl+F","Edit|Find")), 
            0, self, 'help_edit_find')
        self.findAct.setStatusTip(self.trUtf8('Find text in page'))
        self.findAct.setWhatsThis(self.trUtf8(
                """<b>Find</b>"""
                """<p>Find text in the current page.</p>"""
        ))
        self.connect(self.findAct, SIGNAL('triggered()'), self.__find)
        self.__actions.append(self.findAct)
        
        self.findNextAct = E4Action(self.trUtf8('Find next'), 
            UI.PixmapCache.getIcon("findNext.png"),
            self.trUtf8('Find &next'), 
            QKeySequence(self.trUtf8("F3","Edit|Find next")), 
            0, self, 'help_edit_find_next')
        self.findNextAct.setStatusTip(self.trUtf8('Find next occurrence of text in page'))
        self.findNextAct.setWhatsThis(self.trUtf8(
                """<b>Find next</b>"""
                """<p>Find the next occurrence of text in the current page.</p>"""
        ))
        if not self.initShortcutsOnly:
            self.connect(self.findNextAct, SIGNAL('triggered()'), self.findDlg.findNext)
        self.__actions.append(self.findNextAct)
        
        self.findPrevAct = E4Action(self.trUtf8('Find previous'), 
            UI.PixmapCache.getIcon("findPrev.png"),
            self.trUtf8('Find &previous'), 
            QKeySequence(self.trUtf8("Shift+F3","Edit|Find previous")), 
            0, self, 'help_edit_find_previous')
        self.findPrevAct.setStatusTip(\
            self.trUtf8('Find previous occurrence of text in page'))
        self.findPrevAct.setWhatsThis(self.trUtf8(
                """<b>Find previous</b>"""
                """<p>Find the previous occurrence of text in the current page.</p>"""
        ))
        if not self.initShortcutsOnly:
            self.connect(self.findPrevAct, SIGNAL('triggered()'), 
                         self.findDlg.findPrevious)
        self.__actions.append(self.findPrevAct)
        
        self.bookmarksManageAct = E4Action(self.trUtf8('Manage Bookmarks'), 
            self.trUtf8('&Manage Bookmarks...'), 
            QKeySequence(self.trUtf8("Ctrl+Shift+B", "Help|Manage bookmarks")), 
            0, self, 'help_bookmarks_manage')
        self.bookmarksManageAct.setStatusTip(self.trUtf8(
                'Open a dialog to manage the bookmarks.'))
        self.bookmarksManageAct.setWhatsThis(self.trUtf8(
                """<b>Manage Bookmarks...</b>"""
                """<p>Open a dialog to manage the bookmarks.</p>"""
        ))
        self.connect(self.bookmarksManageAct, SIGNAL('triggered()'), 
            self.__showBookmarksDialog)
        self.__actions.append(self.bookmarksManageAct)
        
        self.bookmarksAddAct = E4Action(self.trUtf8('Add Bookmark'), 
            UI.PixmapCache.getIcon("addBookmark.png"),
            self.trUtf8('Add &Bookmark...'), 
            QKeySequence(self.trUtf8("Ctrl+D", "Help|Add bookmark")), 
            0, self, 'help_bookmark_add')
        self.bookmarksAddAct.setIconVisibleInMenu(False)
        self.bookmarksAddAct.setStatusTip(self.trUtf8('Open a dialog to add a bookmark.'))
        self.bookmarksAddAct.setWhatsThis(self.trUtf8(
                """<b>Add Bookmark</b>"""
                """<p>Open a dialog to add the current URL as a bookmark.</p>"""
        ))
        self.connect(self.bookmarksAddAct, SIGNAL('triggered()'), self.__addBookmark)
        self.__actions.append(self.bookmarksAddAct)
        
        self.bookmarksAddFolderAct = E4Action(self.trUtf8('Add Folder'), 
            self.trUtf8('Add &Folder...'), 
            0, 0, self, 'help_bookmark_show_all')
        self.bookmarksAddFolderAct.setStatusTip(self.trUtf8(
                'Open a dialog to add a new bookmarks folder.'))
        self.bookmarksAddFolderAct.setWhatsThis(self.trUtf8(
                """<b>Add Folder...</b>"""
                """<p>Open a dialog to add a new bookmarks folder.</p>"""
        ))
        self.connect(self.bookmarksAddFolderAct, SIGNAL('triggered()'), 
            self.__addBookmarkFolder)
        self.__actions.append(self.bookmarksAddFolderAct)
        
        self.bookmarksAllTabsAct = E4Action(self.trUtf8('Bookmark All Tabs'), 
            self.trUtf8('Bookmark All Tabs...'), 
            0, 0, self, 'help_bookmark_all_tabs')
        self.bookmarksAllTabsAct.setStatusTip(self.trUtf8(
                'Bookmark all open tabs.'))
        self.bookmarksAllTabsAct.setWhatsThis(self.trUtf8(
                """<b>Bookmark All Tabs...</b>"""
                """<p>Open a dialog to add a new bookmarks folder for"""
                """ all open tabs.</p>"""
        ))
        self.connect(self.bookmarksAllTabsAct, SIGNAL('triggered()'), 
            self.__bookmarkAll)
        self.__actions.append(self.bookmarksAllTabsAct)
        
        self.whatsThisAct = E4Action(self.trUtf8('What\'s This?'), 
            UI.PixmapCache.getIcon("whatsThis.png"),
            self.trUtf8('&What\'s This?'), 
            QKeySequence(self.trUtf8("Shift+F1","Help|What's This?'")), 
            0, self, 'help_help_whats_this')
        self.whatsThisAct.setStatusTip(self.trUtf8('Context sensitive help'))
        self.whatsThisAct.setWhatsThis(self.trUtf8(
                """<b>Display context sensitive help</b>"""
                """<p>In What's This? mode, the mouse cursor shows an arrow with a"""
                """ question mark, and you can click on the interface elements to get"""
                """ a short description of what they do and how to use them. In"""
                """ dialogs, this feature can be accessed using the context help button"""
                """ in the titlebar.</p>"""
        ))
        self.connect(self.whatsThisAct, SIGNAL('triggered()'), self.__whatsThis)
        self.__actions.append(self.whatsThisAct)
        
        self.aboutAct = E4Action(self.trUtf8('About'), 
            self.trUtf8('&About'), 
            0, 0, self, 'help_help_about')
        self.aboutAct.setStatusTip(self.trUtf8('Display information about this software'))
        self.aboutAct.setWhatsThis(self.trUtf8(
                """<b>About</b>"""
                """<p>Display some information about this software.</p>"""
        ))
        self.connect(self.aboutAct, SIGNAL('triggered()'), self.__about)
        self.__actions.append(self.aboutAct)
        
        self.aboutQtAct = E4Action(self.trUtf8('About Qt'), 
            self.trUtf8('About &Qt'), 
            0, 0, self, 'help_help_about_qt')
        self.aboutQtAct.setStatusTip(\
            self.trUtf8('Display information about the Qt toolkit'))
        self.aboutQtAct.setWhatsThis(self.trUtf8(
                """<b>About Qt</b>"""
                """<p>Display some information about the Qt toolkit.</p>"""
        ))
        self.connect(self.aboutQtAct, SIGNAL('triggered()'), self.__aboutQt)
        self.__actions.append(self.aboutQtAct)
        
        self.zoomInAct = E4Action(self.trUtf8('Zoom in'), 
            UI.PixmapCache.getIcon("zoomIn.png"),
            self.trUtf8('Zoom &in'), 
            QKeySequence(self.trUtf8("Ctrl++","View|Zoom in")), 
            0, self, 'help_view_zoom_in')
        self.zoomInAct.setStatusTip(self.trUtf8('Zoom in on the text'))
        self.zoomInAct.setWhatsThis(self.trUtf8(
                """<b>Zoom in</b>"""
                """<p>Zoom in on the text. This makes the text bigger.</p>"""
        ))
        self.connect(self.zoomInAct, SIGNAL('triggered()'), self.__zoomIn)
        self.__actions.append(self.zoomInAct)
        
        self.zoomOutAct = E4Action(self.trUtf8('Zoom out'), 
            UI.PixmapCache.getIcon("zoomOut.png"),
            self.trUtf8('Zoom &out'), 
            QKeySequence(self.trUtf8("Ctrl+-","View|Zoom out")), 
            0, self, 'help_view_zoom_out')
        self.zoomOutAct.setStatusTip(self.trUtf8('Zoom out on the text'))
        self.zoomOutAct.setWhatsThis(self.trUtf8(
                """<b>Zoom out</b>"""
                """<p>Zoom out on the text. This makes the text smaller.</p>"""
        ))
        self.connect(self.zoomOutAct, SIGNAL('triggered()'), self.__zoomOut)
        self.__actions.append(self.zoomOutAct)
        
        self.zoomResetAct = E4Action(self.trUtf8('Zoom reset'), 
            UI.PixmapCache.getIcon("zoomReset.png"),
            self.trUtf8('Zoom &reset'), 
            QKeySequence(self.trUtf8("Ctrl+0","View|Zoom reset")), 
            0, self, 'help_view_zoom_reset')
        self.zoomResetAct.setStatusTip(self.trUtf8('Reset the zoom of the text'))
        self.zoomResetAct.setWhatsThis(self.trUtf8(
                """<b>Zoom reset</b>"""
                """<p>Reset the zoom of the text. """
                """This sets the zoom factor to 100%.</p>"""
        ))
        self.connect(self.zoomResetAct, SIGNAL('triggered()'), self.__zoomReset)
        self.__actions.append(self.zoomResetAct)
        
        if hasattr(QWebSettings, 'ZoomTextOnly'):
            self.zoomTextOnlyAct = E4Action(self.trUtf8('Zoom text only'), 
                self.trUtf8('Zoom &text only'), 
                0, 0, self, 'help_view_zoom_text_only')
            self.zoomTextOnlyAct.setCheckable(True)
            self.zoomTextOnlyAct.setStatusTip(self.trUtf8(
                    'Zoom text only; pictures remain constant'))
            self.zoomTextOnlyAct.setWhatsThis(self.trUtf8(
                    """<b>Zoom text only</b>"""
                    """<p>Zoom text only; pictures remain constant.</p>"""
            ))
            self.connect(self.zoomTextOnlyAct, SIGNAL('triggered(bool)'), 
                self.__zoomTextOnly)
            self.__actions.append(self.zoomTextOnlyAct)
        else:
            self.zoomTextOnlyAct = None
        
        self.pageSourceAct = E4Action(self.trUtf8('Show page source'), 
            self.trUtf8('Show page source'), 
            QKeySequence(self.trUtf8('Ctrl+U')), 0,
            self, 'help_show_page_source')
        self.pageSourceAct.setStatusTip(self.trUtf8('Show the page source in an editor'))
        self.pageSourceAct.setWhatsThis(self.trUtf8(
                """<b>Show page source</b>"""
                """<p>Show the page source in an editor.</p>"""
        ))
        self.connect(self.pageSourceAct, SIGNAL('triggered()'), self.__showPageSource)
        self.__actions.append(self.pageSourceAct)
        self.addAction(self.pageSourceAct)
        
        self.fullScreenAct = E4Action(self.trUtf8('Full Screen'), 
            UI.PixmapCache.getIcon("windowFullscreen.png"),
            self.trUtf8('&Full Screen'), 
            QKeySequence(self.trUtf8('F11')), 0,
            self, 'help_view_full_scree')
        self.connect(self.fullScreenAct, SIGNAL('triggered()'), self.__viewFullScreen)
        self.__actions.append(self.fullScreenAct)
        self.addAction(self.fullScreenAct)
        
        self.nextTabAct = E4Action(self.trUtf8('Show next tab'), 
            self.trUtf8('Show next tab'), 
            QKeySequence(self.trUtf8('Ctrl+Alt+Tab')), 0,
            self, 'help_view_next_tab')
        self.connect(self.nextTabAct, SIGNAL('triggered()'), self.__nextTab)
        self.__actions.append(self.nextTabAct)
        self.addAction(self.nextTabAct)
        
        self.prevTabAct = E4Action(self.trUtf8('Show previous tab'), 
            self.trUtf8('Show previous tab'), 
            QKeySequence(self.trUtf8('Shift+Ctrl+Alt+Tab')), 0,
            self, 'help_view_previous_tab')
        self.connect(self.prevTabAct, SIGNAL('triggered()'), self.__prevTab)
        self.__actions.append(self.prevTabAct)
        self.addAction(self.prevTabAct)
        
        self.switchTabAct = E4Action(self.trUtf8('Switch between tabs'), 
            self.trUtf8('Switch between tabs'), 
            QKeySequence(self.trUtf8('Ctrl+1')), 0,
            self, 'help_switch_tabs')
        self.connect(self.switchTabAct, SIGNAL('triggered()'), self.__switchTab)
        self.__actions.append(self.switchTabAct)
        self.addAction(self.switchTabAct)
        
        self.prefAct = E4Action(self.trUtf8('Preferences'),
            UI.PixmapCache.getIcon("configure.png"),
            self.trUtf8('&Preferences...'), 0, 0, self, 'help_preferences')
        self.prefAct.setStatusTip(self.trUtf8('Set the prefered configuration'))
        self.prefAct.setWhatsThis(self.trUtf8(
            """<b>Preferences</b>"""
            """<p>Set the configuration items of the application"""
            """ with your prefered values.</p>"""
        ))
        self.connect(self.prefAct, SIGNAL('triggered()'), self.__showPreferences)
        self.__actions.append(self.prefAct)

        self.acceptedLanguagesAct = E4Action(self.trUtf8('Languages'),
            UI.PixmapCache.getIcon("flag.png"),
            self.trUtf8('&Languages...'), 0, 0, self, 'help_accepted_languages')
        self.acceptedLanguagesAct.setStatusTip(self.trUtf8(
            'Configure the accepted languages for web pages'))
        self.acceptedLanguagesAct.setWhatsThis(self.trUtf8(
            """<b>Languages</b>"""
            """<p>Configure the accepted languages for web pages.</p>"""
        ))
        self.connect(self.acceptedLanguagesAct, SIGNAL('triggered()'), 
                     self.__showAcceptedLanguages)
        self.__actions.append(self.acceptedLanguagesAct)
        
        self.cookiesAct = E4Action(self.trUtf8('Cookies'),
            UI.PixmapCache.getIcon("cookie.png"),
            self.trUtf8('C&ookies...'), 0, 0, self, 'help_cookies')
        self.cookiesAct.setStatusTip(self.trUtf8(
            'Configure cookies handling'))
        self.cookiesAct.setWhatsThis(self.trUtf8(
            """<b>Cookies</b>"""
            """<p>Configure cookies handling.</p>"""
        ))
        self.connect(self.cookiesAct, SIGNAL('triggered()'), 
                     self.__showCookiesConfiguration)
        self.__actions.append(self.cookiesAct)
        
        self.syncTocAct = E4Action(self.trUtf8('Sync with Table of Contents'), 
            UI.PixmapCache.getIcon("syncToc.png"),
            self.trUtf8('Sync with Table of Contents'), 
            0, 0, self, 'help_sync_toc')
        self.syncTocAct.setStatusTip(self.trUtf8(
                'Synchronizes the table of contents with current page'))
        self.syncTocAct.setWhatsThis(self.trUtf8(
                """<b>Sync with Table of Contents</b>"""
                """<p>Synchronizes the table of contents with current page.</p>"""
        ))
        self.connect(self.syncTocAct, SIGNAL('triggered()'), self.__syncTOC)
        self.__actions.append(self.syncTocAct)
        
        self.showTocAct = E4Action(self.trUtf8('Table of Contents'), 
            self.trUtf8('Table of Contents'), 
            0, 0, self, 'help_show_toc')
        self.showTocAct.setStatusTip(self.trUtf8(
                'Shows the table of contents window'))
        self.showTocAct.setWhatsThis(self.trUtf8(
                """<b>Table of Contents</b>"""
                """<p>Shows the table of contents window.</p>"""
        ))
        self.connect(self.showTocAct, SIGNAL('triggered()'), self.__showTocWindow)
        self.__actions.append(self.showTocAct)
        
        self.showIndexAct = E4Action(self.trUtf8('Index'), 
            self.trUtf8('Index'), 
            0, 0, self, 'help_show_index')
        self.showIndexAct.setStatusTip(self.trUtf8(
                'Shows the index window'))
        self.showIndexAct.setWhatsThis(self.trUtf8(
                """<b>Index</b>"""
                """<p>Shows the index window.</p>"""
        ))
        self.connect(self.showIndexAct, SIGNAL('triggered()'), self.__showIndexWindow)
        self.__actions.append(self.showIndexAct)
        
        self.showSearchAct = E4Action(self.trUtf8('Search'), 
            self.trUtf8('Search'), 
            0, 0, self, 'help_show_search')
        self.showSearchAct.setStatusTip(self.trUtf8(
                'Shows the search window'))
        self.showSearchAct.setWhatsThis(self.trUtf8(
                """<b>Search</b>"""
                """<p>Shows the search window.</p>"""
        ))
        self.connect(self.showSearchAct, SIGNAL('triggered()'), self.__showSearchWindow)
        self.__actions.append(self.showSearchAct)
        
        self.manageQtHelpDocsAct = E4Action(self.trUtf8('Manage QtHelp Documents'), 
            self.trUtf8('Manage QtHelp &Documents'), 
            0, 0, self, 'help_qthelp_documents')
        self.manageQtHelpDocsAct.setStatusTip(self.trUtf8(
                'Shows a dialog to manage the QtHelp documentation set'))
        self.manageQtHelpDocsAct.setWhatsThis(self.trUtf8(
                """<b>Manage QtHelp Documents</b>"""
                """<p>Shows a dialog to manage the QtHelp documentation set.</p>"""
        ))
        self.connect(self.manageQtHelpDocsAct, SIGNAL('triggered()'), 
                     self.__manageQtHelpDocumentation)
        self.__actions.append(self.manageQtHelpDocsAct)
        
        self.manageQtHelpFiltersAct = E4Action(self.trUtf8('Manage QtHelp Filters'), 
            self.trUtf8('Manage QtHelp &Filters'), 
            0, 0, self, 'help_qthelp_filters')
        self.manageQtHelpFiltersAct.setStatusTip(self.trUtf8(
                'Shows a dialog to manage the QtHelp filters'))
        self.manageQtHelpFiltersAct.setWhatsThis(self.trUtf8(
                """<b>Manage QtHelp Filters</b>"""
                """<p>Shows a dialog to manage the QtHelp filters.</p>"""
        ))
        self.connect(self.manageQtHelpFiltersAct, SIGNAL('triggered()'), 
                     self.__manageQtHelpFilters)
        self.__actions.append(self.manageQtHelpFiltersAct)
        
        self.reindexDocumentationAct = E4Action(self.trUtf8('Reindex Documentation'), 
            self.trUtf8('&Reindex Documentation'), 
            0, 0, self, 'help_qthelp_reindex')
        self.reindexDocumentationAct.setStatusTip(self.trUtf8(
                'Reindexes the documentation set'))
        self.reindexDocumentationAct.setWhatsThis(self.trUtf8(
                """<b>Reindex Documentation</b>"""
                """<p>Reindexes the documentation set.</p>"""
        ))
        if not self.initShortcutsOnly:
            self.connect(self.reindexDocumentationAct, SIGNAL('triggered()'), 
                         self.__searchEngine.reindexDocumentation)
        self.__actions.append(self.reindexDocumentationAct)
        
        self.clearPrivateDataAct = E4Action(self.trUtf8('Clear private data'), 
                      self.trUtf8('&Clear private data'), 
                      0, 0,
                      self, 'help_clear_private_data')
        self.clearPrivateDataAct.setStatusTip(self.trUtf8('Clear private data'))
        self.clearPrivateDataAct.setWhatsThis(self.trUtf8(
                """<b>Clear private data</b>"""
                """<p>Clears the private data like browsing history, search history"""
                """ or the favicons database.</p>"""
        ))
        self.connect(self.clearPrivateDataAct, SIGNAL('triggered()'), 
                     self.__clearPrivateData)
        self.__actions.append(self.clearPrivateDataAct)
        
        self.clearIconsAct = E4Action(self.trUtf8('Clear icons database'), 
                      self.trUtf8('Clear &icons database'), 
                      0, 0,
                      self, 'help_clear_icons_db')
        self.clearIconsAct.setStatusTip(self.trUtf8('Clear the database of favicons'))
        self.clearIconsAct.setWhatsThis(self.trUtf8(
                """<b>Clear icons database</b>"""
                """<p>Clears the database of favicons of previously visited URLs.</p>"""
        ))
        self.connect(self.clearIconsAct, SIGNAL('triggered()'), self.__clearIconsDatabase)
        self.__actions.append(self.clearIconsAct)
        
        self.searchEnginesAct = E4Action(self.trUtf8('Configure Search Engines'), 
                      self.trUtf8('Configure &Search Engines...'), 
                      0, 0,
                      self, 'help_search_engines')
        self.searchEnginesAct.setStatusTip(self.trUtf8(
                'Configure the available search engines'))
        self.searchEnginesAct.setWhatsThis(self.trUtf8(
                """<b>Configure Search Engines...</b>"""
                """<p>Opens a dialog to configure the available search engines.</p>"""
        ))
        self.connect(self.searchEnginesAct, SIGNAL('triggered()'), 
                     self.__showEnginesConfigurationDialog)
        self.__actions.append(self.searchEnginesAct)
        
        self.passwordsAct = E4Action(self.trUtf8('Manage Saved Passwords'), 
                      self.trUtf8('Manage Saved Passwords...'), 
                      0, 0,
                      self, 'help_manage_passwords')
        self.passwordsAct.setStatusTip(self.trUtf8(
                'Manage the saved passwords'))
        self.passwordsAct.setWhatsThis(self.trUtf8(
                """<b>Manage Saved Passwords...</b>"""
                """<p>Opens a dialog to manage the saved passwords.</p>"""
        ))
        self.connect(self.passwordsAct, SIGNAL('triggered()'), 
                     self.__showPasswordsDialog)
        self.__actions.append(self.passwordsAct)
        
        self.adblockAct = E4Action(self.trUtf8('Ad Block'), 
                      self.trUtf8('&Ad Block...'), 
                      0, 0,
                      self, 'help_adblock')
        self.adblockAct.setStatusTip(self.trUtf8(
                'Configure AdBlock subscriptions and rules'))
        self.adblockAct.setWhatsThis(self.trUtf8(
                """<b>Ad Block...</b>"""
                """<p>Opens a dialog to configure AdBlock subscriptions and rules.</p>"""
        ))
        self.connect(self.adblockAct, SIGNAL('triggered()'), 
                     self.__showAdBlockDialog)
        self.__actions.append(self.adblockAct)
        
        self.toolsMonitorAct = E4Action(self.trUtf8('Show Network Monitor'), 
                      self.trUtf8('Show &Network Monitor'), 
                      0, 0,
                      self, 'help_tools_network_monitor')
        self.toolsMonitorAct.setStatusTip(self.trUtf8('Show the network monitor dialog'))
        self.toolsMonitorAct.setWhatsThis(self.trUtf8(
                """<b>Show Network Monitor</b>"""
                """<p>Shows the network monitor dialog.</p>"""
        ))
        self.connect(self.toolsMonitorAct, SIGNAL('triggered()'), 
                     self.__showNetworkMonitor)
        self.__actions.append(self.toolsMonitorAct)
        
        self.backAct.setEnabled(False)
        self.forwardAct.setEnabled(False)
        
        # now read the keyboard shortcuts for the actions
        Shortcuts.readShortcuts(helpViewer = self)
    
    def getActions(self):
        """
        Public method to get a list of all actions.
        
        @return list of all actions (list of E4Action)
        """
        return self.__actions[:]
        
    def __initMenus(self):
        """
        Private method to create the menus.
        """
        mb = self.menuBar()
        
        menu = mb.addMenu(self.trUtf8('&File'))
        menu.setTearOffEnabled(True)
        menu.addAction(self.newTabAct)
        menu.addAction(self.newAct)
        menu.addAction(self.openAct)
        menu.addAction(self.openTabAct)
        menu.addSeparator()
        menu.addAction(self.saveAsAct)
        menu.addSeparator()
        menu.addAction(self.importBookmarksAct)
        menu.addAction(self.exportBookmarksAct)
        menu.addSeparator()
        menu.addAction(self.printPreviewAct)
        menu.addAction(self.printAct)
        menu.addSeparator()
        menu.addAction(self.closeAct)
        menu.addAction(self.closeAllAct)
        menu.addSeparator()
        menu.addAction(self.privateBrowsingAct)
        menu.addSeparator()
        menu.addAction(self.exitAct)
        
        menu = mb.addMenu(self.trUtf8('&Edit'))
        menu.setTearOffEnabled(True)
        menu.addAction(self.copyAct)
        menu.addSeparator()
        menu.addAction(self.findAct)
        menu.addAction(self.findNextAct)
        menu.addAction(self.findPrevAct)
        
        menu = mb.addMenu(self.trUtf8('&View'))
        menu.setTearOffEnabled(True)
        menu.addAction(self.zoomInAct)
        menu.addAction(self.zoomResetAct)
        menu.addAction(self.zoomOutAct)
        if self.zoomTextOnlyAct is not None:
            menu.addAction(self.zoomTextOnlyAct)
        menu.addSeparator()
        menu.addAction(self.pageSourceAct)
        menu.addAction(self.fullScreenAct)
        
        menu = mb.addMenu(self.trUtf8('&Go'))
        menu.setTearOffEnabled(True)
        menu.addAction(self.backAct)
        menu.addAction(self.forwardAct)
        menu.addAction(self.homeAct)
        menu.addSeparator()
        menu.addAction(self.stopAct)
        menu.addAction(self.reloadAct)
        menu.addSeparator()
        menu.addAction(self.syncTocAct)
        
        self.historyMenu = HistoryMenu(self)
        self.historyMenu.setTearOffEnabled(True)
        self.historyMenu.setTitle(self.trUtf8('H&istory'))
        self.connect(self.historyMenu, SIGNAL("openUrl(const QUrl&, const QString&)"), 
                     self.__openUrl)
        self.connect(self.historyMenu, SIGNAL("newUrl(const QUrl&, const QString&)"), 
                     self.__openUrlNewTab)
        mb.addMenu(self.historyMenu)
        
        self.bookmarksMenu = BookmarksMenuBarMenu(self)
        self.bookmarksMenu.setTearOffEnabled(True)
        self.bookmarksMenu.setTitle(self.trUtf8('&Bookmarks'))
        self.connect(self.bookmarksMenu, SIGNAL("openUrl(const QUrl&, const QString&)"), 
                     self.__openUrl)
        self.connect(self.bookmarksMenu, SIGNAL("newUrl(const QUrl&, const QString&)"), 
                     self.__openUrlNewTab)
        mb.addMenu(self.bookmarksMenu)
        
        bookmarksActions = []
        bookmarksActions.append(self.bookmarksManageAct)
        bookmarksActions.append(self.bookmarksAddAct)
        bookmarksActions.append(self.bookmarksAllTabsAct)
        bookmarksActions.append(self.bookmarksAddFolderAct)
        self.bookmarksMenu.setInitialActions(bookmarksActions)
        
        menu = mb.addMenu(self.trUtf8('&Settings'))
        menu.setTearOffEnabled(True)
        menu.addAction(self.prefAct)
        menu.addAction(self.acceptedLanguagesAct)
        menu.addAction(self.cookiesAct)
        menu.addSeparator()
        menu.addAction(self.searchEnginesAct)
        menu.addSeparator()
        menu.addAction(self.passwordsAct)
        menu.addSeparator()
        menu.addAction(self.adblockAct)
        menu.addSeparator()
        menu.addAction(self.manageQtHelpDocsAct)
        menu.addAction(self.manageQtHelpFiltersAct)
        menu.addAction(self.reindexDocumentationAct)
        menu.addSeparator()
        menu.addAction(self.clearPrivateDataAct)
        menu.addAction(self.clearIconsAct)
        
        menu = mb.addMenu(self.trUtf8("&Tools"))
        menu.setTearOffEnabled(True)
        menu.addAction(self.toolsMonitorAct)
        
        menu = mb.addMenu(self.trUtf8("&Window"))
        menu.setTearOffEnabled(True)
        menu.addAction(self.showTocAct)
        menu.addAction(self.showIndexAct)
        menu.addAction(self.showSearchAct)
        
        mb.addSeparator()
        
        menu = mb.addMenu(self.trUtf8('&Help'))
        menu.setTearOffEnabled(True)
        menu.addAction(self.aboutAct)
        menu.addAction(self.aboutQtAct)
        menu.addSeparator()
        menu.addAction(self.whatsThisAct)
    
    def __initTabContextMenu(self):
        """
        Private mezhod to create the tab context menu.
        """
        self.__tabContextMenu = QMenu(self.tabWidget)
        self.tabContextNewAct = \
            self.__tabContextMenu.addAction(self.newTabAct)
        self.__tabContextMenu.addSeparator()
        self.leftMenuAct = \
            self.__tabContextMenu.addAction(UI.PixmapCache.getIcon("1leftarrow.png"),
            self.trUtf8('Move Left'), self.__tabContextMenuMoveLeft)
        self.rightMenuAct = \
            self.__tabContextMenu.addAction(UI.PixmapCache.getIcon("1rightarrow.png"),
            self.trUtf8('Move Right'), self.__tabContextMenuMoveRight)
        self.__tabContextMenu.addSeparator()
        self.tabContextCloneAct = \
            self.__tabContextMenu.addAction(self.trUtf8("Duplicate Page"), 
                self.__tabContextMenuClone)
        self.__tabContextMenu.addSeparator()
        self.tabContextCloseAct = \
            self.__tabContextMenu.addAction(UI.PixmapCache.getIcon("close.png"),
                self.trUtf8('Close'), self.__tabContextMenuClose)
        self.tabContextCloseOthersAct = \
            self.__tabContextMenu.addAction(self.trUtf8("Close Others"), 
                self.__tabContextMenuCloseOthers)
        self.__tabContextMenu.addAction(self.closeAllAct)
        self.__tabContextMenu.addSeparator()
        self.__tabContextMenu.addAction(UI.PixmapCache.getIcon("printPreview.png"),
            self.trUtf8('Print Preview'), self.__tabContextMenuPrintPreview)
        self.__tabContextMenu.addAction(UI.PixmapCache.getIcon("print.png"),
            self.trUtf8('Print'), self.__tabContextMenuPrint)
        self.__tabContextMenu.addSeparator()
        self.__tabContextMenu.addAction(self.bookmarksAllTabsAct)
    
    def __initToolbars(self):
        """
        Private method to create the toolbars.
        """
        filetb = self.addToolBar(self.trUtf8("File"))
        filetb.setObjectName("FileToolBar")
        filetb.setIconSize(UI.Config.ToolBarIconSize)
        filetb.addAction(self.newTabAct)
        filetb.addAction(self.newAct)
        filetb.addAction(self.openAct)
        filetb.addAction(self.openTabAct)
        filetb.addSeparator()
        filetb.addAction(self.saveAsAct)
        filetb.addSeparator()
        filetb.addAction(self.printPreviewAct)
        filetb.addAction(self.printAct)
        filetb.addSeparator()
        filetb.addAction(self.closeAct)
        filetb.addAction(self.exitAct)
        
        edittb = self.addToolBar(self.trUtf8("Edit"))
        edittb.setObjectName("EditToolBar")
        edittb.setIconSize(UI.Config.ToolBarIconSize)
        edittb.addAction(self.copyAct)
        
        viewtb = self.addToolBar(self.trUtf8("View"))
        viewtb.setObjectName("ViewToolBar")
        viewtb.setIconSize(UI.Config.ToolBarIconSize)
        viewtb.addAction(self.zoomInAct)
        viewtb.addAction(self.zoomResetAct)
        viewtb.addAction(self.zoomOutAct)
        viewtb.addSeparator()
        viewtb.addAction(self.fullScreenAct)
        
        findtb = self.addToolBar(self.trUtf8("Find"))
        findtb.setObjectName("FindToolBar")
        findtb.setIconSize(UI.Config.ToolBarIconSize)
        findtb.addAction(self.findAct)
        findtb.addAction(self.findNextAct)
        findtb.addAction(self.findPrevAct)
        
        filtertb = self.addToolBar(self.trUtf8("Filter"))
        filtertb.setObjectName("FilterToolBar")
        self.filterCombo = QComboBox()
        self.filterCombo.setMinimumWidth(
            QFontMetrics(QFont()).width("ComboBoxWithEnoughWidth"))
        filtertb.addWidget(QLabel(self.trUtf8("Filtered by: ")))
        filtertb.addWidget(self.filterCombo)
        self.connect(self.__helpEngine, SIGNAL("setupFinished()"), 
                     self.__setupFilterCombo)
        self.connect(self.filterCombo, SIGNAL("activated(const QString&)"), 
                     self.__filterQtHelpDocumentation)
        self.__setupFilterCombo()
        
        settingstb = self.addToolBar(self.trUtf8("Settings"))
        settingstb.setObjectName("SettingsToolBar")
        settingstb.setIconSize(UI.Config.ToolBarIconSize)
        settingstb.addAction(self.prefAct)
        settingstb.addAction(self.acceptedLanguagesAct)
        settingstb.addAction(self.cookiesAct)
        
        helptb = self.addToolBar(self.trUtf8("Help"))
        helptb.setObjectName("HelpToolBar")
        helptb.setIconSize(UI.Config.ToolBarIconSize)
        helptb.addAction(self.whatsThisAct)
        
        self.addToolBarBreak()
        
        gotb = self.addToolBar(self.trUtf8("Go"))
        gotb.setObjectName("GoToolBar")
        gotb.setIconSize(UI.Config.ToolBarIconSize)
        gotb.addAction(self.backAct)
        gotb.addAction(self.forwardAct)
        gotb.addAction(self.reloadAct)
        gotb.addAction(self.stopAct)
        gotb.addAction(self.homeAct)
        gotb.addSeparator()
        
        self.iconLabel = QLabel()
        gotb.addWidget(self.iconLabel)
        
        self.pathCombo = QComboBox()
        self.pathCombo.setDuplicatesEnabled(False)
        self.pathCombo.setInsertPolicy(QComboBox.InsertAtTop)
        self.pathCombo.setEditable(1)
        self.pathCombo.setAutoCompletion(True)
        self.connect(self.pathCombo, SIGNAL('activated(const QString&)'),
                     self.__pathSelected)
        self.connect(self.pathCombo.lineEdit(), SIGNAL('returnPressed()'),
                     self.__pathEdited)
        self.pathCombo.setWhatsThis(self.trUtf8(
                """<p>Enter the help file to be displayed directly into this"""
                """ edit field. Select a previously shown help file from the"""
                """ drop down list.</p>"""
        ))
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(6)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pathCombo.sizePolicy().hasHeightForWidth())
        self.pathCombo.setSizePolicy(sizePolicy)
        gotb.addWidget(self.pathCombo)
        self.pathComboDefaultColor = \
            self.pathCombo.lineEdit().palette().color(QPalette.Base)
        self.__historyCompletionModel = HistoryCompletionModel(self)
        self.__historyCompletionModel.setSourceModel(
            self.historyManager().historyFilterModel())
        self.__historyCompleter = HistoryCompleter(self.__historyCompletionModel, self)
        self.connect(self.__historyCompleter, SIGNAL("activated(const QString&)"), 
                     self.__pathSelected)
        self.pathCombo.setCompleter(self.__historyCompleter)
        
        self.privacyLabel = QLabel()
        gotb.addWidget(self.privacyLabel)
        
        gotb.addSeparator()
        self.searchEdit = HelpWebSearchWidget(self)
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(2)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.searchEdit.sizePolicy().hasHeightForWidth())
        self.searchEdit.setSizePolicy(sizePolicy)
        self.connect(self.searchEdit, SIGNAL("search"), self.__linkActivated)
        gotb.addWidget(self.searchEdit)
        
        self.backMenu = QMenu(self)
        self.connect(self.backMenu, SIGNAL("aboutToShow()"), self.__showBackMenu)
        self.connect(self.backMenu, SIGNAL("triggered(QAction*)"), 
                     self.__navigationMenuActionTriggered)
        backButton = gotb.widgetForAction(self.backAct)
        backButton.setMenu(self.backMenu)
        backButton.setPopupMode(QToolButton.MenuButtonPopup)
        
        self.forwardMenu = QMenu(self)
        self.connect(self.forwardMenu, SIGNAL("aboutToShow()"), self.__showForwardMenu)
        self.connect(self.forwardMenu, SIGNAL("triggered(QAction*)"), 
                     self.__navigationMenuActionTriggered)
        forwardButton = gotb.widgetForAction(self.forwardAct)
        forwardButton.setMenu(self.forwardMenu)
        forwardButton.setPopupMode(QToolButton.MenuButtonPopup)
        
        bookmarksModel = self.bookmarksManager().bookmarksModel()
        self.bookmarksToolBar = BookmarksToolBar(bookmarksModel)
        self.bookmarksToolBar.setObjectName("BookmarksToolBar")
        self.bookmarksToolBar.setIconSize(UI.Config.ToolBarIconSize)
        self.connect(self.bookmarksToolBar, 
                     SIGNAL("openUrl(const QUrl&, const QString&)"), 
                     self.__openUrl)
        self.connect(self.bookmarksToolBar, 
                     SIGNAL("newUrl(const QUrl&, const QString&)"), 
                     self.__openUrlNewTab)
        self.addToolBarBreak()
        self.addToolBar(self.bookmarksToolBar)
        
    def __nextTab(self):
        """
        Private slot used to show the next tab.
        """
        fwidget = QApplication.focusWidget()
        while fwidget and not hasattr(fwidget, 'nextTab'):
            fwidget = fwidget.parent()
        if fwidget:
            fwidget.nextTab()
        
    def __prevTab(self):
        """
        Private slot used to show the previous tab.
        """
        fwidget = QApplication.focusWidget()
        while fwidget and not hasattr(fwidget, 'prevTab'):
            fwidget = fwidget.parent()
        if fwidget:
            fwidget.prevTab()
        
    def __switchTab(self):
        """
        Private slot used to switch between the current and the previous current tab.
        """
        fwidget = QApplication.focusWidget()
        while fwidget and not hasattr(fwidget, 'switchTab'):
            fwidget = fwidget.parent()
        if fwidget:
            fwidget.switchTab()
        
    def __whatsThis(self):
        """
        Private slot called in to enter Whats This mode.
        """
        QWhatsThis.enterWhatsThisMode()
        
    def __showHistoryMenu(self):
        """
        Private slot called in order to show the history menu.
        """
        self.historyMenu.clear()
        self.historyMenu.addAction(self.clearHistoryAct)
        self.clearHistoryAct.setData(QVariant(-1))
        self.historyMenu.addSeparator()
        idx = 0
        for hist in self.mHistory:
            act = self.historyMenu.addAction(\
                Utilities.compactPath(unicode(hist), self.maxMenuFilePathLen))
            act.setData(QVariant(idx))
            idx += 1
            act.setIcon(HelpWindow.__getWebIcon(QUrl(hist)))
        
    def __pathEdited(self):
        """
        Private slot called, when a URL has been entered.
        """
        path = self.pathCombo.currentText()
        self.__pathSelected(path)
        
    def __pathSelected(self, path):
        """
        Private slot called when a file is selected in the combobox.
        
        @param path path to be shown (string or QString)
        """
        url = self.__guessUrlFromPath(path)
        self.currentBrowser().setSource(url)
        self.__setPathComboBackground()
    
    def __guessUrlFromPath(self, path):
        """
        Private method to guess an URL given a path string.
        
        @param path path string to guess an URL for (QString)
        @return guessed URL (QUrl)
        """
        manager = self.searchEdit.openSearchManager()
        url = manager.convertKeywordSearchToUrl(path)
        if url.isValid():
            return url
        
        return QUrl(path)
    
    def __setPathComboBackground(self):
        """
        Private slot to change the path combo background to indicate save URLs.
        """
        url = QUrl(self.pathCombo.currentText())
        le = self.pathCombo.lineEdit()
        p = le.palette()
        if url.isEmpty() or url.scheme() != "https":
            p.setBrush(QPalette.Base, self.pathComboDefaultColor)
        else:
            p.setBrush(QPalette.Base, QBrush(Preferences.getHelp("SaveUrlColor")))
        le.setPalette(p)
        le.update()
    
    def __elide(self, txt, mode = Qt.ElideRight, length = 40):
        """
        Private method to elide some text.
        
        @param txt text to be elided (string or QString)
        @keyparam mode elide mode (Qt.TextElideMode)
        @keyparam length amount of characters to be used (integer)
        @return the elided text (QString)
        """
        qs = QString(txt)
        if mode == Qt.ElideNone or qs.length() < length:
            return qs
        elif mode == Qt.ElideLeft:
            return QString("...%1").arg(qs.right(length))
        elif mode == Qt.ElideMiddle:
            return QString("%1...%2").arg(qs.left(length / 2)).arg(qs.right(length / 2))
        elif mode == Qt.ElideRight:
            return QString("%1...").arg(qs.left(length))
        else:
            # just in case
            return qs
    
    def __sourceChanged(self, url):
        """
        Private slot called when the displayed text of the combobox is changed.
        """
        selectedURL = url.toString()
        if not selectedURL.isEmpty() and self.pathCombo:
            i = self.pathCombo.findText(selectedURL)
            if i == -1:
                if not QWebSettings.globalSettings()\
                       .testAttribute(QWebSettings.PrivateBrowsingEnabled):
                    self.pathCombo.insertItem(0, selectedURL)
                    self.pathCombo.setCurrentIndex(0)
            else:
                self.pathCombo.setCurrentIndex(i)
            
            self.__setPathComboBackground()
        
        self.iconChanged(self.currentBrowser().icon())
    
    def __titleChanged(self, title):
        """
        Private slot called to handle a change of the current browsers title.
        
        @param title new title (QString)
        """
        if title == "":
            title = self.currentBrowser().url().toString()
        
        self.tabWidget.setTabText(self.tabWidget.currentIndex(), 
            self.__elide(title.replace("&", "&&")))
        self.tabWidget.setTabToolTip(self.tabWidget.currentIndex(), 
            title)
        self.historyManager().updateHistoryEntry(
            self.currentBrowser().url().toString(), title)
    
    def newTab(self, link = None):
        """
        Public slot called to open a new help window tab.
        
        @param link file to be displayed in the new window (string, QString or QUrl)
        """
        if link is None:
            linkName = ""
        elif isinstance(link, QUrl):
            linkName = link.toString()
        else:
            linkName = link
        self.newBrowser(linkName)
    
    def newWindow(self, link = None):
        """
        Public slot called to open a new help browser dialog.
        
        @param link file to be displayed in the new window (QUrl)
        """
        if link is None:
            linkName = ""
        elif isinstance(link, QUrl):
            linkName = link.toString()
        else:
            linkName = link
        h = HelpWindow(linkName, ".", self.parent(), "qbrowser", self.fromEric)
        h.show()
    
    def __openFile(self):
        """
        Private slot called to open a file.
        """
        fn = KQFileDialog.getOpenFileName(\
            self, self.trUtf8("Open File"),
            QString(),
            self.trUtf8("Help Files (*.html *.htm);;"
                        "PDF Files (*.pdf);;"
                        "CHM Files (*.chm);;"
                        "All Files (*)"
            ))
        if not fn.isEmpty():
            self.currentBrowser().setSource(QUrl("file://" + fn))
        
    def __openFileNewTab(self):
        """
        Private slot called to open a file in a new tab.
        """
        fn = KQFileDialog.getOpenFileName(\
            self, self.trUtf8("Open File"),
            QString(),
            self.trUtf8("Help Files (*.html *.htm);;"
                        "PDF Files (*.pdf);;"
                        "CHM Files (*.chm);;"
                        "All Files (*)"
            ))
        if not fn.isEmpty():
            self.newTab("file://" + fn)
        
    def __savePageAs(self):
        """
        Private slot to save the current page.
        """
        browser = self.currentBrowser()
        if browser is not None:
            browser.saveAs()
        
    def __printFile(self, browser = None):
        """
        Private slot called to print the displayed file.
        
        @param browser reference to the browser to be printed (QTextEdit)
        """
        if browser is None:
            browser = self.currentBrowser()
        
        self.__printRequested(browser.page().mainFrame())
        
    def __printRequested(self, frame):
        """
        Private slot to handle a print request.
        
        @param frame reference to the frame to be printed (QWebFrame)
        """
        printer = KdeQt.KQPrinter.KQPrinter(mode = QPrinter.HighResolution)
        printer.setFullPage(1)
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
        if printDialog.exec_() == QDialog.Accepted:
            try:
                frame.print_(printer)
            except AttributeError:
                KQMessageBox.critical(self,
                    self.trUtf8("Eric Web Browser"),
                    self.trUtf8("""<p>Printing is not available due to a bug in PyQt4."""
                                """Please upgrade.</p>"""))
                return
        
    def __printPreviewFile(self, browser = None):
        """
        Private slot called to show a print preview of the displayed file.
        
        @param browser reference to the browser to be printed (QTextEdit)
        """
        from PyQt4.QtGui import QPrintPreviewDialog
        
        if browser is None:
            browser = self.currentBrowser()
        
        printer = KdeQt.KQPrinter.KQPrinter(mode = QPrinter.HighResolution)
        printer.setFullPage(1)
        if Preferences.getPrinter("ColorMode"):
            printer.setColorMode(KdeQt.KQPrinter.Color)
        else:
            printer.setColorMode(KdeQt.KQPrinter.GrayScale)
        if Preferences.getPrinter("FirstPageFirst"):
            printer.setPageOrder(KdeQt.KQPrinter.FirstPageFirst)
        else:
            printer.setPageOrder(KdeQt.KQPrinter.LastPageFirst)
        printer.setPrinterName(Preferences.getPrinter("PrinterName"))
        
        self.__printPreviewBrowser = browser
        preview = QPrintPreviewDialog(printer, self)
        self.connect(preview, SIGNAL("paintRequested(QPrinter*)"), self.__printPreview)
        preview.exec_()
        
    def __printPreview(self, printer):
        """
        Public slot to generate a print preview.
        
        @param printer reference to the printer object (QPrinter)
        """
        try:
            self.__printPreviewBrowser.print_(printer)
        except AttributeError:
            KQMessageBox.critical(self,
                self.trUtf8("Eric Web Browser"),
                self.trUtf8("""<p>Printing is not available due to a bug in PyQt4."""
                            """Please upgrade.</p>"""))
            return
        
    def __about(self):
        """
        Private slot to show the about information.
        """
        KQMessageBox.about(self, self.trUtf8("Eric Web Browser"), self.trUtf8(
            """<h3>About Eric Web Browser</h3>"""
            """<p>The Eric Web Browser is a combined help file and HTML browser.</p>"""
        ))
        
    def __aboutQt(self):
        """
        Private slot to show info about Qt.
        """
        KQMessageBox.aboutQt(self, self.trUtf8("Eric Web Browser"))

    def __removeOldHistory(self):
        """
        Private method to remove the old history from the eric4 preferences file.
        """
        hist = Preferences.Prefs.settings.value('History/Files')
        if hist.isValid():
            Preferences.Prefs.settings.remove('History/Files')
        
    def __setBackwardAvailable(self, b):
        """
        Private slot called when backward references are available.
        
        @param b flag indicating availability of the backwards action (boolean)
        """
        self.backAct.setEnabled(b)
        
    def __setForwardAvailable(self, b):
        """
        Private slot called when forward references are available.
        
        @param b flag indicating the availability of the forwards action (boolean)
        """
        self.forwardAct.setEnabled(b)
        
    def __setLoadingActions(self, b):
        """
        Private slot to set the loading dependent actions.
        
        @param b flag indicating the loading state to consider (boolean)
        """
        self.reloadAct.setEnabled(not b)
        self.stopAct.setEnabled(b)
        
    def __addBookmark(self):
        """
        Private slot called to add the displayed file to the bookmarks.
        """
        view = self.currentBrowser()
        url = QString(view.url().toEncoded())
        title = view.title()
        
        dlg = AddBookmarkDialog()
        dlg.setUrl(url)
        dlg.setTitle(title)
        menu = self.bookmarksManager().menu()
        idx = self.bookmarksManager().bookmarksModel().nodeIndex(menu)
        dlg.setCurrentIndex(idx)
        dlg.exec_()
        
    def __addBookmarkFolder(self):
        """
        Private slot to add a new bookmarks folder.
        """
        dlg = AddBookmarkDialog()
        menu = self.bookmarksManager().menu()
        idx = self.bookmarksManager().bookmarksModel().nodeIndex(menu)
        dlg.setCurrentIndex(idx)
        dlg.setFolder(True)
        dlg.exec_()
        
    def __showBookmarksDialog(self):
        """
        Private slot to show the bookmarks dialog.
        """
        self.__bookmarksDialog = BookmarksDialog(self)
        self.__bookmarksDialog.setAttribute(Qt.WA_DeleteOnClose)
        self.connect(self.__bookmarksDialog, 
                     SIGNAL("openUrl(const QUrl&, const QString&)"), 
                     self.__openUrl)
        self.connect(self.__bookmarksDialog, 
                     SIGNAL("newUrl(const QUrl&, const QString&)"), 
                     self.__openUrlNewTab)
        self.__bookmarksDialog.show()
        
    def __bookmarkAll(self):
        """
        Private slot to bookmark all open tabs.
        """
        dlg = AddBookmarkDialog()
        dlg.setFolder(True)
        dlg.setTitle(self.trUtf8("Saved Tabs"))
        dlg.exec_()
        
        folder = dlg.addedNode()
        if folder is None:
            return
        
        for index in range(self.tabWidget.count()):
            tab = self.tabWidget.widget(index)
            if tab is None:
                continue
            
            bookmark = BookmarkNode(BookmarkNode.Bookmark)
            bookmark.url = QString.fromUtf8(tab.url().toEncoded())
            bookmark.title = tab.title()
            
            self.bookmarksManager().addBookmark(folder, bookmark)
        
    def __find(self):
        """
        Private slot to handle the find action.
        
        It opens the search dialog in order to perform the various
        search actions and to collect the various search info.
        """
        self.findDlg.showFind()
        
    def closeEvent(self, e):
        """
        Private event handler for the close event.
        
        @param e the close event (QCloseEvent)
                <br />This event is simply accepted after the history has been
                saved and all window references have been deleted.
        """
        self.__closeNetworkMonitor()
        
        self.cookieJar().close()
        
        self.bookmarksManager().close()
        
        self.historyManager().close()
        
        self.passwordManager().close()
        
        self.adblockManager().close()
        
        self.searchEdit.openSearchManager().close()
        
        self.__searchEngine.cancelIndexing()
        self.__searchEngine.cancelSearching()
        
        if self.__helpInstaller:
            self.__helpInstaller.stop()
        
        self.searchEdit.saveSearches()
        
        state = self.saveState()
        Preferences.setHelp("HelpViewerState", state)

        if Preferences.getHelp("SaveGeometry"):
            if not self.__isFullScreen():
                Preferences.setGeometry("HelpViewerGeometry", self.saveGeometry())
        else:
            Preferences.setGeometry("HelpViewerGeometry", QByteArray())
        
        try:
            del self.__class__.helpwindows[self.__class__.helpwindows.index(self)]
        except ValueError:
            pass
        
        if not self.fromEric:
            Preferences.syncPreferences()
        
        e.accept()
        self.emit(SIGNAL("helpClosed"))

    def __backward(self):
        """
        Private slot called to handle the backward action.
        """
        self.currentBrowser().backward()
    
    def __forward(self):
        """
        Private slot called to handle the forward action.
        """
        self.currentBrowser().forward()
    
    def __home(self):
        """
        Private slot called to handle the home action.
        """
        self.currentBrowser().home()
    
    def __reload(self):
        """
        Private slot called to handle the reload action.
        """
        self.currentBrowser().reload()
    
    def __stopLoading(self):
        """
        Private slot called to handle loading of the current page.
        """
        self.currentBrowser().stop()
    
    def __zoomIn(self):
        """
        Private slot called to handle the zoom in action.
        """
        self.currentBrowser().zoomIn()
    
    def __zoomOut(self):
        """
        Private slot called to handle the zoom out action.
        """
        self.currentBrowser().zoomOut()
    
    def __zoomReset(self):
        """
        Private slot called to handle the zoom reset action.
        """
        self.currentBrowser().zoomReset()
    
    def __zoomTextOnly(self, textOnly):
        """
        Private slot called to handle the zoom text only action.
        
        @param textOnly flag indicating to zoom text only (boolean)
        """
        QWebSettings.globalSettings().setAttribute(QWebSettings.ZoomTextOnly, textOnly)
        self.emit(SIGNAL("zoomTextOnlyChanged(bool)"), textOnly)
    
    def __viewFullScreen(self,):
        """
        Private slot called to toggle fullscreen mode.
        """
        if self.__isFullScreen():
            # switch back to normal
            self.setWindowState(self.windowState() & ~Qt.WindowFullScreen)
            self.menuBar().show()
            self.fullScreenAct.setIcon(UI.PixmapCache.getIcon("windowFullscreen.png"))
        else:
            # switch to full screen
            self.setWindowState(self.windowState() | Qt.WindowFullScreen)
            self.menuBar().hide()
            self.fullScreenAct.setIcon(UI.PixmapCache.getIcon("windowRestore.png"))
    
    def __isFullScreen(self):
        """
        Private method to determine, if the window is in full screen mode.
        
        @return flag indicating full screen mode (boolean)
        """
        return self.windowState() & Qt.WindowFullScreen
    
    def __copy(self):
        """
        Private slot called to handle the copy action.
        """
        self.currentBrowser().copy()
    
    def __close(self):
        """
        Private slot called to handle the close action.
        """
        browser = self.currentBrowser()
        self.tabWidget.removeTab(self.tabWidget.currentIndex())
        del browser
        if self.tabWidget.count() == 0:
            self.newTab()
        else:
            self.__currentChanged(self.tabWidget.currentIndex())
    
    def __closeAll(self):
        """
        Private slot called to handle the close all action.
        """
        for index in range(self.tabWidget.count() - 1, -1, -1):
            self.__closeAt(index)
    
    def __closeAt(self, index):
        """
        Private slot to close a window based on it's index.
        
        @param index index of window to close (integer)
        """
        browser = self.tabWidget.widget(index)
        self.tabWidget.removeTab(index)
        del browser
        if self.tabWidget.count() == 0:
            self.newTab()
        else:
            self.__currentChanged(self.tabWidget.currentIndex())
    
    def __windowCloseRequested(self):
        """
        Private slot to handle the windowCloseRequested signal of a browser.
        """
        page = self.sender()
        if page is None:
            return
        
        browser = page.view()
        if browser is None:
            return
        
        index = self.tabWidget.indexOf(browser)
        self.tabWidget.removeTab(index)
        del browser
        if self.tabWidget.count() == 0:
            self.newTab()
        else:
            self.__currentChanged(self.tabWidget.currentIndex())
    
    def __privateBrowsing(self):
        """
        Private slot to switch private browsing.
        """
        settings = QWebSettings.globalSettings()
        pb = settings.testAttribute(QWebSettings.PrivateBrowsingEnabled)
        if not pb:
            txt = self.trUtf8("""<b>Are you sure you want to turn on private"""
                              """ browsing?</b><p>When private browsing is turned on,"""
                              """ web pages are not added to the history, searches"""
                              """ are not added to the list of recent searches and"""
                              """ web site icons and cookies are not stored."""
                              """ Until you close the window, you can still click"""
                              """ the Back and Forward buttons to return to the"""
                              """ web pages you have opened.</p>""")
            res = KQMessageBox.question(self, "", txt,
                QMessageBox.StandardButtons(\
                    QMessageBox.Cancel | \
                    QMessageBox.Ok),
                QMessageBox.Ok)
            if res == QMessageBox.Ok:
                settings.setAttribute(QWebSettings.PrivateBrowsingEnabled, True)
                self.pathCombo.setInsertPolicy(QComboBox.NoInsert)
                self.privacyLabel.setPixmap(
                    UI.PixmapCache.getPixmap("privateBrowsing.png"))
                self.__setIconDatabasePath(False)
        else:
            settings.setAttribute(QWebSettings.PrivateBrowsingEnabled, False)
            self.pathCombo.setInsertPolicy(QComboBox.InsertAtTop)
            self.privacyLabel.setPixmap(QPixmap())
            self.__setIconDatabasePath(True)
    
    def currentBrowser(self):
        """
        Public method to get a reference to the current help browser.
        
        @return reference to the current help browser (HelpBrowser)
        """
        return self.tabWidget.currentWidget()
    
    def browsers(self):
        """
        Public method to get a list of references to all help browsers.
        
        @return list of references to help browsers (list of HelpBrowser)
        """
        l = []
        for index in range(self.tabWidget.count()):
            l.append(self.tabWidget.widget(index))
        return l
    
    def newBrowser(self, link):
        """
        Public method to create a new help browser tab.
        
        @param link link to be shown (string or QString)
        """
        browser = HelpBrowser(self)
        
        self.connect(browser, SIGNAL('sourceChanged(const QUrl &)'),
                     self.__sourceChanged)
        self.connect(browser, SIGNAL("titleChanged(const QString&)"), self.__titleChanged)
        
        index = self.tabWidget.addTab(browser, self.trUtf8("..."))
        self.tabWidget.setCurrentIndex(index)
        
        link = QString(link)
        if link.isEmpty() and Preferences.getHelp("StartupBehavior") == 0:
            link = Preferences.getHelp("HomePage")
        
        if not link.isEmpty():
            browser.setSource(QUrl(link))
            if browser.documentTitle().isNull():
                self.tabWidget.setTabText(index, self.__elide(link, Qt.ElideMiddle))
                self.tabWidget.setTabToolTip(index, link)
            else:
                self.tabWidget.setTabText(index, 
                    self.__elide(browser.documentTitle().replace("&", "&&")))
                self.tabWidget.setTabToolTip(index, browser.documentTitle())
        
        self.connect(browser, SIGNAL('highlighted(const QString&)'),
                     self.statusBar(), SLOT('showMessage(const QString&)'))
        self.connect(browser, SIGNAL('backwardAvailable(bool)'),
                     self.__setBackwardAvailable)
        self.connect(browser, SIGNAL('forwardAvailable(bool)'),
                     self.__setForwardAvailable)
        self.connect(browser.page(), SIGNAL('windowCloseRequested()'), 
                     self.__windowCloseRequested)
        self.connect(browser.page(), SIGNAL('printRequested(QWebFrame*)'), 
                     self.__printRequested)
        self.connect(browser, SIGNAL("search(const QUrl &)"), 
                     self.newTab)
        
        self.closeAct.setEnabled(True)
        self.closeAllAct.setEnabled(True)
        self.closeButton and self.closeButton.setEnabled(True)
        self.navigationButton.setEnabled(True)
    
    def __currentChanged(self, index):
        """
        Private slot to handle the currentChanged signal.
        
        @param index index of the current tab
        """
        if index > -1:
            cb = self.currentBrowser()
            if cb is not None:
                self.__setForwardAvailable(cb.isForwardAvailable())
                self.__setBackwardAvailable(cb.isBackwardAvailable())
                self.__setLoadingActions(cb.isLoading())
                
                url = cb.source().toString()
                index2 = self.pathCombo.findText(url)
                if index2 > -1:
                    self.pathCombo.setCurrentIndex(index2)
                else:
                    self.pathCombo.clearEditText()
                
                self.__setPathComboBackground()
                
                self.printAct.setEnabled(hasattr(cb, 'print_'))
                if self.printPreviewAct:
                    self.printPreviewAct.setEnabled(hasattr(cb, 'print_'))
                
                self.iconChanged(cb.icon())
    
    def __showContextMenu(self, coord, index):
        """
        Private slot to show the tab context menu.
        
        @param coord the position of the mouse pointer (QPoint)
        @param index index of the tab the menu is requested for (integer)
        """
        self.tabContextMenuIndex = index
        self.leftMenuAct.setEnabled(index > 0)
        self.rightMenuAct.setEnabled(index < self.tabWidget.count() - 1)
        
        self.tabContextCloseOthersAct.setEnabled(self.tabWidget.count() > 1)
        
        coord = self.tabWidget.mapToGlobal(coord)
        self.__tabContextMenu.popup(coord)
    
    def __tabContextMenuMoveLeft(self):
        """
        Private method to move a tab one position to the left.
        """
        self.tabWidget.moveTab(self.tabContextMenuIndex, self.tabContextMenuIndex - 1)
    
    def __tabContextMenuMoveRight(self):
        """
        Private method to move a tab one position to the right.
        """
        self.tabWidget.moveTab(self.tabContextMenuIndex, self.tabContextMenuIndex + 1)
    
    def __tabContextMenuClone(self):
        """
        Private method to clone the selected tab.
        """
        idx = self.tabContextMenuIndex
        if idx < 0:
            idx = self.tabWidget.currentIndex()
        if idx < 0 or idx > self.tabWidget.count():
            return
        
        self.newTab(self.tabWidget.widget(idx).url())
    
    def __tabContextMenuClose(self):
        """
        Private method to close the selected tab.
        """
        self.__closeAt(self.tabContextMenuIndex)
    
    def __tabContextMenuCloseOthers(self):
        """
        Private slot to close all other tabs.
        """
        index = self.tabContextMenuIndex
        for i in range(self.tabWidget.count() - 1, index, -1) + range(index - 1, -1, -1):
            self.__closeAt(i)
    
    def __tabContextMenuPrint(self):
        """
        Private method to print the selected tab.
        """
        browser = self.tabWidget.widget(self.tabContextMenuIndex)
        self.__printFile(browser)
        
    def __tabContextMenuPrintPreview(self):
        """
        Private method to show a print preview of the selected tab.
        """
        browser = self.tabWidget.widget(self.tabContextMenuIndex)
        self.__printPreviewFile(browser)
    
    def __showPreferences(self):
        """
        Private slot to set the preferences.
        """
        dlg = ConfigurationDialog(self, 'Configuration', True, 
                                  fromEric = self.fromEric, 
                                  helpBrowserMode = True)
        self.connect(dlg, SIGNAL('preferencesChanged'), 
                     self.preferencesChanged)
        dlg.show()
        dlg.showConfigurationPageByName("empty")
        dlg.exec_()
        QApplication.processEvents()
        if dlg.result() == QDialog.Accepted:
            dlg.setPreferences()
            Preferences.syncPreferences()
            self.preferencesChanged()
    
    def preferencesChanged(self):
        """
        Public slot to handle a change of preferences.
        """
        self.__setPathComboBackground()
        
        self.__initWebSettings()
        
        self.networkAccessManager().preferencesChanged()
        
        self.historyManager().preferencesChanged()
        
        for index in range(self.tabWidget.count()):
            self.tabWidget.widget(index).preferencesChanged()
        
        self.searchEdit.preferencesChanged()
    
    def __showAcceptedLanguages(self):
        """
        Private slot to configure the accepted languages for web pages.
        """
        dlg = HelpLanguagesDialog(self)
        dlg.exec_()
        self.networkAccessManager().languagesChanged()
    
    def __showCookiesConfiguration(self):
        """
        Private slot to configure the cookies handling.
        """
        dlg = CookiesConfigurationDialog(self)
        dlg.exec_()
    
    def setLoading(self, widget):
        """
        Public method to set the loading icon.
        
        @param widget reference to the widget to set the icon for (QWidget)
        """
        index = self.tabWidget.indexOf(widget)
        anim = self.tabWidget.animationLabel(
            index, os.path.join(getConfig("ericPixDir"), "loading.gif"))
        if not anim:
            loading = QIcon(os.path.join(getConfig("ericPixDir"), "loading.gif"))
            self.tabWidget.setTabIcon(index, loading)
        self.statusBar().showMessage(self.trUtf8("Loading..."))
        
        self.__setLoadingActions(True)
    
    def resetLoading(self, widget):
        """
        Public method to reset the loading icon.
        
        @param widget reference to the widget to reset the icon for (QWidget)
        """
        index = self.tabWidget.indexOf(widget)
        self.tabWidget.resetAnimation(index)
        self.tabWidget.setTabIcon(index, widget.icon())
        self.statusBar().showMessage(self.trUtf8("Finished loading"))
        
        self.__setLoadingActions(False)
    
    ############################################################################
    ## Methods to support Webkit based browser below.
    ############################################################################
    
    def progressBar(self):
        """
        Public method to get a reference to the load progress bar.
        
        @return reference to the load progress bar (QProgressBar)
        """
        if self.__progressBar is None:
            self.__progressBar = QProgressBar()
            self.statusBar().addPermanentWidget(self.__progressBar)
            self.__progressBar.setMaximumWidth(100)
            self.__progressBar.setFixedHeight(16)
            self.__progressBar.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
            self.__progressBar.hide()
        
        return self.__progressBar
        
    @classmethod
    def helpEngine(cls):
        """
        Class method to get a reference to the help engine.
        
        @return reference to the help engine (QHelpEngine)
        """
        if cls._helpEngine is None:
            cls._helpEngine = \
                QHelpEngine(os.path.join(Utilities.getConfigDir(), 
                                         "browser", "eric4help.qhc"))
        return cls._helpEngine
        
    @classmethod
    def networkAccessManager(cls):
        """
        Class method to get a reference to the network access manager.
        
        @return reference to the network access manager (NetworkAccessManager)
        """
        if cls._networkAccessManager is None:
            cls._networkAccessManager = \
                NetworkAccessManager(cls.helpEngine())
            cls._cookieJar = CookieJar()
            cls._networkAccessManager.setCookieJar(cls._cookieJar)
        
        return cls._networkAccessManager
        
    @classmethod
    def cookieJar(cls):
        """
        Class method to get a reference to the cookie jar.
        
        @return reference to the cookie jar (CookieJar)
        """
        return cls.networkAccessManager().cookieJar()
        
    def iconChanged(self, icon):
        """
        Public slot to change the icon shown to the left of the URL entry.
        
        @param icon icon to be shown (QIcon)
        """
        self.tabWidget.setTabIcon(self.tabWidget.currentIndex(), icon)
        self.iconLabel.setPixmap(icon.pixmap(16, 16))
        
    def __clearIconsDatabase(self):
        """
        Private slot to clear the icons databse.
        """
        QWebSettings.clearIconDatabase()
        
    @pyqtSignature("QUrl")
    def __linkActivated(self, url):
        """
        Private slot to handle the selection of a link in the TOC window.
        
        @param url URL to be shown (QUrl)
        """
        self.currentBrowser().setSource(url)
        
    def __linksActivated(self, links, keyword):
        """
        Private slot to select a topic to be shown.
        
        @param links dictionary with help topic as key (QString) and
            URL as value (QUrl)
        @param keyword keyword for the link set (QString)
        """
        dlg = HelpTopicDialog(self, keyword, links)
        if dlg.exec_() == QDialog.Accepted:
            self.currentBrowser().setSource(dlg.link())
    
    def __activateCurrentBrowser(self):
        """
        Private slot to activate the current browser.
        """
        self.currentBrowser().setFocus()
        
    def __syncTOC(self):
        """
        Private slot to synchronize the TOC with the currently shown page.
        """
        QApplication.setOverrideCursor(Qt.WaitCursor)
        url = self.currentBrowser().source()
        self.__showTocWindow()
        if not self.__tocWindow.syncToContent(url):
            self.statusBar().showMessage(
                self.trUtf8("Could not find an associated content."), 5000)
        QApplication.restoreOverrideCursor()
        
    def __showTocWindow(self):
        """
        Private method to show the table of contents window.
        """
        self.__activateDock(self.__tocWindow)
        
    def __hideTocWindow(self):
        """
        Private method to hide the table of contents window.
        """
        self.__tocDock.hide()
        
    def __showIndexWindow(self):
        """
        Private method to show the index window.
        """
        self.__activateDock(self.__indexWindow)
        
    def __hideIndexWindow(self):
        """
        Private method to hide the index window.
        """
        self.__indexDock.hide()
        
    def __showSearchWindow(self):
        """
        Private method to show the search window.
        """
        self.__activateDock(self.__searchWindow)
        
    def __hideSearchWindow(self):
        """
        Private method to hide the search window.
        """
        self.__searchDock.hide()
        
    def __activateDock(self, widget):
        """
        Private method to activate the dock widget of the given widget.
        
        @param widget reference to the widget to be activated (QWidget)
        """
        widget.parent().show()
        widget.parent().raise_()
        widget.setFocus()
        
    def __setupFilterCombo(self):
        """
        Private slot to setup the filter combo box.
        """
        curFilter = self.filterCombo.currentText()
        if curFilter.isEmpty():
            curFilter = self.__helpEngine.currentFilter()
        self.filterCombo.clear()
        self.filterCombo.addItems(self.__helpEngine.customFilters())
        idx = self.filterCombo.findText(curFilter)
        if idx < 0:
            idx = 0
        self.filterCombo.setCurrentIndex(idx)
        
    def __filterQtHelpDocumentation(self, customFilter):
        """
        Private slot to filter the QtHelp documentation.
        
        @param customFilter name of filter to be applied (QString)
        """
        self.__helpEngine.setCurrentFilter(customFilter)
        
    def __manageQtHelpDocumentation(self):
        """
        Private slot to manage the QtHelp documentation database.
        """
        dlg = QtHelpDocumentationDialog(self.__helpEngine, self)
        dlg.exec_()
        if dlg.hasChanges():
            for i in sorted(dlg.getTabsToClose(), reverse = True):
                self.__closeAt(i)
            self.__helpEngine.setupData()
        
    def getSourceFileList(self):
        """
        Public method to get a list of all opened source files.
        
        @return dictionary with tab id as key and host/namespace as value
        """
        sourceList = {}
        for i in range(self.tabWidget.count()):
            viewer = self.tabWidget.widget(i)
            if viewer is not None and \
               viewer.source().isValid():
                sourceList[i] = viewer.source().host()
        
        return sourceList
        
    def __manageQtHelpFilters(self):
        """
        Private slot to manage the QtHelp filters.
        """
        dlg = QtHelpFiltersDialog(self.__helpEngine, self)
        dlg.exec_()
        
    def __indexingStarted(self):
        """
        Private slot to handle the start of the indexing process.
        """
        self.__indexing = True
        if self.__indexingProgress is None:
            self.__indexingProgress = QWidget()
            layout = QHBoxLayout(self.__indexingProgress)
            layout.setMargin(0)
            sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
            
            label = QLabel(self.trUtf8("Updating search index"))
            label.setSizePolicy(sizePolicy)
            layout.addWidget(label)
            
            progressBar = QProgressBar()
            progressBar.setRange(0, 0)
            progressBar.setTextVisible(False)
            progressBar.setFixedHeight(16)
            progressBar.setSizePolicy(sizePolicy)
            layout.addWidget(progressBar)
            
            self.statusBar().addPermanentWidget(self.__indexingProgress)
        
    def __indexingFinished(self):
        """
        Private slot to handle the start of the indexing process.
        """
        self.statusBar().removeWidget(self.__indexingProgress)
        self.__indexingProgress = None
        self.__indexing = False
        if self.__searchWord is not None:
            self.__searchForWord()
        
    def __searchForWord(self):
        """
        Private slot to search for a word.
        """
        if not self.__indexing and self.__searchWord is not None:
            self.__searchDock.show()
            self.__searchDock.raise_()
            query = QHelpSearchQuery(QHelpSearchQuery.DEFAULT, [self.__searchWord])
            self.__searchEngine.search([query])
            self.__searchWord = None
        
    def search(self, word):
        """
        Public method to search for a word.
        
        @param word word to search for (string or QString)
        """
        self.__searchWord = word
        self.__searchForWord()
        
    def __lookForNewDocumentation(self):
        """
        Private slot to look for new documentation to be loaded into the
        help database.
        """
        self.__helpInstaller = HelpDocsInstaller(self.__helpEngine.collectionFile())
        self.connect(self.__helpInstaller, SIGNAL("errorMessage(const QString&)"), 
                     self.__showInstallationError)
        self.connect(self.__helpInstaller, SIGNAL("docsInstalled(bool)"), 
                     self.__docsInstalled)
        
        self.statusBar().showMessage(self.trUtf8("Looking for Documentation..."))
        self.__helpInstaller.installDocs()
        
    def __showInstallationError(self, message):
        """
        Private slot to show installation errors.
        
        @param message message to be shown (QString)
        """
        KQMessageBox.warning(self,
            self.trUtf8("eric4 Web Browser"),
            message)
        
    def __docsInstalled(self, installed):
        """
        Private slot handling the end of documentation installation.
        
        @param installed flag indicating that documents were installed (boolean)
        """
        if installed:
            self.__helpEngine.setupData()
        self.statusBar().clearMessage()
        
    def __initHelpDb(self):
        """
        Private slot to initialize the documentation database.
        """
        if not self.__helpEngine.setupData():
            return
        
        unfiltered = self.trUtf8("Unfiltered")
        if unfiltered not in self.__helpEngine.customFilters():
            hc = QHelpEngineCore(self.__helpEngine.collectionFile())
            hc.setupData()
            hc.addCustomFilter(unfiltered, QStringList())
            hc = None
            del hc
            
            self.__helpEngine.blockSignals(True)
            self.__helpEngine.setCurrentFilter(unfiltered)
            self.__helpEngine.blockSignals(False)
            self.__helpEngine.setupData()
        
    def __warning(self, msg):
        """
        Private slot handling warnings from the help engine.
        
        @param msg message sent by the help  engine (QString)
        """
        KQMessageBox.warning(self,
            self.trUtf8("Help Engine"), msg)
        
    def __showNavigationMenu(self):
        """
        Private slot to show the navigation button menu.
        """
        self.__navigationMenu.clear()
        for index in range(self.tabWidget.count()):
            act = self.__navigationMenu.addAction(self.tabWidget.tabIcon(index), 
                                              self.tabWidget.tabText(index))
            act.setData(QVariant(index))
        
    def __navigationMenuTriggered(self, act):
        """
        Private slot called to handle the navigation button menu selection.
        
        @param act reference to the selected action (QAction)
        """
        index, ok = act.data().toInt()
        if ok:
            self.tabWidget.setCurrentIndex(index)
        
    def __showBackMenu(self):
        """
        Private slot showing the backwards navigation menu.
        """
        self.backMenu.clear()
        history = self.currentBrowser().history()
        historyCount = history.count()
        backItems = history.backItems(historyCount)
        for index in range(len(backItems) - 1, -1, -1):
            item = backItems[index]
            act = QAction(self)
            act.setData(QVariant(-1 * (index + 1)))
            icon = HelpWindow.__getWebIcon(item.url())
            act.setIcon(icon)
            act.setText(item.title())
            self.backMenu.addAction(act)
        
    def __showForwardMenu(self):
        """
        Private slot showing the forwards navigation menu.
        """
        self.forwardMenu.clear()
        history = self.currentBrowser().history()
        historyCount = history.count()
        forwardItems = history.forwardItems(historyCount)
        for index in range(len(forwardItems)):
            item = forwardItems[index]
            act = QAction(self)
            act.setData(QVariant(index + 1))
            icon = HelpWindow.__getWebIcon(item.url())
            act.setIcon(icon)
            act.setText(item.title())
            self.forwardMenu.addAction(act)
        
    def __navigationMenuActionTriggered(self, act):
        """
        Private slot to go to the selected page.
        
        @param act reference to the action selected in the navigation menu (QAction)
        """
        offset = act.data().toInt()[0]
        history = self.currentBrowser().history()
        historyCount = history.count()
        if offset < 0:
            # go back
            history.goToItem(history.backItems(historyCount)[-1 * offset - 1])
        else:
            # go forward
            history.goToItem(history.forwardItems(historyCount)[offset - 1])
        
    def __clearPrivateData(self):
        """
        Private slot to clear the private data.
        """
        dlg = HelpClearPrivateDataDialog(self)
        if dlg.exec_() == QDialog.Accepted:
            history, searches, favicons, cache, cookies, passwords = dlg.getData()
            # browsing history, search history, favicons, disk cache, cookies, passwords
            if history:
                self.historyManager().clear()
            if searches:
                self.searchEdit.clear()
            if favicons:
                self.__clearIconsDatabase()
            if cache:
                try:
                    self.networkAccessManager().cache().clear()
                except AttributeError:
                    pass
            if cookies:
                self.cookieJar().clear()
            if passwords:
                self.passwordManager().clear()
        
    def __showEnginesConfigurationDialog(self):
        """
        Private slot to show the search engines configuration dialog.
        """
        from OpenSearch.OpenSearchDialog import OpenSearchDialog
        
        dlg = OpenSearchDialog(self)
        dlg.exec_()
        
    def searchEnginesAction(self):
        """
        Public method to get a reference to the search engines configuration action.
        
        @return reference to the search engines configuration action (QAction)
        """
        return self.searchEnginesAct
        
    def __showPasswordsDialog(self):
        """
        Private slot to show the passwords management dialog.
        """
        from Passwords.PasswordsDialog import PasswordsDialog
        
        dlg = PasswordsDialog(self)
        dlg.exec_()
        
    def __showAdBlockDialog(self):
        """
        Private slot to show the AdBlock configuration dialog.
        """
        self.adblockManager().showDialog()
        
    def __showNetworkMonitor(self):
        """
        Private slot to show the network monitor dialog.
        """
        monitor = E4NetworkMonitor.instance(self.networkAccessManager())
        monitor.show()
        
    def __closeNetworkMonitor(self):
        """
        Private slot to close the network monitor dialog.
        """
        E4NetworkMonitor.closeMonitor()
        
    def __showPageSource(self):
        """
        Private slot to show the source of the current page in  an editor.
        """
        from QScintilla.MiniEditor import MiniEditor
        src = self.currentBrowser().page().mainFrame().toHtml()
        editor = MiniEditor(parent = self)
        editor.setText(src, "Html")
        editor.setLanguage("dummy.html")
        editor.show()
        
    @classmethod
    def icon(cls, url):
        """
        Class method to get the icon for an URL.
        
        @param url URL to get icon for (QUrl)
        @return icon for the URL (QIcon)
        """
        icon = HelpWindow.__getWebIcon(url)
        
        if icon.isNull():
            pixmap = QWebSettings.webGraphic(QWebSettings.DefaultFrameIconGraphic)
            if pixmap.isNull():
                pixmap = UI.PixmapCache.getPixmap("defaultIcon.png")
                QWebSettings.setWebGraphic(QWebSettings.DefaultFrameIconGraphic, pixmap)
            return QIcon(pixmap)
        
        return icon

    @staticmethod
    def __getWebIcon(url):
        """
        Private static method to fetch the icon for a URL.
        
        @param url URL to get icon for (QUrl)
        @return icon for the URL (QIcon)
        """
        icon = QWebSettings.iconForUrl(url)
        if icon.isNull():
            # try again
            QThread.usleep(10)
            icon = QWebSettings.iconForUrl(url)
        if not icon.isNull():
            icon = QIcon(icon.pixmap(22, 22))
        return icon
        
    @classmethod
    def bookmarksManager(cls):
        """
        Class method to get a reference to the bookmarks manager.
        
        @return reference to the bookmarks manager (BookmarksManager)
        """
        if cls._bookmarksManager is None:
            cls._bookmarksManager = BookmarksManager()
        
        return cls._bookmarksManager
        
    def __openUrl(self, url, title):
        """
        Private slot to load a URL from the bookmarks menu or bookmarks toolbar
        in the current tab.
        
        @param url url to be opened (QUrl)
        @param title title of the bookmark (QString)
        """
        self.__linkActivated(url)
        
    def __openUrlNewTab(self, url, title):
        """
        Private slot to load a URL from the bookmarks menu or bookmarks toolbar 
        in a new tab.
        
        @param url url to be opened (QUrl)
        @param title title of the bookmark (QString)
        """
        self.newTab(url)
        
    @classmethod
    def historyManager(cls):
        """
        Class method to get a reference to the history manager.
        
        @return reference to the history manager (HistoryManager)
        """
        if cls._historyManager is None:
            cls._historyManager = HistoryManager()
        
        return cls._historyManager
        
    @classmethod
    def passwordManager(cls):
        """
        Class method to get a reference to the password manager.
        
        @return reference to the password manager (PasswordManager)
        """
        if cls._passwordManager is None:
            cls._passwordManager = PasswordManager()
        
        return cls._passwordManager
        
    @classmethod
    def adblockManager(cls):
        """
        Class method to get a reference to the AdBlock manager.
        
        @return reference to the AdBlock manager (AdBlockManager)
        """
        if cls._adblockManager is None:
            cls._adblockManager = AdBlockManager()
        
        return cls._adblockManager
