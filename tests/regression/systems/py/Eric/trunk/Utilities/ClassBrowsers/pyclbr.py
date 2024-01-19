# -*- coding: utf-8 -*-

# Copyright (c) 2005 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Parse a Python file and retrieve classes, functions/methods and attributes.

Parse enough of a Python file to recognize class and method definitions and
to find out the superclasses of a class as well as its attributes.

This is module is based on pyclbr found in the Python 2.2.2 distribution.
"""


import sys
import os
import imp
import re

import Utilities
import Utilities.ClassBrowsers as ClassBrowsers
import ClbrBaseClasses

TABWIDTH = 4

SUPPORTED_TYPES = [ClassBrowsers.PY_SOURCE, ClassBrowsers.PTL_SOURCE]
    
_getnext = re.compile(r"""
    (?P<String>
       ''' [^"\\]* (?:
                        (?: \\. | "(?!"") )
                        [^"\\]*
                    )*
       '''

    |   ''' [^'\\]* (?:
                        (?: \\. | '(?!'') )
                        [^'\\]*
                    )*
        '''

    |   " [^"\\\n]* (?: \\. [^"\\\n]*)* "

    |   ' [^'\\\n]* (?: \\. [^'\\\n]*)* '
    )

|   (?P<Publics>
        ^
        [ \t]* __all__ [ \t]* = [ \t]* \[
        (?P<Identifiers> [^\]]*? )
        \]
    )

|   (?P<Method>
        ^
        (?P<MethodIndent> [ \t]* )
        def [ \t]+
        (?P<MethodName> [a-zA-Z_] \w* )
        (?: [ \t]* \[ (?: plain | html ) \] )?
        [ \t]* \(
        (?P<MethodSignature> (?: [^)] | \)[ \t]*,? )*? )
        \) [ \t]* :
    )

|   (?P<Class>
        ^
        (?P<ClassIndent> [ \t]* )
        class [ \t]+
        (?P<ClassName> [a-zA-Z_] \w* )
        [ \t]*
        (?P<ClassSupers> \( [^)]* \) )?
        [ \t]* :
    )

|   (?P<Attribute>
        ^
        (?P<AttributeIndent> [ \t]* )
        self [ \t]* \. [ \t]*
        (?P<AttributeName> [a-zA-Z_] \w* )
        [ \t]* =
    )

|   (?P<Variable>
        ^
        (?P<VariableIndent> [ \t]* )
        (?P<VariableName> [a-zA-Z_] \w* )
        [ \t]* =
    )

|   (?P<ConditionalDefine>
        ^
        (?P<ConditionalDefineIndent> [ \t]* )
        (?: (?: if | elif ) [ \t]+ [^:]* | else [ \t]* ) : (?= \s* def)
    )

|   (?P<CodingLine>
        ^ \# \s* [*_-]* \s* coding[:=] \s* (?P<Coding> [-\w_.]+ ) \s* [*_-]* $
    )
""", re.VERBOSE | re.DOTALL | re.MULTILINE).search

_commentsub = re.compile(r"""#[^\n]*\n|#[^\n]*$""").sub

_modules = {}                           # cache of modules we've seen

class VisibilityMixin(ClbrBaseClasses.ClbrVisibilityMixinBase):
    """
    Mixin class implementing the notion of visibility.
    """
    def __init__(self):
        """
        Method to initialize the visibility.
        """
        if self.name.startswith('__'):
            self.setPrivate()
        elif self.name.startswith('_'):
            self.setProtected()
        else:
            self.setPublic()

class Class(ClbrBaseClasses.Class, VisibilityMixin):
    """
    Class to represent a Python class.
    """
    def __init__(self, module, name, super, file, lineno):
        """
        Constructor
        
        @param module name of the module containing this class
        @param name name of this class
        @param super list of class names this class is inherited from
        @param file filename containing this class
        @param lineno linenumber of the class definition
        """
        ClbrBaseClasses.Class.__init__(self, module, name, super, file, lineno)
        VisibilityMixin.__init__(self)

class Function(ClbrBaseClasses.Function, VisibilityMixin):
    """
    Class to represent a Python function.
    """
    def __init__(self, module, name, file, lineno, signature = '', separator = ','):
        """
        Constructor
        
        @param module name of the module containing this function
        @param name name of this function
        @param file filename containing this class
        @param lineno linenumber of the class definition
        @param signature parameterlist of the method
        @param separator string separating the parameters
        """
        ClbrBaseClasses.Function.__init__(self, module, name, file, lineno, 
                                          signature, separator)
        VisibilityMixin.__init__(self)

class Attribute(ClbrBaseClasses.Attribute, VisibilityMixin):
    """
    Class to represent a class attribute.
    """
    def __init__(self, module, name, file, lineno):
        """
        Constructor
        
        @param module name of the module containing this class
        @param name name of this class
        @param file filename containing this attribute
        @param lineno linenumber of the class definition
        """
        ClbrBaseClasses.Attribute.__init__(self, module, name, file, lineno)
        VisibilityMixin.__init__(self)

class Publics(object):
    """
    Class to represent the list of public identifiers.
    """
    def __init__(self, module, file, lineno, idents):
        """
        Constructor
        
        @param module name of the module containing this function
        @param file filename containing this class
        @param lineno linenumber of the class definition
        @param idents list of public identifiers
        """
        self.module = module
        self.name = '__all__'
        self.file = file
        self.lineno = lineno
        self.identifiers = [e.replace('"','').replace("'","").strip() \
                            for e in idents.split(',')]
    
def readmodule_ex(module, path=[], inpackage = False, isPyFile = False):
    '''
    Read a module file and return a dictionary of classes.

    Search for MODULE in PATH and sys.path, read and parse the
    module and return a dictionary with one entry for each class
    found in the module.
    
    @param module name of the module file (string)
    @param path path the module should be searched in (list of strings)
    @param inpackage flag indicating a module inside a package is scanned
    @return the resulting dictionary
    '''

    dict = {}
    dict_counts = {}

    if _modules.has_key(module):
        # we've seen this module before...
        return _modules[module]
    if module in sys.builtin_module_names:
        # this is a built-in module
        _modules[module] = dict
        return dict

    # search the path for the module
    f = None
    if inpackage:
        try:
            f, file, (suff, mode, type) = \
                    ClassBrowsers.find_module(module, path)
        except ImportError:
            f = None
    if f is None:
        fullpath = list(path) + sys.path
        f, file, (suff, mode, type) = \
            ClassBrowsers.find_module(module, fullpath, isPyFile)
    if module.endswith(".py") and type == imp.PKG_DIRECTORY:
        return dict
    if type == imp.PKG_DIRECTORY:
        dict['__path__'] = [file]
        _modules[module] = dict
        path = [file] + path
        f, file, (suff, mode, type) = \
                        ClassBrowsers.find_module('__init__', [file])
    if type not in SUPPORTED_TYPES:
        # not Python source, can't do anything with this module
        f.close()
        _modules[module] = dict
        return dict

    _modules[module] = dict
    classstack = [] # stack of (class, indent) pairs
    conditionalsstack = [] # stack of indents of conditional defines
    deltastack = []
    deltaindent = 0
    deltaindentcalculated = 0
    src = Utilities.decode(f.read())[0]
    f.close()

    lineno, last_lineno_pos = 1, 0
    i = 0
    while 1:
        m = _getnext(src, i)
        if not m:
            break
        start, i = m.span()

        if m.start("Method") >= 0:
            # found a method definition or function
            thisindent = _indent(m.group("MethodIndent"))
            meth_name = m.group("MethodName")
            meth_sig = m.group("MethodSignature")
            meth_sig = meth_sig.replace('\\\n', '')
            meth_sig = _commentsub('', meth_sig)
            lineno = lineno + src.count('\n', last_lineno_pos, start)
            last_lineno_pos = start
            # modify indentation level for conditional defines
            if conditionalsstack:
                if thisindent > conditionalsstack[-1]:
                    if not deltaindentcalculated:
                        deltastack.append(thisindent - conditionalsstack[-1])
                        deltaindent = reduce(lambda x,y: x+y, deltastack)
                        deltaindentcalculated = 1
                    thisindent -= deltaindent
                else:
                    while conditionalsstack and \
                          conditionalsstack[-1] >= thisindent:
                        del conditionalsstack[-1]
                        if deltastack:
                            del deltastack[-1]
                    deltaindentcalculated = 0
            # close all classes indented at least as much
            while classstack and \
                  classstack[-1][1] >= thisindent:
                del classstack[-1]
            if classstack:
                # it's a class method
                cur_class = classstack[-1][0]
                if cur_class:
                    # it's a method/nested def
                    f = Function(None, meth_name,
                                 file, lineno, meth_sig)
                    cur_class._addmethod(meth_name, f)
            else:
                # it's a function
                f = Function(module, meth_name,
                             file, lineno, meth_sig)
                if dict_counts.has_key(meth_name):
                    dict_counts[meth_name] += 1
                    meth_name = "%s_%d" % (meth_name, dict_counts[meth_name])
                else:
                    dict_counts[meth_name] = 0
                dict[meth_name] = f
            classstack.append((f, thisindent)) # Marker for nested fns

        elif m.start("String") >= 0:
            pass

        elif m.start("Class") >= 0:
            # we found a class definition
            thisindent = _indent(m.group("ClassIndent"))
            # close all classes indented at least as much
            while classstack and \
                  classstack[-1][1] >= thisindent:
                del classstack[-1]
            lineno = lineno + src.count('\n', last_lineno_pos, start)
            last_lineno_pos = start
            class_name = m.group("ClassName")
            inherit = m.group("ClassSupers")
            if inherit:
                # the class inherits from other classes
                inherit = inherit[1:-1].strip()
                inherit = _commentsub('', inherit)
                names = []
                for n in inherit.split(','):
                    n = n.strip()
                    if dict.has_key(n):
                        # we know this super class
                        n = dict[n]
                    else:
                        c = n.split('.')
                        if len(c) > 1:
                            # super class
                            # is of the
                            # form module.class:
                            # look in
                            # module for class
                            m = c[-2]
                            c = c[-1]
                            if _modules.has_key(m):
                                d = _modules[m]
                                if d.has_key(c):
                                    n = d[c]
                    names.append(n)
                inherit = names
            # remember this class
            cur_class = Class(module, class_name, inherit,
                              file, lineno)
            if not classstack:
                if dict_counts.has_key(class_name):
                    dict_counts[class_name] += 1
                    class_name = "%s_%d" % (class_name, dict_counts[class_name])
                else:
                    dict_counts[class_name] = 0
                dict[class_name] = cur_class
            else:
                classstack[-1][0]._addclass(class_name, cur_class)
            classstack.append((cur_class, thisindent))

        elif m.start("Attribute") >= 0:
            lineno = lineno + src.count('\n', last_lineno_pos, start)
            last_lineno_pos = start
            index = -1
            while index >= -len(classstack):
                if classstack[index][0] is not None and \
                   not isinstance(classstack[index][0], Function):
                    attr = Attribute(module, m.group("AttributeName"), file, lineno)
                    classstack[index][0]._addattribute(attr)
                    break
                else:
                    index -= 1

        elif m.start("Variable") >= 0:
            thisindent = _indent(m.group("VariableIndent"))
            variable_name = m.group("VariableName")
            lineno = lineno + src.count('\n', last_lineno_pos, start)
            last_lineno_pos = start
            if thisindent == 0:
                # global variable
                if not dict.has_key("@@Globals@@"):
                    dict["@@Globals@@"] = \
                        ClbrBaseClasses.ClbrBase(module, "Globals", file, lineno)
                dict["@@Globals@@"]._addglobal(
                    Attribute(module, variable_name, file, lineno))
            else:
                index = -1
                while index >= -len(classstack):
                    if classstack[index][1] >= thisindent:
                        index -= 1
                    else:
                        if isinstance(classstack[index][0], Class):
                            classstack[index][0]._addglobal(
                                Attribute(module, variable_name, file, lineno))
                        break

        elif m.start("Publics") >= 0:
            idents = m.group("Identifiers")
            lineno = lineno + src.count('\n', last_lineno_pos, start)
            last_lineno_pos = start
            pubs = Publics(module, file, lineno, idents)
            dict['__all__'] = pubs
        
        elif m.start("ConditionalDefine") >= 0:
            # a conditional function/method definition
            thisindent = _indent(m.group("ConditionalDefineIndent"))
            while conditionalsstack and \
                  conditionalsstack[-1] >= thisindent:
                del conditionalsstack[-1]
                if deltastack:
                    del deltastack[-1]
            conditionalsstack.append(thisindent)
            deltaindentcalculated = 0
        
        elif m.start("CodingLine") >= 0:
            # a coding statement
            coding = m.group("Coding")
            lineno = lineno + src.count('\n', last_lineno_pos, start)
            last_lineno_pos = start
            if not dict.has_key("@@Coding@@"):
                dict["@@Coding@@"] = ClbrBaseClasses.Coding(module, file, lineno, coding)
        
        else:
            assert 0, "regexp _getnext found something unexpected"

    if dict.has_key('__all__'):
        # set visibility of all top level elements
        pubs = dict['__all__']
        for key in dict.keys():
            if key == '__all__' or key.startswith("@@"):
                continue
            if key in pubs.identifiers:
                dict[key].setPublic()
            else:
                dict[key].setPrivate()
        del dict['__all__']
    
    return dict

def _indent(ws):
    """
    Module function to return the indentation depth.
    
    @param ws the whitespace to be checked (string)
    @return length of the whitespace string (integer)
    """
    return len(ws.expandtabs(TABWIDTH))
