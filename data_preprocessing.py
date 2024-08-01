import os
import re
import pickle
import pandas as pd
from nltk.util import ngrams
from nltk import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

#---------------------------------------------------------------------------------------------------------------------#
#change the path/name accordingly

rollups_path_name = "C:\\Users\\nikolabaci\\Desktop\\research\\qanon_data\\rollups_master.csv"
submissions_path_name = "C:\\Users\\nikolabaci\\Desktop\\research\\qanon_data\\qanon_subs.csv"
comments_path_name = "C:\\Users\\nikolabaci\\Desktop\\research\\qanon_data\\qanon_coms.csv"
hate_speech_path_name = "C:\\Users\\nikolabaci\\Desktop\\research\\qanon_data\\hsd.csv"
expert_dict_path_name = "C:\\Users\\nikolabaci\\Desktop\\research\\qanon_data\\egl.csv"

#---------------------------------------------------------------------------------------------------------------------#

def loadAltStopwords(filename):
    f = open(filename, "rb")
    stops = f.readlines()
    f.close()
    stops = [str(x)[2:len(x)] for x in stops]
    return stops
#---------------------------------------------------------------------------------------------------------------------#

def getstops():
    newstops = stopwords.words("english")
    return newstops
#---------------------------------------------------------------------------------------------------------------------#

class LemmaTokenizer:
    def __init__(self):
        self.wnl = WordNetLemmatizer()  #lemmatizer...
        self.numpattern = re.compile("\d")

        #import rollup list and set up arrays from the columns
        rollups = rollups_path_name
        replacepath = rollups #updated rollups
        replace = pd.read_csv(replacepath)
        replacetokens = replace["token"]
        groupedtokens = replace["replace"]

        #change all to-be-replaced tokens to lowercase, for matching with tokens in the tokenizing step
        replacetokens = [x.lower() for x in replacetokens]

        #Keep the rollups in a dict for fast lookup
        self.rollup_dict = {}

        #this for loop fills two new arrays with original/replacement tokens when there's a value in the replacement field
        for i in range(0, len(replacetokens)): #for each rollup term
            if not (pd.isna(groupedtokens[i])): #if the terms has a rollup term
                self.rollup_dict[replacetokens[i]] = groupedtokens[i] #then set the rollup term as the value
            else:
                self.rollup_dict[replacetokens[i]] = replacetokens[i] #otherwise set the term itself as the value

        #used in the __call__ of the object
        #remove this all together
        self.rollup_dict = dict(sorted(self.rollup_dict.items(), key=lambda x: -len(x[0])))

        self.keys = self.rollup_dict.keys()
        self.keys = sorted(self.keys, key=lambda x: len(x), reverse = True) #sort the terms to check so that longer words get replaced before shorter ones

        self.patterns = {}
        for key in self.keys:
            self.patterns[key] = re.compile(r'\b{}\b'.format(re.escape(key)))

    def __call__(self, doc, isDictWord = False):
        doc = str(doc)
        #set incoming text to lowercase
        doc = doc.lower()
        #strip whitespace on front and back of incoming text
        doc = doc.strip()
        #remove non-alphanumeric characters
        doc = re.sub(r'[^a-zA-Z0-9]+', " ", doc)
        #perform replacements over entire doc
                #scan the post for the any rollup and replace
        for key, value in self.rollup_dict.items():
            doc = self.patterns[key].sub(value, doc)

        #tokenize the incoming text into unigrams
        unigrams = word_tokenize(doc)
        #lemmatize the unigrams
        unigrams = [self.wnl.lemmatize(t) for t in unigrams]

        newstops = getstops()
        finished = []
        #this loop grabs just words that aren't in the stopwords list...
        for token in unigrams:
            if token not in newstops:
                finished.append(token)

        unigrams = finished

        if not isDictWord:
            #make bigrams from the unigrams
            bigrams = list(ngrams(unigrams, 2))
            bigrams = [" ".join(t) for t in bigrams]

            #make trigrams from the unigrams
            trigrams = list(ngrams(unigrams, 3))
            trigrams = [" ".join(t) for t in trigrams]

            #complete token list is all unigrams, all bigrams, and all trigrams
            tokens = unigrams + bigrams + trigrams
        else:
            tokens = [" ".join(unigrams)]

        return tokens
#---------------------------------------------------------------------------------------------------------------------#

def update_progress(progress, name):
    bar_length = 20
    if isinstance(progress, int):
        progress = float(progress)
    if not isinstance(progress, float):
        progress = 0
    if progress < 0:
        progress = 0
    if progress >= 1:
        progress = 1

    block = int(round(bar_length * progress))
    #clear_output(wait = True)
        #clear_output(wait = True)
    text = "Progress: [{0}] {1:.1f}%".format( "#" * block + "-" * (bar_length - block), progress * 100)
    print(name, text)

#---------------------------------------------------------------------------------------------------------------------#

def preprocessing(column, name, label = [], isDictWord = False):
    lt = LemmaTokenizer()
    result = []
    count = 0
    number_of_elements = len(column)
    step_size = number_of_elements // 100

    for i, row in enumerate(column): #for each post/comment

        res = lt(row, isDictWord)
        if isDictWord:
            res.append(label[i]) #append the label of the dictionary term

        result.append(res) #pre-preocess the text
        #used to show fency progress bar
        count+=1
        if count % 1000 == 0:
            update_progress(count / number_of_elements, name)

    return result #the result is a list of lists [["a", "b", "a b"], [], [],..., []]
#---------------------------------------------------------------------------------------------------------------------#


def main():
    #read the data
    subs = pd.read_csv(submissions_path_name)
    coms = pd.read_csv(comments_path_name)
    hsd = pd.read_csv(hate_speech_path_name)
    egl = pd.read_csv(expert_dict_path_name)

    #remove terms that should be "excluded"
    egl = egl[egl['exclude'] == 0]
    hsd = hsd[hsd['exclude01'] == 0]
    egl = egl.reset_index()
    hsd = hsd.reset_index()

    #preprecess the data and save as a compressed (pickle) file
    print("EGL in Progress...")
    pegl = preprocessing(column = egl['term'], name = "egl", label=egl['label'],  isDictWord = True)
    with open("pegl.pickle", "wb") as fp:   #Pickling
        pickle.dump(pegl, fp)
    print("EGL Done!")

    print("HSD in Progress...")
    phsd = preprocessing(column = hsd['term'], name = "hsd", label=hsd['type'], isDictWord = True)
    with open("phsd.pickle", "wb") as fp:   #Pickling
        pickle.dump(phsd, fp)
    print("HSD Done!")

    print("Submissions in Progress...")
    psubs = preprocessing(column = subs['text'], name = "subs")
    with open("psubs.pickle", "wb") as fp:   #Pickling
        pickle.dump(psubs, fp)
    print("Submissions Done!")


    print("Comments in Progress...")
    pcoms = preprocessing(column = coms['text'], name = "coms")
    with open("pcoms.pickle", "wb") as fp:   #Pickling
        pickle.dump(pcoms, fp)
    print("Comments Done!")
#---------------------------------------------------------------------------------------------------------------------#

if __name__ == "__main__":
    main()

