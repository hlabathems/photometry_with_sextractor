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

   `python run_source_extractor.py -d1 /directory where the extracted catalogs will be stored/ -d2 /directory where the fits files are/ -f /name of outfile from above/` 

4. Open one of the check images as a result of running step 3 above, you should see fixed apertures drawn around the detected objects in ds9. Choose more than one comparison star, preferably close to your target. E.g

   Stars   | IMAGE_RA | IMAGE_DEC
   --- | ---      | ---
   cs1 | 10:23:10.881 | 19:52:06.005
   cs2 | 10:23:36.211 | 19:50:10.505
   cs3  | 10:23:41.751 | 19:51:32.212
   
     and so on. Lastly, your target star
  
    Object   | IMAGE_RA | IMAGE_DEC
   --- | ---      | ---
   target | 10:23:30.600 | 19:51:54.500

5. Now that we have selected our targets, we want to cross match our catalogs (.cat) against the selected objects in step 4.   Do to that we run_cross_match.py. For cs1 above, the code will output an ascii file called cs1.txt with matched information

   `python run_cross_match.py --dir /directory where the catalogs to be read are stored/ --ra 10:23:10.881 --dec 19:52:06.005 --fin /name of outfile from 2/ --fout cs1.txt`
   
6. Lastly, run_differential.py on all cs files.

   `python run_differential.py cs*txt`
