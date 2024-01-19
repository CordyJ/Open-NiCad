# -*- coding: utf-8 -*-

# Copyright (c) 2007 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a dialog showing an imports diagram of a package.
"""

import glob
import os
import sys

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from KdeQt.KQProgressDialog import KQProgressDialog

from UMLDialog import UMLDialog
from ModuleItem import ModuleItem, ModuleModel
from AssociationItem import AssociationItem, Imports
import GraphicsUtilities

import Utilities.ModuleParser
import Utilities

class ImportsDiagram(UMLDialog):
    """
    Class implementing a dialog showing an imports diagram of a package.
    
    Note: Only package internal imports are show in order to maintain
    some readability.
    """
    def __init__(self, package, parent = None, name = None, showExternalImports = False):
        """
        Constructor
        
        @param package name of a python package to show the import 
            relationships (string)
        @param parent parent widget of the view (QWidget)
        @param name name of the view widget (QString or string)
        @keyparam showExternalImports flag indicating to show exports from outside
            the package (boolean)
        """
        self.showExternalImports = showExternalImports
        self.packagePath = Utilities.normabspath(package)
        self.package = self.packagePath.replace(os.sep, '.')[1:]
        hasInit = True
        ppath = self.packagePath
        while hasInit:
            ppath = os.path.dirname(ppath)
            hasInit = len(glob.glob(os.path.join(ppath, '__init__.*'))) > 0
        self.shortPackage = self.packagePath.replace(ppath, '').replace(os.sep, '.')[1:]
        
        UMLDialog.__init__(self, self.packagePath, parent)
        
        if not name:
            self.setObjectName("ImportsDiagram")
        else:
            self.setObjectName(name)
        
        self.connect(self.umlView, SIGNAL("relayout()"), self.relayout)
        
    def __buildModulesDict(self):
        """
        Private method to build a dictionary of modules contained in the package.
        
        @return dictionary of modules contained in the package.
        """
        moduleDict = {}
        modules = glob.glob(Utilities.normjoinpath(self.packagePath,'*.py')) + \
                  glob.glob(Utilities.normjoinpath(self.packagePath,'*.pyw')) + \
                  glob.glob(Utilities.normjoinpath(self.packagePath,'*.ptl'))
        tot = len(modules)
        try:
            prog = 0
            progress = KQProgressDialog(self.trUtf8("Parsing modules..."),
                QString(), 0, tot, self)
            progress.show()
            QApplication.processEvents()
            for module in modules:
                progress.setValue(prog)
                QApplication.processEvents()
                prog = prog + 1
                try: 
                    mod = Utilities.ModuleParser.readModule(module, caching = False)
                except ImportError:
                    continue
                else:
                    name = mod.name
                    if name.startswith(self.package):
                        name = name[len(self.package) + 1:]
                    moduleDict[name] = mod
        finally:
            progress.setValue(tot)
        return moduleDict
        
    def __buildImports(self):
        """
        Private method to build the modules shapes of the diagram.
        """
        initlist = glob.glob(os.path.join(self.packagePath, '__init__.*'))
        if len(initlist) == 0:
            ct = QGraphicsTextItem(None, self.scene)
            ct.setHtml(\
                self.trUtf8("The directory <b>'%1'</b> is not a Python package.")\
                    .arg(self.package))
            return
        
        shapes = {}
        p = 10
        y = 10
        maxHeight = 0
        sceneRect = self.umlView.sceneRect()
        
        modules = self.__buildModulesDict()
        sortedkeys = modules.keys()
        sortedkeys.sort()
        externalMods = []
        packageList = self.shortPackage.split('.')
        packageListLen = len(packageList)
        for module in sortedkeys:
            impLst = []
            for i in modules[module].imports:
                if i.startswith(self.package):
                    n = i[len(self.package) + 1:]
                else:
                    n = i
                if modules.has_key(i):
                    impLst.append(n)
                elif self.showExternalImports:
                    impLst.append(n)
                    if not n in externalMods:
                        externalMods.append(n)
            for i in modules[module].from_imports.keys():
                if i.startswith('.'):
                    dots = len(i) - len(i.lstrip('.'))
                    if dots == 1:
                        n = i[1:]
                        i = n
                    else:
                        if self.showExternalImports:
                            n = '.'.join(\
                                packageList[:packageListLen - dots + 1] + [i[dots:]])
                        else:
                            n = i
                elif i.startswith(self.package):
                    n = i[len(self.package) + 1:]
                else:
                    n = i
                if modules.has_key(i):
                    impLst.append(n)
                elif self.showExternalImports:
                    impLst.append(n)
                    if not n in externalMods:
                        externalMods.append(n)
            classNames = []
            for cls in modules[module].classes.keys():
                className = modules[module].classes[cls].name
                if className not in classNames:
                    classNames.append(className)
            shape = self.__addModule(module, classNames, 0.0, 0.0)
            shapeRect = shape.sceneBoundingRect()
            shapes[module] = (shape, impLst)
            pn = p + shapeRect.width() + 10
            maxHeight = max(maxHeight, shapeRect.height())
            if pn > sceneRect.width():
                p = 10
                y += maxHeight + 10
                maxHeight = shapeRect.height()
                shape.setPos(p, y)
                p += shapeRect.width() + 10
            else:
                shape.setPos(p, y)
                p = pn
        
        for module in externalMods:
            shape = self.__addModule(module, [], 0.0, 0.0)
            shapeRect = shape.sceneBoundingRect()
            shapes[module] = (shape, [])
            pn = p + shapeRect.width() + 10
            maxHeight = max(maxHeight, shapeRect.height())
            if pn > sceneRect.width():
                p = 10
                y += maxHeight + 10
                maxHeight = shapeRect.height()
                shape.setPos(p, y)
                p += shapeRect.width() + 10
            else:
                shape.setPos(p, y)
                p = pn
        
        rect = self.umlView._getDiagramRect(10)
        sceneRect = self.umlView.sceneRect()
        if rect.width() > sceneRect.width():
            sceneRect.setWidth(rect.width())
        if rect.height() > sceneRect.height():
            sceneRect.setHeight(rect.height())
        self.umlView.setSceneSize(sceneRect.width(), sceneRect.height())
        
        self.__createAssociations(shapes)
        
    def __addModule(self, name, classes, x, y):
        """
        Private method to add a module to the diagram.
        
        @param name module name to be shown (string)
        @param classes list of class names contained in the module
            (list of strings)
        @param x x-coordinate (float)
        @param y y-coordinate (float)
        """
        classes.sort()
        impM = ModuleModel(name, classes)
        impW = ModuleItem(impM, x, y, scene = self.scene)
        return impW
        
    def __createAssociations(self, shapes):
        """
        Private method to generate the associations between the module shapes.
        
        @param shapes list of shapes
        """
        for module in shapes.keys():
            for rel in shapes[module][1]:
                assoc = AssociationItem(\
                        shapes[module][0], shapes[rel][0],
                        Imports)
                self.scene.addItem(assoc)
        
    def show(self):
        """
        Overriden method to show the dialog.
        """
        self.__buildImports()
        UMLDialog.show(self)
        
    def relayout(self):
        """
        Method to relayout the diagram.
        """
        self.__buildImports()
