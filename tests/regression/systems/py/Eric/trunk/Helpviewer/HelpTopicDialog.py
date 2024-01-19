# -*- coding: utf-8 -*-

# Copyright (c) 2009 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a dialog to select a help topic to display.
"""

from PyQt4.QtGui import QDialog
from PyQt4.QtCore import pyqtSignature, SIGNAL, QUrl

from Ui_HelpTopicDialog import Ui_HelpTopicDialog

class HelpTopicDialog(QDialog, Ui_HelpTopicDialog):
    """
    Class implementing a dialog to select a help topic to display.
    """
    def __init__(self, parent, keyword, links):
        """
        Constructor
        
        @param parent reference to the parent widget (QWidget)
        @param keyword keyword for the link set (QString)
        @param links dictionary with help topic as key (QString) and
            URL as value (QUrl)
        """
        QDialog.__init__(self, parent)
        self.setupUi(self)
        
        self.label.setText(self.trUtf8("Choose a &topic for <b>%1</b>:")\
            .arg(keyword))
        
        self.__links = links
        for topic in self.__links:
            self.topicsList.addItem(topic)
        if self.topicsList.count() > 0:
            self.topicsList.setCurrentRow(0)
        self.topicsList.setFocus()
        
        self.connect(self.topicsList, SIGNAL("itemActivated(QListWidgetItem*)"), 
                     self.accept)
    
    def link(self):
        """
        Public method to the link of the selected topic.
        
        @return URL of the selected topic (QUrl)
        """
        itm = self.topicsList.currentItem()
        if itm is None:
            return QUrl()
        
        topic = itm.text()
        if topic.isEmpty() or topic not in self.__links:
            return QUrl()
        
        return self.__links[topic]
