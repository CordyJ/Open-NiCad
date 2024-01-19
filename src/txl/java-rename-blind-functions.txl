% NiCad blind renaming - Java functions
% Jim Cordy, May 2010

% Rev 19.5.20 JRC - Added blind renaming for numeric and string literals
% Rev July 2018 JRC - Updated to match new Java 8 grammar 

% NiCad tag grammar
include "nicad.grm"

% Using Java grammar
include "java.grm"

define method_definition
    [method_header]
    '{                     [NL][IN] 
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

% Generic blind renaming
include "generic-rename-blind.rul"

% Literal renaming for Java
include "java-rename-literals.rul"
