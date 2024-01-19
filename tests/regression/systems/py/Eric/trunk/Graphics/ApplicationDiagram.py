# -*- coding: utf-8 -*-

# Copyright (c) 2007 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a dialog showing an imports diagram of the application.
"""

import os
import glob

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from KdeQt.KQProgressDialog import KQProgressDialog

from UMLDialog import UMLDialog
from PackageItem import PackageItem, PackageModel
from AssociationItem import AssociationItem, Imports
import GraphicsUtilities

import Utilities.ModuleParser
import Utilities

class ApplicationDiagram(UMLDialog):
    """
    Class implementing a dialog showing an imports diagram of the application.
    """
    def __init__(self, project, parent = None, name = None,  noModules = False):
        """
        Constructor
        
        @param project reference to the project object
        @param parent parent widget of the view (QWidget)
        @param name name of the view widget (QString or string)
        @keyparam noModules flag indicating, that no module names should be 
            shown (boolean)
        """
        self.project = project
        self.noModules = noModules
        
        UMLDialog.__init__(self, self.project.ppath, parent)
        
        if not name:
            self.setObjectName("ApplicationDiagram")
        else:
            self.setObjectName(name)
        
        self.connect(self.umlView, SIGNAL("relayout()"), self.relayout)
        
    def __buildModulesDict(self):
        """
        Private method to build a dictionary of modules contained in the application.
        
        @return dictionary of modules contained in the application.
        """
        moduleDict = {}
        mods = self.project.pdata["SOURCES"]
        modules = []
        for module in mods:
            modules.append(Utilities.normabsjoinpath(self.project.ppath, module))
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
                prog += 1
                if module.endswith("__init__.py"):
                    continue
                try: 
                    mod = Utilities.ModuleParser.readModule(module)
                except ImportError:
                    continue
                else:
                    name = mod.name
                    moduleDict[name] = mod
        finally:
            progress.setValue(tot)
        return moduleDict
        
    def __buildPackages(self):
        """
        Private method to build the packages shapes of the diagram.
        """
        project = os.path.splitdrive(self.project.ppath)[1].replace(os.sep, '.')[1:]
        packages = {}
        shapes = {}
        p = 10
        y = 10
        maxHeight = 0
        sceneRect = self.umlView.sceneRect()
        
        modules = self.__buildModulesDict()
        sortedkeys = modules.keys()
        sortedkeys.sort()
        
        # step 1: build a dictionary of packages
        for module in sortedkeys:
            l = module.split('.')
            package = '.'.join(l[:-1])
            if packages.has_key(package):
                packages[package][0].append(l[-1])
            else:
                packages[package] = ([l[-1]], [])
                
        # step 2: assign modules to dictionaries and update import relationship
        for module in sortedkeys:
            l = module.split('.')
            package = '.'.join(l[:-1])
            impLst = []
            for i in modules[module].imports:
                if modules.has_key(i):
                    impLst.append(i)
                else:
                    if i.find('.') == -1:
                        n = "%s.%s" % (modules[module].package, i)
                        if modules.has_key(n):
                            impLst.append(n)
                        else:
                            n = "%s.%s" % (project, i)
                            if modules.has_key(n):
                                impLst.append(n)
                            elif packages.has_key(n):
                                n = "%s.<<Dummy>>" % n
                                impLst.append(n)
                    else:
                        n = "%s.%s" % (project, i)
                        if modules.has_key(n):
                            impLst.append(n)
            for i in modules[module].from_imports.keys():
                if i.startswith('.'):
                    dots = len(i) - len(i.lstrip('.'))
                    if dots == 1:
                        i = i[1:]
                    elif dots > 1:
                        packagePath = os.path.dirname(modules[module].file)
                        hasInit = True
                        ppath = packagePath
                        while hasInit:
                            ppath = os.path.dirname(ppath)
                            hasInit = \
                                len(glob.glob(os.path.join(ppath, '__init__.*'))) > 0
                        shortPackage = \
                            packagePath.replace(ppath, '').replace(os.sep, '.')[1:]
                        packageList = shortPackage.split('.')[1:]
                        packageListLen = len(packageList)
                        i = '.'.join(packageList[:packageListLen - dots + 1] + [i[dots:]])
                
                if modules.has_key(i):
                    impLst.append(i)
                else:
                    if i.find('.') == -1:
                        n = "%s.%s" % (modules[module].package, i)
                        if modules.has_key(n):
                            impLst.append(n)
                        else:
                            n = "%s.%s" % (project, i)
                            if modules.has_key(n):
                                impLst.append(n)
                            elif packages.has_key(n):
                                n = "%s.<<Dummy>>" % n
                                impLst.append(n)
                    else:
                        n = "%s.%s" % (project, i)
                        if modules.has_key(n):
                            impLst.append(n)
            for imp in impLst:
                impPackage = '.'.join(imp.split('.')[:-1])
                if not impPackage in packages[package][1] and \
                   not impPackage == package:
                    packages[package][1].append(impPackage)
                    
        sortedkeys = packages.keys()
        sortedkeys.sort()
        for package in sortedkeys:
            if package:
                relPackage = package.replace(project, '')
                if relPackage and relPackage[0] == '.':
                    relPackage = relPackage[1:]
                else:
                    relPackage = unicode(self.trUtf8("<<Application>>"))
            else:
                relPackage = unicode(self.trUtf8("<<Others>>"))
            shape = self.__addPackage(relPackage, packages[package][0], 0.0, 0.0)
            shapeRect = shape.sceneBoundingRect()
            shapes[package] = (shape, packages[package][1])
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
        
    def __addPackage(self, name, modules, x, y):
        """
        Private method to add a package to the diagram.
        
        @param name package name to be shown (string)
        @param modules list of module names contained in the package
            (list of strings)
        @param x x-coordinate (float)
        @param y y-coordinate (float)
        """
        modules.sort()
        pm = PackageModel(name, modules)
        pw = PackageItem(pm, x, y, noModules = self.noModules, scene = self.scene)
        return pw
        
    def __createAssociations(self, shapes):
        """
        Private method to generate the associations between the package shapes.
        
        @param shapes list of shapes
        """
        for package in shapes.keys():
            for rel in shapes[package][1]:
                assoc = AssociationItem(\
                        shapes[package][0], shapes[rel][0],
                        Imports)
                self.scene.addItem(assoc)
        
    def show(self):
        """
        Overriden method to show the dialog.
        """
        self.__buildPackages()
        UMLDialog.show(self)
        
    def relayout(self):
        """
        Method to relayout the diagram.
        """
        self.__buildPackages()
