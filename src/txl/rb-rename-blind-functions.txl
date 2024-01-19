% NiCad blind renaming - Ruby functions
% Jim Cordy, October 2018

% Rev 19.5.20 JRC - Added blind renaming for numeric and string literals

% NiCad tag grammar
include "nicad.grm"

% Using Ruby grammar
include "ruby.grm"

redefine method_definition
	'def [singleton_dot_or_coloncolon?] [fname] [argdecl] 
	    [body_statement]
	'end
end redefine

define potential_clone
    [method_definition]
end define

% Generic blind renaming
include "generic-rename-blind.rul"

% Specialize for Ruby
redefine xml_source_coordinate
    '<source [SPOFF] 'file=[stringlit] [SP] 'startline=[stringlit] [SP] 'endline=[stringlit] '> [SPON] [newline]
end redefine

redefine end_xml_source_coordinate
    [newline] '</source> [newline]
end redefine

% Literal renaming for Python
include "rb-rename-literals.rul"
