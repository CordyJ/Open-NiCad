% NiCad abstract given nonterminals from potential clones - C files version
% Jim Cordy, July 2020

% NiCad tag grammar
include "nicad.grm"

% Using Gnu C grammar
include "c.grm"

% Redefinition for potential clones
define potential_clone
    [translation_unit]
end define

% Make sure that C grammar robustness does not eat NiCad tags
redefine unknown_declaration_or_statement
    [not endsourcetag] ...
end redefine

% Generic abstract
include "generic-abstract.rul"

