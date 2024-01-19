#!/bin/bash 
# Generic NiCad extractor script
#
# Usage:  Extract granularity language system-directory select-pattern ignore-pattern 
#           where granularity is one of:  { functions blocks ... }
#           and   language    is one of:  { c java cs py ... }
#           and   select-pattern is a grep pattern
#           and   ignore-pattern is a grep pattern

# Revised 27.10.20

ulimit -s hard

# Find our installation
lib="${0%%/scripts/extract.sh}"
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
    echo "Usage:  Extract granularity language system-directory select-pattern ignore-pattern"
    echo "          where granularity is one of:  { functions blocks ... }"
    echo "          and   language    is one of:  { c java cs py ... }"
    echo "          and   select-pattern is a grep pattern"
    echo "          and   ignore-pattern is a grep pattern"
    exit 99
fi

# check language
if [ "$1" != "" ] 
then
    language=$1
    shift
else
    echo "Usage:  Extract granularity language system-directory select-pattern ignore-pattern"
    echo "          where granularity is one of:  { functions blocks ... }"
    echo "          and   language    is one of:  { c java cs py ... }"
    echo "          and   select-pattern is a grep pattern"
    echo "          and   ignore-pattern is a grep pattern"
    exit 99
fi

# check at least one system directory
if [ ! -d "$1" ]
then
    echo "Usage:  Extract granularity language system-directory select-pattern ignore-pattern"
    echo "          where granularity is one of:  { functions blocks ... }"
    echo "          and   language    is one of:  { c java cs py ... }"
    echo "          and   select-pattern is a grep pattern"
    echo "          and   ignore-pattern is a grep pattern"
    exit 99
fi

# check we have the extractor we need
if [ ! -s ${lib}/txl/${language}-extract-${granularity}.x ]
then
    echo "*** ERROR: Language ${language} not supported at granularity ${granularity}"
    exit 99
fi

# Check we have a system
system="$1"
if [ ! -d "${system}" ]
then
    echo "*** ERROR: Can't find system source directory ${system}"
    exit 99
fi

# check if we have a select  pattern
shift
if [ "$1" != "" ] 
then
    select="$1"
else
    select=""
fi

# check if we have an ignore pattern
shift
if [ "$1" != "" ] 
then
    ignore="$1"
else
    ignore="_NO_IGNORE_"
fi

# Clean up any previous results
/bin/rm -rf "${system}_${granularity}"
echo -n > "${system}_${granularity}.xml"

# Extract potential clones
date

# Find all language source files in the directory and its subdirectories
echo "${lib}/txl/${language}-extract-${granularity}.x ALL.${language} >> ${system}_${granularity}.xml"

result=0

IFS=$'\n'
for i in `find -H -L "${system}" | grep "${select}" | grep -v "${ignore}" | grep "\.${language}"'$'` 
do
    source="${i}"
    sourcename=`echo "${source}" | sed -e "s;/;_;g" -e "s/ /_/g" -e "s/\.\./__/" -e "s/........................................................................................................................................................................................................\./_TOOLONG./" -e "s/........................................................................................................................................................................................................\./_TOOLONG./"`

    if [ ${language} = "c" ] || [ ${language} = "cs" ]
    then
        # echo "${lib}/txl/ifdef.x ${i} > /tmp/${sourcename}-ifdefed
        ${lib}/txl/ifdef.x "${i}" > /tmp/${sourcename}-ifdefed
        source=/tmp/${sourcename}-ifdefed
    fi
    if [ ${language} = "py" ] 
    then
        # echo "${lib}/txl/pyindent.x ${i} > /tmp/${sourcename}-pyindent
        ${lib}/txl/pyindent.x "${i}" > /tmp/${sourcename}-pyindent
        source=/tmp/${sourcename}-pyindent
    fi

    # echo "${lib}/txl/${language}-extract-${granularity}.x ${source} - ${i} >> ${system}_${granularity}.xml"
    ${lib}/txl/${language}-extract-${granularity}.x "${source}" - "${i}" >> "${system}_${granularity}.xml"

    if [ $? != 0 ]
    then
	result=$?
    fi

    /bin/rm -f /tmp/${sourcename}-ifdefed /tmp/${sourcename}-pyindent
done

echo ""
date
echo ""

exit $result
