/* TXL Version 10.3 (c)1988-2003 Queen's University at Kingston
 * J.R. Cordy, C.D. Halpern, E.M. Promislow & I.H. Carmichael
 * March 2003 
 */

/* Added TL_finalize to assist in converting to re-entrant subroutine -- JRC 16.5.97 */
/* Fixed type of argc to be int -- JRC 3.7.15 */
/* Cleaned up obsolete version logic -- JRC 2.8.15 */

#include "TLglob.h"
extern void TProg();

int main (argc, argv)
int	argc;
char 	**argv;
{
    int code;
    TL_initialize (argc, argv);
    if (setjmp (TL_handlerArea->quit_env)) {
    	TL_finalize ();
	exit (TL_handlerArea->quitCode);
    }
    TProg ();
    TL_finalize ();
    exit (0);
}
