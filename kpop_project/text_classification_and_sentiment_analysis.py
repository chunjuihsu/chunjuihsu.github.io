import numpy as np

from langdetect import detect
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.stem import WordNetLemmatizer
import re

'''
    text preprocessing
'''

def good_language_detect(text):
    try:
        language = detect(text)
        return language
    except:
        return np.nan
    
def text_cleaner(text):
    
    lemmatizer = WordNetLemmatizer()
    
    text = text.lower()                                   # make all romanization characters lowercase
    text = re.sub('k-pop', 'kpop', text)                  # simplify all different writings of K-Pop
    text = re.sub('k pop', 'kpop', text)                  # simplify all different writings of K-Pop
    
    text = re.sub('[^a-zA-Z]', ' ', text)                 # remove all non-romanization characters
    text = word_tokenize(text)                            # tokenize sentences
    text = [t for t in text if len(t)>1]                  # remove all words with only one letters
                                                          # lemmatize words and remove stopwords
    text = [lemmatizer.lemmatize(word) for word in text if not word in set(stopwords.words('english'))]
        
    text = ' '.join(text)                                 # rejoin tokenzied words to sentences
    
    text = re.sub('gon na ', 'go ', text)                 # customize results
    text = re.sub('wan na ', 'want ', text)               # customize results
    
    return text

def dataframe_preparation(dataframe):
    
    # this function only keep english comments at the end
    
    dataframe['language'] = dataframe['text'].apply(lambda x: good_language_detect(x))
    
    old = dataframe.copy()

    new = dataframe.loc[dataframe['language']=='en', :].copy()
    new = new.reset_index(drop=True)
    
    new['processed_text'] = np.nan    
    new['processed_text'] = new['text'].apply(lambda x: text_cleaner(x))
    
    return old, new

'''
    supervised classification 
'''

def classify_facilitator(dataframe, sample_size, cat_list):
    
    #  
    #  this function provide easy way for anyone to hand-code comments to be used for train-test set.
    #
    #  dataframe is a panda dataframe that contains texts for classification
    #  sample_size is the size one wish to hand-code
    #  cat_list is a list of categorizes of text one wish to classify/catagorize
    #
    
    for i in cat_list:    
        dataframe[i] = np.nan
    
    tt_set = dataframe.sample(sample_size).copy()
    
    counter = 0

    for i, r in tt_set.iterrows():
    
        print(r['text'])
        classifier = input('input accordingly with positions seperated by a comma: '+str(tuple(cat_list)))
    
        try:
            code_list = classifier.split(",")
            for a, b in zip(cat_list, code_list):
                dataframe.loc[i, a] = b
            
        except:
            for a in cat_list:
                dataframe.loc[i, a] = np.nan
                
        counter += 1
        print('----encoded-'+str(counter)+'-text----')
    
    c = cat_list[0]
    tt_set= dataframe[dataframe[c].notnull()].copy()
    
    return tt_set, dataframe

'''
    TF-IDF and Navie Bayes classification 
'''

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import BernoulliNB
from sklearn import metrics
from sklearn.metrics import accuracy_score

def tfidf_BernoulliNB_model(tt_set, text_col, cat_col):

    while True:

        x_train, x_test, y_train, y_test = train_test_split(tt_set[text_col], tt_set[cat_col])
    
        vectorizer = TfidfVectorizer(stop_words='english')
        x_train_tfidf = vectorizer.fit_transform(x_train)

        model = BernoulliNB().fit(x_train_tfidf, y_train)
        
        x_test_tfidf = vectorizer.transform(x_test)
        pred = model.predict(x_test_tfidf)

        accu_score = accuracy_score(y_test, pred)
    
        if (accu_score > 0.80) & (y_test.to_list().count(1) >= 5) & (len(np.unique(pred)) == 2):
            # customize model requirement
            
            print('classification report of '+str(cat_col)+': ')
            print('')
            print(metrics.classification_report(y_test, pred))
            
            break
        
        else:
            continue
            
    return vectorizer, model

def model_prediction(vectorizer, model, dataframe, text_col, cat_col):

    x = dataframe[text_col]
    data_tfidf = vectorizer.transform(x)
        
    pre = model.predict(data_tfidf)
    dataframe[cat_col] = pre
    
    return data_tfidf, dataframe


def classification_pipeline(tt_set, dataframe, cat_col):
    
    vectorizer, model = tfidf_BernoulliNB_model(tt_set, 'processed_text', cat_col)
    
    data_tfidf, dataframe = model_prediction(vectorizer, model, dataframe, 'processed_text', cat_col)
    
    return vectorizer, data_tfidf, dataframe

    
'''
    aspect-based sentiment analysis
'''

def customize_vader_sentiment(analyzer):
    
    #
    # analyzer is nltk.sentiment.vader.SentimentIntensityAnalyzer()
    #

    custom_sentiment = {
                        'fighting': 2.0,
                        'koreaboo': -2.0,
                        'cringe': -2.0,
                        }

    analyzer.lexicon.update(custom_sentiment)
    
    return analyzer

def vader_sentiment_type(analyzer, a_sentence):
    
    #
    # analyzer is nltk.sentiment.vader.SentimentIntensityAnalyzer()
    #

    sentiment_dict = analyzer.polarity_scores(a_sentence)

    score = sentiment_dict['compound']
    
    if score > 0:
        pred_sentiment = 'pos'
    elif score == 0:
        pred_sentiment = 'neu'
    else:
        pred_sentiment = 'neg'
        
    return pred_sentiment

def aspect_based_sentiment_analysis(analyzer, a_sentence, lexicons_of_aspects):
    
    #
    # analyzer is nltk.sentiment.vader.SentimentIntensityAnalyzer()
    #
    
    #
    # to best perform the analysis,
    # a_sentence should be a sentence, not a paragraph with multiple sentences.
    #
    # example:
    #
    # lexicons_of_aspects = {'song': ['song', 'music'],
    #                       'vocal': ['voice', 'vocal'],
    #                       'dance': ['dance', 'choreography', 'choreo'],
    #                       'korean': ['language', 'pronunciation']}
    #
    
    aspects_list = list(lexicons_of_aspects.keys())
    
    result = dict()    

    for i in range(len(aspects_list)):
        for j in lexicons_of_aspects[aspects_list[i]]:
            
            if j in a_sentence:
                
                aspect = aspects_list[i]
                st = vader_sentiment_type(analyzer, a_sentence)
                
                result[aspect] = st
    
    return result
            
def sentiment_dictionary_producer(dataframe, analyzer, lexicons_of_aspects):
    
    #
    # analyzer is analyzer is nltk.sentiment.vader.SentimentIntensityAnalyzer()
    #
    # example of parameters:
    #
    # lexicons_of_aspects = {'song': ['song', 'music'],
    #                       'vocal': ['voice', 'vocal'],
    #                       'dance': ['dance', 'choreography', 'choreo'],
    #                       'korean': ['language', 'pronunciation']}
    #
    
    aspects_list = list(lexicons_of_aspects.keys())
    
    sentiment_dic = dict()
    for i in aspects_list:
        sentiment_dic[i] = list()    

    for i, r in dataframe.iterrows():
    
        who = r['group']
        doc = sent_tokenize(r['text'])
        
        for a_sentence in doc:
            a_sentence = a_sentence.lower()
            
            small_dic = aspect_based_sentiment_analysis(analyzer, a_sentence, lexicons_of_aspects)
            for aspect in small_dic.keys():
                sentiment_dic[aspect].append((small_dic[aspect], who))
            
            
    #
    # sentiment_dic == {aspect1: [(predicted sentiment, group), ...],
    #                    aspect2: [(predicted sentiment, group), ...]}
    #
    
    return sentiment_dic