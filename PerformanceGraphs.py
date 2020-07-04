#! /usr/bin/env nix-shell
#! nix-shell -i python3 -p python3 python36Packages.matplotlib

# (C) Copyright 2018-2019 Hewlett Packard Enterprise Development LP

# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR
# OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.

import random
import math
import sys
import matplotlib.pyplot as plt
import matplotlib.cbook as cbook
import numpy as np
import statistics as st
import os
import argparse # TODO utilize
import logging

#lambdas
lambdaPerformanceTime = lambda x: x[1].mean
lambdaSpeedup = lambda x: x[1].speedup
lambdaPerformanceTimeError = lambda x: x[1].stdev
lambdaSpeedupError = lambda x: x[1].speedupError
lambdaParallelEfficiency = lambda x: x[1].parallelEfficiency * 100
lambdaData = lambda x: np.array(x[1].data)

#plotnames
plotNameExecutionTime = "executionTime"
plotNameExecutionTimeViolin = "executionTimeViolin"
plotNameSpeedup = "speedup"
plotNameParallelEfficiency = "parallelEfficiency"
plotNameSpeedupParallelEfficiency = "speedupAndParallelEfficiency"


cli = argparse.ArgumentParser()
cli.add_argument('--delim', '-d', nargs='?', default=';', dest='delim', help='Specifies the delimiter used between single time measurements. Default: ;')
cli.add_argument('--outdir', '-o', nargs='?', default='out', dest='outdir', help='The directory to output the data. The directory is created when not existing. If files are already in there they are overwritten. Default: out')
cli.add_argument('--time-unit', nargs='?', default='ms', dest='time_unit', help='The time unit to print as a label to the diagrams. Default: ms')
cli.add_argument('--hide-x-label', action='store_true', dest='hide_x_label', help='Hides the x label from every Graph. Use this if the label does not fit your use case.')
cli.add_argument('--defaultName', nargs='?', default='default', dest='defaultTestCaseName', help='Defines the default name of a test without a name in the identifier. Default: default')
cli.add_argument('--baselineIndex', '-b', nargs='?', default=0, type=int, dest='baselineIndex', help='Define which index to assume for a baseline to calculate speedup and scalability Default: 0')
cli.add_argument('input', nargs='?', type=argparse.FileType('r'), default=sys.stdin, help='File to read for input data. Defaults to reading stdin')
args = cli.parse_args()

# global variables and read parameters
#y_labels
y_label_Time = f"time in {args.time_unit}"
y_label_Speedup = f"speedup in {args.time_unit}/{args.time_unit}"
y_label_ScaleEff= "parallel efficiency in %"
x_label_numberThreads = "Number of threads used"
if args.hide_x_label:
    x_label_numberThreads = ""


#delim = ";"
if args.delim == None and not type(args.delim) == str:
    raise BaseException("No delimeter specified")

#defaultTestCaseName = "default"

#outdir = "out"
#if outdir == None:
#    outdir = "out"
if args.outdir.endswith('/'):
    args.outdir = args.outdir[:-1]

def createFolder(directory):
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
    except OSError:
        print ('Could not create directory: ' +  directory)
        raise

createFolder(args.outdir)

#def testCaseFolder(testCase):
    #if testCase == None or testCase == "":
        #raise "no Test case specified"
    #if outdir != None and outdir != "":
        #return outdir + "/" + testCase + "/"
    #else:
        #return testCase + "/"

print("Using the following values")
print("\toutdir= " + args.outdir)
print("\tdeliminator= " + args.delim)
print("\tdefault test name= " + args.defaultTestCaseName)
print("\ttime unit= " + args.time_unit)
if args.input is sys.stdin:
    print("\tReading from stdin")
else:
    print("\tReading from file")
if args.hide_x_label:
    print("\tHiding x-labels")

#-------------class Definitions
class SingleTestRun:
    def __init__(self, caseName="", machine="", numThreads="a", data=None):
        self.caseName = caseName
        if self.caseName == None or self.caseName == "": self.caseName = args.defaultTestCaseName
        self.machine = machine
        if self.machine == None or self.machine == "": raise BaseException("machine can't be empty string")
        self.numThreads = int(numThreads)
        self.minimum=min(data)
        self.maximum=max(data)
        self.mean=st.mean(data)
        self.stdev=st.stdev(data)
        self.data=data
        self.relativeError=self.stdev / self.mean
        self.baselineReceived=False

    def calculateValuesFromBaseline(self, baseline):
        if not type(baseline) is SingleTestRun: raise BaseException("Expected Single test run as baseline")
        self.baselineReceived = True
        if self==baseline:
            self.speedup = 1.0
            self.parallelEfficiency = 1.0
            self.speedupError = self.relativeError # * 1.0
        else:
            self.speedup = baseline.mean / self.mean
            self.parallelEfficiency = self.speedup / self.numThreads
            self.speedupError = (self.relativeError + baseline.relativeError) * self.speedup

    def draw(self):
        folder = self.__createTestCaseFolder()
        self.__zero_basedScatter(folder)
        self.__simpleScatter(folder)

    def report(self):
        folder = self.__createTestCaseFolder()
        with open(folder + "/" + "report.txt", 'w') as f:
            f.write(self.toString(separator='\n'))
            f.write('\n') # Line break at end of line for easier reading

    def getCaseIdentifier(self):
        return self.caseName + "$" + self.machine + "$" + str(self.numThreads)

    def toString(self, separator=" "):
        stringData =  self.getCaseIdentifier() + ":"
        stringData += separator + "min: " + str(self.minimum)
        stringData += separator + "max: " + str(self.maximum)
        stringData += separator + "mean: " + str(self.mean)
        stringData += separator + "stdev: " + str(self.stdev)
        stringData += separator + "relativeError: " + str(self.relativeError)
        if self.baselineReceived:
            stringData += separator + "speedup: " + str(self.speedup)
            stringData += separator + "speedupError: " + str(self.speedupError)
            stringData += separator + "parallelEfficiency: " + str(self.parallelEfficiency)
        else:
            stringData += separator + "No baseline received yet"
        return stringData

    def __repr__(self):
        return self.toString()
    def __str__(self):
        return self.toString()

    def __createTestCaseFolder(self):
        folder = args.outdir + "/" + self.caseName
        createFolder(folder)
        folder += "/" + self.machine
        createFolder(folder)
        folder += "/" + str(self.numThreads)
        createFolder(folder)
        return folder

    def __zero_basedScatter(self, folder):
        x_axis = list(range(len(self.data)))
        plt.clf()
        plt.scatter(x=x_axis, y=self.data, marker=".")
        plt.xlabel("n th run")
        plt.ylabel(y_label_Time)
        plt.ylim(bottom=0)
        createFolder(folder)
        plt.savefig(folder + "/zeroBasedScatter.pdf")

    def __simpleScatter(self, folder=""):
        x_axis = list(range(len(self.data)))
        plt.clf()
        plt.scatter(x=x_axis, y=self.data, marker=".")
        plt.axis('tight')
        plt.xlabel("n th run")
        plt.ylabel(y_label_Time)
        createFolder(folder)
        plt.savefig(folder + "/simpleScatter.pdf")


class MachineTestCase:
    def __init__(self, machine="", caseName=""):
        self.caseName = caseName
        if self.caseName == None or self.caseName == "": self.caseName = args.defaultTestCaseName
        self.machine = machine
        if self.machine == None or self.machine == "": raise BaseException("machine can't be empty string")
        self.testRuns = {}

    def addTestRun(self, testRun):
        if not type(testRun) is SingleTestRun: raise TypeError("Expected object of type SingleTestRun")
        if testRun.numThreads in self.testRuns:
            print(self)
            print(testRun)
            raise RuntimeError("Test run already exists: " + testRun.getCaseIdentifier())
        self.testRuns[testRun.numThreads] = testRun

    def __repr__(self):
        return str(self.runsPerMachine)

    def __createTestCaseFolder(self):
        folder = args.outdir + "/" + self.caseName
        createFolder(folder)
        folder += "/" + self.machine
        createFolder(folder)
        return folder

    def generateBaseLine(self, index=0):
        baseline = self.testRuns.get(index, None)
        if not baseline: return False
        for run in self.testRuns.values():
            run.calculateValuesFromBaseline(baseline)
        return True

    def __drawGraph(self, mappingData=None, mappingError=None, plotName="", folder="", y_label="", drawViolin=False):
        if not type(plotName) is str or plotName=="": raise BaseException("Expected plotName that is non empty string")
        if not type(folder) is str or folder=="": raise BaseException("Expected folder that is non empty string")
        plt.clf()
        if drawViolin:
            self.drawViolinPartFromLampda(mappingData)
        else:
            self.drawPartFromLampda(mappingData, mappingError)
        plt.xlabel(x_label_numberThreads)
        plt.ylabel(y_label)
        plt.ylim(bottom=0)
        createFolder(folder)
        plt.savefig(folder + "/" + plotName + ".pdf", bbox_inches='tight')

    def __drawGraphTwins(self, mappingData1=None, mappingData2=None, mappingError1=None, mappingError2=None, plotName="", folder="", y_label1="", y_label2=""):
        if not type(plotName) is str or plotName=="": raise BaseException("Expected plotName that is non empty string")
        if not type(folder) is str or folder=="": raise BaseException("Expected folder that is non empty string")
        plt.clf()
        fig, ax1 = plt.subplots()
        self.drawPartFromLampda(mappingData1, mappingError1, plt=ax1, fmt='b-')
        ax1.set_xlabel(x_label_numberThreads)
        ax1.set_ylabel(y_label1, color='b')
        ax1.set_ylim(bottom=0)
        ax1.tick_params('y', colors='b')

        ax2 = ax1.twinx()
        self.drawPartFromLampda(mappingData2, mappingError2, plt=ax2, fmt='r-')
        ax2.set_ylabel(y_label2, color='r')
        ax2.set_ylim(bottom=0)
        ax2.tick_params('y', colors='r')

        createFolder(folder)
        plt.savefig(folder + "/" + plotName + ".pdf", bbox_inches='tight')


    def drawPartFromLampda(self, mappingData=None, mappingError=None, plt=plt, **kwargs):
        if mappingData == None or mappingError == None: raise BaseException("Expected mapping functions do determine what to draw")
        dictionarySortedByK = sorted(self.testRuns.items())
        x_data = list(map(lambda x: x[0], dictionarySortedByK))
        y_data = list(map(mappingData, dictionarySortedByK))
        y_err = list(map(mappingError, dictionarySortedByK))
        plt.errorbar(x_data, y_data, y_err, label=self.machine, **kwargs)

    def drawPartFromLampdaBar(self, mappingData=None, mappingError=None, plt=plt, width=0.9, offset=-0.45, **kwargs):
        if mappingData == None or mappingError == None: raise BaseException("Expected mapping functions do determine what to draw")
        dictionarySortedByK = sorted(self.testRuns.items())
        x_data = np.array(list(map(lambda x: x[0], dictionarySortedByK))) + offset
        y_data = list(map(mappingData, dictionarySortedByK))
        y_err = list(map(mappingError, dictionarySortedByK))
        plt.bar(x_data, y_data, label=self.machine, yerr=y_err, width=width, **kwargs)

    def drawViolinPartFromLampda(self, mappingData=None):
        if mappingData == None: raise BaseException("Expected mapping functions do determine what to draw")
        dictionarySortedByK = sorted(self.testRuns.items())
        x_data = list(map(lambda x: x[0], dictionarySortedByK))
        y_data = list(map(mappingData, dictionarySortedByK))
        # can't add label for violin plot therefor not adding it
        plt.violinplot(y_data, x_data, showmeans=True)

    def drawAll(self, baselineIndex=0):
        self.draw(baselineIndex=baselineIndex)
        for testRun in self.testRuns.values():
            testRun.draw()

    def reportAll(self):
        for testRun in self.testRuns.values():
            testRun.report()

    def draw(self, baselineIndex=0):
        if len(self.testRuns) <= 1:
            logging.warning(self.caseName + "$" + self.machine + ": Skip drawing graphs because only one datapoint to draw")
        else:
            folder = self.__createTestCaseFolder()
            self.__drawGraph(lambdaPerformanceTime, lambdaPerformanceTimeError, plotNameExecutionTime, folder, y_label_Time)
            self.__drawGraph(lambdaData, plotName=plotNameExecutionTimeViolin, folder=folder, y_label=y_label_Time, drawViolin=True)
            if self.generateBaseLine(index=baselineIndex):
                self.__drawGraph(lambdaSpeedup, lambdaSpeedupError, plotNameSpeedup, folder, y_label_Speedup)
                self.__drawGraph(lambdaParallelEfficiency, lambda x: 0, plotNameParallelEfficiency, folder, y_label_ScaleEff)
                self.__drawGraphTwins(lambdaSpeedup, lambdaParallelEfficiency, lambdaSpeedupError, lambda x: 0, plotNameSpeedupParallelEfficiency, folder, y_label_Speedup, y_label_ScaleEff)
            else:
                logging.warning(self.caseName + "$" + self.machine + ": Skipping speedup and parallel efficiency because not all baselines were found")


class TestCase:
    def __init__(self, caseName=""):
        self.caseName = caseName
        if self.caseName == None or self.caseName == "": self.caseName = args.defaultTestCaseName
        self.machines = {}

    def addTestRun(self, testRun):
        if not type(testRun) is SingleTestRun: raise TypeError("Expected object of type SingleTestRun")
        if not testRun.machine in self.machines:
            self.machines[testRun.machine] = MachineTestCase(testRun.machine, self.caseName)
        self.machines[testRun.machine].addTestRun(testRun)

    def __repr__(self):
        return str(self.runsPerMachine)

    def __createTestCaseFolder(self):
        folder = args.outdir + "/" + self.caseName
        createFolder(folder)
        return folder

    def __drawGraph(self, mappingData=None, mappingError=None, plotName="", folder="", y_label=""):
        if not type(plotName) is str or plotName=="": raise BaseException("Expected plotName that is non empty string")
        if not type(folder) is str or folder=="": raise BaseException("Expected folder that is non empty string")
        plt.clf()
        for machine in self.machines.values():
            machine.drawPartFromLampda(mappingData, mappingError)
        plt.xlabel(x_label_numberThreads)
        plt.ylabel(y_label)
        plt.ylim(bottom=0)
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0.)
        createFolder(folder)
        plt.savefig(folder + "/" + plotName + ".pdf", bbox_inches='tight')

    def __drawGraphBar(self, mappingData=None, mappingError=None, plotName="", folder="", y_label=""):
        if not type(plotName) is str or plotName=="": raise BaseException("Expected plotName that is non empty string")
        if not type(folder) is str or folder=="": raise BaseException("Expected folder that is non empty string")
        plt.clf()
        width = 0.9 / len(self.machines)
        offset = -0.45 + width / 2 # Center around mark at this point
        for machine in self.machines.values():
            machine.drawPartFromLampdaBar(mappingData, mappingError, offset=offset, width=width)
            offset += width
        plt.xlabel(x_label_numberThreads)
        plt.ylabel(y_label)
        plt.ylim(bottom=0)
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0.)
        createFolder(folder)
        plt.savefig(folder + "/" + plotName + "Bar.pdf", bbox_inches='tight')

    def drawAll(self, baselineIndex=0):
        self.draw(baselineIndex=baselineIndex)
        for machine in self.machines.values():
            machine.drawAll(baselineIndex=baselineIndex)

    def reportAll(self):
        for testRun in self.machines.values():
            testRun.reportAll()

    def draw(self, baselineIndex=0):
        if len(self.machines) <= 1:
            logging.warning(self.caseName + ": Skip drawing graphs because only one datapoint to draw")
        else:
            folder = self.__createTestCaseFolder()
            hasAllBaselines = True
            for machine in self.machines.values():
                if not machine.generateBaseLine(index=baselineIndex): hasAllBaselines = False
            self.__drawGraph(lambdaPerformanceTime, lambdaPerformanceTimeError, plotNameExecutionTime, folder, y_label_Time)
            self.__drawGraphBar(lambdaPerformanceTime, lambdaPerformanceTimeError, plotNameExecutionTime, folder, y_label_Time)
            if hasAllBaselines:
                self.__drawGraph(lambdaSpeedup, lambdaSpeedupError, plotNameSpeedup, folder, y_label_Speedup)
                self.__drawGraphBar(lambdaSpeedup, lambdaSpeedupError, plotNameSpeedup, folder, y_label_Speedup)
                self.__drawGraph(lambdaParallelEfficiency, lambda x: 0, plotNameParallelEfficiency, folder, y_label_ScaleEff)
                self.__drawGraphBar(lambdaParallelEfficiency, lambda x: 0, plotNameParallelEfficiency, folder, y_label_ScaleEff)
            else:
                logging.warning(self.caseName + ": Skipping speedup and parallel efficiency because not all baselines were found")


# ------------------- program
testcases = {}
for testCaseString in args.input:# go through each line of the input
    testCaseString.rstrip() # strip any trailing whitespace like linebreaks
    numbers = testCaseString.split(args.delim) # splitting for the numbers

    # take the case identifier apart and remove it from start of list
    testCaseIdentifier = numbers.pop(0).split('$')
    caseName = testCaseIdentifier[0]
    machineIdentifier = testCaseIdentifier[1]
    numThreads = int(testCaseIdentifier[2])
    numbers = list(map(lambda x: float(x), numbers))
    testCaseObj = SingleTestRun(
        caseName = caseName,
        machine = machineIdentifier,
        numThreads = numThreads,
        data=numbers[:]
    )

    # if first test case then add empty dictionaries
    if not caseName in testcases:
        testcases[caseName] = TestCase(caseName)

    testcases[caseName].addTestRun(testCaseObj)

# Output all diagrams to disk
for testCase in testcases.values():
    print("Start drawing test case: " + testCase.caseName)
    testCase.drawAll(baselineIndex=args.baselineIndex)
    print("Start report for test case: " + testCase.caseName)
    testCase.reportAll()
