# -*- coding: utf-8 -*-

# Copyright (c) 2007 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the Tabnanny plugin.
"""

import os

from PyQt4.QtCore import QObject, SIGNAL, QString

from KdeQt.KQApplication import e4App

from E4Gui.E4Action import E4Action

from CheckerPlugins.SyntaxChecker.SyntaxCheckerDialog import SyntaxCheckerDialog

# Start-Of-Header
name = "Syntax Checker Plugin"
author = "Detlev Offenbach <detlev@die-offenbachs.de>"
autoactivate = True
deactivateable = True
version = "4.4.0"
className = "SyntaxCheckerPlugin"
packageName = "__core__"
shortDescription = "Show the Syntax Checker dialog."
longDescription = """This plugin implements the Syntax Checker dialog.""" \
 """ Syntax Checker is used to check Python source files for correct syntax."""
# End-Of-Header

error = QString("")

class SyntaxCheckerPlugin(QObject):
    """
    Class implementing the Syntax Checker plugin.
    """
    def __init__(self, ui):
        """
        Constructor
        
        @param ui reference to the user interface object (UI.UserInterface)
        """
        QObject.__init__(self, ui)
        self.__ui = ui
        self.__initialize()
        
    def __initialize(self):
        """
        Private slot to (re)initialize the plugin.
        """
        self.__projectAct = None
        self.__projectSyntaxCheckerDialog = None
        
        self.__projectBrowserAct = None
        self.__projectBrowserMenu = None
        self.__projectBrowserSyntaxCheckerDialog = None
        
        self.__editors = []
        self.__editorAct = None
        self.__editorSyntaxCheckerDialog = None

    def activate(self):
        """
        Public method to activate this plugin.
        
        @return tuple of None and activation status (boolean)
        """
        menu = e4App().getObject("Project").getMenu("Checks")
        if menu:
            self.__projectAct = E4Action(self.trUtf8('Check Syntax'),
                    self.trUtf8('&Syntax...'), 0, 0,
                    self, 'project_check_syntax')
            self.__projectAct.setStatusTip(\
                self.trUtf8('Check syntax.'))
            self.__projectAct.setWhatsThis(self.trUtf8(
                """<b>Check Syntax...</b>"""
                """<p>This checks Python files for syntax errors.</p>"""
            ))
            self.connect(self.__projectAct, SIGNAL('triggered()'), 
                         self.__projectSyntaxCheck)
            e4App().getObject("Project").addE4Actions([self.__projectAct])
            menu.addAction(self.__projectAct)
        
        self.__editorAct = E4Action(self.trUtf8('Check Syntax'),
                self.trUtf8('&Syntax...'), 0, 0,
                self, "")
        self.__editorAct.setWhatsThis(self.trUtf8(
                """<b>Check Syntax...</b>"""
                """<p>This checks Python files for syntax errors.</p>"""
        ))
        self.connect(self.__editorAct, SIGNAL('triggered()'), self.__editorSyntaxCheck)
        
        self.connect(e4App().getObject("Project"), SIGNAL("showMenu"), 
                     self.__projectShowMenu)
        self.connect(e4App().getObject("ProjectBrowser").getProjectBrowser("sources"), 
                     SIGNAL("showMenu"), self.__projectBrowserShowMenu)
        self.connect(e4App().getObject("ViewManager"), SIGNAL("editorOpenedEd"), 
                     self.__editorOpened)
        self.connect(e4App().getObject("ViewManager"), SIGNAL("editorClosedEd"), 
                     self.__editorClosed)
        
        for editor in e4App().getObject("ViewManager").getOpenEditors():
            self.__editorOpened(editor)
        
        return None, True

    def deactivate(self):
        """
        Public method to deactivate this plugin.
        """
        self.disconnect(e4App().getObject("Project"), SIGNAL("showMenu"), 
                        self.__projectShowMenu)
        self.disconnect(e4App().getObject("ProjectBrowser").getProjectBrowser("sources"), 
                        SIGNAL("showMenu"), self.__projectBrowserShowMenu)
        self.disconnect(e4App().getObject("ViewManager"), SIGNAL("editorOpenedEd"), 
                        self.__editorOpened)
        self.disconnect(e4App().getObject("ViewManager"), SIGNAL("editorClosedEd"), 
                        self.__editorClosed)
        
        menu = e4App().getObject("Project").getMenu("Checks")
        if menu:
            menu.removeAction(self.__projectAct)
        
        if self.__projectBrowserMenu:
            if self.__projectBrowserAct:
                self.__projectBrowserMenu.removeAction(self.__projectBrowserAct)
        
        for editor in self.__editors:
            self.disconnect(editor, SIGNAL("showMenu"), self.__editorShowMenu)
            menu = editor.getMenu("Checks")
            if menu is not None:
                menu.removeAction(self.__editorAct)
        
        self.__initialize()
    
    def __projectShowMenu(self, menuName, menu):
        """
        Private slot called, when the the project menu or a submenu is 
        about to be shown.
        
        @param menuName name of the menu to be shown (string)
        @param menu reference to the menu (QMenu)
        """
        if menuName == "Checks" and self.__projectAct is not None:
            self.__projectAct.setEnabled(\
                e4App().getObject("Project").getProjectLanguage() == "Python")
    
    def __projectBrowserShowMenu(self, menuName, menu):
        """
        Private slot called, when the the project browser menu or a submenu is 
        about to be shown.
        
        @param menuName name of the menu to be shown (string)
        @param menu reference to the menu (QMenu)
        """
        if menuName == "Checks" and \
           e4App().getObject("Project").getProjectLanguage() == "Python":
            self.__projectBrowserMenu = menu
            if self.__projectBrowserAct is None:
                self.__projectBrowserAct = E4Action(self.trUtf8('Check Syntax'),
                        self.trUtf8('&Syntax...'), 0, 0,
                        self, "")
                self.__projectBrowserAct.setWhatsThis(self.trUtf8(
                    """<b>Check Syntax...</b>"""
                    """<p>This checks Python files for syntax errors.</p>"""
                ))
                self.connect(self.__projectBrowserAct, SIGNAL('triggered()'), 
                             self.__projectBrowserSyntaxCheck)
            if not self.__projectBrowserAct in menu.actions():
                menu.addAction(self.__projectBrowserAct)
    
    def __projectSyntaxCheck(self):
        """
        Public slot used to check the project files for bad indentations.
        """
        project = e4App().getObject("Project")
        project.saveAllScripts()
        files = [os.path.join(project.ppath, file) \
            for file in project.pdata["SOURCES"] \
                if file.endswith(".py") or \
                   file.endswith(".pyw") or \
                   file.endswith(".ptl")]
        
        self.__projectSyntaxCheckerDialog = SyntaxCheckerDialog()
        self.__projectSyntaxCheckerDialog.show()
        self.__projectSyntaxCheckerDialog.start(files)
    
    def __projectBrowserSyntaxCheck(self):
        """
        Private method to handle the syntax check context menu action of the project
        sources browser.
        """
        browser = e4App().getObject("ProjectBrowser").getProjectBrowser("sources")
        itm = browser.model().item(browser.currentIndex())
        try:
            fn = itm.fileName()
        except AttributeError:
            fn = itm.dirName()
        
        self.__projectBrowserSyntaxCheckerDialog = SyntaxCheckerDialog()
        self.__projectBrowserSyntaxCheckerDialog.show()
        self.__projectBrowserSyntaxCheckerDialog.start(fn)
    
    def __editorOpened(self, editor):
        """
        Private slot called, when a new editor was opened.
        
        @param editor reference to the new editor (QScintilla.Editor)
        """
        menu = editor.getMenu("Checks")
        if menu is not None:
            menu.addAction(self.__editorAct)
            self.connect(editor, SIGNAL("showMenu"), self.__editorShowMenu)
            self.__editors.append(editor)
    
    def __editorClosed(self, editor):
        """
        Private slot called, when an editor was closed.
        
        @param editor reference to the editor (QScintilla.Editor)
        """
        try:
            self.__editors.remove(editor)
        except ValueError:
            pass
    
    def __editorShowMenu(self, menuName, menu, editor):
        """
        Private slot called, when the the editor context menu or a submenu is 
        about to be shown.
        
        @param menuName name of the menu to be shown (string)
        @param menu reference to the menu (QMenu)
        @param editor reference to the editor
        """
        if menuName == "Checks":
            if not self.__editorAct in menu.actions():
                menu.addAction(self.__editorAct)
            self.__editorAct.setEnabled(editor.isPyFile())
    
    def __editorSyntaxCheck(self):
        """
        Private slot to handle the syntax check context menu action of the editors.
        """
        editor = e4App().getObject("ViewManager").activeWindow()
        if editor is not None:
            self.__editorSyntaxCheckerDialog = SyntaxCheckerDialog()
            self.__editorSyntaxCheckerDialog.show()
            self.__editorSyntaxCheckerDialog.start(editor.getFileName(), 
                                                   unicode(editor.text()))
