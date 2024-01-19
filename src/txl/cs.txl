% TXL C# Edition 7 Basis Grammar
% Version 3.1, April 2019

% Simple null program to test the C# grammar

% TXL C# Grammar
include "csharp.grm"

% Ignore BOM headers from Windows
include "bom.grm"

% Just parse
function main
    replace [program] 
        P [program]
    by
	P
end function

