from astropy.io import fits, ascii
import numpy as np
import subprocess
import argparse
import os
import sys

def extract_columns(filename):
    """
    Parameters
    ----------
    filename: ascii
    
    Returns
    -------
    name, gain, saturate: array-like
    """
    data = ascii.read(filename)

    # only images taken in V filter
    mask = (data['FILTER'] == 'V')

    return data['NAME'][mask], data['GAIN'][mask], data['L1FWHM'][mask], data['SECPIX'][mask], data['PIXSCALE'][mask], data['SATURATE'][mask]

def source_extractor(args):
    """
    Parameters
    ----------
    args: array-like object
            corresponds to arguments passed by the user
            
    Returns
    -------
    catalog, checkimages: ascii, fits
            sextractor will create these and will be stored in args.dir1
    """
    fits_files, gain, seeing_fwhm, secpix, pixel_scale, saturate = extract_columns(args.filename)
    
    # remove the .fits extension
    without_extension_files = [os.path.splitext(os.path.basename(fits_file))[0] for fits_file in fits_files]

    # if directory where the output files will be stored is not there, create it
    if not os.path.isdir(args.dir1):
        os.mkdir(args.dir1)

    for idx, without_extension_file in enumerate(without_extension_files):
        
        detect_minarea = 9
        detect_thresh = 10.
        analysis_thresh = 10.
        
        # convert to pixels
        seeing_fwhm_pix = seeing_fwhm[idx] / secpix[idx]

        # aperture size used, you can change to suit your needs
        aper_size = np.int(np.round(1.5 * seeing_fwhm_pix))  # pixels

        # parameter file which you created, perhaps you used a different name
        parameter_file = 'configuration_file.param'
        configuration_file = 'configuration_file.sex'
                
        # change some options in default.sex via the command line, this will overwrite the default values
        command = 'sex %s/%s -c %s -CATALOG_NAME %s.cat -PARAMETERS_NAME %s -DETECT_MINAREA %s -DETECT_THRESH %s -ANALYSIS_THRESH %s -PHOT_APERTURES %s -SATUR_LEVEL %s -GAIN %s -PIXEL_SCALE %s -SEEING_FWHM %s -CHECKIMAGE_TYPE APERTURES -CHECKIMAGE_NAME %s_checkimage.fits' % (args.dir2, fits_files[idx], configuration_file,  without_extension_file, parameter_file, detect_minarea, detect_thresh, analysis_thresh, aper_size, saturate[idx], gain[idx], pixel_scale[idx], seeing_fwhm_pix, without_extension_file)
        
        try:
            # run the command
            subprocess.call(command.split())
            
        except Exception as e:
            print('Oops something went wrong running sextractor on %s' % (fits_files[idx]))
            
        # move the file to args.dir1 if is there
        if os.path.isfile('%s.cat' % (without_extension_file)):
            os.system('mv %s.cat %s_checkimage.fits %s' % (without_extension_file, without_extension_file, args.dir1))
            
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = 'This program will extract catalog(s) from image(s)')

    parser.add_argument('-d1', '--dir1', action = 'store', help = 'The name of the directory where the extracted catalogs will be stored', type = str)
    parser.add_argument('-d2', '--dir2', action = 'store', help = 'The name of the directory where the fits files are', type = str)
    parser.add_argument('-f', '--filename', action = 'store', help = 'Name of the file containing necessary header information', type = str)

    args = parser.parse_args()

    source_extractor(args)
