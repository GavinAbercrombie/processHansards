# -*- coding: utf-8 -*-

""" 
Gets all spoken utterances from the Hansard record between specified years 
Output: json file for each year in specified range
"""

import calendar
import requests
from urllib.request import urlopen
from bs4 import BeautifulSoup as BS
import json

cal = calendar.Calendar()

#link from each days page looks like this:
# https://hansard.parliament.uk/html/commons/2019-03-05/CommonsChamber
# target url looks like this:
# https://hansard.parliament.uk/commons/2019-03-05/debates/d3b4d1f7-f6d2-481a-add1-a439ce0ace33/CommonsChamber


# TODO:
# should Questions be included? They are in class="Question", at least from 2006
# should we ignore text in square brackets? this is not spoken
# deal with ascii characters (\u2014\)

site = 'https://hansard.parliament.uk/html/commons/'

ignore = ['Monday', 'Tuesday,', 'Wednesday,', 'Thursday,', 'Friday,', 'Saturday,', 'Sunday,']

for y in range(1802, 2020): # specify required date range here
	
	# run through dates in range in format YYYY-MM-DD:
	year = str(y)
	year_dict = {}
	for m in range(1, 13):
		month = str(m)
		if len(month) == 1:
			month = '0' + month
		monthdays = [str(d) for d in cal.itermonthdays(y, m) if d != 0]
		for d in monthdays:
			day = str(d)
			if len(day) == 1:
				day = '0' + day
			date = str(year) + '-' + str(month) + '-' + day

			# find redirect link to relevant target url in Hansard site and get text from all utterances:
			url = site + date + '/CommonsChamber' 
			r = requests.get(url)
			redirecturl = r.url
			if redirecturl[30:37] == 'commons': # make sure it's the actual target url, not the redirect link
				print('Getting transcript from', date)
				year_dict[date] = [] 
				soup = BS(urlopen(redirecturl).read(), 'lxml')
				if int(year) >= 2006: # transcripts before this date do not have a separate class for spoken text and other information like dates, titles
					for utterance in soup.findAll("p", {"class": "hs_Para"}):
						year_dict[date].append(utterance.text)
				else: 
					for utterance in soup.findAll("p", {"class": ""}):
						if len(utterance.text.split()) > 0: # check that text is not empty which throws error
							if utterance.text.split()[0] not in ignore: # ignore dates
								year_dict[date].append(utterance.text)
	with open('hansardCommons' + year + '.json', 'w') as jsonfile:
		json.dump(year_dict, jsonfile)
