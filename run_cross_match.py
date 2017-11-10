from astropy import units as u
from astropy.coordinates import SkyCoord
import numpy as np
from astropy.io import ascii
import argparse
import glob
import os

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

def get_index(ref_catalog, catalog):
    """
    Parameters
    ----------
    ref_catalog, catalog: ascii  
    
    Returns
    -------
    index: int
            matched index
    """

    return np.where(ref_catalog == catalog)[0]

def convertDEC(dec):
    '''
        https://github.com/SAGES-UCSC/Photometry/blob/master/phot_utils.py
    '''
    dec1 = int(np.trunc(dec))
    dec2 = int(np.trunc(np.abs(dec - dec1) * 60))
    dec3 = ((np.abs(dec - dec1) * 60.) - dec2) * 60.

    return str(dec1) + ':' + str(dec2) + ':' + str(round(dec3, 6))

def convertRA(ra):
    '''
        https://github.com/SAGES-UCSC/Photometry/blob/master/phot_utils.py
    '''
    ra1 = int(np.trunc(ra / 15.))
    ra2 = int(np.trunc((ra - ra1 * 15.) * 4))
    ra3 = ((ra - ra1 * 15. - ra2 / 4.) * 240.)
    
    return str(ra1) + ':' + str(ra2) + ':' + str(round(ra3, 6))

def cross_match(args):
    """
    Parameters:
    ----------
    args: array-like object
    
    Returns
    -------
    args.fout: ascii
    """
    # convert to match the format in the .cat files
    c = SkyCoord('%s %s' % (args.ra, args.dec), unit = (u.hourangle, u.deg))
    
    # store the values
    image_ra = c.ra.value
    image_dec = c.dec.value
    
    # use file as reference
    ref = extract_columns(args.fin)
    
    counter = 0
    
    # loop through all the .cat files
    
    for catalog in glob.iglob('%s/*cat*' % (args.dir)):
        try:
            data = extract_columns(catalog)

            # remove the extension .cat
            without_ext = os.path.basename(catalog).split('.cat')[0]
            
            # append .fits
            fits_file = '%s.fits' % (without_ext)
            
            # get index of matching file
            idx = get_index(ref['NAME'], fits_file)

            # use the index to retrieve hjd, observatory, exposure time
            hjd = ref['HJD'][idx]
            observatory = ref['SITEID'][idx]
            exptime = ref['EXPTIME'][idx]

            # change from site names to observatory names, taken from the lco website
            if observatory == 'cpt':
                observatory = 'SAAO'
            if observatory == 'elp':
                observatory = 'McD'
            if observatory == 'lsc':
                observatory = 'CTIO'
            if observatory == 'coj':
                observatory = 'SSO'

            # from .cat
            cat_ra = data['ALPHA_J2000']
            cat_dec = data['DELTA_J2000']
            
            diff_alpha = cat_ra - image_ra
            diff_delta = cat_dec - image_dec

            dist = np.sqrt(np.square(diff_alpha) + np.square(diff_delta))
            j = np.argmin(dist)

            # change to suit your needs
            tolerance = 4e-4
            
            # flag bad data and do not accept negative flux values
            if dist[j] <= tolerance and data['FLAGS'][j] == 0 and data['FLUX_APER'][j] > 0:
                
                # convert to instrumental magnitude
                m = -2.5 * np.log10(data['FLUX_APER'][j] / exptime)
                # associated instrumental error
                merr = 1.0857 * (data['FLUXERR_APER'][j] / data['FLUX_APER'][j])
                
                # save
                with open(args.fout, 'a+') as outfile:
                    outfile.write('%s.cat %s %s %s %s %s %s %s %s\n' % (without_ext, hjd[0], data['FLUX_APER'][j], data['FLUXERR_APER'][j], m[0], merr, data['ALPHA_J2000'][j], data['DELTA_J2000'][j], observatory))
            
                matched_ra, matched_dec = convertRA(cat_ra[j]), convertDEC(cat_dec[j])
            
                print('Matched_RA: '+str(matched_ra), 'Matched_DEC: '+str(matched_dec))
        
                counter = counter + 1
            else:
                print('No match found in file %s' % (catalog))
                    
        except Exception as e:
            print('Could not read file %s' % (catalog))
            continue
            
    # print number of times the match was found
    print('Number of matching targets found: '+str(counter))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = 'This program will create a light curve of an object')

    parser.add_argument('--dir', help = 'Directory where the catalogs to be read are stored', action = 'store', type = str)
    parser.add_argument('--ra', action = 'store', help = 'RA (hh:mm:ss) of an object', type = str)
    parser.add_argument('--dec', action = 'store', help = 'DEC (+/-dd:mm:ss) of an object', type = str)
    parser.add_argument('--fin', action = 'store', help = 'Filename with images sorted according to filter', type = str)
    parser.add_argument('--fout', action = 'store', help = 'Output file (ASCII) to store data', type = str)

    args = parser.parse_args()

    cross_match(args)
