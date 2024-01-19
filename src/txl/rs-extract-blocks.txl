% NiCad block extractor, Rust
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

redefine BlockExpression
    [LoopLabel?]
    [Block]
end redefine

define Block
    	% Input form
	[srclinenumber] 		% Keep track of starting file and line number
    	'{ [IN][NL]
            [InnerAttribute*]
            [Statements] [EX]
	    [srclinenumber] 		% Keep track of ending file and line number
    	'}
    |
	% Output form 
	[not token]			% disallow output form in input parse
	[opt xml_source_coordinate]
    	'{ [IN][NL]
            [InnerAttribute*]
            [Statements] [EX]
    	'}
	[opt end_xml_source_coordinate]
end define

redefine program
	...
    | 	[repeat Block]
end redefine


% Main function - extract and mark up function definitions from parsed input program
function main
    replace [program]
	P [program]
    construct Blocks [repeat Block]
    	_ [^ P] 		% Extract all functions from program
	  [convertBlocks] 	% Mark up with XML
    by 
    	Blocks
end function

rule convertBlocks
    import TXLargs [repeat stringlit]
	FileNameString [stringlit]

    % Find each block and match its input source coordinates
    skipping [Block]
    replace [Block]
	LineNumber [srclinenumber]
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
	'{
	    Attributes
	    Statements [unmarkEmbeddedBlocks] 
	'}
	'</source>
end rule

rule unmarkEmbeddedBlocks
    replace [Block]
        LineNumber [srclinenumber]
	'{
            Attributes [InnerAttribute*]
            Statements [Statements] 
	    EndLineNumber [srclinenumber]
	'}
    construct Empty [opt xml_source_coordinate] 
	% none, to force output form
    by
	Empty
	'{
	    Attributes
	    Statements
	'}
end rule

