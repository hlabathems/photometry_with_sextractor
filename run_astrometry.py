import sys, os

# Store fits files

infiles = sys.argv[1:]

# Put apikey

apikey = 'psqszsmwidmbdmcx'

# Pass fits file to client script

for infile in infiles:

    # Add ast for astrometry
    
    outfile = os.path.splitext(infile)[0] + '_ast' + '.fits'

    # Command to run

    cmd = 'python client.py -k %s -u %s --newfits %s' % (apikey, infile, outfile)

    # Store status
    
    status = os.system(cmd)

    if status != 0:
        
        # Write to log

        with open('log', mode = 'a+') as fo:
            fo.write('%s\n' % (infile))



