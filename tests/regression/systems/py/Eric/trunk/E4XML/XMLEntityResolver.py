# -*- coding: utf-8 -*-

# Copyright (c) 2004 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a specialized entity resolver to find our DTDs.
"""

import os.path
from xml.sax.handler import EntityResolver

import Utilities

from eric4config import getConfig

class XMLEntityResolver(EntityResolver):
    """
    Class implementing a specialized entity resolver to find our DTDs.
    """
    def resolveEntity(self, publicId, systemId):
        """
        Public method to resolve the system identifier of an entity and
        return either the system identifier to read from as a string.
        
        @param publicId publicId of an entity (string)
        @param systemId systemId of an entity to reslove (string)
        @return resolved systemId (string)
        """
        if systemId.startswith('http://'):
            sId = systemId
            
        elif os.path.exists(systemId):
            sId = systemId
            
        else:
            dtdDir = getConfig('ericDTDDir')
            if not os.path.isabs(dtdDir):
                dtdDir = os.path.abspath(dtdDir)
            sId = os.path.join(dtdDir, systemId)
            if not os.path.exists(sId):
                ind = sId.rfind('-')
                if ind != -1:
                    sId = "%s.dtd" % sId[:ind]
                if not os.path.exists(sId):
                    sId = ""
        
        return sId
