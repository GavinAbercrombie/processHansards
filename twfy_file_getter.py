# Gets the highest letter xml file from theyworkforyou.com (lower letter files are incomplete)

import calendar
import string
import requests
import wget

cal = calendar.Calendar()

site = 'https://www.theyworkforyou.com/pwdata/scrapedxml/debates/debates'

for y in range(2003, 2004): # specify required date range here
	year = str(y)
	for m in range(1, 13):
		month = str(m)
		if len(month) == 1:
			month = '0' + month
		monthdays = [str(d) for d in cal.itermonthdays(y, m) if d != 0]
		for d in monthdays:
			got_date = False
			day = str(d)
			if len(day) == 1:
				day = '0' + day
			# Get each days file with the highest letter suffix:
			for letter in string.ascii_lowercase[:8][::-1]: # iterate alphabet in reverse from h-a
				#print(letter)
				url = site + str(year) + '-' + str(month) + '-' + day + letter + '.xml'
				r = requests.get(url)
				if r:
					got_date = True
					wget.download(url)
					break
			# If no letter found for given day, look for file with none:
			if got_date == False:
				url = site + str(year) + '-' + str(month) + '-' + day + '.xml'
				r = requests.get(url)
				if r:
					wget.download(url)
					break
