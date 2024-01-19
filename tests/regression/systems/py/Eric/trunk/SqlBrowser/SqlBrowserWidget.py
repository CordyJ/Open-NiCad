# -*- coding: utf-8 -*-

# Copyright (c) 2009 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the SQL Browser widget.
"""

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtSql import QSqlDatabase, QSqlError, QSqlTableModel, QSqlQueryModel, QSqlQuery

from KdeQt import KQMessageBox

from SqlConnectionDialog import SqlConnectionDialog

from Ui_SqlBrowserWidget import Ui_SqlBrowserWidget

class SqlBrowserWidget(QWidget, Ui_SqlBrowserWidget):
    """
    Class implementing the SQL Browser widget.
    
    @signal statusMessage(QString) emitted to show a status message
    """
    cCount = 0
    
    def __init__(self, parent = None):
        """
        Constructor
        
        @param parent reference to the parent widget (QWidget)
        """
        QWidget.__init__(self, parent)
        self.setupUi(self)
        
        self.table.addAction(self.insertRowAction)
        self.table.addAction(self.deleteRowAction)
        
        if QSqlDatabase.drivers().isEmpty():
            KQMessageBox.information(None,
                self.trUtf8("No database drivers found"),
                self.trUtf8("""This tool requires at least one Qt database driver. """
                """Please check the Qt documentation how to build the """
                """Qt SQL plugins."""))
        
        self.connect(self.connections, SIGNAL("tableActivated(QString)"), 
                     self.on_connections_tableActivated)
        self.connect(self.connections, SIGNAL("schemaRequested(QString)"), 
                     self.on_connections_schemaRequested)
        self.connect(self.connections, SIGNAL("cleared()"), 
                     self.on_connections_cleared)
        
        self.emit(SIGNAL("statusMessage(QString)"), self.trUtf8("Ready"))
    
    @pyqtSignature("")
    def on_clearButton_clicked(self):
        """
        Private slot to clear the SQL entry widget.
        """
        self.sqlEdit.clear()
        self.sqlEdit.setFocus()
    
    @pyqtSignature("")
    def on_executeButton_clicked(self):
        """
        Private slot to execute the entered SQL query.
        """
        self.executeQuery()
        self.sqlEdit.setFocus()
    
    @pyqtSignature("")
    def on_insertRowAction_triggered(self):
        """
        Private slot handling the action to insert a new row.
        """
        self.__insertRow()
    
    @pyqtSignature("")
    def on_deleteRowAction_triggered(self):
        """
        Private slot handling the action to delete a row.
        """
        self.__deleteRow()
    
    @pyqtSignature("QString")
    def on_connections_tableActivated(self, table):
        """
        Private slot to show the contents of a table.
        
        @param table name of the table for which to show the contents (QString)
        """
        self.showTable(table)
    
    @pyqtSignature("QString")
    def on_connections_schemaRequested(self, table):
        """
        Private slot to show the schema of a table.
        
        @param table name of the table for which to show the schema (QString)
        """
        self.showSchema(table)
    
    @pyqtSignature("")
    def on_connections_cleared(self):
        """
        Private slot to clear the table.
        """
        model = QStandardItemModel(self.table)
        self.table.setModel(model)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        
        self.updateActions()
    
    def addConnection(self, driver, dbName, user, password, host, port):
        """
        Public method to add a database connection.
        
        @param driver name of the Qt database driver (QString)
        @param dbName name of the database (QString)
        @param user user name (QString)
        @param password password (QString)
        @param host host name (QString)
        @param port port number (integer)
        """
        err = QSqlError()
        
        self.__class__.cCount += 1
        db = QSqlDatabase.addDatabase(driver.toUpper(), 
                                      QString("Browser%1").arg(self.__class__.cCount))
        db.setDatabaseName(dbName)
        db.setHostName(host)
        db.setPort(port)
        if not db.open(user, password):
            err = db.lastError()
            db = QSqlDatabase()
            QSqlDatabase.removeDatabase(QString("Browser%1").arg(self.__class__.cCount))
        
        self.connections.refresh()
        
        return err
    
    def addConnectionByDialog(self):
        """
        Public slot to add a database connection via an input dialog.
        """
        dlg = SqlConnectionDialog(self)
        if dlg.exec_() == QDialog.Accepted:
            driver, dbName, user, password, host, port = dlg.getData()
            err = self.addConnection(driver, dbName, user, password, host, port)
            
            if err.type() != QSqlError.NoError:
                KQMessageBox.warning(self,
                    self.trUtf8("Unable to open database"),
                    self.trUtf8("""An error occurred while opening the connection."""))
    
    def showTable(self, table):
        """
        Public slot to show the contents of a table.
        
        @param table name of the table to be shown (string or QString)
        """
        model = QSqlTableModel(self.table, self.connections.currentDatabase())
        model.setEditStrategy(QSqlTableModel.OnRowChange)
        model.setTable(table)
        model.select()
        if model.lastError().type() != QSqlError.NoError:
            self.emit(SIGNAL("statusMessage(QString)"), model.lastError().text())
        self.table.setModel(model)
        self.table.setEditTriggers(
            QAbstractItemView.DoubleClicked | QAbstractItemView.EditKeyPressed)
        
        self.table.resizeColumnsToContents()
        
        self.connect(self.table.selectionModel(), 
                     SIGNAL("currentRowChanged(QModelIndex, QModelIndex)"), 
                     self.updateActions)
        
        self.updateActions()
    
    def showSchema(self, table):
        """
        Public slot to show the schema of a table.
        
        @param table name of the table to be shown (string or QString)
        """
        rec = self.connections.currentDatabase().record(table)
        model = QStandardItemModel(self.table)
        
        model.insertRows(0, rec.count())
        model.insertColumns(0, 7)
        
        model.setHeaderData(0, Qt.Horizontal, QVariant("Fieldname"))
        model.setHeaderData(1, Qt.Horizontal, QVariant("Type"))
        model.setHeaderData(2, Qt.Horizontal, QVariant("Length"))
        model.setHeaderData(3, Qt.Horizontal, QVariant("Precision"))
        model.setHeaderData(4, Qt.Horizontal, QVariant("Required"))
        model.setHeaderData(5, Qt.Horizontal, QVariant("Auto Value"))
        model.setHeaderData(6, Qt.Horizontal, QVariant("Default Value"))
        
        for i in range(rec.count()):
            fld = rec.field(i)
            model.setData(model.index(i, 0), QVariant(fld.name()))
            if fld.typeID() == -1:
                model.setData(model.index(i, 1), 
                              QVariant(QString(QVariant.typeToName(fld.type()))))
            else:
                model.setData(model.index(i, 1), QVariant(QString("%1 (%2)")\
                                                 .arg(QVariant.typeToName(fld.type()))\
                                                 .arg(fld.typeID())))
            if fld.length() < 0:
                model.setData(model.index(i, 2), QVariant("?"))
            else:
                model.setData(model.index(i, 2), QVariant(fld.length()))
            if fld.precision() < 0:
                model.setData(model.index(i, 3), QVariant("?"))
            else:
                model.setData(model.index(i, 3), QVariant(fld.precision()))
            if fld.requiredStatus() == -1:
                model.setData(model.index(i, 4), QVariant("?"))
            else:
                model.setData(model.index(i, 4), QVariant(bool(fld.requiredStatus())))
            model.setData(model.index(i, 5), QVariant(fld.isAutoValue()))
            model.setData(model.index(i, 6), QVariant(fld.defaultValue()))
        
        self.table.setModel(model)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        
        self.table.resizeColumnsToContents()
        
        self.updateActions()
    
    def updateActions(self):
        """
        Public slot to update the actions.
        """
        enableIns = isinstance(self.table.model(), QSqlTableModel)
        enableDel = enableIns & self.table.currentIndex().isValid()
        
        self.insertRowAction.setEnabled(enableIns)
        self.deleteRowAction.setEnabled(enableDel)
    
    def __insertRow(self):
        """
        Privat slot to insert a row into the database table.
        """
        model = self.table.model()
        if not isinstance(model, QSqlTableModel):
            return
        
        insertIndex = self.table.currentIndex()
        if insertIndex.row() == -1:
            row = 0
        else:
            row = insertIndex.row()
        model.insertRow(row)
        insertIndex = model.index(row, 0)
        self.table.setCurrentIndex(insertIndex)
        self.table.edit(insertIndex)
    
    def __deleteRow(self):
        """
        Privat slot to delete a row from the database table.
        """
        model = self.table.model()
        if not isinstance(model, QSqlTableModel):
            return
        
        model.setEditStrategy(QSqlTableModel.OnManualSubmit)
        
        currentSelection = self.table.selectionModel().selectedIndexes()
        for selectedIndex in currentSelection:
            if selectedIndex.column() != 0:
                continue
            model.removeRow(selectedIndex.row())
        
        model.submitAll()
        model.setEditStrategy(QSqlTableModel.OnRowChange)
        
        self.updateActions()
    
    def executeQuery(self):
        """
        Public slot to execute the entered query.
        """
        model = QSqlQueryModel(self.table)
        model.setQuery(
            QSqlQuery(self.sqlEdit.toPlainText(), self.connections.currentDatabase()))
        self.table.setModel(model)
        
        if model.lastError().type() != QSqlError.NoError:
            self.emit(SIGNAL("statusMessage(QString)"), model.lastError().text())
        elif model.query().isSelect():
            self.emit(SIGNAL("statusMessage(QString)"), self.trUtf8("Query OK."))
        else:
            self.emit(SIGNAL("statusMessage(QString)"), 
                self.trUtf8("Query OK, number of affected rows: %1")\
                    .arg(model.query().numRowsAffected()))
        
        self.table.resizeColumnsToContents()
        
        self.updateActions()
