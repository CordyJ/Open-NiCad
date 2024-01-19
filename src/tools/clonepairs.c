#include <UNIX64/cinterface.h>
extern TLint4	TL_TLI_TLIARC;

extern void TL_TLI_TLIFA ();

extern void TL_TLX_TLXGE ();

extern void TL_TLX_TLXDT ();

extern void TL_TLX_TLXTM ();

extern void TL_TLX_TLXCL ();

extern void TL_TLX_TLXSC ();

extern void time ();

extern void TL_TLX_TLXSYS ();

extern TLint4 getpid ();

extern void TL_TLI_TLIFS ();

extern void TL_TLK_TLKUEXIT ();
extern TLnat4	TL_TLK_TLKTIME;
extern TLnat4	TL_TLK_TLKEPOCH;

extern void TL_TLK_TLKUDMPA ();

extern void TL_TLK_TLKCINI ();
extern TLboolean	TL_TLK_TLKCLKON;
extern TLnat4	TL_TLK_TLKHZ;
extern TLnat4	TL_TLK_TLKCRESO;
extern TLnat4	TL_TLK_TLKTIME;
extern TLnat4	TL_TLK_TLKEPOCH;

extern void TL_TLK_TLKPSID ();

extern TLnat4 TL_TLK_TLKPGID ();

extern void TL_TLK_TLKRSETP ();
static TLstring	pcfile;
static TLreal8	threshold;
static TLint4	minclonelines;
static TLint4	maxclonelines;
static TLboolean	showsource;

static void useerr () {
    TL_TLI_TLISS ((TLint4) 0, (TLint2) 2);
    TL_TLI_TLIPS ((TLint4) 0, "Usage :  clonepairs.x pcfile.xml [ threshold ] [ minclonesize ] [ maxclonesize ] [ showsource ] > clone-pairs-file.xml", (TLint2) 0);
    TL_TLI_TLIPK ((TLint2) 0);
    TL_TLI_TLISS ((TLint4) 0, (TLint2) 2);
    TL_TLI_TLIPS ((TLint4) 0, "", (TLint2) 0);
    TL_TLI_TLIPK ((TLint2) 0);
    TL_TLI_TLISS ((TLint4) 0, (TLint2) 2);
    TL_TLI_TLIPS ((TLint4) 0, "  e.g.:  clonepairs.x linux_functions.xml 0.2 > linux_functions-clones.xml", (TLint2) 0);
    TL_TLI_TLIPK ((TLint2) 0);
    TL_TLI_TLISS ((TLint4) 0, (TLint2) 2);
    TL_TLI_TLIPS ((TLint4) 0, "", (TLint2) 0);
    TL_TLI_TLIPK ((TLint2) 0);
    TL_TLI_TLISS ((TLint4) 0, (TLint2) 2);
    TL_TLI_TLIPS ((TLint4) 0, "    threshold = difference threshold, 0.0 .. 0.9 (optional, default 0.0 (exact))", (TLint2) 0);
    TL_TLI_TLIPK ((TLint2) 0);
    TL_TLI_TLISS ((TLint4) 0, (TLint2) 2);
    TL_TLI_TLIPS ((TLint4) 0, "    minclonesize = minimum clone size (optional, default 5 lines)", (TLint2) 0);
    TL_TLI_TLIPK ((TLint2) 0);
    TL_TLI_TLISS ((TLint4) 0, (TLint2) 2);
    TL_TLI_TLIPS ((TLint4) 0, "    maxclonesize = maximum clone size (optional, default 2500 lines, max 20000 lines)", (TLint2) 0);
    TL_TLI_TLIPK ((TLint2) 0);
    TL_TLI_TLISS ((TLint4) 0, (TLint2) 2);
    TL_TLI_TLIPS ((TLint4) 0, "    showsource = embed pc source in results (optional, argument present = yes, default no)", (TLint2) 0);
    TL_TLI_TLIPK ((TLint2) 0);
    TL_TLE_TLEQUIT ((TLint4) 1, (char *) 0, 0);
}

static void getprogramarguments ();
typedef	TLchar	linetable___x224[600000001];
static linetable___x224	linetable_lineText;
static TLint4	linetable_lineTextSize;
typedef	TLint4	linetable___x227[12000000];
static linetable___x227	linetable_lineTable;
static TLint4	linetable_lineTableSize;
typedef	TLnat4	linetable_LN;

static TLnat4 linetable_hash (s)
TLstring	s;
{
    typedef	TLnat1	__x231[256];
    typedef	__x231	nat256;
    register TLnat4	h;
    register TLnat4	j;
    h = TL_TLS_TLSLEN(s);
    if (h > 255) {
	h = 255;
    };
    j = h - 1;
    if (h > 0) {
	{
	    register TLint4	i;
	    TLint4	__x233;
	    __x233 = h >> 1;
	    i = 0;
	    if (i <= __x233) {
		for(;;) {
		    h += ((TLint4) h << 1) + ((* (nat256 *) s)[i]);
		    h += ((TLint4) h << 1) + ((* (nat256 *) s)[j]);
		    j -= 1;
		    if (i == __x233) break;
		    i++;
		}
	    };
	};
    };
    return (h);
    /* NOTREACHED */
}
static TLint4	linetable_secondaryHash;
typedef	TLint4	linetable___x238[10];
static linetable___x238	linetable_primes = 
    {1021, 2027, 4091, 8191, 16381, 32003, 65003, 131009, 262007, 524047};
typedef	TLboolean	linetable___x242[256];
static linetable___x242	linetable_spaceP;

static void linetable_strip (rawline, __x82)
TLstring	rawline;
TLstring	__x82;
{
    TLstring	line;
    TLint4	rawlinelength;
    TLint4	first;
    TLint4	last;
    TLSTRASS(4095, line, rawline);
    rawlinelength = TL_TLS_TLSLEN(rawline);
    first = 1;
    for(;;) {
	{
	    TLchar	__x246[2];
	    if ((first > rawlinelength) || ((TL_TLS_TLSBX(__x246, (TLint4) first, line), !(linetable_spaceP[((TLnat4) TLCVTTOCHR(__x246))])))) {
		break;
	    };
	};
	first += 1;
    };
    last = rawlinelength;
    for(;;) {
	{
	    TLchar	__x247[2];
	    if ((last < first) || ((TL_TLS_TLSBX(__x247, (TLint4) last, line), !(linetable_spaceP[((TLnat4) TLCVTTOCHR(__x247))])))) {
		break;
	    };
	};
	last -= 1;
    };
    {
	TLstring	__x248;
	TL_TLS_TLSBXX(__x248, (TLint4) last, (TLint4) first, line);
	TLSTRASS(4095, line, __x248);
    };
    {
	TLSTRASS(4095, __x82, line);
	return;
    };
    /* NOTREACHED */
}

static linetable_LN linetable_install (line)
TLstring	line;
{
    TLnat4	lineIndex;
    TLnat4	startIndex;
    TLint4	linelength;
    lineIndex = linetable_hash(line);
    if (lineIndex >= 12000000) {
	lineIndex = lineIndex % 12000000;
    };
    startIndex = lineIndex;
    linelength = TL_TLS_TLSLEN(line);
    for(;;) {
	if ((linetable_lineTable[lineIndex]) == 0) {
	    if (((linetable_lineTextSize + linelength) + 1) > 600000000) {
		TL_TLI_TLISS ((TLint4) 0, (TLint2) 2);
		TL_TLI_TLIPS ((TLint4) 0, "*** Error: too much total unique line text ( > ", (TLint2) 0);
		TL_TLI_TLIPI ((TLint4) 0, (TLint4) 600000000, (TLint2) 0);
		TL_TLI_TLIPS ((TLint4) 0, " chars)", (TLint2) 0);
		TL_TLI_TLIPK ((TLint2) 0);
		TL_TLE_TLEQUIT ((TLint4) 1, (char *) 0, 0);
	    };
	    TLSTRASS(4095, (* (TLstring *) &linetable_lineText[linetable_lineTextSize - 1]), line);
	    linetable_lineTable[lineIndex] = linetable_lineTextSize;
	    linetable_lineTextSize += linelength + 1;
	    linetable_lineTableSize += 1;
	    break;
	};
	if (strcmp((* (TLstring *) &linetable_lineText[(linetable_lineTable[lineIndex]) - 1]), line) == 0) {
	    break;
	};
	lineIndex += linetable_secondaryHash;
	if (lineIndex >= 12000000) {
	    lineIndex = lineIndex % 12000000;
	};
	if (lineIndex == startIndex) {
	    TL_TLI_TLISS ((TLint4) 0, (TLint2) 2);
	    TL_TLI_TLIPS ((TLint4) 0, "*** Error: too many unique lines ( > ", (TLint2) 0);
	    TL_TLI_TLIPI ((TLint4) 0, (TLint4) 12000000, (TLint2) 0);
	    TL_TLI_TLIPS ((TLint4) 0, ")", (TLint2) 0);
	    TL_TLI_TLIPK ((TLint2) 0);
	    TL_TLE_TLEQUIT ((TLint4) 1, (char *) 0, 0);
	};
    };
    return (lineIndex);
    /* NOTREACHED */
}

static void linetable_gettext (lineIndex, __x93)
linetable_LN	lineIndex;
TLstring	__x93;
{
    {
	TLSTRASS(4095, __x93, (* (TLstring *) &linetable_lineText[(linetable_lineTable[lineIndex]) - 1]));
	return;
    };
    /* NOTREACHED */
}

static void linetable_printstats () {
    TL_TLI_TLISS ((TLint4) 0, (TLint2) 2);
    TL_TLI_TLIPS ((TLint4) 0, "Used ", (TLint2) 0);
    TL_TLI_TLIPI ((TLint4) 0, (TLint4) linetable_lineTextSize, (TLint2) 0);
    TL_TLI_TLIPS ((TLint4) 0, "/", (TLint2) 0);
    TL_TLI_TLIPI ((TLint4) 0, (TLint4) 600000000, (TLint2) 0);
    TL_TLI_TLIPS ((TLint4) 0, " unique line text chars", (TLint2) 0);
    TL_TLI_TLIPK ((TLint2) 0);
    TL_TLI_TLISS ((TLint4) 0, (TLint2) 2);
    TL_TLI_TLIPS ((TLint4) 0, " and ", (TLint2) 0);
    TL_TLI_TLIPI ((TLint4) 0, (TLint4) linetable_lineTableSize, (TLint2) 0);
    TL_TLI_TLIPS ((TLint4) 0, "/", (TLint2) 0);
    TL_TLI_TLIPI ((TLint4) 0, (TLint4) 12000000, (TLint2) 0);
    TL_TLI_TLIPS ((TLint4) 0, " unique lines", (TLint2) 0);
    TL_TLI_TLIPK ((TLint2) 0);
}

static void linetable () {
    linetable_lineTextSize = 1;
    linetable_lineTableSize = 0;
    {
	register TLint4	i;
	for (i = 0; i <= 11999999; i++) {
	    linetable_lineTable[i] = 0;
	};
    };
    TLSTRASS(4095, (* (TLstring *) &linetable_lineText[0]), " ");
    linetable_lineTextSize += 2;
    linetable_lineTable[0] = 2;
    linetable_lineTableSize = 1;
    linetable_secondaryHash = 11;
    {
	register TLint4	i;
	for (i = 1; i <= 10; i++) {
	    if ((i == 10) || ((linetable_primes[i - 1]) > 12000000)) {
		break;
	    };
	    linetable_secondaryHash = linetable_primes[i - 1];
	};
    };
    {
	register TLint4	c;
	for (c = 0; c <= 255; c++) {
	    linetable_spaceP[c] = 0;
	};
    };
    linetable_spaceP[32] = 1;
    linetable_spaceP[9] = 1;
    linetable_spaceP[12] = 1;
}
struct	PC {
    TLint4	num;
    linetable_LN	info;
    linetable_LN	srcfile;
    TLint4	srcstartline, srcendline;
    TLint4	firstline;
    TLint4	nlines;
    TLint4	nomlines;
    TLint4	embedding;
};
typedef	struct PC	__x253[6000000];
static __x253	pcs;
static TLint4	npcs;
typedef	linetable_LN	__x254[100000000];
static __x254	lines;
static TLint4	nlines;
struct	CP {
    TLint4	pc1, pc2;
    TLint4	nlines;
    TLint1	similarity;
};
typedef	struct CP	__x255[20000000];
static __x255	clonepairs;
static TLint4	npairs;
static TLint4	ncompares;
static TLint4	nclones;
static TLint4	nfragments;

static void readpcs () {
    TLint4	pcf;
    TL_TLI_TLIOF ((TLnat2) 2, pcfile, &pcf);
    if (pcf == 0) {
	useerr();
    };
    {
	register TLint4	i;
	for (i = 1; i <= 6000000; i++) {
	    TLBIND((*pc), struct PC);
	    TLstring	sourceheader;
	    TLint4	sfindex;
	    TLint4	sfend;
	    TLint4	slindex;
	    TLint4	slend;
	    TLint4	elindex;
	    TLint4	elend;
	    TLint4	nomlines;
	    if ((i % 1000) == 1) {
		TL_TLI_TLISS ((TLint4) 0, (TLint2) 2);
		TL_TLI_TLIPS ((TLint4) 0, ".", (TLint2) 0);
	    };
	    if (TL_TLI_TLIEOF((TLint4) pcf)) {
		break;
	    };
	    npcs += 1;
	    pc = &(pcs[npcs - 1]);
	    (*pc).num = i;
	    (*pc).embedding = 0;
	    TL_TLI_TLISS ((TLint4) pcf, (TLint2) 1);
	    TL_TLI_TLIGSS((TLint4) 4095, sourceheader, (TLint2) pcf);
	    (*pc).info = linetable_install(sourceheader);
	    if (TL_TLS_TLSIND(sourceheader, "<source ") != 1) {
		TL_TLI_TLISS ((TLint4) 0, (TLint2) 2);
		TL_TLI_TLIPS ((TLint4) 0, "*** Error: synchronization error on pc file", (TLint2) 0);
		TL_TLI_TLIPK ((TLint2) 0);
		TL_TLE_TLEQUIT ((TLint4) 1, (char *) 0, 0);
	    };
	    sfindex = (TL_TLS_TLSIND(sourceheader, "file=") + TL_TLS_TLSLEN("file=")) + 1;
	    sfend = TL_TLS_TLSIND(sourceheader, " startline=") - 2;
	    {
		TLstring	__x256;
		TL_TLS_TLSBXX(__x256, (TLint4) sfend, (TLint4) sfindex, sourceheader);
		(*pc).srcfile = linetable_install(__x256);
	    };
	    slindex = (TL_TLS_TLSIND(sourceheader, "startline=") + TL_TLS_TLSLEN("startline=")) + 1;
	    slend = TL_TLS_TLSIND(sourceheader, " endline=") - 2;
	    {
		TLstring	__x257;
		TL_TLS_TLSBXX(__x257, (TLint4) slend, (TLint4) slindex, sourceheader);
		(*pc).srcstartline = TL_TLS_TLSVSI(__x257, (TLint4) 10);
	    };
	    elindex = (TL_TLS_TLSIND(sourceheader, "endline=") + TL_TLS_TLSLEN("endline=")) + 1;
	    elend = TL_TLS_TLSLEN(sourceheader) - 2;
	    {
		TLstring	__x258;
		TL_TLS_TLSBXX(__x258, (TLint4) elend, (TLint4) elindex, sourceheader);
		(*pc).srcendline = TL_TLS_TLSVSI(__x258, (TLint4) 10);
	    };
	    (*pc).firstline = nlines;
	    nomlines = 0;
	    for(;;) {
		TLstring	line;
		if (TL_TLI_TLIEOF((TLint4) pcf)) {
		    TL_TLI_TLISS ((TLint4) 0, (TLint2) 2);
		    TL_TLI_TLIPS ((TLint4) 0, "*** Error: synchronization error on pc file", (TLint2) 0);
		    TL_TLI_TLIPK ((TLint2) 0);
		    TL_TLE_TLEQUIT ((TLint4) 1, (char *) 0, 0);
		};
		TL_TLI_TLISS ((TLint4) pcf, (TLint2) 1);
		TL_TLI_TLIGSS((TLint4) 4095, line, (TLint2) pcf);
		if (strcmp(line, "</source>") == 0) {
		    break;
		};
		{
		    TLstring	__x259;
		    linetable_strip(line, __x259);
		    TLSTRASS(4095, line, __x259);
		};
		if (((strcmp(line, "") != 0) && (strcmp(line, "INDENT") != 0)) && (strcmp(line, "DEDENT") != 0)) {
		    nomlines += 1;
		    if (strcmp(line, "}") != 0) {
			nlines += 1;
			if (nlines > 100000000) {
			    TL_TLI_TLISS ((TLint4) 0, (TLint2) 2);
			    TL_TLI_TLIPS ((TLint4) 0, "*** Error: too many total lines ( > ", (TLint2) 0);
			    TL_TLI_TLIPI ((TLint4) 0, (TLint4) 100000000, (TLint2) 0);
			    TL_TLI_TLIPS ((TLint4) 0, ")", (TLint2) 0);
			    TL_TLI_TLIPK ((TLint2) 0);
			    TL_TLE_TLEQUIT ((TLint4) 1, (char *) 0, 0);
			};
			lines[nlines - 1] = linetable_install(line);
		    };
		};
	    };
	    (*pc).nlines = nlines - ((*pc).firstline);
	    (*pc).nomlines = nomlines;
	    if ((nomlines < minclonelines) || (nomlines > maxclonelines)) {
		(*pc).nlines = 0;
		(*pc).nomlines = 0;
		nlines = (*pc).firstline;
	    };
	};
    };
    if (!TL_TLI_TLIEOF((TLint4) pcf)) {
	TL_TLI_TLISS ((TLint4) 0, (TLint2) 2);
	TL_TLI_TLIPS ((TLint4) 0, "*** Error: too many potential clones ( > ", (TLint2) 0);
	TL_TLI_TLIPI ((TLint4) 0, (TLint4) 6000000, (TLint2) 0);
	TL_TLI_TLIPS ((TLint4) 0, ")", (TLint2) 0);
	TL_TLI_TLIPK ((TLint2) 0);
    };
    TL_TLI_TLICL ((TLint4) pcf);
}

static void swappcs (i, j)
TLint4	i;
TLint4	j;
{
    struct PC	t;
    TLSTRCTASS(t, pcs[i - 1], struct PC);
    TLSTRCTASS(pcs[i - 1], pcs[j - 1], struct PC);
    TLSTRCTASS(pcs[j - 1], t, struct PC);
}
static TLint4	depth;

static void sortpcs (first, last)
TLint4	first;
TLint4	last;
{
    depth = depth + 1;
    if ((depth % 1000) == 1) {
	TL_TLI_TLISS ((TLint4) 0, (TLint2) 2);
	TL_TLI_TLIPS ((TLint4) 0, ".", (TLint2) 0);
    };
    if (first < last) {
	TLint4	low;
	TLint4	high;
	TLint4	pivot;
	low = first;
	high = last + 1;
	pivot = low;
	for(;;) {
	    for(;;) {
		high -= 1;
		if (low == high) {
		    break;
		};
		if ((pcs[high - 1].nlines) > (pcs[pivot - 1].nlines)) {
		    break;
		};
	    };
	    if (low == high) {
		break;
	    };
	    for(;;) {
		low += 1;
		if (low == high) {
		    break;
		};
		if ((pcs[pivot - 1].nlines) > (pcs[low - 1].nlines)) {
		    break;
		};
	    };
	    if (low == high) {
		break;
	    };
	    swappcs((TLint4) low, (TLint4) high);
	};
	swappcs((TLint4) high, (TLint4) pivot);
	sortpcs((TLint4) first, (TLint4) (high - 1));
	sortpcs((TLint4) (high + 1), (TLint4) last);
    };
    depth = depth - 1;
}
static TLnat2	*dpmatrix;
static TLint4	__x260;

static TLint4 lcs (pc1, pc2, m, n, difflimit)
struct PC	*pc1;
struct PC	*pc2;
TLint4	m;
TLint4	n;
TLint4	difflimit;
{
    TLint4	bi;
    {
	register TLint4	i;
	for (i = 0; i <= 1; i++) {
	    dpmatrix[((0) + __x260 * (i))] = 0;
	};
    };
    {
	register TLint4	j;
	TLint4	__x262;
	__x262 = n;
	j = 0;
	if (j <= __x262) {
	    for(;;) {
		dpmatrix[((j) + __x260 * (0))] = 0;
		if (j == __x262) break;
		j++;
	    }
	};
    };
    bi = 0;
    {
	register TLint4	i;
	TLint4	__x263;
	__x263 = m;
	i = 1;
	if (i <= __x263) {
	    for(;;) {
		bi = i % 2;
		{
		    register TLint4	j;
		    TLint4	__x264;
		    __x264 = n;
		    j = 1;
		    if (j <= __x264) {
			for(;;) {
			    if ((lines[(((*pc1).firstline) + i) - 1]) == (lines[(((*pc2).firstline) + j) - 1])) {
				dpmatrix[((j) + __x260 * (bi))] = (dpmatrix[((j - 1) + __x260 * (1 - bi))]) + 1;
			    } else {
				if ((dpmatrix[((j) + __x260 * (1 - bi))]) >= (dpmatrix[((j - 1) + __x260 * (bi))])) {
				    dpmatrix[((j) + __x260 * (bi))] = dpmatrix[((j) + __x260 * (1 - bi))];
				} else {
				    dpmatrix[((j) + __x260 * (bi))] = dpmatrix[((j - 1) + __x260 * (bi))];
				};
			    };
			    if (j == __x264) break;
			    j++;
			}
		    };
		};
		if ((i - (dpmatrix[((n) + __x260 * (bi))])) > difflimit) {
		    return (0);
		};
		if (i == __x263) break;
		i++;
	    }
	};
    };
    return (dpmatrix[((n) + __x260 * (bi))]);
    /* NOTREACHED */
}

static TLboolean exact (pc1, pc2)
struct PC	*pc1;
struct PC	*pc2;
{
    {
	register TLint4	i;
	TLint4	__x265;
	__x265 = (*pc1).nlines;
	i = 1;
	if (i <= __x265) {
	    for(;;) {
		if ((lines[(((*pc1).firstline) + i) - 1]) != (lines[(((*pc2).firstline) + i) - 1])) {
		    return (0);
		};
		if (i == __x265) break;
		i++;
	    }
	};
    };
    return (1);
    /* NOTREACHED */
}

static TLint4 nearmiss (pc1, pc2)
struct PC	*pc1;
struct PC	*pc2;
{
    TLint4	difflimit;
    TLint4	pc1pc2lcs;
    if (((((*pc2).srcfile) == ((*pc1).srcfile)) && (((*pc2).srcstartline) >= ((*pc1).srcstartline))) && (((*pc2).srcendline) <= ((*pc1).srcendline))) {
	return (0);
    };
    difflimit = TL_TLA_TLA8RD((TLreal8) ((((*pc1).nlines) * threshold) + 0.000001));
    pc1pc2lcs = lcs(&((*pc1)), &((*pc2)), (TLint4) ((*pc1).nlines), (TLint4) ((*pc2).nlines), (TLint4) difflimit);
    if (((((TLreal8) (((*pc1).nlines) - pc1pc2lcs))  / ((TLreal8) ((*pc1).nlines))) <= (threshold + 0.000001)) && ((((TLreal8) (((*pc2).nlines) - pc1pc2lcs))  / ((TLreal8) ((*pc2).nlines))) <= (threshold + 0.000001))) {
	return (TL_TLA_TLA8RD((TLreal8) (((((TLreal8) pc1pc2lcs)  / ((TLreal8) ((*pc1).nlines))) * 100) + 0.000001)));
    } else {
	return (0);
    };
    /* NOTREACHED */
}

static TLint4 clone (pc1, pc2, threshold)
struct PC	*pc1;
struct PC	*pc2;
TLreal8	threshold;
{
    ncompares += 1;
    if ((threshold + 0.000001) < 0.01) {
	if (exact(&((*pc1)), &((*pc2)))) {
	    nclones += 1;
	    nfragments += 1;
	    return (100);
	};
    } else {
	TLint4	sameness;
	sameness = nearmiss(&((*pc1)), &((*pc2)));
	if ((100 - sameness) <= TL_TLA_TLA8RD((TLreal8) ((threshold * 100) + 0.000001))) {
	    nclones += 1;
	    nfragments += 1;
	    return (sameness);
	};
    };
    return (0);
    /* NOTREACHED */
}

static void findclones () {
    {
	register TLint4	i;
	TLint4	__x266;
	__x266 = npcs;
	i = 1;
	if (i <= __x266) {
	    for(;;) {
		if ((i % 1000) == 0) {
		    TL_TLI_TLISS ((TLint4) 0, (TLint2) 2);
		    TL_TLI_TLIPS ((TLint4) 0, ".", (TLint2) 0);
		};
		if ((pcs[i - 1].nlines) != 0) {
		    TLint4	difflimit;
		    difflimit = TL_TLA_TLA8RD((TLreal8) (((pcs[i - 1].nlines) * threshold) + 0.000001));
		    {
			register TLint4	j;
			TLint4	__x267;
			__x267 = npcs;
			j = i + 1;
			if (j <= __x267) {
			    for(;;) {
				if ((pcs[j - 1].nlines) < ((pcs[i - 1].nlines) - difflimit)) {
				    break;
				};
				if ((pcs[j - 1].nlines) != 0) {
				    TLint4	similarity;
				    similarity = clone(&(pcs[i - 1]), &(pcs[j - 1]), (TLreal8) threshold);
				    if (similarity != 0) {
					TLBIND((*cp), struct CP);
					npairs += 1;
					if (npairs > 20000000) {
					    TL_TLI_TLISS ((TLint4) 0, (TLint2) 2);
					    TL_TLI_TLIPS ((TLint4) 0, "*** Error: too many clone pairs", (TLint2) 0);
					    TL_TLI_TLIPK ((TLint2) 0);
					    TL_TLE_TLEQUIT ((TLint4) 1, (char *) 0, 0);
					};
					cp = &(clonepairs[npairs - 1]);
					(*cp).pc1 = i;
					(*cp).pc2 = j;
					(*cp).similarity = similarity;
					(*cp).nlines = (((pcs[i - 1].nomlines) + (pcs[j - 1].nomlines)) + 1) / 2;
				    };
				};
				if (j == __x267) break;
				j++;
			    }
			};
		    };
		};
		if (i == __x266) break;
		i++;
	    }
	};
    };
}
typedef	TLint4	__x268[20000000];
static __x268	clonepairmap;

static void swapclonepairmap (i, j)
TLint4	i;
TLint4	j;
{
    TLint4	t;
    t = clonepairmap[i - 1];
    clonepairmap[i - 1] = clonepairmap[j - 1];
    clonepairmap[j - 1] = t;
}
static TLint4	cdepth;

static void sortclonepairmapbyfile (first, last)
TLint4	first;
TLint4	last;
{
    cdepth = cdepth + 1;
    if ((cdepth % 1000) == 1) {
	TL_TLI_TLISS ((TLint4) 0, (TLint2) 2);
	TL_TLI_TLIPS ((TLint4) 0, ".", (TLint2) 0);
    };
    if (first < last) {
	TLint4	low;
	TLint4	high;
	TLint4	pivot;
	low = first;
	high = last + 1;
	pivot = low;
	for(;;) {
	    for(;;) {
		high -= 1;
		if (low == high) {
		    break;
		};
		if (((pcs[(clonepairs[(clonepairmap[high - 1]) - 1].pc1) - 1].srcfile) > (pcs[(clonepairs[(clonepairmap[pivot - 1]) - 1].pc1) - 1].srcfile)) || (((pcs[(clonepairs[(clonepairmap[high - 1]) - 1].pc1) - 1].srcfile) == (pcs[(clonepairs[(clonepairmap[pivot - 1]) - 1].pc1) - 1].srcfile)) && ((clonepairs[(clonepairmap[high - 1]) - 1].nlines) > (clonepairs[(clonepairmap[pivot - 1]) - 1].nlines)))) {
		    break;
		};
	    };
	    if (low == high) {
		break;
	    };
	    for(;;) {
		low += 1;
		if (low == high) {
		    break;
		};
		if (((pcs[(clonepairs[(clonepairmap[pivot - 1]) - 1].pc1) - 1].srcfile) > (pcs[(clonepairs[(clonepairmap[low - 1]) - 1].pc1) - 1].srcfile)) || (((pcs[(clonepairs[(clonepairmap[pivot - 1]) - 1].pc1) - 1].srcfile) == (pcs[(clonepairs[(clonepairmap[low - 1]) - 1].pc1) - 1].srcfile)) && ((clonepairs[(clonepairmap[pivot - 1]) - 1].nlines) > (clonepairs[(clonepairmap[low - 1]) - 1].nlines)))) {
		    break;
		};
	    };
	    if (low == high) {
		break;
	    };
	    swapclonepairmap((TLint4) low, (TLint4) high);
	};
	swapclonepairmap((TLint4) high, (TLint4) pivot);
	sortclonepairmapbyfile((TLint4) first, (TLint4) (high - 1));
	sortclonepairmapbyfile((TLint4) (high + 1), (TLint4) last);
    };
    cdepth = cdepth - 1;
}

static void pruneembeddedpairs () {
    TLint4	embeddedpairs;
    TLint4	p;
    {
	register TLint4	i;
	TLint4	__x271;
	__x271 = npairs;
	i = 1;
	if (i <= __x271) {
	    for(;;) {
		if (((pcs[(clonepairs[i - 1].pc1) - 1].srcfile) > (pcs[(clonepairs[i - 1].pc2) - 1].srcfile)) || (((pcs[(clonepairs[i - 1].pc1) - 1].srcfile) == (pcs[(clonepairs[i - 1].pc2) - 1].srcfile)) && ((pcs[(clonepairs[i - 1].pc1) - 1].srcstartline) > (pcs[(clonepairs[i - 1].pc2) - 1].srcstartline)))) {
		    TLint4	opc1;
		    opc1 = clonepairs[i - 1].pc1;
		    clonepairs[i - 1].pc1 = clonepairs[i - 1].pc2;
		    clonepairs[i - 1].pc2 = opc1;
		};
		if (i == __x271) break;
		i++;
	    }
	};
    };
    {
	register TLint4	i;
	TLint4	__x272;
	__x272 = npairs;
	i = 1;
	if (i <= __x272) {
	    for(;;) {
		clonepairmap[i - 1] = i;
		if (i == __x272) break;
		i++;
	    }
	};
    };
    sortclonepairmapbyfile((TLint4) 1, (TLint4) npairs);
    embeddedpairs = 0;
    {
	register TLint4	i;
	for (i = npairs; i >= 1; i--) {
	    TLBIND((*pc1), struct PC);
	    TLBIND((*pc2), struct PC);
	    if ((i % 1000) == 1) {
		TL_TLI_TLISS ((TLint4) 0, (TLint2) 2);
		TL_TLI_TLIPS ((TLint4) 0, ".", (TLint2) 0);
	    };
	    pc1 = &(pcs[(clonepairs[(clonepairmap[i - 1]) - 1].pc1) - 1]);
	    pc2 = &(pcs[(clonepairs[(clonepairmap[i - 1]) - 1].pc2) - 1]);
	    {
		register TLint4	j;
		for (j = i - 1; j >= 1; j--) {
		    TLBIND((*bpc1), struct PC);
		    TLBIND((*bpc2), struct PC);
		    bpc1 = &(pcs[(clonepairs[(clonepairmap[j - 1]) - 1].pc1) - 1]);
		    bpc2 = &(pcs[(clonepairs[(clonepairmap[j - 1]) - 1].pc2) - 1]);
		    if (((*bpc1).srcfile) != ((*pc1).srcfile)) {
			break;
		    };
		    if ((((((*bpc1).srcfile) == ((*pc1).srcfile)) && (((*bpc2).srcfile) == ((*pc2).srcfile))) && ((((*bpc1).srcstartline) <= ((*pc1).srcstartline)) && (((*bpc1).srcendline) >= ((*pc1).srcendline)))) && ((((*bpc2).srcstartline) <= ((*pc2).srcstartline)) && (((*bpc2).srcendline) >= ((*pc2).srcendline)))) {
			embeddedpairs += 1;
			clonepairs[(clonepairmap[i - 1]) - 1].pc1 = 0;
			clonepairs[(clonepairmap[i - 1]) - 1].pc2 = 0;
			break;
		    };
		};
	    };
	};
    };
    npairs -= embeddedpairs;
    p = 1;
    {
	register TLint4	i;
	TLint4	__x273;
	__x273 = npairs;
	i = 1;
	if (i <= __x273) {
	    for(;;) {
		for(;;) {
		    if ((clonepairs[p - 1].pc1) != 0) {
			break;
		    };
		    p += 1;
		};
		TLSTRCTASS(clonepairs[i - 1], clonepairs[p - 1], struct CP);
		p += 1;
		if (i == __x273) break;
		i++;
	    }
	};
    };
}

static void showpairs () {
    TLint4	slashindex;
    TLstring	systeminfo;
    TLint4	usindex;
    TLstring	systemname;
    TLstring	granularity;

    extern TLint4 clock ();
    TLint4	cputime;
    slashindex = TL_TLS_TLSLEN(pcfile);
    for(;;) {
	TLchar	pcfchar;
	{
	    TLchar	__x274[2];
	    TL_TLS_TLSBX(__x274, (TLint4) slashindex, pcfile);
	    pcfchar = (* (TLchar *) __x274);
	};
	if ((slashindex == 0) || (pcfchar == '/')) {
	    break;
	};
	slashindex -= 1;
    };
    {
	TLstring	__x276;
	TL_TLS_TLSBXS(__x276, (TLint4) 0, (TLint4) (slashindex + 1), pcfile);
	TLSTRASS(4095, systeminfo, __x276);
    };
    usindex = TL_TLS_TLSLEN(systeminfo);
    for(;;) {
	TLchar	sichar;
	{
	    TLchar	__x277[2];
	    TL_TLS_TLSBX(__x277, (TLint4) usindex, systeminfo);
	    sichar = (* (TLchar *) __x277);
	};
	if ((usindex == 2) || (sichar == '_')) {
	    break;
	};
	usindex -= 1;
    };
    {
	TLstring	__x279;
	TL_TLS_TLSBXX(__x279, (TLint4) (usindex - 1), (TLint4) 1, systeminfo);
	TLSTRASS(4095, systemname, __x279);
    };
    {
	TLstring	__x280;
	TL_TLS_TLSBXX(__x280, (TLint4) (TL_TLS_TLSIND(systeminfo, ".xml") - 1), (TLint4) (usindex + 1), systeminfo);
	TLSTRASS(4095, granularity, __x280);
    };
    TL_TLI_TLISSO ();
    TL_TLI_TLIPS ((TLint4) 0, "<clones>", (TLint2) -1);
    TL_TLI_TLIPK ((TLint2) -1);
    TL_TLI_TLISSO ();
    TL_TLI_TLIPS ((TLint4) 0, "<systeminfo processor=\"nicad6\" system=\"", (TLint2) -1);
    TL_TLI_TLIPS ((TLint4) 0, systemname, (TLint2) -1);
    TL_TLI_TLIPS ((TLint4) 0, "\" granularity=\"", (TLint2) -1);
    TL_TLI_TLIPS ((TLint4) 0, granularity, (TLint2) -1);
    TL_TLI_TLIPS ((TLint4) 0, "\" threshold=\"", (TLint2) -1);
    TL_TLI_TLIPI ((TLint4) 0, (TLint4) TL_TLA_TLA8RD((TLreal8) ((threshold * 100) + 0.000001)), (TLint2) -1);
    TL_TLI_TLIPS ((TLint4) 0, "%\" minlines=\"", (TLint2) -1);
    TL_TLI_TLIPI ((TLint4) 0, (TLint4) minclonelines, (TLint2) -1);
    TL_TLI_TLIPS ((TLint4) 0, "\" maxlines=\"", (TLint2) -1);
    TL_TLI_TLIPI ((TLint4) 0, (TLint4) maxclonelines, (TLint2) -1);
    TL_TLI_TLIPS ((TLint4) 0, "\"/>", (TLint2) -1);
    TL_TLI_TLIPK ((TLint2) -1);
    TL_TLI_TLISSO ();
    TL_TLI_TLIPS ((TLint4) 0, "<cloneinfo npcs=\"", (TLint2) -1);
    TL_TLI_TLIPI ((TLint4) 0, (TLint4) npcs, (TLint2) -1);
    TL_TLI_TLIPS ((TLint4) 0, "\" npairs=\"", (TLint2) -1);
    TL_TLI_TLIPI ((TLint4) 0, (TLint4) npairs, (TLint2) -1);
    TL_TLI_TLIPS ((TLint4) 0, "\"/>", (TLint2) -1);
    TL_TLI_TLIPK ((TLint2) -1);
    cputime = clock();
    TL_TLI_TLISSO ();
    TL_TLI_TLIPS ((TLint4) 0, "<runinfo ncompares=\"", (TLint2) -1);
    TL_TLI_TLIPI ((TLint4) 0, (TLint4) ncompares, (TLint2) -1);
    TL_TLI_TLIPS ((TLint4) 0, "\" cputime=\"", (TLint2) -1);
    TL_TLI_TLIPI ((TLint4) 0, (TLint4) cputime, (TLint2) -1);
    TL_TLI_TLIPS ((TLint4) 0, "\"/>", (TLint2) -1);
    TL_TLI_TLIPK ((TLint2) -1);
    TL_TLI_TLISSO ();
    TL_TLI_TLIPS ((TLint4) 0, "", (TLint2) -1);
    TL_TLI_TLIPK ((TLint2) -1);
    {
	register TLint4	i;
	TLint4	__x281;
	__x281 = npairs;
	i = 1;
	if (i <= __x281) {
	    for(;;) {
		TLBIND((*cp), struct CP);
		TLBIND((*pc1), struct PC);
		TLBIND((*pc2), struct PC);
		if ((i % 1000) == 1) {
		    TL_TLI_TLISS ((TLint4) 0, (TLint2) 2);
		    TL_TLI_TLIPS ((TLint4) 0, ".", (TLint2) 0);
		};
		cp = &(clonepairs[i - 1]);
		TL_TLI_TLISSO ();
		TL_TLI_TLIPS ((TLint4) 0, "<clone nlines=\"", (TLint2) -1);
		TL_TLI_TLIPI ((TLint4) 0, (TLint4) ((*cp).nlines), (TLint2) -1);
		TL_TLI_TLIPS ((TLint4) 0, "\" similarity=\"", (TLint2) -1);
		TL_TLI_TLIPI ((TLint4) 0, (TLint4) ((*cp).similarity), (TLint2) -1);
		TL_TLI_TLIPS ((TLint4) 0, "\">", (TLint2) -1);
		TL_TLI_TLIPK ((TLint2) -1);
		pc1 = &(pcs[((*cp).pc1) - 1]);
		pc2 = &(pcs[((*cp).pc2) - 1]);
		{
		    TLstring	__x283;
		    linetable_gettext((linetable_LN) ((*pc1).info), __x283);
		    {
			TLstring	__x282;
			TL_TLS_TLSBXS(__x282, (TLint4) -1, (TLint4) 1, __x283);
			TL_TLI_TLISSO ();
			TL_TLI_TLIPS ((TLint4) 0, __x282, (TLint2) -1);
			TL_TLI_TLIPS ((TLint4) 0, " pcid=\"", (TLint2) -1);
			TL_TLI_TLIPI ((TLint4) 0, (TLint4) ((*pc1).num), (TLint2) -1);
			TL_TLI_TLIPS ((TLint4) 0, "\">", (TLint2) -1);
		    };
		};
		if (showsource) {
		    TL_TLI_TLISSO ();
		    TL_TLI_TLIPS ((TLint4) 0, "", (TLint2) -1);
		    TL_TLI_TLIPK ((TLint2) -1);
		    {
			register TLint4	k;
			TLint4	__x284;
			__x284 = (*pc1).nlines;
			k = 1;
			if (k <= __x284) {
			    for(;;) {
				{
				    TLstring	__x285;
				    linetable_gettext((linetable_LN) (lines[(((*pc1).firstline) + k) - 1]), __x285);
				    TL_TLI_TLISSO ();
				    TL_TLI_TLIPS ((TLint4) 0, __x285, (TLint2) -1);
				    TL_TLI_TLIPK ((TLint2) -1);
				};
				if (k == __x284) break;
				k++;
			    }
			};
		    };
		};
		TL_TLI_TLISSO ();
		TL_TLI_TLIPS ((TLint4) 0, "</source>", (TLint2) -1);
		TL_TLI_TLIPK ((TLint2) -1);
		{
		    TLstring	__x287;
		    linetable_gettext((linetable_LN) ((*pc2).info), __x287);
		    {
			TLstring	__x286;
			TL_TLS_TLSBXS(__x286, (TLint4) -1, (TLint4) 1, __x287);
			TL_TLI_TLISSO ();
			TL_TLI_TLIPS ((TLint4) 0, __x286, (TLint2) -1);
			TL_TLI_TLIPS ((TLint4) 0, " pcid=\"", (TLint2) -1);
			TL_TLI_TLIPI ((TLint4) 0, (TLint4) ((*pc2).num), (TLint2) -1);
			TL_TLI_TLIPS ((TLint4) 0, "\">", (TLint2) -1);
		    };
		};
		if (showsource) {
		    TL_TLI_TLISSO ();
		    TL_TLI_TLIPS ((TLint4) 0, "", (TLint2) -1);
		    TL_TLI_TLIPK ((TLint2) -1);
		    {
			register TLint4	k;
			TLint4	__x288;
			__x288 = (*pc2).nlines;
			k = 1;
			if (k <= __x288) {
			    for(;;) {
				{
				    TLstring	__x289;
				    linetable_gettext((linetable_LN) (lines[(((*pc2).firstline) + k) - 1]), __x289);
				    TL_TLI_TLISSO ();
				    TL_TLI_TLIPS ((TLint4) 0, __x289, (TLint2) -1);
				    TL_TLI_TLIPK ((TLint2) -1);
				};
				if (k == __x288) break;
				k++;
			    }
			};
		    };
		};
		TL_TLI_TLISSO ();
		TL_TLI_TLIPS ((TLint4) 0, "</source>", (TLint2) -1);
		TL_TLI_TLIPK ((TLint2) -1);
		TL_TLI_TLISSO ();
		TL_TLI_TLIPS ((TLint4) 0, "</clone>", (TLint2) -1);
		TL_TLI_TLIPK ((TLint2) -1);
		TL_TLI_TLISSO ();
		TL_TLI_TLIPS ((TLint4) 0, "", (TLint2) -1);
		TL_TLI_TLIPK ((TLint2) -1);
		if (i == __x281) break;
		i++;
	    }
	};
    };
    TL_TLI_TLISSO ();
    TL_TLI_TLIPS ((TLint4) 0, "</clones>", (TLint2) -1);
    TL_TLI_TLIPK ((TLint2) -1);
}

static void getprogramarguments () {
    if (TL_TLI_TLIARC < 1) {
	useerr();
    };
    {
	TLstring	__x290;
	TL_TLI_TLIFA((TLint4) 1, __x290);
	TLSTRASS(4095, pcfile, __x290);
    };
    if (TL_TLI_TLIARC > 1) {
	{
	    TLstring	__x291;
	    TL_TLI_TLIFA((TLint4) 2, __x291);
	    threshold = TL_TLS_TLSVS8(__x291);
	};
	if ((threshold < 0.0) || (threshold > 1.0)) {
	    useerr();
	};
    };
    if (TL_TLI_TLIARC > 2) {
	{
	    TLstring	__x292;
	    TL_TLI_TLIFA((TLint4) 3, __x292);
	    minclonelines = TL_TLS_TLSVSI(__x292, (TLint4) 10);
	};
	if ((minclonelines < 1) || (minclonelines > 100)) {
	    useerr();
	};
    };
    if (TL_TLI_TLIARC > 3) {
	{
	    TLstring	__x293;
	    TL_TLI_TLIFA((TLint4) 4, __x293);
	    maxclonelines = TL_TLS_TLSVSI(__x293, (TLint4) 10);
	};
	if ((maxclonelines < minclonelines) || (maxclonelines > 20000)) {
	    useerr();
	};
    };
    if (TL_TLI_TLIARC > 4) {
	showsource = 1;
    };
}
static TLint4	oldnpairs;
void TProg () {
    threshold = 0.0;
    minclonelines = 5;
    maxclonelines = 2500;
    showsource = 0;
    getprogramarguments();
    linetable();
    npcs = 0;
    nlines = 0;
    npairs = 0;
    ncompares = 0;
    nclones = 0;
    nfragments = 0;
    depth = 0;
    __x260 = TLDYN(maxclonelines - -1);
    TL_TLB_TLBALL((TLint4) 2 * (__x260 * 2), &dpmatrix);
    cdepth = 0;
    TL_TLI_TLISS ((TLint4) 0, (TLint2) 2);
    TL_TLI_TLIPS ((TLint4) 0, "Processing ", (TLint2) 0);
    TL_TLI_TLIPS ((TLint4) 0, pcfile, (TLint2) 0);
    TL_TLI_TLIPS ((TLint4) 0, " with difference threshold ", (TLint2) 0);
    TL_TLI_TLIPI ((TLint4) 0, (TLint4) TL_TLA_TLA8RD((TLreal8) ((threshold * 100) + 0.000001)), (TLint2) 0);
    TL_TLI_TLIPS ((TLint4) 0, "%, clone size ", (TLint2) 0);
    TL_TLI_TLIPI ((TLint4) 0, (TLint4) minclonelines, (TLint2) 0);
    TL_TLI_TLIPS ((TLint4) 0, " .. ", (TLint2) 0);
    TL_TLI_TLIPI ((TLint4) 0, (TLint4) maxclonelines, (TLint2) 0);
    TL_TLI_TLIPS ((TLint4) 0, " lines", (TLint2) 0);
    if (showsource) {
	TL_TLI_TLISS ((TLint4) 0, (TLint2) 2);
	TL_TLI_TLIPS ((TLint4) 0, ", with pc source", (TLint2) 0);
	TL_TLI_TLIPK ((TLint2) 0);
    } else {
	TL_TLI_TLISS ((TLint4) 0, (TLint2) 2);
	TL_TLI_TLIPS ((TLint4) 0, "", (TLint2) 0);
	TL_TLI_TLIPK ((TLint2) 0);
    };
    TL_TLI_TLISS ((TLint4) 0, (TLint2) 2);
    TL_TLI_TLIPS ((TLint4) 0, "Reading pcs ", (TLint2) 0);
    readpcs();
    TL_TLI_TLISS ((TLint4) 0, (TLint2) 2);
    TL_TLI_TLIPS ((TLint4) 0, " done.", (TLint2) 0);
    TL_TLI_TLIPK ((TLint2) 0);
    TL_TLI_TLISS ((TLint4) 0, (TLint2) 2);
    TL_TLI_TLIPS ((TLint4) 0, "Total ", (TLint2) 0);
    TL_TLI_TLIPI ((TLint4) 0, (TLint4) npcs, (TLint2) 0);
    TL_TLI_TLIPS ((TLint4) 0, "/", (TLint2) 0);
    TL_TLI_TLIPI ((TLint4) 0, (TLint4) 6000000, (TLint2) 0);
    TL_TLI_TLIPS ((TLint4) 0, " potential clones of ", (TLint2) 0);
    TL_TLI_TLIPI ((TLint4) 0, (TLint4) minclonelines, (TLint2) 0);
    TL_TLI_TLIPS ((TLint4) 0, " lines or more", (TLint2) 0);
    TL_TLI_TLIPK ((TLint2) 0);
    TL_TLI_TLISS ((TLint4) 0, (TLint2) 2);
    TL_TLI_TLIPS ((TLint4) 0, "Used ", (TLint2) 0);
    TL_TLI_TLIPI ((TLint4) 0, (TLint4) nlines, (TLint2) 0);
    TL_TLI_TLIPS ((TLint4) 0, "/", (TLint2) 0);
    TL_TLI_TLIPI ((TLint4) 0, (TLint4) 100000000, (TLint2) 0);
    TL_TLI_TLIPS ((TLint4) 0, " total pc lines", (TLint2) 0);
    TL_TLI_TLIPK ((TLint2) 0);
    linetable_printstats();
    TL_TLI_TLISS ((TLint4) 0, (TLint2) 2);
    TL_TLI_TLIPS ((TLint4) 0, "Sorting pcs ", (TLint2) 0);
    sortpcs((TLint4) 1, (TLint4) npcs);
    TL_TLI_TLISS ((TLint4) 0, (TLint2) 2);
    TL_TLI_TLIPS ((TLint4) 0, " done.", (TLint2) 0);
    TL_TLI_TLIPK ((TLint2) 0);
    TL_TLI_TLISS ((TLint4) 0, (TLint2) 2);
    TL_TLI_TLIPS ((TLint4) 0, "Finding clones ", (TLint2) 0);
    findclones();
    TL_TLI_TLISS ((TLint4) 0, (TLint2) 2);
    TL_TLI_TLIPS ((TLint4) 0, " done.", (TLint2) 0);
    TL_TLI_TLIPK ((TLint2) 0);
    TL_TLI_TLISS ((TLint4) 0, (TLint2) 2);
    TL_TLI_TLIPS ((TLint4) 0, "Total ", (TLint2) 0);
    TL_TLI_TLIPI ((TLint4) 0, (TLint4) ncompares, (TLint2) 0);
    TL_TLI_TLIPS ((TLint4) 0, " pc comparisons", (TLint2) 0);
    TL_TLI_TLIPK ((TLint2) 0);
    TL_TLI_TLISS ((TLint4) 0, (TLint2) 2);
    TL_TLI_TLIPS ((TLint4) 0, "Pruning embedded clone pairs ", (TLint2) 0);
    oldnpairs = npairs;
    pruneembeddedpairs();
    TL_TLI_TLISS ((TLint4) 0, (TLint2) 2);
    TL_TLI_TLIPS ((TLint4) 0, " done.", (TLint2) 0);
    TL_TLI_TLIPK ((TLint2) 0);
    TL_TLI_TLISS ((TLint4) 0, (TLint2) 2);
    TL_TLI_TLIPS ((TLint4) 0, "Pruned ", (TLint2) 0);
    TL_TLI_TLIPI ((TLint4) 0, (TLint4) (oldnpairs - npairs), (TLint2) 0);
    TL_TLI_TLIPS ((TLint4) 0, " embedded clone pairs", (TLint2) 0);
    TL_TLI_TLIPK ((TLint2) 0);
    TL_TLI_TLISS ((TLint4) 0, (TLint2) 2);
    TL_TLI_TLIPS ((TLint4) 0, "Found ", (TLint2) 0);
    TL_TLI_TLIPI ((TLint4) 0, (TLint4) npairs, (TLint2) 0);
    TL_TLI_TLIPS ((TLint4) 0, " clone pairs", (TLint2) 0);
    TL_TLI_TLIPK ((TLint2) 0);
    TL_TLI_TLISS ((TLint4) 0, (TLint2) 2);
    TL_TLI_TLIPS ((TLint4) 0, "Generating XML output ", (TLint2) 0);
    showpairs();
    TL_TLI_TLISS ((TLint4) 0, (TLint2) 2);
    TL_TLI_TLIPS ((TLint4) 0, " done.", (TLint2) 0);
    TL_TLI_TLIPK ((TLint2) 0);
    TL_TLI_TLISS ((TLint4) 0, (TLint2) 2);
    TL_TLI_TLIPS ((TLint4) 0, "", (TLint2) 0);
    TL_TLI_TLIPK ((TLint2) 0);
}
