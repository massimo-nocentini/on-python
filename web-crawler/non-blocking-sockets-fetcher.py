
import socket, json, re

from contextlib import suppress
from selectors import DefaultSelector, EVENT_WRITE, EVENT_READ
from functools import wraps
from collections import namedtuple, deque

URL = namedtuple('URL', ['host', 'port', 'resource'])


# Fetcher class, unregister decorator and event-loop def ________________________________________________________ {{{

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

    def __init__(self, url, selector, resource_key=lambda resource: resource,
                 done=lambda url, content: print(content)):
        self.url = url
        self.selector = selector
        self.response = b''
        self.sock = None
        self.done = done
        self.resource_key=lambda: resource_key(self.url.resource)

    def fetch(self):

        self.sock = socket.socket()
        self.sock.setblocking(False)

        self.selector.register(self.sock.fileno(), EVENT_WRITE, self._connected_eventhandler)

        with suppress(BlockingIOError):
            site = self.url.host, self.url.port
            self.sock.connect(site)

    @unregister(include_event_data=True)
    def _connected_eventhandler(self, event_key, event_mask):

        print('Connection established with {} asking resource {}'.format(self.url.host, self.url.resource))

        # Register the next callback, namely for reading the GET response.
        selector.register(event_key.fd, EVENT_READ, self._read_response)

        request = 'GET {} HTTP/1.0\r\nHost: {}\r\n\r\n'.format(self.resource_key(), self.url.host)
        self.sock.send(request.encode('utf8'))

    def _read_response(self, event_key, event_mask):
        chunk = self.sock.recv(4096)  # 4k chunk size.
        if chunk: 
            self.response += chunk # keep reading
        else: 
            selector.unregister(event_key.fd)  # Done reading.
            self.done(self.url, self.response.decode('utf8'))


def loop(selector, guard=lambda: True):
    while guard():
        events = selector.select()
        for event_key, event_mask in events:
            callback = event_key.data
            callback(event_key, event_mask)

#________________________________________________________________________________}}}


# OEIS stuff ____________________________________________________________________{{{

def cross_references(xref):
    regex = re.compile('(?P<id>A\d{6,6})')
    return {r for references in xref for r in regex.findall(references)}

def make_resource(oeis_id):
    return r'/search?q=id%3A{}&fmt=json'.format(oeis_id)

seen_urls = set()

def parse_json(url, content, sections=['xref']):

    try:
        doc = json.loads(content[content.index('\n{'):])
        
        with open('fetched/{}.json'.format(url.resource), 'w') as f:
            json.dump(doc, f)

        seen_urls.add(url.resource)
        print('fetched resource {}'.format(url.resource))

        references = set.union(*(cross_references(result.get(section, [])) 
                                    for result in doc.get('results', []) 
                                    for section in sections))

    except ValueError as e:
        print('Generic error for resource {}:\n{}\nRaw content: {}'.format(url.resource, e, content))
        references = set()

    except json.JSONDecodeError as e:
        print('Decoding error for {}:\nException: {}\nRaw content: {}'.format(url.resource, e, content))
        references = set()

    for ref in references - seen_urls:
        fetcher(URL(host=url.host, port=url.port, resource=ref), selector, 
                done=parse_json, resource_key=make_resource).fetch()


#________________________________________________________________________________}}}

selector = DefaultSelector()

def xkcd():
    fetcher(URL(host='xkcd.com', port=80, resource='/353/'), selector).fetch()
    with suppress(KeyboardInterrupt):
        loop(selector) # start the event-loop

def oeis():
    todo_urls = ['A000045']
    for ref in todo_urls:
        fetcher(URL(host='oeis.org', port=80, resource=ref),
                selector, done=parse_json, resource_key=make_resource).fetch()

    with suppress(KeyboardInterrupt):
        loop(selector, guard=lambda: len(seen_urls) < 20) 

    print('fetched resources: {}'.format(seen_urls))

# uncomment the example you want to run:

#xkcd()
oeis()

