% New efficient implementation of NiCad clone detection tool
% J.R. Cordy, January 2010
% after the original Perl implementation by N. Synytskyy and C.K. Roy (thanks guys!)

% Copyright 2010-2012 J.R. Cordy, C.K. Roy, N. Synytskyy

% Version 5.10 (6 Oct 2020)
%    Space optimized LCS algorithm - JRC 6.10.20

% Version 5.9 (13 July 2020)
%    Updated to ignore lone INDENT and DEDENT lines when comparing - JRC 13.7.20

% Version 5.8 (21 May 2020)
%    Updated to ignore lone "}" lines when comparing - JRC 21.5.20
%    Updated to track nominal lines separately - JRC 21.5.20

% Version 5.7 (15 Feb 2016)
%    Updated nominal clone lines to be average of clone pair - JRC 19.11.15
%    Updated max clones to handle larger experiments - JRC 3.12.15
%    Optimized embedded clone pruning - JRC 3.12.15
%    Added explicit epsilon uncertainty to float comparisons - JRC 3.12.15

% This program is written in Turing Plus and requires the Turing Plus compiler,
% http://txl.ca/tplus/

% Unix system interface, so we can get command line arguments
include "%system"

% Program parameters - from the command line
% clonepairs.x pcfile threshold minclonelines maxcloneslines showsource
var pcfile : string			% name of the system_functions.xml pcs file
var threshold := 0.0			% difference threshold, 0.0 .. 0.9 (optional, default 0.0 (exact))
var minclonelines := 5			% minimum clone size (optional, default 5 lines)
var maxclonelines := 2500		% maximum clone size (optional, default 2500 lines)
var showsource := false			% embed pc source in results (optional, default no)

% Usage message
procedure useerr
    put : 0, "Usage :  clonepairs.x pcfile.xml [ threshold ] [ minclonesize ] [ maxclonesize ] [ showsource ] > clone-pairs-file.xml"
    put : 0, ""
    put : 0, "  e.g.:  clonepairs.x linux_functions.xml 0.2 > linux_functions-clones.xml"
    put : 0, ""
    put : 0, "    threshold = difference threshold, 0.0 .. 0.9 (optional, default 0.0 (exact))"
    put : 0, "    minclonesize = minimum clone size (optional, default 5 lines)"
    put : 0, "    maxclonesize = maximum clone size (optional, default 2500 lines, max 20000 lines)"
    put : 0, "    showsource = embed pc source in results (optional, argument present = yes, default no)"
    quit : 1
end useerr


% Get program parameters
forward procedure getprogramarguments
getprogramarguments


% Internal limits of this implementation
include "nicadsize.i"

const maxtotallines := 2500 * SIZE	% total lines in all potential clones together
const maxpcs := 150 * SIZE		% total number of potential clones
const maxclones := 500 * SIZE 		% maximum number of total clones in all classes

% Hash table for lines
const maxlinechars := 15000 * SIZE	% total characters in all unique lines
const maxlines := 300 * SIZE		% total unique lines

% Line text hash table
include "linetable.i"

% Potential clones - we read all pcs into this array
type PC :
    record
	num : int			% pc id
	info : linetable.LN		% info line, e.g., <source ... >
	srcfile : linetable.LN		% original source file name
	srcstartline, srcendline : int	% original source line range
        firstline : int			% 0 origin index of first line in lines array
	nlines : int			% actual number of comparison lines in the pc
	nomlines : int			% nominal nuber of lines in the pc
	embedding : int			% embedding clone class, intially 0
    end record

var pcs : array 1 .. maxpcs of PC
var npcs := 0

var lines : array 1 .. maxtotallines of linetable.LN
var nlines := 0
    
% Clone pairs - fills as we find them 
type CP :
    record
	pc1, pc2 : int
	nlines : int		% average of pcs
	similarity : int1	% in percent
    end record

var clonepairs: array 1..maxclones of CP
var npairs := 0

% Statistics we collect
var ncompares := 0 
var nclones := 0 
var nfragments := 0 

% Floating point uncertainly (for portability)
const epsilon := 0.000001


% Read the potential clones from the system_functions.xml file
% All line text is stored in the lines array, referenced by pcs array

procedure readpcs
    % Try to open our system_functions.xml file
    var pcf: int
    open : pcf, pcfile, get

    if pcf = 0 then
	useerr
    end if

    % Read the potential clones from it
    for i : 1 .. maxpcs
	% Indicate our progress 
	if i mod 1000 = 1 then
 	    put : 0, "." ..
	end if

	exit when eof (pcf)

	% Process the next pc
	npcs += 1

	bind var pc to pcs (npcs)
	pc.num := i
	pc.embedding := 0

	% Get the info header <source ... >
	var sourceheader : string
	get : pcf, sourceheader : *
	pc.info := linetable.install (sourceheader)

	if index (sourceheader, "<source ") not= 1 then
	    put : 0, "*** Error: synchronization error on pc file"
	    quit : 1
	end if

	% Decode the info header
	const sfindex := index (sourceheader, "file=") + length ("file=") + 1
	const sfend := index (sourceheader, " startline=") - 2
	pc.srcfile := linetable.install (sourceheader (sfindex .. sfend))

	const slindex := index (sourceheader, "startline=") + length ("startline=") + 1
	const slend := index (sourceheader, " endline=") - 2
	pc.srcstartline := strint (sourceheader (slindex .. slend))

	const elindex := index (sourceheader, "endline=") + length ("endline=") + 1
	const elend := length (sourceheader) - 2
	pc.srcendline := strint (sourceheader (elindex .. elend))

	% Store the lines of the pc in the lines array
	% pc.firstline is zero origin, so it is actually one less than the index
	% of the first line of the pc in the lines array
	pc.firstline := nlines 
	var nomlines := 0
	loop
	    if eof (pcf) then
	        put : 0, "*** Error: synchronization error on pc file"
	        quit : 1
	    end if

	    var line : string
	    get : pcf, line : *

	    exit when line = "</source>"

	    line := linetable.strip (line)	% JRC 1.7.15

	    if line not= "" 
		    and line not= "INDENT" 	% JRC 13.7.20 don't count or compare INDENT/DEDENT
		    and line not= "DEDENT" then
		nomlines += 1 
		if line not= "}" then		% JRC 21.5.20 count but don't compare "}" lines
		    nlines += 1		
		    if nlines > maxtotallines then
			put : 0, "*** Error: too many total lines ( > ", maxtotallines, ")"
			quit : 1
		    end if
		    lines (nlines) := linetable.install (line)
		end if
	    end if
	end loop

	pc.nlines := nlines - pc.firstline	% actual comparison size (sic) 
	pc.nomlines := nomlines			% nominal size

  	% We filter out pcs that are smaller or bigger than our pc size limits
	% by setting their size to zero
	if nomlines <  minclonelines or nomlines > maxclonelines then
	    pc.nlines := 0
	    pc.nomlines := 0
	    nlines := pc.firstline 	
	end if
    end for

    if not eof (pcf) then
	put : 0, "*** Error: too many potential clones ( > ", maxpcs, ")"
    end if

    close : pcf
end readpcs


% Use a standard quicksort to sort the pcs by decreasing size from largest to smallest

procedure swappcs (i, j : int)
    var t := pcs (i)
    pcs (i) := pcs (j)
    pcs (j) := t
end swappcs

var depth := 0

procedure sortpcs (first, last : int)
    depth := depth + 1

    % Indicate our progress 
    if depth mod 1000 = 1 then
        put : 0, "." ..
    end if

    
    if first < last then
	var low := first
	var high := last + 1
	var pivot := low
	loop
	    loop
		high -= 1
		exit when low = high 
		exit when pcs (high).nlines > pcs (pivot).nlines
	    end loop

	    exit when low = high

	    loop
		low += 1
		exit when low = high
		exit when pcs (pivot).nlines > pcs (low).nlines
	    end loop

	    exit when low = high

	    swappcs (low, high)
	end loop

	swappcs (high, pivot)
	sortpcs (first, high - 1)
	sortpcs (high + 1, last)
    end if

    depth := depth - 1
end sortpcs


% Standard dynamic programming version of the longest common subsequence (lcs) length algorithm 
% http://en.wikipedia.org/wiki/Longest_common_subsequence_problem#Computing_the_length_of_the_LCS
% Optimized to cut off early using a difference limit

% Space optimized to use only two rows needed - JRC 6.10.20

% var dpmatrix : array 0 .. m, 0 .. maxclonelines of nat2
var dpmatrix : array 0 .. 1, 0 .. maxclonelines of nat2
assert maxclonelines < 65536

function lcs (pc1, pc2 : PC, m, n: int, difflimit: int) : int
    pre m > 0 and n > 0

    % for i : 0 .. m
    for i : 0 .. 1
        dpmatrix (i, 0) := 0
    end for
    for j : 0 .. n
        dpmatrix (0, j) := 0
    end for

    var bi := 0 %

    for i : 1 .. m
	bi := i mod 2 %
        for j : 1 .. n
            if lines (pc1.firstline + i) = lines (pc2.firstline + j) then
                % dpmatrix (i, j) := dpmatrix (i - 1, j - 1) + 1
                dpmatrix (bi, j) := dpmatrix (1 - bi, j - 1) + 1
            % elsif dpmatrix (i - 1, j) >= dpmatrix (i, j - 1) then
            elsif dpmatrix (1 - bi, j) >= dpmatrix (bi, j - 1) then
                % dpmatrix (i, j) := dpmatrix(i - 1, j)
                dpmatrix (bi, j) := dpmatrix(1 - bi, j)
            else
                % dpmatrix (i, j) := dpmatrix (i, j - 1)
                dpmatrix (bi, j) := dpmatrix (bi, j - 1)
            end if
        end for

	% Optimize by cutting off when it's hopeless
	% if i - dpmatrix (i, n) > difflimit then
	if i - dpmatrix (bi, n) > difflimit then
	    result 0
	end if
    end for

    % result dpmatrix (m, n)
    result dpmatrix (bi, n)
end lcs


% We have two different definitions of clone - exact and near miss
% Exact clones' pc lines must match exactly 

function exact (pc1, pc2 : PC) : boolean
    assert pc1.nlines = pc2.nlines 
    for i : 1..pc1.nlines
	if lines (pc1.firstline + i) not= lines (pc2.firstline + i) then
	    result false
	end if
    end for
    result true
end exact


% Near miss clones are relative to our difference threshold
% By the NiCad definition, two pcs are near miss clones if
%    unique lines in pc1 / total lines in pc1 <= threshold, and
%    unique lines in pc2 / total lines in pc2 <= threshold
% where unique lines = total lines - common lines

function nearmiss (pc1, pc2 : PC) : int 	% returns percent same
    % Don't count self-clones
    if pc2.srcfile = pc1.srcfile and
	    pc2.srcstartline >= pc1.srcstartline and
	    pc2.srcendline <= pc1.srcendline then
	result 0
    end if

    % Compute the length of the longest common subsequence of lines
    const difflimit := round (pc1.nlines * threshold + epsilon) 
    const pc1pc2lcs := lcs (pc1, pc2, pc1.nlines, pc2.nlines, difflimit)

    % This condition implements exactly the NiCad nearmiss clone definition
    % quoted above
    if ((pc1.nlines - pc1pc2lcs) / pc1.nlines) <= threshold + epsilon 
	    and ((pc2.nlines - pc1pc2lcs) / pc2.nlines) <= threshold + epsilon then 
        result round (pc1pc2lcs / pc1.nlines * 100 + epsilon)
    else
	result 0
    end if
end nearmiss


% Evaluate whether two pcs are clones, using the above

function clone (pc1, pc2 : PC, threshold : real) : int	% percent same
    ncompares += 1
    if threshold + epsilon < 0.01 then
	if exact (pc1, pc2) then
	    nclones += 1
	    nfragments += 1
	    result 100
	end if
    else
	const sameness := nearmiss (pc1, pc2) 
	if 100 - sameness <= round (threshold * 100 + epsilon) then
	    nclones += 1
	    nfragments += 1
	    result sameness 
	end if
    end if
    result 0
end clone


% The NiCad algorithm - find  all clones by using each one as an exemplar,
% and comparing it to all others within the difference threshold of similar size

procedure findclones 

    for i : 1 .. npcs
	% Indicate our progress
	if i mod 1000 = 0 then
	    put : 0, "." ..
	end if

	% If the pc is within  our limits (already marked by nlines>0)
	if pcs (i).nlines not= 0 then

	    % We only need to look forward in the size-sorted array of pcs, 
	    % because pcs (i) has already been compared to all those before it
	    % of similar size, and our clone definition is commutative 

	    % No need to compare to those that are more than the threshold smaller
	    const difflimit := round (pcs (i).nlines * threshold + epsilon)

	    for j : i+1 .. npcs
		exit when pcs (j).nlines <  pcs (i).nlines - difflimit

		% If the second pc is within  our limits (already marked by nlines>0)
    		if pcs (j).nlines not=0 then

		    % Check for a new clone pair
		    const similarity := clone (pcs (i), pcs (j), threshold) 
		    if similarity not= 0 then
			npairs += 1
			if npairs > maxclones then
			    put : 0, "*** Error: too many clone pairs"
			    quit : 1
			end if
			bind var cp to clonepairs (npairs)
			cp.pc1 := i
			cp.pc2 := j
			cp.similarity := similarity
			cp.nlines := (pcs (i).nomlines + pcs (j).nomlines + 1) div 2	% nominal
		    end if
		end if
	    end for
	end if
    end for
end findclones


% Use a quicksort to create a sorted map of clonepairs by srcfile and size

var clonepairmap : array 1..maxclones of int

procedure swapclonepairmap (i, j : int)
    var t := clonepairmap (i)
    clonepairmap (i) := clonepairmap (j)
    clonepairmap (j) := t
end swapclonepairmap

var cdepth := 0

procedure sortclonepairmapbyfile (first, last : int)
    cdepth := cdepth + 1

    % Indicate our progress 
    if cdepth mod 1000 = 1 then
	put : 0, "." ..
    end if

    
    if first < last then
	var low := first
	var high := last + 1
	var pivot := low
	loop
	    loop
		high -= 1
		exit when low = high 
		exit when pcs (clonepairs (clonepairmap (high)).pc1).srcfile > pcs (clonepairs (clonepairmap (pivot)).pc1).srcfile
		    or pcs (clonepairs (clonepairmap (high)).pc1).srcfile = pcs (clonepairs (clonepairmap (pivot)).pc1).srcfile
			and clonepairs (clonepairmap (high)).nlines > clonepairs (clonepairmap (pivot)).nlines
	    end loop

	    exit when low = high

	    loop
		low += 1
		exit when low = high
		exit when pcs (clonepairs (clonepairmap (pivot)).pc1).srcfile > pcs (clonepairs (clonepairmap (low)).pc1).srcfile
		    or pcs (clonepairs (clonepairmap (pivot)).pc1).srcfile = pcs (clonepairs (clonepairmap (low)).pc1).srcfile
			and clonepairs (clonepairmap (pivot)).nlines > clonepairs (clonepairmap (low)).nlines
	    end loop

	    exit when low = high

	    swapclonepairmap (low, high)
	end loop

	swapclonepairmap (high, pivot)
	sortclonepairmapbyfile (first, high - 1)
	sortclonepairmapbyfile (high + 1, last)
    end if

    cdepth := cdepth - 1
end sortclonepairmapbyfile


% Prune embedded clone pairs 

procedure pruneembeddedpairs 
    % Remove any embedded smaller clone pairs 

    % First normalize srcfile order in pairs by hash code
    for i : 1 .. npairs
	if pcs (clonepairs (i).pc1).srcfile > pcs (clonepairs (i).pc2).srcfile 
		or  pcs (clonepairs (i).pc1).srcfile = pcs (clonepairs (i).pc2).srcfile
			and pcs (clonepairs (i).pc1).srcstartline > pcs (clonepairs (i).pc2).srcstartline then
	    const opc1 := clonepairs (i).pc1
	    clonepairs (i).pc1 := clonepairs (i).pc2
	    clonepairs (i).pc2 := opc1
	end if
    end for

    % Make sorted clone pair map by source file and size
    for i : 1 .. npairs
	clonepairmap (i) := i
    end for

    sortclonepairmapbyfile (1, npairs)

    % Now mark all embedded pairs
    var embeddedpairs := 0

    for decreasing i : npairs .. 1 
	% Indicate our progress 
	if i mod 1000 = 1 then
	    put : 0, "." ..
	end if

	% Test all previous pairs
	bind pc1 to pcs (clonepairs (clonepairmap (i)).pc1)
	bind pc2 to pcs (clonepairs (clonepairmap (i)).pc2)

	for decreasing j : i - 1 .. 1
	    bind bpc1 to pcs (clonepairs (clonepairmap (j)).pc1)
	    bind bpc2 to pcs (clonepairs (clonepairmap (j)).pc2)

	    % Sorted by source file and size
	    exit when bpc1.srcfile not= pc1.srcfile

	    % Check for embedding
	    if (bpc1.srcfile = pc1.srcfile and bpc2.srcfile = pc2.srcfile
		    and (bpc1.srcstartline <= pc1.srcstartline and
			bpc1.srcendline >= pc1.srcendline) 
		    and (bpc2.srcstartline <= pc2.srcstartline and
			bpc2.srcendline >= pc2.srcendline)) then
		embeddedpairs += 1
		% Mark for removal
		clonepairs (clonepairmap (i)).pc1 := 0
		clonepairs (clonepairmap (i)).pc2 := 0
		% Once marked, not need to look further
		exit
	    end if
	end for
    end for

    % Now remove the marked pairs
    npairs -= embeddedpairs
    var p := 1
    for i : 1 .. npairs 
	loop
	    exit when clonepairs (p).pc1 not= 0
	    p += 1
	end loop
	clonepairs (i) := clonepairs (p)
	p += 1
    end for

end pruneembeddedpairs


procedure showpairs
    % System information
    var slashindex := length (pcfile)
    loop
	const pcfchar : char := type (char, pcfile (slashindex))
	exit when slashindex = 0 or pcfchar = '/'
	slashindex -= 1
    end loop

    var systeminfo := pcfile (slashindex + 1 .. *) 
    var usindex := length (systeminfo)
    loop
	const sichar : char := type (char, systeminfo (usindex))
	exit when usindex = 2 or sichar = '_'
	usindex -= 1
    end loop

    var systemname := systeminfo (1 .. usindex - 1)
    var granularity := systeminfo (usindex + 1 .. index (systeminfo, ".xml") - 1)

    put "<clones>"
    put "<systeminfo processor=\"nicad6\" system=\"", systemname, "\" granularity=\"", granularity, "\" threshold=\"", round (threshold * 100 + epsilon), 
	"%\" minlines=\"", minclonelines, "\" maxlines=\"", maxclonelines, "\"/>"
    put "<cloneinfo npcs=\"", npcs, "\" npairs=\"", npairs, "\"/>"
    external "clock" function cpuclock : int
    var cputime := cpuclock
    put "<runinfo ncompares=\"", ncompares, "\" cputime=\"", cputime, "\"/>"
    put ""

    for i : 1 .. npairs
	% Indicate progress
	if i mod 1000 = 1 then
	    put : 0, "." ..
	end if

	bind cp to clonepairs (i)
	put "<clone nlines=\"", cp.nlines, "\" similarity=\"", cp.similarity, "\">" 

	bind pc1 to pcs (cp.pc1)
	bind pc2 to pcs (cp.pc2)

	put linetable.gettext (pc1.info) (1 .. *-1), " pcid=\"", pc1.num, "\">" ..
	if showsource then
	    put ""
	    for k : 1 .. pc1.nlines
		put linetable.gettext (lines (pc1.firstline + k))
	    end for
	end if
	put "</source>"

	put linetable.gettext (pc2.info) (1 .. *-1), " pcid=\"", pc2.num, "\">" ..
	if showsource then
	    put ""
	    for k : 1 .. pc2.nlines
		put linetable.gettext (lines (pc2.firstline + k))
	    end for
	end if
	put "</source>"

	put "</clone>"
	put ""
    end for 
    put "</clones>"
end showpairs


% Proces program arguments

body procedure getprogramarguments
    % Check usage
    if nargs < 1 then
	useerr
    end if

    % Names of the extracted pc XML file
    pcfile := fetcharg(1)

    % Difference threshold
    if nargs > 1 then
	threshold := strreal (fetcharg (2))
	if threshold < 0.0 or threshold > 1.0 then
	    useerr
	end if
    end if

    % Minimum clone size
    if nargs > 2 then
	minclonelines := strint (fetcharg (3))
	if minclonelines < 1 or minclonelines > 100 then
	    useerr
	end if
    end if

    % Maximum clone size
    if nargs > 3 then
	maxclonelines := strint (fetcharg (4))
	if maxclonelines < minclonelines or maxclonelines > 20000 then
	    useerr
	end if
    end if

    % Embedded source in our result
    if nargs > 4 then
	showsource := true
    end if
end getprogramarguments


% Main program

% Steps of the process
put : 0, "Processing ", pcfile, " with difference threshold ", round (threshold * 100 + epsilon), 
    "%, clone size ", minclonelines, " .. ", maxclonelines, " lines" ..
if showsource then
    put : 0, ", with pc source"
else
    put : 0, ""
end if

put : 0, "Reading pcs " ..
readpcs
put : 0, " done."
put : 0, "Total ", npcs, "/", maxpcs, " potential clones of ", minclonelines, " lines or more"
put : 0, "Used ", nlines, "/", maxtotallines, " total pc lines"
linetable.printstats

put : 0, "Sorting pcs " ..
sortpcs (1,npcs)
put : 0, " done."

put : 0, "Finding clones " ..
findclones 
put : 0, " done."

put : 0, "Total ", ncompares, " pc comparisons"

put : 0, "Pruning embedded clone pairs " ..
const oldnpairs := npairs
pruneembeddedpairs
put : 0, " done."

put : 0, "Pruned ", oldnpairs - npairs, " embedded clone pairs"
put : 0, "Found ", npairs, " clone pairs"

put : 0, "Generating XML output " ..
showpairs
put : 0, " done."
put : 0, ""

