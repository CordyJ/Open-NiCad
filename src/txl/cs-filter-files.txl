% NiCad filter given nonterminals from potential clones - C# files version
% Jim Cordy, July 2020

% NiCad tag grammar
include "nicad.grm"

% Using C# grammar
include "csharp.grm"

% Redefinition for potential clones
define potential_clone
    [compilation_unit]
end define

% Generic filter
include "generic-filter.rul"

