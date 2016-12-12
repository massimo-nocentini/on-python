
import socket
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

    def __init__(self, url, selector):
        self.url = url
        self.selector = selector
        self.response = b''
        self.sock = None

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
            print('Done reading content:\n{}'.format(self.response.decode('ascii')))


def loop(selector):
    while True:
        events = selector.select()
        for event_key, event_mask in events:
            callback = event_key.data
            callback(event_key, event_mask)


selector = DefaultSelector()

fetcher(URL(host='xkcd.com', port=80, resource='/353/'), selector).fetch()

with suppress(KeyboardInterrupt):
    loop(selector) # start the event-loop

