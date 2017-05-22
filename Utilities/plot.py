__author__ = 'Bill'

import sys
import matplotlib
matplotlib.use('SVG')
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import spline
import string
import math
import xlrd

class PlotInfo(object):
    def __init__(self):
        self.dataSets = []
        self.xlimLow = None
        self.xlimHigh = None
        self.ylimLow = None
        self.ylimHigh = None
        self.xaxisTitle = None
        self.yaxisTitle = None
        self.smoothPlot = False
        self.legendLoc = None
        self.title = None
        self.numplots = 1

    def readPlotInfo(self, fileName):
        currentDataSet = None
        infile = open(fileName, 'r')
        for line in infile:
            try:
                command, parameters = line.split(':')
            except:
                pass
            command = command.strip()
            parameters = parameters.strip()
            if command == 'title':
                self.title = parameters
            elif command == 'plots':
                self.numplots = int(parameters)
            elif command == 'xlimits':
                xlimLow, xlimHigh = parameters.split(',')
                self.xlimLow = float(xlimLow)
                self.xlimHigh = float(xlimHigh)
            elif command == 'ylimits':
                ylimLow, ylimHigh = parameters.split(',')
                self.ylimLow = float(ylimLow)
                self.ylimHigh = float(ylimHigh)
            elif command == 'xaxisTitle':
                self.xaxisTitle = parameters
            elif command == 'yaxisTitle':
                self.yaxisTitle = parameters
            elif command == 'legend':
                self.legendLoc = parameters
            elif command == 'dataSet':
                parmlist = parameters.split(',')
                currentDataSet = int(parmlist[0])-1
                if len(parmlist) == 1:
                    parmlist.append(1)
                self.dataSets.append({'subplot':int(parmlist[1])})
            elif command == 'name':
                self.dataSets[currentDataSet]['name'] = parameters
            elif command == 'xdata':
                self.dataSets[currentDataSet]['xpoints'] = np.array(parameters.split(','))
            elif command == 'ydata':
                self.dataSets[currentDataSet]['ypoints'] = np.array(parameters.split(','))
        infile.close()

    def readPlotInfoExcel(self, sheet):
        rows = sheet.nrows
        cols = sheet.ncols
        plotstartrow = None
        for row in range(0, rows):
            command = sheet.cell(row, 0).value
            parameters = sheet.cell(row, 1).value
            print (str(command) + ", " + str(parameters));
            if command == 'title':
                self.title = parameters
            elif command == 'xlimits':
                if (parameters != ""):
                    xlimLow, xlimHigh = parameters.split(',')
                    self.xlimLow = float(xlimLow)
                    self.xlimHigh = float(xlimHigh)
            elif command == 'ylimits':
                if (parameters != ""):
                    ylimLow, ylimHigh = parameters.split(',')
                    self.ylimLow = float(ylimLow)
                    self.ylimHigh = float(ylimHigh)
            elif command == 'xaxisTitle':
                self.xaxisTitle = parameters
            elif command == 'yaxisTitle':
                self.yaxisTitle = parameters
            elif command == 'legend':
                self.legendLoc = parameters
            elif command in ['name_1', 'name_2', 'name_3', 'name_4']:
                datasetID = command[-1:]
                print ("dataset " + str(datasetID))
                self.dataSets.append({'subplot':int(datasetID)})
                self.dataSets[int(datasetID)-1]['name'] = parameters
                pass
            elif command == 'plots':
                plotstartrow = row+1
                break

        headers = sheet.row_values(plotstartrow)
        for col in range(0, cols):
            points = []
            for row in range(plotstartrow+1, rows):
                points.append(float((sheet.cell(row, col).value)))
            axis, number = headers[col].split("_")
            if axis == 'xdata':
                self.dataSets[int(number)-1]['xpoints'] = np.array(points)
            elif axis == 'ydata':
                self.dataSets[int(number)-1]['ypoints'] = np.array(points)
            else:
                print("Axis %s Not recognized!" %axis)
        return


def graphIt(plotsInfo, outFileName):

    numplots = len(plotsInfo)
    plotrows = math.floor((numplots+1)/2)
    if numplots > 1:
        plotcols = 2
    else:
        plotcols = 1

    plt.style.use('plotStyle.mplstyle') # set up plot styling
    plt.figure(num=1, figsize=(4*plotcols,3.4*plotrows))
    plt.subplots_adjust(bottom=0.15,top=0.9,wspace=0.3,hspace=0.4)

    for plotnum, plotInfo in enumerate(plotsInfo):
        plt.subplot(plotrows, plotcols, (plotnum+1))
        if plotInfo.title != None:
            plt.title(plotInfo.title)

        for dataSet in plotInfo.dataSets:
            xpoints = dataSet['xpoints']
            ypoints = dataSet['ypoints']

            # xnew = np.linspace(xpoints.min(),xpoints.max(),5*len(xpoints))
            # ysmooth = spline(xpoints, ypoints, xnew)

            plt.plot(xpoints,ypoints, label=dataSet['name'])

        if plotInfo.legendLoc != None:
            plt.legend(loc=plotInfo.legendLoc)

        if plotInfo.xaxisTitle != None:
            plt.xlabel(plotInfo.xaxisTitle)
        if plotInfo.yaxisTitle != None:
            plt.ylabel(plotInfo.yaxisTitle)

        # ax = plt.subplot(111)
        # ax.spines['left'].set_position('center')
        # ax.spines['right'].set_color('none')

        # ax.spines['bottom'].set_position('center')
        # ax.spines['top'].set_color('none')

        if plotInfo.xlimLow != None:
            plt.xlim(plotInfo.xlimLow, plotInfo.xlimHigh)
        if plotInfo.ylimLow != None:
            plt.ylim(plotInfo.ylimLow, plotInfo.ylimHigh)

    # plt.xticks(range(5, 30, 5))

    # plt.show()
    filename = removeDisallowedFilenameChars(outFileName)

    # plt.tight_layout()
    plt.savefig(filename)
    plt.close(1)

def removeDisallowedFilenameChars(filename):
    validFilenameChars = "-_() %s%s%s" % (string.ascii_letters, string.digits,"\\/")
    fileout = ""
    for char in filename:
        if str(char) in validFilenameChars:
            if str(char) == " ":
                char = "_"
            fileout += str(char)
#     return ''.join(c for c in cleanedFilename if c in validFilenameChars)
    return (fileout)


if __name__ == "__main__":

    filetype = None
    if (len(sys.argv) < 3):
        try:
            wb = xlrd.open_workbook(sys.argv[1])
            print ("Excel File")
            filetype = "excel"
        except:
            print ("Text Files")
            filetype = "text"

        if (filetype == "excel"):
            outFileName = sys.argv[1].split(".")[0]
            print ("output @ " + outFileName)
            plotsInfo = []
            for plotnum in range(1,5):
                try:
                    sheet = wb.sheet_by_name("Plot_" + str(plotnum))
                    print ("Reading Sheet Plot_" + str(plotnum))
                except:
                    continue
                plotInfo = PlotInfo()
                plotInfo.readPlotInfoExcel(sheet)
                plotsInfo.append(plotInfo)
            graphIt(plotsInfo, outFileName)

        elif (filetype == "text"):
            plotDefs = open(sys.argv[1], 'r')

            for plotLine in plotDefs:
                plotParms = plotLine.split(',')
                outFileName = plotParms[0]
                plotsInfo = []
                for filename in plotParms[1:]:
                    print(filename)
                    plotInfo = PlotInfo()
                    plotInfo.readPlotInfo(filename.strip())
                    plotsInfo.append(plotInfo)
                graphIt(plotsInfo, outFileName)

            plotDefs.close()
        else:
            print ("Unrecognized file type")

    else:
        print ("Single Text File")
        outFileName = sys.argv[1]
        plotsInfo = []
        for filename in sys.argv[2:]:
            plotInfo = PlotInfo()
            plotInfo.readPlotInfo(filename)
            plotsInfo.append(plotInfo)

        graphIt(plotsInfo, outFileName)
