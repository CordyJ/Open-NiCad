# -*- coding: utf-8 -*-

# Copyright (c) 2009 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a QAction subclass for open search.
"""

from PyQt4.QtCore import SIGNAL, QUrl
from PyQt4.QtGui import QPixmap, QIcon, QAction

import Helpviewer.HelpWindow

class OpenSearchEngineAction(QAction):
    """
    Class implementing a QAction subclass for open search.
    """
    def __init__(self, engine, parent = None):
        """
        Constructor
        
        @param engine reference to the open search engine object (OpenSearchEngine)
        @param parent reference to the parent object (QObject)
        """
        QAction.__init__(self, parent)
        
        self.__engine = engine
        if self.__engine.networkAccessManager() is None:
            self.__engine.setNetworkAccessManager(
                Helpviewer.HelpWindow.HelpWindow.networkAccessManager())
        
        self.setText(engine.name())
        self.__imageChanged()
        
        self.connect(engine, SIGNAL("imageChanged()"), self.__imageChanged)
    
    def __imageChanged(self):
        """
        Private slot handling a change of the associated image.
        """
        image = self.__engine.image()
        if image.isNull():
            self.setIcon(
                Helpviewer.HelpWindow.HelpWindow.icon(QUrl(self.__engine.imageUrl())))
        else:
            self.setIcon(QIcon(QPixmap.fromImage(image)))
