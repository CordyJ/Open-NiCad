% NiCad filter given nonterminals from potential clones - Java functions version
% Jim Cordy, May 2010

% Revised July 2018 - update to match new Java 8 grammar - JRC

% NiCad tag grammar
include "nicad.grm"

% Using Java grammar
include "java.grm"

define method_definition
    [method_header]
    '{  [NL][IN] 
	[method_contents]  [EX]
    '} 
end define

define method_header
        % important: optional type_specifier subsumes constructor_declarations as well
        [repeat modifier] [opt type_parameters] [opt type_specifier] [method_declarator] [opt throws]
end define

define method_contents
	[repeat declaration_or_statement]     
end define

define potential_clone
    [method_definition]
end define

% Generic nonterminal filtering
include "generic-filter.rul"
