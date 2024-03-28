#!/bin/sh
# Nicad Version 7 Uninstallation script
# Copyright 2024, James R. Cordy and others

echo ""
echo "Removing Nicad from your system."
sleep 1

# Default locations
DEFAULT=true
NICADBIN=/usr/local/bin
NICADLIB=/usr/local/lib/nicad

# Localization
unset noclobber

# Check what kind of installation we have here
if [ "`whoami`" != "root" ] 
then
        echo ""
        echo "Error - UninstallNicad must be run as root using 'sudo ./UninstallNicad'"
        exit 99
fi

sleep 1

# Uninstall Nicad commands
echo ""
echo "Uninstalling Nicad commands from $NICADBIN"
/bin/rm -f $NICADBIN/nicad $NICADBIN/nicadcross $NICADBIN/nicadclean $NICADBIN/nicadfix $NICADBIN/nicadsplit
sleep 1

# Uninstall Nicad library
echo ""
echo "Uninstalling the Nicad library $NICADLIB"
/bin/rm -rf $NICADLIB
sleep 1

echo ""
echo "Done."
echo ""

# Rev 15.1.24
