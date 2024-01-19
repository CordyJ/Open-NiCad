% NiCad consistent renaming - Solidity functions
% Faizan Khan, September 2020 

% Rev 5.10.20 JRC - Updated to NiCad 6.1

% NiCad tag grammar
include "nicad.grm"

% Using Solidity grammar
include "sol.grm"

define function_header
    'function [opt id] [ParameterList]
    [FunctionalDefinitionInternalModifiers*]
    [opt OptionalReturnBlock] 
end define

define function_body
    [FunctionInternalEndBlock]
end define

redefine FunctionDefinition
    % Input form 
    [function_header]  [NL]
    [function_body]    [NL]
end define

define potential_clone
    [FunctionDefinition]
end define

% Generic consistent renaming
include "generic-rename-consistent.rul"

% Literal renaming for Java
include "sol-rename-literals.rul"
