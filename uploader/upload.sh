USER=yasound
HOST=ys-web02-vbo.alionis.net
DIR=/space/new/medias/sources/with_id3/

rsync \
    --archive \
    --force \
    --progress \
    --compress \
    --checksum \
    --include "*.mp3" \
    --exclude "*" \
    --remove-source-files \
    -e ssh ./ $USER@$HOST:$DIR/