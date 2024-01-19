# -*- coding: utf-8 -*-

# Copyright (c) 2007 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Package implementing lexers for the various supported programming languages.
"""

from PyQt4.QtCore import QStringList
from PyQt4.QtGui import QApplication
from PyQt4.Qsci import QSCINTILLA_VERSION_STR

from QScintilla.QsciScintillaCompat import QSCINTILLA_VERSION

import Preferences

# The lexer registry
# Dictionary with the language name as key. Each entry is a list with
#       0. display string (QString)
#       1. dummy filename to derive lexer name (string)
#       2. reference to a function instantiating the specific lexer
#          This function must take a reference to the parent as argument.
#       3. list of open file filters (QStringList)
#       4. list of save file filters (QStringList)
#       5. default lexer associations (list of strings of filename wildcard patterns
#          to be associated with the lexer)
LexerRegistry = {}

def registerLexer(name, displayString, filenameSample, getLexerFunc, 
                  openFilters = QStringList(), saveFilters = QStringList(), 
                  defaultAssocs = []):
    """
    Module function to register a custom QScintilla lexer.
    
    @param name lexer language name (string)
    @param displayString display string (QString)
    @param filenameSample dummy filename to derive lexer name (string)
    @param getLexerFunc reference to a function instantiating the specific lexer.
        This function must take a reference to the parent as it's only argument.
    @keyparam openFilters list of open file filters (QStringList)
    @keyparam saveFilters list of save file filters (QStringList)
    @keyparam defaultAssocs default lexer associations (list of strings of filename 
        wildcard patterns to be associated with the lexer)
    @exception KeyError raised when the given name is already in use
    """
    if name in LexerRegistry:
        raise KeyError('Lexer "%s" already registered.' % name)
    else:
        LexerRegistry[name] = [displayString, filenameSample, getLexerFunc, 
                               openFilters, saveFilters, defaultAssocs[:]]

def unregisterLexer(name):
    """
    Module function to unregister a custom QScintilla lexer.
    
    @param name lexer language name (string)
    """
    if name in LexerRegistry:
        del LexerRegistry[name]

def getSupportedLanguages():
    """
    Module function to get a dictionary of supported lexer languages.
    
    @return dictionary of supported lexer languages. The keys are the
        internal language names. The items are lists of two entries.
        The first is the display string for the language, the second
        is a dummy file name, which can be used to derive the lexer.
        (QString, string)
    """
    supportedLanguages = {
        "Bash"       : [QApplication.translate('Lexers', "Bash"),         'dummy.sh'],
        "Batch"      : [QApplication.translate('Lexers', "Batch"),        'dummy.bat'],
        "C++"        : [QApplication.translate('Lexers', "C/C++"),        'dummy.cpp'],
        "C#"         : [QApplication.translate('Lexers', "C#"),           'dummy.cs'],
        "CMake"      : [QApplication.translate('Lexers', "CMake"),        'dummy.cmake'],
        "CSS"        : [QApplication.translate('Lexers', "CSS"),          'dummy.css'],
        "D"          : [QApplication.translate('Lexers', "D"),            'dummy.d'],
        "Diff"       : [QApplication.translate('Lexers', "Diff"),         'dummy.diff'],
        "HTML"       : [QApplication.translate('Lexers', "HTML/PHP/XML"), 'dummy.html'],
        "IDL"        : [QApplication.translate('Lexers', "IDL"),          'dummy.idl'],
        "Java"       : [QApplication.translate('Lexers', "Java"),         'dummy.java'],
        "JavaScript" : [QApplication.translate('Lexers', "JavaScript"),   'dummy.js'],
        "Lua"        : [QApplication.translate('Lexers', "Lua"),          'dummy.lua'],
        "Makefile"   : [QApplication.translate('Lexers', "Makefile"),     'dummy.mak'],
        "Perl"       : [QApplication.translate('Lexers', "Perl"),         'dummy.pl'],
        "Povray"     : [QApplication.translate('Lexers', "Povray"),       'dummy.pov'],
        "Properties" : [QApplication.translate('Lexers', "Properties"),   'dummy.ini'],
        "Python"     : [QApplication.translate('Lexers', "Python"),       'dummy.py'], 
        "Ruby"       : [QApplication.translate('Lexers', "Ruby"),         'dummy.rb'],
        "SQL"        : [QApplication.translate('Lexers', "SQL"),          'dummy.sql'],
        "TeX"        : [QApplication.translate('Lexers', "TeX"),          'dummy.tex'],
        "VHDL"       : [QApplication.translate('Lexers', "VHDL"),         'dummy.vhd'], 
    }
    
    if QSCINTILLA_VERSION() >= 0x020201:
        supportedLanguages["TCL"] = [QApplication.translate('Lexers', "TCL"), 'dummy.tcl']
        supportedLanguages["Fortran"] = \
            [QApplication.translate('Lexers', "Fortran"), 'dummy.f95']
        supportedLanguages["Fortran77"] = \
            [QApplication.translate('Lexers', "Fortran77"), 'dummy.f']
        supportedLanguages["Pascal"] = \
            [QApplication.translate('Lexers', "Pascal"), 'dummy.pas']
        supportedLanguages["PostScript"] = \
            [QApplication.translate('Lexers', "PostScript"), 'dummy.ps']
        supportedLanguages["XML"] = \
            [QApplication.translate('Lexers', "XML"), 'dummy.xml']
        supportedLanguages["YAML"] = \
            [QApplication.translate('Lexers', "YAML"), 'dummy.yml']
    
    for name in LexerRegistry:
        supportedLanguages[name] = LexerRegistry[name][:2]
    
    supportedLanguages["Guessed"] = \
        [QApplication.translate('Lexers', "Pygments"), 'dummy.pygments']
    
    return supportedLanguages

def getLexer(language, parent = None, pyname = ""):
    """
    Module function to instantiate a lexer object for a given language.
    
    @param language language of the lexer (string)
    @param parent reference to the parent object (QObject)
    @keyparam pyname name of the pygments lexer to use (string)
    @return reference to the instanciated lexer object (QsciLexer)
    """
    if not pyname:
        try:
            if language in ["Python", "Python3"]:
                from LexerPython import LexerPython
                return LexerPython(parent)
            elif language == "C++":
                from LexerCPP import LexerCPP
                return LexerCPP(parent, 
                    Preferences.getEditor("CppCaseInsensitiveKeywords"))
            elif language == "C#":
                from LexerCSharp import LexerCSharp
                return LexerCSharp(parent)
            elif language == "IDL":
                from LexerIDL import LexerIDL
                return LexerIDL(parent)
            elif language == "Java":
                from LexerJava import LexerJava
                return LexerJava(parent)
            elif language == "JavaScript":
                from LexerJavaScript import LexerJavaScript
                return LexerJavaScript(parent)
            elif language == "SQL":
                from LexerSQL import LexerSQL
                return LexerSQL(parent)
            elif language == "HTML":
                from LexerHTML import LexerHTML
                return LexerHTML(parent)
            elif language == "Perl":
                from LexerPerl import LexerPerl
                return LexerPerl(parent)
            elif language == "Bash":
                from LexerBash import LexerBash
                return LexerBash(parent)
            elif language == "Ruby":
                from LexerRuby import LexerRuby
                return LexerRuby(parent)
            elif language == "Lua":
                from LexerLua import LexerLua
                return LexerLua(parent)
            elif language == "CSS":
                from LexerCSS import LexerCSS
                return LexerCSS(parent)
            elif language == "TeX":
                from LexerTeX import LexerTeX
                return LexerTeX(parent)
            elif language == "Diff":
                from LexerDiff import LexerDiff
                return LexerDiff(parent)
            elif language == "Makefile":
                from LexerMakefile import LexerMakefile
                return LexerMakefile(parent)
            elif language == "Properties":
                from LexerProperties import LexerProperties
                return LexerProperties(parent)
            elif language == "Batch":
                from LexerBatch import LexerBatch
                return LexerBatch(parent)
            elif language == "D":
                from LexerD import LexerD
                return LexerD(parent)
            elif language == "Povray":
                from LexerPOV import LexerPOV
                return LexerPOV(parent)
            elif language == "CMake":
                from LexerCMake import LexerCMake
                return LexerCMake(parent)
            elif language == "VHDL":
                from LexerVHDL import LexerVHDL
                return LexerVHDL(parent)
            elif language == "TCL":
                from LexerTCL import LexerTCL
                return LexerTCL(parent)
            elif language == "Fortran":
                from LexerFortran import LexerFortran
                return LexerFortran(parent)
            elif language == "Fortran77":
                from LexerFortran77 import LexerFortran77
                return LexerFortran77(parent)
            elif language == "Pascal":
                from LexerPascal import LexerPascal
                return LexerPascal(parent)
            elif language == "PostScript":
                from LexerPostScript import LexerPostScript
                return LexerPostScript(parent)
            elif language == "XML":
                from LexerXML import LexerXML
                return LexerXML(parent)
            elif language == "YAML":
                from LexerYAML import LexerYAML
                return LexerYAML(parent)
            
            elif language in LexerRegistry:
                return LexerRegistry[language][2](parent)
            
            else:
                return __getPygmentsLexer(parent)
        except ImportError:
            return __getPygmentsLexer(parent)
    else:
        return __getPygmentsLexer(parent, name = pyname)

def __getPygmentsLexer(parent, name = ""):
    """
    Private module function to instantiate a pygments lexer.
    
    @param parent reference to the parent widget
    @keyparam name name of the pygments lexer to use (string)
    @return reference to the lexer (LexerPygments) or None
    """
    from LexerPygments import LexerPygments
    lexer = LexerPygments(parent, name = name)
    if lexer.canStyle():
        return lexer
    else:
        return None
    
def getOpenFileFiltersList(includeAll = False, asString = False):
    """
    Module function to get the file filter list for an open file operation.
    
    @param includeAll flag indicating the inclusion of the 
        All Files filter (boolean)
    @param asString flag indicating the list should be returned 
        as a string (boolean)
    @return file filter list (QStringList or QString)
    """
    openFileFiltersList = QStringList() \
        << QApplication.translate('Lexers', 
            'Python Files (*.py *.py3)') \
        << QApplication.translate('Lexers', 
            'Python GUI Files (*.pyw *.pyw3)') \
        << QApplication.translate('Lexers', 
            'Pyrex Files (*.pyx)') \
        << QApplication.translate('Lexers', 
            'Quixote Template Files (*.ptl)') \
        << QApplication.translate('Lexers', 
            'Ruby Files (*.rb)') \
        << QApplication.translate('Lexers', 
            'IDL Files (*.idl)') \
        << QApplication.translate('Lexers', 
            'C Files (*.h *.c)') \
        << QApplication.translate('Lexers', 
            'C++ Files (*.h *.hpp *.hh *.cxx *.cpp *.cc)') \
        << QApplication.translate('Lexers', 
            'C# Files (*.cs)') \
        << QApplication.translate('Lexers', 
            'HTML Files (*.html *.htm *.asp *.shtml)') \
        << QApplication.translate('Lexers', 
            'CSS Files (*.css)') \
        << QApplication.translate('Lexers', 
            'QSS Files (*.qss)') \
        << QApplication.translate('Lexers', 
            'PHP Files (*.php *.php3 *.php4 *.php5 *.phtml)') \
        << QApplication.translate('Lexers', 
            'XML Files (*.xml *.xsl *.xslt *.dtd *.svg *.xul *.xsd)') \
        << QApplication.translate('Lexers', 
            'Qt Resource Files (*.qrc)') \
        << QApplication.translate('Lexers', 
            'D Files (*.d *.di)') \
        << QApplication.translate('Lexers', 
            'Java Files (*.java)') \
        << QApplication.translate('Lexers', 
            'JavaScript Files (*.js)') \
        << QApplication.translate('Lexers', 
            'SQL Files (*.sql)') \
        << QApplication.translate('Lexers', 
            'Docbook Files (*.docbook)') \
        << QApplication.translate('Lexers', 
            'Perl Files (*.pl *.pm *.ph)') \
        << QApplication.translate('Lexers', 
            'Lua Files (*.lua)') \
        << QApplication.translate('Lexers', 
            'Tex Files (*.tex *.sty *.aux *.toc *.idx)') \
        << QApplication.translate('Lexers', 
            'Shell Files (*.sh)') \
        << QApplication.translate('Lexers', 
            'Batch Files (*.bat *.cmd)') \
        << QApplication.translate('Lexers', 
            'Diff Files (*.diff *.patch)') \
        << QApplication.translate('Lexers', 
            'Makefiles (*.mak)') \
        << QApplication.translate('Lexers', 
            'Properties Files (*.properties *.ini *.inf *.reg *.cfg *.cnf *.rc)') \
        << QApplication.translate('Lexers', 
            'Povray Files (*.pov)') \
        << QApplication.translate('Lexers', 
            'CMake Files (CMakeLists.txt *.cmake *.ctest)') \
        << QApplication.translate('Lexers', 
            'VHDL Files (*.vhd *.vhdl)')
    
    if QSCINTILLA_VERSION() >= 0x020201:
        openFileFiltersList \
            << QApplication.translate('Lexers', 
                'TCL/Tk Files (*.tcl *.tk)') \
            << QApplication.translate('Lexers', 
                'Fortran Files (*.f90 *.f95 *.f2k)') \
            << QApplication.translate('Lexers', 
                'Fortran77 Files (*.f *.for)') \
            << QApplication.translate('Lexers', 
                'Pascal Files (*.dpr *.dpk *.pas *.dfm *.inc *.pp)') \
            << QApplication.translate('Lexers', 
                'PostScript Files (*.ps)') \
            << QApplication.translate('Lexers', 
                'YAML Files (*.yaml *.yml)')
    
    for name in LexerRegistry:
        openFileFiltersList << LexerRegistry[name][3]
    
    openFileFiltersList.sort()
    if includeAll:
        openFileFiltersList.append(QApplication.translate('Lexers', 'All Files (*)'))
    
    if asString:
        return openFileFiltersList.join(';;')
    else:
        return openFileFiltersList

def getSaveFileFiltersList(includeAll = False, asString = False):
    """
    Module function to get the file filter list for a save file operation.
    
    @param includeAll flag indicating the inclusion of the 
        All Files filter (boolean)
    @param asString flag indicating the list should be returned 
        as a string (boolean)
    @return file filter list (QStringList or QString)
    """
    saveFileFiltersList = QStringList() \
        << QApplication.translate('Lexers', 
            "Python Files (*.py)") \
        << QApplication.translate('Lexers', 
            "Python3 Files (*.py3)") \
        << QApplication.translate('Lexers', 
            "Python GUI Files (*.pyw)") \
        << QApplication.translate('Lexers', 
            "Python3 GUI Files (*.pyw3)") \
        << QApplication.translate('Lexers', 
            "Pyrex Files (*.pyx)") \
        << QApplication.translate('Lexers', 
            "Quixote Template Files (*.ptl)") \
        << QApplication.translate('Lexers', 
            "Ruby Files (*.rb)") \
        << QApplication.translate('Lexers', 
            "IDL Files (*.idl)") \
        << QApplication.translate('Lexers', 
            "C Files (*.c)") \
        << QApplication.translate('Lexers', 
            "C++ Files (*.cpp)") \
        << QApplication.translate('Lexers', 
            "C++/C Header Files (*.h)") \
        << QApplication.translate('Lexers', 
            "C# Files (*.cs)") \
        << QApplication.translate('Lexers', 
            "HTML Files (*.html)") \
        << QApplication.translate('Lexers', 
            "PHP Files (*.php)") \
        << QApplication.translate('Lexers', 
            "ASP Files (*.asp)") \
        << QApplication.translate('Lexers', 
            "CSS Files (*.css)") \
        << QApplication.translate('Lexers', 
            "QSS Files (*.qss)") \
        << QApplication.translate('Lexers', 
            "XML Files (*.xml)") \
        << QApplication.translate('Lexers', 
            "XSL Files (*.xsl)") \
        << QApplication.translate('Lexers', 
            "DTD Files (*.dtd)") \
        << QApplication.translate('Lexers', 
            "Qt Resource Files (*.qrc)") \
        << QApplication.translate('Lexers', 
            "D Files (*.d)") \
        << QApplication.translate('Lexers', 
            "D Interface Files (*.di)") \
        << QApplication.translate('Lexers', 
            "Java Files (*.java)") \
        << QApplication.translate('Lexers', 
            "JavaScript Files (*.js)") \
        << QApplication.translate('Lexers', 
            "SQL Files (*.sql)") \
        << QApplication.translate('Lexers', 
            "Docbook Files (*.docbook)") \
        << QApplication.translate('Lexers', 
            "Perl Files (*.pl)") \
        << QApplication.translate('Lexers', 
            "Perl Module Files (*.pm)") \
        << QApplication.translate('Lexers', 
            "Lua Files (*.lua)") \
        << QApplication.translate('Lexers', 
            "Shell Files (*.sh)") \
        << QApplication.translate('Lexers', 
            "Batch Files (*.bat)") \
        << QApplication.translate('Lexers', 
            "TeX Files (*.tex)") \
        << QApplication.translate('Lexers', 
            "TeX Template Files (*.sty)") \
        << QApplication.translate('Lexers', 
            "Diff Files (*.diff)") \
        << QApplication.translate('Lexers', 
            "Make Files (*.mak)") \
        << QApplication.translate('Lexers', 
            "Properties Files (*.ini)") \
        << QApplication.translate('Lexers', 
            "Configuration Files (*.cfg)") \
        << QApplication.translate('Lexers', 
            'Povray Files (*.pov)') \
        << QApplication.translate('Lexers', 
            'CMake Files (CMakeLists.txt)') \
        << QApplication.translate('Lexers', 
            'CMake Macro Files (*.cmake)') \
        << QApplication.translate('Lexers', 
            'VHDL Files (*.vhd)')
    
    if QSCINTILLA_VERSION() >= 0x020201:
        saveFileFiltersList \
            << QApplication.translate('Lexers', 
                'TCL Files (*.tcl)') \
            << QApplication.translate('Lexers', 
                'Tk Files (*.tk)') \
            << QApplication.translate('Lexers', 
                'Fortran Files (*.f95)') \
            << QApplication.translate('Lexers', 
                'Fortran77 Files (*.f)') \
            << QApplication.translate('Lexers', 
                'Pascal Files (*.pas)') \
            << QApplication.translate('Lexers', 
                'PostScript Files (*.ps)') \
            << QApplication.translate('Lexers', 
                'YAML Files (*.yml)')
    
    for name in LexerRegistry:
        saveFileFiltersList << LexerRegistry[name][4]
    
    saveFileFiltersList.sort()
    
    if includeAll:
        saveFileFiltersList.append(QApplication.translate('Lexers', 'All Files (*)'))
    
    if asString:
        return saveFileFiltersList.join(';;')
    else:
        return saveFileFiltersList

def getDefaultLexerAssociations():
    assocs = {
        '*.sh'              : "Bash",
        '*.bash'            : "Bash",
        "*.bat"             : "Batch",
        "*.cmd"             : "Batch",
        '*.cpp'             : "C++",
        '*.cxx'             : "C++",
        '*.cc'              : "C++",
        '*.c'               : "C++",
        '*.hpp'             : "C++",
        '*.hh'              : "C++",
        '*.h'               : "C++",
        '*.cs'              : "C#",
        'CMakeLists.txt'    : "CMake", 
        '*.cmake'           : "CMake",
        '*.cmake.in'        : "CMake",
        '*.ctest'           : "CMake",
        '*.ctest.in'        : "CMake",
        '*.css'             : "CSS",
        '*.qss'             : "CSS",
        "*.d"               : "D",
        "*.di"              : "D",
        "*.diff"            : "Diff",
        "*.patch"           : "Diff",
        '*.html'            : "HTML",
        '*.htm'             : "HTML",
        '*.asp'             : "HTML",
        '*.shtml'           : "HTML",
        '*.php'             : "HTML",
        '*.php3'            : "HTML",
        '*.php4'            : "HTML",
        '*.php5'            : "HTML",
        '*.phtml'           : "HTML",
        '*.xml'             : "HTML",
        '*.xsl'             : "HTML",
        '*.svg'             : "HTML",
        '*.xsd'             : "HTML",
        '*.xslt'            : "HTML",
        '*.dtd'             : "HTML",
        '*.rdf'             : "HTML",
        '*.xul'             : "HTML", 
        '*.docbook'         : "HTML",
        '*.ui'              : "HTML",
        '*.ts'              : "HTML",
        '*.qrc'             : "HTML",
        '*.e3d'             : "HTML",
        '*.e3k'             : "HTML",
        '*.e3p'             : "HTML",
        '*.e3s'             : "HTML",
        '*.e3t'             : "HTML",
        '*.e4d'             : "HTML",
        '*.e4k'             : "HTML",
        '*.e4m'             : "HTML", 
        '*.e4p'             : "HTML",
        '*.e4q'             : "HTML",
        '*.e4s'             : "HTML",
        '*.e4t'             : "HTML",
        '*.kid'             : "HTML",
        '*.idl'             : "IDL",
        '*.java'            : "Java",
        '*.js'              : "JavaScript",
        '*.lua'             : "Lua",
        "*makefile"         : "Makefile",
        "Makefile*"         : "Makefile",
        "*.mak"             : "Makefile",
        '*.pl'              : "Perl",
        '*.pm'              : "Perl",
        '*.ph'              : "Perl",
        '*.pov'             : "Povray",
        "*.properties"      : "Properties",
        "*.ini"             : "Properties",
        "*.inf"             : "Properties",
        "*.reg"             : "Properties",
        "*.cfg"             : "Properties",
        "*.cnf"             : "Properties",
        "*.rc"              : "Properties",
        '*.py'              : "Python",
        '*.pyw'             : "Python",
        '*.pyx'             : "Python",
        '*.ptl'             : "Python",
        '*.rb'              : "Ruby",
        '*.rbw'             : "Ruby",
        '*.sql'             : "SQL",
        "*.tex"             : "TeX",
        "*.sty"             : "TeX",
        "*.aux"             : "TeX",
        "*.toc"             : "TeX",
        "*.idx"             : "TeX",
        '*.vhd'             : "VHDL", 
        '*.vhdl'            : "VHDL", 
    }
    
    if QSCINTILLA_VERSION() >= 0x020201:
        assocs["*.tcl"]  = "TCL"
        assocs["*.tk"]   = "TCL"
        assocs["*.f"]    = "Fortran77"
        assocs["*.for"]  = "Fortran77"
        assocs["*.f90"]  = "Fortran"
        assocs["*.f95"]  = "Fortran"
        assocs["*.f2k"]  = "Fortran"
        assocs["*.dpr"]  = "Pascal"
        assocs["*.dpk"]  = "Pascal"
        assocs["*.pas"]  = "Pascal"
        assocs["*.dfm"]  = "Pascal"
        assocs["*.inc"]  = "Pascal"
        assocs["*.pp"]   = "Pascal"
        assocs["*.ps"]   = "PostScript"
        assocs["*.xml"]  = "XML"
        assocs["*.xsl"]  = "XML"
        assocs["*.svg"]  = "XML"
        assocs["*.xsd"]  = "XML"
        assocs["*.xslt"] = "XML"
        assocs["*.dtd"]  = "XML"
        assocs["*.rdf"]  = "XML"
        assocs["*.xul"]  = "XML"
        assocs["*.yaml"] = "YAML"
        assocs["*.yml"]  = "YAML"
    
    for name in LexerRegistry:
        for pattern in LexerRegistry[name][5]:
            assocs[pattern] = name
    
    return assocs
