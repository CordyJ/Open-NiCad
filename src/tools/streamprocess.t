% Stream processor for single file extracted potential clones
% J.R. Cordy, May 2010

% Copyright 2010, J.R. Cordy

% Version 1.0 (20 May 2010)
% v1.1	27 Sep 2018	Revised for T+ 6.0 strings
% v1.2	14 Jul 2020	Added hard limit on number of lines in a batch
% v1.3	4 Nov 2020	Updated to remove temp files

% This program requires the Turing Plus 2009 compiler,
% http://research.cs.queensu.ca/~stl/download/pub/tplus/

% Unix system interface, so we can get command line arguments
include "%system"

% Main program
if fetcharg (1) = "" or fetcharg (2) not= "" then
    put : 0, "Usage:  streamprocess.x normalizing_command < system_functions.xml > system_functions-normalized.xml"
    quit : 1
end if

% Get program arguments
const command := fetcharg (1)	% command to run on potential clones

% We need to run sub-commands
external "system" function csystem (command : string) : int

% Make a new temp name
var unique : int := getpid 
var tempinfile := "/tmp/nicad" + intstr (unique) + ".in"

% Read and process the potential clones 
var line : string
get line:*

loop
    exit when eof 

    if index (line, "<source") not= 1 then
        put : 0, "*** Error: synchronization error on potential clones file"
        quit : 1
    end if
    
    % Get the next N potenial clones and put them in a file for processing
    const batchsize := 100

    var tf: int
    open : tf, tempinfile, put

    if tf = 0 then
        put : 0, "*** Error: can't create temp file "
        quit : 1
    end if

    % Limit total number of lines in a batch
    var nlines := 0
    const maxlines := 10000

    for i : 1 .. batchsize 
        % Next PC
	put : tf, line
	loop
	    % Turing line input gets only 4095 chars - lines can be longer
	    loop
		get line:*
		nlines += 1
		exit when eof or length (line) < 4095
		put : tf, line ..
	    end loop
	    exit when eof or index (line, "</source>") = 1
            put : tf, line
	end loop
        put : tf, line

	if index (line, "</source>") not= 1 then
	    put : 0, "*** Error: synchronization error on potential clones file"
	    quit : 1
	end if

        % Might be at end of PCs
        exit when eof

        get line:*

	% Might have exceeded batch line limit
	exit when nlines > maxlines
    end for

    close : tf

    % Process them using the command - automatically makes the output part of our output
    var rc := 0
    const commandline := command + " < " + tempinfile 
    rc := csystem (commandline)

    if rc not= 0 then
	put : 0, "*** Error: command failed: " + commandline
	quit : 1
    end if
end loop

var rc := 0
rc := csystem ("/bin/rm -f " + tempinfile)

% put : 0, "Done"
