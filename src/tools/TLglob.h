/*
 * Adapted with permission from :
 *
 * Interface for Turing Plus to C translator
 * (c) 1987,1988,1989,1990 Holt Software Associates Inc.
 * All rights reserved.
 *
 * (These definitions may have to change from machine to machine.)
 *
 */

/* Updated library naming conventions to T+ 6.0 standard - JRC 11.7.18 */
/* Revised exception handling to be consistent with T+ 6.0 standard - JRC 11.7.18 */

/* Revised to be both 32- and 64-bit compatible - JRC 11.8.15 */
/* Removed obsolete SYS5 signal handling logic - JRC 11.8.15 */
/* Added missing implicit includes - JRC 11.8.15 */
 
/* Fixed bug in file table overflow handling -- JRC 21.8.95 */
/* Changed preprocessor directives to be legal in old non-ANSI C -- JRC 14.19.95 */
/* Added setting of quitCode to conform to new signal handling -- JRC 4.1.97 */
/* Added heap memory map to assist in converting to re-entrant subroutine -- JRC 16.5.97 */
/* Added TL_RevertSignalHandlers to assist in converting to re-entrant subroutine -- JRC 20.5.97 */
/* Fixed another bug in file table overflow on too many arguments -- JRC 27.3.08 */

/* TLE - Signal handling routines */
#include <setjmp.h>
struct TLHAREA {
	int		quitCode;
	jmp_buf		quit_env;
	struct TLHAREA * old_handlerArea;
} *TL_handlerArea;
struct TLHAREA * TL_currentHandlerArea;
struct TLHAREA defaultHandlerArea;

/* TLB - memory management routines */
#include <stdlib.h>
void *TL_mallocs[100];
int TL_nextmalloc;

/* TLI - I/O routines */
#include <stdio.h>
#define READ_MODE 0
#define WRITE_MODE 1
FILE *TL_files[25];
char *TL_filenames[25];
char TL_filemode[25];
int TL_nextfile;
char TL_pattern[25];
int TL_TLI_lookahead;

/* Program parameters */
int TL_TLI_TLIARC;
char **TL_TLI_TLIARV;

/* Signal handling */
#ifdef BSD
#include <signal.h>
#endif

void TL_RevertSignalHandlers ()
    {
	/* revert to default signal handlers */
#ifdef BSD
	/* Version using BSD signals */
	
	if (signal(SIGINT, SIG_IGN) != SIG_IGN) {
	    (void) signal(SIGINT, SIG_DFL);
	}
	if (signal(SIGILL, SIG_IGN) != SIG_IGN) {
	    (void) signal(SIGILL, SIG_DFL);
	}
	if (signal(SIGFPE, SIG_IGN) != SIG_IGN) {
	    (void) signal(SIGFPE, SIG_DFL);
	}
#ifdef SIGBUS
	if (signal(SIGBUS, SIG_IGN) != SIG_IGN) {
	    (void) signal(SIGBUS, SIG_DFL);
	}
#endif
	if (signal(SIGSEGV, SIG_IGN) != SIG_IGN) {
	    (void) signal(SIGSEGV, SIG_DFL);
	}

#endif
    }


void TL_SignalHandler (signalNo)
    int signalNo;
    {
	/* revert to default signal handlers */

	TL_RevertSignalHandlers ();

	/* print the appropriate message */
#ifdef BSD
	/* Version using BSD signals */

	switch (signalNo) {
	    case SIGINT:
		fputs ("Program terminated\n", stderr);
		break;
	    case SIGILL:
		fputs ("Illegal instruction\n", stderr);
		break;
	    case SIGFPE:
		fputs ("Floating point exception\n", stderr);
		break;
#ifdef SIGBUS
	    case SIGBUS:
		fputs ("Bus error\n", stderr);
		break;
#endif
	    case SIGSEGV:
		fputs ("Segmentation violation\n", stderr);
		break;
	    default:
		fprintf (stderr, "TXL ERROR: Unexpected signal %d\n", signalNo);
		break;
	}

	/* call the Turing handler */
	TL_currentHandlerArea = TL_handlerArea;
	TL_currentHandlerArea->quitCode = signalNo;
        if (TL_currentHandlerArea != &defaultHandlerArea) 
	    TL_handlerArea = TL_currentHandlerArea->old_handlerArea; 
	longjmp (TL_currentHandlerArea->quit_env, signalNo);
#endif
    }


void TL_InitSignalHandlers ()
    {
#ifdef BSD
	/* Version using BSD signals */

	if (signal(SIGINT, SIG_IGN) != SIG_IGN) {
	    (void) signal(SIGINT, TL_SignalHandler);
	}
	(void) signal(SIGILL, TL_SignalHandler);
	(void) signal(SIGFPE, TL_SignalHandler);
#ifdef SIGBUS
	(void) signal(SIGBUS, TL_SignalHandler);
#endif
	(void) signal(SIGSEGV, TL_SignalHandler);
#endif
    }


void TL_initialize (argc, argv)
int argc;
char **argv;
{
    int i;

    /* initialize file map */
    TL_nextfile = 0;
    TL_files[TL_nextfile] = stdin;
    TL_filenames[TL_nextfile] = "stdin";
    TL_filemode[TL_nextfile] = READ_MODE;
    TL_nextfile = 1;
    TL_files[TL_nextfile] = stdout;
    TL_filenames[TL_nextfile] = "stdout";
    TL_filemode[TL_nextfile] = WRITE_MODE;
    TL_nextfile = 2;
    TL_files[TL_nextfile] = stderr;
    TL_filenames[TL_nextfile] = "stderr";
    TL_filemode[TL_nextfile] = WRITE_MODE;
    for (i=TL_nextfile+1; i<25; i++) {
	TL_files[i] = NULL;
	TL_filenames[i] = "";
    }

    /* initialize handlers */
    TL_handlerArea = &defaultHandlerArea;
    TL_handlerArea->old_handlerArea = 0;
    TL_handlerArea->quitCode = 0;
    TL_InitSignalHandlers ();

    /* initalize heap memory map */
    TL_nextmalloc = 0;
    for (i=0; i<25; i++) {
    	TL_mallocs[i] = NULL;
    }

    /* initialize global argv and argc */
    TL_TLI_TLIARC = argc-1;
    TL_TLI_TLIARV = argv;
    for (i=1; i<argc && TL_nextfile<25; i++) {
	if (argv[i][0] != '-') {
	    TL_nextfile++;
	    TL_filenames[TL_nextfile] = argv[i];
	}
    };
    TL_nextfile++;
}

void TL_finalize ()
{
    /* Close all output streams, except stdin, stdout and stderr */
    int i;
    for (i=3; i<25; i++) {
	if (TL_files[i] != NULL) fclose (TL_files[i]);
    }

    /* Release all heap memory */
    for (i=0; i<25; i++) {
        if (TL_mallocs[i] != NULL) free (TL_mallocs[i]);
    }
    
    /* Revert signal handlers */
    TL_RevertSignalHandlers ();
}
