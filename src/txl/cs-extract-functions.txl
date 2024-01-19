% NiCad function extractor, C#
% Jim Cordy, January 2008

% Revised Oct 2020 - new source file name protocol - JRC
% Revised Apr 2019 - updated to use C# Edition 7 grammar - JRC
% Revised Aug 2012 - disallow ouput forms in input parse - JRC
% Revised July 2011 - ignore BOM headers in source
% Revised 30.04.08 - unmark embedded functions - JRC

% NiCad tag grammar
include "nicad.grm"

% Using C# grammar
include "csharp.grm"

% Ignore BOM headers from Windows
include "bom.grm"

% Redefinitions to collect source coordinates for function definitions as parsed input,
% and to allow for XML markup of function definitions as output

redefine method_declaration
        [opt attributes]    % Don't compare attributes in clone detection
	[method_definition] [NL]
    |
	% Uninteresting interface and right arrow forms
	[method_header] [opt right_arrow_expression] '; [NL]
end redefine

define method_definition
	% Input form 
	[srclinenumber] 			% Keep track of starting file and line number
	[method_header]				
	'{                                      [NL][IN] 
	    [opt statement_list]     		[EX]
	    [srclinenumber] 			% Keep track of ending file and line number
	'}  [opt ';]				
    |
	% Output form 
	[not token]				% disallow output form in input parse
	[opt xml_source_coordinate]
	[method_header]				
	'{                                      [NL][IN] 
	    [opt statement_list]     		[EX]
	'}  [opt ';]				
	[opt end_xml_source_coordinate]
end define

redefine program
	...
    | 	[repeat method_definition]
end redefine


% Main function - extract and mark up function definitions from parsed input program
function main
    replace [program]
	P [program]
    construct Functions [repeat method_definition]
    	_ [^ P] 			% Extract all functions from program
	  [convertFunctionDefinitions] 	% Mark up with XML
    by 
    	Functions [removeOptSemis]
	          [removeEmptyStatements]
end function

rule convertFunctionDefinitions
    import TXLargs [repeat stringlit]
	FileNameString [stringlit]

    % Find each function definition and match its input source coordinates
    replace [method_definition]
	LineNumber [srclinenumber]
	FunctionHeader [method_header]
	'{
	    FunctionBody [opt statement_list]
	    EndLineNumber [srclinenumber]
	'}  Semi [opt ';]

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
    replace [method_definition]
	LineNumber [srclinenumber]
	FunctionHeader [method_header]
	'{
	    FunctionBody [opt statement_list]
	    EndLineNumber [srclinenumber]
	'}  Semi [opt ';]
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

rule removeEmptyStatements
    replace [repeat declaration_or_statement+]
	';
	More [repeat declaration_or_statement+]
    by
	More
end rule
