# -*- coding: utf-8 -*-

# Copyright (c) 2005 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a template viewer and associated classes.
"""

import datetime
import os
import sys
import re
import cStringIO

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from KdeQt.KQApplication import e4App

from TemplatePropertiesDialog import TemplatePropertiesDialog
from TemplateMultipleVariablesDialog import TemplateMultipleVariablesDialog
from TemplateSingleVariableDialog import TemplateSingleVariableDialog

import Preferences

from E4XML.XMLUtilities import make_parser
from E4XML.XMLErrorHandler import XMLErrorHandler, XMLFatalParseError
from E4XML.XMLEntityResolver import XMLEntityResolver
from E4XML.TemplatesHandler import TemplatesHandler
from E4XML.TemplatesWriter import TemplatesWriter

import UI.PixmapCache
import Utilities

from KdeQt import KQMessageBox, KQFileDialog
from KdeQt.KQApplication import e4App

class TemplateGroup(QTreeWidgetItem):
    """
    Class implementing a template group.
    """
    def __init__(self, parent, name, language = "All"):
        """
        Constructor
        
        @param parent parent widget of the template group (QWidget)
        @param name name of the group (string or QString)
        @param language programming language for the group (string or QString)
        """
        self.name = unicode(name)
        self.language = unicode(language)
        self.entries = {}
        
        QTreeWidgetItem.__init__(self, parent, QStringList(name))
        
        if Preferences.getTemplates("ShowTooltip"):
            self.setToolTip(0, language)
    
    def setName(self, name):
        """
        Public method to update the name of the group.
        
        @param name name of the group (string or QString)
        """
        self.name = unicode(name)
        self.setText(0, name)

    def getName(self):
        """
        Public method to get the name of the group.
        
        @return name of the group (string)
        """
        return self.name
        
    def setLanguage(self, language):
        """
        Public method to update the name of the group.
        
        @param language programming language for the group (string or QString)
        """
        self.language = unicode(language)
        if Preferences.getTemplates("ShowTooltip"):
            self.setToolTip(0, language)

    def getLanguage(self):
        """
        Public method to get the name of the group.
        
        @return language of the group (string)
        """
        return self.language
        
    def addEntry(self, name, description, template, quiet = False):
        """
        Public method to add a template entry to this group.
        
        @param name name of the entry (string or QString)
        @param description description of the entry to add (string or QString)
        @param template template text of the entry (string or QString)
        @param quiet flag indicating quiet operation (boolean)
        """
        name = unicode(name)
        if self.entries.has_key(name):
            if not quiet:
                KQMessageBox.critical(None,
                    QApplication.translate("TemplateGroup", "Add Template"),
                    QApplication.translate("TemplateGroup",
                                """<p>The group <b>%1</b> already contains a"""
                                """ template named <b>%2</b>.</p>""")\
                        .arg(self.name).arg(name))
            return
        
        self.entries[name] = TemplateEntry(self, name, description, template)
        
        if Preferences.getTemplates("AutoOpenGroups") and not self.isExpanded():
            self.setExpanded(True)
    
    def removeEntry(self, name):
        """
        Public method to remove a template entry from this group.
        
        @param name name of the entry to be removed (string or QString)
        """
        name = unicode(name)
        if not self.entries.has_key(name):
            return
        
        index = self.indexOfChild(self.entries[name])
        self.takeChild(index)
        del self.entries[name]
        
        if len(self.entries) == 0:
            if Preferences.getTemplates("AutoOpenGroups") and self.isExpanded():
                self.setExpanded(False)
    
    def removeAllEntries(self):
        """
        Public method to remove all template entries of this group.
        """
        for name in self.entries.keys()[:]:
            self.removeEntry(name)

    def hasEntry(self, name):
        """
        Public method to check, if the group has an entry with the given name.
        
        @param name name of the entry to check for (string or QString)
        @return flag indicating existence (boolean)
        """
        return unicode(name) in self.entries
    
    def getEntry(self, name):
        """
        Public method to get an entry.
        
        @param name name of the entry to retrieve (string or QString)
        @return reference to the entry (TemplateEntry)
        """
        try:
            return self.entries[unicode(name)]
        except KeyError:
            return None

    def getEntryNames(self, beginning):
        """
        Public method to get the names of all entries, who's name starts with the 
        given string.
        
        @param beginning string denoting the beginning of the template name
            (string or QString)
        @return list of entry names found (list of strings)
        """
        beginning = unicode(beginning)
        names = []
        for name in self.entries:
            if name.startswith(beginning):
                names.append(name)
        
        return names

    def getAllEntries(self):
        """
        Public method to retrieve all entries.
        
        @return list of all entries (list of TemplateEntry)
        """
        return self.entries.values()

class TemplateEntry(QTreeWidgetItem):
    """
    Class immplementing a template entry.
    """
    def __init__(self, parent, name, description, templateText):
        """
        Constructor
        
        @param parent parent widget of the template entry (QWidget)
        @param name name of the entry (string or QString)
        @param description descriptive text for the template (string or QString)
        @param templateText text of the template entry (string or QString)
        """
        self.name = unicode(name)
        self.description = unicode(description)
        self.template = unicode(templateText)
        self.__extractVariables()
        
        QTreeWidgetItem.__init__(self, parent, QStringList(self.__displayText()))
        if Preferences.getTemplates("ShowTooltip"):
            self.setToolTip(0, self.template)

    def __displayText(self):
        """
        Private method to generate the display text.
        
        @return display text (QString)
        """
        if self.description:
            txt = QString("%1 - %2").arg(self.name).arg(self.description)
        else:
            txt = QString(self.name)
        return txt
    
    def setName(self, name):
        """
        Public method to update the name of the entry.
        
        @param name name of the entry (string or QString)
        """
        self.name = unicode(name)
        self.setText(0, self.__displayText())

    def getName(self):
        """
        Public method to get the name of the entry.
        
        @return name of the entry (string)
        """
        return self.name

    def setDescription(self, description):
        """
        Public method to update the description of the entry.
        
        @param description description of the entry (string or QString)
        """
        self.description = unicode(description)
        self.setText(0, self.__displayText())

    def getDescription(self):
        """
        Public method to get the description of the entry.
        
        @return description of the entry (string)
        """
        return self.description

    def getGroupName(self):
        """
        Public method to get the name of the group this entry belongs to.
        
        @return name of the group containing this entry (string)
        """
        return self.parent().getName()
        
    def setTemplateText(self, templateText):
        """
        Public method to update the template text.
        
        @param templateText text of the template entry (string or QString)
        """
        self.template = unicode(templateText)
        self.__extractVariables()
        if Preferences.getTemplates("ShowTooltip"):
            self.setToolTip(0, self.template)

    def getTemplateText(self):
        """
        Public method to get the template text.
        
        @return the template text (string)
        """
        return self.template

    def getExpandedText(self, varDict, indent):
        """
        Public method to get the template text with all variables expanded.
        
        @param varDict dictionary containing the texts of each variable
            with the variable name as key.
        @param indent indentation of the line receiving he expanded 
            template text (string)
        @return a tuple of the expanded template text (string), the
            number of lines (integer) and the length of the last line (integer)
        """
        txt = self.template
        for var, val in varDict.items():
            if var in self.formatedVariables:
                txt = self.__expandFormattedVariable(var, val, txt)
            else:
                txt = txt.replace(var, val)
        sepchar = str(Preferences.getTemplates("SeparatorChar"))
        txt = txt.replace("%s%s" % (sepchar, sepchar), sepchar)
        prefix = "%s%s" % (os.linesep, indent)
        trailingEol = txt.endswith(os.linesep)
        lines = txt.splitlines()
        lineCount = len(lines)
        lineLen = len(lines[-1])
        txt = prefix.join(lines).lstrip()
        if trailingEol:
            txt = "%s%s" % (txt, os.linesep)
            lineCount += 1
            lineLen = 0
        return txt, lineCount, lineLen

    def __expandFormattedVariable(self, var, val, txt):
        """
        Private method to expand a template variable with special formatting.
        
        @param var template variable name (string)
        @param val value of the template variable (string)
        @param txt template text (string)
        """
        t = ""
        for line in txt.splitlines():
            ind = line.find(var)
            if ind >= 0:
                format = var[1:-1].split(':', 1)[1]
                if format == 'rl':
                    prefix = line[:ind]
                    postfix = line [ind+len(var):]
                    for v in val.splitlines():
                        t = "%s%s%s%s%s" % (t, os.linesep, prefix, v, postfix)
                elif format == 'ml':
                    indent = line.replace(line.lstrip(), "")
                    prefix = line[:ind]
                    postfix = line[ind + len(var):]
                    count = 0
                    for v in val.splitlines():
                        if count:
                            t = "%s%s%s%s" % (t, os.linesep, indent, v)
                        else:
                            t = "%s%s%s%s" % (t, os.linesep, prefix, v)
                        count += 1
                    t = "%s%s" % (t, postfix)
                else:
                    t = "%s%s%s" % (t, os.linesep, line)
            else:
                t = "%s%s%s" % (t, os.linesep, line)
        return "".join(t.splitlines(1)[1:])

    def getVariables(self):
        """
        Public method to get the list of variables.
        
        @return list of variables (list of strings)
        """
        return self.variables

    def __extractVariables(self):
        """
        Private method to retrieve the list of variables.
        """
        sepchar = str(Preferences.getTemplates("SeparatorChar"))
        variablesPattern = \
            re.compile(r"""\%s[a-zA-Z][a-zA-Z0-9_]*(?::(?:ml|rl))?\%s""" % \
                       (sepchar, sepchar))
        variables = variablesPattern.findall(self.template)
        self.variables = []
        self.formatedVariables = []
        for var in variables:
            if not var in self.variables:
                self.variables.append(var)
            if var.find(':') >= 0 and not var in self.formatedVariables:
                self.formatedVariables.append(var)

class TemplateViewer(QTreeWidget):
    """
    Class implementing the template viewer.
    """
    def __init__(self, parent, viewmanager):
        """
        Constructor
        
        @param parent the parent (QWidget)
        @param viewmanager reference to the viewmanager object
        """
        QTreeWidget.__init__(self, parent)
        
        self.viewmanager = viewmanager
        self.groups = {}
        
        self.setHeaderLabels(QStringList("Template"))
        self.header().hide()
        self.header().setSortIndicator(0, Qt.AscendingOrder)
        self.setRootIsDecorated(True)
        self.setAlternatingRowColors(True)
        
        self.__menu = QMenu(self)
        self.applyAct = \
            self.__menu.addAction(self.trUtf8("Apply"), self.__templateItemActivated)
        self.__menu.addSeparator()
        self.__menu.addAction(self.trUtf8("Add entry..."), self.__addEntry)
        self.__menu.addAction(self.trUtf8("Add group..."), self.__addGroup)
        self.__menu.addAction(self.trUtf8("Edit..."), self.__edit)
        self.__menu.addAction(self.trUtf8("Remove"), self.__remove)
        self.__menu.addSeparator()
        self.__menu.addAction(self.trUtf8("Save"), self.__save)
        self.__menu.addAction(self.trUtf8("Import..."), self.__import)
        self.__menu.addAction(self.trUtf8("Export..."), self.__export)
        self.__menu.addSeparator()
        self.__menu.addAction(self.trUtf8("Help about Templates..."), self.__showHelp)
        self.__menu.addSeparator()
        self.__menu.addAction(self.trUtf8("Configure..."), self.__configure)
        
        self.__backMenu = QMenu(self)
        self.__backMenu.addAction(self.trUtf8("Add group..."), self.__addGroup)
        self.__backMenu.addSeparator()
        self.__backMenu.addAction(self.trUtf8("Save"), self.__save)
        self.__backMenu.addAction(self.trUtf8("Import..."), self.__import)
        self.__backMenu.addAction(self.trUtf8("Export..."), self.__export)
        self.__backMenu.addSeparator()
        self.__backMenu.addAction(self.trUtf8("Help about Templates..."), self.__showHelp)
        self.__backMenu.addSeparator()
        self.__backMenu.addAction(self.trUtf8("Configure..."), self.__configure)
        
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.connect(self, SIGNAL("customContextMenuRequested(const QPoint &)"),
                     self.__showContextMenu)
        self.connect(self, SIGNAL("itemActivated(QTreeWidgetItem *, int)"),
                     self.__templateItemActivated)
        
        self.setWindowIcon(UI.PixmapCache.getIcon("eric.png"))
        
    def __resort(self):
        """
        Private method to resort the tree.
        """
        self.sortItems(self.sortColumn(), self.header().sortIndicatorOrder())
        
    def __templateItemActivated(self, itm = None, col = 0):
        """
        Private slot to handle the activation of an item. 
        
        @param itm reference to the activated item (QTreeWidgetItem)
        @param col column the item was activated in (integer)
        """
        itm = self.currentItem()
        if isinstance(itm, TemplateEntry):
            self.applyTemplate(itm)
        
    def __showContextMenu(self, coord):
        """
        Private slot to show the context menu of the list.
        
        @param coord the position of the mouse pointer (QPoint)
        """
        itm = self.itemAt(coord)
        coord = self.mapToGlobal(coord)
        if itm is None:
            self.__backMenu.popup(coord)
        else:
            self.applyAct.setEnabled(self.viewmanager.activeWindow() is not None)
            self.__menu.popup(coord)
    
    def __addEntry(self):
        """
        Private slot to handle the Add Entry context menu action.
        """
        itm = self.currentItem()
        if isinstance(itm, TemplateGroup):
            groupName = itm.getName()
        else:
            groupName = itm.getGroupName()
        
        dlg = TemplatePropertiesDialog(self)
        dlg.setSelectedGroup(groupName)
        if dlg.exec_() == QDialog.Accepted:
            name, description, groupName, template = dlg.getData()
            self.addEntry(groupName, name, description, template)
        
    def __addGroup(self):
        """
        Private slot to handle the Add Group context menu action.
        """
        dlg = TemplatePropertiesDialog(self, True)
        if dlg.exec_() == QDialog.Accepted:
            name, language = dlg.getData()
            self.addGroup(name, language)
        
    def __edit(self):
        """
        Private slot to handle the Edit context menu action.
        """
        itm = self.currentItem()
        if isinstance(itm, TemplateEntry):
            editGroup = False
        else:
            editGroup = True
        dlg = TemplatePropertiesDialog(self, editGroup, itm)
        if dlg.exec_() == QDialog.Accepted:
            if editGroup:
                name, language = dlg.getData()
                self.changeGroup(itm.getName(), name, language)
            else:
                name, description, groupName, template = dlg.getData()
                self.changeEntry(itm, name, groupName, description, template)
        
    def __remove(self):
        """
        Private slot to handle the Remove context menu action.
        """
        itm = self.currentItem()
        res = KQMessageBox.question(self,
            self.trUtf8("Remove Template"),
            self.trUtf8("""<p>Do you really want to remove <b>%1</b>?</p>""")\
                .arg(itm.getName()),
            QMessageBox.StandardButtons(\
                QMessageBox.No | \
                QMessageBox.Yes),
            QMessageBox.No)
        if res != QMessageBox.Yes:
            return

        if isinstance(itm, TemplateGroup):
            self.removeGroup(itm)
        else:
            self.removeEntry(itm)

    def __save(self):
        """
        Private slot to handle the Save context menu action.
        """
        self.writeTemplates()

    def __import(self):
        """
        Private slot to handle the Import context menu action.
        """
        fn = KQFileDialog.getOpenFileName(\
            self,
            self.trUtf8("Import Templates"),
            QString(),
            self.trUtf8("Templates Files (*.e3c *.e4c);; All Files (*)"))
        
        if not fn.isEmpty():
            self.readTemplates(fn)

    def __export(self):
        """
        Private slot to handle the Export context menu action.
        """
        selectedFilter = QString("")
        fn = KQFileDialog.getSaveFileName(\
            self,
            self.trUtf8("Export Templates"),
            QString(),
            self.trUtf8("Templates Files (*.e4c);; All Files (*)"),
            selectedFilter,
            QFileDialog.Options(QFileDialog.DontConfirmOverwrite))
        
        if not fn.isEmpty():
            ext = QFileInfo(fn).suffix()
            if ext.isEmpty():
                ex = selectedFilter.section('(*', 1, 1).section(')', 0, 0)
                if not ex.isEmpty():
                    fn.append(ex)
            self.writeTemplates(fn)

    def __showHelp(self):
        """
        Private method to show some help.
        """
        KQMessageBox.information(self,
            self.trUtf8("Template Help"),
            self.trUtf8("""<p><b>Template groups</b> are a means of grouping individual"""
                        """ templates. Groups have an attribute that specifies,"""
                        """ which programming language they apply for."""
                        """ In order to add template entries, at least one group"""
                        """ has to be defined.</p>"""
                        """<p><b>Template entries</b> are the actual templates."""
                        """ They are grouped by the template groups. Help about"""
                        """ how to define them is available in the template edit"""
                        """ dialog. There is an example template available in the"""
                        """ Examples subdirectory of the eric4 distribution.</p>"""))

    def __getPredefinedVars(self):
        """
        Private method to return predefined variables.
        
        @return dictionary of predefined variables and their values
        """
        project = e4App().getObject("Project")
        editor = self.viewmanager.activeWindow()
        today = datetime.datetime.now().date()
        sepchar = str(Preferences.getTemplates("SeparatorChar"))
        if sepchar == '%':
            sepchar = '%%'
        keyfmt = sepchar + "%s" + sepchar
        varValues = {keyfmt % 'date': today.isoformat(),
                     keyfmt % 'year': str(today.year)}

        if project.name:
            varValues[keyfmt % 'project_name'] = project.name

        path_name = editor.getFileName()
        if path_name:
            dir_name, file_name = os.path.split(path_name)
            base_name, ext = os.path.splitext(file_name)
            if ext:
                ext = ext[1:]
            varValues.update({
                    keyfmt % 'path_name': path_name,
                    keyfmt % 'dir_name': dir_name,
                    keyfmt % 'file_name': file_name,
                    keyfmt % 'base_name': base_name,
                    keyfmt % 'ext': ext
            })
        return varValues

    def applyTemplate(self, itm):
        """
        Public method to apply the template.
        
        @param itm reference to the template item to apply (TemplateEntry)
        """
        editor = self.viewmanager.activeWindow()
        if editor is None:
            return
        
        ok = False
        vars = itm.getVariables()
        varValues = self.__getPredefinedVars()
        
        # Remove predefined variables from list so user doesn't have to fill
        # these values out in the dialog.
        for v in varValues.keys():
            if v in vars:
                vars.remove(v)
        
        if vars:
            if Preferences.getTemplates("SingleDialog"):
                dlg = TemplateMultipleVariablesDialog(vars, self)
                if dlg.exec_() == QDialog.Accepted:
                    varValues.update(dlg.getVariables())
                    ok = True
            else:
                for var in vars:
                    dlg = TemplateSingleVariableDialog(var, self)
                    if dlg.exec_() == QDialog.Accepted:
                        varValues[var] = dlg.getVariable()
                    else:
                        return
                    del dlg
                ok = True
        else:
            ok = True
        
        if ok:
            line = unicode(editor.text(editor.getCursorPosition()[0]))\
                   .replace(os.linesep, "")
            indent = line.replace(line.lstrip(), "")
            txt, lines, count = itm.getExpandedText(varValues, indent)
            # It should be done on this way to allow undo
            editor.beginUndoAction()
            if editor.hasSelectedText():
                editor.removeSelectedText()
            line, index = editor.getCursorPosition()
            editor.insert(txt)
            editor.setCursorPosition(line + lines - 1, 
                count and index + count or 0)
            editor.endUndoAction()
            editor.setFocus()

    def applyNamedTemplate(self, templateName):
        """
        Public method to apply a template given a template name.
        
        @param templateName name of the template item to apply (string or QString)
        """
        for group in self.groups.values():
            template = group.getEntry(templateName)
            if template is not None:
                self.applyTemplate(template)
                break
    
    def addEntry(self, groupName, name, description, template, quiet = False):
        """
        Public method to add a template entry.
        
        @param groupName name of the group to add to (string or QString)
        @param name name of the entry to add (string or QString)
        @param description description of the entry to add (string or QString)
        @param template template text of the entry (string or QString)
        @param quiet flag indicating quiet operation (boolean)
        """
        self.groups[unicode(groupName)].addEntry(unicode(name), unicode(description), 
                                                 unicode(template), quiet = quiet)
        self.__resort()
        
    def addGroup(self, name, language = "All"):
        """
        Public method to add a group.
        
        @param name name of the group to be added (string or QString)
        @param language programming language for the group (string or QString)
        """
        name = unicode(name)
        if not self.groups.has_key(name):
            self.groups[name] = TemplateGroup(self, name, language)
        self.__resort()

    def changeGroup(self, oldname, newname, language = "All"):
        """
        Public method to rename a group.
        
        @param oldname old name of the group (string or QString)
        @param newname new name of the group (string or QString)
        @param language programming language for the group (string or QString)
        """
        if oldname != newname:
            if self.groups.has_key(newname):
                KQMessageBox.warning(self,
                    self.trUtf8("Edit Template Group"),
                    self.trUtf8("""<p>A template group with the name"""
                                """ <b>%1</b> already exists.</p>""")\
                        .arg(newname))
                return
            
            self.groups[newname] = self.groups[oldname]
            del self.groups[oldname]
            self.groups[newname].setName(newname)
        
        self.groups[newname].setLanguage(language)
        self.__resort()

    def getAllGroups(self):
        """
        Public method to get all groups.
        
        @return list of all groups (list of TemplateGroup)
        """
        return self.groups.values()
    
    def getGroupNames(self):
        """
        Public method to get all group names.
        
        @return list of all group names (list of strings)
        """
        groups = self.groups.keys()[:]
        groups.sort()
        return groups

    def removeGroup(self, itm):
        """
        Public method to remove a group.
        
        @param itm template group to be removed (TemplateGroup)
        """
        name = itm.getName()
        itm.removeAllEntries()
        index = self.indexOfTopLevelItem(itm)
        self.takeTopLevelItem(index)
        del self.groups[name]

    def removeEntry(self, itm):
        """
        Public method to remove a template entry.
        
        @param itm template entry to be removed (TemplateEntry)
        """
        groupName = itm.getGroupName()
        self.groups[groupName].removeEntry(itm.getName())

    def changeEntry(self, itm, name, groupName, description, template):
        """
        Public method to change a template entry.
        
        @param itm template entry to be changed (TemplateEntry)
        @param name new name for the entry (string or QString)
        @param groupName name of the group the entry should belong to
            (string or QString)
        @param description description of the entry (string or QString)
        @param template template text of the entry (string or QString)
        """
        if itm.getGroupName() != groupName:
            # move entry to another group
            self.groups[itm.getGroupName()].removeEntry(itm.getName())
            self.groups[groupName].addEntry(name, description, template)
            return
        
        if itm.getName() != name:
            # entry was renamed
            self.groups[groupName].removeEntry(itm.getName())
            self.groups[groupName].addEntry(name, description, template)
            return
        
        tmpl = self.groups[groupName].getEntry(name)
        tmpl.setDescription(description)
        tmpl.setTemplateText(template)
        self.__resort()

    def writeTemplates(self, filename = None):
        """
        Public method to write the templates data to an XML file (.e4c).
        
        @param filename name of a templates file to read (string or QString)
        """
        try:
            if filename is None:
                fn = os.path.join(Utilities.getConfigDir(), "eric4templates.e4c")
            else:
                fn = unicode(filename)
            f = open(fn, "wb")
            
            TemplatesWriter(f, self).writeXML()
            
            f.close()
        except IOError:
            KQMessageBox.critical(None,
                self.trUtf8("Save templates"),
                self.trUtf8("<p>The templates file <b>%1</b> could not be written.</p>")
                    .arg(fn))
        
    def readTemplates(self, filename = None):
        """
        Public method to read in the templates file (.e4c)
        
        @param filename name of a templates file to read (string or QString)
        """
        try:
            if filename is None:
                fn = os.path.join(Utilities.getConfigDir(), "eric4templates.e4c")
                if not os.path.exists(fn):
                    return
            else:
                fn = unicode(filename)
            f = open(fn, "rb")
            line = f.readline()
            dtdLine = f.readline()
            f.close()
        except IOError:
            KQMessageBox.critical(None,
                self.trUtf8("Read templates"),
                self.trUtf8("<p>The templates file <b>%1</b> could not be read.</p>")
                    .arg(fn))
            return
            
        # now read the file
        if line.startswith('<?xml'):
            parser = make_parser(dtdLine.startswith("<!DOCTYPE"))
            handler = TemplatesHandler(templateViewer = self)
            er = XMLEntityResolver()
            eh = XMLErrorHandler()
            
            parser.setContentHandler(handler)
            parser.setEntityResolver(er)
            parser.setErrorHandler(eh)
            
            try:
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
                    self.trUtf8("Read templates"),
                    self.trUtf8("<p>The templates file <b>%1</b> could not be read.</p>")
                        .arg(fn))
                return
            except XMLFatalParseError:
                pass
                
            eh.showParseMessages()
        else:
            KQMessageBox.critical(None,
                self.trUtf8("Read templates"),
                self.trUtf8("<p>The templates file <b>%1</b> has an"
                            " unsupported format.</p>")
                    .arg(fn))
    
    def __configure(self):
        """
        Private method to open the configuration dialog.
        """
        e4App().getObject("UserInterface").showPreferences("templatesPage")
    
    def hasTemplate(self, entryName):
        """
        Public method to check, if an entry of the given name exists.
        
        @param entryName name of the entry to check for (string or QString)
        @return flag indicating the existence (boolean)
        """
        for group in self.groups.values():
            if group.hasEntry(entryName):
                return True
        
        return False
    
    def getTemplateNames(self, start):
        """
        Public method to get the names of templates starting with the given string.
        
        @param start start string of the name (string or QString)
        @return sorted list of matching template names (list of strings)
        """
        names = []
        for group in self.groups.values():
            names.extend(group.getEntryNames(start))
        return sorted(names)
