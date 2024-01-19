% NiCad extract files, Python
% Jim Cordy, July 2020

% Revised Oct 2020 - new source file name protocol - JRC

% NiCad tag grammar
include "nicad.grm"

% Using Python grammar
include "python.grm"

% Ignore BOM headers from Windows
include "bom.grm"

% Redefinitions to collect source coordinates for function definitions as parsed input,
% and to allow for XML markup of function definitions as output

redefine program
        % input form
        [srclinenumber] 		% Keep track of starting file and line number
        [file_input]
        [srclinenumber] 		
    |
	% output form
	[not token]			% disallow output form in input parse
	[opt xml_source_coordinate]
        [file_input]
	[opt end_xml_source_coordinate]
end redefine

redefine indent
	[NL] 'INDENT [IN]
end redefine

redefine dedent
	[EX] 'DEDENT [NL]
end redefine

% Specialize for Python
redefine end_xml_source_coordinate
    '</source> [NL]
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
	FileContents [file_input]
        EndLineNumber [srclinenumber] 

    % Convert line numbers to strings for XML
    construct EndLineNumberMinus1 [number]
	_ [pragma "--newline"] [parse EndLineNumber] [- 1]	% correct for DEDENT lines
    construct EndLineNumberString [stringlit]
	_ [quote EndLineNumberMinus1] 

    % Output is XML form with attributes indicating input source coordinates
    construct XmlHeader [xml_source_coordinate]
	'<source file=FileNameString startline="1" endline=EndLineNumberString>
    by
	XmlHeader
	FileContents [removeDocstrings] [reduceEndOfLines] [reduceEndOfLines2] [reduceEmptyStmts]
	'</source>
end rule

rule removeDocstrings
    replace [opt docstring]
	_ [docstring]
    by
	% none
end rule

rule reduceEndOfLines
    replace [repeat endofline]
	EOL [endofline]
	_ [endofline]
	_ [repeat endofline]
    by
	EOL
end rule

rule reduceEndOfLines2
    replace [opt endofline]
	EOL [endofline]
    by
end rule

rule reduceEmptyStmts
    replace [repeat statement_or_newline]
	EOL [endofline]
	Stmts [repeat statement_or_newline]
    by
	Stmts
end rule
