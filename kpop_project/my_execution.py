import pandas as pd

import re
import datetime

import os
import googleapiclient.discovery
    
from mysql.connector import connect, Error

'''

    youtube to database

'''

import api_to_dataframe_to_mysql_database as atdtmd

def youtube_to_database(connector_param, dev_key, song_name, group_name, youtube_id, order, num_of_comments):
    
    #
    #   song_name, group_name should all be lower-case, without space, and without special characters
    #
    
    dataframe = atdtmd.api_youtube_comments_to_dataframe(dev_key, youtube_id, num_of_comments, order)
    
    ##############################    sql functions     ################################
    
    atdtmd.insert_ignore_a_group_into_groups(connector_param, group_name)
    
    atdtmd.insert_ignore_a_mv_into_videos(connector_param, song_name, group_name, youtube_id)
    
    atdtmd.dataframe_to_database(connector_param, song_name, dataframe)

song_list = ['luvwrong', 'feellikethis', 'breakout', 'tonight', 'yourturn', 'photomagic', 'popsicle', 'piri']
group_list = ['expedition', 'expedition', 'prisma', 'blackswan', 'kaachi', 'kaachi', 'uhsn', '5high']
youtube_id_list = ['u0VubbfytQs', 'R8_fuXncjDo','17xRBNkMp14', 'Yb_K5-IIKgg', '1NWzao4xf1E', 'ngf7JiIzyfM', 'g_dqiyxZO_Y', 'zI7XMeqyNA8']

for s, g, y in zip(song_list, group_list, youtube_id_list):
    
    connector_param = (#host, #user, #password, 'kpop')
    dev_key = #your developer key
    
    song_name = s
    group_name = g
    youtube_id = y
    
    order = 'relevance'   # change to 'time' when the purpose to run this program is to update the latest comments 
    
    youtube_to_database(connector_param, dev_key, song_name, group_name, youtube_id, order, 600)

'''

    fetch data from database

'''

h = #host
u = #user
pw = #password

sql = """ SELECT song_name FROM videos """

try:
    with connect(host=h, user=u, password=pw, database=db) as connection:
        
        with connection.cursor() as cursor:            
            cursor.execute(sql)

            song_name_list = [item[0] for item in cursor.fetchall()]
                
except Error as e:
    print(e)
    
comments_table_name_list = list()

for song_name in song_name_list:
    
    table_name = 'comments_'+song_name
    comments_table_name_list.append(table_name)

data = pd.DataFrame()

for table in comments_table_name_list:
    
    select_query = """
    
        SELECT `%s`.text, `%s`.author, `%s`.published_date, kpop_groups.group_name
        
        FROM `%s`
        
        INNER JOIN videos
        
        ON `%s`.video_id = videos.id
        
        INNER JOIN kpop_groups
        
        ON videos.group_id = kpop_groups.id
        
        """
    
    replace_tuple = (table, table, table, table, table)
    
    try:
        with connect(host=h, user=u, password=pw, database=db) as connection:
        
            with connection.cursor() as cursor:            
                cursor.execute(select_query % replace_tuple)
            
                comment = pd.DataFrame(cursor.fetchall())
                
                data = data.append(comment)
                
    except Error as e:
        print(e)

'''

    text classification

'''

import classfication_model_builder as cmb

data = cmb.dataframe_preparation(data)
tt_set, data = classify_facilitator(data, 400,
                                ['quality', 'nationalist_ethnicist', 'kpop'])

tt_set = tt_set[tt_set['kpop'].notnull()].copy()

tt_set['quality'] = tt_set['quality'].astype(int)
tt_set['nationalist_ethnicist'] = tt_set['nationalist_ethnicist'].astype(int)
tt_set['kpop'] = tt_set['kpop'].astype(int)

def work_pipeline(dataframe, cat_col):
    
    vectorizer, model = cmb.tfidf_BernoulliNB_model(tt_set, 'processed_text', cat_col)
    
    data_tfidf, dataframe = cmb.model_prediction(vectorizer, model, dataframe, 'processed_text', cat_col)
    
    cmb.visualize_tfidf_model(vectorizer, data_tfidf, dataframe, cat_col)
    
work_pipeline(data, 'quality')
work_pipeline(data, 'nationalist_ethnicist')
work_pipeline(data, 'kpop')

'''

    sentiment analysis
    
        please see storytelling_execution.ipynb in path \storytelling

'''

