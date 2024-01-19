% NiCad abstract given nonterminals from potential clones - Java files version
% Jim Cordy, July 2020

% NiCad tag grammar
include "nicad.grm"

% Using Java 8 grammar
include "java.grm"

define potential_clone
    [package_declaration]
end define

% Generic nonterminal abstraction
include "generic-abstract.rul"
