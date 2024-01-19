#!/bin/bash
# Cluster clone pairs into classes

# Revised 1.10.18

ulimit -s hard

# Find our installation
lib="${0%%/scripts/clusterpairs.sh}"
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
	echo "Usage:  ClusterPairs system-name_granularity-clones/system-name_granularity-clones-threshold.xml"
	echo "  (Output in system-name_granularity-clones/system-name_granularity-clones-threshold-classes.xml)"
	echo "  e.g., ClusterPairs systems/c/linux_functions-clones/linux_functions-clones-0.2.xml"
	exit 99
    fi

    # Get path of clone results file
    basename="${clonesfile%%.xml}"

    # OK, let's run it
    echo "${lib}/tools/cloneclasses.x ${basename}.xml > ${basename}-classes.xml"
    time ${lib}/tools/cloneclasses.x "${basename}.xml" > "${basename}-classes.xml"
    result=$?

    if [ ${result} != 0 ]
    then
	exit $result
    fi
done

echo ""
date
echo ""

exit 0
