% NiCad consistent renaming - C# functions
% Jim Cordy, May 2010

% Rev 19.5.20 JRC - Added blind renaming for numeric and string literals

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

% Generic consistent renaming
include "generic-rename-consistent.rul"

% Literal renaming for C#
include "cs-rename-literals.rul"
