from __future__ import unicode_literals
import youtube_dl
import psycopg2
import logging
import sys
import re
import csv
import os
import boto3
import time
import tempfile
from botocore.exceptions import ClientError
#from decouple import config
from timeit import default_timer as timer
from dotenv import load_dotenv
from os.path import exists

load_dotenv()
# Get environment variables
SPACES_KEY = os.environ.get('SPACES_KEY')
SPACES_SECRET = os.environ.get('SPACES_SECRET')
DB_USER = os.environ.get('DB_USER');
DB_PASS = os.environ.get('DB_PASS');
DB_HOST = os.environ.get('DB_HOST');
DATABASE = os.environ.get('DATABASE');
DB_PORT = os.environ.get('DB_PORT');
temp_dir=tempfile.gettempdir()
#print ("debug")
#print (DB_USER)
#print (DB_PASS)
#print (DB_HOST)
#print (DB_PORT)
#print (DATABASE)
#print (SPACES_KEY)
#print (SPACES_SECRET)
#print ("debug_end")
print ("OS "+os.name)
conn = None
zip_file_name=""
file_sep='/'
### need a global variable to store these for update
likes=0
views=0
dislikes=0
waiter=0
## on windows machines, the file separator needs to be the other way round
if os.name == 'nt':
    file_sep="\\"

#initial grab of file of file names
while waiter==0:
    try:
        conn = psycopg2.connect(
        host =DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASS,
        database=DATABASE,
        sslmode="require")
        cur = conn.cursor()
        ## this allow the select statement to hold the queue so that there is no contention
        cur.execute("update files set status=1 WHERE file = (SELECT file FROM files where status=0 ORDER BY file FOR UPDATE SKIP LOCKED LIMIT 1) RETURNING *;")
        print("The number of rows: ", cur.rowcount)
        if cur.rowcount ==0:
            quit() ## and shutdown app!
        row = cur.fetchone()
        zip_file_name=row[0]
        conn.commit()
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

    ## connect to the S3 bucket
    session = boto3.session.Session()
    client = session.client('s3',
                            region_name='fra1',
                            endpoint_url='https://fra1.digitaloceanspaces.com',
                            aws_access_key_id=os.getenv('SPACES_KEY'),
                            aws_secret_access_key=os.getenv('SPACES_SECRET'))
    #response = client.list_buckets()
    #for space in response['Buckets']:
    #   print(space['Name'])

    #paginator = client.get_paginator('list_objects')
    #result = paginator.paginate(Bucket='nhc-1', Delimiter='/')
    #for prefix in result.search('CommonPrefixes'):
    #    print(prefix.get('Prefix'))

    ## this is the name of the file of filenames
    print (zip_file_name)
    path_to_zip=temp_dir+file_sep+zip_file_name 

    ## grab the file
    try:
        #zip_file_name="zst_files_12906.txt"
        client.download_file('nhc-1',
                        'extracted_files/'+zip_file_name,
                        path_to_zip)
    except ClientError as e:
            logging.error(e)
            print("E:")
            ##mark as dirty
            try:
                conn = psycopg2.connect(
                host =DB_HOST,
                port=DB_PORT,
                user=DB_USER,
                password=DB_PASS,
                database=DATABASE,
                sslmode="require")
                cur = conn.cursor()
                ## this allow the select statement to hold the queue so that there is no contention
                cur.execute("update files set status=3 WHERE file = %s",[zip_file_name])
                conn.commit()
                cur.close()
            except (Exception, psycopg2.DatabaseError) as error:
                print(error)
            finally:
                if conn is not None:
                    conn.close()
    else:
        waiter=1
        break

## callback from youtube-dl

class MyLogger(object):
    def debug(self, msg):
        print("DEBUG "+msg)
        #Writing video subtitles to: .*?\.(.*?)\.ttml
        match=re.search('Writing video subtitles to: .*?\.(.*?)\.ttml', msg)
        if match:
            lang=match.group(1)
            print ("MATCH "+  lang)
            global tracker
            ## wait until it is written
            upload_file_name=file_name+"."+lang+".ttml"
            upload_file_name_local=temp_dir+file_sep+upload_file_name
            print (upload_file_name_local)
            write_to_csv(file_name,tracker,lang,views,likes,dislikes)
            count_file=1
            while (1):
                if exists(upload_file_name_local):
                    break
                else:
                    print (count_file)
                    time.sleep(1)
            print (upload_file_name)
            upload_file(upload_file_name_local,"nhc-1",'subs/'+upload_file_name)
            tracker-=1

    def warning(self, msg):
        print("WARNING "+msg)

    def error(self, msg):
        print("ERROR "+msg)
        global tracker
        write_to_csv(file_name,"0")
        tracker=0

def my_hook(d):
    if d['status'] == 'finished':
        print('Done downloading, now converting ...')
    print("HOOK: "+d)

def write_to_csv(*args):
    try:
        conn = psycopg2.connect(
        host =DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASS,
        database=DATABASE,
        sslmode="require")
        cur = conn.cursor()
        sql = """INSERT INTO youtube_subs(file, status, lang, views,likes,dislikes)
                VALUES(%s,%s,%s,%s,%s,%s)"""
        
        cur.execute(sql,args)
        conn.commit()
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
    

def upload_file(file_name, bucket, object_name=None):
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """

    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = os.path.basename(file_name)

    # Upload the file
    try:
        response = client.upload_file(file_name, bucket, object_name)
    except ClientError as e:
        logging.error(e)
        return False
    return True
#--sub-format ttml --write-auto-sub --skip-download 
ydl_opts = {
    'writesubtitles': True,
    'skip_download': True,
    'ignoreerrors': True,
    'subtitlesformat': 'ttml',
    'outtmpl': temp_dir+file_sep+'%(id)s.%(ext)s',
    'logger': MyLogger(),
    'progress_hooks': [my_hook],
}
ydl_opts_auto = {
    'writeautomaticsub': True,
    'skip_download': True,
    'ignoreerrors': True,
    'subtitlesformat': 'ttml',
    'outtmpl': temp_dir+file_sep+'%(id)s.%(ext)s',
    'logger': MyLogger(),
    'progress_hooks': [my_hook],
    }

start_time = timer()
counter=0
with open(path_to_zip, newline = '') as files:    
    line_reader = csv.reader(files, delimiter='\t')
    for line in line_reader:
        tracker=2
        if counter>0:
            end_time=timer()
            print (str(counter)+". Current files per second: "+str((end_time-start_time)/counter))
        counter+=1
        file_name=line[0]
        views=line[1]
        likes=line[2]
        dislikes=line[3]
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download(['https://www.youtube.com/watch?v='+file_name])
        print (tracker)
        ### no real subs so try auto
        if tracker==2:
            tracker=1
            print ("NO HUMAN SUBS")
            with youtube_dl.YoutubeDL(ydl_opts_auto) as ydl:
                ydl.download(['https://www.youtube.com/watch?v='+file_name])
            if tracker==1:
                ##no subs at all
                write_to_csv(file_name,"0","none",0,0,0)
            
            
