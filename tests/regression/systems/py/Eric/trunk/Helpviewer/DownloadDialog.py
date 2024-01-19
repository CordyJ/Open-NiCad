# -*- coding: utf-8 -*-

# Copyright (c) 2008 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the download dialog.
"""

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtNetwork import QNetworkReply, QNetworkAccessManager, QNetworkRequest

from KdeQt import KQFileDialog, KQMessageBox

import Preferences

import Helpviewer.HelpWindow

from Ui_DownloadDialog import Ui_DownloadDialog

class DownloadDialog(QWidget, Ui_DownloadDialog):
    """
    Class implementing the download dialog.
    
    @signal done() emitted just before the dialog is closed
    """
    def __init__(self, reply = None, requestFilename = False, webPage = None, 
                 download = False, parent = None):
        """
        Constructor
        
        @param reply reference to the network reply object (QNetworkReply)
        @param requestFilename flag indicating to ask the user for a filename (boolean)
        @param webPage reference to the web page object the download originated 
            from (QWebPage)
        @param download flag indicating a download operation (boolean)
        @param parent reference to the parent widget (QWidget)
        """
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.setAttribute(Qt.WA_DeleteOnClose)
        
        self.__tryAgainButton = \
            self.buttonBox.addButton(self.trUtf8("Try Again"), 
                                     QDialogButtonBox.ActionRole)
        self.__stopButton = \
            self.buttonBox.addButton(self.trUtf8("Stop"), QDialogButtonBox.ActionRole)
        self.__openButton = self.buttonBox.button(QDialogButtonBox.Open)
        self.__closeButton = self.buttonBox.button(QDialogButtonBox.Close)
        
        self.__tryAgainButton.setEnabled(False)
        self.__closeButton.setEnabled(False)
        self.__openButton.setEnabled(False)
        self.keepOpenCheckBox.setChecked(True)
        
        icon = self.style().standardIcon(QStyle.SP_FileIcon)
        self.fileIcon.setPixmap(icon.pixmap(48, 48))
        
        self.__reply = reply
        self.__requestFilename = requestFilename
        self.__page = webPage
        self.__toDownload = download
        self.__bytesReceived = 0
        self.__downloadTime = QTime()
        self.__output = QFile()
        
        self.__initialize()
    
    def __initialize(self):
        """
        Private method to (re)initialize the dialog.
        """
        if self.__reply is None:
            return
        
        self.__startedSaving = False
        self.__downloadFinished = False
        
        self.__url = self.__reply.url()
        self.__reply.setParent(self)
        self.connect(self.__reply, SIGNAL("readyRead()"), self.__readyRead)
        self.connect(self.__reply, SIGNAL("error(QNetworkReply::NetworkError)"), 
                     self.__networkError)
        self.connect(self.__reply, SIGNAL("downloadProgress(qint64, qint64)"), 
                     self.__downloadProgress)
        self.connect(self.__reply, SIGNAL("metaDataChanged()"), 
                     self.__metaDataChanged)
        self.connect(self.__reply, SIGNAL("finished()"), self.__finished)
        
        # reset info
        self.infoLabel.clear()
        self.progressBar.setValue(0)
        self.__getFileName()
        
        # start timer for the download estimation
        self.__downloadTime.start()
        
        if self.__reply.error() != QNetworkReply.NoError:
            self.__networkError()
            self.__finished()
    
    def __getFileName(self):
        """
        Private method to get the filename to save to from the user.
        """
        downloadDirectory = Preferences.getUI("DownloadPath")
        if downloadDirectory.isEmpty():
            downloadDirectory = \
                QDesktopServices.storageLocation(QDesktopServices.DocumentsLocation)
        if not downloadDirectory.isEmpty():
            downloadDirectory += '/'
        
        defaultFileName = self.__saveFileName(downloadDirectory)
        fileName = defaultFileName
        baseName = QFileInfo(fileName).completeBaseName()
        self.__autoOpen = False
        if not self.__toDownload:
            res = KQMessageBox.question(None,
                self.trUtf8("Downloading"),
                self.trUtf8("""<p>You are about to download the file <b>%1</b>.</p>"""
                            """<p>What do you want to do?</p>""").arg(baseName),
                QMessageBox.StandardButtons(\
                    QMessageBox.Open | \
                    QMessageBox.Save))
            self.__autoOpen = res == QMessageBox.Open
            fileName = QDesktopServices.storageLocation(QDesktopServices.TempLocation) + \
                        '/' + baseName
        
        if not self.__autoOpen and self.__requestFilename:
            fileName = KQFileDialog.getSaveFileName(\
                None,
                self.trUtf8("Save File"),
                defaultFileName,
                QString(),
                None)
            if fileName.isEmpty():
                self.__reply.close()
                if not self.keepOpenCheckBox.isChecked():
                    self.close()
                else:
                    self.filenameLabel.setText(self.trUtf8("Download canceled: %1")\
                        .arg(QFileInfo(defaultFileName).fileName()))
                    self.__stop()
                return
        
        self.__output.setFileName(fileName)
        self.filenameLabel.setText(QFileInfo(self.__output.fileName()).fileName())
        if self.__requestFilename:
            self.__readyRead()
    
    def __saveFileName(self, directory):
        """
        Private method to calculate a name for the file to download.
        
        @param directory name of the directory to store the file into (QString)
        @return proposed filename (QString)
        """
        path = QString()
        if self.__reply.hasRawHeader("Content-Disposition"):
            header = QString(self.__reply.rawHeader("Content-Disposition"))
            if not header.isEmpty():
                pos = header.indexOf("filename=")
                if pos != -1:
                    path = header[pos + 9:]
                    if path.startsWith('"') and path.endsWith('"'):
                        path = path[1:-1]
        if path.isEmpty():
            path = self.__url.path()
        
        info = QFileInfo(path)
        baseName = info.completeBaseName()
        endName = info.suffix()
        
        if baseName.isEmpty():
            baseName = QString("unnamed_download")
        
        name = directory + baseName
        if not endName.isEmpty():
           name += '.' + endName
        i = 1
        while QFile.exists(name):
            # file exists already, don't overwrite
            name = directory + baseName + '-' + QString.number(i)
            if not endName.isEmpty():
                name += '.' + endName
            i += 1
        return name
    
    @pyqtSignature("QAbstractButton*")
    def on_buttonBox_clicked(self, button):
        """
        Private slot called by a button of the button box clicked.
        
        @param button button that was clicked (QAbstractButton)
        """
        if button == self.__closeButton:
            self.close()
        elif button == self.__openButton:
            self.__open()
        elif button == self.__stopButton:
            self.__stop()
        elif button == self.__tryAgainButton:
            self.__tryAgain()
    
    def __stop(self):
        """
        Private slot to stop the download.
        """
        self.__stopButton.setEnabled(False)
        self.__closeButton.setEnabled(True)
        self.__tryAgainButton.setEnabled(True)
        self.__reply.abort()
    
    def __open(self):
        """
        Private slot to open the downloaded file.
        """
        info = QFileInfo(self.__output)
        url = QUrl.fromLocalFile(info.absoluteFilePath())
        QDesktopServices.openUrl(url)
    
    def __tryAgain(self):
        """
        Private slot to retry the download.
        """
        self.__tryAgainButton.setEnabled(False)
        self.__closeButton.setEnabled(False)
        self.__stopButton.setEnabled(True)
        
        if self.__page:
            nam = self.__page.networkAccessManager()
        else:
            nam = QNetworkAccessManager()
        reply = nam.get(QNetworkRequest(self.__url))
        if self.__reply:
            self.__reply.deleteLater()
        if self.__output.exists():
            self.__output.remove()
        self.__reply = reply
        self.__initialize()
    
    def __readyRead(self):
        """
        Private slot to read the available data.
        """
        if self.__requestFilename and self.__output.fileName().isEmpty():
            return
        
        if not self.__output.isOpen():
            # in case someone else has already put a file there
            if not self.__requestFilename:
                self.__getFileName()
            if not self.__output.open(QIODevice.WriteOnly):
                self.infoLabel.setText(self.trUtf8("Error opening save file: %1")\
                    .arg(self.__output.errorString()))
                self.__stopButton.click()
                return
        
        bytesWritten = self.__output.write(self.__reply.readAll())
        if bytesWritten == -1:
            self.infoLabel.setText(self.trUtf8("Error saving: %1")\
                .arg(self.__output.errorString()))
            self.__stopButton.click()
        else:
            size = self.__reply.header(QNetworkRequest.ContentLengthHeader).toInt()[0]
            if size == bytesWritten:
                self.__downloadProgress(size, size)
                self.__downloadFinished = True
            self.__startedSaving = True
            if self.__downloadFinished:
                self.__finished()
    
    def __networkError(self):
        """
        Private slot to handle a network error.
        """
        if self.__reply.error() != QNetworkReply.OperationCanceledError:
            self.infoLabel.setText(self.trUtf8("Network Error: %1")\
                .arg(self.__reply.errorString()))
            self.__tryAgainButton.setEnabled(True)
            self.__closeButton.setEnabled(True)
            self.__openButton.setEnabled(False)
    
    def __metaDataChanged(self):
        """
        Private slot to handle a change of the meta data.
        """
        locationHeader = self.__reply.header(QNetworkRequest.LocationHeader)
        if locationHeader.isValid():
            self.__url = locationHeader.toUrl()
            self.__reply.deleteLater()
            self.__reply = Helpviewer.HelpWindow.HelpWindow.networkAccessManager().get(
                           QNetworkRequest(self.__url))
            self.__initialize()
    
    def __downloadProgress(self, received, total):
        """
        Private method show the download progress.
        
        @param received number of bytes received (integer)
        @param total number of total bytes (integer)
        """
        self.__bytesReceived = received
        if total == -1:
            self.progressBar.setValue(0)
            self.progressBar.setMaximum(0)
        else:
            self.progressBar.setValue(received)
            self.progressBar.setMaximum(total)
        self.__updateInfoLabel()
    
    def __updateInfoLabel(self):
        """
        Private method to update the info label.
        """
        if self.__reply.error() != QNetworkReply.NoError and \
           self.__reply.error() != QNetworkReply.OperationCanceledError:
            return
        
        bytesTotal = self.progressBar.maximum()
        running = not self.__downloadedSuccessfully()
        
        info = QString()
        if self.__downloading():
            remaining = QString()
            speed = self.__bytesReceived * 1000.0 / self.__downloadTime.elapsed()
            if bytesTotal != 0:
                timeRemaining = int((bytesTotal - self.__bytesReceived) / speed)
                
                if timeRemaining > 60:
                    minutes = int(timeRemaining / 60)
                    seconds = int(timeRemaining % 60)
                    remaining = self.trUtf8("- %4:%5 minutes remaining")\
                            .arg(minutes)\
                            .arg(seconds, 2, 10, QChar('0'))
                else:
                    # when downloading the eta should never be 0
                    if timeRemaining == 0:
                        timeRemaining = 1
                    
                    remaining = self.trUtf8("- %4 seconds remaining").arg(timeRemaining)
            info = self.trUtf8("%1 of %2 (%3/sec) %4")\
                .arg(self.__dataString(self.__bytesReceived))\
                .arg(bytesTotal == 0 and self.trUtf8("?") \
                                     or self.__dataString(bytesTotal))\
                .arg(self.__dataString(int(speed)))\
                .arg(remaining)
        else:
            if self.__bytesReceived == bytesTotal:
                info = self.trUtf8("%1 downloaded")\
                    .arg(self.__dataString(self.__output.size()))
            else:
                info = self.trUtf8("%1 of %2 - Stopped")\
                    .arg(self.__dataString(self.__bytesReceived))\
                    .arg(self.__dataString(bytesTotal))
        self.infoLabel.setText(info)
    
    def __dataString(self, size):
        """
        Private method to generate a formatted data string.
        
        @param size size to be formatted (integer)
        @return formatted data string (QString)
        """
        unit = QString()
        if size < 1024:
            unit = self.trUtf8("bytes")
        elif size < 1024 * 1024:
            size /= 1024
            unit = self.trUtf8("kB")
        else:
            size /= 1024 * 1024
            unit = self.trUtf8("MB")
        return QString("%1 %2").arg(size).arg(unit)
    
    def __downloading(self):
        """
        Private method to determine, if a download is in progress.
        
        @return flag indicating a download is in progress (boolean)
        """
        return self.__stopButton.isEnabled()
    
    def __downloadedSuccessfully(self):
        """
        Private method to determine the download status.
        
        @return download status (boolean)
        """
        return (not self.__stopButton.isEnabled() and \
                not self.__tryAgainButton.isEnabled())
    
    def __finished(self):
        """
        Private slot to handle the download finished.
        """
        self.__downloadFinished = True
        if not self.__startedSaving:
            return
        
        self.__stopButton.setEnabled(False)
        self.__closeButton.setEnabled(True)
        self.__openButton.setEnabled(True)
        self.__output.close()
        self.__updateInfoLabel()
        
        if not self.keepOpenCheckBox.isChecked() and \
           self.__reply.error() == QNetworkReply.NoError:
            self.close()
        
        if self.__autoOpen:
            self.__open()
    
    def closeEvent(self, evt):
        """
        Protected method called when the dialog is closed.
        """
        self.__output.close()
        self.emit(SIGNAL("done()"))
