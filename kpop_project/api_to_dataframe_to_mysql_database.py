import pandas as pd

import datetime

import googleapiclient.discovery
    
from mysql.connector import connect, Error

''' 

    the first three functions were made to fetch youtube comments
    through youtube api and store the results into a pandas dataframe

'''

def get_comment_threads(youtube, youtube_id, data_list, pages_requested, noc, order='time'):
    
    #
    #  data_list is a list in which you want to store the data.
    #    Individual record will be stored in the form of [text, author, published_date]
    #
    #  pages_requested indicates the number of pages the program will try to look up.
    #
    #  noc is the number of comments the program will try to fetch from each page.
    #
    
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
        
        text = item['snippet']['topLevelComment']['snippet']['textDisplay']
        author = item['snippet']['topLevelComment']['snippet']['authorDisplayName']
        published = item['snippet']['topLevelComment']['snippet']['publishedAt']
        
        data_list.append([text, author, published])
        
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
            
            data_list.append([text, author, published])
        
        page_count += 1
            
        if page_count == pages_requested:
            
            break
    
    return comment_threads

def get_reply_threads(youtube, parent_id, data_list):
    
    #
    #  data_list is a list in which you want to store the data.
    #    Individual record will be stored in the form of [text, author, published_date]
    #
    
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
        
        data_list.append([text, author, published])
        
    return reply_threads    

def api_youtube_comments_to_dataframe(dev_key, youtube_id, num_of_comments, order):

    api_service_name = 'youtube'
    api_version = 'v3'
    DEVELOPER_KEY = dev_key

    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, developerKey = DEVELOPER_KEY)

    ###################### decide how many pages of comments to retreive ###########################
    
    if num_of_comments > 100:
        
        noc = 100
        pages_requested = num_of_comments // 100
        
    else:
        
        noc = num_of_comments
        pages_requested = 1
        
    ###################################   fetching data   ##########################################
    
    data_list = list()
        
    comment_threads = get_comment_threads(youtube, youtube_id, data_list, pages_requested, noc, order)
    
    for thread in comment_threads:

        get_reply_threads(youtube, thread["id"], data_list)
        
    ###################################  making dataframe  #########################################
    
    dataframe = pd.DataFrame(data_list,
                             columns = ['text', 'author', 'published_date'])
    
    def time_to_time(x):
        
        x = datetime.datetime.strptime(x,"%Y-%m-%dT%H:%M:%SZ")
        new_format = "%Y-%m-%d"
        x = x.strftime(new_format)
        
        return x
    
    dataframe['published_date'] = dataframe['published_date'].apply(lambda x: time_to_time(x))      

    return dataframe

'''

    the next five functions were made to store the dataframe that
    contains comments data into a mysql database through mysql

'''

def insert_ignore_a_group_into_groups(connector_param, group_name):
    
    h, u, pw, db = connector_param
    
    insert_groups_query = """

        INSERT IGNORE INTO kpop_groups (group_name) VALUES (%s)
        
                """
    group_name = group_name

    try:
        with connect(host=h, user=u, password=pw, database=db) as connection:
        
            with connection.cursor() as cursor:            
                    cursor.execute(insert_groups_query, (group_name,))
                    connection.commit()
                    
    except Error as e:
        print(e)

def find_group_id(connector_param, group_name):
    
    h, u, pw, db = connector_param

    select_group_id = """ SELECT id FROM kpop_groups WHERE group_name = %s """
    group_name = group_name

    try:
        with connect(host=h, user=u, password=pw, database=db) as connection:
        
            with connection.cursor() as cursor:            
                cursor.execute(select_group_id, (group_name,))
                
                group_id = cursor.fetchone()
                
    except Error as e:
        print(e)
    
    return group_id[0]

def insert_ignore_a_mv_into_videos(connector_param, song_name, group_name, youtube_id):
    
    h, u, pw, db = connector_param
    
    song_name = song_name
    group_id = find_group_id(connector_param, group_name)
    youtube_id = youtube_id
    
    insert_videos_query = """

        INSERT IGNORE INTO videos (song_name, group_id, youtube_id) VALUES (%s, %s, %s)
        
                """
    video_record = (song_name, group_id, youtube_id)
        
    try:
        with connect(host=h, user=u, password=pw, database=db) as connection:
        
            with connection.cursor() as cursor:            
                    cursor.execute(insert_videos_query, video_record)
                    connection.commit()
                    
    except Error as e:
        print(e)

def find_video_id(connector_param, song_name):
    
    h, u, pw, db = connector_param

    select_video_id = """ SELECT id FROM videos WHERE song_name = %s """
    song_name = song_name

    try:
        with connect(host=h, user=u, password=pw, database=db) as connection:
        
            with connection.cursor() as cursor:            
                cursor.execute(select_video_id, (song_name,))
                
                video_id = cursor.fetchone()             
                
    except Error as e:
        print(e)
    
    return video_id[0]

def dataframe_to_database(connector_param, song_name, dataframe):
    
    h, u, pw, db = connector_param
    
    ########################   create a comment table to store comments     #################
    
    create_table_query = """
    
            CREATE TABLE IF NOT EXISTS %s (
            
                    video_id INT,
                    text VARCHAR(1500),
                    author VARCHAR(100),
                    published_date VARCHAR(200),
        
                    FOREIGN KEY(video_id) REFERENCES videos(id)
                    ) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
        
                    """
    
    table_name = 'comments_'+str(song_name)
    create_table_query = create_table_query % table_name
    
    try:
        with connect(host=h, user=u, password=pw, database=db) as connection:
        
            with connection.cursor() as cursor:            
                    cursor.execute(create_table_query)
                    connection.commit()
                    
                    print('created table: '+ str(table_name))
                    
    except Error as e:
        print(e)
        
    ############################   insert data into comment tables   ###########################
    
    dataframe['video_id'] = find_video_id(connector_param, song_name)
    
    loopcounter = 0
    
    for i, r in dataframe.iterrows():
        
        video_id = r['video_id']
        text = r['text']
        author = r['author']
        published_date = r['published_date']
        
        comment_record = (video_id, text, author, published_date)
    
        insert_comments_query = """

            INSERT INTO %s (video_id, text, author, published_date)
                VALUES ( %%s, %%s, %%s, %%s)
        
                            """
        
        insert_comments_query = insert_comments_query % table_name
        
        try:
            with connect(host=h, user=u, password=pw, database=db) as connection:
                
                with connection.cursor() as cursor:
                
                    cursor.execute(insert_comments_query, comment_record)
                    connection.commit()

                    loopcounter += 1

                    if loopcounter % 200 == 0:
                        print('inserted '+str(loopcounter)+' comments')

        except Error as e:
            print(e)