% NiCad block extractor, Java
% Jim Cordy, October 2009

% Revised Oct 2020 - new source file name protocol - JRC
% Revised July 2018 - update to match new Java 8 grammar - JRC
% Revised Aug 2012 - disallow output forms in input parse - JRC
% Revised July 2011 - ignore BOM headers in source

% NiCad tag grammar
include "nicad.grm"

% Using Java grammar
include "java.grm"

% Ignore BOM headers from Windows
include "bom.grm"

% Redefinitions to collect source coordinates for blocks as parsed input,
% and to allow for XML markup of blocks as output

redefine block
        % Input form
        [srclinenumber]                 % Keep track of starting file and line number
        { [IN] [NL]
            [block_contents] [EX]
            [srclinenumber]             % Keep track of ending file and line number
        } [opt ';] [NL]
    |
        % Output form
        [not token]                     % disallow input parse of this form
        [opt xml_source_coordinate]
        { [IN] [NL]
            [block_contents] [EX]
        } [opt ';] [NL]
        [opt end_xml_source_coordinate]
end redefine

define block_contents
        [repeat declaration_or_statement]
end define

redefine program
        ...
    |   [repeat block]
end redefine


% Main function - extract and mark up blocks from parsed input program
function main
    replace [program]
        P [program]
    construct Compounds [repeat block]
        _ [^ P]         % Extract all blocks from program
          [convertCompoundStatements]
    by 
        Compounds [removeOptSemis]
                  [removeEmptyStatements]
end function

rule convertCompoundStatements
    import TXLargs [repeat stringlit]
        FileNameString [stringlit]

    % Find each block and match its input source coordinates
    skipping [block]
    replace [block]
        LineNumber [srclinenumber]
        '{ 
            CompoundBody [block_contents] 
            EndLineNumber [srclinenumber]
        '} Semi [opt ';]

    % Convert line numbers to strings for XML
    construct LineNumberString [stringlit]
        _ [quote LineNumber]
    construct EndLineNumberString [stringlit]
        _ [quote EndLineNumber]

    % Output is XML form with attributes indicating input source coordinates
    construct XmlHeader [xml_source_coordinate]
        '<source file=FileNameString startline=LineNumberString endline=EndLineNumberString>
    by
        XmlHeader
        { 
            CompoundBody [unmarkEmbeddedCompoundStatements] 
        '}
        '</source>
end rule

rule unmarkEmbeddedCompoundStatements
    replace [block]
        LineNumber [srclinenumber]
        '{ 
            CompoundBody [block_contents]
            EndLineNumber [srclinenumber]
        '} Semi [opt ';]
    construct Empty [opt xml_source_coordinate] 
        % none, to force output form
    by
        Empty
        '{
            CompoundBody 
        '}
end rule

rule removeOptSemis
    replace [opt ';]
        ';
    by
        % none
end rule

rule removeEmptyStatements
    replace [repeat declaration_or_statement]
        ';
        More [repeat declaration_or_statement]
    by
        More
end rule
