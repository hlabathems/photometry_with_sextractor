from astropy.io import fits, ascii
import subprocess
import argparse
import os

def extract_columns(filename):
    
    data = ascii.read(filename)

    mask = (data['FILTER'] == 'V')

    return data['NAME'][mask], data['GAIN'][mask], data['SATURATE'][mask]

def source_extractor(args):
    
    fits_files, gain, saturate = extract_columns(args.filename)
    
    without_extension_files = [os.path.splitext(os.path.basename(fits_file))[0] for fits_file in fits_files]

    if not os.path.isdir(args.dir1):
        os.mkdir(args.dir1)

    for idx, without_extension_file in enumerate(without_extension_files):
        
        try:
            with open('%s/LOG' % (args.dir1), 'a+') as fo:
                
                aper_size = 10  # pixels
                pixel_scale = 0 # to use WCS info
                parameter_file = 'config.param'
                
                command = 'sex %s/%s -CATALOG_NAME %s.cat -PARAMETERS_NAME %s -PHOT_APERTURES %s -SATUR_LEVEL %s -GAIN %s -PIXEL_SCALE %s -CHECKIMAGE_TYPE APERTURES -CHECKIMAGE_NAME %s_checkimage.fits' % (args.dir2, fits_files[idx], without_extension_file, parameter_file, aper_size, saturate[idx], gain[idx], pixel_scale, without_extension_file)
            
                subprocess.call(command.split(), stdout = fo)
            
            if os.path.isfile('%s.cat' % (without_extension_file)):
                os.system('mv %s.cat %s_checkimage.fits %s' % (without_extension_file, without_extension_file, args.dir1))
            else:
                print('%s.cat and/or %s_checkimage.fits could not be moved, check if either or both exist?' % (without_extension_file, without_extension_file))

        except Exception as e:
            print('Oops something went wrong running sextractor on %s' % (fits_files[idx]))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = 'This program will extract catalog(s) from image(s)')

    parser.add_argument('-d1', '--dir1', action = 'store', help = 'The name of the directory where the extracted catalogs will be stored', type = str)
    parser.add_argument('-d2', '--dir2', action = 'store', help = 'The name of the directory where the fits files are', type = str)
    parser.add_argument('-f', '--filename', action = 'store', help = 'Name of the file containing necessary header information', type = str)

    args = parser.parse_args()

    source_extractor(args)
