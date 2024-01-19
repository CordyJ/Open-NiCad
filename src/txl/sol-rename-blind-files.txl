% NiCad blind renaming - Solidity files
% Faizan Khan, September 2020 

% Rev 5.10.20 JRC - Updated to NiCad 6.1

% NiCad tag grammar
include "nicad.grm"

% Using Solidity grammar
include "sol.grm"

define potential_clone
    [sourceFile]
end define

% Generic blind renaming
include "generic-rename-blind.rul"

% Literal renaming for Java
include "sol-rename-literals.rul"
