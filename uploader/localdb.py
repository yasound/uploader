import sqlite3
import settings

def _build_cursor():
    conn = sqlite3.connect(settings.SQLITE_DATABASE)
    cursor = conn.cursor()
    return conn, cursor

def build_schema():
    conn, cursor = _build_cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS
        songs (id INTEGER PRIMARY KEY, filename VARCHAR(500), is_new_song BOOLEAN)
    """);
    cursor.close()

def has_song(song_filename):
    conn, cursor = _build_cursor()
    res = cursor.execute('select count(*) from songs where filename = ?', (song_filename,))
    count = res.fetchone()[0]
    cursor.close()
    return count > 0

def insert_song(song_filename, is_new_song=False):
    if has_song(song_filename):
        conn, cursor = _build_cursor()
        cursor.execute('update songs set is_new_song = ? where filename = ?', (is_new_song, song_filename))
        conn.commit()
        cursor.close()
        return
    conn, cursor = _build_cursor()
    cursor.execute('insert into songs  values (NULL, ?, ?)', (song_filename, is_new_song))
    conn.commit()
    cursor.close()

def mark_song_as_sent(song_filename):
    conn, cursor = _build_cursor()
    cursor.execute('update songs set is_new_song = ? where filename = ?', (False, song_filename))
    conn.commit()
    cursor.close()
    
def select_all_songs():
    conn, cursor = _build_cursor()
    cursor.execute(u"SELECT filename from songs")
    songs = []
    for r in cursor:
        songs.append(r[0])
    cursor.close()
    return songs

def select_new_songs():
    conn, cursor = _build_cursor()
    cursor.execute(u"SELECT filename from songs where is_new_song = ?", (True,))
    songs = []
    for r in cursor:
        songs.append(r[0])
    cursor.close()
    return songs

def delete_song(song_filename):
    conn, cursor = _build_cursor()
    cursor.execute('delete from songs  where filename = ?', (song_filename,))
    conn.commit()
    cursor.close()
    
def delete_all_songs():
    conn, cursor = _build_cursor()
    cursor.execute('delete from songs')
    conn.commit()
    cursor.close()
    
    