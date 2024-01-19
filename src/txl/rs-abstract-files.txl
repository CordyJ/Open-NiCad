% NiCad abstract given nonterminals from potential clones - Rust files version
% Jim Cordy, October 2020

% NiCad tag grammar
include "nicad.grm"

% Rust grammar
include "rust.grm"

define potential_clone
    [Crate]
end define

% Generic nonterminal abstraction
include "generic-abstract.rul"
