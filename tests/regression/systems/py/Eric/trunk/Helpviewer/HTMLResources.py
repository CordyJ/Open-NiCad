# -*- coding: utf-8 -*-

# Copyright (c) 2009 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module containing some HTML resources.
"""

from PyQt4.QtCore import QString

notFoundPage_html = QString("""\
<html>
<head>
<title>%1</title>
<style>
body {
  padding: 3em 0em;
  background: #eeeeee;
}
hr {
  color: lightgray;
  width: 100%;
}
img {
  float: left;
  opacity: .8;
}
#box {
  background: white;
  border: 1px solid lightgray;
  width: 600px;
  padding: 60px;
  margin: auto;
}
h1 {
  font-size: 130%;
  font-weight: bold;
  border-bottom: 1px solid lightgray;
  margin-left: 48px;
}
h2 {
  font-size: 100%;
  font-weight: normal;
  border-bottom: 1px solid lightgray;
  margin-left: 48px;
}
ul {
  font-size: 80%;
  padding-left: 48px;
  margin: 5px 0;
}
#reloadButton {
  padding-left: 48px;
}
</style>
</head>
<body>
  <div id="box">
    <img src="data:image/png;base64,IMAGE_BINARY_DATA_HERE" width="32" height="32"/>
    <h1>%2</h1>
    <h2>%3</h2>
    <ul>
      <li>%4</li>
      <li>%5</li>
      <li>%6</li>
    </ul>
  </div>
</body>
</html>
""")

##########################################################################################

startPage_html = QString("""\
<?xml version="1.0" encoding="UTF-8" ?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
"http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en">
<head>
    <title></title>
    <style>
* {
    margin: 0;
    padding: 0;
    font-family: "DejaVu Sans";
}

body {
    background: -webkit-gradient(linear, left top, left bottom, from(#85784A), to(#FDFDFD), color-stop(0.5, #FDFDFD));
    background-repeat: repeat-x;
    margin-top: 200px;
}

#header, #search, #footer {
    width: 600px;
    margin: 10px auto;
}

#header, #search {
    -webkit-border-radius: 0.8em;
    padding: 25px;
}

#header {
    background: -webkit-gradient(linear, left top, left bottom, from(#D57E3E), to(#D57E3E), color-stop(0.5, #FFBA89));
    height: 25px;
}

#header h1 {
    display: inline;
    font-size: 1.7em;
    font-weight: bold;
}

#header img {
    display: inline;
    float: right;
    margin-top: -5px;
}

#search {
    background: -webkit-gradient(linear, left top, right top, from(#85784A), to(#85784A), color-stop(0.5, #C8C2AE));
    height: 50px;
    color: #000;
    text-align: center;
    padding-top: 40px !important;
}

#search fieldset {
    border: 0;
}

#search input[type=text] {
    width: 65%;
}

#search input[type=submit] {
    width: 25%;
}

#footer {
    text-align: center;
    color: #999;
}

#footer a {
    color: #555;
    text-decoration: none;
}

#footer a:hover {
    text-decoration: underline;
}
    </style>
    <script type="text/javascript">
        function update()
        {
            document.title = window.eric.translate('Welcome to Eric Web Browser!');
            document.getElementById('headerTitle').innerHTML = window.eric.translate('Eric Web Browser');
            document.getElementById('searchButton').value = window.eric.translate('Search!');
            document.getElementById('footer').innerHTML = window.eric.providerString()
                                                          + ' | ' + '<a href="http://eric-ide.python-projects.org/">'
                                                          + window.eric.translate('About Eric') + '</a>';
            document.getElementById('lineEdit').placeholder = window.eric.providerString();

            // Try to change the direction of the page:

            var newDir = window.eric.translate('QT_LAYOUT_DIRECTION');
            newDir = newDir.toLowerCase();
            if ((newDir != 'ltr') && (newDir != 'rtl'))
                newDir = 'ltr';
            document.getElementsByTagName('body')[0].setAttribute('dir', newDir);
        }

        function formSubmitted()
        {
            var string = lineEdit.value;

            if (string.length == 0)
                return;

            var url = window.eric.searchUrl(string);
            window.location.href = url;
        }
    </script>
</head>
<body onload="document.forms[0].lineEdit.select(); update();">
    <div id="header">
        <h1 id="headerTitle"></h1>
        <img src="data:image/png;base64,IMAGE_BINARY_DATA_HERE" width="32" height="32"/>
    </div>
    <div id="search">
        <form action="javascript:formSubmitted();">
            <fieldset>
                <input id="lineEdit" name="lineEdit" type="text" />
                <input id="searchButton" type="submit" />
            </fieldset>
        </form>
    </div>
    <div id="footer"></div>
</body>
</html>
""")
