NiCad clone detection system, Version 7.0 (15 Jan 2024)
-------------------------------------------------------
Software Technology Laboratory, Queen's University
April 2010 (Revised Jan 2024)

Copyright 2011-2024, J.R. Cordy & C.K. Roy

This directory contains all of the parsers and tools necessary to
install and run the NiCad near-miss clone detection system.
NiCad should compile and run correctly on all Linux, MacOS systems,
as well as in Cygwin and Msys2 (MinGW) on Windows.

Installing and Running NiCad
----------------------------
NiCad can be installed on Ubuntu, Mac OS X, Cygwin, MinGW and other 
Unix-like systems with a GCC compiler and an OpenTxl distribution.

1. NiCad 7.0 requires that OpenTxl 11 or later be installed on your system.  
   OpenTxl can be downloaded from: 

      https://github.com/CordyJ/OpenTxl/releases

   Install OpenTxl 11 or later before proceeding.

2. NiCad optimizes by using precompiled TXL programs.  Use the command:

      make

   in this directory to compile all of the NiCad tools and TXL plugins 
   before using NiCad. 

3. (Installation-free option) NiCad requires no further installation for 
   personal use. If you are not planning to install NiCad globally for 
   everyone on your system, and just want to use it yourself in this 
   directory, you can stop here and move on to "Testing NiCad" below.

4. (Optional system installation option) To install NiCad permanently for 
   everyone on the computer (for example, if you have a research group 
   all working on the same compute server), use the command:

      sudo ./Install.sh 

Using NiCad
-----------

1. In a command line window, change directory to any writable directory
   where you intend to run NiCad. If you are using the installation-free 
   option and running NiCad in place, change to this directory.

      cd nicad

2. To run NiCad on a system or application, locate the root source directory
   of the system or application and run the nicad command on it, 
   specifying the analysis granularity and language of the system.

   For example, if you are using the installation-free option,

      ./bin/nicad functions java examples/JHotDraw default-report

   or if NiCad has been installed system-wide,

      nicad functions java examples/JHotDraw default-report

   NiCad can handle three granularities: files, functions and blocks.

   NiCad comes with plugins to handle systems with source files written in the 
   languages: C (.c), C# (.cs), Java (.java), Python (.py), PHP (.php), Ruby (.rb), 
   WSDL (.wsdl) and ATL (.atl). 

   Plugins for other languages can easily be added once you have a TXL grammar
   for the language.

3. Output from NiCad can be found in the ./nicadclones subdirectory of the directory
   where the nicad command is run. For example, results from the command shown above
   can be found in ./nicadclones/JHotDraw. 

   You can find the results in the system or application's clone results directory,
   e.g., ./nicadclones/JHotDraw/JHotDraw_functions--blind-clones for the command above.

   NiCad results are reported in three ways: as clone pairs in XML-like format,
   as clone classes in XML-like format (both with and without original sources), 
   and as browsable HTML pages with clone classes and original source for each clone.

   For the command above, the following results files will be created in the system
   or application's clone results directory:

      Clone pairs in XML-like format:
          JHotDraw_functions-blind-clones-0.30.xml

      Clone classes (clusters) in XML-like format:
          JHotDraw_functions-blind-clones-0.30-classes.xml

   If reports are specified in the configuration (as in "default-report" above)
   then the following additional results files will be created:

      Clone classes (clusters) with original sources for clones in XML-like format:
          JHotDraw_functions-blind-clones-0.30-classes-withsource.xml

      Clone classes (clusters) with original sources for clones as an HTML web-page report:
          JHotDraw_functions-blind-clones-0.30-classes-withsource.html

      The HTML web-page report can be opened and viewed in any standard web browser.

   The 0.30 (or equivalently, 0.00, 0.10, 0.20, ...) indicates the near-miss 
   difference threshold used by NiCad in the clone detection run, where 0.00 means 
   exact clones, 0.10 means at most 10% different pretty-printed lines, and so on.
   The default near-miss threshold is 0.30, as shown above.

4. NiCad supports a wide range of customized clone detection options including
   renaming, filtering, abstraction and custom normalization before comparison 
   using configuration files stored in the ./config subdirectory of the NiCad 
   installation directory.  To use a configuration, run NiCad giving the name of 
   the configuration as the last parameter on the command line.  

   E.g., to use the consistent renaming configuration with HTML web-page reporting,

      ./bin/nicad functions java systems/JHotDraw rename-consistent-report

   Or if NiCad is installed system-wide,

      nicad functions java systems/JHotDraw rename-consistent-report

   When using different configurations, the requested transformations will be 
   applied and the results reported in different results directory, e.g., 

      JHotDraw_functions-clones
      JHotDraw_functions-blind-clones
      JHotDraw_functions-consistent-clones
      JHotDraw_functions-blind-abstract-clones

   and so on.

   The default configurations ("default" and "default-report"), specify blind
   renaming with a near-miss threshold of 0.30, to aggressively find Type 3-2 clones.

4. To re-run NiCad on a system, for example with a different configuration,
   you can simply run the NiCad command on the system again:

       ./bin/nicad functions java systems/JHotDraw type2-report

   Or if NiCad is installed system-wide,

       nicad functions java systems/JHotDraw type2-report

   NiCad will optimize to avoid re-running extraction for the same granularity,
   so subsequent runs on the same system will be significantly faster.

   To remove all clone detection results and intermediate files to start over 
   and force a new extraction from the same system, run the command:

       ./bin/nicadclean JHotDraw 

   Or if NiCad is installed system-wide,

       nicadclean JHotDraw 

   To remove all results and intermediate files of all previous NiCad runs,
   use the command:
     
       ./bin/nicadclean

    or:
        nicadclean

NiCadCross
-----------
NiCadCross is the NiCad cross-clone detector.  It does an cross-system test 
- that is, given two systems s1 and s2, it reports only clones of fragments 
of s1 in s2.  This is useful in incremental clone detection for new versions, 
or for detecting clones between two systems to be checked for cross-cloning.

NiCadCross is run in much the same way as NiCad, but giving a second system
source directory on the command line, for example:

      ./bin/nicadcross functions java systems/JHotDraw54b1 systems/JHotDraw76a2 default-report

Results are stored in the first system's cross-clone results directory, 
e.g., ./nicadclones/JHotDraw541/JHotDraw541_functions-blind-crossclones for the command above.

Maintenance and Extension of NiCad
-----------------------------------
Maintaining or adding NiCad TXL plugins is easy - you just create the new
programs with appropriate names (see the ./txl subdirectory of the NiCad 
installation directory for examples), and NiCad will automatically allow
your new plugins to be used as normalizations or languages.

If you plan to change, maintain or recompile the NiCad clone comparison
tools themselves, you will require Turing+ 6.2 or later to be installed on your system.  
See the ./src/tools subdirectory of the NiCad source distribution for details.  

Turing+ can be downloaded from: 
 
      https://github.com/CordyJ/TuringPlus/releases

Rev 15.1.24
