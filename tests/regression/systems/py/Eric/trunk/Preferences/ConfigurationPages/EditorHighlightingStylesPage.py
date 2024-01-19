# -*- coding: utf-8 -*-

# Copyright (c) 2006 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the Editor Highlighting Styles configuration page.
"""

import os

from PyQt4.QtCore import QString, QStringList, pyqtSignature, QFileInfo
from PyQt4.QtGui import QPalette, QFileDialog

from KdeQt import KQColorDialog, KQFontDialog, KQInputDialog, KQFileDialog, KQMessageBox

from ConfigurationPageBase import ConfigurationPageBase
from Ui_EditorHighlightingStylesPage import Ui_EditorHighlightingStylesPage

from E4XML.XMLUtilities import make_parser
from E4XML.XMLErrorHandler import XMLErrorHandler, XMLFatalParseError
from E4XML.XMLEntityResolver import XMLEntityResolver
from E4XML.HighlightingStylesWriter import HighlightingStylesWriter
from E4XML.HighlightingStylesHandler import HighlightingStylesHandler

import Preferences

class EditorHighlightingStylesPage(ConfigurationPageBase, Ui_EditorHighlightingStylesPage):
    """
    Class implementing the Editor Highlighting Styles configuration page.
    """
    def __init__(self, lexers):
        """
        Constructor
        
        @param lexers reference to the lexers dictionary
        """
        ConfigurationPageBase.__init__(self)
        self.setupUi(self)
        self.setObjectName("EditorHighlightingStylesPage")
        
        self.lexer = None
        self.lexers = lexers
        
        # set initial values
        languages = [''] + self.lexers.keys()
        languages.sort()
        for lang in languages:
            self.lexerLanguageComboBox.addItem(lang)
        self.on_lexerLanguageComboBox_activated(QString(''))
        
    def save(self):
        """
        Public slot to save the Editor Highlighting Styles configuration.
        """
        for lexer in self.lexers.values():
            lexer.writeSettings(Preferences.Prefs.settings, "Scintilla")
        
    @pyqtSignature("QString")
    def on_lexerLanguageComboBox_activated(self, language):
        """
        Private slot to fill the style combo of the source page.
        
        @param language The lexer language (string or QString)
        """
        self.styleElementList.clear()
        self.styleGroup.setEnabled(False)
        self.lexer = None
        
        self.exportCurrentButton.setEnabled(not language.isEmpty())
        self.importCurrentButton.setEnabled(not language.isEmpty())
        
        if language.isEmpty():
            return
        
        try:
            self.lexer = self.lexers[unicode(language)]
        except KeyError:
            return
        
        self.styleGroup.setEnabled(True)
        self.styleElementList.addItems(self.lexer.styles)
        self.styleElementList.setCurrentRow(0)
        
    def on_styleElementList_currentRowChanged(self, index):
        """
        Private method to set up the style element part of the source page.
        
        @param index the style index.
        """
        try:
            self.style = self.lexer.ind2style[index]
        except KeyError:
            return
        
        colour = self.lexer.color(self.style)
        paper = self.lexer.paper(self.style)
        eolfill = self.lexer.eolFill(self.style)
        font = self.lexer.font(self.style)
        
        self.sampleText.setFont(font)
        pl = self.sampleText.palette()
        pl.setColor(QPalette.Text, colour)
        pl.setColor(QPalette.Base, paper)
        self.sampleText.setPalette(pl)
        self.sampleText.repaint()
        self.eolfillCheckBox.setChecked(eolfill)
        
    @pyqtSignature("")
    def on_foregroundButton_clicked(self):
        """
        Private method used to select the foreground colour of the selected style 
        and lexer.
        """
        colour = KQColorDialog.getColor(self.lexer.color(self.style))
        if colour.isValid():
            pl = self.sampleText.palette()
            pl.setColor(QPalette.Text, colour)
            self.sampleText.setPalette(pl)
            self.sampleText.repaint()
            if len(self.styleElementList.selectedItems()) > 1:
                for selItem in self.styleElementList.selectedItems():
                    style = self.lexer.ind2style[self.styleElementList.row(selItem)]
                    self.lexer.setColor(colour, style)
            else:
                self.lexer.setColor(colour, self.style)
        
    @pyqtSignature("")
    def on_backgroundButton_clicked(self):
        """
        Private method used to select the background colour of the selected style 
        and lexer.
        """
        colour = KQColorDialog.getColor(self.lexer.paper(self.style))
        if colour.isValid():
            pl = self.sampleText.palette()
            pl.setColor(QPalette.Base, colour)
            self.sampleText.setPalette(pl)
            self.sampleText.repaint()
            if len(self.styleElementList.selectedItems()) > 1:
                for selItem in self.styleElementList.selectedItems():
                    style = self.lexer.ind2style[self.styleElementList.row(selItem)]
                    self.lexer.setPaper(colour, style)
            else:
                self.lexer.setPaper(colour, self.style)
        
    @pyqtSignature("")
    def on_allBackgroundColoursButton_clicked(self):
        """
        Private method used to select the background colour of all styles of a 
        selected lexer.
        """
        colour = KQColorDialog.getColor(self.lexer.paper(self.style))
        if colour.isValid():
            pl = self.sampleText.palette()
            pl.setColor(QPalette.Base, colour)
            self.sampleText.setPalette(pl)
            self.sampleText.repaint()
            for style in self.lexer.ind2style.values():
                self.lexer.setPaper(colour, style)
        
    @pyqtSignature("")
    def on_fontButton_clicked(self):
        """
        Private method used to select the font of the selected style and lexer.
        """
        font, ok = KQFontDialog.getFont(self.lexer.font(self.style))
        if ok:
            self.sampleText.setFont(font)
            if len(self.styleElementList.selectedItems()) > 1:
                for selItem in self.styleElementList.selectedItems():
                    style = self.lexer.ind2style[self.styleElementList.row(selItem)]
                    self.lexer.setFont(font, style)
            else:
                self.lexer.setFont(font, self.style)
        
    @pyqtSignature("")
    def on_allFontsButton_clicked(self):
        """
        Private method used to change the font of all styles of a selected lexer.
        """
        font, ok = KQFontDialog.getFont(self.lexer.font(self.style))
        if ok:
            self.sampleText.setFont(font)
            for style in self.lexer.ind2style.values():
                self.lexer.setFont(font, style)
        
    def on_eolfillCheckBox_toggled(self, b):
        """
        Private method used to set the eolfill for the selected style and lexer.
        
        @param b Flag indicating enabled or disabled state.
        """
        self.lexer.setEolFill(b, self.style)
        
    @pyqtSignature("")
    def on_allEolFillButton_clicked(self):
        """
        Private method used to set the eolfill for all styles of a selected lexer.
        """
        on = self.trUtf8("Enabled")
        off = self.trUtf8("Disabled")
        selection, ok = KQInputDialog.getItem(\
            self,
            self.trUtf8("Fill to end of line"),
            self.trUtf8("Select fill to end of line for all styles"),
            QStringList() << on << off, 
            0, False)
        if ok:
            enabled = selection == on
            self.eolfillCheckBox.setChecked(enabled)
            for style in self.lexer.ind2style.values():
                self.lexer.setEolFill(enabled, style)
        
    @pyqtSignature("")
    def on_defaultButton_clicked(self):
        """
        Private method to set the current style to it's default values.
        """
        if len(self.styleElementList.selectedItems()) > 1:
            for selItem in self.styleElementList.selectedItems():
                style = self.lexer.ind2style[self.styleElementList.row(selItem)]
                self.__setToDefault(style)
        else:
            self.__setToDefault(self.style)
        self.on_styleElementList_currentRowChanged(self.styleElementList.currentRow())
        
    @pyqtSignature("")
    def on_allDefaultButton_clicked(self):
        """
        Private method to set all styles to their default values.
        """
        for style in self.lexer.ind2style.values():
            self.__setToDefault(style)
        self.on_styleElementList_currentRowChanged(self.styleElementList.currentRow())
        
    def __setToDefault(self, style):
        """
        Private method to set a specific style to it's default values.
        
        @param style style to be reset (integer)
        """
        self.lexer.setColor(self.lexer.defaultColor(style), style)
        self.lexer.setPaper(self.lexer.defaultPaper(style), style)
        self.lexer.setFont(self.lexer.defaultFont(style), style)
        self.lexer.setEolFill(self.lexer.defaultEolFill(style), style)
        
    @pyqtSignature("")
    def on_importCurrentButton_clicked(self):
        """
        Private slot to import the styles of the current lexer.
        """
        self.__importStyles({self.lexer.language() : self.lexer})
        
    @pyqtSignature("")
    def on_exportCurrentButton_clicked(self):
        """
        Private slot to export the styles of the current lexer.
        """
        self.__exportStyles([self.lexer])
        
    @pyqtSignature("")
    def on_importAllButton_clicked(self):
        """
        Private slot to import the styles of all lexers.
        """
        self.__importStyles(self.lexers)
        
    @pyqtSignature("")
    def on_exportAllButton_clicked(self):
        """
        Private slot to export the styles of all lexers.
        """
        self.__exportStyles(self.lexers.values())
        
    def __exportStyles(self, lexers):
        """
        Private method to export the styles of the given lexers.
        
        @param lexers list of lexer objects for which to export the styles
        """
        selectedFilter = QString("")
        fn = KQFileDialog.getSaveFileName(\
            self,
            self.trUtf8("Export Highlighting Styles"),
            QString(),
            self.trUtf8("eric4 highlighting styles file (*.e4h)"),
            selectedFilter,
            QFileDialog.Options(QFileDialog.DontConfirmOverwrite))
        
        if fn.isEmpty():
            return
        
        ext = QFileInfo(fn).suffix()
        if ext.isEmpty():
            ex = selectedFilter.section('(*', 1, 1).section(')', 0, 0)
            if not ex.isEmpty():
                fn.append(ex)
        fn = unicode(fn)
        
        try:
            f = open(fn, "wb")
            HighlightingStylesWriter(f, lexers).writeXML()
            f.close()
        except IOError, err:
            KQMessageBox.critical(self,
                self.trUtf8("Export Highlighting Styles"),
                self.trUtf8("""<p>The highlighting styles could not be exported"""
                            """ to file <b>%1</b>.</p><p>Reason: %2</p>""")\
                    .arg(fn)\
                    .arg(unicode(err))
            )
        
    def __importStyles(self, lexers):
        """
        Private method to import the styles of the given lexers.
        
        @param lexers dictionary of lexer objects for which to import the styles
        """
        fn = KQFileDialog.getOpenFileName(\
            self,
            self.trUtf8("Import Highlighting Styles"),
            QString(),
            self.trUtf8("eric4 highlighting styles file (*.e4h)"),
            None)
        
        if fn.isEmpty():
            return
        
        fn = unicode(fn)
        
        try:
            f = open(fn, "rb")
            try:
                line = f.readline()
                dtdLine = f.readline()
            finally:
                f.close()
        except IOError, err:
            KQMessageBox.critical(self,
                self.trUtf8("Import Highlighting Styles"),
                self.trUtf8("""<p>The highlighting styles could not be read"""
                            """ from file <b>%1</b>.</p><p>Reason: %2</p>""")\
                    .arg(fn)\
                    .arg(unicode(err))
            )
            return
        
        validating = dtdLine.startswith("<!DOCTYPE")
        parser = make_parser(validating)
        handler = HighlightingStylesHandler(lexers)
        er = XMLEntityResolver()
        eh = XMLErrorHandler()
        
        parser.setContentHandler(handler)
        parser.setEntityResolver(er)
        parser.setErrorHandler(eh)
        
        try:
            f = open(fn, "rb")
            try:
                try:
                    parser.parse(f)
                except UnicodeEncodeError:
                    f.seek(0)
                    buf = cStringIO.StringIO(f.read())
                    parser.parse(buf)
            finally:
                f.close()
        except IOError, err:
            KQMessageBox.critical(self,
                self.trUtf8("Import Highlighting Styles"),
                self.trUtf8("""<p>The highlighting styles could not be read"""
                            """ from file <b>%1</b>.</p><p>Reason: %2</p>""")\
                    .arg(fn)\
                    .arg(unicode(err))
            )
            return
        except XMLFatalParseError:
            KQMessageBox.critical(self,
                self.trUtf8("Import Highlighting Styles"),
                self.trUtf8("""<p>The highlighting styles file <b>%1</b>"""
                            """ has invalid contents.</p>""").arg(fn))
            eh.showParseMessages()
            return
        
        eh.showParseMessages()
        
        if self.lexer:
            colour = self.lexer.color(self.style)
            paper = self.lexer.paper(self.style)
            eolfill = self.lexer.eolFill(self.style)
            font = self.lexer.font(self.style)
            
            self.sampleText.setFont(font)
            pl = self.sampleText.palette()
            pl.setColor(QPalette.Text, colour)
            pl.setColor(QPalette.Base, paper)
            self.sampleText.setPalette(pl)
            self.sampleText.repaint()
            self.eolfillCheckBox.setChecked(eolfill)
        
    def saveState(self):
        """
        Public method to save the current state of the widget.
        
        @return array containing the index of the selected lexer language (integer)
            and the index of the selected lexer entry (integer)
        """
        savedState = [
            self.lexerLanguageComboBox.currentIndex(),
            self.styleElementList.currentRow(),
        ]
        return savedState
        
    def setState(self, state):
        """
        Public method to set the state of the widget.
        
        @param state state data generated by saveState
        """
        self.lexerLanguageComboBox.setCurrentIndex(state[0])
        self.on_lexerLanguageComboBox_activated(self.lexerLanguageComboBox.currentText())
        self.styleElementList.setCurrentRow(state[1])

def create(dlg):
    """
    Module function to create the configuration page.
    
    @param dlg reference to the configuration dialog
    """
    page = EditorHighlightingStylesPage(dlg.getLexers())
    return page
