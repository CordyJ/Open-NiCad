# -*- coding: utf-8 -*-

# Copyright (c) 2007 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the APIsManager.
"""

import os

from PyQt4.QtCore import *
from PyQt4.Qsci import QsciAPIs, QsciLexer

import Lexers
import Preferences
import Utilities

class APIs(QObject):
    """
    Class implementing an API storage entity.
    
    @signal apiPreparationFinished() emitted after the API preparation has finished
    @signal apiPreparationCancelled() emitted after the API preparation has been cancelled
    @signal apiPreparationStarted() emitted after the API preparation has started
    """
    def __init__(self, language, forPreparation = False, parent = None):
        """
        Constructor
        
        @param language language of the APIs object (string)
        @param forPreparation flag indicating this object is just needed
            for a preparation process (boolean)
        @param parent reference to the parent object (QObject)
        """
        QObject.__init__(self, parent)
        self.setObjectName("APIs_%s" % language)
        
        self.__inPreparation = False
        self.__language = language
        self.__forPreparation = forPreparation
        self.__lexer = Lexers.getLexer(self.__language)
        self.__apifiles = Preferences.getEditorAPI(self.__language)
        self.__apifiles.sort()
        if self.__lexer is None:
            self.__apis = None
        else:
            self.__apis = QsciAPIs(self.__lexer)
            self.connect(self.__apis, SIGNAL("apiPreparationFinished()"),
                         self.__apiPreparationFinished)
            self.connect(self.__apis, SIGNAL("apiPreparationCancelled()"),
                         self.__apiPreparationCancelled)
            self.connect(self.__apis, SIGNAL("apiPreparationStarted()"),
                         self.__apiPreparationStarted)
            self.__loadAPIs()
        
    def __loadAPIs(self):
        """
        Private method to load the APIs.
        """
        if self.__apis.isPrepared():
            # load a prepared API file
            if not self.__forPreparation and Preferences.getEditor("AutoPrepareAPIs"):
                self.prepareAPIs()
            self.__apis.loadPrepared()
        else:
            # load the raw files and prepare the API file
            if not self.__forPreparation and Preferences.getEditor("AutoPrepareAPIs"):
                self.prepareAPIs(ondemand = True)
    
    def reloadAPIs(self):
        """
        Public method to reload the API information.
        """
        if not self.__forPreparation and Preferences.getEditor("AutoPrepareAPIs"):
            self.prepareAPIs()
        self.__loadAPIs()
    
    def getQsciAPIs(self):
        """
        Public method to get a reference to QsciAPIs object.
        
        @return reference to the QsciAPIs object (QsciAPIs)
        """
        if not self.__forPreparation and Preferences.getEditor("AutoPrepareAPIs"):
            self.prepareAPIs()
        return self.__apis
    
    def __apiPreparationFinished(self):
        """
        Private method called to save an API, after it has been prepared.
        """
        res = self.__apis.savePrepared()
        self.__inPreparation = False
        self.emit(SIGNAL('apiPreparationFinished()'))
    
    def __apiPreparationCancelled(self):
        """
        Private method called, after the API preparation process has been cancelled.
        """
        self.__inPreparation = False
        self.emit(SIGNAL('apiPreparationCancelled()'))
    
    def __apiPreparationStarted(self):
        """
        Private method called, when the API preparation process started.
        """
        self.__inPreparation = True
        self.emit(SIGNAL('apiPreparationStarted()'))
    
    def prepareAPIs(self, ondemand = False, rawList = None):
        """
        Public method to prepare the APIs if necessary.
        
        @keyparam ondemand flag indicating a requested preparation (boolean)
        @keyparam rawList list of raw API files (QStringList)
        """
        if self.__apis is None or self.__inPreparation:
            return
        
        needsPreparation = False
        if ondemand:
            needsPreparation = True
        else:
            # check, if a new preparation is necessary
            preparedAPIs = self.__defaultPreparedName()
            if not preparedAPIs.isEmpty():
                preparedAPIsInfo = QFileInfo(preparedAPIs)
                if not preparedAPIsInfo.exists():
                    needsPreparation = True
                else:
                    preparedAPIsTime = preparedAPIsInfo.lastModified()
                    apifiles = Preferences.getEditorAPI(self.__language)
                    apifiles.sort()
                    if self.__apifiles != apifiles:
                        needsPreparation = True
                    for apifile in apifiles:
                        if QFileInfo(apifile).lastModified() > preparedAPIsTime:
                            needsPreparation = True
                            break
        
        if needsPreparation:
            # do the preparation
            self.__apis.clear()
            if rawList:
                apifiles = rawList
            else:
                apifiles = Preferences.getEditorAPI(self.__language)
            for apifile in apifiles:
                self.__apis.load(apifile)
            self.__apis.prepare()
            self.__apifiles = apifiles
    
    def cancelPreparation(self):
        """
        Public slot to cancel the APIs preparation.
        """
        self.__apis and self.__apis.cancelPreparation()
    
    def installedAPIFiles(self):
        """
        Public method to get a list of installed API files.
        
        @return list of installed API files (QStringList)
        """
        if self.__apis is not None:
            return self.__apis.installedAPIFiles()
        else:
            return QStringList()
    
    def __defaultPreparedName(self):
        """
        Private method returning the default name of a prepared API file.
        
        @return complete filename for the Prepared APIs file (QString)
        """
        if self.__apis is not None:
            return self.__apis.defaultPreparedName()
        else:
            return QString()
    
class APIsManager(QObject):
    """
    Class implementing the APIsManager class, which is the central store for
    API information used by autocompletion and calltips.
    """
    def __init__(self, parent = None):
        """
        Constructor
        
        @param parent reference to the parent object (QObject)
        """
        QObject.__init__(self, parent)
        self.setObjectName("APIsManager")
        
        self.__apis = {}
    
    def reloadAPIs(self):
        """
        Public slot to reload the api information.
        """
        for api in self.__apis.values():
            api and api.reloadAPIs()
    
    def getAPIs(self, language, forPreparation = False):
        """
        Public method to get an apis object for autocompletion/calltips.
        
        This method creates and loads an APIs object dynamically upon request. 
        This saves memory for languages, that might not be needed at the moment.
        
        @param language the language of the requested api object (string or QString)
        @param forPreparation flag indicating the requested api object is just needed
            for a preparation process (boolean)
        @return the apis object (APIs)
        """
        language = unicode(language)
        if forPreparation:
            return APIs(language, forPreparation = forPreparation)
        else:
            try:
                return self.__apis[language]
            except KeyError:
                if language in Lexers.getSupportedLanguages().keys():
                    # create the api object
                    self.__apis[language] = APIs(language)
                    return self.__apis[language]
                else:
                    return None