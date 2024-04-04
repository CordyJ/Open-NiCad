#!/bin/bash
# Generic NiCad extract and find clones script
# J.R. Cordy, Queen's University, April 2010

# Revised 11.1.24

usage() {
    echo "Usage:  nicad granularity language systems/systemdir [ config ]"
    echo "          where granularity is one of:  { functions blocks files ... }"
    echo "          and   language    is one of:  { c java cs py ... }"
    echo "          and   config      is one of:  { blindrename ... }"
    echo ""
}

echo ""
echo "NiCad Clone Detector v7.0 (4.4.24)"
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
if [ ! -x ${lib}/tools/clonepairs.x ]
then
    echo "*** Error:  Missing ${lib}/tools/clonepairs.x - type 'make' to make the NiCad tools"
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
    system="${1%/}"
    shift
else
    usage
    exit 99
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
source "${config}"

# normalize threshold to 2 digits
if [[ "$threshold" =~ [0-9].[0-9]$ ]]
then
    threshold="${threshold}0"
fi

echo "system=${system}"
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
if [ ! -d "${system}" ]
then
    echo "*** ERROR: Can't find system source directory ${system}"
    exit 99
fi

# Set up results directory
systempath=`readlink -f "${system}"`
systemfile="${system##*/}"
resultsdir="nicadclones/${systemfile}"

mkdir -p "${resultsdir}"

if [ ! -h "${resultsdir}/${systemfile}" ]
then
    ln -s "${systempath}" "${resultsdir}/${systemfile}"
fi

system="${resultsdir}/${systemfile}"

# Extract potential clones
date
datestamp=`date +%F-%T`
echo ""

if [ -s "${system}_${granularity}.xml" ]
then
    echo "Using previously extracted ${granularity} from ${language} files in ${system}"
    echo > "${system}_${granularity}-clones-${datestamp}.log" 2>&1
else
    echo "Extracting ${granularity} from ${language} files in ${system}"
    time ${lib}/scripts/extract.sh ${granularity} ${language} "${system}" "${include}" "${exclude}" > "${system}_${granularity}-clones-${datestamp}.log" 2>&1
fi

result=$?
echo ""

if [ $result -ge 99 ]
then
    echo "*** ERROR: Extraction failed, code $result"
    echo "Detailed log in ${system}_${granularity}-clones-${datestamp}.log"
    echo ""
    exit 99
fi


# Check for parsing problems
syntaxerrors=`(grep "TXL019[12]E" "${system}_${granularity}-clones-${datestamp}.log" | wc -l)`
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

npcs=`grep "^<source " "${system}_${granularity}.xml" | wc -l`
echo "Extracted ${npcs} ${granularity}"
echo ""

pcfile="${system}_${granularity}"

# Check for transforming to be done
if [ "${transform}" != none ]
then
    if [ -s "${pcfile}-${transform}.xml" ]
    then
	echo "Using previously ${transform} transformed extracted ${granularity} from ${language} files in ${system}"
    else
	echo "Applying ${transform} transformation to extracted ${granularity} from ${language} files in ${system}"
	time ${lib}/scripts/transform.sh ${granularity} ${language} "${pcfile}.xml" ${transform} >> "${system}_${granularity}-clones-${datestamp}.log" 2>&1
    fi

    result=$?
    echo ""

    if [ $result != 0 ]
    then
        echo "*** ERROR: Renaming failed, code $result"
        echo "Detailed log in ${system}_${granularity}-clones-${datestamp}.log"
        echo ""
        exit 99
    fi

    pcfile="${pcfile}-${transform}"
fi

# Check for renaming to be done
if [ "${rename}" != none ]
then
    if [ -s "${pcfile}-${rename}.xml" ]
    then
	echo "Using previously ${rename} renamed extracted ${granularity} from ${language} files in ${system}"
    else
	echo "Applying ${rename} renaming to extracted ${granularity} from ${language} files in ${system}"
	time ${lib}/scripts/rename.sh ${granularity} ${language} "${pcfile}.xml" ${rename} >> "${system}_${granularity}-clones-${datestamp}.log" 2>&1
    fi

    result=$?
    echo ""

    if [ $result != 0 ]
    then
        echo "*** ERROR: Renaming failed, code $result"
        echo "Detailed log in ${system}_${granularity}-clones-${datestamp}.log"
        echo ""
        exit 99
    fi

    pcfile="${pcfile}-${rename}"
fi

# Check for filtering to be done
if [ "${filter}" != none ]
then
    if [ -s "${pcfile}-filter.xml" ]
    then
	echo "Using previously filtered extracted ${granularity} from ${language} files in ${system}"
    else
	echo "Applying filtering of ${filter} to extracted ${granularity} from ${language} files in ${system}"
	time ${lib}/scripts/filter.sh ${granularity} ${language} "${pcfile}.xml" ${filter} >> "${system}_${granularity}-clones-${datestamp}.log" 2>&1
    fi

    result=$?
    echo ""

    if [ $result != 0 ]
    then
        echo "*** ERROR: Filtering failed, code $result"
        echo "Detailed log in ${system}_${granularity}-clones-${datestamp}.log"
        echo ""
        exit 99
    fi

    pcfile="${pcfile}-filter"
fi

# Check for abstraction to be done
if [ "${abstract}" != none ]
then
    if [ -s "${pcfile}-abstract.xml" ]
    then
	echo "Using previously abstracted extracted ${granularity} from ${language} files in ${system}"
    else
	echo "Applying abstraction of ${abstract} to extracted ${granularity} from ${language} files in ${system}"
	time ${lib}/scripts/abstract.sh ${granularity} ${language} "${pcfile}.xml" ${abstract} >> "${system}_${granularity}-clones-${datestamp}.log" 2>&1
    fi

    result=$?
    echo ""

    if [ $result != 0 ]
    then
        echo "*** ERROR: Abstraction failed, code $result"
        echo "Detailed log in ${system}_${granularity}-clones-${datestamp}.log"
        echo ""
        exit 99
    fi

    pcfile="${pcfile}-abstract"
fi

# Check for custom normalization to be done
if [ "${normalize}" != none ]
then
    if [ -s "${pcfile}-normalize.xml" ]
    then
	echo "Using previously normalized extracted ${granularity} from ${language} files in ${system}"
    else
	echo "Applying custom normalization ${normalize} to extracted ${granularity} from ${language} files in ${system}"
	time ${lib}/scripts/normalize.sh ${granularity} ${language} "${pcfile}.xml" ${normalize} >> "${system}_${granularity}-clones-${datestamp}.log" 2>&1
    fi

    result=$?
    echo ""

    if [ $result != 0 ]
    then
        echo "*** ERROR: Custom normalization failed, code $result"
        echo "Detailed log in ${system}_${granularity}-clones-${datestamp}.log"
        echo ""
        exit 99
    fi

    pcfile="${pcfile}-normalized"
fi

# Find near-miss clones
echo "Finding clones between ${minsize} and ${maxsize} lines at UPI threshold ${threshold}"
time ${lib}/scripts/findclonepairs.sh "${pcfile}.xml" ${threshold} ${minsize} ${maxsize} >> "${system}_${granularity}-clones-${datestamp}.log" 2>&1

result=$?
echo ""

if [ $result != 0 ]
then
echo "*** ERROR: Clone analysis failed, code $result"
echo "Detailed log in ${system}_${granularity}-clones-${datestamp}.log"
echo ""
exit 99
fi

grep "^Found " "${system}_${granularity}-clones-${datestamp}.log" | tail -1
echo ""

if [ "${cluster}" = "yes" ]
then
    # Compute clone classes
    echo "Clustering clone pairs into classes"
    time ${lib}/scripts/clusterpairs.sh "${pcfile}-clones/*_${granularity}*-clones-${threshold}.xml" >> "${system}_${granularity}-clones-${datestamp}.log" 2>&1

    result=$?
    echo ""

    if [ $result != 0 ]
    then
	echo "*** ERROR: Clustering failed, code $result"
	echo "Detailed log in ${system}_${granularity}-clones-${datestamp}.log"
	echo ""
	exit 99
    fi

    grep "^Clustered " "${system}_${granularity}-clones-${datestamp}.log" | tail -1
    echo ""
fi

if [ "${report}" = "yes" -o "${report}" = "pairs" ]
then
    # Get original sources
    echo "Getting original sources for clones"

    if [ "${report}" = "pairs" ]
    then
	time ${lib}/scripts/getsource.sh "${pcfile}-clones/*_${granularity}*-clones-${threshold}.xml" >> "${system}_${granularity}-clones-${datestamp}.log" 2>&1

	result=$?
	echo ""

	if [ $result != 0 ]
	then
	    echo "*** ERROR: Get sources failed, code $result"
	    echo "Detailed log in ${system}_${granularity}-clones-${datestamp}.log"
	    echo ""
	    exit 99
	fi
    fi

    if [ "${cluster}" = "yes" ]
    then
	time ${lib}/scripts/getsource.sh "${pcfile}-clones/*_${granularity}*-clones-${threshold}-classes.xml" >> "${system}_${granularity}-clones-${datestamp}.log" 2>&1

	result=$?
	echo ""

	if [ $result != 0 ]
	then
	    echo "*** ERROR: Get sources failed, code $result"
	    echo "Detailed log in ${system}_${granularity}-clones-${datestamp}.log"
	    echo ""
	    exit 99
	fi
    fi

    # Convert to HTML
    echo "Making HTML reports"
    if [ "${report}" = "pairs" ]
    then
	time ${lib}/scripts/makepairhtml.sh "${pcfile}-clones/*_${granularity}*-clones-${threshold}-withsource.xml" >> "${system}_${granularity}-clones-${datestamp}.log" 2>&1

	result=$?
	echo ""

	if [ $result != 0 ]
	then
	    echo "*** ERROR: Make HTML failed, code $result"
	    echo "Detailed log in ${system}_${granularity}-clones-${datestamp}.log"
	    echo ""
	    exit 99
	fi
    fi

    if [ "${cluster}" = "yes" ]
    then
	time ${lib}/scripts/makepairhtml.sh "${pcfile}-clones/*_${granularity}*-clones-${threshold}-classes-withsource.xml" >> "${system}_${granularity}-clones-${datestamp}.log" 2>&1

	result=$?
	echo ""

	if [ $result != 0 ]
	then
	    echo "*** ERROR: Make HTML failed, code $result"
	    echo "Detailed log in ${system}_${granularity}-clones-${datestamp}.log"
	    echo ""
	    exit 99
	fi
    fi

elif [ "${report}" = "normalized" -o "${report}" = "normalizedpairs" ]
then
    # Get normalized sources
    echo "Getting normalized sources for clones"
    if [ "${report}" = "normalizedpairs" ]
    then
	time ${lib}/scripts/getnormsource.sh "${pcfile}.xml" "${pcfile}-clones/*_${granularity}*-clones-${threshold}.xml" >> "${system}_${granularity}-clones-${datestamp}.log" 2>&1

	result=$?
	echo ""

	if [ $result != 0 ]
	then
	    echo "*** ERROR: Get normalized sources failed, code $result"
	    echo "Detailed log in ${system}_${granularity}-clones-${datestamp}.log"
	    echo ""
	    exit 99
	fi
    fi

    if [ "${cluster}" = "yes" ]
    then
	time ${lib}/scripts/getnormsource.sh "${pcfile}.xml" "${pcfile}-clones/*_${granularity}*-clones-${threshold}-classes.xml" >> "${system}_${granularity}-clones-${datestamp}.log" 2>&1

	result=$?
	echo ""

	if [ $result != 0 ]
	then
	    echo "*** ERROR: Get normalized sources failed, code $result"
	    echo "Detailed log in ${system}_${granularity}-clones-${datestamp}.log"
	    echo ""
	    exit 99
	fi
    fi

    # Convert to HTML
    echo "Making HTML reports"
    if [ "${report}" = "normalizedpairs" ]
    then
	time ${lib}/scripts/makepairhtml.sh "${pcfile}-clones/*_${granularity}*-clones-${threshold}-normsource.xml" >> "${system}_${granularity}-clones-${datestamp}.log" 2>&1

	result=$?
	echo ""

	if [ $result != 0 ]
	then
	    echo "*** ERROR: Make HTML failed, code $result"
	    echo "Detailed log in ${system}_${granularity}-clones-${datestamp}.log"
	    echo ""
	    exit 99
	fi
    fi

    if [ "${cluster}" = "yes" ]
    then
	time ${lib}/scripts/makepairhtml.sh "${pcfile}-clones/*_${granularity}*-clones-${threshold}-classes-normsource.xml" >> "${system}_${granularity}-clones-${datestamp}.log" 2>&1

	result=$?
	echo ""

	if [ $result != 0 ]
	then
	    echo "*** ERROR: Make HTML failed, code $result"
	    echo "Detailed log in ${system}_${granularity}-clones-${datestamp}.log"
	    echo ""
	    exit 99
	fi
    fi
fi

echo "Done."
echo ""
echo "Detailed log in ${system}_${granularity}-clones-${datestamp}.log"
echo "Results in ${pcfile}-clones/"
if [ "${report}" != "no" ]
then
    echo "Report in" ${pcfile}-clones/*_${granularity}*-clones-${threshold}-*.html
fi
echo ""
date
echo ""
