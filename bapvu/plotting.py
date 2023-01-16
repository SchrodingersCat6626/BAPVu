#!/usr/bin/python3


def data_decode():
    #decoding the data
    with open('data_test.dat', 'rb') as data_decoded:
        data1=data_decoded.readlines()
        for line in data1:
            line.decode('ascii')
    return data_decoded


from itertools import count
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib import animation
import numpy as np


plt.style.use('ggplot')


def animate():

    # i think my issue is i need to append each line to an empty list in my animate function... see :https://www.geeksforgeeks.org/matplotlib-animate-multiple-lines/
    data = pd.read_csv('/home/thomas/BAPVu/test.txt', delim_whitespace=True)
    x = data['time']
    list_of_columns = [column for column in data]

    fig, axs = plt.subplots(nrows=(len(list_of_columns)-1),ncols=1, sharex=True)


#this function should be used to CREATE the subplots and the data should be appended to each subplot inside animate function?
    for idx, ax in enumerate(axs, start=1):   # start=1 makes index 1, since we ignore the first item of list of columns 

        ax.plot(x, data[list_of_columns[idx]], label=list_of_columns[idx])


#ani = FuncAnimation(plt.gcf(), animate, interval=1000)
plt.show()




