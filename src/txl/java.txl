% TXL Java Grammar
% Version 5.0, November 2023

% Copyright 2001-2023 James R. Cordy, Xinping Guo and Thomas R. Dean

% Simple null program to test the Java grammar

% TXL Java Grammar
include "java.grm"

% Ignore BOM headers 
include "bom.grm"

% Just parse
function main
    replace [program] 
        P [program]
    by
        P
end function
