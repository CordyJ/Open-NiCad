# -*- coding: utf-8 -*-

# Copyright (c) 2004 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing functions dealing with keyboard shortcuts.
"""

import cStringIO

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from KdeQt import KQMessageBox
from KdeQt.KQApplication import e4App

from Preferences import Prefs, syncPreferences

from E4XML.XMLUtilities import make_parser
from E4XML.XMLErrorHandler import XMLErrorHandler, XMLFatalParseError
from E4XML.ShortcutsHandler import ShortcutsHandler
from E4XML.ShortcutsWriter import ShortcutsWriter
from E4XML.XMLEntityResolver import XMLEntityResolver

def __readShortcut(act, category, prefClass):
    """
    Private function to read a single keyboard shortcut from the settings.
    
    @param act reference to the action object (E4Action)
    @param category category the action belongs to (string or QString)
    @param prefClass preferences class used as the storage area
    """
    if not act.objectName().isEmpty():
        accel = prefClass.settings.value(\
            QString("Shortcuts/%1/%2/Accel").arg(category).arg(act.objectName()))
        if accel.isValid():
            act.setShortcut(QKeySequence(accel.toString()))
        accel = prefClass.settings.value(\
            QString("Shortcuts/%1/%2/AltAccel").arg(category).arg(act.objectName()))
        if accel.isValid():
            act.setAlternateShortcut(QKeySequence(accel.toString()))

def readShortcuts(prefClass = Prefs, helpViewer = None, pluginName = None):
    """
    Module function to read the keyboard shortcuts for the defined QActions.
    
    @keyparam prefClass preferences class used as the storage area
    @keyparam helpViewer reference to the help window object
    @keyparam pluginName name of the plugin for which to load shortcuts (string)
    """
    if helpViewer is None and pluginName is None:
        for act in e4App().getObject("Project").getActions():
            __readShortcut(act, "Project", prefClass)
        
        for act in e4App().getObject("UserInterface").getActions('ui'):
            __readShortcut(act, "General", prefClass)
        
        for act in e4App().getObject("UserInterface").getActions('wizards'):
            __readShortcut(act, "Wizards", prefClass)
        
        for act in e4App().getObject("DebugUI").getActions():
            __readShortcut(act, "Debug", prefClass)
        
        for act in e4App().getObject("ViewManager").getActions('edit'):
            __readShortcut(act, "Edit", prefClass)
        
        for act in e4App().getObject("ViewManager").getActions('file'):
            __readShortcut(act, "File", prefClass)
        
        for act in e4App().getObject("ViewManager").getActions('search'):
            __readShortcut(act, "Search", prefClass)
        
        for act in e4App().getObject("ViewManager").getActions('view'):
            __readShortcut(act, "View", prefClass)
        
        for act in e4App().getObject("ViewManager").getActions('macro'):
            __readShortcut(act, "Macro", prefClass)
        
        for act in e4App().getObject("ViewManager").getActions('bookmark'):
            __readShortcut(act, "Bookmarks", prefClass)
        
        for act in e4App().getObject("ViewManager").getActions('spelling'):
            __readShortcut(act, "Spelling", prefClass)
        
        actions = e4App().getObject("ViewManager").getActions('window')
        if actions:
            for act in actions:
                __readShortcut(act, "Window", prefClass)
        
        for category, ref in e4App().getPluginObjects():
            if hasattr(ref, "getActions"):
                actions = ref.getActions()
                for act in actions:
                    __readShortcut(act, category, prefClass)
    
    if helpViewer is not None:
        for act in helpViewer.getActions():
            __readShortcut(act, "HelpViewer", prefClass)
    
    if pluginName is not None:
        try:
            ref = e4App().getPluginObject(pluginName)
            if hasattr(ref, "getActions"):
                actions = ref.getActions()
                for act in actions:
                    __readShortcut(act, pluginName, prefClass)
        except KeyError:
            # silently ignore non available plugins
            pass
    
def __saveShortcut(act, category, prefClass):
    """
    Private function to write a single keyboard shortcut to the settings.
    
    @param act reference to the action object (E4Action)
    @param category category the action belongs to (string or QString)
    @param prefClass preferences class used as the storage area
    """
    if not act.objectName().isEmpty():
        prefClass.settings.setValue(\
            QString("Shortcuts/%1/%2/Accel").arg(category).arg(act.objectName()), 
            QVariant(QString(act.shortcut())))
        prefClass.settings.setValue(\
            QString("Shortcuts/%1/%2/AltAccel").arg(category).arg(act.objectName()), 
            QVariant(QString(act.alternateShortcut())))

def saveShortcuts(prefClass = Prefs):
    """
    Module function to write the keyboard shortcuts for the defined QActions.
    
    @param prefClass preferences class used as the storage area
    """
    # step 1: clear all previously saved shortcuts
    prefClass.settings.beginGroup("Shortcuts")
    prefClass.settings.remove("")
    prefClass.settings.endGroup()
    
    # step 2: save the various shortcuts
    for act in e4App().getObject("Project").getActions():
        __saveShortcut(act, "Project", prefClass)
    
    for act in e4App().getObject("UserInterface").getActions('ui'):
        __saveShortcut(act, "General", prefClass)
    
    for act in e4App().getObject("UserInterface").getActions('wizards'):
        __saveShortcut(act, "Wizards", prefClass)
    
    for act in e4App().getObject("DebugUI").getActions():
        __saveShortcut(act, "Debug", prefClass)
    
    for act in e4App().getObject("ViewManager").getActions('edit'):
        __saveShortcut(act, "Edit", prefClass)
    
    for act in e4App().getObject("ViewManager").getActions('file'):
        __saveShortcut(act, "File", prefClass)
    
    for act in e4App().getObject("ViewManager").getActions('search'):
        __saveShortcut(act, "Search", prefClass)
    
    for act in e4App().getObject("ViewManager").getActions('view'):
        __saveShortcut(act, "View", prefClass)
    
    for act in e4App().getObject("ViewManager").getActions('macro'):
        __saveShortcut(act, "Macro", prefClass)
    
    for act in e4App().getObject("ViewManager").getActions('bookmark'):
        __saveShortcut(act, "Bookmarks", prefClass)
    
    for act in e4App().getObject("ViewManager").getActions('spelling'):
        __saveShortcut(act, "Spelling", prefClass)
    
    actions = e4App().getObject("ViewManager").getActions('window')
    if actions:
        for act in actions:
            __saveShortcut(act, "Window", prefClass)
    
    for category, ref in e4App().getPluginObjects():
        if hasattr(ref, "getActions"):
            actions = ref.getActions()
            for act in actions:
                __saveShortcut(act, category, prefClass)
    
    for act in e4App().getObject("DummyHelpViewer").getActions():
        __saveShortcut(act, "HelpViewer", prefClass)

def exportShortcuts(fn):
    """
    Module function to export the keyboard shortcuts for the defined QActions.
    
    @param fn filename of the export file (string)
    @return flag indicating success
    """
    try:
        if fn.lower().endswith("e4kz"):
            try:
                import gzip
            except ImportError:
                KQMessageBox.critical(None,
                    QApplication.translate("Shortcuts", "Export Keyboard Shortcuts"),
                    QApplication.translate("Shortcuts", 
                        """Compressed keyboard shortcut files"""
                        """ not supported. The compression library is missing."""))
                return 0
            f = gzip.open(fn, "wb")
        else:
            f = open(fn, "wb")
        
        ShortcutsWriter(f).writeXML()
        
        f.close()
        return True
    except IOError:
        return False

def importShortcuts(fn):
    """
    Module function to import the keyboard shortcuts for the defined E4Actions.
    
    @param fn filename of the import file (string)
    @return flag indicating success
    """
    fn = unicode(fn)
    try:
        if fn.lower().endswith("kz"):
            try:
                import gzip
            except ImportError:
                KQMessageBox.critical(None,
                    QApplication.translate("Shortcuts", "Import Keyboard Shortcuts"),
                    QApplication.translate("Shortcuts", 
                        """Compressed keyboard shortcut files"""
                        """ not supported. The compression library is missing."""))
                return False
            f = gzip.open(fn, "rb")
        else:
            f = open(fn, "rb")
        try:
            line = f.readline()
            dtdLine = f.readline()
        finally:
            f.close()
    except IOError:
        KQMessageBox.critical(None,
            QApplication.translate("Shortcuts", "Import Keyboard Shortcuts"),
            QApplication.translate("Shortcuts", 
                "<p>The keyboard shortcuts could not be read from file <b>%1</b>.</p>")
                .arg(fn))
        return False
    
    if fn.lower().endswith("kz"):
        # work around for a bug in xmlproc
        validating = False
    else:
        validating = dtdLine.startswith("<!DOCTYPE")
    parser = make_parser(validating)
    handler = ShortcutsHandler()
    er = XMLEntityResolver()
    eh = XMLErrorHandler()
    
    parser.setContentHandler(handler)
    parser.setEntityResolver(er)
    parser.setErrorHandler(eh)
    
    try:
        if fn.lower().endswith("kz"):
            try:
                import gzip
            except ImportError:
                KQMessageBox.critical(None,
                    QApplication.translate("Shortcuts", "Import Keyboard Shortcuts"),
                    QApplication.translate("Shortcuts", 
                        """Compressed keyboard shortcut files"""
                        """ not supported. The compression library is missing."""))
                return False
            f = gzip.open(fn, "rb")
        else:
            f = open(fn, "rb")
        try:
            try:
                parser.parse(f)
            except UnicodeEncodeError:
                f.seek(0)
                buf = cStringIO.StringIO(f.read())
                parser.parse(buf)
        finally:
            f.close()
    except IOError:
        KQMessageBox.critical(None,
            QApplication.translate("Shortcuts", "Import Keyboard Shortcuts"),
            QApplication.translate("Shortcuts", 
                "<p>The keyboard shortcuts could not be read from file <b>%1</b>.</p>")
                .arg(fn))
        return False
        
    except XMLFatalParseError:
        KQMessageBox.critical(None,
            QApplication.translate("Shortcuts", "Import Keyboard Shortcuts"),
            QApplication.translate("Shortcuts", 
                "<p>The keyboard shortcuts file <b>%1</b> has invalid contents.</p>")
                .arg(fn))
        eh.showParseMessages()
        return False
        
    eh.showParseMessages()
    
    shortcuts = handler.getShortcuts()
    
    if handler.getVersion() == "3.5":
        setActions_35(shortcuts)
    else:
        setActions(shortcuts)
    
    saveShortcuts()
    syncPreferences()
    
    return True

def __setAction(actions, sdict):
    """
    Private function to write a single keyboard shortcut to the settings.
    
    @param actions list of actions to set (list of E4Action)
    @param sdict dictionary containg accelerator information for one category
    """
    for act in actions:
        if not act.objectName().isEmpty():
            try:
                accel, altAccel = sdict[unicode(act.objectName())]
                act.setShortcut(QKeySequence(accel))
                act.setAlternateShortcut(QKeySequence(altAccel))
            except KeyError:
                pass

def setActions(shortcuts):
    """
    Module function to set actions based on new format shortcuts file.
    
    @param shortcuts dictionary containing the accelerator information 
        read from a XML file
    """
    if shortcuts.has_key("Project"):
        __setAction(e4App().getObject("Project").getActions(), 
            shortcuts["Project"])
    
    if shortcuts.has_key("General"):
        __setAction(e4App().getObject("UserInterface").getActions('ui'), 
            shortcuts["General"])
    
    if shortcuts.has_key("Wizards"):
        __setAction(e4App().getObject("UserInterface").getActions('wizards'), 
            shortcuts["Wizards"])
    
    if shortcuts.has_key("Debug"):
        __setAction(e4App().getObject("DebugUI").getActions(), 
            shortcuts["Debug"])
    
    if shortcuts.has_key("Edit"):
        __setAction(e4App().getObject("ViewManager").getActions('edit'), 
            shortcuts["Edit"])
    
    if shortcuts.has_key("File"):
        __setAction(e4App().getObject("ViewManager").getActions('file'), 
            shortcuts["File"])
    
    if shortcuts.has_key("Search"):
        __setAction(e4App().getObject("ViewManager").getActions('search'), 
            shortcuts["Search"])
    
    if shortcuts.has_key("View"):
        __setAction(e4App().getObject("ViewManager").getActions('view'), 
            shortcuts["View"])
    
    if shortcuts.has_key("Macro"):
        __setAction(e4App().getObject("ViewManager").getActions('macro'), 
            shortcuts["Macro"])
    
    if shortcuts.has_key("Bookmarks"):
        __setAction(e4App().getObject("ViewManager").getActions('bookmark'), 
            shortcuts["Bookmarks"])
    
    if shortcuts.has_key("Spelling"):
        __setAction(e4App().getObject("ViewManager").getActions('spelling'), 
            shortcuts["Spelling"])
    
    if shortcuts.has_key("Window"):
        actions = e4App().getObject("ViewManager").getActions('window')
        if actions:
            __setAction(actions, shortcuts["Window"])
    
    for category, ref in e4App().getPluginObjects():
        if shortcuts.has_key(category) and hasattr(ref, "getActions"):
            actions = ref.getActions()
            __setAction(actions, shortcuts[category])
    
    if shortcuts.has_key("HelpViewer"):
        __setAction(e4App().getObject("DummyHelpViewer").getActions(), 
            shortcuts["HelpViewer"])
    
def __setAction35(actions, sdict):
    """
    Private function to write a single keyboard shortcut to the settings (old format).
    
    @param actions list of actions to set (list of E4Action)
    @param sdict dictionary containg accelerator information for one category
    """
    for act in actions:
        if not act.objectName().isEmpty():
            try:
                accel, altAccel = sdict[unicode(act.objectName())]
                act.setShortcut(QKeySequence(accel))
                act.setAlternateShortcut(QKeySequence())
            except KeyError:
                pass

def setActions_35(shortcuts):
    """
    Module function to set actions based on old format shortcuts file.
    
    @param shortcuts dictionary containing the accelerator information 
        read from a XML file
    """
    if shortcuts.has_key("Project"):
        __setAction35(e4App().getObject("Project").getActions(), 
            shortcuts["Project"])
    
    if shortcuts.has_key("General"):
        __setAction35(e4App().getObject("UserInterface").getActions('ui'), 
            shortcuts["General"])
    
    if shortcuts.has_key("Wizards"):
        __setAction35(e4App().getObject("UserInterface").getActions('wizards'), 
            shortcuts["Wizards"])
    
    if shortcuts.has_key("Debug"):
        __setAction35(e4App().getObject("DebugUI").getActions(), 
            shortcuts["Debug"])
    
    if shortcuts.has_key("Edit"):
        __setAction35(e4App().getObject("ViewManager").getActions('edit'), 
            shortcuts["Edit"])
    
    if shortcuts.has_key("File"):
        __setAction35(e4App().getObject("ViewManager").getActions('file'), 
            shortcuts["File"])
    
    if shortcuts.has_key("Search"):
        __setAction35(e4App().getObject("ViewManager").getActions('search'), 
            shortcuts["Search"])
    
    if shortcuts.has_key("View"):
        __setAction35(e4App().getObject("ViewManager").getActions('view'), 
            shortcuts["View"])
    
    if shortcuts.has_key("Macro"):
        __setAction35(e4App().getObject("ViewManager").getActions('macro'), 
            shortcuts["Macro"])
    
    if shortcuts.has_key("Bookmarks"):
        __setAction35(e4App().getObject("ViewManager").getActions('bookmark'), 
            shortcuts["Bookmarks"])
    
    if shortcuts.has_key("Window"):
        actions = e4App().getObject("ViewManager").getActions('window')
        if actions:
            __setAction35(actions, shortcuts["Window"])
    
    for category, ref in e4App().getPluginObjects():
        if shortcuts.has_key(category) and hasattr(ref, "getActions"):
            actions = ref.getActions()
            __setAction35(actions, shortcuts[category])
