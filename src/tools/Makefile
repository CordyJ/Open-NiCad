# Makefile for new NiCad tools
# J.R. Cordy March 2010

# To force 32 or 64 bit, use 'make MACHINESIZE=-m32' or 'make MACHINESIZE=-m64'
# Default to system's default
MACHINESIZE =

# Add platform-dependent compiler flags if necessary
ifeq ($(OS),Windows_NT)     # MinGW or Cygwin
    MACHINESIZE += -Wl,--stack,0x20000000
endif

# Flags to Turing compiler
TURINGSIZE = -mUNIX64 -DHUGE

# Flags for C compiler
COPTS = -w -ansi -fPIC -O -I . $(MACHINESIZE)

all : cloneclasses.x clonepairs.x crossclones.x getsource.x getnormsource.x tohtmlpairs.x streamprocess.x splitclasses.x

clonepairs.x: TLI.c TLS.c TLglob.h UNIX/cinterface.h main.c clonepairs.c
	gcc $(COPTS) -o clonepairs.x main.c TLI.c TLS.c clonepairs.c

cloneclasses.x: TLI.c TLS.c TLglob.h UNIX/cinterface.h main.c cloneclasses.c
	gcc $(COPTS) -o cloneclasses.x main.c TLI.c TLS.c cloneclasses.c

crossclones.x: TLI.c TLS.c TLglob.h UNIX/cinterface.h main.c crossclones.c
	gcc $(COPTS) -o crossclones.x main.c TLI.c TLS.c crossclones.c

getsource.x: TLI.c TLS.c TLglob.h UNIX/cinterface.h main.c getsource.c
	gcc $(COPTS) -o getsource.x main.c TLI.c TLS.c getsource.c

getnormsource.x: TLI.c TLS.c TLglob.h UNIX/cinterface.h main.c getnormsource.c
	gcc $(COPTS) -o getnormsource.x main.c TLI.c TLS.c getnormsource.c

tohtmlpairs.x: TLI.c TLS.c TLglob.h UNIX/cinterface.h main.c tohtmlpairs.c
	gcc $(COPTS) -o tohtmlpairs.x main.c TLI.c TLS.c tohtmlpairs.c

streamprocess.x: TLI.c TLS.c TLglob.h UNIX/cinterface.h main.c streamprocess.c
	gcc $(COPTS) -o streamprocess.x main.c TLI.c TLS.c streamprocess.c

splitclasses.x: TLI.c TLS.c TLglob.h UNIX/cinterface.h main.c splitclasses.c
	gcc $(COPTS) -o splitclasses.x main.c TLI.c TLS.c splitclasses.c

cloneclasses.c: cloneclasses.t linetable.i nicadsize.i
	tpc $(TURINGSIZE) -O -A -q4 cloneclasses.t

clonepairs.c: clonepairs.t linetable.i nicadsize.i
	tpc $(TURINGSIZE) -O -A -q4 clonepairs.t

crossclones.c: crossclones.t linetable.i nicadsize.i
	tpc $(TURINGSIZE) -O -A -q4 crossclones.t

getsource.c: getsource.t nicadsize.i
	tpc $(TURINGSIZE) -O -A -q4 getsource.t

getnormsource.c: getnormsource.t nicadsize.i
	tpc $(TURINGSIZE) -O -A -q4 getnormsource.t

tohtmlpairs.c: tohtmlpairs.t nicadsize.i
	tpc $(TURINGSIZE) -O -A -q4 tohtmlpairs.t

streamprocess.c: streamprocess.t nicadsize.i
	tpc $(TURINGSIZE) -O -A -q4 streamprocess.t

splitclasses.c: splitclasses.t nicadsize.i
	tpc $(TURINGSIZE) -O -A -q4 splitclasses.t

clean:
	/bin/rm -f clonepairs.x cloneclasses.x crossclones.x getsource.x getnormsource.x tohtmlpairs.x streamprocess.x splitclasses.x

reset:
	@echo ""
	@echo "*** Don't do this unless you are CERTAIN that you know what you are doing! ***"
	@echo ""
	@echo "Press return to proceed, CTRL-c to abort: "
	@read x
	/bin/rm -f clonepairs.x clonepairs.c cloneclasses.x cloneclasses.c crossclones.x crossclones.c getsource.x getsource.c getnormsource.x getnormsource.c tohtmlpairs.x tohtmlpairs.c streamprocess.x streamprocess.c splitclasses.x splitclasses.c *.o
