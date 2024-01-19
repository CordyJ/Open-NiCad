# -*- coding: utf-8 -*-

# Copyright (c) 2007 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the About plugin.
"""

from PyQt4.QtCore import QObject, SIGNAL, QString
from PyQt4.QtGui import QMessageBox

import KdeQt

from UI.Info import *
import UI.PixmapCache

from E4Gui.E4Action import E4Action

from AboutPlugin.AboutDialog import AboutDialog

# Start-Of-Header
name = "About Plugin"
author = "Detlev Offenbach <detlev@die-offenbachs.de>"
autoactivate = True
deactivateable = True
version = "4.4.0"
className = "AboutPlugin"
packageName = "__core__"
shortDescription = "Show the About dialogs."
longDescription = """This plugin shows the About dialogs."""
# End-Of-Header

error = QString("")

class AboutPlugin(QObject):
    """
    Class implementing the About plugin.
    """
    def __init__(self, ui):
        """
        Constructor
        
        @param ui reference to the user interface object (UI.UserInterface)
        """
        QObject.__init__(self, ui)
        self.__ui = ui

    def activate(self):
        """
        Public method to activate this plugin.
        
        @return tuple of None and activation status (boolean)
        """
        self.__initActions()
        self.__initMenu()
        
        return None, True

    def deactivate(self):
        """
        Public method to deactivate this plugin.
        """
        menu = self.__ui.getMenu("help")
        if menu:
            menu.removeAction(self.aboutAct)
            menu.removeAction(self.aboutQtAct)
            if self.aboutKdeAct is not None:
                menu.removeAction(self.aboutKdeAct)
        acts = [self.aboutAct, self.aboutQtAct]
        if self.aboutKdeAct is not None:
            acts.append(self.aboutKdeAct)
        self.__ui.removeE4Actions(acts, 'ui')
    
    def __initActions(self):
        """
        Private method to initialize the actions.
        """
        acts = []
        
        self.aboutAct = E4Action(self.trUtf8('About %1').arg(Program),
                UI.PixmapCache.getIcon("helpAbout.png"),
                self.trUtf8('&About %1').arg(Program),
                0, 0, self, 'about_eric')
        self.aboutAct.setStatusTip(self.trUtf8('Display information about this software'))
        self.aboutAct.setWhatsThis(self.trUtf8(
            """<b>About %1</b>"""
            """<p>Display some information about this software.</p>"""
                             ).arg(Program))
        self.connect(self.aboutAct, SIGNAL('triggered()'), self.__about)
        acts.append(self.aboutAct)
        
        self.aboutQtAct = E4Action(self.trUtf8('About Qt'),
                UI.PixmapCache.getIcon("helpAboutQt.png"),
                self.trUtf8('About &Qt'), 0, 0, self, 'about_qt')
        self.aboutQtAct.setStatusTip(\
            self.trUtf8('Display information about the Qt toolkit'))
        self.aboutQtAct.setWhatsThis(self.trUtf8(
            """<b>About Qt</b>"""
            """<p>Display some information about the Qt toolkit.</p>"""
        ))
        self.connect(self.aboutQtAct, SIGNAL('triggered()'), self.__aboutQt)
        acts.append(self.aboutQtAct)
        
        if KdeQt.isKDE():
            self.aboutKdeAct = E4Action(self.trUtf8('About KDE'),
                    UI.PixmapCache.getIcon("helpAboutKde.png"),
                    self.trUtf8('About &KDE'), 0, 0, self, 'about_kde')
            self.aboutKdeAct.setStatusTip(self.trUtf8('Display information about KDE'))
            self.aboutKdeAct.setWhatsThis(self.trUtf8(
                """<b>About KDE</b>"""
                """<p>Display some information about KDE.</p>"""
            ))
            self.connect(self.aboutKdeAct, SIGNAL('triggered()'), self.__aboutKde)
            acts.append(self.aboutKdeAct)
        else:
            self.aboutKdeAct = None
        
        self.__ui.addE4Actions(acts, 'ui')

    def __initMenu(self):
        """
        Private method to add the actions to the right menu.
        """
        menu = self.__ui.getMenu("help")
        if menu:
            act = self.__ui.getMenuAction("help", "show_versions")
            if act:
                menu.insertAction(act, self.aboutAct)
                menu.insertAction(act, self.aboutQtAct)
                if self.aboutKdeAct is not None:
                    menu.insertAction(act, self.aboutKdeAct)
            else:
                menu.addAction(self.aboutAct)
                menu.addAction(self.aboutQtAct)
                if self.aboutKdeAct is not None:
                    menu.addAction(self.aboutKdeAct)
    
    def __about(self):
        """
        Private slot to handle the About dialog.
        """
        dlg = AboutDialog(self.__ui)
        dlg.exec_()
        
    def __aboutQt(self):
        """
        Private slot to handle the About Qt dialog.
        """
        QMessageBox.aboutQt(self.__ui, Program)
        
    def __aboutKde(self):
        """
        Private slot to handle the About KDE dialog.
        """
        from PyKDE4.kdeui import KHelpMenu
        menu = KHelpMenu(self.__ui)
        menu.aboutKDE()
