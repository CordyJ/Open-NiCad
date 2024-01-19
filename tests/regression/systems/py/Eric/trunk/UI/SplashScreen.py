# -*- coding: utf-8 -*-

# Copyright (c) 2006 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a splashscreen for eric4.
"""

import os.path
import logging

from PyQt4.QtCore import Qt
from PyQt4.QtGui import QApplication, QPixmap, QSplashScreen, QColor

from eric4config import getConfig

class SplashScreen(QSplashScreen):
    """
    Class implementing a splashscreen for eric4.
    """
    def __init__(self):
        """
        Constructor
        """
        ericPic = QPixmap(os.path.join(getConfig('ericPixDir'), 'ericSplash.png'))
        self.labelAlignment = \
            Qt.Alignment(Qt.AlignBottom | Qt.AlignRight | Qt.AlignAbsolute)
        QSplashScreen.__init__(self, ericPic)
        self.show()
        QApplication.flush()
        
    def showMessage(self, msg):
        """
        Public method to show a message in the bottom part of the splashscreen.
        
        @param msg message to be shown (string or QString)
        """
        logging.debug(unicode(msg))
        QSplashScreen.showMessage(self, msg, self.labelAlignment, QColor(Qt.white))
        QApplication.processEvents()
        
    def clearMessage(self):
        """
        Public method to clear the message shown.
        """
        QSplashScreen.clearMessage(self)
        QApplication.processEvents()

class NoneSplashScreen(object):
    """
    Class implementing a "None" splashscreen for eric4.
    
    This class implements the same interface as the real splashscreen,
    but simply does nothing.
    """
    def __init__(self):
        """
        Constructor
        """
        pass
        
    def showMessage(self, msg):
        """
        Public method to show a message in the bottom part of the splashscreen.
        
        @param msg message to be shown (string or QString)
        """
        logging.debug(unicode(msg))
        
    def clearMessage(self):
        """
        Public method to clear the message shown.
        """
        pass
        
    def finish(self, widget):
        """
        Public method to finish the splash screen.
        
        @param widget widget to wait for (QWidget)
        """
        pass
