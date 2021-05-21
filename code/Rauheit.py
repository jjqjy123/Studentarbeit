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

def Rauheit_berechnen(data):
    # Ra = 1/(m*n)*sum(|Z(xm, ym)-<Z>|)
    # <Z> = 1/(m*n)*sum(Z(xm, yn))
    ra = np.mean(abs(data-np.mean(data))) 
    print("ra =", ra)
    # Rp = mean(max(column(Zm,n)))
    rp = np.mean(data.max(axis=0))
    print("rp =", rp)
    # Rv = mean(min(column(Zm,n)))
    rv = abs(np.mean(data.min(axis=0)))
    print("rv =", rv)
    # Rz = mean(|max(column(Zm,n)|+|min(column(Zm,n))|)
    rz = abs(np.mean(data.max(axis=0)-data.min(axis=0)))
    print("rz =", rz)
    print('\n')

def Nodes_show(filename):
    with open(path + '/' +filename) as f1:
        print("Nodes =", f1.readline())

def filter_oberflaesche(koordinaten, verschiebung):
    
    # gauss-filter
    M, N = len_(koordinaten[:, 0]), len_(koordinaten[:, 1])                    #: length and width of decke
    u3 = verschiebung[:].reshape(N, M)
    gauss_u3 = gaussian_filter(u3, sigma=4)                                    #: more sigma, more smoothness
    u3_g = u3 - gauss_u3
    
    # cut-off rand
    data = np.c_[koordinaten[:, 0], koordinaten[:, 1], u3_g.reshape(-1, 1)]    #: no matter how many lines, 1 rank. Matrix created(x,y,u3_g)
    # cut-off size n = 5
    data = cut_off_rand(data, 5)
    M, N = len_(data[:, 0]), len_(data[:, 1])                                  #: python can assign many values at the same time             
    z = data[:, 2].reshape(N, M)
    return z

def Calculate(filename):
    Nodes_show(filename)                                                           #: show amount of nodes

    data = np.genfromtxt(path + '/' + filename, delimiter=',', skip_header=1)  
    koordinaten  = np.c_[data[:, 1], data[:, 2]]                                   #: Save als array, calculate faster
    verschiebung = data[:, 4]

    u3_Rauheit = filter_oberflaesche(koordinaten, verschiebung)

    Rauheit_berechnen(u3_Rauheit)


# read data
# data name
path = sys.path[0]                                                             #: absolute path
files = os.listdir(path)
for file in files:
    if file.endswith(".csv"):                                                  #: get the filename
        filename = file
        print(filename)
        Calculate(filename)

