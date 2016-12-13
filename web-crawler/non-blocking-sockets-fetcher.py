
import socket, json, re, os

from contextlib import suppress
from selectors import DefaultSelector, EVENT_WRITE, EVENT_READ
from functools import wraps
from collections import namedtuple, deque
from itertools import count

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


def loop(selector, exit=lambda clock: False):

    for clock in count():
        events = selector.select()
        for event_key, event_mask in events:
            callback = event_key.data
            callback(event_key, event_mask)

        if exit(clock): break

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
        print('Generic error for resource {}:\n{}\nRaw content: {}'.format(url.resource, e, content))
        references = set()

    except json.JSONDecodeError as e:
        print('Decoding error for {}:\nException: {}\nRaw content: {}'.format(url.resource, e, content))
        references = set()

    for ref in references - seen_urls:
        # we start a new fetcher for each new URL, with no concurrency cap
        fetcher(URL(host=url.host, port=url.port, resource=ref), selector, 
                done=parse_json, resource_key=make_resource).fetch()


#________________________________________________________________________________}}}

selector = DefaultSelector()

def xkcd():
    fetcher(URL(host='xkcd.com', port=80, resource='/353/'), selector).fetch()
    with suppress(KeyboardInterrupt):
        loop(selector) # start the event-loop, endlessly

def oeis(at_least=40, initial_resources=set(seen_urls)):

    todo_urls = ['A000045']
    for ref in todo_urls:
        url = URL(host='oeis.org', port=80, resource=ref)
        fetcher(url, selector, done=parse_json, resource_key=make_resource).fetch()
    
    with suppress(KeyboardInterrupt):
        loop(selector, exit=lambda clock: len(seen_urls) - len(initial_resources) > at_least) 

    fetched_urls = seen_urls-initial_resources
    print('fetched {} resources:\n{}'.format(len(fetched_urls), fetched_urls))

# uncomment the example you want to run:

#xkcd()
oeis()


# Notes _________________________________________________________________________
# Note a nice feature of async programming with callbacks: we need no mutex around 
# changes to shared data, such as when we add links to seen_urls. There is no 
# *preemptive multitasking*, so we cannot be interrupted at arbitrary points in our code.
# This implementation makes async's problem plain: spaghetti code. 
# We need some way to express a series of computations and I/O operations, and 
# schedule multiple such series of operations to run concurrently. But without threads, 
# a series of operations cannot be collected into a single function: whenever a function 
# begins an I/O operation, it explicitly saves whatever state will be needed in the future, 
# then returns. You are responsible for thinking about and writing this state-saving code.
# What state does this function remember between one socket operation and the next? 
# It has the socket, a URL, and the accumulating response. A function that runs on a thread 
# uses basic features of the programming language to store this temporary state in local 
# variables, on its stack. The function also has a "continuation"-that is, the code it plans 
# to execute after I/O completes. The runtime remembers the continuation by storing the 
# thread's instruction pointer. You need not think about restoring these local variables 
# and the continuation after I/O. It is built in to the language.
# But with a callback-based async framework, these language features are no help. 
# While waiting for I/O, a function must save its state explicitly, because the function 
# returns and loses its stack frame before I/O completes. In lieu of local variables, 
# our callback-based example stores sock and response as attributes of self, the Fetcher 
# instance. In lieu of the instruction pointer, it stores its continuation by registering 
# the callbacks connected and read_response. As the application's features grow, so does 
# the complexity of the state we manually save across callbacks. Such onerous bookkeeping 
# makes the coder prone to migraines. Even worse, what happens if a callback throws an 
# exception, before it schedules the next callback in the chain?
# The stack trace shows only that the event loop was running a callback. We do not remember 
# what led to the error. The chain is broken on both ends: we forgot where we were going and 
# whence we came. This loss of context is called "stack ripping", and in many cases it 
# confounds the investigator. Stack ripping also prevents us from installing an exception 
# handler for a chain of callbacks, the way a "try / except" block wraps a function call 
# and its tree of descendents. So, even apart from the long debate about the relative 
# efficiencies of multithreading and async, there is this other debate regarding which is 
# more error-prone: threads are susceptible to data races if you make a mistake synchronizing 
# them, but callbacks are stubborn to debug due to stack ripping.


