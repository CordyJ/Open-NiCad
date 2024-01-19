% NiCad filter given nonterminals from potential clones - Solidity functions version
% Faizan Khan, September 2020

% Rev 5.10.20 JRC - Updated to NiCad 6.1

% NiCad tag grammar
include "nicad.grm"

% Solidity grammar
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

% Generic nonterminal filtering
include "generic-filter.rul"
