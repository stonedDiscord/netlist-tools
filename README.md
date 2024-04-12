# netlist-tools
This repository has 2 tools:

## plot
This is supposed to live in MAMEs src/lib/netlist/build folder and will automatically run the netlist and then start gnuplot to create a graph of that netlist.

## nlconvert
This is a python script that will use kinparse to convert KiCAD netlists to MAME ones, skipping the SPICE step.
This avoids a bug in KiCADs SPICE netlist exporter that will omit all parts from multipart symbols except the first one.