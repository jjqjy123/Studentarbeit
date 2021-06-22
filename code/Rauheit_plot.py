from scipy.ndimage import gaussian_filter
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
import sys
import os

def len_(x):
    return len(np.unique(x))                           

def cut_off_rand(data, n=5):

    # n: cut-off size in mm                                                    #: because data in boundary is not accurate
    # n by default = 5
    # cut-off boundary
    condition = np.where((data[:, 0] > min(data[:, 0])+n) & 
                         (data[:, 0] < max(data[:, 0])-n) & 
                         (data[:, 1] > min(data[:, 1])+n) & 
                         (data[:, 1] < max(data[:, 1])-n))
    data = data[condition]                                                     #: mittel data
    return data

def Meshgrid(data):
    M, N = len_(data[:, 0]), len_(data[:, 1])                                  #: python can assign many values at the same time   
    x = data[:, 0].reshape(N, M)  
    y = data[:, 1].reshape(N, M)         
    z = data[:, 2].reshape(N, M)
    return x, y, z

def filter_oberflaesche(koordinaten, verschiebung):
    
    # gauss-filter
    M, N = len_(koordinaten[:, 0]), len_(koordinaten[:, 1])                    #: length and width of decke
    u3 = verschiebung[:].reshape(N, M)
    gauss_u3 = gaussian_filter(u3, sigma=8)                                   #: more sigma, more smoothness
    u3_g = u3 - gauss_u3
    
    # cut-off rand
    data1 = np.c_[koordinaten[:, 0], koordinaten[:, 1], u3_g.reshape(-1, 1)]    #: no matter how many lines, 1 rank. Matrix created(x,y,u3_g)
    data2 = np.c_[koordinaten[:, 0], koordinaten[:, 1], u3.reshape(-1, 1)]
    data3 = np.c_[koordinaten[:, 0], koordinaten[:, 1], gauss_u3.reshape(-1, 1)]
    # cut-off size n = 5
    data1 = cut_off_rand(data1,10)
    data2 = cut_off_rand(data2,10)
    data3 = cut_off_rand(data3,10)
    x1,y1,z1 = Meshgrid(data1)
    x2,y2,z2 = Meshgrid(data2)
    x3,y3,z3 = Meshgrid(data3)  
    
    return x1, y1, z1, x2, y2, z2, x3, y3, z3

def Plot(x, y,z): 
#    maxs = 0 
#    id = 0
#    for i in range(len(x)):
#       x_data = x[i]
#        y_data = y[i]
#        delta = max(y_data) - min(y_data)
#        if delta >maxs:
#            maxs = delta
#            id = i
#    x_data = x[id]
#    y_data = y[id]
#    print(id)

# Plot along y axis   
#   id = len(y)//2
#    x_data = x[:,id]
#   y_data = y[:,id]
#    z_data = z[:,id]
#    plt.plot(y_data, z_data)

# Plot along x axis
    id = len(x)//2
    x_data = x[id]
    y_data = y[id]
    z_data = z[id]
    plt.plot(x_data, z_data)

    print(max(z_data) - min(z_data))

def Calculate(filename):

    data = np.genfromtxt(path + '/' + filename, delimiter=',', skip_header=1)  
    koordinaten  = np.c_[data[:, 1], data[:, 2]]                                   #: Save als array, calculate faster
    verschiebung = data[:, 4]
    x1, y1, z1, x2, y2, z2, x3, y3, z3 = filter_oberflaesche(koordinaten, verschiebung)
  #  Plot(x1, y1, z1)                           # shortwave
    Plot(x2, y2, z2)                            # u3
    Plot(x3, y3, z3)                            # longwave


# read data
# data name
path = sys.path[0]                                                             #: absolute path
files = os.listdir(path)

plt.subplots(figsize=(9,7))
plt.xlabel("x [mm]", fontsize=10)                                                 #: set x and y label
plt.ylabel("U3 [mm]", fontsize=10)
plt.title("Plot", fontsize=10, fontweight='bold') 

for file in files:
    if file.endswith(".csv"):                                                  #: get the filename
        filename = file
        print(filename)
        Calculate(filename)
        plt.show()

