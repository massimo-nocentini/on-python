
import socket
from contextlib import suppress
from selectors import DefaultSelector, EVENT_WRITE
from functools import wraps


def connected_to_xkcd_eventhandler():
    print('connected to xkcd.com')

def connected_to_oeis_eventhandler():
    print('connected to oeis.org')

def connected_to_google_eventhandler():
    print('connected to google.com')
    
sites = {   ('xkcd.com', 80): connected_to_xkcd_eventhandler,
            ('oeis.org', 80): connected_to_oeis_eventhandler, 
            ('google.com', 80): connected_to_google_eventhandler, }

def prepare_sockets(sites, selector):

    sockets = {} 
    for site, callback in sites.items():

        sock = socket.socket()
        sock.setblocking(False)

        @wraps(callback)
        def unregister_and_call(sock=sock, callback=callback):
            selector.unregister(sock.fileno())
            callback()

        selector.register(sock.fileno(), EVENT_WRITE, unregister_and_call)

        sockets[site] = sock

    return sockets

selector = DefaultSelector()

for site, sock in prepare_sockets(sites, selector).items():
    with suppress(BlockingIOError):
        sock.connect(site)

def loop():
    while True:
        # Unlike in our fast-spinning loop above, the call to `select` 
        # here pauses, awaiting the next I/O events. 
        events = selector.select()
        for event_key, event_mask in events:
            callback = event_key.data
            callback()

# An async framework builds on the two features we have shown:
# non-blocking sockets and the event loop, to run concurrent operations on a single thread.

with suppress(KeyboardInterrupt):
    loop()

# We have achieved "concurrency" here, but not what is traditionally called "parallelism". 
# That is, we built a tiny system that does overlapping I/O. It is capable of beginning 
# new operations while others are in flight.
