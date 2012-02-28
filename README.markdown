# Uploader

## Requirements:
* echoprint-codegen
* lastfmfpclient
* ffmpeg

lasftmp client can be found here :

* http://blog.last.fm/2010/07/09/fingerprint-api-and-app-updated

To install echoprint-codegen on OSX:
```
brew install echoprint-codegen --use-clang
```

## Installation:
```
./vtenv.sh
```

## Configuration:
Edit ```uploader/settings.py``` to set your source and directory (not needed on OSX)

## Usage:

To scan for music:

```
cd uploader
./scan.sh
```

To upload mp3 to server:

```
cd uploader
./upload.sh
```

To scan and upload in one pass:

```
cd uploader
./run.sh
```



