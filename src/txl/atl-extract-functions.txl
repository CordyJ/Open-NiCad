% ATL rule extractor - JRC 25.5.18

% Example using TXL 10.5a source coordinate extensions to extract
% a table of all function definitions with source coordinates

% Jim Cordy, January 2008

% Revised Oct 2020 - new source file name protocol - JRC
% Revised Aug 2012 - disallow ouput forms in input parse - JRC
% Revised July 2011 - ignore BOM headers in source

% Using ATL grammar
include "atl.grm"

% Ignore BOM headers from Windows
include "bom.grm"

% Redefinitions to collect source coordinates for function definitions as parsed input,
% and to allow for XML markup of function definitions as output

redefine rule_
	[srclinenumber] 		% Keep track of starting file and line number
	[rule_header]
	'{ [NL][IN] 
	    [rule_body] [EX]
	    [srclinenumber] 		% Keep track of ending file and line number
	'} 
    |
	% Output form
        [not token]  			% disallow output form in input parse
	[opt xml_source_coordinate]
	[rule_header]
	'{ [NL][IN] 
	    [rule_body] [EX]
	'} 
	[opt end_xml_source_coordinate]
end redefine

define rule_header
        [rule_attribute*] 'rule [identifier] [rule_arguments?] [extends_id?] 
end define

define rule_body
	[inPattern?] 
	[using_clause?] 
	[outPattern?] 
	[actionBlock?] 
end define

define rule_attribute
	'unique | 'lazy | 'abstract | 'refining | 'entrypoint | 'endpoint | 'nodefault
end define

define rule_arguments
	'( [list parameter] ') 
end define

define xml_source_coordinate
    '< [SPOFF] 'source [SP] 'file=[stringlit] [SP] 'startline=[stringlit] [SP] 'endline=[stringlit] '> [SPON] [NL]
end define

define end_xml_source_coordinate
    [NL] '< [SPOFF] '/ 'source '> [SPON] [NL]
end define

redefine program
	...
    | 	[repeat rule_]
end redefine


% Main function - extract and mark up function definitions from parsed input program
function main
    replace [program]
	P [program]
    construct Rules [repeat rule_]
    	_ [^ P] 		% Extract all fules from program
	  [convertRules] 	% Mark up with XML
    by 
    	Rules 
end function

rule convertRules
    import TXLargs [repeat stringlit]
	FileNameString [stringlit]

    % Find each function definition and match its input source coordinates
    replace [rule_]
	LineNumber [srclinenumber]
	RuleHeader [rule_header]
	'{
	    RuleBody [rule_body]
	    EndLineNumber [srclinenumber]
	'}

    % Convert line numbers to strings for XML
    construct LineNumberString [stringlit]
	_ [quote LineNumber]
    construct EndLineNumberString [stringlit]
	_ [quote EndLineNumber]

    % Output is XML form with attributes indicating input source coordinates
    construct XmlHeader [xml_source_coordinate]
	'<source file=FileNameString startline=LineNumberString endline=EndLineNumberString>
    by
	XmlHeader
	RuleHeader 
	'{
	    RuleBody 
	'}
	'</source>
end rule

