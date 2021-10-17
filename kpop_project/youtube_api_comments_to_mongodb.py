import pandas as pd
import datetime

import googleapiclient.discovery
import pymongo

def time_to_time(x):
        
    x = datetime.datetime.strptime(x,"%Y-%m-%dT%H:%M:%SZ")
    new_format = "%Y-%m-%d"
    x = x.strftime(new_format)
        
    return x

def youtube_api_connector(dev_key):

    api_service_name = 'youtube'
    api_version = 'v3'
    DEVELOPER_KEY = dev_key

    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, developerKey = DEVELOPER_KEY)
    
    return youtube

def get_comment_threads(youtube, youtube_id, pages_requested, noc, order, song_name, group_name):
    
    #
    #    noc and pages_requested came from function:
    #        number_of_comments_to_noc_and_pages(number_of_comments)
    #
    
    data_storage = list()
    comment_threads = list()
    page_count = 0
    
    results = youtube.commentThreads().list(
        part='snippet',
        videoId=youtube_id,
        textFormat='plainText',
        maxResults=noc,
        order=order
                ).execute()

    for item in results['items']:
        
        comment_threads.append(item)
        
        author = item['snippet']['topLevelComment']['snippet']['authorDisplayName']
        text = item['snippet']['topLevelComment']['snippet']['textDisplay']
        published = item['snippet']['topLevelComment']['snippet']['publishedAt']
        
        doc = {
                'author': author,
                'text'  : text,
                'date'  : time_to_time(published),
                'song' : song_name,
                'group': group_name,
                            
               }
        
        data_storage.append(doc)
        
    page_count += 1

    while ('nextPageToken' in results) & (pages_requested != 1):
        
        results = youtube.commentThreads().list(
            part='snippet',
            videoId=youtube_id,
            pageToken=results['nextPageToken'],
            textFormat='plainText',
            maxResults=noc,
            order=order
                    ).execute()
        
        for item in results['items']:
            
            comment_threads.append(item)

            text = item['snippet']['topLevelComment']['snippet']['textDisplay']
            author = item['snippet']['topLevelComment']['snippet']['authorDisplayName']
            published = item['snippet']['topLevelComment']['snippet']['publishedAt']
            
            doc = {
                    'author': author,
                    'text'  : text,
                    'date'  : time_to_time(published),
                    'song' : song_name,
                    'group': group_name,

                   } 
            
            data_storage.append(doc)
        
        page_count += 1
            
        if page_count == pages_requested:
            
            break
    
    return data_storage, comment_threads

def get_reply_threads(youtube, parent_id, song_name, group_name):
    
    #
    #    parent_id came from comment_threads returned from function:
    #        get_comment_threads
    #
    
    data_storage = list()
    
    results = youtube.comments().list(
        part='snippet',
        parentId=parent_id,
        textFormat="plainText"
                ).execute()
    
    reply_threads = results['items']

    for reply in reply_threads:

        text = reply['snippet']['textDisplay']
        author = reply['snippet']['authorDisplayName']
        published = reply['snippet']['publishedAt']
        
        doc = {
                'author': author,
                'text'  : text,
                'date'  : time_to_time(published),
                'song' : song_name,
                'group': group_name,
                            
               }     
        
        data_storage.append(doc)
        
    return data_storage

def number_of_comments_to_noc_and_pages(number_of_comments):

    if number_of_comments > 100:
        
        noc = 100
        pages_requested = number_of_comments // 100
        
    else:
        
        noc = number_of_comments
        pages_requested = 1
        
    #
    #    noc:
    #        represents the number of comments fetched per request
    #    pages_requested:
    #        represents how mamny requests the program should make
    #
        
    return pages_requested, noc

def youtube_to_data(youtube, youtube_id, number_of_comments, order, song_name, group_name):
    
    data_storage = list()

    ###################### decide how many pages of comments to retreive ###########################
    
    pages_requested, noc = number_of_comments_to_noc_and_pages(number_of_comments)
        
    ###################################   fetching data   ##########################################
        
    data1, comment_threads = get_comment_threads(youtube, youtube_id, pages_requested, noc, order, song_name, group_name)
    
    data_storage = data1
    
    for thread in comment_threads:
        
        data2 = get_reply_threads(youtube, thread["id"], song_name, group_name)
        
        data_storage += data2
        
    return data_storage

def data_to_mongo(dbpw, collection_name, data):
    
    connection = 'mongodb+srv://kpop:{}@cluster0.h8wkg.mongodb.net/myFirstDatabase?retryWrites=true&w=majority'.format(dbpw)
    client = pymongo.MongoClient(connection)
    db = client.get_database('comments')
    collection = db[collection_name]
    collection.insert_many(data)
    
    print('insert ', len(data), ' documents to collection ' + collection_name)


def youtube_api_to_data_mongo_pipeline(dev_key, song_name, group_name, youtube_id, number_of_comments, order, dbpw, collection_name):
    
    metadata = list()
    
    youtube = youtube_api_connector(dev_key)
    
    song_name = song_name
    group_name = group_name
    youtube_id = youtube_id

    number_of_comments = number_of_comments
    order = order   # 'relevance' or 'time'

    data = youtube_to_data(youtube, youtube_id, number_of_comments, order, song_name, group_name)
    
    metadata = metadata + data
    
    data_to_mongo(dbpw, collection_name, metadata)
    
'''
    retrieving data from mongodb atlas
'''

def mongo_to_dataframe(dbpw, collection_name):
    
    connection = 'mongodb+srv://kpop:{}@cluster0.h8wkg.mongodb.net/myFirstDatabase?retryWrites=true&w=majority'.format(dbpw)
    client = pymongo.MongoClient(connection)
    db = client.get_database('comments')
    collection = db[collection_name]
    
    author = list()
    text   = list()
    date   = list()
    song   = list()
    group  = list()

    for i in collection.find():

        author.append(i['author'])
        text.append(i['text'])
        date.append(i['date'])
        song.append(i['song'])
        group.append(i['group'])

    dataframe = pd.DataFrame(zip(author, text, date, song, group), columns=['author', 'text', 'date', 'song', 'group'])
    
    return dataframe

