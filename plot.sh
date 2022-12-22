#!/usr/bin/env bash
#		GMT EXAMPLE 30
#
# Purpose:	Show graph mode and math angles
# GMT modules:	gmtmath, basemap, text and plot
# Unix progs:	echo, rm
#
# Draw generic x-y axes with arrows
gmt begin altitude

	gmt set GMT_THEME cookbook
    # gmt set FORMAT_TIME_STAMP "%Y-%b-%dT%H-%M-%S"
    gmt info altitude.txt
    gmt info altitude2.txt
    gmt info altitude3.txt
    gmt plot altitude.txt -R1671578773/1671591059/14.8019651667/14.8023386667 -B -Wfaint
    gmt plot altitude2.txt -R1671578773/1671591059/50.2165378333/50.2166485 -B -Wfaint,red
    gmt plot altitude3.txt -R1671578773/1671591059/174/213.4 -B -Wfaint,blue

gmt end show
