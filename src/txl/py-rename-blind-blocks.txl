% NiCad blind renaming - Python blocks
% Jim Cordy, May 2010

% Rev 19.5.20 JRC - Added blind renaming for numeric and string literals

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

% Generic blind renaming
include "generic-rename-blind.rul"

% Specialize for Python
redefine xml_source_coordinate
    '<source [SPOFF] 'file=[stringlit] [SP] 'startline=[stringlit] [SP] 'endline=[stringlit] '> [SPON] [newline]
end redefine

redefine end_xml_source_coordinate
    '</source> [newline]
end redefine

% Literal renaming for Python
include "py-rename-literals.rul"
