# Gets House of Commons transcripts in xml format from theyworkforyou.com (twfy)
# The xml files follow the naming scheme: debatesYYYY-MM-DDa.xml
# where the 'a' can be any alphabetic character or not be present (i.e. debatesYYYY-MM-DD.xml).
# For dates with more than one file, the file with the highest position letter is the final file, and others are incomplete.
# This script downloads all complete files from dates within the years specified in line 16.

import sys
from datetime import timedelta, date
import string
import requests
import wget

start_date = date(int(sys.argv[1][:4]), int(sys.argv[1][4:6]), int(sys.argv[1][6:]))
end_date = date(int(sys.argv[2][:4]), int(sys.argv[2][4:6]), int(sys.argv[2][6:]))

day_count = (end_date - start_date).days + 1

url = 'https://www.theyworkforyou.com/pwdata/scrapedxml/debates/debates'

# Get output file path id scpecified:
if len(sys.argv) > 3:
	path_to_output_files = sys.argv[3]
else:
	path_to_output_files = None

print(f'\nDownloading debate transcripts from {start_date} to {end_date} ...\n') #% (start_date,  end_date)) #f"This {drink} costs ${price:.02f}."
for d in (start_date + timedelta(n) for n in range(day_count)):
	# Get each days file with the highest positioned letter in the alphabet:
	got_date = False
	for letter in string.ascii_lowercase[:8][::-1]: # iterate alphabet in reverse from h-a
		f = url + str(d) + letter + '.xml'
		r = requests.get(f)
		if r:
			print('Downloading transcript of ', d)
			got_date = True # can I get rid of this?
			wget.download(f, path_to_output_files)
			break
	# If no letter found for given day, look for file with none:
	if got_date == False:
		f = url + str(d) + '.xml'
		r = requests.get(f)
		if r:
			print('Downloading transcript of ', d)
			wget.download(f, path_to_output_files)
			break