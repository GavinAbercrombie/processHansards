""" 
Get all speeches (concatenated utterances) from TheyWorkForYou files and organise by speaker and debate 
Output: corpus with units: debateid, motion, motionspeakerid, speech, speechspeakerid, vote
        included: debates with exactly one motion and one division
"""
import os, glob, re, sys
from bs4 import BeautifulSoup, Tag, NavigableString
from collections import OrderedDict
import csv, json
from builtins import any as b_any
import string

########## For rule-based debate processing #############

# The following have been found to indicate that a motion continues in the next xml element:
motion_continuers = [':', '-', '–', ',', ';', 
					 '1. ', '2. ', '3. ', '4. ', '5. ', '6. ', '7. ', '8.', '9.',
					 '(1)', '(2)', '(3)', '(4)', '(5)', '(6)', '(7)', '(8)', '(9)',  
					 '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 
					 '(a)', '(b)', '(c)', '(d)', '(e)', 'd', '(f)', '(g)', '(h)', 
					 '(i)', '(ii', '(iv', '(v)', , 
					 '1.–', '2.–', '3.—', '3.-', '4.–', '5.–', 
					 "'4.", "'(9"]

# The following have been found to indicate the end of a debate:
debate_enders = ['That the Question be now put.', 'Question put,', 'Question put.', 'Question put .', 'Question put:—', 
				 'Motion made, and Question put,', 'Question agreed to.', 'Question put and agreed to.', 
				 'Question put forthwith', 'The House divided:', 'Order.', ' The House proceeded to a Division.', 
				 'Question again proposed'] 

# The following non-speech items are removed:
non_speech = ['rose–', 'rose —', 'rose—', 'rose', 'rose——', 'rose— ', ' rose—', ' rose —', 'rose - ', 'r ose—', ' rose -', 
	      'Several hon. Members rose—', 'Members rose—', 'claimed to move the closure.',
			  'indicated dissent.', 'indicated assent.']

# ID and dates-in-office of Speakers:
speakers = {'10040': [20090622, 20191031, 'Bercow, John'], '10295': [20100608, 20191231, 'Hoyle, Lindsay'], '10348': [20131016, 20191231, 'Laing, Eleanor'], 
			'10648': [20170628, 20191231, 'Winterton, Rosie'], '10420': [19970514, 20090621, 'Martin, Michael'], '10054': [19920427, 20001023, 'Boothroyd, Betty'], 
			'10263': [19971514, 20101614, 'Haselhurst, Alan'], '10190': [20100608, 20130910, 'Evans, Nigel'], '10266': [20001023, 20100412, 'Heal, Sylvia'], 
			'11534': [20150603, 20170608, 'Engel, Natascha'], '10489': [20100609, 20150508, 'Primarolo, Dawn'], '10370': [19970514, 20100608, 'Lord, Michael']}

# This file contains MP party affiliation information:
people = json.load(open('../data/new_people.json'))

# Some regexs for removing non-speech text:
brackets_regex = "\[.*?\]"
parenthesis_regex = "\([^)]*\)"
all_brackets_regex = "[\(\[].*?[\)\]]"

######################################

# Add all debates to a dictionary: 
parlvote_dict = OrderedDict()

######### Process the files ##########

# get xml files:
path = '../data/twfy_xmls_temp/'
for xml_file in sorted(glob.glob(os.path.join(path, '*xml'))):
	print('Processing', xml_file.split('/')[-1])
	try:
		xml_dec = open(xml_file, encoding = "utf-8").read() # some files have different encodings
	except:
		xml_dec = open(xml_file, encoding = "ISO-8859-1").read()
	debate_soup = BeautifulSoup(xml_dec, 'lxml')
	publicwhip = debate_soup.find('publicwhip') # publicwhip is 1st level parent of xml, all content is children of this
	
	# Get minor or major headings -- these contain debate titles and indicate start of debates
	for elementTag in publicwhip.findChildren(recursive=False):
		if elementTag.name[-10:] == 'or-heading':
			debate_id = elementTag.attrs['id'].split('/')[-1]
			date = int(debate_id[:4] + debate_id[5:7] + debate_id[8:10])
			parlvote_dict[debate_id] = OrderedDict()
			debate_title = elementTag.contents[0].replace('\n', '').strip()
			parlvote_dict[debate_id]['debate_title'] = debate_title
			divs_no = 0 # keep track of how many divisions this debate has  } in both cases we only want 1
			motions_no = 0 # keep track of how many motions this debate has }
 
 			# Get motions, get id and name of MP who proposes motion; get utterances, id and name of MP:
			for sibling in elementTag.next_siblings:
				if sibling.name != None:
					if sibling.name[-10:] == 'or-heading': # another heading indicates that a different debate starts, so stop
						break

					if sibling.name == 'speech':
						if sibling.p is not None:
							if sibling.p.text[:13] == 'I beg to move': # get motions here
								motions_no += 1
								if 'person_id' in sibling.attrs:
									motion_person_id = sibling.attrs['person_id'].split('/')[-1] # newer files use 'person_id'
									parlvote_dict[debate_id]['motion_person_id'] = motion_person_id
									for k, v in people.items():
										if motion_person_id == k:
											motion_speakername = v['speakername']
											parlvote_dict[debate_id]['motion_speakername'] = motion_speakername
											for ke, va in v.items():
												if ke != 'speakername':
													if date >= int(va['start_date']) and date <= int(va['end_date']):
														motion_party = va['party']
														parlvote_dict[debate_id]['motion_party'] = motion_party
								elif 'speakerid' in sibling.attrs:
									if sibling.attrs['speakerid'] == 'unknown':
										break
									else:
										motion_member_id = sibling.attrs['speakerid'].split('/')[-1]
									for k, v in people.items():
										for ke, va in v.items():
											if motion_member_id == ke:
												motion_speakername = v['speakername']
												parlvote_dict[debate_id]['motion_speakername'] = motion_speakername
												motion_person_id = k
												parlvote_dict[debate_id]['motion_person_id'] = motion_person_id
												motion_party = va['party']
												parlvote_dict[debate_id]['motion_party'] = motion_party

								# get motion text
								motion = sibling.p.text.splitlines()[0].strip('\n')

								if sibling.p.q is not None and motion[-1] != '.':
									for el in sibling.p.contents[1:]:
										if el.name is not None:
											if el.name != 'br' and el.name != 'ol':
												motion = motion + ' ' + el.text.replace('\n', ' ').strip()
										elif el == '\n':
											pass
										else:
											break
									for sib in sibling.p.next_siblings:
										if isinstance(sib, Tag):
											motion = motion + ' ' + sib.text.replace('\n', ' ').strip()

								if motion[-1] != '.' and motion[-2:] != ".'":
									if sibling.p.next_sibling.next_sibling is not None:
										for sib in sibling.p.next_siblings:
											if motion[-1] != '.' and isinstance(sib, Tag):
												motion = motion + ' ' + sib.text.replace('\n', ' ').strip()

								if motion[-1] != '.' and motion[-2:] != ".'":
									for sib in sibling.next_siblings:
										if motion[-1] != '.' and motion[-2:] != ".'":
											if isinstance(sib, Tag):
												motion = motion + ' ' + sib.text.replace('\n', ' ').strip()
										else:
											break
								parlvote_dict[debate_id]['motion'] = motion

								# GET DIVISIONS:
								for sib in sibling.next_siblings:
									if sib.name is not None:
										if sib.name[-10:] == 'or-heading':
											break

										if sib.div is not None: 
											if sib.div['class'][0] == 'division':
												divs_no += 1
												ayes = []
												noes = []
												voters = []
												for element in sib.div:
													if element.name == 'table':
														for el in element: # NEED TO GO THROUGH LEFT COLUMN FIRST THEN RIGHT COLUMN 
															if isinstance(el, Tag) and el.td is not None:
																if len(el.td.text) > 0:
																	if el.td.text != 'AYES' and el.td.text != 'NOES': 
																		if el.td.text[:8] != 'Division' and len(el.td.text) > 0:
																			if len(el.td.text) > 0:
																				if el.td.text[0].isalpha():
																					voter = re.sub(parenthesis_regex, '', el.td.text.strip())
																					if len(voter) > 0:
																						voter = voter.replace('Dr ', '').replace('Miss ', '').replace('Ms ', '').replace('Mrs ', '').replace('Rt Hon ', '').replace('Sir ', '')
																						voters.append(voter)
														for el in element:
															if isinstance(el, Tag) and el.td is not None:
																if el.td.next_sibling is not None:
																	if el.td.next_sibling.next_sibling is not None:
																		if isinstance(el.td.next_sibling.next_sibling, Tag):
																			if el.td.next_sibling.next_sibling.text[:11] == 'Tellers for':
																				break 
																			else:
																				if len(el.td.next_sibling.next_sibling.text) > 0:
																					if el.td.next_sibling.next_sibling.text[0].isalpha():
																						voter = re.sub(parenthesis_regex, '', el.td.next_sibling.next_sibling.text.strip())
																						if len(voter) > 0:
																							voter = voter.replace('Dr ', '').replace('Miss ', '').replace('Ms ', '').replace('Mrs ', '').replace('Rt Hon ', '').replace('Sir ', '')
																							voters.append(voter)
												
												for v in range(len(voters)):
													if voters[v][0].lower() == 'ö' or voters[v][0].lower() == 'õ':
														initial = 'o'
													else:
														initial = voters[v][0].lower()
													if voters[v-1][0].lower() == 'ö' or voters[v-1][0].lower() == 'õ':
														previous = 'o'
													else:
														previous = voters[v-1][0].lower()	
													if string.ascii_lowercase.index(initial) < string.ascii_lowercase.index(previous): # when the initial letter has lower alphabet position than previous, noes list begins
														ayes = voters[:voters.index(voters[v])]
														noes = voters[voters.index(voters[v]):]
 
												for mp in ayes:
													for key, val in parlvote_dict[debate_id].items():
														if key.isdigit():
															speechname = val['speakername']
															if mp == speechname:
																parlvote_dict[debate_id][key]['speech'].append(1)
												for mp in noes:
													for key, val in parlvote_dict[debate_id].items():
														if key.isdigit():
															speechname = val['speakername']
															if mp == speechname:
																parlvote_dict[debate_id][key]['speech'].append(0)
												break

										for e in debate_enders:
											if e in sib.text:
												break

										if 'person_id' in sib.attrs:
											person_id = sib.attrs['person_id'].split('/')[-1] # newer files use 'person_id'
											for k, v in people.items():
												if person_id == k:
													speakername = v['speakername']
													parlvote_dict[debate_id]['speakername'] = speakername
													for ke, va in v.items():
														if ke != 'speakername':
															if date >= int(va['start_date']) and date <= int(va['end_date']):
																party = va['party']
																parlvote_dict[debate_id]['party'] = party
										elif 'speakerid' in sib.attrs:
											member_id = sib.attrs['speakerid'].split('/')[-1]
											for k, v in people.items():
												for ke, va in v.items():
													if member_id == ke:
														speakername = v['speakername']
														person_id = k
														party = va['party']

										if 'speakername' in locals():
											if person_id != motion_person_id: # don't include speeches by mp who tables motion
												if 'Speaker' not in speakername and 'nospeaker' not in sib.attrs: # don't include speeches by speaker
													utterance = re.sub(all_brackets_regex, "", sib.text.strip('\n').replace('\n', ' ').strip())		
													for e in debate_enders:
														if e in utterance:
															utterance = utterance.split(e)[0]
													if utterance not in non_speech and len(utterance) > 1:
														if utterance[-3:] != ' am' and utterance[-3:] != ' pm': # times
															if person_id not in parlvote_dict[debate_id]:
																parlvote_dict[debate_id][person_id] = {'speakername': speakername, 'person_id': person_id, 'party': party}
																parlvote_dict[debate_id][person_id]['speech'] = [utterance]
															else:
																parlvote_dict[debate_id][person_id]['speech'].append(utterance)
					if sibling.name == 'division':
						divs_no += 1
						ayes = []
						noes = []
						for mpname in sibling.find_all('mpname'):
							if 'person_id' in mpname.attrs: # newer files use 'person_id'
								if mpname.attrs['vote'] == 'aye':
									ayes.append(mpname.attrs['person_id'].split('/')[-1])
								elif mpname.attrs['vote'] == 'no':
									noes.append(mpname.attrs['person_id'].split('/')[-1])
							if 'id' in mpname.attrs: # older files 'id'
								for k, v in people.items():
									for m in v:
										if mpname.attrs['id'].split('/')[-1] == m:
											if mpname.attrs['vote'] == 'aye':
												ayes.append(k)
											elif mpname.attrs['vote'] == 'no':
												noes.append(k)
						for mp in ayes:
							if mp in parlvote_dict[debate_id]:
								parlvote_dict[debate_id][mp]['speech'].append(1)
						for mp in noes:
							if mp in parlvote_dict[debate_id]:
								parlvote_dict[debate_id][mp]['speech'].append(0)
						break
 
 			# Keep only debates with exactly 1 motion and 1 division:
			novote_list = []
			if motions_no != 1 or divs_no != 1:
				del parlvote_dict[debate_id]
			else:
				for mp, content in parlvote_dict[debate_id].items():
					if mp.isdigit() and not isinstance(content['speech'][-1], int):
						novote_list.append(mp)
			for novote in novote_list:
				del parlvote_dict[debate_id][novote]

speech_count = 0
utt_count = 0
with open('../parlvote.csv', 'w') as f:
	debate_writer = csv.writer(f, delimiter=',')
	for k, v in parlvote_dict.items():
		for key, val in v.items():
			if key.isdigit():
				try:
					speech = [k, v['motion_person_id'], v['motion_speakername'], v['motion_party'], v['debate_title'], v['motion'], key, val['speakername'], val['party'], val['speech'][-1]] # add debate title and motion text
				except:
					break
				for utt in val['speech'][:-1]:
					utt_count +=1
					speech.append(utt)
				debate_writer.writerow(speech)
				speech_count += 1
print('No of speeches:', speech_count)
print('No of utterances:', utt_count)
print('Mean utterances:', utt_count/speech_count)
