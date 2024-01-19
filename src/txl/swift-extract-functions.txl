% NiCad function extractor, Swift
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

redefine function_declaration
	[function_definition]
    |	[not function_definition] [function_header]	% no body, uninteresting
end redefine

define function_definition
	% Input form 
	[srclinenumber] 			% Keep track of starting file and line number
	[function_header]
	'{ 				[IN][NL]
	    [statements?]		[EX]
	    [srclinenumber] 			% Keep track of ending file and line number
	'}
    |
	% Output form 
        [not input] 				% disallow output form in input parse
	[opt xml_source_coordinate]
	[function_header]
	'{ 				[IN][NL]
	    [statements?]		[EX]
	'}
	[opt end_xml_source_coordinate]
end redefine

define input
	[token] | [key]
end define

redefine program
	...
    | 	[repeat function_definition]
end redefine


% Main function - extract and mark up function definitions from parsed input program
function main
    replace [program]
	P [program]
    construct Functions [repeat function_definition]
    	_ [^ P] 			% Extract all functions from program
	  [convertFunctionDefinitions] 	% Mark up with XML
    by 
    	Functions [removeOptSemis]
end function

rule convertFunctionDefinitions
    import TXLargs [repeat stringlit]
	FileNameString [stringlit]

    % Find each function definition and match its input source coordinates
    replace [function_definition]
	LineNumber [srclinenumber]
	FunctionHeader [function_header]
	'{
	    FunctionBody [statements?]
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
	FunctionHeader 
	'{
	    FunctionBody [unmarkEmbeddedFunctionDefinitions]
	'}
	'</source>
end rule

rule unmarkEmbeddedFunctionDefinitions
    replace [function_definition]
	LineNumber [srclinenumber]
	FunctionHeader [function_header]
	'{
	    FunctionBody [statements?]
	    EndLineNumber [srclinenumber]
	'}
    by
	FunctionHeader 
	'{
	    FunctionBody
	'}
end rule

rule removeOptSemis
    replace [opt ';]
	';
    by
	% none
end rule
