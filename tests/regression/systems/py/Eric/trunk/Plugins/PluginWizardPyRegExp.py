# -*- coding: utf-8 -*-

# Copyright (c) 2007 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the Python re wizard plugin.
"""

from PyQt4.QtCore import QObject, SIGNAL, QString
from PyQt4.QtGui import QDialog

from KdeQt.KQApplication import e4App
from KdeQt import KQMessageBox

from E4Gui.E4Action import E4Action

from WizardPlugins.PyRegExpWizard.PyRegExpWizardDialog import \
    PyRegExpWizardDialog

# Start-Of-Header
name = "Python re Wizard Plugin"
author = "Detlev Offenbach <detlev@die-offenbachs.de>"
autoactivate = True
deactivateable = True
version = "4.4.0"
className = "PyRegExpWizard"
packageName = "__core__"
shortDescription = "Show the Python re wizard."
longDescription = """This plugin shows the Python re wizard."""
# End-Of-Header

error = QString("")

class PyRegExpWizard(QObject):
    """
    Class implementing the Python re wizard plugin.
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
        self.__initAction()
        self.__initMenu()
        
        return None, True

    def deactivate(self):
        """
        Public method to deactivate this plugin.
        """
        menu = self.__ui.getMenu("wizards")
        if menu:
            menu.removeAction(self.action)
        self.__ui.removeE4Actions([self.action], 'wizards')
    
    def __initAction(self):
        """
        Private method to initialize the action.
        """
        self.action = E4Action(self.trUtf8('Python re Wizard'),
             self.trUtf8('&Python re Wizard...'), 0, 0, self,
             'wizards_python_re')
        self.action.setStatusTip(self.trUtf8('Python re Wizard'))
        self.action.setWhatsThis(self.trUtf8(
            """<b>Python re Wizard</b>"""
            """<p>This wizard opens a dialog for entering all the parameters"""
            """ needed to create a Python re string. The generated code is inserted"""
            """ at the current cursor position.</p>"""
        ))
        self.connect(self.action, SIGNAL('triggered()'), self.__handle)
        
        self.__ui.addE4Actions([self.action], 'wizards')

    def __initMenu(self):
        """
        Private method to add the actions to the right menu.
        """
        menu = self.__ui.getMenu("wizards")
        if menu:
            menu.addAction(self.action)
    
    def __callForm(self, editor):
        """
        Private method to display a dialog and get the code.
        
        @param editor reference to the current editor
        @return the generated code (string)
        """
        dlg = PyRegExpWizardDialog(None, True)
        if dlg.exec_() == QDialog.Accepted:
            line, index = editor.getCursorPosition()
            indLevel = editor.indentation(line)/editor.indentationWidth()
            if editor.indentationsUseTabs():
                indString = '\t'
            else:
                indString = editor.indentationWidth() * ' '
            return (dlg.getCode(indLevel, indString), 1)
        else:
            return (None, False)
        
    def __handle(self):
        """
        Private method to handle the wizards action 
        """
        editor = e4App().getObject("ViewManager").activeWindow()
        
        if editor == None:
                KQMessageBox.critical(None, 
                self.trUtf8('No current editor'),
                self.trUtf8('Please open or create a file first.'))
        else:
            code, ok = self.__callForm(editor)
            if ok:
                line, index = editor.getCursorPosition()
                # It should be done on this way to allow undo
                editor.beginUndoAction()
                editor.insertAt(code, line, index)
                editor.endUndoAction()

