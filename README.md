# photometry_with_sextractor
Doing differential photometry using sextractor. This is not a pipeline nor is it intended to be perfect. It assumes that the basic reduction (bias, flat, dark) steps have already been applied to your data.

NB: This is still under development.

Installation
------------

In order to run this, one needs to install the following packages:

  * numpy
  * astropy
  * ccdproc
  * matplotlib
  * sextractor (2.19.0)
  * ds9

Instructions
------------

1. Git clone into your local directory
    https://github.com/hlabathems/photometry_with_sextractor.git
    
2. Run the script run_create_table.py. This will create an ascii file with necessary extracted header information from your fits files using the powerful ccdproc:

    `python run_create_table -p /directory with fits files/ -f output.txt`
    
   You can edit the script to add or replace some of the headers if you don't think they are relevant
   
3. Before we run sextractor, look into config.param and default.sex. In the config.param, we're telling sextractor what output options do we want included in the output catalogs. Look into parameter_definitions file to know what each means. If you want to add or remove parameter(s), you can do so in the config.param file. In the default.sex, the only things we change are the CATALOG_NAME, PARAMETERS_NAME, PHOT_APERTURES, SATUR_LEVEL, GAIN, CHECKIMAGE_TYPE and CHECKIMAGE_NAME via the command line. The SATUR_LEVEL and GAIN are read from the fits header.

   > python run_source_extractor.py -d1 /directory where the extracted catalogs will be stored/ -d2 /directory where the fits files are/ -f /name of outfile from above/ 

4. Open one of the check images as a result of running step 3 above, you should see fixed apertures drawn around the detected objects in ds9.   
