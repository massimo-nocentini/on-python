
import socket, json, re, os

from contextlib import suppress
from selectors import DefaultSelector, EVENT_WRITE, EVENT_READ
from functools import wraps
from collections import namedtuple, deque
from itertools import count

from coroutines import *

URL = namedtuple('URL', ['host', 'port', 'resource'])


# Fetcher class, unregister decorator and event-loop def ________________________________________________________ {{{

'''  {{{
def unregister(key=lambda sock: sock.fileno(), include_event_data=False):

    def U(decoring):

        @wraps(decoring)
        def callback(self, event_key, event_mask, *args, **kwds):
            self.selector.unregister(key(self.sock))
            args = ((event_key, event_mask) if include_event_data else tuple()) + args
            return decoring(self, *args, **kwds) 

        return callback

    return U

}}} '''

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

        with suppress(BlockingIOError):
            site = self.url.host, self.url.port
            self.sock.connect(site)
            
        f = future()

        def connected_eventhandler(event_key, event_mask):
            f.resolve(None)

        self.selector.register(self.sock.fileno(), EVENT_WRITE, connected_eventhandler)

        yield f

        self.selector.unregister(self.sock.fileno())

        print('Connection established with {} asking resource {}'.format(self.url.host, self.url.resource))

        request = 'GET {} HTTP/1.0\r\nHost: {}\r\n\r\n'.format(self.resource_key(), self.url.host)
        self.sock.send(request.encode('utf8'))
        
        while True:

            f = future()

            def readable_eventhandler(event_key, event_mask):
                f.resolve(self.sock.recv(4096))  # 4k chunk size.

            self.selector.register(self.sock.fileno(), EVENT_READ, readable_eventhandler)

            chunk = yield f

            selector.unregister(self.sock.fileno())  # Done reading.

            if chunk: 
                self.response += chunk # keep reading
            else: 
                break

        return self.done(self.url, self.response.decode('utf8'))


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
    t = task(coro=fetcher(URL(host='xkcd.com', port=80, resource='/353/'), selector).fetch())
    t.start()
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

xkcd()
#oeis()


# Notes _________________________________________________________________________


