# To-do

1. For now I am testing GTK3agg backend for plotting since performance is bad. However, this requires installing c++ build tools from MS and installing: pyproject.toml==0.0.10, pygobject==3.46.0, pygtk==2.24.0. I should optimize plotting performance using blitting which does not require so many dependencies.

2. Add status function (which displays current DAQ status in table format), and include a --monitor argument which causes the table to update each second until the user enters a newline.

3. Fix bugs in stop function and plotting function (see comments.)




