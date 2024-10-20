#!/bin/bash
# Find all clones between two given sets of potential clones in XML format

# Revised 1.10.18

ulimit -s hard

# Find our installation
lib="${0%%/scripts/findcrossclones.sh}"
if [ ! -d ${lib} ]
then
    echo "*** Error:  Cannot find NiCad installation ${lib}"
    echo ""
    exit 99
fi

# Check we have a system
if [ ! -f "$1" ] 
then
    echo "Usage:  FindCrossClones system1-name_granularity.xml system2-name_granularity.xml threshold [ minclonesize ] [ maxclonesize] [ showsource ]"
    echo "  e.g.,   FindCrossClones systems/c/linux24_functions.xml systems/c/linux25_functions.xml 0.0"
    echo "  e.g.,   FindCrossClones systems/c/linux24_functions.xml systems/c/linux25_functions.xml 0.2 3 2000 showsource"
    exit 99
else
    pc1file="$1"
    shift
fi

# And second system
if [ ! -f "$1" ] 
then
    echo "Usage:  FindCrossClones system1-name_granularity.xml system2-name_granularity.xml threshold [ minclonesize ] [ maxclonesize] [ showsource ]"
    echo "  e.g.,   FindCrossClones systems/c/linux24_functions.xml systems/c/linux25_functions.xml 0.0"
    echo "  e.g.,   FindCrossClones systems/c/linux24_functions.xml systems/c/linux25_functions.xml 0.2 3 2000 showsource"
    exit 99
else
    pc2file="$1"
    shift
fi

# And a threshold
if [ "$1" != "" ] 
then
    threshold=$1
else
    echo "Usage:  FindCrossClones system1-name_granularity.xml system2-name_granularity.xml threshold [ minclonesize ] [ maxclonesize] [ showsource ]"
    echo "  e.g.,   FindCrossClones systems/c/linux24_functions.xml systems/c/linux25_functions.xml 0.0"
    echo "  e.g.,   FindCrossClones systems/c/linux24_functions.xml systems/c/linux25_functions.xml 0.2 3 2000 showsource"
    exit 99
fi

# Other arguments we just pass on to crossclones.x

# Put our results in the same directory as the potential clones file
basename="${pc1file%%.xml}"
resultsdir="${basename}-crossclones"
mkdir "${resultsdir}" 2> /dev/null
systemname="${basename##*/}"

# OK, let's run it
date
echo "${lib}/tools/crossclones.x ${pc1file} ${pc2file} $* > ${resultsdir}/${systemname}-crossclones-${threshold}.xml"
time ${lib}/tools/crossclones.x "${pc1file}" "${pc2file}" $* > "${resultsdir}/${systemname}-crossclones-${threshold}.xml"

result=$?

echo ""
date
echo ""

exit $result
