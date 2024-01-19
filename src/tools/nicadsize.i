% NiCad 6.0 limits are controlled here
% Every 20,000 requires about 1 Gb
% Remember that 2 Gb is the maximum process size in Windows, Cygwin and MinGW!

#if HUGE then
    const SIZE := 40000
#else
    const SIZE := 10000
#end if
