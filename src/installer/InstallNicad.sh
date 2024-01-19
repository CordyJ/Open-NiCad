#!/bin/sh
# NiCad 7 Installation script
# Copyright 2024, James R. Cordy and others

echo ""
echo "Installing Nicad 7 on your system."
sleep 1

# Install locations
DEFAULT=true
NICADBIN=/usr/local/bin
NICADLIB=/usr/local/lib/txl

# Localization
unset noclobber

# Check what kind of installation we have here
case `uname -s` in
    CYGWIN*|MSYS*|MINGW64*)
        ;;
    *)
        if [ "`whoami`" != "root" ]
        then
            echo ""
            echo "Error - InstallNicad.sh must be run as root using 'sudo ./InstallNicad.sh'"
            exit 99
        fi
esac
sleep 1

# Install Nicad commands
echo ""
echo "Installing Nicad commands into $NICADBIN"
/bin/mkdir -p $NICADBIN
/bin/cp ./bin/* $NICADBIN
sleep 1

# Install Nicad library
echo ""
echo "Installing Nicad library into $NICADLIB"
/bin/mkdir -p $NICADLIB
/bin/cp -r ./lib/nicad/* $NICADLIB
sleep 1

# Enable the Nicad commands in MacOS
if [ `uname -s` = Darwin ]
then
    echo ""
    echo "Enabling Nicad commands in MacOS"
    spctl --remove --label "NICAD" >& /dev/null
    spctl --add --label "NICAD" $NICADBIN/*
    spctl --add --label "NICAD" $NICADLIB/*/*.x
    spctl --enable --label "NICAD"
fi

# Test Nicad
echo ""
echo "Testing Nicad"
echo ""
sleep 1

$NICADBIN/nicad functions java tests/examples/JHotDraw default-report

echo ""
echo "Done."
echo ""

# Rev 15.1.24
