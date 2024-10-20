#!/bin/bash 
# Make HTML pages of results of a FindClonePairs run

# Revised 1.10.18

ulimit -s hard

# Find our installation
lib="${0%%/scripts/makepairhtml.sh}"
if [ ! -d ${lib} ]
then
    echo "*** Error:  cannot find NiCad installation ${lib}"
    echo ""
    exit 99
fi

date

IFS=$'\n'
for clonesfile in $*
do
    # Check we have a system
    if [ ! -f "$clonesfile" ] 
    then
	echo "Usage:  MakePairHTML system-name_granularity-clones/system-name_granularity-clones-threshold-withsource.xml"
	echo "  (Output in system-name_granularity-clones/system-name_granularity-clones-threshold-withsource.html)"
	echo "  e.g., MakePairHTML systems/c/linux_functions-clones/linux_functions-clones-0.2-withsource.xml"
	exit 99
    fi

    # Get path of clone results file
    basename="${clonesfile%%.xml}"

    # OK, let's run it
    echo "${lib}/tools/tohtmlpairs.x ${basename}.xml ${basename}.html"
    time ${lib}/tools/tohtmlpairs.x "${basename}.xml" "${basename}.html"
    result=$?

    if [ $result != 0 ]
    then
	exit $result
    fi
done

echo ""
date
echo ""

exit 0
