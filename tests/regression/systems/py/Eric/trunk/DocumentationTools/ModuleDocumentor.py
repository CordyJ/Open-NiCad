# -*- coding: utf-8 -*-

# Copyright (c) 2003 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the builtin documentation generator.

The different parts of the module document are assembled from the parsed
Python file. The appearance is determined by several templates defined within
this module.
"""

import sys
import re

import TemplatesListsStyle
import TemplatesListsStyleCSS

from Utilities import html_uencode
from Utilities.ModuleParser import RB_SOURCE

_signal = re.compile(r"""
    ^@signal [ \t]+ 
    (?P<SignalName1>
        [a-zA-Z_] \w* [ \t]* \( [^)]* \)
    )
    [ \t]* (?P<SignalDescription1> .*)
|
    ^@signal [ \t]+ 
    (?P<SignalName2>
        [a-zA-Z_] \w*
    )
    [ \t]+ (?P<SignalDescription2> .*)
""", re.VERBOSE | re.DOTALL | re.MULTILINE).search

_event = re.compile(r"""
    ^@event [ \t]+ 
    (?P<EventName1>
        [a-zA-Z_] \w* [ \t]* \( [^)]* \)
    )
    [ \t]* (?P<EventDescription1> .*)
|
    ^@event [ \t]+ 
    (?P<EventName2>
        [a-zA-Z_] \w*
    )
    [ \t]+ (?P<EventDescription2> .*)
""", re.VERBOSE | re.DOTALL | re.MULTILINE).search

class TagError(Exception):
    """
    Exception class raised, if an invalid documentation tag was found.
    """

class ModuleDocument(object):
    """
    Class implementing the builtin documentation generator.
    """
    def __init__(self, module, colors, stylesheet = None):
        """
        Constructor
        
        @param module the information of the parsed Python file
        @param colors dictionary specifying the various colors for the output
            (dictionary of strings)
        @param stylesheet the style to be used for the generated pages (string)
        """
        self.module = module
        self.empty = True
        
        self.stylesheet = stylesheet
        
        if self.stylesheet:
            self.headerTemplate = TemplatesListsStyleCSS.headerTemplate
            self.footerTemplate = TemplatesListsStyleCSS.footerTemplate
            self.moduleTemplate = TemplatesListsStyleCSS.moduleTemplate
            self.rbFileTemplate = TemplatesListsStyleCSS.rbFileTemplate
            self.classTemplate = TemplatesListsStyleCSS.classTemplate
            self.methodTemplate = TemplatesListsStyleCSS.methodTemplate
            self.constructorTemplate = TemplatesListsStyleCSS.constructorTemplate
            self.rbModuleTemplate = TemplatesListsStyleCSS.rbModuleTemplate
            self.rbModulesClassTemplate = TemplatesListsStyleCSS.rbModulesClassTemplate
            self.functionTemplate = TemplatesListsStyleCSS.functionTemplate
            self.listTemplate = TemplatesListsStyleCSS.listTemplate
            self.listEntryTemplate = TemplatesListsStyleCSS.listEntryTemplate
            self.listEntryNoneTemplate = TemplatesListsStyleCSS.listEntryNoneTemplate
            self.listEntryDeprecatedTemplate = \
                TemplatesListsStyleCSS.listEntryDeprecatedTemplate
            self.listEntrySimpleTemplate = TemplatesListsStyleCSS.listEntrySimpleTemplate
            self.paragraphTemplate = TemplatesListsStyleCSS.paragraphTemplate
            self.parametersListTemplate = TemplatesListsStyleCSS.parametersListTemplate
            self.parametersListEntryTemplate = \
                TemplatesListsStyleCSS.parametersListEntryTemplate
            self.returnsTemplate = TemplatesListsStyleCSS.returnsTemplate
            self.exceptionsListTemplate = TemplatesListsStyleCSS.exceptionsListTemplate
            self.exceptionsListEntryTemplate = \
                TemplatesListsStyleCSS.exceptionsListEntryTemplate
            self.signalsListTemplate = TemplatesListsStyleCSS.signalsListTemplate
            self.signalsListEntryTemplate = \
                TemplatesListsStyleCSS.signalsListEntryTemplate
            self.eventsListTemplate = TemplatesListsStyleCSS.eventsListTemplate
            self.eventsListEntryTemplate = TemplatesListsStyleCSS.eventsListEntryTemplate
            self.deprecatedTemplate = TemplatesListsStyleCSS.deprecatedTemplate
            self.authorInfoTemplate = TemplatesListsStyleCSS.authorInfoTemplate
            self.seeListTemplate = TemplatesListsStyleCSS.seeListTemplate
            self.seeListEntryTemplate = TemplatesListsStyleCSS.seeListEntryTemplate
            self.seeLinkTemplate = TemplatesListsStyleCSS.seeLinkTemplate
            self.sinceInfoTemplate = TemplatesListsStyleCSS.sinceInfoTemplate
        else:
            self.headerTemplate = TemplatesListsStyle.headerTemplate % colors
            self.footerTemplate = TemplatesListsStyle.footerTemplate % colors
            self.moduleTemplate = TemplatesListsStyle.moduleTemplate % colors
            self.rbFileTemplate = TemplatesListsStyle.rbFileTemplate % colors
            self.classTemplate = TemplatesListsStyle.classTemplate % colors
            self.methodTemplate = TemplatesListsStyle.methodTemplate % colors
            self.constructorTemplate = TemplatesListsStyle.constructorTemplate % colors
            self.rbModuleTemplate = TemplatesListsStyle.rbModuleTemplate % colors
            self.rbModulesClassTemplate = \
                TemplatesListsStyle.rbModulesClassTemplate % colors
            self.functionTemplate = TemplatesListsStyle.functionTemplate % colors
            self.listTemplate = TemplatesListsStyle.listTemplate % colors
            self.listEntryTemplate = TemplatesListsStyle.listEntryTemplate % colors
            self.listEntryNoneTemplate = \
                TemplatesListsStyle.listEntryNoneTemplate % colors
            self.listEntryDeprecatedTemplate = \
                TemplatesListsStyle.listEntryDeprecatedTemplate % colors
            self.listEntrySimpleTemplate = \
                TemplatesListsStyle.listEntrySimpleTemplate % colors
            self.paragraphTemplate = TemplatesListsStyle.paragraphTemplate % colors
            self.parametersListTemplate = \
                TemplatesListsStyle.parametersListTemplate % colors
            self.parametersListEntryTemplate = \
                TemplatesListsStyle.parametersListEntryTemplate % colors
            self.returnsTemplate = TemplatesListsStyle.returnsTemplate % colors
            self.exceptionsListTemplate = \
                TemplatesListsStyle.exceptionsListTemplate % colors
            self.exceptionsListEntryTemplate = \
                TemplatesListsStyle.exceptionsListEntryTemplate % colors
            self.signalsListTemplate = TemplatesListsStyle.signalsListTemplate % colors
            self.signalsListEntryTemplate = \
                TemplatesListsStyle.signalsListEntryTemplate % colors
            self.eventsListTemplate = TemplatesListsStyle.eventsListTemplate % colors
            self.eventsListEntryTemplate = \
                TemplatesListsStyle.eventsListEntryTemplate % colors
            self.deprecatedTemplate = TemplatesListsStyle.deprecatedTemplate % colors
            self.authorInfoTemplate = TemplatesListsStyle.authorInfoTemplate % colors
            self.seeListTemplate = TemplatesListsStyle.seeListTemplate % colors
            self.seeListEntryTemplate = TemplatesListsStyle.seeListEntryTemplate % colors
            self.seeLinkTemplate = TemplatesListsStyle.seeLinkTemplate % colors
            self.sinceInfoTemplate = TemplatesListsStyle.sinceInfoTemplate % colors
        
        self.keywords = []  # list of tuples containing the name (string) and 
                            # the ref (string). The ref is without the filename part.
        self.generated = False
        
    def isEmpty(self):
        """
        Public method to determine, if the module contains any classes or functions.
        
        @return Flag indicating an empty module (i.e. __init__.py without
            any contents)
        """
        return self.empty
        
    def name(self):
        """
        Public method used to get the module name.
        
        @return The name of the module. (string)
        """
        return self.module.name
        
    def description(self):
        """
        Public method used to get the description of the module.
        
        @return The description of the module. (string)
        """
        return self.__formatDescription(self.module.description)
        
    def shortDescription(self):
        """
        Public method used to get the short description of the module.
        
        The short description is just the first line of the modules
        description.
        
        @return The short description of the module. (string)
        """
        return self.__getShortDescription(self.module.description)
        
    def genDocument(self):
        """
        Public method to generate the source code documentation.
        
        @return The source code documentation. (string)
        """
        doc = self.headerTemplate % { \
                'Title' : self.module.name,
                'Style' : self.stylesheet} + \
              self.__genModuleSection() + \
              self.footerTemplate
        self.generated = True
        return doc
        
    def __genModuleSection(self):
        """
        Private method to generate the body of the document.
        
        @return The body of the document. (string)
        """
        globalsList = self.__genGlobalsListSection()
        classList = self.__genClassListSection()
        functionList = self.__genFunctionListSection()
        try:
            if self.module.type == RB_SOURCE:
                rbModulesList = self.__genRbModulesListSection()
                modBody = self.rbFileTemplate % { \
                    'Module' : self.module.name,
                    'ModuleDescription' : \
                        self.__formatDescription(self.module.description),
                    'GlobalsList' : globalsList, 
                    'ClassList' : classList,
                    'RbModulesList' : rbModulesList,
                    'FunctionList' : functionList,
                }
            else:
                modBody = self.moduleTemplate % { \
                    'Module' : self.module.name,
                    'ModuleDescription' : \
                        self.__formatDescription(self.module.description),
                    'GlobalsList' : globalsList, 
                    'ClassList' : classList,
                    'FunctionList' : functionList,
                }
        except TagError, e:
            sys.stderr.write("Error in tags of description of module %s.\n" % \
                self.module.name)
            sys.stderr.write("%s\n" % e)
            return ""
            
        classesSection = self.__genClassesSection()
        functionsSection = self.__genFunctionsSection()
        if self.module.type == RB_SOURCE:
            rbModulesSection = self.__genRbModulesSection()
        else:
            rbModulesSection = ""
        return "%s%s%s%s" % (modBody, classesSection, rbModulesSection, functionsSection)
        
    def __genListSection(self, names, dict, kwSuffix = ""):
        """
        Private method to generate a list section of the document.
        
        @param names The names to appear in the list. (list of strings)
        @param dict A dictionary containing all relevant information.
        @param kwSuffix suffix to be used for the QtHelp keywords (string)
        @return The list section. (string)
        """
        lst = []
        for name in names:
            lst.append(self.listEntryTemplate % { \
                'Link' : "%s" % name,
                'Name' : dict[name].name,
                'Description' : self.__getShortDescription(dict[name].description),
                'Deprecated' : self.__checkDeprecated(dict[name].description) and \
                    self.listEntryDeprecatedTemplate or "",
            })
            if kwSuffix:
                n = "%s (%s)" % (name, kwSuffix)
            else:
                n = "%s" % name
            self.keywords.append((n, "#%s" % name))
        return ''.join(lst)
        
    def __genGlobalsListSection(self, class_ = None):
        """
        Private method to generate the section listing all global attributes of
        the module.
        
        @param class_ reference to a class object (Class)
        @return The globals list section. (string)
        """
        if class_ is not None:
            attrNames = sorted(class_.globals.keys())
        else:
            attrNames = sorted(self.module.globals.keys())
        if attrNames:
            s = ''.join(
                [self.listEntrySimpleTemplate % {'Name' : name} for name in attrNames])
        else:
            s = self.listEntryNoneTemplate
        return self.listTemplate % { \
            'Entries' : s,
        }
        
    def __genClassListSection(self):
        """
        Private method to generate the section listing all classes of the module.
        
        @return The classes list section. (string)
        """
        names = self.module.classes.keys()
        names.sort()
        if names:
            self.empty = False
            s = self.__genListSection(names, self.module.classes)
        else:
            s = self.listEntryNoneTemplate
        return self.listTemplate % { \
            'Entries' : s,
        }
        
    def __genRbModulesListSection(self):
        """
        Private method to generate the section listing all modules of the file 
        (Ruby only).
        
        @return The modules list section. (string)
        """
        names = self.module.modules.keys()
        names.sort()
        if names:
            self.empty = False
            s = self.__genListSection(names, self.module.modules)
        else:
            s = self.listEntryNoneTemplate
        return self.listTemplate % { \
            'Entries' : s,
        }
        
    def __genFunctionListSection(self):
        """
        Private method to generate the section listing all functions of the module.
        
        @return The functions list section. (string)
        """
        names = self.module.functions.keys()
        names.sort()
        if names:
            self.empty = False
            s = self.__genListSection(names, self.module.functions)
        else:
            s = self.listEntryNoneTemplate
        return self.listTemplate % { \
            'Entries' : s,
        }
        
    def __genClassesSection(self):
        """
        Private method to generate the document section with details about classes.
        
        @return The classes details section. (string)
        """
        classNames = self.module.classes.keys()
        classNames.sort()
        classes = []
        for className in classNames:
            _class = self.module.classes[className]
            supers = _class.super
            if len(supers) > 0:
                supers = ', '.join(supers)
            else:
                supers = 'None'
            
            globalsList = self.__genGlobalsListSection(_class)
            methList, methBodies = self.__genMethodSection(_class, className)
            
            try:
                clsBody = self.classTemplate % { \
                    'Anchor' : className,
                    'Class' : _class.name,
                    'ClassSuper' : supers,
                    'ClassDescription' : self.__formatDescription(_class.description),
                    'GlobalsList' : globalsList, 
                    'MethodList' : methList,
                    'MethodDetails' : methBodies,
                }
            except TagError, e:
                sys.stderr.write("Error in tags of description of class %s.\n" % \
                    className)
                sys.stderr.write("%s\n" % e)
                clsBody = ""
            
            classes.append(clsBody)
            
        return ''.join(classes)
        
    def __genMethodsListSection(self, names, dict, className, clsName):
        """
        Private method to generate the methods list section of a class.
        
        @param names The names to appear in the list. (list of strings)
        @param dict A dictionary containing all relevant information.
        @param className The class name containing the names.
        @param clsName The visible class name containing the names.
        @return The list section. (string)
        """
        lst = []
        try:
            lst.append(self.listEntryTemplate % { \
                'Link' : "%s.%s" % (className, '__init__'),
                'Name' : clsName,
                'Description' : self.__getShortDescription(dict['__init__'].description),
                'Deprecated' : self.__checkDeprecated(dict['__init__'].description) and \
                               self.listEntryDeprecatedTemplate or "",
            })
            self.keywords.append(("%s (Constructor)" % className, 
                                  "#%s.%s" % (className, '__init__')))
        except KeyError:
            pass
            
        for name in names:
            lst.append(self.listEntryTemplate % { \
                'Link' : "%s.%s" % (className, name),
                'Name' : dict[name].name,
                'Description' : self.__getShortDescription(dict[name].description),
                'Deprecated' : self.__checkDeprecated(dict[name].description) and \
                               self.listEntryDeprecatedTemplate or "",
            })
            self.keywords.append(("%s.%s" % (className, name), 
                                  "#%s.%s" % (className, name)))
        return ''.join(lst)
        
    def __genMethodSection(self, obj, className):
        """
        Private method to generate the method details section.
        
        @param obj Reference to the object being formatted.
        @param className Name of the class containing the method. (string)
        @return The method list and method details section. (tuple of two string)
        """
        methList = []
        methBodies = []
        methods = obj.methods.keys()
        methods.sort()
        
        # first do the constructor
        if '__init__' in methods:
            methods.remove('__init__')
            try:
                methBody = self.constructorTemplate % { \
                    'Anchor' : className,
                    'Class' : obj.name,
                    'Method' : '__init__',
                    'MethodDescription' : \
                        self.__formatDescription(obj.methods['__init__'].description),
                    'Params' : ', '.join(obj.methods['__init__'].parameters[1:]),
                }
            except TagError, e:
                sys.stderr.write("Error in tags of description of method %s.%s.\n" % \
                    (className, '__init__'))
                sys.stderr.write("%s\n" % e)
                methBody = ""
            methBodies.append(methBody)
            
        for method in methods:
            try:
                methBody = self.methodTemplate % { \
                    'Anchor' : className,
                    'Class' : obj.name,
                    'Method' : obj.methods[method].name,
                    'MethodDescription' : \
                        self.__formatDescription(obj.methods[method].description),
                    'Params' : ', '.join(obj.methods[method].parameters[1:]),
                }
            except TagError, e:
                sys.stderr.write("Error in tags of description of method %s.%s.\n" % \
                    (className, method))
                sys.stderr.write("%s\n" % e)
                methBody = ""
            methBodies.append(methBody)
            
        methList = self.__genMethodsListSection(methods, obj.methods, className, obj.name)
        
        if not methList:
            methList = self.listEntryNoneTemplate
        return self.listTemplate % { \
            'Entries' : methList,
            }, ''.join(methBodies)
        
    def __genRbModulesSection(self):
        """
        Private method to generate the document section with details about Ruby modules.
        
        @return The Ruby modules details section. (string)
        """
        rbModulesNames = self.module.modules.keys()
        rbModulesNames.sort()
        rbModules = []
        for rbModuleName in rbModulesNames:
            rbModule = self.module.modules[rbModuleName]
            globalsList = self.__genGlobalsListSection(rbModule)
            methList, methBodies = self.__genMethodSection(rbModule, rbModuleName)
            classList, classBodies = \
                self.__genRbModulesClassesSection(rbModule, rbModuleName)
            
            try:
                rbmBody = self.rbModuleTemplate % { \
                    'Anchor' : rbModuleName,
                    'Module' : rbModule.name,
                    'ModuleDescription' : self.__formatDescription(rbModule.description),
                    'GlobalsList' : globalsList, 
                    'ClassesList' : classList,
                    'ClassesDetails' : classBodies,
                    'FunctionsList' : methList,
                    'FunctionsDetails' : methBodies,
                }
            except TagError, e:
                sys.stderr.write("Error in tags of description of Ruby module %s.\n" % \
                    rbModuleName)
                sys.stderr.write("%s\n" % e)
                rbmBody = ""
            
            rbModules.append(rbmBody)
            
        return ''.join(rbModules)

    def __genRbModulesClassesSection(self, obj, modName):
        """
        Private method to generate the Ruby module classes details section.
        
        @param obj Reference to the object being formatted.
        @param modName Name of the Ruby module containing the classes. (string)
        @return The classes list and classes details section. (tuple of two string)
        """
        classNames = obj.classes.keys()
        classNames.sort()
        classes = []
        for className in classNames:
            _class = obj.classes[className]
            supers = _class.super
            if len(supers) > 0:
                supers = ', '.join(supers)
            else:
                supers = 'None'
            
            classname = "%s.%s" % (modName, className)
            methList, methBodies = self.__genMethodSection(_class, className)
            
            try:
                clsBody = self.rbModulesClassTemplate % { \
                    'Anchor' : className,
                    'Class' : _class.name,
                    'ClassSuper' : supers,
                    'ClassDescription' : self.__formatDescription(_class.description),
                    'MethodList' : methList,
                    'MethodDetails' : methBodies,
                }
            except TagError, e:
                sys.stderr.write("Error in tags of description of class %s.\n" % \
                    className)
                sys.stderr.write("%s\n" % e)
                clsBody = ""
            
            classes.append(clsBody)
            
            
        classesList = \
            self.__genRbModulesClassesListSection(classNames, obj.classes, modName)
        
        if not classesList:
            classesList = self.listEntryNoneTemplate
        return self.listTemplate % { \
            'Entries' : classesList,
            }, ''.join(classes)
        
    def __genRbModulesClassesListSection(self, names, dict, moduleName):
        """
        Private method to generate the classes list section of a Ruby module.
        
        @param names The names to appear in the list. (list of strings)
        @param dict A dictionary containing all relevant information.
        @param moduleName Name of the Ruby module containing the classes. (string)
        @return The list section. (string)
        """
        lst = []
        for name in names:
            lst.append(self.listEntryTemplate % { \
                'Link' : "%s.%s" % (moduleName, name),
                'Name' : dict[name].name,
                'Description' : self.__getShortDescription(dict[name].description),
                'Deprecated' : self.__checkDeprecated(dict[name].description) and \
                               self.listEntryDeprecatedTemplate or "",
            })
            self.keywords.append(("%s.%s" % (moduleName, name), 
                                  "#%s.%s" % (moduleName, name)))
        return ''.join(lst)
        
    def __genFunctionsSection(self):
        """
        Private method to generate the document section with details about functions.
        
        @return The functions details section. (string)
        """
        funcBodies = []
        funcNames = self.module.functions.keys()
        funcNames.sort()
        for funcName in funcNames:
            try:
                funcBody = self.functionTemplate % { \
                    'Anchor' : funcName,
                    'Function' : self.module.functions[funcName].name,
                    'FunctionDescription' : self.__formatDescription(\
                        self.module.functions[funcName].description),
                    'Params' : ', '.join(self.module.functions[funcName].parameters),
                }
            except TagError, e:
                sys.stderr.write("Error in tags of description of function %s.\n" % \
                    funcName)
                sys.stderr.write("%s\n" % e)
                funcBody = ""
            
            funcBodies.append(funcBody)
            
        return ''.join(funcBodies)
        
    def __getShortDescription(self, desc):
        """
        Private method to determine the short description of an object.
        
        The short description is just the first non empty line of the
        documentation string.
        
        @param desc The documentation string. (string)
        @return The short description. (string)
        """
        dlist = desc.splitlines()
        sdlist = []
        descfound = 0
        for desc in dlist:
            desc = desc.strip()
            if desc:
                descfound = 1
                dotpos = desc.find('.')
                if dotpos == -1:
                    sdlist.append(desc.strip())
                else:
                    while dotpos+1 < len(desc) and not desc[dotpos+1].isspace():
                        # don't recognize '.' inside a number or word as stop condition
                        dotpos = desc.find('.', dotpos+1)
                        if dotpos == -1:
                            break
                    if dotpos == -1:
                        sdlist.append(desc.strip())
                    else:
                        sdlist.append(desc[:dotpos+1].strip())
                        break   # break if a '.' is found
            else:
                if descfound:
                    break   # break if an empty line is found
        if sdlist:
            return html_uencode(' '.join(sdlist))
        else:
            return ''
        
    def __checkDeprecated(self, descr):
        """
        Private method to check, if the object to be documented contains a 
        deprecated flag.
        
        @param desc The documentation string. (string)
        @return Flag indicating the deprecation status. (boolean)
        """
        dlist = descr.splitlines()
        for desc in dlist:
            desc = desc.strip()
            if desc.startswith("@deprecated"):
                return True
        return False
        
    def __genParagraphs(self, lines):
        """
        Private method to assemble the descriptive paragraphs of a docstring.
        
        A paragraph is made up of a number of consecutive lines without
        an intermediate empty line. Empty lines are treated as a paragraph
        delimiter.
        
        @param lines A list of individual lines. (list of strings)
        @return Ready formatted paragraphs. (string)
        """
        lst = []
        linelist = []
        for line in lines:
            if line.strip():
                if line == '.':
                    linelist.append("")
                else:
                    linelist.append(html_uencode(line))
            else:
                lst.append(self.paragraphTemplate % { \
                    'Lines' : '\n'.join(linelist)
                })
                linelist = []
        if linelist:
            lst.append(self.paragraphTemplate % { \
                'Lines' : '\n'.join(linelist)
            })
        return ''.join(lst)
        
    def __genDescriptionListSection(self, dictionary, template):
        """
        Private method to generate the list section of a description.
        
        @param dictionary Dictionary containing the info for the
            list section.
        @param template The template to be used for the list. (string)
        @return The list section. (string)
        """
        lst = []
        keys = dictionary.keys()
        keys.sort()
        for key in keys:
            lst.append(template % { \
                'Name' : key,
                'Description' : html_uencode('\n'.join(dictionary[key])),
            })
        return ''.join(lst)
        
    def __genParamDescriptionListSection(self, _list, template):
        """
        Private method to generate the list section of a description.
        
        @param _list List containing the info for the
            list section.
        @param template The template to be used for the list. (string)
        @return The list section. (string)
        """
        lst = []
        for name, lines in _list:
            lst.append(template % { \
                'Name' : name,
                'Description' : html_uencode('\n'.join(lines)),
            })
        return ''.join(lst)
        
    def __formatCrossReferenceEntry(self, entry):
        """
        Private method to format a cross reference entry.
        
        This cross reference entry looks like "package.module#member label".
        
        @param entry the entry to be formatted (string)
        @return formatted entry (string)
        """
        if entry.startswith('"'):
            return entry
        elif entry.startswith('<'):
            entry = entry[3:]
        else:
            try:
                reference, label = entry.split(None, 1)
            except ValueError:
                reference = seeEntryString
                label = seeEntryString
            try:
                path, anchor = reference.split('#', 1)
            except ValueError:
                path = reference
                anchor = ''
            reference = path and "%s.html" % path or ''
            if anchor:
                reference = "%s#%s" % (reference, anchor)
            entry = 'href="%s">%s</a>' % (reference, label)
        
        return self.seeLinkTemplate % { \
            'Link' : entry,
        }
        
    def __genSeeListSection(self, _list, template):
        """
        Private method to generate the "see also" list section of a description.
        
        @param _list List containing the info for the section.
        @param template The template to be used for the list. (string)
        @return The list section. (string)
        """
        lst = []
        for seeEntry in _list:
            seeEntryString = ''.join(seeEntry)
            lst.append(template % { \
                'Link' : html_uencode(self.__formatCrossReferenceEntry(seeEntryString)),
            })
        return '\n'.join(lst)
        
    def __processInlineTags(self, desc):
        """
        Private method to process inline tags.
        
        @param desc One line of the description (string)
        @return processed line with inline tags expanded (string)
        """
        start = desc.find('{@')
        while start != -1:
            stop = desc.find('}', start + 2)
            if stop == -1:
                raise TagError, "Unterminated inline tag.\n%s" % desc
            
            tagText = desc[start + 1:stop]
            if tagText.startswith('@link'):
                parts = tagText.split(None, 1)
                if len(parts) < 2:
                    raise TagError, "Wrong format in inline tag %s.\n%s" % \
                                    (parts[0], desc)
                
                formattedTag = self.__formatCrossReferenceEntry(parts[1])
                desc = desc.replace("{%s}" % tagText, formattedTag)
            else:
                tag = tagText.split(None, 1)[0]
                raise TagError, "Unknown inline tag encountered, %s.\n%s" % \
                                (tag, desc)
            
            start = desc.find('{@')
        
        return desc
        
    def __formatDescription(self, descr):
        """
        Private method to format the contents of the documentation string.
        
        @param descr The contents of the documentation string. (string)
        @exception TagError A tag doesn't have the correct number
            of arguments.
        @return The formated contents of the documentation string. (string)
        """
        if not descr:
            return ""
        
        paragraphs = []
        paramList = []
        returns = []
        exceptionDict = {}
        signalDict = {}
        eventDict = {}
        deprecated = []
        authorInfo = []
        sinceInfo = []
        seeList = []
        lastItem = paragraphs
        inTagSection = False
        
        dlist = descr.splitlines()
        while dlist and not dlist[0]:
            del dlist[0]
        for ditem in dlist:
            ditem = self.__processInlineTags(ditem)
            desc = ditem.strip()
            if desc:
                if desc.startswith("@param") or desc.startswith("@keyparam"):
                    inTagSection = True
                    parts = desc.split(None, 2)
                    if len(parts) < 2:
                        raise TagError, "Wrong format in %s line.\n" % parts[0]
                    paramName = parts[1]
                    if parts[0] == "@keyparam":
                        paramName += '='
                    try:
                        paramList.append([paramName, [parts[2]]])
                    except IndexError:
                        paramList.append([paramName, []])
                    lastItem = paramList[-1][1]
                elif desc.startswith("@return"):
                    inTagSection = True
                    parts = desc.split(None, 1)
                    if len(parts) < 2:
                        raise TagError, "Wrong format in %s line.\n" % parts[0]
                    returns = [parts[1]]
                    lastItem = returns
                elif desc.startswith("@exception") or \
                     desc.startswith("@throws") or \
                     desc.startswith("@raise"):
                    inTagSection = True
                    parts = desc.split(None, 2)
                    if len(parts) < 2:
                        raise TagError, "Wrong format in %s line.\n" % parts[0]
                    excName = parts[1]
                    try:
                        exceptionDict[excName] = [parts[2]]
                    except IndexError:
                        exceptionDict[excName] = []
                    lastItem = exceptionDict[excName]
                elif desc.startswith("@signal"):
                    inTagSection = True
                    m = _signal(desc,0)
                    if m is None:
                        raise TagError, "Wrong format in %s line.\n" % parts[0]
                    signalName = 1 and m.group("SignalName1") \
                                   or m.group("SignalName2")
                    signalDesc = 1 and m.group("SignalDescription1") \
                                   or m.group("SignalDescription2")
                    signalDict[signalName] = []
                    if signalDesc is not None:
                        signalDict[signalName].append(signalDesc)
                    lastItem = signalDict[signalName]
                elif desc.startswith("@event"):
                    inTagSection = True
                    m = _event(desc,0)
                    if m is None:
                        raise TagError, "Wrong format in %s line.\n" % parts[0]
                    eventName = 1 and m.group("EventName1") \
                                   or m.group("EventName2")
                    eventDesc = 1 and m.group("EventDescription1") \
                                   or m.group("EventDescription2")
                    eventDict[eventName] = []
                    if eventDesc is not None:
                        eventDict[eventName].append(eventDesc)
                    lastItem = eventDict[eventName]
                elif desc.startswith("@deprecated"):
                    inTagSection = True
                    parts = desc.split(None, 1)
                    if len(parts) < 2:
                        raise TagError, "Wrong format in %s line.\n" % parts[0]
                    deprecated = [parts[1]]
                    lastItem = deprecated
                elif desc.startswith("@author"):
                    inTagSection = True
                    parts = desc.split(None, 1)
                    if len(parts) < 2:
                        raise TagError, "Wrong format in %s line.\n" % parts[0]
                    authorInfo = [parts[1]]
                    lastItem = authorInfo
                elif desc.startswith("@since"):
                    inTagSection = True
                    parts = desc.split(None, 1)
                    if len(parts) < 2:
                        raise TagError, "Wrong format in %s line.\n" % parts[0]
                    sinceInfo = [parts[1]]
                    lastItem = sinceInfo
                elif desc.startswith("@see"):
                    inTagSection = True
                    parts = desc.split(None, 1)
                    if len(parts) < 2:
                        raise TagError, "Wrong format in %s line.\n" % parts[0]
                    seeList.append([parts[1]])
                    lastItem = seeList[-1]
                elif desc.startswith("@@"):
                    lastItem.append(desc[1:])
                elif desc.startswith("@"):
                    tag = desc.split(None, 1)[0]
                    raise TagError, "Unknown tag encountered, %s.\n" % tag
                else:
                    lastItem.append(ditem)
            elif not inTagSection:
                lastItem.append(ditem)
        
        if paragraphs:
            description = self.__genParagraphs(paragraphs)
        else:
            description = ""
        
        if paramList:
            parameterSect = self.parametersListTemplate % { \
                'Parameters' : self.__genParamDescriptionListSection(paramList,
                               self.parametersListEntryTemplate)
            }
        else:
            parameterSect = ""
        
        if returns:
            returnSect = self.returnsTemplate % html_uencode('\n'.join(returns))
        else:
            returnSect = ""
        
        if exceptionDict:
            exceptionSect = self.exceptionsListTemplate % { \
                'Exceptions' : self.__genDescriptionListSection(exceptionDict,
                               self.exceptionsListEntryTemplate)
            }
        else:
            exceptionSect = ""
        
        if signalDict:
            signalSect = self.signalsListTemplate % { \
                'Signals' : self.__genDescriptionListSection(signalDict,
                               self.signalsListEntryTemplate)
            }
        else:
            signalSect = ""
        
        if eventDict:
            eventSect = self.eventsListTemplate % { \
                'Events' : self.__genDescriptionListSection(eventDict,
                               self.eventsListEntryTemplate)
            }
        else:
            eventSect = ""
        
        if deprecated:
            deprecatedSect = self.deprecatedTemplate % { \
                'Lines' : html_uencode('\n'.join(deprecated)),
            }
        else:
            deprecatedSect = ""
        
        if authorInfo:
            authorInfoSect = self.authorInfoTemplate % { \
                'Authors' : html_uencode('\n'.join(authorInfo)),
            }
        else:
            authorInfoSect = ""
        
        if sinceInfo:
            sinceInfoSect = self.sinceInfoTemplate % { \
                'Info' : html_uencode(sinceInfo[0]),
            }
        else:
            sinceInfoSect = ""
        
        if seeList:
            seeSect = self.seeListTemplate % { \
                'Links' : self.__genSeeListSection(seeList, self.seeListEntryTemplate),
            }
        else:
            seeSect = ''
        
        return "%s%s%s%s%s%s%s%s%s%s" % ( \
            deprecatedSect, description, parameterSect, returnSect,
            exceptionSect, signalSect, eventSect, authorInfoSect,
            seeSect, sinceInfoSect
        )
    
    def getQtHelpKeywords(self):
        """
        Public method to retrieve the parts for the QtHelp keywords section.
        
        @return list of tuples containing the name (string) and the ref (string). The ref
            is without the filename part.
        """
        if not self.generated:
            self.genDocument()
        
        return self.keywords
