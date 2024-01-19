# -*- coding: utf-8 -*-

# Copyright (c) 2009 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the password manager.
"""

import os

from PyQt4.QtCore import *
from PyQt4.QtGui import QMessageBox
from PyQt4.QtNetwork import QNetworkRequest
from PyQt4.QtWebKit import *

from Helpviewer.JavaScriptResources import parseForms_js

from Utilities.AutoSaver import AutoSaver
import Utilities
import Preferences

class LoginForm(object):
    """
    Class implementing a data structure for login forms.
    """
    def __init__(self):
        """
        Constructor
        """
        self.url = QUrl()
        self.name = ""
        self.hasAPassword = False
        self.elements = []      # list of tuples of element name and value 
                                # (QString, QString)
        self.elementTypes = {}  # dict of element name as key and type as value
    
    def isValid(self):
        """
        Public method to test for validity.
        
        @return flag indicating a valid form (boolean)
        """
        return len(self.elements) > 0
    
    def load(self, data):
        """
        Public method to load the form data from a file.
        
        @param data list of strings to load data from (list of strings)
        @return flag indicating success (boolean)
        """
        self.url = QUrl(data[0])
        self.name = data[1]
        self.hasAPassword = data[2] == "True"
        for element in data[3:]:
            name, value = element.split(" = ", 1)
            self.elements.append((name, value))
    
    def save(self, f):
        """
        Public method to save the form data to a file.
        
        @param f file or file like object open for writing
        @return flag indicating success (booelan)
        """
        f.write("%s\n" % self.url.toString())
        f.write("%s\n" % self.name)
        f.write("%s\n" % self.hasAPassword)
        for element in self.elements:
            f.write("%s = %s\n" % (element[0], element[1]))

class PasswordManager(QObject):
    """
    Class implementing the password manager.
    
    @signal changed() emitted to indicate a change
    """
    SEPARATOR = "===================="
    FORMS = "=====FORMS====="
    NEVER = "=====NEVER====="
    
    def __init__(self, parent = None):
        """
        Constructor
        
        @param parent reference to the parent object (QObject)
        """
        QObject.__init__(self, parent)
        
        self.__logins = {}
        self.__loginForms = {}
        self.__never = []
        self.__loaded = False
        self.__saveTimer = AutoSaver(self, self.save)
        
        self.connect(self, SIGNAL("changed()"), self.__saveTimer.changeOccurred)
    
    def clear(self):
        """
        Public slot to clear the saved passwords.
        """
        if not self.__loaded:
            self.__load()
        
        self.__logins = {}
        self.__loginForms = {}
        self.__never = []
        self.__saveTimer.changeOccurred()
        self.__saveTimer.saveIfNeccessary()
        
        self.emit(SIGNAL("changed()"))
    
    def getLogin(self, url, realm):
        """
        Public method to get the login credentials.
        
        @param url URL to get the credentials for (QUrl)
        @param realm realm to get the credentials for (string or QString)
        @return tuple containing the user name (string) and password (string)
        """
        if not self.__loaded:
            self.__load()
        
        key = self.__createKey(url, realm)
        try:
            return self.__logins[key][0], Utilities.pwDecode(self.__logins[key][1])
        except KeyError:
            return "", ""
    
    def setLogin(self, url, realm, username, password):
        """
        Public method to set the login credentials.
        
        @param url URL to set the credentials for (QUrl)
        @param realm realm to set the credentials for (string or QString)
        @param username username for the login (string or QString)
        @param password password for the login (string or QString)
        """
        if not self.__loaded:
            self.__load()
        
        key = self.__createKey(url, realm)
        self.__logins[key] = (unicode(username), Utilities.pwEncode(password))
        self.emit(SIGNAL("changed()"))
    
    def __createKey(self, url, realm):
        """
        Private method to create the key string for the login credentials.
        
        @param url URL to get the credentials for (QUrl)
        @param realm realm to get the credentials for (string or QString)
        @return key string (string)
        """
        realm = unicode(realm)
        if realm:
            key = "%s://%s (%s)" % (url.scheme(), url.authority(), realm)
        else:
            key = "%s://%s" % (url.scheme(), url.authority())
        return key
    
    def save(self):
        """
        Public slot to save the login entries to disk.
        """
        if not self.__loaded:
            return
        
        loginFile = os.path.join(Utilities.getConfigDir(), "browser", "logins")
        try:
            f = open(loginFile, "w")
            for key, login in self.__logins.items():
                f.write("%s\n" % key)
                f.write("%s\n" % login[0])
                f.write("%s\n" % login[1])
                f.write("%s\n" % self.SEPARATOR)
            if self.__loginForms:
                f.write("%s\n" % self.FORMS)
                for key, form in self.__loginForms.items():
                    f.write("%s\n" % key)
                    form.save(f)
                    f.write("%s\n" % self.SEPARATOR)
            if self.__never:
                f.write("%s\n" % self.NEVER)
                for key in self.__never:
                    f.write("%s\n") % key
            f.close()
        except IOError, err:
            KQMessageBox.critical(None,
                self.trUtf8("Saving login data"),
                self.trUtf8("""<p>Login data could not be saved to <b>%1</b></p>"""
                            """<p>Reason: %2</p>""").arg(loginFile).arg(unicode(err)))
            return
    
    def __load(self):
        """
        Private method to load the saved login credentials.
        """
        loginFile = os.path.join(Utilities.getConfigDir(), "browser", "logins")
        if os.path.exists(loginFile):
            try:
                f = open(loginFile, "r")
                lines = f.read()
                f.close()
            except IOError, err:
                KQMessageBox.critical(None,
                    self.trUtf8("Loading login data"),
                    self.trUtf8("""<p>Login data could not be loaded from <b>%1</b></p>"""
                                """<p>Reason: %2</p>""").arg(loginFile).arg(unicode(err)))
                return
            
            data = []
            section = 0     # 0 = login data, 1 = forms data, 2 = never store info
            for line in lines.splitlines():
                if line == self.FORMS:
                    section = 1
                    continue
                elif line == self.NEVER:
                    section = 2
                    continue
                
                if section == 0:
                    if line != self.SEPARATOR:
                        data.append(line)
                    else:
                        if len(data) != 3:
                            KQMessageBox.critical(None,
                                self.trUtf8("Loading login data"),
                                self.trUtf8("""<p>Login data could not be loaded """
                                            """from <b>%1</b></p>"""
                                            """<p>Reason: Wrong input format</p>""")\
                                    .arg(loginFile))
                            return
                        self.__logins[data[0]] = (data[1], data[2])
                        data = []
                
                elif section == 1:
                    if line != self.SEPARATOR:
                        data.append(line)
                    else:
                        key = data[0]
                        form = LoginForm()
                        form.load(data[1:])
                        self.__loginForms[key] = form
                        data = []
                
                elif section == 2:
                    self.__never.append(line)
        
        self.__loaded = True
    
    def close(self):
        """
        Public method to close the open search engines manager.
        """
        self.__saveTimer.saveIfNeccessary()
    
    def removePassword(self, site):
        """
        Public method to remove a password entry.
        
        @param site web site name (string or QString)
        """
        site = unicode(site)
        if site in self.__logins:
            del self.__logins[site]
            if site in self.__loginForms:
                del self.__loginForms[site]
            self.emit(SIGNAL("changed()"))
    
    def allSiteNames(self):
        """
        Public method to get a list of all site names.
        
        @return sorted list of all site names (QStringList)
        """
        if not self.__loaded:
            self.__load()
        
        return QStringList(sorted(self.__logins.keys()))
    
    def sitesCount(self):
        """
        Public method to get the number of available sites.
        
        @return number of sites (integer)
        """
        if not self.__loaded:
            self.__load()
        
        return len(self.__logins)
    
    def siteInfo(self, site):
        """
        Public method to get a reference to the named site.
        
        @param site web site name (string or QString)
        @return tuple containing the user name (string) and password (string)
        """
        if not self.__loaded:
            self.__load()
        
        site = unicode(site)
        if site not in self.__logins:
            return None
        
        return self.__logins[site][0], Utilities.pwDecode(self.__logins[site][1])
    
    def post(self, request, data):
        """
        Public method to check, if the data to be sent contains login data.
        
        @param request reference to the network request (QNetworkRequest)
        @param data data to be sent (QByteArray)
        """
        # shall passwords be saved?
        if not Preferences.getHelp("SavePasswords"):
            return
        
        # observe privacy
        if QWebSettings.globalSettings().testAttribute(
                QWebSettings.PrivateBrowsingEnabled):
            return
        
        if not self.__loaded:
            self.__load()
        
        # determine the url
        refererHeader = request.rawHeader("Referer")
        if refererHeader.isEmpty():
            return
        url = QUrl.fromEncoded(refererHeader)
        url = self.__stripUrl(url)
        
        # check that url isn't in __never
        if unicode(url.toString()) in self.__never:
            return
        
        # check the request type
        v = request.attribute(QNetworkRequest.User + 101)
        if not v.isValid():
            return
        navType = v.toInt()[0]
        if navType != QWebPage.NavigationTypeFormSubmitted:
            return
        
        # determine the QWebPage
        v = request.attribute(QNetworkRequest.User + 100)
        webPage = v.toPyObject()
        if webPage == NotImplemented or webPage is None:
            return
        
        # determine the requests content type
        contentTypeHeader = request.rawHeader("Content-Type")
        if contentTypeHeader.isEmpty():
            return
        multipart = contentTypeHeader.startsWith("multipart/form-data")
        if multipart:
            boundary = contentTypeHeader.split(" ")[1].split("=")[1]
        else:
            boundary = None
        
        # find the matching form on the web page
        form = self.__findForm(webPage, data, boundary = boundary)
        if not form.isValid():
            return
        form.url = QUrl(url)
        
        # check, if the form has a password
        if not form.hasAPassword:
            return
        
        # prompt, if the form has never be seen
        key = self.__createKey(url, "")
        if key not in self.__loginForms:
            mb = QMessageBox()
            mb.setText(self.trUtf8(
                """<b>Would you like to save this password?</b><br/>"""
                """To review passwords you have saved and remove them, """
                """use the password management dialog of the Settings menu."""
            ))
            neverButton = mb.addButton(
                self.trUtf8("Never for this site"), QMessageBox.DestructiveRole)
            noButton = mb.addButton(self.trUtf8("Not now"), QMessageBox.RejectRole)
            yesButton = mb.addButton(QMessageBox.Yes)
            mb.exec_()
            if mb.clickedButton() == neverButton:
                self.__never.append(unicode(url.toString()))
                return
            elif mb.clickedButton() == noButton:
                return
        
        # extract user name and password
        user = ""
        password = ""
        for index in range(len(form.elements)):
            element = form.elements[index]
            name = element[0].toLower()
            type_ = form.elementTypes[unicode(element[0])]
            if user == "" and \
               type_ == "text":
                user = element[1]
            elif password == "" and \
                 type_ == "password":
                password = element[1]
                form.elements[index] = (element[0], QString("--PASSWORD--"))
        if user and password:
            self.__logins[key] = (unicode(user), Utilities.pwEncode(password))
            self.__loginForms[key] = form
            self.emit(SIGNAL("changed()"))
    
    def __stripUrl(self, url):
        """
        Private method to strip off all unneeded parts of a URL.
        
        @param url URL to be stripped (QUrl)
        @return stripped URL (QUrl)
        """
        cleanUrl = QUrl(url)
        cleanUrl.setQueryItems([])
        cleanUrl.setFragment("")
        cleanUrl.setUserInfo("")
        return cleanUrl
    
    def __findForm(self, webPage, data, boundary = None):
        """
        Private method to find the form used for logging in.
        
        @param webPage reference to the web page (QWebPage)
        @param data data to be sent (QByteArray)
        @keyparam boundary boundary string (QByteArray) for multipart encoded data,
            None for urlencoded data
        @return parsed form (LoginForm)
        """
        form = LoginForm()
        if boundary is not None:
            args = self.__extractMultipartQueryItems(data, boundary)
        else:
            argsUrl = QUrl.fromEncoded(QByteArray("foo://bar.com/?" + data))
            encodedArgs = argsUrl.queryItems()
            args = set()
            for arg in encodedArgs:
                key = arg[0]
                value = arg[1].replace("+", " ")
                args.add((key, value))
        
        # extract the forms
        lst = webPage.mainFrame().evaluateJavaScript(parseForms_js).toList()
        for formVariant in lst:
            map = formVariant.toMap()
            formHasPasswords = False
            formName = map[QString("name")].toString()
            formIndex = map[QString("index")].toInt()[0]
            elements = map[QString("elements")].toList()
            formElements = set()
            formElementTypes = {}
            deadElements = set()
            for element in elements:
                elementMap = element.toMap()
                name = elementMap[QString("name")].toString()
                value = elementMap[QString("value")].toString()
                type_ = elementMap[QString("type")].toString()
                if type_ == "password":
                    formHasPasswords = True
                t = (name, value)
                try:
                    if elementMap[QString("autocomplete")].toString() == "off":
                        deadElements.add(t)
                except KeyError:
                    pass
                if not name.isEmpty():
                    formElements.add(t)
                    formElementTypes[unicode(name)] = type_
            if formElements.intersection(args) == args:
                form.hasAPassword = formHasPasswords
                if formName.isEmpty():
                    form.name = formIndex
                else:
                    form.name = formName
                args.difference_update(deadElements)
                for elt in deadElements:
                    if unicode(elt[0]) in formElementTypes:
                        del formElementTypes[unicode(elt[0])]
                form.elements = list(args)
                form.elementTypes = formElementTypes
                break
        
        return form
    
    def __extractMultipartQueryItems(self, data, boundary):
        """
        Private method to extract the query items for a post operation.
        
        @param data data to be sent (QByteArray)
        @param boundary boundary string (QByteArray)
        @return set of name, value pairs (set of tuple of QString, QString)
        """
        args = set()
        
        dataStr = QString(data)
        boundaryStr = QString(boundary)
        
        parts = dataStr.split(boundaryStr + "\r\n")
        for part in parts:
            if part.startsWith("Content-Disposition"):
                lines = part.split("\r\n")
                name = lines[0].split("=")[1][1:-1]
                value = lines[2]
                args.add((name, value))
        
        return args
    
    def fill(self, page):
        """
        Public slot to fill login forms with saved data.
        
        @param page reference to the web page (QWebPage)
        """
        if page is None or page.mainFrame() is None:
            return
        
        if not self.__loaded:
            self.__load()
        
        url = page.mainFrame().url()
        url = self.__stripUrl(url)
        key = self.__createKey(url, "")
        if key not in self.__loginForms or \
           key not in self.__logins:
            return
        
        form = self.__loginForms[key]
        if form.url != url:
            return
        
        if form.name == "":
            formName = QString("0")
        else:
            try:
                formName = QString("%d" % int(form.name))
            except ValueError:
                formName = QString('"%1"').arg(form.name)
        for element in form.elements:
            name = element[0]
            value = element[1]
            
            disabled = page.mainFrame().evaluateJavaScript(
                'document.forms[%s].elements["%s"].disabled' % (formName, name)).toBool()
            if disabled:
                continue
            
            readOnly = page.mainFrame().evaluateJavaScript(
                'document.forms[%s].elements["%s"].readOnly' % (formName, name)).toBool()
            if readOnly:
                continue
            
            type_ = page.mainFrame().evaluateJavaScript(
                'document.forms[%s].elements["%s"].type' % (formName, name)).toString()
            if type_ == "" or \
               type_ in ["hidden", "reset", "submit"]:
                continue
            if type_ == "password":
                value = Utilities.pwDecode(self.__logins[key][1])
            setType = type_ == "checkbox" and "checked" or "value"
            value = value.replace("\\", "\\\\")
            value = value.replace('"', '\\"')
            javascript = 'document.forms[%s].elements["%s"].%s="%s";' % \
                         (formName, name, setType, value)
            page.mainFrame().evaluateJavaScript(javascript)
