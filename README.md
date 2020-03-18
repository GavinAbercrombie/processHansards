# processHansards

For obtaining and processing transcripts from UK parliamentary debates. 

Contains the following python scripts:

## getTWFY.py:
Code for getting and processing Hansard House of Commons parliamentary debate data
Downloads xml files from [TheyWorkForYou](https://www.theyworkforyou.com/)

To run:

`python getTWFY.py <YYYYMMDD> <YYYYMMDD> <output_file_path>`

with your required start and end dates (inclusive) included in the above format, and an optional output file path. 

## processTWFYfiles.py

To run:

`python processTWFY.py`

You will need to alter the code to reflect:
1. Line 42: Your path to the `new_people.json` file  (located in this repository in the `data` folder)
2. Line 57: Your path to the xml files downloaded from TheyWorkForYou
3. Line 290: Your output file name and path


## hansard_scraper.py:

Gets all spoken utterances from the Hansard record between specified years 
