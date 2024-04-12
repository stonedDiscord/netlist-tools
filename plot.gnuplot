set datafile separator ' '
set xlabel 'Time'
set ylabel 'Voltage'
set y2range [0:12]
plot filename using 1:2 with lines
