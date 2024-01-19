# -*- coding: utf-8 -*-

# Copyright (c) 2003 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a dialog mixin class providing common callback methods for 
the pysvn client.
"""

from PyQt4.QtGui import QApplication, QDialog, QWidget, QCursor

class SvnDialogMixin(object):
    """
    Class implementing a dialog mixin providing common callback methods for 
    the pysvn client.
    """
    def __init__(self, log = ""):
        """
        Constructor
        
        @param log optional log message (string or QString)
        """
        self.shouldCancel = False
        self.logMessage = log
        
    def _cancel(self):
        """
        Protected method to request a cancellation of the current action.
        """
        self.shouldCancel = True
        
    def _reset(self):
        """
        Protected method to reset the internal state of the dialog.
        """
        self.shouldCancel = False
        
    def _clientCancelCallback(self):
        """
        Protected method called by the client to check for cancellation.
        
        @return flag indicating a cancellation
        """
        QApplication.processEvents()
        return self.shouldCancel
        
    def _clientLoginCallback(self, realm, username, may_save):
        """
        Protected method called by the client to get login information.
        
        @param realm name of the realm of the requested credentials (string)
        @param username username as supplied by subversion (string)
        @param may_save flag indicating, that subversion is willing to save
            the answers returned (boolean)
        @return tuple of four values (retcode, username, password, save).
            Retcode should be True, if username and password should be used 
            by subversion, username and password contain the relevant data 
            as strings and save is a flag indicating, that username and
            password should be saved.
        """
        from SvnLoginDialog import SvnLoginDialog
        cursor = QApplication.overrideCursor()
        if cursor is not None:
            QApplication.restoreOverrideCursor()
        parent = isinstance(self, QWidget) and self or None
        dlg = SvnLoginDialog(realm, username, may_save, parent)
        res = dlg.exec_()
        if cursor is not None:
            QApplication.setOverrideCursor(cursor)
        if res == QDialog.Accepted:
            loginData = dlg.getData()
            return (True, loginData[0], loginData[1], loginData[2])
        else:
            return (False, "", "", False)
        
    def _clientSslServerTrustPromptCallback(self, trust_dict):
        """
        Protected method called by the client to request acceptance for a
        ssl server certificate.
        
        @param trust_dict dictionary containing the trust data
        @return tuple of three values (retcode, acceptedFailures, save).
            Retcode should be true, if the certificate should be accepted,
            acceptedFailures should indicate the accepted certificate failures
            and save should be True, if subversion should save the certificate.
        """
        from KdeQt import KQMessageBox
        from PyQt4.QtGui import QMessageBox
        
        cursor = QCursor(QApplication.overrideCursor())
        if cursor is not None:
            QApplication.restoreOverrideCursor()
        parent = isinstance(self, QWidget) and self or None
        msgBox = KQMessageBox.KQMessageBox(QMessageBox.Question,
            self.trUtf8("Subversion SSL Server Certificate"),
            self.trUtf8("""<p>Accept the following SSL certificate?</p>"""
                        """<table>"""
                        """<tr><td>Realm:</td><td>%1</td></tr>"""
                        """<tr><td>Hostname:</td><td>%2</td></tr>"""
                        """<tr><td>Fingerprint:</td><td>%3</td></tr>"""
                        """<tr><td>Valid from:</td><td>%4</td></tr>"""
                        """<tr><td>Valid until:</td><td>%5</td></tr>"""
                        """<tr><td>Issuer name:</td><td>%6</td></tr>"""
                        """</table>""")\
                .arg(trust_dict["realm"])\
                .arg(trust_dict["hostname"])\
                .arg(trust_dict["finger_print"])\
                .arg(trust_dict["valid_from"])\
                .arg(trust_dict["valid_until"])\
                .arg(trust_dict["issuer_dname"]),
            QMessageBox.StandardButtons(QMessageBox.NoButton),
            parent)
        permButton = msgBox.addButton(self.trUtf8("&Permanent accept"), 
                                      QMessageBox.AcceptRole)
        tempButton = msgBox.addButton(self.trUtf8("&Temporary accept"), 
                                      QMessageBox.AcceptRole)
        rejectButton = msgBox.addButton(self.trUtf8("&Reject"), 
                                        QMessageBox.RejectRole)
        msgBox.exec_()
        if cursor is not None:
            QApplication.setOverrideCursor(cursor)
        if msgBox.clickedButton() == permButton:
            return (True, trust_dict["failures"], True)
        elif msgBox.clickedButton() == tempButton:
            return (True, trust_dict["failures"], False)
        else:
            return (False, 0, False)
        
    def _clientLogCallback(self):
        """
        Protected method called by the client to request a log message.
        
        @return a flag indicating success and the log message (string)
        """
        from SvnCommitDialog import SvnCommitDialog
        if self.logMessage:
            return True, self.logMessage
        else:
            # call CommitDialog and get message from there
            dlg = SvnCommitDialog(self)
            if dlg.exec_() == QDialog.Accepted:
                msg = unicode(dlg.logMessage())
                if msg:
                    return True, msg
                else:
                    return True, "***"  # always supply a valid log message
            else:
                return False, ""
