# -*- coding: utf-8 -*-

# Copyright (c) 2006 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a LED widget.

It was inspired by KLed.
"""

from PyQt4.QtGui import *
from PyQt4.QtCore import *

E4LedRectangular = 0
E4LedCircular    = 1

class E4Led(QWidget):
    """
    Class implementing a LED widget.
    """
    def __init__(self, parent = None, color = None, shape = E4LedCircular, rectRatio = 1):
        """
        Constructor
        
        @param parent reference to parent widget (QWidget)
        @param color color of the LED (QColor)
        @param shape shape of the LED (E4LedCircular, E4LedRectangular)
        @param rectRation ratio width to height, if shape is rectangular (float)
        """
        QWidget.__init__(self, parent)
        
        if color is None:
            color = QColor("green")
        
        self.__led_on = True
        self.__dark_factor = 300
        self.__offcolor = color.dark(self.__dark_factor)
        self.__led_color = color
        self.__framedLed = True
        self.__shape = shape
        self.__rectRatio = rectRatio
        
        self.setColor(color)
        
    def paintEvent(self, evt):
        """
        Protected slot handling the paint event.
        
        @param evt paint event object (QPaintEvent)
        @exception TypeError The E4Led has an unsupported shape type.
        """
        if self.__shape == E4LedCircular:
            self.__paintRound()
        elif self.__shape == E4LedRectangular:
            self.__paintRectangular()
        else:
            raise TypeError("Unsupported shape type for E4Led.")
        
    def __getBestRoundSize(self):
        """
        Private method to calculate the width of the LED.
        
        @return new width of the LED (integer)
        """
        width = min(self.width(), self.height())
        width -= 2  # leave one pixel border
        return width > -1 and width or 0
        
    def __paintRound(self):
        """
        Private method to paint a round raised LED.
        """
        # Initialize coordinates, width and height of the LED
        width = self.__getBestRoundSize()
        
        # Calculate the gradient for the LED
        wh = width / 2
        color = self.__led_on and self.__led_color or self.__offcolor
        gradient = QRadialGradient(wh, wh, wh, 0.8 * wh, 0.8 * wh)
        gradient.setColorAt(0.0, color.light(200))
        gradient.setColorAt(0.6, color)
        if self.__framedLed:
            gradient.setColorAt(0.9, color.dark())
            gradient.setColorAt(1.0, self.palette().color(QPalette.Dark))
        else:
            gradient.setColorAt(1.0, color.dark())
        
        # now do the drawing
        paint = QPainter(self)
        paint.setRenderHint(QPainter.Antialiasing, True)
        paint.setBrush(QBrush(gradient))
        paint.setPen(Qt.NoPen)
        paint.drawEllipse(1, 1, width, width)
        paint.end()
        
    def __paintRectangular(self):
        """
        Private method to paint a rectangular raised LED.
        """
        # Initialize coordinates, width and height of the LED
        width = self.height() * self.__rectRatio
        left = max(0, int((self.width() - width) / 2) - 1)
        right = min(int((self.width() + width) / 2), self.width())
        height = self.height()
        
        # now do the drawing
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        color = self.__led_on and self.__led_color or self.__offcolor

        painter.setPen(color.light(200))
        painter.drawLine(left, 0, left, height - 1)
        painter.drawLine(left + 1, 0, right - 1, 0)
        if self.__framedLed:
            painter.setPen(self.palette().color(QPalette.Dark))
        else:
            painter.setPen(color.dark())
        painter.drawLine(left + 1, height - 1, right - 1, height - 1)
        painter.drawLine(right - 1, 1, right - 1, height - 1)
        painter.fillRect(left + 1, 1, right - 2, height - 2, QBrush(color))
        painter.end()
        
    def isOn(self):
        """
        Public method to return the LED state.
        
        @return flag indicating the light state (boolean)
        """
        return self.__led_on
        
    def shape(self):
        """
        Public method to return the LED shape.
        
        @return LED shape (E4LedCircular, E4LedRectangular)
        """
        return self.__shape
        
    def ratio(self):
        """
        Public method to return the LED rectangular ratio (width / height).
        
        @return LED rectangular ratio (float)
        """
        return self.__rectRatio
        
    def color(self):
        """
        Public method to return the LED color.
        
        @return color of the LED (QColor)
        """
        return self.__led_color
        
    def setOn(self, state):
        """
        Public method to set the LED to on.
        
        @param state new state of the LED (boolean)
        """
        if self.__led_on != state:
            self.__led_on = state
            self.update()
        
    def setShape(self, shape):
        """
        Public method to set the LED shape.
        
        @param shape new LED shape (E4LedCircular, E4LedRectangular)
        """
        if self.__shape != shape:
            self.__shape = shape
            self.update()
        
    def setRatio(self, ratio):
        """
        Public method to set the LED rectangular ratio (width / height).
        
        @param ratio new LED rectangular ratio (float)
        """
        if self.__rectRatio != ratio:
            self.__rectRatio = ratio
            self.update()
        
    def setColor(self, color):
        """
        Public method to set the LED color.
        
        @param color color for the LED (QColor)
        """
        if self.__led_color != color:
            self.__led_color = color
            self.__offcolor = color.dark(self.__dark_factor)
            self.update()
        
    def setDarkFactor(self, darkfactor):
        """
        Public method to set the dark factor.
        
        @param darkfactor value to set for the dark factor (integer)
        """
        if self.__dark_factor != darkfactor:
            self.__dark_factor = darkfactor
            self.__offcolor = self.__led_color.dark(darkfactor)
            self.update()
        
    def darkFactor(self):
        """
        Public method to return the dark factor.
        
        @return the current dark factor (integer)
        """
        return self.__dark_factor
        
    def toggle(self):
        """
        Public slot to toggle the LED state.
        """
        self.setOn(not self.__led_on)
        
    def on(self):
        """
        Public slot to set the LED to on.
        """
        self.setOn(True)
        
    def off(self):
        """
        Public slot to set the LED to off.
        """
        self.setOn(False)
        
    def setFramed(self, framed):
        """
        Public slot to set the __framedLed attribute.
        
        @param framed flag indicating the framed state (boolean)
        """
        if self.__framedLed != framed:
            self.__framedLed = framed
            self.__off_map = None
            self.__on_map = None
            self.update()
        
    def isFramed(self):
        """
        Public method to return the framed state.
        
        @return flag indicating the current framed state (boolean)
        """
        return self.__framedLed
        
    def sizeHint(self):
        """
        Public method to give a hint about our desired size.
        
        @return size hint (QSize)
        """
        return QSize(18, 18)
        
    def minimumSizeHint(self):
        """
        Public method to give a hint about our minimum size.
        
        @return size hint (QSize)
        """
        return QSize(18, 18)
