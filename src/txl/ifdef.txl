% Antoniol et al heuristic to resolve all #ifs in C programs
% Jim Cordy, Feb 2008
% Version 2.4, November 2020
 
% Copyright 2008-2020 James R. Cordy

% Redistribution and use in source and binary forms, with or without
% modification, are permitted provided that the following conditions are met:
%
%    Redistributions of source code must retain the above copyright notice, 
%    this list of conditions and the following disclaimer.
%    Redistributions in binary form must reproduce the above copyright notice,
%    this list of conditions and the following disclaimer in the documentation
%    and/or other materials provided with the distribution.
%
%    THIS SOFTWARE IS PROVIDED "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
%    INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY
%    AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
%    AUTHORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY,
%    OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
%    SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
%    INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
%    CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
%    ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
%    POSSIBILITY OF SUCH DAMAGE.

% Comments out all preprocessor statements, and all #if and #elsif parts
% to leave the body of the #else part of all #ifs only

% Change Log:

% v2.4
%    Fixed another bug not commenting out contuation lines in #elsif - JRC 30.10.20
%    Added handling of tabs after # in directives - JRC 6.11.20
%    Changed all rules to one pass for speed  - JRC 12.11.20
%    Removed erroneous strange comment handling - JRC 13.11.20 

% v2.3
%    Fixed bug not commenting out contuation lines in #elsif - JRC 27.8.20

% v2.2
%    Fixed bug not commenting out empty #else - JRC 10.6.19

% v2.1
%    Added handling of initial BOM header in #ifdef - JRC 6.4.19
%    Refined preprocessor line token patterns - JRC 8.4.19
%    Refined handling of C# - JRC 10.4.19
%    Rationalized to assume no switches by default: - JRC 13.4.19
%     - #ifndef: keep then part
%     - #ifdef: keep #else if present,
%       otherwise first #elif if no #else,
%       otherwise nothing

% v2.0
%    Inverted to keep #else instead of #if part - JRC 16.11.10

% v1.0
%    Refined patterns for commenting out #if 0 - JRC 19.10.09
%    Refined token patterns for #if and preprocessor lines - JRC 6.5.08
%    Corrected token pattern for #elif - JRC 29.1.10
%    Corrected commenting out #elif - JRC 12.11.10

#pragma -char -comment -esc '\\' -width 32767

comments
        //
end comments

tokens
    % Long comments need to be handled specially
    comment     "/\*#[(\*/)']*\*/"
end tokens

compounds
        //
end compounds

tokens
    % A preprocessor line is one beginning with a # and then anything to end of line (\n#n*)
    % If the line ends in backslash, then it continues on the next line (\\\n)
    % Comments are assumed to be part of the preprocessor line (/\*#[(\*/)]*\*/)
    ifdef_line                "(﻿)?[ \t]*\#[ \t]*ifn?(def)?[ \t\(][(\\\n)(/\*#[(\*/)]*\*/)#n]*"
    elsedef_line              "[ \t]*\#[ \t]*else[(\\\n)(/\*#[(\*/)]*\*/)#n]*"
    elsifdef_line             "[ \t]*\#[ \t]*els?ifn?(def)?[ \t\(][(\\\n)(/\*#[(\*/)]*\*/)#n]*"
    endifdef_line             "[ \t]*\#[ \t]*endif[(\\\n)(/\*#[(\*/)]*\*/)#n]*"
    other_preprocessor_line   "[ \t]*\#[(\\\n)(\"#[\"\n]*\")(/\*#[(\*/)]*\*/)#n]*"
    % Anything else, iincluding single line comments, is just a text line to us
    other_line                "#n+" 
end tokens

define program
    [repeat line]
    [opt trailing_ifdef]
end define

define line
        [ifdef]
    |         [opt //] [other_preprocessor_line] [newline]
    |         [opt //] [any_other_line] [newline]
end define

define ifdef
        [opt //] [ifdef_line] [newline]
            [repeat line]
        [repeat elsif_part]
        [opt else_part]
        [opt //] [endifdef_line] [newline]
end define

define trailing_ifdef
        [opt //] [ifdef_line] [newline]
            [repeat line]
 	[see empty]	% EOF
end define

define elsif_part
        [opt //] [elsifdef_line]  [newline]
            [repeat line]
end define

define else_part
        [opt //] [elsedef_line]  [newline]
            [repeat line]
end define

define any_other_line
        [repeat not_newline] 
end define

define not_newline
        [long_comment]
    |         [not ifdef_token] [not newline] [token]
end define

define long_comment
        [repeat comment+]
end define

define ifdef_token
        [ifdef_line]   
    |         [elsedef_line]   
    |         [elsifdef_line]   
    |         [endifdef_line]
end define

function main
    replace [program]
	P [program]
    deconstruct * [newline] P
	NewlineToken [newline]
    construct Newline [stringlit]
	_ [quote NewlineToken]
    export Newline
    by
	P [commentOutPreprocessors]
	  [resolveIfdefsElse]
	  [resolveIfndefsThen]
	  [resolveIfdefsElif]
	  [resolveIfdefsNone]        
	  [resolveTrailingIfdef]        
end function

rule resolveIfdefsElse
    % We take the #else clause of a #if if it has one
    replace $ [ifdef]
	IfDef [ifdef_line] NL [newline]
	    ThenLines [repeat line]
	Elsifs [repeat elsif_part]
	Else [else_part]
	EndIf [endifdef_line] _ [newline]
    % For #ifs only
     where not 
	IfDef [grep "ifn"] [grep "if !"]
    % If a nonempty #else is present, it's probably the best choice
    deconstruct * [other_line] Else
	_ [other_line]
    by
	// IfDef [commentContinuationsIfDef] NL 
	    ThenLines [commentOutLines] 
	Elsifs [commentOutElsifs] 
	    [commentOutLines]
	Else [commentOutFirst] [commentContinuationsElseDef] 
	    % Leave these lines in
	// EndIf [commentContinuationsEndIfDef] NL
end rule

rule resolveIfndefsThen
    % We take the then clause of a #ifn always
    replace $ [ifdef]
	IfDef [ifdef_line] NL [newline]
	    ThenLines [repeat line]
	Elsifs [repeat elsif_part]
	Else [opt else_part]
	EndIf [endifdef_line] _ [newline]
    % For #ifns only
     where 
	IfDef [grep "ifn"] [grep "if !"]
    by
	// IfDef [commentContinuationsIfDef] NL 
	    % Leave these lines in
	    ThenLines         
	Elsifs [commentOutElsifs] 
	    [commentOutLines]
	Else [commentOutFirst] [commentContinuationsElseDef] 
	    [commentOutLines]
	// EndIf [commentContinuationsEndIfDef] NL
end rule

rule resolveIfdefsElif
    % If there is no #else but there are #elifs, we must choose one
    replace $ [ifdef]
	IfDef [ifdef_line] NL [newline]
	    ThenLines [repeat line]
	Elsif [elsif_part]
	Elsifs [repeat elsif_part]
	Else [opt else_part]
	EndIf [endifdef_line] _ [newline]
    deconstruct not * [other_line] Else
	_ [other_line]
    % For #ifs only
    where not 
	IfDef [grep "ifn"] [grep "if !"]
    by
	// IfDef [commentContinuationsIfDef] NL 
	    ThenLines [commentOutLines] 
	Elsif [commentOutFirst] [commentContinuationsElsif]
	    % Leave these lines in
	Elsifs [commentOutElsifs] 
	    [commentOutLines]
	Else [commentOutFirst] [commentContinuationsElseDef] 
	    [commentOutLines]
	// EndIf [commentContinuationsEndIfDef] NL
end rule

rule resolveIfdefsNone
    % If there is no #else and no #elifs, we must choose none to be consistent
    replace $ [ifdef]
	IfDef [ifdef_line] NL [newline]
	    ThenLines [repeat line]
	Elsifs [repeat elsif_part]
	Else [opt else_part]
	EndIf [endifdef_line] _ [newline]
    % For #ifs only
    where not 
	IfDef [grep "ifn"] [grep "if !"]
    by
	// IfDef [commentContinuationsIfDef] NL 
	    ThenLines [commentOutLines] 
	Elsifs [commentOutElsifs] 
	    [commentOutLines]
	Else [commentOutFirst] [commentContinuationsElseDef] 
	    [commentOutLines]
	// EndIf [commentContinuationsEndIfDef] NL
end rule

rule resolveTrailingIfdef
    % Trailing ifdefs are typically test code
    replace $ [trailing_ifdef]
	IfDef [ifdef_line] NL [newline]
	    ThenLines [repeat line]
    by
	// IfDef [commentContinuationsIfDef] NL 
	    % Leave these lines in
	    ThenLines [commentOutLines]         
end rule

function commentOutFirst
    replace * [opt //]
    by
	//
end function

rule commentOutPreprocessors
    replace $ [line]
	PrepLine [other_preprocessor_line] NL [newline]
    by
	// PrepLine [commentContinuationsPrepLine] NL
end rule

rule commentOutElsifs
    replace $ [elsif_part]
	ElsifLine [elsifdef_line] NL [newline]
	    Lines [repeat line]
    by
	// ElsifLine [commentContinuationsElsif] NL
	    Lines
end rule

rule commentOutLines
    replace $ [line]
	Line [line]
    by
	Line [commentOut]
	     [commentContinuationsIfDef]
	     [commentContinuationsElsif]
	     [commentContinuationsElseDef]
	     [commentContinuationsEndIfDef]
	     [commentContinuationsPrepLine]
	     [commentContinuationsCommentLine]
end rule

rule commentOut
    replace $ [opt //]
    by
	//
end rule

rule commentContinuationsIfDef
    import Newline [stringlit]
    replace $ [ifdef_line]
	IfDef [ifdef_line]
    construct NewlineIndex [number]
	_ [index IfDef Newline]
    deconstruct not NewlineIndex
	0
    construct PreNewline [ifdef_line]
	IfDef [: 1 NewlineIndex]
    construct NewlinePlus1 [number]
	NewlineIndex [+1]
    construct PostNewline [ifdef_line]
	IfDef [: NewlinePlus1 9999] [commentContinuationsIfDef]
    by
	PreNewline [+ "//"] [+ PostNewline] 
end rule

rule commentContinuationsElsif
    import Newline [stringlit]
    replace $ [elsifdef_line]
	Elsif [elsifdef_line]
    construct NewlineIndex [number]
	_ [index Elsif Newline]
    deconstruct not NewlineIndex
	0
    construct PreNewline [elsifdef_line]
	Elsif [: 1 NewlineIndex]
    construct NewlinePlus1 [number]
	NewlineIndex [+1]
    construct PostNewline [elsifdef_line]
	Elsif [: NewlinePlus1 9999] [commentContinuationsElsif]
    by
	PreNewline [+ "//"] [+ PostNewline] 
end rule

rule commentContinuationsElseDef
    import Newline [stringlit]
    replace $ [elsedef_line]
	ElseDef [elsedef_line]
    construct NewlineIndex [number]
	_ [index ElseDef Newline]
    deconstruct not NewlineIndex
	0
    construct PreNewline [elsedef_line]
	ElseDef [: 1 NewlineIndex]
    construct NewlinePlus1 [number]
	NewlineIndex [+1]
    construct PostNewline [elsedef_line]
	ElseDef [: NewlinePlus1 9999] [commentContinuationsElseDef]
    by
	PreNewline [+ "//"] [+ PostNewline] 
end rule

rule commentContinuationsEndIfDef
    import Newline [stringlit]
    replace $ [endifdef_line]
	EndIfDef [endifdef_line]
    construct NewlineIndex [number]
	_ [index EndIfDef Newline]
    deconstruct not NewlineIndex
	0
    construct PreNewline [endifdef_line]
	EndIfDef [: 1 NewlineIndex]
    construct NewlinePlus1 [number]
	NewlineIndex [+1]
    construct PostNewline [endifdef_line]
	EndIfDef [: NewlinePlus1 9999] [commentContinuationsEndIfDef]
    by
	PreNewline [+ "//"] [+ PostNewline] 
end rule

rule commentContinuationsPrepLine
    import Newline [stringlit]
    replace $ [other_preprocessor_line]
	PrepLine [other_preprocessor_line]
    construct NewlineIndex [number]
	_ [index PrepLine Newline]
    deconstruct not NewlineIndex
	0
    construct PreNewline [other_preprocessor_line]
	PrepLine [: 1 NewlineIndex]
    construct NewlinePlus1 [number]
	NewlineIndex [+1]
    construct PostNewline [other_preprocessor_line]
	PrepLine [: NewlinePlus1 9999] [commentContinuationsPrepLine]
    by
	PreNewline [+ "//"] [+ PostNewline] 
end rule

rule commentContinuationsCommentLine
    import Newline [stringlit]
    replace $ [comment]
	Comment [comment]
    construct NewlineIndex [number]
	_ [index Comment Newline]
    deconstruct not NewlineIndex
	0
    construct PreNewline [comment]
	Comment [: 1 NewlineIndex]
    construct NewlinePlus1 [number]
	NewlineIndex [+1]
    construct PostNewline [comment]
	Comment [: NewlinePlus1 9999] [commentContinuationsCommentLine]
    by
	PreNewline [+ "//"] [+ PostNewline] 
end rule
