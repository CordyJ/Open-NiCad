# -*- coding: utf-8 -*-

# Copyright (c) 2009 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a thread class populating and updating the QtHelp
documentation database.
"""

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtHelp import QHelpEngineCore

from eric4config import getConfig

class HelpDocsInstaller(QThread):
    """
    Class implementing the worker thread populating and updating the QtHelp
    documentation database.
    
    @signal errorMessage(const QString&) emitted, if an error occurred during
        the installation of the documentation
    @signal docsInstalled(bool) emitted after the installation has finished
    """
    def __init__(self, collection):
        """
        Constructor
        
        @param collection full pathname of the collection file (QString)
        """
        QThread.__init__(self)
        
        self.__abort = False
        self.__collection = collection
        self.__mutex = QMutex()
    
    def stop(self):
        """
        Public slot to stop the installation procedure.
        """
        if not self.isRunning():
            return
        
        self.__mutex.lock()
        self.__abort = True
        self.__mutex.unlock()
        self.wait()
    
    def installDocs(self):
        """
        Public method to start the installation procedure.
        """
        self.start(QThread.LowPriority)
    
    def run(self):
        """
        Protected method executed by the thread.
        """
        engine = QHelpEngineCore(self.__collection)
        engine.setupData()
        changes = False
        
        qtDocs = ["designer", "linguist", "qt"]
        for doc in qtDocs:
            changes |= self.__installQtDoc(doc, engine)
            self.__mutex.lock()
            if self.__abort:
                engine = None
                self.__mutex.unlock()
                return
            self.__mutex.unlock()
        
        changes |= self.__installEric4Doc(engine)
        engine = None
        del engine
        self.emit(SIGNAL("docsInstalled(bool)"), changes)
    
    def __installQtDoc(self, name, engine):
        """
        Private method to install/update a Qt help document.
        
        @param name name of the Qt help document (string or QString)
        @param engine reference to the help engine (QHelpEngineCore)
        @return flag indicating success (boolean)
        """
        versionKey = QString("qt_version_%1@@%2").arg(qVersion()).arg(name)
        info = engine.customValue(versionKey, QVariant("")).toString()
        lst = info.split('|')
        
        dt = QDateTime()
        if len(lst) and not lst[0].isEmpty():
            dt = QDateTime.fromString(lst[0], Qt.ISODate)
        
        qchFile = QString()
        if len(lst) == 2:
            qchFile = lst[1]
        
        docsPath = QDir(QLibraryInfo.location(QLibraryInfo.DocumentationPath) + \
                   QDir.separator() + "qch")
        
        files = docsPath.entryList(QStringList("*.qch"))
        if files.isEmpty():
            engine.setCustomValue(versionKey, 
                QVariant(QDateTime().toString(Qt.ISODate) + '|'))
            return False
        
        for f in files:
            if f.startsWith(name):
                fi = QFileInfo(docsPath.absolutePath() + QDir.separator() + f)
                namespace = QHelpEngineCore.namespaceName(fi.absoluteFilePath())
                if namespace.isEmpty():
                    continue
                
                if dt.isValid() and \
                   namespace in engine.registeredDocumentations() and \
                   fi.lastModified().toString(Qt.ISODate) == dt.toString(Qt.ISODate) and \
                   qchFile == fi.absoluteFilePath():
                    return False
                
                if namespace in engine.registeredDocumentations():
                    engine.unregisterDocumentation(namespace)
                
                if not engine.registerDocumentation(fi.absoluteFilePath()):
                    self.emit(SIGNAL("errorMessage(const QString&)"), 
                        self.trUtf8("""The file <b>%1</b> could not be registered."""
                                    """<br/>Reason: %2""")\
                            .arg(fi.absoluteFilePath)\
                            .arg(engine.error())
                    )
                    return False
                
                engine.setCustomValue(versionKey, 
                    QVariant(fi.lastModified().toString(Qt.ISODate) + '|' + \
                    fi.absoluteFilePath()))
                return True
        
        return False
    
    def __installEric4Doc(self, engine):
        """
        Private method to install/update the eric4 help documentation.
        
        @param engine reference to the help engine (QHelpEngineCore)
        @return flag indicating success (boolean)
        """
        versionKey = QString("eric4_ide")
        info = engine.customValue(versionKey, QVariant("")).toString()
        lst = info.split('|')
        
        dt = QDateTime()
        if len(lst) and not lst[0].isEmpty():
            dt = QDateTime.fromString(lst[0], Qt.ISODate)
        
        qchFile = QString()
        if len(lst) == 2:
            qchFile = lst[1]
        
        docsPath = QDir(QString(getConfig("ericDocDir")) + QDir.separator() + "Help")
        
        files = docsPath.entryList(QStringList("*.qch"))
        if files.isEmpty():
            engine.setCustomValue(versionKey, 
                QVariant(QDateTime().toString(Qt.ISODate) + '|'))
            return False
        
        for f in files:
            if f == "source.qch":
                fi = QFileInfo(docsPath.absolutePath() + QDir.separator() + f)
                if dt.isValid() and \
                   fi.lastModified().toString(Qt.ISODate) == dt.toString(Qt.ISODate) and \
                   qchFile == fi.absoluteFilePath():
                    return False
                
                namespace = QHelpEngineCore.namespaceName(fi.absoluteFilePath())
                if namespace.isEmpty():
                    continue
                
                if namespace in engine.registeredDocumentations():
                    engine.unregisterDocumentation(namespace)
                
                if not engine.registerDocumentation(fi.absoluteFilePath()):
                    self.emit(SIGNAL("errorMessage(const QString&)"), 
                        self.trUtf8("""The file <b>%1</b> could not be registered."""
                                    """<br/>Reason: %2""")\
                            .arg(fi.absoluteFilePath)\
                            .arg(engine.error())
                    )
                    return False
                
                engine.setCustomValue(versionKey, 
                    QVariant(fi.lastModified().toString(Qt.ISODate) + '|' + \
                    fi.absoluteFilePath()))
                return True
        
        return False
