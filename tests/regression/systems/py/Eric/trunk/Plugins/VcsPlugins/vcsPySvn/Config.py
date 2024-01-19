# -*- coding: utf-8 -*-

# Copyright (c) 2004 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module defining configuration variables for the subversion package
"""

from PyQt4.QtCore import QStringList

# Available protocols fpr the repository URL
ConfigSvnProtocols = QStringList()
ConfigSvnProtocols.append('file://')
ConfigSvnProtocols.append('http://')
ConfigSvnProtocols.append('https://')
ConfigSvnProtocols.append('svn://')
ConfigSvnProtocols.append('svn+ssh://')
