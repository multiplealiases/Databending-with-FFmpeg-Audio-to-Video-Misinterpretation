#### BEGINNING OF LICENSE TEXT ####

## Copyright 2021 multiplealiases

## Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

## The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

## THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

#### END OF LICENSE TEXT ####

## DESCRIPTION:
## This is a mildly modified version of a script used to plot the u-law transfer function and print its output to standard output (which can be redirected to a file).
## The chief modifications were swapping out mpmath for math and numpy for performance, as well as adding descriptive comments. 
## This does not change the generated chart in any notable way. I highly doubt it does for the values too, at least at 2 decimal places.
## The original script was created on the 2nd of May 2021 at 8:21 pm, and last modified on the 6th at 8:09 pm.

import matplotlib.pyplot as plt
import numpy as np
import math

## Define variables. "precision" is in 1/x form; it can only be an integer. Poor planning on my part, but I just needed to get the values.
mu = 255
precision = 500000
range_plot = 1
true_precision = range_plot * precision
e = np.exp(1)
end_rounding = 2

## Calculate the dB x-parameter for plotting.
x_values = []
for x in range(0,true_precision):
    x_var = range_plot*x/true_precision + 0.0001
    x_values.append(20*math.log10(np.abs(x_var)))

## Calculate the dB u-law y-parameter for plotting later.
y_values = []
for y in range(0,true_precision):
    y_var = range_plot*y/true_precision + 0.0001
    y_values.append(20*math.log10(
                    np.abs((np.sign(y_var)*
                    math.log(1+mu*np.abs(y_var),e)
                    /math.log(1+mu,e)))))

## Plot the transfer function and its inverse; inverse used as visual aid.
#plt.style.use('dark_background')
plt.plot(x_values, y_values)
plt.plot(y_values, x_values)

## Plot the uncompanded line y = x, cut off at -48 dBFS.
plt.plot([0,-48],[0,-48])

## Plot the 8-bit PCM dynamic range line.
plt.plot([-100,100],[-48,-48],"--")

## Define the legend.
plt.legend(["μ-law compressor","μ-law expander","No compander","8-bit LPCM dynamic range"],loc='upper left',fontsize="x-small")

## Gets current axes so that the aspect ratio is 1:1. This is done for aesthetic purposes.
ax = plt.gca()
ax.set_aspect(1)

plt.xlim(-80,0)
plt.ylim(-80,0)
plt.grid(1)

## Name the x- and y-axes. 
plt.xlabel('Input amplitude (dBFS)')
plt.ylabel("Output amplitude (dBFS)")
  
## Title the graph so that it's obvious what it's supposed to mean.
plt.title("Continuous μ-law transfer function")
  
## Save the plot to an SVG file for later editing.
plt.savefig("u-law_plot-rev2-0-mu-255.svg")

## Print out the points of the transfer function so that it can be used for later.
combinedx = [round(float(i),end_rounding) for i in x_values]
combinedy = [round(float(i),end_rounding) for i in y_values]
print("(")
for i in range(0,len(combinedx)):
    if i != len(combinedx) - 1:
        print(f"({combinedx[i]},{combinedy[i]}),")
    else:
        print(f"({combinedx[i]},{combinedy[i]})")
print(")")
