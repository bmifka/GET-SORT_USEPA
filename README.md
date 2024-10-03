# GET-SORT_USEPA

Code to download multiple US-EPA Meteo and Air Quality data and make custom files consisting of program files:

1. get_EPA_files.sh  downloads the EPA (for now only) hourly files for Wind and scalar (Meteo and/or Air Quality) variables from EPA files from https://aqs.epa.gov/aqsweb/airdata/
   and reduces them to a new smaller files for each year
2. Analyse_EPA_Files_1.py reads the files made in step 1 and checks for the years with available mutual wind and scalar variable (e.g. PM10) data. For now is only possible to have 1 variable. It makes the output file where the user can check for data availability.
3. Sort_EPA_Files.py reads the Meta_File.csv and downloaded files, sorts them, and writes to the custom output file in *.mat format
4. Sort_EPA_Functions.py contains 2 functions for Wind and Scalar Variable extraction and sort: Extract_EPA_Wind Extract_EPA_Variable

