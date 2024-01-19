% NiCad abstract given nonterminals from potential clones - C function version
% Jim Cordy, May 2010

% NiCad tag grammar
include "nicad.grm"

% Using Gnu C grammar
include "c.grm"

% Redefinition for potential clones
redefine function_definition
    [function_header]
    [opt KP_parameter_decls]
    '{ 					[IN][NL]
	[compound_statement_body] 	[EX]
    '} 
end redefine

define potential_clone
    [function_definition]
end define

% Make sure that C grammar robustness does not eat NiCad tags
redefine unknown_declaration_or_statement
    [not endsourcetag] ...
end redefine

% Generic abstract
include "generic-abstract.rul"

