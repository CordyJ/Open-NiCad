% Convert NiCad original source clonepairs XML report to HTML
% J.R. Cordy, April 2010

% v1.5  15 Jul 2020	Fixed bug in row output
% v1.4  20 May 2020	Added show/hide for source fragments, improved layout
% v1.3	16 Apr 2019	Bug fix in long line encoding
% v1.2	27 Sep 2018	Revised for T+ 6.0 strings
% v1.1 (2 May 2017)

% This program requires the Turing Plus 2009 compiler,
% http://research.cs.queensu.ca/~stl/download/pub/tplus/

% Unix system interface, so we can get command line arguments 
include "%system"


% HTML special character encoding
function encode (line : string) : string
    var eline := ""
    for i : 1 .. length (line)
        case ord (line (i)) of
	    label ord ("<") :
		eline += "&lt;"
	    label ord (">") :
		eline += "&gt;"
	    label ord ("&") :
		eline += "&amp;"
	    label :
		eline += line (i)
	end case
    end for
    result eline
end encode

% File name stripper
function strip (srcpath : string) : string
    if index (srcpath, ".ifdefed") = length (srcpath) - 7 then
	result srcpath (1 .. index (srcpath, ".ifdefed") - 1)
    elsif index (srcpath, ".pyindent") = length (srcpath) - 8 then
	result srcpath (1 .. index (srcpath, ".pyindent") - 1)
    else
        result srcpath
    end if
end strip

% Main program
if fetcharg (1) = "" or fetcharg (2) = "" then
    put : 0, "Usage:  tothml.x system_functions-clonepairs-withsource.xml system_functions-clonepairs-withsource.html"
    quit : 1
end if

% Get program argument
const ccfile := fetcharg (1)	% name of the sourced clonepairs XML file, e.g., system_functions-clonepairs-withsource.xml

% Try to open our system_functions-clonepairs-withsource.xml file
var ccf: int
open : ccf, ccfile, get 

if ccf = 0 then
    put : 0, "*** Error: can't open sourced clone classes input file"
    quit : 1
end if

% Create the resolved output file
var rccfile := fetcharg (2)	% name of the sourced clonepairs HTML file, e.g., system_functions-clonepairs-withsource.html
var rccf: int
open : rccf, rccfile, put 

% HTML style header
put : rccf, "<html>"
put : rccf, "<head>"
put : rccf, "    <title>NiCad6 Clone Report</title>"
put : rccf, "    <style type=\"text/css\">"
put : rccf, "        body {font-family:sans-serif;}"
put : rccf, "        table {background-color:white; border:0px; padding:0px; border-spacing:4px; width:auto; margin-left:30px; margin-right:auto;}"
put : rccf, "        td {background-color:rgba(192,212,238,0.8); border:0px; padding:8px; width:auto; vertical-align:top; border-radius:8px}"
put : rccf, "        pre {background-color:white; padding:4px;}"
put : rccf, "        a {color:darkblue;}"
put : rccf, "    </style>"
put : rccf, "</head>"
put : rccf, "<body>"
put : rccf, "<h2>NiCad6 Clone Report</h2>"

% Check file type
var line: string
get : ccf, line:* 

if line not= "<clones>" then
    put : 0, "*** Error: malformed sourced clone classes input file"
    quit : 1
end if

% Helper function to get tag attributes from systeminfo tag
function getinfo (infoline, infoname : string) : string
    const infohead := infoname + "=\""
    var info := ""
    if index (infoline, infohead) not= 0 then
        info := infoline (index (infoline, infohead) + length (infohead) .. *)
        info := info (1 .. index (info, "\"") - 1)
    end if
    result info
end getinfo

% Get system and summary information
% <systeminfo  system="httpd-2.2.8" [system2="httpd-3.4.1"] granularity="functions" threshold="30%" minlines="3", maxlines="2000"/>
get : ccf, line:* 
const system1name := getinfo (line, "system")
const system2name := getinfo (line, "system2")
const granularity := getinfo (line, "granularity")
const threshold := getinfo (line, "threshold")
const minlines := getinfo (line, "minlines")
const maxlines := getinfo (line, "maxlines")

% What clone type?
put : 0, granularity
put : 0, threshold
var clonetype := "1"
if index (granularity, "-blind") not= 0 then
    clonetype := "2"
elsif index (granularity, "-consistent") not= 0 then
    clonetype := "2c"
end if
if threshold not= "0%" then
    clonetype := "3-" + clonetype
end if

% <cloneinfo npcs="2886" npairs="294"/>
get : ccf, line:* 
const npcs := getinfo (line, "npcs") 
const npairs := getinfo (line, "npairs") 

% <runinfo ncompares="2915575" cputime="480000"/>
get : ccf, line:* 
/*
const ncompares := line (index (line, "ncompares=\"") + length ("ncompares=\"") .. index (line, "\" cputime=") - 1)
const cputime := line (index (line, "cputime=\"") + length ("cputime=\"") .. index (line, "\"/>") - 1)
const cputotalms := strint (cputime) div 1000
const cpums := cputotalms mod 1000
const cpusec := (cpums div 1000) mod 60
const cpumin := (cpums div 1000) div 60 
*/

% Optional classes header
get : ccf, line:*

var nclasses := ""
if index (line, "<classinfo ") = 1 then
    % <classinfo nclasses="69"/>
    nclasses := getinfo (line, "nclasses") 
    get : ccf, line:*
end if

% Output report summary 
put : rccf, "<table>"
put : rccf, "<tr style=\"font-size:14pt\">"
if system2name = "" then
    put : rccf, "<td><b>System:</b> &nbsp; ", system1name, "</td>"
else
    put : rccf, "<td><b>System 1:</b> &nbsp; ", system1name, "</td>"
    put : rccf, "<td><b>System 2:</b> &nbsp; ", system2name, "</td>"
end if
put : rccf, "<td><b>Clone pairs:</b> &nbsp; ", npairs, "</td>"
if nclasses not= "" then
    put : rccf, "<td><b>Clone classes:</b> &nbsp; ", nclasses, "</td>"
end if
put : rccf, "</tr>"

put : rccf, "<tr style=\"font-size:12pt\">"
put : rccf, "<td style=\"background-color:white\">Clone type: &nbsp; ", clonetype, "</td>"
put : rccf, "<td style=\"background-color:white\">Granularity: &nbsp; ", granularity, "</td>"
put : rccf, "<td style=\"background-color:white\">Max diff threshold: &nbsp; ", threshold, "</td>"
put : rccf, "<td style=\"background-color:white\">Clone size: &nbsp; ", minlines, " - ", maxlines, " lines", "</td>"
put : rccf, "<td style=\"background-color:white\">Total ", granularity, ": &nbsp; ", npcs, "</td>"
put : rccf, "</tr>"

/*
put : rccf, "<tr>"
put : rccf, "<td style=\"background-color:white\"><b>LCS compares:</b> &nbsp; ", ncompares, "</td>"
put : rccf, "<td style=\"background-color:white\"><b>CPU time:</b> &nbsp; ", cpumin, " min ", cpusec, ".", cpums, " sec", "</td>"
put : rccf, "</tr>"
*/

put : rccf, "</table>"

% Read the clone pairs 
loop
    exit when eof (ccf)

    % For each clone pair or class
    var nclassclones := "2"

    if index (line, "<clone ") = 1 or index (line, "<class ") = 1 then

	if index (line, "<clone ") = 1 then
	    % <clone  nlines="12" similarity="71">
	    const pairlines := line (index (line, "nlines=\"") + length ("nlines=\"") .. index (line, "\" similarity=") - 1)
	    const similarity := line (index (line, "similarity=\"") + length ("similarity=\"") .. index (line, "\">") - 1)

	    put : rccf, "<br>"
	    put : rccf, "<table style=\"width:1000px; border:2px solid lightgrey; border-radius:8px;\">"
            put : rccf, "<tr><td style=\"background-color:white\">"
	    put : rccf, "<p style=\"font-size:14pt\">" ..
	    put : rccf, "<b>Clone pair:</b> &nbsp; nominal size ", pairlines, " lines, similarity ", similarity, "%" ..
	    put : rccf, "</p>"
	    put : rccf, "<table cellpadding=4 border=2>"

        else 
	    assert index (line, "<class ") = 1
	    % <class classid="2"  nclones="1" nlines="12" similarity="70">
	    const classid := line (index (line, "classid=\"") + length ("classid=\"") .. index (line, "\" nclones=") - 1)
	    nclassclones := line (index (line, "nclones=\"") + length ("nclones=\"") .. index (line, "\" nlines=") - 1)
	    const classlines := line (index (line, "nlines=\"") + length ("nlines=\"") .. index (line, "\" similarity=") - 1)
	    const similarity := line (index (line, "similarity=\"") + length ("similarity=\"") .. index (line, "\">") - 1)

	    put : rccf, "<br>"
	    put : rccf, "<table style=\"width:1000px; border:2px solid lightgrey; border-radius:8px;\">"
            put : rccf, "<tr><td style=\"background-color:white\">"
	    put : rccf, "<p style=\"font-size:14pt\">" ..
	    put : rccf, "<b>Class ", classid, ":</b> &nbsp; ", nclassclones, " fragments, nominal size ", classlines, " lines, similarity ", similarity, "%" ..
	    put : rccf, "</p>"
	    put : rccf, "<table cellpadding=4 border=2>"
	end if

	% Limit the number of clones per row
	const maxclonesperline := 5
	var clonesperline := strint (nclassclones)
	loop
	    exit when clonesperline <= maxclonesperline
	    clonesperline := clonesperline div 2  
	end loop

	% For each clone in the class
	put : rccf, "<tr>" 
	var c := 0

	loop
	    exit when eof (ccf)
	    get : ccf, line:* 

	    exit when line = "</clone>" or line = "</class>"

	    if index (line, "<source") = 1 then

		% <source file="systems/c/httpd-2.2.8/server/mpm/worker/worker.c.ifdefed" startline="1650" endline="1875" pcid="2553">
		const srcfile := line (index (line, "file=\"") + length ("file=\"") .. index (line, "\" startline=") - 1)
		const startline := line (index (line, "startline=\"") + length ("startline=\"") .. index (line, "\" endline=") - 1)
		const endline := line (index (line, "endline=\"") + length ("endline=\"") .. index (line, "\" pcid=") - 1)
		const pcid := line (index (line, "pcid=\"") + length ("pcid=\"") .. index (line, "\">") - 1)

		var shortfile := srcfile
		if index (srcfile, "/" + system1name + "/") not= 0 then
		    shortfile := strip (srcfile (index (srcfile, "/" + system1name + "/") + 1 .. *))
		elsif index (srcfile, "/" + system2name + "/") not= 0 then
		    shortfile := strip (srcfile (index (srcfile, "/" + system2name + "/") + 1 .. *))
		end if

		put : rccf, "<td width=\"auto\">"
	
                put : rccf, "<a onclick=\"javascript:ShowHide('frag", pcid, "')\" href=\"javascript:;\">"
		put : rccf, shortfile, ": ", startline, "-", endline
		put : rccf, "</a>"

		put : rccf, "<div class=\"mid\" id=\"frag", pcid, "\" style=\"display:none\"><pre>"

		loop
		    exit when eof (ccf)

		    % Turing line input gets only 4095 chars - lines can be longer
		    loop
		        get : ccf, line:* 
			exit when eof (ccf) or length (line) < 4095
			% Encoding may make a line longer
		        put : rccf, encode (line (1..1000)) ..
		        put : rccf, encode (line (1001..2000)) ..
		        put : rccf, encode (line (2001..3000)) ..
		        put : rccf, encode (line (3001..*)) ..
		    end loop

		    exit when line = "</source>"

		    % Encoding may make a line longer
		    const lengthline := length (line)
		    if lengthline > 3000 then
		        put : rccf, encode (line (1..1000)) ..
		        put : rccf, encode (line (1001..2000)) ..
		        put : rccf, encode (line (2001..3000)) ..
		        put : rccf, encode (line (3001..*)) ..
		    elsif lengthline > 2000 then
		        put : rccf, encode (line (1..1000)) ..
		        put : rccf, encode (line (1001..2000)) ..
		        put : rccf, encode (line (2001..*)) ..
		    elsif lengthline > 1000 then
		        put : rccf, encode (line (1..1000)) ..
		        put : rccf, encode (line (1001..*)) ..
		    else
			put : rccf, encode (line)
		    end if
		end loop

		put : rccf, "</pre></div>"
		put : rccf, "</td>"
	    end if

	    if line not= "</source>" then
		put : 0, "*** Error: clone source file synchronization error"
		quit : 1 
	    end if

	    % Limit number of fragments per line
	    c += 1
	    if c mod clonesperline = 0 then
		put : rccf, "</tr><tr>"
	    end if
	end loop

	put : rccf, "</tr>"

	if line not= "</clone>" and line not= "</class>" then
	    put : 0, "*** Error: clone pair / class file synchronization error"
	    quit : 1 
	end if

	put : rccf, "</table>"
        put : rccf, "</td></tr>"
	put : rccf, "</table>"
    end if

    get : ccf, line:* 
end loop

% Hide/show function
put : rccf, "<script language=\"JavaScript\">"
put : rccf, "function ShowHide(divId) { "
put : rccf, "    if(document.getElementById(divId).style.display == 'none') {"
put : rccf, "        document.getElementById(divId).style.display='block';"
put : rccf, "    } else { "
put : rccf, "        document.getElementById(divId).style.display = 'none';"
put : rccf, "    } "
put : rccf, "}"
put : rccf, "</script>"

% HTML trailer
put : rccf, "</body>"
put : rccf, "</html>"

close : ccf
close : rccf
