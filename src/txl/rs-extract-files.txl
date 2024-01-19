% NiCad file extractor, Rust
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

redefine program
	% Input form 
	[srclinenumber] 		% Keep track of starting file and line number
	[Crate]
        [srclinenumber] 		% Keep track of ending file and line number
    |
	% Output form 
	[not token]			% disallow output form in input parse
	[opt xml_source_coordinate]
	[Crate]
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
	FileContents [Crate]
        EndLineNumber [srclinenumber]

    % Convert line numbers to strings for XML
    construct EndLineNumberString [stringlit]
	_ [quote EndLineNumber] 

    % Output is XML form with attributes indicating input source coordinates
    construct XmlHeader [xml_source_coordinate]
	'<source file=FileNameString startline="1" endline=EndLineNumberString>
    by
	XmlHeader
	FileContents 
	'</source>
end rule
