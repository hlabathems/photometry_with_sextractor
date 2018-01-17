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

def cross_match(args):
    """
    Parameters:
    -----------
    args: array-like object
    
    Returns:
    --------
    args.fout: ascii
    """
    # convert to match the format in the .cat file
    c = SkyCoord('%s %s' % (args.ra, args.dec), unit = (u.hourangle, u.deg))

    # use file as reference
    ref = extract_columns(args.fin)
    
    # headers to write to a new file
    fo = open(args.fout, 'w')
    fo.write('CAT NUMBER HJD FLUX FLUXERR M MERR S/N ALPHA_J2000 DELTA_J2000 OBS FLAG\n')
    fo.close()
    
    counter = 0

    # loop through all the .cat files dated 2016
    
    for cat in glob.iglob('%s/*2016*cat*' % (args.dir)):
        try:
            data = extract_columns(cat)

            # remove the .cat extension
            without_ext = os.path.basename(cat).split('.cat')[0]
            
            # append .fits
            fits_file = '%s.fits' % (without_ext)
            
            # get index of matched file
            pos = get_index(ref['NAME'], fits_file)
            
            # use the index to retrieve hjd, observatory, exposure time
            observatory = ref['SITEID'][pos]
            hjd = ref['HJD'][pos]
            
            # change from site names to observatory names, taken from lco website
            if observatory == 'cpt':
                observatory = 'SAAO'
            if observatory == 'elp':
                observatory = 'McD'
            if observatory == 'lsc':
                observatory = 'CTIO'
            if observatory == 'coj':
                observatory = 'SSO'

            # this will give the closest coordinates to the ones inputed by the user
            against = SkyCoord(data['ALPHA_J2000'], data['DELTA_J2000'], unit = (u.degree, u.degree))
            idx, d2d, d3d = c.match_to_catalog_sky(against)

            matches = against[idx]
            
            # distance from the inputs
            dra = matches.ra - c.ra
            ddec = matches.dec - c.dec
            
            d = np.sqrt(np.square(dra) + np.square(ddec))
            
            # degree of accuracy
            tolerance = 4e-4

            # check against tolerance
            if d.value <= tolerance:

                # magnitude
                m = data['MAG_APER'][idx]
                
                # associated error
                merr = data['MAGERR_APER'][idx]
                
                signal_to_noise = data['FLUX_APER'][idx] / data['FLUXERR_APER'][idx]

                # save
                with open(args.fout, 'a+') as outfile:
                    outfile.write('%s.cat %s %s %s %s %s %s %s %s %s %s %s\n' % (without_ext, data['NUMBER'][idx], hjd[0], data['FLUX_APER'][idx], data['FLUXERR_APER'][idx], m, merr, signal_to_noise, data['ALPHA_J2000'][idx], data['DELTA_J2000'][idx], observatory, data['FLAGS'][idx]))
                        
                counter += 1
                    
        except Exception as e:
            print(e)
            pass

    print('Total number of matched target(s): ', counter)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = 'This program will create a light curve of an object')
    
    parser.add_argument('--dir', help = 'Directory where the catalogs to be read are stored', action = 'store', type = str)
    parser.add_argument('--ra', action = 'store', help = 'RA (hh:mm:ss) of an object', type = str)
    parser.add_argument('--dec', action = 'store', help = 'DEC (+/-dd:mm:ss) of an object', type = str)
    parser.add_argument('--fin', action = 'store', help = 'Filename with images sorted according to filter', type = str)
    parser.add_argument('--fout', action = 'store', help = 'Output file (ASCII) to store data', type = str)
    
    args = parser.parse_args()
    
    cross_match(args)
