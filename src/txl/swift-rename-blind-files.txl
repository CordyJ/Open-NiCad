% NiCad blind renaming - Swift files
% Jim Cordy, June 2020

% Rev 19.5.20 JRC - Added blind renaming for numeric and string literals

% NiCad tag grammar
include "nicad.grm"

% Using Swift 5.2 grammar
include "swift.grm"

define potential_clone
    [top_level_declaration]
end define

% Tag specialization for Swift strings
redefine xml_source_coordinate
    '<source [SPOFF] 'file=[simple_string_literal] [SP] 'startline=[simple_string_literal] [SP] 'endline=[simple_string_literal] '> [SPON] [NL]
end redefine

%% % Generic blind renaming
%% include "generic-rename-blind.rul"

% Specialized blind renaming for Swift
% In Swift, keywords can be used as identifiers

define source_unit  
    [xml_source_coordinate]
        [potential_clone]
    [end_xml_source_coordinate]
end define

redefine program
    [repeat source_unit]
end redefine

% Main program

rule main
    skipping [source_unit]
    replace $ [source_unit]
	BeginXML [xml_source_coordinate]
	    PC [potential_clone]
	EndXML [end_xml_source_coordinate]
    by
	BeginXML 
	    PC [renameIds]
	EndXML 
end rule

% In Swift, an identifier could be a keyword, so we need to generalize
rule renameIds
    replace $ [identifier]  % [id]
        _ [identifier]  % [id]
    by
	'x
end rule

% Literal renaming for Swift
include "swift-rename-literals.rul"
