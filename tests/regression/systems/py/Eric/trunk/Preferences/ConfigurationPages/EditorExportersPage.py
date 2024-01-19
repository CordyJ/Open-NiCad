# -*- coding: utf-8 -*-

# Copyright (c) 2007 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the Editor Exporters configuration page.
"""

from PyQt4.QtCore import QVariant, pyqtSignature

from KdeQt import KQFontDialog

from ConfigurationPageBase import ConfigurationPageBase
from Ui_EditorExportersPage import Ui_EditorExportersPage

import Preferences

class EditorExportersPage(ConfigurationPageBase, Ui_EditorExportersPage):
    """
    Class implementing the Editor Typing configuration page.
    """
    def __init__(self):
        """
        Constructor
        """
        ConfigurationPageBase.__init__(self)
        self.setupUi(self)
        self.setObjectName("EditorExportersPage")
        
        # set initial values
        self.pageIds = {}
        self.pageIds[' '] = self.stackedWidget.indexOf(self.emptyPage)
        self.pageIds['HTML'] = self.stackedWidget.indexOf(self.htmlPage)
        self.pageIds['PDF'] = self.stackedWidget.indexOf(self.pdfPage)
        self.pageIds['RTF'] = self.stackedWidget.indexOf(self.rtfPage)
        self.pageIds['TeX'] = self.stackedWidget.indexOf(self.texPage)
        exporters = self.pageIds.keys()
        exporters.sort()
        for exporter in exporters:
            self.exportersCombo.addItem(exporter, QVariant(self.pageIds[exporter]))
        
        self.pdfFontCombo.addItem(self.trUtf8("Courier"), QVariant("Courier"))
        self.pdfFontCombo.addItem(self.trUtf8("Helvetica"), QVariant("Helvetica"))
        self.pdfFontCombo.addItem(self.trUtf8("Times"), QVariant("Times"))
        
        self.pdfPageSizeCombo.addItem(self.trUtf8("A4"), QVariant("A4"))
        self.pdfPageSizeCombo.addItem(self.trUtf8("Letter"), QVariant("Letter"))
        
        # HTML
        self.htmlWysiwygCheckBox.setChecked(\
            Preferences.getEditorExporter("HTML/WYSIWYG"))
        self.htmlFoldingCheckBox.setChecked(\
            Preferences.getEditorExporter("HTML/Folding"))
        self.htmlStylesCheckBox.setChecked(\
            Preferences.getEditorExporter("HTML/OnlyStylesUsed"))
        self.htmlTitleCheckBox.setChecked(\
            Preferences.getEditorExporter("HTML/FullPathAsTitle"))
        self.htmlTabsCheckBox.setChecked(\
            Preferences.getEditorExporter("HTML/UseTabs"))
        
        # PDF
        self.pdfMagnificationSlider.setValue(\
            Preferences.getEditorExporter("PDF/Magnification"))
        ind = self.pdfFontCombo.findData(QVariant(\
            Preferences.getEditorExporter("PDF/Font")))
        self.pdfFontCombo.setCurrentIndex(ind)
        ind = self.pdfPageSizeCombo.findData(QVariant(\
            Preferences.getEditorExporter("PDF/PageSize")))
        self.pdfPageSizeCombo.setCurrentIndex(ind)
        self.pdfMarginTopSpin.setValue(\
            Preferences.getEditorExporter("PDF/MarginTop"))
        self.pdfMarginBottomSpin.setValue(\
            Preferences.getEditorExporter("PDF/MarginBottom"))
        self.pdfMarginLeftSpin.setValue(\
            Preferences.getEditorExporter("PDF/MarginLeft"))
        self.pdfMarginRightSpin.setValue(\
            Preferences.getEditorExporter("PDF/MarginRight"))
        
        # RTF
        self.rtfWysiwygCheckBox.setChecked(\
            Preferences.getEditorExporter("RTF/WYSIWYG"))
        self.rtfTabsCheckBox.setChecked(\
            Preferences.getEditorExporter("RTF/UseTabs"))
        self.rtfFont = Preferences.getEditorExporter("RTF/Font")
        self.rtfFontSample.setFont(self.rtfFont)
        
        # TeX
        self.texStylesCheckBox.setChecked(\
            Preferences.getEditorExporter("TeX/OnlyStylesUsed"))
        self.texTitleCheckBox.setChecked(\
            Preferences.getEditorExporter("TeX/FullPathAsTitle"))
        
        self.on_exportersCombo_activated(' ')
    
    def save(self):
        """
        Public slot to save the Editor Typing configuration.
        """
        # HTML
        Preferences.setEditorExporter("HTML/WYSIWYG",
            int(self.htmlWysiwygCheckBox.isChecked()))
        Preferences.setEditorExporter("HTML/Folding",
            int(self.htmlFoldingCheckBox.isChecked()))
        Preferences.setEditorExporter("HTML/OnlyStylesUsed",
            int(self.htmlStylesCheckBox.isChecked()))
        Preferences.setEditorExporter("HTML/FullPathAsTitle",
            int(self.htmlTitleCheckBox.isChecked()))
        Preferences.setEditorExporter("HTML/UseTabs",
            int(self.htmlTabsCheckBox.isChecked()))
        
        # PDF
        Preferences.setEditorExporter("PDF/Magnification", 
            self.pdfMagnificationSlider.value())
        Preferences.setEditorExporter("PDF/Font", 
            self.pdfFontCombo.itemData(self.pdfFontCombo.currentIndex())\
                             .toString())
        Preferences.setEditorExporter("PDF/PageSize", 
            self.pdfPageSizeCombo.itemData(self.pdfPageSizeCombo.currentIndex())\
                                 .toString())
        Preferences.setEditorExporter("PDF/MarginTop", 
            self.pdfMarginTopSpin.value())
        Preferences.setEditorExporter("PDF/MarginBottom", 
            self.pdfMarginBottomSpin.value())
        Preferences.setEditorExporter("PDF/MarginLeft", 
            self.pdfMarginLeftSpin.value())
        Preferences.setEditorExporter("PDF/MarginRight", 
            self.pdfMarginRightSpin.value())
        
        # RTF
        Preferences.setEditorExporter("RTF/WYSIWYG",
            int(self.rtfWysiwygCheckBox.isChecked()))
        Preferences.setEditorExporter("RTF/UseTabs",
            int(self.rtfTabsCheckBox.isChecked()))
        Preferences.setEditorExporter("RTF/Font", self.rtfFont)
        
        # TeX
        Preferences.setEditorExporter("TeX/OnlyStylesUsed",
            int(self.texStylesCheckBox.isChecked()))
        Preferences.setEditorExporter("TeX/FullPathAsTitle",
            int(self.texTitleCheckBox.isChecked()))
    
    @pyqtSignature("QString")
    def on_exportersCombo_activated(self, exporter):
        """
        Private slot to select the page related to the selected exporter.
        
        @param exporter name of the selected exporter (QString)
        """
        try:
            index = self.pageIds[str(exporter)]
        except KeyError:
            index = self.pageIds[' ']
        self.stackedWidget.setCurrentIndex(index)
    
    @pyqtSignature("")
    def on_rtfFontButton_clicked(self):
        """
        Private method used to select the font for the RTF export.
        """
        font, ok = KQFontDialog.getFont(self.rtfFont)
        if ok:
            self.rtfFontSample.setFont(font)
            self.rtfFont = font

def create(dlg):
    """
    Module function to create the configuration page.
    
    @param dlg reference to the configuration dialog
    """
    page = EditorExportersPage()
    return page
