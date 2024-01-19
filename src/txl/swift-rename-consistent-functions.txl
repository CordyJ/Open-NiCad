% NiCad consistent renaming - Swift functions
% Jim Cordy, June 2020

% Rev 19.5.20 JRC - Added blind renaming for numeric and string literals

% NiCad tag grammar
include "nicad.grm"

% Using Swift 5.2 grammar
include "swift.grm"

redefine function_declaration
	[function_definition]
    |	[not function_definition] [function_header]	% no body, uninteresting
end redefine

define function_definition
	[function_header]
	'{ 				[IN][NL]
	    [statements?]		[EX]
	'}
end redefine

define potential_clone
    [function_definition]
end define

% Tag specialization for Swift strings
redefine xml_source_coordinate
    '<source [SPOFF] 'file=[simple_string_literal] [SP] 'startline=[simple_string_literal] [SP] 'endline=[simple_string_literal] '> [SPON] [NL]
end redefine

%% % Generic consistent renaming
%% include "generic-rename-consistent.rul"

% Specialized consistent renaming for Swift
% In Swift, keywords can be used as identifiers

redefine xml_source_coordinate
    '<source [SPOFF] 'file=[simple_string_literal] [SP] 'startline=[simple_string_literal] [SP] 'endline=[simple_string_literal] '> [SPON] [NL]
end redefine

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

% Rule to normalize using consistent renaming of identifiers
% to normal form (x1, x2, x3, ...)

function renameIds
    replace [potential_clone]
        PC [potential_clone]

    % Make a list of all of the unique identifiers 
    construct Ids [repeat identifier]
        _ [^ PC] [removeDuplicateIds]

    % Make normalized new names of the form xN for each of them
    construct GenIds [repeat identifier]
        Ids [genIds 0]

    % Consistently replace each instance of each one by its normalized form
    by
        PC [$ each Ids GenIds]
end function

% Utility rule - remove duplicate ids from a list

function removeDuplicateIds
    replace [repeat identifier]
        Id [identifier] 
	Rest [repeat identifier]
    by
	Id
        Rest [removeIds Id]
	     [removeDuplicateIds]
end function

rule removeIds Id [identifier]
    replace [repeat identifier]
        Id
	More [repeat identifier]
    by
        More
end rule

% Utility rule - make a normalized id of the form xN for each unique id in a list

function genIds NM1 [number]
    % For each id in the list
    replace [repeat identifier]
        _ [identifier] 
        Rest [repeat identifier] 

    % Generate the next xN id
    construct N [number]
        NM1 [+ 1]
    construct GenId [id]
        _ [+ 'x] [+ N]

    % Replace the id with the generated one
    % and recursively do the next one
    by
        GenId 
        Rest [genIds N]
end function

% Literal renaming for Swift
include "swift-rename-literals.rul"
