# This program plots wavelets and approximations of different detail levels.
#
# A lot of help came from:
# - post on stackexchange
#       https://dsp.stackexchange.com/questions/44285/discrete-wavelet-transform-how-to-interpret-approximation-and-detail-coefficien
# - good introduction to the procedure of wavelet transform
#       https://www.math.aau.dk/digitalAssets/120/120646_r-2003-24.pdf
# - good overview to understand wavelets
#       Wavelets: A Student Guide by Peter Nickolas
# - pywavelets rough documentation is found here
#       https://pywavelets.readthedocs.io/en/latest/index.html
# - also helpful for understanding
#       https://dsp.stackexchange.com/questions/47437/discrete-wavelet-transform-visualizing-relation-between-decomposed-detail-coef

import numpy as np

import matplotlib
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter

import pywt

import scipy.stats as stats

from statsmodels.robust import mad

from spectrum_analysis import spectrum as sp

from matplotlib import rcParams
rcParams['font.family'] = 'serif'
rcParams['text.usetex'] = True
rcParams['font.size'] = 14

# choose your wavelet
wavelet_name = 'haar' # or sym8
                      # how do sym wavelets work?
# select your function
gaussian = True
linear = True
sinus = False
noise = False
spike = True

# True if need to show plot
show = True

# should be 2^n (n = natural number)
number_of_points = 128

# generate testdata
x = np.linspace(-1.,1.,number_of_points)
y = np.zeros_like(x)

if gaussian:
    y += 1 * stats.norm.pdf(x, 0, 0.05)
if linear:
    y += 2*x / np.max(x)
if sinus:
    y += np.sin(100 * np.pi * x)
if noise:
    y += np.random.randint(1, 5, size=number_of_points)

y_spikefree = np.copy(y)
if spike:
    size = 1
    y[20] += 7*size
    y[21] += 15*size
    y[22] += 9*size

# the coefficients array has the for of
# coeff = [cA(n-1) cD(n-1) cD(n-2) ... cD(2) cD(1)]
# here cA are the approximation coefficients and
# cD the detail coefficients
coeff = pywt.wavedec(y, wavelet_name)

length = len(coeff)

# create figures for all wavelets and detail levels
fig, ax = plt.subplots(figsize=(8,6), nrows=length-1, ncols=3)
# create big figure for raw data
gs = ax[0,0].get_gridspec()
# remove the underlying axes
for axis in ax[0:, 0]:
    axis.remove()
axbig = fig.add_subplot(gs[0:, 0])
# plot raw data
axbig.plot(x, y, label='raw')
axbig.set_ylabel('Intensity (arb. u.)')
axbig.set_xlabel('')

# plot all levels and create the reconstruction for each level
y_arr = []
for current_level in range(1, length):
    # set all but the current level to zero
    single_coeff = coeff.copy()
    for i in range(0, length):
        if i is not current_level:
            single_coeff[i] = np.zeros_like(single_coeff[i])
        else:
            pass
    # reconstruct the current coefficient's level
    y_single = pywt.waverec(single_coeff, wavelet_name)
    # create the sum of the reconstructed wavelets up to the selected level
    y_arr.append(y_single)
    # plot the reconstructed coefficients
    ax[current_level-1][1].plot(x, y_single)
    ax[current_level-1][1].tick_params(axis='x', labelbottom=False, bottom=False)
    ax[current_level-1][1].yaxis.set_major_formatter(FormatStrFormatter('%.1f'))
    ax[current_level-1][1].text(0.075, 0.75, f'$D_{{{current_level-1}}}$',
                                horizontalalignment='center',
                                verticalalignment='center',
                                transform = ax[current_level-1][1].transAxes)

# plot the sum for each level of reconstruction
for current_level in range(1, length):
    y_sum = np.zeros_like(y_arr[0])
    for i in range(0, current_level):
        y_sum += y_arr[i]
    ax[current_level-1][2].plot(x, y_sum)
    ax[current_level-1][2].tick_params(axis='x', labelbottom=False, bottom=False)
    #ax[current_level-1][2].set_ylabel(f'$\sum\limits_{{j=0}}^{{{current_level-1}}} D_j$',
    #                                  rotation=90)
    #ax[current_level-1][2].yaxis.set_label_position('right')
    ax[current_level-1][2].yaxis.set_major_formatter(FormatStrFormatter('%.1f'))
    ax[current_level-1][2].text(0.075, 0.75, f'$A_{{{current_level-1}}}$',
                                horizontalalignment='center',
                                verticalalignment='center',
                                transform = ax[current_level-1][2].transAxes)

axbig.set_title('Model Data')
ax[0][1].set_title('Details ($D_j$)')
ax[0][2].set_title('Approximations ($A_N$)')
ax[-1][1].tick_params(axis='x', labelbottom=True, bottom=True)
ax[-1][2].tick_params(axis='x', labelbottom=True, bottom=True)

plt.tight_layout(h_pad=-0.25, w_pad=0.5)
fig.savefig('wavelet.svg', format='svg')
if show:
    plt.show()
plt.close()

# new plot
#fig, ax = plt.subplots(figsize=(8,3), nrows=1, ncols=3)
#ax[0].plot(x, y)
#ax[1].plot(x, y_arr[-1])
#ax[2].plot(x, y_spikefree)
#plt.show()
