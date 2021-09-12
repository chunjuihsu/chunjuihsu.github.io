import numpy as np

from langdetect import detect
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
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
    
lemmatizer = WordNetLemmatizer()
    
def text_cleaner(text):
    
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
    
    dataframe = dataframe.reset_index(drop=True)
    dataframe.columns = ['text', 'author', 'date', 'group']
    dataframe['language'] = dataframe['text'].apply(lambda x: good_language_detect(x))

    result = dataframe.loc[ dataframe['language']=='en', :].copy()
    result = result.reset_index(drop=True)
    
    result['processed_text'] = np.nan    
    result['processed_text'] = result['text'].apply(lambda x: text_cleaner(x))
    
    return result

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

import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import BernoulliNB
from sklearn import metrics
from sklearn.metrics import accuracy_score

import matplotlib.pyplot as plt

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

'''

    The following four functions were made to evaluate tfidf model.

'''

def top_tfidf_feats(row, features, top_n=25):
    
    # Get top n tfidf values in row and return them with their corresponding feature names.

    topn_ids = np.argsort(row)[::-1][:top_n]
    top_feats = [(features[i], row[i]) for i in topn_ids]
    
    df = pd.DataFrame(top_feats)
    df.columns = ['feature', 'tfidf']
    
    return df

def top_feats_in_doc(Xtr, features, row_id, top_n=25):
    
    # Top tfidf features in specific document (matrix row)
    
    row = np.squeeze(Xtr[row_id].toarray())
    return top_tfidf_feats(row, features, top_n)

def top_mean_feats(Xtr, features, grp_ids=None, min_tfidf=0.1, top_n=25):
    
    # Return the top n features that on average are most important amongst documents in rows
    #    indentified by indices in grp_ids.
    
    if grp_ids:
        D = Xtr[grp_ids].toarray()
    else:
        D = Xtr.toarray()

    D[D < min_tfidf] = 0
    tfidf_means = np.mean(D, axis=0)
    return top_tfidf_feats(tfidf_means, features, top_n)

def top_feats_by_class(Xtr, y, features, min_tfidf=0.1, top_n=25):
    
    # Return a list of dfs, where each df holds top_n features and their mean tfidf value
    #   calculated across documents with the same class label.
    
    dfs = []
    labels = np.unique(y)
    
    for label in labels:
        
        ids = np.where(y==label)
        feats_df = top_mean_feats(Xtr, features, ids, min_tfidf=min_tfidf, top_n=top_n)
        feats_df.label = label
        dfs.append(feats_df)
        
    df0, df1 = tuple(dfs)
    
    return df0, df1

'''

    visualize tfidf model result

'''

def visualize_tfidf_model(vectorizer, data_tfidf, dataframe, cat_col):
    
    features = vectorizer.get_feature_names()
    _0, _1 = top_feats_by_class(data_tfidf, dataframe[cat_col].values, features, min_tfidf=0.1, top_n=25)
    
    y_1 = _1['feature']
    x_1 = _1['tfidf']

    y_0 = _0['feature']
    x_0 = _0['tfidf']

    fig, axs = plt.subplots(1, 2, figsize=(12, 9))
    barh1 = axs[0].barh(y_1, x_1)
    barh2 = axs[1].barh(y_0, x_0)

    axs[0].set_title('Comments about '+str(cat_col))
    axs[0].set_xlabel('mean tf-idf score')
    axs[0].spines['right'].set_visible(False)
    axs[0].spines['top'].set_visible(False)
    axs[0].set_ylim([-1, 25])
    axs[0].invert_yaxis()

    axs[1].set_title('Comments not about '+str(cat_col))
    axs[1].set_xlabel('mean tf-idf score')
    axs[1].spines['right'].set_visible(False)
    axs[1].spines['top'].set_visible(False)
    axs[1].set_ylim([-1, 25])
    axs[1].invert_yaxis()
    
    plt.savefig('tfidf_model_'+str(cat_col)+'.png', dpi=300)
    plt.show()