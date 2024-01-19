# -*- coding: utf-8 -*-

# Copyright (c) 2006 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the Editor Styles configuration page.
"""

from PyQt4.QtCore import pyqtSignature
from PyQt4.QtGui import QPixmap, QIcon
from PyQt4.Qsci import QsciScintilla

from QScintilla.QsciScintillaCompat import QSCINTILLA_VERSION

from ConfigurationPageBase import ConfigurationPageBase
from Ui_EditorStylesPage import Ui_EditorStylesPage

import Preferences

class EditorStylesPage(ConfigurationPageBase, Ui_EditorStylesPage):
    """
    Class implementing the Editor Styles configuration page.
    """
    def __init__(self):
        """
        Constructor
        """
        ConfigurationPageBase.__init__(self)
        self.setupUi(self)
        self.setObjectName("EditorStylesPage")
        
        self.foldStyles = [
            QsciScintilla.PlainFoldStyle,
            QsciScintilla.CircledFoldStyle,
            QsciScintilla.BoxedFoldStyle,
            QsciScintilla.CircledTreeFoldStyle,
            QsciScintilla.BoxedTreeFoldStyle
        ]
        
        self.edgeModes = [
            QsciScintilla.EdgeNone,
            QsciScintilla.EdgeLine,
            QsciScintilla.EdgeBackground
        ]
        
        self.editorColours = {}
        
        # set initial values
        try:
            self.foldingStyleComboBox.setCurrentIndex(
                self.foldStyles.index(Preferences.getEditor("FoldingStyle")))
        except ValueError:
            self.foldingStyleComboBox.setCurrentIndex(0)
        self.marginsFont = Preferences.getEditorOtherFonts("MarginsFont")
        self.marginsFontSample.setFont(self.marginsFont)
        self.defaultFont = Preferences.getEditorOtherFonts("DefaultFont")
        self.defaultFontSample.setFont(self.defaultFont)
        self.monospacedFont = Preferences.getEditorOtherFonts("MonospacedFont")
        self.monospacedFontSample.setFont(self.monospacedFont)
        self.monospacedCheckBox.setChecked(\
            Preferences.getEditor("UseMonospacedFont"))
        self.linenowidthSlider.setValue(\
            Preferences.getEditor("LinenoWidth"))
        self.linenoCheckBox.setChecked(\
            Preferences.getEditor("LinenoMargin"))
        self.foldingCheckBox.setChecked(\
            Preferences.getEditor("FoldingMargin"))
        if QSCINTILLA_VERSION() >= 0x020301:
            self.unifiedMarginsCheckBox.setChecked(\
                Preferences.getEditor("UnifiedMargins"))
        else:
            self.unifiedMarginsCheckBox.setEnabled(False)
            self.unifiedMarginsCheckBox.setChecked(True)
        
        self.caretlineVisibleCheckBox.setChecked(\
            Preferences.getEditor("CaretLineVisible"))
        self.caretWidthSpinBox.setValue(\
            Preferences.getEditor("CaretWidth"))
        self.colourizeSelTextCheckBox.setChecked(\
            Preferences.getEditor("ColourizeSelText"))
        self.customSelColourCheckBox.setChecked(\
            Preferences.getEditor("CustomSelectionColours"))
        self.extentSelEolCheckBox.setChecked(\
            Preferences.getEditor("ExtendSelectionToEol"))
        
        self.editorColours["CaretForeground"] = \
            self.initColour("CaretForeground", self.caretForegroundButton, 
                Preferences.getEditorColour)
        self.editorColours["CaretLineBackground"] = \
            self.initColour("CaretLineBackground", self.caretlineBackgroundButton, 
                Preferences.getEditorColour)
        self.editorColours["SelectionForeground"] = \
            self.initColour("SelectionForeground", self.selectionForegroundButton, 
                Preferences.getEditorColour)
        self.editorColours["SelectionBackground"] = \
            self.initColour("SelectionBackground", self.selectionBackgroundButton, 
                Preferences.getEditorColour)
        self.editorColours["CurrentMarker"] = \
            self.initColour("CurrentMarker", self.currentLineMarkerButton, 
                Preferences.getEditorColour)
        self.editorColours["ErrorMarker"] = \
            self.initColour("ErrorMarker", self.errorMarkerButton, 
                Preferences.getEditorColour)
        self.editorColours["MarginsForeground"] = \
            self.initColour("MarginsForeground", self.marginsForegroundButton, 
                Preferences.getEditorColour)
        self.editorColours["MarginsBackground"] = \
            self.initColour("MarginsBackground", self.marginsBackgroundButton, 
                Preferences.getEditorColour)
        self.editorColours["FoldmarginBackground"] = \
            self.initColour("FoldmarginBackground", self.foldmarginBackgroundButton, 
                Preferences.getEditorColour)
        
        self.eolCheckBox.setChecked(Preferences.getEditor("ShowEOL"))
        self.wrapLongLinesCheckBox.setChecked(\
            Preferences.getEditor("WrapLongLines"))
        
        self.edgeModeCombo.setCurrentIndex(
            self.edgeModes.index(Preferences.getEditor("EdgeMode")))
        self.edgeLineColumnSlider.setValue(\
            Preferences.getEditor("EdgeColumn"))
        self.editorColours["Edge"] = \
            self.initColour("Edge", self.edgeBackgroundColorButton, 
                Preferences.getEditorColour)
        
        self.bracehighlightingCheckBox.setChecked(\
            Preferences.getEditor("BraceHighlighting"))
        self.editorColours["MatchingBrace"] = \
            self.initColour("MatchingBrace", self.matchingBracesButton, 
                Preferences.getEditorColour)
        self.editorColours["MatchingBraceBack"] = \
            self.initColour("MatchingBraceBack", self.matchingBracesBackButton, 
                Preferences.getEditorColour)
        self.editorColours["NonmatchingBrace"] = \
            self.initColour("NonmatchingBrace", self.nonmatchingBracesButton, 
                Preferences.getEditorColour)
        self.editorColours["NonmatchingBraceBack"] = \
            self.initColour("NonmatchingBraceBack", self.nonmatchingBracesBackButton, 
                Preferences.getEditorColour)
        
        self.whitespaceCheckBox.setChecked(\
            Preferences.getEditor("ShowWhitespace"))
        self.miniMenuCheckBox.setChecked(\
            Preferences.getEditor("MiniContextMenu"))
        
    def save(self):
        """
        Public slot to save the Editor Styles configuration.
        """
        Preferences.setEditor("FoldingStyle",
            self.foldStyles[self.foldingStyleComboBox.currentIndex()])
        Preferences.setEditorOtherFonts("MarginsFont", self.marginsFont)
        Preferences.setEditorOtherFonts("DefaultFont", self.defaultFont)
        Preferences.setEditorOtherFonts("MonospacedFont", self.monospacedFont)
        Preferences.setEditor("UseMonospacedFont",
            int(self.monospacedCheckBox.isChecked()))
        
        Preferences.setEditor("LinenoWidth", 
            self.linenowidthSlider.value())
        Preferences.setEditor("LinenoMargin", 
            int(self.linenoCheckBox.isChecked()))
        Preferences.setEditor("FoldingMargin", 
            int(self.foldingCheckBox.isChecked()))
        if QSCINTILLA_VERSION() >= 0x020301:
            Preferences.setEditor("UnifiedMargins", 
                int(self.unifiedMarginsCheckBox.isChecked()))
        
        Preferences.setEditor("CaretLineVisible",
            int(self.caretlineVisibleCheckBox.isChecked()))
        Preferences.setEditor("ColourizeSelText",
            int(self.colourizeSelTextCheckBox.isChecked()))
        Preferences.setEditor("CustomSelectionColours", 
            int(self.customSelColourCheckBox.isChecked()))
        Preferences.setEditor("ExtendSelectionToEol", 
            int(self.extentSelEolCheckBox.isChecked()))
        
        Preferences.setEditor("CaretWidth", 
            self.caretWidthSpinBox.value())
        
        Preferences.setEditor("ShowEOL", 
            int(self.eolCheckBox.isChecked()))
        Preferences.setEditor("WrapLongLines",
            int(self.wrapLongLinesCheckBox.isChecked()))
        Preferences.setEditor("EdgeMode",
            self.edgeModes[self.edgeModeCombo.currentIndex()])
        Preferences.setEditor("EdgeColumn",
            self.edgeLineColumnSlider.value())
        
        Preferences.setEditor("BraceHighlighting",
            int(self.bracehighlightingCheckBox.isChecked()))
        
        Preferences.setEditor("ShowWhitespace", 
            int(self.whitespaceCheckBox.isChecked()))
        Preferences.setEditor("MiniContextMenu",
            int(self.miniMenuCheckBox.isChecked()))
        
        for key in self.editorColours.keys():
            Preferences.setEditorColour(key, self.editorColours[key])
        
    @pyqtSignature("")
    def on_linenumbersFontButton_clicked(self):
        """
        Private method used to select the font for the editor margins.
        """
        self.marginsFont = self.selectFont(self.marginsFontSample, self.marginsFont)
        
    @pyqtSignature("")
    def on_defaultFontButton_clicked(self):
        """
        Private method used to select the default font for the editor.
        """
        self.defaultFont = self.selectFont(self.defaultFontSample, self.defaultFont)
        
    @pyqtSignature("")
    def on_monospacedFontButton_clicked(self):
        """
        Private method used to select the font to be used as the monospaced font.
        """
        self.monospacedFont = \
            self.selectFont(self.monospacedFontSample, self.monospacedFont)
        
    @pyqtSignature("")
    def on_caretForegroundButton_clicked(self):
        """
        Private slot to set the foreground colour of the caret.
        """
        self.editorColours["CaretForeground"] = \
            self.selectColour(self.caretForegroundButton, 
                self.editorColours["CaretForeground"])
        
    @pyqtSignature("")
    def on_caretlineBackgroundButton_clicked(self):
        """
        Private slot to set the background colour of the caretline.
        """
        self.editorColours["CaretLineBackground"] = \
            self.selectColour(self.caretlineBackgroundButton, 
                self.editorColours["CaretLineBackground"])
        
    @pyqtSignature("")
    def on_selectionForegroundButton_clicked(self):
        """
        Private slot to set the foreground colour of the selection.
        """
        self.editorColours["SelectionForeground"] = \
            self.selectColour(self.selectionForegroundButton, 
                self.editorColours["SelectionForeground"])
        
    @pyqtSignature("")
    def on_selectionBackgroundButton_clicked(self):
        """
        Private slot to set the background colour of the selection.
        """
        self.editorColours["SelectionBackground"] = \
            self.selectColour(self.selectionBackgroundButton, 
                self.editorColours["SelectionBackground"])
        
    @pyqtSignature("")
    def on_currentLineMarkerButton_clicked(self):
        """
        Private slot to set the colour for the highlight of the current line.
        """
        self.editorColours["CurrentMarker"] = \
            self.selectColour(self.currentLineMarkerButton, 
                self.editorColours["CurrentMarker"])
        
    @pyqtSignature("")
    def on_errorMarkerButton_clicked(self):
        """
        Private slot to set the colour for the highlight of the error line.
        """
        self.editorColours["ErrorMarker"] = \
            self.selectColour(self.errorMarkerButton, 
                self.editorColours["ErrorMarker"])
        
    @pyqtSignature("")
    def on_marginsForegroundButton_clicked(self):
        """
        Private slot to set the foreground colour for the margins.
        """
        self.editorColours["MarginsForeground"] = \
            self.selectColour(self.marginsForegroundButton, 
                self.editorColours["MarginsForeground"])
        
    @pyqtSignature("")
    def on_marginsBackgroundButton_clicked(self):
        """
        Private slot to set the background colour for the margins.
        """
        self.editorColours["MarginsBackground"] = \
            self.selectColour(self.marginsBackgroundButton, 
                self.editorColours["MarginsBackground"])
        
    @pyqtSignature("")
    def on_foldmarginBackgroundButton_clicked(self):
        """
        Private slot to set the background colour for the foldmargin.
        """
        self.editorColours["FoldmarginBackground"] = \
            self.selectColour(self.foldmarginBackgroundButton, 
                self.editorColours["FoldmarginBackground"])
        
    @pyqtSignature("")
    def on_edgeBackgroundColorButton_clicked(self):
        """
        Private slot to set the colour for the edge background or line.
        """
        self.editorColours["Edge"] = \
            self.selectColour(self.edgeBackgroundColorButton, self.editorColours["Edge"])
        
    @pyqtSignature("")
    def on_matchingBracesButton_clicked(self):
        """
        Private slot to set the colour for highlighting matching braces.
        """
        self.editorColours["MatchingBrace"] = \
            self.selectColour(self.matchingBracesButton, 
                self.editorColours["MatchingBrace"])
        
    @pyqtSignature("")
    def on_matchingBracesBackButton_clicked(self):
        """
        Private slot to set the background colour for highlighting matching braces.
        """
        self.editorColours["MatchingBraceBack"] = \
            self.selectColour(self.matchingBracesBackButton, 
                self.editorColours["MatchingBraceBack"])
        
    @pyqtSignature("")
    def on_nonmatchingBracesButton_clicked(self):
        """
        Private slot to set the colour for highlighting nonmatching braces.
        """
        self.editorColours["NonmatchingBrace"] = \
            self.selectColour(self.nonmatchingBracesButton, 
                self.editorColours["NonmatchingBrace"])
        
    @pyqtSignature("")
    def on_nonmatchingBracesBackButton_clicked(self):
        """
        Private slot to set the background colour for highlighting nonmatching braces.
        """
        self.editorColours["NonmatchingBraceBack"] = \
            self.selectColour(self.nonmatchingBracesBackButton, 
                self.editorColours["NonmatchingBraceBack"])
        
    def polishPage(self):
        """
        Public slot to perform some polishing actions.
        """
        self.marginsFontSample.setFont(self.marginsFont)
        self.defaultFontSample.setFont(self.defaultFont)
        self.monospacedFontSample.setFont(self.monospacedFont)

def create(dlg):
    """
    Module function to create the configuration page.
    
    @param dlg reference to the configuration dialog
    """
    page = EditorStylesPage()
    return page
