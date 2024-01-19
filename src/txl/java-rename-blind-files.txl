% NiCad blind renaming - Java files
% Jim Cordy, July 2020

% NiCad tag grammar
include "nicad.grm"

% Using Java grammar
include "java.grm"

define potential_clone
    [package_declaration]
end define

% Generic blind renaming
include "generic-rename-blind.rul"

% Literal renaming for Java
include "java-rename-literals.rul"
