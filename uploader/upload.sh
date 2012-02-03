#!/bin/sh
USER=yasound
HOST=ys-web02-vbo.alionis.net
DIR=/space/new/medias/sources/with_id3/

while read line; do
  echo "$line"
    scp "$line" $USER@$HOST:$DIR/
done < new_songs.txt
