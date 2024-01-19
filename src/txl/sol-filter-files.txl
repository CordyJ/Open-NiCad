% NiCad filter given nonterminals from potential clones - Solidity files version
% Faizan Khan, September 2020

% Rev 5.10.20 JRC - Updated to NiCad 6.1

% NiCad tag grammar
include "nicad.grm"

% Solidity grammar
include "sol.grm"

define potential_clone
	[sourceFile]
end define

% Generic nonterminal filtering
include "generic-filter.rul"
