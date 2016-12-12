
import socket, json, re

from contextlib import suppress
from selectors import DefaultSelector, EVENT_WRITE, EVENT_READ
from functools import wraps
from collections import namedtuple

URL = namedtuple('URL', ['host', 'port', 'resource'])


def unregister(key=lambda sock: sock.fileno(), include_event_data=False):

    def U(decoring):

        @wraps(decoring)
        def callback(self, event_key, event_mask, *args, **kwds):
            self.selector.unregister(key(self.sock))
            args = ((event_key, event_mask) if include_event_data else tuple()) + args
            return decoring(self, *args, **kwds) 

        return callback

    return U

class fetcher:

    def __init__(self, url, selector, 
                 done=lambda response: print('Done reading content:\n{}'.format(response))):
        self.url = url
        self.selector = selector
        self.response = b''
        self.sock = None
        self.done = done

    def fetch(self):

        self.sock = socket.socket()
        self.sock.setblocking(False)

        self.selector.register(self.sock.fileno(), EVENT_WRITE, self._connected_eventhandler)

        with suppress(BlockingIOError):
            site = self.url.host, self.url.port
            self.sock.connect(site)

    @unregister(include_event_data=True)
    def _connected_eventhandler(self, event_key, event_mask):

        print('Connection established with: {}'.format(self.url.host))

        # Register the next callback, namely for reading the GET response.
        selector.register(event_key.fd, EVENT_READ, self._read_response)

        request = 'GET {} HTTP/1.0\r\nHost: {}\r\n\r\n'.format(self.url.resource, self.url.host)
        self.sock.send(request.encode('ascii'))

    def _read_response(self, event_key, event_mask):
        chunk = self.sock.recv(4096)  # 4k chunk size.
        if chunk: 
            self.response += chunk # keep reading
        else: 
            selector.unregister(event_key.fd)  # Done reading.
            self.done(self.response.decode('utf8'))

def loop(selector):
    while True:
        events = selector.select()
        for event_key, event_mask in events:
            callback = event_key.data
            callback(event_key, event_mask)

def cross_references(xref):
    regex = re.compile('(?P<id>A\d{6,6})')
    return {r for references in xref for r in regex.findall(references)}


def parse_json(response):

    try:
        doc = json.loads(response[response.index('\n{'):])
    except json.JSONDecodeError as e:
        print(e)
        doc = {}

    references = set.union(*(cross_references(result[section]) 
                                for result in doc.get('results', []) 
                                for section in ['xref']))
    print(references)

def make_resource(oeis_id):
    return r'/search?q=id%3A{}&fmt=json'.format(oeis_id)

selector = DefaultSelector()

#fetcher(URL(host='xkcd.com', port=80, resource='/353/'), selector).fetch()
fetcher(URL(host='oeis.org', port=80, resource=make_resource(oeis_id='A000045')), 
            selector, done=parse_json).fetch()

with suppress(KeyboardInterrupt):
    loop(selector) # start the event-loop

