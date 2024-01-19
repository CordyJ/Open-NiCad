# -*- coding: utf-8 -*-

# Copyright (c) 2002 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the variables viewer widget.
"""

import types
from math import log10
import sys

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from KdeQt.KQApplication import e4App

from Config import ConfigVarTypeDispStrings, ConfigVarTypeStrings
from VariableDetailDialog import VariableDetailDialog
from Utilities import toUnicode

import Preferences


class VariableItem(QTreeWidgetItem):
    """
    Class implementing the data structure for variable items.
    """
    def __init__(self, parent, dvar, dvalue, dtype):
        """
        Constructor.
        
        @param parent reference to the parent item
        @param dvar variable name (string or QString)
        @param dvalue value string (string or QString)
        @param dtype type string (string or QString)
        """
        self.value = QString(dvalue)
        if len(dvalue) > 2048:     # 1024 * 2
            dvalue = QApplication.translate("VariableItem", 
                                            "<double click to show value>")
        
        QTreeWidgetItem.__init__(self, parent, QStringList() << dvar << dvalue << dtype)
        
        self.populated = True
        
    def getValue(self):
        """
        Public method to return the value of the item.
        
        @return value of the item (QString)
        """
        return self.value
        
    def data(self, column, role):
        """
        Public method to return the data for the requested role.
        
        This implementation changes the original behavior in a way, that the display
        data is returned as the tooltip for column 1.
        
        @param column column number (integer)
        @param role data role (Qt.ItemDataRole)
        @return requested data (QVariant)
        """
        if column == 1 and role == Qt.ToolTipRole:
            role = Qt.DisplayRole
        return QTreeWidgetItem.data(self, column, role)
        
    def attachDummy(self):
        """
        Public method to attach a dummy sub item to allow for lazy population.
        """
        QTreeWidgetItem(self, QStringList("DUMMY"))
        
    def deleteChildren(self):
        """
        Public method to delete all children (cleaning the subtree).
        """
        for itm in self.takeChildren():
            del itm
        
    def key(self, column):
        """
        Public method generating the key for this item.
        
        @param column the column to sort on (integer)
        """
        return self.text(column)
        
    def __lt__(self, other):
        """
        Public method to check, if the item is less than the other one.
        
        @param other reference to item to compare against (QTreeWidgetItem)
        @return true, if this item is less than other (boolean)
        """
        column = self.treeWidget().sortColumn()
        return self.key(column) < other.key(column)
        
    def expand(self):
        """
        Public method to expand the item.
        
        Note: This is just a do nothing and should be overwritten.
        """
        return
        
    def collapse(self):
        """
        Public method to collapse the item.
        
        Note: This is just a do nothing and should be overwritten.
        """
        return

class SpecialVarItem(VariableItem):
    """
    Class implementing a VariableItem that represents a special variable node.
    
    These special variable nodes are generated for classes, lists, 
    tuples and dictionaries.
    """
    def __init__(self, parent, dvar, dvalue, dtype, frmnr, scope):
        """
        Constructor
        
        @param parent parent of this item
        @param dvar variable name (string or QString)
        @param dvalue value string (string or QString)
        @param dtype type string (string or QString)
        @param frmnr frame number (0 is the current frame) (int)
        @param scope flag indicating global (1) or local (0) variables
        """
        VariableItem.__init__(self, parent, dvar, dvalue, dtype)
        self.attachDummy()
        self.populated = False
        
        self.framenr = frmnr
        self.scope = scope

    def expand(self):
        """
        Public method to expand the item.
        """
        self.deleteChildren()
        self.populated = True
        
        pathlist = [str(self.text(0))]
        par = self.parent()
        
        # step 1: get a pathlist up to the requested variable
        while par is not None:
            pathlist.insert(0, str(par.text(0)))
            par = par.parent()
        
        # step 2: request the variable from the debugger
        filter = e4App().getObject("DebugUI").variablesFilter(self.scope)
        e4App().getObject("DebugServer").remoteClientVariable(\
            self.scope, filter, pathlist, self.framenr)

class ArrayElementVarItem(VariableItem):
    """
    Class implementing a VariableItem that represents an array element.
    """
    def __init__(self, parent, dvar, dvalue, dtype):
        """
        Constructor
        
        @param parent parent of this item
        @param dvar variable name (string or QString)
        @param dvalue value string (string or QString)
        @param dtype type string (string or QString)
        """
        VariableItem.__init__(self, parent, dvar, dvalue, dtype)
        
        """
        Array elements have numbers as names, but the key must be
        right justified and zero filled to 6 decimal places. Then 
        element 2 will have a key of '000002' and appear before 
        element 10 with a key of '000010'
        """
        keyStr = str(self.text(0))
        self.arrayElementKey = QString("%.6d" % int(keyStr))

    def key(self, column):
        """
        Public method generating the key for this item.
        
        @param column the column to sort on (integer)
        """
        if column == 0:
            return self.arrayElementKey
        else:
            return VariableItem.key(self, column)

class SpecialArrayElementVarItem(SpecialVarItem):
    """
    Class implementing a QTreeWidgetItem that represents a special array variable node.
    """
    def __init__(self, parent, dvar, dvalue, dtype, frmnr, scope):
        """
        Constructor
        
        @param parent parent of this item
        @param dvar variable name (string or QString)
        @param dvalue value string (string or QString)
        @param dtype type string (string or QString)
        @param frmnr frame number (0 is the current frame) (int)
        @param scope flag indicating global (1) or local (0) variables
        """
        SpecialVarItem.__init__(self, parent, dvar, dvalue, dtype, frmnr, scope)
        
        """
        Array elements have numbers as names, but the key must be
        right justified and zero filled to 6 decimal places. Then 
        element 2 will have a key of '000002' and appear before 
        element 10 with a key of '000010'
        """
        keyStr = str(self.text(0))[:-2] # strip off [], () or {}
        self.arrayElementKey = QString("%.6d" % int(keyStr))

    def key(self, column):
        """
        Public method generating the key for this item.
        
        @param column the column to sort on (integer)
        """
        if column == 0:
            return self.arrayElementKey
        else:
            return SpecialVarItem.key(self, column)

class VariablesViewer(QTreeWidget):
    """
    Class implementing the variables viewer widget.
    
    This widget is used to display the variables of the program being
    debugged in a tree. Compound types will be shown with
    their main entry first. Once the subtree has been expanded, the 
    individual entries will be shown. Double clicking an entry will
    popup a dialog showing the variables parameters in a more readable
    form. This is especially useful for lengthy strings.
    
    This widget has two modes for displaying the global and the local
    variables.
    """
    def __init__(self, parent=None, scope=1):
        """
        Constructor
        
        @param parent the parent (QWidget)
        @param scope flag indicating global (1) or local (0) variables
        """
        QTreeWidget.__init__(self, parent)
        
        self.indicators = {'list' : '[]', 'tuple' : '()', 'dict' : '{}', # Python types
                           'Array' : '[]', 'Hash' : '{}'}                # Ruby types
        
        self.rx_class = QRegExp('<.*(instance|object) at 0x.*>')
        self.rx_class2 = QRegExp('class .*')
        self.rx_class3 = QRegExp('<class .* at 0x.*>')
        self.dvar_rx_class1 = QRegExp(r'<.*(instance|object) at 0x.*>(\[\]|\{\}|\(\))')
        self.dvar_rx_class2 = QRegExp(r'<class .* at 0x.*>(\[\]|\{\}|\(\))')
        self.dvar_rx_array_element = QRegExp(r'^\d+$')
        self.dvar_rx_special_array_element = QRegExp(r'^\d+(\[\]|\{\}|\(\))$')
        self.rx_nonprintable = QRegExp(r"""(\\x\d\d)+""")
        
        self.framenr = 0
        
        self.loc = Preferences.getSystem("StringEncoding")
        
        self.openItems = []
        
        self.setRootIsDecorated(True)
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        
        self.scope = scope
        if scope:
            self.setWindowTitle(self.trUtf8("Global Variables"))
            self.setHeaderLabels(QStringList() << \
                self.trUtf8("Globals") << \
                self.trUtf8("Value") << \
                self.trUtf8("Type"))
            self.setWhatsThis(self.trUtf8(
                """<b>The Global Variables Viewer Window</b>"""
                """<p>This window displays the global variables"""
                """ of the debugged program.</p>"""
            ))
        else:
            self.setWindowTitle(self.trUtf8("Local Variables"))
            self.setHeaderLabels(QStringList() << \
                self.trUtf8("Locals") << \
                self.trUtf8("Value") << \
                self.trUtf8("Type"))
            self.setWhatsThis(self.trUtf8(
                """<b>The Local Variables Viewer Window</b>"""
                """<p>This window displays the local variables"""
                """ of the debugged program.</p>"""
            ))
        
        header = self.header()
        header.setSortIndicator(0, Qt.AscendingOrder)
        header.setSortIndicatorShown(True)
        header.setClickable(True)
        header.resizeSection(0, 120)    # variable column
        header.resizeSection(1, 150)    # value column
        
        self.__createPopupMenus()
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.connect(self,SIGNAL('customContextMenuRequested(const QPoint &)'),
                     self.__showContextMenu)
        
        self.connect(self, SIGNAL("itemExpanded(QTreeWidgetItem *)"), 
            self.__expandItemSignal)
        self.connect(self, SIGNAL("itemCollapsed(QTreeWidgetItem *)"), 
            self.collapseItem)
        
        self.resortEnabled = True
        
    def __createPopupMenus(self):
        """
        Private method to generate the popup menus.
        """
        self.menu = QMenu()
        self.menu.addAction(self.trUtf8("Show Details..."), self.__showDetails)
        self.menu.addSeparator()
        self.menu.addAction(self.trUtf8("Configure..."), self.__configure)
        
        self.backMenu = QMenu()
        self.backMenu.addAction(self.trUtf8("Configure..."), self.__configure)
        
    def __showContextMenu(self, coord):
        """
        Private slot to show the context menu.
        
        @param coord the position of the mouse pointer (QPoint)
        """
        gcoord = self.mapToGlobal(coord)
        if self.itemAt(coord) is not None:
            self.menu.popup(gcoord)
        else:
            self.backMenu.popup(gcoord)
        
    def __findItem(self, slist, column, node=None):
        """
        Private method to search for an item.
        
        It is used to find a specific item in column,
        that is a child of node. If node is None, a child of the
        QTreeWidget is searched.
        
        @param slist searchlist (list of strings or QStrings)
        @param column index of column to search in (int)
        @param node start point of the search
        @return the found item or None
        """
        if node is None:
            count = self.topLevelItemCount()
        else:
            count = node.childCount()
        
        for index in range(count):
            if node is None:
                itm = self.topLevelItem(index)
            else:
                itm = node.child(index)
            if QString.compare(itm.text(column), slist[0]) == 0:
                if len(slist) > 1:
                    itm = self.__findItem(slist[1:], column, itm)
                return itm
        
        return None
        
    def showVariables(self, vlist, frmnr):
        """
        Public method to show variables in a list.
        
        @param vlist the list of variables to be displayed. Each
                listentry is a tuple of three values.
                <ul>
                <li>the variable name (string)</li>
                <li>the variables type (string)</li>
                <li>the variables value (string)</li>
                </ul>
        @param frmnr frame number (0 is the current frame) (int)
        """
        self.current = self.currentItem()
        if self.current:
            self.curpathlist = self.__buildTreePath(self.current)
        self.clear()
        self.__scrollToItem = None
        self.framenr = frmnr
        
        if len(vlist):
            self.resortEnabled = False
            for (var, vtype, value) in vlist:
                self.__addItem(None, vtype, var, value)
            
            # reexpand tree
            openItems = self.openItems[:]
            openItems.sort()
            self.openItems = []
            for itemPath in openItems:
                itm = self.__findItem(itemPath, 0)
                if itm is not None:
                    self.expandItem(itm)
                else:
                    self.openItems.append(itemPath)
            
            if self.current:
                citm = self.__findItem(self.curpathlist, 0)
                if citm:
                    self.setCurrentItem(citm)
                    self.setItemSelected(citm, True)
                    self.scrollToItem(citm, QAbstractItemView.PositionAtTop)
                    self.current = None
            
            self.resortEnabled = True
            self.__resort()

    def showVariable(self, vlist):
        """
        Public method to show variables in a list.
        
        @param vlist the list of subitems to be displayed. 
                The first element gives the path of the
                parent variable. Each other listentry is 
                a tuple of three values.
                <ul>
                <li>the variable name (string)</li>
                <li>the variables type (string)</li>
                <li>the variables value (string)</li>
                </ul>
        """
        resortEnabled = self.resortEnabled
        self.resortEnabled = False
        if self.current is None:
            self.current = self.currentItem()
            if self.current:
                self.curpathlist = self.__buildTreePath(self.current)
        
        subelementsAdded = False
        if vlist:
            itm = self.__findItem(vlist[0], 0)
            for var, vtype, value in vlist[1:]:
                self.__addItem(itm, vtype, var, value)
            subelementsAdded = True

        # reexpand tree
        openItems = self.openItems[:]
        openItems.sort()
        self.openItems = []
        for itemPath in openItems:
            itm = self.__findItem(itemPath, 0)
            if itm is not None and not itm.isExpanded():
                if itm.populated:
                    self.blockSignals(True)
                    itm.setExpanded(True)
                    self.blockSignals(False)
                else:
                    self.expandItem(itm)
        self.openItems = openItems[:]
            
        if self.current:
            citm = self.__findItem(self.curpathlist, 0)
            if citm:
                self.setCurrentItem(citm)
                self.setItemSelected(citm, True)
                if self.__scrollToItem:
                    self.scrollToItem(self.__scrollToItem, 
                                      QAbstractItemView.PositionAtTop)
                else:
                    self.scrollToItem(citm, QAbstractItemView.PositionAtTop)
                self.current = None
        elif self.__scrollToItem:
            self.scrollToItem(self.__scrollToItem, QAbstractItemView.PositionAtTop)
        
        self.resortEnabled = resortEnabled
        self.__resort()

    def __generateItem(self, parent, dvar, dvalue, dtype, isSpecial = False):
        """
        Private method used to generate a VariableItem.
        
        @param parent parent of the item to be generated
        @param dvar variable name (string or QString)
        @param dvalue value string (string or QString)
        @param dtype type string (string or QString)
        @param isSpecial flag indicating that a special node should be generated (boolean)
        @return The item that was generated (VariableItem).
        """
        if isSpecial and \
           (self.dvar_rx_class1.exactMatch(dvar) or \
            self.dvar_rx_class2.exactMatch(dvar)):
            isSpecial = False
        
        if self.rx_class2.exactMatch(dtype):
            return SpecialVarItem(parent, dvar, dvalue, dtype[7:-1], 
                                  self.framenr, self.scope)
        elif dtype != "void *" and \
             (self.rx_class.exactMatch(dvalue) or \
              self.rx_class3.exactMatch(dvalue) or \
              isSpecial):
            if self.dvar_rx_special_array_element.exactMatch(dvar):
                return SpecialArrayElementVarItem(parent, dvar, dvalue, dtype, 
                                                  self.framenr, self.scope)
            else:
                return SpecialVarItem(parent, dvar, dvalue, dtype, 
                                      self.framenr, self.scope)
        else:
            if isinstance(dvalue, str):
                dvalue = QString.fromLocal8Bit( dvalue )
            if self.dvar_rx_array_element.exactMatch(dvar):
                return ArrayElementVarItem(parent, dvar, dvalue, dtype)
            else:
                return VariableItem(parent, dvar, dvalue, dtype)
        
    def __unicode(self, s):
        """
        Private method to convert a string to unicode.
        
        @param s the string to be converted (string)
        @return unicode representation of s (unicode object)
        """
        if type(s) is type(u""):
            return s
        try:
            u = unicode(s, self.loc)
        except TypeError:
            u = str(s)
        except UnicodeError:
            u = toUnicode(s)
        return u
        
    def __addItem(self, parent, vtype, var, value):
        """
        Private method used to add an item to the list.
        
        If the item is of a type with subelements (i.e. list, dictionary, 
        tuple), these subelements are added by calling this method recursively.
        
        @param parent the parent of the item to be added
            (QTreeWidgetItem or None)
        @param vtype the type of the item to be added
            (string)
        @param var the variable name (string)
        @param value the value string (string)
        @return The item that was added to the listview (QTreeWidgetItem).
        """
        if parent is None:
            parent = self
        try:
            dvar = '%s%s' % (var, self.indicators[vtype])
        except KeyError:
            dvar = var
        dvtype = self.__getDispType(vtype)
        
        if vtype in ['list', 'Array', 'tuple', 'dict', 'Hash']:
            itm = self.__generateItem(parent, dvar, self.trUtf8("%1 items").arg(value), 
                                    dvtype, True)
        elif vtype in ['unicode', 'str']:
            if self.rx_nonprintable.indexIn(value) != -1:
                sval = value
            else:
                try:
                    sval = eval(value)
                except:
                    sval = value
            itm = self.__generateItem(parent, dvar, self.__unicode(sval), dvtype)
        
        else:
            itm = self.__generateItem(parent, dvar, value, dvtype)
            
        return itm

    def __getDispType(self, vtype):
        """
        Private method used to get the display string for type vtype.
        
        @param vtype the type, the display string should be looked up for
              (string)
        @return displaystring (string or QString)
        """
        try:
            i = ConfigVarTypeStrings.index(vtype)
            dvtype = self.trUtf8(ConfigVarTypeDispStrings[i])
        except ValueError:
            if vtype == 'classobj':
                dvtype = self.trUtf8(\
                    ConfigVarTypeDispStrings[ConfigVarTypeStrings.index('instance')]\
                )
            else:
                dvtype = vtype
        return dvtype

    def mouseDoubleClickEvent(self, mouseEvent):
        """
        Protected method of QAbstractItemView. 
        
        Reimplemented to disable expanding/collapsing
        of items when double-clicking. Instead the double-clicked entry is opened.
        
        @param mouseEvent the mouse event object (QMouseEvent)
        """
        itm = self.itemAt(mouseEvent.pos())
        self.__showVariableDetails(itm)
        
    def __showDetails(self):
        """
        Private slot to show details about the selected variable.
        """
        itm = self.currentItem()
        self.__showVariableDetails(itm)
        
    def __showVariableDetails(self, itm):
        """
        Private method to show details about a variable.
        
        @param itm reference to the variable item
        """
        if itm is None:
            return
        
        val = itm.getValue()
        
        if val.isEmpty():
            return  # do not display anything, if the variable has no value
            
        vtype = itm.text(2)
        name = unicode(itm.text(0))
        if name[-2:] in ['[]', '{}', '()']:
            name = name[:-2]
        
        par = itm.parent()
        nlist = [name]
        # build up the fully qualified name
        while par is not None:
            pname = unicode(par.text(0))
            if pname[-2:] in ['[]', '{}', '()']:
                if nlist[0].endswith("."):
                    nlist[0] = '[%s].' % nlist[0][:-1]
                else:
                    nlist[0] = '[%s]' % nlist[0]
                nlist.insert(0, pname[:-2])
            else:
                nlist.insert(0, '%s.' % pname)
            par = par.parent()
            
        name = ''.join(nlist)
        # now show the dialog
        dlg = VariableDetailDialog(name, vtype, val)
        dlg.exec_()
    
    def __buildTreePath(self, itm):
        """
        Private method to build up a path from the top to an item.
        
        @param itm item to build the path for (QTreeWidgetItem)
        @return list of names denoting the path from the top (list of strings)
        """
        name = unicode(itm.text(0))
        pathlist = [name]
        
        par = itm.parent()
        # build up a path from the top to the item
        while par is not None:
            pname = unicode(par.text(0))
            pathlist.insert(0, pname)
            par = par.parent()
        
        return pathlist[:]
    
    def __expandItemSignal(self, parentItem):
        """
        Private slot to handle the expanded signal.
        
        @param parentItem reference to the item being expanded (QTreeWidgetItem)
        """
        self.expandItem(parentItem)
        self.__scrollToItem = parentItem
        
    def expandItem(self, parentItem):
        """
        Public slot to handle the expanded signal.
        
        @param parentItem reference to the item being expanded (QTreeWidgetItem)
        """
        pathlist = self.__buildTreePath(parentItem)
        self.openItems.append(pathlist)
        if parentItem.populated:
            return
        
        try:
            parentItem.expand()
            self.__resort()
        except AttributeError:
            QTreeWidget.expandItem(self, parentItem)

    def collapseItem(self, parentItem):
        """
        Public slot to handle the collapsed signal.
        
        @param parentItem reference to the item being collapsed (QTreeWidgetItem)
        """
        pathlist = self.__buildTreePath(parentItem)
        self.openItems.remove(pathlist)
        
        try:
            parentItem.collapse()
        except AttributeError:
            QTreeWidget.collapseItem(self, parentItem)

    def __resort(self):
        """
        Private method to resort the tree.
        """
        if self.resortEnabled:
            self.sortItems(self.sortColumn(), self.header().sortIndicatorOrder())
    
    def handleResetUI(self):
        """
        Public method to reset the VariablesViewer.
        """
        self.clear()
        self.openItems = []
    
    def __configure(self):
        """
        Private method to open the configuration dialog.
        """
        e4App().getObject("UserInterface").showPreferences("debuggerGeneralPage")
