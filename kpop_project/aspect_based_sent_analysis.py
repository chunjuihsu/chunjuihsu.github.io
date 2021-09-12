import pandas as pd

from nltk.tokenize import sent_tokenize
from nltk.sentiment.vader import SentimentIntensityAnalyzer

analyzer = SentimentIntensityAnalyzer()

def customize_vader_sentiment():

    custom_sentiment = {
                        'fighting': 2.0,
                        'koreaboo': -2.0,
                        'cringe': -2.0,
                        }

    analyzer.lexicon.update(custom_sentiment)

def vader_sentiment_type(sentence):

    sentiment_dict = analyzer.polarity_scores(sentence)

    score = sentiment_dict['compound']
    
    if score > 0:
        pred_sentiment = 'pos'
    elif score == 0:
        pred_sentiment = 'neu'
    else:
        pred_sentiment = 'neg'
        
    return pred_sentiment

def aspect_based_sentiment_analysis(dataframe, lexicons_of_aspects):
    
    #
    # example:
    #
    # lexicons_of_aspects = {'song': ['song', 'music'],
    #                       'vocal': ['voice', 'vocal'],
    #                       'dance': ['dance', 'choreography'],
    #                       'korean': ['korean']}
    #
    
    aspects_list = list(lexicons_of_aspects.keys())
    
    sentiment_dic = dict()
    for i in aspects_list:
        sentiment_dic[i] = list()    

    for i, r in dataframe.iterrows():
    
        who = r['group']
        doc = sent_tokenize(r['text'])
        
        for sent in doc:
            sent = sent.lower()
            
            for j in range(len(lexicons_of_aspects)):
            
                for v in lexicons_of_aspects[aspects_list[j]]:
                
                    if v in sent:
                        ps = vader_sentiment_type(sent)
                        sentiment_dic[aspects_list[j]].append((ps, who))

    return sentiment_dic