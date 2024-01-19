# -*- coding: utf-8 -*-

# Copyright (c) 2009 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the AdBlock rule class.
"""

from PyQt4.QtCore import *

class AdBlockRule(object):
    """
    Class implementing the AdBlock rule.
    """
    def __init__(self, filter = QString()):
        """
        Constructor
        """
        self.__regExp = QRegExp()
        self.__options = QStringList()
        
        self.setFilter(filter)
    
    def filter(self):
        """
        Public method to get the rule filter string.
        
        @return rule filter string (QString)
        """
        return QString(self.__filter)
    
    def setFilter(self, filter):
        """
        Public method to set the rule filter string.
        
        @param filter rule filter string (string or QString)
        """
        self.__filter = QString(filter)
        
        self.__cssRule = False
        self.__enabled = True
        self.__exception = False
        regExpRule = False
        
        if filter.startsWith("!") or filter.trimmed().isEmpty():
            self.__enabled = False
        
        if filter.contains("##"):
            self.__cssRule = True
        
        parsedLine = QString(filter)
        if parsedLine.startsWith("@@"):
            self.__exception = True
            parsedLine = parsedLine[2:]
        if parsedLine.startsWith("/"):
            if parsedLine.endsWith("/"):
                parsedLine = parsedLine[1:-1]
                regExpRule = True
        
        options = parsedLine.indexOf("$")
        if options >= 0:
            self.__options = parsedLine[options + 1].split(",")
            parsedLine = parsedLine[:options]
        
        self.setPattern(parsedLine, regExpRule)
        
        if "match-case" in self.__options:
            self.__regExp.setCaseSensitivity(Qt.CaseSensitive)
            self.__options.removeAll("match-case")
    
    def networkMatch(self, encodedUrl):
        """
        Public method to check the rule for a match.
        
        @param encodedUrl string encoded URL to be checked (string or QString)
        @return flag indicating a match (boolean)
        """
        encodedUrl = QString(encodedUrl)
        
        if self.__cssRule:
            return False
        
        if not self.__enabled:
            return False
        
        matched = self.__regExp.indexIn(encodedUrl) != -1
        
        if matched and not len(self.__options) == 0:
            # only domain rules are supported
            if len(self.__options) == 1:
                for option in self.__options:
                    if option.startsWith("domain="):
                        url = QUrl.fromEncoded(encodedUrl.toUtf8())
                        host = url.host()
                        domainOptions = option[7:].split("|")
                        for domainOption in domainOptions:
                            negate = domainOption.startsWith("~")
                            if negate:
                                domainOption = domainOption[1:]
                            hostMatched = domainOption == host
                            if hostMatched and not negate:
                                return True
                            if not hostMatched and negate:
                                return True
            
            return False
        
        return matched
    
    def isException(self):
        """
        Public method to check, if the rule defines an exception.
        
        @return flag indicating an exception (boolean)
        """
        return self.__exception
    
    def setException(self, exception):
        """
        Public method to set the rule's exception flag.
        
        @param exception flag indicating an exception rule (boolean)
        """
        self.__exception = exception
    
    def isEnabled(self):
        """
        Public method to check, if the rule is enabled.
        
        @return flag indicating enabled state (boolean)
        """
        return self.__enabled
    
    def setEnabled(self, enabled):
        """
        Public method to set the rule's enabled state.
        
        @param enabled flag indicating the new enabled state (boolean)
        """
        self.__enabled = enabled
        if not enabled:
            self.__filter = "!" + self.__filter
        else:
            self.__filter = self.__filter[1:]
    
    def isCSSRule(self):
        """
        Public method to check, if the rule is a CSS rule.
        
        @return flag indicating a CSS rule (boolean)
        """
        return self.__cssRule
    
    def regExpPattern(self):
        """
        Public method to get the regexp pattern of the rule.
        
        @return regexp pattern (QRegExp)
        """
        return self.__regExp.pattern()
    
    def __convertPatternToRegExp(self, wildcardPattern):
        """
        Private method to convert a wildcard pattern to a regular expression.
        
        @param wildcardPattern string containing the wildcard pattern (string or QString)
        @return string containing a regular expression (QString)
        """
        pattern = QString(wildcardPattern)
        
        pattern = pattern.replace(QRegExp(r"\*+"), "*")      # remove multiple wildcards
        pattern = pattern.replace(QRegExp(r"\^\|$"), "^")    # remove anchors following separator placeholder
        pattern = pattern.replace(QRegExp(r"^(\*)"), "")     # remove leading wildcards
        pattern = pattern.replace(QRegExp(r"(\*)$"), "")     # remove trailing wildcards
        pattern = pattern.replace(QRegExp(r"(\W)"), "")      # escape special symbols
        pattern = pattern.replace(QRegExp(r"^\\\|\\\|"),
            r"^[\w\-]+:\/+(?!\/)(?:[^\/]+\.)?")              # process extended anchor at expression start
        pattern = pattern.replace(QRegExp(r"\\\^"), 
            r"(?:[^\w\d\-.%]|$)")                            # process separator placeholders
        pattern = pattern.replace(QRegExp(r"^\\\|"), "^")    # process anchor at expression start
        pattern = pattern.replace(QRegExp(r"\\\|$"), "$")    # process anchor at expression end
        pattern = pattern.replace(QRegExp(r"\\\*"), ".*")    # replace wildcards by .*
        
        return pattern
    
    def setPattern(self, pattern, isRegExp):
        """
        Public method to set the rule pattern.
        
        @param pattern string containing the pattern (string or QString)
        @param isRegExp flag indicating a reg exp pattern (boolean)
        """
        pattern = QString(pattern)
        if isRegExp:
            self.__regExp = QRegExp(pattern, Qt.CaseInsensitive, QRegExp.RegExp2)
        else:
            self.__regExp = QRegExp(self.__convertPatternToRegExp(pattern), 
                                    Qt.CaseInsensitive, QRegExp.RegExp2)
