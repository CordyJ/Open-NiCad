# -*- coding: utf-8 -*-

# Copyright (c) 2005 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the templates properties dialog.
"""

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from KdeQt import KQMessageBox

import QScintilla.Lexers

from Ui_TemplatePropertiesDialog import Ui_TemplatePropertiesDialog


class TemplatePropertiesDialog(QDialog, Ui_TemplatePropertiesDialog):
    """
    Class implementing the templates properties dialog.
    """
    def __init__(self, parent, groupMode = False, itm = None):
        """
        Constructor
        
        @param parent the parent widget (QWidget)
        @param groupMode flag indicating group mode (boolean)
        @param itm item (TemplateEntry or TemplateGroup) to
            read the data from
        """
        QDialog.__init__(self, parent)
        self.setupUi(self)
        
        if not groupMode:
            self.nameEdit.setWhatsThis(self.trUtf8(
                """<b>Template name<b><p>Enter the name of the template."""
                """ Templates may be autocompleted upon this name."""
                """ In order to support autocompletion. the template name"""
                """ must only consist of letters (a-z and A-Z),"""
                """ digits (0-9) and underscores (_).</p>"""
            ))
            self.__nameValidator = QRegExpValidator(QRegExp("[a-zA-Z0-9_]+"), 
                                                    self.nameEdit)
            self.nameEdit.setValidator(self.__nameValidator)
        
        self.languages = [("All", self.trUtf8("All"))]
        supportedLanguages = QScintilla.Lexers.getSupportedLanguages()
        languages = supportedLanguages.keys()
        languages.sort()
        for language in languages:
            self.languages.append((language, supportedLanguages[language][0]))
        
        self.groupMode = groupMode
        if groupMode:
            langList = QStringList()
            for lang, langDisp in self.languages:
                langList.append(langDisp)
            
            self.groupLabel.setText(self.trUtf8("Language:"))
            self.groupCombo.addItems(langList)
            self.templateLabel.setEnabled(False)
            self.templateEdit.setEnabled(False)
            self.templateEdit.setPlainText(self.trUtf8("GROUP"))
            self.helpButton.setEnabled(False)
            self.descriptionLabel.hide()
            self.descriptionEdit.hide()
        else:
            groups = QStringList()
            for group in parent.getGroupNames():
                groups.append(group)
            self.groupCombo.addItems(groups)
        
        if itm is not None:
            self.nameEdit.setText(itm.getName())
            if groupMode:
                lang = itm.getLanguage()
                for l, d in self.languages:
                    if l == lang:
                        self.setSelectedGroup(d)
                        break
            else:
                self.setSelectedGroup(itm.getGroupName())
                self.templateEdit.setPlainText(itm.getTemplateText())
                self.descriptionEdit.setText(itm.getDescription())
            
            self.nameEdit.selectAll()

    def keyPressEvent(self, ev):
        """
        Re-implemented to handle the user pressing the escape key.
        
        @param ev key event (QKeyEvent)
        """
        if ev.key() == Qt.Key_Escape:
            res = KQMessageBox.question(self,
                self.trUtf8("Close dialog"),
                self.trUtf8("""Do you really want to close the dialog?"""),
                QMessageBox.StandardButtons(\
                    QMessageBox.No | \
                    QMessageBox.Yes),
                QMessageBox.No)
            if res == QMessageBox.Yes:
                self.reject()
    
    @pyqtSignature("")
    def on_helpButton_clicked(self):
        """
        Public slot to show some help.
        """
        KQMessageBox.information(self,
            self.trUtf8("Template Help"),
            self.trUtf8(\
                """<p>To use variables in a template, you just have to enclose"""
                """ the variablename with $-characters. When you use the template,"""
                """ you will then be asked for a value for this variable.</p>"""
                """<p>Example template: This is a $VAR$</p>"""
                """<p>When you use this template you will be prompted for a value"""
                """ for the variable $VAR$. Any occurrences of $VAR$ will then be"""
                """ replaced with whatever you've entered.</p>"""
                """<p>If you need a single $-character in a template, which is not"""
                """ used to enclose a variable, type $$(two dollar characters)"""
                """ instead. They will automatically be replaced with a single"""
                """ $-character when you use the template.</p>"""
                """<p>If you want a variables contents to be treated specially,"""
                """ the variablename must be followed by a ':' and one formatting"""
                """ specifier (e.g. $VAR:ml$). The supported specifiers are:"""
                """<table>"""
                """<tr><td>ml</td><td>Specifies a multiline formatting."""
                """ The first line of the variable contents is prefixed with the string"""
                """ occuring before the variable on the same line of the template."""
                """ All other lines are prefixed by the same amount of whitespace"""
                """ as the line containing the variable."""
                """</td></tr>"""
                """<tr><td>rl</td><td>Specifies a repeated line formatting."""
                """ Each line of the variable contents is prefixed with the string"""
                """ occuring before the variable on the same line of the template."""
                """</td></tr>"""
                """</table></p>"""
                """<p>The following predefined variables may be used in a template:"""
                """<table>"""
                """<tr><td>date</td>"""
                """<td>today's date in ISO format (YYYY-MM-DD)</td></tr>"""
                """<tr><td>year</td>"""
                """<td>the current year</td></tr>"""
                """<tr><td>project_name</td>"""
                """<td>the name of the project (if any)</td></tr>"""
                """<tr><td>path_name</td>"""
                """<td>full path of the current file</td></tr>"""
                """<tr><td>dir_name</td>"""
                """<td>full path of the parent directory</td></tr>"""
                """<tr><td>file_name</td>"""
                """<td>the current file name (without directory)</td></tr>"""
                """<tr><td>base_name</td>"""
                """<td>like <i>file_name</i>, but without extension</td></tr>"""
                """<tr><td>ext</td>"""
                """<td>the extension of the current file</td></tr>"""
                """</table></p>"""
                """<p>If you want to change the default delimiter to anything"""
                """ different, please use the configuration dialog to do so.</p>"""))
        
    def setSelectedGroup(self, name):
        """
        Public method to select a group.
        
        @param name name of the group to be selected (string or QString)
        """
        index = self.groupCombo.findText(name)
        self.groupCombo.setCurrentIndex(index)

    def getData(self):
        """
        Public method to get the data entered into the dialog.
        
        @return a tuple of two strings (name, language), if the dialog is in group mode,
            and a tuple of four strings (name, description,group name, template) 
            otherwise.
        """
        if self.groupMode:
            return (unicode(self.nameEdit.text()),
                    self.languages[self.groupCombo.currentIndex()][0]
                   )
        else:
            return (unicode(self.nameEdit.text()),
                    unicode(self.descriptionEdit.text()), 
                    unicode(self.groupCombo.currentText()),
                    unicode(self.templateEdit.toPlainText())
                   )
