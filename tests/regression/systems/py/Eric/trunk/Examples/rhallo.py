#!/usr/bin/env python

import sys

import eric4dbgstub

def main():
    print "Hello World!"
    sys.exit(0)
    
if __name__ == "__main__":
    if eric4dbgstub.initDebugger("standard"):
# or   if eric4dbgstub.initDebugger("threads"):
        eric4dbgstub.debugger.startDebugger()

    main()
