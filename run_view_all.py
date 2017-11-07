import sys, os
import matplotlib.pyplot as plt
from astropy.io import ascii

def extract_columns(filename):
    data = ascii.read(filename)
    
    return data

for filename in sys.argv[1:]:
    data = extract_columns(filename)
    
    hjd = data['col2']
    flux = data['col3']
    
    fname = os.path.basename(filename)
    
    print(len(hjd), fname)

    plt.plot(hjd - 2450000, flux, '.', label = '%s' % (fname))

plt.legend(loc = 'best')
plt.grid()
plt.show()
