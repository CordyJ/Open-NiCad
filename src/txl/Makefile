# Makefile to compile all TXL tools used in NiCad

# TXL tool size - recommended default 400
# On 32-bit platoforms, max 1000
# On 64-bit platformss, max 4000

SIZE=400

# *** WARNING: larger sizes make parsing significantly slower
#     in the presence of syntax errors.

.SUFFIXES:
.SUFFIXES:.txl .x

SRCS = $(wildcard *.txl)
FILTEREDSRCS = $(filter-out generic-%.txl,$(SRCS))
OBJS = $(patsubst %.txl,%.x,$(FILTEREDSRCS))   

all: $(OBJS)

%.x: %.txl
	txlc -s $(SIZE) $<

clean:
	/bin/rm -f *.x

