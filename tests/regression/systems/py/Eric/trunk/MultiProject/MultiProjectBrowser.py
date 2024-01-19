# -*- coding: utf-8 -*-

# Copyright (c) 2008 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the multi project browser.
"""

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from KdeQt.KQApplication import e4App

from AddProjectDialog import AddProjectDialog

import UI.PixmapCache

class MultiProjectBrowser(QListWidget):
    """
    Class implementing the multi project browser.
    """
    def __init__(self, multiProject, parent = None):
        """
        Constructor
        
        @param project reference to the multi project object
        @param parent parent widget (QWidget)
        """
        QListWidget.__init__(self, parent)
        self.multiProject = multiProject
        
        self.setWindowIcon(UI.PixmapCache.getIcon("eric.png"))
        self.setAlternatingRowColors(True)
        
        self.connect(self.multiProject, SIGNAL("newMultiProject"), 
                     self.__newMultiProject)
        self.connect(self.multiProject, SIGNAL("multiProjectOpened"), 
                     self.__multiProjectOpened)
        self.connect(self.multiProject, SIGNAL("multiProjectClosed"), 
                     self.__multiProjectClosed)
        self.connect(self.multiProject, SIGNAL("projectDataChanged"), 
                     self.__projectDataChanged)
        self.connect(self.multiProject, SIGNAL("projectAdded"), 
                     self.__projectAdded)
        self.connect(self.multiProject, SIGNAL("projectRemoved"), 
                     self.__projectRemoved)
        self.connect(self.multiProject, SIGNAL("projectOpened"), 
                     self.__projectOpened)
        
        self.__createPopupMenu()
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.connect(self, SIGNAL("customContextMenuRequested(const QPoint &)"),
                     self.__contextMenuRequested)
        self.connect(self, SIGNAL("itemActivated(QListWidgetItem*)"), self.__openItem)
    
    ############################################################################
    ## Slot handling methods below
    ############################################################################
    
    def __newMultiProject(self):
        """
        Private slot to handle the creation of a new multi project.
        """
        self.clear()
    
    def __multiProjectOpened(self):
        """
        Private slot to handle the opening of a multi project.
        """
        for project in self.multiProject.getProjects():
            self.__addProject(project)
        
        self.sortItems()
    
    def __multiProjectClosed(self):
        """
        Private slot to handle the closing of a multi project.
        """
        self.clear()
    
    def __projectAdded(self, project):
        """
        Private slot to handle the addition of a project to the multi project.
        
        @param project reference to the project data dictionary
        """
        self.__addProject(project)
        self.sortItems()
    
    def __projectRemoved(self, project):
        """
        Private slot to handle the removal of a project from the multi project.
        
        @param project reference to the project data dictionary
        """
        row = self.__findProjectItem(project)
        if row > -1:
            itm = self.takeItem(row)
            del itm
    
    def __projectDataChanged(self, project):
        """
        Private slot to handle the change of a project of the multi project.
        
        @param project reference to the project data dictionary
        """
        row = self.__findProjectItem(project)
        if row > -1:
            self.__setItemData(self.item(row), project)
            
            self.sortItems()
    
    def __projectOpened(self, projectfile):
        """
        Private slot to handle the opening of a project.
        """
        project = {
            'name' : "", 
            'file' : projectfile, 
            'master' : False, 
            'description' : "", 
        }
        row = self.__findProjectItem(project)
        if row > -1:
            self.item(row).setSelected(True)
    
    def __contextMenuRequested(self, coord):
        """
        Private slot to show the context menu.
        
        @param coord the position of the mouse pointer (QPoint)
        """
        itm = self.itemAt(coord)
        if itm is None:
            self.__backMenu.popup(self.mapToGlobal(coord))
        else:
            self.__menu.popup(self.mapToGlobal(coord))
    
    def __openItem(self, itm = None):
        """
        Private slot to open a project.
        
        @param itm reference to the project item to be opened (QListWidgetItem)
        """
        if itm is None:
            itm = self.currentItem()
            if itm is None:
                return
        
        filename = unicode(itm.data(Qt.UserRole).toString())
        if filename:
            self.multiProject.openProject(filename)
    
    ############################################################################
    ## Private methods below
    ############################################################################
    
    def __addProject(self, project):
        """
        Private method to add a project to the list.
        
        @param project reference to the project data dictionary
        """
        itm = QListWidgetItem(self)
        self.__setItemData(itm, project)
    
    def __setItemData(self, itm, project):
        """
        Private method to set the data of a project item.
        
        @param itm reference to the item to be set (QListWidgetItem)
        @param project reference to the project data dictionary
        """
        itm.setText(project['name'])
        if project['master']:
            itm.setIcon(UI.PixmapCache.getIcon("masterProject.png"))
        else:
            itm.setIcon(UI.PixmapCache.getIcon("empty.png"))
        itm.setToolTip(project['file'])
        itm.setData(Qt.UserRole, QVariant(project['file']))
    
    def __findProjectItem(self, project):
        """
        Private method to search a specific project item.
        
        @param project reference to the project data dictionary
        """
        row = 0
        while row < self.count():
            itm = self.item(row)
            data = itm.data(Qt.UserRole).toString()
            if data == project['file']:
                return row
            row += 1
        
        return -1
    
    def __removeProject(self):
        """
        Private method to handle the Remove context menu entry.
        """
        itm = self.currentItem()
        if itm is not None:
            filename = unicode(itm.data(Qt.UserRole).toString())
            if filename:
                self.multiProject.removeProject(filename)
    
    def __showProjectProperties(self):
        """
        Private method to show the data of a project entry.
        """
        itm = self.currentItem()
        if itm is not None:
            filename = unicode(itm.data(Qt.UserRole).toString())
            if filename:
                project = self.multiProject.getProject(filename)
                if project is not None:
                    dlg = AddProjectDialog(self, project = project)
                    if dlg.exec_() == QDialog.Accepted:
                        name, filename, isMaster, description = dlg.getData()
                        project = {
                            'name' : name, 
                            'file' : filename, 
                            'master' : isMaster, 
                            'description' : description, 
                        }
                        self.multiProject.changeProjectProperties(project)
    
    def __createPopupMenu(self):
        """
        Private method to create the popup menu.
        """
        self.__menu = QMenu(self)
        self.__menu.addAction(self.trUtf8("Open"), self.__openItem)
        self.__menu.addAction(self.trUtf8("Remove"), self.__removeProject)
        self.__menu.addAction(self.trUtf8("Properties"), self.__showProjectProperties)
        self.__menu.addSeparator()
        self.__menu.addAction(self.trUtf8("Configure..."), self.__configure)
        
        self.__backMenu = QMenu(self)
        self.__backMenu.addAction(self.trUtf8("Configure..."), self.__configure)
    
    def __configure(self):
        """
        Private method to open the configuration dialog.
        """
        e4App().getObject("UserInterface").showPreferences("multiProjectPage")
