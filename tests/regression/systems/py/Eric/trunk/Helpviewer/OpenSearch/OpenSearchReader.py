# -*- coding: utf-8 -*-

# Copyright (c) 2009 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a reader for open search engine descriptions.
"""

from PyQt4.QtCore import *

from OpenSearchEngine import OpenSearchEngine

class OpenSearchReader(QXmlStreamReader):
    """
    Class implementing a reader for open search engine descriptions.
    """
    def read(self, device):
        """
        Public method to read the description.
        
        @param device device to read the description from (QIODevice)
        @return search engine object (OpenSearchEngine)
        """
        self.clear()
        
        if not device.isOpen():
            device.open(QIODevice.ReadOnly)
        
        self.setDevice(device)
        return self.__read()
    
    def __read(self):
        """
        Private method to read and parse the description.
        
        @return search engine object (OpenSearchEngine)
        """
        engine = OpenSearchEngine()
        
        while not self.isStartElement() and not self.atEnd():
            self.readNext()
        
        if self.name() != "OpenSearchDescription" or \
           self.namespaceUri() != "http://a9.com/-/spec/opensearch/1.1/":
            self.raiseError(self.trUtf8("The file is not an OpenSearch 1.1 file."))
            return engine
        
        while not self.atEnd():
            self.readNext()
            
            if not self.isStartElement():
                continue
            
            if self.name() == "ShortName":
                engine.setName(self.readElementText())
                
            elif self.name() == "Description":
                engine.setDescription(self.readElementText())
                
            elif self.name() == "Url":
                type_ = self.attributes().value("type").toString()
                url = self.attributes().value("template").toString()
                method = self.attributes().value("method").toString()
                
                if type_ == "application/x-suggestions+json" and \
                   not engine.suggestionsUrlTemplate().isEmpty():
                    continue
                
                if (type_.isEmpty() or \
                    type_ == "text/html" or \
                    type_ == "application/xhtml+xml") and \
                   not engine.suggestionsUrlTemplate().isEmpty():
                    continue
                
                if url.isEmpty():
                    continue
                
                parameters = []
                
                self.readNext()
                
                while not (self.isEndElement() and self.name() == "Url"):
                    if not self.isStartElement() or \
                       (self.name() != "Param" and self.name() != "Parameter"):
                        self.readNext()
                        continue
                    
                    key = self.attributes().value("name").toString()
                    value = self.attributes().value("value").toString()
                    
                    if not key.isEmpty() and not value.isEmpty():
                        parameters.append((key, value))
                    
                    while not self.isEndElement():
                        self.readNext()
                
                if type_ == "application/x-suggestions+json":
                    engine.setSuggestionsUrlTemplate(url)
                    engine.setSuggestionsParameters(parameters)
                    engine.setSuggestionsMethod(method)
                elif type_.isEmpty() or \
                     type_ == "text/html" or \
                     type_ == "application/xhtml+xml":
                    engine.setSearchUrlTemplate(url)
                    engine.setSearchParameters(parameters)
                    engine.setSearchMethod(method)
                
            elif self.name() == "Image":
                engine.setImageUrl(self.readElementText())
                
            
            if not engine.name().isEmpty() and \
               not engine.description().isEmpty() and \
               not engine.suggestionsUrlTemplate().isEmpty() and \
               not engine.searchUrlTemplate().isEmpty() and \
               not engine.imageUrl().isEmpty():
                break
        
        return engine
