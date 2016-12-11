
import socket
from contextlib import suppress
from selectors import DefaultSelector, EVENT_WRITE
from functools import wraps


def unregister(selector, key=lambda sock: sock.fileno()):

    def U(decorated):

        def make_callback(sock):

            @wraps(decorated)
            def callback(*args, **kwds):
                selector.unregister(key(sock))
                return decorated(*args, **kwds)

            return callback

        return make_callback

    return U

def prepare_sockets(sites, selector):

    sockets = {} 
    for site, handler in sites.items():

        sock = socket.socket()
        sock.setblocking(False)
        
        selector.register(sock.fileno(), EVENT_WRITE, handler(sock))

        sockets[site] = sock

    return sockets

def loop(selector):
    while True:
        # Unlike in our fast-spinning loop above, the call to `select` 
        # here pauses, awaiting the next I/O events. 
        events = selector.select()
        for event_key, event_mask in events:
            callback = event_key.data
            callback()

# An async framework builds on the two features we have shown:
# non-blocking sockets and the event loop, to run concurrent operations on a single thread.

selector = DefaultSelector()

@unregister(selector)
def connected_to_xkcd_eventhandler():
    print('connected to xkcd.com')

@unregister(selector)
def connected_to_oeis_eventhandler():
    print('connected to oeis.org')

@unregister(selector)
def connected_to_google_eventhandler():
    print('connected to google.com')

sites = {   ('xkcd.com', 80): connected_to_xkcd_eventhandler,
            ('oeis.org', 80): connected_to_oeis_eventhandler, 
            ('google.com', 80): connected_to_google_eventhandler, }

for site, sock in prepare_sockets(sites, selector).items():
    with suppress(BlockingIOError):
        sock.connect(site)

with suppress(KeyboardInterrupt):
    loop(selector)

# We have achieved "concurrency" here, but not what is traditionally called "parallelism". 
# That is, we built a tiny system that does overlapping I/O. It is capable of beginning 
# new operations while others are in flight.
