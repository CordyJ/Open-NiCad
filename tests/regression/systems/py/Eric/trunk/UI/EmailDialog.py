# -*- coding: utf-8 -*-

# Copyright (c) 2003 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a dialog to send bug reports.
"""

import sys
import os
import mimetypes
import smtplib
import socket

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from KdeQt import KQFileDialog, KQMessageBox, KQInputDialog
import KdeQt

from Ui_EmailDialog import Ui_EmailDialog
from Info import Program, Version, BugAddress, FeatureAddress
import Preferences
import Utilities

from email import Encoders
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email.MIMEImage import MIMEImage
from email.MIMEAudio import MIMEAudio
from email.MIMEMultipart import MIMEMultipart

class EmailDialog(QDialog, Ui_EmailDialog):
    """
    Class implementing a dialog to send bug reports.
    """
    def __init__(self, mode = "bug", parent = None):
        """
        Constructor
        
        @param mode mode of this dialog (string, "bug" or "feature")
        @param parent parent widget of this dialog (QWidget)
        """
        QDialog.__init__(self, parent)
        self.setupUi(self)
        
        self.__mode = mode
        if self.__mode == "feature":
            self.setWindowTitle(self.trUtf8("Send feature request"))
            self.msgLabel.setText(self.trUtf8(
                "Enter your &feature request below."
                " Version information is added automatically."))
            self.__toAddress = FeatureAddress
        else:
            # default is bug
            self.msgLabel.setText(self.trUtf8(
                "Enter your &bug description below."
                " Version information is added automatically."))
            self.__toAddress = BugAddress
        
        self.sendButton = \
            self.buttonBox.addButton(self.trUtf8("Send"), QDialogButtonBox.ActionRole)
        self.sendButton.setEnabled(False)
        self.sendButton.setDefault(True)
        
        height = self.height()
        self.mainSplitter.setSizes([int(0.7 * height), int(0.3 * height)])
        
        self.attachments.headerItem().setText(self.attachments.columnCount(), "")
        self.attachments.header().setResizeMode(QHeaderView.Interactive)
        
        sig = Preferences.getUser("Signature")
        if sig:
            self.message.setPlainText(sig)
            cursor = self.message.textCursor()
            cursor.setPosition(0)
            self.message.setTextCursor(cursor)
            self.message.ensureCursorVisible()
        
        self.__deleteFiles = []
        
    def keyPressEvent(self, ev):
        """
        Re-implemented to handle the user pressing the escape key.
        
        @param ev key event (QKeyEvent)
        """
        if ev.key() == Qt.Key_Escape:
            res = KQMessageBox.question(self,
                self.trUtf8("Close dialog"),
                self.trUtf8("""Do you really want to close the dialog?"""),
                QMessageBox.StandardButtons(\
                    QMessageBox.No | \
                    QMessageBox.Yes),
                QMessageBox.No)
            if res == QMessageBox.Yes:
                self.reject()
        
    def on_buttonBox_clicked(self, button):
        """
        Private slot called by a button of the button box clicked.
        
        @param button button that was clicked (QAbstractButton)
        """
        if button == self.sendButton:
            self.on_sendButton_clicked()
        
    def on_buttonBox_rejected(self):
        """
        Private slot to handle the rejected signal of the button box.
        """
        res = KQMessageBox.question(self,
            self.trUtf8("Close dialog"),
            self.trUtf8("""Do you really want to close the dialog?"""),
            QMessageBox.StandardButtons(\
                QMessageBox.No | \
                QMessageBox.Yes),
            QMessageBox.No)
        if res == QMessageBox.Yes:
            self.reject()
        
    @pyqtSignature("")
    def on_sendButton_clicked(self):
        """
        Private slot to send the email message.
        """
        if self.attachments.topLevelItemCount():
            msg = self.__createMultipartMail()
        else:
            msg = self.__createSimpleMail()
            
        ok = self.__sendmail(msg)
        
        if ok:
            for f in self.__deleteFiles:
                try:
                    os.remove(f)
                except OSError:
                    pass
            self.accept()
        
    def __createSimpleMail(self):
        """
        Private method to create a simple mail message.
        
        @return string containing the mail message
        """
        try:
            import sipconfig
            sip_version_str = sipconfig.Configuration().sip_version_str
        except ImportError:
            sip_version_str = "sip version not available"
        
        msgtext = "%s\r\n----\r\n%s----\r\n%s----\r\n%s" % \
            (unicode(self.message.toPlainText()), 
             Utilities.generateVersionInfo("\r\n"), 
             Utilities.generatePluginsVersionInfo("\r\n"), 
             Utilities.generateDistroInfo("\r\n"))
        
        msg = MIMEText(msgtext, 
                       _charset = unicode(Preferences.getSystem("StringEncoding")))
        msg['From']    = unicode(Preferences.getUser("Email"))
        msg['To']      = self.__toAddress
        msg['Subject'] = '[eric4] %s' % unicode(self.subject.text())
            
        return msg.as_string()
        
    def __createMultipartMail(self):
        """
        Private method to create a multipart mail message.
        
        @return string containing the mail message
        """
        try:
            import sipconfig
            sip_version_str = sipconfig.Configuration().sip_version_str
        except ImportError:
            sip_version_str = "sip version not available"
        
        mpPreamble = ("This is a MIME-encoded message with attachments. "
            "If you see this message, your mail client is not "
            "capable of displaying the attachments.")
        
        msgtext = "%s\r\n----\r\n%s----\r\n%s----\r\n%s" % \
            (unicode(self.message.toPlainText()), 
             Utilities.generateVersionInfo("\r\n"), 
             Utilities.generatePluginsVersionInfo("\r\n"), 
             Utilities.generateDistroInfo("\r\n"))
        
        # first part of multipart mail explains format
        msg = MIMEMultipart()
        msg['From']    = unicode(Preferences.getUser("Email"))
        msg['To']      = self.__toAddress
        msg['Subject'] = '[eric4] %s' % unicode(self.subject.text())
        msg.preamble = mpPreamble
        msg.epilogue = ''
        
        # second part is intended to be read
        att = MIMEText(msgtext, 
                       _charset = unicode(Preferences.getSystem("StringEncoding")))
        msg.attach(att)
        
        # next parts contain the attachments
        for index in range(self.attachments.topLevelItemCount()):
            itm = self.attachments.topLevelItem(index)
            maintype, subtype = str(itm.text(1)).split('/', 1)
            fname = unicode(itm.text(0))
            name = os.path.basename(fname)
            
            if maintype == 'text':
                att = MIMEText(open(fname, 'rb').read(), _subtype = subtype)
            elif maintype == 'image':
                att = MIMEImage(open(fname, 'rb').read(), _subtype = subtype)
            elif maintype == 'audio':
                att = MIMEAudio(open(fname, 'rb').read(), _subtype = subtype)
            else:
                att = MIMEBase(maintype, subtype)
                att.set_payload(open(fname, 'rb').read())
                Encoders.encode_base64(att)
            att.add_header('Content-Disposition', 'attachment', filename = fname)
            msg.attach(att)
            
        return msg.as_string()

    def __sendmail(self, msg):
        """
        Private method to actually send the message.
        
        @param msg the message to be sent (string)
        @return flag indicating success (boolean)
        """
        try:
            server = smtplib.SMTP(str(Preferences.getUser("MailServer")), 
                                  Preferences.getUser("MailServerPort"))
            if Preferences.getUser("MailServerUseTLS"):
                server.starttls()
            if Preferences.getUser("MailServerAuthentication"):
                # mail server needs authentication
                password = unicode(Preferences.getUser("MailServerPassword"))
                if not password:
                    password, ok = KQInputDialog.getText(\
                        self, 
                        self.trUtf8("Mail Server Password"),
                        self.trUtf8("Enter your mail server password"),
                        QLineEdit.Password)
                    if not ok:
                        # abort
                        return False
                try:
                    server.login(unicode(Preferences.getUser("MailServerUser")),
                                 str(password))
                except (smtplib.SMTPException, socket.error), e:
                    res = KQMessageBox.critical(self,
                        self.trUtf8("Send bug report"),
                        self.trUtf8("""<p>Authentication failed.<br>Reason: %1</p>""")
                            .arg(unicode(e)),
                        QMessageBox.StandardButtons(\
                            QMessageBox.Abort | \
                            QMessageBox.Retry),
                        QMessageBox.Retry)
                    if res == QMessageBox.Retry:
                        return self.__sendmail(msg)
                    else:
                        return False

            QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
            QApplication.processEvents()
            result = server.sendmail(unicode(Preferences.getUser("Email")),
                self.__toAddress, msg)
            server.quit()
            QApplication.restoreOverrideCursor()
        except (smtplib.SMTPException, socket.error), e:
            QApplication.restoreOverrideCursor()
            res = KQMessageBox.critical(self,
                self.trUtf8("Send bug report"),
                self.trUtf8("""<p>Message could not be sent.<br>Reason: %1</p>""")
                    .arg(unicode(e)),
                QMessageBox.StandardButtons(\
                    QMessageBox.Abort | \
                    QMessageBox.Retry),
                QMessageBox.Retry)
            if res == QMessageBox.Retry:
                return self.__sendmail(msg)
            else:
                return False
        return True
        
    @pyqtSignature("")
    def on_addButton_clicked(self):
        """
        Private slot to handle the Add... button.
        """
        fname = KQFileDialog.getOpenFileName(\
            self,
            self.trUtf8("Attach file"),
            QString(),
            QString())
        if not fname.isEmpty():
            self.attachFile(fname, False)
        
    def attachFile(self, fname, deleteFile):
        """
        Public method to add an attachment.
        
        @param fname name of the file to be attached (string or QString)
        @param deleteFile flag indicating to delete the file after it has 
            been sent (boolean)
        """
        fname = unicode(fname)
        type = mimetypes.guess_type(fname)[0]
        if not type:
            type = "application/octet-stream"
        itm = QTreeWidgetItem(self.attachments, QStringList() << fname << type)
        self.attachments.header().resizeSections(QHeaderView.ResizeToContents)
        self.attachments.header().setStretchLastSection(True)
        
        if deleteFile:
            self.__deleteFiles.append(fname)
        
    @pyqtSignature("")
    def on_deleteButton_clicked(self):
        """
        Private slot to handle the Delete button.
        """
        itm = self.attachments.currentItem()
        if itm is not None:
            itm = self.attachments.takeTopLevelItem(\
                self.attachments.indexOfTopLevelItem(itm))
            del itm
        
    def on_subject_textChanged(self, txt):
        """
        Private slot to handle the textChanged signal of the subject edit.
        
        @param txt changed text (QString)
        """
        self.sendButton.setEnabled(\
            not self.subject.text().isEmpty() and \
            not self.message.toPlainText().isEmpty())
        
    def on_message_textChanged(self):
        """
        Private slot to handle the textChanged signal of the message edit.
        
        @param txt changed text (QString)
        """
        self.sendButton.setEnabled(\
            not self.subject.text().isEmpty() and \
            not self.message.toPlainText().isEmpty())
