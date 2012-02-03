from mutagen.mp3 import MP3
import db
import echogen
import json
import lastfm
import logging
import os
import requests
import settings
import shutil
import psycopg2
from multiprocessing import Process

conn_string = "host='yasound.com' port='5433' dbname='yasound' user='yaapp' password='N3EDTnz945FSh6D'"

logging.basicConfig()
log = logging.getLogger("uploader")
log.setLevel(logging.INFO)

def get_mp3_infos(filename):
    log.info("looking for mp3 infos about %s" % (filename))
    is_valid = True
    f = None
    try:
        f = MP3(filename)
    except:
        is_valid=False
        pass
    title = None
    artist = None
    album = None
    bitrate = 0
    
    if f and f.tags:
        if 'TIT2' in f.tags:
            title = f.tags.get('TIT2')[0]
        if 'TPE1' in f.tags:
            artist = f.tags.get('TPE1')[0]
        if 'TALB' in f.tags:
            album = f.tags.get('TALB')[0]
    if f:
        bitrate = f.info.bitrate / 1000

    if bitrate < 192:
        log.info('bitrate is too low (%d)' % (bitrate))
        is_valid = False
    info = {
        'is_valid': is_valid,
        'bitrate': bitrate,
        'artist': artist,
        'title': title,
        'album': album,
        'year': '9999',
        'type': None,
        'status': None,
        'albumid': None,
        'artistid': None,
        'fingerprint': None,
        'echonest_id': None,
        'lastfm_id': None,
    }
    log.info('title = %s, album = %s, artist = %s' % (title, album, artist))
    echo_data = echogen.run_echogen(filename)
    if echo_data and len(echo_data) > 0:
        if 'code' in echo_data[0]:
            info['fingerprint'] = echo_data[0]['code']
        info['echonest_id'] = echogen.get_echonest_id(echo_data[0])
        
    lastfm_data = lastfm.run_fp(filename)
    if lastfm_data:
        info['lastfm_id'] = lastfm.get_lastfm_id(lastfm_data)
        
    return info

def find_fuzzy(infos):
    payload = {'name': infos['title'],
               'album': infos['album'],
               'artist': infos['artist'],
               'key':settings.FUZZY_KEY
    }
    headers = {'content-type': 'application/json'}
    r = requests.post('https://dev.yasound.com/yaref/find.json/', data=json.dumps(payload), headers=headers, verify=False)
    if not r.status_code == 200:
        return None
    result = r.text
    data = json.loads(result)
    return data['db_id']

def check_if_new(mp3):
    conn = psycopg2.connect(conn_string)
    infos = get_mp3_infos(mp3)
    if not infos['is_valid']:
        log.info('invalid file')
        return False

    log.debug("trying echonest and lastfm")
    db_id = db.find_by_echonest_or_lastfm(conn, infos['echonest_id'], infos['lastfm_id'])
    if not db_id:
        log.info("trying fuzzy")
        db_id = find_fuzzy(infos)
    
    if not db_id:
        log.info("no db_id found")
        return True
    
    log.info('db_id found : %d' % db_id)
    return False

def run(root, file, filename):
    log.info("running!")
    if check_if_new(os.path.join(root,file)):
        log.info("new file!")
        dest = settings.DEST_FOLDER + '/' + file
        shutil.copyfile(filename, dest)
    
    
def main():
    pool = []
    source_folder = settings.SOURCE_FOLDER
    log.info("source folder is %s" % (source_folder))
    shutil.copyfile("./upload.sh", settings.DEST_FOLDER + '/upload.sh')
    for root, subFolders, files in os.walk(source_folder):
        for file in files:
            filename, extension = os.path.splitext(os.path.join(root,file))
            if extension == '.mp3':
                log.info("checking %s" % filename)
                p = Process(target=run, args=(root, file, filename + extension))
                pool.append(p)
                if len(pool) >= settings.POOL_SIZE:
                    [p.start() for p in pool]
                    [p.join() for p in pool]
                    pool = []
    [p.start() for p in pool]
    [p.join() for p in pool]

if __name__ == "__main__":
    main()
#    print check_if_new('../data/song.mp3')    
