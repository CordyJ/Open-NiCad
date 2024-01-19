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
static TLstring	ccfile;
static TLstring	rccfile;
static TLint4	minclonelines;
static TLint4	maxclonelines;

static void useerr () {
    TL_TLI_TLISS ((TLint4) 0, (TLint2) 2);
    TL_TLI_TLIPS ((TLint4) 0, "Usage :  getnormsource.x pcfile.xml inclonesfile.xml outclonesfile.xml", (TLint2) 0);
    TL_TLI_TLIPK ((TLint2) 0);
    TL_TLI_TLISS ((TLint4) 0, (TLint2) 2);
    TL_TLI_TLIPS ((TLint4) 0, "", (TLint2) 0);
    TL_TLI_TLIPK ((TLint2) 0);
    TL_TLI_TLISS ((TLint4) 0, (TLint2) 2);
    TL_TLI_TLIPS ((TLint4) 0, "  e.g.:  getnormsource.x linux_functions.xml linux_functions-clones.xml linux_functions-clones-withnormsource.xml", (TLint2) 0);
    TL_TLI_TLIPK ((TLint2) 0);
    TL_TLI_TLISS ((TLint4) 0, (TLint2) 2);
    TL_TLI_TLIPS ((TLint4) 0, "", (TLint2) 0);
    TL_TLI_TLIPK ((TLint2) 0);
    TL_TLE_TLEQUIT ((TLint4) 1, (char *) 0, 0);
}
typedef	TLchar	linetable___x131[600000001];
static linetable___x131	linetable_lineText;
static TLint4	linetable_lineTextSize;
typedef	TLint4	linetable___x134[12000000];
static linetable___x134	linetable_lineTable;
static TLint4	linetable_lineTableSize;
typedef	TLnat4	linetable_LN;

static TLnat4 linetable_hash (s)
TLstring	s;
{
    typedef	TLnat1	__x138[256];
    typedef	__x138	nat256;
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
	    TLint4	__x140;
	    __x140 = h >> 1;
	    i = 0;
	    if (i <= __x140) {
		for(;;) {
		    h += ((TLint4) h << 1) + ((* (nat256 *) s)[i]);
		    h += ((TLint4) h << 1) + ((* (nat256 *) s)[j]);
		    j -= 1;
		    if (i == __x140) break;
		    i++;
		}
	    };
	};
    };
    return (h);
    /* NOTREACHED */
}
static TLint4	linetable_secondaryHash;
typedef	TLint4	linetable___x145[10];
static linetable___x145	linetable_primes = 
    {1021, 2027, 4091, 8191, 16381, 32003, 65003, 131009, 262007, 524047};
typedef	TLboolean	linetable___x149[256];
static linetable___x149	linetable_spaceP;

static void linetable_strip (rawline, __x81)
TLstring	rawline;
TLstring	__x81;
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
	    TLchar	__x153[2];
	    if ((first > rawlinelength) || ((TL_TLS_TLSBX(__x153, (TLint4) first, line), !(linetable_spaceP[((TLnat4) TLCVTTOCHR(__x153))])))) {
		break;
	    };
	};
	first += 1;
    };
    last = rawlinelength;
    for(;;) {
	{
	    TLchar	__x154[2];
	    if ((last < first) || ((TL_TLS_TLSBX(__x154, (TLint4) last, line), !(linetable_spaceP[((TLnat4) TLCVTTOCHR(__x154))])))) {
		break;
	    };
	};
	last -= 1;
    };
    {
	TLstring	__x155;
	TL_TLS_TLSBXX(__x155, (TLint4) last, (TLint4) first, line);
	TLSTRASS(4095, line, __x155);
    };
    {
	TLSTRASS(4095, __x81, line);
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

static void linetable_gettext (lineIndex, __x92)
linetable_LN	lineIndex;
TLstring	__x92;
{
    {
	TLSTRASS(4095, __x92, (* (TLstring *) &linetable_lineText[(linetable_lineTable[lineIndex]) - 1]));
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
    TLint4	embedding;
};
typedef	struct PC	__x160[6000000];
static __x160	pcs;
static TLint4	npcs;
typedef	linetable_LN	__x161[100000000];
static __x161	lines;
static TLint4	nlines;

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
		TLstring	__x162;
		TL_TLS_TLSBXX(__x162, (TLint4) sfend, (TLint4) sfindex, sourceheader);
		(*pc).srcfile = linetable_install(__x162);
	    };
	    slindex = (TL_TLS_TLSIND(sourceheader, "startline=") + TL_TLS_TLSLEN("startline=")) + 1;
	    slend = TL_TLS_TLSIND(sourceheader, " endline=") - 2;
	    {
		TLstring	__x163;
		TL_TLS_TLSBXX(__x163, (TLint4) slend, (TLint4) slindex, sourceheader);
		(*pc).srcstartline = TL_TLS_TLSVSI(__x163, (TLint4) 10);
	    };
	    elindex = (TL_TLS_TLSIND(sourceheader, "endline=") + TL_TLS_TLSLEN("endline=")) + 1;
	    elend = TL_TLS_TLSLEN(sourceheader) - 2;
	    {
		TLstring	__x164;
		TL_TLS_TLSBXX(__x164, (TLint4) elend, (TLint4) elindex, sourceheader);
		(*pc).srcendline = TL_TLS_TLSVSI(__x164, (TLint4) 10);
	    };
	    (*pc).firstline = nlines;
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
		if (strcmp(line, "") != 0) {
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
	    (*pc).nlines = nlines - ((*pc).firstline);
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

static void getprogramarguments () {
    if (TL_TLI_TLIARC != 3) {
	useerr();
    };
    {
	TLstring	__x165;
	TL_TLI_TLIFA((TLint4) 1, __x165);
	TLSTRASS(4095, pcfile, __x165);
    };
    {
	TLstring	__x166;
	TL_TLI_TLIFA((TLint4) 2, __x166);
	TLSTRASS(4095, ccfile, __x166);
    };
    {
	TLstring	__x167;
	TL_TLI_TLIFA((TLint4) 3, __x167);
	TLSTRASS(4095, rccfile, __x167);
    };
}

static void resolvepcsources () {
    TLint4	ccf;
    TLint4	rccf;
    TL_TLI_TLIOF ((TLnat2) 2, ccfile, &ccf);
    if (ccf == 0) {
	useerr();
    };
    TL_TLI_TLIOF ((TLnat2) 4, rccfile, &rccf);
    if (rccf == 0) {
	useerr();
    };
    {
	register TLint4	i;
	for (i = 1; i <= 999999999; i++) {
	    TLstring	line;
	    if ((i % 100) == 1) {
		TL_TLI_TLISS ((TLint4) 0, (TLint2) 2);
		TL_TLI_TLIPS ((TLint4) 0, ".", (TLint2) 0);
	    };
	    if (TL_TLI_TLIEOF((TLint4) ccf)) {
		break;
	    };
	    TL_TLI_TLISS ((TLint4) ccf, (TLint2) 1);
	    TL_TLI_TLIGSS((TLint4) 4095, line, (TLint2) ccf);
	    if (TL_TLS_TLSIND(line, "<source ") == 1) {
		TLstring	sourceheader;
		TLstring	textpcid;
		TLint4	pcid;
		TLBIND((*pc), struct PC);
		{
		    TLstring	__x168;
		    TL_TLS_TLSBXX(__x168, (TLint4) TL_TLS_TLSIND(line, "></source>"), (TLint4) 1, line);
		    TLSTRASS(4095, sourceheader, __x168);
		};
		TL_TLI_TLISS ((TLint4) rccf, (TLint2) 2);
		TL_TLI_TLIPS ((TLint4) 0, sourceheader, (TLint2) rccf);
		TL_TLI_TLIPK ((TLint2) rccf);
		{
		    TLstring	__x169;
		    TL_TLS_TLSBXX(__x169, (TLint4) (TL_TLS_TLSLEN(sourceheader) - 1), (TLint4) ((TL_TLS_TLSIND(sourceheader, "pcid=") + TL_TLS_TLSLEN("pcid=")) + 1), sourceheader);
		    TLSTRASS(4095, textpcid, __x169);
		};
		pcid = TL_TLS_TLSVSI(textpcid, (TLint4) 10);
		pc = &(pcs[pcid - 1]);
		if (((*pc).num) != pcid) {
		    TL_TLI_TLISS ((TLint4) 0, (TLint2) 2);
		    TL_TLI_TLIPS ((TLint4) 0, "*** Error in pc number", (TLint2) 0);
		    TL_TLI_TLIPK ((TLint2) 0);
		    TL_TLE_TLEQUIT ((TLint4) 99, (char *) 0, 0);
		};
		{
		    register TLint4	k;
		    TLint4	__x170;
		    __x170 = (*pc).nlines;
		    k = 1;
		    if (k <= __x170) {
			for(;;) {
			    {
				TLstring	__x171;
				linetable_gettext((linetable_LN) (lines[(((*pc).firstline) + k) - 1]), __x171);
				TL_TLI_TLISS ((TLint4) rccf, (TLint2) 2);
				TL_TLI_TLIPS ((TLint4) 0, __x171, (TLint2) rccf);
				TL_TLI_TLIPK ((TLint2) rccf);
			    };
			    if (k == __x170) break;
			    k++;
			}
		    };
		};
		TL_TLI_TLISS ((TLint4) rccf, (TLint2) 2);
		TL_TLI_TLIPS ((TLint4) 0, "</source>", (TLint2) rccf);
		TL_TLI_TLIPK ((TLint2) rccf);
	    } else {
		TL_TLI_TLISS ((TLint4) rccf, (TLint2) 2);
		TL_TLI_TLIPS ((TLint4) 0, line, (TLint2) rccf);
		TL_TLI_TLIPK ((TLint2) rccf);
	    };
	};
    };
    TL_TLI_TLICL ((TLint4) rccf);
}
void TProg () {
    minclonelines = 5;
    maxclonelines = 2500;
    linetable();
    npcs = 0;
    nlines = 0;
    getprogramarguments();
    TL_TLI_TLISS ((TLint4) 0, (TLint2) 2);
    TL_TLI_TLIPS ((TLint4) 0, "Reading pcs ", (TLint2) 0);
    readpcs();
    TL_TLI_TLISS ((TLint4) 0, (TLint2) 2);
    TL_TLI_TLIPS ((TLint4) 0, " done.", (TLint2) 0);
    TL_TLI_TLIPK ((TLint2) 0);
    TL_TLI_TLISS ((TLint4) 0, (TLint2) 2);
    TL_TLI_TLIPS ((TLint4) 0, "Resolving normalized pc sources ", (TLint2) 0);
    resolvepcsources();
    TL_TLI_TLISS ((TLint4) 0, (TLint2) 2);
    TL_TLI_TLIPS ((TLint4) 0, " done.", (TLint2) 0);
    TL_TLI_TLIPK ((TLint2) 0);
    TL_TLI_TLISS ((TLint4) 0, (TLint2) 2);
    TL_TLI_TLIPS ((TLint4) 0, "", (TLint2) 0);
    TL_TLI_TLIPK ((TLint2) 0);
}
