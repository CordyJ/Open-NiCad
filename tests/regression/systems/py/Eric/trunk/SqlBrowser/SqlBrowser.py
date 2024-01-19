# -*- coding: utf-8 -*-

# Copyright (c) 2009 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the SQL Browser main window.
"""

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtSql import QSqlError, QSqlDatabase

from KdeQt.KQMainWindow import KQMainWindow
from KdeQt import KQMessageBox

from E4Gui.E4Action import E4Action

from SqlBrowserWidget import SqlBrowserWidget

import UI.PixmapCache
import UI.Config

class SqlBrowser(KQMainWindow):
    """
    Class implementing the SQL Browser main window.
    """
    def __init__(self, connections = [], parent = None):
        """
        Constructor
        
        @param connections list of database connections to add (list of strings)
        @param reference to the parent widget (QWidget)
        """
        KQMainWindow.__init__(self, parent)
        self.setObjectName("SqlBrowser")
        
        self.setWindowTitle(self.trUtf8("SQL Browser"))
        self.setWindowIcon(UI.PixmapCache.getIcon("eric.png"))
        
        self.__browser = SqlBrowserWidget(self)
        self.setCentralWidget(self.__browser)
        
        self.connect(self.__browser, SIGNAL("statusMessage(QString)"), 
                     self.statusBar().showMessage)
        
        self.__initActions()
        self.__initMenus()
        self.__initToolbars()
        
        self.resize(self.__browser.size())
        
        self.__warnings = []
        
        for connection in connections:
            url = QUrl(connection, QUrl.TolerantMode)
            if not url.isValid():
                self.__warnings.append(self.trUtf8("Invalid URL: %1").arg(connection))
                continue
            
            err = self.__browser.addConnection(url.scheme(), url.path(), 
                                               url.userName(), url.password(), 
                                               url.host(), url.port(-1))
            if err.type() != QSqlError.NoError:
                self.__warnings.append(
                    self.trUtf8("Unable to open connection: %1").arg(err.text()))
        
        QTimer.singleShot(0, self.__uiStartUp)
    
    def __uiStartUp(self):
        """
        Private slot to do some actions after the UI has started and the main loop is up.
        """
        for warning in self.__warnings:
            KQMessageBox.warning(self,
                self.trUtf8("SQL Browser startup problem"),
                warning)
        
        if QSqlDatabase.connectionNames().isEmpty():
            self.__browser.addConnectionByDialog()
    
    def __initActions(self):
        """
        Private method to define the user interface actions.
        """
        # list of all actions
        self.__actions = []
        
        self.addConnectionAct = E4Action(self.trUtf8('Add Connection'), 
            UI.PixmapCache.getIcon("databaseConnection.png"),
            self.trUtf8('Add &Connection...'), 
            0, 0, self, 'sql_file_add_connection')
        self.addConnectionAct.setStatusTip(self.trUtf8(
                'Open a dialog to add a new database connection'))
        self.addConnectionAct.setWhatsThis(self.trUtf8(
                """<b>Add Connection</b>"""
                """<p>This opens a dialog to add a new database connection.</p>"""
        ))
        self.connect(self.addConnectionAct, SIGNAL('triggered()'), 
                     self.__browser.addConnectionByDialog)
        self.__actions.append(self.addConnectionAct)
        
        self.exitAct = E4Action(self.trUtf8('Quit'), 
            UI.PixmapCache.getIcon("exit.png"),
            self.trUtf8('&Quit'), 
            QKeySequence(self.trUtf8("Ctrl+Q","File|Quit")), 
            0, self, 'sql_file_quit')
        self.exitAct.setStatusTip(self.trUtf8('Quit the SQL browser'))
        self.exitAct.setWhatsThis(self.trUtf8(
                """<b>Quit</b>"""
                """<p>Quit the SQL browser.</p>"""
        ))
        self.connect(self.exitAct, SIGNAL('triggered()'), 
                     qApp, SLOT('closeAllWindows()'))
        
        self.aboutAct = E4Action(self.trUtf8('About'), 
            self.trUtf8('&About'), 
            0, 0, self, 'sql_help_about')
        self.aboutAct.setStatusTip(self.trUtf8('Display information about this software'))
        self.aboutAct.setWhatsThis(self.trUtf8(
                """<b>About</b>"""
                """<p>Display some information about this software.</p>"""
        ))
        self.connect(self.aboutAct, SIGNAL('triggered()'), self.__about)
        self.__actions.append(self.aboutAct)
        
        self.aboutQtAct = E4Action(self.trUtf8('About Qt'), 
            self.trUtf8('About &Qt'), 
            0, 0, self, 'sql_help_about_qt')
        self.aboutQtAct.setStatusTip(\
            self.trUtf8('Display information about the Qt toolkit'))
        self.aboutQtAct.setWhatsThis(self.trUtf8(
                """<b>About Qt</b>"""
                """<p>Display some information about the Qt toolkit.</p>"""
        ))
        self.connect(self.aboutQtAct, SIGNAL('triggered()'), self.__aboutQt)
        self.__actions.append(self.aboutQtAct)
    
    def __initMenus(self):
        """
        Private method to create the menus.
        """
        mb = self.menuBar()
        
        menu = mb.addMenu(self.trUtf8('&File'))
        menu.setTearOffEnabled(True)
        menu.addAction(self.addConnectionAct)
        menu.addSeparator()
        menu.addAction(self.exitAct)
        
        mb.addSeparator()
        
        menu = mb.addMenu(self.trUtf8('&Help'))
        menu.setTearOffEnabled(True)
        menu.addAction(self.aboutAct)
        menu.addAction(self.aboutQtAct)
    
    def __initToolbars(self):
        """
        Private method to create the toolbars.
        """
        filetb = self.addToolBar(self.trUtf8("File"))
        filetb.setObjectName("FileToolBar")
        filetb.setIconSize(UI.Config.ToolBarIconSize)
        filetb.addAction(self.addConnectionAct)
        filetb.addSeparator()
        filetb.addAction(self.exitAct)
    
    def __about(self):
        """
        Private slot to show the about information.
        """
        KQMessageBox.about(self, self.trUtf8("SQL Browser"), self.trUtf8(
            """<h3>About SQL Browser</h3>"""
            """<p>The SQL browser window is a little tool to examine """
            """the data and the schema of a database and to execute """
            """queries on a database.</p>"""
        ))
    
    def __aboutQt(self):
        """
        Private slot to show info about Qt.
        """
        KQMessageBox.aboutQt(self, self.trUtf8("SQL Browser"))
