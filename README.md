# processHansards

For obtaining and processing transcripts from UK parliamentary debates. 

Contains the following python scripts:

## getTWFY.py:
Code for getting Hansard House of Commons parliamentary debate data.

Downloads xml files from [TheyWorkForYou](https://www.theyworkforyou.com/)

To run:

`python getTWFY.py <YYYYMMDD> <YYYYMMDD> <output_file_path>`

with your required start and end dates (inclusive) included in the above format, and an optional output file path. 

## processTWFYfiles.py

Process the files obtained with getTWFY.py

Outputs a `csv` file with the following fields:

`debate id, motion speaker id, motion speaker name, motion speaker party, debate title, motion text, speaker id, speaker name, speaker party, vote, utterance 1, utterance 2, ..., utterance n`

Obtains debates with *exactly* one motion and one division.

To run:

`python processTWFYfiles.py`

You will need to alter the code to reflect:
1. Line 42: Your path to the `new_people.json` file  (located in this repository in the `data` folder)
2. Line 57: Your path to the xml files downloaded from TheyWorkForYou
3. Line 290: Your output file name and path


## hansard_scraper.py:

Gets all spoken utterances from the Hansard record (at [https://hansard.parliament.uk]) between specified years (line 31).

To run:

`python hansard_scraper.py`

