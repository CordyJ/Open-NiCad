% NiCad blind renaming - C# files
% Jim Cordy, July 2020

% Rev 19.5.20 JRC - Added blind renaming for numeric and string literals

% NiCad tag grammar
include "nicad.grm"

% Using C# grammar
include "csharp.grm"

% Redefinition for potential clones

define potential_clone
    [compilation_unit]
end define

% Generic blind renaming
include "generic-rename-blind.rul"

% Literal renaming for C#
include "cs-rename-literals.rul"
