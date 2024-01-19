% NiCad extract functions, Python
% Jim Cordy, January 2008

% Revised Oct 2020 - new source file name protocol - JRC
% Revised Aug 2012 - disallow ouput forms in input parse - JRC
% Revised July 2011 - ignore BOM headers in source
% Revised 30.04.08 - unmark embedded blocks - JRC

% NiCad tag grammar
include "nicad.grm"

% Using Python grammar
include "python.grm"

% Ignore BOM headers from Windows
include "bom.grm"

% Redefinitions to collect source coordinates for block definitions as parsed input,
% and to allow for XML markup of block definitions as output

redefine block
	% input form
        [srclinenumber]				% Keep track of starting file and line number
        [indent] [endofline]
	    [opt docstring]
            [repeat statement_or_newline+]
	    [srclinenumber] 			% Keep track of ending file and line number
        [dedent]
    |
	% output form
	[not token]				% disallow output form in input parse
	[opt xml_source_coordinate]
        [indent] [endofline]
            [repeat statement_or_newline+]
        [dedent]
	[opt end_xml_source_coordinate]
end redefine

redefine indent
	[NL] 'INDENT [IN]
    |   [firstindent]
end redefine

define firstindent
	'INDENT [IN]
end define

redefine dedent
	[EX] 'DEDENT [NL]
end redefine

redefine program
	...
    | 	[repeat block]
end redefine

% Specialize for Python
redefine end_xml_source_coordinate
     '</source> [NL]
end redefine


% Main function - extract and mark up block definitions from parsed input program
function main
    replace [program]
	P [program]
    construct Blocks [repeat block]
    	_ [^ P] 			% Extract all blocks from program
	  [removeEmptyBlocks]		% Get rid of empty ones
	  [convertBlockDefinitions] 	% Mark up with XML
    by 
    	Blocks
end function

rule convertBlockDefinitions
    import TXLargs [repeat stringlit]
	FileNameString [stringlit]

    % Find each block definition and match its input source coordinates
    replace [block]
	LineNumber [srclinenumber]
        Indent [indent] EOL [endofline] 
	    DocString [opt docstring]
            BlockBody [repeat statement_or_newline+] 
	    EndLineNumber [srclinenumber]
	Dedent [dedent] 

    % Convert line numbers to strings for XML
    construct LineNumberString [stringlit]
	_ [quote LineNumber] 
    construct LineNumberPlus1 [number]
	_ [unquote LineNumberString] [+ 1]
    construct LineNumberPlus1String [stringlit]
	_ [quote LineNumberPlus1] 
    construct EndLineNumberString [stringlit]
	_ [quote EndLineNumber] 
    construct EndLineNumberMinus1 [number]
	_ [unquote EndLineNumberString] [- 1]
    construct EndLineNumberMinus1String [stringlit]
        _ [quote EndLineNumberMinus1]      
    construct FirstIndent [firstindent]
	'INDENT

    % Output is XML form with attributes indicating input source coordinates
    construct XmlHeader [xml_source_coordinate]
	'<source file=FileNameString startline=LineNumberPlus1String endline=EndLineNumberMinus1String>
    by
	XmlHeader
	    FirstIndent EOL 
	        BlockBody [unmarkEmbeddedBlockDefinitions] 
			  [reduceEndOfLines] 
		   	  [reduceEndOfLines2]
			  [reduceEmptyStmts]
	    Dedent 
	'</source>
end rule

rule unmarkEmbeddedBlockDefinitions
    replace [block]
	LineNumber [srclinenumber]
        Indent [indent] EOL [endofline] 
	    DocString [opt docstring]
            BlockBody [repeat statement_or_newline+] 
	    EndLineNumber [srclinenumber]
	Dedent [dedent] 
    by
        Indent EOL 
            BlockBody 
	Dedent 
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

rule removeEmptyBlocks
    replace [repeat block]
	LineNumber [srclinenumber]
        Indent [indent] EOL [endofline] 
	    DocString [opt docstring]
            BlockBody [repeat statement_or_newline+] 
	    EndLineNumber [srclinenumber]
	Dedent [dedent] 
        More [repeat block]
    deconstruct not * [statement] BlockBody
        Stmt [statement]
    by
        More
end rule
