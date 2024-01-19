% NiCad file extractor, Java
% Jim Cordy, July 2020

% Revised Oct 2020 - new source file name protocol - JRC
% Revised July 2018 - update to match new Java 8 grammar - JRC
% Revised Nov 2012 - remove @Override annotations from clone comparison - JRC
% Revised Aug 2012 - disallow ouput forms in input parse - JRC
% Revised July 2011 - ignore BOM headers in source
% Revised 25.03.11 - match constructors as methods - JRC
% Revised 30.04.08 - unmark embedded functions - JRC

% NiCad tag grammar
include "nicad.grm"

% Using Java 8 grammar
include "java.grm"

% Ignore BOM headers from Windows
include "bom.grm"

% Redefinitions to collect source coordinates for function definitions as parsed input,
% and to allow for XML markup of function definitions as output

% Modified to match constructors as well.  Even though the grammar still
% has constructor_declaration in it, this one will match first. - JRC 25mar11

redefine program
	% Input form 
	[srclinenumber] 		% Keep track of starting file and line number
	[package_declaration]
        [srclinenumber] 		% Keep track of ending file and line number
    |
	% Output form 
	[not token]			% disallow output form in input parse
	[opt xml_source_coordinate]
	[package_declaration]
	[opt end_xml_source_coordinate]
end redefine


% Main function - extract and mark up function definitions from parsed input program
function main
    replace [program]
	P [program]
    by 
    	P [convertProgram]
end function

rule convertProgram
    import TXLargs [repeat stringlit]
	FileNameString [stringlit]

    skipping [program]
    replace [program]
	LineNumber [srclinenumber]
	FileContents [package_declaration]
        EndLineNumber [srclinenumber]

    % Convert line numbers to strings for XML
    construct EndLineNumberString [stringlit]
	_ [quote EndLineNumber] 

    % Output is XML form with attributes indicating input source coordinates
    construct XmlHeader [xml_source_coordinate]
	'<source file=FileNameString startline="1" endline=EndLineNumberString>
    by
	XmlHeader
	FileContents [removeOptSemis] [removeEmptyStatements]
	'</source>
end rule

rule removeOptSemis
    replace [opt ';]
	';
    by
	% none
end rule

rule removeEmptyStatements
    replace [repeat declaration_or_statement]
	';
	More [repeat declaration_or_statement]
    by
	More
end rule
