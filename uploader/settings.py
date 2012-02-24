# -*- coding: utf-8 -*-
# source folder
import os
SOURCE_FOLDER=u'%s/Music/iTunes/iTunes Media/Music/' % (os.path.expanduser("~"))

# type of files to be scanned
AUTHORIZED_EXTENSIONS = ('.mp3', '.m4a', '.ogg', '.aac', '.flac')

# binaries needed
ECHOPRINT_CODEGEN='echoprint-codegen'
LASTFMFPCLIENT='lastfmfpclient'
FFMPEG = 'ffmpeg'

# conversion parameters
FFMPEG_OPTIONS = '-map_meta_data 0:0 -ab 192000'

# multi processing
POOL_SIZE = 10

# local stuff
SQLITE_DATABASE='./songs.dat'

# remote server informations
UPLOAD_URL='https://dev.yasound.com/api/v1/upload_song/'
UPLOAD_KEY='weeriwjwsdiwew9ei9nksxsdwxj,.29x2jdnjweapnfnhshdf'

# API keys
ECHOGEN_SERVER='http://developer.echonest.com/api/v4/song/identify?api_key=Y9DBQSOHTHKMSMIDG&bucket=audio_summary'
LASTFM_APIKEY='39150a05f7f575c9da31b20c48937207'
FUZZY_KEY='ksdjwIueudfnksx(@38*2jdnjweapnfnhshdf'

FUZZY_SERVER='https://dev.yasound.com/yaref/find.json/'