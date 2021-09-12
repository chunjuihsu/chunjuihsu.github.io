from mysql.connector import connect, Error

h = #host
u = #user
pw = #password

#######################################################################################

drop_database_query = """

    DROP DATABASE IF EXISTS kpop
    
    """

try:
    with connect(host=h, user=u, password=pw) as connection:
        
        with connection.cursor() as cursor:            
            cursor.execute(drop_database_query)
        
except Error as e:
    print(e)

#######################################################################################

create_database_query = """

    CREATE DATABASE IF NOT EXISTS kpop
    
    """

try:
    with connect(host=h, user=u, password=pw) as connection:
        
        with connection.cursor() as cursor:            
            cursor.execute(create_database_query)
        
except Error as e:
    print(e)
    
#######################################################################################

create_table_groups = """


    CREATE TABLE kpop_groups(    
    
        id INT AUTO_INCREMENT PRIMARY KEY,
        group_name VARCHAR(100) UNIQUE

        )
        
        """

try:
    with connect(host=h, user=u, password=pw, database='kpop') as connection:
        
        with connection.cursor() as cursor:            
            cursor.execute(create_table_groups)
            connection.commit()

except Error as e:
    print(e)

#######################################################################################

create_table_videos = """

    CREATE TABLE videos(
    
        id INT AUTO_INCREMENT PRIMARY KEY,
        song_name VARCHAR(50),
        group_id INT,
        youtube_id VARCHAR(500) UNIQUE,
        
        FOREIGN KEY(group_id) REFERENCES kpop_groups(id)
        )
        
        """

try:
    with connect(host=h, user=u, password=pw, database='kpop') as connection:
        
        with connection.cursor() as cursor:            
            cursor.execute(create_table_videos)
            connection.commit()

except Error as e:
    print(e)