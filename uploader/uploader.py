import mutagen
import db
import echogen
import json
import lastfm
import logging
import os
import requests
import settings
import psycopg2
import localdb
from multiprocessing import Process
import sys
import getopt
import subprocess as sub
import filetools


conn_string = "host='yasound.com' port='5433' dbname='yasound' user='yaapp' password='N3EDTnz945FSh6D'"

logging.basicConfig()
log = logging.getLogger("uploader")
log.setLevel(logging.INFO)

def get_file_infos(filename):
    log.info("looking for file infos about %s" % (filename))
    is_valid = True
    f = None
    try:
        f = mutagen.File(filename, easy=True)
    except:
        log.info('%s: skip' % (filename))
        is_valid=False
        pass
    title = None
    artist = None
    album = None
    bitrate = 0
    genres = []
    if f and f.tags:
        if 'title' in f.tags:
            title = f.tags.get('title')[0]
        if 'artist' in f.tags:
            artist = f.tags.get('artist')[0]
        if 'album' in f.tags:
            album = f.tags.get('album')[0]
        if 'genre' in f.tags:
            genres = f.tags.get('genre')
    
    if f:
        bitrate = f.info.bitrate / 1000
        if  (bitrate < 128 and ('audio/mp4' in f._mimes)) or ('audio/x-flac' in f._mimes) or (bitrate < 128 and ('application/ogg' in f._mimes)) or (bitrate < 128 and ('audio/x-wma' in f._mimes)) or (bitrate < 128):
            log.info('%s: bitrate is too low (%d)' % (filename, bitrate))
            is_valid = False
    info = {
        'is_valid': is_valid,
        'bitrate': bitrate,
        'artist': artist,
        'title': title,
        'album': album,
        'duration': 0,
        'year': '9999',
        'type': None,
        'status': None,
        'fingerprint': None,
        'echonest_id': None,
        'echonest_data': None,
        'echoprint_version': None,
        'lastfm_id': None,
        'lastfm_data': None,
        'album_lastfm_id': None,
        'genres': genres,
    }
    log.info('title = %s, album = %s, artist = %s' % (title, album, artist))
    echo_data = echogen.run_echogen(filename)
    if echo_data and len(echo_data) > 0:
        if 'metadata' in echo_data[0]:
            info['echoprint_version'] = echo_data[0]['metadata']['version']
            info['duration'] = echo_data[0]['metadata']['duration']
        if 'code' in echo_data[0]:
            info['fingerprint'] = echo_data[0]['code']
        info['echonest_id'], info['echonest_data'] = echogen.get_echonest_id(echo_data[0])

    lastfm_data = lastfm.run_fp(filename)
    if lastfm_data:
        info['lastfm_id'], info['lastfm_data'] = lastfm.get_lastfm_id(lastfm_data)
        if info['lastfm_data'] is not None:
            if 'album' in info['lastfm_data']:
                album_data = info['lastfm_data']['album']
                if 'mbid' in album_data:
                    mbid = album_data['mbid']
                    info['album_lastfm_id'] = lastfm.get_lastfm_album_id(mbid)
    return info

def find_fuzzy(infos):
    payload = {'name': infos['title'],
               'album': infos['album'],
               'artist': infos['artist'],
               'key':settings.FUZZY_KEY
    }
    headers = {'content-type': 'application/json'}
    r = requests.post(settings.FUZZY_SERVER, data=json.dumps(payload), headers=headers, verify=False)
    if not r.status_code == 200:
        return None
    result = r.text
    data = json.loads(result)
    return data['db_id']

def check_if_new(file):
    """
    return boolean, infos
    """
    conn = psycopg2.connect(conn_string)
    infos = get_file_infos(file)
    if not infos['is_valid']:
        log.info('%s: invalid file' % (file))
        return False, infos

    log.debug("%s: trying echonest and lastfm" % (file))
    db_id = db.find_by_echonest_or_lastfm(conn, infos['echonest_id'], infos['lastfm_id'])
    if not db_id:
        log.info("%s: trying fuzzy" % (file))
        db_id = find_fuzzy(infos)

    if not db_id:
        log.info("%s: no db_id found" % (file))
        return True, infos

    log.info('%s: db_id found : %d' % (file, db_id))
    return False, infos

def upload_song(filename, convert=False, infos=None):
    log.info('processing %s' % (filename))
    source_file = filename
    delete_source = False
    if convert:
        source_file = filetools.convert_with_ffmpeg(filename)
        delete_source = True 

    if infos is None:
        log.info('no metadata, looking for it')
        infos = get_file_infos(source_file)
        
    payload = {
        'data': json.dumps(infos),
        'key': settings.UPLOAD_KEY
    }
    with open(source_file) as f:
        log.info('uploading song to server')
        r = requests.post(settings.UPLOAD_URL, 
                          files={'song': f},
                          data=payload,
                          verify=False)
        if r.status_code == 200:
            log.info('success')
            localdb.mark_song_as_sent(filename)
        else:
            log.info('failure')
            log.info(r.content)
        
    if delete_source:
        os.remove(source_file)    

def run(root, file, filename, upload, convert):
    is_new_song, infos = check_if_new(os.path.join(root,file))
    
    if is_new_song:
        log.info("%s: new file!" % (filename))

    localdb.insert_song(filename, is_new_song=is_new_song)
    if upload:
        upload_song(filename, convert, infos)
        

def check_for_new_songs(upload=False, convert=False):
    log.info("checking for new songs")
    pool = []
    source_folder = unicode(settings.SOURCE_FOLDER)
    log.info("source folder is %s" % (source_folder))

    for root, subFolders, files in os.walk(source_folder):
        for file in files:
            filename, extension = os.path.splitext(os.path.join(root,file))
            if extension not in settings.AUTHORIZED_EXTENSIONS:
                continue
            log.info("checking %s" % filename)
            if localdb.has_song(filename+extension):
                log.info("skipping %s (already in local database)" % (filename))
                continue
            p = Process(target=run, args=(root, file, filename + extension, upload, convert))
            pool.append(p)
            if len(pool) >= settings.POOL_SIZE:
                [p.start() for p in pool]
                [p.join() for p in pool]
                pool = []

    [p.start() for p in pool]
    [p.join() for p in pool]
    

def upload_new_songs(convert=False):
    log.info("uploading new songs")
    songs = localdb.select_new_songs()
    for song in songs:
        upload_song(song, convert)
    
def main(scan=False, upload=False, clear_db=False, convert=False):
    localdb.build_schema()
    if clear_db:
        localdb.delete_all_songs()
    if scan:
        check_for_new_songs(upload, convert)
    elif upload:
        upload_new_songs(convert=convert)
        
def usage():
    print "usage : uploader [--scan][--upload][--cleardb][--convert]"
    print "-s --scan      : scan for new songs"    
    print "-u --upload    : upload new songs to yasound server"    
    print "-c --cleardb   : erase db content"    
    print "-o --convert   : convert data to mp3 before uploading"    

if __name__ == "__main__":
    scan = False
    upload = False
    clear_db = False
    convert = False
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hsuc:v", ["help", "scan", "upload", "cleardb", "convert"])
    except getopt.GetoptError, err:
        # print help information and exit:
        print str(err) # will print something like "option -a not recognized"
        usage()
        sys.exit(2)
    output = None
    verbose = False
    for o, a in opts:
        if o == "-v":
            verbose = True
        elif o in ("-h", "--help"):
            usage()
            sys.exit()
        elif o in ("-s", "--scan"):
            scan = True
        elif o in ("-u", "--upload"):
            upload = True
        elif o in ("-c", "--cleardb"):
            clear_db = True
        elif o in ("-o", "--convert"):
            convert = True
        else:
            assert False, "unhandled option"
        
    main(scan=scan, upload=upload, clear_db=clear_db, convert=convert)
