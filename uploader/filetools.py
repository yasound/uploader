import subprocess as sub
import settings
import logging
import uuid
log = logging.getLogger("uploader")

def convert_with_ffmpeg(filename):
    log.info('converting %s' % (filename))
    dest_filename = '/tmp/' + str(uuid.uuid1()) + '.mp3'
    args = [settings.FFMPEG, 
            '-i',
            filename]
    args.extend(settings.FFMPEG_OPTIONS.split(" "))
    args.append(dest_filename)
    
    p = sub.Popen(args,stdout=sub.PIPE,stderr=sub.PIPE)
    output, errors = p.communicate()
    print output
    print errors
    if len(errors) == 0:
        log.info(errors)
    return dest_filename

def copy_to_server(filename):
    log.info('copying %s to server' % (filename))
    args = '%s@%s:%s' % (settings.USER, settings.HOST, settings.DIR)
    p = sub.Popen(['scp', filename, args],stdout=sub.PIPE,stderr=sub.PIPE)
    output, errors = p.communicate()
    log.info(output)
    log.info(errors)
    return output, errors
    