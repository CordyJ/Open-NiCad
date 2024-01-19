# -*- coding: utf-8 -*-

# Copyright (c) 2004 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Compatibility module to use the KDE Message Box instead of the Qt Message Box.
"""

import sys

from PyQt4.QtCore import QCoreApplication
from PyQt4.QtGui import QMessageBox

import Preferences

if Preferences.getUI("UseKDEDialogs") and not sys.e4nokde:
    try:
        from PyKDE4.kdeui import KMessageBox, KStandardGuiItem, KGuiItem
        from PyQt4.QtCore import QString
        
        def __nrButtons(buttons):
            """
            Private function to determine the number of buttons defined.
            
            @param buttons flags indicating which buttons to show 
                (QMessageBox.StandardButtons)
            @return number of buttons defined (integer)
            """
            count = 0
            flag = int(buttons)
            while flag > 0:
                if flag & 1:
                    count += 1
                flag = flag >> 1
            return count
        
        def __getGuiItem(button):
            """
            Private function to create a KGuiItem for a button.
            
            @param button flag indicating the button (QMessageBox.StandardButton)
            @return item for the button (KGuiItem)
            """
            if button == QMessageBox.Ok:
                return KStandardGuiItem.ok()
            elif button == QMessageBox.Cancel:
                return KStandardGuiItem.cancel()
            elif button == QMessageBox.Yes:
                return KStandardGuiItem.yes()
            elif button == QMessageBox.No:
                return KStandardGuiItem.no()
            elif button == QMessageBox.Discard:
                return KStandardGuiItem.discard()
            elif button == QMessageBox.Save:
                return KStandardGuiItem.save()
            elif button == QMessageBox.Apply:
                return KStandardGuiItem.apply()
            elif button == QMessageBox.Help:
                return KStandardGuiItem.help()
            elif button == QMessageBox.Close:
                return KStandardGuiItem.close()
            elif button == QMessageBox.Open:
                return KStandardGuiItem.open()
            elif button == QMessageBox.Reset:
                return KStandardGuiItem.reset()
            elif button == QMessageBox.Ignore:
                return KGuiItem(QCoreApplication.translate("KQMessageBox", "Ignore"))
            elif button == QMessageBox.Abort:
                return KGuiItem(QCoreApplication.translate("KQMessageBox", "Abort"))
            elif button == QMessageBox.RestoreDefaults:
                return KGuiItem(QCoreApplication.translate("KQMessageBox", "Restore Defaults"))
            elif button == QMessageBox.SaveAll:
                return KGuiItem(QCoreApplication.translate("KQMessageBox", "Save All"))
            elif button == QMessageBox.YesToAll:
                return KGuiItem(QCoreApplication.translate("KQMessageBox", "Yes to &All"))
            elif button == QMessageBox.NoToAll:
                return KGuiItem(QCoreApplication.translate("KQMessageBox", "N&o to All"))
            elif button == QMessageBox.Retry:
                return KGuiItem(QCoreApplication.translate("KQMessageBox", "Retry"))
            elif button == QMessageBox.NoButton:
                return KGuiItem()
            else:
                return KStandardGuiItem.ok()
        
        def __getLowestFlag(flags):
            """
            Private function to get the lowest flag.
            
            @param flags flags to be checked (integer)
            @return lowest flag (integer)
            """
            i = 1
            while i <= 0x80000000:
                if int(flags) & i == i:
                    return i
                i = i << 1
            return 0
        
        def __kdeInformation(parent, title, text, 
                             buttons = QMessageBox.Ok, defaultButton = QMessageBox.NoButton):
            """
            Function to show a modal information message box.
            
            @param parent parent widget of the message box
            @param title caption of the message box
            @param text text to be shown by the message box
            @param buttons flags indicating which buttons to show 
                (QMessageBox.StandardButtons)
            @param defaultButton flag indicating the default button
                (QMessageBox.StandardButton)
            @return button pressed by the user 
                (QMessageBox.StandardButton, always QMessageBox.NoButton)
            """
            KMessageBox.information(parent, text, title)
            return QMessageBox.NoButton
        
        def __kdeWarning(parent, title, text, 
                         buttons = QMessageBox.Ok, defaultButton = QMessageBox.NoButton):
            """
            Function to show a modal warning message box.
            
            @param parent parent widget of the message box
            @param title caption of the message box
            @param text text to be shown by the message box
            @param buttons flags indicating which buttons to show 
                (QMessageBox.StandardButtons)
            @param defaultButton flag indicating the default button
                (QMessageBox.StandardButton)
            @return button pressed by the user (QMessageBox.StandardButton)
            """
            if __nrButtons(buttons) == 1:
                KMessageBox.sorry(parent, text, title)
                return buttons
            
            if __nrButtons(buttons) == 2:
                if defaultButton == QMessageBox.NoButton:
                    defaultButton = __getLowestFlag(buttons)
                noButton = defaultButton
                noItem = __getGuiItem(noButton)
                yesButton = int(buttons & ~noButton)
                yesItem = __getGuiItem(yesButton)
                res = KMessageBox.warningYesNo(parent, text, title, yesItem, noItem)
                if res == KMessageBox.Yes:
                    return yesButton
                else:
                    return noButton
            
            if __nrButtons(buttons) == 3:
                if defaultButton == QMessageBox.NoButton:
                    defaultButton = __getLowestFlag(buttons)
                yesButton = defaultButton
                yesItem = __getGuiItem(yesButton)
                buttons = buttons & ~yesButton
                noButton = __getLowestFlag(buttons)
                noItem = __getGuiItem(noButton)
                cancelButton = int(buttons & ~noButton)
                cancelItem = __getGuiItem(cancelButton)
                res = KMessageBox.warningYesNoCancel(parent, text, title, 
                    yesItem, noItem, cancelItem)
                if res == KMessageBox.Yes:
                    return yesButton
                elif res == KMessageBox.No:
                    return noButton
                else:
                    return cancelButton
            
            raise RuntimeError("More than three buttons are not supported.")
        
        def __kdeCritical(parent, title, text, 
                          buttons = QMessageBox.Ok, defaultButton = QMessageBox.NoButton):
            """
            Function to show a modal critical message box.
            
            @param parent parent widget of the message box
            @param title caption of the message box
            @param text text to be shown by the message box
            @param buttons flags indicating which buttons to show 
                (QMessageBox.StandardButtons)
            @param defaultButton flag indicating the default button
                (QMessageBox.StandardButton)
            @return button pressed by the user (QMessageBox.StandardButton)
            """
            return warning(parent, title, text, buttons, defaultButton)
        
        def __kdeQuestion(parent, title, text, 
                          buttons = QMessageBox.Ok, defaultButton = QMessageBox.NoButton):
            """
            Function to show a modal critical message box.
            
            @param parent parent widget of the message box
            @param title caption of the message box
            @param text text to be shown by the message box
            @param buttons flags indicating which buttons to show 
                (QMessageBox.StandardButtons)
            @param defaultButton flag indicating the default button
                (QMessageBox.StandardButton)
            @return button pressed by the user (QMessageBox.StandardButton)
            """
            if __nrButtons(buttons) == 1:
                if defaultButton == QMessageBox.NoButton:
                    defaultButton = __getLowestFlag(buttons)
                yesButton = defaultButton
                yesItem = __getGuiItem(yesButton)
                KMessageBox.questionYesNo(parent, text, title, yesItem, KGuiItem())
                return yesButton
            
            if __nrButtons(buttons) == 2:
                if defaultButton == QMessageBox.NoButton:
                    defaultButton = __getLowestFlag(buttons)
                yesButton = defaultButton
                yesItem = __getGuiItem(yesButton)
                noButton = int(buttons & ~yesButton)
                noItem = __getGuiItem(noButton)
                res = KMessageBox.questionYesNo(parent, text, title, yesItem, noItem)
                if res == KMessageBox.Yes:
                    return yesButton
                else:
                    return noButton
            
            if __nrButtons(buttons) == 3:
                if defaultButton == QMessageBox.NoButton:
                    defaultButton = __getLowestFlag(buttons)
                yesButton = defaultButton
                yesItem = __getGuiItem(yesButton)
                buttons = buttons & ~yesButton
                noButton = __getLowestFlag(buttons)
                noItem = __getGuiItem(noButton)
                cancelButton = int(buttons & ~noButton)
                cancelItem = __getGuiItem(cancelButton)
                res = KMessageBox.questionYesNoCancel(parent, text, title, 
                    yesItem, noItem, cancelItem)
                if res == KMessageBox.Yes:
                    return yesButton
                elif res == KMessageBox.No:
                    return noButton
                else:
                    return cancelButton
            
            raise RuntimeError("More than three buttons are not supported.")
            
        def __kdeAbout(parent, title, text):
            """
            Function to show a modal about message box.
            
            @param parent parent widget of the message box
            @param title caption of the message box
            @param text text to be shown by the message box
            """
            KMessageBox.about(parent, text, title)

    except (ImportError, RuntimeError):
        sys.e4nokde = True

__qtAbout = QMessageBox.about
__qtAboutQt = QMessageBox.aboutQt

__qtInformation = QMessageBox.information
__qtWarning = QMessageBox.warning
__qtCritical = QMessageBox.critical
__qtQuestion = QMessageBox.question

################################################################################

KQMessageBox = QMessageBox

def information(parent, title, text, 
                buttons = QMessageBox.Ok, defaultButton = QMessageBox.NoButton):
    """
    Function to show a modal information message box.
    
    @param parent parent widget of the message box
    @param title caption of the message box
    @param text text to be shown by the message box
    @param buttons flags indicating which buttons to show 
        (QMessageBox.StandardButtons)
    @param defaultButton flag indicating the default button
        (QMessageBox.StandardButton)
    @return button pressed by the user 
        (QMessageBox.StandardButton, always QMessageBox.NoButton)
    """
    if Preferences.getUI("UseKDEDialogs") and not sys.e4nokde:
        return __kdeInformation(parent, title, text, buttons, defaultButton)
    else:
        return __qtInformation(parent, title, text, buttons, defaultButton)

def warning(parent, title, text, 
            buttons = QMessageBox.Ok, defaultButton = QMessageBox.NoButton):
    """
    Function to show a modal warning message box.
    
    @param parent parent widget of the message box
    @param title caption of the message box
    @param text text to be shown by the message box
    @param buttons flags indicating which buttons to show 
        (QMessageBox.StandardButtons)
    @param defaultButton flag indicating the default button
        (QMessageBox.StandardButton)
    @return button pressed by the user (QMessageBox.StandardButton)
    """
    if Preferences.getUI("UseKDEDialogs") and not sys.e4nokde:
        return __kdeWarning(parent, title, text, buttons, defaultButton)
    else:
        return __qtWarning(parent, title, text, buttons, defaultButton)

def critical(parent, title, text, 
            buttons = QMessageBox.Ok, defaultButton = QMessageBox.NoButton):
    """
    Function to show a modal critical message box.
    
    @param parent parent widget of the message box
    @param title caption of the message box
    @param text text to be shown by the message box
    @param buttons flags indicating which buttons to show 
        (QMessageBox.StandardButtons)
    @param defaultButton flag indicating the default button
        (QMessageBox.StandardButton)
    @return button pressed by the user (QMessageBox.StandardButton)
    """
    if Preferences.getUI("UseKDEDialogs") and not sys.e4nokde:
        return __kdeCritical(parent, title, text, buttons, defaultButton)
    else:
        return __qtCritical(parent, title, text, buttons, defaultButton)

def question(parent, title, text, 
            buttons = QMessageBox.Ok, defaultButton = QMessageBox.NoButton):
    """
    Function to show a modal critical message box.
    
    @param parent parent widget of the message box
    @param title caption of the message box
    @param text text to be shown by the message box
    @param buttons flags indicating which buttons to show 
        (QMessageBox.StandardButtons)
    @param defaultButton flag indicating the default button
        (QMessageBox.StandardButton)
    @return button pressed by the user (QMessageBox.StandardButton)
    """
    if Preferences.getUI("UseKDEDialogs") and not sys.e4nokde:
        return __kdeQuestion(parent, title, text, buttons, defaultButton)
    else:
        return __qtQuestion(parent, title, text, buttons, defaultButton)

def about(parent, title, text):
    """
    Function to show a modal about message box.
    
    @param parent parent widget of the message box
    @param title caption of the message box
    @param text text to be shown by the message box
    """
    if Preferences.getUI("UseKDEDialogs") and not sys.e4nokde:
        return __kdeAbout(parent, title, text)
    else:
        return __qtAbout(parent, title, text)

def aboutQt(parent, title):
    """
    Function to show a modal about message box.
    
    @param parent parent widget of the message box
    @param title caption of the message box
    """
    return __qtAboutQt(parent, title)
