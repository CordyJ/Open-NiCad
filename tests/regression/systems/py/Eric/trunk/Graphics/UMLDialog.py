# -*- coding: utf-8 -*-

# Copyright (c) 2007 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a dialog showing UML like diagrams.
"""

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from KdeQt.KQMainWindow import KQMainWindow

from UMLGraphicsView import UMLGraphicsView

import UI.Config
import UI.PixmapCache

class UMLDialog(KQMainWindow):
    """
    Class implementing a dialog showing UML like diagrams.
    """
    def __init__(self, diagramName = "Unnamed", parent = None, name = None):
        """
        Constructor
        
        @param parent parent widget of the view (QWidget)
        @param name name of the view widget (QString or string)
        """
        KQMainWindow.__init__(self, parent)
        
        if not name:
            self.setObjectName("UMLDialog")
        else:
            self.setObjectName(name)
        
        self.scene = QGraphicsScene(0.0, 0.0, 800.0, 600.0)
        self.umlView = UMLGraphicsView(self.scene, diagramName, self, "umlView")
        
        self.closeAct = \
            QAction(UI.PixmapCache.getIcon("close.png"),
                    self.trUtf8("Close"), self)
        self.connect(self.closeAct, SIGNAL("triggered()"), self.close)
        
        self.windowToolBar = QToolBar(self.trUtf8("Window"), self)
        self.windowToolBar.setIconSize(UI.Config.ToolBarIconSize)
        self.windowToolBar.addAction(self.closeAct)
        
        self.umlToolBar = self.umlView.initToolBar()
        
        self.addToolBar(Qt.TopToolBarArea, self.windowToolBar)
        self.addToolBar(Qt.TopToolBarArea, self.umlToolBar)
        
        self.setCentralWidget(self.umlView)
