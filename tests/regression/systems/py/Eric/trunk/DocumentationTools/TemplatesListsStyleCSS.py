# -*- coding: utf-8 -*-

# Copyright (c) 2005 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
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
<title>%(Title)s</title>
<style>
%(Style)s
</style>
</head>
<body>'''

footerTemplate = '''
</body></html>'''

#########################################
##  Templates for documentation files  ##
#########################################

moduleTemplate = \
'''<a NAME="top" ID="top"></a>
<h1>%(Module)s</h1>
%(ModuleDescription)s
<h3>Global Attributes</h3>
%(GlobalsList)s
<h3>Classes</h3>
%(ClassList)s
<h3>Functions</h3>
%(FunctionList)s
<hr />'''

rbFileTemplate = \
'''<a NAME="top" ID="top"></a>
<h1>%(Module)s</h1>
%(ModuleDescription)s
<h3>Global Attributes</h3>
%(GlobalsList)s
<h3>Classes</h3>
%(ClassList)s
<h3>Modules</h3>
%(RbModulesList)s
<h3>Functions</h3>
%(FunctionList)s
<hr />'''

classTemplate = \
'''<hr />
<a NAME="%(Anchor)s" ID="%(Anchor)s"></a>
<h2>%(Class)s</h2>
%(ClassDescription)s
<h3>Derived from</h3>
%(ClassSuper)s
<h3>Class Attributes</h3>
%(GlobalsList)s
<h3>Methods</h3>
%(MethodList)s
%(MethodDetails)s
<div align="right"><a href="#top">Up</a></div>
<hr />'''

methodTemplate = \
'''<a NAME="%(Anchor)s.%(Method)s" ID="%(Anchor)s.%(Method)s"></a>
<h4>%(Class)s.%(Method)s</h4>
<b>%(Method)s</b>(<i>%(Params)s</i>)
%(MethodDescription)s'''

constructorTemplate = \
'''<a NAME="%(Anchor)s.%(Method)s" ID="%(Anchor)s.%(Method)s"></a>
<h4>%(Class)s (Constructor)</h4>
<b>%(Class)s</b>(<i>%(Params)s</i>)
%(MethodDescription)s'''

rbModuleTemplate = \
'''<hr />
<a NAME="%(Anchor)s" ID="%(Anchor)s"></a>
<h2>%(Module)s</h2>
%(ModuleDescription)s
<h3>Module Attributes</h3>
%(GlobalsList)s
<h3>Classes</h3>
%(ClassesList)s
<h3>Functions</h3>
%(FunctionsList)s
<hr />
%(ClassesDetails)s
%(FunctionsDetails)s
<div align="right"><a href="#top">Up</a></div>
<hr />'''

rbModulesClassTemplate = \
'''<a NAME="%(Anchor)s" ID="%(Anchor)s"></a>
<h2>%(Class)s</h2>
%(ClassDescription)s
<h3>Derived from</h3>
%(ClassSuper)s
<h3>Methods</h3>
%(MethodList)s
%(MethodDetails)s
<div align="right"><a href="#top">Up</a></div>
<hr />'''

functionTemplate = \
'''<hr />
<a NAME="%(Anchor)s" ID="%(Anchor)s"></a>
<h2>%(Function)s</h2>
<b>%(Function)s</b>(<i>%(Params)s</i>)
%(FunctionDescription)s
<div align="right"><a href="#top">Up</a></div>
<hr />'''

listTemplate = \
'''<table>
%(Entries)s
</table>'''

listEntryTemplate = \
'''<tr>
<td><a href="#%(Link)s">%(Name)s</a></td>
<td>%(Deprecated)s%(Description)s</td>
</tr>'''

listEntryNoneTemplate = \
'''<tr><td>None</td></tr>'''

listEntryDeprecatedTemplate = \
'''<b>Deprecated.</b>'''

listEntrySimpleTemplate = \
'''<tr><td>%(Name)s</td></tr>'''

paragraphTemplate = \
'''<p>
%(Lines)s
</p>'''

parametersListTemplate = \
'''<dl>
%(Parameters)s
</dl>'''

parametersListEntryTemplate = \
'''<dt><i>%(Name)s</i></dt>
<dd>
%(Description)s
</dd>'''

returnsTemplate = \
'''<dl>
<dt>Returns:</dt>
<dd>
%s
</dd>
</dl>'''

exceptionsListTemplate = \
'''<dl>
%(Exceptions)s
</dl>'''

exceptionsListEntryTemplate = \
'''<dt>Raises <b>%(Name)s</b>:</dt>
<dd>
%(Description)s
</dd>'''

signalsListTemplate = \
'''<h4>Signals</h4>
<dl>
%(Signals)s
</dl>'''

signalsListEntryTemplate = \
'''<dt>%(Name)s</dt>
<dd>
%(Description)s
</dd>'''

eventsListTemplate = \
'''<h4>Events</h4>
<dl>
%(Events)s
</dl>'''

eventsListEntryTemplate = \
'''<dt>%(Name)s</dt>
<dd>
%(Description)s
</dd>'''

deprecatedTemplate = \
'''<p>
<b>Deprecated.</b>
%(Lines)s
</p>'''

authorInfoTemplate = \
'''<p>
<i>Author(s)</i>:
%(Authors)s
</p>'''

seeListTemplate = \
'''<dl>
<dt><b>See Also:</b></dt>
%(Links)s
</dl>'''

seeListEntryTemplate = \
'''<dd>
%(Link)s
</dd>'''

seeLinkTemplate = \
'''<a %(Link)s'''

sinceInfoTemplate = \
'''<p>
<b>since</b> %(Info)s
</p>'''

#################################
##  Templates for index files  ##
#################################

indexBodyTemplate = '''
<h1>%(Title)s</h1>
%(Description)s
%(Subpackages)s
%(Modules)s'''

indexListPackagesTemplate = '''
<h3>Packages</h3>
<table>
%(Entries)s
</table>'''

indexListModulesTemplate = '''
<h3>Modules</h3>
<table>
%(Entries)s
</table>'''

indexListEntryTemplate = \
'''<tr>
<td><a href="%(Link)s">%(Name)s</a></td>
<td>%(Description)s</td>
</tr>'''
