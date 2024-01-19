# -*- coding: utf-8 -*-

# Copyright (c) 2004 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing templates for the documentation generator (lists style).
"""

#################################################
##  Common templates for index and docu files  ##
#################################################

headerTemplate = \
'''<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html PUBLIC '-//W3C//DTD XHTML 1.0 Strict//EN'
'http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd'>
<html><head>
<title>%%(Title)s</title>
</head>
<body style="background-color:%(BodyBgColor)s;color:%(BodyColor)s">'''

footerTemplate = '''
</body></html>'''

#########################################
##  Templates for documentation files  ##
#########################################

moduleTemplate = \
'''<a NAME="top" ID="top"></a>
<h1 style="background-color:%(Level1HeaderBgColor)s;color:%(Level1HeaderColor)s">%%(Module)s</h1>
%%(ModuleDescription)s
<h3 style="background-color:%(Level2HeaderBgColor)s;color:%(Level2HeaderColor)s">Global Attributes</h3>
%%(GlobalsList)s
<h3 style="background-color:%(Level2HeaderBgColor)s;color:%(Level2HeaderColor)s">Classes</h3>
%%(ClassList)s
<h3 style="background-color:%(Level2HeaderBgColor)s;color:%(Level2HeaderColor)s">Functions</h3>
%%(FunctionList)s
<hr />'''

rbFileTemplate = \
'''<a NAME="top" ID="top"></a>
<h1 style="background-color:%(Level1HeaderBgColor)s;color:%(Level1HeaderColor)s">%%(Module)s</h1>
%%(ModuleDescription)s
<h3 style="background-color:%(Level2HeaderBgColor)s;color:%(Level2HeaderColor)s">Global Attributes</h3>
%%(GlobalsList)s
<h3 style="background-color:%(Level2HeaderBgColor)s;color:%(Level2HeaderColor)s">Classes</h3>
%%(ClassList)s
<h3 style="background-color:%(Level2HeaderBgColor)s;color:%(Level2HeaderColor)s">Modules</h3>
%%(RbModulesList)s
<h3 style="background-color:%(Level2HeaderBgColor)s;color:%(Level2HeaderColor)s">Functions</h3>
%%(FunctionList)s
<hr />'''

classTemplate = \
'''<hr />
<a NAME="%%(Anchor)s" ID="%%(Anchor)s"></a>
<h2 style="background-color:%(CFBgColor)s;color:%(CFColor)s">%%(Class)s</h2>
%%(ClassDescription)s
<h3 style="background-color:%(Level2HeaderBgColor)s;color:%(Level2HeaderColor)s">Derived from</h3>
%%(ClassSuper)s
<h3 style="background-color:%(Level2HeaderBgColor)s;color:%(Level2HeaderColor)s">Class Attributes</h3>
%%(GlobalsList)s
<h3 style="background-color:%(Level2HeaderBgColor)s;color:%(Level2HeaderColor)s">Methods</h3>
%%(MethodList)s
%%(MethodDetails)s
<div align="right"><a style="color:%(LinkColor)s" href="#top">Up</a></div>
<hr />'''

methodTemplate = \
'''<a NAME="%%(Anchor)s.%%(Method)s" ID="%%(Anchor)s.%%(Method)s"></a>
<h3 style="background-color:%(Level2HeaderBgColor)s;color:%(Level2HeaderColor)s">%%(Class)s.%%(Method)s</h3>
<b>%%(Method)s</b>(<i>%%(Params)s</i>)
%%(MethodDescription)s'''

constructorTemplate = \
'''<a NAME="%%(Anchor)s.%%(Method)s" ID="%%(Anchor)s.%%(Method)s"></a>
<h3 style="background-color:%(Level2HeaderBgColor)s;color:%(Level2HeaderColor)s">%%(Class)s (Constructor)</h3>
<b>%%(Class)s</b>(<i>%%(Params)s</i>)
%%(MethodDescription)s'''

rbModuleTemplate = \
'''<hr />
<a NAME="%%(Anchor)s" ID="%%(Anchor)s"></a>
<h2 style="background-color:%(CFBgColor)s;color:%(CFColor)s">%%(Module)s</h2>
%%(ModuleDescription)s
<h3 style="background-color:%(Level2HeaderBgColor)s;color:%(Level2HeaderColor)s">Module Attributes</h3>
%%(GlobalsList)s
<h3 style="background-color:%(Level2HeaderBgColor)s;color:%(Level2HeaderColor)s">Classes</h3>
%%(ClassesList)s
<h3 style="background-color:%(Level2HeaderBgColor)s;color:%(Level2HeaderColor)s">Functions</h3>
%%(FunctionsList)s
<hr />
%%(ClassesDetails)s
%%(FunctionsDetails)s
<div align="right"><a style="color:%(LinkColor)s" href="#top">Up</a></div>
<hr />'''

rbModulesClassTemplate = \
'''<a NAME="%%(Anchor)s" ID="%%(Anchor)s"></a>
<h2 style="background-color:%(CFBgColor)s;color:%(CFColor)s">%%(Class)s</h2>
%%(ClassDescription)s
<h3 style="background-color:%(Level2HeaderBgColor)s;color:%(Level2HeaderColor)s">Derived from</h3>
%%(ClassSuper)s
<h3 style="background-color:%(Level2HeaderBgColor)s;color:%(Level2HeaderColor)s">Methods</h3>
%%(MethodList)s
%%(MethodDetails)s
<div align="right"><a style="color:%(LinkColor)s" href="#top">Up</a></div>
<hr />'''

functionTemplate = \
'''<hr />
<a NAME="%%(Anchor)s" ID="%%(Anchor)s"></a>
<h2 style="background-color:%(CFBgColor)s;color:%(CFColor)s">%%(Function)s</h2>
<b>%%(Function)s</b>(<i>%%(Params)s</i>)
%%(FunctionDescription)s
<div align="right"><a style="color:%(LinkColor)s" href="#top">Up</a></div>
<hr />'''

listTemplate = \
'''<table>
%%(Entries)s
</table>'''

listEntryTemplate = \
'''<tr>
<td><a style="color:%(LinkColor)s" href="#%%(Link)s">%%(Name)s</a></td>
<td>%%(Deprecated)s%%(Description)s</td>
</tr>'''

listEntryNoneTemplate = \
'''<tr><td>None</td></tr>'''

listEntryDeprecatedTemplate = \
'''<b>Deprecated.</b>'''

listEntrySimpleTemplate = \
'''<tr><td>%%(Name)s</td></tr>'''

paragraphTemplate = \
'''<p>
%%(Lines)s
</p>'''

parametersListTemplate = \
'''<dl>
%%(Parameters)s
</dl>'''

parametersListEntryTemplate = \
'''<dt><i>%%(Name)s</i></dt>
<dd>
%%(Description)s
</dd>'''

returnsTemplate = \
'''<dl>
<dt>Returns:</dt>
<dd>
%%s
</dd>
</dl>'''

exceptionsListTemplate = \
'''<dl>
%%(Exceptions)s
</dl>'''

exceptionsListEntryTemplate = \
'''<dt>Raises <b>%%(Name)s</b>:</dt>
<dd>
%%(Description)s
</dd>'''

signalsListTemplate = \
'''<h4>Signals</h4>
<dl>
%%(Signals)s
</dl>'''

signalsListEntryTemplate = \
'''<dt>%%(Name)s</dt>
<dd>
%%(Description)s
</dd>'''

eventsListTemplate = \
'''<h4>Events</h4>
<dl>
%%(Events)s
</dl>'''

eventsListEntryTemplate = \
'''<dt>%%(Name)s</dt>
<dd>
%%(Description)s
</dd>'''

deprecatedTemplate = \
'''<p>
<b>Deprecated.</b>
%%(Lines)s
</p>'''

authorInfoTemplate = \
'''<p>
<i>Author(s)</i>:
%%(Authors)s
</p>'''

seeListTemplate = \
'''<dl>
<dt><b>See Also:</b></dt>
%%(Links)s
</dl>'''

seeListEntryTemplate = \
'''<dd>
%%(Link)s
</dd>'''

seeLinkTemplate = \
'''<a style="color:%(LinkColor)s" %%(Link)s'''

sinceInfoTemplate = \
'''<p>
<b>since</b> %%(Info)s
</p>'''

#################################
##  Templates for index files  ##
#################################

indexBodyTemplate = '''
<h1 style="background-color:%(Level1HeaderBgColor)s;color:%(Level1HeaderColor)s">%%(Title)s</h1>
%%(Description)s
%%(Subpackages)s
%%(Modules)s'''

indexListPackagesTemplate = '''
<h3 style="background-color:%(Level2HeaderBgColor)s;color:%(Level2HeaderColor)s">Packages</h3>
<table>
%%(Entries)s
</table>'''

indexListModulesTemplate = '''
<h3 style="background-color:%(Level2HeaderBgColor)s;color:%(Level2HeaderColor)s">Modules</h3>
<table>
%%(Entries)s
</table>'''

indexListEntryTemplate = \
'''<tr>
<td><a style="color:%(LinkColor)s" href="%%(Link)s">%%(Name)s</a></td>
<td>%%(Description)s</td>
</tr>'''
