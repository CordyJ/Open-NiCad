# -*- coding: utf-8 -*-

# Copyright (c) 2004 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a base class for all of eric4s XML writers.
"""

import os
from types import *
try:
    import cPickle as pickle
except ImportError:
    import pickle

class XMLWriterBase(object):
    """
    Class implementing a base class for all of eric4s XML writers.
    """
    def __init__(self, file):
        """
        Constructor
        
        @param file open file (like) object for writing
        """
        self.pf = file
        
        self.basics = {
            NoneType    : self._write_none,
            IntType     : self._write_int,
            LongType    : self._write_long,
            FloatType   : self._write_float,
            ComplexType : self._write_complex,
            BooleanType : self._write_bool,
            StringType  : self._write_string,
            UnicodeType : self._write_unicode,
            TupleType   : self._write_tuple,
            ListType    : self._write_list,
            DictType    : self._write_dictionary,
        }
        
        self.NEWPARA = unichr(0x2029)
        self.NEWLINE = unichr(0x2028)
        
    def _write(self, s, newline = True):
        """
        Protected method used to do the real write operation.
        
        @param s string to be written to the XML file
        @param newline flag indicating a linebreak
        """
        self.pf.write("%s%s" % (s.encode('utf-8'), 
            newline and os.linesep or ""))
        
    def writeXML(self):
        """
        Public method to write the XML to the file.
        """
        # write the XML header
        self._write('<?xml version="1.0" encoding="UTF-8"?>')
    
    def escape(self, data, attribute=False):
        """
        Function to escape &, <, and > in a string of data.
        
        @param data data to be escaped (string)
        @param attribute flag indicating escaping is done for an attribute
        @return the escaped data (string)
        """
    
        # must do ampersand first
        data = data.replace("&", "&amp;")
        data = data.replace(">", "&gt;")
        data = data.replace("<", "&lt;")
        if attribute:
            data = data.replace('"', "&quot;")
        return data
    
    def encodedNewLines(self, text):
        """
        Public method to encode newlines and paragraph breaks.
        
        @param text text to encode (string or QString)
        """
        return text.replace("\n\n", self.NEWPARA).replace("\n", self.NEWLINE)
    
    def _writeBasics(self, pyobject, indent = 0):
        """
        Protected method to dump an object of a basic Python type.
        
        @param pyobject object to be dumped
        @param indent indentation level for prettier output (integer)
        """
        writeMethod = self.basics.get(type(pyobject)) or self._write_unimplemented
        writeMethod(pyobject, indent)

    ############################################################################
    ## The various writer methods for basic types
    ############################################################################

    def _write_none(self, value, indent):
        """
        Protected method to dump a NoneType object.
        
        @param value value to be dumped (None) (ignored)
        @param indent indentation level for prettier output (integer)
        """
        self._write('%s<none />' % ("  " * indent))
        
    def _write_int(self, value, indent):
        """
        Protected method to dump an IntType object.
        
        @param value value to be dumped (integer)
        @param indent indentation level for prettier output (integer)
        """
        self._write('%s<int>%s</int>' % ("  " * indent, value))
        
    def _write_long(self, value, indent):
        """
        Protected method to dump a LongType object.
        
        @param value value to be dumped (long)
        @param indent indentation level for prettier output (integer)
        """
        self._write('%s<long>%s</long>' % ("  " * indent, value))
        
    def _write_bool(self, value, indent):
        """
        Protected method to dump a BooleanType object.
        
        @param value value to be dumped (boolean)
        @param indent indentation level for prettier output (integer)
        """
        self._write('%s<bool>%s</bool>' % ("  " * indent, value))
        
    def _write_float(self, value, indent):
        """
        Protected method to dump a FloatType object.
        
        @param value value to be dumped (float)
        @param indent indentation level for prettier output (integer)
        """
        self._write('%s<float>%s</float>' % ("  " * indent, value))
        
    def _write_complex(self, value, indent):
        """
        Protected method to dump a ComplexType object.
        
        @param value value to be dumped (complex)
        @param indent indentation level for prettier output (integer)
        """
        self._write('%s<complex>%s %s</complex>' % \
            ("  " * indent, value.real, value.imag))
        
    def _write_string(self, value, indent):
        """
        Protected method to dump a StringType object.
        
        @param value value to be dumped (string)
        @param indent indentation level for prettier output (integer)
        """
        self._write('%s<string>%s</string>' % ("  " * indent, self.escape(value)))
        
    def _write_unicode(self, value, indent):
        """
        Protected method to dump an UnicodeType object.
        
        @param value value to be dumped (unicode)
        @param indent indentation level for prettier output (integer)
        """
        self._write('%s<unicode>%s</unicode>' % ("  " * indent, self.escape(value)))
        
    def _write_tuple(self, value, indent):
        """
        Protected method to dump a TupleType object.
        
        @param value value to be dumped (tuple)
        @param indent indentation level for prettier output (integer)
        """
        self._write('%s<tuple>' % ("  " * indent))
        nindent = indent + 1
        for elem in value:
            self._writeBasics(elem, nindent)
        self._write('%s</tuple>' % ("  " * indent))
        
    def _write_list(self, value, indent):
        """
        Protected method to dump a ListType object.
        
        @param value value to be dumped (list)
        @param indent indentation level for prettier output (integer)
        """
        self._write('%s<list>' % ("  " * indent))
        nindent = indent + 1
        for elem in value:
            self._writeBasics(elem, nindent)
        self._write('%s</list>' % ("  " * indent))
        
    def _write_dictionary(self, value, indent):
        """
        Protected method to dump a DictType object.
        
        @param value value to be dumped (dictionary)
        @param indent indentation level for prettier output (integer)
        """
        self._write('%s<dict>' % ("  " * indent))
        nindent1 = indent + 1
        nindent2 = indent + 2
        keys = value.keys()
        keys.sort()
        for key in keys:
            self._write('%s<key>' % ("  " * nindent1))
            self._writeBasics(key, nindent2)
            self._write('%s</key>' % ("  " * nindent1))
            self._write('%s<value>' % ("  " * nindent1))
            self._writeBasics(value[key], nindent2)
            self._write('%s</value>' % ("  " * nindent1))
        self._write('%s</dict>' % ("  " * indent))
        
    def _write_unimplemented(self, value, indent):
        """
        Protected method to dump a type, that has no special method.
        
        @param value value to be dumped (any pickleable object)
        @param indent indentation level for prettier output (integer)
        """
        self._write('%s<pickle method="pickle" encoding="base64">%s</pickle>' % \
            ("  " * indent, pickle.dumps(value).encode('base64')))
