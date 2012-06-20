import settings
import urllib
import requests
import logging
from xml.dom.minidom import parseString

log = logging.getLogger("uploader")

class NotTextNodeError:
    pass


def getTextFromNode(node):
    """
    scans through all children of node and gathers the
    text. if node has non-text child-nodes, then
    NotTextNodeError is raised.
    """
    t = ""
    for n in node.childNodes:
        if n.nodeType == n.TEXT_NODE:
            t += n.nodeValue
        else:
            raise NotTextNodeError
    return t


def nodeToDic(node):
    """
    nodeToDic() scans through the children of node and makes a
    dictionary from the content.
    three cases are differentiated:
    - if the node contains no other nodes, it is a text-node
    and {nodeName:text} is merged into the dictionary.
    - if there is more than one child with the same name
    then these children will be appended to a list and this
    list is merged to the dictionary in the form: {nodeName:list}.
    - else, nodeToDic() will call itself recursively on
    the nodes children (merging {nodeName:nodeToDic()} to
    the dictionary).
    """
    dic = {} 
    multlist = {} # holds temporary lists where there are multiple children
    if node.attributes:
        for key in node.attributes.keys():
            value = node.attributes[key]
            dic.update({key:getTextFromNode(value)})
            
    for n in node.childNodes:

        multiple = False 
        if n.nodeType != n.ELEMENT_NODE:
            continue
        # find out if there are multiple records    
        if len(node.getElementsByTagName(n.nodeName)) > 1:
            multiple = True 
            # and set up the list to hold the values
            if not multlist.has_key(n.nodeName):
                multlist[n.nodeName] = []
        
        try:
            #text node
            text = getTextFromNode(n)
        except NotTextNodeError:
            if multiple:
                # append to our list
                multlist[n.nodeName].append(nodeToDic(n))
                dic.update({n.nodeName:multlist[n.nodeName]})
                continue
            else: 
                # 'normal' node
                dic.update({n.nodeName:nodeToDic(n)})
                continue

        # text node
        if multiple:
            multlist[n.nodeName].append(text)
            dic.update({n.nodeName:multlist[n.nodeName]})
        else:
            dic.update({n.nodeName:text})
            
    return dic


def run_fp(mp3):
    """
    run lastfmfpclient in order to get suitable data to query
    """
    import subprocess as sub
    p = sub.Popen([settings.LASTFMFPCLIENT, mp3],stdout=sub.PIPE,stderr=sub.PIPE)
    output, errors = p.communicate()
    
    return output

def find_fingerprintid(mp3):
    import subprocess as sub
    p = sub.Popen([settings.LASTFMFPCLIENT, mp3, '-nometadata'],stdout=sub.PIPE,stderr=sub.PIPE)
    output, errors = p.communicate()
    if 'FOUND' in output:
        res = output.split(' ')
        return res[0]
    return None

def find_rank(fingerprintid):
    url = 'http://ws.audioscrobbler.com/2.0/'
    params = {
        "method": 'track.getFingerprintMetadata',
        "api_key": settings.LASTFM_APIKEY,
        "fingerprintid": fingerprintid,
    }
    r = requests.get(url, params=params)
    try:
        result = r.content.encode('utf-8')
    except:
        result = r.content

    track = {}
    try:
        data = nodeToDic(parseString(result))
        track = data['lfm']['tracks']['track']
        if type(track) == type([]):
            track = track[0]
    except Exception, e:
        log.info("cannot parse result from lastfm call: %s" % (r.content))
        log.info("exception is: %s" % (e))
    return track.get('rank')
    

def get_lastfm_album_id(album_mbid):
    lastfm_id = None
    url = 'http://ws.audioscrobbler.com/2.0/'
    params = {
        "method": 'album.getinfo',
        "api_key": settings.LASTFM_APIKEY,
        "mbid": album_mbid,
    }
    r = requests.get(url, params=params)

    try:
        result = r.content.encode('utf-8')
    except:
        result = r.content

    try:
        data = nodeToDic(parseString(result))
        lastfm_id = data['lfm']['album']['id']
        log.info("album lastfm_id: %s" % (lastfm_id))
    except Exception, e:
        log.info("cannot parse result from lastfm call: %s" % (r.content))
        log.info("exception is: %s" % (e))
    return lastfm_id

def get_lastfm_id(doc):
    url = 'http://ws.audioscrobbler.com/2.0/'
    lastfm_id = None
    try:
        data = nodeToDic(parseString(doc))
        track = data['lfm']['tracks']['track']
        if type(track) == type([]):
            track = track[0]
        name = track['name'][0]
        artist = track['artist']['name']
    except:
        log.info("cannot build document from xml description given by lastfmpclient")
        return lastfm_id, None
    
    params = {
        "method": 'track.getinfo',
        "api_key": settings.LASTFM_APIKEY,
        "artist": artist,
        "track": name
    }
    r = requests.get(url, params=params)
    lastfm_data = None
    
    try:
        result = r.content.encode('utf-8')
    except:
        result = r.content

    try:
        data = nodeToDic(parseString(result))
        lastfm_id = data['lfm']['track']['id']
        lastfm_data = data['lfm']['track']
        log.info("track lastfm_id: %s" % (lastfm_id))
    except Exception, e:
        log.info("cannot parse result from lastfm call: %s" % (r.content))
        log.info("exception is: %s" % (e))
    return lastfm_id, lastfm_data


def find_by_name_artist(name, artist):
    url = 'http://ws.audioscrobbler.com/2.0/'
    params = {
        "method": 'track.getinfo',
        "api_key": settings.LASTFM_APIKEY,
        "artist": artist,
        "track": name
    }
    r = requests.get(url, params=params)
    
    try:
        result = r.content.encode('utf-8')
    except:
        result = r.content
    
    return _parse_lastfm_content(result)

def find_by_mbid(mbid):
    url = 'http://ws.audioscrobbler.com/2.0/'
    params = {
        "method": 'track.getinfo',
        "api_key": settings.LASTFM_APIKEY,
        "mbid": mbid,
    }
    r = requests.get(url, params=params)
    
    try:
        result = r.content.encode('utf-8')
    except:
        result = r.content
    
    return _parse_lastfm_content(result)

def _get_from_data(data, key):
    if not data:
        return None

    value = None
    if type(data) == type([]):
        value = data[0].get(key)
    else:
        value = data.get(key)
    
    if value and type(value) == type([]):
        return value[0]
    return value
        

def _parse_lastfm_content(result):
    lastfm_id = 0
    lastfm_name = None
    lastfm_artist = None
    lastfm_album = None
    lastfm_mbid = None
    is_valid = False
    try:
        data = nodeToDic(parseString(result))
        lastfm_id = data['lfm']['track']['id']
        lastfm_data = data['lfm']['track']
        
        lastfm_name =  _get_from_data(lastfm_data, 'name')
        lastfm_mbid = _get_from_data(lastfm_data, 'mbid')
        
        lastfm_artist = _get_from_data(lastfm_data['artist'], 'name')
        lastfm_album = _get_from_data(lastfm_data['album'], 'title')
        is_valid = True
    except Exception, _e:    
        pass
        
    metadata = {
        'id': lastfm_id,
        'name': lastfm_name,
        'artist': lastfm_artist,
        'album': lastfm_album,
        'mbid': lastfm_mbid
    }
    return metadata, is_valid

