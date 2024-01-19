# -*- coding: utf-8 -*-

# Copyright (c) 2009 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the open search engine.
"""

try:
    import json
except ImportError:
    try:
        import simplejson as json
    except ImportError:
        import ThirdParty.SimpleJSON.simplejson as json

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtNetwork import QNetworkRequest, QNetworkAccessManager

from UI.Info import Program

import Preferences

class OpenSearchEngine(QObject):
    """
    Class implementing the open search engine.
    
    @signal imageChanged() emitted after the icon has been changed
    @signal suggestions(const QStringList&) emitted after the suggestions have 
            been received
    """
    loc = Preferences.getUILanguage()
    if loc == "System":
        loc = QLocale.system().name()
    if loc is None:
        _language = QString("en")
    elif loc == "C":
        _language = QString()
    else:
        _language = loc[:2]
    
    def __init__(self, parent = None):
        """
        Constructor
        
        @param parent reference to the parent object (QObject)
        """
        QObject.__init__(self, parent)
        
        self.__suggestionsReply = None
        self.__networkAccessManager = None
        self._name = QString()
        self._description = QString()
        self._searchUrlTemplate = QString()
        self._suggestionsUrlTemplate = QString()
        self._searchParameters = []            # list of two tuples
        self._suggestionsParameters = []       # list of two tuples
        self._imageUrl = QString()
        self.__image = QImage()
        self.__iconMoved = False
        self.__searchMethod = QString("get")
        self.__suggestionsMethod = QString("get")
        self.__requestMethods = {
            QString("get")  : QNetworkAccessManager.GetOperation, 
            QString("post") : QNetworkAccessManager.PostOperation, 
        }
    
    @classmethod
    def parseTemplate(cls, searchTerm, searchTemplate):
        """
        Class method to parse a search template.
        
        @param searchTerm term to search for (string or QString)
        @param searchTemplate template to be parsed (string or QString)
        @return parsed template (QString)
        """
        result = QString(searchTemplate)
        result.replace("{count}", "20")
        result.replace("{startIndex}", "0")
        result.replace("{startPage}", "0")
        result.replace("{language}", cls._language)
        result.replace("{inputEncoding}", "UTF-8")
        result.replace("{outputEncoding}", "UTF-8")
        result.replace("{searchTerms}", QString(QUrl.toPercentEncoding(searchTerm)))
        result.replace(QRegExp(r"""\{([^\}]*:|)source\??\}"""), Program)

        return result
    
    @pyqtSignature("", "QString")
    def name(self):
        """
        Public method to get the name of the engine.
        
        @return name of the engine (QString)
        """
        return QString(self._name)
    
    def setName(self, name):
        """
        Public method to set the engine name.
        
        @param name name of the engine (string or QString)
        """
        self._name = QString(name)
    
    def description(self):
        """
        Public method to get the description of the engine.
        
        @return description of the engine (QString)
        """
        return QString(self._description)
    
    def setDescription(self, description):
        """
        Public method to set the engine description.
        
        @param description description of the engine (string or QString)
        """
        self._description = QString(description)
    
    def searchUrlTemplate(self):
        """
        Public method to get the search URL template of the engine.
        
        @return search URL template of the engine (QString)
        """
        return QString(self._searchUrlTemplate)
    
    def setSearchUrlTemplate(self, searchUrlTemplate):
        """
        Public method to set the engine search URL template.
        
        @param searchUrlTemplate search URL template of the engine (string or QString)
        """
        self._searchUrlTemplate = QString(searchUrlTemplate)
    
    def searchUrl(self, searchTerm):
        """
        Public method to get a URL ready for searching.
        
        @param searchTerm term to search for (string or QString)
        @return URL (QUrl)
        """
        if self._searchUrlTemplate.isEmpty():
            return QUrl()
        
        ret = QUrl.fromEncoded(
              self.parseTemplate(searchTerm, self._searchUrlTemplate).toUtf8())
        
        if self.__searchMethod != "post":
            for parameter in self._searchParameters:
                ret.addQueryItem(parameter[0], 
                                 self.parseTemplate(searchTerm, parameter[1]))
        
        return ret
    
    def providesSuggestions(self):
        """
        Public method to check, if the engine provides suggestions.
        
        @return flag indicating suggestions are provided (boolean)
        """
        return not self._suggestionsUrlTemplate.isEmpty()
    
    def suggestionsUrlTemplate(self):
        """
        Public method to get the search URL template of the engine.
        
        @return search URL template of the engine (QString)
        """
        return QString(self._suggestionsUrlTemplate)
    
    def setSuggestionsUrlTemplate(self, suggestionsUrlTemplate):
        """
        Public method to set the engine suggestions URL template.
        
        @param suggestionsUrlTemplate suggestions URL template of the
            engine (string or QString)
        """
        self._suggestionsUrlTemplate = QString(suggestionsUrlTemplate)
    
    def suggestionsUrl(self, searchTerm):
        """
        Public method to get a URL ready for suggestions.
        
        @param searchTerm term to search for (string or QString)
        @return URL (QUrl)
        """
        if self._suggestionsUrlTemplate.isEmpty():
            return QUrl()
        
        ret = QUrl.fromEncoded(
              self.parseTemplate(searchTerm, self._suggestionsUrlTemplate).toUtf8())
        
        if self.__searchMethod != "post":
            for parameter in self._suggestionsParameters:
                ret.addQueryItem(parameter[0], self.parseTemplate(searchTerm, parameter[1]))
        
        return ret
    
    def searchParameters(self):
        """
        Public method to get the search parameters of the engine.
        
        @return search parameters of the engine (list of two tuples)
        """
        return self._searchParameters[:]
    
    def setSearchParameters(self, searchParameters):
        """
        Public method to set the engine search parameters.
        
        @param searchParameters search parameters of the engine (list of two tuples)
        """
        self._searchParameters = searchParameters[:]
    
    def suggestionsParameters(self):
        """
        Public method to get the suggestions parameters of the engine.
        
        @return suggestions parameters of the engine (list of two tuples)
        """
        return self._suggestionsParameters[:]
    
    def setSuggestionsParameters(self, suggestionsParameters):
        """
        Public method to set the engine suggestions parameters.
        
        @param suggestionsParameters suggestions parameters of the 
            engine (list of two tuples)
        """
        self._suggestionsParameters = suggestionsParameters[:]
    
    def searchMethod(self):
        """
        Public method to get the HTTP request method used to perform search requests.
        
        @return HTTP request method (QString)
        """
        return self.__searchMethod
    
    def setSearchMethod(self, method):
        """
        Public method to set the HTTP request method used to perform search requests.
        
        @param method HTTP request method (QString)
        """
        requestMethod = QString(method).toLower()
        if requestMethod not in self.__requestMethods:
            return
        
        self.__searchMethod = requestMethod
    
    def suggestionsMethod(self):
        """
        Public method to get the HTTP request method used to perform suggestions requests.
        
        @return HTTP request method (QString)
        """
        return self.__suggestionsMethod
    
    def setSuggestionsMethod(self, method):
        """
        Public method to set the HTTP request method used to perform suggestions requests.
        
        @param method HTTP request method (QString)
        """
        requestMethod = QString(method).toLower()
        if requestMethod not in self.__requestMethods:
            return
        
        self.__suggestionsMethod = requestMethod
    
    def imageUrl(self):
        """
        Public method to get the image URL of the engine.
        
        @return image URL of the engine (QString)
        """
        return QString(self._imageUrl)
    
    def setImageUrl(self, imageUrl):
        """
        Public method to set the engine image URL.
        
        @param description image URL of the engine (string or QString)
        """
        self._imageUrl = QString(imageUrl)
    
    def setImageUrlAndLoad(self, imageUrl):
        """
        Public method to set the engine image URL.
        
        @param description image URL of the engine (string or QString)
        """
        self.setImageUrl(imageUrl)
        self.__iconMoved = False
        self.loadImage()
    
    def loadImage(self):
        """
        Public method to load the image of the engine.
        """
        if self.__networkAccessManager is None or self._imageUrl.isEmpty():
            return
        
        reply = self.__networkAccessManager.get(
            QNetworkRequest(QUrl.fromEncoded(self._imageUrl.toUtf8())))
        self.connect(reply, SIGNAL("finished()"), self.__imageObtained)
    
    def __imageObtained(self):
        """
        Private slot to receive the image of the engine.
        """
        reply = self.sender()
        if reply is None:
            return
        
        response = reply.readAll()
        
        reply.close()
        reply.deleteLater()
        
        if response.isEmpty():
            return
        
        if response.startsWith("<html>") or response.startsWith("HTML"):
            self.__iconMoved = True
            self.__image = QImage()
        else:
            self.__image.loadFromData(response)
        self.emit(SIGNAL("imageChanged()"))
    
    def image(self):
        """
        Public method to get the image of the engine.
        
        @return image of the engine (QImage)
        """
        if not self.__iconMoved and self.__image.isNull():
            self.loadImage()
        
        return self.__image
    
    def setImage(self, image):
        """
        Public method to set the image of the engine.
        
        @param image image to be set (QImage)
        """
        if self._imageUrl.isEmpty():
            imageBuffer = QBuffer()
            imageBuffer.open(QIODevice.ReadWrite)
            if image.save(imageBuffer, "PNG"):
                self._imageUrl = QString("data:image/png;base64,%1")\
                                .arg(QString(imageBuffer.buffer().toBase64()))
        
        self.__image = QImage(image)
        self.emit(SIGNAL("imageChanged()"))
    
    def isValid(self):
        """
        Public method to check, if the engine is valid.
        
        @return flag indicating validity (boolean)
        """
        return not self._name.isEmpty() and not self._searchUrlTemplate.isEmpty()
    
    def __eq__(self, other):
        """
        Public method implementing the == operator.
        
        @param other reference to an open search engine (OpenSearchEngine)
        @return flag indicating equality (boolean)
        """
        if not isinstance(other, OpenSearchEngine):
            return NotImplemented
        
        return self._name == other._name and \
            self._description == other._description and \
            self._imageUrl == other._imageUrl and \
            self._searchUrlTemplate == other._searchUrlTemplate and \
            self._suggestionsUrlTemplate ==other._suggestionsUrlTemplate and \
            self._searchParameters == other._searchParameters and \
            self._suggestionsParameters == other._suggestionsParameters
    
    def __lt__(self, other):
        """
        Public method implementing the < operator.
        
        @param other reference to an open search engine (OpenSearchEngine)
        @return flag indicating less than (boolean)
        """
        if not isinstance(other, OpenSearchEngine):
            return NotImplemented
        
        return self._name < other._name
    
    def requestSuggestions(self, searchTerm):
        """
        Public method to request suggestions.
        
        @param searchTerm term to get suggestions for (string or QString)
        """
        searchTerm = QString(searchTerm)
        if searchTerm.isEmpty() or not self.providesSuggestions():
            return
        
        if self.__networkAccessManager is None:
            return
        
        if self.__suggestionsReply is not None:
            self.__suggestionsReply.disconnect(self)
            self.__suggestionsReply.abort()
            self.__suggestionsReply = None
        
        if self.__suggestionsMethod not in self.__requestMethods:
            # ignore
            return
        
        if self.__suggestionsMethod == "get":
            self.__suggestionsReply = self.networkAccessManager().get(
                QNetworkRequest(self.suggestionsUrl(searchTerm)))
        else:
            parameters = QStringList()
            for parameter in self._suggestionsParameters:
                parameters.append(parameter[0] + "=" + parameter[1])
            data = parameters.join("&").toUtf8()
            self.__suggestionsReply = self.networkAccessManager().post(
                QNetworkRequest(self.suggestionsUrl(searchTerm)), data)
        self.connect(self.__suggestionsReply, SIGNAL("finished()"), 
                     self.__suggestionsObtained)
    
    def __suggestionsObtained(self):
        """
        Private slot to receive the suggestions.
        """
        response = unicode(self.__suggestionsReply.readAll(), "utf-8")
        response = response.strip()
        
        self.__suggestionsReply.close()
        self.__suggestionsReply = None
        
        if len(response) == 0:
            return
        
        try:
            result = json.loads(response)
        except ValueError:
            return
        
        try:
            suggestions = QStringList(result[1])
        except IndexError:
            return
        
        self.emit(SIGNAL("suggestions(const QStringList&)"), suggestions)
    
    def networkAccessManager(self):
        """
        Public method to get a reference to the network access manager object.
        
        @return reference to the network access manager object (QNetworkAccessManager)
        """
        return self.__networkAccessManager
    
    def setNetworkAccessManager(self, networkAccessManager):
        """
        Public method to set the reference to the network access manager.
        
        @param networkAccessManager reference to the network access manager 
            object (QNetworkAccessManager)
        """
        self.__networkAccessManager = networkAccessManager
