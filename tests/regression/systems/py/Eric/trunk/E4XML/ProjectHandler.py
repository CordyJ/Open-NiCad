# -*- coding: utf-8 -*-

# Copyright (c) 2003 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the handler class for reading an XML project file.
"""

import os
try:
    import cPickle as pickle
except ImportError:
    import pickle

from Config import projectFileFormatVersion
from XMLHandlerBase import XMLHandlerBase

import Utilities

class ProjectHandler(XMLHandlerBase):
    """
    Class implementing a sax handler to read an XML project file.
    """
    def __init__(self, project):
        """
        Constructor
        
        @param project Reference to the project object to store the
                information into.
        """
        XMLHandlerBase.__init__(self)
        
        self.startDocumentSpecific = self.startDocumentProject
        
        self.elements.update({
            'Project' : (self.startProject, self.defaultEndElement),
            'Language' : (self.defaultStartElement, self.endLanguage), 
            'ProjectWordList' : (self.defaultStartElement, self.endProjectWordList), 
            'ProjectExcludeList' : (self.defaultStartElement, 
                                    self.endProjectExcludeList), 
            'ProgLanguage' : (self.startProgLanguage, self.endProgLanguage),
            'ProjectType' : (self.defaultStartElement, self.endProjectType),
            'Description' : (self.defaultStartElement, self.endDescription),
            'Version' : (self.defaultStartElement, self.endVersion),
            'Author' : (self.defaultStartElement, self.endAuthor),
            'Email' : (self.defaultStartElement, self.endEmail),
            'VcsType' : (self.defaultStartElement, self.endVcsType),
            'VcsOptions' : (self.startVcsOptions, self.endVcsOptions),
            'VcsOtherData' : (self.startVcsOtherData, self.endVcsOtherData),
            'Dir' : (self.defaultStartElement, self.endDir),
            'Name' : (self.defaultStartElement, self.endName),
            'Source' : (self.startSource, self.endSource),
            'Form' : (self.startForm, self.endForm),
            'Translation' : (self.startTranslation, self.endTranslation),
            'TranslationPattern' : (self.defaultStartElement, 
                                    self.endTranslationPattern),
            'TranslationsBinPath' : (self.startTranslationsBinPath, 
                                     self.endTranslationsBinPath),
            'TranslationException' : (self.startTranslationException, 
                                      self.endTranslationException),
            'Resource' : (self.startResource, self.endResource),
            'Interface' : (self.startInterface, self.endInterface),
            'Other' : (self.startOther, self.endOther),
            'MainScript' : (self.startMainScript, self.endMainScript),
            'FiletypeAssociation' : (self.startFiletypeAssociation, 
                                     self.defaultEndElement),
            'LexerAssociation' : (self.startLexerAssociation, 
                                  self.defaultEndElement), 
            'ProjectTypeSpecificData' : (self.startProjectTypeSpecificData, 
                                     self.endProjectTypeSpecificData), 
            'DocumentationParams' : (self.startDocumentationParams, 
                                     self.endDocumentationParams), 
            'PackagersParams' : (self.startPackagersParams, self.endPackagersParams), 
            'CheckersParams' : (self.startCheckersParams, self.endCheckersParams),
            'OtherToolsParams' : (self.startOtherToolsParams, self.endOtherToolsParams),
            # parameters kept for backward compatibility
            'UIType' : (self.defaultStartElement, self.endUIType),
            'TranslationPrefix' : (self.startTranslationPrefix, 
                                   self.endTranslationPrefix),
            'Eric3DocParams' : (self.defaultStartElement, self.endEric3DocParams),
            'Eric3ApiParams' : (self.defaultStartElement, self.endEric3ApiParams),
            'Eric4DocParams' : (self.startEric4DocParams, self.endEric4DocParams),
            'Eric4ApiParams' : (self.startEric4ApiParams, self.endEric4ApiParams),
            'CxfreezeParams' : (self.startCxfreezeParams, self.endCxfreezeParams),
            'PyLintParams' : (self.startPyLintParams, self.endPyLintParams),
            # for really old project files
            'HappyDocParams' : (self.defaultStartElement, self.defaultEndElement),
        })
        
        self.project = project
        
    def startDocumentProject(self):
        """
        Handler called, when the document parsing is started.
        """
        self.version = ''
        self.pathStack = []
    
    ###################################################
    ## below follow the individual handler functions
    ###################################################
    
    def endLanguage(self):
        """
        Handler method for the "Language" end tag.
        """
        self.buffer = self.utf8_to_code(self.buffer)
        self.project.pdata["SPELLLANGUAGE"] = [self.buffer]
        
    def endProjectWordList(self):
        """
        Handler method for the "ProjectWordList" end tag.
        """
        path = unicode(Utilities.toNativeSeparators(self.utf8_to_code(self.buffer)))
        self.project.pdata["SPELLWORDS"] = [path]
        
    def endProjectExcludeList(self):
        """
        Handler method for the "ProjectExcludeList" end tag.
        """
        path = unicode(Utilities.toNativeSeparators(self.utf8_to_code(self.buffer)))
        self.project.pdata["SPELLEXCLUDES"] = [path]
        
    def startProgLanguage(self, attrs):
        """
        Handler method for the "Source" start tag.
        
        @param attrs list of tag attributes
        """
        mixedLanguage = int(attrs.get("mixed", "0"))
        self.project.pdata["MIXEDLANGUAGE"] = [mixedLanguage]
        self.buffer = ""
        
    def endProgLanguage(self):
        """
        Handler method for the "ProgLanguage" end tag.
        """
        self.buffer = self.utf8_to_code(self.buffer)
        self.project.pdata["PROGLANGUAGE"] = [self.buffer]
        
    def endProjectType(self):
        """
        Handler method for the "ProjectType" end tag.
        """
        self.buffer = self.utf8_to_code(self.buffer)
        self.project.pdata["PROJECTTYPE"] = [self.buffer]
        
    def endDescription(self):
        """
        Handler method for the "Description" end tag.
        """
        self.buffer = self.unescape(self.utf8_to_code(self.buffer))
        if self.version >= '4.3':
            self.project.pdata["DESCRIPTION"] = [self.decodedNewLines(self.buffer)]
        else:
            self.project.pdata["DESCRIPTION"] = [self.buffer]
        
    def endVersion(self):
        """
        Handler method for the "Version" end tag.
        """
        self.buffer = self.unescape(self.utf8_to_code(self.buffer))
        self.project.pdata["VERSION"] = [self.buffer]
        
    def endAuthor(self):
        """
        Handler method for the "Author" end tag.
        """
        self.buffer = self.unescape(self.utf8_to_code(self.buffer))
        self.project.pdata["AUTHOR"] = [self.buffer]
        
    def endEmail(self):
        """
        Handler method for the "Email" end tag.
        """
        self.buffer = self.unescape(self.utf8_to_code(self.buffer))
        self.project.pdata["EMAIL"] = [self.buffer]
        
    def endVcsType(self):
        """
        Handler method for the "VcsType" end tag.
        """
        self.buffer = self.utf8_to_code(self.buffer)
        self.project.pdata["VCS"] = [self.buffer]
        
    def startVcsOptions(self, attrs):
        """
        Handler method for the "VcsOptions" start tag.
        
        @param attrs list of tag attributes
        """
        self.defaultStartElement(attrs)
        if self.version >= '4.0':
            self._prepareBasics()
        
    def endVcsOptions(self):
        """
        Handler method for the "VcsOptions" end tag.
        """
        if self.version >= '4.0':
            try:
                self.project.pdata["VCSOPTIONS"] = [self.stack[-1]]
            except IndexError:
                self.project.pdata["VCSOPTIONS"] = []
        else:
            self.buffer = self.utf8_to_code(self.buffer)
            if self.buffer:
                if self.version > '3.8':
                    self.project.pdata["VCSOPTIONS"] = \
                        [pickle.loads(self.buffer.encode("utf8"))]
                else:
                    if self.project.checkSecurityString(self.buffer, 'VcsOptions'):
                        self.project.pdata["VCSOPTIONS"] = []
                    else:
                        self.project.pdata["VCSOPTIONS"] = [eval(self.buffer)]
            else:
                self.project.pdata["VCSOPTIONS"] = []
        
    def startVcsOtherData(self, attrs):
        """
        Handler method for the "VcsOtherData" start tag.
        
        @param attrs list of tag attributes
        """
        self.defaultStartElement(attrs)
        if self.version >= '4.0':
            self._prepareBasics()
        
    def endVcsOtherData(self):
        """
        Handler method for the "VcsOtherData" end tag.
        """
        if self.version >= '4.0':
            try:
                self.project.pdata["VCSOTHERDATA"] = [self.stack[-1]]
            except IndexError:
                self.project.pdata["VCSOTHERDATA"] = []
        else:
            self.buffer = self.utf8_to_code(self.buffer)
            if self.buffer:
                if self.version > '3.8':
                    self.project.pdata["VCSOTHERDATA"] = \
                        [pickle.loads(self.buffer.encode("utf8"))]
                else:
                    if self.project.checkSecurityString(self.buffer, 'VcsOtherData'):
                        self.project.pdata["VCSOTHERDATA"] = []
                    else:
                        self.project.pdata["VCSOTHERDATA"] = [eval(self.buffer)]
            else:
                self.project.pdata["VCSOTHERDATA"] = []
        
    def startProjectTypeSpecificData(self, attrs):
        """
        Handler method for the "ProjectTypeSpecificData" start tag.
        
        @param attrs list of tag attributes
        """
        self.defaultStartElement(attrs)
        self._prepareBasics()
        
    def endProjectTypeSpecificData(self):
        """
        Handler method for the "ProjectTypeSpecificData" end tag.
        """
        try:
            self.project.pdata["PROJECTTYPESPECIFICDATA"] = self.stack[-1]
        except IndexError:
            self.project.pdata["PROJECTTYPESPECIFICDATA"] = {}
        
    def startDocumentationParams(self, attrs):
        """
        Handler method for the "DocumentationParams" start tag.
        
        @param attrs list of tag attributes
        """
        self.defaultStartElement(attrs)
        self._prepareBasics()
        
    def endDocumentationParams(self):
        """
        Handler method for the "DocumentationParams" end tag.
        """
        try:
            self.project.pdata["DOCUMENTATIONPARMS"] = self.stack[-1]
        except IndexError:
            self.project.pdata["DOCUMENTATIONPARMS"] = {}
        
    def startPackagersParams(self, attrs):
        """
        Handler method for the "PackagersParams" start tag.
        
        @param attrs list of tag attributes
        """
        self.defaultStartElement(attrs)
        self._prepareBasics()
        
    def endPackagersParams(self):
        """
        Handler method for the "PackagersParams" end tag.
        """
        try:
            self.project.pdata["PACKAGERSPARMS"] = self.stack[-1]
        except IndexError:
            self.project.pdata["PACKAGERSPARMS"] = {}
        
    def startCheckersParams(self, attrs):
        """
        Handler method for the "CheckersParams" start tag.
        
        @param attrs list of tag attributes
        """
        self.defaultStartElement(attrs)
        self._prepareBasics()
        
    def endCheckersParams(self):
        """
        Handler method for the "CheckersParams" end tag.
        """
        try:
            self.project.pdata["CHECKERSPARMS"] = self.stack[-1]
        except IndexError:
            self.project.pdata["CHECKERSPARMS"] = {}
        
    def startOtherToolsParams(self, attrs):
        """
        Handler method for the "OtherToolsParams" start tag.
        
        @param attrs list of tag attributes
        """
        self.defaultStartElement(attrs)
        self._prepareBasics()
        
    def endOtherToolsParams(self):
        """
        Handler method for the "OtherToolsParams" end tag.
        """
        try:
            self.project.pdata["OTHERTOOLSPARMS"] = self.stack[-1]
        except IndexError:
            self.project.pdata["OTHERTOOLSPARMS"] = {}
        
    def endDir(self):
        """
        Handler method for the "Dir" end tag.
        """
        self.buffer = self.utf8_to_code(self.buffer)
        self.pathStack.append(self.buffer)
        
    def endName(self):
        """
        Handler method for the "Name" end tag.
        """
        self.buffer = self.utf8_to_code(self.buffer)
        self.pathStack.append(self.buffer)
        
    def endTranslationPattern(self):
        """
        Handler method for the "TranslationPattern" end tag.
        """
        self.project.pdata["TRANSLATIONPATTERN"].append(
            unicode(Utilities.toNativeSeparators(self.utf8_to_code(self.buffer))))
        
    def startTranslationsBinPath(self, attrs):
        """
        Handler method for the "TranslationsBinPath" start tag.
        
        @param attrs list of tag attributes
        """
        self.pathStack = []
        self.buffer = ""
        
    def endTranslationsBinPath(self):
        """
        Handler method for the "TranslationsBinPath" end tag.
        """
        if self.version >= '4.3':
            path = unicode(Utilities.toNativeSeparators(self.utf8_to_code(self.buffer)))
        else:
            path = self.__buildPath()
        self.project.pdata["TRANSLATIONSBINPATH"].append(path)
        
    def startSource(self, attrs):
        """
        Handler method for the "Source" start tag.
        
        @param attrs list of tag attributes
        """
        self.pathStack = []
        self.buffer = ""
        
    def endSource(self):
        """
        Handler method for the "Source" end tag.
        """
        if self.version >= '4.3':
            path = unicode(Utilities.toNativeSeparators(self.utf8_to_code(self.buffer)))
        else:
            path = self.__buildPath()
        self.project.pdata["SOURCES"].append(path)
        
    def startForm(self, attrs):
        """
        Handler method for the "Form" start tag.
        
        @param attrs list of tag attributes
        """
        self.pathStack = []
        self.buffer = ""
        
    def endForm(self):
        """
        Handler method for the "Form" end tag.
        """
        if self.version >= '4.3':
            path = unicode(Utilities.toNativeSeparators(self.utf8_to_code(self.buffer)))
        else:
            path = self.__buildPath()
        self.project.pdata["FORMS"].append(path)
        
    def startTranslation(self, attrs):
        """
        Handler method for the "Translation" start tag.
        
        @param attrs list of tag attributes
        """
        self.pathStack = []
        self.buffer = ""
        
    def endTranslation(self):
        """
        Handler method for the "Translation" end tag.
        """
        if self.version >= '4.3':
            path = unicode(Utilities.toNativeSeparators(self.utf8_to_code(self.buffer)))
        else:
            path = self.__buildPath()
        self.project.pdata["TRANSLATIONS"].append(path)
        
    def startTranslationException(self, attrs):
        """
        Handler method for the "TranslationException" start tag.
        
        @param attrs list of tag attributes
        """
        self.pathStack = []
        self.buffer = ""
        
    def endTranslationException(self):
        """
        Handler method for the "TranslationException" end tag.
        """
        if self.version >= '4.3':
            path = unicode(Utilities.toNativeSeparators(self.utf8_to_code(self.buffer)))
        else:
            path = self.__buildPath()
        self.project.pdata["TRANSLATIONEXCEPTIONS"].append(path)
        
    def startResource(self, attrs):
        """
        Handler method for the "Resource" start tag.
        
        @param attrs list of tag attributes
        """
        self.pathStack = []
        self.buffer = ""
        
    def endResource(self):
        """
        Handler method for the "Resource" end tag.
        """
        if self.version >= '4.3':
            path = unicode(Utilities.toNativeSeparators(self.utf8_to_code(self.buffer)))
        else:
            path = self.__buildPath()
        self.project.pdata["RESOURCES"].append(path)
        
    def startInterface(self, attrs):
        """
        Handler method for the "Interface" start tag.
        
        @param attrs list of tag attributes
        """
        self.pathStack = []
        self.buffer = ""
        
    def endInterface(self):
        """
        Handler method for the "Interface" end tag.
        """
        if self.version >= '4.3':
            path = unicode(Utilities.toNativeSeparators(self.utf8_to_code(self.buffer)))
        else:
            path = self.__buildPath()
        self.project.pdata["INTERFACES"].append(path)
        
    def startOther(self, attrs):
        """
        Handler method for the "Other" start tag.
        
        @param attrs list of tag attributes
        """
        self.pathStack = []
        self.buffer = ""
        
    def endOther(self):
        """
        Handler method for the "Other" end tag.
        """
        if self.version >= '4.3':
            path = unicode(Utilities.toNativeSeparators(self.utf8_to_code(self.buffer)))
        else:
            path = self.__buildPath()
        self.project.pdata["OTHERS"].append(path)
        
    def startMainScript(self, attrs):
        """
        Handler method for the "MainScript" start tag.
        
        @param attrs list of tag attributes
        """
        self.pathStack = []
        self.buffer = ""
        
    def endMainScript(self):
        """
        Handler method for the "MainScript" end tag.
        """
        if self.version >= '4.3':
            path = unicode(Utilities.toNativeSeparators(self.utf8_to_code(self.buffer)))
        else:
            path = self.__buildPath()
        self.project.pdata["MAINSCRIPT"] = [path]
        
    def startFiletypeAssociation(self, attrs):
        """
        Handler method for the "FiletypeAssociation" start tag.
        
        @param attrs list of tag attributes
        """
        pattern = attrs.get("pattern", "")
        filetype = attrs.get("type", "OTHERS")
        if pattern:
            self.project.pdata["FILETYPES"][pattern] = filetype
        
    def startLexerAssociation(self, attrs):
        """
        Handler method for the "LexerAssociation" start tag.
        
        @param attrs list of tag attributes
        """
        pattern = attrs.get("pattern", "")
        lexer = attrs.get("lexer", "")
        if pattern:
            self.project.pdata["LEXERASSOCS"][pattern] = lexer
        
    def __buildPath(self):
        """
        Private method to assemble a path.
        
        @return The ready assembled path. (string)
        """
        path = ""
        if self.pathStack and not self.pathStack[0]:
            self.pathStack[0] = os.sep
        for p in self.pathStack:
            path = os.path.join(path, p)
        return path
        
    def startProject(self, attrs):
        """
        Handler method for the "Project" start tag.
        
        @param attrs list of tag attributes
        """
        self.version = attrs.get('version', projectFileFormatVersion)
        
    def getVersion(self):
        """
        Public method to retrieve the version of the project.
        
        @return String containing the version number.
        """
        return self.version
    
    ###############################################################
    ## below are handler methods kept for backward compatibility
    ###############################################################
    
    def endUIType(self):
        """
        Handler method for the "UIType" end tag.
        """
        self.buffer = self.utf8_to_code(self.buffer)
        self.project.pdata["PROJECTTYPE"] = [self.buffer]
        
    def startTranslationPrefix(self, attrs):
        """
        Handler method for the "TranslationPrefix" start tag.
        
        @param attrs list of tag attributes
        """
        self.pathStack = []
        self.buffer = ""
        
    def endTranslationPrefix(self):
        """
        Handler method for the "TranslationPrefix" end tag.
        """
        if self.version >= '4.3':
            path = unicode(Utilities.toNativeSeparators(self.utf8_to_code(self.buffer)))
        else:
            path = self.__buildPath()
        if not path.endswith("_"):
            path = "%s_" % path
        self.project.pdata["TRANSLATIONPATTERN"].append("%s%%language%%.ts" % path)
        
    def endEric3DocParams(self):
        """
        Handler method for the "Eric3DocParams" end tag.
        """
        self.buffer = self.utf8_to_code(self.buffer)
        if self.buffer:
            if self.version > '3.8':
                self.project.pdata["DOCUMENTATIONPARMS"]["ERIC4DOC"] = \
                    pickle.loads(self.buffer.encode("utf8"))
            else:
                if not self.project.checkSecurityString(self.buffer, 'Eric4DocParams'):
                    self.project.pdata["DOCUMENTATIONPARMS"]["ERIC4DOC"] = \
                        eval(self.buffer)
        
    def endEric3ApiParams(self):
        """
        Handler method for the "Eric3ApiParams" end tag.
        """
        self.buffer = self.utf8_to_code(self.buffer)
        if self.buffer:
            if self.version > '3.8':
                self.project.pdata["DOCUMENTATIONPARMS"]["ERIC4API"] = \
                    pickle.loads(self.buffer.encode("utf8"))
            else:
                if not self.project.checkSecurityString(self.buffer, 'Eric4ApiParams'):
                    self.project.pdata["DOCUMENTATIONPARMS"]["ERIC4API"] = \
                        eval(self.buffer)
        
    def startEric4DocParams(self, attrs):
        """
        Handler method for the "Eric4DocParams" start tag.
        
        @param attrs list of tag attributes
        """
        self.defaultStartElement(attrs)
        self._prepareBasics()
        
    def endEric4DocParams(self):
        """
        Handler method for the "Eric4DocParams" end tag.
        """
        try:
            self.project.pdata["DOCUMENTATIONPARMS"]["ERIC4DOC"] = self.stack[-1]
        except IndexError:
            pass
        
    def startEric4ApiParams(self, attrs):
        """
        Handler method for the "Eric4ApiParams" start tag.
        
        @param attrs list of tag attributes
        """
        self.defaultStartElement(attrs)
        self._prepareBasics()
        
    def endEric4ApiParams(self):
        """
        Handler method for the "Eric4ApiParams" end tag.
        """
        try:
            self.project.pdata["DOCUMENTATIONPARMS"]["ERIC4API"] = self.stack[-1]
        except IndexError:
            pass
        
    def startCxfreezeParams(self, attrs):
        """
        Handler method for the "CxfreezeParams" start tag.
        
        @param attrs list of tag attributes
        """
        self.defaultStartElement(attrs)
        if self.version >= '4.0':
            self._prepareBasics()
        
    def endCxfreezeParams(self):
        """
        Handler method for the "CxfreezeParams" end tag.
        """
        if self.version >= '4.0':
            try:
                self.project.pdata["PACKAGERSPARMS"]["CXFREEZE"] = self.stack[-1]
            except IndexError:
                self.project.pdata["PACKAGERSPARMS"] = {}
        else:
            self.buffer = self.utf8_to_code(self.buffer)
            if self.buffer:
                if self.version > '3.8':
                    self.project.pdata["PACKAGERSPARMS"]["CXFREEZE"] = \
                        pickle.loads(self.buffer.encode("utf8"))
                else:
                    if self.project.checkSecurityString(self.buffer, 'CxfreezeParams'):
                        self.project.pdata["PACKAGERSPARMS"] = {}
                    else:
                        self.project.pdata["PACKAGERSPARMS"]["CXFREEZE"] = \
                            eval(self.buffer)
            else:
                self.project.pdata["PACKAGERSPARMS"] = {}
        
    def startPyLintParams(self, attrs):
        """
        Handler method for the "PyLintParams" start tag.
        
        @param attrs list of tag attributes
        """
        self.defaultStartElement(attrs)
        if self.version >= '4.0':
            self._prepareBasics()
        
    def endPyLintParams(self):
        """
        Handler method for the "PyLintParams" end tag.
        """
        if self.version >= '4.0':
            try:
                self.project.pdata["CHECKERSPARMS"]["PYLINT"] = self.stack[-1]
            except IndexError:
                self.project.pdata["CHECKERSPARMS"] = {}
        else:
            self.buffer = self.utf8_to_code(self.buffer)
            if self.buffer:
                if self.version > '3.8':
                    self.project.pdata["CHECKERSPARMS"]["PYLINT"] = \
                        pickle.loads(self.buffer.encode("utf8"))
                else:
                    if self.project.checkSecurityString(self.buffer, 'PyLintParams'):
                        self.project.pdata["CHECKERSPARMS"]["PYLINT"] = {}
                    else:
                        self.project.pdata["CHECKERSPARMS"]["PYLINT"] = eval(self.buffer)
            else:
                self.project.pdata["CHECKERSPARMS"]["PYLINT"] = {}
