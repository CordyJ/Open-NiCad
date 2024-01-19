% NiCad 3.0 clone pair clustering
% J.R. Cordy, January 2012

% Copyright 2012 J.R. Cordy

% Version 2.0 (3 Dec 2015)
%    Changed to n*log n clustering algorithm - JRC 19.11.15
%    Updated max clone pairs to handle bigger experiments - JRC 3.12.15

% This program requires the Turing Plus 2009 compiler,
% http://research.cs.queensu.ca/~stl/download/pub/tplus/

% Unix system interface, so we can get command line arguments
include "%system"

% Program parameters - from the command line
% cloneclass.x clonepairsfile 
var cpfile : string			% name of the system_functions-clonepairs.xml file

% Usage message
procedure useerr
    put : 0, "Usage :  cloneclass.x cpfile.xml > clone-clusters-file.xml"
    put : 0, ""
    put : 0, "  e.g.:  cloneclass.x linux_functions-clonepairs.xml > linux_functions-clone-clusters.xml"
    put : 0, ""
    quit : 1
end useerr


% Limits of this implementation
include "nicadsize.i"

const maxpcs := 150 * SIZE		% total number of potential clones
const maxclusters := 50 * SIZE		% maximum number of clone classes
const maxclones := 500 * SIZE		% maximum number of total clones in all classes
const maxpairs := 2 * maxclones		% clone pairs are commutative, we represent both directions

% Hash table for lines
const maxlinechars := 1500 * SIZE	% total characters in all unique clone pair names
const maxlines := 300 * SIZE		% total unique lines

% Line text hash table
include "linetable.i"

% System information - we read this from the clone pairs file
var systeminfo, cloneinfo, runinfo : int
 
% Cloned pairs - we read all clone pairs into this array
type CP :
    record
	info : int			% clone pair info line
	nlines : int			% nominal size 
	similarity : int		% percent similar
	pc1info, pc2info : int		% pc info lines
	pc1, pc2 : int			% pc numbers
	cluster : int			% which cluster is this pair in?
    end record

var pairs : array 1..maxpairs of CP
var npairs := 0

% Map pcs to their first direct clone after sorting
% Sorting groups clone pairs by first pc
var pcpair : array 1..maxpcs of int
for z: 1..maxpcs
    pcpair (z) := 0
end for


% Read the clone pairs from the system_functions-clonepairs.xml file
% All line text is stored in the lines array, referenced by pcs array

procedure readclonepairs
    % Try to open our system_functions.xml file
    var cpf: int
    open : cpf, cpfile, get

    if cpf = 0 then
	useerr
    end if

    % <clones>
    var line : string
    get : cpf, line : *
    if line not= "<clones>" then
	put : 0, "*** Error: input file not a clone pair file"
 	useerr
    end if

    % <systeminfo  system="JHotDraw54b1" granularity="functions" threshold="30%" minlines="5" maxlines="500"/>
    get : cpf, line : *
    if index (line, "<systeminfo ") not= 1 then
	put : 0, "*** Error: synchronization error on clone pair file"
	quit : 1
    else
	systeminfo := linetable.install (line)
    end if

    % <cloneinfo npcs="2886" npairs="293"/>
    get : cpf, line : *
    if index (line, "<cloneinfo ") not= 1 then
	put : 0, "*** Error: synchronization error on clone pair file"
	quit : 1
    else
	cloneinfo := linetable.install (line)
    end if

    % <runinfo ncompares="1895191" cputime="16"/>
    get : cpf, line : *
    if index (line, "<runinfo ") not= 1 then
	put : 0, "*** Error: synchronization error on clone pair file"
	quit : 1
    else
	runinfo := linetable.install (line)
    end if

    % Read the clone pairs from it
    for i : 1 .. maxclones
	% Indicate our progress 
	if i mod 1000 = 1 then
 	    put : 0, "." ..
	end if

	exit when eof (cpf)

	% Process the next clone pair

	% <clone nlines="5" similarity="100">
	get : cpf, line : *
	if line = "" then
	    get : cpf, line : *
	end if

	exit when index (line, "</clones>") = 1

	if index (line, "<clone ") not= 1 then
	    put : 0, "*** Error: synchronization error on clone pair file"
	    quit : 1
	end if

	npairs += 1

	bind var pair to pairs (npairs)

	pair.info := linetable.install (line)
	const nlines := line (index (line, "nlines=\"") + length ("nlines=\"") .. index (line, " similarity=\"") - 2)
	const similarity := line (index (line, "similarity=\"") + length ("similarity=\"") .. index (line, "\">") - 1)
	pair.nlines := strint (nlines) 
	pair.similarity := strint (similarity) % linetable.install (similarity)
	pair.cluster := 0

	% <source file="examples/JHotDraw54b1/src/CH/ifa/draw/contrib/PolygonScaleHandle.java" startline="141" endline="145" pcid="691"></source>
	get : cpf, line : *
	if line = "" then
	    get : cpf, line : *
	end if
	if index (line, "<source ") not= 1 then
	    put : 0, "*** Error: synchronization error on clone pair file"
	    quit : 1
	end if

	pair.pc1info := linetable.install (line)
	const pcid1 := line (index (line, "pcid=\"") + length ("pcid=\"") .. index (line, "\">") - 1)
	pair.pc1 := strint (pcid1) 

	% <source file="examples/JHotDraw54b1/src/CH/ifa/draw/figures/RadiusHandle.java" startline="88" endline="92" pcid="1296"></source>
	get : cpf, line : *
	if line = "" then
	    get : cpf, line : *
	end if
	if index (line, "<source ") not= 1 then
	    put : 0, "*** Error: synchronization error on clone pair file"
	    quit : 1
	end if

	pair.pc2info := linetable.install (line)
	const pcid2 := line (index (line, "pcid=\"") + length ("pcid=\"") .. index (line, "\">") - 1)
	pair.pc2 := strint (pcid2) 

	% enter reverse pair
	npairs += 1

	bind var revpair to pairs (npairs)

	revpair := pair
	revpair.pc1 := pair.pc2
	revpair.pc1info := pair.pc2info
	revpair.pc2 := pair.pc1
	revpair.pc2info := pair.pc1info

	% </clone>
	get : cpf, line : *
	if index (line, "</clone>") not= 1 then
	    put : 0, "*** Error: synchronization error on clone pair file"
	    quit : 1
	end if
    end for

    if not eof (cpf) then
	put : 0, "*** Error: too many clone pairs ( > ", maxclones, ")"
    end if

    close : cpf
end readclonepairs


% Use a standard quicksort to sort pairs by first pc number
% This effectively groups all clone pairs for each pc together

procedure swapclonepairs (i, j : int)
    var t := pairs (i)
    pairs (i) := pairs (j)
    pairs (j) := t
end swapclonepairs

var depth := 0

procedure quicksortclonepairs (first, last : int)
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
		exit when pairs (high).pc1 < pairs (pivot).pc1
	    end loop

	    exit when low = high

	    loop
		low += 1
		exit when low = high
		exit when pairs (pivot).pc1 < pairs (low).pc1
	    end loop

	    exit when low = high

	    swapclonepairs (low, high)
	end loop

	swapclonepairs (high, pivot)
	quicksortclonepairs (first, high - 1)
	quicksortclonepairs (high + 1, last)
    end if

    depth := depth - 1
end quicksortclonepairs

procedure indexpairs
    for i : 1 .. npairs
        % Indicate our progress 
        if i mod 2000 = 1 then
	    put : 0, "." ..
        end if

	bind pair to pairs (i)
	if pcpair (pair.pc1) = 0 then
	    pcpair (pair.pc1) := i
	end if
    end for
end indexpairs


% The difference threshold was decided when the pairs were created.  
% So all we need to do is cluster the sets of pcs that are related by the clone pair relation.

% Clone classes - fills in as we find them 
type CL :
    record
	pairs : int			% 0 origin index of first pair in clusterpairs array
	npairs : int
    end record

var clusters: array 1..maxclusters of CL
var nclusters := 0

var clusterpairs : array 1 .. maxclones of int 
var nclusterpairs := 0

procedure clusterclonepairs

    for i : 1 .. npairs
	% Indicate our progress 
	if i mod 2000 = 1 then
	    put : 0, "." ..
	end if

	bind var pair to pairs (i)

	if pair.cluster = 0 then
	    % Each unclustered pair starts a new cluster
	    nclusters += 1
	    pair.cluster := nclusters

	    % First fill the cluster with the pairs for this one
	    bind var cluster to clusters (nclusters)
	    cluster.pairs := nclusterpairs
	    cluster.npairs := 1
	    nclusterpairs += 1
	    clusterpairs (nclusterpairs) := i

	    % Add in the rest of the pairs for pc1
	    for j : i+1 .. npairs
		exit when pairs (j).pc1 not= pair.pc1
		pairs (j).cluster := nclusters
		cluster.npairs += 1
		nclusterpairs += 1
		clusterpairs (nclusterpairs) := j
	    end for

	    % Closure - add in the pairs for those pairs' pc2s
	    var cp := cluster.pairs
	    loop
		exit when cp > nclusterpairs

		bind pcp to pairs (clusterpairs (cp))

		if pcpair (pcp.pc2) not= 0 then
		    for j : pcpair (pcp.pc2) .. npairs
			exit when pairs (j).pc1 not= pcp.pc2 

			bind var newpair to pairs (j)

			if newpair.cluster = 0 then
			    % it's in this cluster
			    newpair.cluster := nclusters

			    % do we already have this clone pair's target pc2?
			    var alreadyhaveit := false
			    for k: 1 .. nclusterpairs 
			        bind oldpair to pairs (clusterpairs (cluster.pairs + k - 1))
			        if oldpair.pc2 = newpair.pc2 then
				    alreadyhaveit := true
			        end if
				exit when alreadyhaveit
			    end for
			
			    % if not, we need to add this pair to expore its clones
			    if not alreadyhaveit then
			        cluster.npairs += 1
			        nclusterpairs += 1
			        clusterpairs (nclusterpairs) := j
			    end if
			end if
		    end for
		end if

		cp += 1
	    end loop

	    % We have a minimum set of pairs, but individual pcs can appear in more than one clone pair.
	    % Blank copies out to yeild the set of unique pcs in the cluster
	    cp := cluster.pairs
	    loop
		exit when cp > nclusterpairs

		bind pcp to pairs (clusterpairs (cp))

		for ccp: cp + 1 .. nclusterpairs
		    bind var pccp to pairs (clusterpairs (ccp))
		    if pccp.pc1 = pcp.pc1 or pccp.pc1 = pcp.pc2 then
			pccp.pc1 := 0
		    end if
		    if pccp.pc2 = pcp.pc1 or pccp.pc2 = pcp.pc2 then
			pccp.pc2 := 0
		    end if
		end for

		cp += 1
	    end loop
	end if
    end for
end clusterclonepairs


% Generate XML output of our result

procedure showclusters
    % System information
    put "<clones>"
    put linetable.gettext (systeminfo)
    put linetable.gettext (cloneinfo)
    put linetable.gettext (runinfo)
    put "<classinfo nclasses=\"", nclusters, "\"/>"
    put ""

    for i : 1 .. nclusters
	% Indicate progress
	if i mod 100 = 1 then
	    put : 0, "." ..
	end if

	bind cl to clusters (i)
	var nclones := 0
	var similarity := 100
	var nlines := 0

	for j : 1 .. cl.npairs
	    bind cp to pairs (clusterpairs (cl.pairs + j))
	    if cp.pc1 not= 0 then
		nclones += 1
	        nlines += cp.nlines
	    end if
	    if cp.pc2 not= 0 then
		nclones += 1
	        nlines += cp.nlines
	    end if
	    if cp.similarity < similarity then
		similarity := cp.similarity
	    end if
	end for
	nlines := nlines div nclones

	put "<class classid=\"", i, "\" nclones=\"", nclones, "\" nlines=\"", nlines, "\" similarity=\"", similarity, "\">"

	for j : 1 .. cl.npairs
	    bind cp to pairs (clusterpairs (cl.pairs + j))
	    if cp.pc1 not= 0 then
		put linetable.gettext (cp.pc1info)
	    end if
	    if cp.pc2 not= 0 then
		put linetable.gettext (cp.pc2info)
	    end if
	end for

	put "</class>"
	put ""
    end for 
    put "</clones>"
end showclusters


% Proces program arguments

procedure getprogramarguments
    % Check usage
    if nargs not= 1 then
	useerr
    end if
    % Name of the extracted pc XML file
    cpfile := fetcharg(1)
end getprogramarguments


% Main program

% Get program arguments
getprogramarguments

% Steps of the process
put : 0, "Processing ", cpfile

put : 0, "Reading clone pairs " ..
readclonepairs
put : 0, " done."
put : 0, "Total ", npairs div 2, " pairs"  % (sic) - we save commutative versions of each pair

put : 0, "Sorting pairs " ..
quicksortclonepairs (1,npairs)
put : 0, " done."

put : 0, "Indexing pairs " ..
indexpairs
put : 0, " done."

put : 0, "Computing classes " ..
clusterclonepairs
put : 0, " done."

put : 0, "Clustered clone pairs into ", nclusters, " classes"

put : 0, "Generating XML output " ..
showclusters
put : 0, " done."
put : 0, ""

