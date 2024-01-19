# -*- coding: utf-8 -*-

# Copyright (c) 2009 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a dialog to edit the data of a search engine.
"""

from PyQt4.QtGui import QDialog

from Ui_OpenSearchEditDialog import Ui_OpenSearchEditDialog

class OpenSearchEditDialog(QDialog, Ui_OpenSearchEditDialog):
    """
    Class implementing a dialog to edit the data of a search engine.
    """
    def __init__(self, engine, parent = None):
        """
        Constructor
        """
        QDialog.__init__(self, parent)
        self.setupUi(self)
        
        self.__engine = engine
        
        self.nameEdit.setText(engine.name())
        self.descriptionEdit.setText(engine.description())
        self.imageEdit.setText(engine.imageUrl())
        self.searchEdit.setText(engine.searchUrlTemplate())
        self.suggestionsEdit.setText(engine.suggestionsUrlTemplate())
    
    def accept(self):
        """
        Public slot to accept the data entered.
        """
        self.__engine.setName(self.nameEdit.text())
        self.__engine.setDescription(self.descriptionEdit.text())
        self.__engine.setImageUrlAndLoad(self.imageEdit.text())
        self.__engine.setSearchUrlTemplate(self.searchEdit.text())
        self.__engine.setSuggestionsUrlTemplate(self.suggestionsEdit.text())
        
        QDialog.accept(self)
