# -*- coding: utf-8 -*-
'''

# orca-uv

'''

import sys                              #sys files processing
import os                               #os file processing
import re                               #regular expressions
import argparse                         #argument parser
import numpy as np                      #summation
import matplotlib.pyplot as plt         #plots
from scipy.signal import find_peaks     #peak detection

# global constants
found_uv_section=False                                                                   #check for uv data in out
specstring_start = 'ABSORPTION SPECTRUM VIA TRANSITION ELECTRIC DIPOLE MOMENTS'          #check orca.out from here
specstring_end = 'ABSORPTION SPECTRUM VIA TRANSITION VELOCITY DIPOLE MOMENTS'            #stop reading orca.out from here
w_wn = 1000                                                                              #w = line width for broadening - wave numbers, FWHM
w_nm = 20                                                                                #w = line width for broadening - nm, FWHM
export_delim = " "                                                                       #delimiter for data export

# plot config section - configure here
nm_plot = True                              #wavelength plot /nm if True, if False wave number plot /cm-1
show_single_gauss = False                   #show single gauss functions if True
show_single_gauss_area = False              #show single gauss functions - area plot if True
show_conv_spectrum = True                   #show the convoluted spectra if True (if False peak labels will not be shown)
show_sticks = True                          #show the stick spectra if True
label_peaks = True                          #show peak labels if True
minor_ticks = True                          #show minor ticks if True
show_grid = False                           #show grid if True
linear_locator = True                       #tick locations at the beginning and end of the spectrum x-axis, evenly spaced
spectrum_title = "Absorption spectrum"      #title
spectrum_title_weight = "bold"              #weight of the title font: 'normal' | 'bold' | 'heavy' | 'light' | 'ultrabold' | 'ultralight'
y_label = "intensity"                       #label of y-axis 
x_label_wn = r'energy /cm$^{-1}$'           #label of the x-axis - wave number
x_label_nm = r'$\lambda$ /nm'               #label of the x-axis - nm
figure_dpi = 300                            #DPI of the picture

#global lists
energylist=list()           #energy cm-1
intenslist=list()           #fosc
gauss_sum=list()            #list for the sum of single gaussian spectra = the convoluted spectrum for cm-1

def roundup(x):
    #round to next 10 or 100
    if nm_plot:
        return x if x % 10 == 0 else x + 10 - x % 10
    else:
        return x if x % 100 == 0 else x + 100 - x % 100

def rounddown(x):
    #round to next 10 or 100
    if nm_plot:
        return x if x % 10 == 0 else x - 10 - x % 10
    else:
        return x if x % 100 == 0 else x - 100 - x % 100

def gauss(a,m,x,w):
    # calculation of the Gaussian line shape
    # a = amplitude (max y, intensity)
    # x = position
    # m = maximum/meadian (stick position in x, wave number)
    # w = line width, FWHM
    return a*np.exp(-(np.log(2)*((m-x)/w)**2))

# parse arguments
parser = argparse.ArgumentParser(prog='orca_uv', description='Easily plot absorption spectra from orca.out')

#filename is required
parser.add_argument("filename", help="the ORCA output file")

#show the matplotlib window
parser.add_argument('-s','--show',
    default=0, action='store_true',
    help='show the plot window')

#do not save the png file of the spectrum
parser.add_argument('-n','--nosave',
    default=1, action='store_false',
    help='do not save the spectrum')

#plot the wave number spectrum
parser.add_argument('-pwn','--plotwn',
    default=1, action='store_false',
    help='plot the wave number spectrum')

#change line with (integer) for line broadening - nm
parser.add_argument('-wnm','--linewidth_nm',
    type=int,
    default=20 ,
    help='line width for broadening - wavelength in nm')

#change line with (integer) for line broadening - wn
parser.add_argument('-wwn','--linewidth_wn',
    type=int,
    default=1000 ,
    help='line width for broadening - wave number in cm**-1')

#individual x range - start
parser.add_argument('-x0','--startx',
    type=int,
    help='start spectrum at x nm or cm**-1')

#individual x range - end
parser.add_argument('-x1','--endx',
    type=int,
    help='end spectrum at x nm or cm**-1')

#export data for the line spectrum in a csv-like fashion
parser.add_argument('-e','--export',
    default=0, action='store_true',
    help='export data')

#pare arguments
args = parser.parse_args()

#change values according to arguments
show_spectrum = args.show
save_spectrum = args.nosave
export_spectrum = args.export
nm_plot = args.plotwn

#check if w for nm is between 1 and 500, else reset to 20
if 1<= args.linewidth_nm <= 500:
    w_nm = args.linewidth_nm
else:
    print("warning! line width exceeds range, reset to 20")
    w_nm = 20
    
#check if w for wn is between 100 and 20000, else reset to 1000
if 100<= args.linewidth_wn <= 20000:
    w_wn = args.linewidth_wn
else:
    print("warning! line width exceeds range, reset to 1000")
    w_wn = 1000

#check if startx and endx are equal - exit if true.
if args.startx is not None and args.endx is not None and args.startx == args.endx:
    print("Warning. x0 and x1 are equal. Exit.")
    sys.exit(1)

#check if startx < 0 - exit if true.
if args.startx:
    if args.startx < 0:
        print("Warning. x0 < 0. Exit.")
        sys.exit(1)

#check if endx < 0 - exit if true
if args.endx:
    if args.endx < 0:
        print("Warning. x1 < 0. Exit.")
        sys.exit(1)

    
#open a file
#check existence
try:
    with open(args.filename, "r") as input_file:
        for line in input_file:
            #start exctract text 
            if "Program Version 6" in line:
                #thanks to the orca prgrmrs all is different 
                energy_column=4
                intens_column=6
            elif "Program Version" in line:
                energy_column=1
                intens_column=3
            if specstring_start in line:
            #found UV data in orca.out
                found_uv_section=True
                for line in input_file:
                    #stop exctract text 
                    if specstring_end in line:
                        break
                    #only recognize lines that start with number
                    #split line into 2 lists energy, intensities
                    #line should start with a number
                    if re.search("\d\s{1,}\d",line): 
                        energylist.append(float(line.strip().split()[energy_column]))
                        intenslist.append(float(line.strip().split()[intens_column]))
                        
#file not found -> exit here
except IOError:
    print(f"'{args.filename}'" + " not found")
    sys.exit(1)

#no UV data in orca.out -> exit here
if found_uv_section == False:
    print(f"'{specstring_start}'" + "not found in" + f"'{args.filename}'")
    sys.exit(1)
    
if nm_plot:
    #convert wave number to nm for nm plot
    energylist=[1/wn*10**7 for wn in energylist]
    w = w_nm #use line width for nm axis
else:
    w = w_wn #use line width for wave number axis
    
#prepare plot
fig, ax = plt.subplots()

#plotrange must start at 0 for peak detection
plt_range_x=np.arange(0,max(energylist)+w*3,1)


#plot single gauss function for every frequency freq
#generate summation of single gauss functions
for index, wn in enumerate(energylist):
    #single gauss function line plot
    if show_single_gauss:
        ax.plot(plt_range_x,gauss(intenslist[index], plt_range_x, wn, w),color="grey",alpha=0.5) 
    #single gauss function filled plot
    if show_single_gauss_area:
        ax.fill_between(plt_range_x,gauss(intenslist[index], plt_range_x, wn, w),color="grey",alpha=0.5)
    # sum of gauss functions
    gauss_sum.append(gauss(intenslist[index], plt_range_x, wn, w))

#y values of the gauss summation /cm-1
plt_range_gauss_sum_y = np.sum(gauss_sum,axis=0)

#find peaks scipy function, change height for level of detection

peaks , _ = find_peaks(plt_range_gauss_sum_y,height=0)

#plot spectra
if show_conv_spectrum:
    ax.plot(plt_range_x,plt_range_gauss_sum_y,color="black",linewidth=0.8)

#plot sticks
if show_sticks:
    ax.stem(energylist,intenslist,linefmt="dimgrey",markerfmt=" ",basefmt=" ")

#optional mark peaks - uncomment in case
#ax.plot(peaks,plt_range_gauss_sum_y_wn[peaks],"x")

#label peaks
#show peak labels only if the convoluted spectrum is shown (first if)
if show_conv_spectrum:  
    if label_peaks: 
        for index, txt in enumerate(peaks):
            ax.annotate(peaks[index],xy=(peaks[index],plt_range_gauss_sum_y[peaks[index]]),ha="center",rotation=90,size=8,
                xytext=(0,5), textcoords='offset points')
            
#label x axis
if nm_plot:
    ax.set_xlabel(x_label_nm)
else:
    ax.set_xlabel(x_label_wn)
    
ax.set_ylabel(y_label)                                          #label y axis
ax.set_title(spectrum_title,fontweight=spectrum_title_weight)   #title
ax.get_yaxis().set_ticks([])                                    #remove ticks from y axis
plt.tight_layout()                                              #tight layout

#show minor ticks
if minor_ticks:
    ax.minorticks_on()

#if startx argument is given - x-axis range
if args.startx:
    xlim_autostart = args.startx
#if startx argument is not given or zero - x-axis range
else:
    if args.startx == 0:
        xlim_autostart = 0
    else:
        xlim_autostart = rounddown(min(energylist)-w*3) #startx from data

#if endx argument is given - x-axis range
if args.endx:
    xlim_autoend = args.endx
#if endx argument is not given or zero - x-axis range
else:
    if args.endx == 0:
        xlim_autoend = 0
    else:
        xlim_autoend = roundup(max(plt_range_x)) #auto endx from data

#x should not below zero - x-axis range
if xlim_autostart < 0:
    plt.xlim(0,xlim_autoend) 
else:
    plt.xlim(xlim_autostart,xlim_autoend) 

#y-axis range - no dynamic y range
#plt.ylim(0,max(plt_range_gauss_sum_y)+max(plt_range_gauss_sum_y)*0.1) # +10% for labels

#y-axis range - dynamic y range
xmin=int(ax.get_xlim()[0]) #get recent xlim min
xmax=int(ax.get_xlim()[1]) #get recent xlim max
if xmin > xmax:
    ymax=max(plt_range_gauss_sum_y[xmax:xmin])  #get y max from recent x range for inverted x axis
    ax.set_ylim(0,ymax+ymax*0.1)                # +10% for labels
elif xmax > xmin:
    ymax=max(plt_range_gauss_sum_y[xmin:xmax])  #get y max from recent x range for normal x axis
    ax.set_ylim(0,ymax+ymax*0.1)                # +10% for labels


#tick locations at the beginning and end of the spectrum x-axis, evenly spaced
if linear_locator:
    ax.xaxis.set_major_locator(plt.LinearLocator())
    
#show grid
if show_grid:
    ax.grid(True,which='major', axis='x',color='black',linestyle='dotted', linewidth=0.5)

#increase figure size N times
N = 1.5
params = plt.gcf()
plSize = params.get_size_inches()
params.set_size_inches((plSize[0]*N, plSize[1]*N))

#save the plot
if save_spectrum:
    filename, file_extension = os.path.splitext(args.filename)
    plt.savefig(f"{filename}-abs.png", dpi=figure_dpi)
    
#export data
if export_spectrum:
    #get data from plot (window)
    plotdata = ax.lines[0]
    xdata = plotdata.get_xdata()
    ydata = plotdata.get_ydata()
    xlimits = plt.gca().get_xlim()
    try:
        with open(args.filename + "-mod.dat","w") as output_file:
            for elements in range(len(xdata)):
                if xdata[elements] >= xlimits[0] and xdata[elements] <= xlimits[1]:
                    output_file.write(str(xdata[elements]) + export_delim + str(ydata[elements]) +'\n')
    #file not found -> exit here
    except IOError:
        print("Write error. Exit.")
        sys.exit(1)

#show the plot
if show_spectrum:
    plt.show()
