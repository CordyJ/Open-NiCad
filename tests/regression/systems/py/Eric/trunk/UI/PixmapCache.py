# -*- coding: utf-8 -*-

# Copyright (c) 2004 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a pixmap cache for icons.
"""

import os

from PyQt4.QtCore import QStringList
from PyQt4.QtGui import QPixmap, QIcon

class PixmapCache(object):
    """
    Class implementing a pixmap cache for icons.
    """
    def __init__(self):
        """
        Constructor
        """
        self.pixmapCache = {}
        self.searchPath = QStringList()

    def getPixmap(self, key):
        """
        Public method to retrieve a pixmap.

        @param key name of the wanted pixmap (string)
        @return the requested pixmap (QPixmap)
        """
        if key:
            try:
                return self.pixmapCache[key]
            except KeyError:
                if not os.path.isabs(key):
                    for path in self.searchPath:
                        pm = QPixmap(path + "/" + key)
                        if not pm.isNull():
                            break
                    else:
                        pm = QPixmap()
                else:
                    pm = QPixmap(key)
                self.pixmapCache[key] = pm
                return self.pixmapCache[key]
        return QPixmap()

    def addSearchPath(self, path):
        """
        Public method to add a path to the search path.

        @param path path to add (QString)
        """
        if not path in self.searchPath:
            self.searchPath.append(path)

pixCache = PixmapCache()

def getPixmap(key, cache = pixCache):
    """
    Module function to retrieve a pixmap.

    @param key name of the wanted pixmap (string)
    @return the requested pixmap (QPixmap)
    """
    return cache.getPixmap(key)

def getIcon(key, cache = pixCache):
    """
    Module function to retrieve an icon.

    @param key name of the wanted icon (string)
    @return the requested icon (QIcon)
    """
    return QIcon(cache.getPixmap(key))

def addSearchPath(path, cache = pixCache):
    """
    Module function to add a path to the search path.

    @param path path to add (QString)
    """
    cache.addSearchPath(path)
