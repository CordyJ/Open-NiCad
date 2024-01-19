# -*- coding: utf-8 -*-

# Copyright (c) 2004 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing various XML utility functions.
"""

def make_parser(validating):
    """
    Function to generate an XML parser.
    
    First it will be tried to generate a validating parser. If
    this attempt fails, a non validating parser is tried next.
    
    @param validating flag indicating a validating parser is requested
    @return XML parser object
    """
    if validating:
        # see if we have a working validating parser available
        try:
            import _xmlplus
        except ImportError:
            validating = False
        else:
            try:
                v = _xmlplus.version_info
            except AttributeError:
                validating = False
            else:
                if v < (0, 8, 3):
                    validating = False
    
    if validating:
        try:
            from xml.sax.sax2exts import XMLValParserFactory
            return XMLValParserFactory.make_parser()
        except ImportError:
            from xml.sax import make_parser as sax_make_parser
            return sax_make_parser()
    else:
        from xml.sax import make_parser as sax_make_parser
        return sax_make_parser()
