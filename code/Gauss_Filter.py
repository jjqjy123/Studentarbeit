from scipy.ndimage import gaussian_filter
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
import time
import sys
import os

np.set_printoptions(threshold=np.inf)                                          #: Matrix show entirely

def reshape_(M, N):
    
    # data reshape to mesh 
    return lambda a : a.reshape(M, N)                                          #: Parameter x,y,z reshape to M*N(mesh)

def len_(x):
    return int(len(np.unique(np.array(x.round(6)))))                           #: np.round + np.unique. must np.array???

def cut_off_rand(data, n=2):

    # n: cut-off size in mm                                                    #: because data in boundary is not accurate
    # n by default = 2
    # cut-off boundary
    condition = np.where((data[:, 0] > min(data[:, 0])+n) & 
                         (data[:, 0] < max(data[:, 0])-n) & 
                         (data[:, 1] > min(data[:, 1])+n) & 
                         (data[:, 1] < max(data[:, 1])-n))
    data = data[condition]                                                     #: mittel data
    return data

def shape_matrix(data):
    
    # reshape of matrix
    M, N = len_(data[:, 0]), len_(data[:, 1])                                  #: python can assign many values at the same time
    shape_MN = reshape_(N, M)                                                  #: N lines(y), M ranks(x)
    x = shape_MN(data[:, 0])                                                   #: Parameter define here
    y = shape_MN(data[:, 1])
    z = shape_MN(data[:, 2])
    return [x, y, z]
    
def filter_oberflaesche(koordinaten, verschiebung):
    
    # gauss-filter
    M, N = len_(koordinaten[:, 0]), len_(koordinaten[:, 1])
    u3 = verschiebung[:].reshape(N, M)
    gauss_u3 = gaussian_filter(u3, sigma=4)                                    #: more sigma, more smoothness
    u3_g = u3 - gauss_u3
    
    # cut-off rand
    data = np.c_[koordinaten[:, 0], koordinaten[:, 1], u3_g.reshape(-1, 1)]    #: no matter how many lines, 1 rank. Matrix created(x,y,u3_g)
    # cut-off size n = 5
    data = cut_off_rand(data, 5)
    [x, y, z] = shape_matrix(data)
    return [x, y, z, gauss_u3]

def Node_berechnen(data):
    print("Nodes =", len(data))

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

# read data
# data name
path = sys.path[0]                                                             #: absolute path
files = os.listdir(path)
for file in files:
    if file.endswith(".csv"):                                                  #: get the filename
        filename = file
        break 
print(filename)                                                          
data = np.genfromtxt(path + '/' + filename, delimiter=',')  
koordinaten  = np.c_[data[:, 1], data[:, 2]]                                   #: Save als array, calculate faster
verschiebung = data[:, 4]

Node_berechnen(verschiebung)                                                   #: calculate amount of nodes

# visualisation
fig = plt.figure(figsize=(10, 10))                                             #: Height and width of figure, figure define

# z label for subplot 1 - 3
z_label = ['u3 [mm]', 'u3 [mm]', 'gefiltere Markierung u3 [mm]']

# subplot title for subplot 1 - 3
sub_title = ['Oberfläche', 'Long Wave', 'gefiltere Oberfläche']

# 1. subplot data
[x_, y_, u3_] = shape_matrix(np.c_[koordinaten[:, 0], koordinaten[:, 1],       #: np_c: Data matrix created(x,y,u3)
                                   verschiebung[:]])

Rauheit_berechnen(u3_)                                                         #: calculate the surface roughness

# 2. & 3. subplot data
[x, y, u3, u3_gaussian] = filter_oberflaesche(koordinaten, verschiebung)

# data for subplot 1 - 3
x = [x_, x_, x]
y = [y_, y_, y]
z = [u3_[::-1, :], u3_gaussian[::-1, :], u3[::-1, :]]

for i in range(1, 4):
    
    sub = fig.add_subplot(2, 2, i, projection='3d')                            #: divided to 2*2, i is position, 3d shape
    sub.plot_surface(x[i-1], y[i-1], z[i-1], rstride=1, cstride=1,             #: rstride and cstride control smoothness
                     linewidth=0, antialiased=False, cmap=cm.jet)              #: cmap means type of rainbow, antialiased(true) is smoother but lower 
    sub.set_xlabel('x [mm]', fontsize=10)                           
    sub.set_ylabel('y [mm]', fontsize=10)
    sub.set_zlabel(z_label[i-1], fontsize=10)
    sub.set_title(sub_title[i-1], fontsize=10, fontweight='bold')              #: fontweight means thick or thin

# 4. subplot data
ax4 = fig.add_subplot(2, 2, 4)
plt.imshow(u3, cmap=cm.jet, aspect='auto')                                     #: imshow is heatmap, aspect means cellsize
ax4.axes.get_xaxis().set_ticks([])                                             #: hide ticks, in [] you can mark ticks want to show
ax4.axes.get_yaxis().set_ticks([])
plt.colorbar()                                                                 #: create colormap related to data 

plt.show()