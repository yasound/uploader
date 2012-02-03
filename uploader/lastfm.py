import settings
import urllib
import requests
import logging
log = logging.getLogger("uploader")


import re
import xml.sax.handler

def xml2obj(src):
    """
    A simple function to converts XML data into native Python object.
    """

    non_id_char = re.compile('[^_0-9a-zA-Z]')
    def _name_mangle(name):
        return non_id_char.sub('_', name)

    class DataNode(object):
        def __init__(self):
            self._attrs = {}    # XML attributes and child elements
            self.data = None    # child text data
        def __len__(self):
            # treat single element as a list of 1
            return 1
        def __getitem__(self, key):
            if isinstance(key, basestring):
                return self._attrs.get(key,None)
            else:
                return [self][key]
        def __contains__(self, name):
            return self._attrs.has_key(name)
        def __nonzero__(self):
            return bool(self._attrs or self.data)
        def __getattr__(self, name):
            if name.startswith('__'):
                # need to do this for Python special methods???
                raise AttributeError(name)
            return self._attrs.get(name,None)
        def _add_xml_attr(self, name, value):
            if name in self._attrs:
                # multiple attribute of the same name are represented by a list
                children = self._attrs[name]
                if not isinstance(children, list):
                    children = [children]
                    self._attrs[name] = children
                children.append(value)
            else:
                self._attrs[name] = value
        def __str__(self):
            return self.data or ''
        def __repr__(self):
            items = sorted(self._attrs.items())
            if self.data:
                items.append(('data', self.data))
            return u'{%s}' % ', '.join([u'%s:%s' % (k,repr(v)) for k,v in items])

    class TreeBuilder(xml.sax.handler.ContentHandler):
        def __init__(self):
            self.stack = []
            self.root = DataNode()
            self.current = self.root
            self.text_parts = []
        def startElement(self, name, attrs):
            self.stack.append((self.current, self.text_parts))
            self.current = DataNode()
            self.text_parts = []
            # xml attributes --> python attributes
            for k, v in attrs.items():
                self.current._add_xml_attr(_name_mangle(k), v)
        def endElement(self, name):
            text = ''.join(self.text_parts).strip()
            if text:
                self.current.data = text
            if self.current._attrs:
                obj = self.current
            else:
                # a text only node is simply represented by the string
                obj = text or ''
            self.current, self.text_parts = self.stack.pop()
            self.current._add_xml_attr(_name_mangle(name), obj)
        def characters(self, content):
            self.text_parts.append(content)

    builder = TreeBuilder()
    if isinstance(src,basestring):
        xml.sax.parseString(src, builder)
    else:
        xml.sax.parse(src, builder)
    return builder.root._attrs.values()[0]


def run_fp(mp3):
    """
    run lastfmfpclient in order to get suitable data to query
    """
    import subprocess as sub
    log.info("launching lastfmfpclient")
    p = sub.Popen([settings.LASTFMFPCLIENT, mp3],stdout=sub.PIPE,stderr=sub.PIPE)
    output, errors = p.communicate()
    
    return output


def get_lastfm_id(doc):
    url = 'http://ws.audioscrobbler.com/2.0/'
    lastfm_id = None
    try:
        data = xml2obj(doc)
    except:
        log.info("cannot build document from xml description given by lastfmpclient")
        return lastfm_id
    
    name = data['tracks'].track[0].name
    artist = data['tracks'].track[0].artist.name
    
    params = {
        "method": 'track.getinfo',
        "api_key": settings.LASTFM_APIKEY,
        "artist": artist,
        "track": name
    }
    r = requests.get(url, params=params)
    try:
        result = r.text.encode('utf-8', 'replace')
        data = xml2obj(result)
        lastfm_id = data.track.id
    except:
        log.info("cannot parse result from lastfm call")
    return lastfm_id




