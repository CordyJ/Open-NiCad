# -*- coding: utf-8 -*-

# Copyright (c) 2006 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the Debugger General configuration page.
"""

import socket

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtNetwork import *

from KdeQt import KQInputDialog, KQMessageBox
from KdeQt.KQApplication import e4App

from E4Gui.E4Completers import E4FileCompleter, E4DirCompleter

from ConfigurationPageBase import ConfigurationPageBase
from Ui_DebuggerGeneralPage import Ui_DebuggerGeneralPage

import Preferences
import Utilities

class DebuggerGeneralPage(ConfigurationPageBase, Ui_DebuggerGeneralPage):
    """
    Class implementing the Debugger General configuration page.
    """
    def __init__(self):
        """
        Constructor
        """
        ConfigurationPageBase.__init__(self)
        self.setupUi(self)
        self.setObjectName("DebuggerGeneralPage")
        
        t = self.execLineEdit.whatsThis()
        if not t.isEmpty():
            t.append(Utilities.getPercentReplacementHelp())
            self.execLineEdit.setWhatsThis(t)
        
        try:
            backends = e4App().getObject("DebugServer").getSupportedLanguages()
            for backend in sorted(backends):
                self.passiveDbgBackendCombo.addItem(backend)
        except KeyError:
            self.passiveDbgGroup.setEnabled(False)
        
        t = self.consoleDbgEdit.whatsThis()
        if not t.isEmpty():
            t.append(Utilities.getPercentReplacementHelp())
            self.consoleDbgEdit.setWhatsThis(t)
        
        self.consoleDbgCompleter = E4FileCompleter(self.consoleDbgEdit)
        self.dbgTranslationLocalCompleter = E4DirCompleter(self.dbgTranslationLocalEdit)
        
        # set initial values
        interfaces = QStringList()
        networkInterfaces = QNetworkInterface.allInterfaces()
        for networkInterface in networkInterfaces:
            addressEntries = networkInterface.addressEntries()
            if len(addressEntries) > 0:
                for addressEntry in addressEntries:
                    if ":" in addressEntry.ip().toString() and not socket.has_ipv6:
                        continue    # IPv6 not supported by Python
                    interfaces.append(QString("%1 (%2)")\
                                      .arg(networkInterface.name())\
                                      .arg(addressEntry.ip().toString()))
        self.interfacesCombo.addItems(interfaces)
        interface = Preferences.getDebugger("NetworkInterface")
        if not socket.has_ipv6:
            # IPv6 not supported by Python
            self.all6InterfacesButton.setEnabled(False)
            if interface == "allv6":
                interface = "all"
        if interface == "all":
            self.allInterfacesButton.setChecked(True)
        elif interface == "allv6":
            self.all6InterfacesButton.setChecked(True)
        else:
            self.selectedInterfaceButton.setChecked(True)
            index = interfaces.indexOf(QRegExp(QString(".*%1.*").arg(interface)))
            self.interfacesCombo.setCurrentIndex(index)
        
        self.allowedHostsList.addItems(\
            Preferences.getDebugger("AllowedHosts"))
        
        self.remoteCheckBox.setChecked(\
            Preferences.getDebugger("RemoteDbgEnabled"))
        self.hostLineEdit.setText(\
            Preferences.getDebugger("RemoteHost"))
        self.execLineEdit.setText(\
            Preferences.getDebugger("RemoteExecution"))
        
        if self.passiveDbgGroup.isEnabled():
            self.passiveDbgCheckBox.setChecked(\
                Preferences.getDebugger("PassiveDbgEnabled"))
            self.passiveDbgPortSpinBox.setValue(\
                Preferences.getDebugger("PassiveDbgPort"))
            index = self.passiveDbgBackendCombo.findText(
                Preferences.getDebugger("PassiveDbgType"))
            if index == -1:
                index = 0
            self.passiveDbgBackendCombo.setCurrentIndex(index)
        
        self.debugEnvironReplaceCheckBox.setChecked(\
            Preferences.getDebugger("DebugEnvironmentReplace"))
        self.debugEnvironEdit.setText(\
            Preferences.getDebugger("DebugEnvironment"))
        self.automaticResetCheckBox.setChecked(\
            Preferences.getDebugger("AutomaticReset"))
        self.debugAutoSaveScriptsCheckBox.setChecked(\
            Preferences.getDebugger("Autosave"))
        self.consoleDbgCheckBox.setChecked(\
            Preferences.getDebugger("ConsoleDbgEnabled"))
        self.consoleDbgEdit.setText(\
            Preferences.getDebugger("ConsoleDbgCommand"))
        self.dbgPathTranslationCheckBox.setChecked(\
            Preferences.getDebugger("PathTranslation"))
        self.dbgTranslationRemoteEdit.setText(\
            Preferences.getDebugger("PathTranslationRemote"))
        self.dbgTranslationLocalEdit.setText(\
            Preferences.getDebugger("PathTranslationLocal"))
        self.debugThreeStateBreakPoint.setChecked(\
            Preferences.getDebugger("ThreeStateBreakPoints"))
        self.dontShowClientExitCheckBox.setChecked(\
            Preferences.getDebugger("SuppressClientExit"))
        self.exceptionBreakCheckBox.setChecked(\
            Preferences.getDebugger("BreakAlways"))
        
    def save(self):
        """
        Public slot to save the Debugger General (1) configuration.
        """
        Preferences.setDebugger("RemoteDbgEnabled", 
            int(self.remoteCheckBox.isChecked()))
        Preferences.setDebugger("RemoteHost", 
            self.hostLineEdit.text())
        Preferences.setDebugger("RemoteExecution", 
            self.execLineEdit.text())
        
        Preferences.setDebugger("PassiveDbgEnabled", 
            int(self.passiveDbgCheckBox.isChecked()))
        Preferences.setDebugger("PassiveDbgPort", 
            self.passiveDbgPortSpinBox.value())
        Preferences.setDebugger("PassiveDbgType", 
            self.passiveDbgBackendCombo.currentText())
        
        if self.allInterfacesButton.isChecked():
            Preferences.setDebugger("NetworkInterface", "all")
        elif self.all6InterfacesButton.isChecked():
            Preferences.setDebugger("NetworkInterface", "allv6")
        else:
            interface = self.interfacesCombo.currentText()
            interface = interface.section("(", 1, 1).section(")", 0, 0)
            if interface.isEmpty():
                Preferences.setDebugger("NetworkInterface", "all")
            else:
                Preferences.setDebugger("NetworkInterface", interface)
        
        allowedHosts = QStringList()
        for row in range(self.allowedHostsList.count()):
            allowedHosts.append(self.allowedHostsList.item(row).text())
        Preferences.setDebugger("AllowedHosts", allowedHosts)
        
        Preferences.setDebugger("DebugEnvironmentReplace", 
            int(self.debugEnvironReplaceCheckBox.isChecked()))
        Preferences.setDebugger("DebugEnvironment", 
            self.debugEnvironEdit.text())
        Preferences.setDebugger("AutomaticReset", 
            int(self.automaticResetCheckBox.isChecked()))
        Preferences.setDebugger("Autosave", 
            int(self.debugAutoSaveScriptsCheckBox.isChecked()))
        Preferences.setDebugger("ConsoleDbgEnabled", 
            int(self.consoleDbgCheckBox.isChecked()))
        Preferences.setDebugger("ConsoleDbgCommand", 
            self.consoleDbgEdit.text())
        Preferences.setDebugger("PathTranslation", 
            int(self.dbgPathTranslationCheckBox.isChecked()))
        Preferences.setDebugger("PathTranslationRemote",
            unicode(self.dbgTranslationRemoteEdit.text()))
        Preferences.setDebugger("PathTranslationLocal",
            unicode(self.dbgTranslationLocalEdit.text()))
        Preferences.setDebugger("ThreeStateBreakPoints",
            int(self.debugThreeStateBreakPoint.isChecked()))
        Preferences.setDebugger("SuppressClientExit",
            int(self.dontShowClientExitCheckBox.isChecked()))
        Preferences.setDebugger("BreakAlways",
            int(self.exceptionBreakCheckBox.isChecked()))
        
    def on_allowedHostsList_currentItemChanged(self, current, previous):
        """
        Private method set the state of the edit and delete button.
        
        @param current new current item (QListWidgetItem)
        @param previous previous current item (QListWidgetItem)
        """
        self.editAllowedHostButton.setEnabled(current is not None)
        self.deleteAllowedHostButton.setEnabled(current is not None)
        
    @pyqtSignature("")
    def on_addAllowedHostButton_clicked(self):
        """
        Private slot called to add a new allowed host.
        """
        allowedHost, ok = KQInputDialog.getText(\
            None,
            self.trUtf8("Add allowed host"),
            self.trUtf8("Enter the IP address of an allowed host"),
            QLineEdit.Normal)
        if ok and not allowedHost.isEmpty():
            if QHostAddress(allowedHost).protocol() in \
               [QAbstractSocket.IPv4Protocol, QAbstractSocket.IPv6Protocol]:
                self.allowedHostsList.addItem(allowedHost)
            else:
                KQMessageBox.critical(None,
                    self.trUtf8("Add allowed host"),
                    self.trUtf8("""<p>The entered address <b>%1</b> is not"""
                        """ a valid IP v4 or IP v6 address. Aborting...</p>""")\
                        .arg(allowedHost))
        
    @pyqtSignature("")
    def on_deleteAllowedHostButton_clicked(self):
        """
        Private slot called to delete an allowed host.
        """
        self.allowedHostsList.takeItem(self.allowedHostsList.currentRow())
        
    @pyqtSignature("")
    def on_editAllowedHostButton_clicked(self):
        """
        Private slot called to edit an allowed host.
        """
        allowedHost = self.allowedHostsList.currentItem().text()
        allowedHost, ok = KQInputDialog.getText(\
            None,
            self.trUtf8("Edit allowed host"),
            self.trUtf8("Enter the IP address of an allowed host"),
            QLineEdit.Normal,
            allowedHost)
        if ok and not allowedHost.isEmpty():
            if QHostAddress(allowedHost).protocol() in \
               [QAbstractSocket.IPv4Protocol, QAbstractSocket.IPv6Protocol]:
                self.allowedHostsList.currentItem().setText(allowedHost)
            else:
                KQMessageBox.critical(None,
                    self.trUtf8("Edit allowed host"),
                    self.trUtf8("""<p>The entered address <b>%1</b> is not"""
                        """ a valid IP v4 or IP v6 address. Aborting...</p>""")\
                        .arg(allowedHost))
    
def create(dlg):
    """
    Module function to create the configuration page.
    
    @param dlg reference to the configuration dialog
    """
    page = DebuggerGeneralPage()
    return page
