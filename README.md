# TimeMeasurementsScripts
This is a small collection of scripts to measure the execution time of a windows executable and visualize the measured time.

Currently they support the ability to measure time for a given executable and print the results in a defined format. This format can then be parsed by PerformanceGraphs.py to produce a set of graphs depending on how much data was presented.

## Usage
In order to use these script you properly just want to read the .bat and .ps1 files to give yourself an understanding of how they work. As the structure of your arguments is highly depending on what you want to do, there is currently no explanation on how to utilize the parameter as they can change in the future.

In order to use the PerformanceGraphs.py your data has to be structured in the form:
```
identifier<delimiter>time<delimiter>time<delimiter>time...
identifier<delimiter>time<delimiter>time<delimiter>time...
...
```
Hereby the identifier must consist of three parts separated by `$` where the last part stands for the number of threads used in the run and the other are for grouping the data for comparisons.

Note: A thread count of 0 stands for the (normally sequential) baseline to use.

## Contributing
Feel free to fork the script and adapt it to your needs. When you feel that you made a change that could be beneficial for this repository feel free to open a PR.
