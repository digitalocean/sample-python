from __future__ import unicode_literals
import youtube_dl
import psycopg2
import sys
import re
import csv
import os
#from decouple import config
from timeit import default_timer as timer
from dotenv import load_dotenv

load_dotenv()
# Get environment variables
SPACES_KEY = os.environ.get('SPACES_KEY')
SPACES_SECRET = os.environ.get('SPACES_SECRET')
DB_USER = os.environ.get('DB_USER');
DB_PASS = os.environ.get('DB_PASS');
DB_HOST = os.environ.get('DB_HOST');
DATABASE = os.environ.get('DATABASE');
DB_PORT = os.environ.get('DB_PORT');


conn = None
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
    print(row[0])
    conn.commit()
    cur.close()
except (Exception, psycopg2.DatabaseError) as error:
    print(error)
finally:
    if conn is not None:
        conn.close()
quit()
class MyLogger(object):
    def debug(self, msg):
        print("DEBUG "+msg)
        #Writing video subtitles to: .*?\.(.*?)\.ttml
        match=re.search('Writing video subtitles to: \.\/subs\/.*?\.(.*?)\.ttml', msg)
        if match:
            lang=match.group(1)
            print ("MATCH "+  lang)
            global tracker
            write_to_csv(file_name,tracker,lang)
            tracker-=1

    def warning(self, msg):
        print("WARNING "+msg)

    def error(self, msg):
        print("ERROR "+msg)
        global tracker
        write_to_csv(file_name,"0")
        tracker=0
##from https://thispointer.com/python-get-last-n-lines-of-a-text-file-like-tail-command/

def get_last_n_lines(file_name, N):
    # Create an empty list to keep the track of last N lines
    list_of_lines = []
    # Open file for reading in binary mode
    with open(file_name, 'rb') as read_obj:
        # Move the cursor to the end of the file
        read_obj.seek(0, os.SEEK_END)
        # Create a buffer to keep the last read line
        buffer = bytearray()
        # Get the current position of pointer i.e eof
        pointer_location = read_obj.tell()
        # Loop till pointer reaches the top of the file
        while pointer_location >= 0:
            # Move the file pointer to the location pointed by pointer_location
            read_obj.seek(pointer_location)
            # Shift pointer location by -1
            pointer_location = pointer_location -1
            # read that byte / character
            new_byte = read_obj.read(1)
            # If the read byte is new line character then it means one line is read
            if new_byte == b'\n':
                # Save the line in list of lines
                list_of_lines.append(buffer.decode()[::-1])
                # If the size of list reaches N, then return the reversed list
                if len(list_of_lines) == N:
                    return list(reversed(list_of_lines))
                # Reinitialize the byte array to save next line
                buffer = bytearray()
            else:
                # If last read character is not eol then add it in buffer
                buffer.extend(new_byte)
        # As file is read completely, if there is still data in buffer, then its first line.
        if len(buffer) > 0:
            list_of_lines.append(buffer.decode()[::-1])
    # return the reversed list
    return list(reversed(list_of_lines))

def my_hook(d):
    if d['status'] == 'finished':
        print('Done downloading, now converting ...')
    print("HOOK: "+d)

def write_to_csv(*args):
    f = open('sub_file.csv', 'a')
    writer = csv.writer(f)
    writer.writerow(args)
    f.close()
    
#--sub-format ttml --write-auto-sub --skip-download 
ydl_opts = {
    'writesubtitles': True,
    'skip_download': True,
    'ignoreerrors': True,
    'subtitlesformat': 'ttml',
    'outtmpl': './subs/%(id)s.%(ext)s',
    'logger': MyLogger(),
    'progress_hooks': [my_hook],
}
ydl_opts_auto = {
    'writeautomaticsub': True,
    'skip_download': True,
    'ignoreerrors': True,
    'subtitlesformat': 'ttml',
    'outtmpl': './subs/%(id)s.%(ext)s',
    'logger': MyLogger(),
    'progress_hooks': [my_hook],
}
d=get_last_n_lines('sub_file.csv',2)
x=d[0].split(",")
start=x[0]
runner=0
counter=0
start_time = timer()

with open(sys.argv[1], newline = '') as files:    
    line_reader = csv.reader(files, delimiter='\t')
    for line in line_reader:
        if line[0] !=start and runner==0:
            #print (line)
            continue
        elif line[0] == start:
            runner =1
            start_time = timer()
            continue
        
        tracker=2
        if line[11]=="1":
            if counter>0:
                end_time=timer()
                print (str(counter)+". Current files per second: "+str((end_time-start_time)/counter))
            counter+=1
            file_name=line[0]
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
                    write_to_csv(file_name,"0")
                
                
