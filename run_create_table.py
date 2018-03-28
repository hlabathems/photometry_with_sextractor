from ccdproc import ImageFileCollection
from astropy.io import ascii
import argparse

def create_table(args):
    ic = ImageFileCollection(location = args.path, keywords = ['HJD', 'FILTER', 'AIRMASS', 'EXPTIME', 'GAIN', 'SATURATE', 'L1FWHM', 'SECPIX', 'L1ZP', 'L1ZPERR', 'SITEID'])
    
    data = [ic.summary['file'], ic.summary['HJD'], ic.summary['FILTER'], ic.summary['AIRMASS'], ic.summary['EXPTIME'], ic.summary['GAIN'], ic.summary['SATURATE'], ic.summary['L1FWHM'], ic.summary['SECPIX'], ic.summary['L1ZP'], ic.summary['L1ZPERR'], ic.summary['SITEID']]

    ascii.write(data, args.filename, names = ['NAME', 'HJD', 'FILTER', 'AIRMASS', 'EXPTIME', 'GAIN', 'SATURATE', 'L1FWHM', 'SECPIX', 'L1ZP', 'L1ZPERR', 'SITEID'], overwrite = True)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = 'This program will create a table containing raw images sorted according to type of filter, airmass etc')

    parser.add_argument('-p', '--path', action = 'store', help = 'Full path to directory containing the raw images', type = str)
    parser.add_argument('-f', '--filename', action = 'store', help = 'Name of the output file (ASCII) to store necessary header information', type = str)

    args = parser.parse_args()

    create_table(args)
