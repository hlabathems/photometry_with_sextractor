from astropy import units as u
from astropy.coordinates import SkyCoord
import numpy as np
from astropy.io import fits, ascii
import argparse
import glob
import os

def extract_columns(filename):
    data = ascii.read(filename)

    return data

def get_index(ref_catalog, catalog):

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
    ra1 = int(np.trunc(ra / 15.))
    ra2 = int(np.trunc((ra - ra1 * 15.) * 4))
    ra3 = ((ra - ra1 * 15. - ra2 / 4.) * 240.)
    
    return str(ra1) + ':' + str(ra2) + ':' + str(round(ra3, 6))

def cross_match(args):
    c = SkyCoord('%s %s' % (args.ra, args.dec), unit = (u.hourangle, u.deg))
    
    user_alpha = c.ra.value
    user_delta = c.dec.value
    
    ref = extract_columns(args.fin)
    
    counter = 0
    
    for catalog in glob.iglob('%s/*cat*' % (args.dir)):
        try:
            data = extract_columns(catalog)

            without_ext = os.path.basename(catalog).split('.cat')[0]
            fits_file = '%s.fits' % (without_ext)
            idx = get_index(ref['NAME'], fits_file)

            hjd = ref['HJD'][idx]
            observatory = ref['SITEID'][idx]
            exptime = ref['EXPTIME'][idx]

            if observatory == 'cpt':
                observatory = 'SAAO'
            if observatory == 'elp':
                observatory = 'McD'
            if observatory == 'lsc':
                observatory = 'CTIO'
            if observatory == 'coj':
                observatory = 'SSO'

            diff_alpha = data['ALPHA_J2000'] - user_alpha
            diff_delta = data['DELTA_J2000'] - user_delta

            dist = np.sqrt(np.square(diff_alpha) + np.square(diff_delta))
            j = np.argmin(dist)

            if dist[j] <= 0.0004 and data['FLAGS'][j] == 0 and data['FLUX_APER'][j] > 0:
                
                m = -2.5 * np.log10(data['FLUX_APER'][j] / exptime)
                merr = 1.0857 * (data['FLUXERR_APER'][j] / data['FLUX_APER'][j])
                S_N = data['FLUX_APER'][j] / data['FLUXERR_APER'][j]  # signal-to-noise
                
                with open(args.fout, 'a+') as outfile:
                    outfile.write('%s.cat %s %s %s %s %s %s %s %s %s\n' % (without_ext, hjd[0], data['FLUX_APER'][j], data['FLUXERR_APER'][j], S_N, m[0], merr, data['ALPHA_J2000'][j], data['DELTA_J2000'][j], observatory))
            
                cat_ra, cat_dec = convertRA(data['ALPHA_J2000'][j]), convertDEC(data['DELTA_J2000'][j])
            
                print('Matched_RA: '+str(cat_ra), 'Matched_DEC: '+str(cat_dec))
        
                counter = counter + 1
            else:
                print('No match found in file %s' % (catalog))
                    
        except Exception as e:
            print('Could not read file %s' % (catalog))
            continue

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
