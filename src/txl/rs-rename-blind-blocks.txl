% NiCad blind renaming - Rust blocks
% Jim Cordy, October 2020

% NiCad tag grammar
include "nicad.grm"

% Using Rust grammar
include "rust.grm"

define potential_clone
    [BlockExpression]
end define

% Generic blind renaming
include "generic-rename-blind.rul"

% Literal renaming for Java
include "rs-rename-literals.rul"
