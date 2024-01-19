# -*- coding: utf-8 -*-

# Copyright (c) 2007 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#


"""
Module implementing a dialog showing the available plugins.
"""

import sys
import os
import zipfile
import cStringIO

from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4.QtNetwork import QHttp, QNetworkProxy

from KdeQt import KQMessageBox
from KdeQt.KQMainWindow import KQMainWindow

from Ui_PluginRepositoryDialog import Ui_PluginRepositoryDialog

from UI.AuthenticationDialog import AuthenticationDialog

from E4XML.XMLUtilities import make_parser
from E4XML.XMLErrorHandler import XMLErrorHandler, XMLFatalParseError
from E4XML.XMLEntityResolver import XMLEntityResolver
from E4XML.PluginRepositoryHandler import PluginRepositoryHandler

import Utilities
import Preferences

import UI.PixmapCache

from eric4config import getConfig

descrRole    = Qt.UserRole
urlRole      = Qt.UserRole + 1
filenameRole = Qt.UserRole + 2
authorRole   = Qt.UserRole + 3

class PluginRepositoryWidget(QWidget, Ui_PluginRepositoryDialog):
    """
    Class implementing a dialog showing the available plugins.
    
    @signal closeAndInstall emitted when the Close & Install button is pressed
    """
    def __init__(self, parent = None):
        """
        Constructor
        
        @param parent parent of this dialog (QWidget)
        """
        QWidget.__init__(self, parent)
        self.setupUi(self)
        
        self.__updateButton = \
            self.buttonBox.addButton(self.trUtf8("Update"), QDialogButtonBox.ActionRole)
        self.__downloadButton = \
            self.buttonBox.addButton(self.trUtf8("Download"), QDialogButtonBox.ActionRole)
        self.__downloadButton.setEnabled(False)
        self.__downloadCancelButton = \
            self.buttonBox.addButton(self.trUtf8("Cancel"), QDialogButtonBox.ActionRole)
        self.__installButton = \
            self.buttonBox.addButton(self.trUtf8("Close && Install"), 
                                     QDialogButtonBox.ActionRole)
        self.__downloadCancelButton.setEnabled(False)
        self.__installButton.setEnabled(False)
        
        self.repositoryList.headerItem().setText(self.repositoryList.columnCount(), "")
        self.repositoryList.header().setSortIndicator(0, Qt.AscendingOrder)
        
        self.pluginRepositoryFile = \
            os.path.join(Utilities.getConfigDir(), "PluginRepository")
        
        self.__http = None
        self.__doneMethod = None
        self.__inDownload = False
        self.__pluginsToDownload = []
        self.__pluginsDownloaded = QStringList()
        
        self.__populateList()
    
    @pyqtSignature("QAbstractButton*")
    def on_buttonBox_clicked(self, button):
        """
        Private slot to handle the click of a button of the button box.
        """
        if button == self.__updateButton:
            self.__updateList()
        elif button == self.__downloadButton:
            self.__downloadPlugins()
        elif button == self.__downloadCancelButton:
            self.__downloadCancel()
        elif button == self.__installButton:
            self.emit(SIGNAL("closeAndInstall"))
    
    def __formatDescription(self, lines):
        """
        Private method to format the description.
        
        @param lines lines of the description (QStringList)
        @return formatted description (QString)
        """
        # remove empty line at start and end
        newlines = lines[:]
        if len(newlines) and newlines[0] == '':
            del newlines[0]
        if len(newlines) and newlines[-1] == '':
            del newlines[-1]
        
        # replace empty lines by newline character
        index = 0
        while index < len(newlines):
            if newlines[index] == '':
                newlines[index] = '\n'
            index += 1
        
        # join lines by a blank
        return newlines.join(' ')
    
    @pyqtSignature("QTreeWidgetItem*, QTreeWidgetItem*")
    def on_repositoryList_currentItemChanged(self, current, previous):
        """
        Private slot to handle the change of the current item.
        
        @param current reference to the new current item (QTreeWidgetItem)
        @param previous reference to the old current item (QTreeWidgetItem)
        """
        if self.__repositoryMissing or current is None:
            return
        
        self.urlEdit.setText(current.data(0, urlRole).toString())
        self.descriptionEdit.setPlainText(\
            self.__formatDescription(current.data(0, descrRole).toStringList()))
        self.authorEdit.setText(current.data(0, authorRole).toString())
    
    def __selectedItems(self):
        """
        Private method to get all selected items without the toplevel ones.
        
        @return list of selected items (QList)
        """
        ql = self.repositoryList.selectedItems()
        for index in range(self.repositoryList.topLevelItemCount()):
            ti = self.repositoryList.topLevelItem(index)
            if ti in ql:
                ql.remove(ti)
        return ql
    
    @pyqtSignature("")
    def on_repositoryList_itemSelectionChanged(self):
        """
        Private slot to handle a change of the selection.
        """
        self.__downloadButton.setEnabled(len(self.__selectedItems()))
    
    def __updateList(self):
        """
        Private slot to download a new list and display the contents.
        """
        url = Preferences.getUI("PluginRepositoryUrl")
        self.__downloadFile(url, 
                            self.pluginRepositoryFile, 
                            self.__downloadRepositoryFileDone)
    
    def __downloadRepositoryFileDone(self, status, filename):
        """
        Private method called after the repository file was downloaded.
        
        @param status flaging indicating a successful download (boolean)
        @param filename full path of the downloaded file (QString)
        """
        self.__populateList()
    
    def __downloadPluginDone(self, status, filename):
        """
        Private method called, when the download of a plugin is finished.
        
        @param status flaging indicating a successful download (boolean)
        @param filename full path of the downloaded file (QString)
        """
        if status:
            self.__pluginsDownloaded.append(filename)
        
        del self.__pluginsToDownload[0]
        if len(self.__pluginsToDownload):
            self.__downloadPlugin()
        else:
            self.__downloadPluginsDone()
    
    def __downloadPlugin(self):
        """
        Private method to download the next plugin.
        """
        self.__downloadFile(self.__pluginsToDownload[0][0], 
                            self.__pluginsToDownload[0][1], 
                            self.__downloadPluginDone)
    
    def __downloadPlugins(self):
        """
        Private slot to download the selected plugins.
        """
        self.__pluginsDownloaded.clear()
        self.__pluginsToDownload = []
        self.__downloadButton.setEnabled(False)
        self.__installButton.setEnabled(False)
        for itm in self.repositoryList.selectedItems():
            if itm not in [self.__stableItem, self.__unstableItem, self.__unknownItem]:
                url = itm.data(0, urlRole).toString()
                filename = os.path.join(\
                    unicode(Preferences.getPluginManager("DownloadPath")),
                    unicode(itm.data(0, filenameRole).toString()))
                self.__pluginsToDownload.append((url, filename))
        self.__downloadPlugin()
    
    def __downloadPluginsDone(self):
        """
        Private method called, when the download of the plugins is finished.
        """
        self.__downloadButton.setEnabled(len(self.__selectedItems()))
        self.__installButton.setEnabled(True)
        self.__doneMethod = None
        KQMessageBox.information(None,
            self.trUtf8("Download Plugin Files"),
            self.trUtf8("""The requested plugins were downloaded."""))
        self.downloadProgress.setValue(0)
        
        # repopulate the list to update the refresh icons
        self.__populateList()
    
    def __resortRepositoryList(self):
        """
        Private method to resort the tree.
        """
        self.repositoryList.sortItems(self.repositoryList.sortColumn(), 
                                      self.repositoryList.header().sortIndicatorOrder())
    
    def __populateList(self):
        """
        Private method to populate the list of available plugins.
        """
        self.repositoryList.clear()
        self.__stableItem = None
        self.__unstableItem = None
        self.__unknownItem = None
        
        self.downloadProgress.setValue(0)
        self.__doneMethod = None
        
        if os.path.exists(self.pluginRepositoryFile):
            self.__repositoryMissing = False
            try:
                f = open(self.pluginRepositoryFile, "rb")
                line = f.readline()
                dtdLine = f.readline()
                f.close()
            except IOError:
                KQMessageBox.critical(None,
                    self.trUtf8("Read plugins repository file"),
                    self.trUtf8("<p>The plugins repository file <b>%1</b> "
                                "could not be read. Select Update</p>")\
                        .arg(self.pluginRepositoryFile))
                return
            
            # now read the file
            if line.startswith('<?xml'):
                parser = make_parser(dtdLine.startswith("<!DOCTYPE"))
                handler = PluginRepositoryHandler(self)
                er = XMLEntityResolver()
                eh = XMLErrorHandler()
                
                parser.setContentHandler(handler)
                parser.setEntityResolver(er)
                parser.setErrorHandler(eh)
                
                try:
                    f = open(self.pluginRepositoryFile, "rb")
                    try:
                        try:
                            parser.parse(f)
                        except UnicodeEncodeError:
                            f.seek(0)
                            buf = cStringIO.StringIO(f.read())
                            parser.parse(buf)
                    finally:
                        f.close()
                except IOError:
                    KQMessageBox.critical(None,
                        self.trUtf8("Read plugins repository file"),
                        self.trUtf8("<p>The plugins repository file <b>%1</b> "
                                    "could not be read. Select Update</p>")\
                            .arg(self.pluginRepositoryFile))
                    return
                except XMLFatalParseError:
                    pass
                
                eh.showParseMessages()
                
                self.repositoryList.resizeColumnToContents(0)
                self.repositoryList.resizeColumnToContents(1)
                self.repositoryList.resizeColumnToContents(2)
                self.__resortRepositoryList()
            else:
                KQMessageBox.critical(None,
                    self.trUtf8("Read plugins repository file"),
                    self.trUtf8("<p>The plugins repository file <b>%1</b> "
                                "has an unsupported format.</p>")\
                        .arg(self.pluginRepositoryFile))
        else:
            self.__repositoryMissing = True
            QTreeWidgetItem(self.repositoryList, \
                QStringList() \
                    << "" \
                    << self.trUtf8("No plugin repository file available."
                                   "\nSelect Update."))
            self.repositoryList.resizeColumnToContents(1)
    
    def __downloadFile(self, url, filename, doneMethod = None):
        """
        Private slot to download the given file.
        
        @param url URL for the download (string or QString)
        @param filename local name of the file (string or QString)
        @param doneMethod method to be called when done
        """
        if self.__http is None:
            self.__http = QHttp()
            self.connect(self.__http, SIGNAL("done(bool)"), self.__downloadFileDone)
            self.connect(self.__http, SIGNAL("dataReadProgress(int, int)"), 
                self.__dataReadProgress)
            self.connect(self.__http, 
                SIGNAL('proxyAuthenticationRequired(const QNetworkProxy &, QAuthenticator *)'),
                self.__proxyAuthenticationRequired)
            self.connect(self.__http, SIGNAL("sslErrors(const QList<QSslError>&)"), 
                self.__sslErrors)
        
        if Preferences.getUI("UseProxy"):
            host = Preferences.getUI("ProxyHost")
            if host.isEmpty():
                KQMessageBox.critical(None,
                    self.trUtf8("Error downloading file"),
                    self.trUtf8("""Proxy usage was activated"""
                                """ but no proxy host configured."""))
                return
            else:
                pProxyType = Preferences.getUI("ProxyType")
                if pProxyType == 0:
                    proxyType = QNetworkProxy.HttpProxy
                elif pProxyType == 1:
                    proxyType = QNetworkProxy.HttpCachingProxy
                elif pProxyType == 2:
                    proxyType = QNetworkProxy.Socks5Proxy
                self.__proxy = QNetworkProxy(proxyType, host, 
                    Preferences.getUI("ProxyPort"),
                    Preferences.getUI("ProxyUser"),
                    Preferences.getUI("ProxyPassword"))
                self.__http.setProxy(self.__proxy)
        
        self.__updateButton.setEnabled(False)
        self.__downloadButton.setEnabled(False)
        self.__downloadCancelButton.setEnabled(True)
        
        self.statusLabel.setText(url)
        
        self.__doneMethod = doneMethod
        self.__downloadURL = url
        self.__downloadFileName = QString(filename)
        self.__downloadIODevice = QFile(self.__downloadFileName + ".tmp")
        self.__downloadCancelled = False
        
        if QUrl(url).scheme().toLower() == 'https':
            connectionMode = QHttp.ConnectionModeHttps
        else:
            connectionMode = QHttp.ConnectionModeHttp
        self.__http.setHost(QUrl(url).host(), connectionMode, QUrl(url).port(0))
        self.__http.get(QUrl(url).path(), self.__downloadIODevice)
    
    def __downloadFileDone(self, error):
        """
        Private method called, after the file has been downloaded
        from the internet.
        
        @param error flag indicating an error condition (boolean)
        """
        self.__updateButton.setEnabled(True)
        self.__downloadCancelButton.setEnabled(False)
        self.statusLabel.setText("  ")
        
        ok = True
        if error or self.__http.lastResponse().statusCode() != 200:
            ok = False
            if not self.__downloadCancelled:
                if error:
                    msg = self.__http.errorString()
                else:
                    msg = self.__http.lastResponse().reasonPhrase()
                KQMessageBox.warning(None,
                    self.trUtf8("Error downloading file"),
                    self.trUtf8(
                        """<p>Could not download the requested file from %1.</p>"""
                        """<p>Error: %2</p>"""
                    ).arg(self.__downloadURL).arg(msg)
                )
            self.downloadProgress.setValue(0)
            self.__downloadURL = None
            self.__downloadIODevice.remove()
            self.__downloadIODevice = None
            if self.repositoryList.topLevelItemCount():
                if self.repositoryList.currentItem() is None:
                    self.repositoryList.setCurrentItem(\
                        self.repositoryList.topLevelItem(0))
                else:
                    self.__downloadButton.setEnabled(len(self.__selectedItems()))
            return
        
        if QFile.exists(self.__downloadFileName):
            QFile.remove(self.__downloadFileName)
        self.__downloadIODevice.rename(self.__downloadFileName)
        self.__downloadIODevice = None
        self.__downloadURL = None
        
        if self.__doneMethod is not None:
            self.__doneMethod(ok, self.__downloadFileName)
    
    def __downloadCancel(self):
        """
        Private slot to cancel the current download.
        """
        if self.__http is not None:
            self.__downloadCancelled = True
            self.__pluginsToDownload = []
            self.__http.abort()
    
    def __dataReadProgress(self, done, total):
        """
        Private slot to show the download progress.
        
        @param done number of bytes downloaded so far (integer)
        @param total total bytes to be downloaded (integer)
        """
        self.downloadProgress.setMaximum(total)
        self.downloadProgress.setValue(done)
    
    def addEntry(self, name, short, description, url, author, version, filename, status):
        """
        Public method to add an entry to the list.
        
        @param name data for the name field (string or QString)
        @param short data for the short field (string or QString)
        @param description data for the description field (list of string or QStringList)
        @param url data for the url field (string or QString)
        @param author data for the author field (string or QString)
        @param version data for the version field (string or QString)
        @param filename data for the filename field (string or QString)
        @param status status of the plugin (string [stable, unstable, unknown])
        """
        if status == "stable":
            if self.__stableItem is None:
                self.__stableItem = \
                    QTreeWidgetItem(self.repositoryList, 
                                    QStringList(self.trUtf8("Stable")))
                self.__stableItem.setExpanded(True)
            parent = self.__stableItem
        elif status == "unstable":
            if self.__unstableItem is None:
                self.__unstableItem = \
                    QTreeWidgetItem(self.repositoryList, 
                                    QStringList(self.trUtf8("Unstable")))
                self.__unstableItem.setExpanded(True)
            parent = self.__unstableItem
        else:
            if self.__unknownItem is None:
                self.__unknownItem = \
                    QTreeWidgetItem(self.repositoryList, 
                                    QStringList(self.trUtf8("Unknown")))
                self.__unknownItem.setExpanded(True)
            parent = self.__unknownItem
        itm = QTreeWidgetItem(parent, 
                              QStringList() << name << version << short)
        
        itm.setData(0, urlRole, QVariant(url))
        itm.setData(0, filenameRole, QVariant(filename))
        itm.setData(0, authorRole, QVariant(author))
        if type(description) == type([]):
            descr = QStringList()
            for line in description:
                descr.append(line)
        else:
            descr = description
        itm.setData(0, descrRole, QVariant(descr))
        
        if self.__isUpToDate(filename, version):
            itm.setIcon(1, UI.PixmapCache.getIcon("empty.png"))
        else:
            itm.setIcon(1, UI.PixmapCache.getIcon("download.png"))
    
    def __isUpToDate(self, filename, version):
        """
        Private method to check, if the given archive is up-to-date.
        
        @param filename data for the filename field (string or QString)
        @param version data for the version field (string or QString)
        @return flag indicating up-to-date (boolean)
        """
        archive = os.path.join(unicode(Preferences.getPluginManager("DownloadPath")),
                               filename)

        # check, if the archive exists
        if not os.path.exists(archive):
            return False
        
        # check, if the archive is a valid zip file
        if not zipfile.is_zipfile(archive):
            return False
        
        zip = zipfile.ZipFile(archive, "r")
        try:
            aversion = zip.read("VERSION")
        except KeyError:
            aversion = ""
        zip.close()
        
        return aversion == version
    
    def __proxyAuthenticationRequired(self, proxy, auth):
        """
        Private slot to handle a proxy authentication request.
        
        @param proxy reference to the proxy object (QNetworkProxy)
        @param auth reference to the authenticator object (QAuthenticator)
        """
        info = self.trUtf8("<b>Connect to proxy '%1' using:</b>")\
            .arg(Qt.escape(proxy.hostName()))
        
        dlg = AuthenticationDialog(info, proxy.user(), True)
        if dlg.exec_() == QDialog.Accepted:
            username, password = dlg.getData()
            auth.setUser(username)
            auth.setPassword(password)
            if dlg.shallSave():
                Preferences.setUI("ProxyUser", username)
                Preferences.setUI("ProxyPassword", password)
    
    def __sslErrors(self, sslErrors):
        """
        Private slot to handle SSL errors.
        
        @param sslErrors list of SSL errors (list of QSslError)
        """
        errorStrings = QStringList()
        for err in sslErrors:
            errorStrings.append(err.errorString())
        errorString = errorStrings.join('.<br />')
        ret = KQMessageBox.warning(self,
            self.trUtf8("SSL Errors"),
            self.trUtf8("""<p>SSL Errors:</p>"""
                        """<p>%1</p>"""
                        """<p>Do you want to ignore these errors?</p>""")\
                .arg(errorString),
            QMessageBox.StandardButtons(\
                QMessageBox.No | \
                QMessageBox.Yes),
            QMessageBox.No)
        if ret == QMessageBox.Yes:
            self.__http.ignoreSslErrors()
        else:
            self.__downloadCancelled = True
            self.__http.abort()
    
    def getDownloadedPlugins(self):
        """
        Public method to get the list of recently downloaded plugin files.
        
        @return list of plugin filenames (QStringList)
        """
        return self.__pluginsDownloaded

class PluginRepositoryDialog(QDialog):
    """
    Class for the dialog variant.
    """
    def __init__(self, parent = None):
        """
        Constructor
        
        @param parent reference to the parent widget (QWidget)
        """
        QDialog.__init__(self, parent)
        self.setSizeGripEnabled(True)
        
        self.__layout = QVBoxLayout(self)
        self.__layout.setMargin(0)
        self.setLayout(self.__layout)
        
        self.cw = PluginRepositoryWidget(self)
        size = self.cw.size()
        self.__layout.addWidget(self.cw)
        self.resize(size)
        
        self.connect(self.cw.buttonBox, SIGNAL("accepted()"), self.accept)
        self.connect(self.cw.buttonBox, SIGNAL("rejected()"), self.reject)
        self.connect(self.cw, SIGNAL("closeAndInstall"), self.__closeAndInstall)
        
    def __closeAndInstall(self):
        """
        Private slot to handle the closeAndInstall signal.
        """
        self.done(QDialog.Accepted + 1)
    
    def getDownloadedPlugins(self):
        """
        Public method to get the list of recently downloaded plugin files.
        
        @return list of plugin filenames (QStringList)
        """
        return self.cw.getDownloadedPlugins()

class PluginRepositoryWindow(KQMainWindow):
    """
    Main window class for the standalone dialog.
    """
    def __init__(self, parent = None):
        """
        Constructor
        
        @param parent reference to the parent widget (QWidget)
        """
        KQMainWindow.__init__(self, parent)
        self.cw = PluginRepositoryWidget(self)
        size = self.cw.size()
        self.setCentralWidget(self.cw)
        self.resize(size)
        
        self.connect(self.cw.buttonBox, SIGNAL("accepted()"), self.close)
        self.connect(self.cw.buttonBox, SIGNAL("rejected()"), self.close)
        self.connect(self.cw, SIGNAL("closeAndInstall"), self.__startPluginInstall)
    
    def __startPluginInstall(self):
        """
        Private slot to start the eric4 plugin installation dialog.
        """
        proc = QProcess()
        applPath = os.path.join(getConfig("ericDir"), "eric4-plugininstall.py")
        
        args = QStringList()
        args.append(applPath)
        args += self.cw.getDownloadedPlugins()
        
        if not os.path.isfile(applPath) or not proc.startDetached(sys.executable, args):
            KQMessageBox.critical(self,
                self.trUtf8('Process Generation Error'),
                self.trUtf8(
                    '<p>Could not start the process.<br>'
                    'Ensure that it is available as <b>%1</b>.</p>'
                ).arg(applPath),
                self.trUtf8('OK'))
        
        self.close()
