# -*- coding: utf-8 -*-
# source folder
SOURCE_FOLDER=u'/Users/meeloo/Music/iTunes/iTunes Media/Music/'
# type of files to be scanned
AUTHORIZED_EXTENSIONS = ('.mp3', '.m4a', '.ogg', '.aac', 'flac')

# binaries needed
ECHOPRINT_CODEGEN='echoprint-codegen'
LASTFMFPCLIENT='lastfmfpclient'
FFMPEG = 'ffmpeg'

# conversion parameters
FFMPEG_OPTIONS = '-ab 192000'

# multi processing
POOL_SIZE = 10

# local stuff
SQLITE_DATABASE='/tmp/songs.dat'

# remote server informations
USER='yasound'
HOST='ys-web02-vbo.alionis.net'
DIR='/space/new/medias/sources/with_id3/'

# API keys
ECHOGEN_SERVER='http://developer.echonest.com/api/v4/song/identify?api_key=Y9DBQSOHTHKMSMIDG'
LASTFM_APIKEY='39150a05f7f575c9da31b20c48937207'
FUZZY_KEY='ksdjwIueudfnksx(@38*2jdnjweapnfnhshdf'
