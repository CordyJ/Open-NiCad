% Based on ATL grammar
include "atl.grm"

redefine program
	...
    |	[empty]
end redefine

function main
    replace [program]
	P [program]

    % Count rules
    construct Rules [rule_*]
	_ [^ P]
    construct NumberRules [number]
	_ [length Rules] [putp "rules "]

    % Count using clauses
    construct Usings [using_clause*]
	_ [^ P]
    construct NumberUsings [number]
	_ [length Usings] [putp "using clauses "]

    by
	% nada
end function
