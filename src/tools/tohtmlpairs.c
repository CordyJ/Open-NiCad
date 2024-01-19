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

static void encode (line, __x45)
TLstring	line;
TLstring	__x45;
{
    TLstring	eline;
    TLSTRASS(4095, eline, "");
    {
	register TLint4	i;
	TLint4	__x90;
	__x90 = TL_TLS_TLSLEN(line);
	i = 1;
	if (i <= __x90) {
	    for(;;) {
		{
		    TLchar	__x91[2];
		    TL_TLS_TLSBX(__x91, (TLint4) i, line);
		    switch (((TLnat4) TLCVTTOCHR(__x91))) {
			case 60:
			    {
				TLSTRCATASS(eline, "&lt;", 4095);
			    }
			    break;
			case 62:
			    {
				TLSTRCATASS(eline, "&gt;", 4095);
			    }
			    break;
			case 38:
			    {
				TLSTRCATASS(eline, "&amp;", 4095);
			    }
			    break;
			default :
			    {
				{
				    TLchar	__x92[2];
				    TL_TLS_TLSBX(__x92, (TLint4) i, line);
				    TLSTRCATASS(eline, __x92, 4095);
				};
			    }
			    break;
		    };
		};
		if (i == __x90) break;
		i++;
	    }
	};
    };
    {
	TLSTRASS(4095, __x45, eline);
	return;
    };
    /* NOTREACHED */
}

static void strip (srcpath, __x50)
TLstring	srcpath;
TLstring	__x50;
{
    if (TL_TLS_TLSIND(srcpath, ".ifdefed") == (TL_TLS_TLSLEN(srcpath) - 7)) {
	{
	    {
		TLstring	__x94;
		TL_TLS_TLSBXX(__x94, (TLint4) (TL_TLS_TLSIND(srcpath, ".ifdefed") - 1), (TLint4) 1, srcpath);
		TLSTRASS(4095, __x50, __x94);
	    };
	    return;
	};
    } else {
	if (TL_TLS_TLSIND(srcpath, ".pyindent") == (TL_TLS_TLSLEN(srcpath) - 8)) {
	    {
		{
		    TLstring	__x95;
		    TL_TLS_TLSBXX(__x95, (TLint4) (TL_TLS_TLSIND(srcpath, ".pyindent") - 1), (TLint4) 1, srcpath);
		    TLSTRASS(4095, __x50, __x95);
		};
		return;
	    };
	} else {
	    {
		TLSTRASS(4095, __x50, srcpath);
		return;
	    };
	};
    };
    /* NOTREACHED */
}
static TLstring	ccfile;
static TLint4	ccf;
static TLstring	rccfile;
static TLint4	rccf;
static TLstring	line;

static void getinfo (infoline, infoname, __x59)
TLstring	infoline;
TLstring	infoname;
TLstring	__x59;
{
    TLstring	infohead;
    TLstring	info;
    {
	TLstring	__x101;
	TL_TLS_TLSCAT(infoname, "=\"", __x101);
	TLSTRASS(4095, infohead, __x101);
    };
    TLSTRASS(4095, info, "");
    if (TL_TLS_TLSIND(infoline, infohead) != 0) {
	{
	    TLstring	__x102;
	    TL_TLS_TLSBXS(__x102, (TLint4) 0, (TLint4) (TL_TLS_TLSIND(infoline, infohead) + TL_TLS_TLSLEN(infohead)), infoline);
	    TLSTRASS(4095, info, __x102);
	};
	{
	    TLstring	__x103;
	    TL_TLS_TLSBXX(__x103, (TLint4) (TL_TLS_TLSIND(info, "\"") - 1), (TLint4) 1, info);
	    TLSTRASS(4095, info, __x103);
	};
    };
    {
	TLSTRASS(4095, __x59, info);
	return;
    };
    /* NOTREACHED */
}
static TLstring	system1name;
static TLstring	system2name;
static TLstring	granularity;
static TLstring	threshold;
static TLstring	minlines;
static TLstring	maxlines;
static TLstring	clonetype;
static TLstring	npcs;
static TLstring	npairs;
static TLstring	nclasses;
void TProg () {
    {
	TLstring	__x97;
	{
	    TLstring	__x96;
	    TL_TLI_TLIFA((TLint4) 1, __x96);
	    if ((strcmp(__x96, "") == 0) || ((TL_TLI_TLIFA((TLint4) 2, __x97), strcmp(__x97, "") == 0))) {
		TL_TLI_TLISS ((TLint4) 0, (TLint2) 2);
		TL_TLI_TLIPS ((TLint4) 0, "Usage:  tothml.x system_functions-clonepairs-withsource.xml system_functions-clonepairs-withsource.html", (TLint2) 0);
		TL_TLI_TLIPK ((TLint2) 0);
		TL_TLE_TLEQUIT ((TLint4) 1, (char *) 0, 0);
	    };
	};
    };
    {
	TLstring	__x98;
	TL_TLI_TLIFA((TLint4) 1, __x98);
	TLSTRASS(4095, ccfile, __x98);
    };
    TL_TLI_TLIOF ((TLnat2) 2, ccfile, &ccf);
    if (ccf == 0) {
	TL_TLI_TLISS ((TLint4) 0, (TLint2) 2);
	TL_TLI_TLIPS ((TLint4) 0, "*** Error: can\'t open sourced clone classes input file", (TLint2) 0);
	TL_TLI_TLIPK ((TLint2) 0);
	TL_TLE_TLEQUIT ((TLint4) 1, (char *) 0, 0);
    };
    {
	TLstring	__x99;
	TL_TLI_TLIFA((TLint4) 2, __x99);
	TLSTRASS(4095, rccfile, __x99);
    };
    TL_TLI_TLIOF ((TLnat2) 4, rccfile, &rccf);
    TL_TLI_TLISS ((TLint4) rccf, (TLint2) 2);
    TL_TLI_TLIPS ((TLint4) 0, "<html>", (TLint2) rccf);
    TL_TLI_TLIPK ((TLint2) rccf);
    TL_TLI_TLISS ((TLint4) rccf, (TLint2) 2);
    TL_TLI_TLIPS ((TLint4) 0, "<head>", (TLint2) rccf);
    TL_TLI_TLIPK ((TLint2) rccf);
    TL_TLI_TLISS ((TLint4) rccf, (TLint2) 2);
    TL_TLI_TLIPS ((TLint4) 0, "    <title>NiCad6 Clone Report</title>", (TLint2) rccf);
    TL_TLI_TLIPK ((TLint2) rccf);
    TL_TLI_TLISS ((TLint4) rccf, (TLint2) 2);
    TL_TLI_TLIPS ((TLint4) 0, "    <style type=\"text/css\">", (TLint2) rccf);
    TL_TLI_TLIPK ((TLint2) rccf);
    TL_TLI_TLISS ((TLint4) rccf, (TLint2) 2);
    TL_TLI_TLIPS ((TLint4) 0, "        body {font-family:sans-serif;}", (TLint2) rccf);
    TL_TLI_TLIPK ((TLint2) rccf);
    TL_TLI_TLISS ((TLint4) rccf, (TLint2) 2);
    TL_TLI_TLIPS ((TLint4) 0, "        table {background-color:white; border:0px; padding:0px; border-spacing:4px; width:auto; margin-left:30px; margin-right:auto;}", (TLint2) rccf);
    TL_TLI_TLIPK ((TLint2) rccf);
    TL_TLI_TLISS ((TLint4) rccf, (TLint2) 2);
    TL_TLI_TLIPS ((TLint4) 0, "        td {background-color:rgba(192,212,238,0.8); border:0px; padding:8px; width:auto; vertical-align:top; border-radius:8px}", (TLint2) rccf);
    TL_TLI_TLIPK ((TLint2) rccf);
    TL_TLI_TLISS ((TLint4) rccf, (TLint2) 2);
    TL_TLI_TLIPS ((TLint4) 0, "        pre {background-color:white; padding:4px;}", (TLint2) rccf);
    TL_TLI_TLIPK ((TLint2) rccf);
    TL_TLI_TLISS ((TLint4) rccf, (TLint2) 2);
    TL_TLI_TLIPS ((TLint4) 0, "        a {color:darkblue;}", (TLint2) rccf);
    TL_TLI_TLIPK ((TLint2) rccf);
    TL_TLI_TLISS ((TLint4) rccf, (TLint2) 2);
    TL_TLI_TLIPS ((TLint4) 0, "    </style>", (TLint2) rccf);
    TL_TLI_TLIPK ((TLint2) rccf);
    TL_TLI_TLISS ((TLint4) rccf, (TLint2) 2);
    TL_TLI_TLIPS ((TLint4) 0, "</head>", (TLint2) rccf);
    TL_TLI_TLIPK ((TLint2) rccf);
    TL_TLI_TLISS ((TLint4) rccf, (TLint2) 2);
    TL_TLI_TLIPS ((TLint4) 0, "<body>", (TLint2) rccf);
    TL_TLI_TLIPK ((TLint2) rccf);
    TL_TLI_TLISS ((TLint4) rccf, (TLint2) 2);
    TL_TLI_TLIPS ((TLint4) 0, "<h2>NiCad6 Clone Report</h2>", (TLint2) rccf);
    TL_TLI_TLIPK ((TLint2) rccf);
    TL_TLI_TLISS ((TLint4) ccf, (TLint2) 1);
    TL_TLI_TLIGSS((TLint4) 4095, line, (TLint2) ccf);
    if (strcmp(line, "<clones>") != 0) {
	TL_TLI_TLISS ((TLint4) 0, (TLint2) 2);
	TL_TLI_TLIPS ((TLint4) 0, "*** Error: malformed sourced clone classes input file", (TLint2) 0);
	TL_TLI_TLIPK ((TLint2) 0);
	TL_TLE_TLEQUIT ((TLint4) 1, (char *) 0, 0);
    };
    TL_TLI_TLISS ((TLint4) ccf, (TLint2) 1);
    TL_TLI_TLIGSS((TLint4) 4095, line, (TLint2) ccf);
    {
	TLstring	__x104;
	getinfo(line, "system", __x104);
	TLSTRASS(4095, system1name, __x104);
    };
    {
	TLstring	__x105;
	getinfo(line, "system2", __x105);
	TLSTRASS(4095, system2name, __x105);
    };
    {
	TLstring	__x106;
	getinfo(line, "granularity", __x106);
	TLSTRASS(4095, granularity, __x106);
    };
    {
	TLstring	__x107;
	getinfo(line, "threshold", __x107);
	TLSTRASS(4095, threshold, __x107);
    };
    {
	TLstring	__x108;
	getinfo(line, "minlines", __x108);
	TLSTRASS(4095, minlines, __x108);
    };
    {
	TLstring	__x109;
	getinfo(line, "maxlines", __x109);
	TLSTRASS(4095, maxlines, __x109);
    };
    TL_TLI_TLISS ((TLint4) 0, (TLint2) 2);
    TL_TLI_TLIPS ((TLint4) 0, granularity, (TLint2) 0);
    TL_TLI_TLIPK ((TLint2) 0);
    TL_TLI_TLISS ((TLint4) 0, (TLint2) 2);
    TL_TLI_TLIPS ((TLint4) 0, threshold, (TLint2) 0);
    TL_TLI_TLIPK ((TLint2) 0);
    TLSTRASS(4095, clonetype, "1");
    if (TL_TLS_TLSIND(granularity, "-blind") != 0) {
	TLSTRASS(4095, clonetype, "2");
    } else {
	if (TL_TLS_TLSIND(granularity, "-consistent") != 0) {
	    TLSTRASS(4095, clonetype, "2c");
	};
    };
    if (strcmp(threshold, "0%") != 0) {
	{
	    TLstring	__x110;
	    TL_TLS_TLSCAT("3-", clonetype, __x110);
	    TLSTRASS(4095, clonetype, __x110);
	};
    };
    TL_TLI_TLISS ((TLint4) ccf, (TLint2) 1);
    TL_TLI_TLIGSS((TLint4) 4095, line, (TLint2) ccf);
    {
	TLstring	__x111;
	getinfo(line, "npcs", __x111);
	TLSTRASS(4095, npcs, __x111);
    };
    {
	TLstring	__x112;
	getinfo(line, "npairs", __x112);
	TLSTRASS(4095, npairs, __x112);
    };
    TL_TLI_TLISS ((TLint4) ccf, (TLint2) 1);
    TL_TLI_TLIGSS((TLint4) 4095, line, (TLint2) ccf);
    TL_TLI_TLISS ((TLint4) ccf, (TLint2) 1);
    TL_TLI_TLIGSS((TLint4) 4095, line, (TLint2) ccf);
    TLSTRASS(4095, nclasses, "");
    if (TL_TLS_TLSIND(line, "<classinfo ") == 1) {
	{
	    TLstring	__x113;
	    getinfo(line, "nclasses", __x113);
	    TLSTRASS(4095, nclasses, __x113);
	};
	TL_TLI_TLISS ((TLint4) ccf, (TLint2) 1);
	TL_TLI_TLIGSS((TLint4) 4095, line, (TLint2) ccf);
    };
    TL_TLI_TLISS ((TLint4) rccf, (TLint2) 2);
    TL_TLI_TLIPS ((TLint4) 0, "<table>", (TLint2) rccf);
    TL_TLI_TLIPK ((TLint2) rccf);
    TL_TLI_TLISS ((TLint4) rccf, (TLint2) 2);
    TL_TLI_TLIPS ((TLint4) 0, "<tr style=\"font-size:14pt\">", (TLint2) rccf);
    TL_TLI_TLIPK ((TLint2) rccf);
    if (strcmp(system2name, "") == 0) {
	TL_TLI_TLISS ((TLint4) rccf, (TLint2) 2);
	TL_TLI_TLIPS ((TLint4) 0, "<td><b>System:</b> &nbsp; ", (TLint2) rccf);
	TL_TLI_TLIPS ((TLint4) 0, system1name, (TLint2) rccf);
	TL_TLI_TLIPS ((TLint4) 0, "</td>", (TLint2) rccf);
	TL_TLI_TLIPK ((TLint2) rccf);
    } else {
	TL_TLI_TLISS ((TLint4) rccf, (TLint2) 2);
	TL_TLI_TLIPS ((TLint4) 0, "<td><b>System 1:</b> &nbsp; ", (TLint2) rccf);
	TL_TLI_TLIPS ((TLint4) 0, system1name, (TLint2) rccf);
	TL_TLI_TLIPS ((TLint4) 0, "</td>", (TLint2) rccf);
	TL_TLI_TLIPK ((TLint2) rccf);
	TL_TLI_TLISS ((TLint4) rccf, (TLint2) 2);
	TL_TLI_TLIPS ((TLint4) 0, "<td><b>System 2:</b> &nbsp; ", (TLint2) rccf);
	TL_TLI_TLIPS ((TLint4) 0, system2name, (TLint2) rccf);
	TL_TLI_TLIPS ((TLint4) 0, "</td>", (TLint2) rccf);
	TL_TLI_TLIPK ((TLint2) rccf);
    };
    TL_TLI_TLISS ((TLint4) rccf, (TLint2) 2);
    TL_TLI_TLIPS ((TLint4) 0, "<td><b>Clone pairs:</b> &nbsp; ", (TLint2) rccf);
    TL_TLI_TLIPS ((TLint4) 0, npairs, (TLint2) rccf);
    TL_TLI_TLIPS ((TLint4) 0, "</td>", (TLint2) rccf);
    TL_TLI_TLIPK ((TLint2) rccf);
    if (strcmp(nclasses, "") != 0) {
	TL_TLI_TLISS ((TLint4) rccf, (TLint2) 2);
	TL_TLI_TLIPS ((TLint4) 0, "<td><b>Clone classes:</b> &nbsp; ", (TLint2) rccf);
	TL_TLI_TLIPS ((TLint4) 0, nclasses, (TLint2) rccf);
	TL_TLI_TLIPS ((TLint4) 0, "</td>", (TLint2) rccf);
	TL_TLI_TLIPK ((TLint2) rccf);
    };
    TL_TLI_TLISS ((TLint4) rccf, (TLint2) 2);
    TL_TLI_TLIPS ((TLint4) 0, "</tr>", (TLint2) rccf);
    TL_TLI_TLIPK ((TLint2) rccf);
    TL_TLI_TLISS ((TLint4) rccf, (TLint2) 2);
    TL_TLI_TLIPS ((TLint4) 0, "<tr style=\"font-size:12pt\">", (TLint2) rccf);
    TL_TLI_TLIPK ((TLint2) rccf);
    TL_TLI_TLISS ((TLint4) rccf, (TLint2) 2);
    TL_TLI_TLIPS ((TLint4) 0, "<td style=\"background-color:white\">Clone type: &nbsp; ", (TLint2) rccf);
    TL_TLI_TLIPS ((TLint4) 0, clonetype, (TLint2) rccf);
    TL_TLI_TLIPS ((TLint4) 0, "</td>", (TLint2) rccf);
    TL_TLI_TLIPK ((TLint2) rccf);
    TL_TLI_TLISS ((TLint4) rccf, (TLint2) 2);
    TL_TLI_TLIPS ((TLint4) 0, "<td style=\"background-color:white\">Granularity: &nbsp; ", (TLint2) rccf);
    TL_TLI_TLIPS ((TLint4) 0, granularity, (TLint2) rccf);
    TL_TLI_TLIPS ((TLint4) 0, "</td>", (TLint2) rccf);
    TL_TLI_TLIPK ((TLint2) rccf);
    TL_TLI_TLISS ((TLint4) rccf, (TLint2) 2);
    TL_TLI_TLIPS ((TLint4) 0, "<td style=\"background-color:white\">Max diff threshold: &nbsp; ", (TLint2) rccf);
    TL_TLI_TLIPS ((TLint4) 0, threshold, (TLint2) rccf);
    TL_TLI_TLIPS ((TLint4) 0, "</td>", (TLint2) rccf);
    TL_TLI_TLIPK ((TLint2) rccf);
    TL_TLI_TLISS ((TLint4) rccf, (TLint2) 2);
    TL_TLI_TLIPS ((TLint4) 0, "<td style=\"background-color:white\">Clone size: &nbsp; ", (TLint2) rccf);
    TL_TLI_TLIPS ((TLint4) 0, minlines, (TLint2) rccf);
    TL_TLI_TLIPS ((TLint4) 0, " - ", (TLint2) rccf);
    TL_TLI_TLIPS ((TLint4) 0, maxlines, (TLint2) rccf);
    TL_TLI_TLIPS ((TLint4) 0, " lines", (TLint2) rccf);
    TL_TLI_TLIPS ((TLint4) 0, "</td>", (TLint2) rccf);
    TL_TLI_TLIPK ((TLint2) rccf);
    TL_TLI_TLISS ((TLint4) rccf, (TLint2) 2);
    TL_TLI_TLIPS ((TLint4) 0, "<td style=\"background-color:white\">Total ", (TLint2) rccf);
    TL_TLI_TLIPS ((TLint4) 0, granularity, (TLint2) rccf);
    TL_TLI_TLIPS ((TLint4) 0, ": &nbsp; ", (TLint2) rccf);
    TL_TLI_TLIPS ((TLint4) 0, npcs, (TLint2) rccf);
    TL_TLI_TLIPS ((TLint4) 0, "</td>", (TLint2) rccf);
    TL_TLI_TLIPK ((TLint2) rccf);
    TL_TLI_TLISS ((TLint4) rccf, (TLint2) 2);
    TL_TLI_TLIPS ((TLint4) 0, "</tr>", (TLint2) rccf);
    TL_TLI_TLIPK ((TLint2) rccf);
    TL_TLI_TLISS ((TLint4) rccf, (TLint2) 2);
    TL_TLI_TLIPS ((TLint4) 0, "</table>", (TLint2) rccf);
    TL_TLI_TLIPK ((TLint2) rccf);
    for(;;) {
	TLstring	nclassclones;
	if (TL_TLI_TLIEOF((TLint4) ccf)) {
	    break;
	};
	TLSTRASS(4095, nclassclones, "2");
	if ((TL_TLS_TLSIND(line, "<clone ") == 1) || (TL_TLS_TLSIND(line, "<class ") == 1)) {
	    TLint4	clonesperline;
	    TLint4	c;
	    if (TL_TLS_TLSIND(line, "<clone ") == 1) {
		TLstring	pairlines;
		TLstring	similarity;
		{
		    TLstring	__x114;
		    TL_TLS_TLSBXX(__x114, (TLint4) (TL_TLS_TLSIND(line, "\" similarity=") - 1), (TLint4) (TL_TLS_TLSIND(line, "nlines=\"") + TL_TLS_TLSLEN("nlines=\"")), line);
		    TLSTRASS(4095, pairlines, __x114);
		};
		{
		    TLstring	__x115;
		    TL_TLS_TLSBXX(__x115, (TLint4) (TL_TLS_TLSIND(line, "\">") - 1), (TLint4) (TL_TLS_TLSIND(line, "similarity=\"") + TL_TLS_TLSLEN("similarity=\"")), line);
		    TLSTRASS(4095, similarity, __x115);
		};
		TL_TLI_TLISS ((TLint4) rccf, (TLint2) 2);
		TL_TLI_TLIPS ((TLint4) 0, "<br>", (TLint2) rccf);
		TL_TLI_TLIPK ((TLint2) rccf);
		TL_TLI_TLISS ((TLint4) rccf, (TLint2) 2);
		TL_TLI_TLIPS ((TLint4) 0, "<table style=\"width:1000px; border:2px solid lightgrey; border-radius:8px;\">", (TLint2) rccf);
		TL_TLI_TLIPK ((TLint2) rccf);
		TL_TLI_TLISS ((TLint4) rccf, (TLint2) 2);
		TL_TLI_TLIPS ((TLint4) 0, "<tr><td style=\"background-color:white\">", (TLint2) rccf);
		TL_TLI_TLIPK ((TLint2) rccf);
		TL_TLI_TLISS ((TLint4) rccf, (TLint2) 2);
		TL_TLI_TLIPS ((TLint4) 0, "<p style=\"font-size:14pt\">", (TLint2) rccf);
		TL_TLI_TLISS ((TLint4) rccf, (TLint2) 2);
		TL_TLI_TLIPS ((TLint4) 0, "<b>Clone pair:</b> &nbsp; nominal size ", (TLint2) rccf);
		TL_TLI_TLIPS ((TLint4) 0, pairlines, (TLint2) rccf);
		TL_TLI_TLIPS ((TLint4) 0, " lines, similarity ", (TLint2) rccf);
		TL_TLI_TLIPS ((TLint4) 0, similarity, (TLint2) rccf);
		TL_TLI_TLIPS ((TLint4) 0, "%", (TLint2) rccf);
		TL_TLI_TLISS ((TLint4) rccf, (TLint2) 2);
		TL_TLI_TLIPS ((TLint4) 0, "</p>", (TLint2) rccf);
		TL_TLI_TLIPK ((TLint2) rccf);
		TL_TLI_TLISS ((TLint4) rccf, (TLint2) 2);
		TL_TLI_TLIPS ((TLint4) 0, "<table cellpadding=4 border=2>", (TLint2) rccf);
		TL_TLI_TLIPK ((TLint2) rccf);
	    } else {
		TLstring	classid;
		TLstring	classlines;
		TLstring	similarity;
		{
		    TLstring	__x116;
		    TL_TLS_TLSBXX(__x116, (TLint4) (TL_TLS_TLSIND(line, "\" nclones=") - 1), (TLint4) (TL_TLS_TLSIND(line, "classid=\"") + TL_TLS_TLSLEN("classid=\"")), line);
		    TLSTRASS(4095, classid, __x116);
		};
		{
		    TLstring	__x117;
		    TL_TLS_TLSBXX(__x117, (TLint4) (TL_TLS_TLSIND(line, "\" nlines=") - 1), (TLint4) (TL_TLS_TLSIND(line, "nclones=\"") + TL_TLS_TLSLEN("nclones=\"")), line);
		    TLSTRASS(4095, nclassclones, __x117);
		};
		{
		    TLstring	__x118;
		    TL_TLS_TLSBXX(__x118, (TLint4) (TL_TLS_TLSIND(line, "\" similarity=") - 1), (TLint4) (TL_TLS_TLSIND(line, "nlines=\"") + TL_TLS_TLSLEN("nlines=\"")), line);
		    TLSTRASS(4095, classlines, __x118);
		};
		{
		    TLstring	__x119;
		    TL_TLS_TLSBXX(__x119, (TLint4) (TL_TLS_TLSIND(line, "\">") - 1), (TLint4) (TL_TLS_TLSIND(line, "similarity=\"") + TL_TLS_TLSLEN("similarity=\"")), line);
		    TLSTRASS(4095, similarity, __x119);
		};
		TL_TLI_TLISS ((TLint4) rccf, (TLint2) 2);
		TL_TLI_TLIPS ((TLint4) 0, "<br>", (TLint2) rccf);
		TL_TLI_TLIPK ((TLint2) rccf);
		TL_TLI_TLISS ((TLint4) rccf, (TLint2) 2);
		TL_TLI_TLIPS ((TLint4) 0, "<table style=\"width:1000px; border:2px solid lightgrey; border-radius:8px;\">", (TLint2) rccf);
		TL_TLI_TLIPK ((TLint2) rccf);
		TL_TLI_TLISS ((TLint4) rccf, (TLint2) 2);
		TL_TLI_TLIPS ((TLint4) 0, "<tr><td style=\"background-color:white\">", (TLint2) rccf);
		TL_TLI_TLIPK ((TLint2) rccf);
		TL_TLI_TLISS ((TLint4) rccf, (TLint2) 2);
		TL_TLI_TLIPS ((TLint4) 0, "<p style=\"font-size:14pt\">", (TLint2) rccf);
		TL_TLI_TLISS ((TLint4) rccf, (TLint2) 2);
		TL_TLI_TLIPS ((TLint4) 0, "<b>Class ", (TLint2) rccf);
		TL_TLI_TLIPS ((TLint4) 0, classid, (TLint2) rccf);
		TL_TLI_TLIPS ((TLint4) 0, ":</b> &nbsp; ", (TLint2) rccf);
		TL_TLI_TLIPS ((TLint4) 0, nclassclones, (TLint2) rccf);
		TL_TLI_TLIPS ((TLint4) 0, " fragments, nominal size ", (TLint2) rccf);
		TL_TLI_TLIPS ((TLint4) 0, classlines, (TLint2) rccf);
		TL_TLI_TLIPS ((TLint4) 0, " lines, similarity ", (TLint2) rccf);
		TL_TLI_TLIPS ((TLint4) 0, similarity, (TLint2) rccf);
		TL_TLI_TLIPS ((TLint4) 0, "%", (TLint2) rccf);
		TL_TLI_TLISS ((TLint4) rccf, (TLint2) 2);
		TL_TLI_TLIPS ((TLint4) 0, "</p>", (TLint2) rccf);
		TL_TLI_TLIPK ((TLint2) rccf);
		TL_TLI_TLISS ((TLint4) rccf, (TLint2) 2);
		TL_TLI_TLIPS ((TLint4) 0, "<table cellpadding=4 border=2>", (TLint2) rccf);
		TL_TLI_TLIPK ((TLint2) rccf);
	    };
	    clonesperline = TL_TLS_TLSVSI(nclassclones, (TLint4) 10);
	    for(;;) {
		if (clonesperline <= 5) {
		    break;
		};
		clonesperline = clonesperline / 2;
	    };
	    TL_TLI_TLISS ((TLint4) rccf, (TLint2) 2);
	    TL_TLI_TLIPS ((TLint4) 0, "<tr>", (TLint2) rccf);
	    TL_TLI_TLIPK ((TLint2) rccf);
	    c = 0;
	    for(;;) {
		if (TL_TLI_TLIEOF((TLint4) ccf)) {
		    break;
		};
		TL_TLI_TLISS ((TLint4) ccf, (TLint2) 1);
		TL_TLI_TLIGSS((TLint4) 4095, line, (TLint2) ccf);
		if ((strcmp(line, "</clone>") == 0) || (strcmp(line, "</class>") == 0)) {
		    break;
		};
		if (TL_TLS_TLSIND(line, "<source") == 1) {
		    TLstring	srcfile;
		    TLstring	startline;
		    TLstring	endline;
		    TLstring	pcid;
		    TLstring	shortfile;
		    {
			TLstring	__x120;
			TL_TLS_TLSBXX(__x120, (TLint4) (TL_TLS_TLSIND(line, "\" startline=") - 1), (TLint4) (TL_TLS_TLSIND(line, "file=\"") + TL_TLS_TLSLEN("file=\"")), line);
			TLSTRASS(4095, srcfile, __x120);
		    };
		    {
			TLstring	__x121;
			TL_TLS_TLSBXX(__x121, (TLint4) (TL_TLS_TLSIND(line, "\" endline=") - 1), (TLint4) (TL_TLS_TLSIND(line, "startline=\"") + TL_TLS_TLSLEN("startline=\"")), line);
			TLSTRASS(4095, startline, __x121);
		    };
		    {
			TLstring	__x122;
			TL_TLS_TLSBXX(__x122, (TLint4) (TL_TLS_TLSIND(line, "\" pcid=") - 1), (TLint4) (TL_TLS_TLSIND(line, "endline=\"") + TL_TLS_TLSLEN("endline=\"")), line);
			TLSTRASS(4095, endline, __x122);
		    };
		    {
			TLstring	__x123;
			TL_TLS_TLSBXX(__x123, (TLint4) (TL_TLS_TLSIND(line, "\">") - 1), (TLint4) (TL_TLS_TLSIND(line, "pcid=\"") + TL_TLS_TLSLEN("pcid=\"")), line);
			TLSTRASS(4095, pcid, __x123);
		    };
		    TLSTRASS(4095, shortfile, srcfile);
		    {
			TLstring	__x125;
			TL_TLS_TLSCAT("/", system1name, __x125);
			{
			    TLstring	__x124;
			    TL_TLS_TLSCAT(__x125, "/", __x124);
			    if (TL_TLS_TLSIND(srcfile, __x124) != 0) {
				{
				    TLstring	__x128;
				    TL_TLS_TLSCAT("/", system1name, __x128);
				    {
					TLstring	__x127;
					TL_TLS_TLSCAT(__x128, "/", __x127);
					{
					    TLstring	__x126;
					    TL_TLS_TLSBXS(__x126, (TLint4) 0, (TLint4) (TL_TLS_TLSIND(srcfile, __x127) + 1), srcfile);
					    {
						TLstring	__x129;
						strip(__x126, __x129);
						TLSTRASS(4095, shortfile, __x129);
					    };
					};
				    };
				};
			    } else {
				{
				    TLstring	__x131;
				    TL_TLS_TLSCAT("/", system2name, __x131);
				    {
					TLstring	__x130;
					TL_TLS_TLSCAT(__x131, "/", __x130);
					if (TL_TLS_TLSIND(srcfile, __x130) != 0) {
					    {
						TLstring	__x134;
						TL_TLS_TLSCAT("/", system2name, __x134);
						{
						    TLstring	__x133;
						    TL_TLS_TLSCAT(__x134, "/", __x133);
						    {
							TLstring	__x132;
							TL_TLS_TLSBXS(__x132, (TLint4) 0, (TLint4) (TL_TLS_TLSIND(srcfile, __x133) + 1), srcfile);
							{
							    TLstring	__x135;
							    strip(__x132, __x135);
							    TLSTRASS(4095, shortfile, __x135);
							};
						    };
						};
					    };
					};
				    };
				};
			    };
			};
		    };
		    TL_TLI_TLISS ((TLint4) rccf, (TLint2) 2);
		    TL_TLI_TLIPS ((TLint4) 0, "<td width=\"auto\">", (TLint2) rccf);
		    TL_TLI_TLIPK ((TLint2) rccf);
		    TL_TLI_TLISS ((TLint4) rccf, (TLint2) 2);
		    TL_TLI_TLIPS ((TLint4) 0, "<a onclick=\"javascript:ShowHide(\'frag", (TLint2) rccf);
		    TL_TLI_TLIPS ((TLint4) 0, pcid, (TLint2) rccf);
		    TL_TLI_TLIPS ((TLint4) 0, "\')\" href=\"javascript:;\">", (TLint2) rccf);
		    TL_TLI_TLIPK ((TLint2) rccf);
		    TL_TLI_TLISS ((TLint4) rccf, (TLint2) 2);
		    TL_TLI_TLIPS ((TLint4) 0, shortfile, (TLint2) rccf);
		    TL_TLI_TLIPS ((TLint4) 0, ": ", (TLint2) rccf);
		    TL_TLI_TLIPS ((TLint4) 0, startline, (TLint2) rccf);
		    TL_TLI_TLIPS ((TLint4) 0, "-", (TLint2) rccf);
		    TL_TLI_TLIPS ((TLint4) 0, endline, (TLint2) rccf);
		    TL_TLI_TLIPK ((TLint2) rccf);
		    TL_TLI_TLISS ((TLint4) rccf, (TLint2) 2);
		    TL_TLI_TLIPS ((TLint4) 0, "</a>", (TLint2) rccf);
		    TL_TLI_TLIPK ((TLint2) rccf);
		    TL_TLI_TLISS ((TLint4) rccf, (TLint2) 2);
		    TL_TLI_TLIPS ((TLint4) 0, "<div class=\"mid\" id=\"frag", (TLint2) rccf);
		    TL_TLI_TLIPS ((TLint4) 0, pcid, (TLint2) rccf);
		    TL_TLI_TLIPS ((TLint4) 0, "\" style=\"display:none\"><pre>", (TLint2) rccf);
		    TL_TLI_TLIPK ((TLint2) rccf);
		    for(;;) {
			TLint4	lengthline;
			if (TL_TLI_TLIEOF((TLint4) ccf)) {
			    break;
			};
			for(;;) {
			    TL_TLI_TLISS ((TLint4) ccf, (TLint2) 1);
			    TL_TLI_TLIGSS((TLint4) 4095, line, (TLint2) ccf);
			    if (TL_TLI_TLIEOF((TLint4) ccf) || (TL_TLS_TLSLEN(line) < 4095)) {
				break;
			    };
			    {
				TLstring	__x136;
				TL_TLS_TLSBXX(__x136, (TLint4) 1000, (TLint4) 1, line);
				{
				    TLstring	__x137;
				    encode(__x136, __x137);
				    TL_TLI_TLISS ((TLint4) rccf, (TLint2) 2);
				    TL_TLI_TLIPS ((TLint4) 0, __x137, (TLint2) rccf);
				};
			    };
			    {
				TLstring	__x138;
				TL_TLS_TLSBXX(__x138, (TLint4) 2000, (TLint4) 1001, line);
				{
				    TLstring	__x139;
				    encode(__x138, __x139);
				    TL_TLI_TLISS ((TLint4) rccf, (TLint2) 2);
				    TL_TLI_TLIPS ((TLint4) 0, __x139, (TLint2) rccf);
				};
			    };
			    {
				TLstring	__x140;
				TL_TLS_TLSBXX(__x140, (TLint4) 3000, (TLint4) 2001, line);
				{
				    TLstring	__x141;
				    encode(__x140, __x141);
				    TL_TLI_TLISS ((TLint4) rccf, (TLint2) 2);
				    TL_TLI_TLIPS ((TLint4) 0, __x141, (TLint2) rccf);
				};
			    };
			    {
				TLstring	__x142;
				TL_TLS_TLSBXS(__x142, (TLint4) 0, (TLint4) 3001, line);
				{
				    TLstring	__x143;
				    encode(__x142, __x143);
				    TL_TLI_TLISS ((TLint4) rccf, (TLint2) 2);
				    TL_TLI_TLIPS ((TLint4) 0, __x143, (TLint2) rccf);
				};
			    };
			};
			if (strcmp(line, "</source>") == 0) {
			    break;
			};
			lengthline = TL_TLS_TLSLEN(line);
			if (lengthline > 3000) {
			    {
				TLstring	__x144;
				TL_TLS_TLSBXX(__x144, (TLint4) 1000, (TLint4) 1, line);
				{
				    TLstring	__x145;
				    encode(__x144, __x145);
				    TL_TLI_TLISS ((TLint4) rccf, (TLint2) 2);
				    TL_TLI_TLIPS ((TLint4) 0, __x145, (TLint2) rccf);
				};
			    };
			    {
				TLstring	__x146;
				TL_TLS_TLSBXX(__x146, (TLint4) 2000, (TLint4) 1001, line);
				{
				    TLstring	__x147;
				    encode(__x146, __x147);
				    TL_TLI_TLISS ((TLint4) rccf, (TLint2) 2);
				    TL_TLI_TLIPS ((TLint4) 0, __x147, (TLint2) rccf);
				};
			    };
			    {
				TLstring	__x148;
				TL_TLS_TLSBXX(__x148, (TLint4) 3000, (TLint4) 2001, line);
				{
				    TLstring	__x149;
				    encode(__x148, __x149);
				    TL_TLI_TLISS ((TLint4) rccf, (TLint2) 2);
				    TL_TLI_TLIPS ((TLint4) 0, __x149, (TLint2) rccf);
				};
			    };
			    {
				TLstring	__x150;
				TL_TLS_TLSBXS(__x150, (TLint4) 0, (TLint4) 3001, line);
				{
				    TLstring	__x151;
				    encode(__x150, __x151);
				    TL_TLI_TLISS ((TLint4) rccf, (TLint2) 2);
				    TL_TLI_TLIPS ((TLint4) 0, __x151, (TLint2) rccf);
				};
			    };
			} else {
			    if (lengthline > 2000) {
				{
				    TLstring	__x152;
				    TL_TLS_TLSBXX(__x152, (TLint4) 1000, (TLint4) 1, line);
				    {
					TLstring	__x153;
					encode(__x152, __x153);
					TL_TLI_TLISS ((TLint4) rccf, (TLint2) 2);
					TL_TLI_TLIPS ((TLint4) 0, __x153, (TLint2) rccf);
				    };
				};
				{
				    TLstring	__x154;
				    TL_TLS_TLSBXX(__x154, (TLint4) 2000, (TLint4) 1001, line);
				    {
					TLstring	__x155;
					encode(__x154, __x155);
					TL_TLI_TLISS ((TLint4) rccf, (TLint2) 2);
					TL_TLI_TLIPS ((TLint4) 0, __x155, (TLint2) rccf);
				    };
				};
				{
				    TLstring	__x156;
				    TL_TLS_TLSBXS(__x156, (TLint4) 0, (TLint4) 2001, line);
				    {
					TLstring	__x157;
					encode(__x156, __x157);
					TL_TLI_TLISS ((TLint4) rccf, (TLint2) 2);
					TL_TLI_TLIPS ((TLint4) 0, __x157, (TLint2) rccf);
				    };
				};
			    } else {
				if (lengthline > 1000) {
				    {
					TLstring	__x158;
					TL_TLS_TLSBXX(__x158, (TLint4) 1000, (TLint4) 1, line);
					{
					    TLstring	__x159;
					    encode(__x158, __x159);
					    TL_TLI_TLISS ((TLint4) rccf, (TLint2) 2);
					    TL_TLI_TLIPS ((TLint4) 0, __x159, (TLint2) rccf);
					};
				    };
				    {
					TLstring	__x160;
					TL_TLS_TLSBXS(__x160, (TLint4) 0, (TLint4) 1001, line);
					{
					    TLstring	__x161;
					    encode(__x160, __x161);
					    TL_TLI_TLISS ((TLint4) rccf, (TLint2) 2);
					    TL_TLI_TLIPS ((TLint4) 0, __x161, (TLint2) rccf);
					};
				    };
				} else {
				    {
					TLstring	__x162;
					encode(line, __x162);
					TL_TLI_TLISS ((TLint4) rccf, (TLint2) 2);
					TL_TLI_TLIPS ((TLint4) 0, __x162, (TLint2) rccf);
					TL_TLI_TLIPK ((TLint2) rccf);
				    };
				};
			    };
			};
		    };
		    TL_TLI_TLISS ((TLint4) rccf, (TLint2) 2);
		    TL_TLI_TLIPS ((TLint4) 0, "</pre></div>", (TLint2) rccf);
		    TL_TLI_TLIPK ((TLint2) rccf);
		    TL_TLI_TLISS ((TLint4) rccf, (TLint2) 2);
		    TL_TLI_TLIPS ((TLint4) 0, "</td>", (TLint2) rccf);
		    TL_TLI_TLIPK ((TLint2) rccf);
		};
		if (strcmp(line, "</source>") != 0) {
		    TL_TLI_TLISS ((TLint4) 0, (TLint2) 2);
		    TL_TLI_TLIPS ((TLint4) 0, "*** Error: clone source file synchronization error", (TLint2) 0);
		    TL_TLI_TLIPK ((TLint2) 0);
		    TL_TLE_TLEQUIT ((TLint4) 1, (char *) 0, 0);
		};
		c += 1;
		if ((c % clonesperline) == 0) {
		    TL_TLI_TLISS ((TLint4) rccf, (TLint2) 2);
		    TL_TLI_TLIPS ((TLint4) 0, "</tr><tr>", (TLint2) rccf);
		    TL_TLI_TLIPK ((TLint2) rccf);
		};
	    };
	    TL_TLI_TLISS ((TLint4) rccf, (TLint2) 2);
	    TL_TLI_TLIPS ((TLint4) 0, "</tr>", (TLint2) rccf);
	    TL_TLI_TLIPK ((TLint2) rccf);
	    if ((strcmp(line, "</clone>") != 0) && (strcmp(line, "</class>") != 0)) {
		TL_TLI_TLISS ((TLint4) 0, (TLint2) 2);
		TL_TLI_TLIPS ((TLint4) 0, "*** Error: clone pair / class file synchronization error", (TLint2) 0);
		TL_TLI_TLIPK ((TLint2) 0);
		TL_TLE_TLEQUIT ((TLint4) 1, (char *) 0, 0);
	    };
	    TL_TLI_TLISS ((TLint4) rccf, (TLint2) 2);
	    TL_TLI_TLIPS ((TLint4) 0, "</table>", (TLint2) rccf);
	    TL_TLI_TLIPK ((TLint2) rccf);
	    TL_TLI_TLISS ((TLint4) rccf, (TLint2) 2);
	    TL_TLI_TLIPS ((TLint4) 0, "</td></tr>", (TLint2) rccf);
	    TL_TLI_TLIPK ((TLint2) rccf);
	    TL_TLI_TLISS ((TLint4) rccf, (TLint2) 2);
	    TL_TLI_TLIPS ((TLint4) 0, "</table>", (TLint2) rccf);
	    TL_TLI_TLIPK ((TLint2) rccf);
	};
	TL_TLI_TLISS ((TLint4) ccf, (TLint2) 1);
	TL_TLI_TLIGSS((TLint4) 4095, line, (TLint2) ccf);
    };
    TL_TLI_TLISS ((TLint4) rccf, (TLint2) 2);
    TL_TLI_TLIPS ((TLint4) 0, "<script language=\"JavaScript\">", (TLint2) rccf);
    TL_TLI_TLIPK ((TLint2) rccf);
    TL_TLI_TLISS ((TLint4) rccf, (TLint2) 2);
    TL_TLI_TLIPS ((TLint4) 0, "function ShowHide(divId) { ", (TLint2) rccf);
    TL_TLI_TLIPK ((TLint2) rccf);
    TL_TLI_TLISS ((TLint4) rccf, (TLint2) 2);
    TL_TLI_TLIPS ((TLint4) 0, "    if(document.getElementById(divId).style.display == \'none\') {", (TLint2) rccf);
    TL_TLI_TLIPK ((TLint2) rccf);
    TL_TLI_TLISS ((TLint4) rccf, (TLint2) 2);
    TL_TLI_TLIPS ((TLint4) 0, "        document.getElementById(divId).style.display=\'block\';", (TLint2) rccf);
    TL_TLI_TLIPK ((TLint2) rccf);
    TL_TLI_TLISS ((TLint4) rccf, (TLint2) 2);
    TL_TLI_TLIPS ((TLint4) 0, "    } else { ", (TLint2) rccf);
    TL_TLI_TLIPK ((TLint2) rccf);
    TL_TLI_TLISS ((TLint4) rccf, (TLint2) 2);
    TL_TLI_TLIPS ((TLint4) 0, "        document.getElementById(divId).style.display = \'none\';", (TLint2) rccf);
    TL_TLI_TLIPK ((TLint2) rccf);
    TL_TLI_TLISS ((TLint4) rccf, (TLint2) 2);
    TL_TLI_TLIPS ((TLint4) 0, "    } ", (TLint2) rccf);
    TL_TLI_TLIPK ((TLint2) rccf);
    TL_TLI_TLISS ((TLint4) rccf, (TLint2) 2);
    TL_TLI_TLIPS ((TLint4) 0, "}", (TLint2) rccf);
    TL_TLI_TLIPK ((TLint2) rccf);
    TL_TLI_TLISS ((TLint4) rccf, (TLint2) 2);
    TL_TLI_TLIPS ((TLint4) 0, "</script>", (TLint2) rccf);
    TL_TLI_TLIPK ((TLint2) rccf);
    TL_TLI_TLISS ((TLint4) rccf, (TLint2) 2);
    TL_TLI_TLIPS ((TLint4) 0, "</body>", (TLint2) rccf);
    TL_TLI_TLIPK ((TLint2) rccf);
    TL_TLI_TLISS ((TLint4) rccf, (TLint2) 2);
    TL_TLI_TLIPS ((TLint4) 0, "</html>", (TLint2) rccf);
    TL_TLI_TLIPK ((TLint2) rccf);
    TL_TLI_TLICL ((TLint4) ccf);
    TL_TLI_TLICL ((TLint4) rccf);
}
