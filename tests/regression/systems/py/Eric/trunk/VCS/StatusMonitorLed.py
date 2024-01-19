# -*- coding: utf-8 -*-

# Copyright (c) 2007 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a LED to indicate the status of the VCS status monitor thread.
"""

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from KdeQt import KQInputDialog

from E4Gui.E4Led import E4Led, E4LedRectangular

import Preferences

class StatusMonitorLed(E4Led):
    """
    Class implementing a LED to indicate the status of the VCS status monitor thread.
    """
    def __init__(self, project, parent):
        """
        Constructor
        
        @param project reference to the project object (Project.Project)
        @param parent reference to the parent object (QWidget)
        """
        E4Led.__init__(self, parent, shape = E4LedRectangular, rectRatio = 1.0)
        
        self.project = project
        self.vcsMonitorLedColors = {
            "off"       : QColor(Qt.lightGray),
            "ok"        : QColor(Qt.green),
            "nok"       : QColor(Qt.red),
            "op"        : QColor(Qt.yellow),
            "send"      : QColor(Qt.blue), 
            "wait"      : QColor(Qt.cyan), 
            "timeout"   : QColor(Qt.darkRed)
        }
        self.__on = False
        
        self.setWhatsThis(self.trUtf8(
            """<p>This LED indicates the operating"""
            """ status of the VCS monitor thread (off = monitoring off,"""
            """ green = monitoring on and ok, red = monitoring on, but not ok,"""
            """ yellow = checking VCS status). A status description is given"""
            """ in the tooltip.</p>"""
        ))
        self.setToolTip(\
            self.trUtf8("Repository status checking is switched off")
        )
        self.setColor(self.vcsMonitorLedColors["off"])
        
        # define a context menu
        self.__menu = QMenu(self)
        self.__checkAct = \
            self.__menu.addAction(self.trUtf8("Check status"), self.__checkStatus)
        self.__intervalAct = \
            self.__menu.addAction(self.trUtf8("Set interval..."), self.__setInterval)
        self.__menu.addSeparator()
        self.__onAct  = \
            self.__menu.addAction(self.trUtf8("Switch on"), self.__switchOn)
        self.__offAct = \
            self.__menu.addAction(self.trUtf8("Switch off"), self.__switchOff)
        self.__checkActions()
        
        # connect signals to our slots
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.connect(self, SIGNAL("customContextMenuRequested(const QPoint &)"),
                     self._showContextMenu)
        self.connect(self.project, SIGNAL('vcsStatusMonitorStatus(QString, QString)'),
                     self.__projectVcsMonitorStatus)
    
    def __checkActions(self):
        """
        Private method to set the enabled status of the context menu actions.
        """
        if self.project.pudata["VCSSTATUSMONITORINTERVAL"]:
            vcsStatusMonitorInterval = self.project.pudata["VCSSTATUSMONITORINTERVAL"][0]
        else:
            vcsStatusMonitorInterval = Preferences.getVCS("StatusMonitorInterval")
        self.__checkAct.setEnabled(self.__on)
        self.__intervalAct.setEnabled(self.__on)
        self.__onAct.setEnabled((not self.__on) and vcsStatusMonitorInterval > 0)
        self.__offAct.setEnabled(self.__on)
        
    def __projectVcsMonitorStatus(self, status, statusMsg):
        """
        Private method to receive the status monitor status.
        
        @param status status of the monitoring thread (QString, ok, nok or off)
        @param statusMsg explanotory text for the signaled status (QString)
        """
        self.setColor(self.vcsMonitorLedColors[unicode(status)])
        self.setToolTip(statusMsg)
        
        self.__on = unicode(status) != 'off'
    
    def _showContextMenu(self, coord):
        """
        Protected slot to show the context menu.
        
        @param coord the position of the mouse pointer (QPoint)
        """
        if not self.project.isOpen():
            return
        
        self.__checkActions()
        self.__menu.popup(self.mapToGlobal(coord))
    
    def __checkStatus(self):
        """
        Private slot to initiate a new status check.
        """
        self.project.checkVCSStatus()
    
    def __setInterval(self):
        """
        Private slot to change the status check interval.
        """
        interval,  ok = KQInputDialog.getInteger(\
            None,
            self.trUtf8("VCS Status Monitor"),
            self.trUtf8("Enter monitor interval [s]"),
            self.project.getStatusMonitorInterval(), 
            0, 3600, 1)
        if ok:
            self.project.setStatusMonitorInterval(interval)
    
    def __switchOn(self):
        """
        Private slot to switch the status monitor thread to On.
        """
        self.project.startStatusMonitor()
    
    def __switchOff(self):
        """
        Private slot to switch the status monitor thread to Off.
        """
        self.project.stopStatusMonitor()
