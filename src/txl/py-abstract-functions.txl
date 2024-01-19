% NiCad abstract given nonterminals from potential clones - Python function version
% Jim Cordy, May 2010

% NiCad tag grammar
include "nicad.grm"

% Using Python grammar
include "python.grm"

% Redefinition for potential clones
define block_funcdef
    [funcdef_header] ': 
    [indent] [endofline] 
	[repeat fstatement+] 
    [dedent] 
end define

define fstatement
    [repeat newline] [statement]
end define

define potential_clone
    [block_funcdef]
end define

redefine indent
	[newline] 'INDENT [IN]
end redefine

redefine dedent
	[EX] 'DEDENT [newline]
end redefine

% Generic abstract
include "generic-abstract.rul"

% Specialize for Python
redefine xml_source_coordinate
    '<source [SPOFF] 'file=[stringlit] [SP] 'startline=[stringlit] [SP] 'endline=[stringlit] '> [SPON] [newline]
end redefine

redefine end_xml_source_coordinate
    '</source> [newline]
end redefine
