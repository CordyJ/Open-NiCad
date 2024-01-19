# -*- coding: utf-8 -*-

# Copyright (c) 2007 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the exporter base class.
"""

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from KdeQt import KQFileDialog, KQMessageBox

import Utilities

class ExporterBase(QObject):
    """
    Class implementing the exporter base class.
    """
    def __init__(self, editor, parent = None):
        """
        Constructor
        
        @param editor reference to the editor object (QScintilla.Editor.Editor)
        @param parent parent object of the exporter (QObject)
        """
        QObject.__init__(self, parent)
        self.editor = editor
    
    def _getFileName(self, filter):
        """
        Protected method to get the file name of the export file from the user.
        
        @param filter the filter string to be used (QString). The filter for
            "All Files (*)" is appended by this method.
        """
        filter_ = QString(filter)
        filter_.append(";;")
        filter_.append(QApplication.translate('Exporter', "All Files (*)"))
        selectedFilter = QString()
        fn = KQFileDialog.getSaveFileName(\
            self.editor,
            self.trUtf8("Export source"),
            QString(),
            filter_,
            selectedFilter,
            QFileDialog.Options(QFileDialog.DontConfirmOverwrite))
        
        if not fn.isEmpty():
            ext = QFileInfo(fn).suffix()
            if ext.isEmpty():
                ex = selectedFilter.section('(*', 1, 1).section(')', 0, 0)
                if not ex.isEmpty():
                    fn.append(ex)
            if QFileInfo(fn).exists():
                res = KQMessageBox.warning(self.editor,
                    self.trUtf8("Export source"),
                    self.trUtf8("<p>The file <b>%1</b> already exists.</p>")
                        .arg(fn),
                    QMessageBox.StandardButtons(\
                        QMessageBox.Abort | \
                        QMessageBox.Save),
                    QMessageBox.Abort)
                if res == QMessageBox.Abort or res == QMessageBox.Cancel:
                    return QString()
            
            fn = Utilities.toNativeSeparators(fn)
        
        return fn
    
    def exportSource(self):
        """
        Public method performing the export.
        
        This method must be overridden by the real exporters.
        """
        raise NotImplementedError
