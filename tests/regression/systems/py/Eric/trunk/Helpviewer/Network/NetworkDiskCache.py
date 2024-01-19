# -*- coding: utf-8 -*-

# Copyright (c) 2009 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a disk cache respecting privacy.
"""

from PyQt4.QtWebKit import QWebSettings
try:
    from PyQt4.QtNetwork import QNetworkDiskCache
    
    class NetworkDiskCache(QNetworkDiskCache):
        """
        Class implementing a disk cache respecting privacy.
        """
        def prepare(self, metaData):
            """
            Public method to prepare the disk cache file.
            
            @param metaData meta data for a URL (QNetworkCacheMetaData)
            @return reference to the IO device (QIODevice)
            """
            if QWebSettings.globalSettings().testAttribute(
                    QWebSettings.PrivateBrowsingEnabled):
                return None
            
            return QNetworkDiskCache.prepare(self, metaData)
    
except ImportError:
    NetworkDiskCache = None
