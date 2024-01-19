# -*- coding: utf-8 -*-

# Copyright (c) 2006 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the Editor Properties configuration page.
"""

from PyQt4.Qsci import QsciScintilla

from QScintilla.QsciScintillaCompat import QSCINTILLA_VERSION

from ConfigurationPageBase import ConfigurationPageBase
from Ui_EditorPropertiesPage import Ui_EditorPropertiesPage

import Preferences

class EditorPropertiesPage(ConfigurationPageBase, Ui_EditorPropertiesPage):
    """
    Class implementing the Editor Properties configuration page.
    """
    def __init__(self, lexers):
        """
        Constructor
        
        @param lexers reference to the lexers dictionary
        """
        ConfigurationPageBase.__init__(self)
        self.setupUi(self)
        self.setObjectName("EditorPropertiesPage")
        
        self.languages = sorted(lexers.keys()[:])
        
        # set initial values
        # All
        self.allFoldCompactCheckBox.setChecked(\
            Preferences.getEditor("AllFoldCompact"))
        
        # Bash
        self.foldBashCommentCheckBox.setChecked(\
            Preferences.getEditor("BashFoldComment"))
        
        # CMake
        self.cmakeFoldAtElseCheckBox.setChecked(\
            Preferences.getEditor("CMakeFoldAtElse"))
        
        # C++
        self.foldCppCommentCheckBox.setChecked(\
            Preferences.getEditor("CppFoldComment"))
        self.foldCppPreprocessorCheckBox.setChecked(\
            Preferences.getEditor("CppFoldPreprocessor"))
        self.foldCppAtElseCheckBox.setChecked(\
            Preferences.getEditor("CppFoldAtElse"))
        self.cppIndentOpeningBraceCheckBox.setChecked(\
            Preferences.getEditor("CppIndentOpeningBrace"))
        self.cppIndentClosingBraceCheckBox.setChecked(\
            Preferences.getEditor("CppIndentClosingBrace"))
        self.cppCaseInsensitiveCheckBox.setChecked(\
            Preferences.getEditor("CppCaseInsensitiveKeywords"))
        if QSCINTILLA_VERSION() >= 0x020400:
            self.cppDollarAllowedCheckBox.setChecked(
                Preferences.getEditor("CppDollarsAllowed"))
        else:
            self.cppDollarAllowedCheckBox.setEnabled(False)
        
        # CSS
        self.foldCssCommentCheckBox.setChecked(\
            Preferences.getEditor("CssFoldComment"))
        
        # D
        self.foldDCommentCheckBox.setChecked(\
            Preferences.getEditor("DFoldComment"))
        self.foldDAtElseCheckBox.setChecked(\
            Preferences.getEditor("DFoldAtElse"))
        self.dIndentOpeningBraceCheckBox.setChecked(\
            Preferences.getEditor("DIndentOpeningBrace"))
        self.dIndentClosingBraceCheckBox.setChecked(\
            Preferences.getEditor("DIndentClosingBrace"))
        
        # HTML
        self.foldHtmlPreprocessorCheckBox.setChecked(\
            Preferences.getEditor("HtmlFoldPreprocessor"))
        self.htmlCaseSensitiveTagsCheckBox.setChecked(\
            Preferences.getEditor("HtmlCaseSensitiveTags"))
        if QSCINTILLA_VERSION() >= 0x020400:
            self.foldHtmlScriptCommentsCheckBox.setChecked(
                Preferences.getEditor("HtmlFoldScriptComments"))
            self.foldHtmlScriptHereDocsCheckBox.setChecked(
                Preferences.getEditor("HtmlFoldScriptHeredocs"))
        else:
            self.foldHtmlScriptCommentsCheckBox.setEnabled(False)
            self.foldHtmlScriptHereDocsCheckBox.setEnabled(False)
        
        # Pascal
        if "Pascal" in self.languages:
            self.pascalGroup.setEnabled(True)
            self.foldPascalCommentCheckBox.setChecked(\
                Preferences.getEditor("PascalFoldComment"))
            self.foldPascalPreprocessorCheckBox.setChecked(\
                Preferences.getEditor("PascalFoldPreprocessor"))
            if QSCINTILLA_VERSION() >= 0x020400:
                self.pascalSmartHighlightingCheckBox.setChecked(
                    Preferences.getEditor("PascalSmartHighlighting"))
            else:
                self.pascalSmartHighlightingCheckBox.setEnabled(False)
        else:
            self.pascalGroup.setEnabled(False)
        
        # Perl
        self.foldPerlCommentCheckBox.setChecked(\
            Preferences.getEditor("PerlFoldComment"))
        if QSCINTILLA_VERSION() >= 0x020400:
            self.foldPerlPackagesCheckBox.setChecked(
                Preferences.getEditor("PerlFoldPackages"))
            self.foldPerlPODBlocksCheckBox.setChecked(
                Preferences.getEditor("PerlFoldPODBlocks"))
        else:
            self.foldPerlPackagesCheckBox.setEnabled(False)
            self.foldPerlPODBlocksCheckBox.setEnabled(False)
        
        # PostScript
        if "PostScript" in self.languages:
            self.postscriptGroup.setEnabled(True)
            self.psFoldAtElseCheckBox.setChecked(\
                Preferences.getEditor("PostScriptFoldAtElse"))
            self.psMarkTokensCheckBox.setChecked(\
                Preferences.getEditor("PostScriptTokenize"))
            self.psLevelSpinBox.setValue(\
                Preferences.getEditor("PostScriptLevel"))
        else:
            self.postscriptGroup.setEnabled(False)
        
        # Povray
        self.foldPovrayCommentCheckBox.setChecked(\
            Preferences.getEditor("PovFoldComment"))
        self.foldPovrayDirectivesCheckBox.setChecked(\
            Preferences.getEditor("PovFoldDirectives"))
        
        # Python
        self.foldPythonCommentCheckBox.setChecked(\
            Preferences.getEditor("PythonFoldComment"))
        self.foldPythonStringCheckBox.setChecked(\
            Preferences.getEditor("PythonFoldString"))
        self.pythonBadIndentationCheckBox.setChecked(\
            Preferences.getEditor("PythonBadIndentation"))
        self.pythonAutoindentCheckBox.setChecked(\
            Preferences.getEditor("PythonAutoIndent"))
        if QSCINTILLA_VERSION() >= 0x020400:
            self.pythonV2UnicodeAllowedCheckBox.setChecked(
                Preferences.getEditor("PythonAllowV2Unicode"))
            self.pythonV3BinaryAllowedCheckBox.setChecked(
                Preferences.getEditor("PythonAllowV3Binary"))
            self.pythonV3BytesAllowedCheckBox.setChecked(
                Preferences.getEditor("PythonAllowV3Bytes"))
        else:
            self.pythonV2UnicodeAllowedCheckBox.setEnabled(False)
            self.pythonV3BinaryAllowedCheckBox.setEnabled(False)
            self.pythonV3BytesAllowedCheckBox.setEnabled(False)
        
        # SQL
        self.foldSqlCommentCheckBox.setChecked(\
            Preferences.getEditor("SqlFoldComment"))
        self.sqlBackslashEscapesCheckBox.setChecked(\
            Preferences.getEditor("SqlBackslashEscapes"))
        
        # VHDL
        self.vhdlFoldCommentCheckBox.setChecked(\
            Preferences.getEditor("VHDLFoldComment"))
        self.vhdlFoldAtElseCheckBox.setChecked(\
            Preferences.getEditor("VHDLFoldAtElse"))
        self.vhdlFoldAtBeginCheckBox.setChecked(\
            Preferences.getEditor("VHDLFoldAtBegin"))
        self.vhdlFoldAtParenthesisCheckBox.setChecked(\
            Preferences.getEditor("VHDLFoldAtParenthesis"))
        
        # XML
        if QSCINTILLA_VERSION() >= 0x020400:
            self.xmlSyleScriptsCheckBox.setChecked(
                Preferences.getEditor("XMLStyleScripts"))
        else:
            self.xmlGroup.setEnabled(False)
        
        # YAML
        if "YAML" in self.languages:
            self.yamlGroup.setEnabled(True)
            self.foldYamlCommentCheckBox.setChecked(\
                Preferences.getEditor("YAMLFoldComment"))
        else:
            self.yamlGroup.setEnabled(False)
        
    def save(self):
        """
        Public slot to save the Editor Properties (1) configuration.
        """
        # All
        Preferences.setEditor("AllFoldCompact",
            int(self.allFoldCompactCheckBox.isChecked()))
        
        # Bash
        Preferences.setEditor("BashFoldComment",
            int(self.foldBashCommentCheckBox.isChecked()))
        
        # CMake
        Preferences.setEditor("CMakeFoldAtElse",
            int(self.cmakeFoldAtElseCheckBox.isChecked()))
        
        # C++
        Preferences.setEditor("CppFoldComment",
            int(self.foldCppCommentCheckBox.isChecked()))
        Preferences.setEditor("CppFoldPreprocessor",
            int(self.foldCppPreprocessorCheckBox.isChecked()))
        Preferences.setEditor("CppFoldAtElse",
            int(self.foldCppAtElseCheckBox.isChecked()))
        Preferences.setEditor("CppIndentOpeningBrace",
            int(self.cppIndentOpeningBraceCheckBox.isChecked()))
        Preferences.setEditor("CppIndentClosingBrace",
            int(self.cppIndentClosingBraceCheckBox.isChecked()))
        Preferences.setEditor("CppCaseInsensitiveKeywords",
            int(self.cppCaseInsensitiveCheckBox.isChecked()))
        if QSCINTILLA_VERSION() >= 0x020400:
            Preferences.setEditor("CppDollarsAllowed",
                int(self.cppDollarAllowedCheckBox.isChecked()))
        
        # CSS
        Preferences.setEditor("CssFoldComment",
            int(self.foldCssCommentCheckBox.isChecked()))
        
        # D
        Preferences.setEditor("DFoldComment",
            int(self.foldDCommentCheckBox.isChecked()))
        Preferences.setEditor("DFoldAtElse",
            int(self.foldDAtElseCheckBox.isChecked()))
        Preferences.setEditor("DIndentOpeningBrace",
            int(self.dIndentOpeningBraceCheckBox.isChecked()))
        Preferences.setEditor("DIndentClosingBrace",
            int(self.dIndentClosingBraceCheckBox.isChecked()))
        
        # HTML
        Preferences.setEditor("HtmlFoldPreprocessor",
            int(self.foldHtmlPreprocessorCheckBox.isChecked()))
        Preferences.setEditor("HtmlCaseSensitiveTags",
            int(self.htmlCaseSensitiveTagsCheckBox.isChecked()))
        if QSCINTILLA_VERSION() >= 0x020400:
            Preferences.setEditor("HtmlFoldScriptComments",
                int(self.foldHtmlScriptCommentsCheckBox.isChecked()))
            Preferences.setEditor("HtmlFoldScriptHeredocs",
                int(self.foldHtmlScriptHereDocsCheckBox.isChecked()))
        
        # Pascal
        if "Pascal" in self.languages:
            Preferences.setEditor("PascalFoldComment",
                int(self.foldPascalCommentCheckBox.isChecked()))
            Preferences.setEditor("PascalFoldPreprocessor",
                int(self.foldPascalPreprocessorCheckBox.isChecked()))
            if QSCINTILLA_VERSION() >= 0x020400:
                Preferences.setEditor("PascalSmartHighlighting",
                    int(self.pascalSmartHighlightingCheckBox.isChecked()))
        
        # Perl
        Preferences.setEditor("PerlFoldComment",
            int(self.foldPerlCommentCheckBox.isChecked()))
        if QSCINTILLA_VERSION() >= 0x020400:
            Preferences.setEditor("PerlFoldPackages",
                int(self.foldPerlPackagesCheckBox.isChecked()))
            Preferences.setEditor("PerlFoldPODBlocks",
                int(self.foldPerlPODBlocksCheckBox.isChecked()))
        
        # PostScript
        if "PostScript" in self.languages:
            Preferences.setEditor("PostScriptFoldAtElse",
                int(self.psFoldAtElseCheckBox.isChecked()))
            Preferences.setEditor("PostScriptTokenize",
                int(self.psMarkTokensCheckBox.isChecked()))
            Preferences.setEditor("PostScriptLevel", 
                self.psLevelSpinBox.value())
        
        # Povray
        Preferences.setEditor("PovFoldComment",
            int(self.foldPovrayCommentCheckBox.isChecked()))
        Preferences.setEditor("PovFoldDirectives",
            int(self.foldPovrayDirectivesCheckBox.isChecked()))
        
        # Python
        Preferences.setEditor("PythonFoldComment",
            int(self.foldPythonCommentCheckBox.isChecked()))
        Preferences.setEditor("PythonFoldString",
            int(self.foldPythonStringCheckBox.isChecked()))
        Preferences.setEditor("PythonBadIndentation",
            int(self.pythonBadIndentationCheckBox.isChecked()))
        Preferences.setEditor("PythonAutoIndent",
            int(self.pythonAutoindentCheckBox.isChecked()))
        if QSCINTILLA_VERSION() >= 0x020400:
            Preferences.setEditor("PythonAllowV2Unicode",
                int(self.pythonV2UnicodeAllowedCheckBox.isChecked()))
            Preferences.setEditor("PythonAllowV3Binary",
                int(self.pythonV3BinaryAllowedCheckBox.isChecked()))
            Preferences.setEditor("PythonAllowV3Bytes",
                int(self.pythonV3BytesAllowedCheckBox.isChecked()))
        
        # SQL
        Preferences.setEditor("SqlFoldComment",
            int(self.foldSqlCommentCheckBox.isChecked()))
        Preferences.setEditor("SqlBackslashEscapes",
            int(self.sqlBackslashEscapesCheckBox.isChecked()))
        
        # VHDL
        Preferences.setEditor("VHDLFoldComment",
            int(self.vhdlFoldCommentCheckBox.isChecked()))
        Preferences.setEditor("VHDLFoldAtElse",
            int(self.vhdlFoldAtElseCheckBox.isChecked()))
        Preferences.setEditor("VHDLFoldAtBegin",
            int(self.vhdlFoldAtBeginCheckBox.isChecked()))
        Preferences.setEditor("VHDLFoldAtParenthesis",
            int(self.vhdlFoldAtParenthesisCheckBox.isChecked()))
        
        # XML
        if QSCINTILLA_VERSION() >= 0x020400:
            Preferences.setEditor("XMLStyleScripts",
                int(self.xmlSyleScriptsCheckBox.isChecked()))
        
        # YAML
        if "YAML" in self.languages:
            Preferences.setEditor("YAMLFoldComment", 
                int(self.foldYamlCommentCheckBox.isChecked()))

def create(dlg):
    """
    Module function to create the configuration page.
    
    @param dlg reference to the configuration dialog
    """
    page = EditorPropertiesPage(dlg.getLexers())
    return page
