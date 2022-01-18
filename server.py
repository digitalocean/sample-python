from __future__ import unicode_literals
from cProfile import run
import youtube_dl
import psycopg2
import logging
import sys
import re
import csv
import boto3
import tempfile
import ntpath
import requests
from botocore.exceptions import ClientError
#from decouple import config
from timeit import default_timer as timer
from dotenv import load_dotenv
from os.path import exists
import signal
import sys
import urllib.request
import os
import time
import psutil
import urllib.error
from subprocess import Popen
# generate random integer values
#from random import seed
from random import randint
# seed random number generator

try:
    external_ip = urllib.request.urlopen('https://ident.me').read().decode('utf8')
except urllib.error.URLError as e:
    print (str(e.reason))
    external_ip="No IP"

load_dotenv()
# Get environment variables
WORKER_COUNT = os.environ.get('WORKER_COUNT') or "1"
SPACE = os.environ.get('SPACE')
SPACES_KEY = os.environ.get('SPACES_KEY')
SPACES_SECRET = os.environ.get('SPACES_SECRET')
DB_USER = os.environ.get('DB_USER');
DB_PASS = os.environ.get('DB_PASS');
DB_HOST = os.environ.get('DB_HOST');
DATABASE = os.environ.get('DATABASE');
DB_PORT = os.environ.get('DB_PORT');
PROXY = os.environ.get('PROXY');
APP = os.environ.get('APP') or "local";
#test-double-3-qqy7q.ondigitalocean.app
#assumes that app is "${APP_DOMAIN}"
APP=APP.rsplit('-', 1)[0]
### child gets the proxy port from the parent
proxy_port=sys.argv[1] if len(sys.argv) > 1 else ""

### add in the sys.argv function for the proxy port
proxy=""
port=0

## start the proxy server and wait
if PROXY and not proxy_port:    
    port = str(randint(10000, 20000))
    proxy="socks5://localhost:"+port
    print("PROXY "+proxy)
    ## start proxy
    result = os.system('torpy_socks -p '+port+' --hops 2 &')
    
    waiter=0
    counter=0
    #
    proxies = {'http': "socks5://127.0.0.1:"+port}

    while waiter==0:
        try: 
            requests.get('http://google.com', proxies=proxies)
            waiter=1
            print("proxy up")
        except requests.exceptions.RequestException as e:
            counter+=1
            print ("WAITING "+ str(counter))
            if counter == 20:
                quit()
            else:
                time.sleep(10)
elif PROXY and proxy_port:
    proxy="socks5://localhost:"+proxy_port
    print("PROXY STARTED BY PARENT"+proxy)    

temp_dir=tempfile.gettempdir()
#print ("debug")
print ("debug_space: "+SPACE)
print ("debug_WORKER_COUNT: "+WORKER_COUNT)
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
last_file=""
file_sep='/'
### quickest time in seconds the process should run
min_run_time=3
#min_run_time=min_run_time*int(WORKER_COUNT)
### need a global variable to store these for update
likes=0
views=0
dislikes=0
waiter=0
collector=""
file_name=""
parent=""
my_pid=str(os.getpid())
sub_pid=[]
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
        cur.execute("update files set status=1 WHERE file = (SELECT file FROM files where status=0 or status=3 ORDER BY file FOR UPDATE SKIP LOCKED LIMIT 1) RETURNING *;")
        print("The number of rows found: ", cur.rowcount)
        if cur.rowcount ==0:
            quit() ## and shutdown app!
        row = cur.fetchone()
        print ("STATUS:" + str(row[1]))
        zip_file_name=row[0]
        last_file=row[2]
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
        print("DEBUG "+msg+ " "+ external_ip)
        #Writing video subtitles to: .*?\.(.*?)\.ttml
        match=re.search('Writing video subtitles to: .*?\.(.*?)\.ttml', msg)
        if match:
            lang=match.group(1)
            print ("MATCH "+  lang + " - "+file_name)
            global tracker
            ## wait until it is written
            upload_file_name=file_name+"."+lang+".ttml"
            upload_file_name_local=temp_dir+file_sep+upload_file_name
            print (upload_file_name_local)
            global collector
            collector=upload_file_name_local
            count_file=1
            ## do not put upload here
            # it creates a race condition               
            write_to_csv(file_name,tracker,lang,views,likes,dislikes,SPACE,APP)
            tracker-=1


    def warning(self, msg):
        print("WARNING "+msg+ " "+ external_ip+" "+file_name)
        match=re.search('Error 429',msg)
        if match:
            if not PROXY:
            ### reboot - if it's not a proxy, wait to stop spamming the IP
                time.sleep(360)
            send_sig()

    def error(self, msg):
        print("ERROR "+msg+ " "+ external_ip+" "+file_name)
        global tracker
        match=re.search('Connection refused|4 bytes|violation of protocol',msg)
        match_1=re.search('Gone',msg)
        if match:
            send_sig()
        elif match_1:
            write_to_csv(file_name,"3","0","0","0","0","",APP)
        else:
            write_to_csv(file_name,"0","0","0","0","0","",APP)    
            tracker=0

def my_hook(d):
    if d['status'] == 'finished':
        print('Done downloading, now converting ...')
    print("HOOK: "+d)

def checkIfProcessRunning(processName):
    '''
    Check if there is any running process that contains the given name processName.
    '''
    #Iterate over the all the running process
    for proc in psutil.process_iter():
        try:
            # Check if process name contains the given name string.
            #print (proc.cmdline())
            if processName in proc.cmdline():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False;

def dirty_db():
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
        sql = """INSERT INTO youtube_subs(file, status, lang, views,likes,dislikes,space,app)
                VALUES(%s,%s,%s,%s,%s,%s,%s,%s) ON CONFLICT DO NOTHING"""
        sql_1 = """UPDATE files SET last_file =%s where file=%s"""
        cur.execute(sql,args)
        cur.execute(sql_1,[args[0],zip_file_name])
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

## mark the db as dirty before stopping

def exit_handler(signum, stack_frame):
    print('Termination event received: Updating DB '+str(signum)+ " "+ my_pid)
    dirty_db()
    ### Am I the parent
    if parent=="none":
        print('SINGLE WORKER Termination at :', time.ctime())
    elif parent=="true":
        ###cleanup
        print(my_pid+' Termination by parent sent at :', time.ctime())
        for pid in sub_pid:
            if check_pid(pid):
                os.kill(pid,14)  # kill the sub 
                print ("Terminating "+str(pid))
        count= proc_count()
        timer=1
        ## cleanup or ten seconds
        while count>1:
            time.sleep(1)
            count= proc_count()
            print ("WAIT COUNT: "+str(count))
            count+=1
            if timer ==10:
                print ("TIMEOUT: "+str(count-1)+" subs left")
                count=1
        print("parent cleaning up")
    elif not parent:
        ## regular termination
        print(my_pid+' regular termination:', time.ctime())
        ### do cleanup
        if signum!=14:
            print(my_pid+' regular termination sent to parent:', time.ctime())
            os.kill(psutil.Process(os.getpid()).ppid(),14)
    sys.exit()
    
    
def proc_count():
    return sum(1 for proc in psutil.process_iter() if 'server.py' in proc.cmdline())

def check_pid(pid):        
    """ Check For the existence of a unix pid. """
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    else:
        return True

def send_sig():
    ### need to trigger the cleanup of other workers
    # unless it is only one worker
    
    if int(WORKER_COUNT)==1:
        dirty_db()
        sys.exit()
    else:
        os.kill(os.getpid(),signal.SIGTERM)
 

signal.signal(signal.SIGINT, exit_handler)
signal.signal(signal.SIGTERM, exit_handler)


ydl_opts = {
    'writesubtitles': True,
    'skip_download': True,
    'ignoreerrors': True,
    'subtitlesformat': 'ttml',
    'outtmpl': temp_dir+file_sep+'%(id)s.%(ext)s',
    'logger': MyLogger(),
    'progress_hooks': [my_hook],
    'proxy': proxy
}
ydl_opts_auto = {
    'writeautomaticsub': True,
    'skip_download': True,
    'ignoreerrors': True,
    'subtitlesformat': 'ttml',
    'outtmpl': temp_dir+file_sep+'%(id)s.%(ext)s',
    'logger': MyLogger(),
    'progress_hooks': [my_hook],
    'proxy': proxy
    }

### go for the number of workers, less 1
### could be done without this "if" but windows complains
if int(WORKER_COUNT)>1:
    count = proc_count()
    if count >1:
        print(str(count)+' I am the child '+my_pid)
    else:
        print(str(count)+' I am the parent '+my_pid)
        parent="true"
        for x in range(int(WORKER_COUNT)-1):
    # Python >= 3.3 has subprocess.DEVNULL
            p=Popen(['python','server.py',port])
            sub_pid.append(p.pid)
else:
    parent="none"

start_time = timer()
counter=0
runner=0
run_time=2
sleep_time=0
with open(path_to_zip, newline = '') as files:    
    line_reader = csv.reader(files, delimiter='\t')
    for line in line_reader:
        ### is there already a file processed and we have marked the dirty as clean
        if last_file:
            if line[0] !=last_file and runner==0:
                #print (line)
                continue
            elif line[0] == last_file:
                runner =1
                start_time = timer()
                continue
        tracker=2
        if counter>0:
            end_time=timer()
            run_time=(end_time-start_time)/counter
            print (str(counter)+". Current files per second: "+str(run_time))
            if run_time <min_run_time:
                sleep_time=int(min_run_time-run_time)+1
                print("SLEEP TIME UPDATED: "+str(sleep_time))
            else:
                sleep_time=0
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
                write_to_csv(file_name,"0","none",0,0,0,"",APP)
        if collector:
            ### the file exists, just needs to finish downloading
            if exists(collector):
                    upload_file(collector,SPACE,'subs/'+ntpath.basename(collector))
                    ## take out the trash
                    try:
                        print ("REMOVING " +collector)
                        os.remove(collector)
                    except OSError:
                        print ("CANNOT REMOVE "+ collector)
                    
            else:
                print (collector+"failed to upload")
            collector=""
            time.sleep(sleep_time)        
            