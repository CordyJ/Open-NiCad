# -*- coding: utf-8 -*-

# Copyright (c) 2004 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the builtin API generator.

"""

import sys

from QScintilla.Editor import Editor

class APIGenerator(object):
    """
    Class implementing the builtin documentation generator.
    """
    def __init__(self, module):
        """
        Constructor
        
        @param module The information of the parsed Python file.
        """
        self.module = module
        
    def genAPI(self, newStyle, basePackage, includePrivate):
        """
        Method to generate the source code documentation.
        
        @param newStyle flag indicating the api generation for QScintilla 1.7 and 
            newer (boolean)
        @param basePackage name of the base package (string)
        @param includePrivate flag indicating to include 
            private methods/functions (boolean)
        @return The API information. (string)
        """
        self.includePrivate = includePrivate
        self.newStyle = newStyle
        if self.newStyle:
            modulePath = self.module.name.split('.')
            if modulePath[-1] == '__init__':
                del modulePath[-1]
            if basePackage:
                modulePath[0] = basePackage
            self.moduleName = "%s." % '.'.join(modulePath)
        else:
            self.moduleName = ""
        self.api = []
        self.__addGlobalsAPI()
        self.__addClassesAPI()
        self.__addFunctionsAPI()
        return self.api
        
    def __isPrivate(self, obj):
        """
        Private method to check, if an object is considered private.
        
        @param obj reference to the object to be checked
        @return flag indicating, that object is considered private (boolean)
        """
        private = obj.isPrivate() and not self.includePrivate
        return private
        
    def __addGlobalsAPI(self):
        """
        Private method to generate the api section for global variables. 
        """
        if self.newStyle:
            moduleNameStr = "%s" % self.moduleName
        else:
            moduleNameStr = ""
        
        for globalName in sorted(self.module.globals.keys()):
            if not self.__isPrivate(self.module.globals[globalName]):
                if self.module.globals[globalName].isPublic():
                    id = Editor.AttributeID
                elif self.module.globals[globalName].isProtected():
                    id = Editor.AttributeProtectedID
                else:
                    id = Editor.AttributePrivateID
                self.api.append("%s%s?%d" % (moduleNameStr, globalName, id))
        
    def __addClassesAPI(self):
        """
        Private method to generate the api section for classes.
        """
        classNames = self.module.classes.keys()
        classNames.sort()
        for className in classNames:
            if not self.__isPrivate(self.module.classes[className]):
                self.__addClassVariablesAPI(className)
                self.__addMethodsAPI(className)
        
    def __addMethodsAPI(self, className):
        """
        Private method to generate the api section for class methods.
        
        @param classname Name of the class containing the method. (string)
        """
        _class = self.module.classes[className]
        methods = _class.methods.keys()
        methods.sort()
        
        # first do the constructor
        if '__init__' in methods:
            methods.remove('__init__')
            if _class.isPublic():
                id = Editor.ClassID
            elif _class.isProtected():
                id = Editor.ClassProtectedID
            else:
                id = Editor.ClassPrivateID
            self.api.append('%s%s?%d(%s)' % \
                (self.moduleName, _class.name, id, 
                 ', '.join(_class.methods['__init__'].parameters[1:])))
            
        if self.newStyle:
            classNameStr = "%s%s." % (self.moduleName, className)
        else:
            classNameStr = ""
        for method in methods:
            if not self.__isPrivate(_class.methods[method]): 
                if _class.methods[method].isPublic():
                    id = Editor.MethodID
                elif _class.methods[method].isProtected():
                    id = Editor.MethodProtectedID
                else:
                    id = Editor.MethodPrivateID
                self.api.append('%s%s?%d(%s)' % \
                    (classNameStr, method, id, 
                     ', '.join(_class.methods[method].parameters[1:])))
        
    def __addClassVariablesAPI(self, className):
        """
        Private method to generate class api section for class variables.
        
        @param classname Name of the class containing the class variables. (string)
        """
        _class = self.module.classes[className]
        if self.newStyle:
            classNameStr = "%s%s." % (self.moduleName, className)
        else:
            classNameStr = ""
        for variable in sorted(_class.globals.keys()):
            if not self.__isPrivate(_class.globals[variable]): 
                if _class.globals[variable].isPublic():
                    id = Editor.AttributeID
                elif _class.globals[variable].isProtected():
                    id = Editor.AttributeProtectedID
                else:
                    id = Editor.AttributePrivateID
                self.api.append('%s%s?%d' % (classNameStr, variable, id))
        
    def __addFunctionsAPI(self):
        """
        Private method to generate the api section for functions.
        """
        funcNames = self.module.functions.keys()
        funcNames.sort()
        for funcName in funcNames:
            if not self.__isPrivate(self.module.functions[funcName]): 
                if self.module.functions[funcName].isPublic():
                    id = Editor.MethodID
                elif self.module.functions[funcName].isProtected():
                    id = Editor.MethodProtectedID
                else:
                    id = Editor.MethodPrivateID
                self.api.append('%s%s?%d(%s)' % \
                    (self.moduleName, self.module.functions[funcName].name, id, 
                     ', '.join(self.module.functions[funcName].parameters)))
