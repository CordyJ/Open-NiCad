# -*- coding: utf-8 -*-

# Copyright (c) 2002 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the icon editor main window.
"""

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from KdeQt import KQMessageBox, KQFileDialog
from KdeQt.KQMainWindow import KQMainWindow
import KdeQt

from E4Gui.E4Action import E4Action, createActionGroup

from IconEditorGrid import IconEditorGrid
from IconZoomDialog import IconZoomDialog
from IconEditorPalette import IconEditorPalette

import UI.PixmapCache
import UI.Config

import Preferences

from eric4config import getConfig

class IconEditorWindow(KQMainWindow):
    """
    Class implementing the web browser main window.
    
    @signal editorClosed() emitted after the window was requested to close down
    """
    windows = []
    
    def __init__(self, fileName = "", parent = None, fromEric = False, 
                 initShortcutsOnly = False):
        """
        Constructor
        
        @param fileName name of a file to load on startup (string or QString)
        @param parent parent widget of this window (QWidget)
        @keyparam fromEric flag indicating whether it was called from within eric4 (boolean)
        @keyparam initShortcutsOnly flag indicating to just initialize the keyboard
            shortcuts (boolean)
        """
        KQMainWindow.__init__(self, parent)
        self.setObjectName("eric4_icon_editor")
        self.setAttribute(Qt.WA_DeleteOnClose)
        
        self.fromEric = fromEric
        self.initShortcutsOnly = initShortcutsOnly
        self.setWindowIcon(UI.PixmapCache.getIcon("iconEditor.png"))
        
        if self.initShortcutsOnly:
            self.__initActions()
        else:
            self.__editor = IconEditorGrid()
            self.__scrollArea = QScrollArea()
            self.__scrollArea.setWidget(self.__editor)
            self.__scrollArea.viewport().setBackgroundRole(QPalette.Dark)
            self.__scrollArea.viewport().setAutoFillBackground(True)
            self.setCentralWidget(self.__scrollArea)
            
            g = Preferences.getGeometry("IconEditorGeometry")
            if g.isEmpty():
                s = QSize(600, 500)
                self.resize(s)
            else:
                self.restoreGeometry(g)
            
            self.__initActions()
            self.__initMenus()
            self.__initToolbars()
            self.__createStatusBar()
            self.__initFileFilters()
            self.__createPaletteDock()
            
            self.__palette.previewChanged(self.__editor.previewPixmap())
            self.__palette.colorChanged(self.__editor.penColor())
            
            self.__class__.windows.append(self)
            
            state = Preferences.getIconEditor("IconEditorState")
            self.restoreState(state)
            
            self.connect(self.__editor, SIGNAL("imageChanged(bool)"), 
                         self.__modificationChanged)
            self.connect(self.__editor, SIGNAL("positionChanged(int, int)"), 
                         self.__updatePosition)
            self.connect(self.__editor, SIGNAL("sizeChanged(int, int)"), 
                         self.__updateSize)
            self.connect(self.__editor, SIGNAL("previewChanged(const QPixmap&)"), 
                         self.__palette.previewChanged)
            self.connect(self.__editor, SIGNAL("colorChanged(const QColor&)"), 
                         self.__palette.colorChanged)
            self.connect(self.__palette, SIGNAL("colorSelected(QColor)"), 
                         self.__editor.setPenColor)
            
            self.__setCurrentFile(QString(""))
            if fileName:
                self.__loadIconFile(fileName)
            
            self.__checkActions()
    
    def __initFileFilters(self):
        """
        Private method to define the supported image file filters.
        """
        filters = {
            'bmp' : self.trUtf8("Windows Bitmap File (*.bmp)"), 
            'gif' : self.trUtf8("Graphic Interchange Format File (*.gif)"), 
            'ico' : self.trUtf8("Windows Icon File (*.ico)"), 
            'jpg' : self.trUtf8("JPEG File (*.jpg)"), 
            'mng' : self.trUtf8("Multiple-Image Network Graphics File (*.mng)"), 
            'pbm' : self.trUtf8("Portable Bitmap File (*.pbm)"), 
            'pgm' : self.trUtf8("Portable Graymap File (*.pgm)"), 
            'png' : self.trUtf8("Portable Network Graphics File (*.png)"), 
            'ppm' : self.trUtf8("Portable Pixmap File (*.ppm)"), 
            'svg' : self.trUtf8("Scalable Vector Graphics File (*.svg)"), 
            'tif' : self.trUtf8("TIFF File (*.tif)"), 
            'xbm' : self.trUtf8("X11 Bitmap File (*.xbm)"), 
            'xpm' : self.trUtf8("X11 Pixmap File (*.xpm)"), 
        }
        
        inputFormats = []
        readFormats = QImageReader.supportedImageFormats()
        for readFormat in readFormats:
            try:
                inputFormats.append(unicode(filters[unicode(readFormat)]))
            except KeyError:
                pass
        inputFormats.sort()
        inputFormats.append(unicode(self.trUtf8("All Files (*)")))
        self.__inputFilter = ';;'.join(inputFormats)
        
        outputFormats = []
        writeFormats = QImageWriter.supportedImageFormats()
        for writeFormat in writeFormats:
            try:
                outputFormats.append(unicode(filters[unicode(writeFormat)]))
            except KeyError:
                pass
        outputFormats.sort()
        self.__outputFilter = ';;'.join(outputFormats)
        
        self.__defaultFilter = filters['png']
    
    def __initActions(self):
        """
        Private method to define the user interface actions.
        """
        # list of all actions
        self.__actions = []
        
        self.__initFileActions()
        self.__initEditActions()
        self.__initViewActions()
        self.__initToolsActions()
        self.__initHelpActions()
        
    def __initFileActions(self):
        """
        Private method to define the file related user interface actions.
        """
        self.newAct = E4Action(self.trUtf8('New'), 
            UI.PixmapCache.getIcon("new.png"),
            self.trUtf8('&New'), 
            QKeySequence(self.trUtf8("Ctrl+N","File|New")), 
            0, self, 'iconEditor_file_new')
        self.newAct.setStatusTip(self.trUtf8('Create a new icon'))
        self.newAct.setWhatsThis(self.trUtf8(
                """<b>New</b>"""
                """<p>This creates a new icon.</p>"""
        ))
        self.connect(self.newAct, SIGNAL('triggered()'), self.__newIcon)
        self.__actions.append(self.newAct)
        
        self.newWindowAct = E4Action(self.trUtf8('New Window'), 
            UI.PixmapCache.getIcon("newWindow.png"),
            self.trUtf8('New &Window'), 
            0, 0, self, 'iconEditor_file_new_window')
        self.newWindowAct.setStatusTip(self.trUtf8('Open a new icon editor window'))
        self.newWindowAct.setWhatsThis(self.trUtf8(
                """<b>New Window</b>"""
                """<p>This opens a new icon editor window.</p>"""
        ))
        self.connect(self.newWindowAct, SIGNAL('triggered()'), self.__newWindow)
        self.__actions.append(self.newWindowAct)
        
        self.openAct = E4Action(self.trUtf8('Open'), 
            UI.PixmapCache.getIcon("open.png"),
            self.trUtf8('&Open...'), 
            QKeySequence(self.trUtf8("Ctrl+O","File|Open")), 
            0, self, 'iconEditor_file_open')
        self.openAct.setStatusTip(self.trUtf8('Open an icon file for editing'))
        self.openAct.setWhatsThis(self.trUtf8(
                """<b>Open File</b>"""
                """<p>This opens a new icon file for editing."""
                """ It pops up a file selection dialog.</p>"""
        ))
        self.connect(self.openAct, SIGNAL('triggered()'), self.__openIcon)
        self.__actions.append(self.openAct)
        
        self.saveAct = E4Action(self.trUtf8('Save'),
                UI.PixmapCache.getIcon("fileSave.png"),
                self.trUtf8('&Save'),
                QKeySequence(self.trUtf8("Ctrl+S", "File|Save")), 
                0, self, 'iconEditor_file_save')
        self.saveAct.setStatusTip(self.trUtf8('Save the current icon'))
        self.saveAct.setWhatsThis(self.trUtf8(
            """<b>Save File</b>"""
            """<p>Save the contents of the icon editor window.</p>"""
        ))
        self.connect(self.saveAct, SIGNAL('triggered()'), self.__saveIcon)
        self.__actions.append(self.saveAct)
        
        self.saveAsAct = E4Action(self.trUtf8('Save As'), 
            UI.PixmapCache.getIcon("fileSaveAs.png"),
            self.trUtf8('Save &As...'), 
            QKeySequence(self.trUtf8("Shift+Ctrl+S","File|Save As")), 
            0, self, 'iconEditor_file_save_as')
        self.saveAsAct.setStatusTip(\
            self.trUtf8('Save the current icon to a new file'))
        self.saveAsAct.setWhatsThis(self.trUtf8(
                """<b>Save As...</b>"""
                """<p>Saves the current icon to a new file.</p>"""
        ))
        self.connect(self.saveAsAct, SIGNAL('triggered()'), self.__saveIconAs)
        self.__actions.append(self.saveAsAct)
        
        self.closeAct = E4Action(self.trUtf8('Close'), 
            UI.PixmapCache.getIcon("close.png"),
            self.trUtf8('&Close'), 
            QKeySequence(self.trUtf8("Ctrl+W","File|Close")), 
            0, self, 'iconEditor_file_close')
        self.closeAct.setStatusTip(self.trUtf8('Close the current icon editor window'))
        self.closeAct.setWhatsThis(self.trUtf8(
                """<b>Close</b>"""
                """<p>Closes the current icon editor window.</p>"""
        ))
        self.connect(self.closeAct, SIGNAL('triggered()'), self.close)
        self.__actions.append(self.closeAct)
        
        self.closeAllAct = E4Action(self.trUtf8('Close All'), 
            self.trUtf8('Close &All'), 
            0, 0, self, 'iconEditor_file_close_all')
        self.closeAllAct.setStatusTip(self.trUtf8('Close all icon editor windows'))
        self.closeAllAct.setWhatsThis(self.trUtf8(
                """<b>Close All</b>"""
                """<p>Closes all icon editor windows except the first one.</p>"""
        ))
        self.connect(self.closeAllAct, SIGNAL('triggered()'), self.__closeAll)
        self.__actions.append(self.closeAllAct)
        
        self.exitAct = E4Action(self.trUtf8('Quit'), 
            UI.PixmapCache.getIcon("exit.png"),
            self.trUtf8('&Quit'), 
            QKeySequence(self.trUtf8("Ctrl+Q","File|Quit")), 
            0, self, 'iconEditor_file_quit')
        self.exitAct.setStatusTip(self.trUtf8('Quit the icon editor'))
        self.exitAct.setWhatsThis(self.trUtf8(
                """<b>Quit</b>"""
                """<p>Quit the icon editor.</p>"""
        ))
        if self.fromEric:
            self.connect(self.exitAct, SIGNAL('triggered()'), self.close)
        else:
            self.connect(self.exitAct, SIGNAL('triggered()'), 
                         qApp, SLOT('closeAllWindows()'))
        self.__actions.append(self.exitAct)
    
    def __initEditActions(self):
        """
        Private method to create the Edit actions.
        """
        self.undoAct = E4Action(self.trUtf8('Undo'),
                UI.PixmapCache.getIcon("editUndo.png"),
                self.trUtf8('&Undo'),
                QKeySequence(self.trUtf8("Ctrl+Z", "Edit|Undo")), 
                QKeySequence(self.trUtf8("Alt+Backspace", "Edit|Undo")), 
                self, 'iconEditor_edit_undo')
        self.undoAct.setStatusTip(self.trUtf8('Undo the last change'))
        self.undoAct.setWhatsThis(self.trUtf8(\
            """<b>Undo</b>"""
            """<p>Undo the last change done.</p>"""
        ))
        self.connect(self.undoAct, SIGNAL('triggered()'), self.__editor.editUndo)
        self.__actions.append(self.undoAct)
        
        self.redoAct = E4Action(self.trUtf8('Redo'),
                UI.PixmapCache.getIcon("editRedo.png"),
                self.trUtf8('&Redo'),
                QKeySequence(self.trUtf8("Ctrl+Shift+Z", "Edit|Redo")), 
                0, self, 'iconEditor_edit_redo')
        self.redoAct.setStatusTip(self.trUtf8('Redo the last change'))
        self.redoAct.setWhatsThis(self.trUtf8(\
            """<b>Redo</b>"""
            """<p>Redo the last change done.</p>"""
        ))
        self.connect(self.redoAct, SIGNAL('triggered()'), self.__editor.editRedo)
        self.__actions.append(self.redoAct)
        
        self.cutAct = E4Action(self.trUtf8('Cut'),
                UI.PixmapCache.getIcon("editCut.png"),
                self.trUtf8('Cu&t'),
                QKeySequence(self.trUtf8("Ctrl+X", "Edit|Cut")),
                QKeySequence(self.trUtf8("Shift+Del", "Edit|Cut")),
                self, 'iconEditor_edit_cut')
        self.cutAct.setStatusTip(self.trUtf8('Cut the selection'))
        self.cutAct.setWhatsThis(self.trUtf8(\
            """<b>Cut</b>"""
            """<p>Cut the selected image area to the clipboard.</p>"""
        ))
        self.connect(self.cutAct, SIGNAL('triggered()'), self.__editor.editCut)
        self.__actions.append(self.cutAct)
        
        self.copyAct = E4Action(self.trUtf8('Copy'),
                UI.PixmapCache.getIcon("editCopy.png"),
                self.trUtf8('&Copy'),
                QKeySequence(self.trUtf8("Ctrl+C", "Edit|Copy")), 
                QKeySequence(self.trUtf8("Ctrl+Ins", "Edit|Copy")), 
                self, 'iconEditor_edit_copy')
        self.copyAct.setStatusTip(self.trUtf8('Copy the selection'))
        self.copyAct.setWhatsThis(self.trUtf8(\
            """<b>Copy</b>"""
            """<p>Copy the selected image area to the clipboard.</p>"""
        ))
        self.connect(self.copyAct, SIGNAL('triggered()'), self.__editor.editCopy)
        self.__actions.append(self.copyAct)
        
        self.pasteAct = E4Action(self.trUtf8('Paste'),
                UI.PixmapCache.getIcon("editPaste.png"),
                self.trUtf8('&Paste'),
                QKeySequence(self.trUtf8("Ctrl+V", "Edit|Paste")), 
                QKeySequence(self.trUtf8("Shift+Ins", "Edit|Paste")), 
                self, 'iconEditor_edit_paste')
        self.pasteAct.setStatusTip(self.trUtf8('Paste the clipboard image'))
        self.pasteAct.setWhatsThis(self.trUtf8(\
            """<b>Paste</b>"""
            """<p>Paste the clipboard image.</p>"""
        ))
        self.connect(self.pasteAct, SIGNAL('triggered()'), self.__editor.editPaste)
        self.__actions.append(self.pasteAct)
        
        self.pasteNewAct = E4Action(self.trUtf8('Paste as New'),
                self.trUtf8('Paste as &New'),
                0, 0, self, 'iconEditor_edit_paste_as_new')
        self.pasteNewAct.setStatusTip(self.trUtf8(
            'Paste the clipboard image replacing the current one'))
        self.pasteNewAct.setWhatsThis(self.trUtf8(\
            """<b>Paste as New</b>"""
            """<p>Paste the clipboard image replacing the current one.</p>"""
        ))
        self.connect(self.pasteNewAct, SIGNAL('triggered()'), self.__editor.editPasteAsNew)
        self.__actions.append(self.pasteNewAct)
        
        self.deleteAct = E4Action(self.trUtf8('Clear'),
                UI.PixmapCache.getIcon("editDelete.png"),
                self.trUtf8('Cl&ear'),
                QKeySequence(self.trUtf8("Alt+Shift+C", "Edit|Clear")), 
                0,
                self, 'iconEditor_edit_clear')
        self.deleteAct.setStatusTip(self.trUtf8('Clear the icon image'))
        self.deleteAct.setWhatsThis(self.trUtf8(\
            """<b>Clear</b>"""
            """<p>Clear the icon image and set it to be completely transparent.</p>"""
        ))
        self.connect(self.deleteAct, SIGNAL('triggered()'), self.__editor.editClear)
        self.__actions.append(self.deleteAct)
        
        self.selectAllAct = E4Action(self.trUtf8('Select All'),
                self.trUtf8('&Select All'),
                QKeySequence(self.trUtf8("Ctrl+A", "Edit|Select All")), 
                0,
                self, 'iconEditor_edit_select_all')
        self.selectAllAct.setStatusTip(self.trUtf8('Select the complete icon image'))
        self.selectAllAct.setWhatsThis(self.trUtf8(\
            """<b>Select All</b>"""
            """<p>Selects the complete icon image.</p>"""
        ))
        self.connect(self.selectAllAct, SIGNAL('triggered()'), self.__editor.editSelectAll)
        self.__actions.append(self.selectAllAct)
        
        self.resizeAct = E4Action(self.trUtf8('Change Size'),
                UI.PixmapCache.getIcon("transformResize.png"),
                self.trUtf8('Change Si&ze...'),
                0, 0,
                self, 'iconEditor_edit_change_size')
        self.resizeAct.setStatusTip(self.trUtf8('Change the icon size'))
        self.resizeAct.setWhatsThis(self.trUtf8(\
            """<b>Change Size...</b>"""
            """<p>Changes the icon size.</p>"""
        ))
        self.connect(self.resizeAct, SIGNAL('triggered()'), self.__editor.editResize)
        self.__actions.append(self.resizeAct)
        
        self.grayscaleAct = E4Action(self.trUtf8('Grayscale'),
                UI.PixmapCache.getIcon("grayscale.png"),
                self.trUtf8('&Grayscale'),
                0, 0,
                self, 'iconEditor_edit_grayscale')
        self.grayscaleAct.setStatusTip(self.trUtf8('Change the icon to grayscale'))
        self.grayscaleAct.setWhatsThis(self.trUtf8(\
            """<b>Grayscale</b>"""
            """<p>Changes the icon to grayscale.</p>"""
        ))
        self.connect(self.grayscaleAct, SIGNAL('triggered()'), self.__editor.grayScale)
        self.__actions.append(self.grayscaleAct)
        
        self.redoAct.setEnabled(False)
        self.connect(self.__editor, SIGNAL("canRedoChanged(bool)"), 
                     self.redoAct, SLOT("setEnabled(bool)"))
        
        self.undoAct.setEnabled(False)
        self.connect(self.__editor, SIGNAL("canUndoChanged(bool)"), 
                     self.undoAct, SLOT("setEnabled(bool)"))
        
        self.cutAct.setEnabled(False)
        self.copyAct.setEnabled(False)
        self.connect(self.__editor, SIGNAL("selectionAvailable(bool)"), 
                     self.cutAct, SLOT("setEnabled(bool)"))
        self.connect(self.__editor, SIGNAL("selectionAvailable(bool)"), 
                     self.copyAct, SLOT("setEnabled(bool)"))
        
        self.pasteAct.setEnabled(self.__editor.canPaste())
        self.pasteNewAct.setEnabled(self.__editor.canPaste())
        self.connect(self.__editor, SIGNAL("clipboardImageAvailable(bool)"), 
                     self.pasteAct, SLOT("setEnabled(bool)"))
        self.connect(self.__editor, SIGNAL("clipboardImageAvailable(bool)"), 
                     self.pasteNewAct, SLOT("setEnabled(bool)"))
    
    def __initViewActions(self):
        """
        Private method to create the View actions.
        """
        self.zoomInAct = E4Action(self.trUtf8('Zoom in'), 
            UI.PixmapCache.getIcon("zoomIn.png"),
            self.trUtf8('Zoom &in'), 
            QKeySequence(self.trUtf8("Ctrl++", "View|Zoom in")), 
            0, self, 'iconEditor_view_zoom_in')
        self.zoomInAct.setStatusTip(self.trUtf8('Zoom in on the icon'))
        self.zoomInAct.setWhatsThis(self.trUtf8(
                """<b>Zoom in</b>"""
                """<p>Zoom in on the icon. This makes the grid bigger.</p>"""
        ))
        self.connect(self.zoomInAct, SIGNAL('triggered()'), self.__zoomIn)
        self.__actions.append(self.zoomInAct)
        
        self.zoomOutAct = E4Action(self.trUtf8('Zoom out'), 
            UI.PixmapCache.getIcon("zoomOut.png"),
            self.trUtf8('Zoom &out'), 
            QKeySequence(self.trUtf8("Ctrl+-", "View|Zoom out")), 
            0, self, 'iconEditor_view_zoom_out')
        self.zoomOutAct.setStatusTip(self.trUtf8('Zoom out on the icon'))
        self.zoomOutAct.setWhatsThis(self.trUtf8(
                """<b>Zoom out</b>"""
                """<p>Zoom out on the icon. This makes the grid smaller.</p>"""
        ))
        self.connect(self.zoomOutAct, SIGNAL('triggered()'), self.__zoomOut)
        self.__actions.append(self.zoomOutAct)
        
        self.zoomResetAct = E4Action(self.trUtf8('Zoom reset'), 
            UI.PixmapCache.getIcon("zoomReset.png"),
            self.trUtf8('Zoom &reset'), 
            QKeySequence(self.trUtf8("Ctrl+0", "View|Zoom reset")), 
            0, self, 'iconEditor_view_zoom_reset')
        self.zoomResetAct.setStatusTip(self.trUtf8('Reset the zoom of the icon'))
        self.zoomResetAct.setWhatsThis(self.trUtf8(
                """<b>Zoom reset</b>"""
                """<p>Reset the zoom of the icon. """
                """This sets the zoom factor to 100%.</p>"""
        ))
        self.connect(self.zoomResetAct, SIGNAL('triggered()'), self.__zoomReset)
        self.__actions.append(self.zoomResetAct)
        
        self.zoomToAct = E4Action(self.trUtf8('Zoom'),
            UI.PixmapCache.getIcon("zoomTo.png"),
            self.trUtf8('&Zoom...'),
            QKeySequence(self.trUtf8("Ctrl+#", "View|Zoom")), 
            0,
            self, 'iconEditor_view_zoom')
        self.zoomToAct.setStatusTip(self.trUtf8('Zoom the icon'))
        self.zoomToAct.setWhatsThis(self.trUtf8(
                """<b>Zoom</b>"""
                """<p>Zoom the icon. This opens a dialog where the"""
                """ desired zoom factor can be entered.</p>"""
                ))
        self.connect(self.zoomToAct, SIGNAL('triggered()'), self.__zoom)
        self.__actions.append(self.zoomToAct)
        
        self.showGridAct = E4Action(self.trUtf8('Show Grid'),
            UI.PixmapCache.getIcon("grid.png"),
            self.trUtf8('Show &Grid'),
            0, 0,
            self, 'iconEditor_view_show_grid')
        self.showGridAct.setStatusTip(self.trUtf8('Toggle the display of the grid'))
        self.showGridAct.setWhatsThis(self.trUtf8(
                """<b>Show Grid</b>"""
                """<p>Toggle the display of the grid.</p>"""
                ))
        self.connect(self.showGridAct, SIGNAL('triggered(bool)'), 
                     self.__editor.setGridEnabled)
        self.__actions.append(self.showGridAct)
        self.showGridAct.setCheckable(True)
        self.showGridAct.setChecked(self.__editor.isGridEnabled())
    
    def __initToolsActions(self):
        """
        Private method to create the View actions.
        """
        self.esm = QSignalMapper(self)
        self.connect(self.esm, SIGNAL('mapped(int)'), self.__editor.setTool)
        
        self.drawingActGrp = createActionGroup(self)
        self.drawingActGrp.setExclusive(True)
        
        self.drawPencilAct = E4Action(self.trUtf8('Freehand'), 
            UI.PixmapCache.getIcon("drawBrush.png"),
            self.trUtf8('&Freehand'), 
            0, 0, 
            self.drawingActGrp, 'iconEditor_tools_pencil')
        self.drawPencilAct.setWhatsThis(self.trUtf8(
                """<b>Free hand</b>"""
                """<p>Draws non linear lines.</p>"""
        ))
        self.drawPencilAct.setCheckable(True)
        self.esm.setMapping(self.drawPencilAct, IconEditorGrid.Pencil)
        self.connect(self.drawPencilAct, SIGNAL('triggered()'), 
                     self.esm, SLOT('map()'))
        self.__actions.append(self.drawPencilAct)
        
        self.drawColorPickerAct = E4Action(self.trUtf8('Color Picker'), 
            UI.PixmapCache.getIcon("colorPicker.png"),
            self.trUtf8('&Color Picker'), 
            0, 0, 
            self.drawingActGrp, 'iconEditor_tools_color_picker')
        self.drawColorPickerAct.setWhatsThis(self.trUtf8(
                """<b>Color Picker</b>"""
                """<p>The color of the pixel clicked on will become """
                """the current draw color.</p>"""
        ))
        self.drawColorPickerAct.setCheckable(True)
        self.esm.setMapping(self.drawColorPickerAct, IconEditorGrid.ColorPicker)
        self.connect(self.drawColorPickerAct, SIGNAL('triggered()'), 
                     self.esm, SLOT('map()'))
        self.__actions.append(self.drawColorPickerAct)
        
        self.drawRectangleAct = E4Action(self.trUtf8('Rectangle'), 
            UI.PixmapCache.getIcon("drawRectangle.png"),
            self.trUtf8('&Rectangle'), 
            0, 0, 
            self.drawingActGrp, 'iconEditor_tools_rectangle')
        self.drawRectangleAct.setWhatsThis(self.trUtf8(
                """<b>Rectangle</b>"""
                """<p>Draw a rectangle.</p>"""
        ))
        self.drawRectangleAct.setCheckable(True)
        self.esm.setMapping(self.drawRectangleAct, IconEditorGrid.Rectangle)
        self.connect(self.drawRectangleAct, SIGNAL('triggered()'), 
                     self.esm, SLOT('map()'))
        self.__actions.append(self.drawRectangleAct)
        
        self.drawFilledRectangleAct = E4Action(self.trUtf8('Filled Rectangle'), 
            UI.PixmapCache.getIcon("drawRectangleFilled.png"),
            self.trUtf8('F&illed Rectangle'), 
            0, 0, 
            self.drawingActGrp, 'iconEditor_tools_filled_rectangle')
        self.drawFilledRectangleAct.setWhatsThis(self.trUtf8(
                """<b>Filled Rectangle</b>"""
                """<p>Draw a filled rectangle.</p>"""
        ))
        self.drawFilledRectangleAct.setCheckable(True)
        self.esm.setMapping(self.drawFilledRectangleAct, IconEditorGrid.FilledRectangle)
        self.connect(self.drawFilledRectangleAct, SIGNAL('triggered()'), 
                     self.esm, SLOT('map()'))
        self.__actions.append(self.drawFilledRectangleAct)
        
        self.drawCircleAct = E4Action(self.trUtf8('Circle'), 
            UI.PixmapCache.getIcon("drawCircle.png"),
            self.trUtf8('Circle'), 
            0, 0, 
            self.drawingActGrp, 'iconEditor_tools_circle')
        self.drawCircleAct.setWhatsThis(self.trUtf8(
                """<b>Circle</b>"""
                """<p>Draw a circle.</p>"""
        ))
        self.drawCircleAct.setCheckable(True)
        self.esm.setMapping(self.drawCircleAct, IconEditorGrid.Circle)
        self.connect(self.drawCircleAct, SIGNAL('triggered()'), 
                     self.esm, SLOT('map()'))
        self.__actions.append(self.drawCircleAct)
        
        self.drawFilledCircleAct = E4Action(self.trUtf8('Filled Circle'), 
            UI.PixmapCache.getIcon("drawCircleFilled.png"),
            self.trUtf8('Fille&d Circle'), 
            0, 0, 
            self.drawingActGrp, 'iconEditor_tools_filled_circle')
        self.drawFilledCircleAct.setWhatsThis(self.trUtf8(
                """<b>Filled Circle</b>"""
                """<p>Draw a filled circle.</p>"""
        ))
        self.drawFilledCircleAct.setCheckable(True)
        self.esm.setMapping(self.drawFilledCircleAct, IconEditorGrid.FilledCircle)
        self.connect(self.drawFilledCircleAct, SIGNAL('triggered()'), 
                     self.esm, SLOT('map()'))
        self.__actions.append(self.drawFilledCircleAct)
        
        self.drawEllipseAct = E4Action(self.trUtf8('Ellipse'), 
            UI.PixmapCache.getIcon("drawEllipse.png"),
            self.trUtf8('&Ellipse'), 
            0, 0, 
            self.drawingActGrp, 'iconEditor_tools_ellipse')
        self.drawEllipseAct.setWhatsThis(self.trUtf8(
                """<b>Ellipse</b>"""
                """<p>Draw an ellipse.</p>"""
        ))
        self.drawEllipseAct.setCheckable(True)
        self.esm.setMapping(self.drawEllipseAct, IconEditorGrid.Ellipse)
        self.connect(self.drawEllipseAct, SIGNAL('triggered()'), 
                     self.esm, SLOT('map()'))
        self.__actions.append(self.drawEllipseAct)
        
        self.drawFilledEllipseAct = E4Action(self.trUtf8('Filled Ellipse'), 
            UI.PixmapCache.getIcon("drawEllipseFilled.png"),
            self.trUtf8('Fille&d Elli&pse'), 
            0, 0, 
            self.drawingActGrp, 'iconEditor_tools_filled_ellipse')
        self.drawFilledEllipseAct.setWhatsThis(self.trUtf8(
                """<b>Filled Ellipse</b>"""
                """<p>Draw a filled ellipse.</p>"""
        ))
        self.drawFilledEllipseAct.setCheckable(True)
        self.esm.setMapping(self.drawFilledEllipseAct, IconEditorGrid.FilledEllipse)
        self.connect(self.drawFilledEllipseAct, SIGNAL('triggered()'), 
                     self.esm, SLOT('map()'))
        self.__actions.append(self.drawFilledEllipseAct)
        
        self.drawFloodFillAct = E4Action(self.trUtf8('Flood Fill'), 
            UI.PixmapCache.getIcon("drawFill.png"),
            self.trUtf8('Fl&ood Fill'), 
            0, 0, 
            self.drawingActGrp, 'iconEditor_tools_flood_fill')
        self.drawFloodFillAct.setWhatsThis(self.trUtf8(
                """<b>Flood Fill</b>"""
                """<p>Fill adjoining pixels with the same color with """
                """the current color.</p>"""
        ))
        self.drawFloodFillAct.setCheckable(True)
        self.esm.setMapping(self.drawFloodFillAct, IconEditorGrid.Fill)
        self.connect(self.drawFloodFillAct, SIGNAL('triggered()'), 
                     self.esm, SLOT('map()'))
        self.__actions.append(self.drawFloodFillAct)
        
        self.drawLineAct = E4Action(self.trUtf8('Line'), 
            UI.PixmapCache.getIcon("drawLine.png"),
            self.trUtf8('&Line'), 
            0, 0, 
            self.drawingActGrp, 'iconEditor_tools_line')
        self.drawLineAct.setWhatsThis(self.trUtf8(
                """<b>Line</b>"""
                """<p>Draw a line.</p>"""
        ))
        self.drawLineAct.setCheckable(True)
        self.esm.setMapping(self.drawLineAct, IconEditorGrid.Line)
        self.connect(self.drawLineAct, SIGNAL('triggered()'), 
                     self.esm, SLOT('map()'))
        self.__actions.append(self.drawLineAct)
        
        self.drawEraserAct = E4Action(self.trUtf8('Eraser (Transparent)'), 
            UI.PixmapCache.getIcon("drawEraser.png"),
            self.trUtf8('Eraser (&Transparent)'), 
            0, 0, 
            self.drawingActGrp, 'iconEditor_tools_eraser')
        self.drawEraserAct.setWhatsThis(self.trUtf8(
                """<b>Eraser (Transparent)</b>"""
                """<p>Erase pixels by setting them to transparent.</p>"""
        ))
        self.drawEraserAct.setCheckable(True)
        self.esm.setMapping(self.drawEraserAct, IconEditorGrid.Rubber)
        self.connect(self.drawEraserAct, SIGNAL('triggered()'), 
                     self.esm, SLOT('map()'))
        self.__actions.append(self.drawEraserAct)
        
        self.drawRectangleSelectionAct = E4Action(self.trUtf8('Rectangular Selection'), 
            UI.PixmapCache.getIcon("selectRectangle.png"),
            self.trUtf8('Rect&angular Selection'), 
            0, 0, 
            self.drawingActGrp, 'iconEditor_tools_selection_rectangle')
        self.drawRectangleSelectionAct.setWhatsThis(self.trUtf8(
                """<b>Rectangular Selection</b>"""
                """<p>Select a rectangular section of the icon using the mouse.</p>"""
        ))
        self.drawRectangleSelectionAct.setCheckable(True)
        self.esm.setMapping(self.drawRectangleSelectionAct, 
                            IconEditorGrid.RectangleSelection)
        self.connect(self.drawRectangleSelectionAct, SIGNAL('triggered()'), 
                     self.esm, SLOT('map()'))
        self.__actions.append(self.drawRectangleSelectionAct)
        
        self.drawCircleSelectionAct = E4Action(self.trUtf8('Circular Selection'), 
            UI.PixmapCache.getIcon("selectCircle.png"),
            self.trUtf8('Rect&angular Selection'), 
            0, 0, 
            self.drawingActGrp, 'iconEditor_tools_selection_circle')
        self.drawCircleSelectionAct.setWhatsThis(self.trUtf8(
                """<b>Circular Selection</b>"""
                """<p>Select a circular section of the icon using the mouse.</p>"""
        ))
        self.drawCircleSelectionAct.setCheckable(True)
        self.esm.setMapping(self.drawCircleSelectionAct, 
                            IconEditorGrid.CircleSelection)
        self.connect(self.drawCircleSelectionAct, SIGNAL('triggered()'), 
                     self.esm, SLOT('map()'))
        self.__actions.append(self.drawCircleSelectionAct)
        
        self.drawPencilAct.setChecked(True)
    
    def __initHelpActions(self):
        """
        Private method to create the Help actions.
        """
        self.aboutAct = E4Action(self.trUtf8('About'),
                self.trUtf8('&About'),
                0, 0, self, 'iconEditor_help_about')
        self.aboutAct.setStatusTip(self.trUtf8('Display information about this software'))
        self.aboutAct.setWhatsThis(self.trUtf8(
            """<b>About</b>"""
            """<p>Display some information about this software.</p>"""))
        self.connect(self.aboutAct, SIGNAL('triggered()'), self.__about)
        self.__actions.append(self.aboutAct)
        
        self.aboutQtAct = E4Action(self.trUtf8('About Qt'),
                self.trUtf8('About &Qt'), 
                0, 0, self, 'iconEditor_help_about_qt')
        self.aboutQtAct.setStatusTip(\
            self.trUtf8('Display information about the Qt toolkit'))
        self.aboutQtAct.setWhatsThis(self.trUtf8(
            """<b>About Qt</b>"""
            """<p>Display some information about the Qt toolkit.</p>"""
        ))
        self.connect(self.aboutQtAct, SIGNAL('triggered()'), self.__aboutQt)
        self.__actions.append(self.aboutQtAct)
        
        if KdeQt.isKDE():
            self.aboutKdeAct = E4Action(self.trUtf8('About KDE'),
                    self.trUtf8('About &KDE'), 
                    0, 0, self, 'iconEditor_help_about_kde')
            self.aboutKdeAct.setStatusTip(self.trUtf8('Display information about KDE'))
            self.aboutKdeAct.setWhatsThis(self.trUtf8(
                """<b>About KDE</b>"""
                """<p>Display some information about KDE.</p>"""
            ))
            self.connect(self.aboutKdeAct, SIGNAL('triggered()'), self.__aboutKde)
            self.__actions.append(self.aboutKdeAct)
        else:
            self.aboutKdeAct = None
        
        self.whatsThisAct = E4Action(self.trUtf8('What\'s This?'), 
            UI.PixmapCache.getIcon("whatsThis.png"),
            self.trUtf8('&What\'s This?'), 
            QKeySequence(self.trUtf8("Shift+F1","Help|What's This?'")), 
            0, self, 'iconEditor_help_whats_this')
        self.whatsThisAct.setStatusTip(self.trUtf8('Context sensitive help'))
        self.whatsThisAct.setWhatsThis(self.trUtf8(
                """<b>Display context sensitive help</b>"""
                """<p>In What's This? mode, the mouse cursor shows an arrow with a"""
                """ question mark, and you can click on the interface elements to get"""
                """ a short description of what they do and how to use them. In"""
                """ dialogs, this feature can be accessed using the context help button"""
                """ in the titlebar.</p>"""
        ))
        self.connect(self.whatsThisAct, SIGNAL('triggered()'), self.__whatsThis)
        self.__actions.append(self.whatsThisAct)
    
    def __initMenus(self):
        """
        Private method to create the menus.
        """
        mb = self.menuBar()
        
        menu = mb.addMenu(self.trUtf8('&File'))
        menu.setTearOffEnabled(True)
        menu.addAction(self.newAct)
        menu.addAction(self.newWindowAct)
        menu.addAction(self.openAct)
        menu.addSeparator()
        menu.addAction(self.saveAct)
        menu.addAction(self.saveAsAct)
        menu.addSeparator()
        menu.addAction(self.closeAct)
        menu.addAction(self.closeAllAct)
        menu.addSeparator()
        menu.addAction(self.exitAct)
        
        menu = mb.addMenu(self.trUtf8("&Edit"))
        menu.setTearOffEnabled(True)
        menu.addAction(self.undoAct)
        menu.addAction(self.redoAct)
        menu.addSeparator()
        menu.addAction(self.cutAct)
        menu.addAction(self.copyAct)
        menu.addAction(self.pasteAct)
        menu.addAction(self.pasteNewAct)
        menu.addAction(self.deleteAct)
        menu.addSeparator()
        menu.addAction(self.selectAllAct)
        menu.addSeparator()
        menu.addAction(self.resizeAct)
        menu.addAction(self.grayscaleAct)
        
        menu = mb.addMenu(self.trUtf8('&View'))
        menu.setTearOffEnabled(True)
        menu.addAction(self.zoomInAct)
        menu.addAction(self.zoomResetAct)
        menu.addAction(self.zoomOutAct)
        menu.addAction(self.zoomToAct)
        menu.addSeparator()
        menu.addAction(self.showGridAct)
        
        menu = mb.addMenu(self.trUtf8('&Tools'))
        menu.setTearOffEnabled(True)
        menu.addAction(self.drawPencilAct)
        menu.addAction(self.drawColorPickerAct)
        menu.addAction(self.drawRectangleAct)
        menu.addAction(self.drawFilledRectangleAct)
        menu.addAction(self.drawCircleAct)
        menu.addAction(self.drawFilledCircleAct)
        menu.addAction(self.drawEllipseAct)
        menu.addAction(self.drawFilledEllipseAct)
        menu.addAction(self.drawFloodFillAct)
        menu.addAction(self.drawLineAct)
        menu.addAction(self.drawEraserAct)
        menu.addSeparator()
        menu.addAction(self.drawRectangleSelectionAct)
        menu.addAction(self.drawCircleSelectionAct)
        
        mb.addSeparator()
        
        menu = mb.addMenu(self.trUtf8("&Help"))
        menu.addAction(self.aboutAct)
        menu.addAction(self.aboutQtAct)
        if self.aboutKdeAct is not None:
            menu.addAction(self.aboutKdeAct)
        menu.addSeparator()
        menu.addAction(self.whatsThisAct)
    
    def __initToolbars(self):
        """
        Private method to create the toolbars.
        """
        filetb = self.addToolBar(self.trUtf8("File"))
        filetb.setObjectName("FileToolBar")
        filetb.setIconSize(UI.Config.ToolBarIconSize)
        filetb.addAction(self.newAct)
        filetb.addAction(self.newWindowAct)
        filetb.addAction(self.openAct)
        filetb.addSeparator()
        filetb.addAction(self.saveAct)
        filetb.addAction(self.saveAsAct)
        filetb.addSeparator()
        filetb.addAction(self.closeAct)
        filetb.addAction(self.exitAct)
        
        edittb = self.addToolBar(self.trUtf8("Edit"))
        edittb.setObjectName("EditToolBar")
        edittb.setIconSize(UI.Config.ToolBarIconSize)
        edittb.addAction(self.undoAct)
        edittb.addAction(self.redoAct)
        edittb.addSeparator()
        edittb.addAction(self.cutAct)
        edittb.addAction(self.copyAct)
        edittb.addAction(self.pasteAct)
        edittb.addSeparator()
        edittb.addAction(self.resizeAct)
        edittb.addAction(self.grayscaleAct)
        
        viewtb = self.addToolBar(self.trUtf8("View"))
        viewtb.setObjectName("ViewToolBar")
        viewtb.setIconSize(UI.Config.ToolBarIconSize)
        viewtb.addAction(self.zoomInAct)
        viewtb.addAction(self.zoomResetAct)
        viewtb.addAction(self.zoomOutAct)
        viewtb.addAction(self.zoomToAct)
        viewtb.addSeparator()
        viewtb.addAction(self.showGridAct)
        
        toolstb = self.addToolBar(self.trUtf8("Tools"))
        toolstb.setObjectName("ToolsToolBar")
        toolstb.setIconSize(UI.Config.ToolBarIconSize)
        toolstb.addAction(self.drawPencilAct)
        toolstb.addAction(self.drawColorPickerAct)
        toolstb.addAction(self.drawRectangleAct)
        toolstb.addAction(self.drawFilledRectangleAct)
        toolstb.addAction(self.drawCircleAct)
        toolstb.addAction(self.drawFilledCircleAct)
        toolstb.addAction(self.drawEllipseAct)
        toolstb.addAction(self.drawFilledEllipseAct)
        toolstb.addAction(self.drawFloodFillAct)
        toolstb.addAction(self.drawLineAct)
        toolstb.addAction(self.drawEraserAct)
        toolstb.addSeparator()
        toolstb.addAction(self.drawRectangleSelectionAct)
        toolstb.addAction(self.drawCircleSelectionAct)
        
        helptb = self.addToolBar(self.trUtf8("Help"))
        helptb.setObjectName("HelpToolBar")
        helptb.setIconSize(UI.Config.ToolBarIconSize)
        helptb.addAction(self.whatsThisAct)
    
    def __createStatusBar(self):
        """
        Private method to initialize the status bar.
        """
        self.__statusBar = self.statusBar()
        self.__statusBar.setSizeGripEnabled(True)

        self.__sbZoom = QLabel(self.__statusBar)
        self.__statusBar.addPermanentWidget(self.__sbZoom)
        self.__sbZoom.setWhatsThis(self.trUtf8(
            """<p>This part of the status bar displays the current zoom factor.</p>"""
        ))
        self.__updateZoom()

        self.__sbSize = QLabel(self.__statusBar)
        self.__statusBar.addPermanentWidget(self.__sbSize)
        self.__sbSize.setWhatsThis(self.trUtf8(
            """<p>This part of the status bar displays the icon size.</p>"""
        ))
        self.__updateSize(*self.__editor.iconSize())

        self.__sbPos = QLabel(self.__statusBar)
        self.__statusBar.addPermanentWidget(self.__sbPos)
        self.__sbPos.setWhatsThis(self.trUtf8(
            """<p>This part of the status bar displays the cursor position.</p>"""
        ))
        self.__updatePosition(0, 0)
    
    def __createPaletteDock(self):
        """
        Private method to initialize the palette dock widget.
        """
        self.__paletteDock = QDockWidget(self)
        self.__paletteDock.setObjectName("paletteDock")
        self.__paletteDock.setFeatures(
            QDockWidget.DockWidgetFeatures(QDockWidget.AllDockWidgetFeatures))
        self.__paletteDock.setWindowTitle("Palette")
        self.__palette = IconEditorPalette()
        self.__paletteDock.setWidget(self.__palette)
        self.addDockWidget(Qt.RightDockWidgetArea, self.__paletteDock)
    
    def closeEvent(self, evt):
        """
        Private event handler for the close event.
        
        @param evt the close event (QCloseEvent)
                <br />This event is simply accepted after the history has been
                saved and all window references have been deleted.
        """
        if self.__maybeSave():
            self.__editor.shutdown()
            
            state = self.saveState()
            Preferences.setIconEditor("IconEditorState", state)

            Preferences.setGeometry("IconEditorGeometry", self.saveGeometry())
            
            try:
                del self.__class__.windows[self.__class__.windows.index(self)]
            except ValueError:
                pass
            
            if not self.fromEric:
                Preferences.syncPreferences()
            
            evt.accept()
            self.emit(SIGNAL("editorClosed"))
        else:
            evt.ignore()
    
    def __newIcon(self):
        """
        Private slot to create a new icon.
        """
        if self.__maybeSave():
            self.__editor.editNew()
            self.__setCurrentFile(QString(""))
        
        self.__checkActions()
    
    def __newWindow(self):
        """
        Public slot called to open a new icon editor window.
        """
        ie = IconEditorWindow(parent = self.parent(), fromEric = self.fromEric)
        ie.show()
    
    def __openIcon(self):
        """
        Private slot to open an icon file.
        """
        if self.__maybeSave():
            selectedFilter = QString(self.__defaultFilter)
            fileName = KQFileDialog.getOpenFileName(\
                self,
                self.trUtf8("Open icon file"),
                QString(),
                self.__inputFilter,
                selectedFilter)
            if not fileName.isEmpty():
                self.__loadIconFile(fileName)
        self.__checkActions()
    
    def __saveIcon(self):
        """
        Private slot to save the icon.
        """
        if self.__fileName.isEmpty():
            return self.__saveIconAs()
        else:
            return self.__saveIconFile(self.__fileName)
    
    def __saveIconAs(self):
        """
        Private slot to save the icon with a new name.
        """
        selectedFilter = QString(self.__defaultFilter)
        fileName = KQFileDialog.getSaveFileName(\
            self,
            self.trUtf8("Save icon file"),
            QString(),
            self.__outputFilter,
            selectedFilter,
            QFileDialog.Options(QFileDialog.DontConfirmOverwrite))
        if fileName.isEmpty():
            return False
        
        ext = QFileInfo(fileName).suffix()
        if ext.isEmpty():
            ex = selectedFilter.section('(*',1,1).section(')',0,0)
            if not ex.isEmpty():
                fileName.append(ex)
        if QFileInfo(fileName).exists():
            res = KQMessageBox.warning(self,
                self.trUtf8("Save icon file"),
                self.trUtf8("<p>The file <b>%1</b> already exists.</p>")
                    .arg(fileName),
                QMessageBox.StandardButtons(\
                    QMessageBox.Abort | \
                    QMessageBox.Save),
                QMessageBox.Abort)
            if res == QMessageBox.Abort or res == QMessageBox.Cancel:
                return False
        
        return self.__saveIconFile(fileName)
    
    def __closeAll(self):
        """
        Private slot to close all other windows.
        """
        for win in self.__class__.windows[:]:
            if win != self:
                win.close()
    
    def __loadIconFile(self, fileName):
        """
        Private method to load an icon file.
        
        @param fileName name of the icon file to load (string or QString).
        """
        file= QFile(fileName)
        if not file.exists():
            KQMessageBox.warning(self, self.trUtf8("eric4 Icon Editor"),
                                 self.trUtf8("The file %1 does not exist.")\
                                    .arg(fileName))
            return
        
        if not file.open(QFile.ReadOnly):
            KQMessageBox.warning(self, self.trUtf8("eric4 Icon Editor"),
                                 self.trUtf8("Cannot read file %1:\n%2.")\
                                    .arg(fileName)\
                                    .arg(file.errorString()))
            return
        file.close()
        
        img = QImage(fileName)
        self.__editor.setIconImage(img, clearUndo = True)
        self.__setCurrentFile(fileName)

    def __saveIconFile(self, fileName):
        """
        Private method to save to the given file.
        
        @param fileName name of the file to save to (string or QString)
        @return flag indicating success (boolean)
        """
        file = QFile(fileName)
        if not file.open(QFile.WriteOnly):
            KQMessageBox.warning(self, self.trUtf8("eric4 Icon Editor"),
                                 self.trUtf8("Cannot write file %1:\n%2.")\
                                 .arg(fileName)\
                                 .arg(file.errorString()))
        
            self.__checkActions()
            
            return False
        
        img = self.__editor.iconImage()
        res = img.save(file)
        file.close()
        
        if not res:
            KQMessageBox.warning(self, self.trUtf8("eric4 Icon Editor"),
                                 self.trUtf8("Cannot write file %1:\n%2.")\
                                 .arg(fileName)\
                                 .arg(file.errorString()))
        
            self.__checkActions()
            
            return False
        
        self.__editor.setDirty(False, setCleanState = True)
        
        self.__setCurrentFile(fileName)
        self.__statusBar.showMessage(self.trUtf8("Icon saved"), 2000)
        
        self.__checkActions()
        
        return True

    def __setCurrentFile(self, fileName):
        """
        Private method to register the file name of the current file.
        
        @param fileName name of the file to register (string or QString)
        """
        self.__fileName = QString(fileName)
        
        if self.__fileName.isEmpty():
            shownName = self.trUtf8("Untitled")
        else:
            shownName = self.__strippedName(self.__fileName)
        
        self.setWindowTitle(self.trUtf8("%1[*] - %2")\
                            .arg(shownName)\
                            .arg(self.trUtf8("Icon Editor")))
        
        self.setWindowModified(self.__editor.isDirty())
    
    def __strippedName(self, fullFileName):
        """
        Private method to return the filename part of the given path.
        
        @param fullFileName full pathname of the given file (QString)
        @return filename part (QString)
        """
        return QFileInfo(fullFileName).fileName()
    
    def __maybeSave(self):
        """
        Private method to ask the user to save the file, if it was modified.
        
        @return flag indicating, if it is ok to continue (boolean)
        """
        if self.__editor.isDirty():
            ret = KQMessageBox.warning(self,
                self.trUtf8("eric4 Icon Editor"),
                self.trUtf8("""The icon image has been modified.\n"""
                            """Do you want to save your changes?"""),
                QMessageBox.StandardButtons(\
                    QMessageBox.Cancel | \
                    QMessageBox.No | \
                    QMessageBox.Yes),
                QMessageBox.Cancel)
            if ret == QMessageBox.Yes:
                return self.__saveIcon()
            elif ret == QMessageBox.Cancel:
                return False
        return True
    
    def __checkActions(self):
        """
        Private slot to check some actions for their enable/disable status.
        """
        self.saveAct.setEnabled(self.__editor.isDirty())

    def __modificationChanged(self, m):
        """
        Private slot to handle the modificationChanged signal. 
        
        @param m modification status
        """
        self.setWindowModified(m)
        self.__checkActions()
    
    def __updatePosition(self, x, y):
        """
        Private slot to show the current cursor position.
        
        @param x x-coordinate (integer)
        @param y y-coordinate (integer)
        """
        self.__sbPos.setText("%d, %d" % (x + 1, y + 1))
    
    def __updateSize(self, w, h):
        """
        Private slot to show the current icon size.
        
        @param w width of the icon (integer)
        @param h height of the icon (integer)
        """
        self.__sbSize.setText("%d x %d" % (w, h))
    
    def __updateZoom(self):
        """
        Private slot to show the current zoom factor.
        """
        zoom = self.__editor.zoomFactor()
        self.__sbZoom.setText("%d %%" % (zoom * 100, ))
        self.zoomOutAct.setEnabled(self.__editor.zoomFactor() > 1)
    
    def __zoomIn(self):
        """
        Private slot called to handle the zoom in action.
        """
        self.__editor.setZoomFactor(self.__editor.zoomFactor() + 1)
        self.__updateZoom()
    
    def __zoomOut(self):
        """
        Private slot called to handle the zoom out action.
        """
        self.__editor.setZoomFactor(self.__editor.zoomFactor() - 1)
        self.__updateZoom()
    
    def __zoomReset(self):
        """
        Private slot called to handle the zoom reset action.
        """
        self.__editor.setZoomFactor(1)
        self.__updateZoom()
    
    def __zoom(self):
        """
        Private method to handle the zoom action.
        """
        dlg = IconZoomDialog(self.__editor.zoomFactor(), self)
        if dlg.exec_() == QDialog.Accepted:
            self.__editor.setZoomFactor(dlg.getZoomFactor())
            self.__updateZoom()
    
    def __about(self):
        """
        Private slot to show a little About message.
        """
        KQMessageBox.about(self, self.trUtf8("About eric4 Icon Editor"),
            self.trUtf8("The eric4 Icon Editor is a simple editor component"
                        " to perform icon drawing tasks."))
    
    def __aboutQt(self):
        """
        Private slot to handle the About Qt dialog.
        """
        QMessageBox.aboutQt(self, "eric4 Icon Editor")
    
    def __aboutKde(self):
        """
        Private slot to handle the About KDE dialog.
        """
        from PyKDE4.kdeui import KHelpMenu
        menu = KHelpMenu(self)
        menu.aboutKDE()
    
    def __whatsThis(self):
        """
        Private slot called in to enter Whats This mode.
        """
        QWhatsThis.enterWhatsThisMode()
