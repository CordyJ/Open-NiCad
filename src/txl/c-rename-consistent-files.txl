% NiCad consistent renaming - C files
% Jim Cordy, July 2020

% Rev 19.5.20 JRC - Added blind renaming for numeric and string literals

% NiCad tag grammar
include "nicad.grm"

% Using Gnu C grammar
include "c.grm"

define potential_clone
    [translation_unit]
end define

% Make sure that C grammar robustness does not eat NiCad tags
redefine unknown_declaration_or_statement
    [not endsourcetag] ...
end redefine

% Generic consistent renaming
include "generic-rename-consistent.rul"

% Literal renaming for C
include "c-rename-literals.rul"
