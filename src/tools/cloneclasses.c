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
static TLstring	cpfile;

static void useerr () {
    TL_TLI_TLISS ((TLint4) 0, (TLint2) 2);
    TL_TLI_TLIPS ((TLint4) 0, "Usage :  cloneclass.x cpfile.xml > clone-clusters-file.xml", (TLint2) 0);
    TL_TLI_TLIPK ((TLint2) 0);
    TL_TLI_TLISS ((TLint4) 0, (TLint2) 2);
    TL_TLI_TLIPS ((TLint4) 0, "", (TLint2) 0);
    TL_TLI_TLIPK ((TLint2) 0);
    TL_TLI_TLISS ((TLint4) 0, (TLint2) 2);
    TL_TLI_TLIPS ((TLint4) 0, "  e.g.:  cloneclass.x linux_functions-clonepairs.xml > linux_functions-clone-clusters.xml", (TLint2) 0);
    TL_TLI_TLIPK ((TLint2) 0);
    TL_TLI_TLISS ((TLint4) 0, (TLint2) 2);
    TL_TLI_TLIPS ((TLint4) 0, "", (TLint2) 0);
    TL_TLI_TLIPK ((TLint2) 0);
    TL_TLE_TLEQUIT ((TLint4) 1, (char *) 0, 0);
}
typedef	TLchar	linetable___x165[60000001];
static linetable___x165	linetable_lineText;
static TLint4	linetable_lineTextSize;
typedef	TLint4	linetable___x168[12000000];
static linetable___x168	linetable_lineTable;
static TLint4	linetable_lineTableSize;
typedef	TLnat4	linetable_LN;

static TLnat4 linetable_hash (s)
TLstring	s;
{
    typedef	TLnat1	__x172[256];
    typedef	__x172	nat256;
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
	    TLint4	__x174;
	    __x174 = h >> 1;
	    i = 0;
	    if (i <= __x174) {
		for(;;) {
		    h += ((TLint4) h << 1) + ((* (nat256 *) s)[i]);
		    h += ((TLint4) h << 1) + ((* (nat256 *) s)[j]);
		    j -= 1;
		    if (i == __x174) break;
		    i++;
		}
	    };
	};
    };
    return (h);
    /* NOTREACHED */
}
static TLint4	linetable_secondaryHash;
typedef	TLint4	linetable___x179[10];
static linetable___x179	linetable_primes = 
    {1021, 2027, 4091, 8191, 16381, 32003, 65003, 131009, 262007, 524047};
typedef	TLboolean	linetable___x183[256];
static linetable___x183	linetable_spaceP;

static void linetable_strip (rawline, __x78)
TLstring	rawline;
TLstring	__x78;
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
	    TLchar	__x187[2];
	    if ((first > rawlinelength) || ((TL_TLS_TLSBX(__x187, (TLint4) first, line), !(linetable_spaceP[((TLnat4) TLCVTTOCHR(__x187))])))) {
		break;
	    };
	};
	first += 1;
    };
    last = rawlinelength;
    for(;;) {
	{
	    TLchar	__x188[2];
	    if ((last < first) || ((TL_TLS_TLSBX(__x188, (TLint4) last, line), !(linetable_spaceP[((TLnat4) TLCVTTOCHR(__x188))])))) {
		break;
	    };
	};
	last -= 1;
    };
    {
	TLstring	__x189;
	TL_TLS_TLSBXX(__x189, (TLint4) last, (TLint4) first, line);
	TLSTRASS(4095, line, __x189);
    };
    {
	TLSTRASS(4095, __x78, line);
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
	    if (((linetable_lineTextSize + linelength) + 1) > 60000000) {
		TL_TLI_TLISS ((TLint4) 0, (TLint2) 2);
		TL_TLI_TLIPS ((TLint4) 0, "*** Error: too much total unique line text ( > ", (TLint2) 0);
		TL_TLI_TLIPI ((TLint4) 0, (TLint4) 60000000, (TLint2) 0);
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

static void linetable_gettext (lineIndex, __x89)
linetable_LN	lineIndex;
TLstring	__x89;
{
    {
	TLSTRASS(4095, __x89, (* (TLstring *) &linetable_lineText[(linetable_lineTable[lineIndex]) - 1]));
	return;
    };
    /* NOTREACHED */
}

static void linetable_printstats () {
    TL_TLI_TLISS ((TLint4) 0, (TLint2) 2);
    TL_TLI_TLIPS ((TLint4) 0, "Used ", (TLint2) 0);
    TL_TLI_TLIPI ((TLint4) 0, (TLint4) linetable_lineTextSize, (TLint2) 0);
    TL_TLI_TLIPS ((TLint4) 0, "/", (TLint2) 0);
    TL_TLI_TLIPI ((TLint4) 0, (TLint4) 60000000, (TLint2) 0);
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
static TLint4	systeminfo;
static TLint4	cloneinfo;
static TLint4	runinfo;
struct	CP {
    TLint4	info;
    TLint4	nlines;
    TLint4	similarity;
    TLint4	pc1info, pc2info;
    TLint4	pc1, pc2;
    TLint4	cluster;
};
typedef	struct CP	__x194[40000000];
static __x194	pairs;
static TLint4	npairs;
typedef	TLint4	__x195[6000000];
static __x195	pcpair;

static void readclonepairs () {
    TLint4	cpf;
    TLstring	line;
    TL_TLI_TLIOF ((TLnat2) 2, cpfile, &cpf);
    if (cpf == 0) {
	useerr();
    };
    TL_TLI_TLISS ((TLint4) cpf, (TLint2) 1);
    TL_TLI_TLIGSS((TLint4) 4095, line, (TLint2) cpf);
    if (strcmp(line, "<clones>") != 0) {
	TL_TLI_TLISS ((TLint4) 0, (TLint2) 2);
	TL_TLI_TLIPS ((TLint4) 0, "*** Error: input file not a clone pair file", (TLint2) 0);
	TL_TLI_TLIPK ((TLint2) 0);
	useerr();
    };
    TL_TLI_TLISS ((TLint4) cpf, (TLint2) 1);
    TL_TLI_TLIGSS((TLint4) 4095, line, (TLint2) cpf);
    if (TL_TLS_TLSIND(line, "<systeminfo ") != 1) {
	TL_TLI_TLISS ((TLint4) 0, (TLint2) 2);
	TL_TLI_TLIPS ((TLint4) 0, "*** Error: synchronization error on clone pair file", (TLint2) 0);
	TL_TLI_TLIPK ((TLint2) 0);
	TL_TLE_TLEQUIT ((TLint4) 1, (char *) 0, 0);
    } else {
	systeminfo = linetable_install(line);
    };
    TL_TLI_TLISS ((TLint4) cpf, (TLint2) 1);
    TL_TLI_TLIGSS((TLint4) 4095, line, (TLint2) cpf);
    if (TL_TLS_TLSIND(line, "<cloneinfo ") != 1) {
	TL_TLI_TLISS ((TLint4) 0, (TLint2) 2);
	TL_TLI_TLIPS ((TLint4) 0, "*** Error: synchronization error on clone pair file", (TLint2) 0);
	TL_TLI_TLIPK ((TLint2) 0);
	TL_TLE_TLEQUIT ((TLint4) 1, (char *) 0, 0);
    } else {
	cloneinfo = linetable_install(line);
    };
    TL_TLI_TLISS ((TLint4) cpf, (TLint2) 1);
    TL_TLI_TLIGSS((TLint4) 4095, line, (TLint2) cpf);
    if (TL_TLS_TLSIND(line, "<runinfo ") != 1) {
	TL_TLI_TLISS ((TLint4) 0, (TLint2) 2);
	TL_TLI_TLIPS ((TLint4) 0, "*** Error: synchronization error on clone pair file", (TLint2) 0);
	TL_TLI_TLIPK ((TLint2) 0);
	TL_TLE_TLEQUIT ((TLint4) 1, (char *) 0, 0);
    } else {
	runinfo = linetable_install(line);
    };
    {
	register TLint4	i;
	for (i = 1; i <= 20000000; i++) {
	    TLBIND((*pair), struct CP);
	    TLstring	nlines;
	    TLstring	similarity;
	    TLstring	pcid1;
	    TLstring	pcid2;
	    TLBIND((*revpair), struct CP);
	    if ((i % 1000) == 1) {
		TL_TLI_TLISS ((TLint4) 0, (TLint2) 2);
		TL_TLI_TLIPS ((TLint4) 0, ".", (TLint2) 0);
	    };
	    if (TL_TLI_TLIEOF((TLint4) cpf)) {
		break;
	    };
	    TL_TLI_TLISS ((TLint4) cpf, (TLint2) 1);
	    TL_TLI_TLIGSS((TLint4) 4095, line, (TLint2) cpf);
	    if (strcmp(line, "") == 0) {
		TL_TLI_TLISS ((TLint4) cpf, (TLint2) 1);
		TL_TLI_TLIGSS((TLint4) 4095, line, (TLint2) cpf);
	    };
	    if (TL_TLS_TLSIND(line, "</clones>") == 1) {
		break;
	    };
	    if (TL_TLS_TLSIND(line, "<clone ") != 1) {
		TL_TLI_TLISS ((TLint4) 0, (TLint2) 2);
		TL_TLI_TLIPS ((TLint4) 0, "*** Error: synchronization error on clone pair file", (TLint2) 0);
		TL_TLI_TLIPK ((TLint2) 0);
		TL_TLE_TLEQUIT ((TLint4) 1, (char *) 0, 0);
	    };
	    npairs += 1;
	    pair = &(pairs[npairs - 1]);
	    (*pair).info = linetable_install(line);
	    {
		TLstring	__x198;
		TL_TLS_TLSBXX(__x198, (TLint4) (TL_TLS_TLSIND(line, " similarity=\"") - 2), (TLint4) (TL_TLS_TLSIND(line, "nlines=\"") + TL_TLS_TLSLEN("nlines=\"")), line);
		TLSTRASS(4095, nlines, __x198);
	    };
	    {
		TLstring	__x199;
		TL_TLS_TLSBXX(__x199, (TLint4) (TL_TLS_TLSIND(line, "\">") - 1), (TLint4) (TL_TLS_TLSIND(line, "similarity=\"") + TL_TLS_TLSLEN("similarity=\"")), line);
		TLSTRASS(4095, similarity, __x199);
	    };
	    (*pair).nlines = TL_TLS_TLSVSI(nlines, (TLint4) 10);
	    (*pair).similarity = TL_TLS_TLSVSI(similarity, (TLint4) 10);
	    (*pair).cluster = 0;
	    TL_TLI_TLISS ((TLint4) cpf, (TLint2) 1);
	    TL_TLI_TLIGSS((TLint4) 4095, line, (TLint2) cpf);
	    if (strcmp(line, "") == 0) {
		TL_TLI_TLISS ((TLint4) cpf, (TLint2) 1);
		TL_TLI_TLIGSS((TLint4) 4095, line, (TLint2) cpf);
	    };
	    if (TL_TLS_TLSIND(line, "<source ") != 1) {
		TL_TLI_TLISS ((TLint4) 0, (TLint2) 2);
		TL_TLI_TLIPS ((TLint4) 0, "*** Error: synchronization error on clone pair file", (TLint2) 0);
		TL_TLI_TLIPK ((TLint2) 0);
		TL_TLE_TLEQUIT ((TLint4) 1, (char *) 0, 0);
	    };
	    (*pair).pc1info = linetable_install(line);
	    {
		TLstring	__x200;
		TL_TLS_TLSBXX(__x200, (TLint4) (TL_TLS_TLSIND(line, "\">") - 1), (TLint4) (TL_TLS_TLSIND(line, "pcid=\"") + TL_TLS_TLSLEN("pcid=\"")), line);
		TLSTRASS(4095, pcid1, __x200);
	    };
	    (*pair).pc1 = TL_TLS_TLSVSI(pcid1, (TLint4) 10);
	    TL_TLI_TLISS ((TLint4) cpf, (TLint2) 1);
	    TL_TLI_TLIGSS((TLint4) 4095, line, (TLint2) cpf);
	    if (strcmp(line, "") == 0) {
		TL_TLI_TLISS ((TLint4) cpf, (TLint2) 1);
		TL_TLI_TLIGSS((TLint4) 4095, line, (TLint2) cpf);
	    };
	    if (TL_TLS_TLSIND(line, "<source ") != 1) {
		TL_TLI_TLISS ((TLint4) 0, (TLint2) 2);
		TL_TLI_TLIPS ((TLint4) 0, "*** Error: synchronization error on clone pair file", (TLint2) 0);
		TL_TLI_TLIPK ((TLint2) 0);
		TL_TLE_TLEQUIT ((TLint4) 1, (char *) 0, 0);
	    };
	    (*pair).pc2info = linetable_install(line);
	    {
		TLstring	__x201;
		TL_TLS_TLSBXX(__x201, (TLint4) (TL_TLS_TLSIND(line, "\">") - 1), (TLint4) (TL_TLS_TLSIND(line, "pcid=\"") + TL_TLS_TLSLEN("pcid=\"")), line);
		TLSTRASS(4095, pcid2, __x201);
	    };
	    (*pair).pc2 = TL_TLS_TLSVSI(pcid2, (TLint4) 10);
	    npairs += 1;
	    revpair = &(pairs[npairs - 1]);
	    TLSTRCTASS((*revpair), (*pair), struct CP);
	    (*revpair).pc1 = (*pair).pc2;
	    (*revpair).pc1info = (*pair).pc2info;
	    (*revpair).pc2 = (*pair).pc1;
	    (*revpair).pc2info = (*pair).pc1info;
	    TL_TLI_TLISS ((TLint4) cpf, (TLint2) 1);
	    TL_TLI_TLIGSS((TLint4) 4095, line, (TLint2) cpf);
	    if (TL_TLS_TLSIND(line, "</clone>") != 1) {
		TL_TLI_TLISS ((TLint4) 0, (TLint2) 2);
		TL_TLI_TLIPS ((TLint4) 0, "*** Error: synchronization error on clone pair file", (TLint2) 0);
		TL_TLI_TLIPK ((TLint2) 0);
		TL_TLE_TLEQUIT ((TLint4) 1, (char *) 0, 0);
	    };
	};
    };
    if (!TL_TLI_TLIEOF((TLint4) cpf)) {
	TL_TLI_TLISS ((TLint4) 0, (TLint2) 2);
	TL_TLI_TLIPS ((TLint4) 0, "*** Error: too many clone pairs ( > ", (TLint2) 0);
	TL_TLI_TLIPI ((TLint4) 0, (TLint4) 20000000, (TLint2) 0);
	TL_TLI_TLIPS ((TLint4) 0, ")", (TLint2) 0);
	TL_TLI_TLIPK ((TLint2) 0);
    };
    TL_TLI_TLICL ((TLint4) cpf);
}

static void swapclonepairs (i, j)
TLint4	i;
TLint4	j;
{
    struct CP	t;
    TLSTRCTASS(t, pairs[i - 1], struct CP);
    TLSTRCTASS(pairs[i - 1], pairs[j - 1], struct CP);
    TLSTRCTASS(pairs[j - 1], t, struct CP);
}
static TLint4	depth;

static void quicksortclonepairs (first, last)
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
		if ((pairs[high - 1].pc1) < (pairs[pivot - 1].pc1)) {
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
		if ((pairs[pivot - 1].pc1) < (pairs[low - 1].pc1)) {
		    break;
		};
	    };
	    if (low == high) {
		break;
	    };
	    swapclonepairs((TLint4) low, (TLint4) high);
	};
	swapclonepairs((TLint4) high, (TLint4) pivot);
	quicksortclonepairs((TLint4) first, (TLint4) (high - 1));
	quicksortclonepairs((TLint4) (high + 1), (TLint4) last);
    };
    depth = depth - 1;
}

static void indexpairs () {
    {
	register TLint4	i;
	TLint4	__x202;
	__x202 = npairs;
	i = 1;
	if (i <= __x202) {
	    for(;;) {
		TLBIND((*pair), struct CP);
		if ((i % 2000) == 1) {
		    TL_TLI_TLISS ((TLint4) 0, (TLint2) 2);
		    TL_TLI_TLIPS ((TLint4) 0, ".", (TLint2) 0);
		};
		pair = &(pairs[i - 1]);
		if ((pcpair[((*pair).pc1) - 1]) == 0) {
		    pcpair[((*pair).pc1) - 1] = i;
		};
		if (i == __x202) break;
		i++;
	    }
	};
    };
}
struct	CL {
    TLint4	pairs;
    TLint4	npairs;
};
typedef	struct CL	__x203[2000000];
static __x203	clusters;
static TLint4	nclusters;
typedef	TLint4	__x204[20000000];
static __x204	clusterpairs;
static TLint4	nclusterpairs;

static void clusterclonepairs () {
    {
	register TLint4	i;
	TLint4	__x207;
	__x207 = npairs;
	i = 1;
	if (i <= __x207) {
	    for(;;) {
		TLBIND((*pair), struct CP);
		if ((i % 2000) == 1) {
		    TL_TLI_TLISS ((TLint4) 0, (TLint2) 2);
		    TL_TLI_TLIPS ((TLint4) 0, ".", (TLint2) 0);
		};
		pair = &(pairs[i - 1]);
		if (((*pair).cluster) == 0) {
		    TLBIND((*cluster), struct CL);
		    TLint4	cp;
		    nclusters += 1;
		    (*pair).cluster = nclusters;
		    cluster = &(clusters[nclusters - 1]);
		    (*cluster).pairs = nclusterpairs;
		    (*cluster).npairs = 1;
		    nclusterpairs += 1;
		    clusterpairs[nclusterpairs - 1] = i;
		    {
			register TLint4	j;
			TLint4	__x208;
			__x208 = npairs;
			j = i + 1;
			if (j <= __x208) {
			    for(;;) {
				if ((pairs[j - 1].pc1) != ((*pair).pc1)) {
				    break;
				};
				pairs[j - 1].cluster = nclusters;
				(*cluster).npairs += 1;
				nclusterpairs += 1;
				clusterpairs[nclusterpairs - 1] = j;
				if (j == __x208) break;
				j++;
			    }
			};
		    };
		    cp = (*cluster).pairs;
		    for(;;) {
			TLBIND((*pcp), struct CP);
			if (cp > nclusterpairs) {
			    break;
			};
			pcp = &(pairs[(clusterpairs[cp - 1]) - 1]);
			if ((pcpair[((*pcp).pc2) - 1]) != 0) {
			    {
				register TLint4	j;
				TLint4	__x209;
				__x209 = npairs;
				j = pcpair[((*pcp).pc2) - 1];
				if (j <= __x209) {
				    for(;;) {
					TLBIND((*newpair), struct CP);
					if ((pairs[j - 1].pc1) != ((*pcp).pc2)) {
					    break;
					};
					newpair = &(pairs[j - 1]);
					if (((*newpair).cluster) == 0) {
					    TLboolean	alreadyhaveit;
					    (*newpair).cluster = nclusters;
					    alreadyhaveit = 0;
					    {
						register TLint4	k;
						TLint4	__x210;
						__x210 = nclusterpairs;
						k = 1;
						if (k <= __x210) {
						    for(;;) {
							TLBIND((*oldpair), struct CP);
							oldpair = &(pairs[(clusterpairs[((((*cluster).pairs) + k) - 1) - 1]) - 1]);
							if (((*oldpair).pc2) == ((*newpair).pc2)) {
							    alreadyhaveit = 1;
							};
							if (alreadyhaveit) {
							    break;
							};
							if (k == __x210) break;
							k++;
						    }
						};
					    };
					    if (!alreadyhaveit) {
						(*cluster).npairs += 1;
						nclusterpairs += 1;
						clusterpairs[nclusterpairs - 1] = j;
					    };
					};
					if (j == __x209) break;
					j++;
				    }
				};
			    };
			};
			cp += 1;
		    };
		    cp = (*cluster).pairs;
		    for(;;) {
			TLBIND((*pcp), struct CP);
			if (cp > nclusterpairs) {
			    break;
			};
			pcp = &(pairs[(clusterpairs[cp - 1]) - 1]);
			{
			    register TLint4	ccp;
			    TLint4	__x211;
			    __x211 = nclusterpairs;
			    ccp = cp + 1;
			    if (ccp <= __x211) {
				for(;;) {
				    TLBIND((*pccp), struct CP);
				    pccp = &(pairs[(clusterpairs[ccp - 1]) - 1]);
				    if ((((*pccp).pc1) == ((*pcp).pc1)) || (((*pccp).pc1) == ((*pcp).pc2))) {
					(*pccp).pc1 = 0;
				    };
				    if ((((*pccp).pc2) == ((*pcp).pc1)) || (((*pccp).pc2) == ((*pcp).pc2))) {
					(*pccp).pc2 = 0;
				    };
				    if (ccp == __x211) break;
				    ccp++;
				}
			    };
			};
			cp += 1;
		    };
		};
		if (i == __x207) break;
		i++;
	    }
	};
    };
}

static void showclusters () {
    TL_TLI_TLISSO ();
    TL_TLI_TLIPS ((TLint4) 0, "<clones>", (TLint2) -1);
    TL_TLI_TLIPK ((TLint2) -1);
    {
	TLstring	__x212;
	linetable_gettext((linetable_LN) systeminfo, __x212);
	TL_TLI_TLISSO ();
	TL_TLI_TLIPS ((TLint4) 0, __x212, (TLint2) -1);
	TL_TLI_TLIPK ((TLint2) -1);
    };
    {
	TLstring	__x213;
	linetable_gettext((linetable_LN) cloneinfo, __x213);
	TL_TLI_TLISSO ();
	TL_TLI_TLIPS ((TLint4) 0, __x213, (TLint2) -1);
	TL_TLI_TLIPK ((TLint2) -1);
    };
    {
	TLstring	__x214;
	linetable_gettext((linetable_LN) runinfo, __x214);
	TL_TLI_TLISSO ();
	TL_TLI_TLIPS ((TLint4) 0, __x214, (TLint2) -1);
	TL_TLI_TLIPK ((TLint2) -1);
    };
    TL_TLI_TLISSO ();
    TL_TLI_TLIPS ((TLint4) 0, "<classinfo nclasses=\"", (TLint2) -1);
    TL_TLI_TLIPI ((TLint4) 0, (TLint4) nclusters, (TLint2) -1);
    TL_TLI_TLIPS ((TLint4) 0, "\"/>", (TLint2) -1);
    TL_TLI_TLIPK ((TLint2) -1);
    TL_TLI_TLISSO ();
    TL_TLI_TLIPS ((TLint4) 0, "", (TLint2) -1);
    TL_TLI_TLIPK ((TLint2) -1);
    {
	register TLint4	i;
	TLint4	__x215;
	__x215 = nclusters;
	i = 1;
	if (i <= __x215) {
	    for(;;) {
		TLBIND((*cl), struct CL);
		TLint4	nclones;
		TLint4	similarity;
		TLint4	nlines;
		if ((i % 100) == 1) {
		    TL_TLI_TLISS ((TLint4) 0, (TLint2) 2);
		    TL_TLI_TLIPS ((TLint4) 0, ".", (TLint2) 0);
		};
		cl = &(clusters[i - 1]);
		nclones = 0;
		similarity = 100;
		nlines = 0;
		{
		    register TLint4	j;
		    TLint4	__x216;
		    __x216 = (*cl).npairs;
		    j = 1;
		    if (j <= __x216) {
			for(;;) {
			    TLBIND((*cp), struct CP);
			    cp = &(pairs[(clusterpairs[(((*cl).pairs) + j) - 1]) - 1]);
			    if (((*cp).pc1) != 0) {
				nclones += 1;
				nlines += (*cp).nlines;
			    };
			    if (((*cp).pc2) != 0) {
				nclones += 1;
				nlines += (*cp).nlines;
			    };
			    if (((*cp).similarity) < similarity) {
				similarity = (*cp).similarity;
			    };
			    if (j == __x216) break;
			    j++;
			}
		    };
		};
		nlines = nlines / nclones;
		TL_TLI_TLISSO ();
		TL_TLI_TLIPS ((TLint4) 0, "<class classid=\"", (TLint2) -1);
		TL_TLI_TLIPI ((TLint4) 0, (TLint4) i, (TLint2) -1);
		TL_TLI_TLIPS ((TLint4) 0, "\" nclones=\"", (TLint2) -1);
		TL_TLI_TLIPI ((TLint4) 0, (TLint4) nclones, (TLint2) -1);
		TL_TLI_TLIPS ((TLint4) 0, "\" nlines=\"", (TLint2) -1);
		TL_TLI_TLIPI ((TLint4) 0, (TLint4) nlines, (TLint2) -1);
		TL_TLI_TLIPS ((TLint4) 0, "\" similarity=\"", (TLint2) -1);
		TL_TLI_TLIPI ((TLint4) 0, (TLint4) similarity, (TLint2) -1);
		TL_TLI_TLIPS ((TLint4) 0, "\">", (TLint2) -1);
		TL_TLI_TLIPK ((TLint2) -1);
		{
		    register TLint4	j;
		    TLint4	__x217;
		    __x217 = (*cl).npairs;
		    j = 1;
		    if (j <= __x217) {
			for(;;) {
			    TLBIND((*cp), struct CP);
			    cp = &(pairs[(clusterpairs[(((*cl).pairs) + j) - 1]) - 1]);
			    if (((*cp).pc1) != 0) {
				{
				    TLstring	__x218;
				    linetable_gettext((linetable_LN) ((*cp).pc1info), __x218);
				    TL_TLI_TLISSO ();
				    TL_TLI_TLIPS ((TLint4) 0, __x218, (TLint2) -1);
				    TL_TLI_TLIPK ((TLint2) -1);
				};
			    };
			    if (((*cp).pc2) != 0) {
				{
				    TLstring	__x219;
				    linetable_gettext((linetable_LN) ((*cp).pc2info), __x219);
				    TL_TLI_TLISSO ();
				    TL_TLI_TLIPS ((TLint4) 0, __x219, (TLint2) -1);
				    TL_TLI_TLIPK ((TLint2) -1);
				};
			    };
			    if (j == __x217) break;
			    j++;
			}
		    };
		};
		TL_TLI_TLISSO ();
		TL_TLI_TLIPS ((TLint4) 0, "</class>", (TLint2) -1);
		TL_TLI_TLIPK ((TLint2) -1);
		TL_TLI_TLISSO ();
		TL_TLI_TLIPS ((TLint4) 0, "", (TLint2) -1);
		TL_TLI_TLIPK ((TLint2) -1);
		if (i == __x215) break;
		i++;
	    }
	};
    };
    TL_TLI_TLISSO ();
    TL_TLI_TLIPS ((TLint4) 0, "</clones>", (TLint2) -1);
    TL_TLI_TLIPK ((TLint2) -1);
}

static void getprogramarguments () {
    if (TL_TLI_TLIARC != 1) {
	useerr();
    };
    {
	TLstring	__x220;
	TL_TLI_TLIFA((TLint4) 1, __x220);
	TLSTRASS(4095, cpfile, __x220);
    };
}
void TProg () {
    linetable();
    npairs = 0;
    {
	register TLint4	z;
	for (z = 1; z <= 6000000; z++) {
	    pcpair[z - 1] = 0;
	};
    };
    depth = 0;
    nclusters = 0;
    nclusterpairs = 0;
    getprogramarguments();
    TL_TLI_TLISS ((TLint4) 0, (TLint2) 2);
    TL_TLI_TLIPS ((TLint4) 0, "Processing ", (TLint2) 0);
    TL_TLI_TLIPS ((TLint4) 0, cpfile, (TLint2) 0);
    TL_TLI_TLIPK ((TLint2) 0);
    TL_TLI_TLISS ((TLint4) 0, (TLint2) 2);
    TL_TLI_TLIPS ((TLint4) 0, "Reading clone pairs ", (TLint2) 0);
    readclonepairs();
    TL_TLI_TLISS ((TLint4) 0, (TLint2) 2);
    TL_TLI_TLIPS ((TLint4) 0, " done.", (TLint2) 0);
    TL_TLI_TLIPK ((TLint2) 0);
    TL_TLI_TLISS ((TLint4) 0, (TLint2) 2);
    TL_TLI_TLIPS ((TLint4) 0, "Total ", (TLint2) 0);
    TL_TLI_TLIPI ((TLint4) 0, (TLint4) (npairs / 2), (TLint2) 0);
    TL_TLI_TLIPS ((TLint4) 0, " pairs", (TLint2) 0);
    TL_TLI_TLIPK ((TLint2) 0);
    TL_TLI_TLISS ((TLint4) 0, (TLint2) 2);
    TL_TLI_TLIPS ((TLint4) 0, "Sorting pairs ", (TLint2) 0);
    quicksortclonepairs((TLint4) 1, (TLint4) npairs);
    TL_TLI_TLISS ((TLint4) 0, (TLint2) 2);
    TL_TLI_TLIPS ((TLint4) 0, " done.", (TLint2) 0);
    TL_TLI_TLIPK ((TLint2) 0);
    TL_TLI_TLISS ((TLint4) 0, (TLint2) 2);
    TL_TLI_TLIPS ((TLint4) 0, "Indexing pairs ", (TLint2) 0);
    indexpairs();
    TL_TLI_TLISS ((TLint4) 0, (TLint2) 2);
    TL_TLI_TLIPS ((TLint4) 0, " done.", (TLint2) 0);
    TL_TLI_TLIPK ((TLint2) 0);
    TL_TLI_TLISS ((TLint4) 0, (TLint2) 2);
    TL_TLI_TLIPS ((TLint4) 0, "Computing classes ", (TLint2) 0);
    clusterclonepairs();
    TL_TLI_TLISS ((TLint4) 0, (TLint2) 2);
    TL_TLI_TLIPS ((TLint4) 0, " done.", (TLint2) 0);
    TL_TLI_TLIPK ((TLint2) 0);
    TL_TLI_TLISS ((TLint4) 0, (TLint2) 2);
    TL_TLI_TLIPS ((TLint4) 0, "Clustered clone pairs into ", (TLint2) 0);
    TL_TLI_TLIPI ((TLint4) 0, (TLint4) nclusters, (TLint2) 0);
    TL_TLI_TLIPS ((TLint4) 0, " classes", (TLint2) 0);
    TL_TLI_TLIPK ((TLint2) 0);
    TL_TLI_TLISS ((TLint4) 0, (TLint2) 2);
    TL_TLI_TLIPS ((TLint4) 0, "Generating XML output ", (TLint2) 0);
    showclusters();
    TL_TLI_TLISS ((TLint4) 0, (TLint2) 2);
    TL_TLI_TLIPS ((TLint4) 0, " done.", (TLint2) 0);
    TL_TLI_TLIPK ((TLint2) 0);
    TL_TLI_TLISS ((TLint4) 0, (TLint2) 2);
    TL_TLI_TLIPS ((TLint4) 0, "", (TLint2) 0);
    TL_TLI_TLIPK ((TLint2) 0);
}
