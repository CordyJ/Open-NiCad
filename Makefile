# Recompile all NiCad tools and plugins

# Usage:
#    make [options]
#
#    where options can be one or more of:
#
#        MACHINESIZE=-mXX    - Force XX-bit tools, where XX=32 or 64 (default: system default)
#
#        SIZE=NNNN           - Compile TXL plugins to size -s NNNN (default: 400, max: 4000)
#                              (warning: larger sizes use more memory and slows syntax error recovery)
#				

# Localization
OS := $(shell (uname -s | sed 's/_.*//'))

MESSAGE = "Unrecognized platform - making Nicad using gcc and no signal handling"

ifeq ($(OS), Darwin)
    MESSAGE = "Making Nicad on MacOS using gcc and BSD signal handling"
    CFLAGS := $(CFLAGS) -mmacosx-version-min=10.12 
    LDFLAGS := $(LDFLAGS) -mmacosx-version-min=10.12
    SIGTYPE = BSD

else ifeq ($(OS), Linux)
    MESSAGE = "Making Nicad on Linux using gcc and BSD signal handling"
    CFLAGS := $(CFLAGS) -Wno-format-truncation -Wno-format-overflow -Wno-unused-result
    SIGTYPE = BSD

else ifeq ($(OS), CYGWIN)
    MESSAGE = "Making Nicad on Cygwin using gcc and BSD signal handling"
    CFLAGS := $(CFLAGS) -Wno-stringop-overread -Wno-stringop-overflow
    LDFLAGS := $(LDFLAGS) -Wl,--stack,8388608
    EXE = .exe
    SIGTYPE = BSD

else ifeq ($(OS), MSYS)
    MESSAGE = "Making Nicad on Msys / MinGW using gcc and BSD signal handling"
    CFLAGS := $(CFLAGS) -Wno-stringop-overread -Wno-stringop-overflow
    LDFLAGS := $(LDFLAGS) -Wl,--stack,8388608
    EXE = .exe
    SIGTYPE = BSD

else ifeq ($(OS), MINGW64)
    MESSAGE = "Making Nicad on Msys / MinGW using gcc and BSD signal handling"
    LDFLAGS := $(LDFLAGS) -Wl,--stack,8388608
    EXE = .exe
    SIGTYPE = BSD
endif

# Build
all: clean lib/nicad/scripts lib/nicad/tools lib/nicad/txl lib/nicad/config

lib/nicad/tools:
	mkdir -p lib/nicad/tools
	(cd src/tools; make)
	cp src/tools/*.x lib/nicad/tools/

lib/nicad/txl:
	mkdir -p lib/nicad/txl
	(cd src/txl; make)
	cp src/txl/*.x lib/nicad/txl/

lib/nicad/scripts:
	mkdir -p lib/nicad/scripts
	cp src/scripts/* lib/nicad/scripts

lib/nicad/config:
	mkdir -p lib/nicad/config
	cp src/config/* lib/nicad/config

# Make distribution release for this platform

distrib : lib/nicad/tools lib/nicad/txl lib/nicad/scripts lib/nicad/config
	/bin/rm -rf nicad-$(OS)
	mkdir -p nicad/bin
	cp bin/* nicad/bin/
	mkdir -p nicad/lib
	cp -r lib/* nicad/lib/
	cp -r src/installer/* nicad/
	cp *.txt nicad/
	mv nicad nicad-$(OS)
	tar cfz nicad-$(OS).tar.gz nicad-$(OS)

clean:
	(cd src/tools; make clean)
	(cd src/txl; make clean)
	/bin/rm -rf lib/*
	/bin/rm -rf nicad-$(OS)
	/bin/rm -f nicad-$(OS).tar.gz
	/bin/rm -rf nicadclones
