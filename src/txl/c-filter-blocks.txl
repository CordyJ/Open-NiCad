% NiCad filter given nonterminals from potential clones - C block version
% Jim Cordy, May 2010

% NiCad tag grammar
include "nicad.grm"

% Using Gnu C grammar
include "c.grm"

% Redefinition for potential clones
redefine compound_statement
    { [IN] [NL]
        [compound_statement_body] [EX]
    } [NL]
end redefine

define potential_clone
    [compound_statement]
end define

% Make sure that C grammar robustness does not eat NiCad tags
redefine unknown_declaration_or_statement
    [not endsourcetag] ...
end redefine

% Generic filter
include "generic-filter.rul"
