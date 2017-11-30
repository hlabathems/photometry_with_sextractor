"""
This will plot all the comparison stars on one plot for inspection
"""
import sys, os
import matplotlib.pyplot as plt
from astropy.io import ascii

def extract_columns(filename):
    """
    Parameters
    ----------
    filename: ascii
    
    Returns
    -------
    data: array-like object
    """
    data = ascii.read(filename)
    
    return data

# loop through files
for filename in sys.argv[1:]:
    data = extract_columns(filename)
    
    hjd = data['HJD']
    flux = data['FLUX']
    
    fname = os.path.basename(filename)
    
    # see how many data points each have
    print(len(hjd), fname)

    plt.plot(hjd - 2450000, flux, '.', label = '%s' % (fname))

plt.legend(loc = 'best')
plt.grid()
plt.show()
