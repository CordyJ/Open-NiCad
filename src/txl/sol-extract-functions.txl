% NiCad function extractor, Solidity
% Faizan Khan, September 2020 

% Revised Oct 2020 - new source file name protocol - JRC
% Rev 5.10.20 JRC - Updated to NiCad 6.1

% NiCad tag grammar
include "nicad.grm"

% Using Solidity grammar
include "sol.grm"

% Ignore BOM headers from Windows
include "bom.grm"

% Redefinitions to collect source coordinates for function definitions as parsed input,
% and to allow for XML markup of function definitions as output

redefine FunctionDefinition
	[FunctionDeclaration]		% with body
    |	[FunctionHeader] '; [NL]	% no body, uninteresting
end redefine

define FunctionHeader
    'function [opt id] [ParameterList]
    [FunctionalDefinitionInternalModifiers*]
    [opt OptionalReturnBlock] 
end define

redefine FunctionDeclaration
	% Input form 
	[srclinenumber] 		% Keep track of starting file and line number
	[FunctionHeader] 
  	'{ [NL] [IN]
 	    [Statement*] [EX]
	    [srclinenumber] 		% Keep track of ending file and line number 
	'} 
	
    |
	% Output form 
	[not token]			% disallow output form in input parse
	[opt xml_source_coordinate]
	[FunctionHeader] 
  	'{ [NL] [IN]
 	    [Statement*] [EX]
	'} 
	[opt end_xml_source_coordinate]
end define

define program
	... 
    | 	[repeat FunctionDeclaration] 
end define


% Main function - extract and mark up function definitions from parsed input program
function main
    replace [program]
        P [program]
    construct Functions [repeat FunctionDeclaration]
        _ [^ P] 
    by
        Functions [convertFunctionDeclarations]
end function

rule convertFunctionDeclarations
    import TXLargs [repeat stringlit]
	FileNameString [stringlit]

    % Find each function definition and match its input source coordinates
    replace [FunctionDeclaration]
	LineNumber [srclinenumber]
	Header [FunctionHeader] 
  	'{ 
 	    Statements [Statement*] 
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
	Header 
  	'{ 
 	    Statements 
	'} 
	'</source>
end rule
