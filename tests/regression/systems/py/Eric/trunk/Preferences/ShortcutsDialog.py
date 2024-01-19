# -*- coding: utf-8 -*-

# Copyright (c) 2003 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a dialog for the configuration of eric4s keyboard shortcuts.
"""

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from KdeQt import KQMessageBox
from KdeQt.KQApplication import e4App

from Ui_ShortcutsDialog import Ui_ShortcutsDialog
from ShortcutDialog import ShortcutDialog

import UI.PixmapCache

import Preferences
from Preferences import Shortcuts


class ShortcutsDialog(QDialog, Ui_ShortcutsDialog):
    """
    Class implementing a dialog for the configuration of eric4s keyboard shortcuts.
    """
    objectNameRole = Qt.UserRole
    noCheckRole    = Qt.UserRole + 1
    objectTypeRole = Qt.UserRole + 2
    
    def __init__(self, parent = None, name = None, modal = False):
        """
        Constructor
        
        @param parent The parent widget of this dialog. (QWidget)
        @param name The name of this dialog. (QString)
        @param modal Flag indicating a modal dialog. (boolean)
        """
        QDialog.__init__(self, parent)
        if name:
            self.setObjectName(name)
        self.setModal(modal)
        self.setupUi(self)
        
        self.clearSearchButton.setIcon(UI.PixmapCache.getIcon("clearLeft.png"))
        self.shortcutsList.headerItem().setText(self.shortcutsList.columnCount(), "")
        self.shortcutsList.header().setSortIndicator(0, Qt.AscendingOrder)
        
        self.shortcutDialog = ShortcutDialog()
        self.connect(self.shortcutDialog, SIGNAL('shortcutChanged'),
                     self.__shortcutChanged)
        
    def __resort(self):
        """
        Private method to resort the tree.
        """
        self.shortcutsList.sortItems(self.shortcutsList.sortColumn(), 
            self.shortcutsList.header().sortIndicatorOrder())
        
    def __resizeColumns(self):
        """
        Private method to resize the list columns.
        """
        self.shortcutsList.header().resizeSections(QHeaderView.ResizeToContents)
        self.shortcutsList.header().setStretchLastSection(True)
        
    def __generateCategoryItem(self, title):
        """
        Private method to generate a category item.
        
        @param title title for the item (QString)
        @return reference to the category item (QTreeWidgetItem)
        """
        itm = QTreeWidgetItem(self.shortcutsList, QStringList(title))
        itm.setExpanded(True)
        return itm
        
    def __generateShortcutItem(self, category, action, 
                               noCheck = False, objectType = None):
        """
        Private method to generate a keyboard shortcut item.
        
        @param category reference to the category item (QTreeWidgetItem)
        @param action reference to the keyboard action (E4Action)
        @keyparam noCheck flag indicating that no uniqueness check should
            be performed (boolean)
        @keyparam objectType type of the object (string). Objects of the same type
            are not checked for duplicate shortcuts.
        """
        itm = QTreeWidgetItem(category, 
            QStringList() << action.iconText() << QString(action.shortcut().toString()) \
                << QString(action.alternateShortcut().toString()))
        itm.setIcon(0, action.icon())
        itm.setData(0, self.objectNameRole, QVariant(action.objectName()))
        itm.setData(0, self.noCheckRole, QVariant(noCheck))
        if objectType:
            itm.setData(0, self.objectTypeRole, QVariant(objectType))
        else:
            itm.setData(0, self.objectTypeRole, QVariant())
        
    def populate(self):
        """
        Public method to populate the dialog.
        """
        self.searchEdit.clear()
        self.searchEdit.setFocus()
        self.shortcutsList.clear()
        self.actionButton.setChecked(True)
        
        # let the plugin manager create on demand plugin objects
        pm = e4App().getObject("PluginManager")
        pm.initOnDemandPlugins()
        
        # populate the various lists
        self.projectItem = self.__generateCategoryItem(self.trUtf8("Project"))
        for act in e4App().getObject("Project").getActions():
            self.__generateShortcutItem(self.projectItem, act)
        
        self.uiItem = self.__generateCategoryItem(self.trUtf8("General"))
        for act in e4App().getObject("UserInterface").getActions('ui'):
            self.__generateShortcutItem(self.uiItem, act)
        
        self.wizardsItem = self.__generateCategoryItem(self.trUtf8("Wizards"))
        for act in e4App().getObject("UserInterface").getActions('wizards'):
            self.__generateShortcutItem(self.wizardsItem, act)
        
        self.debugItem = self.__generateCategoryItem(self.trUtf8("Debug"))
        for act in e4App().getObject("DebugUI").getActions():
            self.__generateShortcutItem(self.debugItem, act)
        
        self.editItem = self.__generateCategoryItem(self.trUtf8("Edit"))
        for act in e4App().getObject("ViewManager").getActions('edit'):
            self.__generateShortcutItem(self.editItem, act)
        
        self.fileItem = self.__generateCategoryItem(self.trUtf8("File"))
        for act in e4App().getObject("ViewManager").getActions('file'):
            self.__generateShortcutItem(self.fileItem, act)
        
        self.searchItem = self.__generateCategoryItem(self.trUtf8("Search"))
        for act in e4App().getObject("ViewManager").getActions('search'):
            self.__generateShortcutItem(self.searchItem, act)
        
        self.viewItem = self.__generateCategoryItem(self.trUtf8("View"))
        for act in e4App().getObject("ViewManager").getActions('view'):
            self.__generateShortcutItem(self.viewItem, act)
        
        self.macroItem = self.__generateCategoryItem(self.trUtf8("Macro"))
        for act in e4App().getObject("ViewManager").getActions('macro'):
            self.__generateShortcutItem(self.macroItem, act)
        
        self.bookmarkItem = self.__generateCategoryItem(self.trUtf8("Bookmarks"))
        for act in e4App().getObject("ViewManager").getActions('bookmark'):
            self.__generateShortcutItem(self.bookmarkItem, act)
        
        self.spellingItem = self.__generateCategoryItem(self.trUtf8("Spelling"))
        for act in e4App().getObject("ViewManager").getActions('spelling'):
            self.__generateShortcutItem(self.spellingItem, act)
        
        actions = e4App().getObject("ViewManager").getActions('window')
        if actions:
            self.windowItem = self.__generateCategoryItem(self.trUtf8("Window"))
            for act in actions:
                self.__generateShortcutItem(self.windowItem, act)
        
        self.pluginCategoryItems = []
        for category, ref in e4App().getPluginObjects():
            if hasattr(ref, "getActions"):
                categoryItem = self.__generateCategoryItem(category)
                objectType = e4App().getPluginObjectType(category)
                for act in ref.getActions():
                    self.__generateShortcutItem(categoryItem, act, 
                                                objectType = objectType)
                self.pluginCategoryItems.append(categoryItem)
        
        self.helpViewerItem = self.__generateCategoryItem(self.trUtf8("Web Browser"))
        for act in e4App().getObject("DummyHelpViewer").getActions():
            self.__generateShortcutItem(self.helpViewerItem, act, True)
        
        self.__resort()
        self.__resizeColumns()
        
        self.__editTopItem = None
        
    def on_shortcutsList_itemDoubleClicked(self, itm, column):
        """
        Private slot to handle a double click in the shortcuts list.
        
        @param itm the list item that was double clicked (QTreeWidgetItem)
        @param column the list item was double clicked in (integer)
        """
        if itm.childCount():
            return
        
        self.__editTopItem = itm.parent()
        
        self.shortcutDialog.setKeys(QKeySequence(itm.text(1)), QKeySequence(itm.text(2)), 
            itm.data(0, self.noCheckRole).toBool(), 
            itm.data(0, self.objectTypeRole).toString())
        self.shortcutDialog.show()
        
    def on_shortcutsList_itemClicked(self, itm, column):
        """
        Private slot to handle a click in the shortcuts list.
        
        @param itm the list item that was clicked (QTreeWidgetItem)
        @param column the list item was clicked in (integer)
        """
        if itm.childCount() or column not in [1, 2]:
            return
        
        self.shortcutsList.openPersistentEditor(itm, column)
        
    def on_shortcutsList_itemChanged(self, itm, column):
        """
        Private slot to handle the edit of a shortcut key.
        
        @param itm reference to the item changed (QTreeWidgetItem)
        @param column column changed (integer)
        """
        if column != 0:
            keystr = unicode(itm.text(column)).title()
            if not itm.data(0, self.noCheckRole).toBool() and \
               not self.__checkShortcut(QKeySequence(keystr), 
                                        itm.data(0, self.objectTypeRole).toString(), 
                                        itm.parent()):
                itm.setText(column, "")
            else:
                itm.setText(column, keystr)
            self.shortcutsList.closePersistentEditor(itm, column)

    def __shortcutChanged(self, keysequence, altKeysequence, noCheck, objectType):
        """
        Private slot to handle the shortcutChanged signal of the shortcut dialog.
        
        @param keysequence the keysequence of the changed action (QKeySequence)
        @param altKeysequence the alternative keysequence of the changed 
            action (QKeySequence)
        @param noCheck flag indicating that no uniqueness check should
            be performed (boolean)
        @param objectType type of the object (string).
        """
        if not noCheck and \
           (not self.__checkShortcut(keysequence, objectType, self.__editTopItem) or \
            not self.__checkShortcut(altKeysequence, objectType, self.__editTopItem)):
            return
        
        self.shortcutsList.currentItem().setText(1, QString(keysequence))
        self.shortcutsList.currentItem().setText(2, QString(altKeysequence))
        
        self.__resort()
        self.__resizeColumns()
        
    def __checkShortcut(self, keysequence, objectType, origTopItem):
        """
        Private method to check a keysequence for uniqueness.
        
        @param keysequence the keysequence to check (QKeySequence)
        @param objectType type of the object (string). Entries with the same
            object type are not checked for uniqueness.
        @param origTopItem refrence to the parent of the item to be checked
            (QTreeWidgetItem)
        @return flag indicating uniqueness (boolean)
        """
        if keysequence.isEmpty():
            return True
        
        keystr = unicode(QString(keysequence))
        keyname = unicode(self.shortcutsList.currentItem().text(0))
        for topIndex in range(self.shortcutsList.topLevelItemCount()):
            topItem = self.shortcutsList.topLevelItem(topIndex)
            for index in range(topItem.childCount()):
                itm = topItem.child(index)
                
                # 1. shall a check be performed?
                if itm.data(0, self.noCheckRole).toBool():
                    continue
                
                # 2. check object type
                itmObjectType = itm.data(0, self.objectTypeRole).toString()
                if itmObjectType and \
                   itmObjectType == objectType and \
                   topItem != origTopItem:
                    continue
                
                # 3. check key name
                if unicode(itm.text(0)) != keyname:
                    for col in [1, 2]:  # check against primary, then alternative binding
                        itmseq = unicode(itm.text(col))
                        # step 1: check if shortcut is already allocated
                        if keystr == itmseq:
                            res = KQMessageBox.warning(None,
                                self.trUtf8("Edit shortcuts"),
                                self.trUtf8(\
                                    """<p><b>%1</b> has already been allocated"""
                                    """ to the <b>%2</b> action. """
                                    """Remove this binding?</p>""")
                                    .arg(keystr).arg(itm.text(0)),
                                QMessageBox.StandardButtons(\
                                    QMessageBox.No | \
                                    QMessageBox.Yes),
                                QMessageBox.No)
                            if res == QMessageBox.Yes:
                                itm.setText(col, "")
                                return True
                            else:
                                return False
                        
                        if not itmseq:
                            continue
                        
                        # step 2: check if shortcut hides an already allocated
                        if itmseq.startswith("%s+" % keystr):
                            res = KQMessageBox.warning(None,
                                self.trUtf8("Edit shortcuts"),
                                self.trUtf8(\
                                    """<p><b>%1</b> hides the <b>%2</b> action. """
                                    """Remove this binding?</p>""")
                                    .arg(keystr).arg(itm.text(0)),
                                QMessageBox.StandardButtons(\
                                    QMessageBox.No | \
                                    QMessageBox.Yes),
                                QMessageBox.No)
                            if res == QMessageBox.Yes:
                                itm.setText(col, "")
                                return True
                            else:
                                return False
                        
                        # step 3: check if shortcut is hidden by an already allocated
                        if keystr.startswith("%s+" % itmseq):
                            res = KQMessageBox.warning(None,
                                self.trUtf8("Edit shortcuts"),
                                self.trUtf8(\
                                    """<p><b>%1</b> is hidden by the <b>%2</b> action. """
                                    """Remove this binding?</p>""")
                                    .arg(keystr).arg(itm.text(0)),
                                QMessageBox.StandardButtons(\
                                    QMessageBox.No | \
                                    QMessageBox.Yes),
                                QMessageBox.No)
                            if res == QMessageBox.Yes:
                                itm.setText(col, "")
                                return True
                            else:
                                return False
            
        return True
        
    def __saveCategoryActions(self, category, actions):
        """
        Private method to save the actions for a category.
        
        @param category reference to the category item (QTreeWidgetItem)
        @param actions list of actions for the category (list of E4Action)
        """
        for index in range(category.childCount()):
            itm = category.child(index)
            txt = str(itm.text(4)) # this is one more due to empty last section
            txt = itm.data(0, self.objectNameRole).toString()
            for act in actions:
                if txt == act.objectName():
                    act.setShortcut(QKeySequence(itm.text(1)))
                    act.setAlternateShortcut(QKeySequence(itm.text(2)))
                    break
        
    def on_buttonBox_accepted(self):
        """
        Private slot to handle the OK button press.
        """
        self.__saveCategoryActions(self.projectItem, 
            e4App().getObject("Project").getActions())
        self.__saveCategoryActions(self.uiItem, 
            e4App().getObject("UserInterface").getActions('ui'))
        self.__saveCategoryActions(self.wizardsItem, 
            e4App().getObject("UserInterface").getActions('wizards'))
        self.__saveCategoryActions(self.debugItem, 
            e4App().getObject("DebugUI").getActions())
        self.__saveCategoryActions(self.editItem, 
            e4App().getObject("ViewManager").getActions('edit'))
        self.__saveCategoryActions(self.fileItem, 
            e4App().getObject("ViewManager").getActions('file'))
        self.__saveCategoryActions(self.searchItem, 
            e4App().getObject("ViewManager").getActions('search'))
        self.__saveCategoryActions(self.viewItem, 
            e4App().getObject("ViewManager").getActions('view'))
        self.__saveCategoryActions(self.macroItem, 
            e4App().getObject("ViewManager").getActions('macro'))
        self.__saveCategoryActions(self.bookmarkItem, 
            e4App().getObject("ViewManager").getActions('bookmark'))
        self.__saveCategoryActions(self.spellingItem, 
            e4App().getObject("ViewManager").getActions('spelling'))
        
        actions = e4App().getObject("ViewManager").getActions('window')
        if actions:
            self.__saveCategoryActions(self.windowItem, actions)
        
        for categoryItem in self.pluginCategoryItems:
            category = unicode(categoryItem.text(0))
            ref = e4App().getPluginObject(category)
            if ref is not None and hasattr(ref, "getActions"):
                self.__saveCategoryActions(categoryItem, ref.getActions())
        
        self.__saveCategoryActions(self.helpViewerItem, 
            e4App().getObject("DummyHelpViewer").getActions())
        
        Shortcuts.saveShortcuts()
        Preferences.syncPreferences()
        
        self.emit(SIGNAL('updateShortcuts'))
        self.hide()
    
    @pyqtSignature("QString")
    def on_searchEdit_textChanged(self, txt):
        """
        Private slot called, when the text in the search edit changes.
        
        @param txt text of the search edit (QString)
        """
        for topIndex in range(self.shortcutsList.topLevelItemCount()):
            topItem = self.shortcutsList.topLevelItem(topIndex)
            childHiddenCount = 0
            for index in range(topItem.childCount()):
                itm = topItem.child(index)
                if (self.actionButton.isChecked() and \
                    not itm.text(0).contains(QRegExp(txt, Qt.CaseInsensitive))) or \
                   (self.shortcutButton.isChecked() and \
                    not itm.text(1).contains(txt, Qt.CaseInsensitive) and \
                    not itm.text(2).contains(txt, Qt.CaseInsensitive)):
                    itm.setHidden(True)
                    childHiddenCount += 1
                else:
                    itm.setHidden(False)
            topItem.setHidden(childHiddenCount == topItem.childCount())
    
    @pyqtSignature("")
    def on_clearSearchButton_clicked(self):
        """
        Private slot called by a click of the clear search button.
        """
        self.searchEdit.clear()
    
    @pyqtSignature("bool")
    def on_actionButton_toggled(self, checked):
        """
        Private slot called, when the action radio button is toggled.
        
        @param checked state of the action radio button (boolean)
        """
        if checked:
            self.on_searchEdit_textChanged(self.searchEdit.text())
    
    @pyqtSignature("bool")
    def on_shortcutButton_toggled(self, checked):
        """
        Private slot called, when the shortcuts radio button is toggled.
        
        @param checked state of the shortcuts radio button (boolean)
        """
        if checked:
            self.on_searchEdit_textChanged(self.searchEdit.text())
