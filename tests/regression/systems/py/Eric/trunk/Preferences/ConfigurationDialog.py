# -*- coding: utf-8 -*-

# Copyright (c) 2002 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a dialog for the configuration of eric4.
"""

import os
import types

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from KdeQt import KQMessageBox
from KdeQt.KQMainWindow import KQMainWindow
from KdeQt.KQApplication import e4App

import QScintilla.Lexers

import Preferences

from PreferencesLexer import PreferencesLexer, PreferencesLexerLanguageError
import UI.PixmapCache

from eric4config import getConfig

class ConfigurationPageItem(QTreeWidgetItem):
    """
    Class implementing a QTreeWidgetItem holding the configuration page data.
    """
    def __init__(self, parent, text, pageName, iconFile):
        """
        Constructor
        
        @param parent parent widget of the item (QTreeWidget or QTreeWidgetItem)
        @param text text to be displayed (string or QString)
        @param pageName name of the configuration page (string or QString)
        @param iconFile file name of the icon to be shown (string)
        """
        QTreeWidgetItem.__init__(self, parent, QStringList(text))
        self.setIcon(0, UI.PixmapCache.getIcon(iconFile))
        
        self.__pageName = unicode(pageName)
        
    def getPageName(self):
        """
        Public method to get the name of the associated configuration page.
        
        @return name of the configuration page (string)
        """
        return self.__pageName

class ConfigurationWidget(QWidget):
    """
    Class implementing a dialog for the configuration of eric4.
    
    @signal preferencesChanged emitted after settings have been changed
    """
    def __init__(self, parent = None, fromEric = True, helpBrowserMode = False):
        """
        Constructor
        
        @param parent The parent widget of this dialog. (QWidget)
        @keyparam fromEric flag indicating a dialog generation from within the 
            eric4 ide (boolean)
        @keyparam helpBrowserMode flag indicating to show only help pages
            for entries related to the help browser (boolean)
        """
        QWidget.__init__(self, parent)
        self.fromEric = fromEric
        self.helpBrowserMode = helpBrowserMode
        
        self.__setupUi()
        
        self.itmDict = {}
        
        if not fromEric:
            from PluginManager.PluginManager import PluginManager
            try:
                self.pluginManager = e4App().getObject("PluginManager")
            except KeyError:
                self.pluginManager = PluginManager(self)
                e4App().registerObject("PluginManager", self.pluginManager)
        
        if not helpBrowserMode:
            self.configItems = {
                # key : [display string, pixmap name, dialog module name or 
                #        page creation function, parent key,
                #        reference to configuration page (must always be last)]
                # The dialog module must have the module function create to create
                # the configuration page. This must have the method save to save 
                # the settings.
                "applicationPage" : \
                    [self.trUtf8("Application"), "preferences-application.png",
                     "ApplicationPage", None, None],
                "corbaPage" : \
                    [self.trUtf8("CORBA"), "preferences-orbit.png",
                    "CorbaPage", None, None],
                "emailPage" : \
                    [self.trUtf8("Email"), "preferences-mail_generic.png",
                    "EmailPage", None, None],
                "graphicsPage" : \
                    [self.trUtf8("Graphics"), "preferences-graphics.png",
                    "GraphicsPage", None, None],
                "iconsPage" : \
                    [self.trUtf8("Icons"), "preferences-icons.png",
                    "IconsPage", None, None],
                "networkPage" : \
                    [self.trUtf8("Network"), "preferences-network.png", 
                    "NetworkPage", None, None], 
                "pluginManagerPage" : \
                    [self.trUtf8("Plugin Manager"), "preferences-pluginmanager.png",
                    "PluginManagerPage", None, None],
                "printerPage" : \
                    [self.trUtf8("Printer"), "preferences-printer.png",
                    "PrinterPage", None, None],
                "pythonPage" : \
                    [self.trUtf8("Python"), "preferences-python.png",
                    "PythonPage", None, None],
                "qtPage" : \
                    [self.trUtf8("Qt"), "preferences-qtlogo.png",
                    "QtPage", None, None],
                "shellPage" : \
                    [self.trUtf8("Shell"), "preferences-shell.png",
                    "ShellPage", None, None],
                "tasksPage" : \
                    [self.trUtf8("Tasks"), "task.png",
                    "TasksPage", None, None],
                "templatesPage" : \
                    [self.trUtf8("Templates"), "preferences-template.png",
                    "TemplatesPage", None, None],
                "terminalPage" : \
                    [self.trUtf8("Terminal"), "terminal.png",
                    "TerminalPage", None, None],
                "vcsPage" : \
                    [self.trUtf8("Version Control Systems"), "preferences-vcs.png",
                    "VcsPage", None, None],
                
                "0debuggerPage": \
                    [self.trUtf8("Debugger"), "preferences-debugger.png",
                    None, None, None],
                "debuggerGeneralPage" : \
                    [self.trUtf8("General"), "preferences-debugger.png",
                    "DebuggerGeneralPage", "0debuggerPage", None],
                "debuggerPythonPage" : \
                    [self.trUtf8("Python"), "preferences-pyDebugger.png",
                    "DebuggerPythonPage", "0debuggerPage", None],
                "debuggerPython3Page" : \
                    [self.trUtf8("Python3"), "preferences-pyDebugger.png",
                    "DebuggerPython3Page", "0debuggerPage", None],
                "debuggerRubyPage" : \
                    [self.trUtf8("Ruby"), "preferences-rbDebugger.png",
                    "DebuggerRubyPage", "0debuggerPage", None],
                
                "0editorPage" : \
                    [self.trUtf8("Editor"), "preferences-editor.png",
                    None, None, None],
                "editorAPIsPage" : \
                    [self.trUtf8("APIs"), "preferences-api.png",
                    "EditorAPIsPage", "0editorPage", None],
                "editorAutocompletionPage" : \
                    [self.trUtf8("Autocompletion"), "preferences-autocompletion.png",
                    "EditorAutocompletionPage", "0editorPage", None],
                "editorAutocompletionQScintillaPage" : \
                    [self.trUtf8("QScintilla"), "qscintilla.png",
                    "EditorAutocompletionQScintillaPage", 
                    "editorAutocompletionPage", None],
                "editorCalltipsPage" : \
                    [self.trUtf8("Calltips"), "preferences-calltips.png",
                    "EditorCalltipsPage", "0editorPage", None],
                "editorCalltipsQScintillaPage" : \
                    [self.trUtf8("QScintilla"), "qscintilla.png",
                    "EditorCalltipsQScintillaPage", "editorCalltipsPage", None],
                "editorGeneralPage" : \
                    [self.trUtf8("General"), "preferences-general.png",
                    "EditorGeneralPage", "0editorPage", None],
                "editorFilePage" : \
                    [self.trUtf8("Filehandling"), "preferences-filehandling.png",
                    "EditorFilePage", "0editorPage", None],
                "editorSearchPage" : \
                    [self.trUtf8("Searching"), "preferences-search.png",
                    "EditorSearchPage", "0editorPage", None],
                "editorSpellCheckingPage" : \
                    [self.trUtf8("Spell checking"), "preferences-spellchecking.png", 
                    "EditorSpellCheckingPage", "0editorPage", None],
                "editorStylesPage" : \
                    [self.trUtf8("Style"), "preferences-styles.png",
                    "EditorStylesPage", "0editorPage", None],
                "editorTypingPage" : \
                    [self.trUtf8("Typing"), "preferences-typing.png",
                    "EditorTypingPage", "0editorPage", None],
                "editorExportersPage" : \
                    [self.trUtf8("Exporters"), "preferences-exporters.png",
                    "EditorExportersPage", "0editorPage", None],
                
                "1editorLexerPage" : \
                    [self.trUtf8("Highlighters"), "preferences-highlighting-styles.png",
                    None, "0editorPage", None],
                "editorHighlightersPage" : \
                    [self.trUtf8("Filetype Associations"), 
                    "preferences-highlighter-association.png",
                    "EditorHighlightersPage", "1editorLexerPage", None],
                "editorHighlightingStylesPage" : \
                    [self.trUtf8("Styles"), 
                    "preferences-highlighting-styles.png",
                    "EditorHighlightingStylesPage", "1editorLexerPage", None],
                "editorPropertiesPage" : \
                    [self.trUtf8("Properties"), "preferences-properties.png",
                    "EditorPropertiesPage", "1editorLexerPage", None],
                
                "0helpPage" : \
                    [self.trUtf8("Help"), "preferences-help.png",
                    None, None, None],
                "helpAppearancePage" : \
                    [self.trUtf8("Appearance"), "preferences-styles.png",
                    "HelpAppearancePage", "0helpPage", None], 
                "helpDocumentationPage" : \
                    [self.trUtf8("Help Documentation"), 
                    "preferences-helpdocumentation.png",
                    "HelpDocumentationPage", "0helpPage", None],
                "helpViewersPage" : \
                    [self.trUtf8("Help Viewers"), "preferences-helpviewers.png",
                    "HelpViewersPage", "0helpPage", None],
                "helpWebBrowserPage" : \
                    [self.trUtf8("Eric Web Browser"), "ericWeb.png",
                    "HelpWebBrowserPage", "0helpPage", None],
                
                "0projectPage" : \
                    [self.trUtf8("Project"), "preferences-project.png",
                    None, None, None],
                "projectBrowserPage" : \
                    [self.trUtf8("Project Viewer"), "preferences-project.png",
                    "ProjectBrowserPage", "0projectPage", None],
                "projectPage" : \
                    [self.trUtf8("Project"), "preferences-project.png",
                    "ProjectPage", "0projectPage", None],
                "multiProjectPage" : \
                    [self.trUtf8("Multiproject"), "preferences-multiproject.png",
                    "MultiProjectPage", "0projectPage", None],
                
                "0interfacePage" : \
                    [self.trUtf8("Interface"), "preferences-interface.png",
                    None, None, None], 
                "interfacePage" : \
                    [self.trUtf8("Interface"), "preferences-interface.png",
                    "InterfacePage", "0interfacePage", None],
                "viewmanagerPage" : \
                    [self.trUtf8("Viewmanager"), "preferences-viewmanager.png",
                    "ViewmanagerPage", "0interfacePage", None],
            }
            
            self.configItems.update(
                e4App().getObject("PluginManager").getPluginConfigData())
        else:
            self.configItems = {
                # key : [display string, pixmap name, dialog module name or 
                #        page creation function, parent key,
                #        reference to configuration page (must always be last)]
                # The dialog module must have the module function create to create
                # the configuration page. This must have the method save to save 
                # the settings.
                "networkPage" : \
                    [self.trUtf8("Network"), "preferences-network.png", 
                     "NetworkPage", None, None], 
                "pythonPage" : \
                    [self.trUtf8("Python"), "preferences-python.png",
                    "PythonPage", None, None],
                
                "0helpPage" : \
                    [self.trUtf8("Help"), "preferences-help.png",
                    None, None, None],
                "helpAppearancePage" : \
                    [self.trUtf8("Appearance"), "preferences-styles.png",
                    "HelpAppearancePage", "0helpPage", None], 
                "helpDocumentationPage" : \
                    [self.trUtf8("Help Documentation"), 
                    "preferences-helpdocumentation.png",
                    "HelpDocumentationPage", "0helpPage", None],
                "helpViewersPage" : \
                    [self.trUtf8("Help Viewers"), "preferences-helpviewers.png",
                    "HelpViewersPage", "0helpPage", None],
                "helpWebBrowserPage" : \
                    [self.trUtf8("Eric Web Browser"), "ericWeb.png",
                    "HelpWebBrowserPage", "0helpPage", None],
            }
        
        # generate the list entries
        itemsToExpand = []
        keys = self.configItems.keys()
        keys.sort()
        for key in keys:
            pageData = self.configItems[key]
            if pageData[3]:
                pitm = self.itmDict[pageData[3]] # get the parent item
            else:
                pitm = self.configList
            self.itmDict[key] = ConfigurationPageItem(pitm, pageData[0], key, pageData[1])
            self.itmDict[key].setExpanded(True)
        self.configList.sortByColumn(0, Qt.AscendingOrder)
        
        # set the initial size of the splitter
        self.configSplitter.setSizes([200, 600])
        
        self.connect(self.configList, SIGNAL("itemActivated(QTreeWidgetItem *, int)"),
            self.__showConfigurationPage)
        self.connect(self.configList, SIGNAL("itemClicked(QTreeWidgetItem *, int)"),
            self.__showConfigurationPage)
        
        self.__initLexers()
        
    def __setupUi(self):
        """
        Private method to perform the general setup of the configuration widget.
        """
        self.setObjectName("ConfigurationDialog")
        self.resize(900, 650)
        self.setProperty("sizeGripEnabled", QVariant(True))
        self.verticalLayout_2 = QVBoxLayout(self)
        self.verticalLayout_2.setSpacing(6)
        self.verticalLayout_2.setMargin(6)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        
        self.configSplitter = QSplitter(self)
        self.configSplitter.setOrientation(Qt.Horizontal)
        self.configSplitter.setObjectName("configSplitter")
        
        self.configList = QTreeWidget(self.configSplitter)
        self.configList.setObjectName("configList")
        
        self.scrollArea = QScrollArea(self.configSplitter)
        self.scrollArea.setFrameShape(QFrame.NoFrame)
        self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scrollArea.setWidgetResizable(False)
        self.scrollArea.setObjectName("scrollArea")
        
        self.configStack = QStackedWidget()
        self.configStack.setFrameShape(QFrame.Box)
        self.configStack.setFrameShadow(QFrame.Sunken)
        self.configStack.setObjectName("configStack")
        self.scrollArea.setWidget(self.configStack)
        
        self.emptyPage = QWidget()
        self.emptyPage.setGeometry(QRect(0, 0, 372, 591))
        self.emptyPage.setObjectName("emptyPage")
        self.vboxlayout = QVBoxLayout(self.emptyPage)
        self.vboxlayout.setSpacing(6)
        self.vboxlayout.setMargin(6)
        self.vboxlayout.setObjectName("vboxlayout")
        spacerItem = QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.vboxlayout.addItem(spacerItem)
        self.emptyPagePixmap = QLabel(self.emptyPage)
        self.emptyPagePixmap.setAlignment(Qt.AlignCenter)
        self.emptyPagePixmap.setObjectName("emptyPagePixmap")
        self.emptyPagePixmap.setPixmap(
            QPixmap(os.path.join(getConfig('ericPixDir'), 'eric.png')))
        self.vboxlayout.addWidget(self.emptyPagePixmap)
        self.textLabel1 = QLabel(self.emptyPage)
        self.textLabel1.setAlignment(Qt.AlignCenter)
        self.textLabel1.setObjectName("textLabel1")
        self.vboxlayout.addWidget(self.textLabel1)
        spacerItem1 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.vboxlayout.addItem(spacerItem1)
        self.configStack.addWidget(self.emptyPage)
        
        self.verticalLayout_2.addWidget(self.configSplitter)
        
        self.buttonBox = QDialogButtonBox(self)
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(
            QDialogButtonBox.Apply | QDialogButtonBox.Cancel | \
            QDialogButtonBox.Ok | QDialogButtonBox.Reset)
        self.buttonBox.setObjectName("buttonBox")
        if not self.fromEric and not self.helpBrowserMode:
            self.buttonBox.button(QDialogButtonBox.Apply).hide()
        self.buttonBox.button(QDialogButtonBox.Apply).setEnabled(False)
        self.buttonBox.button(QDialogButtonBox.Reset).setEnabled(False)
        self.verticalLayout_2.addWidget(self.buttonBox)

        self.setWindowTitle(self.trUtf8("Preferences"))
        
        self.configList.header().hide()
        self.configList.header().setSortIndicator(0, Qt.AscendingOrder)
        self.configList.setSortingEnabled(True)
        self.textLabel1.setText(self.trUtf8("Please select an entry of the list \n"
            "to display the configuration page."))
        
        QMetaObject.connectSlotsByName(self)
        self.setTabOrder(self.configList, self.configStack)
        
        self.configStack.setCurrentWidget(self.emptyPage)
    
    def __initLexers(self):
        """
        Private method to initialize the dictionary of preferences lexers.
        """
        self.lexers = {}
        for language in QScintilla.Lexers.getSupportedLanguages().keys():
            try:
                self.lexers[language] = PreferencesLexer(language, self)
            except PreferencesLexerLanguageError:
                pass
        
    def __importConfigurationPage(self, name):
        """
        Private method to import a configuration page module.
        
        @param name name of the configuration page module (string)
        @return reference to the configuration page module
        """
        modName = "Preferences.ConfigurationPages.%s" % name
        try:
            mod = __import__(modName)
            components = modName.split('.')
            for comp in components[1:]:
                mod = getattr(mod, comp)
            return mod
        except ImportError:
            KQMessageBox.critical(None,
                self.trUtf8("Configuration Page Error"),
                self.trUtf8("""<p>The configuration page <b>%1</b>"""
                            """ could not be loaded.</p>""").arg(name))
            return None
        
    def __showConfigurationPage(self, itm, column):
        """
        Private slot to show a selected configuration page.
        
        @param itm reference to the selected item (QTreeWidgetItem)
        @param column column that was selected (integer) (ignored)
        """
        pageName = itm.getPageName()
        self.showConfigurationPageByName(pageName)
        
    def __initPage(self, pageData):
        """
        Private method to initialize a configuration page.
        
        @param pageData data structure for the page to initialize
        @return reference to the initialized page
        """
        page = None
        if type(pageData[2] ) is types.FunctionType:
            page = pageData[2](self)
        else:
            mod = self.__importConfigurationPage(pageData[2])
            if mod:
                page = mod.create(self)
        if page is not None:
            self.configStack.addWidget(page)
            pageData[-1] = page
        return page
        
    def showConfigurationPageByName(self, pageName):
        """
        Public slot to show a named configuration page.
        
        @param pageName name of the configuration page to show (string or QString)
        """
        if pageName == "empty":
            page = self.emptyPage
        else:
            pageName = unicode(pageName)
            pageData = self.configItems[pageName]
            if pageData[-1] is None and pageData[2] is not None:
                # the page was not loaded yet, create it
                page = self.__initPage(pageData)
            else:
                page = pageData[-1]
            if page is None:
                page = self.emptyPage
        self.configStack.setCurrentWidget(page)
        ssize = self.scrollArea.size()
        if self.scrollArea.horizontalScrollBar():
            ssize.setHeight(
                ssize.height() - self.scrollArea.horizontalScrollBar().height() - 2)
        if self.scrollArea.verticalScrollBar():
            ssize.setWidth(
                ssize.width() - self.scrollArea.verticalScrollBar().width() - 2)
        psize = page.minimumSizeHint()
        self.configStack.resize(max(ssize.width(), psize.width()), 
                                max(ssize.height(), psize.height()))
        
        if page != self.emptyPage:
            page.polishPage()
            self.buttonBox.button(QDialogButtonBox.Apply).setEnabled(True)
            self.buttonBox.button(QDialogButtonBox.Reset).setEnabled(True)
        else:
            self.buttonBox.button(QDialogButtonBox.Apply).setEnabled(False)
            self.buttonBox.button(QDialogButtonBox.Reset).setEnabled(False)
        
        # reset scrollbars
        for sb in [self.scrollArea.horizontalScrollBar(), 
                   self.scrollArea.verticalScrollBar()]:
            if sb:
                sb.setValue(0)
        
    def calledFromEric(self):
        """
        Public method to check, if invoked from within eric.
        
        @return flag indicating invocation from within eric (boolean)
        """
        return self.fromEric
        
    def getPage(self, pageName):
        """
        Public method to get a reference to the named page.
        
        @param pageName name of the configuration page (string)
        @return reference to the page or None, indicating page was
            not loaded yet
        """
        return self.configItems[pageName][-1]
        
    def getLexers(self):
        """
        Public method to get a reference to the lexers dictionary.
        
        @return reference to the lexers dictionary
        """
        return self.lexers
        
    def setPreferences(self):
        """
        Public method called to store the selected values into the preferences storage.
        """
        for key, pageData in self.configItems.items():
            if pageData[-1]:
                pageData[-1].save()
                # page was loaded (and possibly modified)
                QApplication.processEvents()    # ensure HMI is responsive
        
    def on_buttonBox_clicked(self, button):
        """
        Private slot called by a button of the button box clicked.
        
        @param button button that was clicked (QAbstractButton)
        """
        if button == self.buttonBox.button(QDialogButtonBox.Apply):
            self.on_applyButton_clicked()
        elif button == self.buttonBox.button(QDialogButtonBox.Reset):
            self.on_resetButton_clicked()
        
    @pyqtSignature("")
    def on_applyButton_clicked(self):
        """
        Private slot called to apply the settings of the current page.
        """
        if self.configStack.currentWidget() != self.emptyPage:
            page = self.configStack.currentWidget()
            savedState = page.saveState()
            page.save()
            self.emit(SIGNAL('preferencesChanged'))
            if savedState is not None:
                page.setState(savedState)
        
    @pyqtSignature("")
    def on_resetButton_clicked(self):
        """
        Private slot called to reset the settings of the current page.
        """
        if self.configStack.currentWidget() != self.emptyPage:
            currentPage = self.configStack.currentWidget()
            savedState = currentPage.saveState()
            pageName = self.configList.currentItem().getPageName()
            self.configStack.removeWidget(currentPage)
            if pageName == "editorHighlightingStylesPage":
                self.__initLexers()
            pageData = self.configItems[unicode(pageName)]
            pageData[-1] = None
            
            self.showConfigurationPageByName(pageName)
            if savedState is not None:
                self.configStack.currentWidget().setState(savedState)

class ConfigurationDialog(QDialog):
    """
    Class for the dialog variant.
    
    @signal preferencesChanged emitted after settings have been changed
    """
    def __init__(self, parent = None, name = None, modal = False, 
                 fromEric = True, helpBrowserMode = False):
        """
        Constructor
        
        @param parent The parent widget of this dialog. (QWidget)
        @param name The name of this dialog. (QString)
        @param modal Flag indicating a modal dialog. (boolean)
        @keyparam fromEric flag indicating a dialog generation from within the 
            eric4 ide (boolean)
        @keyparam helpBrowserMode flag indicating to show only help pages
            for entries related to the help browser (boolean)
        """
        QDialog.__init__(self, parent)
        if name:
            self.setObjectName(name)
        self.setModal(modal)
        self.layout = QVBoxLayout(self)
        self.layout.setMargin(0)
        self.layout.setSpacing(0)
        
        self.cw = ConfigurationWidget(self, fromEric = fromEric, 
                                      helpBrowserMode = helpBrowserMode)
        size = self.cw.size()
        self.layout.addWidget(self.cw)
        self.resize(size)
        
        self.connect(self.cw.buttonBox, SIGNAL("accepted()"), self.accept)
        self.connect(self.cw.buttonBox, SIGNAL("rejected()"), self.reject)
        self.connect(self.cw, SIGNAL('preferencesChanged'), 
                     self.__preferencesChanged)
        
    def __preferencesChanged(self):
        """
        Private slot to handle a change of the preferences.
        """
        self.emit(SIGNAL('preferencesChanged'))
        
    def showConfigurationPageByName(self, pageName):
        """
        Public slot to show a named configuration page.
        
        @param pageName name of the configuration page to show (string or QString)
        """
        self.cw.showConfigurationPageByName(pageName)
        
    def setPreferences(self):
        """
        Public method called to store the selected values into the preferences storage.
        """
        self.cw.setPreferences()

class ConfigurationWindow(KQMainWindow):
    """
    Main window class for the standalone dialog.
    """
    def __init__(self, parent = None):
        """
        Constructor
        
        @param parent reference to the parent widget (QWidget)
        """
        KQMainWindow.__init__(self, parent)
        
        self.cw = ConfigurationWidget(self, fromEric = False)
        size = self.cw.size()
        self.setCentralWidget(self.cw)
        self.resize(size)
        
        self.connect(self.cw.buttonBox, SIGNAL("accepted()"), self.accept)
        self.connect(self.cw.buttonBox, SIGNAL("rejected()"), self.close)
        
    def showConfigurationPageByName(self, pageName):
        """
        Public slot to show a named configuration page.
        
        @param pageName name of the configuration page to show (string or QString)
        """
        self.cw.showConfigurationPageByName(pageName)
        
    def accept(self):
        """
        Protected slot called by the Ok button. 
        """
        self.cw.setPreferences()
        Preferences.saveResetLayout()
        Preferences.syncPreferences()
        self.close()
