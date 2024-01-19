% Example custom context-dependent normalization: 
% abstract only if-condition expressions in Java 
% Jim Cordy, May 2010

% Revised July 2018 - update to match new Java 8 grammar - JRC

% NiCad tag grammar
include "nicad.grm"

% Using Java grammar
include "java.grm"

define method_definition
    [method_header]
    '{  [NL][IN] 
	[method_contents] [EX]
    '} 
end define

define method_header
        % important: optional type_specifier subsumes constructor_declarations as well
        [repeat modifier] [opt type_parameters] [opt type_specifier] [method_declarator] [opt throws]
end define

define method_contents
	[repeat declaration_or_statement]     
end define

define potential_clone
    [method_definition]
end define

% Generic normalization
include "generic-normalize.rul"


% The custom context-dependent normalizing rule you want applied

rule normalize
    replace $ [if_statement]
        'if '( Condition [expression] ')     
            ThenPart [statement]
        ElsePart [opt else_clause]      
    by
        'if '( 'expression ')     
            ThenPart 
        ElsePart 
end rule
