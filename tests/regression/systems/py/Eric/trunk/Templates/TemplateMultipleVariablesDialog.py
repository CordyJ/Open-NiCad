# -*- coding: utf-8 -*-

# Copyright (c) 2005 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a dialog for entering multiple template variables.
"""

from PyQt4.QtCore import *
from PyQt4.QtGui import *

class TemplateMultipleVariablesDialog(QDialog):
    """
    Class implementing a dialog for entering multiple template variables.
    """
    def __init__(self, variables, parent = None):
        """
        Constructor
        
        @param variables list of template variable names (list of strings)
        @param parent parent widget of this dialog (QWidget)
        """
        QDialog.__init__(self, parent)

        self.TemplateMultipleVariablesDialogLayout = QVBoxLayout(self)
        self.TemplateMultipleVariablesDialogLayout.setMargin(6)
        self.TemplateMultipleVariablesDialogLayout.setSpacing(6)
        self.TemplateMultipleVariablesDialogLayout.setObjectName(\
            "TemplateMultipleVariablesDialogLayout")
        self.setLayout(self.TemplateMultipleVariablesDialogLayout)

        # generate the scrollarea
        self.variablesView = QScrollArea(self)
        self.variablesView.setObjectName("variablesView")
        self.TemplateMultipleVariablesDialogLayout.addWidget(self.variablesView)
        
        self.variablesView.setWidgetResizable(True)
        self.variablesView.setFrameStyle(QFrame.NoFrame)
        
        self.top = QWidget(self)
        self.variablesView.setWidget(self.top)
        self.grid = QGridLayout(self.top)
        self.grid.setMargin(0)
        self.grid.setSpacing(6)
        self.top.setLayout(self.grid)

        # populate the scrollarea with labels and text edits
        self.variablesEntries = {}
        row = 0
        for var in variables:
            l = QLabel("%s:" % var, self.top)
            self.grid.addWidget(l, row, 0, Qt.Alignment(Qt.AlignTop))
            if var.find(":") >= 0:
                formatStr = var[1:-1].split(":")[1]
                if formatStr in ["ml", "rl"]:
                    t = QTextEdit(self.top)
                    t.setTabChangesFocus(True)
                else:
                    t = QLineEdit(self.top)
            else:
                t = QLineEdit(self.top)
            self.grid.addWidget(t, row, 1)
            self.variablesEntries[var] = t
            row += 1
        # add a spacer to make the entries aligned at the top
        spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.grid.addItem(spacer, row, 1)
        self.variablesEntries[variables[0]].setFocus()
        self.top.adjustSize()

        # generate the buttons
        layout1 = QHBoxLayout()
        layout1.setMargin(0)
        layout1.setSpacing(6)
        layout1.setObjectName("layout1")
        
        spacer1 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        layout1.addItem(spacer1)

        self.okButton = QPushButton(self)
        self.okButton.setObjectName("okButton")
        self.okButton.setDefault(True)
        layout1.addWidget(self.okButton)

        self.cancelButton = QPushButton(self)
        self.cancelButton.setObjectName("cancelButton")
        layout1.addWidget(self.cancelButton)
        
        spacer2 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        layout1.addItem(spacer2)
        
        self.TemplateMultipleVariablesDialogLayout.addLayout(layout1)

        # set the texts of the standard widgets
        self.setWindowTitle(self.trUtf8("Enter Template Variables"))
        self.okButton.setText(self.trUtf8("&OK"))
        self.cancelButton.setText(self.trUtf8("&Cancel"))

        # polish up the dialog
        self.resize(QSize(400, 480).expandedTo(self.minimumSizeHint()))

        self.connect(self.okButton, SIGNAL("clicked()"), self.accept)
        self.connect(self.cancelButton, SIGNAL("clicked()"), self.reject)

    def getVariables(self):
        """
        Public method to get the values for all variables.
        
        @return dictionary with the variable as a key and its value (string)
        """
        values = {}
        for var, textEdit in self.variablesEntries.items():
            try:
                values[var] = unicode(textEdit.text())
            except AttributeError:
                values[var] = unicode(textEdit.toPlainText())
        return values
