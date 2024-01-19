#!/bin/bash 
# Generic NiCad transform script
#
# Usage:  Transform granularity language pcfile.xml transform 
#           where  granularity is one of:  { functions blocks ... }
#           and    language    is one of:  { c java cs py ... }
#           and    pcfile.xml is an edtracted potential clones file
#           and    transform    is one of:  { sort ... }

# Revised 1.10.18

ulimit -s hard

# Find our installation
lib="${0%%/scripts/transform.sh}"
if [ ! -d ${lib} ]
then
    echo "*** Error:  cannot find NiCad installation ${lib}"
    echo ""
    exit 99
fi

# check granularity
if [ "$1" != "" ]
then
    granularity=$1
    shift
else
    echo "Usage:  Transform granularity language pcfile.xml transform "
    echo "          where  granularity is one of:  { functions blocks ... }"
    echo "          and    language    is one of:  { c java cs py ... }"
    echo "          and    pcfile.xml is an edtracted potential clones file"
    echo "          and    transform    is one of:  { sort ... }"
    exit 99
fi

# check language
if [ "$1" != "" ]
then
    language=$1
    shift
else
    echo "Usage:  Transform granularity language pcfile.xml transform "
    echo "          where  granularity is one of:  { functions blocks ... }"
    echo "          and    language    is one of:  { c java cs py ... }"
    echo "          and    pcfile.xml is an edtracted potential clones file"
    echo "          and    transform    is one of:  { sort ... }"
    exit 99
fi

# check we have a potential clones file
if [ "$1" != "" ]
then
    pcfile="${1%%.xml}"
    shift
else
    pcfile=""
fi

if [ ! -s "${pcfile}.xml" ]
then
    echo "Usage:  Transform granularity language pcfile.xml transform "
    echo "          where  granularity is one of:  { functions blocks ... }"
    echo "          and    language    is one of:  { c java cs py ... }"
    echo "          and    pcfile.xml is an edtracted potential clones file"
    echo "          and    transform    is one of:  { sort ... }"
    exit 99
fi

# check transform
if [ "$1" != "" ]
then
    transform=$1
    shift
else
    echo "Usage:  Transform granularity language pcfile.xml transform "
    echo "          where  granularity is one of:  { functions blocks ... }"
    echo "          and    language    is one of:  { c java cs py ... }"
    echo "          and    pcfile.xml is an edtracted potential clones file"
    echo "          and    transform    is one of:  { sort ... }"
    exit 99
fi

# check we have the transformer we need
if [ ! -s ${lib}/txl/${language}-transform-${transform}-${granularity}.x ]
then
    echo "*** ERROR: ${transform} transform not supported for ${language} ${granularity}"
    exit 99
fi

# Clean up any previous results
/bin/rm -f "${pcfile}-${transform}.xml"

# Transform potential clones
date

echo "${lib}/tools/streamprocess.x '${lib}/txl/${language}-transform-${transform}-${granularity}.x stdin' < ${pcfile}.xml > ${pcfile}-${transform}.xml"
time ${lib}/tools/streamprocess.x "${lib}/txl/${language}-transform-${transform}-${granularity}.x stdin" < "${pcfile}.xml" > "${pcfile}-${transform}.xml"

result=$?

echo ""
date
echo ""

exit $result
