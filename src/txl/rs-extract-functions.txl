% NiCad function extractor, Rust
% Jim Cordy, October 2020

% Revised Oct 2020 - new source file name protocol - JRC

% NiCad tag grammar
include "nicad.grm"

% Using Rust grammar
include "rust.grm"

% Ignore BOM headers from Windows
include "bom.grm"

% Redefinitions to collect source coordinates for function definitions as parsed input,
% and to allow for XML markup of function definitions as output

redefine Function
	[FunctionDeclaration]
    |	[FunctionHeader] '; [NL]	% no body, not interesting
end redefine

define FunctionHeader
    	[FunctionQualifiers] 'fn [IDENTIFIER] [Generics?] '( [FunctionParameters?] ')
            [FunctionReturnType?] [WhereClause?]
end define

define FunctionDeclaration
    	% Input form
	[srclinenumber] 		% Keep track of starting file and line number
	[FunctionHeader]
	[LoopLabel?] 	
    	'{ [IN][NL]
            [InnerAttribute*]
            [Statements] [EX]
	    [srclinenumber] 		% Keep track of ending file and line number
    	'}
    |
	% Output form 
	[not token]			% disallow output form in input parse
	[opt xml_source_coordinate]
	[FunctionHeader]
	[LoopLabel?] 	
    	'{ [IN][NL]
            [InnerAttribute*]
            [Statements] [EX]
    	'}
	[opt end_xml_source_coordinate]
end define

redefine program
	...
    | 	[repeat FunctionDeclaration]
end redefine


% Main function - extract and mark up function definitions from parsed input program
function main
    replace [program]
	P [program]
    construct Functions [repeat FunctionDeclaration]
    	_ [^ P] 			% Extract all functions from program
	  [convertFunctionDefinitions] 	% Mark up with XML
    by 
    	Functions 
end function

rule convertFunctionDefinitions
    import TXLargs [repeat stringlit]
	FileNameString [stringlit]

    % Find each function definition and match its input source coordinates
    replace [FunctionDeclaration]
	LineNumber [srclinenumber]
	FunctionHeader [FunctionHeader]
	Label [LoopLabel?] 	
	'{
            Attributes [InnerAttribute*]
            Statements [Statements] 
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
	Label
	'{
	    Attributes
	    Statements [unmarkEmbeddedFunctionDefinitions] 
	'}
	'</source>
end rule

rule unmarkEmbeddedFunctionDefinitions
    replace [FunctionDeclaration]
	LineNumber [srclinenumber]
	FunctionHeader [FunctionHeader]
	Label [LoopLabel?] 	
	'{
            Attributes [InnerAttribute*]
            Statements [Statements] 
	    EndLineNumber [srclinenumber]
	'}
    by
	FunctionHeader 
	Label 
	'{
	    Attributes
	    Statements
	'}
end rule

