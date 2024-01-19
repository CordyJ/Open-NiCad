% NiCad abstract given nonterminals from potential clones - C# function version
% Jim Cordy, May 2010

% NiCad tag grammar
include "nicad.grm"

% Using C# grammar
include "csharp.grm"

% Redefinition for potential clones

define method_definition
    [method_header]				
    '{  [NL][IN] 
	[opt statement_list]  [EX]
    '}  
end define

define potential_clone
    [method_definition]
end define

% Generic abstract
include "generic-abstract.rul"

