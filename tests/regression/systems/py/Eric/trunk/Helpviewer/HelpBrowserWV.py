# -*- coding: utf-8 -*-

# Copyright (c) 2008 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#


"""
Module implementing the helpbrowser using QWebView.
"""

import os

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtWebKit import QWebView, QWebPage, QWebSettings
from PyQt4.QtNetwork import QNetworkProxy, QNetworkAccessManager, QNetworkReply, \
    QNetworkRequest

from KdeQt import KQMessageBox

import Preferences
import Utilities
import UI.PixmapCache

from DownloadDialog import DownloadDialog
from HelpWebSearchWidget import HelpWebSearchWidget
from Bookmarks.AddBookmarkDialog import AddBookmarkDialog
from JavaScriptResources import fetchLinks_js
from HTMLResources import notFoundPage_html
import Helpviewer.HelpWindow

from Network.NetworkAccessManagerProxy import NetworkAccessManagerProxy

from OpenSearch.OpenSearchEngineAction import OpenSearchEngineAction

##########################################################################################

class JavaScriptExternalObject(QObject):
    """
    Class implementing an external javascript object to add search providers.
    """
    @pyqtSignature("QString")
    def AddSearchProvider(self, url):
        """
        Public slot to add a search provider.
        
        @param url url of the XML file defining the search provider (QString)
        """
        HelpWebSearchWidget.openSearchManager().addEngine(QUrl(url));

class LinkedResource(object):
    """
    Class defining a data structure for linked resources.
    """
    def __init__(self):
        """
        Constructor
        """
        self.rel = QString()
        self.type_ = QString()
        self.href = QString()
        self.title = QString()

##########################################################################################

class JavaScriptEricObject(QObject):
    """
    Class implementing an external javascript object to search via the startpage.
    """
    # these must be in line with the strings used by the javascript part of the start page
    translations = [
        QT_TRANSLATE_NOOP("JavaScriptEricObject", "Welcome to Eric Web Browser!"), 
        QT_TRANSLATE_NOOP("JavaScriptEricObject", "Eric Web Browser"), 
        QT_TRANSLATE_NOOP("JavaScriptEricObject", "Search!"), 
        QT_TRANSLATE_NOOP("JavaScriptEricObject", "About Eric"), 
    ]
    
    @pyqtSignature("QString", "QString")
    def translate(self, trans):
        """
        Public method to translate the given string.
        
        @param trans string to be translated (QString)
        @return translation (QString)
        """
        if trans == "QT_LAYOUT_DIRECTION":
            # special handling to detect layout direction
            if qApp.isLeftToRight():
                return "LTR"
            else:
                return "RTL"
        
        return self.trUtf8(trans.toUtf8())
    
    @pyqtSignature("", "QString")
    def providerString(self):
        """
        Public method to get a string for the search provider.
        
        @return string for the search provider (QString)
        """
        return self.trUtf8("Search results provided by %1")\
            .arg(HelpWebSearchWidget.openSearchManager().currentEngineName())
    
    @pyqtSignature("QString", "QString")
    def searchUrl(self, searchStr):
        """
        Public method to get the search URL for the given search term.
        
        @param searchStr search term (QString)
        @return search URL (QString)
        """
        return QString.fromUtf8(
            HelpWebSearchWidget.openSearchManager().currentEngine()\
            .searchUrl(searchStr).toEncoded())

##########################################################################################

class HelpWebPage(QWebPage):
    """
    Class implementing an enhanced web page.
    """
    def __init__(self, parent = None):
        """
        Constructor
        
        @param parent parent widget of this window (QWidget)
        """
        QWebPage.__init__(self, parent)
        
        self.__lastRequest = None
        self.__lastRequestType = QWebPage.NavigationTypeOther
        
        self.__proxy = NetworkAccessManagerProxy(self)
        self.__proxy.setWebPage(self)
        self.__proxy.setPrimaryNetworkAccessManager(
            Helpviewer.HelpWindow.HelpWindow.networkAccessManager())
        self.setNetworkAccessManager(self.__proxy)
    
    def acceptNavigationRequest(self, frame, request, type_):
        """
        Protected method to determine, if a request may be accepted.
        
        @param frame reference to the frame sending the request (QWebFrame)
        @param request reference to the request object (QNetworkRequest)
        @param type_ type of the navigation request (QWebPage.NavigationType)
        @return flag indicating acceptance (boolean)
        """
        self.__lastRequest = request
        self.__lastRequestType = type_
        
        return QWebPage.acceptNavigationRequest(self, frame, request, type_)
    
    def populateNetworkRequest(self, request):
        """
        Public method to add data to a network request.
        
        @param request reference to the network request object (QNetworkRequest)
        """
        request.setAttribute(QNetworkRequest.User + 100, QVariant(self))
        request.setAttribute(QNetworkRequest.User + 101, 
                             QVariant(self.__lastRequestType))
    
    def pageAttributeId(self):
        """
        Public method to get the attribute id of the page attribute.
        
        @return attribute id of the page attribute (integer)
        """
        return QNetworkRequest.User + 100

##########################################################################################

class HelpBrowser(QWebView):
    """
    Class implementing the helpbrowser widget.
    
    This is a subclass of the Qt QWebView to implement an
    interface compatible with the QTextBrowser based variant.
    
    @signal sourceChanged(const QUrl &) emitted after the current URL has changed
    @signal forwardAvailable(bool) emitted after the current URL has changed
    @signal backwardAvailable(bool) emitted after the current URL has changed
    @signal highlighted(const QString&) emitted, when the mouse hovers over a link
    @signal search(const QUrl &) emitted, when a search is requested
    """
    def __init__(self, parent = None, name = QString("")):
        """
        Constructor
        
        @param parent parent widget of this window (QWidget)
        @param name name of this window (string or QString)
        """
        QWebView.__init__(self, parent)
        self.setObjectName(name)
        self.setWhatsThis(self.trUtf8(
                """<b>Help Window</b>"""
                """<p>This window displays the selected help information.</p>"""
        ))
        
        self.__page = HelpWebPage(self)
        self.setPage(self.__page)
        
        self.mw = parent
        self.ctrlPressed = False
        self.__downloadWindows = []
        self.__isLoading = False
        
        self.__currentZoom = 100
        self.__zoomLevels = [
            30, 50, 67, 80, 90, 
            100, 
            110, 120, 133, 150, 170, 200, 240, 300, 
        ]
        
        self.__javaScriptBinding = None
        self.__javaScriptEricObject = None
        
        self.connect(self.mw, SIGNAL("zoomTextOnlyChanged(bool)"), self.__applyZoom)
        
        self.page().setLinkDelegationPolicy(QWebPage.DelegateAllLinks)
        self.connect(self, SIGNAL('linkClicked(const QUrl &)'), self.setSource)
        self.connect(self, SIGNAL('iconChanged()'), self.__iconChanged)
        
        self.connect(self, SIGNAL('urlChanged(const QUrl &)'), self.__urlChanged)
        self.connect(self, SIGNAL('statusBarMessage(const QString &)'), 
            self.__statusBarMessage)
        self.connect(self.page(), 
            SIGNAL('linkHovered(const QString &, const QString &, const QString &)'), 
            self.__linkHovered)
        
        self.connect(self, SIGNAL('loadStarted()'), self.__loadStarted)
        self.connect(self, SIGNAL('loadProgress(int)'), self.__loadProgress)
        self.connect(self, SIGNAL('loadFinished(bool)'), self.__loadFinished)
        
        self.page().setForwardUnsupportedContent(True)
        self.connect(self.page(), SIGNAL('unsupportedContent(QNetworkReply *)'), 
            self.__unsupportedContent)
        
        self.connect(self.page(), SIGNAL('downloadRequested(const QNetworkRequest &)'), 
            self.__downloadRequested)
        self.connect(self.page(), SIGNAL("frameCreated(QWebFrame *)"), 
            self.__addExternalBinding)
        self.__addExternalBinding(self.page().mainFrame())
        
        self.connect(HelpWebSearchWidget.openSearchManager(), 
                     SIGNAL("currentEngineChanged()"), 
                     self.__currentEngineChanged)
    
    def __addExternalBinding(self, frame = None):
        """
        Private slot to add javascript bindings for adding search providers.
        
        @param frame reference to the web frame (QWebFrame)
        """
        self.page().settings().setAttribute(QWebSettings.JavascriptEnabled, True)
        if self.__javaScriptBinding is None:
            self.__javaScriptBinding = JavaScriptExternalObject(self)
        
        if frame is None:
            # called from QWebFrame.javaScriptWindowObjectCleared
            frame = self.sender()
            if frame.url().scheme() == "pyrc" and frame.url().path() == "home":
                if self.__javaScriptEricObject is None:
                    self.__javaScriptEricObject = JavaScriptEricObject(self)
                frame.addToJavaScriptWindowObject("eric", self.__javaScriptEricObject)
        else:
            # called from QWebPage.frameCreated
            self.connect(frame, SIGNAL("javaScriptWindowObjectCleared()"), 
                self.__addExternalBinding)
        frame.addToJavaScriptWindowObject("external", self.__javaScriptBinding)
    
    def linkedResources(self, relation = QString()):
        """
        Public method to extract linked resources.
        
        @param relation relation to extract (QString)
        @return list of linked resources (list of LinkedResource)
        """
        relation = QString(relation)
        resources = []
        
        lst = self.page().mainFrame().evaluateJavaScript(fetchLinks_js).toList()
        for variant in lst:
            m = variant.toMap()
            rel = m[QString("rel")].toString()
            type_ = m[QString("type")].toString()
            href = m[QString("href")].toString()
            title =  m[QString("title")].toString()
            
            if href.isEmpty() or type_.isEmpty():
                continue
            if not relation.isEmpty() and rel != relation:
                continue
            
            resource = LinkedResource()
            resource.rel = rel
            resource.type_ = type_
            resource.href = href
            resource.title = title
            
            resources.append(resource)
        
        return resources
    
    def __currentEngineChanged(self):
        """
        Private slot to track a change of the current search engine.
        """
        if self.url().toString() == "pyrc:home":
            self.reload()
    
    def setSource(self, name):
        """
        Public method used to set the source to be displayed.
        
        @param name filename to be shown (QUrl)
        """
        if name is None or not name.isValid():
            return
        
        if self.ctrlPressed:
            # open in a new window
            self.mw.newTab(name)
            self.ctrlPressed = False
            return
        
        if name.scheme().isEmpty():
            name.setUrl(Preferences.getHelp("DefaultScheme") + name.toString())
        
        if name.scheme().length() == 1 or \
           name.scheme() == "file":
            # name is a local file
            if not name.scheme().isEmpty() and \
               name.scheme().length() == 1:
                # it is a local path on win os
                name = QUrl.fromLocalFile(name.toString())
            
            if not QFileInfo(name.toLocalFile()).exists():
                QMessageBox.critical(None,
                    self.trUtf8("Web Browser"),
                    self.trUtf8("""<p>The file <b>%1</b> does not exist.</p>""")\
                        .arg(name.toLocalFile()),
                    QMessageBox.StandardButtons(\
                        QMessageBox.Ok))
                return

            if name.toLocalFile().endsWith(".pdf") or \
               name.toLocalFile().endsWith(".PDF") or \
               name.toLocalFile().endsWith(".chm") or \
               name.toLocalFile().endsWith(".CHM"):
                started = QDesktopServices.openUrl(name)
                if not started:
                    KQMessageBox.critical(self,
                        self.trUtf8("Web Browser"),
                        self.trUtf8("""<p>Could not start a viewer"""
                        """ for file <b>%1</b>.</p>""").arg(name.path()))
                return
        elif name.scheme() in ["mailto", "ftp"]:
            started = QDesktopServices.openUrl(name)
            if not started:
                KQMessageBox.critical(self,
                    self.trUtf8("Web Browser"),
                    self.trUtf8("""<p>Could not start an application"""
                    """ for URL <b>%1</b>.</p>""").arg(name.toString()))
            return
        elif name.scheme() == "javascript":
            scriptSource = name.toString()[11:]
            res = self.page().mainFrame().evaluateJavaScript(scriptSource).toString()
            if not res.isEmpty():
                self.setHtml(res)
            return
        else:
            if name.toString().endsWith(".pdf") or \
               name.toString().endsWith(".PDF") or \
               name.toString().endsWith(".chm") or \
               name.toString().endsWith(".CHM"):
                started = QDesktopServices.openUrl(name)
                if not started:
                    KQMessageBox.critical(self,
                        self.trUtf8("Web Browser"),
                        self.trUtf8("""<p>Could not start a viewer"""
                        """ for file <b>%1</b>.</p>""").arg(name.path()))
                return
        
        self.load(name)

    def source(self):
        """
        Public method to return the URL of the loaded page.
        
        @return URL loaded in the help browser (QUrl)
        """
        return self.url()
    
    def documentTitle(self):
        """
        Public method to return the title of the loaded page.
        
        @return title (QString)
        """
        return self.title()
    
    def backward(self):
        """
        Public slot to move backwards in history.
        """
        self.triggerPageAction(QWebPage.Back)
        self.__urlChanged(self.history().currentItem().url())
    
    def forward(self):
        """
        Public slot to move forward in history.
        """
        self.triggerPageAction(QWebPage.Forward)
        self.__urlChanged(self.history().currentItem().url())
    
    def home(self):
        """
        Public slot to move to the first page loaded.
        """
        homeUrl = QUrl(Preferences.getHelp("HomePage"))
        self.setSource(homeUrl)
        self.__urlChanged(self.history().currentItem().url())
    
    def reload(self):
        """
        Public slot to reload the current page.
        """
        self.triggerPageAction(QWebPage.Reload)
    
    def copy(self):
        """
        Public slot to copy the selected text.
        """
        self.triggerPageAction(QWebPage.Copy)
    
    def isForwardAvailable(self):
        """
        Public method to determine, if a forward move in history is possible.
        
        @return flag indicating move forward is possible (boolean)
        """
        return self.history().canGoForward()
    
    def isBackwardAvailable(self):
        """
        Public method to determine, if a backwards move in history is possible.
        
        @return flag indicating move backwards is possible (boolean)
        """
        return self.history().canGoBack()
    
    def __levelForZoom(self, zoom):
        """
        Private method determining the zoom level index given a zoom factor.
        
        @param zoom zoom factor (integer)
        @return index of zoom factor (integer)
        """
        try:
            index = self.__zoomLevels.index(zoom)
        except ValueError:
            for index in range(len(self.__zoomLevels)):
                if zoom <= self.__zoomLevels[index]:
                    break
        return index
    
    def __applyZoom(self):
        """
        Private slot to apply the current zoom factor.
        """
        try:
            self.setZoomFactor(self.__currentZoom / 100.0)
        except AttributeError:
            self.setTextSizeMultiplier(self.__currentZoom / 100.0)
    
    def zoomIn(self):
        """
        Public slot to zoom into the page.
        """
        index = self.__levelForZoom(self.__currentZoom)
        if index < len(self.__zoomLevels) - 1:
            self.__currentZoom = self.__zoomLevels[index + 1]
        self.__applyZoom()
    
    def zoomOut(self):
        """
        Public slot to zoom out of the page.
        """
        index = self.__levelForZoom(self.__currentZoom)
        if index > 0:
            self.__currentZoom = self.__zoomLevels[index - 1]
        self.__applyZoom()
    
    def zoomReset(self): 
        """
        Public method to reset the zoom factor.
        """
        self.__currentZoom = 100
        self.__applyZoom()
    
    def wheelEvent(self, evt):
        """
        Protected method to handle wheel events.
        
        @param evt reference to the wheel event (QWheelEvent)
        """
        if evt.modifiers() & Qt.ControlModifier:
            degrees = evt.delta() / 8
            steps = degrees / 15
            self.__currentZoom += steps * 10
            self.__applyZoom()
            evt.accept()
            return
        
        QWebView.wheelEvent(self, evt)
    
    def hasSelection(self):
        """
        Public method to determine, if there is some text selected.
        
        @return flag indicating text has been selected (boolean)
        """
        return not self.selectedText().isEmpty()
    
    def findNextPrev(self, txt, case, backwards, wrap):
        """
        Public slot to find the next occurrence of a text.
        
        @param txt text to search for (QString)
        @param case flag indicating a case sensitive search (boolean)
        @param backwards flag indicating a backwards search (boolean)
        @param wrap flag indicating to wrap around (boolean)
        """
        findFlags = QWebPage.FindFlags()
        if case:
            findFlags |= QWebPage.FindCaseSensitively
        if backwards:
            findFlags |= QWebPage.FindBackward
        if wrap:
            findFlags |= QWebPage.FindWrapsAroundDocument
        
        return self.findText(txt, findFlags)
    
    def contextMenuEvent(self, evt):
        """
        Protected method called to create a context menu.
        
        This method is overridden from QWebView.
        
        @param evt reference to the context menu event object (QContextMenuEvent)
        """
        pos = evt.pos()
        menu = QMenu(self)
        
        hit = self.page().mainFrame().hitTestContent(evt.pos())
        if not hit.linkUrl().isEmpty():
            act = menu.addAction(self.trUtf8("Open Link in New Tab\tCtrl+LMB"),
                self.__openLinkInNewTab)
            act.setData(QVariant(hit.linkUrl()))
            menu.addSeparator()
            menu.addAction(self.trUtf8("Save Lin&k"), self.__downloadLink)
            act = menu.addAction(self.trUtf8("Bookmark this Link"), self.__bookmarkLink)
            act.setData(QVariant(hit.linkUrl()))
            menu.addSeparator()
            menu.addAction(self.trUtf8("Copy Link to Clipboard"), self.__copyLink)
        
        if not hit.imageUrl().isEmpty():
            if not menu.isEmpty():
                menu.addSeparator()
            act = menu.addAction(self.trUtf8("Open Image in New Tab"), 
                self.__openLinkInNewTab)
            act.setData(QVariant(hit.imageUrl()))
            menu.addSeparator()
            menu.addAction(self.trUtf8("Save Image"), self.__downloadImage)
            menu.addAction(self.trUtf8("Copy Image to Clipboard"), self.__copyImage)
            act = menu.addAction(self.trUtf8("Copy Image Location to Clipboard"), 
                self.__copyImageLocation)
            act.setData(QVariant(hit.imageUrl().toString()))
            menu.addSeparator()
            act = menu.addAction(self.trUtf8("Block Image"), self.__blockImage)
            act.setData(QVariant(hit.imageUrl().toString()))
        
        if not menu.isEmpty():
            menu.addSeparator()
        menu.addAction(self.mw.newTabAct)
        menu.addAction(self.mw.newAct)
        menu.addSeparator()
        menu.addAction(self.mw.saveAsAct)
        menu.addSeparator()
        menu.addAction(self.trUtf8("Bookmark this Page"), self.__addBookmark)
        menu.addSeparator()
        menu.addAction(self.mw.backAct)
        menu.addAction(self.mw.forwardAct)
        menu.addAction(self.mw.homeAct)
        menu.addSeparator()
        menu.addAction(self.mw.zoomInAct)
        menu.addAction(self.mw.zoomOutAct)
        menu.addSeparator()
        if not self.selectedText().isEmpty():
            menu.addAction(self.mw.copyAct)
        menu.addAction(self.mw.findAct)
        menu.addSeparator()
        if not self.selectedText().isEmpty():
            self.__searchMenu = menu.addMenu(self.trUtf8("Search with..."))
            
            engineNames = HelpWebSearchWidget.openSearchManager().allEnginesNames()
            for engineName in engineNames:
                engine = HelpWebSearchWidget.openSearchManager().engine(engineName)
                act = OpenSearchEngineAction(engine, self.__searchMenu)
                self.__searchMenu.addAction(act)
                act.setData(QVariant(engineName))
            self.connect(self.__searchMenu, SIGNAL("triggered(QAction *)"), 
                         self.__searchRequested)
            
            menu.addSeparator()
        menu.addAction(self.trUtf8("Web Inspector..."), self.__webInspector)
        
        menu.exec_(evt.globalPos())
    
    def __openLinkInNewTab(self):
        """
        Private method called by the context menu to open a link in a new window.
        """
        act = self.sender()
        url = act.data().toUrl()
        if url.isEmpty():
            return
        
        oldCtrlPressed = self.ctrlPressed
        self.ctrlPressed = True
        self.setSource(url)
        self.ctrlPressed = oldCtrlPressed
    
    def __bookmarkLink(self):
        """
        Private slot to bookmark a link via the context menu.
        """
        act = self.sender()
        url = act.data().toUrl()
        if url.isEmpty():
            return
        
        dlg = AddBookmarkDialog()
        dlg.setUrl(QString(url.toEncoded()))
        dlg.exec_()
    
    def __downloadLink(self):
        """
        Private slot to download a link and save it to disk.
        """
        self.pageAction(QWebPage.DownloadLinkToDisk).trigger()
    
    def __copyLink(self):
        """
        Private slot to copy a link to the clipboard.
        """
        self.pageAction(QWebPage.CopyLinkToClipboard).trigger()
    
    def __downloadImage(self):
        """
        Private slot to download an image and save it to disk.
        """
        self.pageAction(QWebPage.DownloadImageToDisk).trigger()
    
    def __copyImage(self):
        """
        Private slot to copy an image to the clipboard.
        """
        self.pageAction(QWebPage.CopyImageToClipboard).trigger()
    
    def __copyImageLocation(self):
        """
        Private slot to copy an image location to the clipboard.
        """
        act = self.sender()
        url = act.data().toString()
        QApplication.clipboard().setText(url)
    
    def __blockImage(self):
        """
        Private slot to add a block rule for an image URL.
        """
        act = self.sender()
        url = act.data().toString()
        dlg = Helpviewer.HelpWindow.HelpWindow.adblockManager().showDialog()
        dlg.addCustomRule(url)
    
    def __searchRequested(self, act):
        """
        Private slot to search for some text with a selected search engine.
        
        @param act reference to the action that triggered this slot (QAction)
        """
        searchText = self.selectedText()
        
        if searchText.isEmpty():
            return
        
        engineName = act.data().toString()
        if not engineName.isEmpty():
            engine = HelpWebSearchWidget.openSearchManager().engine(engineName)
            self.emit(SIGNAL("search(const QUrl &)"), engine.searchUrl(searchText))
    
    def __webInspector(self):
        """
        Private slot to show the web inspector window.
        """
        self.triggerPageAction(QWebPage.InspectElement)
    
    def __addBookmark(self):
        """
        Private slot to bookmark the current link.
        """
        dlg = AddBookmarkDialog()
        dlg.setUrl(QString(self.url().toEncoded()))
        dlg.setTitle(self.title())
        dlg.exec_()
    
    def keyPressEvent(self, evt):
        """
        Protected method called by a key press.
        
        This method is overridden from QTextBrowser.
        
        @param evt the key event (QKeyEvent)
        """
        self.ctrlPressed = (evt.key() == Qt.Key_Control)
        QWebView.keyPressEvent(self, evt)
    
    def keyReleaseEvent(self, evt):
        """
        Protected method called by a key release.
        
        This method is overridden from QTextBrowser.
        
        @param evt the key event (QKeyEvent)
        """
        self.ctrlPressed = False
        QWebView.keyReleaseEvent(self, evt)
    
    def clearHistory(self):
        """
        Public slot to clear the history.
        """
        self.history().clear()
        self.__urlChanged(self.history().currentItem().url())
    
    ############################################################################
    ## Signal converters below
    ############################################################################
    
    def __urlChanged(self, url):
        """
        Private slot to handle the urlChanged signal.
        
        @param url the new url (QUrl)
        """
        self.emit(SIGNAL('sourceChanged(const QUrl &)'), url)
        
        self.emit(SIGNAL('forwardAvailable(bool)'), self.isForwardAvailable())
        self.emit(SIGNAL('backwardAvailable(bool)'), self.isBackwardAvailable())
    
    def __statusBarMessage(self, text):
        """
        Private slot to handle the statusBarMessage signal.
        
        @param text text to be shown in the status bar (QString)
        """
        self.mw.statusBar().showMessage(text)
    
    def __linkHovered(self, link,  title, textContent):
        """
        Private slot to handle the linkHovered signal.
        
        @param link the URL of the link (QString)
        @param title the link title (QString)
        @param textContent text content of the link (QString)
        """
        self.emit(SIGNAL('highlighted(const QString&)'), link)
    
    ############################################################################
    ## Signal handlers below
    ############################################################################
    
    def __loadStarted(self):
        """
        Private method to handle the loadStarted signal.
        """
        self.__isLoading = True
        self.mw.setLoading(self)
        self.mw.progressBar().show()
    
    def __loadProgress(self, progress):
        """
        Private method to handle the loadProgress signal.
        
        @param progress progress value (integer)
        """
        self.mw.progressBar().setValue(progress)
    
    def __loadFinished(self, ok):
        """
        Private method to handle the loadFinished signal.
        
        @param ok flag indicating the result (boolean)
        """
        self.__isLoading = False
        self.mw.progressBar().hide()
        self.mw.resetLoading(self)
        
        self.__iconChanged()
        
        self.mw.passwordManager().fill(self.page())
    
    def isLoading(self):
        """
        Public method to get the loading state.
        
        @return flag indicating the loading state (boolean)
        """
        return self.__isLoading
    
    def saveAs(self):
        """
        Public method to save the current page to a file.
        """
        url = self.url()
        if url.isEmpty():
            return
        
        req = QNetworkRequest(url)
        reply = self.mw.networkAccessManager().get(req)
        self.__unsupportedContent(reply, True)
    
    def __unsupportedContent(self, reply, requestFilename = None, download = False):
        """
        Private slot to handle the unsupportedContent signal.
        
        @param reply reference to the reply object (QNetworkReply)
        @keyparam requestFilename indicating to ask for a filename 
            (boolean or None). If it is None, the behavior is determined
            by a configuration option.
        @keyparam download flag indicating a download operation (boolean)
        """
        if reply is None:
            return
        
        replyUrl = reply.url()
        
        if replyUrl.scheme() == "abp":
            return
        
        if reply.error() == QNetworkReply.NoError:
            if reply.url().isEmpty():
                return
            header = reply.header(QNetworkRequest.ContentLengthHeader)
            size, ok = header.toInt()
            if ok and size == 0:
                return
            
            if requestFilename is None:
                requestFilename = Preferences.getUI("RequestDownloadFilename")
            dlg = DownloadDialog(reply, requestFilename, self.page(), download)
            self.connect(dlg, SIGNAL("done()"), self.__downloadDone)
            self.__downloadWindows.append(dlg)
            dlg.show()
        else:
            replyUrl = reply.url()
            if replyUrl.isEmpty():
                return
            
            html = QString(notFoundPage_html)
            urlString = QString.fromUtf8(replyUrl.toEncoded())
            title = self.trUtf8("Error loading page: %1").arg(urlString)
            pixmap = qApp.style()\
                     .standardIcon(QStyle.SP_MessageBoxWarning, None, self)\
                     .pixmap(32, 32)
            imageBuffer = QBuffer()
            imageBuffer.open(QIODevice.ReadWrite)
            if pixmap.save(imageBuffer, "PNG"):
                html.replace("IMAGE_BINARY_DATA_HERE", 
                             QString(imageBuffer.buffer().toBase64()))
            html = html.arg(
                title, 
                reply.errorString(), 
                self.trUtf8("When connecting to: %1.").arg(urlString), 
                self.trUtf8("Check the address for errors such as <b>ww</b>.example.org "
                            "instead of <b>www</b>.example.org"), 
                self.trUtf8("If the address is correct, try checking the network "
                            "connection."), 
                self.trUtf8("If your computer or network is protected by a firewall or "
                            "proxy, make sure that the browser is permitted to access "
                            "the network.")
            )
            self.setHtml(html, replyUrl)
            self.mw.historyManager().removeHistoryEntry(replyUrl, self.title())
            self.emit(SIGNAL('loadFinished(bool)'), False)
    
    def __downloadDone(self):
        """
        Private slot to handle the done signal of the download dialogs.
        """
        dlg = self.sender()
        if dlg in self.__downloadWindows:
            self.disconnect(dlg, SIGNAL("done()"), self.__downloadDone)
            self.__downloadWindows.remove(dlg)
            dlg.deleteLater()
    
    def __downloadRequested(self, request):
        """
        Private slot to handle a download request.
        
        @param request reference to the request object (QNetworkRequest)
        """
        if request.url().isEmpty():
            return
        mgr = self.page().networkAccessManager()
        self.__unsupportedContent(mgr.get(request), download = True)
    
    def __iconChanged(self):
        """
        Private slot to handle the icon change.
        """
        self.mw.iconChanged(self.icon())
    
    ############################################################################
    ## Miscellaneous methods below
    ############################################################################
    
    def createWindow(self, windowType):
        """
        Protected method called, when a new window should be created.
        
        @param windowType type of the requested window (QWebPage.WebWindowType)
        """
        self.mw.newTab()
        return self.mw.currentBrowser()
    
    def preferencesChanged(self):
        """
        Public method to indicate a change of the settings.
        """
        self.reload()
