import matplotlib
matplotlib.use("TkAgg")
from pylab import *
import pandas as pd
from matplotlib.ticker import (MultipleLocator, FormatStrFormatter,
                               AutoMinorLocator)
from matplotlib.ticker import MaxNLocator

matplotlib.rcParams['font.sans-serif'] = "Helvetica World" # this sets the font to be Helvetica. you may need to change to just 'Helvetica'.
mpl.rcParams['xtick.major.pad'] = 8 # gives the origin values breathing room so they don't overlap.
mpl.rcParams['ytick.major.pad'] = 8 # gives the origin values breathing room so they don't overlap.
def graph(file): # function that plots a file.

    size = 16   # set font sizes
    data = pd.read_csv(file, sep='\t', header=None)     # read the datafile that is passed into the function; delimiter is tab, no headers

    print(data) # it's good to print stuff to the console to make sure it's importing correctly. makes it easier to debug.
    xrange = x_range(data)  #this runs the function below to get the max and min x values to help get the range of your graph looking good.
    yrange = y_range(data)  #same as above but for y-axis. I have a multiplier for the max Y value so there's some breathing room at the top.

    fig, ax = plt.subplots() #  create a figure w/ an axis class to manipulate all parts of hte plot
    plt.plot(data[0], data[1],linewidth=2,linestyle='solid',color='#440154FF')  # plot the x data (data[0] is the x column, data[1] is the y column). is a line charge with width=2, and color is purple.

    plt.xticks(size=size)   #set x-ticks to be = size variable above. I use 1 variable so I dont have to change every font size by hand; just do it once up above.
    plt.yticks(size=size)   # same as previous line
    ax.set_ylabel('Absorbance (arb. units)', size=size) # set axis label
    ax.set_xlabel('Wavelength (nm)', size=size) # same as above

    ax.xaxis.set_minor_locator(MultipleLocator(50)) # this sets the location of minor ticks (x-axis)
    ax.yaxis.set_minor_locator(MultipleLocator(.1)) # this sets the location of minor ticks (y-axis)

    plt.xlim([xrange[0], xrange[1]]) #  specify the range of the x axis; don't want excess whitespace. first value = min value for x, second = max x
    plt.ylim([yrange[0], yrange[1]])    # same for y axis. first = min for y, second = max for y
    ax.tick_params(direction='in', length=8)    # format major ticks
    ax.tick_params(which='minor',direction='in', length=4) # same for minor ticks

    ax.yaxis.set_ticks_position('both') # get ticks on all sides
    ax.xaxis.set_ticks_position('both') # same as above

    plt.tight_layout()  #this clips whitespace on side of graph so it's nicely sized for publication
    plt.savefig("jason_file.png", dpi=600)  # save the file to the working directory at 600 DPI
    plt.show()  #also show the graph to plot

def x_range(data): #simple function that stores the max/min x axis values into an array. that array is called in lines 31 above to specify range of axis
    x_range = [data[0].min(), data[0].max()]    # array that gets the min value from column 0 (first column; header=0); and max from same column
    return x_range  # return the array. this array is what is called in line 31

def y_range(data):
    y_min = data[1].min()   # another example of getting the y-min value
    y_max = data[1].max()   # same as above but for max
    y_range = [0, round(y_max*1.15,1)]  #store the min and max into an array (I set the min to 0 by hand here); the max is multiplied by 1.15 and rounded to nearest 0.1 to add white space to top of graph so y-max doesn't touch top line
    return y_range # returns the array you make. is what's used up in line 32


graph('TPP_UV.txt') # this is what actaully runs! you call function graph and pass the file TPP_UV.txt. so that is the datafile you use to plot.
