% NiCad blind renaming - PHP functions
% Jim Cordy, October 2018

% Rev 19.5.20 JRC - Added blind renaming for numeric and string literals

% NiCad tag grammar
include "nicad.grm"

% Using PHP grammar
include "php.grm"

define method_definition
    [function_header]
    '{				[NL][IN] 
	[repeat TopStatement]	[EX]
    '}
end define

define function_header
    'function [opt '&] [opt id] '( [Param,] ')	[NL]
end define

define potential_clone
    [method_definition]
end define

% Generic blind renaming
include "generic-rename-blind.rul"

% Literal renaming for Java
include "php-rename-literals.rul"
