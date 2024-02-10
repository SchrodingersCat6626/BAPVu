#!/usr/bin/python3
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib import animation
import numpy as np
import matplotlib.style as mplstyle
from numpy import genfromtxt
mplstyle.use('fast')

"""
    To do: 

        -Optimize performance of plotting (very slow).
        -Set blit to True to optimize performance.

        -ignore columns that are non numeric (ie. 'off')
        
        - add enough colours for 16 channels. Set limit of devices to 4 (16 channels)


"""

import os
import time
from itertools import groupby
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from random import randrange

def readNewChunk(filename,chunkSize=None):
    """ Reads the end of file to obtain new chunk of data.
    By default chunk_size is set to None. If this is the case. It will read from end to file to beginning if a chunk size is specified.
    """
    if chunkSize is not None:
        with open(filename, 'rb') as f:
            try:  # catch OSError in case of a one line file 
                newline_counter = 0

                f.seek(-2, os.SEEK_END)
            
                while newline_counter!=chunkSize: # reads current byte
                
                    f.seek(-2, os.SEEK_CUR) ## moves two char back from current position.
                
                    if f.read(1) == b'\n':
                        newline_counter = newline_counter+1


            except OSError:
                f.seek(0)
        
            chunk = f.readlines()
            f.close()

    else:
        with open(filename, 'rb') as f:
            
            chunk = f.readlines()
            f.close()


    return chunk



def decode_chunk(chunk,nth=None,removeFirstLine=False,maxLines=None):
    """ Takes in a new chunk. Decodes it and returns a list of list. Every line of data is a list
    """

    new_chunk = [[]]

    lineNumber = 0

    for line in chunk:

        if maxLines is not None:
            if lineNumber == maxLines:
                break
            else:
                lineNumber = lineNumber + 1

        line = line.decode()
        line = line.split(sep=',')
        if nth is not None:
            line = remove_every_nth(line,nth,skip_first_element=True) # removes every nth (to get rid of unit cols)
        new_chunk.append(line)


    del new_chunk[0] # removing first empty list

    if removeFirstLine == True:
        del new_chunk[0] # used to delete heading (typically)

    return new_chunk


def animate2(i):
    if filesize_prev != os.path.getsize(file):
        #loads data from file
        data = pd.read_csv(file)
        data = data.loc[:,~data.columns.str.startswith('unit')] # removing the unit columns
        #time column (x-values)
        x = data['systime']
        #clears axis
        plt.cla()
        #gets all the y data. i is the current frame... I think.... 
        [[data[column][i] for column in dataHeader] for empty_lists in list_of_dataHeader]
        #plotting axis... I think...
        for idx, ax in enumerate(axs, start=1):   # start=1 makes index 1, since we ignore the first item of list of columns
            ax.plot(x, data[dataHeader[idx]], label=dataHeader[idx], color=col[idx])

        filesize_prev = os.path.getsize(file)

    else:
        sleep(1) ### do not update plot if the filesize hasn't changed.

    return

    
def remove_every_nth(lst, n,skip_first_element=True):
    if skip_first_element:
        time=lst[0]
        lst=lst[1::]
        del lst[n-1::n]
        lst.insert(0, time)
    else:
        del lst[n-1::n]
    return lst

def convToFloat(x):
    try:
        value = float(x)

    except ValueError:
        return None

    return value

def convToInt(x):
    try:
        value = int(x)

    except ValueError:
        return None

    return value

def convToStr(x):
    try:
        value = str(x)

    except ValueError:
        return None

    return value

def select(lstOfLsts,index,dtype='float'):
    """ To select an element of index i in each list for a list of list
    Effectively acting like selecting a column in dataset.
    """
    if dtype=='float':

        newList = [convToFloat(lst[index]) for lst in lstOfLsts]

    elif dtype=='int':

        newList = [convToInt(lst[index]) for lst in lstOfLsts]

    elif dtype=='str':

        newList = [convToStr(lst[index]) for lst in lstOfLsts]

    else:

        print('Invalid dtype!')

        return None

    return newList




def initPlot(filename):
    """ To read initial data from file """
    

    return data





def plot(filename,chunk_size):
    # Given that I know that the number of channels can be 4 or 8 or 12 or 16.
    # Since I have a limit of 4 daqs, have just set 4 different if statements
    # for 4 different animations
    # based on: https://stackoverflow.com/questions/29832055/animated-subplots-using-matplotlib#29834816

    col = ["#000000", "#E69F00", "#56B4E9", "#009E73","#F0E442", "#0072B2", "#D55E00", "#CC79A7" , "#0e2f8a", "#210f87",'#531078','#801455', '#8f1622']
    
    data = readNewChunk(filename) # reading all data from file

    dataHeader = decode_chunk(data,nth=2,maxLines=1) # getting headers
    dataHeader = dataHeader[0] # converting to list instead of list of list

    initialData = decode_chunk(data,nth=2,removeFirstLine=True) # getting data

    #initialData = np.array(initialData,dtype=float) # converting to array

    
    number_of_channels = len(dataHeader)
    timecolumns = 1 # the first column is time. There is one time column.
        

    if len(initialData) == 0:
        # initialize empty data lists
        if number_of_channels >= 4 + timecolumns:
            xdata, y1data, y2data, y3data, y4data = [], [], [], [], []
        elif number_of_channels >= 8 + timecolumns:
            xdata, y1data, y2data, y3data, y4data, y5data, y6data, y7data, y8data = [], [], [], [], [], [], [], [], []
        elif number_of_channels >= 12 + timecolumns:
            xdata, y1data, y2data, y3data, y4data, y5data, y6data, y7data, y8data, y9data, y10data, y11data, y12data = [], [], [], [], [], [], [], [], [], [], [], [], []
    else:
        # Initialize arrays with data
                # initialize empty data arrays
        if number_of_channels == 4 + timecolumns:
            xdata, y1data, y2data, y3data, y4data = select(initialData,0), select(initialData,1), select(initialData,2), select(initialData,3), select(initialData,4)
        elif number_of_channels == 8 + timecolumns:
            xdata, y1data, y2data, y3data, y4data, y5data, y6data, y7data, y8data = select(initialData,0), select(initialData,1), select(initialData,2), select(initialData,3), select(initialData,4), select(initialData,5), select(initialData,6), select(initialData,7), select(initialData,8)
        elif number_of_channels == 12 + timecolumns:
            xdata, y1data, y2data, y3data, y4data, y5data, y6data, y7data, y8data, y9data, y10data, y11data, y12data = select(initialData,0), select(initialData,1), select(initialData,2), select(initialData,3), select(initialData,4), select(initialData,5), select(initialData,6), select(initialData,7), select(initialData,8), select(initialData,9), select(initialData,10), select(initialData,11), select(initialData,12)


    if number_of_channels == (4+timecolumns):
        
        fig, (ax1, ax2, ax3, ax4) = plt.subplots(nrows=4,ncols=1, sharex=True)

        # intialize four line objects (one in each axes)
        line1, = ax1.plot(xdata, y1data, lw=2, color=col[0])
        line2, = ax2.plot(xdata, y2data, lw=2, color=col[2])
        line3, = ax3.plot(xdata, y3data, lw=2, color=col[3])
        line4, = ax4.plot(xdata, y4data, lw=2, color=col[4])

    elif number_of_channels == (8+timecolumns):

        fig, (ax1, ax2, ax3, ax4, ax5, ax6, ax7, ax8) = plt.subplots(nrows=8,ncols=1, sharex=True)
        # intialize four line objects (one in each axes)
        line1, = ax1.plot(xdata, y1data, lw=2, color=col[0])
        line2, = ax2.plot(xdata, y2data, lw=2, color=col[2])
        line3, = ax3.plot(xdata, y3data, lw=2, color=col[3])
        line4, = ax4.plot(xdata, y4data, lw=2, color=col[4])
        line5, = ax5.plot(xdata, y5data, lw=2, color=col[5])
        line6, = ax6.plot(xdata, y6data, lw=2, color=col[6])
        line7, = ax7.plot(xdata, y7data, lw=2, color=col[7])
        line8, = ax8.plot(xdata, y8data, lw=2, color=col[8])

    elif number_of_channels == (12+timecolumns):

        fig, (ax1, ax2, ax3, ax4, ax5, ax6, ax7, ax8, ax9, ax10, ax11, ax12) = plt.subplots(nrows=12,ncols=1, sharex=True)
        # intialize four line objects (one in each axes)
        line1, = ax1.plot(xdata, y1data, lw=2, color=col[0])
        line2, = ax2.plot(xdata, y2data, lw=2, color=col[2])
        line3, = ax3.plot(xdata, y3data, lw=2, color=col[3])
        line4, = ax4.plot(xdata, y4data, lw=2, color=col[4])
        line5, = ax5.plot(xdata, y5data, lw=2, color=col[5])
        line6, = ax6.plot(xdata, y6data, lw=2, color=col[6])
        line7, = ax7.plot(xdata, y7data, lw=2, color=col[7])
        line8, = ax8.plot(xdata, y8data, lw=2, color=col[8])
        line9, = ax9.plot(xdata, y9data, lw=2, color=col[9])
        line10, = ax10.plot(xdata, y10data, lw=2, color=col[10])
        line11, = ax11.plot(xdata, y11data, lw=2, color=col[11])
        line12, = ax12.plot(xdata, y12data, lw=2, color=col[12])

    else:

        print('Cannot plot more than 12 channels!')



    line = [line1, line2, line3, line4]

    if number_of_channels >= 8 + timecolumns:
        line.append(line5)
        line.append(line6)
        line.append(line7)
        line.append(line8)

    if number_of_channels >= 12 + timecolumns:
        line.append(line9)
        line.append(line10)
        line.append(line11)
        line.append(line12)



    def updatePlot(i,xdata,y1data,y2data,y3data,y4data,y5data,y6data,y7data,y8data):
        """ Function used to update the plot in the animate function """

        if 'filesize_prev' in locals() and filesize_prev == os.path.getsize(filename):
            
            time.sleep(1) ### do not update plot if the filesize hasn't changed.

            return line
        
        else:

            timecolumns = 1

            chunk = readNewChunk(filename,chunkSize=chunk_size)
            new_data = decode_chunk(chunk,nth=2)

            # update the data
            if number_of_channels == (4+timecolumns):
                t, y1, y2, y3, y4 = select(new_data,0), select(new_data,1), select(new_data,2), select(new_data,3), select(new_data,4)
                xdata.append(t)
                y1data.append(y1)
                y2data.append(y2)
                y3data.append(y3)
                y4data.append(y4)

                # axis limits checking.
                #for ax in [ax1, ax2, ax3, ax4]:
                #    xmin, xmax = ax.get_xlim()
                #    if t >= xmax:
                #        ax.set_xlim(xmin, 2*xmax)
                #        ax.figure.canvas.draw()

                # update the data of both line objects
                line[0].set_data(xdata, y1data)
                line[1].set_data(xdata, y2data)
                line[2].set_data(xdata, y3data)
                line[3].set_data(xdata, y4data)

            elif number_of_channels==(8+timecolumns):
                t, y1, y2, y3, y4, y5, y6, y7, y8 = select(new_data,0), select(new_data,1), select(new_data,2), select(new_data,3), select(new_data,4), select(new_data,5), select(new_data,6), select(new_data,7), select(new_data,8)
                xdata = xdata + t
                y1data = y1data + y1
                y2data = y2data + y2
                y3data = y3data + y3
                y4data = y4data + y4
                y5data = y5data + y5
                y6data = y6data + y6
                y7data = y7data + y7
                y8data = y8data + y8

                # axis limits checking. Same as before, just for both axes
                #for ax in [ax1, ax2, ax3, ax4, ax5, ax6, ax7, ax8]:
                #    xmin, xmax = ax.get_xlim()
                #    if t >= xmax:
                #        ax.set_xlim(xmin, 2*xmax)
                #        ax.figure.canvas.draw()

                # update the data of both line objects
                line[0].set_data(xdata, y1data)
                line[1].set_data(xdata, y2data)
                line[2].set_data(xdata, y3data)
                line[3].set_data(xdata, y4data)
                line[4].set_data(xdata, y5data)
                line[5].set_data(xdata, y6data)
                line[6].set_data(xdata, y7data)
                line[7].set_data(xdata, y8data)


                    
            elif number_of_channels==(12+timecolumns):
                t, y1, y2, y3, y4, y5, y6, y7, y8, y9, y10, y11, y12 = select(new_data,1), select(new_data,2), select(new_data,3), select(new_data,4), select(new_data,5), select(new_data,6), select(new_data,7), select(new_data,8), select(new_data,9), select(new_data,10), select(new_data,11), select(new_data,12)
                xdata.np.append(t)
                y1data.append(y1)
                y2data.append(y2)
                y3data.append(y3)
                y4data.append(y4)
                y5data.append(y5)
                y6data.append(y6)
                y7data.append(y7)
                y8data.append(y8)
                y9data.append(y9)
                y10data.append(y10)
                y11data.append(y11)
                y12data.append(y12)

                # axis limits checking. Same as before, just for both axes
                #for ax in [ax1, ax2, ax3, ax4, ax5, ax6, ax7, ax8, ax9, ax10, ax11, ax12]:
               #     xmin, xmax = ax.get_xlim()
               #     if t >= xmax:
               #         ax.set_xlim(xmin, 2*xmax)
               #         ax.figure.canvas.draw()


                # update the data of both line objects
                line[0].set_data(xdata, y1data)
                line[1].set_data(xdata, y2data)
                line[2].set_data(xdata, y3data)
                line[3].set_data(xdata, y4data)
                line[4].set_data(xdata, y5data)
                line[5].set_data(xdata, y6data)
                line[6].set_data(xdata, y7data)
                line[7].set_data(xdata, y8data)
                line[8].set_data(xdata, y9data)
                line[9].set_data(xdata, y10data)
                line[10].set_data(xdata, y11data)
                line[11].set_data(xdata, y12data)

            filesize_prev = os.path.getsize(filename)
            
            fig.gca().relim()
            fig.gca().autoscale_view() 

            return line
            



    ani = animation.FuncAnimation(fig, updatePlot,fargs=(xdata,y1data,y2data,y3data,y4data,y5data,y6data,y7data,y8data,), blit=True)

    #ani = FuncAnimation(fig, updatePlot, fargs=(xdata,y1data,y2data,y3data,y4data,y5data,y6data,y7data,y8data,),
    #interval=2000, 
    #frames=1,
   # repeat=False, 
    #cache_frame_data=False,
    #save_count=0#,
    #blit=True) #AttributeError: 'FuncAnimation' object has no attribute '_resize_id' <- to fix first
    #)
    fig.show()
    plt.show()