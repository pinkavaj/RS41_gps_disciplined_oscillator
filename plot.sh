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
    gmt plot altitude.txt -Ra -B -Wfaint

gmt end show
