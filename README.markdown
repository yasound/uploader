# Uploader

## Requirements:
* echoprint-codegen
* lastfmfpclient

lasftmp client can be found here :

* http://blog.last.fm/2010/07/09/fingerprint-api-and-app-updated

To install echoprint-codegen :
```
brew install echoprint-codegen --use-clang
```

## Installation:
```
./vtenv.sh
```

## Configuration:
Edit ```uploader/settings.py``` to set your source and directory

## Usage:

To find suitable mp3:
```
cd uploader
./run.sh
```

To upload mp3 to server:
```
cd uploader
./upload.sh
```


