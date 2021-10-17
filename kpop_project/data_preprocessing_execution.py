import pandas as pd

import youtube_api_comments_to_mongodb as ym
import text_classification_and_sentiment_analysis as ta

dbpw = 'kpop'
collection_name = 'comments'

data = ym.mongo_to_dataframe(dbpw, collection_name)

allcomments, englishcomments = ta.dataframe_preparation(data)

tt_set, englishcomments = ta.classify_facilitator(englishcomments, 300,
                                ['quality', 'nationalist_ethnicist', 'kpop'])

allcomments.to_pickle('allcomments.pickle')
englishcomments.to_pickle('englishcomments.pickle')
tt_set.to_pickle('tt_set.pickle')
