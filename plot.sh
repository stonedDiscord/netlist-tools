#!/bin/bash
# usage: ./plot.sh atari/nl_pong.cpp videomix
# this is supposed to live next to nltool in src/lib/netlist/build
# default is 1 second
./nltool -c run -t 0.05 -l $2 ../../../mame/$1
gnuplot -p -e "filename='log_${2}.log';" plot.gnuplot 
