from astropy.io import fits
from pyraf import iraf
import sys

infiles = sys.argv[1:]

for img in infiles:
    
    data, hdr = fits.getdata(img, header = True)
    
    _observatory = hdr['SITEID']
    
    if _observatory == 'cpt':
        _observatory = 'saao'
    elif _observatory == 'elp':
        _observatory = 'het'
    elif _observatory == 'lsc':
        _observatory = 'ctio'
    elif _observatory = 'ogg':
        _observatory = 'cfht'
    elif _observatory == 'coj':
        _observatory = 'sso'

    if 'HJD' not in hdr.keys():
        iraf.noao.astutil.setjd(img, date = 'DATE-OBS', time = 'UTSTART', exposure = 'EXPTIME', ra = 'ra', dec = 'dec', epoch = '', observa = _observatory)

