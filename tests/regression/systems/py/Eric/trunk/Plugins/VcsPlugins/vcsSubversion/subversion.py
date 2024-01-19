# -*- coding: utf-8 -*-

# Copyright (c) 2003 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the version control systems interface to Subversion.
"""

import os
import shutil
import types
import urllib

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from KdeQt import KQMessageBox, KQInputDialog
from KdeQt.KQApplication import e4App

from VCS.VersionControl import VersionControl

from SvnDialog import SvnDialog
from SvnCommitDialog import SvnCommitDialog
from SvnLogDialog import SvnLogDialog
from SvnLogBrowserDialog import SvnLogBrowserDialog
from SvnDiffDialog import SvnDiffDialog
from SvnRevisionSelectionDialog import SvnRevisionSelectionDialog
from SvnStatusDialog import SvnStatusDialog
from SvnTagDialog import SvnTagDialog
from SvnTagBranchListDialog import SvnTagBranchListDialog
from SvnCopyDialog import SvnCopyDialog
from SvnCommandDialog import SvnCommandDialog
from SvnSwitchDialog import SvnSwitchDialog
from SvnMergeDialog import SvnMergeDialog
from SvnPropListDialog import SvnPropListDialog
from SvnPropSetDialog import SvnPropSetDialog
from SvnOptionsDialog import SvnOptionsDialog
from SvnNewProjectOptionsDialog import SvnNewProjectOptionsDialog
from SvnBlameDialog import SvnBlameDialog
from SvnRelocateDialog import SvnRelocateDialog
from SvnUrlSelectionDialog import SvnUrlSelectionDialog
from SvnRepoBrowserDialog import SvnRepoBrowserDialog
from SvnStatusMonitorThread import SvnStatusMonitorThread

from ProjectBrowserHelper import SvnProjectBrowserHelper
from ProjectHelper import SvnProjectHelper

import Preferences
import Utilities

class Subversion(VersionControl):
    """
    Class implementing the version control systems interface to Subversion.
    
    @signal committed() emitted after the commit action has completed
    """
    def __init__(self, plugin, parent=None, name=None):
        """
        Constructor
        
        @param plugin reference to the plugin object
        @param parent parent widget (QWidget)
        @param name name of this object (string or QString)
        """
        VersionControl.__init__(self, parent, name)
        self.defaultOptions = {
            'global' : [''],
            'commit' : [''],
            'checkout' : [''],
            'update' : [''],
            'add' : [''],
            'remove' : [''],
            'diff' : [''],
            'log' : [''],
            'history' : [''],
            'status' : [''],
            'tag' : [''],
            'export' : ['']
        }
        self.interestingDataKeys = [
            "standardLayout",
        ]
        
        self.__plugin = plugin
        self.__ui = parent
        
        self.options = self.defaultOptions
        self.otherData["standardLayout"] = True
        self.tagsList = QStringList()
        self.branchesList = QStringList()
        self.allTagsBranchesList = QStringList()
        self.mergeList = [QStringList(), QStringList(), QStringList()]
        self.showedTags = False
        self.showedBranches = False
        
        self.tagTypeList = QStringList()
        self.tagTypeList.append('tags')
        self.tagTypeList.append('branches')
        
        self.commandHistory = QStringList()
        self.wdHistory = QStringList()
        
        if os.environ.has_key("SVN_ASP_DOT_NET_HACK"):
            self.adminDir = '_svn'
        else:
            self.adminDir = '.svn'
        
        self.log = None
        self.diff = None
        self.status = None
        self.propList = None
        self.tagbranchList = None
        self.blame = None
        self.repoBrowser = None
        
        # regular expression object for evaluation of the status output
        self.rx_status1 = QRegExp('(.{8})\\s+([0-9-]+)\\s+([0-9?]+)\\s+([\\w?]+)\\s+(.+)')
        self.rx_status2 = QRegExp('(.{8})\\s+(.+)\\s*')
        self.statusCache = {}
        
        self.__commitData = {}
        self.__commitDialog = None
        
    def getPlugin(self):
        """
        Public method to get a reference to the plugin object.
        
        @return reference to the plugin object (VcsSubversionPlugin)
        """
        return self.__plugin
        
    def vcsShutdown(self):
        """
        Public method used to shutdown the Subversion interface.
        """
        if self.log is not None:
            self.log.close()
        if self.diff is not None:
            self.diff.close()
        if self.status is not None:
            self.status.close()
        if self.propList is not None:
            self.propList.close()
        if self.tagbranchList is not None:
            self.tagbranchList.close()
        if self.blame is not None:
            self.blame.close()
        if self.repoBrowser is not None:
            self.repoBrowser.close()
        
    def vcsExists(self):
        """
        Public method used to test for the presence of the svn executable.
        
        @return flag indicating the existance (boolean) and an error message (QString)
        """
        self.versionStr = ''
        errMsg = QString()
        ioEncoding = str(Preferences.getSystem("IOEncoding"))
        
        process = QProcess()
        process.start('svn', QStringList('--version'))
        procStarted = process.waitForStarted()
        if procStarted:
            finished = process.waitForFinished(30000)
            if finished and process.exitCode() == 0:
                output = \
                    unicode(process.readAllStandardOutput(), ioEncoding, 'replace')
                self.versionStr = output.split()[2]
                return True, errMsg
            else:
                if finished:
                    errMsg = \
                        self.trUtf8("The svn process finished with the exit code %1")\
                        .arg(process.exitCode())
                else:
                    errMsg = self.trUtf8("The svn process did not finish within 30s.")
        else:
            errMsg = self.trUtf8("Could not start the svn executable.")
        
        return False, errMsg
        
    def vcsInit(self, vcsDir, noDialog = False):
        """
        Public method used to initialize the subversion repository.
        
        The subversion repository has to be initialized from outside eric4
        because the respective command always works locally. Therefore we
        always return TRUE without doing anything.
        
        @param vcsDir name of the VCS directory (string)
        @param noDialog flag indicating quiet operations (boolean)
        @return always TRUE
        """
        return True
        
    def vcsConvertProject(self, vcsDataDict, project):
        """
        Public method to convert an uncontrolled project to a version controlled project.
        
        @param vcsDataDict dictionary of data required for the conversion
        @param project reference to the project object
        """
        success = self.vcsImport(vcsDataDict, project.ppath)[0]
        if not success:
            KQMessageBox.critical(None,
                self.trUtf8("Create project in repository"),
                self.trUtf8("""The project could not be created in the repository."""
                            """ Maybe the given repository doesn't exist or the"""
                            """ repository server is down."""))
        else:
            cwdIsPpath = False
            if os.getcwd() == project.ppath:
                os.chdir(os.path.dirname(project.ppath))
                cwdIsPpath = True
            tmpProjectDir = "%s_tmp" % project.ppath
            shutil.rmtree(tmpProjectDir, True)
            os.rename(project.ppath, tmpProjectDir)
            os.makedirs(project.ppath)
            self.vcsCheckout(vcsDataDict, project.ppath)
            if cwdIsPpath:
                os.chdir(project.ppath)
            self.vcsCommit(project.ppath, vcsDataDict["message"], True)
            pfn = project.pfile
            if not os.path.isfile(pfn):
                pfn += "z"
            if not os.path.isfile(pfn):
                KQMessageBox.critical(None,
                    self.trUtf8("New project"),
                    self.trUtf8("""The project could not be checked out of the"""
                                """ repository.<br />"""
                                """Restoring the original contents."""))
                if os.getcwd() == project.ppath:
                    os.chdir(os.path.dirname(project.ppath))
                    cwdIsPpath = True
                else:
                    cwdIsPpath = False
                shutil.rmtree(project.ppath, True)
                os.rename(tmpProjectDir, project.ppath)
                project.pdata["VCS"] = ['None']
                project.vcs = None
                project.setDirty(True)
                project.saveProject()
                project.closeProject()
                return
            shutil.rmtree(tmpProjectDir, True)
            project.openProject(pfn)
        
    def vcsImport(self, vcsDataDict, projectDir, noDialog = False):
        """
        Public method used to import the project into the Subversion repository.
        
        @param vcsDataDict dictionary of data required for the import
        @param projectDir project directory (string)
        @param noDialog flag indicating quiet operations
        @return flag indicating an execution without errors (boolean)
            and a flag indicating the version controll status (boolean)
        """
        noDialog = False
        msg = QString(vcsDataDict["message"])
        if msg.isEmpty():
            msg = QString('***')
        
        vcsDir = self.svnNormalizeURL(vcsDataDict["url"])
        if vcsDir.startswith('/'):
            vcsDir = 'file://%s' % vcsDir
        elif vcsDir[1] in ['|', ':']:
            vcsDir = 'file:///%s' % vcsDir
        
        project = vcsDir[vcsDir.rfind('/')+1:]
        
        # create the dir structure to be imported into the repository
        tmpDir = '%s_tmp' % projectDir
        try:
            os.makedirs(tmpDir)
            if self.otherData["standardLayout"]:
                os.mkdir(os.path.join(tmpDir, project))
                os.mkdir(os.path.join(tmpDir, project, 'branches'))
                os.mkdir(os.path.join(tmpDir, project, 'tags'))
                shutil.copytree(projectDir, os.path.join(tmpDir, project, 'trunk'))
            else:
                shutil.copytree(projectDir, os.path.join(tmpDir, project))
        except OSError, e:
            if os.path.isdir(tmpDir):
                shutil.rmtree(tmpDir, True)            
            return False, False
        
        args = QStringList()
        args.append('import')
        self.addArguments(args, self.options['global'])
        args.append('-m')
        args.append(msg)
        args.append(self.__svnURL(vcsDir))
        
        if noDialog:
            status = self.startSynchronizedProcess(QProcess(), "svn", args,
                os.path.join(tmpDir, project))
        else:
            dia = SvnDialog(self.trUtf8('Importing project into Subversion repository'))
            res = dia.startProcess(args, os.path.join(tmpDir, project))
            if res:
                dia.exec_()
            status = dia.normalExit()
        
        shutil.rmtree(tmpDir, True)
        return status, False
        
    def vcsCheckout(self, vcsDataDict, projectDir, noDialog = False):
        """
        Public method used to check the project out of the Subversion repository.
        
        @param vcsDataDict dictionary of data required for the checkout
        @param projectDir project directory to create (string)
        @param noDialog flag indicating quiet operations
        @return flag indicating an execution without errors (boolean)
        """
        noDialog = False
        try:
            tag = vcsDataDict["tag"]
        except KeyError:
            tag = None
        vcsDir = self.svnNormalizeURL(vcsDataDict["url"])
        if vcsDir.startswith('/'):
            vcsDir = 'file://%s' % vcsDir
        elif vcsDir[1] in ['|', ':']:
            vcsDir = 'file:///%s' % vcsDir
            
        if self.otherData["standardLayout"]:
            if tag is None or tag == '':
                svnUrl = '%s/trunk' % vcsDir
            else:
                if not tag.startswith('tags') and not tag.startswith('branches'):
                    type, ok = KQInputDialog.getItem(\
                        None,
                        self.trUtf8("Subversion Checkout"),
                        self.trUtf8("The tag must be a normal tag (tags) or"
                            " a branch tag (branches)."
                            " Please select from the list."),
                        self.tagTypeList,
                        0, False)
                    if not ok:
                        return False
                    tag = '%s/%s' % (unicode(type), tag)
                svnUrl = '%s/%s' % (vcsDir, tag)
        else:
            svnUrl = vcsDir
        
        args = QStringList()
        args.append('checkout')
        self.addArguments(args, self.options['global'])
        self.addArguments(args, self.options['checkout'])
        args.append(self.__svnURL(svnUrl))
        args.append(projectDir)
        
        if noDialog:
            return self.startSynchronizedProcess(QProcess(), 'svn', args)
        else:
            dia = SvnDialog(self.trUtf8('Checking project out of Subversion repository'))
            res = dia.startProcess(args)
            if res:
                dia.exec_()
            return dia.normalExit()
        
    def vcsExport(self, vcsDataDict, projectDir):
        """
        Public method used to export a directory from the Subversion repository.
        
        @param vcsDataDict dictionary of data required for the checkout
        @param projectDir project directory to create (string)
        @return flag indicating an execution without errors (boolean)
        """
        try:
            tag = vcsDataDict["tag"]
        except KeyError:
            tag = None
        vcsDir = self.svnNormalizeURL(vcsDataDict["url"])
        if vcsDir.startswith('/') or vcsDir[1] == '|':
            vcsDir = 'file://%s' % vcsDir
            
        if self.otherData["standardLayout"]:
            if tag is None or tag == '':
                svnUrl = '%s/trunk' % vcsDir
            else:
                if not tag.startswith('tags') and not tag.startswith('branches'):
                    type, ok = KQInputDialog.getItem(\
                        None,
                        self.trUtf8("Subversion Export"),
                        self.trUtf8("The tag must be a normal tag (tags) or"
                            " a branch tag (branches)."
                            " Please select from the list."),
                        self.tagTypeList,
                        0, False)
                    if not ok:
                        return False
                    tag = '%s/%s' % (unicode(type), tag)
                svnUrl = '%s/%s' % (vcsDir, tag)
        else:
            svnUrl = vcsDir
        
        args = QStringList()
        args.append('export')
        self.addArguments(args, self.options['global'])
        args.append("--force")
        args.append(self.__svnURL(svnUrl))
        args.append(projectDir)
        
        dia = SvnDialog(self.trUtf8('Exporting project from Subversion repository'))
        res = dia.startProcess(args)
        if res:
            dia.exec_()
        return dia.normalExit()
        
    def vcsCommit(self, name, message, noDialog = False):
        """
        Public method used to make the change of a file/directory permanent in the
        Subversion repository.
        
        @param name file/directory name to be committed (string or list of strings)
        @param message message for this operation (string)
        @param noDialog flag indicating quiet operations
        """
        msg = QString(message)
        
        if not noDialog and msg.isEmpty():
            # call CommitDialog and get message from there
            if self.__commitDialog is None:
                self.__commitDialog = SvnCommitDialog(self, self.__ui)
                self.connect(self.__commitDialog, SIGNAL("accepted()"), 
                             self.__vcsCommit_Step2)
            self.__commitDialog.show()
            self.__commitDialog.raise_()
            self.__commitDialog.activateWindow()
        
        self.__commitData["name"] = name
        self.__commitData["msg"] = msg
        self.__commitData["noDialog"] = noDialog
        
        if noDialog:
            self.__vcsCommit_Step2()
        
    def __vcsCommit_Step2(self):
        """
        Private slot performing the second step of the commit action.
        """
        name = self.__commitData["name"]
        msg = self.__commitData["msg"]
        noDialog = self.__commitData["noDialog"]
        
        if self.__commitDialog is not None:
            msg = self.__commitDialog.logMessage()
            if self.__commitDialog.hasChangelists():
                changelists, keepChangelists = self.__commitDialog.changelistsData()
            else:
                changelists, keepChangelists = QStringList(), False
            self.disconnect(self.__commitDialog, SIGNAL("accepted()"), 
                            self.__vcsCommit_Step2)
            self.__commitDialog = None
        else:
            changelists, keepChangelists = QStringList(), False
        
        if msg.isEmpty():
            msg = QString('***')
        
        args = QStringList()
        args.append('commit')
        self.addArguments(args, self.options['global'])
        self.addArguments(args, self.options['commit'])
        if keepChangelists:
            args.append("--keep-changelists")
        for changelist in changelists:
            args.append("--changelist")
            args.append(changelist)
        args.append("-m")
        args.append(msg)
        if type(name) is types.ListType:
            dname, fnames = self.splitPathList(name)
            self.addArguments(args, fnames)
        else:
            dname, fname = self.splitPath(name)
            args.append(fname)
        
        if self.svnGetReposName(dname).startswith('http') or \
           self.svnGetReposName(dname).startswith('svn'):
            noDialog = False
        
        if noDialog:
            self.startSynchronizedProcess(QProcess(), "svn", args, dname)
        else:
            dia = SvnDialog(self.trUtf8('Commiting changes to Subversion repository'))
            res = dia.startProcess(args, dname)
            if res:
                dia.exec_()
        self.emit(SIGNAL("committed()"))
        self.checkVCSStatus()
        
    def vcsUpdate(self, name, noDialog = False):
        """
        Public method used to update a file/directory with the Subversion repository.
        
        @param name file/directory name to be updated (string or list of strings)
        @param noDialog flag indicating quiet operations (boolean)
        @return flag indicating, that the update contained an add
            or delete (boolean)
        """
        args = QStringList()
        args.append('update')
        self.addArguments(args, self.options['global'])
        self.addArguments(args, self.options['update'])
        if self.versionStr >= '1.5.0':
            args.append('--accept')
            args.append('postpone')
        if type(name) is types.ListType:
            dname, fnames = self.splitPathList(name)
            self.addArguments(args, fnames)
        else:
            dname, fname = self.splitPath(name)
            args.append(fname)
        
        if noDialog:
            self.startSynchronizedProcess(QProcess(), "svn", args, dname)
            res = False
        else:
            dia = SvnDialog(self.trUtf8('Synchronizing with the Subversion repository'))
            res = dia.startProcess(args, dname)
            if res:
                dia.exec_()
                res = dia.hasAddOrDelete()
        self.checkVCSStatus()
        return res
        
    def vcsAdd(self, name, isDir = False, noDialog = False):
        """
        Public method used to add a file/directory to the Subversion repository.
        
        @param name file/directory name to be added (string)
        @param isDir flag indicating name is a directory (boolean)
        @param noDialog flag indicating quiet operations
        """
        args = QStringList()
        args.append('add')
        self.addArguments(args, self.options['global'])
        self.addArguments(args, self.options['add'])
        args.append('--non-recursive')
        if noDialog and '--force' not in args:
            args.append('--force')
        
        if type(name) is types.ListType:
            if isDir:
                dname, fname = os.path.split(unicode(name[0]))
            else:
                dname, fnames = self.splitPathList(name)
        else:
            if isDir:
                dname, fname = os.path.split(unicode(name))
            else:
                dname, fname = self.splitPath(name)
        tree = []
        wdir = dname
        while not os.path.exists(os.path.join(dname, self.adminDir)):
            # add directories recursively, if they aren't in the repository already
            tree.insert(-1, dname)
            dname = os.path.split(dname)[0]
            wdir = dname
        self.addArguments(args, tree)
        
        if type(name) is types.ListType:
            tree2 = []
            for n in name:
                d = os.path.split(n)[0]
                while not os.path.exists(os.path.join(d, self.adminDir)):
                    if d in tree2 + tree:
                        break
                    tree2.append(d)
                    d = os.path.split(d)[0]
            tree2.reverse()
            self.addArguments(args, tree2)
            self.addArguments(args, name)
        else:
            args.append(name)
        
        if noDialog:
            self.startSynchronizedProcess(QProcess(), "svn", args, wdir)
        else:
            dia = SvnDialog(\
                self.trUtf8('Adding files/directories to the Subversion repository'))
            res = dia.startProcess(args, wdir)
            if res:
                dia.exec_()
        
    def vcsAddBinary(self, name, isDir = False):
        """
        Public method used to add a file/directory in binary mode to the
        Subversion repository.
        
        @param name file/directory name to be added (string)
        @param isDir flag indicating name is a directory (boolean)
        """
        self.vcsAdd(name, isDir)
        
    def vcsAddTree(self, path):
        """
        Public method to add a directory tree rooted at path to the Subversion repository.
        
        @param path root directory of the tree to be added (string or list of strings))
        """
        args = QStringList()
        args.append('add')
        self.addArguments(args, self.options['global'])
        self.addArguments(args, self.options['add'])
        
        tree = []
        if type(path) is types.ListType:
            dname, fnames = self.splitPathList(path)
            for n in path:
                d = os.path.split(n)[0]
                while not os.path.exists(os.path.join(d, self.adminDir)):
                    # add directories recursively, 
                    # if they aren't in the repository already
                    if d in tree:
                        break
                    tree.append(d)
                    d = os.path.split(d)[0]
            tree.reverse()
        else:
            dname, fname = os.path.split(unicode(path))
            while not os.path.exists(os.path.join(dname, self.adminDir)):
                # add directories recursively,
                # if they aren't in the repository already
                tree.insert(-1, dname)
                dname = os.path.split(dname)[0]
        if tree:
            self.vcsAdd(tree, True)
        
        if type(path) is types.ListType:
            self.addArguments(args, path)
        else:
            args.append(path)
        
        dia = SvnDialog(\
            self.trUtf8('Adding directory trees to the Subversion repository'))
        res = dia.startProcess(args, dname)
        if res:
            dia.exec_()
        
    def vcsRemove(self, name, project = False, noDialog = False):
        """
        Public method used to remove a file/directory from the Subversion repository.
        
        The default operation is to remove the local copy as well.
        
        @param name file/directory name to be removed (string or list of strings))
        @param project flag indicating deletion of a project tree (boolean) (not needed)
        @param noDialog flag indicating quiet operations
        @return flag indicating successfull operation (boolean)
        """
        args = QStringList()
        args.append('delete')
        self.addArguments(args, self.options['global'])
        self.addArguments(args, self.options['remove'])
        if noDialog and '--force' not in args:
            args.append('--force')
        
        if type(name) is types.ListType:
            self.addArguments(args, name)
        else:
            args.append(name)
        
        if noDialog:
            res = self.startSynchronizedProcess(QProcess(), "svn", args)
        else:
            dia = SvnDialog(\
                self.trUtf8('Removing files/directories from the Subversion repository'))
            res = dia.startProcess(args)
            if res:
                dia.exec_()
                res = dia.normalExit()
        
        return res
        
    def vcsMove(self, name, project, target = None, noDialog = False):
        """
        Public method used to move a file/directory.
        
        @param name file/directory name to be moved (string)
        @param project reference to the project object
        @param target new name of the file/directory (string)
        @param noDialog flag indicating quiet operations
        @return flag indicating successfull operation (boolean)
        """
        rx_prot = QRegExp('(file:|svn:|svn+ssh:|http:|https:).+')
        opts = self.options['global'][:]
        force = '--force' in opts
        if force:
            del opts[opts.index('--force')]
        
        res = False
        if noDialog:
            if target is None:
                return False
            force = True
            accepted = True
        else:
            dlg = SvnCopyDialog(name, None, True, force)
            accepted = (dlg.exec_() == QDialog.Accepted)
            if accepted:
                target, force = dlg.getData()
        
        if accepted:
            isdir = os.path.isdir(name)
            args = QStringList()
            args.append('move')
            self.addArguments(args, opts)
            if force:
                args.append('--force')
            if rx_prot.exactMatch(target):
                args.append('--message')
                args.append(QString('Moving %1 to %2').arg(name).arg(target))
                target = self.__svnURL(target)
            else:
                target = unicode(target)
            args.append(name)
            args.append(target)
            
            if noDialog:
                res = self.startSynchronizedProcess(QProcess(), "svn", args)
            else:
                dia = SvnDialog(self.trUtf8('Moving %1')
                    .arg(name))
                res = dia.startProcess(args)
                if res:
                    dia.exec_()
                    res = dia.normalExit()
            if res and not rx_prot.exactMatch(target):
                if target.startswith(project.getProjectPath()):
                    if os.path.isdir(name):
                        project.moveDirectory(name, target)
                    else:
                        project.renameFileInPdata(name, target)
                else:
                    if os.path.isdir(name):
                        project.removeDirectory(name)
                    else:
                        project.removeFile(name)
        return res
        
    def vcsLog(self, name):
        """
        Public method used to view the log of a file/directory from the 
        Subversion repository.
        
        @param name file/directory name to show the log of (string)
        """
        self.log = SvnLogDialog(self)
        self.log.show()
        self.log.start(name)
        
    def vcsDiff(self, name):
        """
        Public method used to view the difference of a file/directory to the 
        Subversion repository.
        
        If name is a directory and is the project directory, all project files
        are saved first. If name is a file (or list of files), which is/are being edited 
        and has unsaved modification, they can be saved or the operation may be aborted.
        
        @param name file/directory name to be diffed (string)
        """
        if type(name) is types.ListType:
            names = name[:]
        else:
            names = [name]
        for nam in names:
            if os.path.isfile(nam):
                editor = e4App().getObject("ViewManager").getOpenEditor(nam)
                if editor and not editor.checkDirty() :
                    return
            else:
                project = e4App().getObject("Project")
                if nam == project.ppath and not project.saveAllScripts():
                    return
        self.diff = SvnDiffDialog(self)
        self.diff.show()
        QApplication.processEvents()
        self.diff.start(name)
        
    def vcsStatus(self, name):
        """
        Public method used to view the status of files/directories in the 
        Subversion repository.
        
        @param name file/directory name(s) to show the status of
            (string or list of strings)
        """
        self.status = SvnStatusDialog(self)
        self.status.show()
        self.status.start(name)
        
    def vcsTag(self, name):
        """
        Public method used to set the tag of a file/directory in the 
        Subversion repository.
        
        @param name file/directory name to be tagged (string)
        """
        dname, fname = self.splitPath(name)
        
        reposURL = self.svnGetReposName(dname)
        if reposURL is None:
            KQMessageBox.critical(None,
                self.trUtf8("Subversion Error"),
                self.trUtf8("""The URL of the project repository could not be"""
                    """ retrieved from the working copy. The tag operation will"""
                    """ be aborted"""))
            return
        
        if self.otherData["standardLayout"]:
            url = None
        else:
            url = self.svnNormalizeURL(reposURL)
        dlg = SvnTagDialog(self.allTagsBranchesList, url, 
                           self.otherData["standardLayout"])
        if dlg.exec_() == QDialog.Accepted:
            tag, tagOp = dlg.getParameters()
            self.allTagsBranchesList.removeAll(tag)
            self.allTagsBranchesList.prepend(tag)
        else:
            return
        
        if self.otherData["standardLayout"]:
            rx_base = QRegExp('(.+)/(trunk|tags|branches).*')
            if not rx_base.exactMatch(reposURL):
                KQMessageBox.critical(None,
                    self.trUtf8("Subversion Error"),
                    self.trUtf8("""The URL of the project repository has an"""
                        """ invalid format. The tag operation will"""
                        """ be aborted"""))
                return
            
            reposRoot = unicode(rx_base.cap(1))
            if tagOp in [1, 4]:
                url = '%s/tags/%s' % (reposRoot, urllib.quote(unicode(tag)))
            elif tagOp in [2, 8]:
                url = '%s/branches/%s' % (reposRoot, urllib.quote(unicode(tag)))
        else:
            url = self.__svnURL(unicode(tag))
        
        args = QStringList()
        if tagOp in [1, 2]:
            args.append('copy')
            self.addArguments(args, self.options['global'])
            self.addArguments(args, self.options['tag'])
            args.append('--message')
            args.append('Created tag <%s>' % unicode(tag))
            args.append(reposURL)
            args.append(url)
        else:
            args.append('delete')
            self.addArguments(args, self.options['global'])
            self.addArguments(args, self.options['tag'])
            args.append('--message')
            args.append('Deleted tag <%s>' % unicode(tag))
            args.append(url)
        
        dia = SvnDialog(self.trUtf8('Tagging %1 in the Subversion repository')
            .arg(name))
        res = dia.startProcess(args)
        if res:
            dia.exec_()
        
    def vcsRevert(self, name):
        """
        Public method used to revert changes made to a file/directory.
        
        @param name file/directory name to be reverted (string)
        """
        args = QStringList()
        args.append('revert')
        self.addArguments(args, self.options['global'])
        if type(name) is types.ListType:
            self.addArguments(args, name)
        else:
            if os.path.isdir(name):
                args.append('--recursive')
            args.append(name)
        
        dia = SvnDialog(self.trUtf8('Reverting changes'))
        res = dia.startProcess(args)
        if res:
            dia.exec_()
        self.checkVCSStatus()
    
    def vcsSwitch(self, name):
        """
        Public method used to switch a directory to a different tag/branch.
        
        @param name directory name to be switched (string)
        """
        dname, fname = self.splitPath(name)
        
        reposURL = self.svnGetReposName(dname)
        if reposURL is None:
            KQMessageBox.critical(None,
                self.trUtf8("Subversion Error"),
                self.trUtf8("""The URL of the project repository could not be"""
                    """ retrieved from the working copy. The switch operation will"""
                    """ be aborted"""))
            return
        
        if self.otherData["standardLayout"]:
            url = None
        else:
            url = self.svnNormalizeURL(reposURL)
        dlg = SvnSwitchDialog(self.allTagsBranchesList, url, 
                              self.otherData["standardLayout"])
        if dlg.exec_() == QDialog.Accepted:
            tag, tagType = dlg.getParameters()
            self.allTagsBranchesList.removeAll(tag)
            self.allTagsBranchesList.prepend(tag)
        else:
            return
        
        if self.otherData["standardLayout"]:
            rx_base = QRegExp('(.+)/(trunk|tags|branches).*')
            if not rx_base.exactMatch(reposURL):
                KQMessageBox.critical(None,
                    self.trUtf8("Subversion Error"),
                    self.trUtf8("""The URL of the project repository has an"""
                        """ invalid format. The switch operation will"""
                        """ be aborted"""))
                return
            
            reposRoot = unicode(rx_base.cap(1))
            tn = tag
            if tagType == 1:
                url = '%s/tags/%s' % (reposRoot, urllib.quote(unicode(tag)))
            elif tagType == 2:
                url = '%s/branches/%s' % (reposRoot, urllib.quote(unicode(tag)))
            elif tagType == 4:
                url = '%s/trunk' % (reposRoot)
                tn = QString('HEAD')
        else:
            url = self.__svnURL(unicode(tag))
            tn = url
        
        args = QStringList()
        args.append('switch')
        if self.versionStr >= '1.5.0':
            args.append('--accept')
            args.append('postpone')
        args.append(url)
        args.append(name)
        
        dia = SvnDialog(self.trUtf8('Switching to %1')
            .arg(tn))
        res = dia.startProcess(args)
        if res:
            dia.exec_()
        
    def vcsMerge(self, name):
        """
        Public method used to merge a URL/revision into the local project.
        
        @param name file/directory name to be merged (string)
        """
        dname, fname = self.splitPath(name)
        
        opts = self.options['global'][:]
        force = '--force' in opts
        if force:
            del opts[opts.index('--force')]
        
        dlg = SvnMergeDialog(self.mergeList[0], self.mergeList[1], self.mergeList[2], 
                             force)
        if dlg.exec_() == QDialog.Accepted:
            urlrev1, urlrev2, target, force = dlg.getParameters()
        else:
            return
        
        # remember URL or revision
        self.mergeList[0].removeAll(urlrev1)
        self.mergeList[0].prepend(urlrev1)
        self.mergeList[1].removeAll(urlrev2)
        self.mergeList[1].prepend(urlrev2)
        
        rx_rev = QRegExp('\\d+|HEAD')
        
        args = QStringList()
        args.append('merge')
        self.addArguments(args, opts)
        if self.versionStr >= '1.5.0':
            args.append('--accept')
            args.append('postpone')
        if force:
            args.append('--force')
        if rx_rev.exactMatch(urlrev1):
            args.append('-r')
            args.append(QString('%1:%2').arg(urlrev1).arg(urlrev2))
            if target.isEmpty():
                args.append(name)
            else:
                args.append(target)
                
            # remember target
            self.mergeList[2].removeAll(target)
            self.mergeList[2].prepend(target)
        else:
            args.append(self.__svnURL(urlrev1))
            args.append(self.__svnURL(urlrev2))
        args.append(fname)
        
        dia = SvnDialog(self.trUtf8('Merging %1').arg(name))
        res = dia.startProcess(args, dname)
        if res:
            dia.exec_()
        
    def vcsRegisteredState(self, name):
        """
        Public method used to get the registered state of a file in the vcs.
        
        @param name filename to check (string or QString)
        @return a combination of canBeCommited and canBeAdded
        """
        dname, fname = self.splitPath(name)
        
        if fname == '.':
            if os.path.isdir(os.path.join(dname, self.adminDir)):
                return self.canBeCommitted
            else:
                return self.canBeAdded
        
        name = os.path.normcase(unicode(name))
        states = { name : 0 }
        states = self.vcsAllRegisteredStates(states, dname, False)
        if states[name] == self.canBeCommitted:
            return self.canBeCommitted
        else:
            return self.canBeAdded
        
    def vcsAllRegisteredStates(self, names, dname, shortcut = True):
        """
        Public method used to get the registered states of a number of files in the vcs.
        
        <b>Note:</b> If a shortcut is to be taken, the code will only check, if the named
        directory has been scanned already. If so, it is assumed, that the states for
        all files has been populated by the previous run.
        
        @param names dictionary with all filenames to be checked as keys
        @param dname directory to check in (string)
        @param shortcut flag indicating a shortcut should be taken (boolean)
        @return the received dictionary completed with a combination of 
            canBeCommited and canBeAdded or None in order to signal an error
        """
        dname = unicode(dname)
        if not os.path.isdir(os.path.join(dname, self.adminDir)):
            # not under version control -> do nothing
            return names
        
        found = False
        for name in self.statusCache.keys():
            if os.path.dirname(name) == dname:
                if shortcut:
                    found = True
                    break
                if names.has_key(name):
                    found = True
                    names[name] = self.statusCache[name]
        
        if not found:
            ioEncoding = str(Preferences.getSystem("IOEncoding"))
            process = QProcess()
            args = QStringList()
            args.append('status')
            args.append('--verbose')
            args.append('--non-interactive')
            args.append(dname)
            process.start('svn', args)
            procStarted = process.waitForStarted()
            if procStarted:
                finished = process.waitForFinished(30000)
                if finished and process.exitCode() == 0:
                    output = \
                        unicode(process.readAllStandardOutput(), ioEncoding, 'replace')
                    for line in output.splitlines():
                        if self.rx_status1.exactMatch(line):
                            flags = str(self.rx_status1.cap(1))
                            path = self.rx_status1.cap(5).trimmed()
                        elif self.rx_status2.exactMatch(line):
                            flags = str(self.rx_status2.cap(1))
                            path = self.rx_status2.cap(2).trimmed()
                        else:
                            continue
                        name = os.path.normcase(unicode(path))
                        if flags[0] not in "?I":
                            if names.has_key(name):
                                names[name] = self.canBeCommitted
                            self.statusCache[name] = self.canBeCommitted
                        else:
                            self.statusCache[name] = self.canBeAdded
        
        return names
        
    def clearStatusCache(self):
        """
        Public method to clear the status cache.
        """
        self.statusCache = {}
        
    def vcsName(self):
        """
        Public method returning the name of the vcs.
        
        @return always 'Subversion' (string)
        """
        return "Subversion"

    def vcsCleanup(self, name):
        """
        Public method used to cleanup the working copy.
        
        @param name directory name to be cleaned up (string)
        """
        args = QStringList()
        args.append('cleanup')
        self.addArguments(args, self.options['global'])
        args.append(name)
        
        dia = SvnDialog(self.trUtf8('Cleaning up %1')
            .arg(name))
        res = dia.startProcess(args)
        if res:
            dia.exec_()
    
    def vcsCommandLine(self, name):
        """
        Public method used to execute arbitrary subversion commands.
        
        @param name directory name of the working directory (string)
        """
        dlg = SvnCommandDialog(self.commandHistory, self.wdHistory, name)
        if dlg.exec_() == QDialog.Accepted:
            command, wd = dlg.getData()
            commandList = Utilities.parseOptionString(command)
            
            # This moves any previous occurrence of these arguments to the head
            # of the list.
            self.commandHistory.removeAll(command)
            self.commandHistory.prepend(command)
            self.wdHistory.removeAll(wd)
            self.wdHistory.prepend(wd)
            
            args = QStringList()
            self.addArguments(args, commandList)
            
            dia = SvnDialog(self.trUtf8('Subversion command'))
            res = dia.startProcess(args, wd)
            if res:
                dia.exec_()
        
    def vcsOptionsDialog(self, project, archive, editable = False, parent = None):
        """
        Public method to get a dialog to enter repository info.
        
        @param project reference to the project object
        @param archive name of the project in the repository (string)
        @param editable flag indicating that the project name is editable (boolean)
        @param parent parent widget (QWidget)
        """
        return SvnOptionsDialog(self, project, parent)
        
    def vcsNewProjectOptionsDialog(self, parent = None):
        """
        Public method to get a dialog to enter repository info for getting a new project.
        
        @param parent parent widget (QWidget)
        """
        return SvnNewProjectOptionsDialog(self, parent)
        
    def vcsRepositoryInfos(self, ppath):
        """
        Public method to retrieve information about the repository.
        
        @param ppath local path to get the repository infos (string)
        @return string with ready formated info for display (QString)
        """
        info = {\
            'committed-rev' : '',
            'committed-date' : '',
            'committed-time' : '',
            'url' : '',
            'last-author' : '',
            'revision' : ''
        }
        
        ioEncoding = str(Preferences.getSystem("IOEncoding"))
        
        process = QProcess()
        args = QStringList()
        args.append('info')
        args.append('--non-interactive')
        args.append('--xml')
        args.append(ppath)
        process.start('svn', args)
        procStarted = process.waitForStarted()
        if procStarted:
            finished = process.waitForFinished(30000)
            if finished and process.exitCode() == 0:
                output = unicode(process.readAllStandardOutput(), ioEncoding, 'replace')
                entryFound = False
                commitFound = False
                for line in output.splitlines():
                    line = line.strip()
                    if line.startswith('<entry'):
                        entryFound = True
                    elif line.startswith('<commit'):
                        commitFound = True
                    elif line.startswith('</commit>'):
                        commitFound = False
                    elif line.startswith("revision="):
                        rev = line[line.find('"')+1:line.rfind('"')]
                        if entryFound:
                            info['revision'] = rev
                            entryFound = False
                        elif commitFound:
                            info['committed-rev'] = rev
                    elif line.startswith('<url>'):
                        info['url'] = \
                            line.replace('<url>', '').replace('</url>', '')
                    elif line.startswith('<author>'):
                        info['last-author'] = \
                            line.replace('<author>', '').replace('</author>', '')
                    elif line.startswith('<date>'):
                        value = line.replace('<date>', '').replace('</date>', '')
                        date, time = value.split('T')
                        info['committed-date'] = date
                        info['committed-time'] = "%s%s" % (time.split('.')[0], time[-1])
        
        return QString(QApplication.translate('subversion',
            """<h3>Repository information</h3>"""
            """<table>"""
            """<tr><td><b>Subversion V.</b></td><td>%1</td></tr>"""
            """<tr><td><b>URL</b></td><td>%2</td></tr>"""
            """<tr><td><b>Current revision</b></td><td>%3</td></tr>"""
            """<tr><td><b>Committed revision</b></td><td>%4</td></tr>"""
            """<tr><td><b>Committed date</b></td><td>%5</td></tr>"""
            """<tr><td><b>Comitted time</b></td><td>%6</td></tr>"""
            """<tr><td><b>Last author</b></td><td>%7</td></tr>"""
            """</table>"""
            ))\
            .arg(self.versionStr)\
            .arg(info['url'])\
            .arg(info['revision'])\
            .arg(info['committed-rev'])\
            .arg(info['committed-date'])\
            .arg(info['committed-time'])\
            .arg(info['last-author'])\
    
    ############################################################################
    ## Public Subversion specific methods are below.
    ############################################################################
    
    def svnGetReposName(self, path):
        """
        Public method used to retrieve the URL of the subversion repository path.
        
        @param path local path to get the svn repository path for (string)
        @return string with the repository path URL
        """
        ioEncoding = str(Preferences.getSystem("IOEncoding"))
        
        process = QProcess()
        args = QStringList()
        args.append('info')
        args.append('--xml')
        args.append('--non-interactive')
        args.append(path)
        process.start('svn', args)
        procStarted = process.waitForStarted()
        if procStarted:
            finished = process.waitForFinished(30000)
            if finished and process.exitCode() == 0:
                output = unicode(process.readAllStandardOutput(), ioEncoding, 'replace')
                for line in output.splitlines():
                    line = line.strip()
                    if line.startswith('<url>'):
                        reposURL = line.replace('<url>', '').replace('</url>', '')
                        return reposURL
        
        return None

    def svnResolve(self, name):
        """
        Public method used to resolve conflicts of a file/directory.
        
        @param name file/directory name to be resolved (string)
        """
        args = QStringList()
        if self.versionStr >= '1.5.0':
            args.append('resolve')
            args.append('--accept')
            args.append('working')
        else:
            args.append('resolved')
        self.addArguments(args, self.options['global'])
        if type(name) is types.ListType:
            self.addArguments(args, name)
        else:
            if os.path.isdir(name):
                args.append('--recursive')
            args.append(name)
        
        dia = SvnDialog(self.trUtf8('Resolving conficts'))
        res = dia.startProcess(args)
        if res:
            dia.exec_()
        self.checkVCSStatus()
    
    def svnCopy(self, name, project):
        """
        Public method used to copy a file/directory.
        
        @param name file/directory name to be copied (string)
        @param project reference to the project object
        @return flag indicating successfull operation (boolean)
        """
        rx_prot = QRegExp('(file:|svn:|svn+ssh:|http:|https:).+')
        dlg = SvnCopyDialog(name)
        res = False
        if dlg.exec_() == QDialog.Accepted:
            target, force = dlg.getData()
            
            args = QStringList()
            args.append('copy')
            self.addArguments(args, self.options['global'])
            if rx_prot.exactMatch(target):
                args.append('--message')
                args.append(QString('Copying %1 to %2').arg(name).arg(target))
                target = self.__svnURL(target)
            else:
                target = unicode(target)
            args.append(name)
            args.append(target)
            
            dia = SvnDialog(self.trUtf8('Copying %1')
                .arg(name))
            res = dia.startProcess(args)
            if res:
                dia.exec_()
                res = dia.normalExit()
                if res and \
                   not rx_prot.exactMatch(target) and \
                   target.startswith(project.getProjectPath()):
                    if os.path.isdir(name):
                        project.copyDirectory(name, target)
                    else:
                        project.appendFile(target)
        return res
    
    def svnListProps(self, name, recursive = False):
        """
        Public method used to list the properties of a file/directory.
        
        @param name file/directory name (string or list of strings)
        @param recursive flag indicating a recursive list is requested
        """
        self.propList = SvnPropListDialog(self)
        self.propList.show()
        self.propList.start(name, recursive)
        
    def svnSetProp(self, name, recursive = False):
        """
        Public method used to add a property to a file/directory.
        
        @param name file/directory name (string or list of strings)
        @param recursive flag indicating a recursive list is requested
        """
        dlg = SvnPropSetDialog()
        if dlg.exec_() == QDialog.Accepted:
            propName, fileFlag, propValue = dlg.getData()
            if propName.isEmpty():
                KQMessageBox.critical(None,
                    self.trUtf8("Subversion Set Property"),
                    self.trUtf8("""You have to supply a property name. Aborting."""))
                return
            
            args = QStringList()
            args.append('propset')
            self.addArguments(args, self.options['global'])
            if recursive:
                args.append('--recursive')
            args.append(propName)
            if fileFlag:
                args.append('--file')
            args.append(propValue)
            if type(name) is types.ListType:
                dname, fnames = self.splitPathList(name)
                self.addArguments(args, fnames)
            else:
                dname, fname = self.splitPath(name)
                args.append(fname)
            
            dia = SvnDialog(self.trUtf8('Subversion Set Property'))
            res = dia.startProcess(args, dname)
            if res:
                dia.exec_()
        
    def svnDelProp(self, name, recursive = False):
        """
        Public method used to delete a property of a file/directory.
        
        @param name file/directory name (string or list of strings)
        @param recursive flag indicating a recursive list is requested
        """
        propName, ok = KQInputDialog.getText(\
            None,
            self.trUtf8("Subversion Delete Property"),
            self.trUtf8("Enter property name"),
            QLineEdit.Normal)
        
        if not ok:
            return
        
        if propName.isEmpty():
            KQMessageBox.critical(None,
                self.trUtf8("Subversion Delete Property"),
                self.trUtf8("""You have to supply a property name. Aborting."""))
            return
        
        args = QStringList()
        args.append('propdel')
        self.addArguments(args, self.options['global'])
        if recursive:
            args.append('--recursive')
        args.append(propName)
        if type(name) is types.ListType:
            dname, fnames = self.splitPathList(name)
            self.addArguments(args, fnames)
        else:
            dname, fname = self.splitPath(name)
            args.append(fname)
        
        dia = SvnDialog(self.trUtf8('Subversion Delete Property'))
        res = dia.startProcess(args, dname)
        if res:
            dia.exec_()
        
    def svnListTagBranch(self, path, tags = True):
        """
        Public method used to list the available tags or branches.
        
        @param path directory name of the project (string)
        @param tags flag indicating listing of branches or tags
                (False = branches, True = tags)
        """
        self.tagbranchList = SvnTagBranchListDialog(self)
        self.tagbranchList.show()
        if tags:
            if not self.showedTags:
                self.showedTags = True
                allTagsBranchesList = self.allTagsBranchesList
            else:
                self.tagsList = QStringList()
                allTagsBranchesList = None
            self.tagbranchList.start(path, tags, 
                                     self.tagsList, allTagsBranchesList)
        elif not tags:
            if not self.showedBranches:
                self.showedBranches = True
                allTagsBranchesList = self.allTagsBranchesList
            else:
                self.branchesList = QStringList()
                allTagsBranchesList = None
            self.tagbranchList.start(path, tags, 
                                     self.branchesList, self.allTagsBranchesList)
        
    def svnBlame(self, name):
        """
        Public method to show the output of the svn blame command.
        
        @param name file name to show the blame for (string)
        """
        self.blame = SvnBlameDialog(self)
        self.blame.show()
        self.blame.start(name)
        
    def svnExtendedDiff(self, name):
        """
        Public method used to view the difference of a file/directory to the 
        Subversion repository.
        
        If name is a directory and is the project directory, all project files
        are saved first. If name is a file (or list of files), which is/are being edited 
        and has unsaved modification, they can be saved or the operation may be aborted.
        
        This method gives the chance to enter the revisions to be compared.
        
        @param name file/directory name to be diffed (string)
        """
        if type(name) is types.ListType:
            names = name[:]
        else:
            names = [name]
        for nam in names:
            if os.path.isfile(nam):
                editor = e4App().getObject("ViewManager").getOpenEditor(nam)
                if editor and not editor.checkDirty() :
                    return
            else:
                project = e4App().getObject("Project")
                if nam == project.ppath and not project.saveAllScripts():
                    return
        dlg = SvnRevisionSelectionDialog()
        if dlg.exec_() == QDialog.Accepted:
            revisions = dlg.getRevisions()
            self.diff = SvnDiffDialog(self)
            self.diff.show()
            self.diff.start(name, revisions)

    def svnUrlDiff(self, name):
        """
        Public method used to view the difference of a file/directory of two
        repository URLs.
        
        If name is a directory and is the project directory, all project files
        are saved first. If name is a file (or list of files), which is/are being edited 
        and has unsaved modification, they can be saved or the operation may be aborted.
        
        This method gives the chance to enter the revisions to be compared.
        
        @param name file/directory name to be diffed (string)
        """
        if type(name) is types.ListType:
            names = name[:]
        else:
            names = [name]
        for nam in names:
            if os.path.isfile(nam):
                editor = e4App().getObject("ViewManager").getOpenEditor(nam)
                if editor and not editor.checkDirty() :
                    return
            else:
                project = e4App().getObject("Project")
                if nam == project.ppath and not project.saveAllScripts():
                    return
        
        dname = self.splitPath(names[0])[0]
        
        dlg = SvnUrlSelectionDialog(self, self.tagsList, self.branchesList, dname)
        if dlg.exec_() == QDialog.Accepted:
            urls, summary = dlg.getURLs()
            self.diff = SvnDiffDialog(self)
            self.diff.show()
            QApplication.processEvents()
            self.diff.start(name, urls = urls, summary = summary)
        
    def svnLogLimited(self, name):
        """
        Public method used to view the (limited) log of a file/directory from the 
        Subversion repository.
        
        @param name file/directory name to show the log of (string)
        """
        noEntries, ok = KQInputDialog.getInteger(\
            None,
            self.trUtf8("Subversion Log"),
            self.trUtf8("Select number of entries to show."),
            self.getPlugin().getPreferences("LogLimit"), 1, 999999, 1)
        if ok:
            self.log = SvnLogDialog(self)
            self.log.show()
            self.log.start(name, noEntries)
        
    def svnLogBrowser(self, path):
        """
        Public method used to browse the log of a file/directory from the 
        Subversion repository.
        
        @param path file/directory name to show the log of (string)
        """
        self.logBrowser = SvnLogBrowserDialog(self)
        self.logBrowser.show()
        self.logBrowser.start(path)
        
    def svnLock(self, name, stealIt=False, parent=None):
        """
        Public method used to lock a file in the Subversion repository.
        
        @param name file/directory name to be locked (string or list of strings)
        @param stealIt flag indicating a forced operation (boolean)
        @param parent reference to the parent object of the subversion dialog (QWidget)
        """
        args = QStringList()
        args.append('lock')
        self.addArguments(args, self.options['global'])
        if stealIt:
            args.append('--force')
        if type(name) is types.ListType:
            dname, fnames = self.splitPathList(name)
            self.addArguments(args, fnames)
        else:
            dname, fname = self.splitPath(name)
            args.append(fname)
        
        dia = SvnDialog(self.trUtf8('Locking in the Subversion repository'), parent)
        res = dia.startProcess(args, dname)
        if res:
            dia.exec_()
        
    def svnUnlock(self, name, breakIt=False, parent=None):
        """
        Public method used to unlock a file in the Subversion repository.
        
        @param name file/directory name to be unlocked (string or list of strings)
        @param breakIt flag indicating a forced operation (boolean)
        @param parent reference to the parent object of the subversion dialog (QWidget)
        """
        args = QStringList()
        args.append('unlock')
        self.addArguments(args, self.options['global'])
        if breakIt:
            args.append('--force')
        if type(name) is types.ListType:
            dname, fnames = self.splitPathList(name)
            self.addArguments(args, fnames)
        else:
            dname, fname = self.splitPath(name)
            args.append(fname)
        
        dia = SvnDialog(self.trUtf8('Unlocking in the Subversion repository'), parent)
        res = dia.startProcess(args, dname)
        if res:
            dia.exec_()
        
    def svnRelocate(self, projectPath):
        """
        Public method to relocate the working copy to a new repository URL.
        
        @param projectPath path name of the project (string)
        """
        currUrl = self.svnGetReposName(projectPath)
        dlg = SvnRelocateDialog(currUrl)
        if dlg.exec_() == QDialog.Accepted:
            newUrl, inside = dlg.getData()
            args = QStringList()
            args.append('switch')
            if not inside:
                args.append('--relocate')
                args.append(currUrl)
            args.append(newUrl)
            args.append(projectPath)
            
            dia = SvnDialog(self.trUtf8('Relocating'))
            res = dia.startProcess(args)
            if res:
                dia.exec_()
        
    def svnRepoBrowser(self, projectPath = None):
        """
        Public method to open the repository browser.
        
        @param projectPath path name of the project (string)
        """
        if projectPath:
            url = self.svnGetReposName(projectPath)
        else:
            url = None
        
        if url is None:
            url, ok = KQInputDialog.getText(\
                None,
                self.trUtf8("Repository Browser"),
                self.trUtf8("Enter the repository URL."),
                QLineEdit.Normal)
            if not ok or url.isEmpty():
                return
        
        self.repoBrowser = SvnRepoBrowserDialog(self)
        self.repoBrowser.show()
        self.repoBrowser.start(url)
        
    def svnRemoveFromChangelist(self, names):
        """
        Public method to remove a file or directory from it's changelist.
        
        Note: Directories will be removed recursively.
        
        @param names name or list of names of file or directory to remove
            (string or QString)
        """
        args = QStringList()
        args.append('changelist')
        self.addArguments(args, self.options['global'])
        args.append('--remove')
        args.append('--recursive')
        if type(names) is types.ListType:
            dname, fnames = self.splitPathList(names)
            self.addArguments(args, fnames)
        else:
            dname, fname = self.splitPath(names)
            args.append(fname)
        
        dia = SvnDialog(self.trUtf8('Remove from changelist'))
        res = dia.startProcess(args, dname)
        if res:
            dia.exec_()
        
    def svnAddToChangelist(self, names):
        """
        Public method to add a file or directory to a changelist.
        
        Note: Directories will be added recursively.
        
        @param names name or list of names of file or directory to add
            (string or QString)
        """
        clname, ok = KQInputDialog.getText(\
            None,
            self.trUtf8("Add to changelist"),
            self.trUtf8("Enter name of the changelist:"),
            QLineEdit.Normal)
        if not ok or clname.isEmpty():
            return

        args = QStringList()
        args.append('changelist')
        self.addArguments(args, self.options['global'])
        args.append('--recursive')
        args.append(clname)
        if type(names) is types.ListType:
            dname, fnames = self.splitPathList(names)
            self.addArguments(args, fnames)
        else:
            dname, fname = self.splitPath(names)
            args.append(fname)
        
        dia = SvnDialog(self.trUtf8('Remove from changelist'))
        res = dia.startProcess(args, dname)
        if res:
            dia.exec_()

    ############################################################################
    ## Private Subversion specific methods are below.
    ############################################################################
    
    def __svnURL(self, url):
        """
        Private method to format a url for subversion.
        
        @param url unformatted url string (string)
        @return properly formated url for subversion
        """
        url = self.svnNormalizeURL(url)
        url = tuple(url.split(':', 2))
        if len(url) == 3:
            scheme = url[0]
            host = url[1]
            port, path = url[2].split("/",1)
            return "%s:%s:%s/%s" % (scheme, host, port, urllib.quote(path))
        else:
            scheme = url[0]
            if scheme == "file":
                return "%s:%s" % (scheme, urllib.quote(url[1]))
            else:
                host, path = url[1][2:].split("/",1)
                return "%s://%s/%s" % (scheme, host, urllib.quote(path))

    def svnNormalizeURL(self, url):
        """
        Public method to normalize a url for subversion.
        
        @param url url string (string)
        @return properly normalized url for subversion
        """
        url = url.replace('\\', '/')
        if url.endswith('/'):
            url = url[:-1]
        urll = url.split('//')
        return "%s//%s" % (urll[0], '/'.join(urll[1:]))

    ############################################################################
    ## Methods to get the helper objects are below.
    ############################################################################
    
    def vcsGetProjectBrowserHelper(self, browser, project, isTranslationsBrowser = False):
        """
        Public method to instanciate a helper object for the different project browsers.
        
        @param browser reference to the project browser object
        @param project reference to the project object
        @param isTranslationsBrowser flag indicating, the helper is requested for the
            translations browser (this needs some special treatment)
        @return the project browser helper object
        """
        return SvnProjectBrowserHelper(self, browser, project, isTranslationsBrowser)
        
    def vcsGetProjectHelper(self, project):
        """
        Public method to instanciate a helper object for the project.
        
        @param project reference to the project object
        @return the project helper object
        """
        helper = self.__plugin.getProjectHelper()
        helper.setObjects(self, project)
        return helper

    ############################################################################
    ##  Status Monitor Thread methods
    ############################################################################

    def _createStatusMonitorThread(self, interval, project):
        """
        Protected method to create an instance of the VCS status monitor thread.
        
        @param project reference to the project object
        @param interval check interval for the monitor thread in seconds (integer)
        @return reference to the monitor thread (QThread)
        """
        return SvnStatusMonitorThread(interval, project.ppath, self)
