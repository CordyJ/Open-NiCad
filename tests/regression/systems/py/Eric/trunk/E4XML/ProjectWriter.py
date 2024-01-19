# -*- coding: utf-8 -*-

# Copyright (c) 2004 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the writer class for writing an XML project file.
"""

import os
import time

from KdeQt.KQApplication import e4App

from XMLWriterBase import XMLWriterBase
from Config import projectFileFormatVersion

import Preferences
import Utilities

class ProjectWriter(XMLWriterBase):
    """
    Class implementing the writer class for writing an XML project file.
    """
    def __init__(self, file, projectName):
        """
        Constructor
        
        @param file open file (like) object for writing
        @param projectName name of the project (string)
        """
        XMLWriterBase.__init__(self, file)
        
        self.pdata = e4App().getObject("Project").pdata
        self.name = projectName
        
    def writeXML(self):
        """
        Public method to write the XML to the file.
        """
        XMLWriterBase.writeXML(self)
        
        self._write('<!DOCTYPE Project SYSTEM "Project-%s.dtd">' % \
            projectFileFormatVersion)
        
        # add some generation comments
        self._write("<!-- eric4 project file for project %s -->" % self.name)
        if Preferences.getProject("XMLTimestamp"):
            self._write("<!-- Saved: %s -->" % time.strftime('%Y-%m-%d, %H:%M:%S'))
            self._write("<!-- Copyright (C) %s %s, %s -->" % \
                    (time.strftime('%Y'), 
                     self.escape(self.pdata["AUTHOR"][0]), 
                     self.escape(self.pdata["EMAIL"][0])))
        
        # add the main tag
        self._write('<Project version="%s">' % projectFileFormatVersion)
        
        # do the language (used for spell checking)
        self._write('  <Language>%s</Language>' % self.pdata["SPELLLANGUAGE"][0])
        if len(self.pdata["SPELLWORDS"][0]) > 0:
            self._write("  <ProjectWordList>%s</ProjectWordList>" % \
                Utilities.fromNativeSeparators(self.pdata["SPELLWORDS"][0]))
        if len(self.pdata["SPELLEXCLUDES"][0]) > 0:
            self._write("  <ProjectExcludeList>%s</ProjectExcludeList>" % \
                Utilities.fromNativeSeparators(self.pdata["SPELLEXCLUDES"][0]))
        
        # do the programming language
        self._write('  <ProgLanguage mixed="%d">%s</ProgLanguage>' % \
            (self.pdata["MIXEDLANGUAGE"][0], self.pdata["PROGLANGUAGE"][0]))
        
        # do the UI type
        self._write('  <ProjectType>%s</ProjectType>' % self.pdata["PROJECTTYPE"][0])
        
        # do description
        if self.pdata["DESCRIPTION"]:
            self._write("  <Description>%s</Description>" % \
                self.escape(self.encodedNewLines(self.pdata["DESCRIPTION"][0])))
        
        # do version, author and email
        for key in ["VERSION", "AUTHOR", "EMAIL"]:
            element = key.capitalize()
            if self.pdata[key]:
                self._write("  <%s>%s</%s>" % \
                    (element, self.escape(self.pdata[key][0]), element))
            
        # do the translation pattern
        if self.pdata["TRANSLATIONPATTERN"]:
            self._write("  <TranslationPattern>%s</TranslationPattern>" % \
                Utilities.fromNativeSeparators(self.pdata["TRANSLATIONPATTERN"][0]))
        
        # do the binary translations path
        if self.pdata["TRANSLATIONSBINPATH"]:
            self._write("  <TranslationsBinPath>%s</TranslationsBinPath>" % \
                Utilities.fromNativeSeparators(self.pdata["TRANSLATIONSBINPATH"][0]))
        
        # do the sources
        self._write("  <Sources>")
        for name in self.pdata["SOURCES"]:
            self._write("    <Source>%s</Source>" % \
                Utilities.fromNativeSeparators(name))
        self._write("  </Sources>")
        
        # do the forms
        self._write("  <Forms>")
        for name in self.pdata["FORMS"]:
            self._write("    <Form>%s</Form>" % \
                Utilities.fromNativeSeparators(name))
        self._write("  </Forms>")
        
        # do the translations
        self._write("  <Translations>")
        for name in self.pdata["TRANSLATIONS"]:
            self._write("    <Translation>%s</Translation>" % \
                Utilities.fromNativeSeparators(name))
        self._write("  </Translations>")
        
        # do the translation exceptions
        if self.pdata["TRANSLATIONEXCEPTIONS"]:
            self._write("  <TranslationExceptions>")
            for name in self.pdata["TRANSLATIONEXCEPTIONS"]:
                self._write("    <TranslationException>%s</TranslationException>" % \
                    Utilities.fromNativeSeparators(name))
            self._write("  </TranslationExceptions>")
        
        # do the resources
        self._write("  <Resources>")
        for name in self.pdata["RESOURCES"]:
            self._write("    <Resource>%s</Resource>" % \
                Utilities.fromNativeSeparators(name))
        self._write("  </Resources>")
        
        # do the interfaces (IDL)
        self._write("  <Interfaces>")
        for name in self.pdata["INTERFACES"]:
            self._write("    <Interface>%s</Interface>" % \
                Utilities.fromNativeSeparators(name))
        self._write("  </Interfaces>")
        
        # do the others
        self._write("  <Others>")
        for name in self.pdata["OTHERS"]:
            self._write("    <Other>%s</Other>" % \
                Utilities.fromNativeSeparators(name))
        self._write("  </Others>")
        
        # do the main script
        if self.pdata["MAINSCRIPT"]:
            self._write("  <MainScript>%s</MainScript>" % \
                Utilities.fromNativeSeparators(self.pdata["MAINSCRIPT"][0]))
        
        # do the vcs stuff
        self._write("  <Vcs>")
        if self.pdata["VCS"]:
            self._write("    <VcsType>%s</VcsType>" % self.pdata["VCS"][0])
        if self.pdata["VCSOPTIONS"]:
            self._write("    <VcsOptions>")
            self._writeBasics(self.pdata["VCSOPTIONS"][0], 3)
            self._write("    </VcsOptions>")
        if self.pdata["VCSOTHERDATA"]:
            self._write("    <VcsOtherData>")
            self._writeBasics(self.pdata["VCSOTHERDATA"][0], 3)
            self._write("    </VcsOtherData>")
        self._write("  </Vcs>")
        
        # do the filetype associations
        self._write("  <FiletypeAssociations>")
        for pattern, filetype in self.pdata["FILETYPES"].items():
            self._write('    <FiletypeAssociation pattern="%s" type="%s" />' % \
                (pattern, filetype))
        self._write("  </FiletypeAssociations>")
        
        # do the lexer associations
        if self.pdata["LEXERASSOCS"]:
            self._write("  <LexerAssociations>")
            for pattern, lexer in self.pdata["LEXERASSOCS"].items():
                self._write('    <LexerAssociation pattern="%s" lexer="%s" />' % \
                    (pattern, lexer))
            self._write("  </LexerAssociations>")
        
        # do the extra project data stuff
        if len(self.pdata["PROJECTTYPESPECIFICDATA"]):
            self._write("  <ProjectTypeSpecific>")
            if self.pdata["PROJECTTYPESPECIFICDATA"]:
                self._write("    <ProjectTypeSpecificData>")
                self._writeBasics(self.pdata["PROJECTTYPESPECIFICDATA"], 3)
                self._write("    </ProjectTypeSpecificData>")
            self._write("  </ProjectTypeSpecific>")
        
        # do the documentation generators stuff
        if len(self.pdata["DOCUMENTATIONPARMS"]):
            self._write("  <Documentation>")
            if self.pdata["DOCUMENTATIONPARMS"]:
                self._write("    <DocumentationParams>")
                self._writeBasics(self.pdata["DOCUMENTATIONPARMS"], 3)
                self._write("    </DocumentationParams>")
            self._write("  </Documentation>")
        
        # do the packagers stuff
        if len(self.pdata["PACKAGERSPARMS"]):
            self._write("  <Packagers>")
            if self.pdata["PACKAGERSPARMS"]:
                self._write("    <PackagersParams>")
                self._writeBasics(self.pdata["PACKAGERSPARMS"], 3)
                self._write("    </PackagersParams>")
            self._write("  </Packagers>")
        
        # do the checkers stuff
        if len(self.pdata["CHECKERSPARMS"]):
            self._write("  <Checkers>")
            if self.pdata["CHECKERSPARMS"]:
                self._write("    <CheckersParams>")
                self._writeBasics(self.pdata["CHECKERSPARMS"], 3)
                self._write("    </CheckersParams>")
            self._write("  </Checkers>")
        
        # do the other tools stuff
        if len(self.pdata["OTHERTOOLSPARMS"]):
            self._write("  <OtherTools>")
            if self.pdata["OTHERTOOLSPARMS"]:
                self._write("    <OtherToolsParams>")
                self._writeBasics(self.pdata["OTHERTOOLSPARMS"], 3)
                self._write("    </OtherToolsParams>")
            self._write("  </OtherTools>")
        
        self._write("</Project>", newline = False)
