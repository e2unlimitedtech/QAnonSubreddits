import pandas as pd
import numpy as np
import pickle

path = 'C:\\Users\\nikolabaci\\Dropbox (QBCC)\\Magazine Archives\\_QAnonSubReddits\\CombinedQAnon\\'

#read the data (submissions & comments) for both subreddits: Great Awakening & CBTS Stream
ga_subs = pd.read_csv(path + "greatawakening_subs_combined.csv")
cbts_subs = pd.read_csv(path + "cbts_stream_subs_combined.csv")

ga_coms = pd.read_csv(path + "greatawakening_comms_combined.csv")
cbts_coms = pd.read_csv(path + "cbts_stream_comms_combined.csv")

#combine comments and submissions
subs = pd.concat([cbts_subs, ga_subs])
coms = pd.concat([cbts_coms, ga_coms])

#get only the listed columns
subs = subs[['author', 'subreddit', 'created_utc', 'post_id', 'title', 'selftext', 'score']]
subs['text'] = subs['title'].astype(str) + subs['selftext'].astype(str)

coms['text'] = coms['body'].astype(str)
coms = coms[['author', 'subreddit', 'created_utc', 'post_id', 'parent_comment_id', 'associated_sub_id', 'score','text']]

#save the data
subs.to_csv('qanon_subs.csv')
coms.to_csv('qanon_coms.csv')

