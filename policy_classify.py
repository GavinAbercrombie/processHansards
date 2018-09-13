import pandas as pd 
import csv
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.multiclass import OneVsRestClassifier
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from nltk.corpus import stopwords
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import KFold
from sklearn.svm import LinearSVC
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.metrics import precision_score
from sklearn.metrics import recall_score
from sklearn.metrics import f1_score
from scipy import sparse
from nltk.stem import *
from nltk.stem.porter import *
from nltk.stem.snowball import SnowballStemmer
import nltk
from nltk.corpus import sentiwordnet as swn
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords

# Pre-process stuff:
stop_words = set(stopwords.words('english'))
stemmer = PorterStemmer()

# load debate data:
data = open('../motions_big_agree.csv')
dataset = csv.reader(data)

# get all labels onto motions:
motions_dict = {}
labels_list = []
labels_dict = {}
parties = []
mps = []
for row in dataset:
	date = row[0]
	name = row[1]
	party = row[2]
	title = row[3]
	motion = row[4]
	premotion = row[5]
	label = row[-1]
	if label in labels_dict:
		labels_dict[label] += 1
	else:
		labels_dict[label] = 1
	mp = row[1]
	if label not in labels_list:
		labels_list.append(label)
	if mp not in mps:
		mps.append(mp)
	if party not in parties:
		parties.append(party)
	aidi = date + name + title + motion 
	if aidi not in motions_dict:
		motions_dict[aidi] = [date, name, party, title, motion, premotion, [label]]
	else:
		motions_dict[aidi][-1].append(label)
del motions_dict['datemotion_speakertitlemotion']
print('Policy labels:', labels_list)
labelled_motions = {}
idee = 0

for k, v in motions_dict.items():
	date = v[0].split('-')[0]
	if date.isdigit():
		date = (int(date)-1997)/22
	mpees = np.zeros(len(mps))
	for mp in range(len(mps)):
		if mps[mp] == v[1]:
			mpees[mp] = 1
	parts = np.zeros(len(parties))
	for p in range(len(parties)):
		if parties[p] == v[2]:
			parts[p] = 1
	labels = np.zeros(len(labels_list))	
	for lab in range(len(labels_list)):
		for label in v[-1]:
			if label == labels_list[lab]:
				labels[lab] = 1
	debate = v[:-1]
	debate.append(mpees)
	debate.append(parts)
	debate.append(date)
	debate.append(labels)
	labelled_motions[idee] = debate
	idee += 1

organised_motions = {}
for k, v in labelled_motions.items():
	cats_no = len(v)
	pols_no = len(v[-1])
	content = v[:-1]
	for i in v[-1]:
		content.append(i)
	organised_motions[k] =  content

df = pd.DataFrame.from_dict(organised_motions, orient='index')

rowsums = df.iloc[:,10:].sum(axis=1)
x=rowsums.value_counts()

#SOME PLOTS TO EXAMINE THE DATA:

# plot how many motions for each policy label:
df_pols = df.loc[:, 10:]
counts = []
categories = list(df_pols.columns.values)
pol_pos = 1
for i in categories:
    counts.append((labels_list[pol_pos], df_pols[i].sum()))
    pol_pos += 1
df_stats = pd.DataFrame(counts, columns=['category', 'number_of_comments'])
print('Max. comments:', int(np.max(df_stats['number_of_comments'].tolist())))
df_stats.plot(x='category', y='number_of_comments', kind='bar', legend=False, grid=True, figsize=(8, 5))
plt.title("Number of motions per Policy label")
plt.ylabel('Number of motions', fontsize=12)
plt.xlabel('Policy label number', fontsize=12)
plt.tight_layout()
plt.show()

# plot histgram showing how many labels the motions have:
colours = [(0.12156862745098039, 0.4666666666666667, 0.7058823529411765), (1.0, 0.4980392156862745, 0.054901960784313725)]
sns.set(style="white", font_scale=1.2)
plt.figure(figsize=(8,5))
ax = sns.barplot([1,2], x.values, palette=colours)
plt.title("Number of Policy labels per motion")
plt.ylabel('Number of motions', fontsize=12)
plt.xlabel('Number of topic labels', fontsize=12)
plt.show()

# RUN CLASSIFICATION:
its_no = 1#20 # no of iterations -- how many times to run the experiment
policies = list(range(10, pols_no+9))
effone = 0
print('Running', its_no, 'tests')
for i in range(its_no):
	train, test = train_test_split(df, test_size=0.1, shuffle=True)#, random_state=42)

	X_train = []
	X_test = []
	X_mp_train, X_mp_test = [], []
	X_party_train, X_party_test = [], []
	X_date_train, X_date_test = [], []
	for row in range(len(train.iloc[:,4])):
		X_train.append(train.iloc[row,3])# + ' ' + train.iloc[row,4])# + ' ' + train.iloc[row,5])
		X_mp_train.append(train.iloc[row,6])
		X_party_train.append(train.iloc[row,7])
		X_date_train.append(train.iloc[row,8])
	for row in range(len(test.iloc[:,4])):
		X_test.append(test.iloc[row,3])# + ' ' + test.iloc[row,4])# + ' ' + train.iloc[row,5])
		X_mp_test.append(test.iloc[row,6])
		X_party_test.append(train.iloc[row,7])
		X_date_test.append(test.iloc[row,8])

	X_party_train = np.array(X_party_train)
	X_party_test = np.array(X_party_test)
	X_mp_train = np.array(X_mp_train)
	X_mp_test = np.array(X_mp_test)
	X_date_train = np.array(X_date_train)
	X_date_test = np.array(X_date_test)

	vectorizer = TfidfVectorizer(min_df=3, max_df = 1.0, stop_words=stop_words, ngram_range=(1,2), sublinear_tf=True)
	SVC = OneVsRestClassifier(LinearSVC(), n_jobs=1)

	all_true_labels = []
	all_predictions = []

	for policy in policies:
	  # train the model using X_dtm & y
		X_train = [stemmer.stem(motion) for motion in X_train]
		X_test = [stemmer.stem(motion) for motion in X_test]
		train_corpus = vectorizer.fit_transform(X_train)
		test_corpus = vectorizer.transform(X_test)
		train_corpus = sparse.hstack((train_corpus, X_party_train))
		test_corpus = sparse.hstack((test_corpus, X_party_test))
		train_corpus = sparse.hstack((train_corpus, X_mp_train))
		test_corpus = sparse.hstack((test_corpus, X_mp_test))
	  #train_corpus = sparse.hstack((train_corpus, X_date_train))
	  #test_corpus = sparse.hstack((test_corpus, X_date_test))  
	  #train_corpus = np.hstack((X_party_train, X_mp_train))
	  #test_corpus = np.hstack((X_party_test, X_mp_test))   
		
		SVC.fit(train_corpus, train[policy])


	  # compute the testing accuracy
		prediction = SVC.predict(test_corpus)
		for l in test[policy]:
			all_true_labels.append(l)
		for p in list(prediction):
			all_predictions.append(p)


	score = f1_score(all_true_labels, all_predictions)
	print('Test f1 is {}'.format(score))
	effone += score
	
print('\nMean f1 score:', effone/its_no)
