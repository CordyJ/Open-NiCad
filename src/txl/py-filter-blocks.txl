% NiCad filter given nonterminals from potential clones - Python block version
% Jim Cordy, May 2010

% NiCad tag grammar
include "nicad.grm"

% Using Python grammar
include "python.grm"

% Redefinition for potential clones
define potential_clone
    [block]
end define

redefine indent
	[opt newline] 'INDENT [IN]
end redefine

redefine dedent
	[EX] 'DEDENT [newline]
end redefine

% Generic filter
include "generic-filter.rul"

% Specialize for Python
redefine xml_source_coordinate
    '<source [SPOFF] 'file=[stringlit] [SP] 'startline=[stringlit] [SP] 'endline=[stringlit] '> [SPON] [newline]
end redefine

redefine end_xml_source_coordinate
    '</source> [newline]
end redefine
