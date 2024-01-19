# -*- coding: utf-8 -*-

# Copyright (c) 2009 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a palette widget for the icon editor.
"""

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from KdeQt import KQColorDialog

class IconEditorPalette(QWidget):
    """
    Class implementing a palette widget for the icon editor.
    
    @signal colorSelected(QColor) emitted after a new color has been selected
    """
    def __init__(self, parent = None):
        """
        Constructor
        
        @param parent reference to the parent widget (QWidget)
        """
        QWidget.__init__(self, parent)
        
        if self.layoutDirection == Qt.Horizontal:
            direction = QBoxLayout.LeftToRight
        else:
            direction = QBoxLayout.TopToBottom
        self.__layout = QBoxLayout(direction, self)
        self.setLayout(self.__layout)
        
        self.__preview = QLabel(self)
        self.__preview.setFrameStyle(QFrame.Panel | QFrame.Sunken)
        self.__preview.setFixedHeight(64)
        self.__preview.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.__preview.setWhatsThis(self.trUtf8(
            """<b>Preview</b>"""
            """<p>This is a 1:1 preview of the current icon.</p>"""
        ))
        self.__layout.addWidget(self.__preview)
        
        self.__color = QLabel(self)
        self.__color.setFrameStyle(QFrame.Panel | QFrame.Sunken)
        self.__color.setFixedHeight(24)
        self.__color.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.__color.setWhatsThis(self.trUtf8(
            """<b>Current Color</b>"""
            """<p>This is the currently selected color used for drawing.</p>"""
        ))
        self.__layout.addWidget(self.__color)
        
        self.__colorTxt = QLabel(self)
        self.__colorTxt.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.__colorTxt.setWhatsThis(self.trUtf8(
            """<b>Current Color Value</b>"""
            """<p>This is the currently selected color value used for drawing.</p>"""
        ))
        self.__layout.addWidget(self.__colorTxt)
        
        self.__colorButton = QPushButton(self.trUtf8("Select Color"), self)
        self.__colorButton.setWhatsThis(self.trUtf8(
            """<b>Select Color</b>"""
            """<p>Select the current drawing color via a color selection dialog.</p>"""
        ))
        self.connect(self.__colorButton, SIGNAL("clicked()"), self.__selectColor)
        self.__layout.addWidget(self.__colorButton)
        
        self.__colorAlpha = QSpinBox(self)
        self.__colorAlpha.setRange(0, 255)
        self.__colorAlpha.setWhatsThis(self.trUtf8(
            """<b>Select alpha channel value</b>"""
            """<p>Select the value for the alpha channel of the current color.</p>"""
        ))
        self.__layout.addWidget(self.__colorAlpha)
        self.connect(self.__colorAlpha, SIGNAL("valueChanged(int)"), 
                     self.__alphaChanged)
        
        spacer = QSpacerItem(10, 10, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.__layout.addItem(spacer)
    
    def previewChanged(self, pixmap):
        """
        Public slot to update the preview.
        """
        self.__preview.setPixmap(pixmap)
    
    def colorChanged(self, color):
        """
        Public slot to update the color preview.
        """
        self.__currentColor = color
        self.__currentAlpha = color.alpha()
        
        pm = QPixmap(90, 18)
        pm.fill(color)
        self.__color.setPixmap(pm)
        
        self.__colorTxt.setText(
            "%d, %d, %d, %d" % (color.red(), color.green(), color.blue(), color.alpha()))
        
        self.__colorAlpha.setValue(self.__currentAlpha)
    
    def __selectColor(self):
        """
        Private slot to select a new drawing color.
        """
        col = KQColorDialog.getColor(self.__currentColor)
        col.setAlpha(self.__currentAlpha)
        
        if col.isValid():
            self.emit(SIGNAL("colorSelected(QColor)"), col)
    
    def __alphaChanged(self, val):
        """
        Private slot to track changes of the alpha channel.
        
        @param val value of the alpha channel
        """
        if val != self.__currentAlpha:
           col = QColor(self.__currentColor) 
           col.setAlpha(val)
           self.emit(SIGNAL("colorSelected(QColor)"), col)
