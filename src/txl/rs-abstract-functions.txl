% NiCad abstract given nonterminals from potential clones - Rust functions version
% Jim Cordy, October 2020

% NiCad tag grammar
include "nicad.grm"

% Rust grammar
include "rust.grm"

define potential_clone
    [Function]
end define

% Generic nonterminal abstraction
include "generic-abstract.rul"
