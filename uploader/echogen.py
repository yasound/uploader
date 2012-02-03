import settings
import json
import requests
import logging

log = logging.getLogger("uploader")

def run_echogen(mp3):
    """
    run echoprint-echogen in order to get suitable data to query
    """
    import subprocess as sub
    log.info("launching echoprint_codegen")
    p = sub.Popen([settings.ECHOPRINT_CODEGEN, mp3, '0', '30'],stdout=sub.PIPE,stderr=sub.PIPE)
    output, errors = p.communicate()
    return json.loads(output)
    
def get_echonest_id(echogen_data):
    """
    query echogen server to get echonest id
    """
    log.info("look for echonest id")
    echonest_id = None
    headers = {'content-type': 'multipart/form-data'}
    data = {
        "query": json.dumps(echogen_data)
    }
    r = requests.post(settings.ECHOGEN_SERVER, data=data)
    if r.status_code != 200:
        return echonest_id
    data = json.loads(r.text)
    response = data['response']
    songs = response['songs']
    if len(songs) > 0:
        song = songs[0]
        if 'id' in song:
            echonest_id = song['id']
            log.info("found : %s", echonest_id)
    return echonest_id
