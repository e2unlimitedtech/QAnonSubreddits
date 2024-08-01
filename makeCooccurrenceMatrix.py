#!/usr/bin/env python3
from __future__ import print_function
import pandas as pd     
import numpy as np
import re
import nltk
from pprint import pprint
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation

from nltk.corpus import stopwords # Import the stop word list
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize

#inTweets='TweetsContainingPatriot.csv'
#inData='TweetsFromPatriotProfiles.csv'
#inData='Tweet_Text_Oath_250000_No_Dupes.csv'
inData = 'QAnon/extractedCommsAndSubsExplicitOnly.csv'
inCol='text'
outFile='QAnon/explict_cooccurrence_matrix_11_12_2023.csv'

class CustomCountVectorizer(CountVectorizer):
	def build_analyzer(self):
	    lemmatizer = WordNetLemmatizer()
	    analyzer = super().build_analyzer()
	    stop_words = set(stopwords.words('english'))
	    stop_words=stop_words.union({'amp','http', 'https','rt','unknown','www','com','org','net','gov','reddit','subreddit','deleted','removed','board','thread','archive'}) #twitter stop words

	    def custom_analyzer(doc):
	        tokens = [lemmatizer.lemmatize(token) for token in analyzer(doc)]
	        tokens = [token for token in tokens if token not in stop_words]
	        #tokens = [token for token in tokens if token.isalpha()]
	        return tokens
	    return custom_analyzer

#applies the rollups file to the corpus
#precondition: corpus is a pandas series object, text is all lowercase
#postcondition: text has been updated with rollup replacements
def applyRollups(corpus):
	rollups ={}
	with open("rollups10.csv") as f:
		lines=f.readlines()
		lines=lines[1:] # get rid of header
		print(f"num rollups with dupes {len(lines)}")
		for line in lines:
			fields=line.strip().split(',')
			rollups[fields[0].strip()]=fields[1].strip()

	print (f"num rollups after dupes removed {len(rollups)}")

	rollupsFound={}
	count=0
	sorted_keys = sorted(rollups.keys(), key=lambda x: len(x), reverse=True)
	for key in sorted_keys:
		count+=1
		if count%100==0:
			print(f"working on keyword {key}")
		if len(key)<3:
			break
		for index, workingtext in corpus.items():
			if key in workingtext:
			#	print(f"found {key}, checking regex")
				search_keyword=r'\b'+re.escape(key)+r'\b'
				new_text = re.sub(search_keyword, rollups[key],workingtext)
				if new_text != workingtext:
					#print (f"found: {new_text} at index {index}")
					corpus.at[index] = new_text
					if key in rollupsFound:
						rollupsFound[key]+=1
					else:
						rollupsFound[key]=1
	print(f"rollups actually found {len(rollupsFound)}")
	print (rollupsFound)
	print(corpus[0:100])


if __name__=='__main__':

	corpus=pd.read_csv(inData)
	corpus.dropna(subset=[inCol], inplace=True)
	corpus=corpus[inCol].str.lower()
	print(len(corpus))
	print(type(corpus))

	applyRollups(corpus)

	stop_words = stopwords.words("english")
	stop_words.extend(['amp','http', 'https','rt','unknown','www','com','org','net','gov','reddit','subreddit','deleted','removed','board','thread','archive']) #twitter stop words

# Initialize Custom CountVectorizer with custom options
#vectorizer = CustomCountVectorizer(min_df=2, max_df=0.8, stop_words='english')

	tf_vectorizer = CustomCountVectorizer(strip_accents = 'unicode',
	                                stop_words = stop_words,
	                                ngram_range = (1,1),
	                                lowercase = False,
	                                token_pattern = r'\b[a-zA-Z\_]{3,}\b',
	                                min_df = 200,
	                                max_df=.3)


	term_document_matrix = tf_vectorizer.fit_transform(corpus)
	num_docs, num_terms = term_document_matrix.shape
	print("Size of term-document matrix: {} documents x {} terms".format(num_docs, num_terms))

#	term_document_matrix = vectorizer.fit_transform(documents)
	# Transform term-document matrix to term-frequency matrix
	term_frequency_matrix = term_document_matrix.toarray()
	feature_names = tf_vectorizer.get_feature_names_out()
	print(feature_names)

	print("Calculating co-occurrence matrix")
	# Calculate co-occurrence matrix
	cooccurrence_matrix = np.dot(term_frequency_matrix.T, term_frequency_matrix)

	print("Done")
	# Get the feature names (terms)
	feature_names = tf_vectorizer.get_feature_names_out()

	# Create a DataFrame to store term co-occurrences
	cooccurrence_df = pd.DataFrame(cooccurrence_matrix, columns=feature_names, index=feature_names)

	# Stack the DataFrame to create a tidy format
	stacked_df = cooccurrence_df.stack().reset_index()
	stacked_df.columns = ['Term1', 'Term2', 'Count']

	# Convert Term1 and Term2 to strings to ensure they are treated as text
	stacked_df['Term1'] = stacked_df['Term1'].astype(str)
	stacked_df['Term2'] = stacked_df['Term2'].astype(str)


	# Filter rows where Count is greater than 0
	filtered_stacked_df = stacked_df[ (stacked_df['Count'] > 1) & (stacked_df["Term1"]<stacked_df["Term2"])]

	# Write the DataFrame to a CSV file
	filtered_stacked_df.to_csv(outFile, index=False)
