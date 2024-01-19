# -*- coding: utf-8 -*-

# Copyright (c) 2002 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Package implementing the preferences interface.

The preferences interface consists of a class, which defines the default
values for all configuration items and stores the actual values. These
values are read and written to the eric4 preferences file by module
functions. The data is stored in a file in a subdirectory of the users home 
directory. The individual configuration data is accessed by accessor functions 
defined on the module level. The module is simply imported wherever it is needed
with the statement 'import Preferences'. Do not use 'from Preferences import *'
to import it.
"""

import sys
import os
import fnmatch
import shutil

from PyQt4 import QtCore, QtGui
from PyQt4 import Qsci
from PyQt4.QtWebKit import QWebSettings

import QScintilla.Lexers

from Globals import settingsNameOrganization, settingsNameGlobal, settingsNameRecent, \
    isWindowsPlatform

from Project.ProjectBrowserFlags import SourcesBrowserFlag, FormsBrowserFlag, \
    ResourcesBrowserFlag, TranslationsBrowserFlag, InterfacesBrowserFlag, \
    OthersBrowserFlag, AllBrowsersFlag

class Prefs(object):
    """
    A class to hold all configuration items for the application.
    """
    # defaults for the variables window
    varDefaults = {
        "LocalsFilter" : [],
        "GlobalsFilter" : []
    }
    
    # defaults for the debugger
    debuggerDefaults = {
        "RemoteDbgEnabled" : 0,
        "RemoteHost" : "",
        "RemoteExecution" : "",
        "PassiveDbgEnabled" : 0,
        "PassiveDbgPort" : 42424,
        "PassiveDbgType" : "Python", 
        "AutomaticReset" : 0,
        "Autosave" : 0,
        "ThreeStateBreakPoints": 0,
        "SuppressClientExit" : 0, 
        "BreakAlways" : 0, 
        "CustomPythonInterpreter" : 0,
        "PythonInterpreter" : "",
        "Python3Interpreter" : "",
        "RubyInterpreter" : "/usr/bin/ruby",
        "DebugClientType" : "standard",     # supported "standard", "threaded", "custom"
        "DebugClient" : "",
        "DebugClientType3" : "standard",    # supported "standard", "threaded", "custom"
        "DebugClient3" : "",
        "PythonExtensions" : ".py .pyw .ptl", # space separated list of Python extensions
        "Python3Extensions" : ".py3 .pyw3",   # space separated list of Python3 extensions
        "DebugEnvironmentReplace" : 0,
        "DebugEnvironment" : "",
        "PythonRedirect" : 1,
        "PythonNoEncoding" : 0,
        "Python3Redirect" : 1,
        "Python3NoEncoding" : 0,
        "RubyRedirect" : 1,
        "ConsoleDbgEnabled" : 0,
        "ConsoleDbgCommand" : "",
        "PathTranslation" : 0,
        "PathTranslationRemote" : "",
        "PathTranslationLocal" : "",
        "NetworkInterface" : "127.0.0.1",
    }
    debuggerDefaults["AllowedHosts"] = \
        QtCore.QStringList("127.0.0.1") << QtCore.QString("0:0:0:0:0:0:0:1%0")
    
    uiDefaults = {
        "Language" : "System",
        "Style" : "System",
        "StyleSheet" : "",
        "ViewManager" : "tabview",
        "LayoutType" : "Toolboxes",
        # allowed values are "DockWindows", "FloatingWindows", "Toolboxes" and "Sidebars"
        "LayoutShellEmbedded" : 0,          # 0 = separate
                                            # 1 = embedded in debug browser
        "LayoutFileBrowserEmbedded" : 1,    # 0 = separate
                                            # 1 = embedded in debug browser
                                            # 2 = embedded in project browser
        "BrowsersListFoldersFirst" : 1,
        "BrowsersHideNonPublic" : 0,
        "BrowsersListContentsByOccurrence" : 0, 
        "LogViewerAutoRaise" : 1, 
        "SingleApplicationMode" : 0,
        "CaptionShowsFilename" : 1,
        "CaptionFilenameLength" : 100,
        "RecentNumber" : 9, 
        "TopLeftByLeft" : 1, 
        "BottomLeftByLeft" : 0, 
        "TopRightByRight" : 1, 
        "BottomRightByRight" : 0, 
        "TabViewManagerFilenameLength" : 40,
        "TabViewManagerFilenameOnly" : 1, 
        # the order in ViewProfiles is Project-Viewer, File-Browser,
        # Debug-Viewer, Python-Shell, Log-Viewer, Task-Viewer,
        # Templates-Viewer, Multiproject-Viewer, Terminal
        "ViewProfiles" : {
            "edit"  : [
                        # visibility (0)
                        [ 1,  0,  0,  1,  1,  1,  1,  1, 1],
                        # saved state main window with dock windows (1)
                        "",
                        # saved states floating windows (2)
                        ["", "", "", "", "", "", "", "", ""],
                        # saved state main window with floating windows (3)
                        "", 
                        # saved state main window with toolbox windows (4)
                        "", 
                        # visibility of the toolboxes (5)
                        [ 1,  1], 
                        # saved states of the splitters and sidebars of the 
                        # sidebars layout (6)
                        ["", "", "", ""], 
                      ],
            "debug" : [
                        # visibility (0)
                        [ 0,  0,  1,  1,  1,  1,  0,  0, 1], 
                        # saved state main window with dock windows (1)
                        "",
                        # saved states floating windows (2)
                        ["", "", "", "", "", "", "", "", ""],
                        # saved state main window with floating windows (3)
                        "", 
                        # saved state main window with toolbox windows (4)
                        "", 
                        # visibility of the toolboxes (5)
                        [ 0,  1], 
                        # saved states of the splitters and sidebars of the 
                        # sidebars layout (6)
                        ["", "", "", ""], 
                      ],
        },
        "ToolbarManagerState" : QtCore.QByteArray(), 
        "ShowSplash" : 1,
        "UseKDEDialogs" : 0, 
        "SingleCloseButton" : 1, 
        
        "PerformVersionCheck" : 4,      # 0 = off
                                        # 1 = at startup
                                        # 2 = daily
                                        # 3 = weekly
                                        # 4 = monthly
        "UseProxy" : 0,
        "ProxyHost" : "",
        "ProxyPort" : 80,
        "ProxyUser" : "",
        "ProxyPassword" : "",
        "ProxyType" : 0,            # 0 = transparent HTTP proxy
                                    # 1 = caching HTTP proxy
                                    # 2 = SOCKS5 proxy
        
        "PluginRepositoryUrl" : \
            "http://die-offenbachs.homelinux.org/eric/plugins/repository.xml",
        "VersionsUrls" : QtCore.QStringList() \
            << "http://die-offenbachs.homelinux.org/eric/snapshots4/versions" \
            << "http://eric-ide.python-projects.org/snapshots4/versions", 
        
        "OpenOnStartup" : 0,        # 0 = nothing
                                    # 1 = last file
                                    # 2 = last project
                                    # 3 = last multiproject
                                    # 4 = last global session
        
        "DownloadPath" : "", 
        "RequestDownloadFilename" : 1, 
        "CheckErrorLog" : 1, 
        
        "LogStdErrColour" : QtGui.QColor(QtCore.Qt.red),
    }
    viewProfilesLength = len(uiDefaults["ViewProfiles"]["edit"][2])
    
    iconsDefaults = {
        "Path" : QtCore.QStringList(),
    }
    
    # defaults for the editor settings
    editorDefaults = {
        "AutosaveInterval" : 0,
        "TabWidth" : 4,
        "IndentWidth" : 4,
        "LinenoWidth" : 4,
        "IndentationGuides" : 1,
        "UnifiedMargins" : 0, 
        "LinenoMargin" : 1,
        "FoldingMargin" : 1,
        "FoldingStyle" : 1,
        "TabForIndentation" : 0,
        "TabIndents" : 1,
        "ConvertTabsOnLoad" : 0,
        "AutomaticEOLConversion" : 1,
        "ShowWhitespace" : 0,
        "ShowEOL" : 0,
        "UseMonospacedFont" : 0,
        "WrapLongLines" : 0,
        "WarnFilesize" : 512,
        "ClearBreaksOnClose" : 1,
        "StripTrailingWhitespace" : 0, 
        "CommentColumn0" : 1, 
        
        "EdgeMode" : Qsci.QsciScintilla.EdgeNone,
        "EdgeColumn" : 80,
        
        "AutoIndentation" : 1,
        "BraceHighlighting" : 1,
        "CreateBackupFile" : 0,
        "CaretLineVisible" : 0,
        "CaretWidth" : 1,
        "ColourizeSelText" : 0,
        "CustomSelectionColours" : 0,
        "ExtendSelectionToEol" : 0,
        
        "AutoPrepareAPIs" : 0,
        
        "AutoCompletionEnabled" : 0,
        "AutoCompletionCaseSensitivity" : 1,
        "AutoCompletionReplaceWord" : 0,
        "AutoCompletionShowSingle" : 0,
        "AutoCompletionSource" : Qsci.QsciScintilla.AcsDocument,
        "AutoCompletionThreshold" : 2,
        "AutoCompletionFillups" : 0,
        
        "CallTipsEnabled" : 0,
        "CallTipsVisible" : 0,
        "CallTipsStyle"   : Qsci.QsciScintilla.CallTipsNoContext,
        "CallTipsScintillaOnFail" : 0,  # show QScintilla calltips, if plugin fails
        
        "AutoCheckSyntax" : 1,
        "AutoReopen" : 0,
        
        "MiniContextMenu" : 0,
        
        "SearchMarkersEnabled" : 1, 
        "QuickSearchMarkersEnabled" : 1, 
        "MarkOccurrencesEnabled" : 1, 
        "MarkOccurrencesTimeout" : 500,     # 500 milliseconds
        "AdvancedEncodingDetection" : 1, 
        
        "SpellCheckingEnabled" : 1, 
        "AutoSpellCheckingEnabled" : 1, 
        "AutoSpellCheckChunkSize" : 30, 
        "SpellCheckStringsOnly" : 1, 
        "SpellCheckingMinWordSize" : 3, 
        "SpellCheckingDefaultLanguage" : "en", 
        "SpellCheckingPersonalWordList" : "", 
        "SpellCheckingPersonalExcludeList" : "", 
        
        "DefaultEncoding" : "utf-8",
        "DefaultOpenFilter" : "",
        "DefaultSaveFilter" : "",
        
        # All (most) lexers
        "AllFoldCompact" : 1,
        
        # Bash specifics
        "BashFoldComment" : 1,
        
        # CMake specifics
        "CMakeFoldAtElse" : 0,
        
        # C++ specifics
        "CppCaseInsensitiveKeywords" : 0, 
        "CppFoldComment" : 1,
        "CppFoldPreprocessor" : 0,
        "CppFoldAtElse" : 0,
        "CppIndentOpeningBrace" : 0,
        "CppIndentClosingBrace" : 0,
        "CppDollarsAllowed" : 1, 
        
        # CSS specifics
        "CssFoldComment" : 1,
        
        # D specifics
        "DFoldComment" : 1,
        "DFoldAtElse" : 0,
        "DIndentOpeningBrace" : 0,
        "DIndentClosingBrace" : 0,
        
        # HTML specifics
        "HtmlFoldPreprocessor" : 0,
        "HtmlFoldScriptComments" : 0, 
        "HtmlFoldScriptHeredocs" : 0, 
        "HtmlCaseSensitiveTags" : 0,
        
        # Pascal specifics
        "PascalFoldComment" : 1, 
        "PascalFoldPreprocessor" : 0, 
        "PascalSmartHighlighting" : 1, 
        
        # Perl specifics
        "PerlFoldComment" : 1,
        "PerlFoldPackages" : 1, 
        "PerlFoldPODBlocks" : 1, 
        
        # PostScript specifics
        "PostScriptTokenize" : 0, 
        "PostScriptLevel" : 3, 
        "PostScriptFoldAtElse" : 0, 
        
        # Povray specifics
        "PovFoldComment" : 1,
        "PovFoldDirectives" : 0,
        
        # Python specifics
        "PythonBadIndentation" : 1,
        "PythonFoldComment" : 1,
        "PythonFoldString" : 1,
        "PythonAutoIndent" : 1,
        "PythonAllowV2Unicode" : 1, 
        "PythonAllowV3Binary" : 1, 
        "PythonAllowV3Bytes" : 1, 
        
        # SQL specifics
        "SqlFoldComment" : 1,
        "SqlBackslashEscapes" : 0,
        
        # VHDL specifics
        "VHDLFoldComment" : 1,
        "VHDLFoldAtElse" : 1,
        "VHDLFoldAtBegin" : 1, 
        "VHDLFoldAtParenthesis" : 1, 
        
        # XML specifics
        "XMLStyleScripts" : 1, 
        
        # YAML specifics
        "YAMLFoldComment" : 0, 
    }
    
    if isWindowsPlatform():
        editorDefaults["EOLMode"] = Qsci.QsciScintilla.EolWindows
    else:
        editorDefaults["EOLMode"] = Qsci.QsciScintilla.EolUnix
    
    editorColourDefaults = {
        "CurrentMarker"        : QtGui.QColor(QtCore.Qt.yellow),
        "ErrorMarker"          : QtGui.QColor(QtCore.Qt.red),
        "MatchingBrace"        : QtGui.QColor(QtCore.Qt.green),
        "MatchingBraceBack"    : QtGui.QColor(QtCore.Qt.white),
        "NonmatchingBrace"     : QtGui.QColor(QtCore.Qt.red),
        "NonmatchingBraceBack" : QtGui.QColor(QtCore.Qt.white),
        "CallTipsBackground"   : QtGui.QColor(QtCore.Qt.white),
        "CaretForeground"      : QtGui.QColor(QtCore.Qt.black),
        "CaretLineBackground"  : QtGui.QColor(QtCore.Qt.white),
        "Edge"                 : QtGui.QColor(QtCore.Qt.lightGray),
        "SelectionBackground"  : QtGui.QColor(QtCore.Qt.black),
        "SelectionForeground"  : QtGui.QColor(QtCore.Qt.white),
        "SearchMarkers"        : QtGui.QColor(QtCore.Qt.blue),
        "MarginsBackground"    : QtGui.QColor(QtCore.Qt.lightGray),
        "MarginsForeground"    : QtGui.QColor(QtCore.Qt.black),
        "FoldmarginBackground" : QtGui.QColor(230, 230, 230),
        "SpellingMarkers"      : QtGui.QColor(QtCore.Qt.red),
    }
    
    editorOtherFontsDefaults = {
        "MarginsFont"    : "Sans Serif,10,-1,5,50,0,0,0,0,0",
        "DefaultFont"    : "Sans Serif,10,-1,5,50,0,0,0,0,0",
        "MonospacedFont" : "Courier,10,-1,5,50,0,0,0,0,0", 
    }
    
    editorTypingDefaults = {
        "Python/EnabledTypingAids"  : 1, 
        "Python/InsertClosingBrace" : 1,
        "Python/IndentBrace"        : 1,
        "Python/SkipBrace"          : 1,
        "Python/InsertQuote"        : 1,
        "Python/DedentElse"         : 1,
        "Python/DedentExcept"       : 1,
        "Python/Py24StyleTry"       : 1, 
        "Python/InsertImport"       : 1,
        "Python/InsertSelf"         : 1,
        "Python/InsertBlank"        : 1,
        "Python/ColonDetection"     : 1,
        "Python/DedentDef"          : 0, 
        
        "Ruby/EnabledTypingAids"    : 1, 
        "Ruby/InsertClosingBrace"   : 1,
        "Ruby/IndentBrace"          : 1,
        "Ruby/SkipBrace"            : 1,
        "Ruby/InsertQuote"          : 1,
        "Ruby/InsertBlank"          : 1,
        "Ruby/InsertHereDoc"        : 1, 
        "Ruby/InsertInlineDoc"      : 1, 
    }
    
    editorExporterDefaults = {
        "HTML/WYSIWYG"          : 1, 
        "HTML/Folding"          : 0, 
        "HTML/OnlyStylesUsed"   : 0, 
        "HTML/FullPathAsTitle"  : 0, 
        "HTML/UseTabs"          : 0, 
        
        "RTF/WYSIWYG"           : 1, 
        "RTF/UseTabs"           : 0, 
        "RTF/Font"              : "Courier New,10,-1,5,50,0,0,0,0,0", 
        
        "PDF/Magnification"     : 0, 
        "PDF/Font"              : "Helvetica",  # must be Courier, Helvetica or Times
        "PDF/PageSize"          : "A4",         # must be A4 or Letter
        "PDF/MarginLeft"        : 36, 
        "PDF/MarginRight"       : 36, 
        "PDF/MarginTop"         : 36, 
        "PDF/MarginBottom"      : 36, 
        
        "TeX/OnlyStylesUsed"    : 0, 
        "TeX/FullPathAsTitle"   : 0, 
    }
    
    # defaults for the printer settings
    printerDefaults = {
        "PrinterName" : "",
        "ColorMode" : 1,
        "FirstPageFirst" : 1,
        "Magnification" : -3,
        "Orientation" : 0,
        "PageSize": 0,
        "HeaderFont" : "Serif,10,-1,5,50,0,0,0,0,0", 
        "LeftMargin" : 1.0, 
        "RightMargin" : 1.0, 
        "TopMargin" : 1.0, 
        "BottomMargin" : 1.0, 
    }
    
    # defaults for the project settings
    projectDefaults = {
        "SearchNewFiles" : 0,
        "SearchNewFilesRecursively" : 0,
        "AutoIncludeNewFiles" : 0,
        "AutoLoadSession" : 0,
        "AutoSaveSession" : 0,
        "SessionAllBreakpoints" : 0,
        "CompressedProjectFiles" : 0,
        "XMLTimestamp" : 1,
        "AutoCompileForms" : 0,
        "AutoCompileResources" : 0,
        "AutoLoadDbgProperties" : 0,
        "AutoSaveDbgProperties" : 0,
        "HideGeneratedForms" : 0,
        "FollowEditor" : 1, 
        "RecentNumber" : 9, 
    }
    
    # defaults for the multi project settings
    multiProjectDefaults = {
        "OpenMasterAutomatically" : 1, 
        "XMLTimestamp" : 1,
        "RecentNumber" : 9, 
    }
    
    # defaults for the project browser flags settings
    projectBrowserFlagsDefaults = {
        "Qt4" : 
            SourcesBrowserFlag | \
            FormsBrowserFlag | \
            ResourcesBrowserFlag | \
            TranslationsBrowserFlag | \
            InterfacesBrowserFlag | \
            OthersBrowserFlag, 
        "Qt4C" : 
            SourcesBrowserFlag | \
            ResourcesBrowserFlag | \
            TranslationsBrowserFlag | \
            InterfacesBrowserFlag | \
            OthersBrowserFlag, 
        "E4Plugin" : 
            SourcesBrowserFlag | \
            FormsBrowserFlag | \
            ResourcesBrowserFlag | \
            TranslationsBrowserFlag | \
            InterfacesBrowserFlag | \
            OthersBrowserFlag, 
        "Kde4" : 
            SourcesBrowserFlag | \
            FormsBrowserFlag | \
            ResourcesBrowserFlag | \
            InterfacesBrowserFlag | \
            OthersBrowserFlag, 
        "Console" : 
            SourcesBrowserFlag | \
            InterfacesBrowserFlag | \
            OthersBrowserFlag, 
        "Other" : 
            SourcesBrowserFlag | \
            InterfacesBrowserFlag | \
            OthersBrowserFlag, 
        "PySide" :
            SourcesBrowserFlag | \
            FormsBrowserFlag | \
            ResourcesBrowserFlag | \
            TranslationsBrowserFlag | \
            InterfacesBrowserFlag | \
            OthersBrowserFlag, 
        "PySideC" :
            SourcesBrowserFlag | \
            ResourcesBrowserFlag | \
            TranslationsBrowserFlag | \
            InterfacesBrowserFlag | \
            OthersBrowserFlag, 
    }
    
    # defaults for the project browser colour settings
    projectBrowserColourDefaults = {
        "Highlighted" : QtGui.QColor(QtCore.Qt.red),
        
        "VcsAdded"    : QtGui.QColor(QtCore.Qt.blue),
        "VcsConflict" : QtGui.QColor(QtCore.Qt.red),
        "VcsModified" : QtGui.QColor(QtCore.Qt.yellow),
        "VcsReplaced" : QtGui.QColor(QtCore.Qt.cyan), 
        "VcsUpdate"   : QtGui.QColor(QtCore.Qt.green),
    }
    
    # defaults for the help settings
    helpDefaults = {
        "HelpViewerType" : 1,      # this coresponds with the radio button id
        "CustomViewer" : "",
        "PythonDocDir" : "",
        "QtDocDir" : "",
        "Qt4DocDir" : "",
        "PyQt4DocDir" : "",
        "PyKDE4DocDir" : "",
        "PySideDocDir" : "", 
        "SingleHelpWindow" : 1,
        "SaveGeometry" : 1,
        "HelpViewerState" : QtCore.QByteArray(), 
        "WebSearchSuggestions" : 1, 
        "WebSearchEngine" : "Google", 
        "WebSearchKeywords" : [],   # array of two tuples (keyword, search engine name)
        "DiskCacheEnabled" : 1, 
        "DiskCacheSize" : 50,       # 50 MB
        "AcceptCookies" : 2,        # CookieJar.AcceptOnlyFromSitesNavigatedTo
        "KeepCookiesUntil" : 0,     # CookieJar.KeepUntilExpire
        "FilterTrackingCookies" : 1, 
        "PrintBackgrounds" : 0, 
        "StartupBehavior" : 0,      # show home page
        "HomePage": "pyrc:home",
        "HistoryLimit" : 30, 
        "DefaultScheme" : "file://", 
        "SavePasswords" : 0, 
        "AdBlockEnabled" : 0, 
        "AdBlockSubscriptions" : QtCore.QStringList(), 
    }
    
    websettings = QWebSettings.globalSettings()
    fontFamily = websettings.fontFamily(QWebSettings.StandardFont)
    fontSize = websettings.fontSize(QWebSettings.DefaultFontSize)
    helpDefaults["StandardFont"] = QtGui.QFont(fontFamily, fontSize).toString()
    fontFamily = websettings.fontFamily(QWebSettings.FixedFont)
    fontSize = websettings.fontSize(QWebSettings.DefaultFixedFontSize)
    helpDefaults["FixedFont"] = QtGui.QFont(fontFamily, fontSize).toString()
    helpDefaults.update({
        "AutoLoadImages" : 
            websettings.testAttribute(QWebSettings.AutoLoadImages), 
        "UserStyleSheet" : "", 
        "SaveUrlColor" : QtGui.QColor(248, 248, 210), 
        "JavaEnabled" : 
            websettings.testAttribute(QWebSettings.JavaEnabled), 
        "JavaScriptEnabled" : 
            websettings.testAttribute(QWebSettings.JavascriptEnabled), 
        "JavaScriptCanOpenWindows" : 
            websettings.testAttribute(QWebSettings.JavascriptCanOpenWindows), 
        "JavaScriptCanAccessClipboard" : 
            websettings.testAttribute(QWebSettings.JavascriptCanAccessClipboard), 
        "PluginsEnabled" :
            websettings.testAttribute(QWebSettings.PluginsEnabled), 
    })

    # defaults for system settings
    sysDefaults = {
        "StringEncoding" : "utf-8",
        "IOEncoding"     : "utf-8",
    }
    
    # defaults for the shell settings
    shellDefaults = {
        "LinenoWidth" : 4,
        "LinenoMargin" : 1,
        "AutoCompletionEnabled" : 1,
        "CallTipsEnabled" : 1,
        "WrapEnabled" : 1,
        "MaxHistoryEntries" : 100,
        "SyntaxHighlightingEnabled" : 1,
        "ShowStdOutErr" : 1, 
        "UseMonospacedFont" : 0,
        "MonospacedFont" : "Courier,10,-1,5,50,0,0,0,0,0", 
        "MarginsFont" : "Sans Serif,10,-1,5,50,0,0,0,0,0",
    }

    # defaults for the terminal settings
    terminalDefaults = {
        "LinenoWidth" : 4,
        "LinenoMargin" : 1,
        "MaxHistoryEntries" : 100,
        "SyntaxHighlightingEnabled" : 1,
        "Shell" : "", 
        "ShellInteractive" : 1, 
        "UseMonospacedFont" : 0,
        "MonospacedFont" : "Courier,10,-1,5,50,0,0,0,0,0", 
        "MarginsFont" : "Sans Serif,10,-1,5,50,0,0,0,0,0",
    }
    if sys.platform.lower().startswith("linux"):
        terminalDefaults["Shell"] = "bash"

    # defaults for Qt related stuff
    qtDefaults = {
        "Qt4TranslationsDir" : "",
        "QtToolsPrefix4" : "", 
        "QtToolsPostfix4" : "", 
        "Qt4Dir" : "", 
    }
    
    # defaults for corba related stuff
    corbaDefaults = {
        "omniidl" : "omniidl"
    }
    
    # defaults for user related stuff
    userDefaults = {
        "Email" : "",
        "MailServer" : "",
        "Signature" : "",
        "MailServerAuthentication" : 0,
        "MailServerUser" : "",
        "MailServerPassword" : "",
        "MailServerUseTLS" : 0, 
        "MailServerPort" : 25, 
        "UseSystemEmailClient" : 0, 
    }
    
    # defaults for vcs related stuff
    vcsDefaults = {
        "AutoClose" : 0,
        "AutoSaveFiles" : 1,
        "AutoSaveProject" : 1,
        "AutoUpdate" : 0, 
        "StatusMonitorInterval" : 30,
        "MonitorLocalStatus" : 0, 
    }
    
    # defaults for tasks related stuff
    tasksDefaults = {
        "TasksMarkers"       : "TO" + "DO:", 
        "TasksMarkersBugfix" : "FIX" + "ME:",
        # needed to keep it from being recognized as a task
        "TasksColour"          : QtGui.QColor(QtCore.Qt.black),
        "TasksBugfixColour"    : QtGui.QColor(QtCore.Qt.red),
        "TasksBgColour"        : QtGui.QColor(QtCore.Qt.white),
        "TasksProjectBgColour" : QtGui.QColor(QtCore.Qt.lightGray),
    }
    
    # defaults for templates related stuff
    templatesDefaults = {
        "AutoOpenGroups" : 1,
        "SingleDialog"   : 0,
        "ShowTooltip"    : 0,
        "SeparatorChar"  : "$",
    }
    
    # defaults for plugin manager related stuff
    pluginManagerDefaults = {
        "ActivateExternal" : 1,
        "DownloadPath" : ""
    }
    
    # defaults for the printer settings
    graphicsDefaults = {
        "Font" : "SansSerif,10,-1,5,50,0,0,0,0,0"
    }
    
    # defaults for the icon editor
    iconEditorDefaults = {
        "IconEditorState" : QtCore.QByteArray(), 
    }
    
    # defaults for geometry
    geometryDefaults = {
        "HelpViewerGeometry" : QtCore.QByteArray(),
        "IconEditorGeometry" : QtCore.QByteArray(),
        "MainGeometry"       : QtCore.QByteArray(),
        "MainMaximized"      : 0, 
    }

    # if true, revert layouts to factory defaults
    resetLayout = False

def readToolGroups(prefClass = Prefs):
    """
    Module function to read the tool groups configuration.
    
    @param prefClass preferences class used as the storage area
    @return list of tuples defing the tool groups
    """
    toolGroups = []
    groups = prefClass.settings.value("Toolgroups/Groups", 
        QtCore.QVariant(0)).toInt()[0]
    for groupIndex in range(groups):
        groupName = \
            prefClass.settings.value("Toolgroups/%02d/Name" % groupIndex).toString()
        group = [unicode(groupName), []]
        items = prefClass.settings.value("Toolgroups/%02d/Items" % groupIndex, 
            QtCore.QVariant(0)).toInt()[0]
        for ind in range(items):
            menutext = prefClass.settings.value(\
                "Toolgroups/%02d/%02d/Menutext" % (groupIndex, ind)).toString()
            icon = prefClass.settings.value(\
                "Toolgroups/%02d/%02d/Icon" % (groupIndex, ind)).toString()
            executable = prefClass.settings.value(\
                "Toolgroups/%02d/%02d/Executable" % (groupIndex, ind)).toString()
            arguments = prefClass.settings.value(\
                "Toolgroups/%02d/%02d/Arguments" % (groupIndex, ind)).toString()
            redirect = prefClass.settings.value(\
                "Toolgroups/%02d/%02d/Redirect" % (groupIndex, ind)).toString()
            
            if not menutext.isEmpty():
                if unicode(menutext) == '--':
                    tool = {
                        'menutext' : '--',
                        'icon' : '',
                        'executable' : '',
                        'arguments' : '',
                        'redirect' : 'no',
                    }
                    group[1].append(tool)
                elif not executable.isEmpty():
                    tool = {
                        'menutext' : unicode(menutext),
                        'icon' : unicode(icon),
                        'executable' : unicode(executable),
                        'arguments' : unicode(arguments),
                        'redirect' : unicode(redirect),
                    }
                    group[1].append(tool)
        toolGroups.append(group)
    currentGroup = prefClass.settings.value("Toolgroups/Current Group", 
        QtCore.QVariant(-1)).toInt()[0]
    return toolGroups, currentGroup
    
def saveToolGroups(toolGroups, currentGroup, prefClass = Prefs):
    """
    Module function to write the tool groups configuration.
    
    @param toolGroups reference to the list of tool groups
    @param currentGroup index of the currently selected tool group (integer)
    @param prefClass preferences class used as the storage area
    """
    # first step, remove all tool group entries
    prefClass.settings.remove("Toolgroups")
    
    # second step, write the tool group entries
    prefClass.settings.setValue("Toolgroups/Groups", QtCore.QVariant(len(toolGroups)))
    groupIndex = 0
    for group in toolGroups:
        prefClass.settings.setValue("Toolgroups/%02d/Name" % groupIndex,
            QtCore.QVariant(group[0]))
        prefClass.settings.setValue("Toolgroups/%02d/Items" % groupIndex,
            QtCore.QVariant(len(group[1])))
        ind = 0
        for tool in group[1]:
            prefClass.settings.setValue(\
                "Toolgroups/%02d/%02d/Menutext" % (groupIndex, ind), 
                QtCore.QVariant(tool['menutext']))
            prefClass.settings.setValue(\
                "Toolgroups/%02d/%02d/Icon" % (groupIndex, ind), 
                QtCore.QVariant(tool['icon']))
            prefClass.settings.setValue(\
                "Toolgroups/%02d/%02d/Executable" % (groupIndex, ind), 
                QtCore.QVariant(tool['executable']))
            prefClass.settings.setValue(\
                "Toolgroups/%02d/%02d/Arguments" % (groupIndex, ind), 
                QtCore.QVariant(tool['arguments']))
            prefClass.settings.setValue(\
                "Toolgroups/%02d/%02d/Redirect" % (groupIndex, ind), 
                QtCore.QVariant(tool['redirect']))
            ind += 1
        groupIndex += 1
    prefClass.settings.setValue(\
        "Toolgroups/Current Group", QtCore.QVariant(currentGroup))
    
def initPreferences():
    """
    Module function to initialize the central configuration store. 
    """
    if not isWindowsPlatform():
        cfile = os.path.join(os.path.expanduser("~"), ".config", 
            settingsNameOrganization, settingsNameGlobal + ".conf")
        ifile = os.path.splitext(cfile)[0] + ".ini"
        if os.path.exists(cfile) and not os.path.exists(ifile):
            os.rename(cfile, ifile)
    Prefs.settings = QtCore.QSettings(
        QtCore.QSettings.IniFormat, QtCore.QSettings.UserScope, 
        settingsNameOrganization, settingsNameGlobal)
    if not isWindowsPlatform():
        hp = QtCore.QDir.homePath()
        dn = QtCore.QDir(hp)
        dn.mkdir(".eric4")
    QtCore.QCoreApplication.setOrganizationName(settingsNameOrganization)
    QtCore.QCoreApplication.setApplicationName(settingsNameGlobal)
    
def syncPreferences(prefClass = Prefs):
    """
    Module function to sync the preferences to disk.
    
    In addition to syncing, the central configuration store is reinitialized as well.
    
    @param prefClass preferences class used as the storage area
    """
    prefClass.settings.setValue("General/Configured", QtCore.QVariant(1))
    initPreferences()
    
def exportPreferences(prefClass = Prefs):
    """
    Module function to export the current preferences.
    
    @param prefClass preferences class used as the storage area
    """
    from KdeQt import KQFileDialog

    filename = KQFileDialog.getSaveFileName(\
        None,
        QtCore.QCoreApplication.translate("Preferences", "Export Preferences"),
        QtCore.QString(),
        QtCore.QString(),
        None,
        QtGui.QFileDialog.Options(QtGui.QFileDialog.DontConfirmOverwrite))
    if not filename.isEmpty():
        settingsFile = unicode(prefClass.settings.fileName())
        prefClass.settings = None
        shutil.copy(settingsFile, unicode(filename))
        initPreferences()

def importPreferences(prefClass = Prefs):
    """
    Module function to import preferences from a file previously saved by
    the export function.
    
    @param prefClass preferences class used as the storage area
    """
    from KdeQt import KQFileDialog
    
    filename = KQFileDialog.getOpenFileName(\
        None,
        QtCore.QCoreApplication.translate("Preferences", "Import Preferences"),
        QtCore.QString(),
        QtCore.QString(),
        None)
    if not filename.isEmpty():
        settingsFile = unicode(prefClass.settings.fileName())
        shutil.copy(unicode(filename), settingsFile)
        initPreferences()

def isConfigured(prefClass = Prefs):
    """
    Module function to check, if the the application has been configured.
    
    @param prefClass preferences class used as the storage area
    @return flag indicating the configured status (boolean)
    """
    return prefClass.settings.value("General/Configured", QtCore.QVariant(0)).toInt()[0]
    
def initRecentSettings():
    """
    Module function to initialize the central configuration store for recently
    opened files and projects. 
    
    This function is called once upon import of the module.
    """
    if not isWindowsPlatform():
        cfile = os.path.join(os.path.expanduser("~"), ".config", 
            settingsNameOrganization, settingsNameRecent + ".conf")
        ifile = os.path.splitext(cfile)[0] + ".ini"
        if os.path.exists(cfile) and not os.path.exists(ifile):
            os.rename(cfile, ifile)
    Prefs.rsettings = QtCore.QSettings(
        QtCore.QSettings.IniFormat, QtCore.QSettings.UserScope, 
        settingsNameOrganization, settingsNameRecent)
    
def getVarFilters(prefClass = Prefs):
    """
    Module function to retrieve the variables filter settings.
    
    @param prefClass preferences class used as the storage area
    @return a tuple defing the variables filter
    """
    localsFilter = eval(unicode(prefClass.settings.value("Variables/LocalsFilter", 
        QtCore.QVariant(unicode(prefClass.varDefaults["LocalsFilter"]))).toString()))
    globalsFilter = eval(unicode(prefClass.settings.value("Variables/GlobalsFilter", 
        QtCore.QVariant(unicode(prefClass.varDefaults["GlobalsFilter"]))).toString()))
    return (localsFilter, globalsFilter)
    
def setVarFilters(filters, prefClass = Prefs):
    """
    Module function to store the variables filter settings.
    
    @param prefClass preferences class used as the storage area
    """
    prefClass.settings.setValue("Variables/LocalsFilter",
        QtCore.QVariant(unicode(filters[0])))
    prefClass.settings.setValue("Variables/GlobalsFilter",
        QtCore.QVariant(unicode(filters[1])))
    
def getDebugger(key, prefClass = Prefs):
    """
    Module function to retrieve the debugger settings.
    
    @param key the key of the value to get
    @param prefClass preferences class used as the storage area
    @return the requested debugger setting
    """
    if key in ["RemoteDbgEnabled", "PassiveDbgEnabled",
                "PassiveDbgPort", "CustomPythonInterpreter",
                "AutomaticReset", "DebugEnvironmentReplace",
                "PythonRedirect", "PythonNoEncoding", 
                "Python3Redirect", "Python3NoEncoding", 
                "RubyRedirect",
                "ConsoleDbgEnabled", "PathTranslation", 
                "Autosave", "ThreeStateBreakPoints", 
                "SuppressClientExit", "BreakAlways", 
              ]:
        return prefClass.settings.value("Debugger/" + key,
            QtCore.QVariant(prefClass.debuggerDefaults[key])).toInt()[0]
    
    if key in ["RemoteHost", "RemoteExecution", "PythonInterpreter",
                "Python3Interpreter", "RubyInterpreter", 
                "DebugClient", "DebugClientType",
                "DebugClient3", "DebugClientType3",
                "DebugEnvironment", "ConsoleDbgCommand",
                "PathTranslationRemote", "PathTranslationLocal",
                "NetworkInterface", "PassiveDbgType", 
                "PythonExtensions", "Python3Extensions"]:
        return prefClass.settings.value("Debugger/" + key,
            QtCore.QVariant(prefClass.debuggerDefaults[key])).toString()
    
    if key in ["AllowedHosts"]:
        return prefClass.settings.value("Debugger/" + key,
            QtCore.QVariant(prefClass.debuggerDefaults[key])).toStringList()
    
def setDebugger(key, value, prefClass = Prefs):
    """
    Module function to store the debugger settings.
    
    @param key the key of the setting to be set
    @param value the value to be set
    @param prefClass preferences class used as the storage area
    """
    prefClass.settings.setValue("Debugger/" + key, QtCore.QVariant(value))

def getPython(key, prefClass = Prefs):
    """
    Module function to retrieve the Python settings.
    
    @param key the key of the value to get
    @param prefClass preferences class used as the storage area
    @return the requested debugger setting
    """
    if key in ["PythonExtensions", "Python3Extensions"]:
        exts = []
        for ext in unicode(getDebugger(key, prefClass)).split():
            if ext.startswith("."):
                exts.append(ext)
            else:
                exts.append(".%s" % ext)
        return exts

def setPython(key, value, prefClass = Prefs):
    """
    Module function to store the Python settings.
    
    @param key the key of the setting to be set
    @param value the value to be set
    @param prefClass preferences class used as the storage area
    """
    if key in ["PythonExtensions", "Python3Extensions"]:
        setDebugger(key, value, prefClass)

def getUILanguage(prefClass = Prefs):
    """
    Module function to retrieve the language for the user interface.
    
    @param prefClass preferences class used as the storage area
    @return the language for the UI
    """
    lang = \
        prefClass.settings.value("UI/Language",
            QtCore.QVariant(prefClass.uiDefaults["Language"])).toString()
    if unicode(lang) == "None" or unicode(lang) == "" or lang is None:
        return None
    else:
        return unicode(lang)
    
def setUILanguage(lang, prefClass = Prefs):
    """
    Module function to store the language for the user interface.
    
    @param lang the language
    @param prefClass preferences class used as the storage area
    """
    if lang is None:
        prefClass.settings.setValue("UI/Language", QtCore.QVariant("None"))
    else:
        prefClass.settings.setValue("UI/Language", QtCore.QVariant(lang))

def getUILayout(prefClass = Prefs):
    """
    Module function to retrieve the layout for the user interface.
    
    @param prefClass preferences class used as the storage area
    @return the UI layout as a tuple of main layout, flag for
        an embedded shell and a value for an embedded file browser
    """
    layout = (\
        prefClass.settings.value("UI/LayoutType", 
            QtCore.QVariant(prefClass.uiDefaults["LayoutType"])).toString(), 
        prefClass.settings.value("UI/LayoutShellEmbedded", 
            QtCore.QVariant(prefClass.uiDefaults["LayoutShellEmbedded"]))\
            .toInt()[0], 
        prefClass.settings.value("UI/LayoutFileBrowserEmbedded", 
            QtCore.QVariant(prefClass.uiDefaults["LayoutFileBrowserEmbedded"]))\
            .toInt()[0], 
    )
    return layout
    
def setUILayout(layout, prefClass = Prefs):
    """
    Module function to store the layout for the user interface.
    
    @param layout the layout type
    @param prefClass preferences class used as the storage area
    """
    prefClass.settings.setValue("UI/LayoutType", 
        QtCore.QVariant(layout[0]))
    prefClass.settings.setValue("UI/LayoutShellEmbedded", 
        QtCore.QVariant(layout[1]))
    prefClass.settings.setValue("UI/LayoutFileBrowserEmbedded", 
        QtCore.QVariant(layout[2]))

def getViewManager(prefClass = Prefs):
    """
    Module function to retrieve the selected viewmanager type.
    
    @param prefClass preferences class used as the storage area
    @return the viewmanager type
    """
    return unicode(prefClass.settings.value("UI/ViewManager",
        QtCore.QVariant(prefClass.uiDefaults["ViewManager"])).toString())
    
def setViewManager(vm, prefClass = Prefs):
    """
    Module function to store the selected viewmanager type.
    
    @param vm the viewmanager type
    @param prefClass preferences class used as the storage area
    """
    prefClass.settings.setValue("UI/ViewManager", QtCore.QVariant(vm))

def getUI(key, prefClass = Prefs):
    """
    Module function to retrieve the various UI settings.
    
    @param key the key of the value to get
    @param prefClass preferences class used as the storage area
    @return the requested UI setting
    """
    if key in ["BrowsersListFoldersFirst", "BrowsersHideNonPublic",
                "BrowsersListContentsByOccurrence", "LogViewerAutoRaise", 
                "SingleApplicationMode", "TabViewManagerFilenameLength",
                "TabViewManagerFilenameOnly", 
                "CaptionShowsFilename", "CaptionFilenameLength",
                "RecentNumber", "UseKDEDialogs", "ShowSplash", 
                "PerformVersionCheck", "SingleCloseButton", 
                "UseProxy", "ProxyPort", "ProxyType", 
                "TopLeftByLeft", "BottomLeftByLeft", 
                "TopRightByRight", "BottomRightByRight", 
                "OpenOnStartup", "RequestDownloadFilename", 
                "LayoutShellEmbedded", "LayoutFileBrowserEmbedded", 
                "CheckErrorLog"]:
        return prefClass.settings.value("UI/" + key,
            QtCore.QVariant(prefClass.uiDefaults[key])).toInt()[0]
    if key in ["Style", "StyleSheet", 
                "ProxyHost", "ProxyUser", 
                "PluginRepositoryUrl", "DownloadPath"]:
        return prefClass.settings.value("UI/" + key,
            QtCore.QVariant(prefClass.uiDefaults[key])).toString()
    if key == "ProxyPassword":
        from Utilities import pwDecode
        return pwDecode(prefClass.settings.value("UI/" + key,
            QtCore.QVariant(prefClass.uiDefaults[key])).toString())
    if key in ["VersionsUrls"]:
        return prefClass.settings.value("UI/" + key, 
            QtCore.QVariant(prefClass.uiDefaults[key])).toStringList()
    if key in ["LogStdErrColour"]:
        col = prefClass.settings.value("UI/" + key)
        if col.isValid():
            return QtGui.QColor(col.toString())
        else:
            return prefClass.uiDefaults[key]
    if key == "ViewProfiles":
        v = prefClass.settings.value("UI/ViewProfiles")
        if v.isValid():
            viewProfiles = eval(unicode(v.toString()))
            for name in ["edit", "debug"]:
                # adjust entries for individual windows
                vpLength = len(viewProfiles[name][0])
                if vpLength < prefClass.viewProfilesLength:
                    viewProfiles[name][0].extend(\
                        prefClass.uiDefaults["ViewProfiles"][name][0][vpLength:])
                
                vpLength = len(viewProfiles[name][2])
                if vpLength < prefClass.viewProfilesLength:
                    viewProfiles[name][2].extend(\
                        prefClass.uiDefaults["ViewProfiles"][name][2][vpLength:])
                
                # adjust profile
                vpLength = len(viewProfiles[name])
                if vpLength < len(prefClass.uiDefaults["ViewProfiles"][name]):
                    viewProfiles[name].extend(
                        prefClass.uiDefaults["ViewProfiles"][name][vpLength:])
        else:
            viewProfiles = prefClass.uiDefaults["ViewProfiles"]
        return viewProfiles
    if key == "ToolbarManagerState":
        v = prefClass.settings.value("UI/ToolbarManagerState")
        if v.isValid():
            return v.toByteArray()
        else:
            return prefClass.uiDefaults["ToolbarManagerState"]
    
def setUI(key, value, prefClass = Prefs):
    """
    Module function to store the various UI settings.
    
    @param key the key of the setting to be set
    @param value the value to be set
    @param prefClass preferences class used as the storage area
    """
    if key == "ViewProfiles":
        prefClass.settings.setValue("UI/" + key, QtCore.QVariant(unicode(value)))
    elif key == "LogStdErrColour":
        prefClass.settings.setValue("UI/" + key, QtCore.QVariant(value.name()))
    elif key == "ProxyPassword":
        from Utilities import pwEncode
        prefClass.settings.setValue(
            "UI/" + key, QtCore.QVariant(pwEncode(value)))
    else:
        prefClass.settings.setValue("UI/" + key, QtCore.QVariant(value))
    
def getIcons(key, prefClass = Prefs):
    """
    Module function to retrieve the various Icons settings.
    
    @param key the key of the value to get
    @param prefClass preferences class used as the storage area
    @return the requested Icons setting
    """
    dirlist = prefClass.settings.value("UI/Icons/" + key)
    if dirlist.isValid():
        return dirlist.toStringList()
    else:
        return prefClass.iconsDefaults[key]
    
def setIcons(key, value, prefClass = Prefs):
    """
    Module function to store the various Icons settings.
    
    @param key the key of the setting to be set
    @param value the value to be set
    @param prefClass preferences class used as the storage area
    """
    prefClass.settings.setValue("UI/Icons/" + key, QtCore.QVariant(value))
    
def getEditor(key, prefClass = Prefs):
    """
    Module function to retrieve the various editor settings.
    
    @param key the key of the value to get
    @param prefClass preferences class used as the storage area
    @return the requested editor setting
    """
    if key in ["DefaultEncoding", "DefaultOpenFilter", "DefaultSaveFilter", 
               "SpellCheckingDefaultLanguage", "SpellCheckingPersonalWordList", 
               "SpellCheckingPersonalExcludeList"]:
        return prefClass.settings.value("Editor/" + key,
            QtCore.QVariant(prefClass.editorDefaults[key])).toString()
    else:
        return prefClass.settings.value("Editor/" + key,
            QtCore.QVariant(prefClass.editorDefaults[key])).toInt()[0]
    
def setEditor(key, value, prefClass = Prefs):
    """
    Module function to store the various editor settings.
    
    @param key the key of the setting to be set
    @param value the value to be set
    @param prefClass preferences class used as the storage area
    """
    prefClass.settings.setValue("Editor/" + key, QtCore.QVariant(value))
    
def getEditorColour(key, prefClass = Prefs):
    """
    Module function to retrieve the various editor marker colours.
    
    @param key the key of the value to get
    @param prefClass preferences class used as the storage area
    @return the requested editor colour
    """
    col = prefClass.settings.value("Editor/Colour/" + key)
    if col.isValid():
        return QtGui.QColor(col.toString())
    else:
        return prefClass.editorColourDefaults[key]
    
def setEditorColour(key, value, prefClass = Prefs):
    """
    Module function to store the various editor marker colours.
    
    @param key the key of the colour to be set
    @param value the colour to be set
    @param prefClass preferences class used as the storage area
    """
    prefClass.settings.setValue("Editor/Colour/" + key, QtCore.QVariant(value.name()))
    
def getEditorOtherFonts(key, prefClass = Prefs):
    """
    Module function to retrieve the various editor fonts except the lexer fonts.
    
    @param key the key of the value to get
    @param prefClass preferences class used as the storage area
    @return the requested editor font (QFont)
    """
    f = QtGui.QFont()
    f.fromString(prefClass.settings.value("Editor/Other Fonts/" + key,
        QtCore.QVariant(prefClass.editorOtherFontsDefaults[key])).toString())
    return f
    
def setEditorOtherFonts(key, font, prefClass = Prefs):
    """
    Module function to store the various editor fonts except the lexer fonts.
    
    @param key the key of the font to be set
    @param font the font to be set (QFont)
    @param prefClass preferences class used as the storage area
    """
    prefClass.settings.setValue("Editor/Other Fonts/" + key,
        QtCore.QVariant(font.toString()))
    
def getEditorAPI(key, prefClass = Prefs):
    """
    Module function to retrieve the various lists of api files.
    
    @param key the key of the value to get
    @param prefClass preferences class used as the storage area
    @return the requested list of api files (QStringList)
    """
    ap = prefClass.settings.value("Editor/APIs/" + key)
    if ap.isValid():
        apis = ap.toStringList()
        if len(apis) and apis[0].isEmpty():
            return QtCore.QStringList()
        else:
            return apis
    else:
        return QtCore.QStringList()
    
def setEditorAPI(key, apilist, prefClass = Prefs):
    """
    Module function to store the various lists of api files.
    
    @param key the key of the api to be set
    @param apilist the list of api files (QStringList)
    @param prefClass preferences class used as the storage area
    """
    prefClass.settings.setValue("Editor/APIs/" + key, QtCore.QVariant(apilist))
    
def getEditorLexerAssocs(prefClass = Prefs):
    """
    Module function to retrieve all lexer associations.
    
    @param prefClass preferences class used as the storage area
    @return a reference to the list of lexer associations
        (dictionary of strings)
    """
    editorLexerAssoc = {}
    prefClass.settings.beginGroup("Editor/LexerAssociations")
    keyList = prefClass.settings.childKeys()
    prefClass.settings.endGroup()
    editorLexerAssocDefaults = QScintilla.Lexers.getDefaultLexerAssociations()
    
    if len(keyList) == 0:
        # build from scratch
        for key in editorLexerAssocDefaults.keys():
            editorLexerAssoc[key] = \
                QtCore.QString(editorLexerAssocDefaults[key])
    else:
        for key in keyList:
            key = unicode(key)
            if editorLexerAssocDefaults.has_key(key):
                defaultValue = editorLexerAssocDefaults[key]
            else:
                defaultValue = QtCore.QString()
            editorLexerAssoc[key] = \
                prefClass.settings.value("Editor/LexerAssociations/" + key,
                    QtCore.QVariant(defaultValue)).toString()
        if len(editorLexerAssoc.keys()) < len(editorLexerAssocDefaults.keys()):
            # new default lexer associations
            for key in editorLexerAssocDefaults.keys():
                if not editorLexerAssoc.has_key(key):
                    editorLexerAssoc[key] = \
                        QtCore.QString(editorLexerAssocDefaults[key])
    return editorLexerAssoc
    
def setEditorLexerAssocs(assocs, prefClass = Prefs):
    """
    Module function to retrieve all lexer associations.
    
    @param assocs dictionary of lexer associations to be set
    @param prefClass preferences class used as the storage area
    """
    # first remove lexer associations that no longer exist, than save the rest
    prefClass.settings.beginGroup("Editor/LexerAssociations")
    keyList = prefClass.settings.childKeys()
    prefClass.settings.endGroup()
    for key in keyList:
        key = unicode(key)
        if not assocs.has_key(key):
            prefClass.settings.remove("Editor/LexerAssociations/" + key)
    for key in assocs.keys():
        prefClass.settings.setValue("Editor/LexerAssociations/" + key,
            QtCore.QVariant(assocs[key]))
    
def getEditorLexerAssoc(filename, prefClass = Prefs):
    """
    Module function to retrieve a lexer association.
    
    @param filename filename used to determine the associated lexer language (string)
    @param prefClass preferences class used as the storage area
    @return the requested lexer language (string)
    """
    for pattern, language in getEditorLexerAssocs().items():
        if fnmatch.fnmatch(filename, pattern):
            return unicode(language)
    
    return ""
    
def getEditorTyping(key, prefClass = Prefs):
    """
    Module function to retrieve the various editor typing settings.
    
    @param key the key of the value to get
    @param prefClass preferences class used as the storage area
    @return the requested editor setting
    """
    return prefClass.settings.value("Editor/Typing/" + key,
        QtCore.QVariant(prefClass.editorTypingDefaults[key])).toInt()[0]
    
def setEditorTyping(key, value, prefClass = Prefs):
    """
    Module function to store the various editor typing settings.
    
    @param key the key of the setting to be set
    @param value the value to be set
    @param prefClass preferences class used as the storage area
    """
    prefClass.settings.setValue("Editor/Typing/" + key, QtCore.QVariant(value))
    
def getEditorExporter(key, prefClass = Prefs):
    """
    Module function to retrieve the various editor exporters settings.
    
    @param key the key of the value to get
    @param prefClass preferences class used as the storage area
    @return the requested editor setting
    """
    if key in ["RTF/Font"]:
        f = QtGui.QFont()
        f.fromString(prefClass.settings.value("Editor/Exporters/" + key,
            QtCore.QVariant(prefClass.editorExporterDefaults[key])).toString())
        return f
    elif key in ["PDF/Font", "PDF/PageSize"]:
        return prefClass.settings.value("Editor/Exporters/" + key, 
            QtCore.QVariant(prefClass.editorExporterDefaults[key])).toString()
    else:
        return prefClass.settings.value("Editor/Exporters/" + key,
            QtCore.QVariant(prefClass.editorExporterDefaults[key])).toInt()[0]

def setEditorExporter(key, value, prefClass = Prefs):
    """
    Module function to store the various editor exporters settings.
    
    @param key the key of the setting to be set
    @param value the value to be set
    @param prefClass preferences class used as the storage area
    """
    if key in ["RTF/Font"]:
        v = value.toString()
    else:
        v = value
    prefClass.settings.setValue("Editor/Exporters/" + key, QtCore.QVariant(v))
    
def getPrinter(key, prefClass = Prefs):
    """
    Module function to retrieve the various printer settings.
    
    @param key the key of the value to get
    @param prefClass preferences class used as the storage area
    @return the requested printer setting
    """
    if key in ["ColorMode", "FirstPageFirst", "Magnification", 
                "Orientation", "PageSize"]:
        return prefClass.settings.value("Printer/" + key,
            QtCore.QVariant(prefClass.printerDefaults[key])).toInt()[0]
    if key in ["LeftMargin", "RightMargin", "TopMargin", "BottomMargin"]:
        return prefClass.settings.value("Printer/" + key,
            QtCore.QVariant(prefClass.printerDefaults[key])).toDouble()[0]
    if key in ["PrinterName"]:
        return prefClass.settings.value("Printer/" + key,
            QtCore.QVariant(prefClass.printerDefaults[key])).toString()
    if key in ["HeaderFont"]:
        f = QtGui.QFont()
        f.fromString(prefClass.settings.value("Printer/" + key,
            QtCore.QVariant(prefClass.printerDefaults[key])).toString())
        return f

def setPrinter(key, value, prefClass = Prefs):
    """
    Module function to store the various printer settings.
    
    @param key the key of the setting to be set
    @param value the value to be set
    @param prefClass preferences class used as the storage area
    """
    if key in ["HeaderFont"]:
        v = value.toString()
    else:
        v = value
    prefClass.settings.setValue("Printer/" + key, QtCore.QVariant(v))

def getShell(key, prefClass = Prefs):
    """
    Module function to retrieve the various shell settings.
    
    @param key the key of the value to get
    @param prefClass preferences class used as the storage area
    @return the requested shell setting
    """
    if key in ["MonospacedFont", "MarginsFont"]:
        f = QtGui.QFont()
        f.fromString(prefClass.settings.value("Shell/" + key,
            QtCore.QVariant(prefClass.shellDefaults[key])).toString())
        return f
    else:
        return prefClass.settings.value("Shell/" + key,
            QtCore.QVariant(prefClass.shellDefaults[key])).toInt()[0]

def setShell(key, value, prefClass = Prefs):
    """
    Module function to store the various shell settings.
    
    @param key the key of the setting to be set
    @param value the value to be set
    @param prefClass preferences class used as the storage area
    """
    if key in ["MonospacedFont", "MarginsFont"]:
        prefClass.settings.setValue("Shell/" + key,
            QtCore.QVariant(value.toString()))
    else:
        prefClass.settings.setValue("Shell/" + key, QtCore.QVariant(value))

def getTerminal(key, prefClass = Prefs):
    """
    Module function to retrieve the various terminal settings.
    
    @param key the key of the value to get
    @param prefClass preferences class used as the storage area
    @return the requested shell setting
    """
    if key in ["Shell"]:
        return prefClass.settings.value("Terminal/" + key,
            QtCore.QVariant(prefClass.terminalDefaults[key])).toString()
    elif key in ["MonospacedFont", "MarginsFont"]:
        f = QtGui.QFont()
        f.fromString(prefClass.settings.value("Terminal/" + key,
            QtCore.QVariant(prefClass.terminalDefaults[key])).toString())
        return f
    else:
        return prefClass.settings.value("Terminal/" + key,
            QtCore.QVariant(prefClass.terminalDefaults[key])).toInt()[0]

def setTerminal(key, value, prefClass = Prefs):
    """
    Module function to store the various terminal settings.
    
    @param key the key of the setting to be set
    @param value the value to be set
    @param prefClass preferences class used as the storage area
    """
    if key in ["MonospacedFont", "MarginsFont"]:
        prefClass.settings.setValue("Terminal/" + key,
            QtCore.QVariant(value.toString()))
    else:
        prefClass.settings.setValue("Terminal/" + key, QtCore.QVariant(value))

def getProject(key, prefClass = Prefs):
    """
    Module function to retrieve the various project handling settings.
    
    @param key the key of the value to get
    @param prefClass preferences class used as the storage area
    @return the requested project setting
    """
    return prefClass.settings.value("Project/" + key,
        QtCore.QVariant(prefClass.projectDefaults[key])).toInt()[0]
    
def setProject(key, value, prefClass = Prefs):
    """
    Module function to store the various project handling settings.
    
    @param key the key of the setting to be set
    @param value the value to be set
    @param prefClass preferences class used as the storage area
    """
    prefClass.settings.setValue("Project/" + key, QtCore.QVariant(value))
    
def getProjectBrowserFlags(key, prefClass = Prefs):
    """
    Module function to retrieve the various project browser flags settings.
    
    @param key the key of the value to get
    @param prefClass preferences class used as the storage area
    @return the requested project setting
    """
    try:
        default = prefClass.projectBrowserFlagsDefaults[key]
    except KeyError:
        default = AllBrowsersFlag
    
    return prefClass.settings.value("Project/BrowserFlags/" + key,
        QtCore.QVariant(default)).toInt()[0]
    
def setProjectBrowserFlags(key, value, prefClass = Prefs):
    """
    Module function to store the various project browser flags settings.
    
    @param key the key of the setting to be set
    @param value the value to be set
    @param prefClass preferences class used as the storage area
    """
    prefClass.settings.setValue("Project/BrowserFlags/" + key, QtCore.QVariant(value))
    
def setProjectBrowserFlagsDefault(key, value, prefClass = Prefs):
    """
    Module function to store the various project browser flags settings.
    
    @param key the key of the setting to be set
    @param value the value to be set
    @param prefClass preferences class used as the storage area
    """
    prefClass.projectBrowserFlagsDefaults[key] = value
    
def removeProjectBrowserFlags(key, prefClass = Prefs):
    """
    Module function to remove a project browser flags setting.
    
    @param key the key of the setting to be removed
    @param prefClass preferences class used as the storage area
    """
    prefClass.settings.remove("Project/BrowserFlags/" + key)
    
def getProjectBrowserColour(key, prefClass = Prefs):
    """
    Module function to retrieve the various project browser colours.
    
    @param key the key of the value to get
    @param prefClass preferences class used as the storage area
    @return the requested project browser colour
    """
    col = prefClass.settings.value("Project/Colour/" + key)
    if col.isValid():
        return QtGui.QColor(col.toString())
    else:
        return prefClass.projectBrowserColourDefaults[key]
    
def setProjectBrowserColour(key, value, prefClass = Prefs):
    """
    Module function to store the various project browser colours.
    
    @param key the key of the colour to be set
    @param value the colour to be set
    @param prefClass preferences class used as the storage area
    """
    prefClass.settings.setValue("Project/Colour/" + key, QtCore.QVariant(value.name()))
    
def getMultiProject(key, prefClass = Prefs):
    """
    Module function to retrieve the various project handling settings.
    
    @param key the key of the value to get
    @param prefClass preferences class used as the storage area
    @return the requested project setting
    """
    return prefClass.settings.value("MultiProject/" + key,
        QtCore.QVariant(prefClass.multiProjectDefaults[key])).toInt()[0]
    
def setMultiProject(key, value, prefClass = Prefs):
    """
    Module function to store the various project handling settings.
    
    @param key the key of the setting to be set
    @param value the value to be set
    @param prefClass preferences class used as the storage area
    """
    prefClass.settings.setValue("MultiProject/" + key, QtCore.QVariant(value))
    
def getQt4DocDir(prefClass = Prefs):
    """
    Module function to retrieve the Qt4DocDir setting.
    
    @param prefClass preferences class used as the storage area
    @return the requested Qt4DocDir setting (string)
    """
    s = prefClass.settings.value("Help/Qt4DocDir",
        QtCore.QVariant(prefClass.helpDefaults["Qt4DocDir"])).toString()
    if s.isEmpty():
        return os.getenv("QT4DOCDIR", "")
    else:
        return unicode(s)
    
def getHelp(key, prefClass = Prefs):
    """
    Module function to retrieve the various help settings.
    
    @param key the key of the value to get
    @param prefClass preferences class used as the storage area
    @return the requested help setting
    """
    if key in ["CustomViewer", \
               "PythonDocDir", "QtDocDir", "Qt4DocDir", "PyQt4DocDir", "PyKDE4DocDir", 
               "UserStyleSheet", "WebSearchEngine", "HomePage", "PySideDocDir", 
               "DefaultScheme"]:
        return prefClass.settings.value("Help/" + key,
            QtCore.QVariant(prefClass.helpDefaults[key])).toString()
    elif key in ["AdBlockSubscriptions"]:
        return prefClass.settings.value("Help/" + key,
            QtCore.QVariant(prefClass.helpDefaults[key])).toStringList()
    elif key in ["StandardFont", "FixedFont"]:
        f = QtGui.QFont()
        f.fromString(prefClass.settings.value("Help/" + key,
            QtCore.QVariant(prefClass.helpDefaults[key])).toString())
        return f
    elif key in ["SaveUrlColor"]:
        col = prefClass.settings.value("Help/" + key)
        if col.isValid():
            return QtGui.QColor(col.toString())
        else:
            return prefClass.helpDefaults[key]
    elif key in ["HelpViewerState"]:
        return prefClass.settings.value("Help/" + key,
            QtCore.QVariant(prefClass.helpDefaults[key])).toByteArray()
    elif key in ["WebSearchKeywords"]:
        # return a list of tuples of (keyword, engine name)
        keywords = []
        size = prefClass.settings.beginReadArray("Help/" + key);
        for index in range(size):
            prefClass.settings.setArrayIndex(index)
            keyword = prefClass.settings.value("Keyword").toString()
            engineName = prefClass.settings.value("Engine").toString()
            keywords.append((keyword, engineName))
        prefClass.settings.endArray()
        return keywords
    else:
        # default is integer value
        return prefClass.settings.value("Help/" + key,
            QtCore.QVariant(prefClass.helpDefaults[key])).toInt()[0]
    
def setHelp(key, value, prefClass = Prefs):
    """
    Module function to store the various help settings.
    
    @param key the key of the setting to be set
    @param value the value to be set
    @param prefClass preferences class used as the storage area
    """
    if key in ["StandardFont", "FixedFont"]:
        prefClass.settings.setValue("Help/" + key,
            QtCore.QVariant(value.toString()))
    elif key == "SaveUrlColor":
        prefClass.settings.setValue("Help/" + key, QtCore.QVariant(value.name()))
    elif key == "WebSearchKeywords":
        # value is list of tuples of (keyword, engine name)
        prefClass.settings.beginWriteArray("Help/" + key, len(value))
        index = 0
        for v in value:
            prefClass.settings.setArrayIndex(index)
            prefClass.settings.setValue("Keyword", QtCore.QVariant(v[0]))
            prefClass.settings.setValue("Engine", QtCore.QVariant(v[1]))
            index += 1
        prefClass.settings.endArray()
    else:
        prefClass.settings.setValue("Help/" + key, QtCore.QVariant(value))
    
def getSystem(key, prefClass = Prefs):
    """
    Module function to retrieve the various system settings.
    
    @param key the key of the value to get
    @param prefClass preferences class used as the storage area
    @return the requested system setting
    """
    from Utilities import supportedCodecs
    if key in ["StringEncoding", "IOEncoding"]:
        encoding = unicode(prefClass.settings.value("System/" + key, 
            QtCore.QVariant(prefClass.sysDefaults[key])).toString())
        if encoding not in supportedCodecs:
            encoding = prefClass.sysDefaults[key]
        return encoding
    
def setSystem(key, value, prefClass = Prefs):
    """
    Module function to store the various system settings.
    
    @param key the key of the setting to be set
    @param value the value to be set
    @param prefClass preferences class used as the storage area
    """
    prefClass.settings.setValue("System/" + key, QtCore.QVariant(value))
    
def getQt4TranslationsDir(prefClass = Prefs):
    """
    Module function to retrieve the Qt4TranslationsDir setting.
    
    @param prefClass preferences class used as the storage area
    @return the requested Qt4TranslationsDir setting (string)
    """
    s = prefClass.settings.value("Qt/Qt4TranslationsDir", 
        QtCore.QVariant(prefClass.qtDefaults["Qt4TranslationsDir"])).toString()
    if s.isEmpty():
        return os.getenv("QT4TRANSLATIONSDIR", "")
    else:
        return unicode(s)
    
def getQt(key, prefClass = Prefs):
    """
    Module function to retrieve the various Qt settings.
    
    @param key the key of the value to get
    @param prefClass preferences class used as the storage area
    @return the requested Qt setting
    """
    if key == "Qt4TranslationsDir":
        return getQt4TranslationsDir(prefClass)
    elif key in ["QtToolsPrefix4", "QtToolsPostfix4"]: 
        return prefClass.settings.value("Qt/" + key, 
            QtCore.QVariant(prefClass.qtDefaults[key])).toString()
    elif key in ["Qt4Dir"]:
        return unicode(prefClass.settings.value("Qt/" + key, 
            QtCore.QVariant(prefClass.qtDefaults[key])).toString())
    else: 
        return prefClass.settings.value("Qt/" + key, 
            QtCore.QVariant(prefClass.qtDefaults[key])).toInt()[0]
    
def setQt(key, value, prefClass = Prefs):
    """
    Module function to store the various Qt settings.
    
    @param key the key of the setting to be set
    @param value the value to be set
    @param prefClass preferences class used as the storage area
    """
    prefClass.settings.setValue("Qt/" + key, QtCore.QVariant(value))
    
def getCorba(key, prefClass = Prefs):
    """
    Module function to retrieve the various corba settings.
    
    @param key the key of the value to get
    @param prefClass preferences class used as the storage area
    @return the requested corba setting
    """
    return prefClass.settings.value("Corba/" + key,
        QtCore.QVariant(prefClass.corbaDefaults[key])).toString()
    
def setCorba(key, value, prefClass = Prefs):
    """
    Module function to store the various corba settings.
    
    @param key the key of the setting to be set
    @param value the value to be set
    @param prefClass preferences class used as the storage area
    """
    prefClass.settings.setValue("Corba/" + key, QtCore.QVariant(value))
    
def getUser(key, prefClass = Prefs):
    """
    Module function to retrieve the various user settings.
    
    @param key the key of the value to get
    @param prefClass preferences class used as the storage area
    @return the requested user setting
    """
    if key in ["MailServerAuthentication", "MailServerUseTLS", 
               "MailServerPort", "UseSystemEmailClient"]:
        return prefClass.settings.value("User/" + key,
            QtCore.QVariant(prefClass.userDefaults[key])).toInt()[0]
    elif key == "MailServerPassword":
        from Utilities import pwDecode
        return pwDecode(prefClass.settings.value("User/" + key,
            QtCore.QVariant(prefClass.userDefaults[key])).toString())
    else:
        return prefClass.settings.value("User/" + key,
            QtCore.QVariant(prefClass.userDefaults[key])).toString()
    
def setUser(key, value, prefClass = Prefs):
    """
    Module function to store the various user settings.
    
    @param key the key of the setting to be set
    @param value the value to be set
    @param prefClass preferences class used as the storage area
    """
    if key == "MailServerPassword":
        from Utilities import pwEncode
        prefClass.settings.setValue(
            "User/" + key, QtCore.QVariant(pwEncode(value)))
    else:
        prefClass.settings.setValue("User/" + key, QtCore.QVariant(value))
    
def getVCS(key, prefClass = Prefs):
    """
    Module function to retrieve the VCS related settings.
    
    @param key the key of the value to get
    @param prefClass preferences class used as the storage area
    @return the requested user setting
    """
    return prefClass.settings.value("VCS/" + key,
        QtCore.QVariant(prefClass.vcsDefaults[key])).toInt()[0]
    
def setVCS(key, value, prefClass = Prefs):
    """
    Module function to store the VCS related settings.
    
    @param key the key of the setting to be set
    @param value the value to be set
    @param prefClass preferences class used as the storage area
    """
    prefClass.settings.setValue("VCS/" + key, QtCore.QVariant(value))
    
def getTasks(key, prefClass = Prefs):
    """
    Module function to retrieve the Tasks related settings.
    
    @param key the key of the value to get
    @param prefClass preferences class used as the storage area
    @return the requested user setting
    """
    if key in ["TasksColour", "TasksBugfixColour", 
               "TasksBgColour", "TasksProjectBgColour"]:
        col = prefClass.settings.value("Tasks/" + key)
        if col.isValid():
            return QtGui.QColor(col.toString())
        else:
            return prefClass.tasksDefaults[key]
    else:
        return prefClass.settings.value("Tasks/" + key,
            QtCore.QVariant(prefClass.tasksDefaults[key])).toString()
    
def setTasks(key, value, prefClass = Prefs):
    """
    Module function to store the Tasks related settings.
    
    @param key the key of the setting to be set
    @param value the value to be set
    @param prefClass preferences class used as the storage area
    """
    if key in ["TasksColour", "TasksBugfixColour",
               "TasksBgColour", "TasksProjectBgColour"]:
        prefClass.settings.setValue("Tasks/" + key, QtCore.QVariant(value.name()))
    else:
        prefClass.settings.setValue("Tasks/" + key, QtCore.QVariant(value))
    
def getTemplates(key, prefClass = Prefs):
    """
    Module function to retrieve the Templates related settings.
    
    @param key the key of the value to get
    @param prefClass preferences class used as the storage area
    @return the requested user setting
    """
    if key in ["SeparatorChar"]:
        return prefClass.settings.value("Templates/" + key,
            QtCore.QVariant(prefClass.templatesDefaults[key])).toString()
    else:
        return prefClass.settings.value("Templates/" + key,
            QtCore.QVariant(prefClass.templatesDefaults[key])).toInt()[0]
    
def setTemplates(key, value, prefClass = Prefs):
    """
    Module function to store the Templates related settings.
    
    @param key the key of the setting to be set
    @param value the value to be set
    @param prefClass preferences class used as the storage area
    """
    prefClass.settings.setValue("Templates/" + key, QtCore.QVariant(value))
    
def getPluginManager(key, prefClass = Prefs):
    """
    Module function to retrieve the plugin manager related settings.
    
    @param key the key of the value to get
    @param prefClass preferences class used as the storage area
    @return the requested user setting
    """
    if key in ["ActivateExternal"]:
        return prefClass.settings.value("PluginManager/" + key,
            QtCore.QVariant(prefClass.pluginManagerDefaults[key])).toInt()[0]
    else:
        return prefClass.settings.value("PluginManager/" + key,
            QtCore.QVariant(prefClass.pluginManagerDefaults[key])).toString()
    
def setPluginManager(key, value, prefClass = Prefs):
    """
    Module function to store the plugin manager related settings.
    
    @param key the key of the setting to be set
    @param value the value to be set
    @param prefClass preferences class used as the storage area
    """
    prefClass.settings.setValue("PluginManager/" + key, QtCore.QVariant(value))
    
def getGraphics(key, prefClass = Prefs):
    """
    Module function to retrieve the Graphics related settings.
    
    @param key the key of the value to get
    @param prefClass preferences class used as the storage area
    @return the requested user setting
    """
    if key in ["Font"]:
        f = QtGui.QFont()
        f.fromString(prefClass.settings.value("Graphics/" + key,
            QtCore.QVariant(prefClass.graphicsDefaults[key])).toString())
        return f
    else:
        return prefClass.settings.value("Graphics/" + key,
            QtCore.QVariant(prefClass.graphicsDefaults[key])).toString()
    
def setGraphics(key, value, prefClass = Prefs):
    """
    Module function to store the Graphics related settings.
    
    @param key the key of the setting to be set
    @param value the value to be set
    @param prefClass preferences class used as the storage area
    """
    if key in ["Font"]:
        prefClass.settings.setValue("Graphics/" + key, QtCore.QVariant(value.toString()))
    else:
        prefClass.settings.setValue("Graphics/" + key, QtCore.QVariant(value))
    
def getIconEditor(key, prefClass = Prefs):
    """
    Module function to retrieve the Icon Editor related settings.
    
    @param key the key of the value to get
    @param prefClass preferences class used as the storage area
    @return the requested user setting
    """
    if key in ["IconEditorState"]:
        return prefClass.settings.value("IconEditor/" + key,
            QtCore.QVariant(prefClass.iconEditorDefaults[key])).toByteArray()
    else:
        return prefClass.settings.value("IconEditor/" + key,
            QtCore.QVariant(prefClass.iconEditorDefaults[key])).toString()
    
def setIconEditor(key, value, prefClass = Prefs):
    """
    Module function to store the Icon Editor related settings.
    
    @param key the key of the setting to be set
    @param value the value to be set
    @param prefClass preferences class used as the storage area
    """
    prefClass.settings.setValue("IconEditor/" + key, QtCore.QVariant(value))
    
def getGeometry(key, prefClass = Prefs):
    """
    Module function to retrieve the display geometry.
    
    @param key the key of the value to get
    @param prefClass preferences class used as the storage area
    @return the requested geometry setting
    """
    if key in ["MainMaximized"]:
        return prefClass.settings.value("Geometry/" + key,
            QtCore.QVariant(prefClass.geometryDefaults[key])).toInt()[0]
    else:
        v = prefClass.settings.value("Geometry/" + key)
        if v.isValid():
            return v.toByteArray()
        else:
            return prefClass.geometryDefaults[key]

def setGeometry(key, value, prefClass = Prefs):
    """
    Module function to store the display geometry.
    
    @param key the key of the setting to be set
    @param value the geometry to be set
    @param prefClass preferences class used as the storage area
    """
    if key in ["MainMaximized"]:
        prefClass.settings.setValue("Geometry/" + key, QtCore.QVariant(value))
    else:
        if prefClass.resetLayout:
            v = prefClass.geometryDefaults[key]
        else:
            v = value
        prefClass.settings.setValue("Geometry/" + key, QtCore.QVariant(v))

def resetLayout(prefClass = Prefs):
    """
    Module function to set a flag not storing the current layout.
    
    @param prefClass preferences class used as the storage area
    """
    prefClass.resetLayout = True

def shouldResetLayout(prefClass = Prefs):
    """
    Module function to indicate a reset of the layout.
    
    @param prefClass preferences class used as the storage area
    @return flag indicating a reset of the layout (boolean)
    """
    return prefClass.resetLayout
    
def saveResetLayout(prefClass = Prefs):
    """
    Module function to save the reset layout.
    """
    if prefClass.resetLayout:
        for key in prefClass.geometryDefaults.keys():
            prefClass.settings.setValue("Geometry/" + key, 
                QtCore.QVariant(prefClass.geometryDefaults[key]))
    
initPreferences()
initRecentSettings()
