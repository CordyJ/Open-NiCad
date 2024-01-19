% NiCad blind renaming - C# blocks
% Jim Cordy, May 2010

% Rev 19.5.20 JRC - Added blind renaming for numeric and string literals

% NiCad tag grammar
include "nicad.grm"

% Using C# grammar
include "csharp.grm"

% Redefinition for potential clones
redefine block
    { [IN] [NL]
	[opt statement_list] [EX]
    } [NL]
end redefine

define potential_clone
    [block]
end define

% Generic blind renaming
include "generic-rename-blind.rul"

% Literal renaming for C#
include "cs-rename-literals.rul"
