#!/usr/bin/python3
"""

Note: the first column should be time and should probably be posix time. but it must be named time for this to work!


"""
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib import animation
import numpy as np

def plot(file):
    """
    Very messy function which plots data from a file (given as an argument) in realtime using the FuncAnimation from matplotlib. 
    Todo: 

    - dealing with units!?
    - there seems to currently be a bug where the y axis of  all the subplots except for the bottom one do not rescale y axis when the data points increase significantly...
    - this function really needs to be cleaned up properly...

        """

    # colour blind accessible default colours for plot.
    col = ["#000000", "#E69F00", "#56B4E9", "#009E73","#F0E442", "#0072B2", "#D55E00", "#CC79A7" , "#0e2f8a", "#210f87",'#531078','#801455', '#8f1622']

    #intially reading from file to use in initializing the plot (ie. how many columns there are)
    data = pd.read_csv(file)
    data = data.loc[:,~data.columns.str.startswith('unit')] # removing the unit columns

    #list of columns for various stuff below...
    list_of_columns = [column for column in data]

    # I can't recall if this does anything...
    from itertools import count
    #creates empty lists. automatically creates x and y list. then it will create list based on the number of columns (-2 since x and y are already created).



    #generates a list of empty lists for each column of the dataset. Basically each axis needs an empty list to add data to in the animation. Thus, I made a list of lists where each list is a column.
    list_of_list_of_columns = [[] for column in list_of_columns]
    myvar = count(0,(len(list_of_columns)-2))

    # sets the plotting style as ggplot (which is what I wish I could be using to plot in this program :) )
    plt.style.use('ggplot')

    # initializes subplots based on the number of columns - 1 (since the first column in time (x-value))
    fig, axs = plt.subplots(nrows=(len(list_of_columns)-1),ncols=1, sharex=True)

    #animate function. If I actually understood this well this wouldn't have taken me like 4hrs to figure out how to get the animation to work..
    def animate(i):
        #loads data from file
        data = pd.read_csv(file)
        data = data.loc[:,~data.columns.str.startswith('unit')] # removing the unit columns
        #time column (x-values)
        x = data['systime']
        #clears axis
        plt.cla()
        #gets all the y data. i is the current frame... I think.... 
        [[data[column][i] for column in list_of_columns] for empty_lists in list_of_list_of_columns]
        #plotting axis... I think...
        for idx, ax in enumerate(axs, start=1):   # start=1 makes index 1, since we ignore the first item of list of columns
            ax.plot(x, data[list_of_columns[idx]], label=list_of_columns[idx], color=col[idx])


    ani = FuncAnimation(plt.gcf(), animate, interval=2000)
    plt.show()

