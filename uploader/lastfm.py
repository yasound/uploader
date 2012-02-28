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
        name = data['lfm']['tracks']['track'][0]['name'][0]
        artist = data['lfm']['tracks']['track'][0]['artist']['name']
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




