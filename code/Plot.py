import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import ConnectionPatch
import sys
import os

def set_zoom(ax, axin):
    xlim0 = 25
    xlim1 = 27.5
    ylim0 = -0.05
    ylim1 = -0.035
    axin.set_xlim([xlim0, xlim1])                                                 #: x range of zoom
    axin.set_ylim([ylim0, ylim1])                                                 #: y range of zoom

    sx = [xlim0, xlim1, xlim1, xlim0, xlim0]                                      
    sy = [ylim0, ylim0, ylim1, ylim1, ylim0]
    ax.plot(sx, sy, "red")                                                        #: mark zoom range in global figure

fig, ax = plt.subplots(figsize=(9,7))
axin = ax.inset_axes([0.3, 0.1, 0.4, 0.3])                                        #: add local figure
plt.xlabel("x [mm]", fontsize=10)                                                 #: set x and y label
plt.ylabel("U3 [mm]", fontsize=10)
plt.title("Plot", fontsize=10, fontweight='bold')      
# read data
# data name
path = sys.path[0]                                                                #: absolute path
files = os.listdir(path)                                                                       
for file in files:
    if file.endswith(".csv"):                                                     #: get all csv files data
        filename = file
        data = np.genfromtxt(path + '/' + filename, delimiter=',', skip_header=1) 
        name = filename.rsplit('.', 1)[0]
        plt.plot(data[:, 1], data[:, 4], label=name)                              #: create curve in global figure
        axin.plot(data[:, 1],data[:, 4], linewidth=2)                                          #: create curve in local figure

set_zoom(ax, axin)                                                                #: set zoom range
    
plt.grid(linewidth=0.4)
plt.legend(loc='upper right')
plt.show()