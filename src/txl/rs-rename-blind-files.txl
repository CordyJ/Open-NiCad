% NiCad blind renaming - Rust files
% Jim Cordy, October 2020

% NiCad tag grammar
include "nicad.grm"

% Using Rust grammar
include "rust.grm"

define potential_clone
    [Crate]
end define

% Generic blind renaming
include "generic-rename-blind.rul"

% Literal renaming for Java
include "rs-rename-literals.rul"
