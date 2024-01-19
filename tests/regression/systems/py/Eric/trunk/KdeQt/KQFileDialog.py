# -*- coding: utf-8 -*-

# Copyright (c) 2004 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Compatibility module to use the KDE File Dialog instead of the Qt File Dialog.
"""

import sys

from PyQt4.QtCore import QString, QStringList, QDir
from PyQt4.QtGui import QFileDialog

import Preferences

if Preferences.getUI("UseKDEDialogs") and not sys.e4nokde:
    try:
        from PyKDE4.kio import KFileDialog, KFile
        from PyKDE4.kdecore import KUrl
        from PyQt4.QtCore import QRegExp, QFileInfo
        from PyQt4.QtGui import QApplication
        
        def __convertFilter(filter, selectedFilter = None):
            """
            Private function to convert a Qt file filter to a KDE file filter.
            
            @param filter Qt file filter (QString or string)
            @param selectedFilter this is set to the selected filter
            @return the corresponding KDE file filter (QString)
            """
            rx = QRegExp("^[^(]*\(([^)]*)\).*$")
            fileFilters = filter.split(';;')
            
            newfilter = QStringList()
            for fileFilter in fileFilters:
                sf = selectedFilter and selectedFilter.compare(fileFilter) == 0
                namefilter = QString(fileFilter).replace(rx, "\\1")
                fileFilter = QString(fileFilter).replace('/', '\\/')
                if sf:
                    newfilter.prepend("%s|%s" % (namefilter, fileFilter))
                else:
                    newfilter.append("%s|%s" % (namefilter, fileFilter))
            return newfilter.join('\n')
        
        def __workingDirectory(path_):
            """
            Private function to determine working directory for the file dialog.
            
            @param path_ path of the intended working directory (string or QString)
            @return calculated working directory (QString)
            """
            path = QString(path_)
            if not path.isEmpty():
                info = QFileInfo(path)
                if info.exists() and info.isDir():
                    return info.absoluteFilePath()
                return info.absolutePath()
            return QDir.currentPath()
        
        def __kdeGetOpenFileName(parent = None, caption = QString(), dir_ = QString(),
                                 filter = QString(), selectedFilter = None, 
                                 options = QFileDialog.Options()):
            """
            Module function to get the name of a file for opening it.
            
            @param parent parent widget of the dialog (QWidget)
            @param caption window title of the dialog (QString)
            @param dir_ working directory of the dialog (QString)
            @param filter filter string for the dialog (QString)
            @param selectedFilter selected filter for the dialog (QString)
            @param options various options for the dialog (QFileDialog.Options)
            @return name of file to be opened (QString)
            """
            if not QString(filter).isEmpty():
                filter = __convertFilter(filter, selectedFilter)
            wdir = __workingDirectory(dir_)
            dlg = KFileDialog(KUrl.fromPath(wdir), filter, parent)
            dlg.setOperationMode(KFileDialog.Opening)
            dlg.setMode(KFile.Modes(KFile.File) | KFile.Modes(KFile.LocalOnly))
            dlg.setWindowTitle(caption.isEmpty() and \
                QApplication.translate('KFileDialog', 'Open') or caption)
            
            dlg.exec_()
            
            if selectedFilter is not None:
                flt = dlg.currentFilter()
                flt.prepend("(").append(")")
                selectedFilter.replace(0, selectedFilter.length(), flt)
            
            return dlg.selectedFile()
        
        def __kdeGetSaveFileName(parent = None, caption = QString(), dir_ = QString(),
                                 filter = QString(), selectedFilter = None, 
                                 options = QFileDialog.Options()):
            """
            Module function to get the name of a file for saving it.
            
            @param parent parent widget of the dialog (QWidget)
            @param caption window title of the dialog (QString)
            @param dir_ working directory of the dialog (QString)
            @param filter filter string for the dialog (QString)
            @param selectedFilter selected filter for the dialog (QString)
            @param options various options for the dialog (QFileDialog.Options)
            @return name of file to be saved (QString)
            """
            if not QString(filter).isEmpty():
                filter = __convertFilter(filter, selectedFilter)
            wdir = __workingDirectory(dir_)
            dlg = KFileDialog(KUrl.fromPath(wdir), filter, parent)
            dlg.setSelection(dir_)
            dlg.setOperationMode(KFileDialog.Saving)
            dlg.setMode(KFile.Modes(KFile.File) | KFile.Modes(KFile.LocalOnly))
            dlg.setWindowTitle(caption.isEmpty() and \
                QApplication.translate('KFileDialog', 'Save As') or caption)
            
            dlg.exec_()
            
            if selectedFilter is not None:
                flt = dlg.currentFilter()
                flt.prepend("(").append(")")
                selectedFilter.replace(0, selectedFilter.length(), flt)
            
            return dlg.selectedFile()
            
        def __kdeGetOpenFileNames(parent = None, caption = QString(), dir_ = QString(),
                                  filter = QString(), selectedFilter = None, 
                                  options = QFileDialog.Options()):
            """
            Module function to get a list of names of files for opening.
            
            @param parent parent widget of the dialog (QWidget)
            @param caption window title of the dialog (QString)
            @param dir_ working directory of the dialog (QString)
            @param filter filter string for the dialog (QString)
            @param selectedFilter selected filter for the dialog (QString)
            @param options various options for the dialog (QFileDialog.Options)
            @return list of filenames to be opened (QStringList)
            """
            if not QString(filter).isEmpty():
                filter = __convertFilter(filter, selectedFilter)
            wdir = __workingDirectory(dir_)
            dlg = KFileDialog(KUrl.fromPath(wdir), filter, parent)
            dlg.setOperationMode(KFileDialog.Opening)
            dlg.setMode(KFile.Modes(KFile.Files) | KFile.Modes(KFile.LocalOnly))
            dlg.setWindowTitle(caption.isEmpty() and \
                QApplication.translate('KFileDialog', 'Open') or caption)
            
            dlg.exec_()
            
            if selectedFilter is not None:
                flt = dlg.currentFilter()
                flt.prepend("(").append(")")
                selectedFilter.replace(0, selectedFilter.length(), flt)
                
            return dlg.selectedFiles()
        
        def __kdeGetExistingDirectory(parent = None, caption = QString(), dir_ = QString(),
                                    options = QFileDialog.Options(QFileDialog.ShowDirsOnly)):
            """
            Module function to get the name of a directory.
            
            @param parent parent widget of the dialog (QWidget)
            @param caption window title of the dialog (QString)
            @param dir_ working directory of the dialog (QString)
            @param options various options for the dialog (QFileDialog.Options)
            @return name of selected directory (QString)
            """
            wdir = __workingDirectory(dir_)
            dlg = KFileDialog(KUrl.fromPath(wdir), QString(), parent)
            dlg.setOperationMode(KFileDialog.Opening)
            dlg.setMode(KFile.Modes(KFile.Directory) | KFile.Modes(KFile.LocalOnly) | \
                        KFile.Modes(KFile.ExistingOnly))
            dlg.setWindowTitle(caption.isEmpty() and \
                QApplication.translate('KFileDialog', 'Select Directory') or caption)
            
            dlg.exec_()
            
            return dlg.selectedFile()
        
    except (ImportError, RuntimeError):
        sys.e4nokde = True
    
__qtGetOpenFileName = QFileDialog.getOpenFileName
__qtGetOpenFileNames = QFileDialog.getOpenFileNames
__qtGetSaveFileName = QFileDialog.getSaveFileName
__qtGetExistingDirectory = QFileDialog.getExistingDirectory

################################################################################

def getOpenFileName(parent = None, caption = QString(), dir_ = QString(),
                    filter = QString(), selectedFilter = None, 
                    options = QFileDialog.Options()):
    """
    Module function to get the name of a file for opening it.
    
    @param parent parent widget of the dialog (QWidget)
    @param caption window title of the dialog (QString)
    @param dir_ working directory of the dialog (QString)
    @param filter filter string for the dialog (QString)
    @param selectedFilter selected filter for the dialog (QString)
    @param options various options for the dialog (QFileDialog.Options)
    @return name of file to be opened (QString)
    """
    if Preferences.getUI("UseKDEDialogs") and not sys.e4nokde:
        f = __kdeGetOpenFileName(parent, caption, dir_, 
                                filter, selectedFilter, options)
    else:
        f = __qtGetOpenFileName(parent, caption, dir_, 
                                filter, selectedFilter, options)
    return QDir.toNativeSeparators(f)
    
def getOpenFileNames(parent = None, caption = QString(), dir_ = QString(),
                    filter = QString(), selectedFilter = None, 
                    options = QFileDialog.Options()):
    """
    Module function to get a list of names of files for opening.
    
    @param parent parent widget of the dialog (QWidget)
    @param caption window title of the dialog (QString)
    @param dir_ working directory of the dialog (QString)
    @param filter filter string for the dialog (QString)
    @param selectedFilter selected filter for the dialog (QString)
    @param options various options for the dialog (QFileDialog.Options)
    @return list of filenames to be opened (QStringList)
    """
    if Preferences.getUI("UseKDEDialogs") and not sys.e4nokde:
        l = __kdeGetOpenFileNames(parent, caption, dir_, 
                                  filter, selectedFilter, options)
    else:
        l =  __qtGetOpenFileNames(parent, caption, dir_, 
                                  filter, selectedFilter, options)
    fl = QStringList()
    for f in l:
        fl.append(QDir.toNativeSeparators(f))
    return fl
    
def getSaveFileName(parent = None, caption = QString(), dir_ = QString(),
                    filter = QString(), selectedFilter = None, 
                    options = QFileDialog.Options()):
    """
    Module function to get the name of a file for saving it.
    
    @param parent parent widget of the dialog (QWidget)
    @param caption window title of the dialog (QString)
    @param dir_ working directory of the dialog (QString)
    @param filter filter string for the dialog (QString)
    @param selectedFilter selected filter for the dialog (QString)
    @param options various options for the dialog (QFileDialog.Options)
    @return name of file to be saved (QString)
    """
    if Preferences.getUI("UseKDEDialogs") and not sys.e4nokde:
        f = __kdeGetSaveFileName(parent, caption, dir_, 
                                 filter, selectedFilter, options)
    else:
        f = __qtGetSaveFileName(parent, caption, dir_, 
                                filter, selectedFilter, options)
    return QDir.toNativeSeparators(f)
    
def getExistingDirectory(parent = None, caption = QString(), dir_ = QString(),
                         options = QFileDialog.Options(QFileDialog.ShowDirsOnly)):
    """
    Module function to get the name of a directory.
    
    @param parent parent widget of the dialog (QWidget)
    @param caption window title of the dialog (QString)
    @param dir_ working directory of the dialog (QString)
    @param options various options for the dialog (QFileDialog.Options)
    @return name of selected directory (QString)
    """
    if Preferences.getUI("UseKDEDialogs") and not sys.e4nokde:
        d = __kdeGetExistingDirectory(parent, caption, dir_, options)
    else:
        d = __qtGetExistingDirectory(parent, caption, dir_, options)
    return QDir.toNativeSeparators(d)
