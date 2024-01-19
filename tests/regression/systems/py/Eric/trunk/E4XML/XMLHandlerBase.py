# -*- coding: utf-8 -*-

# Copyright (c) 2004 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a base class for all of eric4s XML handlers.
"""

import sys
from types import UnicodeType
try:
    import cPickle as pickle
except ImportError:
    import pickle

from xml.sax.handler import ContentHandler

class XMLHandlerBase(ContentHandler):
    """
    Class implementing the base class for al of eric4s XML handlers.
    """
    def __init__(self):
        """
        Constructor
        """
        self.startDocumentSpecific = None
        
        self.elements = {
            'none'    : (self.defaultStartElement, self.endNone),
            'int'     : (self.defaultStartElement, self.endInt),
            'long'    : (self.defaultStartElement, self.endLong),
            'float'   : (self.defaultStartElement, self.endFloat),
            'complex' : (self.defaultStartElement, self.endComplex),
            'bool'    : (self.defaultStartElement, self.endBool),
            'string'  : (self.defaultStartElement, self.endString),
            'unicode' : (self.defaultStartElement, self.endUnicode),
            'tuple'   : (self.startTuple, self.endTuple),
            'list'    : (self.startList, self.endList),
            'dict'    : (self.startDictionary, self.endDictionary),
            'pickle'  : (self.startPickle, self.endPickle),
        }
        
        self.buffer = ""
        self.stack = []
        self._marker = '__MARKER__'
        
        self.NEWPARA = unichr(0x2029)
        self.NEWLINE = unichr(0x2028)
        
    def utf8_to_code(self, text):
        """
        Public method to convert a string to unicode and encode it for XML.
        
        @param text the text to encode (string)
        """
        if type(text) is not UnicodeType:
            text = unicode(text, "utf-8")
        return text
        
    def unescape(self, text, attribute = False):
        """
        Public method used to unescape certain characters.
        
        @param text the text to unescape (string)
        @param attribute flag indicating unescaping is done for an attribute
        """
        if attribute:
            return text.replace("&quot;",'"').replace("&gt;",">")\
                       .replace("&lt;","<").replace("&amp;","&")
        else:
            return text.replace("&gt;",">").replace("&lt;","<").replace("&amp;","&")
        
    def decodedNewLines(self, text):
        """
        Public method to decode newlines and paragraph breaks.
        
        @param text text to decode (string or QString)
        """
        return text.replace(self.NEWPARA, "\n\n").replace(self.NEWLINE, "\n")
        
    def startDocument(self):
        """
        Handler called, when the document parsing is started.
        """
        self.buffer = ""
        if self.startDocumentSpecific is not None:
            self.startDocumentSpecific()
        
    def startElement(self, name, attrs):
        """
        Handler called, when a starting tag is found.
        
        @param name name of the tag (string)
        @param attrs list of tag attributes
        """
        try:
            self.elements[name][0](attrs)
        except KeyError:
            pass
        
    def endElement(self, name):
        """
        Handler called, when an ending tag is found.
        
        @param name name of the tag (string)
        """
        try:
            self.elements[name][1]()
        except KeyError:
            pass
        
    def characters(self, chars):
        """
        Handler called for ordinary text.
        
        @param chars the scanned text (string)
        """
        self.buffer += chars
        
    def defaultStartElement(self, attrs):
        """
        Handler method for common start tags.
        
        @param attrs list of tag attributes
        """
        self.buffer = ""
        
    def defaultEndElement(self):
        """
        Handler method for the common end tags.
        """
        pass
        
    def _prepareBasics(self):
        """
        Protected method to prepare the parsing of XML for basic python types.
        """
        self.stack = []

    ############################################################################
    ## The various handler methods for basic types
    ############################################################################

    def endNone(self):
        """
        Handler method for the "none" end tag.
        """
        self.stack.append(None)
        
    def endInt(self):
        """
        Handler method for the "int" end tag.
        """
        self.stack.append(int(self.buffer.strip()))
        
    def endLong(self):
        """
        Handler method for the "long" end tag.
        """
        self.stack.append(long(self.buffer.strip()))
        
    def endBool(self):
        """
        Handler method for the "bool" end tag.
        """
        if self.buffer.strip() == "True":
            self.stack.append(True)
        else:
            self.stack.append(False)
        
    def endFloat(self):
        """
        Handler method for the "float" end tag.
        """
        self.stack.append(float(self.buffer.strip()))
        
    def endComplex(self):
        """
        Handler method for the "complex" end tag.
        """
        real, imag = self.buffer.strip().split()
        self.stack.append(float(real) + float(imag)*1j)
        
    def endString(self):
        """
        Handler method for the "string" end tag.
        """
        s = str(self.utf8_to_code(self.unescape(self.buffer)))
        self.stack.append(s)
        
    def endUnicode(self):
        """
        Handler method for the "unicode" end tag.
        """
        u = unicode(self.utf8_to_code(self.unescape(self.buffer)))
        self.stack.append(u)
        
    def startList(self, attrs):
        """
        Handler method for the "list" start tag.
        
        @param attrs list of tag attributes
        """
        self.stack.append(self._marker)
        self.stack.append([])
        
    def endList(self):
        """
        Handler method for the "list" end tag.
        """
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i] is self._marker:
                break
        assert i != -1
        l = self.stack[i + 1]
        l[:] = self.stack[i + 2:len(self.stack)]
        self.stack[i:] = [l]
        
    def startTuple(self, attrs):
        """
        Handler method for the "tuple" start tag.
        
        @param attrs list of tag attributes
        """
        self.stack.append(self._marker)
        
    def endTuple(self):
        """
        Handler method for the "tuple" end tag.
        """
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i] is self._marker:
                break
        assert i != -1
        t = tuple(self.stack[i + 1:len(self.stack)])
        self.stack[i:] = [t]
        
    def startDictionary(self, attrs):
        """
        Handler method for the "dictionary" start tag.
        
        @param attrs list of tag attributes
        """
        self.stack.append(self._marker)
        self.stack.append({})
        
    def endDictionary(self):
        """
        Handler method for the "dictionary" end tag.
        """
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i] is self._marker:
                break
        assert i != -1
        d = self.stack[i + 1]
        for j in range(i + 2, len(self.stack), 2):
            d[self.stack[j]] = self.stack[j + 1]
        self.stack[i:] = [d]
        
    def startPickle(self, attrs):
        """
        Handler method for the "pickle" start tag.
        
        @param attrs list of tag attributes
        """
        self.pickleEnc = attrs.get("encoding", "base64")
        
    def endPickle(self):
        """
        Handler method for the "pickle" end tag.
        """
        pic = self.utf8_to_code(self.buffer).decode(self.pickleEnc)
        self.stack.append(pickle.loads(pic))
