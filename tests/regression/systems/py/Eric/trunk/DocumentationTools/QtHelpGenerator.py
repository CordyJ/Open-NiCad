# -*- coding: utf-8 -*-

# Copyright (c) 2009 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the QtHelp generator for the builtin documentation generator.
"""

import sys
import os
import shutil
import codecs
import subprocess

from Utilities import joinext, relpath, html_encode

HelpCollection = r"""<?xml version="1.0" encoding="utf-8" ?>
<QHelpCollectionProject version="1.0">
  <docFiles>
    <register>
      <file>%(helpfile)s</file>
    </register>
  </docFiles>
</QHelpCollectionProject>
"""

HelpProject = r"""<?xml version="1.0" encoding="UTF-8"?>
<QtHelpProject version="1.0">
  <namespace>%(namespace)s</namespace>
  <virtualFolder>%(folder)s</virtualFolder>
  <customFilter name="%(filter_name)s">
%(filter_attributes)s
  </customFilter>
  <filterSection>
%(filter_attributes)s
    <toc>
%(sections)s
    </toc>
    <keywords>
%(keywords)s
    </keywords>
    <files>
%(files)s
    </files>
  </filterSection>
</QtHelpProject>
"""

HelpProjectFile = 'source.qhp'
HelpHelpFile = 'source.qch'
HelpCollectionProjectFile = 'source.qhcp'
HelpCollectionFile = 'collection.qhc'

class QtHelpGenerator(object):
    """
    Class implementing the QtHelp generator for the builtin documentation generator.
    """
    def __init__(self, htmlDir, 
                 outputDir, namespace, virtualFolder, filterName, filterAttributes, 
                 title, createCollection):
        """
        Constructor
        
        @param htmlDir directory containing the HTML files (string)
        @param outputDir output directory for the files (string)
        @param namespace namespace to be used (string)
        @param virtualFolder virtual folder to be used (string)
        @param filterName name of the custom filter (string)
        @param filterAttributes ':' separated list of filter attributes (string)
        @param title title to be used for the generated help (string)
        @param createCollection flag indicating the generation of the collection
            files (boolean)
        """
        self.htmlDir = htmlDir
        self.outputDir = outputDir
        self.namespace = namespace
        self.virtualFolder = virtualFolder
        self.filterName = filterName
        self.filterAttributes = filterAttributes and filterAttributes.split(':') or []
        self.relPath = relpath(self.htmlDir, self.outputDir)
        self.title = title
        self.createCollection = createCollection
        
        self.packages = {
            "00index" : {
                "subpackages" : {},
                "modules" : {}
            }
        }
        self.remembered = False
        self.keywords = []
    
    def remember(self, file, moduleDocument, basename=""):
        """
        Public method to remember a documentation file.
        
        @param file The filename to be remembered. (string)
        @param moduleDocument The ModuleDocument object containing the 
            information for the file.
        @param basename The basename of the file hierarchy to be documented.
            The basename is stripped off the filename if it starts with
            the basename.
        """
        self.remembered = True
        if basename:
            file = file.replace(basename, "")
        
        if "__init__" in file:
            dir = os.path.dirname(file)
            udir = os.path.dirname(dir)
            base = os.path.basename(dir)
            if udir:
                upackage = udir.replace(os.sep, ".")
                try:
                    elt = self.packages[upackage]
                except KeyError:
                    elt = self.packages["00index"]
            else:
                elt = self.packages["00index"]
            package = dir.replace(os.sep, ".")
            elt["subpackages"][package] = moduleDocument.name()
            
            self.packages[package] = {
                "subpackages" : {},
                "modules" : {}
            }
            
            kwEntry = ("%s (Package)" % package.split('.')[-1], 
                       joinext("index-%s" % package, ".html"))
            if kwEntry not in self.keywords:
                self.keywords.append(kwEntry)
            
            if moduleDocument.isEmpty():
                return
        
        package = os.path.dirname(file).replace(os.sep, ".")
        try:
            elt = self.packages[package]
        except KeyError:
            elt = self.packages["00index"]
        elt["modules"][moduleDocument.name()] = moduleDocument.name()
        
        if "__init__" not in file:
            kwEntry = ("%s (Module)" % moduleDocument.name().split('.')[-1], 
                       joinext(moduleDocument.name(), ".html"))
            if kwEntry not in self.keywords:
                self.keywords.append(kwEntry)
        for kw in moduleDocument.getQtHelpKeywords():
            kwEntry = (kw[0], "%s%s" % (joinext(moduleDocument.name(), ".html"), kw[1]))
            if kwEntry not in self.keywords:
                self.keywords.append(kwEntry)
    
    def __generateSections(self, package, level):
        """
        Private method to generate the sections part.
        
        @param package name of the package to process (string)
        @param level indentation level (integer)
        @return sections part (string)
        """
        indent = level * '  '
        indent1 = indent + '  '
        s  = indent + '<section title="%s" ref="%s">\n' % \
            (package == "00index" and self.title or package, 
             package == "00index" and \
                joinext("index", ".html") or \
                joinext("index-%s" % package, ".html"))
        for subpack in sorted(self.packages[package]["subpackages"]):
            s += self.__generateSections(subpack, level + 1)
        for mod in sorted(self.packages[package]["modules"]):
            s += indent1 + '<section title="%s" ref="%s" />\n' % \
                (mod, joinext(mod, ".html"))
        s += indent + '</section>\n'
        return s
    
    def __generateKeywords(self):
        """
        Private method to generate the keywords section.
        
        @return keywords section (string)
        """
        indent = level * '  '
        return "\n".join([])
    
    def generateFiles(self, basename = ""):
        """
        Public method to generate all index files.
        
        @param basename The basename of the file hierarchy to be documented.
            The basename is stripped off the filename if it starts with
            the basename.
        """
        if not self.remembered:
            sys.stderr.write("No QtHelp to generate.\n")
            return
        
        if basename:
            basename = basename.replace(os.sep, ".")
            if not basename.endswith("."):
                basename = "%s." % basename
        
        sections = self.__generateSections("00index", 3)
        filesList = sorted([e for e in os.listdir(self.htmlDir) if e.endswith('.html')])
        files = "\n".join(["      <file>%s</file>" % f for f in filesList])
        filterAttribs = "\n".join(["    <filterAttribute>%s</filterAttribute>" % a \
                                  for a in self.filterAttributes])
        keywords = "\n".join(
            ['      <keyword name="%s" id="%s" ref="%s" />' % \
             (html_encode(kw[0]), html_encode(kw[0]), html_encode(kw[1])) \
             for kw in self.keywords])
        
        helpAttribs = {
            "namespace" : self.namespace, 
            "folder" : self.virtualFolder, 
            "filter_name" : self.filterName, 
            "filter_attributes" : filterAttribs, 
            "sections" : sections, 
            "keywords" : keywords, 
            "files" : files, 
        }
        
        f = codecs.open(os.path.join(self.outputDir, HelpProjectFile), 'w', 'utf-8')
        f.write(HelpProject % helpAttribs)
        f.close()
        
        if self.createCollection and \
           not os.path.exists(os.path.join(self.outputDir, HelpCollectionProjectFile)):
            collectionAttribs = {
                "helpfile" : HelpHelpFile, 
            }
        
            f = codecs.open(os.path.join(self.outputDir, HelpCollectionProjectFile), 
                            'w', 'utf-8')
            f.write(HelpCollection % collectionAttribs)
            f.close()
        
        sys.stdout.write("QtHelp files written.\n")
        sys.stdout.write("Generating QtHelp documentation...\n")
        sys.stdout.flush()
        sys.stderr.flush()
        
        cwd = os.getcwd()
        # generate the compressed files
        shutil.copy(os.path.join(self.outputDir, HelpProjectFile), self.htmlDir)
        os.chdir(self.htmlDir)
        subprocess.call(["qhelpgenerator", "source.qhp", 
                         "-o", os.path.join(self.outputDir, HelpHelpFile)])
        os.remove(HelpProjectFile)
        
        if self.createCollection:
            sys.stdout.write("Generating QtHelp collection...\n")
            sys.stdout.flush()
            sys.stderr.flush()
            os.chdir(self.outputDir)
            subprocess.call(["qcollectiongenerator", "source.qhcp", "-o", "collection.qhc"])
        
        os.chdir(cwd)
