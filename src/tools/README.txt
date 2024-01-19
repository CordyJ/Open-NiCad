Tools Required by the NiCad Process
-----------------------------------

To make them all, type:

	make

To recompile them all, type:

	make clean
	make

To recompile them from Turing+ source if you are changing it 
(requires Turing+ 6.0 (2018) or later to be installed), type:

	make reset
	make

Turing+ is available here:

	http://txl.ca/tplus


Increasing NiCad Clone Detector Limits
--------------------------------------

The NiCad clone detector comes preconfigured with limits large
enough to handle several versions of Linux, FreeBSD or Debian
as one piece, so it is unlikely you will ever have to increase them.
They are the largest limits that can be run on a 4 Gb machine.

However, if you need to increase clone detection limits beyond the 
present ones, you can do so as follows:

	(1) change SIZE in nicadsize.i to, for example:

		const SIZE := 100000

	    (every 50,000 will require 4 Gb, so 100,000
	     will need a machine with a minimum of 8 Gb)

	(2) recompile from Turing+ source, by typing:

		make reset
		make

Turing+ is available here:

	http://txl.ca/tplus

