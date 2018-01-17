from astropy.io import fits, ascii
import subprocess
import argparse
import os

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

    return data['NAME'][mask], data['GAIN'][mask], data['SATURATE'][mask]

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
    fits_files, gain, saturate = extract_columns(args.filename)
    
    # remove the .fits extension
    without_extension_files = [os.path.splitext(os.path.basename(fits_file))[0] for fits_file in fits_files]

    # if directory where the output files will be stored is not there, create it
    if not os.path.isdir(args.dir1):
        os.mkdir(args.dir1)

    for idx, without_extension_file in enumerate(without_extension_files):
            
        # aperture size used, you can change to suit your needs
        aper_size = 10  # pixels
                
        # default is 1, change to 0 to use WCS info
        pixel_scale = 0 
                
        # parameter file which you created, perhaps you used a different name
        parameter_file = 'config.param'
                
        # change some options in default.sex via the command line, this will overwrite the default values and save the terminal output to log file
        command = 'sex %s/%s -CATALOG_NAME %s.cat -PARAMETERS_NAME %s -PHOT_APERTURES %s -SATUR_LEVEL %s -GAIN %s -PIXEL_SCALE %s -CHECKIMAGE_TYPE APERTURES -CHECKIMAGE_NAME %s_checkimage.fits | tee -a log' % (args.dir2, fits_files[idx], without_extension_file, parameter_file, aper_size, saturate[idx], gain[idx], pixel_scale, without_extension_file)
        
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
