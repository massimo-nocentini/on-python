
import socket, json, re, os

from contextlib import suppress
from selectors import DefaultSelector, EVENT_WRITE, EVENT_READ
from functools import wraps
from collections import namedtuple, deque
from itertools import count

URL = namedtuple('URL', ['host', 'port', 'resource'])

# future and task classes _______________________________________________________{{{

class future:
    ''' I represent some pending result that a coroutine is waiting for. '''

    def __init__(self):
        self.result = None
        self._callbacks = []

    def add_done_callbacks(self, callback):
        self._callbacks.append(callback)

    def resolve(self, value):
        self.result = value
        for c in self._callbacks: 
            c(resolved_future=self)

class task:

    def __init__(self, coro):
        self.coro = coro

    def start(self):
        return self(resolved_future=future())

    def __call__(self, resolved_future, return_value=None):
        try:
            pending_future = self.coro.send(resolved_future.result)
            pending_future.add_done_callbacks(self)
        except StopIteration as stop:
            return getattr(stop, 'value', return_value)

#________________________________________________________________________________}}}

# fetcher class and event-loop def ________________________________________________________ {{{

class fetcher:

    def __init__(self, url, selector, resource_key=lambda resource: resource,
                 done=lambda url, content: print(content)):
        self.url = url
        self.selector = selector
        self.response = b''
        self.sock = None
        self.done = done
        self.resource_key=lambda: resource_key(self.url.resource)

    def encode_request(self, encoding='utf8'):

        request = 'GET {} HTTP/1.0\r\nHost: {}\r\n\r\n'.format(
                self.resource_key(), self.url.host)

        return request.encode(encoding)

    def fetch(self):

        self.sock = socket.socket()
        self.sock.setblocking(False)

        with suppress(BlockingIOError):
            site = self.url.host, self.url.port
            self.sock.connect(site)
            
        f = future()

        connected_message = 'socket connected, ready for transmission'
        def connected_eventhandler(event_key, event_mask):
            f.resolve(value=connected_message)

        self.selector.register( self.sock.fileno(), 
                                EVENT_WRITE, 
                                connected_eventhandler)

        # the following `yield` makes method `fetch` a generator function.
        # We create a pending future, then yield it to pause `fetch` until the 
        # socket is ready. The inner function `connected_eventhandler` resolves the future.
        should_be_connected = yield f
        assert connected_message == should_be_connected

        self.selector.unregister(self.sock.fileno())

        print('Connection established with {} asking resource {}'.format(
                self.url.host, self.url.resource))

        # once the socket is connected, we send the HTTP GET request and read the 
        # server response. These steps need no longer be scattered among callbacks; 
        # we gather them into this very same generator function `fetch`:
        self.sock.send(self.encode_request())
        
        self.response = yield from self.read_all()

        return self.done(self.url, self.response.decode('utf8'))

    def read(self):

        f = future()

        def readable_eventhandler(event_key, event_mask):
            f.resolve(value=self.sock.recv(4096))  # 4k chunk size.

        self.selector.register( self.sock.fileno(), 
                                EVENT_READ, 
                                readable_eventhandler)

        chunk = yield f # read _one_ chunk

        selector.unregister(self.sock.fileno())

        return chunk

    def read_all(self):

        response = []

        while True:
            chunk = yield from self.read()
            if not chunk: 
                break
            else:
                response.append(chunk)

        return b''.join(response)

def loop(selector, exit=lambda clock: False):

    for clock in count():
        events = selector.select()
        for event_key, event_mask in events:
            callback = event_key.data
            callback(event_key, event_mask)

        if exit(clock): break

    return clock

#________________________________________________________________________________}}}


# OEIS stuff ____________________________________________________________________{{{

def cross_references(xref):
    regex = re.compile('(?P<id>A\d{6,6})')
    return {r for references in xref for r in regex.findall(references)}

def make_resource(oeis_id):
    return r'/search?q=id%3A{}&fmt=json'.format(oeis_id)

# loads urls already present in `fetched` directory
seen_urls = {filename[:filename.index('.json')] 
                for filename in os.listdir('./fetched/') 
                if filename.endswith('.json')}

# urls currently under fetching
fetching_urls = set()

def parse_json(url, content, sections=['xref'], whole_search=False):

    try:
        doc = json.loads(content[content.index('\n{'):])
        
        with open('fetched/{}.json'.format(url.resource), 'w') as f:
            if whole_search:
                json.dump(doc, f)
            else:
                results = doc.get('results', [])
                if results: json.dump(results[0], f)
            f.flush()

        seen_urls.add(url.resource)
        print('fetched resource {}'.format(url.resource))

        sets = [cross_references(result.get(section, [])) 
                                    for result in doc.get('results', []) 
                                    for section in sections]
        references = set.union(*sets)

    except ValueError as e:
        message = 'Generic error for resource {}:\n{}\nRaw content: {}'
        print(message.format(url.resource, e, content))
        references = set()

    except json.JSONDecodeError as e:
        message = 'Decoding error for {}:\nException: {}\nRaw content: {}'
        print(message.format(url.resource, e, content))
        references = set()

    for ref in references - seen_urls - fetching_urls:
        # we start a new `task` object for each new URL, with no concurrency cap
        url = URL(host=url.host, port=url.port, resource=ref)
        preparing = fetcher(url, selector, done=parse_json, resource_key=make_resource)
        download = task(preparing.fetch())
        download.start()
        fetching_urls.add(ref)

#________________________________________________________________________________}}}

selector = DefaultSelector()

def xkcd():

    url = URL(host='xkcd.com', port=80, resource='/353/')
    download = task(coro=fetcher(url, selector).fetch())
    download.start()
    
    with suppress(KeyboardInterrupt):
        loop(selector) # start the event-loop, endlessly

def oeis(at_least=40, initial_resources=set(seen_urls)):

    todo_urls = ['A000045']
    for ref in todo_urls:
        url = URL(host='oeis.org', port=80, resource=ref)
        preparing = fetcher(url, selector, done=parse_json, resource_key=make_resource)
        download = task(coro=preparing.fetch())
        download.start()
        fetching_urls.add(ref)
    
    def exit(clock): 
        return len(seen_urls) - len(initial_resources) > at_least 

    with suppress(KeyboardInterrupt):
        clock = loop(selector, exit) 

    fetched_urls = seen_urls-initial_resources
    print('fetched {} resources in {} clock ticks:\n{}'.format(
            len(fetched_urls), clock, fetched_urls))

# uncomment the example you want to run:

#xkcd()
oeis()


# Notes _________________________________________________________________________
# The `task` starts the `fetch` generator by sending a resolved future, 
# namely `None`, into it. Then `fetch` runs until it yields a future, which the 
# task captures as `pending_future`. When the socket is connected, the event loop 
# runs the callback `connected_eventhandler`, which resolves the future, 
# which calls `task.__call__`, which resumes `fetch`.

