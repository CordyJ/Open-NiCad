#!/bin/bash
# Generic NiCad cross-system extract and find clones script
# J.R. Cordy, Queen's University, January 2011

# Revised 11.1.23

usage() {
    echo "Usage:  nicadcross granularity language systemdir system2dir [ config ]"
    echo "          where granularity is one of:  { functions blocks files ... }"
    echo "          and   language    is one of:  { c java cs py ... }"
    echo "          and   config      is one of:  { blindrename ... }"
    echo ""
}

echo ""
echo "NiCad Cross-Clone Detector v7.0 (4.4.24)"
echo ""

# check we have an installation
if [ -d "$1" ]
then
    lib="$1"
    shift
else
    lib=.
fi

if [ ! -d ${lib}/tools ]
then
    echo "*** Error:  Cannot find NiCad installation ${lib}"
    echo ""
    exit 99
fi
 
# check we compiled the tools
if [ ! -x ${lib}/tools/crossclones.x ]
then
    echo "*** Error:  Missing ${lib}/tools/crossclones.x - type 'make' to make the NiCad tools"
    echo ""
    exit 99
fi

# check granularity
if [ "$1" != "" ]
then
    granularity="$1"
    shift
else
    usage
    exit 99
fi

# check language
if [ "$1" != "" ]
then
    language="$1"
    shift
else
    usage
    exit 99
fi

# check we have a system directory
if [ -d "$1" ]
then
    system1="${1%/}"
    shift
else
    usage
    exit 99
fi

# check we have a second system directory 
if [ -d "$1" ]
then
    system2="${1%/}"
    shift
else
    usage
fi

# check for a configuration
if [ "$1" = "" ]
then
    config="${lib}/config/default.cfg"
else
    config="${lib}/config/$1.cfg"
fi

if [ ! -s "${config}" ]
then
    usage
    exit 99
fi

echo "config=${config}"

# get NiCad configuration parameters
source ${config}

# normalize threshold to 2 digits
if [[ "$threshold" =~ [0-9].[0-9]$ ]]
then
    threshold="${threshold}0"
fi

echo "system1=${system1}"
echo "system2=${system2}"
echo "threshold=${threshold}"
echo "granularity=${granularity}"
echo "language=${language}"
echo "transform=${transform}"
echo "rename=${rename}"
echo "filter=${filter}"
echo "abstract=${abstract}"
echo "normalize=${normalize}"
echo "cluster=${cluster}"
echo "report=${report}"
echo "include=${include}"
echo "exclude=${exclude}"
echo ""

# Check we have a system
if [ ! -d "${system1}" ]
then
    echo "*** ERROR: Can't find system source directory ${system1}"
    exit 99
fi

# And a second system to compare to it
if [ ! -d "${system2}" ]
then
    echo "*** ERROR: Can't find system source directory ${system2}"
    exit 99
fi

# Set up results directory
system1path=`readlink -f "${system1}"`
system1file="${system1##*/}"

system2path=`readlink -f "${system2}"`
system2file="${system2##*/}"

resultsdir="nicadclones/${system1file}"
mkdir -p "${resultsdir}"

if [ ! -h "${resultsdir}/${system1file}" ]
then
    ln -s "${system1path}" "${resultsdir}/${system1file}"
fi

if [ ! -h "${resultsdir}/${system2file}" ]
then
    ln -s "${system2path}" "${resultsdir}/${system2file}"
fi

system1="${resultsdir}/${system1file}"
system2="${resultsdir}/${system2file}"

# Extract system potential clones
date
datestamp=`date +%F-%T`
echo ""

if [ -s "${system1}_${granularity}.xml" ]
then
    echo "Using previously extracted ${granularity} from ${language} files in ${system1}"
    echo > "${system1}_${granularity}-crossclones-${datestamp}.log" 2>&1
else
    echo "Extracting ${granularity} from ${language} files in ${system1}"
    time ${lib}/scripts/extract.sh ${granularity} ${language} "${system1}" "${include}" "${exclude}" > "${system1}_${granularity}-crossclones-${datestamp}.log" 2>&1
fi

result=$?
echo ""

if [ $result -ge 99 ]
then
    echo "*** ERROR: Extraction failed, code $result"
    echo "Detailed log in ${system1}_${granularity}-crossclones-${datestamp}.log"
    echo ""
    exit 99
fi

# Check for parsing problems
syntaxerrors=`(grep "TXL019[12]E" "${system1}_${granularity}-crossclones-${datestamp}.log" | wc -l)`
if [ ${syntaxerrors} != 0 ]
then
    if [ ${syntaxerrors} = 1 ]
    then
	echo "*** Warning: 1 source file failed to parse"
    else
	echo "*** Warning: ${syntaxerrors} source files failed to parse"
    fi
    echo ""
fi

npcs=`grep "^<source " "${system1}_${granularity}.xml" | wc -l`
echo "Extracted ${npcs} ${granularity}"
echo ""

pc1file="${system1}_${granularity}"


# Extract second system potential clones
date
datestamp=`date +%F-%T`
echo ""

if [ -s "${system2}_${granularity}.xml" ]
then
    echo "Using previously extracted ${granularity} from ${language} files in ${system2}"
    echo > "${system2}_${granularity}-crossclones-${datestamp}.log" 2>&1
else
    echo "Extracting ${granularity} from ${language} files in ${system2}"
    time ${lib}/scripts/extract.sh ${granularity} ${language} "${system2}" "${include}" "${exclude}" > "${system2}_${granularity}-crossclones-${datestamp}.log" 2>&1
fi

result=$?
echo ""

if [ $result -ge 99 ]
then
    echo "*** ERROR: Extraction failed, code $result"
    echo "Detailed log in ${system2}_${granularity}-crossclones-${datestamp}.log"
    echo ""
    exit 99
fi

# Check for parsing problems
syntaxerrors=`(grep "TXL019[12]E" "${system2}_${granularity}-crossclones-${datestamp}.log" | wc -l)`
if [ ${syntaxerrors} != 0 ]
then
    if [ ${syntaxerrors} = 1 ]
    then
	echo "*** Warning: 1 source file failed to parse"
    else
	echo "*** Warning: ${syntaxerrors} source files failed to parse"
    fi
    echo ""
fi

npcs=`grep "^<source " "${system2}_${granularity}.xml" | wc -l`
echo "Extracted ${npcs} ${granularity}"
echo ""

pc2file="${system2}_${granularity}"


# Check for transformation to be done
if [ "${transform}" != none ]
then
    if [ -s "${pc1file}-${transform}.xml" ]
    then
	echo "Using previously ${transform} transformd extracted ${granularity} from ${language} files in ${system1}"
    else
	echo "Applying ${transform} transformation to extracted ${granularity} from ${language} files in ${system1}"
	time ${lib}/scripts/transform.sh ${granularity} ${language} "${pc1file}.xml" ${transform} >> "${system1}_${granularity}-crossclones-${datestamp}.log" 2>&1
    fi

    result=$?
    echo ""

    if [ $result != 0 ]
    then
        echo "*** ERROR: Renaming failed, code $result"
        echo "Detailed log in ${system1}_${granularity}-crossclones-${datestamp}.log"
        echo ""
        exit 99
    fi

    pc1file="${pc1file}-${transform}"

    if [ -s "${pc2file}-${transform}.xml" ]
    then
	echo "Using previously ${transform} transformd extracted ${granularity} from ${language} files in ${system2}"
    else
	echo "Applying ${transform} transformation to extracted ${granularity} from ${language} files in ${system2}"
	time ${lib}/scripts/transform.sh ${granularity} ${language} "${pc2file}.xml" ${transform} >> "${system2}_${granularity}-crossclones-${datestamp}.log" 2>&1
    fi

    result=$?
    echo ""

    if [ $result != 0 ]
    then
        echo "*** ERROR: Renaming failed, code $result"
        echo "Detailed log in ${system2}_${granularity}-crossclones-${datestamp}.log"
        echo ""
        exit 99
    fi

    pc2file="${pc2file}-${transform}"
fi

# Check for renaming to be done
if [ "${rename}" != none ]
then
    if [ -s "${pc1file}-${rename}.xml" ]
    then
	echo "Using previously ${rename} renamed extracted ${granularity} from ${language} files in ${system1}"
    else
	echo "Applying ${rename} renaming to extracted ${granularity} from ${language} files in ${system1}"
	time ${lib}/scripts/rename.sh ${granularity} ${language} "${pc1file}.xml" ${rename} >> "${system1}_${granularity}-crossclones-${datestamp}.log" 2>&1
    fi

    result=$?
    echo ""

    if [ $result != 0 ]
    then
        echo "*** ERROR: Renaming failed, code $result"
        echo "Detailed log in ${system1}_${granularity}-crossclones-${datestamp}.log"
        echo ""
        exit 99
    fi

    pc1file="${pc1file}-${rename}"

    if [ -s "${pc2file}-${rename}.xml" ]
    then
	echo "Using previously ${rename} renamed extracted ${granularity} from ${language} files in ${system2}"
    else
	echo "Applying ${rename} renaming to extracted ${granularity} from ${language} files in ${system2}"
	time ${lib}/scripts/rename.sh ${granularity} ${language} "${pc2file}.xml" ${rename} >> "${system2}_${granularity}-crossclones-${datestamp}.log" 2>&1
    fi

    result=$?
    echo ""

    if [ $result != 0 ]
    then
        echo "*** ERROR: Renaming failed, code $result"
        echo "Detailed log in ${system2}_${granularity}-crossclones-${datestamp}.log"
        echo ""
        exit 99
    fi

    pc2file="${pc2file}-${rename}"
fi

# Check for filtering to be done
if [ "${filter}" != none ]
then
    if [ -s "${pc1file}-filter.xml" ]
    then
	echo "Using previously filtered extracted ${granularity} from ${language} files in ${system1}"
    else
	echo "Applying filtering of ${filter} to extracted ${granularity} from ${language} files in ${system1}"
	time ${lib}/scripts/filter.sh ${granularity} ${language} "${pc1file}.xml" ${filter} >> "${system1}_${granularity}-crossclones-${datestamp}.log" 2>&1
    fi

    result=$?
    echo ""

    if [ $result != 0 ]
    then
        echo "*** ERROR: Filtering failed, code $result"
        echo "Detailed log in ${system1}_${granularity}-crossclones-${datestamp}.log"
        echo ""
        exit 99
    fi

    pc1file="${pc1file}-filter"

    if [ -s "${pc2file}-filter.xml" ]
    then
	echo "Using previously filtered extracted ${granularity} from ${language} files in ${system2}"
    else
	echo "Applying filtering of ${filter} to extracted ${granularity} from ${language} files in ${system2}"
	time ${lib}/scripts/filter.sh ${granularity} ${language} "${pc2file}.xml" ${filter} >> "${system2}_${granularity}-crossclones-${datestamp}.log" 2>&1
    fi

    result=$?
    echo ""

    if [ $result != 0 ]
    then
        echo "*** ERROR: Filtering failed, code $result"
        echo "Detailed log in ${system2}_${granularity}-crossclones-${datestamp}.log"
        echo ""
        exit 99
    fi

    pc2file="${pc2file}-filter"
fi

# Check for abstraction to be done
if [ "${abstract}" != none ]
then
    if [ -s "${pc1file}-abstract.xml" ]
    then
	echo "Using previously abstracted extracted ${granularity} from ${language} files in ${system1}"
    else
	echo "Applying abstraction of ${abstract} to extracted ${granularity} from ${language} files in ${system1}"
	time ${lib}/scripts/abstract.sh ${granularity} ${language} "${pc1file}.xml" ${abstract} >> "${system1}_${granularity}-crossclones-${datestamp}.log" 2>&1
    fi

    result=$?
    echo ""

    if [ $result != 0 ]
    then
        echo "*** ERROR: Abstraction failed, code $result"
        echo "Detailed log in ${system1}_${granularity}-crossclones-${datestamp}.log"
        echo ""
        exit 99
    fi

    pc1file="${pc1file}-abstract"

    if [ -s "${pc2file}-abstract.xml" ]
    then
	echo "Using previously abstracted extracted ${granularity} from ${language} files in ${system2}"
    else
	echo "Applying abstraction of ${abstract} to extracted ${granularity} from ${language} files in ${system2}"
	time ${lib}/scripts/abstract.sh ${granularity} ${language} "${pc2file}.xml" ${abstract} >> "${system2}_${granularity}-crossclones-${datestamp}.log" 2>&1
    fi

    result=$?
    echo ""

    if [ $result != 0 ]
    then
        echo "*** ERROR: Abstraction failed, code $result"
        echo "Detailed log in ${system2}_${granularity}-crossclones-${datestamp}.log"
        echo ""
        exit 99
    fi

    pc2file="${pc2file}-abstract"
fi

# Check for custom normalization to be done
if [ "${normalize}" != none ]
then
    if [ -s "${pc1file}-normalize.xml" ]
    then
	echo "Using previously normalized extracted ${granularity} from ${language} files in ${system1}"
    else
	echo "Applying custom normalization ${normalize} to extracted ${granularity} from ${language} files in ${system1}"
	time ${lib}/scripts/normalize.sh ${granularity} ${language} "${pc1file}.xml" ${normalize} >> "${system1}_${granularity}-crossclones-${datestamp}.log" 2>&1
    fi

    result=$?
    echo ""

    if [ $result != 0 ]
    then
        echo "*** ERROR: Custom normalization failed, code $result"
        echo "Detailed log in ${system1}_${granularity}-crossclones-${datestamp}.log"
        echo ""
        exit 99
    fi

    pc1file="${pc1file}-normalized"

    if [ -s "${pc2file}-normalize.xml" ]
    then
	echo "Using previously normalized extracted ${granularity} from ${language} files in ${system2}"
    else
	echo "Applying custom normalization ${normalize} to extracted ${granularity} from ${language} files in ${system2}"
	time ${lib}/scripts/normalize.sh ${granularity} ${language} "${pc2file}.xml" ${normalize} >> "${system2}_${granularity}-crossclones-${datestamp}.log" 2>&1
    fi

    result=$?
    echo ""

    if [ $result != 0 ]
    then
        echo "*** ERROR: Custom normalization failed, code $result"
        echo "Detailed log in ${system2}_${granularity}-crossclones-${datestamp}.log"
        echo ""
        exit 99
    fi

    pc2file="${pc2file}-normalized"
fi

# Find near-miss clones
echo "Finding cross-clones between ${minsize} and ${maxsize} lines at UPI threshold ${threshold}"
time ${lib}/scripts/findcrossclones.sh "${pc1file}.xml" "${pc2file}.xml" ${threshold} ${minsize} ${maxsize} >> "${system1}_${granularity}-crossclones-${datestamp}.log" 2>&1

result=$?
echo ""

if [ $result != 0 ]
then
    echo "*** ERROR: Cross-clone analysis failed, code $result"
    echo "Detailed log in ${system1}_${granularity}-crossclones-${datestamp}.log"
    echo ""
    exit 99
fi

grep "^Found " "${system1}_${granularity}-crossclones-${datestamp}.log" | tail -1
echo ""

if [ "${cluster}" = "yes" ]
then
    # Compute clone classes
    echo "Clustering clone pairs into classes"
    time ${lib}/scripts/clusterpairs.sh "${pc1file}-crossclones/*_${granularity}*-crossclones-${threshold}.xml" >> "${system1}_${granularity}-crossclones-${datestamp}.log" 2>&1

    result=$?
    echo ""

    if [ $result != 0 ]
    then
	echo "*** ERROR: Clustering failed, code $result"
	echo "Detailed log in ${system1}_${granularity}-crossclones-${datestamp}.log"
	echo ""
	exit 99
    fi

    grep "^Clustered " "${system1}_${granularity}-crossclones-${datestamp}.log" | tail -1
    echo ""
fi

if [ "${report}" = "yes" -o "${report}" = "pairs" ]
then
    # Get original sources
    echo "Getting original sources for clones"

    if [ "${report}" = "pairs" ]
    then
	time ${lib}/scripts/getsource.sh "${pc1file}-crossclones/*_${granularity}*-crossclones-${threshold}.xml" >> "${system1}_${granularity}-crossclones-${datestamp}.log" 2>&1

	result=$?
	echo ""

	if [ $result != 0 ]
	then
	    echo "*** ERROR: Get sources failed, code $result"
	    echo "Detailed log in ${system1}_${granularity}-crossclones-${datestamp}.log"
	    echo ""
	    exit 99
	fi
    fi

    if [ "${cluster}" = "yes" ]
    then
	time ${lib}/scripts/getsource.sh "${pc1file}-crossclones/*_${granularity}*-crossclones-${threshold}-classes.xml" >> "${system1}_${granularity}-crossclones-${datestamp}.log" 2>&1

	result=$?
	echo ""

	if [ $result != 0 ]
	then
	    echo "*** ERROR: Get sources failed, code $result"
	    echo "Detailed log in ${system1}_${granularity}-crossclones-${datestamp}.log"
	    echo ""
	    exit 99
	fi
    fi

    # Convert to HTML
    echo "Making HTML reports"
    if [ "${report}" = "pairs" ]
    then
	time ${lib}/scripts/makepairhtml.sh "${pc1file}-crossclones/*_${granularity}*-crossclones-${threshold}-withsource.xml" >> "${system1}_${granularity}-crossclones-${datestamp}.log" 2>&1

	result=$?
	echo ""

	if [ $result != 0 ]
	then
	    echo "*** ERROR: Make HTML failed, code $result"
	    echo "Detailed log in ${system1}_${granularity}-crossclones-${datestamp}.log"
	    echo ""
	    exit 99
	fi
    fi

    if [ "${cluster}" = "yes" ]
    then
	time ${lib}/scripts/makepairhtml.sh "${pc1file}-crossclones/*_${granularity}*-crossclones-${threshold}-classes-withsource.xml" >> "${system1}_${granularity}-crossclones-${datestamp}.log" 2>&1

	result=$?
	echo ""

	if [ $result != 0 ]
	then
	    echo "*** ERROR: Make HTML failed, code $result"
	    echo "Detailed log in ${system1}_${granularity}-crossclones-${datestamp}.log"
	    echo ""
	    exit 99
	fi
    fi

elif [ "${report}" = "normalized" -o ${report} = "normalizedpairs" ]
then
    # Get normalized sources
    echo "Getting normalized sources for clones"
    if [ "${report}" = "normalizedpairs" ]
    then
	time ${lib}/scripts/getnormsource.sh "${pc1file}.xml" "${pc1file}-clones/*_${granularity}*-crossclones-${threshold}.xml" >> "${system1}_${granularity}-clones-${datestamp}.log" 2>&1

	result=$?
	echo ""

	if [ $result != 0 ]
	then
	    echo "*** ERROR: Get normalized sources failed, code $result"
	    echo "Detailed log in ${system1}_${granularity}-clones-${datestamp}.log"
	    echo ""
	    exit 99
	fi
    fi

    if [ "${cluster}" = "yes" ]
    then
	time ${lib}/scripts/getnormsource.sh "${pc1file}.xml" "${pc1file}-clones/*_${granularity}*-crossclones-${threshold}-classes.xml" >> "${system1}_${granularity}-clones-${datestamp}.log" 2>&1

	result=$?
	echo ""

	if [ $result != 0 ]
	then
	    echo "*** ERROR: Get normalized sources failed, code $result"
	    echo "Detailed log in ${system1}_${granularity}-clones-${datestamp}.log"
	    echo ""
	    exit 99
	fi
    fi

    # Convert to HTML
    echo "Making HTML reports"
    if [ "${report}" = "normalizedpairs" ]
    then
	time ${lib}/scripts/makepairhtml.sh "${pc1file}-clones/*_${granularity}*-crossclones-${threshold}-normsource.xml" >> "${system1}_${granularity}-clones-${datestamp}.log" 2>&1

	result=$?
	echo ""

	if [ $result != 0 ]
	then
	    echo "*** ERROR: Make HTML failed, code $result"
	    echo "Detailed log in ${system1}_${granularity}-clones-${datestamp}.log"
	    echo ""
	    exit 99
	fi
    fi

    if [ "${cluster}" = "yes" ]
    then
	time ${lib}/scripts/makepairhtml.sh "${pc1file}-clones/*_${granularity}*-crossclones-${threshold}-classes-normsource.xml" >> "${system1}_${granularity}-clones-${datestamp}.log" 2>&1

	result=$?
	echo ""

	if [ $result != 0 ]
	then
	    echo "*** ERROR: Make HTML failed, code $result"
	    echo "Detailed log in ${system1}_${granularity}-clones-${datestamp}.log"
	    echo ""
	    exit 99
	fi
    fi
fi

echo "Done."
echo ""
echo "Detailed log in ${system1}_${granularity}-crossclones-${datestamp}.log"
echo "Results in ${pc1file}-crossclones/"
if [ "${report}" != "no" ]
then
    echo "Report in" ${pc1file}-crossclones/*_${granularity}*-crossclones-${threshold}-*.html
fi
echo ""
date
echo ""
