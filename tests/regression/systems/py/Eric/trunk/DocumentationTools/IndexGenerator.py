# -*- coding: utf-8 -*-

# Copyright (c) 2003 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the index generator for the builtin documentation generator.
"""

import sys
import os

import TemplatesListsStyle
import TemplatesListsStyleCSS

from Utilities import joinext

class IndexGenerator(object):
    """
    Class implementing the index generator for the builtin documentation generator.
    """
    def __init__(self, outputDir, colors, stylesheet = None):
        """
        Constructor
        
        @param outputDir The output directory for the files. (string)
        @param colors Dictionary specifying the various colors for the output.
            (dictionary of strings)
        @param stylesheet the style to be used for the generated pages (string)
        """
        self.outputDir = outputDir
        self.packages = {
            "00index" : {
                "description" : "",
                "subpackages" : {},
                "modules" : {}
            }
        }
        self.remembered = False
        
        self.stylesheet = stylesheet
        
        if self.stylesheet:
            self.headerTemplate = TemplatesListsStyleCSS.headerTemplate
            self.footerTemplate = TemplatesListsStyleCSS.footerTemplate
            self.indexBodyTemplate = TemplatesListsStyleCSS.indexBodyTemplate
            self.indexListPackagesTemplate = \
                TemplatesListsStyleCSS.indexListPackagesTemplate
            self.indexListModulesTemplate = \
                TemplatesListsStyleCSS.indexListModulesTemplate
            self.indexListEntryTemplate = TemplatesListsStyleCSS.indexListEntryTemplate
        else:
            self.headerTemplate = TemplatesListsStyle.headerTemplate % colors
            self.footerTemplate = TemplatesListsStyle.footerTemplate % colors
            self.indexBodyTemplate = TemplatesListsStyle.indexBodyTemplate % colors
            self.indexListPackagesTemplate = \
                TemplatesListsStyle.indexListPackagesTemplate % colors
            self.indexListModulesTemplate = \
                TemplatesListsStyle.indexListModulesTemplate % colors
            self.indexListEntryTemplate = \
                TemplatesListsStyle.indexListEntryTemplate % colors
        
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
            elt["subpackages"][package] = moduleDocument.shortDescription()
                
            self.packages[package] = {
                "description" : moduleDocument.description(),
                "subpackages" : {},
                "modules" : {}
            }
            
            if moduleDocument.isEmpty():
                return
            
        package = os.path.dirname(file).replace(os.sep, ".")
        name = os.path.splitext(file)[0].replace(os.sep, ".")
        try:
            elt = self.packages[package]
        except KeyError:
            elt = self.packages["00index"]
        elt["modules"][moduleDocument.name()] = \
            moduleDocument.shortDescription()
    
    def __writeIndex(self, packagename, package):
        """
        Private method to generate an index file for a package.
        
        @param packagename The name of the package. (string)
        @param package A dictionary with information about the package.
        @return The name of the generated index file.
        """
        if packagename == "00index":
            f = os.path.join(self.outputDir, "index")
            title = "Table of contents"
        else:
            f = os.path.join(self.outputDir, "index-%s" % packagename)
            title = packagename
        
        filename = joinext(f, ".html")
        
        subpackages = ""
        modules = ""
        
        # 1) subpackages
        if package["subpackages"]:
            subpacks = package["subpackages"]
            names = subpacks.keys()
            names.sort()
            lst = []
            for name in names:
                link = joinext("index-%s" % name, ".html")
                lst.append(self.indexListEntryTemplate % {
                    "Description" : subpacks[name],
                    "Name" : name.split(".")[-1],
                    "Link" : link,
                })
            subpackages = self.indexListPackagesTemplate % {
                "Entries" : "".join(lst),
            }
            
        # 2) modules
        if package["modules"]:
            mods = package["modules"]
            names = mods.keys()
            names.sort()
            lst = []
            for name in names:
                link = joinext(name, ".html")
                nam = name.split(".")[-1]
                if nam == "__init__":
                    nam = name.split(".")[-2]
                lst.append(self.indexListEntryTemplate % {
                    "Description" : mods[name],
                    "Name" : nam,
                    "Link" : link,
                })
            modules = self.indexListModulesTemplate % {
                "Entries" : "".join(lst),
            }
            
        doc = self.headerTemplate % { \
                "Title" : title,
                "Style" : self.stylesheet} + \
              self.indexBodyTemplate % { \
                "Title" : title,
                "Description" : package["description"],
                "Subpackages" : subpackages,
                "Modules" : modules,
              } + \
              self.footerTemplate
    
        f = open(filename, "wb")
        f.write(doc)
        f.close()
    
        return filename
    
    def writeIndices(self, basename = ""):
        """
        Public method to generate all index files.
        
        @param basename The basename of the file hierarchy to be documented.
            The basename is stripped off the filename if it starts with
            the basename.
        """
        if not self.remembered:
            sys.stderr.write("No index to generate.\n")
            return
            
        if basename:
            basename = basename.replace(os.sep, ".")
            if not basename.endswith("."):
                basename = "%s." % basename
        for package, element in self.packages.items():
            try:
                if basename:
                    package = package.replace(basename,"")
                out = self.__writeIndex(package, element)
            except IOError, v:
                sys.stderr.write("%s error: %s\n" % (package, v[1]))
            else:
                if out:
                    sys.stdout.write("%s ok\n" % out)
    
        sys.stdout.write("Indices written.\n")
        sys.stdout.flush()
        sys.stderr.flush()
