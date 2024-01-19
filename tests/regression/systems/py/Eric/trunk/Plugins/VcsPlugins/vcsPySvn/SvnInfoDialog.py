# -*- coding: utf-8 -*-

# Copyright (c) 2003 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a dialog to show repository related information for a file/directory.
"""

import os

import pysvn

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from SvnUtilities import formatTime
from SvnDialogMixin import SvnDialogMixin
from VCS.Ui_RepositoryInfoDialog import Ui_VcsRepositoryInfoDialog

class SvnInfoDialog(QDialog, SvnDialogMixin, Ui_VcsRepositoryInfoDialog):
    """
    Class implementing a dialog to show repository related information 
    for a file/directory.
    """
    def __init__(self, vcs, parent = None):
        """
        Constructor
        
        @param vcs reference to the vcs object
        @param parent parent widget (QWidget)
        """
        QDialog.__init__(self, parent)
        self.setupUi(self)
        SvnDialogMixin.__init__(self)
        
        self.vcs = vcs
        
        self.client = self.vcs.getClient()
        self.client.callback_cancel = \
            self._clientCancelCallback
        self.client.callback_get_login = \
            self._clientLoginCallback
        self.client.callback_ssl_server_trust_prompt = \
            self._clientSslServerTrustPromptCallback
        
        self.show()
        QApplication.processEvents()
        
    def start(self, projectPath, fn):
        """
        Public slot to start the svn info command.
        
        @param projectPath path name of the project (string)
        @param fn file or directory name relative to the project (string)
        """
        locker = QMutexLocker(self.vcs.vcsExecutionMutex)
        cwd = os.getcwd()
        os.chdir(projectPath)
        try:
            entries = self.client.info2(fn, recurse = False)
            infoStr = QString("<table>")
            for path, info in entries:
                infoStr.append(self.trUtf8(\
                    "<tr><td><b>Path (relative to project):</b></td><td>%1</td></tr>")\
                    .arg(path))
                if info['URL']:
                    infoStr.append(self.trUtf8(\
                        "<tr><td><b>Url:</b></td><td>%1</td></tr>")\
                        .arg(info['URL']))
                if info['rev']:
                    infoStr.append(self.trUtf8(\
                        "<tr><td><b>Revision:</b></td><td>%1</td></tr>")\
                        .arg(info['rev'].number))
                if info['repos_root_URL']:
                    infoStr.append(self.trUtf8(\
                        "<tr><td><b>Repository root URL:</b></td><td>%1</td></tr>")\
                        .arg(info['repos_root_URL']))
                if info['repos_UUID']:
                    infoStr.append(self.trUtf8(\
                        "<tr><td><b>Repository UUID:</b></td><td>%1</td></tr>")\
                        .arg(info['repos_UUID']))
                if info['last_changed_author']:
                    infoStr.append(self.trUtf8(\
                        "<tr><td><b>Last changed author:</b></td><td>%1</td></tr>")\
                        .arg(info['last_changed_author']))
                if info['last_changed_date']:
                    infoStr.append(self.trUtf8(\
                        "<tr><td><b>Last Changed Date:</b></td><td>%1</td></tr>")\
                        .arg(formatTime(info['last_changed_date'])))
                if info['last_changed_rev'] and \
                   info['last_changed_rev'].kind == pysvn.opt_revision_kind.number:
                    infoStr.append(self.trUtf8(\
                        "<tr><td><b>Last changed revision:</b></td><td>%1</td></tr>")\
                        .arg(info['last_changed_rev'].number))
                if info['kind']:
                    if info['kind'] == pysvn.node_kind.file:
                        nodeKind = self.trUtf8("file")
                    elif info['kind'] == pysvn.node_kind.dir:
                        nodeKind = self.trUtf8("directory")
                    elif info['kind'] == pysvn.node_kind.none:
                        nodeKind = self.trUtf8("none")
                    else:
                        nodeKind = self.trUtf8("unknown")
                    infoStr.append(self.trUtf8(\
                        "<tr><td><b>Node kind:</b></td><td>%1</td></tr>")\
                        .arg(nodeKind))
                if info['lock']:
                    lockInfo = info['lock']
                    infoStr.append(self.trUtf8(\
                        "<tr><td><b>Lock Owner:</b></td><td>%1</td></tr>")\
                        .arg(lockInfo['owner']))
                    infoStr.append(self.trUtf8(\
                        "<tr><td><b>Lock Creation Date:</b></td><td>%1</td></tr>")\
                        .arg(formatTime(lockInfo['creation_date'])))
                    if lockInfo['expiration_date'] is not None:
                        infoStr.append(\
                            self.trUtf8(\
                            "<tr><td><b>Lock Expiration Date:</b></td><td>%1</td></tr>")\
                            .arg(formatTime(lockInfo['expiration_date'])))
                    infoStr.append(self.trUtf8(\
                        "<tr><td><b>Lock Token:</b></td><td>%1</td></tr>")\
                        .arg(lockInfo['token']))
                    infoStr.append(self.trUtf8(\
                        "<tr><td><b>Lock Comment:</b></td><td>%1</td></tr>")\
                        .arg(lockInfo['comment']))
                if info['wc_info']:
                    wcInfo = info['wc_info']
                    if wcInfo['schedule']:
                        if wcInfo['schedule'] == pysvn.wc_schedule.normal:
                            schedule = self.trUtf8("normal")
                        elif wcInfo['schedule'] == pysvn.wc_schedule.add:
                            schedule = self.trUtf8("add")
                        elif wcInfo['schedule'] == pysvn.wc_schedule.delete:
                            schedule = self.trUtf8("delete")
                        elif wcInfo['schedule'] == pysvn.wc_schedule.replace:
                            schedule = self.trUtf8("replace")
                        infoStr.append(self.trUtf8(\
                            "<tr><td><b>Schedule:</b></td><td>%1</td></tr>")\
                            .arg(schedule))
                    if wcInfo['copyfrom_url']:
                        infoStr.append(self.trUtf8(\
                            "<tr><td><b>Copied From URL:</b></td><td>%1</td></tr>")\
                            .arg(wcInfo['copyfrom_url']))
                        infoStr.append(self.trUtf8(\
                            "<tr><td><b>Copied From Rev:</b></td><td>%1</td></tr>")\
                            .arg(wcInfo['copyfrom_rev'].number))
                    if wcInfo['text_time']:
                        infoStr.append(self.trUtf8(\
                            "<tr><td><b>Text Last Updated:</b></td><td>%1</td></tr>")\
                            .arg(formatTime(wcInfo['text_time'])))
                    if wcInfo['prop_time']:
                        infoStr.append(self.trUtf8(\
                            "<tr><td><b>Properties Last Updated:</b></td><td>%1</td></tr>")\
                            .arg(formatTime(wcInfo['prop_time'])))
                    if wcInfo['checksum']:
                        infoStr.append(self.trUtf8(\
                            "<tr><td><b>Checksum:</b></td><td>%1</td></tr>")\
                            .arg(wcInfo['checksum']))
            infoStr.append("</table>")
            self.infoBrowser.setHtml(infoStr)
        except pysvn.ClientError, e:
            self.__showError(e.args[0])
        locker.unlock()
        os.chdir(cwd)
        
    def __showError(self, msg):
        """
        Private slot to show an error message.
        
        @param msg error message to show (string or QString)
        """
        infoStr = QString("<p>%1</p>").arg(msg)
        self.infoBrowser.setHtml(infoStr)
