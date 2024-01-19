# -*- coding: utf-8 -*-

# Copyright (c) 2007 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing an exporter for TeX.
"""

# This code is a port of the C++ code found in SciTE 1.74
# Original code: Copyright 1998-2006 by Neil Hodgson <neilh@scintilla.org>

import os

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.Qsci import QsciScintilla

from KdeQt import KQMessageBox

from ExporterBase import ExporterBase

import Preferences

class ExporterTEX(ExporterBase):
    """
    Class implementing an exporter for TeX.
    """
    CHARZ = ord('z') - ord('a') + 1
    
    def __init__(self, editor, parent = None):
        """
        Constructor
        
        @param editor reference to the editor object (QScintilla.Editor.Editor)
        @param parent parent object of the exporter (QObject)
        """
        ExporterBase.__init__(self, editor, parent)
    
    def __getTexRGB(self, color):
        """
        Private method to convert a color object to a TeX color string
        
        @param color color object to convert (QColor)
        @return TeX color string (string)
        """
        # texcolor[rgb]{0,0.5,0}{....}
        rf = color.red() / 256.0
        gf = color.green() / 256.0
        bf = color.blue() / 256.0
        
        # avoid breakage due to locale setting
        r = int(rf * 10 + 0.5)
        g = int(gf * 10 + 0.5)
        b = int(bf * 10 + 0.5)
        
        return "%d.%d, %d.%d, %d.%d" % (r / 10, r % 10, g / 10, g % 10, b / 10, b % 10)
    
    def __texStyle(self, style):
        """
        Private method to calculate a style name string for a given style number.
        
        @param style style number (integer)
        @return style name string (string)
        """
        buf = ""
        if style == 0:
            buf = "a"
        else:
            while style > 0:
                buf += chr(ord('a') + (style % self.CHARZ))
                style /= self.CHARZ
        return buf
    
    def __defineTexStyle(self, font, color, paper, file, istyle):
        """
        Private method to define a new TeX style.
        
        @param font the font to be used (QFont)
        @param color the foreground color to be used (QColor)
        @param paper the background color to be used (QColor)
        @param file reference to the open file to write to (file object)
        @param istyle style number (integer)
        """
        closing_brackets = 3
        file.write("\\newcommand{\\eric%s}[1]{\\noindent{\\ttfamily{" % \
                   self.__texStyle(istyle))
        if font.italic():
            file.write("\\textit{")
            closing_brackets += 1
        if font.bold():
            file.write("\\textbf{")
            closing_brackets += 1
        if color != self.defaultColor:
            file.write("\\textcolor[rgb]{%s}{" % self.__getTexRGB(color))
            closing_brackets += 1
        if paper != self.defaultPaper:
            file.write("\\colorbox[rgb]{%s}{" % self.__getTexRGB(paper))
            closing_brackets += 1
        file.write("#1%s\n" % ('}' * closing_brackets))
    
    def exportSource(self):
        """
        Public method performing the export.
        """
        filename = self._getFileName(self.trUtf8("TeX Files (*.tex)"))
        if filename.isEmpty():
            return
        else:
            filename = unicode(filename)
        
        try:
            QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
            QApplication.processEvents()
            
            self.editor.recolor(0, -1)
            
            tabSize = Preferences.getEditor("TabWidth")
            if tabSize == 0:
                tabSize = 4
            
            onlyStylesUsed = Preferences.getEditorExporter("TeX/OnlyStylesUsed")
            titleFullPath = Preferences.getEditorExporter("TeX/FullPathAsTitle")
            
            lex = self.editor.getLexer()
            self.defaultPaper = lex and \
                                lex.paper(QsciScintilla.STYLE_DEFAULT) or \
                                self.editor.paper().name()
            self.defaultColor = lex and \
                                lex.color(QsciScintilla.STYLE_DEFAULT) or \
                                self.editor.color().name()
            self.defaultFont = lex and \
                                lex.color(QsciScintilla.STYLE_DEFAULT) or \
                                Preferences.getEditorOtherFonts("DefaultFont")
            
            lengthDoc = self.editor.length()
            styleIsUsed = {}
            if onlyStylesUsed:
                for index in range(QsciScintilla.STYLE_MAX + 1):
                    styleIsUsed[index] = False
                # check the used styles
                pos = 0
                while pos < lengthDoc:
                    styleIsUsed[self.editor.styleAt(pos) & 0x7F] = True
                    pos += 1
            else:
                for index in range(QsciScintilla.STYLE_MAX + 1):
                    styleIsUsed[index] = True
            styleIsUsed[QsciScintilla.STYLE_DEFAULT] = True
            
            try:
                f = open(filename, "wb")
                
                f.write("\\documentclass[a4paper]{article}\n")
                f.write("\\usepackage[a4paper,margin=1.5cm]{geometry}\n")
                f.write("\\usepackage[T1]{fontenc}\n")
                f.write("\\usepackage{color}\n")
                f.write("\\usepackage{alltt}\n")
                f.write("\\usepackage{times}\n")
                if self.editor.isUtf8():
                    f.write("\\usepackage[utf8]{inputenc}\n")
                else:
                    f.write("\\usepackage[latin1]{inputenc}\n")
                
                if lex:
                    istyle = 0
                    while istyle <= QsciScintilla.STYLE_MAX:
                        if (istyle <= QsciScintilla.STYLE_DEFAULT or \
                            istyle > QsciScintilla.STYLE_LASTPREDEFINED) and \
                           styleIsUsed[istyle]:
                            if not lex.description(istyle).isEmpty() or \
                               istyle == QsciScintilla.STYLE_DEFAULT:
                                font = lex.font(istyle)
                                colour = lex.color(istyle)
                                paper = lex.paper(istyle)
                                
                                self.__defineTexStyle(font, colour, paper, f, istyle)
                        istyle += 1
                else:
                    colour = self.editor.color()
                    paper = self.editor.paper()
                    font = Preferences.getEditorOtherFonts("DefaultFont")
                    
                    self.__defineTexStyle(font, colour, paper, f, 0)
                    self.__defineTexStyle(font, colour, paper, f, 
                                          QsciScintilla.STYLE_DEFAULT)
                
                f.write("\\begin{document}\n\n")
                if titleFullPath:
                    title = self.editor.getFileName()
                else:
                    title = os.path.basename(self.editor.getFileName())
                f.write("Source File: %s\n\n\\noindent\n\\tiny{\n" % title)
                
                styleCurrent = self.editor.styleAt(0)
                f.write("\\eric%s{" % self.__texStyle(styleCurrent))
                
                lineIdx = 0
                pos = 0
                
                while pos < lengthDoc:
                    ch = self.editor.rawCharAt(pos)
                    style = self.editor.styleAt(pos)
                    if style != styleCurrent:
                        # new style
                        f.write("}\n\\eric%s{" % self.__texStyle(style))
                        styleCurrent = style
                    
                    if ch == '\t':
                        ts = tabSize - (lineIdx % tabSize)
                        lineIdx += ts - 1
                        f.write("\\hspace*{%dem}" % ts)
                    elif ch == '\\':
                        f.write("{\\textbackslash}")
                    elif ch in ['>', '<', '@']:
                        f.write("$%c$" % ch)
                    elif ch in ['{', '}', '^', '_', '&', '$', '#', '%', '~']:
                        f.write("\\%c" % ch)
                    elif ch in ['\r', '\n']:
                        lineIdx = -1    # because incremented below
                        if ch == '\r' and self.editor.rawCharAt(pos + 1) == '\n':
                            pos += 1    # skip the LF
                        styleCurrent = self.editor.styleAt(pos + 1)
                        f.write("} \\\\\n\\eric%s{" % self.__texStyle(styleCurrent))
                    elif ch == ' ':
                        if self.editor.rawCharAt(pos + 1) == ' ':
                            f.write("{\\hspace*{1em}}")
                        else:
                            f.write(' ')
                    else:
                        f.write(ch)
                    lineIdx += 1
                    pos += 1
                
                # close last empty style macros and document too
                f.write("}\n} %end tiny\n\n\\end{document}\n")
                f.close()
            except IOError, err:
                QApplication.restoreOverrideCursor()
                KQMessageBox.critical(self.editor,
                    self.trUtf8("Export source"),
                    self.trUtf8(\
                        """<p>The source could not be exported to <b>%1</b>.</p>"""
                        """<p>Reason: %2</p>""")\
                        .arg(filename).arg(unicode(err)),
                    QMessageBox.StandardButtons(\
                        QMessageBox.Ok))
        finally:
            QApplication.restoreOverrideCursor()
