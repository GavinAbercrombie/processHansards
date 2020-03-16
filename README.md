# processHansards

For obtaining and processing transcripts from UK parliamentary debates. 

Contains the following python scripts:

## getTWFY.py:
Code for getting and processing Hansard House of Commons parliamentary debate data
Downloads xml files from theyworkforyou.com

To run:

python getTWFY.py <YYYYMMDD> <YYYYMMDD> <outputF-file_path>

with your required start and end dates (inclusive) included in the above format, and an optional output file path. 

## policy_classify.py:
Multilabel classification of House of Commons debate motions

## hansard_scraper.py:
Gets all spoken utterances from the Hansard record between specified years 
