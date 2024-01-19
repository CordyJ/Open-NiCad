% NiCad block extractor, Swift
% Jim Cordy, June 2020

% Revised Oct 2020 - new source file name protocol - JRC

% NiCad tag grammar
include "nicad.grm"

% Using Swift 5.2 grammar
include "swift.grm"

% Ignore BOM headers from Windows
include "bom.grm"

% Redefinitions to collect source coordinates for function definitions as parsed input,
% and to allow for XML markup of function definitions as output

redefine code_block
	% Input form 
	[srclinenumber] 		% Keep track of starting file and line number
	{ [IN] [NL]
	    [statements?] [EX]
	    [srclinenumber] 		% Keep track of ending file and line number
        } [NL]
    |
	% Output form 
	[not token]			% disallow input parse of this form
	[opt xml_source_coordinate]
	{ [IN] [NL]
	    [statements?] [EX]
        } [NL]
	[opt end_xml_source_coordinate]
end redefine

redefine program
	...
    | 	[repeat code_block]
end redefine


% Main function - extract and mark up compound statements from parsed input program
function main
    replace [program]
	P [program]
    construct Compounds [repeat code_block]
    	_ [^ P] 	% Extract all compound statements from program
	  [convertCompoundStatements]
    by 
    	Compounds [removeOptSemis]
end function

rule convertCompoundStatements
    import TXLargs [repeat stringlit]
	FileNameString [stringlit]

    % Find each compound statement and match its input source coordinates
    skipping [code_block]
    replace [code_block]
	LineNumber [srclinenumber]
	'{ 
	    CompoundBody [statements?] 
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
	{ 
	    CompoundBody [unmarkEmbeddedCompoundStatements] 
	'}
	'</source>
end rule

rule unmarkEmbeddedCompoundStatements
    replace [code_block]
	LineNumber [srclinenumber]
	'{ 
	    CompoundBody [statements?] 
	    EndLineNumber [srclinenumber]
	'} 
    construct Empty [opt xml_source_coordinate] 
	% none, to force output form
    by
	Empty
	'{
	    CompoundBody 
	'}
end rule

rule removeOptSemis
    replace [opt ';]
	';
    by
	% none
end rule
