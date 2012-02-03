import psycopg2
import hashlib
conn_string = "host='yasound.com' port='5433' dbname='yasound' user='yaapp' password='N3EDTnz945FSh6D'"
conn = psycopg2.connect(conn_string)

def get_remote_infos(db_id):
    """
    return informations about song id in yasound database
    """
    cursor = conn.cursor()
    cursor.execute("SELECT lastfm_id, echonest_id, fingerprint, quality FROM yasound_song WHERE id=%s", (db_id,))
    (lastfm_id, echonest_id, fingerprint, quality) = cursor.fetchone()
    cursor.close()
    infos = {
        "fingerprint": fingerprint,
        "lastfm_id": lastfm_id,
        "echonest_id": echonest_id,
        "quality": quality
    }
    return infos

def find_by_fingerprint(fingerprint):
    if not fingerprint:
        return None
    fingerprint_hash = hashlib.sha1(fingerprint).hexdigest()
    print "find by fingerprint : %s" % (fingerprint_hash)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM yasound_song WHERE fingerprint_hash=%s" , (fingerprint_hash,))
    try:
        (db_id,) = cursor.fetchone()
    except:
        db_id = None
    cursor.close()
    return db_id

def find_by_echonest_or_lastfm(echonest_id, lastfm_id):
    if not echonest_id:
        return find_by_lastfm_id(lastfm_id)
    if not lastfm_id:
        return find_by_echonest_id(echonest_id)
    
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM yasound_song WHERE echonest_id=%s or lastfm_id=%s" , (echonest_id, lastfm_id))
    try:
        (db_id,) = cursor.fetchone()
    except:
        db_id = None
    cursor.close()
    return db_id

def find_by_echonest_id(echonest_id):
    if not echonest_id:
        return None
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM yasound_song WHERE echonest_id=%s" , (echonest_id,))
    try:
        (db_id,) = cursor.fetchone()
    except:
        db_id = None
    cursor.close()
    return db_id

def find_by_lastfm_id(lastfm_id):
    if not lastfm_id:
        return None
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM yasound_song WHERE lastfm_id=%s" , (lastfm_id,))
    try:
        (db_id,) = cursor.fetchone()
    except:
        db_id = None
    cursor.close()
    return db_id