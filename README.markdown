# Uploader

## Requirements:
* echoprint-codegen
* lastfmfpclient
* ffmpeg

lastfmfp client can be found here :

* http://blog.last.fm/2010/07/09/fingerprint-api-and-app-updated

To install lastfmfpclient on OSX:
```
brew install lastfmfpclient
```

To install echoprint-codegen on OSX:
```
brew install echoprint-codegen --use-clang
```

## Installation:
```
./vtenv.sh
```

## Configuration:
Edit ```uploader/settings.py``` to set your source and directory (on OSX, iTunes music directory is used by default)

## Usage:

Scan for music:

```
cd uploader
./scan.sh
```

Upload mp3 to server:

```
cd uploader
./upload.sh
```

Scan and upload in one pass:

```
cd uploader
./run.sh
```



